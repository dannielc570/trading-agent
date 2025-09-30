"""Modern Web UI FastAPI Application"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys
from datetime import datetime
import os

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.chdir(str(Path(__file__).parent.parent.parent))

from src.database import get_db_context, Strategy, Backtest, ScrapedContent, OptimizationRun

# Create FastAPI app
app = FastAPI(title="Trading Platform UI", version="1.0.0")

# Setup templates
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Try to mount static files (create if doesn't exist)
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    with get_db_context() as db:
        total_strategies = db.query(Strategy).count()
        total_backtests = db.query(Backtest).count()
        completed_backtests = db.query(Backtest).filter(Backtest.status == "completed").count()
        total_scraped = db.query(ScrapedContent).count()
        
        # Get best performing strategy
        best_backtest = db.query(Backtest).filter(
            Backtest.status == "completed",
            Backtest.total_return.isnot(None)
        ).order_by(Backtest.total_return.desc()).first()
        
        best_strategy_name = None
        best_return = 0
        if best_backtest and best_backtest.strategy:
            best_strategy_name = best_backtest.strategy.name
            best_return = best_backtest.total_return
        
        # Average metrics
        completed = db.query(Backtest).filter(
            Backtest.status == "completed",
            Backtest.total_return.isnot(None)
        ).all()
        
        avg_return = sum(b.total_return for b in completed) / len(completed) if completed else 0
        avg_sharpe = sum(b.sharpe_ratio for b in completed if b.sharpe_ratio) / len(completed) if completed else 0
        
        return {
            "total_strategies": total_strategies,
            "total_backtests": total_backtests,
            "completed_backtests": completed_backtests,
            "total_scraped": total_scraped,
            "best_strategy": best_strategy_name,
            "best_return": round(best_return * 100, 2) if best_return else 0,
            "avg_return": round(avg_return * 100, 2),
            "avg_sharpe": round(avg_sharpe, 2)
        }


@app.get("/api/strategies")
async def get_strategies():
    """Get all strategies with their performance"""
    with get_db_context() as db:
        strategies = db.query(Strategy).all()
        
        result = []
        for strategy in strategies:
            # Get best backtest for this strategy
            best_backtest = db.query(Backtest).filter(
                Backtest.strategy_id == strategy.id,
                Backtest.status == "completed",
                Backtest.total_return.isnot(None)
            ).order_by(Backtest.total_return.desc()).first()
            
            # Count backtests
            backtest_count = db.query(Backtest).filter(
                Backtest.strategy_id == strategy.id
            ).count()
            
            result.append({
                "id": strategy.id,
                "name": strategy.name,
                "category": strategy.category or "unknown",
                "status": strategy.status,
                "backtest_count": backtest_count,
                "best_return": round(best_backtest.total_return * 100, 2) if best_backtest and best_backtest.total_return else 0,
                "best_sharpe": round(best_backtest.sharpe_ratio, 2) if best_backtest and best_backtest.sharpe_ratio else 0,
                "created_at": strategy.created_at.isoformat() if strategy.created_at else None
            })
        
        # Sort by best return
        result.sort(key=lambda x: x["best_return"], reverse=True)
        return result


@app.get("/api/backtests")
async def get_backtests(limit: int = 50):
    """Get recent backtests"""
    with get_db_context() as db:
        backtests = db.query(Backtest).order_by(Backtest.created_at.desc()).limit(limit).all()
        
        result = []
        for bt in backtests:
            result.append({
                "id": bt.id,
                "strategy_name": bt.strategy.name if bt.strategy else "Unknown",
                "symbol": bt.symbol,
                "timeframe": bt.timeframe,
                "total_return": round(bt.total_return * 100, 2) if bt.total_return else 0,
                "sharpe_ratio": round(bt.sharpe_ratio, 2) if bt.sharpe_ratio else 0,
                "max_drawdown": round(bt.max_drawdown * 100, 2) if bt.max_drawdown else 0,
                "win_rate": round(bt.win_rate * 100, 2) if bt.win_rate else 0,
                "total_trades": bt.total_trades or 0,
                "status": bt.status,
                "created_at": bt.created_at.isoformat() if bt.created_at else None
            })
        
        return result


@app.get("/api/performance-chart")
async def get_performance_chart():
    """Get data for performance chart"""
    with get_db_context() as db:
        backtests = db.query(Backtest).filter(
            Backtest.status == "completed",
            Backtest.total_return.isnot(None)
        ).all()
        
        # Group by strategy
        strategy_performance = {}
        for bt in backtests:
            strategy_name = bt.strategy.name if bt.strategy else "Unknown"
            if strategy_name not in strategy_performance:
                strategy_performance[strategy_name] = []
            
            strategy_performance[strategy_name].append({
                "symbol": bt.symbol,
                "return": round(bt.total_return * 100, 2),
                "sharpe": round(bt.sharpe_ratio, 2) if bt.sharpe_ratio else 0
            })
        
        return strategy_performance


@app.get("/api/asset-comparison")
async def get_asset_comparison():
    """Get asset comparison data"""
    with get_db_context() as db:
        backtests = db.query(Backtest).filter(
            Backtest.status == "completed",
            Backtest.total_return.isnot(None)
        ).all()
        
        # Group by asset
        asset_stats = {}
        for bt in backtests:
            if bt.symbol not in asset_stats:
                asset_stats[bt.symbol] = {
                    "returns": [],
                    "sharpes": [],
                    "test_count": 0
                }
            
            asset_stats[bt.symbol]["returns"].append(bt.total_return * 100)
            if bt.sharpe_ratio:
                asset_stats[bt.symbol]["sharpes"].append(bt.sharpe_ratio)
            asset_stats[bt.symbol]["test_count"] += 1
        
        # Calculate averages
        result = []
        for symbol, stats in asset_stats.items():
            result.append({
                "symbol": symbol,
                "avg_return": round(sum(stats["returns"]) / len(stats["returns"]), 2),
                "avg_sharpe": round(sum(stats["sharpes"]) / len(stats["sharpes"]), 2) if stats["sharpes"] else 0,
                "test_count": stats["test_count"]
            })
        
        result.sort(key=lambda x: x["avg_return"], reverse=True)
        return result


def create_app():
    """Create and configure the app"""
    return app

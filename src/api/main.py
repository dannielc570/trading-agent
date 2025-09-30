"""FastAPI application"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import asyncio

from ..database import get_db, init_db, Strategy, Backtest, ScrapedContent
from ..data_collection import WebSearcher, GenericWebScraper, MarketDataCollector
from ..config import settings
from .schemas import (
    StrategyCreate, StrategyResponse,
    BacktestCreate, BacktestResponse,
    SearchRequest, SearchResponse
)

app = FastAPI(
    title="Trading Strategy Platform API",
    description="API for trading strategy research and optimization",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Trading Strategy Platform API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Strategies
@app.get("/strategies", response_model=List[StrategyResponse])
async def list_strategies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all strategies"""
    strategies = db.query(Strategy).offset(skip).limit(limit).all()
    return strategies


@app.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get strategy by ID"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@app.post("/strategies", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create new strategy"""
    db_strategy = Strategy(**strategy.dict())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


# Backtests
@app.get("/backtests", response_model=List[BacktestResponse])
async def list_backtests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all backtests"""
    backtests = db.query(Backtest).offset(skip).limit(limit).all()
    return backtests


@app.get("/backtests/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(backtest_id: int, db: Session = Depends(get_db)):
    """Get backtest by ID"""
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return backtest


# Search and scraping
@app.post("/search", response_model=SearchResponse)
async def search_strategies(request: SearchRequest):
    """Search for trading strategies"""
    searcher = WebSearcher()
    results = await searcher.search_strategies(
        query=request.query,
        max_results=request.max_results
    )
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results)
    )


@app.post("/scrape")
async def scrape_url(url: str, db: Session = Depends(get_db)):
    """Scrape content from URL"""
    scraper = GenericWebScraper()
    content = await scraper.scrape(url)
    
    if not content:
        raise HTTPException(status_code=400, detail="Failed to scrape URL")
    
    # Save to database
    scraped_content = ScrapedContent(
        source_url=content["url"],
        source_type=content.get("source_type", "article"),
        title=content.get("title"),
        content=content.get("content"),
        raw_html=content.get("raw_html"),
        extracted_data=content
    )
    db.add(scraped_content)
    db.commit()
    db.refresh(scraped_content)
    
    return {"status": "success", "content_id": scraped_content.id}


@app.get("/scraped")
async def list_scraped_content(
    skip: int = 0,
    limit: int = 100,
    processed: bool = None,
    db: Session = Depends(get_db)
):
    """List scraped content"""
    query = db.query(ScrapedContent)
    
    if processed is not None:
        query = query.filter(ScrapedContent.processed == processed)
    
    items = query.offset(skip).limit(limit).all()
    return items


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    total_strategies = db.query(Strategy).count()
    total_backtests = db.query(Backtest).count()
    total_scraped = db.query(ScrapedContent).count()
    
    completed_backtests = db.query(Backtest).filter(
        Backtest.status == "completed"
    ).count()
    
    return {
        "total_strategies": total_strategies,
        "total_backtests": total_backtests,
        "completed_backtests": completed_backtests,
        "total_scraped_content": total_scraped,
    }

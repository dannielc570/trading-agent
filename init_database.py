"""Initialize database tables for the trading platform"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.database import Base, engine
from src.database import get_db_context
from src.database.models import Strategy, Backtest, OptimizationRun, ScrapedContent, MarketData
from loguru import logger

def init_database():
    """Create all database tables"""
    try:
        logger.info("🔧 Initializing database...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully!")
        
        # Verify tables exist
        with get_db_context() as db:
            # Try a simple query to each table
            strategy_count = db.query(Strategy).count()
            backtest_count = db.query(Backtest).count()
            logger.info(f"📊 Database initialized: {strategy_count} strategies, {backtest_count} backtests")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

"""Database models for the trading platform"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base


class Strategy(Base):
    """Trading strategy model"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(512), nullable=True)
    category = Column(String(100), nullable=True, index=True)  # e.g., "momentum", "mean_reversion"
    
    # Strategy code/configuration
    code = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)  # Strategy parameters as JSON
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(50), default="discovered")  # discovered, tested, optimized, forward_testing, live
    
    # Relationships
    backtests = relationship("Backtest", back_populates="strategy", cascade="all, delete-orphan")
    optimizations = relationship("OptimizationRun", back_populates="strategy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', status='{self.status}')>"


class Backtest(Base):
    """Backtest results model"""
    __tablename__ = "backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    # Test configuration
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(20), nullable=False)  # e.g., "1m", "5m", "1h", "1d"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    
    # Performance metrics
    total_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    total_trades = Column(Integer, nullable=True)
    
    # Additional metrics
    metrics = Column(JSON, nullable=True)  # Store all metrics as JSON
    equity_curve = Column(JSON, nullable=True)  # Store equity curve data
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")
    
    def __repr__(self):
        return f"<Backtest(id={self.id}, strategy_id={self.strategy_id}, symbol='{self.symbol}')>"


class OptimizationRun(Base):
    """Strategy optimization run model"""
    __tablename__ = "optimization_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    # Optimization configuration
    optimization_type = Column(String(50), nullable=False)  # grid_search, bayesian, genetic
    parameter_space = Column(JSON, nullable=False)  # Parameters to optimize
    n_trials = Column(Integer, nullable=False)
    
    # Results
    best_parameters = Column(JSON, nullable=True)
    best_score = Column(Float, nullable=True)
    optimization_metric = Column(String(50), nullable=False)  # sharpe_ratio, total_return, etc.
    
    # All trial results
    trials = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Relationships
    strategy = relationship("Strategy", back_populates="optimizations")
    
    def __repr__(self):
        return f"<OptimizationRun(id={self.id}, strategy_id={self.strategy_id}, status='{self.status}')>"


class ScrapedContent(Base):
    """Scraped content from web sources"""
    __tablename__ = "scraped_content"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source information
    source_url = Column(String(512), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # article, forum_post, video, chart_data
    title = Column(String(512), nullable=True)
    
    # Content
    content = Column(Text, nullable=True)
    raw_html = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)  # Structured data extracted from content
    
    # Classification
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Processing status
    processed = Column(Boolean, default=False, index=True)
    strategy_created = Column(Boolean, default=False)
    
    # Metadata
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ScrapedContent(id={self.id}, source_type='{self.source_type}', title='{self.title}')>"


class MarketData(Base):
    """Market data storage (OHLCV)"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    source = Column(String(50), nullable=True)  # yfinance, tradingview, alpha_vantage, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', timeframe='{self.timeframe}', timestamp={self.timestamp})>"

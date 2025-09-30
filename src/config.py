"""
Configuration management for the trading platform
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = Field(
        default="sqlite:///./data/trading_platform.db",
        description="Database connection URL"
    )
    
    # API Keys
    alpha_vantage_api_key: Optional[str] = Field(default=None, description="Alpha Vantage API key")
    serpapi_key: Optional[str] = Field(default=None, description="SerpAPI key for advanced search")
    
    # Application
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Scraping
    max_concurrent_scrapers: int = Field(default=5, description="Maximum concurrent scraping tasks")
    scrape_interval_minutes: int = Field(default=60, description="Interval between scraping runs")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="User agent for web requests"
    )
    
    # Backtesting
    backtest_initial_capital: float = Field(default=10000.0, description="Initial capital for backtests")
    backtest_commission: float = Field(default=0.001, description="Commission rate (0.1%)")
    backtest_slippage: float = Field(default=0.0005, description="Slippage rate (0.05%)")
    
    # ML/Optimization
    optimization_trials: int = Field(default=100, description="Number of optimization trials")
    n_jobs: int = Field(default=-1, description="Number of parallel jobs (-1 for all CPUs)")
    
    # Dashboard
    dashboard_port: int = Field(default=8501, description="Streamlit dashboard port")
    api_port: int = Field(default=8000, description="FastAPI server port")
    
    # TradingView
    tradingview_username: Optional[str] = Field(default=None, description="TradingView username")
    tradingview_password: Optional[str] = Field(default=None, description="TradingView password")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

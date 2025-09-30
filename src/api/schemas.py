"""Pydantic schemas for API"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class StrategyCreate(BaseModel):
    """Schema for creating a strategy"""
    name: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class StrategyResponse(BaseModel):
    """Schema for strategy response"""
    id: int
    name: str
    description: Optional[str]
    source_url: Optional[str]
    category: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class BacktestCreate(BaseModel):
    """Schema for creating a backtest"""
    strategy_id: int
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(default=10000.0)


class BacktestResponse(BaseModel):
    """Schema for backtest response"""
    id: int
    strategy_id: int
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    total_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    win_rate: Optional[float]
    total_trades: Optional[int]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Schema for search request"""
    query: str = Field(default="trading strategies")
    max_results: int = Field(default=20, ge=1, le=100)


class SearchResponse(BaseModel):
    """Schema for search response"""
    query: str
    results: List[Dict[str, Any]]
    total: int

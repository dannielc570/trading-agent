"""Tests for database module"""
import pytest
from datetime import datetime

from src.database import init_db, Strategy, Backtest, get_db_context


def test_database_initialization():
    """Test database initialization"""
    init_db()  # Should not raise any errors


def test_create_strategy():
    """Test creating a strategy"""
    with get_db_context() as db:
        strategy = Strategy(
            name="Test Strategy",
            description="A test strategy",
            category="test",
            status="discovered"
        )
        db.add(strategy)
        db.commit()
        
        # Query back
        retrieved = db.query(Strategy).filter(Strategy.name == "Test Strategy").first()
        assert retrieved is not None
        assert retrieved.name == "Test Strategy"
        assert retrieved.category == "test"


def test_create_backtest():
    """Test creating a backtest"""
    with get_db_context() as db:
        # Create strategy first
        strategy = Strategy(
            name="Test Strategy for Backtest",
            description="Test",
            status="discovered"
        )
        db.add(strategy)
        db.flush()
        
        # Create backtest
        backtest = Backtest(
            strategy_id=strategy.id,
            symbol="TEST",
            timeframe="1d",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 12, 31),
            initial_capital=10000,
            status="pending"
        )
        db.add(backtest)
        db.commit()
        
        # Query back
        retrieved = db.query(Backtest).filter(Backtest.symbol == "TEST").first()
        assert retrieved is not None
        assert retrieved.symbol == "TEST"
        assert retrieved.strategy_id == strategy.id

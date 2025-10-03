"""ML models for market prediction and regime detection"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from loguru import logger

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MarketRegimeDetector:
    """Detect market regimes using ML"""
    
    def __init__(self):
        """Initialize market regime detector"""
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn not available")
            return
        
        # Lazy initialization to avoid sklearn import hang
        self._model = None
        self._scaler = None
        self.is_trained = False
    
    @property
    def model(self):
        if self._model is None and SKLEARN_AVAILABLE:
            self._model = RandomForestClassifier(n_estimators=100, random_state=42)
        return self._model
    
    @property
    def scaler(self):
        if self._scaler is None and SKLEARN_AVAILABLE:
            self._scaler = StandardScaler()
        return self._scaler
    
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features for regime detection
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            DataFrame with features
        """
        df = data.copy()
        
        # Returns
        df['returns'] = df['close'].pct_change()
        df['returns_5'] = df['close'].pct_change(5)
        df['returns_20'] = df['close'].pct_change(20)
        
        # Volatility
        df['volatility'] = df['returns'].rolling(20).std()
        df['volatility_50'] = df['returns'].rolling(50).std()
        
        # Volume
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Trend
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['trend'] = (df['sma_20'] - df['sma_50']) / df['sma_50']
        
        # Range
        df['range'] = (df['high'] - df['low']) / df['close']
        df['avg_range'] = df['range'].rolling(20).mean()
        
        # Drop NaN
        df = df.dropna()
        
        feature_cols = [
            'returns', 'returns_5', 'returns_20',
            'volatility', 'volatility_50',
            'volume_ratio', 'trend', 'range', 'avg_range'
        ]
        
        return df[feature_cols]
    
    def create_labels(self, data: pd.DataFrame, forward_periods: int = 5) -> pd.Series:
        """
        Create regime labels
        
        Regimes:
        0 = Bearish/Downtrend
        1 = Sideways/Range-bound
        2 = Bullish/Uptrend
        
        Args:
            data: OHLCV DataFrame
            forward_periods: Periods to look forward for labeling
            
        Returns:
            Series with regime labels
        """
        future_returns = data['close'].pct_change(forward_periods).shift(-forward_periods)
        
        labels = pd.Series(1, index=data.index)  # Default: sideways
        labels[future_returns > 0.02] = 2  # Bullish
        labels[future_returns < -0.02] = 0  # Bearish
        
        return labels
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train regime detection model
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Training results
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn not available'}
        
        try:
            logger.info("Training market regime detector")
            
            # Extract features and labels
            features = self.extract_features(data)
            labels = self.create_labels(data)
            
            # Align features and labels
            common_index = features.index.intersection(labels.index)
            X = features.loc[common_index]
            y = labels.loc[common_index]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            self.is_trained = True
            
            results = {
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score),
                'n_samples': len(X),
                'status': 'success'
            }
            
            logger.info(f"Training complete. Test accuracy: {test_score:.4f}")
            return results
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def predict(self, data: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Predict market regime
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Array of regime predictions
        """
        if not self.is_trained:
            logger.error("Model not trained")
            return None
        
        try:
            features = self.extract_features(data)
            features_scaled = self.scaler.transform(features)
            predictions = self.model.predict(features_scaled)
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def get_regime_name(self, regime: int) -> str:
        """Get human-readable regime name"""
        regime_names = {
            0: "Bearish",
            1: "Sideways",
            2: "Bullish"
        }
        return regime_names.get(regime, "Unknown")

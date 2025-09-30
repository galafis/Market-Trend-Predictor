#!/usr/bin/env python3
"""
Unit tests for Market Trend Predictor
Tests basic functionality of prediction models and data processing.
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import market_predictor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market_predictor import MarketTrendPredictor


class TestMarketTrendPredictor:
    """Test suite for MarketTrendPredictor class."""
    
    @pytest.fixture
    def predictor(self):
        """Create a MarketTrendPredictor instance for testing."""
        return MarketTrendPredictor()
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample market data for testing."""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 2)
        data = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        return data
    
    def test_predictor_initialization(self, predictor):
        """Test that predictor initializes correctly."""
        assert predictor is not None
        assert hasattr(predictor, 'models')
        assert hasattr(predictor, 'scalers')
        assert hasattr(predictor, 'data')
        assert hasattr(predictor, 'predictions')
        assert isinstance(predictor.models, dict)
        assert isinstance(predictor.scalers, dict)
        assert isinstance(predictor.data, dict)
    
    def test_generate_synthetic_data(self, predictor):
        """Test synthetic data generation."""
        symbol = 'TEST'
        data = predictor.generate_synthetic_data(symbol, days=100)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 100
        assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
        assert all(data['Close'] > 0)  # Prices should be positive
        assert all(data['High'] >= data['Low'])  # High should be >= Low
    
    def test_prepare_lstm_data(self, predictor, sample_data):
        """Test LSTM data preparation."""
        lookback = 60
        X, y, scaler = predictor.prepare_lstm_data(sample_data, lookback_window=lookback)
        
        assert X is not None
        assert y is not None
        assert scaler is not None
        assert X.shape[1] == lookback  # Lookback window size
        assert X.shape[2] == 1  # Single feature (Close price)
        assert len(X) == len(y)
        assert len(X) == len(sample_data) - lookback
    
    def test_build_lstm_model(self, predictor):
        """Test LSTM model building."""
        input_shape = (60, 1)
        model = predictor.build_lstm_model(input_shape)
        
        assert model is not None
        assert len(model.layers) > 0
        assert model.input_shape == (None, 60, 1)
        assert model.output_shape == (None, 1)
    
    def test_calculate_technical_indicators(self, predictor, sample_data):
        """Test technical indicators calculation."""
        indicators_df = predictor.calculate_technical_indicators(sample_data)
        
        assert 'MA_5' in indicators_df.columns
        assert 'MA_10' in indicators_df.columns
        assert 'MA_20' in indicators_df.columns
        assert 'MA_50' in indicators_df.columns
        assert 'RSI' in indicators_df.columns
        assert 'MACD' in indicators_df.columns
        assert 'BB_Upper' in indicators_df.columns
        assert 'BB_Lower' in indicators_df.columns
        
        # Check RSI bounds (should be between 0 and 100)
        rsi_values = indicators_df['RSI'].dropna()
        assert all(rsi_values >= 0)
        assert all(rsi_values <= 100)
    
    def test_predict_future_prices_structure(self, predictor):
        """Test that predict_future_prices returns correct structure."""
        # Generate synthetic data and set it
        symbol = 'TEST'
        predictor.data[symbol] = predictor.generate_synthetic_data(symbol, days=200)
        
        # Train a simple model
        predictor.train_lstm_model(symbol, epochs=2, batch_size=32)
        
        # Test prediction
        days_ahead = 10
        predictions = predictor.predict_future_prices(symbol, days_ahead=days_ahead)
        
        assert isinstance(predictions, pd.DataFrame)
        assert len(predictions) == days_ahead
        assert 'Date' in predictions.columns
        assert 'Predicted_Price' in predictions.columns
        assert all(predictions['Predicted_Price'] > 0)  # Prices should be positive
    
    def test_generate_trading_signals(self, predictor, sample_data):
        """Test trading signal generation."""
        symbol = 'TEST'
        predictor.data[symbol] = sample_data
        
        signals_df = predictor.generate_trading_signals(symbol)
        
        assert 'Signal' in signals_df.columns
        unique_signals = signals_df['Signal'].unique()
        assert all(signal in ['BUY', 'SELL', 'HOLD'] for signal in unique_signals)
    
    def test_train_lstm_model_returns_results(self, predictor):
        """Test that LSTM training returns expected results structure."""
        symbol = 'TEST'
        predictor.data[symbol] = predictor.generate_synthetic_data(symbol, days=200)
        
        results = predictor.train_lstm_model(symbol, epochs=2, batch_size=32)
        
        assert 'model' in results
        assert 'scaler' in results
        assert 'train_rmse' in results
        assert 'test_rmse' in results
        assert 'train_mae' in results
        assert 'test_mae' in results
        assert results['train_rmse'] > 0
        assert results['test_rmse'] > 0
    
    def test_data_persistence_after_fetch(self, predictor):
        """Test that data persists in predictor after generation."""
        symbol = 'TEST'
        data = predictor.generate_synthetic_data(symbol, days=100)
        predictor.data[symbol] = data
        
        assert symbol in predictor.data
        assert len(predictor.data[symbol]) == 100
        assert predictor.data[symbol].equals(data)


class TestDataValidation:
    """Test suite for data validation and edge cases."""
    
    def test_synthetic_data_ohlc_consistency(self):
        """Test that synthetic data maintains OHLC consistency."""
        predictor = MarketTrendPredictor()
        data = predictor.generate_synthetic_data('TEST', days=50)
        
        for idx in range(len(data)):
            row = data.iloc[idx]
            assert row['High'] >= row['Open'], f"High < Open at index {idx}"
            assert row['High'] >= row['Close'], f"High < Close at index {idx}"
            assert row['Low'] <= row['Open'], f"Low > Open at index {idx}"
            assert row['Low'] <= row['Close'], f"Low > Close at index {idx}"
    
    def test_empty_data_handling(self):
        """Test handling of empty or missing data."""
        predictor = MarketTrendPredictor()
        
        with pytest.raises(ValueError):
            predictor.train_lstm_model('NONEXISTENT')
        
        with pytest.raises(ValueError):
            predictor.generate_trading_signals('NONEXISTENT')
    
    def test_prediction_without_training(self):
        """Test that prediction fails without trained model."""
        predictor = MarketTrendPredictor()
        
        with pytest.raises(ValueError):
            predictor.predict_future_prices('UNTRAINED')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

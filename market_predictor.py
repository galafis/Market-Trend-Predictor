#!/usr/bin/env python3
"""
Market Trend Predictor
LSTM-based stock price predictor with technical indicators (RSI, MACD, Bollinger Bands).
Fetches data via yfinance, trains an LSTM neural network, and predicts future prices.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import yfinance as yf
from datetime import datetime, timedelta

class MarketTrendPredictor:
    def __init__(self):
        """Initialize the market trend predictor."""
        self.models = {}
        self.scalers = {}
        self.data = {}
        self.predictions = {}
        
    def fetch_market_data(self, symbols=['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'], period='2y'):
        """Fetch real market data from Yahoo Finance."""
        market_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                market_data[symbol] = data
                print(f"Fetched data for {symbol}: {len(data)} records")
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                # Generate synthetic data as fallback
                market_data[symbol] = self.generate_synthetic_data(symbol)
        
        self.data = market_data
        return market_data
    
    def generate_synthetic_data(self, symbol, days=730):
        """Generate synthetic market data for testing."""
        np.random.seed(hash(symbol) % 2**32)
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             end=datetime.now(), freq='D')
        
        # Generate realistic price movements
        initial_price = np.random.uniform(50, 500)
        returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
        
        prices = [initial_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 1))  # Ensure positive prices
        
        # Generate OHLCV data
        data = pd.DataFrame({
            'Open': [p * np.random.uniform(0.98, 1.02) for p in prices],
            'High': [p * np.random.uniform(1.00, 1.05) for p in prices],
            'Low': [p * np.random.uniform(0.95, 1.00) for p in prices],
            'Close': prices,
            'Volume': [np.random.randint(1000000, 10000000) for _ in prices]
        }, index=dates)
        
        # Ensure OHLC consistency
        for i in range(len(data)):
            high = max(data.iloc[i]['Open'], data.iloc[i]['Close'])
            low = min(data.iloc[i]['Open'], data.iloc[i]['Close'])
            data.iloc[i, data.columns.get_loc('High')] = max(data.iloc[i]['High'], high)
            data.iloc[i, data.columns.get_loc('Low')] = min(data.iloc[i]['Low'], low)
        
        return data
    
    def prepare_lstm_data(self, data, lookback_window=60, target_column='Close'):
        """Prepare data for LSTM model."""
        # Scale the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data[[target_column]])
        
        # Create sequences
        X, y = [], []
        for i in range(lookback_window, len(scaled_data)):
            X.append(scaled_data[i-lookback_window:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y, scaler
    
    def build_lstm_model(self, input_shape):
        """Build LSTM neural network model."""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train_lstm_model(self, symbol, epochs=50, batch_size=32):
        """Train LSTM model for a specific symbol."""
        if symbol not in self.data:
            raise ValueError(f"No data available for symbol {symbol}")
        
        data = self.data[symbol]
        X, y, scaler = self.prepare_lstm_data(data)
        
        # Split data
        split_index = int(len(X) * 0.8)
        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        
        # Build and train model
        model = self.build_lstm_model((X_train.shape[1], 1))
        history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, 
                           validation_data=(X_test, y_test), verbose=0)
        
        # Store model and scaler
        self.models[f'{symbol}_lstm'] = model
        self.scalers[f'{symbol}_lstm'] = scaler
        
        # Make predictions
        train_predictions = model.predict(X_train)
        test_predictions = model.predict(X_test)
        
        # Inverse transform predictions
        train_predictions = scaler.inverse_transform(train_predictions)
        test_predictions = scaler.inverse_transform(test_predictions)
        y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
        
        # Calculate metrics
        train_rmse = np.sqrt(mean_squared_error(y_train_actual, train_predictions))
        test_rmse = np.sqrt(mean_squared_error(y_test_actual, test_predictions))
        train_mae = mean_absolute_error(y_train_actual, train_predictions)
        test_mae = mean_absolute_error(y_test_actual, test_predictions)
        
        results = {
            'model': model,
            'scaler': scaler,
            'history': history.history,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_predictions': train_predictions,
            'test_predictions': test_predictions,
            'y_train_actual': y_train_actual,
            'y_test_actual': y_test_actual
        }
        
        return results
    
    def predict_future_prices(self, symbol, days_ahead=30, lookback_window=60):
        """Predict future prices for a given symbol."""
        if f'{symbol}_lstm' not in self.models:
            raise ValueError(f"No trained model available for symbol {symbol}")
        
        model = self.models[f'{symbol}_lstm']
        scaler = self.scalers[f'{symbol}_lstm']
        data = self.data[symbol]
        
        # Prepare last sequence
        last_sequence = data['Close'].values[-lookback_window:]
        last_sequence_scaled = scaler.transform(last_sequence.reshape(-1, 1))
        
        predictions = []
        current_sequence = last_sequence_scaled[-lookback_window:].reshape(1, lookback_window, 1)
        
        for _ in range(days_ahead):
            next_pred = model.predict(current_sequence, verbose=0)
            predictions.append(next_pred[0, 0])
            
            # Update sequence for next prediction
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, 0] = next_pred[0, 0]
        
        # Inverse transform predictions
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = scaler.inverse_transform(predictions)
        
        # Create future dates
        last_date = data.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                   periods=days_ahead, freq='D')
        
        future_predictions = pd.DataFrame({
            'Date': future_dates,
            'Predicted_Price': predictions.flatten()
        })
        
        return future_predictions
    
    def calculate_technical_indicators(self, data):
        """Calculate technical indicators for enhanced predictions."""
        df = data.copy()
        
        # Moving averages
        df['MA_5'] = df['Close'].rolling(window=5).mean()
        df['MA_10'] = df['Close'].rolling(window=10).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential moving averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Volume indicators
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        return df
    
    def generate_trading_signals(self, symbol):
        """Generate trading signals based on technical analysis."""
        if symbol not in self.data:
            raise ValueError(f"No data available for symbol {symbol}")
        
        data = self.calculate_technical_indicators(self.data[symbol])
        
        signals = []
        
        for i in range(len(data)):
            if i < 50:  # Need enough data for indicators
                signals.append('HOLD')
                continue
            
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            buy_signals = 0
            sell_signals = 0
            
            # Moving average crossover
            if current['MA_5'] > current['MA_20'] and previous['MA_5'] <= previous['MA_20']:
                buy_signals += 1
            elif current['MA_5'] < current['MA_20'] and previous['MA_5'] >= previous['MA_20']:
                sell_signals += 1
            
            # MACD crossover
            if current['MACD'] > current['MACD_Signal'] and previous['MACD'] <= previous['MACD_Signal']:
                buy_signals += 1
            elif current['MACD'] < current['MACD_Signal'] and previous['MACD'] >= previous['MACD_Signal']:
                sell_signals += 1
            
            # RSI levels
            if current['RSI'] < 30:  # Oversold
                buy_signals += 1
            elif current['RSI'] > 70:  # Overbought
                sell_signals += 1
            
            # Bollinger Bands
            if current['Close'] < current['BB_Lower']:  # Below lower band
                buy_signals += 1
            elif current['Close'] > current['BB_Upper']:  # Above upper band
                sell_signals += 1
            
            # Generate final signal
            if buy_signals >= 2:
                signals.append('BUY')
            elif sell_signals >= 2:
                signals.append('SELL')
            else:
                signals.append('HOLD')
        
        data['Signal'] = signals
        return data
    
    def create_market_dashboard(self, symbols):
        """Create comprehensive market analysis dashboard."""
        dashboard_data = {}
        
        for symbol in symbols:
            if symbol not in self.data:
                continue
            
            # Train model and get predictions
            try:
                lstm_results = self.train_lstm_model(symbol, epochs=20)  # Reduced epochs for speed
                future_predictions = self.predict_future_prices(symbol, days_ahead=30)
                signals_data = self.generate_trading_signals(symbol)
                
                # Calculate performance metrics
                current_price = self.data[symbol]['Close'].iloc[-1]
                price_change_1d = ((current_price - self.data[symbol]['Close'].iloc[-2]) / 
                                 self.data[symbol]['Close'].iloc[-2] * 100)
                price_change_7d = ((current_price - self.data[symbol]['Close'].iloc[-7]) / 
                                 self.data[symbol]['Close'].iloc[-7] * 100)
                
                # Get latest technical indicators
                latest_indicators = signals_data.iloc[-1]
                
                dashboard_data[symbol] = {
                    'current_price': round(current_price, 2),
                    'price_change_1d': round(price_change_1d, 2),
                    'price_change_7d': round(price_change_7d, 2),
                    'predicted_price_30d': round(future_predictions['Predicted_Price'].iloc[-1], 2),
                    'model_accuracy': {
                        'train_rmse': round(lstm_results['train_rmse'], 2),
                        'test_rmse': round(lstm_results['test_rmse'], 2)
                    },
                    'technical_indicators': {
                        'RSI': round(latest_indicators['RSI'], 2),
                        'MACD': round(latest_indicators['MACD'], 4),
                        'Signal': latest_indicators['Signal']
                    },
                    'future_predictions': future_predictions.to_dict('records')
                }
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                dashboard_data[symbol] = {'error': str(e)}
        
        return dashboard_data
    
    def run_complete_analysis(self, symbols=['AAPL', 'GOOGL', 'MSFT']):
        """Run complete market trend analysis."""
        print("Starting Market Trend Prediction Analysis...")
        
        # Fetch market data
        print("1. Fetching market data...")
        self.fetch_market_data(symbols)
        
        # Create dashboard
        print("2. Training models and generating predictions...")
        dashboard = self.create_market_dashboard(symbols)
        
        print("3. Analysis completed!")
        
        return dashboard

def main():
    """Main function to run market trend prediction."""
    predictor = MarketTrendPredictor()
    
    # Run analysis
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    results = predictor.run_complete_analysis(symbols)
    
    # Print results
    print("\n" + "="*70)
    print("MARKET TREND PREDICTION DASHBOARD")
    print("="*70)
    
    for symbol, data in results.items():
        if 'error' in data:
            print(f"\n{symbol}: Error - {data['error']}")
            continue
        
        print(f"\n{symbol}:")
        print(f"  Current Price: ${data['current_price']}")
        print(f"  1-Day Change: {data['price_change_1d']:+.2f}%")
        print(f"  7-Day Change: {data['price_change_7d']:+.2f}%")
        print(f"  30-Day Prediction: ${data['predicted_price_30d']}")
        print(f"  Model RMSE: {data['model_accuracy']['test_rmse']}")
        print(f"  RSI: {data['technical_indicators']['RSI']}")
        print(f"  Trading Signal: {data['technical_indicators']['Signal']}")

if __name__ == "__main__":
    main()


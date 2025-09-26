#!/usr/bin/env python3
"""
Configuration module for Market Trend Predictor
Contains all configuration constants and settings
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# API Configuration
API_CONFIG = {
    "ALPHA_VANTAGE_API_KEY": os.getenv("ALPHA_VANTAGE_API_KEY", ""),
    "YAHOO_FINANCE_ENABLED": True,
    "RATE_LIMIT_DELAY": 12,  # seconds between API calls
    "MAX_RETRIES": 3
}

# Model Configuration
MODEL_CONFIG = {
    "SEQUENCE_LENGTH": 60,  # Number of days to look back
    "PREDICTION_HORIZON": 5,  # Days to predict ahead
    "TRAIN_SPLIT": 0.8,  # Training data percentage
    "VALIDATION_SPLIT": 0.1,  # Validation data percentage
    "BATCH_SIZE": 32,
    "EPOCHS": 100,
    "LEARNING_RATE": 0.001,
    "DROPOUT_RATE": 0.2
}

# Default symbols to analyze
DEFAULT_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
    "META", "NVDA", "NFLX", "AMD", "INTC"
]

# Technical indicators configuration
TECHNICAL_INDICATORS = {
    "SMA_PERIODS": [10, 20, 50, 200],
    "EMA_PERIODS": [12, 26],
    "RSI_PERIOD": 14,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "BOLLINGER_PERIOD": 20,
    "BOLLINGER_STD": 2
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_handler": True,
    "console_handler": True,
    "log_file": LOGS_DIR / "market_predictor.log"
}

# Web interface configuration
WEB_CONFIG = {
    "HOST": "127.0.0.1",
    "PORT": 8000,
    "DEBUG": True,
    "AUTO_RELOAD": True
}

# Data processing configuration
DATA_CONFIG = {
    "MIN_DATA_POINTS": 252,  # Minimum trading days (1 year)
    "OUTLIER_THRESHOLD": 3,  # Standard deviations for outlier detection
    "MISSING_DATA_THRESHOLD": 0.1,  # Maximum percentage of missing data allowed
    "SCALING_METHOD": "MinMaxScaler",  # Options: MinMaxScaler, StandardScaler
    "FEATURE_SELECTION": True
}

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

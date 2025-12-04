"""
Configuration of projet
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Créer les dossiers si nécessaire
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Assets disponibles
DEFAULT_ASSETS = {
    "ENGIE": "ENGI.PA",
    "EUR/USD": "EURUSD=X",
    "Gold": "GC=F",
    "CAC 40": "^FCHI",
    "Bitcoin": "BTC-USD",
    "Total": "TTE.PA",
    "LVMH": "MC.PA"
}

# Data settings
REFRESH_INTERVAL = 300  # 5 minutes en secondes
LOOKBACK_PERIODS = {
    "1d": "1 Jour",
    "5d": "5 Jours", 
    "1mo": "1 Mois",
    "3mo": "3 Mois",
    "1y": "1 An"
}

# Strategy parameters
STRATEGY_DEFAULTS = {
    "momentum": {
        "short_window": 20,
        "long_window": 50
    },
    "rsi": {
        "period": 14,
        "oversold": 30,
        "overbought": 70
    },
    "mean_reversion": {
        "window": 20,
        "num_std": 2
    }
}

# Report settings
REPORT_TIME = "20:00"
REPORT_TIMEZONE = "Europe/Paris"
REPORT_FORMAT = "%Y-%m-%d_%H%M%S"

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# API Settings
FOREX_API_URL = "https://www.freeforexapi.com/api/live"
REQUEST_TIMEOUT = 5

# Streamlit settings
STREAMLIT_PORT = 8501
STREAMLIT_ADDRESS = "0.0.0.0"

# Initial capital
DEFAULT_INITIAL_CAPITAL = 10000

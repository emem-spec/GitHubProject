import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Default assets
DEFAULT_ASSETS = {
    "ENGIE": "ENGI.PA",
    "EUR/USD": "EURUSD=X",
    "Gold": "GC=F",
    "CAC 40": "^FCHI",
    "Bitcoin": "BTC-USD"
}

# Data settings
REFRESH_INTERVAL = 300  # 5 minutes in seconds
LOOKBACK_DAYS = 365

# Strategy parameters defaults
DEFAULT_MOMENTUM_WINDOW = 20
DEFAULT_REBALANCE_FREQ = "1D"

# Report settings
REPORT_TIME = "20:00"  # 8 PM
REPORT_TIMEZONE = "Europe/Paris"

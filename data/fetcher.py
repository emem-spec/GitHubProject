import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches real-time financial data from Yahoo Finance"""
    
    def __init__(self, ticker, period="1y", interval="1d"):
        """
        Initialize data fetcher
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'ENGI.PA')
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        """
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.stock = yf.Ticker(ticker)
        
    def get_historical_data(self):
        """Fetch historical data"""
        try:
            df = self.stock.history(period=self.period, interval=self.interval)
            if df.empty:
                logger.error(f"No data retrieved for {self.ticker}")
                return None
            
            df.index = pd.to_datetime(df.index)
            logger.info(f"Retrieved {len(df)} data points for {self.ticker}")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {self.ticker}: {str(e)}")
            return None
    
    def get_current_price(self):
        """Get current/latest price"""
        try:
            data = self.stock.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error fetching current price: {str(e)}")
            return None
    
    def get_info(self):
        """Get stock information"""
        try:
            return self.stock.info
        except Exception as e:
            logger.error(f"Error fetching info: {str(e)}")
            return {}
    
    def get_intraday_data(self, days=5):
        """Get intraday data for recent days"""
        try:
            df = self.stock.history(period=f"{days}d", interval="5m")
            if df.empty:
                logger.warning(f"No intraday data for {self.ticker}")
                return None
            return df
        except Exception as e:
            logger.error(f"Error fetching intraday data: {str(e)}")
            return None


def fetch_multiple_tickers(tickers, period="1y", interval="1d"):
    """
    Fetch data for multiple tickers
    
    Args:
        tickers (list): List of ticker symbols
        period (str): Data period
        interval (str): Data interval
    
    Returns:
        dict: Dictionary with ticker as key and dataframe as value
    """
    data_dict = {}
    for ticker in tickers:
        fetcher = DataFetcher(ticker, period, interval)
        df = fetcher.get_historical_data()
        if df is not None:
            data_dict[ticker] = df
    
    return data_dict

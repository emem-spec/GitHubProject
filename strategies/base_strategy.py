import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, data, initial_capital=10000):
        """
        Initialize strategy
        
        Args:
            data (pd.DataFrame): OHLCV data
            initial_capital (float): Initial capital for backtesting
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.positions = None
        self.portfolio_value = None
        
    @abstractmethod
    def generate_signals(self):
        """Generate trading signals (must be implemented by subclasses)"""
        pass
    
    def backtest(self):
        """
        Run backtest on the strategy
        
        Returns:
            pd.DataFrame: DataFrame with positions and portfolio values
        """
        # Generate signals
        self.generate_signals()
        
        # Calculate returns
        self.data['Returns'] = self.data['Close'].pct_change()
        
        # Calculate strategy returns
        self.data['Strategy_Returns'] = self.data['Position'].shift(1) * self.data['Returns']
        
        # Calculate cumulative returns
        self.data['Cumulative_Returns'] = (1 + self.data['Returns']).cumprod()
        self.data['Cumulative_Strategy_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
        
        # Calculate portfolio value
        self.data['Portfolio_Value'] = self.initial_capital * self.data['Cumulative_Strategy_Returns']
        
        return self.data
    
    def get_positions(self):
        """Get position series"""
        return self.data['Position'] if 'Position' in self.data.columns else None
    
    def get_portfolio_value(self):
        """Get portfolio value series"""
        return self.data['Portfolio_Value'] if 'Portfolio_Value' in self.data.columns else None

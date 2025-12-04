from strategies.base_strategy import BaseStrategy
import pandas as pd
import numpy as np


class MomentumStrategy(BaseStrategy):
    """
    Momentum strategy based on moving averages
    Buy when short MA > long MA, sell otherwise
    """
    
    def __init__(self, data, initial_capital=10000, short_window=20, long_window=50):
        """
        Initialize Momentum strategy
        
        Args:
            data (pd.DataFrame): OHLCV data
            initial_capital (float): Initial capital
            short_window (int): Short moving average window
            long_window (int): Long moving average window
        """
        super().__init__(data, initial_capital)
        self.short_window = short_window
        self.long_window = long_window
        self.name = f"Momentum ({short_window}/{long_window})"
    
    def generate_signals(self):
        """
        Generate signals based on moving average crossover
        Position = 1 when short MA > long MA (bullish)
        Position = 0 when short MA < long MA (bearish)
        """
        # Calculate moving averages
        self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_window).mean()
        self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_window).mean()
        
        # Generate signals
        self.data['Position'] = 0
        self.data.loc[self.data['SMA_Short'] > self.data['SMA_Long'], 'Position'] = 1
        
        # Forward fill to maintain position until signal changes
        self.data['Position'] = self.data['Position'].fillna(method='ffill').fillna(0)
        
        return self.data


class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) mean reversion strategy
    Buy when RSI < oversold threshold, sell when RSI > overbought threshold
    """
    
    def __init__(self, data, initial_capital=10000, period=14, oversold=30, overbought=70):
        """
        Initialize RSI strategy
        
        Args:
            data (pd.DataFrame): OHLCV data
            initial_capital (float): Initial capital
            period (int): RSI calculation period
            oversold (float): Oversold threshold
            overbought (float): Overbought threshold
        """
        super().__init__(data, initial_capital)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.name = f"RSI ({period})"
    
    def calculate_rsi(self):
        """Calculate RSI indicator"""
        delta = self.data['Close'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self):
        """
        Generate signals based on RSI
        Buy when RSI < oversold, sell when RSI > overbought
        """
        # Calculate RSI
        self.data['RSI'] = self.calculate_rsi()
        
        # Generate signals
        self.data['Position'] = 0
        
        # Buy signal: RSI crosses above oversold
        self.data.loc[self.data['RSI'] < self.oversold, 'Position'] = 1
        
        # Sell signal: RSI crosses above overbought
        self.data.loc[self.data['RSI'] > self.overbought, 'Position'] = 0
        
        # Forward fill positions
        self.data['Position'] = self.data['Position'].replace(0, np.nan).fillna(method='ffill').fillna(0)
        
        return self.data

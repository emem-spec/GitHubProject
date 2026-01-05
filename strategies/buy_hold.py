from strategies.base_strategy import BaseStrategy
import pandas as pd


class BuyHoldStrategy(BaseStrategy):
    """
    Simple Buy and Hold strategy
    Buys at the beginning and holds until the end
    """
    
    def __init__(self, data, initial_capital=10000):
        """
        Initialize Buy and Hold strategy
        
        Args:
            data (pd.DataFrame): OHLCV data
            initial_capital (float): Initial capital
        """
        super().__init__(data, initial_capital)
        self.name = "Buy & Hold"
    
    def generate_signals(self):
        """
        Generate signals: always hold (position = 1)
        """
        # Always in the market (position = 1)
        self.data['Position'] = 1
        
        return self.data

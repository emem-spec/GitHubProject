"""
Moteur de backtesting pour les stratégies
"""
import pandas as pd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Backtester:
    """
    Moteur de backtesting unifié pour toutes les stratégies
    """
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 10000):
        """
        Initialize backtester
        
        Args:
            data: OHLCV DataFrame
            initial_capital: Starting capital
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.results = None
        
    def run(self, strategy) -> pd.DataFrame:
        """
        Run backtest for a given strategy
        
        Args:
            strategy: Strategy object with generate_signals method
        
        Returns:
            DataFrame with backtest results
        """
        logger.info(f"Running backtest for {strategy.name}")
        
        # Generate signals
        signals_data = strategy.generate_signals()
        self.data = signals_data.copy()
        
        # Calculate returns
        self.data['Returns'] = self.data['Close'].pct_change()
        
        # Calculate strategy returns
        # Position is shifted by 1 to avoid lookahead bias
        self.data['Strategy_Returns'] = self.data['Position'].shift(1) * self.data['Returns']
        
        # Calculate cumulative returns
        self.data['Cumulative_Returns'] = (1 + self.data['Returns']).cumprod()
        self.data['Cumulative_Strategy_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
        
        # Calculate portfolio value
        self.data['Portfolio_Value'] = self.initial_capital * self.data['Cumulative_Strategy_Returns']
        self.data['Buy_Hold_Value'] = self.initial_capital * self.data['Cumulative_Returns']
        
        # Calculate drawdown
        self.data['Running_Max'] = self.data['Portfolio_Value'].expanding().max()
        self.data['Drawdown'] = (self.data['Portfolio_Value'] - self.data['Running_Max']) / self.data['Running_Max']
        
        self.results = self.data
        logger.info(f"Backtest completed: {len(self.data)} periods")
        
        return self.results
    
    def get_trades(self) -> pd.DataFrame:
        """
        Extract trade information from backtest results
        
        Returns:
            DataFrame with trade details
        """
        if self.results is None:
            logger.warning("No backtest results available")
            return pd.DataFrame()
        
        # Detect position changes
        position_changes = self.results['Position'].diff()
        
        trades = []
        entry_idx = None
        entry_price = None
        
        for idx, change in position_changes.items():
            if change == 1:  # Entry
                entry_idx = idx
                entry_price = self.results.loc[idx, 'Close']
            elif change == -1 and entry_idx is not None:  # Exit
                exit_price = self.results.loc[idx, 'Close']
                trade_return = (exit_price - entry_price) / entry_price
                
                trades.append({
                    'Entry Date': entry_idx,
                    'Exit Date': idx,
                    'Entry Price': entry_price,
                    'Exit Price': exit_price,
                    'Return (%)': trade_return * 100,
                    'Duration': (idx - entry_idx).days if hasattr(idx - entry_idx, 'days') else 1
                })
                
                entry_idx = None
                entry_price = None
        
        return pd.DataFrame(trades)
    
    def get_summary_stats(self) -> dict:
        """
        Get summary statistics of the backtest
        
        Returns:
            Dictionary with summary stats
        """
        if self.results is None:
            return {}
        
        strategy_returns = self.results['Strategy_Returns'].dropna()
        
        stats = {
            'Initial Capital': self.initial_capital,
            'Final Portfolio Value': self.results['Portfolio_Value'].iloc[-1],
            'Total Return': (self.results['Portfolio_Value'].iloc[-1] / self.initial_capital - 1) * 100,
            'Buy & Hold Return': (self.results['Buy_Hold_Value'].iloc[-1] / self.initial_capital - 1) * 100,
            'Number of Trades': len(self.get_trades()),
            'Win Rate': (strategy_returns > 0).sum() / len(strategy_returns) * 100 if len(strategy_returns) > 0 else 0,
            'Max Drawdown': self.results['Drawdown'].min() * 100,
            'Sharpe Ratio': self._calculate_sharpe(strategy_returns)
        }
        
        return stats
    
    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def plot_results(self):
        """
        Generate plotly figure of backtest results
        (To be used in Streamlit)
        """
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        if self.results is None:
            logger.warning("No results to plot")
            return None
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxis=True,
            vertical_spacing=0.1,
            subplot_titles=('Portfolio Value vs Buy & Hold', 'Drawdown'),
            row_heights=[0.7, 0.3]
        )
        
        # Portfolio value
        fig.add_trace(
            go.Scatter(
                x=self.results.index,
                y=self.results['Portfolio_Value'],
                name='Strategy',
                line=dict(color='green', width=2)
            ),
            row=1, col=1
        )
        
        # Buy & Hold
        fig.add_trace(
            go.Scatter(
                x=self.results.index,
                y=self.results['Buy_Hold_Value'],
                name='Buy & Hold',
                line=dict(color='blue', width=2, dash='dash')
            ),
            row=1, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(
                x=self.results.index,
                y=self.results['Drawdown'] * 100,
                name='Drawdown',
                fill='tozeroy',
                line=dict(color='red', width=1)
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Value (€)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
        
        fig.update_layout(
            height=700,
            hovermode='x unified',
            showlegend=True
        )
        
        return fig

import numpy as np
import pandas as pd


def calculate_returns(prices):
    """Calculate returns from price series"""
    return prices.pct_change().dropna()


def calculate_cumulative_returns(returns):
    """Calculate cumulative returns"""
    return (1 + returns).cumprod()


def calculate_sharpe_ratio(returns, risk_free_rate=0.02, periods_per_year=252):
    """
    Calculate Sharpe ratio
    
    Args:
        returns (pd.Series): Returns series
        risk_free_rate (float): Annual risk-free rate
        periods_per_year (int): Trading periods per year (252 for daily)
    
    Returns:
        float: Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / periods_per_year
    if excess_returns.std() == 0:
        return 0.0
    
    return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()


def calculate_max_drawdown(cumulative_returns):
    """
    Calculate maximum drawdown
    
    Args:
        cumulative_returns (pd.Series): Cumulative returns series
    
    Returns:
        float: Maximum drawdown as percentage
    """
    if len(cumulative_returns) == 0:
        return 0.0
    
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    return drawdown.min() * 100


def calculate_volatility(returns, periods_per_year=252):
    """
    Calculate annualized volatility
    
    Args:
        returns (pd.Series): Returns series
        periods_per_year (int): Trading periods per year
    
    Returns:
        float: Annualized volatility as percentage
    """
    if len(returns) == 0:
        return 0.0
    
    return returns.std() * np.sqrt(periods_per_year) * 100


def calculate_sortino_ratio(returns, risk_free_rate=0.02, periods_per_year=252):
    """
    Calculate Sortino ratio (uses downside deviation)
    
    Args:
        returns (pd.Series): Returns series
        risk_free_rate (float): Annual risk-free rate
        periods_per_year (int): Trading periods per year
    
    Returns:
        float: Sortino ratio
    """
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / periods_per_year
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    
    downside_std = downside_returns.std()
    return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std


def calculate_calmar_ratio(returns, cumulative_returns):
    """
    Calculate Calmar ratio (return / max drawdown)
    
    Args:
        returns (pd.Series): Returns series
        cumulative_returns (pd.Series): Cumulative returns series
    
    Returns:
        float: Calmar ratio
    """
    if len(returns) == 0:
        return 0.0
    
    annual_return = returns.mean() * 252 * 100
    max_dd = abs(calculate_max_drawdown(cumulative_returns))
    
    if max_dd == 0:
        return 0.0
    
    return annual_return / max_dd


def calculate_win_rate(returns):
    """Calculate percentage of positive returns"""
    if len(returns) == 0:
        return 0.0
    
    return (returns > 0).sum() / len(returns) * 100


def generate_performance_summary(prices, strategy_returns=None):
    """
    Generate complete performance summary
    
    Args:
        prices (pd.Series): Price series
        strategy_returns (pd.Series, optional): Strategy returns if different from buy-hold
    
    Returns:
        dict: Performance metrics
    """
    returns = calculate_returns(prices)
    cum_returns = calculate_cumulative_returns(returns)
    
    if strategy_returns is not None:
        returns = strategy_returns
        cum_returns = calculate_cumulative_returns(returns)
    
    metrics = {
        'Total Return (%)': (cum_returns.iloc[-1] - 1) * 100 if len(cum_returns) > 0 else 0,
        'Annualized Return (%)': returns.mean() * 252 * 100 if len(returns) > 0 else 0,
        'Volatility (%)': calculate_volatility(returns),
        'Sharpe Ratio': calculate_sharpe_ratio(returns),
        'Sortino Ratio': calculate_sortino_ratio(returns),
        'Max Drawdown (%)': calculate_max_drawdown(cum_returns),
        'Calmar Ratio': calculate_calmar_ratio(returns, cum_returns),
        'Win Rate (%)': calculate_win_rate(returns),
        'Best Day (%)': returns.max() * 100 if len(returns) > 0 else 0,
        'Worst Day (%)': returns.min() * 100 if len(returns) > 0 else 0
    }
    
    return metrics

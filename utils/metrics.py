"""
Fonctions de calcul des métriques de performance
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate returns from price series"""
    return prices.pct_change().dropna()


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """Calculate cumulative returns"""
    return (1 + returns).cumprod()


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, 
                          periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: Returns series
        risk_free_rate: Annual risk-free rate
        periods_per_year: Trading periods per year (252 for daily)
    
    Returns:
        Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / periods_per_year
    if excess_returns.std() == 0:
        return 0.0
    
    return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()


def calculate_max_drawdown(cumulative_returns: pd.Series) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        cumulative_returns: Cumulative returns series
    
    Returns:
        Maximum drawdown as percentage
    """
    if len(cumulative_returns) == 0:
        return 0.0
    
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    return drawdown.min() * 100


def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility
    
    Args:
        returns: Returns series
        periods_per_year: Trading periods per year
    
    Returns:
        Annualized volatility as percentage
    """
    if len(returns) == 0:
        return 0.0
    
    return returns.std() * np.sqrt(periods_per_year) * 100


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02, 
                           periods_per_year: int = 252) -> float:
    """
    Calculate Sortino ratio (uses downside deviation)
    
    Args:
        returns: Returns series
        risk_free_rate: Annual risk-free rate
        periods_per_year: Trading periods per year
    
    Returns:
        Sortino ratio
    """
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / periods_per_year
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    
    downside_std = downside_returns.std()
    return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std


def calculate_calmar_ratio(returns: pd.Series, cumulative_returns: pd.Series) -> float:
    """
    Calculate Calmar ratio (return / max drawdown)
    
    Args:
        returns: Returns series
        cumulative_returns: Cumulative returns series
    
    Returns:
        Calmar ratio
    """
    if len(returns) == 0:
        return 0.0
    
    annual_return = returns.mean() * 252 * 100
    max_dd = abs(calculate_max_drawdown(cumulative_returns))
    
    if max_dd == 0:
        return 0.0
    
    return annual_return / max_dd


def calculate_win_rate(returns: pd.Series) -> float:
    """Calculate percentage of positive returns"""
    if len(returns) == 0:
        return 0.0
    
    return (returns > 0).sum() / len(returns) * 100


def generate_performance_summary(prices: pd.Series, 
                                strategy_returns: Optional[pd.Series] = None) -> Dict:
    """
    Generate complete performance summary
    
    Args:
        prices: Price series
        strategy_returns: Strategy returns if different from buy-hold
    
    Returns:
        Dictionary with performance metrics
    """
    returns = calculate_returns(prices)
    cum_returns = calculate_cumulative_returns(returns)
    
    if strategy_returns is not None:
        returns = strategy_returns
        cum_returns = calculate_cumulative_returns(returns)
    
    metrics = {
        'Total Return (%)': round((cum_returns.iloc[-1] - 1) * 100, 2) if len(cum_returns) > 0 else 0,
        'Annualized Return (%)': round(returns.mean() * 252 * 100, 2) if len(returns) > 0 else 0,
        'Volatility (%)': round(calculate_volatility(returns), 2),
        'Sharpe Ratio': round(calculate_sharpe_ratio(returns), 2),
        'Sortino Ratio': round(calculate_sortino_ratio(returns), 2),
        'Max Drawdown (%)': round(calculate_max_drawdown(cum_returns), 2),
        'Calmar Ratio': round(calculate_calmar_ratio(returns, cum_returns), 2),
        'Win Rate (%)': round(calculate_win_rate(returns), 2),
        'Best Day (%)': round(returns.max() * 100, 2) if len(returns) > 0 else 0,
        'Worst Day (%)': round(returns.min() * 100, 2) if len(returns) > 0 else 0
    }
    
    return metrics


def format_metrics_for_display(metrics: Dict) -> Dict:
    """
    Format metrics for nice display
    
    Args:
        metrics: Raw metrics dictionary
    
    Returns:
        Formatted metrics dictionary
    """
    formatted = {}
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            if 'Ratio' in key:
                formatted[key] = f"{value:.2f}"
            elif '%' in key:
                formatted[key] = f"{value:+.2f}%"
            else:
                formatted[key] = f"{value:,.2f}"
        else:
            formatted[key] = str(value)
    
    return formatted

"""
Visualization Functions
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional


def create_price_strategy_chart(data: pd.DataFrame, 
                                asset_name: str = "Asset",
                                show_signals: bool = False) -> go.Figure:
    """
    Make a graph combining price and portfolio value
    
    Args:
        data: DataFrame with Close et Portfolio_Value
        asset_name: Name asset
        show_signals: Show buy/sell signals
    
    Returns:
        Figure Plotly
    """
    fig = go.Figure()
    
    # Asset price
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name=f'{asset_name} Price',
        line=dict(color='#1f77b4', width=2),
        yaxis='y1'
    ))
    
    # Portfolio value
    if 'Portfolio_Value' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Portfolio_Value'],
            name='Portfolio Value',
            line=dict(color='#2ca02c', width=2),
            yaxis='y2'
        ))
    
    # Buy & Hold for comparaison
    if 'Buy_Hold_Value' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Buy_Hold_Value'],
            name='Buy & Hold',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            yaxis='y2'
        ))
    
    # buy/sell signals
    if show_signals and 'Position' in data.columns:
        # Buy signals
        buy_signals = data[data['Position'].diff() == 1]
        if not buy_signals.empty:
            fig.add_trace(go.Scatter(
                x=buy_signals.index,
                y=buy_signals['Close'],
                mode='markers',
                name='Buy Signal',
                marker=dict(color='green', size=10, symbol='triangle-up'),
                yaxis='y1'
            ))
        
        # Sell signals
        sell_signals = data[data['Position'].diff() == -1]
        if not sell_signals.empty:
            fig.add_trace(go.Scatter(
                x=sell_signals.index,
                y=sell_signals['Close'],
                mode='markers',
                name='Sell Signal',
                marker=dict(color='red', size=10, symbol='triangle-down'),
                yaxis='y1'
            ))
    
    # Layout with double axis Y
    fig.update_layout(
        title=f'{asset_name} - Price vs Strategy Performance',
        xaxis_title='Date',
        yaxis=dict(
            title='Price (€)',
            side='left',
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis2=dict(
            title='Portfolio Value (€)',
            side='right',
            overlaying='y',
            showgrid=False
        ),
        hovermode='x unified',
        height=600,
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        template='plotly_white'
    )
    
    return fig


def create_drawdown_chart(data: pd.DataFrame) -> go.Figure:
    """
    Make a drawdown graph
    
    Args:
        data: DataFrame with Drawdown
    
    Returns:
        Figure Plotly
    """
    fig = go.Figure()
    
    if 'Drawdown' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Drawdown'] * 100,
            fill='tozeroy',
            name='Drawdown',
            line=dict(color='red', width=1),
            fillcolor='rgba(255,0,0,0.2)'
        ))
    
    fig.update_layout(
        title='Strategy Drawdown',
        xaxis_title='Date',
        yaxis_title='Drawdown (%)',
        hovermode='x unified',
        height=300,
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def create_returns_distribution(returns: pd.Series) -> go.Figure:
    """
    Histogramme distribution returns
    
    Args:
        returns: Series of returns
    
    Returns:
        Figure Plotly
    """
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=returns * 100,
        nbinsx=50,
        name='Returns',
        marker=dict(
            color='lightblue',
            line=dict(color='darkblue', width=1)
        )
    ))
    
    fig.update_layout(
        title='Returns Distribution',
        xaxis_title='Return (%)',
        yaxis_title='Frequency',
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def create_moving_averages_chart(data: pd.DataFrame) -> go.Figure:
    """
    Graph Moving Average
    
    Args:
        data: DataFrame avec colonnes Close, SMA_Short, SMA_Long
    
    Returns:
        Figure Plotly
    """
    fig = go.Figure()
    
    # Price
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Price',
        line=dict(color='black', width=2)
    ))
    
    # SMA short
    if 'SMA_Short' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA_Short'],
            name='Short MA',
            line=dict(color='blue', width=1.5)
        ))
    
    # SMA long
    if 'SMA_Long' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA_Long'],
            name='Long MA',
            line=dict(color='red', width=1.5)
        ))
    
    fig.update_layout(
        title='Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price (€)',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    return fig


def create_rsi_chart(data: pd.DataFrame) -> go.Figure:
    """
    Graph RSI
    
    Args:
        data: DataFrame with RSI
    
    Returns:
        Figure Plotly
    """
    if 'RSI' not in data.columns:
        return go.Figure()
    
    fig = go.Figure()
    
    # RSI line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['RSI'],
        name='RSI',
        line=dict(color='purple', width=2)
    ))
    
    # Overbought line (70)
    fig.add_hline(y=70, line_dash="dash", line_color="red", 
                  annotation_text="Overbought (70)")
    
    # Oversold line (30)
    fig.add_hline(y=30, line_dash="dash", line_color="green", 
                  annotation_text="Oversold (30)")
    
    fig.update_layout(
        title='Relative Strength Index (RSI)',
        xaxis_title='Date',
        yaxis_title='RSI',
        hovermode='x unified',
        height=300,
        yaxis=dict(range=[0, 100]),
        template='plotly_white'
    )
    
    return fig


def create_metrics_comparison_bar(metrics_dict: dict) -> go.Figure:
    """
    Metrics comparison barchart
    
    Args:
        metrics_dict: Dict avec nom de stratégie -> métriques
    
    Returns:
        Figure Plotly
    """
    strategies = list(metrics_dict.keys())
    
    # Extract metrics
    metric_names = ['Total Return (%)', 'Sharpe Ratio', 'Max Drawdown (%)']
    
    fig = go.Figure()
    
    for metric in metric_names:
        values = [metrics_dict[s].get(metric, 0) for s in strategies]
        fig.add_trace(go.Bar(
            name=metric,
            x=strategies,
            y=values
        ))
    
    fig.update_layout(
        title='Strategy Comparison',
        xaxis_title='Strategy',
        yaxis_title='Value',
        barmode='group',
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_rolling_sharpe_chart(returns: pd.Series, window: int = 126) -> go.Figure:
    """
    Rolling Sharpe graph
    Args:
        returns: Strategy Returns
        window: Rolling window 
    """
    # Calculate annualized rolling Sharpe
    # Formule : (average / std) * sqrt(252)
    rolling_sharpe = returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rolling_sharpe.index,
        y=rolling_sharpe,
        name=f'Rolling Sharpe ({window}d)',
        line=dict(color='#9467bd', width=2)
    ))
    
    # add a line of 0 (break-even vs risk-free)
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    
    # add a line of 1 (good threshold)
    fig.add_hline(y=1, line_dash="dot", line_color="green", opacity=0.5)

    fig.update_layout(
        title=f'Rolling Sharpe Ratio (Window: {window} days)',
        xaxis_title='Date',
        yaxis_title='Sharpe Ratio',
        hovermode='x unified',
        height=350,
        template='plotly_white'
    )
    return fig

"""
Fonctions de visualisation avec Plotly
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional


def create_price_strategy_chart(data: pd.DataFrame, 
                                asset_name: str = "Asset",
                                show_signals: bool = False) -> go.Figure:
    """
    Crée un graphique combinant prix et valeur du portfolio
    
    Args:
        data: DataFrame avec colonnes Close et Portfolio_Value
        asset_name: Nom de l'actif
        show_signals: Afficher les signaux d'achat/vente
    
    Returns:
        Figure Plotly
    """
    fig = go.Figure()
    
    # Prix de l'actif (axe Y gauche)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name=f'{asset_name} Price',
        line=dict(color='#1f77b4', width=2),
        yaxis='y1'
    ))
    
    # Valeur du portfolio (axe Y droit)
    if 'Portfolio_Value' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Portfolio_Value'],
            name='Portfolio Value',
            line=dict(color='#2ca02c', width=2),
            yaxis='y2'
        ))
    
    # Buy & Hold pour comparaison
    if 'Buy_Hold_Value' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Buy_Hold_Value'],
            name='Buy & Hold',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            yaxis='y2'
        ))
    
    # Signaux d'achat/vente
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
    
    # Layout avec double axe Y
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
    Crée un graphique du drawdown
    
    Args:
        data: DataFrame avec colonne Drawdown
    
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
    Crée un histogramme de la distribution des returns
    
    Args:
        returns: Series de returns
    
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
    Crée un graphique avec les moyennes mobiles
    
    Args:
        data: DataFrame avec colonnes Close, SMA_Short, SMA_Long
    
    Returns:
        Figure Plotly
    """
    fig = go.Figure()
    
    # Prix
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Price',
        line=dict(color='black', width=2)
    ))
    
    # SMA courte
    if 'SMA_Short' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA_Short'],
            name='Short MA',
            line=dict(color='blue', width=1.5)
        ))
    
    # SMA longue
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
    Crée un graphique du RSI
    
    Args:
        data: DataFrame avec colonne RSI
    
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
    Crée un graphique en barres comparant plusieurs métriques
    
    Args:
        metrics_dict: Dict avec nom de stratégie -> métriques
    
    Returns:
        Figure Plotly
    """
    strategies = list(metrics_dict.keys())
    
    # Extraire les métriques communes
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

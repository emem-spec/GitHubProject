"""
Module Quant A - Single Asset Analysis
Nom du fichier : quant_a_module.py
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import logging
import time # Importé pour le refresh

# Imports locaux
# Note : Assurez-vous que le dossier s'appelle bien 'analysis' et non 'utils'
from config.settings import *
from data.fetcher import DataFetcher
from strategies.buy_hold import BuyHoldStrategy
from strategies.momentum import MomentumStrategy, RSIStrategy
from utils.backtester import Backtester 
from utils.metrics import generate_performance_summary, format_metrics_for_display
from visualization.charts import (
    create_price_strategy_chart, 
    create_drawdown_chart,
    create_moving_averages_chart,
    create_rsi_chart,
    create_returns_distribution
)

# Configuration du logging
logger = logging.getLogger(__name__)

def run_quant_a():
    """
    Fonction principale qui contient toute la logique du module Quant A.
    Appelée par app.py.
    """
    
    # CSS personnalisé (Déplacé ici pour être chargé quand le module s'ouvre)
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
    </style>
    """, unsafe_allow_html=True)

    # Titre principal
    st.markdown('<p class="main-header">📊 Single Asset Quantitative Analysis</p>', 
                unsafe_allow_html=True)
    st.markdown("---")

    # === SIDEBAR - Configuration ===
    st.sidebar.header("⚙️ Configuration (Quant A)")

    # Sélection de l'actif
    asset_name = st.sidebar.selectbox(
        "Asset",
        options=list(DEFAULT_ASSETS.keys()),
        index=0,
        key="qa_asset_select" # Ajout de clés uniques pour éviter les conflits
    )
    ticker = DEFAULT_ASSETS[asset_name]

    # Période
    period = st.sidebar.selectbox(
        "Period",
        options=list(LOOKBACK_PERIODS.keys()),
        format_func=lambda x: LOOKBACK_PERIODS[x],
        index=2,  # Default: 1 mois
        key="qa_period"
    )

    # Intervalle
    interval_options = {
        "5 minutes": "5m",
        "15 minutes": "15m",
        "1 heure": "1h",
        "1 jour": "1d"
    }
    interval_label = st.sidebar.selectbox(
        "Interval",
        options=list(interval_options.keys()),
        index=3,  # Default: 1 jour
        key="qa_interval"
    )
    interval = interval_options[interval_label]

    st.sidebar.markdown("---")

    # Sélection de la stratégie
    st.sidebar.subheader("📈 Strategy Selection")
    strategy_name = st.sidebar.selectbox(
        "Trading Strategy",
        ["Buy & Hold", "Momentum", "RSI"],
        key="qa_strategy"
    )

    # Capital initial
    initial_capital = st.sidebar.number_input(
        "Initial Capital (€)",
        min_value=1000,
        max_value=1000000,
        value=DEFAULT_INITIAL_CAPITAL,
        step=1000,
        key="qa_capital"
    )

    # Paramètres de stratégie
    st.sidebar.subheader("🔧 Strategy Parameters")

    # Initialisation des variables par défaut pour éviter les erreurs d'undefined
    short_window, long_window = 20, 50
    rsi_period, oversold, overbought = 14, 30, 70

    if strategy_name == "Momentum":
        short_window = st.sidebar.slider(
            "Short MA Window",
            min_value=5,
            max_value=50,
            value=STRATEGY_DEFAULTS["momentum"]["short_window"],
            key="qa_mom_short"
        )
        long_window = st.sidebar.slider(
            "Long MA Window",
            min_value=20,
            max_value=200,
            value=STRATEGY_DEFAULTS["momentum"]["long_window"],
            key="qa_mom_long"
        )

    elif strategy_name == "RSI":
        rsi_period = st.sidebar.slider(
            "RSI Period",
            min_value=5,
            max_value=30,
            value=STRATEGY_DEFAULTS["rsi"]["period"],
            key="qa_rsi_per"
        )
        oversold = st.sidebar.slider(
            "Oversold Threshold",
            min_value=20,
            max_value=40,
            value=STRATEGY_DEFAULTS["rsi"]["os"]
        )
        overbought = st.sidebar.slider(
            "Overbought Threshold",
            min_value=60,
            max_value=80,
            value=STRATEGY_DEFAULTS["rsi"]["ob"]
        )

    st.sidebar.markdown("---")

    # Options d'affichage
    st.sidebar.subheader("📊 Display Options")
    show_signals = st.sidebar.checkbox("Show Buy/Sell Signals", value=False, key="qa_show_sig")
    show_indicators = st.sidebar.checkbox("Show Technical Indicators", value=True, key="qa_show_ind")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=False, key="qa_refresh")

    # Bouton de rafraîchissement
    if st.sidebar.button("🔄 Refresh Data", key="qa_btn_refresh"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info(f"🕐 Last update: {datetime.now().strftime('%H:%M:%S')}")

    # === MAIN CONTENT ===

    # Fonction de chargement des données avec cache
    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data(ticker, period, interval):
        """Charge les données avec cache"""
        try:
            fetcher = DataFetcher(ticker, period, interval)
            df = fetcher.get_historical_data()
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None

    # Chargement des données
    with st.spinner(f'📥 Loading data for {asset_name}...'):
        df = load_data(ticker, period, interval)

    if df is None or df.empty:
        st.error(f"❌ Unable to load data for {asset_name}. Please check the ticker symbol.")
        return # On retourne simplement au lieu de st.stop() pour ne pas casser l'app principale

    # === MÉTRIQUES PRINCIPALES ===
    st.subheader("💰 Current Market Data")

    col1, col2, col3, col4, col5 = st.columns(5)

    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[0]
    price_change = current_price - prev_price
    price_change_pct = (price_change / prev_price) * 100

    with col1:
        st.metric("💵 Current Price", f"€{current_price:.2f}", f"{price_change_pct:+.2f}%")
    with col2:
        st.metric("📈 High", f"€{df['High'].max():.2f}")
    with col3:
        st.metric("📉 Low", f"€{df['Low'].min():.2f}")
    with col4:
        st.metric("📊 Volume", f"{df['Volume'].iloc[-1]:,.0f}")
    with col5:
        volatility = df['Close'].pct_change().std() * 100
        st.metric("📉 Volatility", f"{volatility:.2f}%")

    st.markdown("---")

    # === BACKTESTING ===
    st.subheader(f"🎯 Backtesting - {strategy_name}")

    # Sélection de la stratégie
    strategy = None
    if strategy_name == "Buy & Hold":
        strategy = BuyHoldStrategy(df, initial_capital)
    elif strategy_name == "Momentum":
        strategy = MomentumStrategy(df, initial_capital, short_window, long_window)
    elif strategy_name == "RSI":
        strategy = RSIStrategy(df, initial_capital, rsi_period, oversold, overbought)

    # Exécuter le backtest
    if strategy:
        backtester = Backtester(df, initial_capital)
        results = backtester.run(strategy)

        # Graphique principal
        st.plotly_chart(
            create_price_strategy_chart(results, asset_name, show_signals),
            use_container_width=True
        )

        # === MÉTRIQUES DE PERFORMANCE ===
        st.subheader("📊 Performance Metrics")

        strategy_returns = results['Strategy_Returns'].dropna()
        metrics = generate_performance_summary(results['Close'], strategy_returns)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: st.metric("Total Return", f"{metrics['Total Return (%)']:.2f}%")
        with col2: st.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
        with col3: st.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']:.2f}%")
        with col4: st.metric("Volatility", f"{metrics['Volatility (%)']:.2f}%")
        with col5: st.metric("Win Rate", f"{metrics['Win Rate (%)']:.2f}%")

        # Métriques supplémentaires
        with st.expander("📈 Additional Metrics"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Annualized Return", f"{metrics['Annualized Return (%)']:.2f}%")
                st.metric("Sortino Ratio", f"{metrics['Sortino Ratio']:.2f}")
            with col2:
                st.metric("Best Day", f"{metrics['Best Day (%)']:.2f}%")
                st.metric("Worst Day", f"{metrics['Worst Day (%)']:.2f}%")
            with col3:
                st.metric("Calmar Ratio", f"{metrics['Calmar Ratio']:.2f}")
                final_value = results['Portfolio_Value'].iloc[-1]
                st.metric("Final Portfolio Value", f"€{final_value:,.2f}")

        st.markdown("---")

        # === GRAPHIQUES SUPPLÉMENTAIRES ===
        if show_indicators:
            st.subheader("📉 Additional Analysis")
            tab1, tab2, tab3 = st.tabs(["Drawdown", "Returns Distribution", "Technical Indicators"])
            
            with tab1: st.plotly_chart(create_drawdown_chart(results), use_container_width=True)
            with tab2: st.plotly_chart(create_returns_distribution(strategy_returns), use_container_width=True)
            with tab3:
                if strategy_name == "Momentum":
                    st.plotly_chart(create_moving_averages_chart(results), use_container_width=True)
                elif strategy_name == "RSI":
                    st.plotly_chart(create_rsi_chart(results), use_container_width=True)
                else:
                    st.info("No technical indicators for Buy & Hold strategy")

        # === DONNÉES BRUTES ===
        with st.expander("📋 View Raw Data"):
            st.dataframe(results[['Close', 'Position', 'Returns', 'Strategy_Returns', 'Portfolio_Value', 'Drawdown']].tail(50), use_container_width=True)

        # === TRADES HISTORY ===
        with st.expander("💼 Trade History"):
            trades = backtester.get_trades()
            if not trades.empty:
                st.dataframe(trades, use_container_width=True)
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Total Trades", len(trades))
                with col2: st.metric("Avg Return per Trade", f"{trades['Return (%)'].mean():.2f}%")
                with col3: st.metric("Avg Trade Duration", f"{trades['Duration'].mean():.1f} days" if 'Duration' in trades.columns else "N/A")
            else:
                st.info("No trades executed")

    # === FOOTER ===
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<div style='text-align: center; color: gray;'><p>Quant A Module - Single Asset Analysis</p></div>", unsafe_allow_html=True)

    # Auto-refresh
    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

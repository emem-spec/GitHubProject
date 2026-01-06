import streamlit as st
import logging
from datetime import datetime
import time

# --- IMPORTS ---
from config.settings import (
    DEFAULT_ASSETS, 
    LOOKBACK_PERIODS, 
    DEFAULT_INITIAL_CAPITAL, 
    STRATEGY_DEFAULTS, 
    REFRESH_INTERVAL
)
from data.fetcher import DataFetcher
from strategies.buy_hold import BuyHoldStrategy
from strategies.momentum import MomentumStrategy, RSIStrategy
from utils.backtester import Backtester
from utils.metrics import generate_performance_summary
from visualization.charts import (
    create_price_strategy_chart,
    create_drawdown_chart,
    create_moving_averages_chart,
    create_rsi_chart,
    create_returns_distribution,
    create_rolling_sharpe_chart
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_quant_a():
    """
    Fonction principale du module Quant A.
    Tout le code (UI, Logique, Sidebar) est encapsulé ici.
    """
    
    # Injection CSS (Scope local)
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("📊 Single Asset Quantitative Analysis (Quant A)")
    st.markdown("---")

    # ==========================================
    # 1. SIDEBAR CONFIGURATION (Tout est indenté)
    # ==========================================
    st.sidebar.header("⚙️ Configuration (Quant A)")

    # Sélection de l'actif
    asset_name = st.sidebar.selectbox(
        "Asset",
        options=list(DEFAULT_ASSETS.keys()),
        index=0,
        key="qa_asset_select"
    )
    ticker = DEFAULT_ASSETS[asset_name]

    # Période (Mise à jour pour accepter les nouvelles clés de settings.py)
    # On cherche l'index par défaut (1y ou 1mo)
    default_period_index = 2
    period_keys = list(LOOKBACK_PERIODS.keys())
    if "1y" in period_keys:
        default_period_index = period_keys.index("1y")
    
    period = st.sidebar.selectbox(
        "Period",
        options=period_keys,
        format_func=lambda x: LOOKBACK_PERIODS.get(x, x),
        index=default_period_index,
        key="qa_period_select"
    )

    # Intervalle
    interval_options = {
        "5 minutes": "5m",
        "15 minutes": "15m",
        "1 heure": "1h",
        "1 jour": "1d",
        "1 semaine": "1wk"
    }
    # Logique pour adapter l'intervalle si la période est longue (Yahoo bloque les données intraday sur > 60j)
    default_interval = 3 # 1 jour
    if period in ["2y", "5y", "10y", "max"]:
        st.sidebar.info("ℹ️ Long period selected: Interval set to Daily/Weekly")
        # Filtrer pour ne garder que jour/semaine
        interval_options = {"1 jour": "1d", "1 semaine": "1wk"}
        default_interval = 0

    interval_label = st.sidebar.selectbox(
        "Interval",
        options=list(interval_options.keys()),
        index=default_interval,
        key="qa_interval_select"
    )
    interval = interval_options[interval_label]

    st.sidebar.markdown("---")

    # Sélection de la stratégie
    st.sidebar.subheader("📈 Strategy Selection")
    strategy_name = st.sidebar.selectbox(
        "Trading Strategy",
        ["Buy & Hold", "Momentum", "RSI"],
        key="qa_strategy_select"
    )

    # Capital initial
    initial_capital = st.sidebar.number_input(
        "Initial Capital (€)",
        min_value=1000,
        max_value=1000000,
        value=DEFAULT_INITIAL_CAPITAL,
        step=1000,
        key="qa_capital_input"
    )

    # Paramètres de stratégie
    st.sidebar.subheader("🔧 Strategy Parameters")

    # Valeurs par défaut
    short_window = STRATEGY_DEFAULTS["momentum"]["short_window"]
    long_window = STRATEGY_DEFAULTS["momentum"]["long_window"]
    rsi_period = STRATEGY_DEFAULTS["rsi"]["period"]
    oversold = STRATEGY_DEFAULTS["rsi"]["oversold"]
    overbought = STRATEGY_DEFAULTS["rsi"]["overbought"]

    if strategy_name == "Momentum":
        short_window = st.sidebar.slider(
            "Short MA Window",
            min_value=5,
            max_value=100, # Augmenté pour les longues périodes
            value=short_window,
            key="qa_short_window"
        )
        long_window = st.sidebar.slider(
            "Long MA Window",
            min_value=20,
            max_value=365, # Augmenté pour supporter 1 an de moyenne mobile
            value=long_window,
            key="qa_long_window"
        )

    elif strategy_name == "RSI":
        rsi_period = st.sidebar.slider(
            "RSI Period",
            min_value=5,
            max_value=30,
            value=rsi_period,
            key="qa_rsi_period"
        )
        oversold = st.sidebar.slider(
            "Oversold Threshold",
            min_value=20,
            max_value=40,
            value=oversold,
            key="qa_rsi_oversold"
        )
        overbought = st.sidebar.slider(
            "Overbought Threshold",
            min_value=60,
            max_value=80,
            value=overbought,
            key="qa_rsi_overbought"
        )

    st.sidebar.markdown("---")

    # Options d'affichage
    st.sidebar.subheader("📊 Display Options")
    show_signals = st.sidebar.checkbox("Show Buy/Sell Signals", value=False, key="qa_show_signals")
    show_indicators = st.sidebar.checkbox("Show Technical Indicators", value=True, key="qa_show_indicators")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=False, key="qa_auto_refresh")

    # Bouton de rafraîchissement
    if st.sidebar.button("🔄 Refresh Data", key="qa_refresh_btn"):
        st.cache_data.clear()
        st.rerun()

    # Petit footer dans la sidebar (doit aussi être indenté !)
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

    # ==========================================
    # 2. DATA LOADING
    # ==========================================
    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data_cached(ticker_symbol, period_val, interval_val):
        try:
            fetcher = DataFetcher(ticker_symbol, period_val, interval_val)
            return fetcher.get_historical_data()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None

    with st.spinner(f'📥 Loading data for {asset_name} ({period})...'):
        df = load_data_cached(ticker, period, interval)

    if df is None or df.empty:
        st.error(f"❌ Unable to load data for {asset_name}. Please check the ticker symbol or try a shorter period.")
        return

    # ==========================================
    # 3. MARKET METRICS
    # ==========================================
    st.subheader("💰 Current Market Data")
    col1, col2, col3, col4, col5 = st.columns(5)

    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[0]
    price_change = current_price - prev_price
    price_change_pct = (price_change / prev_price) * 100
    
    # Gestion sécurisée de la volatilité
    returns = df['Close'].pct_change().dropna()
    volatility_val = returns.std() * 100 if not returns.empty else 0

    col1.metric("💵 Price", f"€{current_price:.2f}", f"{price_change_pct:+.2f}%")
    col2.metric("📈 High", f"€{df['High'].max():.2f}")
    col3.metric("📉 Low", f"€{df['Low'].min():.2f}")
    col4.metric("📊 Volume", f"{df['Volume'].iloc[-1]:,.0f}")
    col5.metric("⚡ Volatility (Period)", f"{volatility_val:.2f}%")

    st.markdown("---")

    # ==========================================
    # 4. BACKTESTING
    # ==========================================
    st.subheader(f"🎯 Backtesting - {strategy_name}")

    if strategy_name == "Buy & Hold":
        strategy = BuyHoldStrategy(df, initial_capital)
    elif strategy_name == "Momentum":
        strategy = MomentumStrategy(df, initial_capital, short_window, long_window)
    elif strategy_name == "RSI":
        strategy = RSIStrategy(df, initial_capital, rsi_period, oversold, overbought)

    backtester = Backtester(df, initial_capital)
    results = backtester.run(strategy)

    st.plotly_chart(
        create_price_strategy_chart(results, asset_name, show_signals),
        use_container_width=True
    )

    # ==========================================
    # 5. PERFORMANCE METRICS
    # ==========================================
    st.subheader("📊 Performance Metrics")

    strategy_returns = results['Strategy_Returns'].dropna()
    metrics = generate_performance_summary(results['Close'], strategy_returns)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Return", f"{metrics['Total Return (%)']:.2f}%")
    c2.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
    c3.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']:.2f}%")
    c4.metric("Annual Return", f"{metrics['Annualized Return (%)']:.2f}%")
    
    final_val = results['Portfolio_Value'].iloc[-1]
    delta_val = final_val - initial_capital
    c5.metric("Portfolio Value", f"€{final_val:,.2f}", f"{delta_val:+.2f} €")

   # ==========================================
    # 6. ADDITIONAL ANALYSIS
    # ==========================================
    if show_indicators:
        st.subheader("📉 Additional Analysis")
        # Ajout de l'onglet "Risk Analysis"
        tab1, tab2, tab3, tab4 = st.tabs(["Drawdown", "Risk Analysis", "Returns Dist.", "Technical Ind."])
        
        with tab1:
            st.plotly_chart(create_drawdown_chart(results), use_container_width=True)
            
        with tab2:
            st.markdown("**Rolling Sharpe Ratio (6-Month Window)**")
            # On utilise les rendements de la stratégie calculés plus haut
            if len(strategy_returns) > 126: # Vérifier qu'on a assez de données
                st.plotly_chart(create_rolling_sharpe_chart(strategy_returns, window=126), use_container_width=True)
            else:
                st.info("⚠️ Not enough data to calculate 6-month Rolling Sharpe Ratio (Need > 126 days).")
                
        with tab3:
            st.plotly_chart(create_returns_distribution(strategy_returns), use_container_width=True)
            
        with tab4:
            if strategy_name == "Momentum":
                st.plotly_chart(create_moving_averages_chart(results), use_container_width=True)
            elif strategy_name == "RSI":
                st.plotly_chart(create_rsi_chart(results), use_container_width=True)
            else:
                st.info("No technical indicators specific to Buy & Hold strategy")

    # ==========================================
    # 7. RAW DATA & TRADES
    # ==========================================
    with st.expander("📋 View Raw Data & Trade History"):
        col_data, col_trades = st.columns(2)
        
        with col_data:
            st.markdown("**Latest Market Data**")
            st.dataframe(
                results[['Close', 'Position', 'Returns', 'Strategy_Returns', 'Portfolio_Value']].tail(50),
                use_container_width=True
            )
            
        with col_trades:
            st.markdown("**Trade Logs**")
            trades = backtester.get_trades()
            if not trades.empty:
                st.dataframe(trades, use_container_width=True)
            else:
                st.info("No trades executed.")

    # Logique d'auto-refresh (DOIT ETRE INDENTEE AUSSI)
    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

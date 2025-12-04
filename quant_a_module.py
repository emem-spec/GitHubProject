import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging

# --- CONFIGURATION LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 1. MOTEUR DE DONNÉES (Backend)
# ==========================================
class DataFetcher:
    def __init__(self, ticker, period="1y", interval="1d"):
        self.ticker = ticker
        self.period = period
        self.interval = interval
    
    def get_historical_data(self):
        try:
            stock = yf.Ticker(self.ticker)
            df = stock.history(period=self.period, interval=self.interval, auto_adjust=True)
            if df.empty: return None
            df.index = pd.to_datetime(df.index)
            return df
        except Exception as e:
            logger.error(f"Erreur fetch: {e}")
            return None

# ==========================================
# 2. MOTEUR DE STRATÉGIES
# ==========================================
class Strategy:
    def __init__(self, data, initial_capital):
        self.data = data.copy()
        self.initial_capital = initial_capital

class BuyHoldStrategy(Strategy):
    def generate_signals(self):
        self.data['Signal'] = 1 # Toujours investi
        return self.data

class MomentumStrategy(Strategy):
    def __init__(self, data, capital, short_window, long_window):
        super().__init__(data, capital)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_window).mean()
        self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_window).mean()
        self.data['Signal'] = np.where(self.data['SMA_Short'] > self.data['SMA_Long'], 1, 0)
        return self.data

class RSIStrategy(Strategy):
    def __init__(self, data, capital, period, oversold, overbought):
        super().__init__(data, capital)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # 1 = Achat, 0 = Cash
        self.data['Signal'] = np.where(self.data['RSI'] < self.oversold, 1, 0)
        # Vente si surachat
        self.data['Signal'] = np.where(self.data['RSI'] > self.overbought, 0, self.data['Signal'])
        return self.data

# ==========================================
# 3. MOTEUR DE BACKTEST & METRIQUES
# ==========================================
class Backtester:
    def __init__(self, data, initial_capital):
        self.data = data
        self.initial_capital = initial_capital

    def run(self, strategy_instance):
        df = strategy_instance.generate_signals()
        
        # Calcul des rendements
        df['Returns'] = df['Close'].pct_change()
        # Le signal agit sur le rendement du lendemain (shift 1)
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
        df['Strategy_Returns'] = df['Strategy_Returns'].fillna(0)
        
        # Valeur du portefeuille
        df['Portfolio_Value'] = self.initial_capital * (1 + df['Strategy_Returns']).cumprod()
        
        # Calcul du Drawdown
        df['CumMax'] = df['Portfolio_Value'].cummax()
        df['Drawdown'] = (df['Portfolio_Value'] - df['CumMax']) / df['CumMax'] * 100
        
        # Simulation de Position (pour l'historique des trades)
        df['Position'] = df['Signal'].diff() # 1 = Buy, -1 = Sell
        
        return df

    def get_trades(self):
        # Simulation simplifiée de l'historique des trades
        trades = self.data[self.data['Position'] != 0].copy()
        if trades.empty: return pd.DataFrame()
        trades['Action'] = np.where(trades['Position'] == 1, 'BUY', 'SELL')
        trades = trades[['Close', 'Action', 'Portfolio_Value']]
        return trades

def generate_performance_summary(closes, strategy_returns):
    # Métriques Annuelles
    total_return = (1 + strategy_returns).prod() - 1
    ann_return = strategy_returns.mean() * 252
    volatility = strategy_returns.std() * np.sqrt(252)
    sharpe = (ann_return / volatility) if volatility != 0 else 0
    
    # Max Drawdown & Win Rate
    cum_returns = (1 + strategy_returns).cumprod()
    drawdown = (cum_returns / cum_returns.cummax()) - 1
    max_drawdown = drawdown.min()
    win_rate = len(strategy_returns[strategy_returns > 0]) / len(strategy_returns) * 100

    return {
        "Total Return (%)": total_return * 100,
        "Annualized Return (%)": ann_return * 100,
        "Volatility (%)": volatility * 100,
        "Sharpe Ratio": sharpe,
        "Max Drawdown (%)": max_drawdown * 100,
        "Win Rate (%)": win_rate,
        "Sortino Ratio": sharpe * 1.5, # Approximation
        "Calmar Ratio": abs(ann_return / max_drawdown) if max_drawdown != 0 else 0,
        "Best Day (%)": strategy_returns.max() * 100,
        "Worst Day (%)": strategy_returns.min() * 100
    }

# ==========================================
# 4. MOTEUR GRAPHIQUE (VISUALIZATION)
# ==========================================
def create_price_strategy_chart(results, asset_name, show_signals):
    fig = go.Figure()
    # Prix de base
    fig.add_trace(go.Scatter(x=results.index, y=results['Close'], name=asset_name, line=dict(color='gray', width=1)))
    
    # Valeur Portefeuille (rebasée sur le prix initial pour comparaison visuelle)
    scale_factor = results['Close'].iloc[0] / results['Portfolio_Value'].iloc[0]
    scaled_portfolio = results['Portfolio_Value'] * scale_factor
    
    fig.add_trace(go.Scatter(x=results.index, y=scaled_portfolio, name='Stratégie', line=dict(color='blue', width=2)))
    
    if show_signals:
        buys = results[results['Position'] == 1]
        sells = results[results['Position'] == -1]
        fig.add_trace(go.Scatter(x=buys.index, y=buys['Close'], mode='markers', name='Buy', marker=dict(color='green', size=10, symbol='triangle-up')))
        fig.add_trace(go.Scatter(x=sells.index, y=sells['Close'], mode='markers', name='Sell', marker=dict(color='red', size=10, symbol='triangle-down')))
        
    fig.update_layout(title="Comparaison Prix vs Stratégie", template="plotly_white", hovermode="x unified")
    return fig

def create_drawdown_chart(results):
    fig = px.area(results, y='Drawdown', title="Underwater Plot (Drawdown)", color_discrete_sequence=['red'])
    fig.update_layout(yaxis_title="Drawdown %")
    return fig

def create_returns_distribution(returns):
    fig = px.histogram(returns, title="Distribution des Rendements", nbins=50, color_discrete_sequence=['blue'])
    return fig

def create_moving_averages_chart(results):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results.index, y=results['Close'], name='Prix'))
    if 'SMA_Short' in results.columns:
        fig.add_trace(go.Scatter(x=results.index, y=results['SMA_Short'], name='SMA Courte', line=dict(color='orange')))
    if 'SMA_Long' in results.columns:
        fig.add_trace(go.Scatter(x=results.index, y=results['SMA_Long'], name='SMA Longue', line=dict(color='purple')))
    fig.update_layout(title="Moyennes Mobiles")
    return fig

def create_rsi_chart(results):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results.index, y=results['RSI'], name='RSI', line=dict(color='purple')))
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.update_layout(title="Indicateur RSI", yaxis_range=[0, 100])
    return fig


# ==========================================
# 5. FONCTION PRINCIPALE (UI)
# ==========================================
def run_quant_a():
    # --- CSS PERSONNALISÉ ---
    st.markdown("""
    <style>
        .metric-card { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

    st.header("📊 Single Asset Quantitative Analysis (Quant A)")
    st.markdown("---")

    # === SIDEBAR CONFIGURATION ===
    st.sidebar.header("⚙️ Configuration")
    
    # Actifs par défaut
    DEFAULT_ASSETS = {"Apple": "AAPL", "Bitcoin": "BTC-USD", "Euro/USD": "EURUSD=X", "Gold": "GC=F", "Google": "GOOGL"}
    LOOKBACK_PERIODS = {"1 mois": "1mo", "3 mois": "3mo", "6 mois": "6mo", "1 an": "1y", "5 ans": "5y"}
    
    asset_name = st.sidebar.selectbox("Asset", options=list(DEFAULT_ASSETS.keys()))
    ticker = DEFAULT_ASSETS[asset_name]
    
    period_label = st.sidebar.selectbox("Period", options=list(LOOKBACK_PERIODS.keys()), index=3)
    period = LOOKBACK_PERIODS[period_label]
    
    # Stratégie
    st.sidebar.subheader("📈 Strategy Selection")
    strategy_name = st.sidebar.selectbox("Trading Strategy", ["Buy & Hold", "Momentum", "RSI"])
    
    initial_capital = st.sidebar.number_input("Initial Capital (€)", 1000, 1000000, 10000)

    # Paramètres Dynamiques
    short_window, long_window, rsi_period, oversold, overbought = 20, 50, 14, 30, 70
    
    if strategy_name == "Momentum":
        short_window = st.sidebar.slider("Short MA", 5, 50, 20)
        long_window = st.sidebar.slider("Long MA", 20, 200, 50)
    elif strategy_name == "RSI":
        rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
        oversold = st.sidebar.slider("Oversold", 10, 40, 30)
        overbought = st.sidebar.slider("Overbought", 60, 90, 70)

    show_signals = st.sidebar.checkbox("Show Signals", value=True)
    show_indicators = st.sidebar.checkbox("Show Indicators", value=True)

    # === CHARGEMENT DES DONNÉES ===
    fetcher = DataFetcher(ticker, period=period)
    df = fetcher.get_historical_data()
    
    if df is not None:
        # Affichage Métriques Marché
        current_price = df['Close'].iloc[-1]
        delta = df['Close'].pct_change().iloc[-1] * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Prix Actuel", f"{current_price:.2f}", f"{delta:.2f}%")
        c2.metric("Plus Haut", f"{df['High'].max():.2f}")
        c3.metric("Plus Bas", f"{df['Low'].min():.2f}")
        
        st.markdown("---")

        # === EXÉCUTION BACKTEST ===
        if strategy_name == "Buy & Hold":
            strategy = BuyHoldStrategy(df, initial_capital)
        elif strategy_name == "Momentum":
            strategy = MomentumStrategy(df, initial_capital, short_window, long_window)
        elif strategy_name == "RSI":
            strategy = RSIStrategy(df, initial_capital, rsi_period, oversold, overbought)
            
        backtester = Backtester(df, initial_capital)
        results = backtester.run(strategy)
        
        # === GRAPHIQUE PRINCIPAL ===
        st.subheader(f"Performance: {strategy_name}")
        st.plotly_chart(create_price_strategy_chart(results, asset_name, show_signals), use_container_width=True)
        
        # === METRIQUES DE PERFORMANCE ===
        st.subheader("📊 Performance Metrics")
        strat_ret = results['Strategy_Returns']
        metrics = generate_performance_summary(results['Close'], strat_ret)
        
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        mc1.metric("Total Return", f"{metrics['Total Return (%)']:.2f}%")
        mc2.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
        mc3.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']:.2f}%")
        mc4.metric("Win Rate", f"{metrics['Win Rate (%)']:.2f}%")
        mc5.metric("Final Value", f"€{results['Portfolio_Value'].iloc[-1]:,.0f}")
        
        # === ONGLETS D'ANALYSE ===
        if show_indicators:
            tab1, tab2, tab3 = st.tabs(["Drawdown", "Distribution", "Indicateurs Tech"])
            with tab1:
                st.plotly_chart(create_drawdown_chart(results), use_container_width=True)
            with tab2:
                st.plotly_chart(create_returns_distribution(strat_ret), use_container_width=True)
            with tab3:
                if strategy_name == "Momentum":
                    st.plotly_chart(create_moving_averages_chart(results), use_container_width=True)
                elif strategy_name == "RSI":
                    st.plotly_chart(create_rsi_chart(results), use_container_width=True)
        
        # === DONNÉES BRUTES ===
        with st.expander("Voir les données brutes"):
            st.dataframe(results.tail(100))
            
    else:
        st.error("Erreur de chargement des données")

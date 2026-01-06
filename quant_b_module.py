import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime
import time
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_data(tickers, period, interval="1d"):
    try:
        df = yf.download(tickers, period=period, interval=interval, auto_adjust=True)
        if 'Close' in df.columns:
            data = df['Close']
        else:
            data = df
        return data.dropna()
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None


def calculate_metrics(series):
    """Calculate key metrics (Returns, Volatility, Sharpe, Drawdown)"""
    returns = series.pct_change().dropna()
    
    # Total Return
    total_return = (series.iloc[-1] / series.iloc[0]) - 1
    
    # Annualized Volatility (252 trading days)
    volatility = returns.std() * np.sqrt(252)
    
    # Sharpe Ratio (Risk-free rate assumed at 2%)
    risk_free_rate = 0.02
    annualized_return = returns.mean() * 252
    if volatility != 0 :
        sharpe = (annualized_return - risk_free_rate) / volatility
    else :
        sharpe=0
    
    # Max Drawdown
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns / running_max) - 1
    max_drawdown = drawdown.min()
    
    return {
        "Total Return": total_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_drawdown
    }

# Main function
def run_quant_b():
    # Custom CSS for metric cards
    st.markdown("""
    <style>
        .metric-card { background-color: #f0f2f6; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; }
        .live-badge { background-color: #d4edda; color: #155724; padding: 5px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.header(" Multi-Asset Portfolio Manager (Quant B)")
    
    st.markdown("### Live Market Monitor (24h)")
    
    col_refresh, col_time = st.columns([1, 3])
    with col_refresh:
        auto_refresh = st.checkbox("Auto-refresh (5 min)", value=True)
    
    with col_time:
        now = datetime.now().strftime("%d %B %Y - %H:%M:%S")
        st.markdown(f"<span class='live-badge'>Last Update: {now}</span>", unsafe_allow_html=True)

    if 'tickers_input' not in st.session_state:
        st.session_state.tickers_input = "AAPL, MSFT, GOOGL, AMZN, TSLA"
    default_tickers_list = [x.strip().upper() for x in st.session_state.tickers_input.split(',') if x.strip() != '']

    with st.spinner("Fetching live data..."):
        live_data = get_data(default_tickers_list, period="5d", interval="5m")
    
    if live_data is not None and not live_data.empty:
        # Normalize to 100 for comparison
        normalized_live = (live_data / live_data.iloc[0]) * 100
        
        # Plot Intraday
        fig_live = px.line(normalized_live, title="Short Term Trends (Last 5 Days - 5m interval)")
        fig_live.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_live, use_container_width=True)
        
        # Display Current Values
        cols = st.columns(len(default_tickers))
        for i, ticker in enumerate(default_tickers):
            if ticker in live_data.columns:
                last_price = live_data[ticker].iloc[-1]
                prev_price = live_data[ticker].iloc[-2]
                delta = (last_price - prev_price) / prev_price * 100
                cols[i].metric(ticker, f"${last_price:.2f}", f"{delta:.2f}%")
    
    st.markdown("---")

    st.sidebar.header("Investment Universe")
    tickers_input = st.sidebar.text_input("Tickers (comma separated)", default_tickers)
    tickers = [x.strip().upper() for x in tickers_input.split(',') if x.strip() != '']
    
    period = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y", "max"], index=2)

    if len(tickers) < 3:
        st.error("The project requires at least 3 assets for diversification.")
        return

    data = get_data(tickers, period, interval="1d")

    if data is None or data.empty:
        st.error("Error fetching data historical data")
        return

    # Check available tickers
    available_tickers = data.columns.tolist()
    missing = set(tickers) - set(available_tickers)
    if missing:
        st.warning(f"Data not found for: {', '.join(missing)}")
    
    if len(available_tickers) < 2:
        st.error("Not enough valid data to build a portfolio.")
        return

    # Allocation
    st.sidebar.header("Allocation")
    st.sidebar.write("Portfolio Weights:")
    
    weights_input = []
    for t in available_tickers:
        # Initialize with equal weights
        w = st.sidebar.slider(f"{t}", 0.0, 1.0, 1.0/len(available_tickers), 0.05, key=t)
        weights_input.append(w)
    
    # Normalization (Sum = 100%)
    total_w = sum(weights_input)
    if total_w == 0:
        weights = np.array([1/len(available_tickers)] * len(available_tickers))
    else:
        weights = np.array([w/total_w for w in weights_input])
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Effective Weights:** {np.round(weights*100, 1)}%")

    # Portfolio calculations metrics
    # Daily returns of assets
    returns_df = data.pct_change().dropna()
    
    # Portfolio Return (Matrix Dot Product)
    # R_p = w1*R1 + w2*R2 ...
    portfolio_returns = returns_df.dot(weights)
    
    # Reconstruct Value Index (Base 100)
    portfolio_value = (1 + portfolio_returns).cumprod() * 100
    assets_value = (1 + returns_df).cumprod() * 100
    
    # Merge for charting
    chart_data = assets_value.copy()
    chart_data['PORTFOLIO'] = portfolio_value

    # Dashboard display
    
    #  Performance Chart (Line Chart)
    st.subheader("Assets vs Portfolio Comparison (Base 100)")
    
    fig_perf = go.Figure()
    # Plot assets in gray/thin
    for col in assets_value.columns:
        fig_perf.add_trace(go.Scatter(x=assets_value.index, y=assets_value[col], 
                                      name=col, line=dict(width=1, dash='dot'), opacity=0.7))
    
    # Plot portfolio in bold/blue
    fig_perf.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value, 
                                  name='PORTFOLIO', line=dict(color='blue', width=4)))
    
    fig_perf.update_layout(hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig_perf, use_container_width=True)

    # B. Metrics & Diversification
    st.subheader("Performance & Risk Metrics")
    
    # Calculate Portfolio Metrics
    port_metrics = calculate_metrics(portfolio_value)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Return", f"{port_metrics['Total Return']*100:.2f} %")
    col2.metric("Annual Volatility", f"{port_metrics['Volatility']*100:.2f} %")
    col3.metric("Sharpe Ratio", f"{port_metrics['Sharpe Ratio']:.2f}")
    col4.metric("Max Drawdown", f"{port_metrics['Max Drawdown']*100:.2f} %")

    # C. Diversification Effect (Quant B Specific)
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("🔗 Correlation Matrix")
        corr_matrix = returns_df.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        st.plotly_chart(fig_corr, use_container_width=True)
        
    with c2:
        st.subheader("🛡️ Diversification Effect")
        # Calculation: Weighted average of individual volatilities vs Actual portfolio volatility
        
        asset_vols = returns_df.std() * np.sqrt(252)
        weighted_avg_vol = np.dot(weights, asset_vols)
        actual_vol = port_metrics['Volatility']
        
        diversification_benefit = weighted_avg_vol - actual_vol
        div_pct = (diversification_benefit / weighted_avg_vol) * 100
        
        st.write(f"Weighted Avg Volatility: **{weighted_avg_vol*100:.2f}%**")
        st.write(f"Actual Portfolio Volatility: **{actual_vol*100:.2f}%**")
        
        st.success(f"📉 Diversification Gain: **-{div_pct:.2f}%** risk eliminated due to imperfect correlations.")
        
        # Risk/Return Chart (Scatter Plot)
        # Create a small DataFrame for the plot
        risk_ret_data = pd.DataFrame({
            'Volatility': asset_vols,
            'Return': returns_df.mean() * 252,
            'Type': ['Asset'] * len(asset_vols),
            'Ticker': asset_vols.index
        })
        
        # Add Portfolio point
        risk_ret_data.loc['PORTFOLIO'] = [actual_vol, returns_df.mean().dot(weights) * 252, 'Portfolio', 'PORTFOLIO']
        
        fig_scatter = px.scatter(risk_ret_data, x='Volatility', y='Return', color='Type', 
                                 text='Ticker', size=[1]*len(risk_ret_data), size_max=10,
                                 title="Risk / Return Map", color_discrete_map={'Portfolio': 'blue', 'Asset': 'gray'})
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)

    # D. Raw Data
    with st.expander("View Raw Data"):
        st.dataframe(data.tail())
    if auto_refresh:
        time.sleep(300) # 300 seconds = 5 minutes
        st.rerun()

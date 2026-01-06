import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# Import custom modules 
from data_manager import get_data
from portfolio_analytics import calculate_metrics, calculate_portfolio_performance

def run_quant_b():
    # Custom CSS
    st.markdown("""
    <style>
        .metric-card { background-color: #f0f2f6; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; }
        .live-badge { background-color: #d4edda; color: #155724; padding: 5px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.header("📊 Multi-Asset Portfolio Manager (Quant B)")

    #Allocation and configuration

    if 'tickers_input' not in st.session_state:
        st.session_state.tickers_input = "AAPL, MSFT, GOOGL, AMZN"

    st.sidebar.header("I) Investment Universe")
    tickers_input_raw = st.sidebar.text_input("Tickers (comma separated)", key="tickers_input")
    clean_input = tickers_input_raw.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
    tickers = [x.strip().upper() for x in clean_input.split(',') if x.strip() != '']
    
    period = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y", "max"], index=2, key="qb_period")

    if len(tickers) < 3:
        st.error("The project requires at least 3 assets for diversification.")
        return

    # Fetch Historical Data
    data = get_data(tickers, period, interval="1d")
    
    if data is None or data.empty:
        st.error("Error fetching historical data. Please check tickers.")
        return
        
    available_tickers = data.columns.tolist()
    
    # Allocation Sliders
    st.sidebar.header("II) Allocation")
    st.sidebar.write("Portfolio Weights:")
    
    weights_input = []
    for t in available_tickers:
        slider_key = f"w_{t}"
        if slider_key not in st.session_state:
            st.session_state[slider_key] = 1.0 / len(available_tickers)
        w = st.sidebar.slider(f"{t}", 0.0, 1.0, key=slider_key)
        weights_input.append(w)
    
    total_w = sum(weights_input)
    if total_w == 0:
        weights = np.array([1/len(available_tickers)] * len(available_tickers))
    else:
        weights = np.array([w/total_w for w in weights_input])
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Effective Weights:** {np.round(weights*100, 1)}%")

    #Live market
    st.markdown("### Live Market Monitor (Last 24h)")
    col_refresh, col_time = st.columns([1, 3])
    with col_refresh:
        auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=True, key="qb_autorefresh")
    with col_time:
        now = datetime.now().strftime("%d %B %Y - %H:%M:%S")
        st.markdown(f"<span class='live-badge'>Last Update: {now}</span>", unsafe_allow_html=True)

    with st.spinner("Fetching live data..."):
        live_data = get_data(available_tickers, period="1d", interval="5m")
    
    if live_data is not None and not live_data.empty:
        normalized_live = (live_data / live_data.iloc[0]) * 100
        live_portfolio_series = normalized_live.dot(weights)
        
        fig_live = go.Figure()
        # Plot Assets
        for col in available_tickers:
            if col in normalized_live.columns:
                fig_live.add_trace(go.Scatter(x=normalized_live.index, y=normalized_live[col], name=col, line=dict(width=1, dash='dot'), opacity=0.6))
        # Plot Portfolio
        fig_live.add_trace(go.Scatter(x=live_portfolio_series.index, y=live_portfolio_series, name='PORTFOLIO', line=dict(color='blue', width=3)))
        
        fig_live.update_layout(title="Intraday Trends (Last 24h - 5m interval)", height=350, margin=dict(l=0, r=0, t=30, b=0), template="plotly_white", hovermode="x unified")
        st.plotly_chart(fig_live, use_container_width=True)
        
        # Display Current Values
        cols = st.columns(len(available_tickers))
        for i, ticker in enumerate(available_tickers):
            if ticker in live_data.columns:
                last_price = live_data[ticker].iloc[-1]
                prev_price = live_data[ticker].iloc[-2] if len(live_data) > 1 else last_price
                delta = (last_price - prev_price) / prev_price * 100
                if i < 4:
                    cols[i].metric(ticker, f"${last_price:.2f}", f"{delta:.2f}%")
    
    st.markdown("---")

    
    #Metrics Analysis

    portfolio_value, assets_value, returns_df = calculate_portfolio_performance(data, weights)
    
    st.subheader(" Assets vs Portfolio Comparison (Base 100)")
    fig_perf = go.Figure()
    for col in assets_value.columns:
        fig_perf.add_trace(go.Scatter(x=assets_value.index, y=assets_value[col], name=col, line=dict(width=1, dash='dot'), opacity=0.7))
    fig_perf.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value, name='PORTFOLIO', line=dict(color='blue', width=4)))
    fig_perf.update_layout(hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig_perf, use_container_width=True)

    st.subheader(" Advanced Performance & Risk Metrics")
    port_metrics = calculate_metrics(portfolio_value)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Return", f"{port_metrics['Total Return']*100:.2f} %")
    c2.metric("Volatility", f"{port_metrics['Volatility']*100:.2f} %")
    c3.metric("Max Drawdown", f"{port_metrics['Max Drawdown']*100:.2f} %",help="Maximum observed loss from a peak to a trough")
    c4.metric("Calmar Ratio", f"{port_metrics['Calmar Ratio']:.2f}", help="Annual Return / Abs(Max Drawdown)")
    
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Sharpe Ratio", f"{port_metrics['Sharpe Ratio']:.2f}", help="Reward per unit of total risk")
    c6.metric("Sortino Ratio", f"{port_metrics['Sortino Ratio']:.2f}", help="Reward per unit of downside risk")
    c7.metric("VaR (95%)", f"{port_metrics['VaR (95%)']*100:.2f} %")
    c8.metric("CVaR (95%)", f"{port_metrics['CVaR (95%)']*100:.2f} %")

    st.markdown("---")
    
    # Diversification
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader(" Correlation Matrix")
        fig_corr = px.imshow(returns_df.corr(), text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        st.plotly_chart(fig_corr, use_container_width=True)
        
    with c2:
        st.subheader(" Risk Analysis (Risk/Return)")
        asset_vols = returns_df.std() * np.sqrt(252)
        weighted_avg_vol = np.dot(weights, asset_vols)
        actual_vol = port_metrics['Volatility']
        div_benefit = (weighted_avg_vol - actual_vol) / weighted_avg_vol * 100
        
        st.write(f"Weighted Avg Volatility: **{weighted_avg_vol*100:.2f}%**")
        st.write(f"Actual Portfolio Volatility: **{actual_vol*100:.2f}%**")
        st.success(f" Diversification Gain: **-{div_pct if 'div_pct' in locals() else div_benefit:.2f}%** risk eliminated.")
        
        risk_ret_data = pd.DataFrame({
            'Volatility': asset_vols,
            'Return': returns_df.mean() * 252,
            'Type': ['Asset'] * len(asset_vols),
            'Ticker': asset_vols.index
        })
        risk_ret_data.loc['PORTFOLIO'] = [actual_vol, returns_df.mean().dot(weights) * 252, 'Portfolio', 'PORTFOLIO']
        
        fig_scatter = px.scatter(risk_ret_data, x='Volatility', y='Return', color='Type', text='Ticker', size_max=10)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(data.tail())

    if auto_refresh:
        time.sleep(300)
        st.rerun()

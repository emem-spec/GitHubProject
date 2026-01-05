import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_data(tickers, period):
    df = yf.download(tickers, period=period, auto_adjust=True)
    if 'Close' in df.columns:
        data = df['Close']
    else:
        data = df
    
    data = data.dropna()
    return data

def calculate_metrics(series):
    returns = series.pct_change().dropna()
    
    # return total
    total_return = (series.iloc[-1] / series.iloc[0]) - 1
    
    # annual vol
    volatility = returns.std() * np.sqrt(252)
    
    # Sharpe Ratio 
    risk_free_rate = 0.02
    annualized_return = returns.mean() * 252
    if volatility!=0 :
        sharpe = (annualized_return - risk_free_rate) / volatility
    else :
        sharpe=0
    
    # Max Drawdown
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns / running_max) - 1
    max_drawdown = drawdown.min()
    
    return {
        "Rendement Total": total_return,
        "Volatilité": volatility,
        "Sharpe": sharpe,
        "Max Drawdown": max_drawdown
    }

def run_quant_b():
    st.markdown("""
    <style>
        .metric-card { background-color: #f0f2f6; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

    st.header(" Multi-Asset Portfolio Manager ")
    st.markdown("---")

    # SIDEBAR CONFIGURATION 
    st.sidebar.header("1. Univers d'Investissement")
    
    default_tickers = "AAPL, MSFT, GOOGL, AMZN, TSLA"
    tickers_input = st.sidebar.text_input("Tickers (séparés par virgules)", default_tickers)
    tickers = [x.strip().upper() for x in tickers_input.split(',') if x.strip() != '']
    
    period = st.sidebar.selectbox("Période", ["3mo", "6mo", "1y", "2y", "5y", "max"], index=2)

    # Data recuperation
    if len(tickers) < 3:
        st.error("Project ask for at least 3 assets")
        return

    with st.spinner("Recuperation data"):
        data = get_data(tickers, period)

    if data is None or data.empty:
        st.error("Error check the tickers")
        return

    #making sure we didn't missed a ticker
    available_tickers = data.columns.tolist()
    missing = set(tickers) - set(available_tickers)
    if missing:
        st.warning(f"Données introuvables pour : {', '.join(missing)}")
    
    st.sidebar.header("Allocation")
    st.sidebar.write("Weighting of the portfolio :")
    
    weights_input = []
    for t in available_tickers:
        w = st.sidebar.slider(f"{t}", 0.0, 1.0, 1.0/len(available_tickers), 0.05, key=t)
        weights_input.append(w)
    
    total_w = sum(weights_input)
    if total_w == 0:
        weights = np.array([1/len(available_tickers)] * len(available_tickers))
    else:
        weights = np.array([w/total_w for w in weights_input])
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Poids effectifs :** {np.round(weights*100, 1)}%")

    # Calculations
    # daily returns
    returns_df = data.pct_change().dropna()
    
    # Return of the portfolio
    # R_p = w1*R1 + w2*R2 ...
    portfolio_returns = returns_df.dot(weights)
    
    portfolio_value = (1 + portfolio_returns).cumprod() * 100
    assets_value = (1 + returns_df).cumprod() * 100
    
    chart_data = assets_value.copy()
    chart_data['PORTFOLIO'] = portfolio_value

    # Display Dashboard
    
    # Performance return
    st.subheader("📈 Comparaison Actifs vs Portefeuille (Base 100)")
    
    fig_perf = go.Figure()
    
    for col in assets_value.columns:
        fig_perf.add_trace(go.Scatter(x=assets_value.index, y=assets_value[col], 
                                      name=col, line=dict(width=1, dash='dot'), opacity=0.7))
    
    fig_perf.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value, 
                                  name='PORTFOLIO', line=dict(color='blue', width=4)))
    
    fig_perf.update_layout(hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig_perf, use_container_width=True)

    # Metrics
    st.subheader("Performance & Risk")
    
    # Computation of metrics
    port_metrics = calculate_metrics(portfolio_value)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rendement Total", f"{port_metrics['Rendement Total']*100:.2f} %")
    col2.metric("Volatilité (Annu.)", f"{port_metrics['Volatilité']*100:.2f} %")
    col3.metric("Sharpe Ratio", f"{port_metrics['Sharpe']:.2f}")
    col4.metric("Max Drawdown", f"{port_metrics['Max Drawdown']*100:.2f} %")

    # C. Effet de Diversification (Spécifique Quant B)
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
     
    with c1:
        st.subheader("🔗 Matrice de Corrélation")
        corr_matrix = returns_df.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        st.plotly_chart(fig_corr, use_container_width=True)
        
    with c2:
        st.subheader("🛡️ Effet de Diversification")
        # Calcul : Moyenne pondérée des volatilités individuelles vs Volatilité réelle du portefeuille
        # Si Vol_Portefeuille < Moyenne_Pondérée_Vol, c'est qu'il y a diversification
        
        asset_vols = returns_df.std() * np.sqrt(252)
        weighted_avg_vol = np.dot(weights, asset_vols)
        actual_vol = port_metrics['Volatilité']
        
        diversification_benefit = weighted_avg_vol - actual_vol
        div_pct = (diversification_benefit / weighted_avg_vol) * 100
        
        st.write(f"Volatilité Moyenne Pondérée : **{weighted_avg_vol*100:.2f}%**")
        st.write(f"Volatilité Réelle Portefeuille : **{actual_vol*100:.2f}%**")
        
        st.success(f"📉 Gain de Diversification : **-{div_pct:.2f}%** de risque éliminé grâce aux corrélations imparfaites.")
        
        # Graphique Risk/Return (Scatter Plot)
        # On crée un petit DataFrame pour le plot
        risk_ret_data = pd.DataFrame({
            'Volatilité': asset_vols,
            'Rendement': returns_df.mean() * 252,
            'Type': ['Actif'] * len(asset_vols),
            'Ticker': asset_vols.index
        })
        
        # Ajout du portefeuille
        risk_ret_data.loc['PORTFOLIO'] = [actual_vol, returns_df.mean().dot(weights) * 252, 'Portefeuille', 'PORTFOLIO']
        
        fig_scatter = px.scatter(risk_ret_data, x='Volatilité', y='Rendement', color='Type', 
                                 text='Ticker', size=[1]*len(risk_ret_data), size_max=10,
                                 title="Carte Risque / Rendement", color_discrete_map={'Portefeuille': 'blue', 'Actif': 'gray'})
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)

    # D. Données
    with st.expander("Voir les données brutes"):
        st.dataframe(data.tail())
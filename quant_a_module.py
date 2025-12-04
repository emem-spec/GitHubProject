import streamlit as st
import plotly.express as px
import pandas as pd
from fetcher import DataFetcher

def run_quant_a():
    st.header("🔎 Analyse Mono-Actif (Quant A)")
    st.markdown("---")
    
    # 1. Barre latérale spécifique
    col_input, col_period = st.columns([2, 1])
    
    with col_input:
        ticker = st.text_input("Symbole de l'actif (ex: AAPL, BTC-USD, EURUSD=X)", "AAPL")
    
    with col_period:
        period = st.selectbox("Période", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)

    if st.button("Lancer l'analyse"):
        st.write(f"🔄 Connexion à l'API via DataFetcher pour **{ticker}**...")
        
        # --- UTILISATION DE SA CLASSE DataFetcher ---
        try:
            # On instancie sa classe
            fetcher = DataFetcher(ticker, period=period)
            
            # On récupère les données via ses méthodes
            df = fetcher.get_historical_data()
            price = fetcher.get_current_price()
            info = fetcher.get_info()

            if df is not None and not df.empty:
                # Affichage des métriques
                col1, col2, col3 = st.columns(3)
                col1.metric("Prix Actuel", f"{price:.2f} $")
                col2.metric("Secteur", info.get('sector', 'N/A'))
                col3.metric("Industrie", info.get('industry', 'N/A'))

                # Graphique avec Plotly
                st.subheader("Graphique des Prix")
                fig = px.line(df, y='Close', title=f"Historique de {ticker}")
                st.plotly_chart(fig, use_container_width=True)

                # --- EXEMPLE DE STRATÉGIE SIMPLE (Requis pour Quant A) ---
                st.subheader("Stratégie : Moyenne Mobile (SMA)")
                window = st.slider("Fenêtre Moyenne Mobile", 5, 100, 20)
                
                # Calcul de la moyenne mobile
                df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
                
                # Graphique comparatif
                fig_strat = px.line(df, y=['Close', f'SMA_{window}'], title="Prix vs Moyenne Mobile")
                st.plotly_chart(fig_strat, use_container_width=True)

            else:
                st.error("Impossible de récupérer les données. Vérifiez le ticker.")

        except Exception as e:
            st.error(f"Erreur technique : {e}")

import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta

# Configuration du logging (pour le debug)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. CLASSE BACKEND (Anciennement fetcher.py) ---
class DataFetcher:
    """Récupère les données financières en temps réel via Yahoo Finance"""
    
    def __init__(self, ticker, period="1y", interval="1d"):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.stock = yf.Ticker(ticker)
        
    def get_historical_data(self):
        """Récupère l'historique des prix"""
        try:
            # auto_adjust=True est crucial pour éviter les bugs récents de yfinance
            df = self.stock.history(period=self.period, interval=self.interval, auto_adjust=True)
            if df.empty:
                logger.error(f"Aucune donnée trouvée pour {self.ticker}")
                return None
            
            # On s'assure que l'index est bien en datetime
            df.index = pd.to_datetime(df.index)
            return df
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération pour {self.ticker}: {str(e)}")
            return None
    
    def get_current_price(self):
        """Récupère le dernier prix disponible"""
        try:
            # On demande 1 jour de data pour avoir le dernier point
            data = self.stock.history(period="1d", interval="1m", auto_adjust=True)
            if not data.empty:
                return data['Close'].iloc[-1]
            # Fallback si pas de data intraday (marché fermé)
            data_daily = self.stock.history(period="5d", auto_adjust=True)
            return data_daily['Close'].iloc[-1]
        except Exception as e:
            logger.error(f"Erreur prix actuel: {str(e)}")
            return 0.0
    
    def get_info(self):
        """Récupère les métadonnées (Secteur, Industrie...)"""
        try:
            return self.stock.info
        except Exception as e:
            logger.error(f"Erreur info: {str(e)}")
            return {}

# --- 2. FONCTION FRONTEND (Interface Streamlit) ---
def run_quant_a():
    st.header("🔎 Analyse Mono-Actif (Quant A)")
    st.markdown("---")
    
    # Barre latérale spécifique
    col_input, col_period = st.columns([2, 1])
    
    with col_input:
        ticker = st.text_input("Symbole de l'actif (ex: AAPL, BTC-USD, EURUSD=X)", "AAPL")
    
    with col_period:
        period = st.selectbox("Période", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)

    if st.button("Lancer l'analyse"):
        st.write(f"🔄 Connexion à l'API pour **{ticker}**...")
        
        try:
            # On instancie la classe définie juste au-dessus
            fetcher = DataFetcher(ticker, period=period)
            
            # Récupération des données
            df = fetcher.get_historical_data()
            price = fetcher.get_current_price()
            info = fetcher.get_info()

            if df is not None and not df.empty:
                # Affichage des métriques clés
                col1, col2, col3 = st.columns(3)
                col1.metric("Prix Actuel", f"{price:.2f} $")
                col2.metric("Secteur", info.get('sector', 'N/A'))
                col3.metric("Industrie", info.get('industry', 'N/A'))

                # Graphique Principal
                st.subheader("Graphique des Prix")
                fig = px.line(df, y='Close', title=f"Historique de {ticker}")
                st.plotly_chart(fig, use_container_width=True)

                # --- STRATÉGIE (Moyenne Mobile) ---
                st.subheader("Stratégie : Moyenne Mobile (SMA)")
                window = st.slider("Fenêtre Moyenne Mobile", 5, 100, 20)
                
                # Calcul SMA
                df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
                
                # Graphique Comparatif
                fig_strat = px.line(df, y=['Close', f'SMA_{window}'], 
                                    title="Prix vs Moyenne Mobile",
                                    color_discrete_map={'Close': 'blue', f'SMA_{window}': 'orange'})
                st.plotly_chart(fig_strat, use_container_width=True)

                # Affichage des données brutes
                with st.expander("Voir les données brutes"):
                    st.dataframe(df.tail())

            else:
                st.error("Impossible de récupérer les données. Vérifiez le ticker.")

        except Exception as e:
            st.error(f"Erreur technique : {e}")

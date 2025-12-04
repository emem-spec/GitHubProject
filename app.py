import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Portfolio Manager", layout="wide")

st.title("Gestion de Portefeuille Multi-Actifs (Quant B)")
st.markdown("---")

# --- 1. Sidebar : Paramètres ---
st.sidebar.header("1. Choix des Actifs")

# Choix des tickers (Modifiable par l'utilisateur)
default_tickers = "AAPL, MSFT, GOOGL, AMZN"
tickers_input = st.sidebar.text_input("Entrez les tickers (séparés par des virgules)", default_tickers)
tickers = [x.strip().upper() for x in tickers_input.split(',')]

# Choix de la période
period = st.sidebar.selectbox("Période d'analyse", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

st.sidebar.header("2. Allocation du Portefeuille")
st.sidebar.write("Définissez les poids pour chaque actif :")

# Création dynamique des sliders pour les poids
weights = []
for ticker in tickers:
    w = st.sidebar.slider(f"Poids pour {ticker}", 0.0, 1.0, 1.0/len(tickers), 0.05)
    weights.append(w)

# Normalisation des poids pour que la somme fasse 100% (1.0)
total_weight = sum(weights)
if total_weight == 0:
    norm_weights = [1/len(tickers)] * len(tickers) # Sécurité
else:
    norm_weights = [w / total_weight for w in weights]

# Affichage de la répartition réelle
st.sidebar.info(f"Poids normalisés : {[round(w, 2) for w in norm_weights]}")


# --- 2. Récupération des Données ---
if len(tickers) < 3:
    st.error("⚠️ Le sujet exige au moins 3 actifs pour la diversification.")
else:
    try:
        with st.spinner("Téléchargement des données..."):
            # Récupération des données (auto_adjust=True pour éviter les bugs)
            df = yf.download(tickers, period=period, auto_adjust=True)
            
            # Extraction des prix de clôture (Close)
            # Attention: Si un seul ticker, la structure est différente, mais ici on impose >=3
            closes = df['Close']
            
            # Gestion des données manquantes
            closes = closes.dropna()

        # --- 3. Calculs Financiers ---
        
        # Rendements quotidiens
        daily_returns = closes.pct_change().dropna()
        
        # Calcul du rendement du portefeuille pondéré
        # Formule matricielle : R_port = R_assets * Weights
        portfolio_return = daily_returns.dot(norm_weights)
        
        # Indices Base 100 (Pour le graphique)
        cumulative_returns = (1 + daily_returns).cumprod() * 100
        cumulative_portfolio = (1 + portfolio_return).cumprod() * 100
        
        # On ajoute le portefeuille au tableau pour le graphique
        chart_data = cumulative_returns.copy()
        chart_data['PORTFOLIO'] = cumulative_portfolio

        # --- 4. Affichage du Dashboard ---

        # Colonnes pour les KPIs
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Performance Comparée")
            # Graphique interactif avec Plotly (plus pro que line_chart)
            fig = px.line(chart_data, title="Évolution Base 100 (Actifs vs Portefeuille)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🔗 Matrice de Corrélation")
            st.write("C'est essentiel pour mesurer la diversification.")
            
            # Calcul de la matrice
            corr_matrix = daily_returns.corr()
            
            # Affichage avec une carte de chaleur (Heatmap)
            fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
            st.plotly_chart(fig_corr, use_container_width=True)

        # Statistiques du Portefeuille
        st.markdown("---")
        st.subheader("📊 Statistiques du Portefeuille")
        
        # Calcul Volatilité (Annualisée)
        volatility = portfolio_return.std() * (252 ** 0.5)
        # Calcul Rendement Total
        total_ret = cumulative_portfolio.iloc[-1] - 100
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        stat_col1.metric("Rendement Total", f"{total_ret:.2f} %")
        stat_col2.metric("Volatilité Annualisée", f"{volatility*100:.2f} %")
        stat_col3.metric("Nombre d'actifs", len(tickers))

        # Affichage des données brutes
        with st.expander("Voir les données brutes"):
            st.dataframe(closes.tail())

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
        st.write("Vérifiez les tickers ou votre connexion internet.")

import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Titre de l'application
st.title("Mon Dashboard Finance (Quant B)")

# 2. Liste des actifs (Hardcodé pour faire simple au début)
# On choisit 3 actifs technologiques
tickers = ['AAPL', 'MSFT', 'GOOGL']
st.write("Actifs analysés :", tickers)

# 3. Téléchargement des données
st.write("Téléchargement des données en cours...")
# On récupère juste le prix de fermeture ajusté ('Adj Close')
data = yf.download(tickers, period='1y')['Adj Close']

# Afficher les 5 premières lignes pour montrer que ça marche
st.subheader("Aperçu des données brutes")
st.dataframe(data.head())

# 4. Calculs simples
# Calcul des rendements quotidiens (variation en %)
returns = data.pct_change()

# Création d'un portefeuille "Equipondéré" (1/3 chacun)
# On fait la moyenne des rendements des 3 actifs pour simuler le portefeuille
data['Mon Portefeuille'] = returns.mean(axis=1)

# On recalcule le prix cumulé (base 100) pour faire un joli graphique
# (C'est la formule standard : (1 + rendement).cumprod())
cumulative_returns = (1 + returns).cumprod()
cumulative_portfolio = (1 + data['Mon Portefeuille']).cumprod()

# 5. Affichage du Graphique
st.subheader("Comparaison : Mes Actions vs Mon Portefeuille")

# On utilise le graphique de base de Streamlit (pas besoin de Plotly)
st.line_chart(cumulative_returns)

st.write("Le graphique montre l'évolution de 1€ investi il y a un an.")

import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Titre de l'application
st.title("Mon Dashboard Finance (Quant B)")

# 2. Liste des actifs (Hardcodé pour faire simple au début)
tickers = ['AAPL', 'MSFT', 'GOOGL']
st.write("Actifs analysés :", tickers)

# 3. Téléchargement des données
st.write("Téléchargement des données en cours...")

# CORRECTION ICI : On utilise auto_adjust=True pour avoir des données propres
# et on ne demande pas ['Adj Close'] explicitement pour éviter le bug.
try:
    # Téléchargement des données
    df = yf.download(tickers, period='1y', auto_adjust=True)
    
    # On récupère uniquement la colonne 'Close' (Prix de fermeture)
    # Cela crée un tableau propre avec les tickers en colonnes
    data = df['Close']

    # Afficher les 5 dernières lignes pour vérifier que ça marche
    st.subheader("Aperçu des données brutes")
    st.dataframe(data.tail())

    # 4. Calculs simples
    # Calcul des rendements quotidiens (variation en %)
    returns = data.pct_change()

    # Création d'un portefeuille "Equipondéré" (1/3 chacun)
    # On fait la moyenne des rendements des 3 actifs
    data['Mon Portefeuille'] = returns.mean(axis=1)

    # On recalcule le prix cumulé (base 100) pour le graphique
    cumulative_returns = (1 + returns).cumprod()
    cumulative_portfolio = (1 + data['Mon Portefeuille']).cumprod()

    # 5. Affichage du Graphique
    st.subheader("Comparaison : Mes Actions vs Mon Portefeuille")
    
    # On affiche tout sur le même graphique
    # On combine les actions et le portefeuille
    combined_data = cumulative_returns.copy()
    combined_data['PORTFOLIO'] = cumulative_portfolio
    
    st.line_chart(combined_data)
    st.write("Le graphique montre l'évolution de 1€ investi il y a un an.")

except Exception as e:
    st.error(f"Une erreur s'est produite : {e}")
    st.write("Essaie de relancer l'application ou vérifie ta connexion internet.")

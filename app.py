import streamlit as st

# Importation des deux modules (fichiers locaux)
import quant_b_module
import quant_a_module

# Configuration Globale de la page (Doit être la première commande Streamlit)
st.set_page_config(page_title="Projet Finance - Groupe 12", layout="wide")

# Sidebar de Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller vers", ["Accueil", "Module Quant A (Mono-Actif)", "Module Quant B (Portefeuille)"])

if page == "Accueil":
    st.title("Projet Python pour la Finance 📈")
    st.write("Bienvenue sur notre plateforme d'analyse financière.")
    st.write("Utilisez le menu à gauche pour naviguer entre les modules.")
    st.info("👈 Sélectionnez un module dans la barre latérale.")

elif page == "Module Quant A (Mono-Actif)":
    # On appelle la fonction du fichier quant_a_module.py
    quant_a_module.run_quant_a()

elif page == "Module Quant B (Portefeuille)":
    # On appelle la fonction du fichier quant_b_module.py
    quant_b_module.run_quant_b()
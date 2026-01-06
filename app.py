import streamlit as st
import quant_b_module
import quant_a_module

st.set_page_config(page_title="Project Finance - Group 12", layout="wide")

# Sidebar of Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Menu", "Module Quant A (Mono-Actif)", "Module Quant B (Portefeuille)"])

if page == "Menu":
    st.title("Project Python Git - Group 12")
    st.write("Welcome on our web platform for financial analysis.")
    st.write("Use the left menu to navigate")
    st.info("👈 Select a module from the sidebar.")

elif page == "Module Quant A (Mono-Actif)":
    quant_a_module.run_quant_a()

elif page == "Module Quant B (Portefeuille)":
    quant_b_module.run_quant_b()

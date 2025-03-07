import streamlit as st
import pandas as pd
import data_processing as dp
import page2  
from streamlit_option_menu import option_menu  # Menu esthétique
from data_processing import load_data
import page3



# Configuration de la page
st.set_page_config(layout="wide", page_title="Extracteur de courbe")

# Ajouter des styles CSS globaux
st.markdown("""
    <style>
        h1 {
            font-size: 32px !important;
        }
        h2 {
            font-size: 28px !important;
        }
        h3 {
            font-size: 24px !important;
        }
        p, label {
            font-size: 18px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Barre de navigation avec option_menu
with st.sidebar:
    page = option_menu(
        menu_title="Navigation",  # Titre du menu

        options=["Découpage de courbes","Superposition des lots"],  # Pages disponibles
        icons=["scissors","graph-up"],  # Icônes pour chaque page

        menu_icon="menu-button",  # Icône du menu principal
        default_index=0,  # Page par défaut
    )


# Initialiser les états de session
dp.initialize_session_states()

# Page 2: Superposition des lots
if page == "Superposition des lots":
    page2.app()  


elif page =="Découpage de courbes":
    page3.app()



























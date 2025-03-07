import pandas as pd
import streamlit as st

def load_data(file_path, separator):
    """Charge les données à partir d'un fichier CSV avec le séparateur spécifié."""
    return pd.read_csv(file_path, sep=separator)

def save_selected_data(selected_data):
    """Enregistre les données sélectionnées dans un fichier CSV."""
    selected_data.to_csv("all_selected_data.csv", index=False)
    return "Toutes les données sélectionnées ont été sauvegardées dans 'all_selected_data.csv'"

def add_selected_range(lot_data, start_index, end_index, lot):
    """Ajoute une plage sélectionnée au dataframe global."""
    if start_index <= end_index:
        selected_range = lot_data.iloc[start_index:end_index + 1].copy()
        selected_range[st.session_state.lot_column] = lot  # Utiliser la colonne de lot sélectionnée
        st.session_state.selected_data = pd.concat([st.session_state.selected_data, selected_range], ignore_index=True)
        return f"Plage sélectionnée pour le lot {lot} ajoutée."
    else:
        return "L'indice de début doit être inférieur ou égal à l'indice de fin."

def initialize_session_states():
    """Initialise les états de session pour l'application."""
    if 'current_lot_index' not in st.session_state:
        st.session_state.current_lot_index = 0
    if 'selected_data' not in st.session_state:
        st.session_state.selected_data = pd.DataFrame()
    if 'selections' not in st.session_state:
        st.session_state.selections = {}
    if 'columns_validated' not in st.session_state:
        st.session_state.columns_validated = False

def get_default_indices(lot, lot_data):
    """
    Récupère les indices par défaut de début et de fin pour un lot donné.
    Initialise les indices si le lot n'est pas déjà dans les sélections.
    """
    if lot not in st.session_state.selections:
        st.session_state.selections[lot] = {
            'start_index': 0,
            'end_index': len(lot_data) - 1
        }
    return st.session_state.selections[lot]['start_index'], st.session_state.selections[lot]['end_index']
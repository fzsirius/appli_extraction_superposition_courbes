# page2.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_processing import load_data
import numpy as np

def app():
    st.title("Superposition de paramètres de plusieurs lots")
    
    # 1. Importer les données
    uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")
    separator = st.selectbox("Choisissez le séparateur", [",", ";"],index=0)

    if uploaded_file is not None:
        data = load_data(uploaded_file, separator)
        data = data.replace("", np.nan)
        st.session_state.page2_data = data
        st.session_state.page2_data_loaded = True
        st.success("Fichier CSV importé avec succès.")
    elif 'page2_data_loaded' in st.session_state and st.session_state.page2_data_loaded:
        data = st.session_state.page2_data
    else:
        st.warning("Veuillez importer un fichier CSV pour continuer.")
        st.stop()
    
    # 2. Sélectionner les colonnes nécessaires
    st.markdown("### Sélectionnez les colonnes nécessaires")
    
    if 'page2_lot_column' not in st.session_state:
        st.session_state.page2_lot_column = data.columns[0]
    if 'page2_date_column' not in st.session_state:
        st.session_state.page2_date_column = data.columns[1] if len(data.columns) > 1 else data.columns[0]
    
    lot_column = st.selectbox(
        "Choisir la colonne contenant les lots",
        options=data.columns,
        index=data.columns.tolist().index(st.session_state.page2_lot_column)
    )
    
    date_column = st.selectbox(
        "Choisir la colonne contenant les dates",
        options=data.columns,
        index=data.columns.tolist().index(st.session_state.page2_date_column)
    )
    
    # Bouton pour valider les colonnes sélectionnées
    if st.button("Valider les colonnes sélectionnées"):
        st.session_state.page2_columns_validated = True
        st.session_state.page2_lot_column = lot_column
        st.session_state.page2_date_column = date_column
        st.success("Colonnes validées avec succès !")
    
    # Vérifier si les colonnes sont validées
    if not st.session_state.get("page2_columns_validated", False):
        st.stop()
    
 #____________________J'ai modifié ceci car avant, on devait cliquer deux fois pour qu'un lot s'affiche   
    st.write("---")
    st.markdown("### Lots et paramètres à superposer")

    # Convertir en string pour éviter les erreurs
    data[lot_column] = data[lot_column].astype(str)
    lots = sorted(data[lot_column].unique())

    # Initialiser `st.session_state` proprement
    if "page2_selected_lots" not in st.session_state:
        st.session_state.page2_selected_lots = None  # Sélectionner tous les lots par défaut
    if "page2_selected_parameters" not in st.session_state:
        st.session_state.page2_selected_parameters = []

    # Colonnes pour sélectionner/désélectionner
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sélectionner tous les lots"):
            st.session_state.page2_selected_lots = lots

    with col2:
        if st.button("Désélectionner tous les lots"):
            st.session_state.page2_selected_lots = []

    #  Ne pas redéfinir `st.session_state.page2_selected_lots` manuellement
    selected_lots = st.multiselect(
        "Sélectionner les lots à superposer",
        options=lots,
        default=st.session_state.page2_selected_lots,
        key="page2_multiselect_lots"
    )

    # --- Sélection des paramètres ---
    parameters = [col for col in data.columns if col not in [lot_column, date_column]]

    selected_parameters = st.multiselect(
        "Sélectionner les paramètres à superposer",
        options=parameters,
        default=st.session_state.page2_selected_parameters,
        key="page2_multiselect_parameters"
    )

    # Ne pas redéfinir `st.session_state.page2_selected_parameters` manuellement

    # --- Affichage du graphique ---
    st.write("---")
    st.markdown("### Graphique Superposé")

    if selected_lots and selected_parameters:
        fig = go.Figure()

        for lot in selected_lots:
            lot_data = data[data[lot_column] == lot].copy()
            lot_data[date_column] = pd.to_datetime(lot_data[date_column], errors='coerce',dayfirst=False)
            lot_data = lot_data.dropna(subset=[date_column]).sort_values(date_column).reset_index(drop=True)

            if not lot_data.empty:
                start_time = lot_data[date_column].min()
                lot_data["time_since_start"] = (lot_data[date_column] - start_time).dt.total_seconds()

                for param in selected_parameters:
                    fig.add_trace(go.Scatter(
                        x=lot_data["time_since_start"],
                        y=lot_data[param],
                        mode="lines+markers",
                        name=f"{param} (Lot {lot})",
                        marker=dict(size=3),
                        line=dict(width=2)
                    ))

        fig.update_layout(
            title="Superposition des paramètres pour les lots sélectionnés",
            xaxis=dict(title="Temps relatif (secondes)", showgrid=True),
            yaxis=dict(title=selected_parameters[0] if selected_parameters else ""),
            template="plotly_white",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("Veuillez sélectionner au moins un lot et un paramètre pour afficher le graphique.")

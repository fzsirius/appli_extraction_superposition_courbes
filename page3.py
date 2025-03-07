import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_plotly_events import plotly_events
import data_processing as dp

def app():
    st.title("Découpage de courbes avec la souris")

    # --------------------------------------------------------------------------------
    # 1. Import des données
    # --------------------------------------------------------------------------------
    uploaded_file = st.file_uploader("Importer un fichier CSV", type=["csv"])
    separator = st.selectbox("Choisissez le séparateur", [",", ";"], index=0)

    if uploaded_file is None:
        st.info("Veuillez sélectionner un fichier CSV.")
        st.stop()

    # Charger le CSV
    data = dp.load_data(uploaded_file, separator)  
    st.success("Données chargées avec succès !")

    # --------------------------------------------------------------------------------
    # 2. Sélection des colonnes : lot, date, cible, overlay
    # --------------------------------------------------------------------------------
    st.markdown("### Sélection des colonnes")
    all_columns = data.columns.tolist()
    lot_column = st.selectbox("Colonne du lot", all_columns)
    date_column = st.selectbox("Colonne de date", all_columns)
    target_column = st.selectbox("Colonne à découper (cible)", all_columns)

    # Colonnes supplémentaires à superposer
    overlay_columns = st.multiselect(
        "Colonnes supplémentaires à superposer",
        [col for col in all_columns if col not in [lot_column, date_column, target_column]]
    )
     # -- ICI on enregistre ces infos dans st.session_state pour dp.add_selected_range()
    st.session_state["lot_column"] = lot_column
    st.session_state["date_column"] = date_column
    st.session_state["target_column"] = target_column
    st.session_state["overlay_columns"] = overlay_columns
    # --------------------------------------------------------------------------------
    # 3. Choix du lot + navigation
    # --------------------------------------------------------------------------------
    st.markdown("### Visualisation")
    lots = sorted(data[lot_column].unique())
    if "current_lot_index" not in st.session_state:
        st.session_state.current_lot_index = 0

    # Navigation par boutons Précédent/Suivant
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lot précédent"):
            st.session_state.current_lot_index = max(0, st.session_state.current_lot_index - 1)
    with col2:
        if st.button("Lot suivant"):
            st.session_state.current_lot_index = min(len(lots) - 1, st.session_state.current_lot_index + 1)

    # Recherche directe d'un lot via selectbox
    selected_lot = st.selectbox(
        "Rechercher un lot",
        options=lots,
        index=st.session_state.current_lot_index
    )
    # Synchroniser l'index du lot avec le selectbox
    if lots[st.session_state.current_lot_index] != selected_lot:
        st.session_state.current_lot_index = lots.index(selected_lot)

    current_lot = lots[st.session_state.current_lot_index]

    # Filtrer les données sur le lot courant
    lot_data = data[data[lot_column] == current_lot].copy().reset_index(drop=True)

    # Convertir la colonne date/temps en datetime 
    lot_data[date_column] = pd.to_datetime(lot_data[date_column], errors='coerce',dayfirst=True)

    # --------------------------------------------------------------------------------
    # 4. Initialisation / stockage des sélections à la souris
    # --------------------------------------------------------------------------------
    # Dans st.session_state, on stocke un dictionnaire { lot: [idx1, idx2] }
    if "mouse_selections" not in st.session_state:
        st.session_state.mouse_selections = {}

    # S'assurer que chaque lot a sa liste d'indices cliqués
    if current_lot not in st.session_state.mouse_selections:
        st.session_state.mouse_selections[current_lot] = []

    # Bouton pour réinitialiser la sélection de ce lot
    if st.button("Réinitialiser la sélection pour ce lot"):
        st.session_state.mouse_selections[current_lot] = []

    # --------------------------------------------------------------------------------
    # 5. Construction du graphique Plotly
    # --------------------------------------------------------------------------------
    fig = go.Figure()

    # Trace principale (colonne cible) - avec markers pour pouvoir cliquer
    fig.add_trace(go.Scatter(
        x=lot_data[date_column],
        y=lot_data[target_column],
        mode='lines+markers',
        marker=dict(size=2),  # Marker plus gros pour faciliter le clic
        name=f"{target_column} - Lot {current_lot}",
        customdata=lot_data.index,  # Permet de récupérer l'index lors du clic
        connectgaps=True,
        hovertemplate=(
            "Index: %{customdata}<br>"
            f"{date_column}: %{{x}}<br>"
            f"{target_column}: %{{y}}<extra></extra>"
        )
    ))

    # Ajout de colonnes supplémentaires sur axes décalés
    axis_positions = [
        0.1 + (0.8 / (len(overlay_columns) + 1)) * i
        for i in range(len(overlay_columns))
    ]
    for i, col in enumerate(overlay_columns):
        fig.add_trace(go.Scatter(
            x=lot_data[date_column],
            y=lot_data[col],
            mode='lines',  
            #marker=dict(size=6),
            name=f"{col} - Lot {current_lot}",
            customdata=lot_data.index,
            hovertemplate=(
                "Index: %{customdata}<br>"
                f"{date_column}: %{{x}}<br>"
                f"{col}: %{{y}}<extra></extra>"
            ),
            yaxis=f"y{i+2}"
        ))
        fig.update_layout(
            **{
                f"yaxis{i+2}": dict(
                    title=col,
                    overlaying="y",
                    side="right",
                    position=axis_positions[i]
                )
            }
        )

    # Configuration du layout
    fig.update_layout(
        clickmode='event+select',   # <-- pour activer le renvoi des données de clic
        hovermode='closest',
        title=f"Lot {current_lot}",
        xaxis=dict(
            title=date_column,
            rangeslider=dict(visible=False)  
        ),
        yaxis=dict(title=target_column),
        template="plotly_white",
        height=600
    )

    # --------------------------------------------------------------------------------
    # 6. Affichage du graphique + récupération des clics
    # --------------------------------------------------------------------------------
    selected_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        override_height=600,
        override_width="100%"
    )


    # Si l'utilisateur clique, on récupère l'index
    if selected_points:
        for pt in selected_points:
            # 1) Si "customdata" existe, on l'utilise
            if "customdata" in pt:
                idx_clicked = pt["customdata"]
            else:
                # 2) Sinon, fallback sur pointNumber
                idx_clicked = pt["pointNumber"]

            # Vérification
            st.write(f"**Point cliqué** → raw index = {idx_clicked}")
            
            if idx_clicked is not None:
                # On limite volontairement à 2 indices max (début/fin)
                if len(st.session_state.mouse_selections[current_lot]) < 2:
                    st.session_state.mouse_selections[current_lot].append(idx_clicked)

    # Affichage de la sélection actuelle pour le lot
    current_selection = st.session_state.mouse_selections[current_lot]
    if len(current_selection) == 0:
        st.info("Aucun point n'a été cliqué pour ce lot.")
    elif len(current_selection) == 1:
        st.info(f"Un seul point sélectionné (index = {current_selection[0]}). Cliquez sur un autre point pour définir la fin.")
    else:
        st.success(f"Deux points sélectionnés (index = {current_selection}).")

    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------
    # 7. Validation de la sélection pour extraction
    # --------------------------------------------------------------------------------

    # Désactivation du bouton si on n'a pas encore cliqué sur 2 points
    disable_validation = (len(current_selection) < 2)

    valider_btn = st.button(
        "Valider la sélection",
        disabled=disable_validation
    )

    if valider_btn:
        # Ici, on sait qu'il y a au moins 2 points, puisque le bouton était inactif avant.
        start_idx = min(current_selection)
        end_idx = max(current_selection)
        message = dp.add_selected_range(
            lot_data, start_idx, end_idx, current_lot
        )
        if "ajoutée" in message:
            st.success(message)
        else:
            st.error(message)


    # 8. Export CSV
    st.write("---")
    export_filename = st.text_input(
        "Nom du fichier CSV à exporter :",
        value=f"extractions_souris_{current_lot}.csv"
    )

    export_btn = st.button("Exporter toutes les sélections déjà validées")
    if export_btn:
        if "selected_data" in st.session_state and not st.session_state.selected_data.empty:
            csv_data = st.session_state.selected_data.to_csv(index=False)
            st.download_button(
                label="Télécharger les données sélectionnées",
                data=csv_data,
                file_name=export_filename,
                mime="text/csv"
            )
        else:
            st.warning("Aucune sélection validée à exporter pour le moment.")
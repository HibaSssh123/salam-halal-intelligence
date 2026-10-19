import streamlit as st

from src.config import APP_NAME, APP_NOTICE, APP_SUBTITLE
from src.database.connection import initialize_database
from src.database.repositories import Repository
from src.simulation.data_generator import seed_demo_data
from src.ui.about_page import render_about_page
from src.ui.batches_page import render_batches_page
from src.ui.cold_chain_page import render_cold_chain_page
from src.ui.dashboard import render_dashboard
from src.ui.expiration_page import render_expiration_page
from src.ui.forecasting_page import render_forecasting_page
from src.ui.inventory_page import render_inventory_page


st.set_page_config(page_title=APP_NAME, layout="wide")
initialize_database()
repo = Repository()
seed_demo_data(repo, force_reset=False)

st.markdown(
    """
<style>
[data-testid="stSidebar"] {background-color: #0e1b3d;}
[data-testid="stSidebar"] * {color: #f4f7ff !important;}
.main .block-container {background: #f7f9fc; border-radius: 12px; padding: 1.5rem 2rem;}
.stButton>button {background-color: #1f7a4c; color: white; border: none;}
</style>
    """,
    unsafe_allow_html=True,
)

st.title(APP_NAME)
st.caption(APP_SUBTITLE)
st.warning(APP_NOTICE)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Aller à",
        [
            "Tableau de bord",
            "Production et traçabilité",
            "Gestion des stocks",
            "Dates de péremption",
            "Surveillance de la chaîne du froid",
            "Prévision de la demande",
            "À propos du projet",
        ],
    )
    st.markdown("---")
    if st.button("Réinitialiser / régénérer les données de démonstration"):
        seed_demo_data(repo, force_reset=True)
        st.success("Données de démonstration recréées (SIMULATED DATA).")

if page == "Tableau de bord":
    render_dashboard(repo)
elif page == "Production et traçabilité":
    render_batches_page(repo)
elif page == "Gestion des stocks":
    render_inventory_page(repo)
elif page == "Dates de péremption":
    render_expiration_page(repo)
elif page == "Surveillance de la chaîne du froid":
    render_cold_chain_page(repo)
elif page == "Prévision de la demande":
    render_forecasting_page(repo)
else:
    render_about_page()

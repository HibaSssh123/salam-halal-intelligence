import streamlit as st


def render_about_page():
    st.subheader("À propos du projet")
    st.markdown(
        """
**SALAM HALAL INTELLIGENCE** est un prototype académique de suivi industriel et d'aide à la décision.

- Toutes les données générées dans l'application sont explicitement marquées **SIMULATED DATA**.
- Ce projet ne prétend pas représenter des données opérationnelles réelles de Salam Halal.
- Les alertes de péremption et de chaîne du froid sont des aides administratives.
- Le module de prévision illustre une démarche méthodologique (split chronologique, baseline, modèle ML, métriques MAE/RMSE).
        """
    )

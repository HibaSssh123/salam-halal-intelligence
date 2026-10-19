import pandas as pd
import streamlit as st

from src.processing.expiration import expiration_alerts


def render_expiration_page(repo):
    st.subheader("Dates de péremption")
    st.caption("Alerte administrative de suivi interne, sans valeur de certification sanitaire.")

    warning_days = st.slider("Nombre de jours pour alerte anticipée", min_value=1, max_value=60, value=7)
    batches = repo.list_batches()
    if not batches:
        st.info("Aucun lot disponible.")
        return

    alerts = expiration_alerts(batches, warning_days)

    st.markdown("#### Lots expirés")
    st.dataframe(pd.DataFrame(alerts["expired"]) if alerts["expired"] else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

    st.markdown("#### Lots proches de péremption")
    st.dataframe(pd.DataFrame(alerts["expiring_soon"]) if alerts["expiring_soon"] else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

    st.markdown("#### Lots sans date de péremption")
    st.dataframe(pd.DataFrame(alerts["missing_expiration"]) if alerts["missing_expiration"] else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

    st.markdown("#### Lots à revoir")
    st.dataframe(pd.DataFrame(alerts["review"]) if alerts["review"] else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

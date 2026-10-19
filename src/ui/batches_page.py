from datetime import date

import pandas as pd
import streamlit as st

from src.config import BATCH_STATUSES
from src.processing.validation import validate_batch_input


def render_batches_page(repo):
    st.subheader("Production et traçabilité")
    products = repo.list_products()
    if not products:
        st.info("Aucun produit disponible. Générez les données de démonstration depuis la barre latérale.")
        return

    st.markdown("#### Créer un lot")
    with st.form("batch_form"):
        batch_code = st.text_input("Code unique du lot")
        product_label_to_id = {f"{p['name']} ({p['category']})": p["id"] for p in products}
        product_label = st.selectbox("Produit", list(product_label_to_id.keys()))
        prod_date = st.date_input("Date de production", value=date.today())
        exp_date = st.date_input("Date de péremption", value=date.today())
        qty = st.number_input("Quantité produite (kg)", min_value=0.0, step=1.0)
        status = st.selectbox("Statut", BATCH_STATUSES)
        notes = st.text_area("Notes (optionnel)")
        submitted = st.form_submit_button("Enregistrer le lot")

    if submitted:
        try:
            existing = {b["batch_code"] for b in repo.list_batches()}
            normalized_batch_code = validate_batch_input(existing, batch_code, qty, prod_date, exp_date)
            repo.create_batch_atomic(
                batch_code=normalized_batch_code,
                product_id=product_label_to_id[product_label],
                production_date=prod_date.isoformat(),
                expiration_date=exp_date.isoformat(),
                quantity_produced=qty,
                status=status,
                notes=notes,
            )
            st.success("Lot enregistré avec succès.")
        except Exception as exc:
            st.error(f"Erreur de validation : {exc}")

    st.markdown("#### Recherche et filtres")
    col1, col2, col3 = st.columns(3)
    search = col1.text_input("Recherche (code/notes)")
    status_filter = col2.selectbox("Filtre statut", [""] + BATCH_STATUSES)
    product_filter = col3.selectbox("Filtre produit", [""] + [p["name"] for p in products])
    product_id = next((p["id"] for p in products if p["name"] == product_filter), None)

    rows = repo.list_batches(search=search, status=status_filter, product_id=product_id)
    if not rows:
        st.info("Aucun lot correspondant.")
        return

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    ids = {f"{r['batch_code']} ({r['product_name']})": r["id"] for r in rows}
    selected = st.selectbox("Détails du lot", list(ids.keys()))
    details = repo.get_batch_details(ids[selected])
    if details:
        st.markdown("#### Détail du lot")
        st.json({k: v for k, v in details.items() if k != "history"})
        st.markdown("#### Historique des mouvements")
        st.dataframe(pd.DataFrame(details["history"]) if details["history"] else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

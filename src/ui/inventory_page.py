import pandas as pd
import streamlit as st


def render_inventory_page(repo):
    st.subheader("Gestion des stocks")
    st.caption("Portée actuelle : stock des produits finis.")

    products = repo.list_products()
    if not products:
        st.info("Aucun produit disponible.")
        return

    with st.form("inventory_movement_form"):
        product_map = {p["name"]: p["id"] for p in products}
        product_name = st.selectbox("Produit", list(product_map.keys()))
        movement_type = st.selectbox("Type de mouvement", ["entrée", "sortie"])
        quantity = st.number_input("Quantité (kg)", min_value=0.0, step=1.0)
        movement_date = st.date_input("Date du mouvement")
        reason = st.text_input("Raison")
        submit = st.form_submit_button("Ajouter le mouvement")

    if submit:
        try:
            repo.record_inventory_movement(
                product_id=product_map[product_name],
                batch_id=None,
                movement_type=movement_type,
                quantity=quantity,
                movement_date=movement_date.isoformat(),
                reason=reason or "Mouvement manuel",
            )
            st.success("Mouvement enregistré.")
        except Exception as exc:
            st.error(str(exc))

    product_filter = st.selectbox("Filtrer par produit", ["Tous"] + [p["name"] for p in products])
    pid = product_map.get(product_filter) if product_filter != "Tous" else None

    movements = repo.list_inventory_movements(product_id=pid)
    stocks = repo.get_stock_levels()
    low = [r for r in stocks if r["alerte_stock_bas"]]

    st.markdown("#### Niveaux de stock")
    st.dataframe(pd.DataFrame(stocks), use_container_width=True)
    if low:
        st.warning(f"{len(low)} produit(s) sous le seuil minimal.")

    st.markdown("#### Historique des mouvements")
    dmov = pd.DataFrame(movements)
    st.dataframe(dmov if not dmov.empty else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

    if not dmov.empty:
        csv = dmov.to_csv(index=False).encode("utf-8")
        st.download_button("Exporter les mouvements (CSV)", data=csv, file_name="mouvements_stock.csv", mime="text/csv")

import pandas as pd
import plotly.express as px
import streamlit as st

from src.processing.cold_chain import analyze_temperature_measurements
from src.processing.expiration import expiration_alerts


def render_dashboard(repo):
    st.subheader("Tableau de bord")
    metrics = repo.dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nombre de lots enregistrés", int(metrics["nombre_lots"]))
    c2.metric("Quantité totale produite (kg)", f"{metrics['quantite_totale']:.1f}")
    c3.metric("Stock disponible (kg)", f"{metrics['stock_disponible']:.1f}")
    c4.metric("Nombre d'alertes actives", int(metrics["alertes_actives"]))

    batches = repo.list_batches()
    movements = repo.list_inventory_movements(limit=100)
    temps = repo.list_temperatures(limit=300)
    stocks = repo.get_stock_levels()

    if batches:
        dfb = pd.DataFrame(batches)
        prod_daily = dfb.groupby("production_date", as_index=False)["quantity_produced"].sum()
        st.plotly_chart(px.bar(prod_daily, x="production_date", y="quantity_produced", title="Production quotidienne"), use_container_width=True)

        repartition = dfb.groupby("product_name", as_index=False)["quantity_produced"].sum()
        st.plotly_chart(px.pie(repartition, names="product_name", values="quantity_produced", title="Répartition des produits"), use_container_width=True)
    else:
        st.info("Aucun lot enregistré pour le moment.")

    if temps:
        dft = pd.DataFrame(temps)
        dft["measured_at"] = pd.to_datetime(dft["measured_at"])
        dft = dft.sort_values("measured_at")
        fig = px.line(dft, x="measured_at", y="temperature_c", color="location", title="Évolution des températures")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun relevé de température disponible.")

    if stocks:
        dfs = pd.DataFrame(stocks)
        st.plotly_chart(px.bar(dfs, x="product", y="stock_actuel", title="Niveau des stocks par produit"), use_container_width=True)

    alerts = expiration_alerts(batches, warning_days=7)
    temp_analysis = analyze_temperature_measurements(temps)

    st.markdown("### Lots proches de leur date de péremption")
    near = alerts["expiring_soon"]
    st.dataframe(pd.DataFrame(near) if near else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

    st.markdown("### Derniers mouvements de stock")
    st.dataframe(pd.DataFrame(movements[:15]) if movements else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

    st.markdown("### Derniers relevés de température")
    st.dataframe(pd.DataFrame(temps[:15]) if temps else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

    st.markdown("### Alertes nécessitant une vérification")
    alerts_lines = []
    if alerts["expired"]:
        alerts_lines.append(f"- {len(alerts['expired'])} lot(s) expiré(s)")
    if alerts["expiring_soon"]:
        alerts_lines.append(f"- {len(alerts['expiring_soon'])} lot(s) proche(s) de péremption")
    if temp_analysis["out_of_range_count"]:
        alerts_lines.append(f"- {temp_analysis['out_of_range_count']} mesure(s) de température hors plage")
    low_stock = [s for s in stocks if s["alerte_stock_bas"]]
    if low_stock:
        alerts_lines.append(f"- {len(low_stock)} produit(s) en stock bas")

    if alerts_lines:
        st.warning("\n".join(alerts_lines))
    else:
        st.success("Aucune alerte critique pour le moment.")

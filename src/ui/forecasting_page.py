import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.forecasting.demand_model import run_forecast_experiment


def render_forecasting_page(repo):
    st.subheader("Prévision de la demande")
    st.caption("Module académique : ventes simulées, résultats non opérationnels pour une entreprise réelle.")

    products = repo.list_products()
    if not products:
        st.info("Aucun produit disponible.")
        return

    product_map = {"Tous": None}
    product_map.update({p["name"]: p["id"] for p in products})
    selected = st.selectbox("Produit", list(product_map.keys()))
    sales_df = repo.sales_dataframe(product_map[selected])

    result = run_forecast_experiment(sales_df)
    if result.mode == "insufficient":
        st.warning(result.message)
        return

    if result.mode == "fallback":
        st.warning(result.message)
    else:
        st.success(result.message)

    if result.metrics:
        st.write(
            {
                "MAE": round(result.metrics.get("mae", 0.0), 3),
                "RMSE": round(result.metrics.get("rmse", 0.0), 3),
                "MAE baseline": round(result.metrics.get("baseline_mae", result.metrics.get("mae", 0.0)), 3),
                "RMSE baseline": round(result.metrics.get("baseline_rmse", result.metrics.get("rmse", 0.0)), 3),
            }
        )

    if not result.eval_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result.eval_df["sale_date"], y=result.eval_df["quantity_sold"], name="Réel", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=result.eval_df["sale_date"], y=result.eval_df["pred"], name="Prédit", mode="lines+markers"))
        if "baseline" in result.eval_df:
            fig.add_trace(go.Scatter(x=result.eval_df["sale_date"], y=result.eval_df["baseline"], name="Baseline", mode="lines"))
        fig.update_layout(title="Réel vs Prédit (jeu de test chronologique)")
        st.plotly_chart(fig, use_container_width=True)

    if not result.future_df.empty:
        st.markdown("#### Prévision de démonstration sur 7 jours")
        st.dataframe(result.future_df, use_container_width=True)

    st.info("Limites : données simulées, simplification des variables métier, pas d'engagement sur la demande réelle de Salam Halal.")

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.processing.cold_chain import analyze_temperature_measurements


def render_cold_chain_page(repo):
    st.subheader("Surveillance de la chaîne du froid")
    st.caption("Les seuils min/max sont configurables selon le contexte et ne sont pas universels.")

    with st.form("temp_form"):
        location = st.text_input("Emplacement")
        measured_at = st.text_input("Horodatage ISO (AAAA-MM-JJTHH:MM:SS)")
        if not measured_at:
            measured_at = pd.Timestamp.now().isoformat(timespec="seconds")
        temperature_c = st.number_input("Température (°C)", step=0.1)
        min_c = st.number_input("Seuil minimum (°C)", value=0.0, step=0.1)
        max_c = st.number_input("Seuil maximum (°C)", value=4.0, step=0.1)
        source = st.text_input("Source", value="Saisie manuelle")
        submit = st.form_submit_button("Ajouter le relevé")
    if submit:
        try:
            repo.add_temperature_measurement(location, measured_at, temperature_c, min_c, max_c, source)
            st.success("Relevé ajouté.")
        except Exception as exc:
            st.error(f"Erreur : {exc}")

    rows = repo.list_temperatures(limit=500)
    if not rows:
        st.info("Aucun relevé disponible.")
        return

    analysis = analyze_temperature_measurements(rows)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Min (°C)", f"{analysis['min_temp']:.2f}")
    c2.metric("Max (°C)", f"{analysis['max_temp']:.2f}")
    c3.metric("Moyenne (°C)", f"{analysis['avg_temp']:.2f}")
    c4.metric("Hors plage", analysis["out_of_range_count"])
    c5.metric("% dans la plage", f"{analysis['within_range_pct']:.1f}%")

    df = pd.DataFrame(rows)
    df["measured_at"] = pd.to_datetime(df["measured_at"])
    df = df.sort_values("measured_at")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["measured_at"], y=df["temperature_c"], mode="lines+markers", name="Température"))
    fig.add_trace(go.Scatter(x=df["measured_at"], y=df["minimum_allowed_c"], mode="lines", name="Seuil min", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=df["measured_at"], y=df["maximum_allowed_c"], mode="lines", name="Seuil max", line=dict(dash="dash")))
    fig.update_layout(title="Évolution de la température et seuils")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Relevés à revoir")
    st.dataframe(pd.DataFrame(analysis["out_of_range_rows"]) if analysis["out_of_range_rows"] else pd.DataFrame(columns=["Aucune donnée"]), use_container_width=True)

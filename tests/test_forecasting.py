from datetime import date, timedelta

import pandas as pd

from src.forecasting.demand_model import run_forecast_experiment


def test_forecasting_sufficient_data_ml_or_fallback_with_metrics():
    start = date.today() - timedelta(days=60)
    rows = []
    for i in range(61):
        d = start + timedelta(days=i)
        rows.append({"sale_date": d.isoformat(), "product_id": 1, "product_name": "P1", "quantity_sold": 20 + (i % 7)})
    df = pd.DataFrame(rows)
    result = run_forecast_experiment(df)
    assert result.mode in {"ml", "fallback"}
    assert "mae" in result.metrics
    assert "rmse" in result.metrics


def test_forecasting_insufficient_data_fallback_or_insufficient():
    start = date.today() - timedelta(days=5)
    rows = []
    for i in range(6):
        d = start + timedelta(days=i)
        rows.append({"sale_date": d.isoformat(), "product_id": 1, "product_name": "P1", "quantity_sold": 10})
    df = pd.DataFrame(rows)
    result = run_forecast_experiment(df)
    assert result.mode in {"fallback", "insufficient"}

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.forecasting.features import build_time_series_features


@dataclass
class ForecastResult:
    mode: str
    message: str
    metrics: dict
    eval_df: pd.DataFrame
    future_df: pd.DataFrame


def _baseline_predict(train: pd.Series, test_len: int) -> np.ndarray:
    window = min(7, len(train))
    avg = float(train.tail(window).mean()) if len(train) else 0.0
    return np.array([avg] * test_len)


def run_forecast_experiment(sales_df: pd.DataFrame) -> ForecastResult:
    feat = build_time_series_features(sales_df)
    if feat.empty:
        return ForecastResult(
            mode="insufficient",
            message="Données insuffisantes : aucune vente disponible.",
            metrics={},
            eval_df=pd.DataFrame(),
            future_df=pd.DataFrame(),
        )

    series = feat.groupby("sale_date", as_index=False)["quantity_sold"].sum().sort_values("sale_date")
    series["lag_1"] = series["quantity_sold"].shift(1)
    series["lag_7"] = series["quantity_sold"].shift(7)
    series["dayofweek"] = series["sale_date"].dt.dayofweek
    series["month"] = series["sale_date"].dt.month
    series["day"] = series["sale_date"].dt.day
    model_df = series.dropna().copy()

    if len(model_df) < 24:
        baseline = _baseline_predict(series["quantity_sold"], min(7, max(1, len(series) // 3)))
        test_slice = series.tail(len(baseline)).copy()
        test_slice["pred"] = baseline
        mae = mean_absolute_error(test_slice["quantity_sold"], test_slice["pred"])
        rmse = np.sqrt(mean_squared_error(test_slice["quantity_sold"], test_slice["pred"]))

        future_dates = pd.date_range(series["sale_date"].max() + pd.Timedelta(days=1), periods=7, freq="D")
        future = pd.DataFrame({"sale_date": future_dates, "forecast": [float(baseline[-1])] * 7})

        return ForecastResult(
            mode="fallback",
            message="Données limitées : utilisation d'une moyenne mobile de démonstration (pas d'entraînement ML robuste).",
            metrics={"mae": float(mae), "rmse": float(rmse), "baseline": "moving_average"},
            eval_df=test_slice,
            future_df=future,
        )

    feature_cols = ["lag_1", "lag_7", "dayofweek", "month", "day"]
    split_index = int(len(model_df) * 0.8)
    train = model_df.iloc[:split_index]
    test = model_df.iloc[split_index:]

    if len(test) == 0:
        return ForecastResult(
            mode="insufficient",
            message="Données insuffisantes après séparation chronologique.",
            metrics={},
            eval_df=pd.DataFrame(),
            future_df=pd.DataFrame(),
        )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(train[feature_cols], train["quantity_sold"])
    pred = model.predict(test[feature_cols])

    baseline_pred = test["lag_1"].fillna(train["quantity_sold"].mean())

    mae = mean_absolute_error(test["quantity_sold"], pred)
    rmse = np.sqrt(mean_squared_error(test["quantity_sold"], pred))
    baseline_mae = mean_absolute_error(test["quantity_sold"], baseline_pred)
    baseline_rmse = np.sqrt(mean_squared_error(test["quantity_sold"], baseline_pred))

    eval_df = test[["sale_date", "quantity_sold"]].copy()
    eval_df["pred"] = pred
    eval_df["baseline"] = baseline_pred.values

    last_known = series.copy()
    future_rows = []
    lag_1 = float(last_known.iloc[-1]["quantity_sold"])
    lag_7_vals = list(last_known["quantity_sold"].tail(7).values)
    for i in range(1, 8):
        d = pd.to_datetime(last_known.iloc[-1]["sale_date"]) + pd.Timedelta(days=i)
        lag_7 = float(lag_7_vals[-7]) if len(lag_7_vals) >= 7 else float(np.mean(lag_7_vals))
        x = pd.DataFrame([{"lag_1": lag_1, "lag_7": lag_7, "dayofweek": d.dayofweek, "month": d.month, "day": d.day}])
        y = float(model.predict(x)[0])
        future_rows.append({"sale_date": d, "forecast": y})
        lag_7_vals.append(y)
        lag_1 = y

    future_df = pd.DataFrame(future_rows)

    return ForecastResult(
        mode="ml",
        message="Modèle RandomForest entraîné sur données chronologiques simulées.",
        metrics={
            "mae": float(mae),
            "rmse": float(rmse),
            "baseline_mae": float(baseline_mae),
            "baseline_rmse": float(baseline_rmse),
        },
        eval_df=eval_df,
        future_df=future_df,
    )

import pandas as pd


def build_time_series_features(sales_df: pd.DataFrame) -> pd.DataFrame:
    if sales_df.empty:
        return pd.DataFrame()
    df = sales_df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"]) 
    agg = df.groupby(["sale_date", "product_id", "product_name"], as_index=False)["quantity_sold"].sum()
    agg = agg.sort_values(["product_id", "sale_date"])
    agg["dayofweek"] = agg["sale_date"].dt.dayofweek
    agg["month"] = agg["sale_date"].dt.month
    agg["day"] = agg["sale_date"].dt.day
    agg["lag_1"] = agg.groupby("product_id")["quantity_sold"].shift(1)
    agg["lag_7"] = agg.groupby("product_id")["quantity_sold"].shift(7)
    agg["rolling_7"] = agg.groupby("product_id")["quantity_sold"].shift(1).rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)
    return agg

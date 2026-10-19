from typing import List

import numpy as np


def analyze_temperature_measurements(rows: List[dict]) -> dict:
    if not rows:
        return {
            "min_temp": None,
            "max_temp": None,
            "avg_temp": None,
            "out_of_range_count": 0,
            "within_range_pct": 0.0,
            "out_of_range_rows": [],
        }

    temps = np.array([float(r["temperature_c"]) for r in rows], dtype=float)
    out_of_range = [
        r
        for r in rows
        if float(r["temperature_c"]) < float(r["minimum_allowed_c"])
        or float(r["temperature_c"]) > float(r["maximum_allowed_c"])
    ]
    within = len(rows) - len(out_of_range)

    return {
        "min_temp": float(np.min(temps)),
        "max_temp": float(np.max(temps)),
        "avg_temp": float(np.mean(temps)),
        "out_of_range_count": len(out_of_range),
        "within_range_pct": (within / len(rows)) * 100,
        "out_of_range_rows": out_of_range,
    }

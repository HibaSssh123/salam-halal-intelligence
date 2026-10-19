from src.processing.cold_chain import analyze_temperature_measurements


def test_cold_chain_threshold_detection():
    rows = [
        {"temperature_c": 2.0, "minimum_allowed_c": 0.0, "maximum_allowed_c": 4.0},
        {"temperature_c": 5.2, "minimum_allowed_c": 0.0, "maximum_allowed_c": 4.0},
    ]
    out = analyze_temperature_measurements(rows)
    assert out["out_of_range_count"] == 1
    assert out["within_range_pct"] == 50.0

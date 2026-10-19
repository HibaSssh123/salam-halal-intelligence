from datetime import date, timedelta

from src.processing.expiration import expiration_alerts


def test_expiration_alerts_detects_expired_and_soon():
    today = date.today()
    rows = [
        {"batch_code": "A", "expiration_date": (today - timedelta(days=1)).isoformat(), "status": "Terminé"},
        {"batch_code": "B", "expiration_date": (today + timedelta(days=2)).isoformat(), "status": "Terminé"},
        {"batch_code": "C", "expiration_date": None, "status": "Bloqué"},
    ]
    out = expiration_alerts(rows, warning_days=7)
    assert len(out["expired"]) == 1
    assert len(out["expiring_soon"]) == 1
    assert len(out["missing_expiration"]) == 1
    assert len(out["review"]) >= 1

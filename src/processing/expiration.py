from datetime import date, timedelta
from typing import List


def expiration_alerts(batch_rows: List[dict], warning_days: int) -> dict:
    today = date.today()
    soon_limit = today + timedelta(days=warning_days)

    expired = []
    soon = []
    missing = []
    review = []

    for row in batch_rows:
        exp = row.get("expiration_date")
        status = row.get("status", "")
        if not exp:
            missing.append(row)
            review.append(row)
            continue
        exp_date = date.fromisoformat(str(exp))
        if exp_date < today:
            expired.append(row)
        elif today <= exp_date <= soon_limit:
            soon.append(row)
        if status in {"Bloqué", "Expiré"}:
            review.append(row)

    return {
        "expired": expired,
        "expiring_soon": soon,
        "missing_expiration": missing,
        "review": review,
    }

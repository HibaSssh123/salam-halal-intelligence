from typing import Iterable, List

from src.config import INCOMING_TYPES


def calculate_stock(movements: Iterable[dict]) -> float:
    stock = 0.0
    for movement in movements:
        qty = float(movement["quantity"])
        if movement["movement_type"] in INCOMING_TYPES:
            stock += qty
        else:
            stock -= qty
    return stock


def compute_low_stock_alerts(stock_rows: List[dict]) -> List[dict]:
    return [r for r in stock_rows if float(r["stock_actuel"]) < float(r["minimum_stock_level"])]

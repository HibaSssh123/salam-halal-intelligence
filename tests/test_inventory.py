from datetime import date, timedelta

import pytest

from src.database.connection import initialize_database
from src.database.repositories import Repository


def test_inventory_balance_and_negative_prevention(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    repo = Repository(db_path)

    pid = repo.create_product("Produit Stock", "Cat", "kg", 20)
    repo.create_batch_atomic("LOT-STOCK-1", pid, date.today().isoformat(), (date.today() + timedelta(days=10)).isoformat(), 100, "Terminé")

    repo.record_inventory_movement(pid, None, "sortie", 30, date.today().isoformat(), "Vente")
    levels = repo.get_stock_levels()
    stock = [r for r in levels if r["product_id"] == pid][0]["stock_actuel"]
    assert stock == pytest.approx(70)

    with pytest.raises(ValueError):
        repo.record_inventory_movement(pid, None, "sortie", 1000, date.today().isoformat(), "Retrait excessif")

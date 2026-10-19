import sqlite3
from datetime import date, timedelta

import pytest

from src.database.connection import initialize_database
from src.database.repositories import Repository
from src.processing.validation import validate_batch_input


def test_database_initialization_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    counts = repo.counts()
    assert set(counts.keys()) == {"products", "batches", "inventory_movements", "temperature_measurements", "sales"}


def test_unique_batch_code_enforced(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    pid = repo.create_product("Produit A", "Catégorie", "kg", 10)

    repo.create_batch_atomic("L001", pid, date.today().isoformat(), (date.today() + timedelta(days=5)).isoformat(), 10, "Terminé")
    with pytest.raises(sqlite3.IntegrityError):
        repo.create_batch_atomic("L001", pid, date.today().isoformat(), (date.today() + timedelta(days=7)).isoformat(), 12, "Terminé")


def test_invalid_quantity_and_dates_validation():
    with pytest.raises(ValueError):
        validate_batch_input(set(), "L1", 0, date.today(), date.today())

    with pytest.raises(ValueError):
        validate_batch_input(set(), "L2", 10, date.today(), date.today() - timedelta(days=1))

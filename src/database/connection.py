import sqlite3
from pathlib import Path
from typing import Optional

from src.config import DB_PATH
from src.database.schema import create_schema


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = Path(db_path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as conn:
        create_schema(conn)

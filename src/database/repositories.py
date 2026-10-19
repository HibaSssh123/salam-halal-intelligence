from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.config import INCOMING_TYPES, OUTGOING_TYPES
from src.database.connection import get_connection


@dataclass
class Repository:
    db_path: Optional[Path] = None

    def _conn(self):
        return get_connection(self.db_path)

    def list_products(self) -> List[dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
            return [dict(r) for r in rows]

    def create_product(self, name: str, category: str, unit: str = "kg", minimum_stock_level: float = 0.0) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO products(name, category, unit, minimum_stock_level)
                VALUES (?, ?, ?, ?)
                """,
                (name, category, unit, minimum_stock_level),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_product(self, product_id: int) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            return dict(row) if row else None

    def create_batch_atomic(
        self,
        batch_code: str,
        product_id: int,
        production_date: str,
        expiration_date: Optional[str],
        quantity_produced: float,
        status: str,
        notes: str = "",
    ) -> int:
        with self._conn() as conn:
            conn.execute("BEGIN")
            cur = conn.execute(
                """
                INSERT INTO batches(batch_code, product_id, production_date, expiration_date, quantity_produced, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (batch_code, product_id, production_date, expiration_date, quantity_produced, status, notes),
            )
            batch_id = int(cur.lastrowid)
            conn.execute(
                """
                INSERT INTO inventory_movements(product_id, batch_id, movement_type, quantity, movement_date, reason)
                VALUES (?, ?, 'production', ?, ?, ?)
                """,
                (product_id, batch_id, quantity_produced, production_date, "Entrée automatique issue de la production (SIMULATED DATA si démonstration)"),
            )
            conn.commit()
            return batch_id

    def list_batches(
        self,
        search: str = "",
        status: str = "",
        product_id: Optional[int] = None,
    ) -> List[dict]:
        query = """
            SELECT b.*, p.name AS product_name
            FROM batches b
            JOIN products p ON p.id = b.product_id
            WHERE 1=1
        """
        params: List[Any] = []
        if search:
            query += " AND (b.batch_code LIKE ? OR COALESCE(b.notes,'') LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        if status:
            query += " AND b.status = ?"
            params.append(status)
        if product_id:
            query += " AND b.product_id = ?"
            params.append(product_id)
        query += " ORDER BY b.production_date DESC, b.id DESC"

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_batch_details(self, batch_id: int) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT b.*, p.name AS product_name, p.category, p.unit
                FROM batches b JOIN products p ON p.id = b.product_id
                WHERE b.id = ?
                """,
                (batch_id,),
            ).fetchone()
            if not row:
                return None
            movements = conn.execute(
                """
                SELECT * FROM inventory_movements
                WHERE batch_id = ?
                ORDER BY movement_date DESC, id DESC
                """,
                (batch_id,),
            ).fetchall()
            payload = dict(row)
            payload["history"] = [dict(m) for m in movements]
            return payload

    def record_inventory_movement(
        self,
        product_id: int,
        batch_id: Optional[int],
        movement_type: str,
        quantity: float,
        movement_date: str,
        reason: str,
    ) -> int:
        with self._conn() as conn:
            if movement_type in OUTGOING_TYPES:
                current = self._stock_for_product_conn(conn, product_id)
                if quantity > current:
                    raise ValueError("Stock insuffisant : retrait impossible sans stock négatif.")
            cur = conn.execute(
                """
                INSERT INTO inventory_movements(product_id, batch_id, movement_type, quantity, movement_date, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (product_id, batch_id, movement_type, quantity, movement_date, reason),
            )
            conn.commit()
            return int(cur.lastrowid)

    def _stock_for_product_conn(self, conn, product_id: int) -> float:
        rows = conn.execute(
            "SELECT movement_type, quantity FROM inventory_movements WHERE product_id = ?",
            (product_id,),
        ).fetchall()
        stock = 0.0
        for row in rows:
            if row["movement_type"] in INCOMING_TYPES:
                stock += row["quantity"]
            else:
                stock -= row["quantity"]
        return stock

    def get_stock_levels(self) -> List[dict]:
        with self._conn() as conn:
            products = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
            out = []
            for p in products:
                stock = self._stock_for_product_conn(conn, p["id"])
                out.append(
                    {
                        "product_id": p["id"],
                        "product": p["name"],
                        "minimum_stock_level": p["minimum_stock_level"],
                        "stock_actuel": stock,
                        "alerte_stock_bas": stock < p["minimum_stock_level"],
                    }
                )
            return out

    def list_inventory_movements(self, product_id: Optional[int] = None, limit: int = 200) -> List[dict]:
        query = """
            SELECT m.*, p.name AS product_name, b.batch_code
            FROM inventory_movements m
            JOIN products p ON p.id = m.product_id
            LEFT JOIN batches b ON b.id = m.batch_id
            WHERE 1=1
        """
        params: List[Any] = []
        if product_id:
            query += " AND m.product_id = ?"
            params.append(product_id)
        query += " ORDER BY m.movement_date DESC, m.id DESC LIMIT ?"
        params.append(limit)

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def add_temperature_measurement(
        self,
        location: str,
        measured_at: str,
        temperature_c: float,
        minimum_allowed_c: float,
        maximum_allowed_c: float,
        source: str,
    ) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO temperature_measurements(location, measured_at, temperature_c, minimum_allowed_c, maximum_allowed_c, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (location, measured_at, temperature_c, minimum_allowed_c, maximum_allowed_c, source),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_temperatures(self, limit: int = 500) -> List[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM temperature_measurements ORDER BY measured_at DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def add_sale(self, product_id: int, sale_date: str, quantity_sold: float) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO sales(product_id, sale_date, quantity_sold) VALUES (?, ?, ?)",
                (product_id, sale_date, quantity_sold),
            )
            conn.commit()
            return int(cur.lastrowid)

    def sales_dataframe(self, product_id: Optional[int] = None) -> pd.DataFrame:
        query = """
            SELECT s.sale_date, s.product_id, p.name AS product_name, SUM(s.quantity_sold) AS quantity_sold
            FROM sales s
            JOIN products p ON p.id = s.product_id
            WHERE 1=1
        """
        params: List[Any] = []
        if product_id:
            query += " AND s.product_id = ?"
            params.append(product_id)
        query += " GROUP BY s.sale_date, s.product_id, p.name ORDER BY s.sale_date"

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        if not rows:
            return pd.DataFrame(columns=["sale_date", "product_id", "product_name", "quantity_sold"])
        return pd.DataFrame([dict(r) for r in rows])

    def dashboard_metrics(self) -> Dict[str, float]:
        with self._conn() as conn:
            total_batches = conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
            total_quantity = conn.execute("SELECT COALESCE(SUM(quantity_produced),0) FROM batches").fetchone()[0]
            stock_total = sum(row["stock_actuel"] for row in self.get_stock_levels())
            near_expiry = conn.execute(
                """
                SELECT COUNT(*) FROM batches
                WHERE expiration_date IS NOT NULL
                AND date(expiration_date) <= date('now', '+7 day')
                AND date(expiration_date) >= date('now')
                """
            ).fetchone()[0]
            expired = conn.execute(
                "SELECT COUNT(*) FROM batches WHERE expiration_date IS NOT NULL AND date(expiration_date) < date('now')"
            ).fetchone()[0]
            temp_alerts = conn.execute(
                """
                SELECT COUNT(*) FROM temperature_measurements
                WHERE temperature_c < minimum_allowed_c OR temperature_c > maximum_allowed_c
                """
            ).fetchone()[0]
            low_stock = sum(1 for s in self.get_stock_levels() if s["alerte_stock_bas"])

        return {
            "nombre_lots": total_batches,
            "quantite_totale": float(total_quantity),
            "stock_disponible": float(stock_total),
            "alertes_actives": int(near_expiry + expired + temp_alerts + low_stock),
        }

    def counts(self) -> Dict[str, int]:
        with self._conn() as conn:
            return {
                "products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
                "batches": conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0],
                "inventory_movements": conn.execute("SELECT COUNT(*) FROM inventory_movements").fetchone()[0],
                "temperature_measurements": conn.execute("SELECT COUNT(*) FROM temperature_measurements").fetchone()[0],
                "sales": conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0],
            }

    def reset_all_data(self) -> None:
        with self._conn() as conn:
            conn.execute("BEGIN")
            for table in ["sales", "temperature_measurements", "inventory_movements", "batches", "products"]:
                conn.execute(f"DELETE FROM {table}")
            conn.commit()

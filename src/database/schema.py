import sqlite3


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'kg',
            minimum_stock_level REAL NOT NULL DEFAULT 0 CHECK (minimum_stock_level >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY,
            batch_code TEXT NOT NULL UNIQUE,
            product_id INTEGER NOT NULL,
            production_date TEXT NOT NULL,
            expiration_date TEXT,
            quantity_produced REAL NOT NULL CHECK (quantity_produced > 0),
            status TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS inventory_movements (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_id INTEGER,
            movement_type TEXT NOT NULL,
            quantity REAL NOT NULL CHECK (quantity > 0),
            movement_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (batch_id) REFERENCES batches(id)
        );

        CREATE TABLE IF NOT EXISTS temperature_measurements (
            id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            measured_at TEXT NOT NULL,
            temperature_c REAL NOT NULL,
            minimum_allowed_c REAL NOT NULL,
            maximum_allowed_c REAL NOT NULL,
            source TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            quantity_sold REAL NOT NULL CHECK (quantity_sold >= 0),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE INDEX IF NOT EXISTS idx_batches_product ON batches(product_id);
        CREATE INDEX IF NOT EXISTS idx_batches_expiration ON batches(expiration_date);
        CREATE INDEX IF NOT EXISTS idx_inventory_product_date ON inventory_movements(product_id, movement_date);
        CREATE INDEX IF NOT EXISTS idx_temp_measured_at ON temperature_measurements(measured_at);
        CREATE INDEX IF NOT EXISTS idx_sales_product_date ON sales(product_id, sale_date);
        """
    )
    conn.commit()

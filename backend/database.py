"""
Database models and connection for Membrane OMP System.
"""
import sqlite3
import os
from typing import Optional

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "membrane_omp.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solute (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            MW REAL,
            charge REAL,
            logD REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membrane (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            membrane_type TEXT,
            MWCO REAL,
            contact_angle REAL,
            zeta_potential REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solute_id INTEGER NOT NULL,
            membrane_id INTEGER NOT NULL,
            rejection_rate REAL,
            FOREIGN KEY (solute_id) REFERENCES solute(id),
            FOREIGN KEY (membrane_id) REFERENCES membrane(id)
        )
    """)

    # Create indexes for faster searching
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_solute_name ON solute(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_membrane_name ON membrane(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_solute_name_lower ON solute(name COLLATE NOCASE)")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")

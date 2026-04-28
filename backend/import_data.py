"""
Import data from data_set.xlsx into SQLite database.
"""
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import get_db_connection, init_db, DATABASE_PATH

# Use environment variable or workspace default
DATA_PATH = os.environ.get('DATA_PATH', os.path.join(os.path.dirname(__file__), "..", "..", "data_set.xlsx"))


def import_data(excel_path: str = None):
    if excel_path is None:
        excel_path = DATA_PATH

    print(f"Reading data from {excel_path}...")
    df = pd.read_excel(excel_path)

    # Clean column names (some have trailing spaces)
    df.columns = df.columns.str.strip()

    print(f"Total records: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    # Initialize DB
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM experiment")
    cursor.execute("DELETE FROM solute")
    cursor.execute("DELETE FROM membrane")
    conn.commit()

    # Get unique solutes
    solutes = df[['OMP', 'MW', 'Neutral charge', 'Neutral logD']].drop_duplicates(subset=['OMP'])
    solutes = solutes.dropna(subset=['OMP'])
    print(f"Importing {len(solutes)} unique solutes...")

    solute_map = {}
    for _, row in solutes.iterrows():
        cursor.execute(
            "INSERT INTO solute (name, MW, charge, logD) VALUES (?, ?, ?, ?)",
            (row['OMP'], row['MW'], row['Neutral charge'], row['Neutral logD'])
        )
        solute_map[row['OMP']] = cursor.lastrowid

    # Get unique membranes
    membranes = df[['Membrane_N', 'Membrane Type', 'MWCO', 'Contact angle', 'Zeta potential']].drop_duplicates(subset=['Membrane_N'])
    membranes = membranes.dropna(subset=['Membrane_N'])
    print(f"Importing {len(membranes)} unique membranes...")

    membrane_map = {}
    for _, row in membranes.iterrows():
        cursor.execute(
            "INSERT INTO membrane (name, membrane_type, MWCO, contact_angle, zeta_potential) VALUES (?, ?, ?, ?, ?)",
            (row['Membrane_N'], row['Membrane Type'], row['MWCO'], row['Contact angle'], row['Zeta potential'])
        )
        membrane_map[row['Membrane_N']] = cursor.lastrowid

    # Import experiments
    print(f"Importing {len(df)} experiment records...")
    for _, row in df.iterrows():
        solute_id = solute_map.get(row['OMP'])
        membrane_id = membrane_map.get(row['Membrane_N'])
        if solute_id and membrane_id:
            cursor.execute(
                "INSERT INTO experiment (solute_id, membrane_id, rejection_rate) VALUES (?, ?, ?)",
                (solute_id, membrane_id, row['Rejection'])
            )

    conn.commit()
    conn.close()
    print("Data import completed successfully!")


if __name__ == "__main__":
    import_data()

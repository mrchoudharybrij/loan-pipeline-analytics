# 04_load_to_sqlite.py
# --------------------------------------------------------------
# Step 4a: clean CSV files ko SQLite database mein daalna.
# SQLite = ek chhota database jo ek hi file (.db) mein hota hai,
# koi server install nahi karna padta. MySQL jaisa hi SQL chalta hai.
# --------------------------------------------------------------

import sqlite3
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CLEAN = BASE / "data" / "clean"
DB = BASE / "data" / "dream_villa.db"

if DB.exists():
    DB.unlink()          # har baar fresh database

conn = sqlite3.connect(DB)
for table in ["applications", "lenders", "properties"]:
    file = "applications_clean.csv" if table == "applications" else f"{table}.csv"
    df = pd.read_csv(CLEAN / file)
    df.to_sql(table, conn, index=False)
    print(f"{table}: {len(df)} rows loaded")
conn.close()
print("Database ready:", DB.name)

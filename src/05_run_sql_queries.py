# 05_run_sql_queries.py
# --------------------------------------------------------------
# Step 4b: sql/analysis_queries.sql ki har query chalao aur
# result ko outputs/ folder mein CSV ki tarah save karo.
# (Dashboard inhi CSV files se banega.)
# Har query ke upar "-- name: xyz" likha hai, wahi file ka naam banega.
# --------------------------------------------------------------

import sqlite3
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "data" / "dream_villa.db"
SQL_FILE = BASE / "sql" / "analysis_queries.sql"
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)

text = SQL_FILE.read_text()

# "-- name:" se file ko tukdon mein todo
queries = {}
for block in text.split("-- name:")[1:]:
    name = block.split("\n", 1)[0].strip()
    sql = block.split("\n", 1)[1]
    sql = sql.split(";")[0] + ";"          # pehle ; tak hi query hai
    queries[name] = sql

conn = sqlite3.connect(DB)
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
for name, sql in queries.items():
    result = pd.read_sql_query(sql, conn)
    result.to_csv(OUT / f"{name}.csv", index=False)
    print(f"\n### {name}")
    print(result.to_string(index=False) if len(result) <= 30 else result.head(30).to_string(index=False))
conn.close()

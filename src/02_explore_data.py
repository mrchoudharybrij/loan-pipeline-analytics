# 02_explore_data.py
# --------------------------------------------------------------
# Step 1: data ko samajhna (EDA - Exploratory Data Analysis)
# Kuch bhi clean karne se pehle dekhte hain:
#   - kitni rows / columns
#   - har column ka type
#   - kis time period ka data hai
#   - kitne missing values, duplicates, gande formats
# --------------------------------------------------------------

import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

apps = pd.read_csv(RAW / "applications_raw.csv")
lenders = pd.read_csv(RAW / "lenders.csv")
props = pd.read_csv(RAW / "properties.csv")

print("=== SHAPE (rows, columns) ===")
print("applications:", apps.shape)
print("lenders:", lenders.shape)
print("properties:", props.shape)

print("\n=== COLUMN TYPES (applications) ===")
print(apps.dtypes.to_string())

print("\n=== MISSING VALUES (sirf jinme hain) ===")
missing = apps.isna().sum()
print(missing[missing > 0].to_string())

print("\n=== DUPLICATES ===")
print("poori row duplicate:", apps.duplicated().sum())
print("application_id duplicate:", apps.application_id.duplicated().sum())

print("\n=== TIME PERIOD (login_date) ===")
# mixed formats hain, isliye pehle sirf dekhte hain kitne format hain
iso = apps.login_date.str.match(r"^\d{4}-\d{2}-\d{2}$")
print("yyyy-mm-dd format:", iso.sum(), "| doosra format:", (~iso).sum())
d = pd.concat([pd.to_datetime(apps.login_date[iso], format="%Y-%m-%d"),
               pd.to_datetime(apps.login_date[~iso], format="%d/%m/%Y")])
print("from", d.min().date(), "to", d.max().date())

print("\n=== GANDE FORMATS ===")
print("city ke alag spellings:", sorted(apps.city.unique().tolist()))
print("status ke values:", apps.status.value_counts().to_dict())
text_amt = apps.requested_amount.astype(str).str.startswith("Rs.")
print("requested_amount text ('Rs.' wala):", text_amt.sum())
print("sanctioned_amount max:", apps.sanctioned_amount.max(),
      "| 99th percentile:", apps.sanctioned_amount.quantile(0.99))

print("\n=== CATEGORIES ===")
for col in ["product", "segment", "sourcing_channel", "lender_id", "rejection_stage"]:
    print(col, "->", apps[col].value_counts(dropna=False).to_dict())

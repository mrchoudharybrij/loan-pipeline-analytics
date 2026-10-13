# 03_clean_data.py
# --------------------------------------------------------------
# Step 3: Data cleaning
# 02_explore_data.py mein jo 6 problems mili thi, unko yahan
# ek-ek karke theek karte hain:
#   1. duplicate rows
#   2. city ke alag spellings
#   3. dates ke 2 formats
#   4. amount text mein ("Rs.16,00,000")
#   5. status ki spelling
#   6. outliers (extra zero wali typo)
# Plus: missing sourcing_channel ko "Unknown" bana dete hain.
#
# Asli raw file ko CHANGE nahi karte - clean data alag file mein save hota hai.
# --------------------------------------------------------------

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
CLEAN = BASE / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW / "applications_raw.csv")
print("Start rows:", len(df))

# ---- 1. Duplicates hatao ----
# same application_id do baar hai to ek hi rakho
before = len(df)
df = df.drop_duplicates(subset="application_id", keep="first")
print("1. duplicates removed:", before - len(df))

# ---- 2. City ka naam theek karo ----
# extra space hatao (strip) aur pehla letter capital (title)
df["city"] = df["city"].str.strip().str.title()
print("2. cities now:", sorted(df["city"].unique()))

# ---- 3. Dates ek format mein ----
def parse_date(x):
    # do formats aate hain: 2025-11-02 ya 02/11/2025
    if pd.isna(x):
        return pd.NaT
    if "/" in str(x):
        return pd.to_datetime(x, format="%d/%m/%Y")
    return pd.to_datetime(x, format="%Y-%m-%d")

for col in ["login_date", "sanction_date", "disbursement_date"]:
    df[col] = df[col].apply(parse_date)
print("3. login_date range:", df.login_date.min().date(), "to", df.login_date.max().date())

# ---- 4. Amount text -> number ----
def clean_amount(x):
    # "Rs.16,00,000" -> 1600000
    if pd.isna(x):
        return np.nan
    x = str(x).replace("Rs.", "").replace(",", "").strip()
    return float(x)

df["requested_amount"] = df["requested_amount"].apply(clean_amount)
print("4. requested_amount is now:", df.requested_amount.dtype)

# ---- 5. Status ki spelling ----
df["status"] = df["status"].str.strip()
df.loc[df.status.str.lower() == "disbursed", "status"] = "Disbursed"
print("5. status values:", df.status.value_counts().to_dict())

# ---- 6. Outliers (extra zero) ----
# Logic: lender kabhi bhi maange gaye amount se ZYADA sanction nahi karta.
# Agar sanctioned > requested hai to wo typo hai -> 10 se divide karke check karo.
typo = df.sanctioned_amount > df.requested_amount
print("6. typo outliers found:", typo.sum())
df.loc[typo, "sanctioned_amount"] = df.loc[typo, "sanctioned_amount"] / 10
# EMI pehle se sahi amount pe bani thi, to check: EMI formula se match hona chahiye
r = df.roi_pct / 12 / 100
n = df.tenure_months
emi_check = df.sanctioned_amount * r * (1 + r) ** n / ((1 + r) ** n - 1)
diff = (emi_check - df.emi).abs()
print("   EMI mismatch (> Rs 5) after fix:", (diff > 5).sum(), "(roi missing wale ignore)")

# ---- 7. Missing values ----
# sourcing_channel missing -> "Unknown" (row delete nahi karte, data kam ho jayega)
df["sourcing_channel"] = df["sourcing_channel"].fillna("Unknown")
# roi_pct missing (sirf sanctioned files mein) -> EMI se wapas nikal sakte hain,
# lekin simple rakhne ke liye usi lender + segment ka median bhar dete hain
med = df.groupby(["lender_id", "segment"])["roi_pct"].transform("median")
miss_roi = df.roi_pct.isna() & df.sanction_date.notna()
df.loc[miss_roi, "roi_pct"] = med[miss_roi]
print("7. roi filled with median:", miss_roi.sum())

# ---- 8. Kuch helpful naye columns (feature engineering) ----
df["login_month"] = df.login_date.dt.to_period("M").astype(str)
df["is_sanctioned"] = df.sanction_date.notna().astype(int)
df["is_disbursed"] = (df.status == "Disbursed").astype(int)
df["days_login_to_sanction"] = (df.sanction_date - df.login_date).dt.days
df["days_sanction_to_disb"] = (df.disbursement_date - df.sanction_date).dt.days

lenders = pd.read_csv(RAW / "lenders.csv")
df = df.merge(lenders[["lender_id", "payout_pct"]], on="lender_id", how="left")
# payout sirf disbursed file pe milta hai
df["payout_amount"] = np.where(df.is_disbursed == 1,
                               df.sanctioned_amount * df.payout_pct / 100, 0).round(0)
df = df.drop(columns="payout_pct")

# date ko simple text format mein save karo (SQL ke liye easy)
for col in ["login_date", "sanction_date", "disbursement_date"]:
    df[col] = df[col].dt.strftime("%Y-%m-%d")

df.to_csv(CLEAN / "applications_clean.csv", index=False)
lenders.to_csv(CLEAN / "lenders.csv", index=False)
pd.read_csv(RAW / "properties.csv").to_csv(CLEAN / "properties.csv", index=False)
print("\nFinal rows:", len(df), "| columns:", df.shape[1])
print("Saved to data/clean/")

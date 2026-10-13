# 01_generate_synthetic_data.py
# --------------------------------------------------------------
# Ye script NAKLI (synthetic) data banati hai.
# Asli customer data confidential hai, isliye maine asli sanction
# letters ka sirf STRUCTURE dekha (kaunse fields hote hain) aur
# usi structure pe random data banaya.
#
# Koi bhi naam, phone, address asli nahi hai.
# Lender names bhi fake hain (Bank A, HFC B ...).
#
# Output (data/raw/ folder mein):
#   lenders.csv, properties.csv, applications_raw.csv
#
# applications_raw.csv mein maine jaan-boojh ke thodi gandagi
# (messy data) daali hai - jaise real office ke Excel mein hoti hai -
# taaki cleaning step practice ho sake.
# --------------------------------------------------------------

import numpy as np
import pandas as pd
from pathlib import Path

# seed fix kiya taaki har baar same data bane (reproducible)
rng = np.random.default_rng(42)

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = pd.Timestamp("2024-10-01")
END_DATE = pd.Timestamp("2026-09-30")   # data "as of" ye date
N_APPLICATIONS = 1800
DSA_CODE = "DVF001"                      # firm ka franchisee / DSA code (fake)


# ==============================================================
# 1. LENDERS TABLE
# ==============================================================
# har lender ka type, payout %, aur ek "strictness" (kitna reject karta hai)
lenders = pd.DataFrame({
    "lender_id":   ["L01", "L02", "L03", "L04", "L05", "L06", "L07", "L08"],
    "lender_name": ["Bank A", "Bank B", "Bank C", "HFC A", "HFC B", "HFC C", "NBFC A", "NBFC B"],
    "lender_type": ["Bank", "Bank", "Bank", "HFC", "HFC", "HFC", "NBFC", "NBFC"],
    "payout_pct":  [0.40, 0.45, 0.50, 0.65, 0.70, 0.60, 0.90, 1.00],   # % of disbursed amount
})

# ye columns sirf data banane ke liye hain, CSV mein nahi jayenge
# base_roi = us lender ka typical rate (%), strict = rejection badhane wala factor
lender_profile = {
    "L01": {"base_roi": 8.6,  "strict": 1.30, "speed": 1.2, "share": 0.16},
    "L02": {"base_roi": 8.8,  "strict": 1.20, "speed": 1.1, "share": 0.12},
    "L03": {"base_roi": 9.0,  "strict": 1.10, "speed": 1.0, "share": 0.08},
    "L04": {"base_roi": 9.6,  "strict": 0.90, "speed": 0.8, "share": 0.18},
    "L05": {"base_roi": 9.9,  "strict": 0.85, "speed": 0.9, "share": 0.14},
    "L06": {"base_roi": 10.3, "strict": 0.80, "speed": 1.0, "share": 0.12},
    "L07": {"base_roi": 11.8, "strict": 0.65, "speed": 0.7, "share": 0.11},
    "L08": {"base_roi": 12.5, "strict": 0.60, "speed": 0.6, "share": 0.09},
}


# ==============================================================
# 2. PROPERTIES TABLE (projects / colonies)
# ==============================================================
cities = ["Indore", "Dewas", "Ujjain", "Pithampur", "Mhow", "Sanwer"]
city_weights = [0.55, 0.12, 0.10, 0.09, 0.08, 0.06]

project_words_1 = ["Shree", "Sai", "Royal", "Green", "Golden", "Sunrise", "Krishna",
                   "Shiv", "Silver", "Kalpana", "Om", "Lotus", "Narmada", "Ganga"]
project_words_2 = ["Vihar", "Nagar", "City", "Residency", "Enclave", "Park",
                   "Greens", "Heights", "Colony", "Avenue", "Dham", "Valley"]
builder_names = [f"Builder {chr(65 + i)}{chr(65 + j)} Realty Pvt Ltd"
                 for i in range(5) for j in range(5)]   # 25 fake builders

N_PROPERTIES = 140
prop_rows = []
for i in range(N_PROPERTIES):
    name = f"{rng.choice(project_words_1)} {rng.choice(project_words_2)}"
    approval = rng.choice(["Approved", "Pending", "Not Approved"], p=[0.70, 0.18, 0.12])
    approved_date = None
    if approval == "Approved":
        approved_date = START_DATE - pd.Timedelta(days=int(rng.integers(0, 700)))
    prop_rows.append({
        "property_id": f"P{1000 + i}",
        "project_name": name,
        "builder_name": rng.choice(builder_names),
        "city": rng.choice(cities, p=city_weights),
        "approval_status": approval,
        "approved_date": approved_date,
        "total_units": int(rng.integers(20, 300)),
        "on_hold": "Y" if rng.random() < 0.06 else "N",
    })
properties = pd.DataFrame(prop_rows)


# ==============================================================
# 3. APPLICATIONS TABLE (main table - ek row = ek loan file)
# ==============================================================

# --- login dates: business thoda badhta hai + festive season (Oct-Nov)
#     aur March (year end) mein zyada files
all_days = pd.date_range(START_DATE, END_DATE, freq="D")
day_weight = []
for d in all_days:
    w = 1.0 + 0.35 * (d - START_DATE).days / 730      # slow growth
    if d.month in (10, 11):
        w *= 1.35                                     # Diwali / festive
    if d.month == 3:
        w *= 1.20                                     # financial year end
    if d.dayofweek == 6:
        w *= 0.25                                     # Sunday kam kaam
    day_weight.append(w)
day_weight = np.array(day_weight) / sum(day_weight)
login_dates = rng.choice(all_days, size=N_APPLICATIONS, p=day_weight)
login_dates = np.sort(login_dates)

products = ["Home Loan - Purchase", "Self Construction", "Plot + Construction",
            "Balance Transfer", "Loan Against Property"]
product_p = [0.38, 0.20, 0.17, 0.12, 0.13]

channels = ["Builder Tie-up", "Connector", "Walk-in", "Referral", "Digital"]
channel_p = [0.32, 0.28, 0.15, 0.15, 0.10]

lender_ids = list(lender_profile.keys())
lender_share = [lender_profile[l]["share"] for l in lender_ids]

# rejection reasons har stage ke liye
reasons = {
    "FI": ["Negative residence FI", "Negative office FI", "Address not traceable"],
    "Legal/Technical": ["Title not clear", "Property not approved", "Valuation shortfall",
                        "Construction deviation"],
    "FCU": ["Document mismatch", "Income document suspicious", "Profile not matching"],
    "Credit": ["Low CIBIL score", "High FOIR (existing EMIs)", "Income not sufficient",
               "Policy - age / tenure"],
}


def calc_emi(amount, annual_rate, months):
    # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1),  r = monthly rate
    r = annual_rate / 12 / 100
    return amount * r * (1 + r) ** months / ((1 + r) ** months - 1)


rows = []
customer_counter = 0
prev_customers = []   # repeat customers ke liye

for i in range(N_APPLICATIONS):
    login = pd.Timestamp(login_dates[i])

    # --- customer id: ~7% files purane customer ki hoti hain (re-login / naya loan)
    if prev_customers and rng.random() < 0.07:
        customer_id = rng.choice(prev_customers)
    else:
        customer_counter += 1
        customer_id = f"C{10000 + customer_counter}"
        prev_customers.append(customer_id)

    lender = rng.choice(lender_ids, p=lender_share)
    lp = lender_profile[lender]
    lender_type = lenders.loc[lenders.lender_id == lender, "lender_type"].iloc[0]

    product = rng.choice(products, p=product_p)
    channel = rng.choice(channels, p=channel_p)
    city = rng.choice(cities, p=city_weights)

    # --- segment: NBFC/HFC pe affordable zyada
    aff_prob = {"Bank": 0.30, "HFC": 0.55, "NBFC": 0.70}[lender_type]
    segment = "Affordable" if rng.random() < aff_prob else "Prime"

    # --- requested amount (lakh mein socha, phir rupees)
    if segment == "Affordable":
        amt_lakh = rng.lognormal(mean=np.log(12), sigma=0.40)
        amt_lakh = min(max(amt_lakh, 4), 35)
    else:
        amt_lakh = rng.lognormal(mean=np.log(32), sigma=0.45)
        amt_lakh = min(max(amt_lakh, 15), 150)
    if product == "Loan Against Property":
        amt_lakh *= 0.8
    requested_amount = int(round(amt_lakh * 100000, -4))   # 10,000 ke multiple

    tenure = int(rng.choice([120, 180, 240, 300, 360], p=[0.10, 0.25, 0.35, 0.15, 0.15]))
    if product == "Loan Against Property":
        tenure = min(tenure, 180)

    # --- property sirf property-wale products ke liye link karte hain
    property_id = None
    prop_status = "Approved"
    if product in ("Home Loan - Purchase", "Plot + Construction") and rng.random() < 0.75:
        prop = properties.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        property_id = prop["property_id"]
        prop_status = prop["approval_status"]
        city = prop["city"]

    # ==========================================================
    # FUNNEL: Login -> FI -> Legal/Technical -> FCU -> Credit (sanction) -> Disbursement
    # har stage pe fail hone ka chance alag hai
    # ==========================================================
    stage_fail = {
        "FI": 0.06,
        "Legal/Technical": 0.07 + (0.20 if prop_status == "Not Approved" else 0)
                                + (0.06 if prop_status == "Pending" else 0),
        "FCU": 0.05,
        "Credit": 0.12,
    }
    if segment == "Affordable":
        stage_fail["Credit"] += 0.05
        stage_fail["FI"] += 0.02
    if channel == "Connector":
        stage_fail["FCU"] += 0.04       # connector files mein document issue thoda zyada
    if channel == "Builder Tie-up":
        stage_fail["Legal/Technical"] -= 0.03

    # stage ki time (days) - "speed" < 1 matlab jaldi
    stage_days = {
        "FI": rng.integers(1, 6),
        "Legal/Technical": rng.integers(3, 12),
        "FCU": rng.integers(1, 7),
        "Credit": rng.integers(2, 9),
    }

    status = None
    rejection_stage = None
    rejection_reason = None
    stage_result = {}
    current_date = login
    data_cutoff = END_DATE

    for stage in ["FI", "Legal/Technical", "FCU", "Credit"]:
        days = int(np.ceil(stage_days[stage] * lp["speed"]))
        current_date = current_date + pd.Timedelta(days=days)
        if current_date > data_cutoff:
            status = "In Process"           # abhi file chal rahi hai
            stage_result[stage] = "Pending"
            break
        # customer khud bhi beech mein file chhod sakta hai
        if rng.random() < 0.025:
            status = "Withdrawn"
            stage_result[stage] = "Not Done"
            rejection_stage = stage
            rejection_reason = "Customer withdrew"
            break
        fail_p = min(max(stage_fail[stage] * lp["strict"], 0.01), 0.6)
        if rng.random() < fail_p:
            status = "Rejected"
            stage_result[stage] = "Negative"
            rejection_stage = stage
            rejection_reason = rng.choice(reasons[stage])
            break
        stage_result[stage] = "Positive"

    sanction_date = None
    disbursement_date = None
    sanctioned_amount = None
    roi = None
    emi = None
    processing_fee = None
    life_ins = None
    general_ins = None

    if status is None:
        # sab stage clear -> sanction
        sanction_date = current_date
        # lender kabhi kabhi kam amount sanction karta hai
        cut = 1.0 if rng.random() < 0.75 else rng.uniform(0.75, 0.95)
        sanctioned_amount = int(round(requested_amount * cut, -4))

        roi = lp["base_roi"] + rng.normal(0, 0.25)
        if segment == "Affordable":
            roi += rng.uniform(0.8, 1.8)
        if product == "Loan Against Property":
            roi += 1.0
        roi = round(roi, 2)
        emi = round(calc_emi(sanctioned_amount, roi, tenure), 0)

        # processing fee ~0.5% (GST 18% ke saath), min 2,500
        processing_fee = round(max(sanctioned_amount * 0.005, 2500) * 1.18, 0)

        # insurance cross-sell: HFC/NBFC zyada bechte hain
        ins_prob = {"Bank": 0.45, "HFC": 0.70, "NBFC": 0.80}[lender_type]
        if rng.random() < ins_prob:
            life_ins = round(sanctioned_amount * rng.uniform(0.012, 0.025), -2)
            general_ins = round(sanctioned_amount * rng.uniform(0.002, 0.006), -2)
        else:
            life_ins, general_ins = 0, 0

        # sanction ke baad disbursement (7-45 din), kuch log disburse nahi karte
        if rng.random() < 0.09:
            status = "Sanctioned - Not Disbursed"
        else:
            gap = int(rng.integers(7, 46) * lp["speed"])
            disb = sanction_date + pd.Timedelta(days=gap)
            if disb > data_cutoff:
                status = "Sanctioned - Disbursement Pending"
            else:
                status = "Disbursed"
                disbursement_date = disb

    rows.append({
        "application_id": f"APP{24000 + i}",
        "dsa_code": DSA_CODE,
        "customer_id": customer_id,
        "lender_id": lender,
        "product": product,
        "bt_flag": "BT" if product == "Balance Transfer" else "Non BT",
        "segment": segment,
        "sourcing_channel": channel,
        "city": city,
        "property_id": property_id,
        "login_date": login,
        "fi_status": stage_result.get("FI", "Not Done"),
        "legal_technical_status": stage_result.get("Legal/Technical", "Not Done"),
        "fcu_status": stage_result.get("FCU", "Not Done"),
        "credit_status": stage_result.get("Credit", "Not Done"),
        "status": status,
        "rejection_stage": rejection_stage,
        "rejection_reason": rejection_reason,
        "sanction_date": sanction_date,
        "disbursement_date": disbursement_date,
        "requested_amount": requested_amount,
        "sanctioned_amount": sanctioned_amount,
        "tenure_months": tenure,
        "roi_pct": roi,
        "emi": emi,
        "processing_fee": processing_fee,
        "life_insurance_premium": life_ins,
        "general_insurance_premium": general_ins,
        "repayment_mode": "NACH" if sanction_date is not None else None,
    })

apps = pd.DataFrame(rows)


# ==============================================================
# 4. JAAN-BOOJH KE GANDAGI (messy data) - real Excel jaisa
# ==============================================================
messy = apps.copy()

# (a) city ke naam alag-alag tarike se likhe hue
idx = messy.sample(frac=0.10, random_state=1).index
messy.loc[idx, "city"] = messy.loc[idx, "city"].apply(
    lambda c: rng.choice([c.upper(), c.lower(), c + " ", " " + c]))

# (b) kuch amounts "Rs.16,00,000" jaise text mein (Indian comma style)
def to_indian_text(x):
    s = str(int(x))
    last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return "Rs." + ",".join(parts + [last3]) if parts else "Rs." + last3

messy["requested_amount"] = messy["requested_amount"].astype(object)
idx = messy.sample(frac=0.08, random_state=2).index
messy.loc[idx, "requested_amount"] = messy.loc[idx, "requested_amount"].apply(to_indian_text)

# (c) dates ko text bana ke kuch rows mein dd/mm/yyyy format
for col in ["login_date", "sanction_date", "disbursement_date"]:
    messy[col] = messy[col].apply(lambda d: d.strftime("%Y-%m-%d") if pd.notna(d) else None)
idx = messy.sample(frac=0.12, random_state=3).index
messy.loc[idx, "login_date"] = pd.to_datetime(messy.loc[idx, "login_date"]).dt.strftime("%d/%m/%Y")

# (d) status mein spelling / case ka farak
idx = messy[messy.status == "Disbursed"].sample(frac=0.05, random_state=4).index
messy.loc[idx, "status"] = rng.choice(["disbursed", "DISBURSED", "Disbursed "], size=len(idx))

# (e) kuch missing values (data entry chhoot gayi)
idx = messy.sample(frac=0.03, random_state=5).index
messy.loc[idx, "sourcing_channel"] = None
idx = messy[messy.roi_pct.notna()].sample(frac=0.02, random_state=6).index
messy.loc[idx, "roi_pct"] = None

# (f) duplicate rows (same file do baar entry ho gayi)
dups = messy.sample(n=25, random_state=7)
messy = pd.concat([messy, dups]).sample(frac=1, random_state=8).reset_index(drop=True)

# (g) kuch typo wale outliers - ek zero extra laga diya
idx = messy[messy.sanctioned_amount.notna()].sample(n=4, random_state=9).index
messy.loc[idx, "sanctioned_amount"] = messy.loc[idx, "sanctioned_amount"] * 10


# ==============================================================
# 5. SAVE
# ==============================================================
lenders.to_csv(OUT_DIR / "lenders.csv", index=False)
properties.to_csv(OUT_DIR / "properties.csv", index=False)
messy.to_csv(OUT_DIR / "applications_raw.csv", index=False)

print("Done!")
print("lenders:", lenders.shape)
print("properties:", properties.shape)
print("applications_raw:", messy.shape)

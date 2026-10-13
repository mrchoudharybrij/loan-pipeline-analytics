# 06_make_readme_charts.py
# --------------------------------------------------------------
# README ke liye ek static image (dashboard/summary.png) banata hai.
# Saare numbers outputs/ ki CSV files se aate hain (05 script ke baad chalao).
# --------------------------------------------------------------

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "outputs"

BLUE, MUTED, RED = "#2a78d6", "#c9c8c2", "#d03b3b"
INK, INK2, BG = "#0b0b0b", "#52514e", "#fcfcfb"

plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": MUTED})

funnel = pd.read_csv(OUT / "q1_funnel_stages.csv").sort_values("step")
monthly = pd.read_csv(OUT / "q4_monthly_disbursements.csv")
lenders = pd.read_csv(OUT / "q2_lender_performance.csv")
channels = pd.read_csv(OUT / "q3_channel_quality.csv")
channels = channels[channels.sourcing_channel != "Unknown"]

fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), facecolor=BG)
for ax in axes.flat:
    ax.set_facecolor(BG)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

# 1. Funnel - biggest loss red
ax = axes[0, 0]
lost = funnel.files.shift(1) - funnel.files
worst = lost.idxmax()
colors = [RED if i == worst else BLUE for i in funnel.index]
y = range(len(funnel))[::-1]
ax.barh(list(y), funnel.files, color=colors, height=0.6)
ax.set_yticks(list(y), funnel.stage)
for yi, f, l in zip(y, funnel.files, lost):
    txt = f"{f:,}" + (f"  (−{int(l):,})" if pd.notna(l) else "")
    ax.text(f + 15, yi, txt, va="center", color=INK2)
ax.set_xlim(0, funnel.files.max() * 1.3)
ax.set_title("Where files drop out (red = biggest loss)", loc="left", fontweight="bold")
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)

# 2. Monthly disbursements
ax = axes[0, 1]
ax.bar(monthly.month, monthly.disbursed_crore, color=BLUE, width=0.7)
labels = pd.to_datetime(monthly.month).dt.strftime("%b %y")
ax.set_xticks(range(0, len(monthly), 4), list(labels[::4]), rotation=0)
ax.set_ylabel("₹ crore disbursed")
ax.grid(axis="y", color="#ecebe7")
ax.set_axisbelow(True)
ax.set_title("Monthly disbursements", loc="left", fontweight="bold")

# 3. Payout per login by lender
ax = axes[1, 0]
lp = lenders.sort_values("payout_per_login_rs")
c = [BLUE if v == lp.payout_per_login_rs.max() else MUTED for v in lp.payout_per_login_rs]
ax.barh(lp.lender_name, lp.payout_per_login_rs, color=c, height=0.6)
for i, v in enumerate(lp.payout_per_login_rs):
    ax.text(v + 150, i, f"₹{v:,.0f}", va="center", color=INK2)
ax.set_xlim(0, lp.payout_per_login_rs.max() * 1.2)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.set_title("Payout earned per file logged in", loc="left", fontweight="bold")

# 4. FCU rejection by channel
ax = axes[1, 1]
ch = channels.sort_values("fcu_reject_pct")
c = [RED if v == ch.fcu_reject_pct.max() else MUTED for v in ch.fcu_reject_pct]
ax.barh(ch.sourcing_channel, ch.fcu_reject_pct, color=c, height=0.6)
for i, v in enumerate(ch.fcu_reject_pct):
    ax.text(v + 0.15, i, f"{v:.1f}%", va="center", color=INK2)
ax.set_xlim(0, ch.fcu_reject_pct.max() * 1.25)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.set_title("FCU (document/fraud) rejection by channel", loc="left", fontweight="bold")

fig.suptitle("Dream Villa Finance · loan pipeline (synthetic data, Oct 2024 – Sep 2026)",
             x=0.01, ha="left", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(BASE / "dashboard" / "summary.png", dpi=150, facecolor=BG)
print("Saved dashboard/summary.png")

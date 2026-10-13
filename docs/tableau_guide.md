# Tableau Public pe dashboard banana (Mac)

## Pehle decision: Tableau Public ya Power BI?

**Abhi: Tableau Public.** Wajah:
- Mac pe seedha chalta hai aur free hai. Uni ke Power BI access ka wait nahi karna padega.
- Publish karne pe ek public link milta hai, jo CV aur LinkedIn pe daal sakte ho. Data synthetic hai, toh public karne mein koi problem nahi.
- UK job ads mein Power BI zyada maanga jaata hai, lekin interviewer dekhta hai ki tum dashboard *soch* sakte ho ya nahi. Tool badalna 1–2 din ka kaam hai.

**Baad mein (optional):** jab uni ka Power BI access mil jaaye, library ke Windows PC pe yahi 4 charts Power BI mein bana lo. Phir CV pe "Tableau, Power BI" dono likh sakoge. Same CSV files kaam aayengi.

Analogy: Tableau aur Power BI dono car hain, bas ek Maruti hai aur ek Hyundai. Driving (dashboard sense) seekh li, toh dono chala loge.

## Steps

1. Tableau Public download karo: public.tableau.com → "Create" → Tableau Public desktop app (Mac).
2. **Connect → Text file** → `data/clean/applications_clean.csv` kholo.
3. Data tab mein **Add** → `lenders.csv` → `lender_id` pe join karo (Tableau isse "relationship" kehta hai).
4. Ye 4 sheets banao:

| Sheet | Rows / Columns | Mark | Kya dikhega |
|---|---|---|---|
| Monthly trend | Columns: `disbursement_date` (Month), Rows: SUM(`sanctioned_amount`) | Bar | Mahine ka disbursement. Filter: `is_disbursed` = 1 |
| Lender scorecard | Rows: `lender_name`, Columns: SUM(`payout_amount`) / COUNT(`application_id`) | Bar | Payout per login |
| Channel quality | Rows: `sourcing_channel`, Columns: AVG(`is_disbursed`) | Bar | Disbursal rate |
| Rejection reasons | Rows: `rejection_reason`, Columns: COUNT, Filter: `status` = Rejected | Bar, sorted | Top reasons |

5. **Calculated field** banao (Analysis → Create Calculated Field):
   - `Payout per login` = `SUM([payout_amount]) / COUNT([application_id])`
   - `Disbursal rate` = `SUM([is_disbursed]) / COUNT([application_id])` → percentage format
6. **Dashboard → New Dashboard**: upar 4 KPI tiles (Text marks) rakho, neeche 4 charts. Ek filter `lender_type` pe lagao jo saare charts pe apply ho.
7. **Ek note zaroor likho:** "Synthetic data modelled on real sanction letters".
8. File → **Save to Tableau Public** → link copy karo → README aur LinkedIn mein daalo.
9. Screenshot lo → `dashboard/screenshot.png` naam se save karo → README mein `![Dashboard](dashboard/screenshot.png)` add karo.

## Check
Tableau ke numbers SQL outputs se match hone chahiye (jaise total payout = ₹143.5 lakh, `outputs/kpi_summary.csv`). Match nahi hua toh koi filter galat laga hai.

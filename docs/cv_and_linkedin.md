# CV aur LinkedIn ke liye text

## CV (Experience ya Projects section)

**Freelance Data Analyst** · Dream Villa Finance (home-loan DSA), Indore, India · Remote · Oct 2026 – Present

- Built an end-to-end loan-pipeline analytics workflow in Python (pandas) and SQL (SQLite) that tracks applications across 8 bank, HFC and NBFC lenders from login to disbursement.
- Designed a 1,800-application synthetic dataset modelled on real sanction-letter structures, to protect confidential client data. Validated the EMI logic against real bank sanction letters (within ₹1) and cleaned 7 classes of injected data-quality issues.
- Wrote 16 SQL queries (joins, CASE aggregations, window functions) and an interactive dashboard covering funnel drop-off, lender payout per login, channel quality and revenue leakage, with five recommendations for the firm.

> Agar CV pe jagah kam ho, toh bullets 1 aur 3 rakho.
> Date tab se likho jab se kaam shuru hua. "Present" tab tak, jab tak bhai ise use kar rahe hain.

## LinkedIn → Projects

**Title:** Loan Pipeline Analytics for a Home-Loan DSA

**Associated with:** Dream Villa Finance (freelance)

**Description:**
My brother runs Dream Villa Finance, a DSA firm in Indore that sources home-loan customers for several banks and housing finance companies. A DSA earns only when a loan is disbursed, so I built a pipeline to show where files drop out and which lenders and sourcing channels convert best.

Client data is confidential, so I studied the structure of real sanction letters (benchmark rate + spread, EMI, fees, insurance, FI / legal / FCU checks) and generated a synthetic dataset with the same structure. My EMI formula matched real bank letters within ₹1.

Work: data profiling and cleaning in pandas (duplicates, mixed date formats, text amounts, typo outliers), SQL analysis in SQLite (16 queries including window functions), and an interactive dashboard. I also documented two analysis traps: recent periods looking weak because files are still in progress (right-censoring), and a misleading result from a 48-file sample.

Skills: Python · pandas · SQL · Data cleaning · Dashboarding · Business analysis

**Link:** [GitHub repo link] · [Dashboard link] (optional: Tableau Public link, agar baad mein banao)

## Interview ke liye 30-second pitch (English)
"My brother runs a loan DSA firm in India. They earn only when a loan is disbursed, so I built an analytics pipeline to show where applications drop out. Their data is confidential, so I reverse-engineered the structure of real sanction letters and generated synthetic data with the same fields. I even checked my EMI formula against real sanction letters. Then I cleaned it in pandas, analysed it in SQL and built a dashboard. The biggest drop-off was the credit decision, and connector-sourced files failed fraud checks two to three times as often as other channels. The firm now runs the same pipeline on its own data."

> Last line tabhi bolna jab bhai sach mein use kar rahe hon.

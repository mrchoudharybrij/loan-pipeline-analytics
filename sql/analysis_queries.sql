-- ==============================================================
-- Dream Villa Finance - SQL Analysis (SQLite)
-- Har query ke upar: business sawaal + "kyun" ye query aise likhi
-- Note: data SYNTHETIC hai (asli client data confidential hai)
-- ==============================================================


-- --------------------------------------------------------------
-- Q1. FUNNEL: 100 files login hoti hain to kitni sanction aur
--     kitni disburse hoti hain? Aur sabse zyada files kis stage pe girti hain?
-- Kyun: DSA ki kamai sirf DISBURSED file pe hai. Jahan files girti hain,
--       wahi improvement ka sabse bada mauka hai.
-- 'In Process' files ko hata dete hain kyunki unka result abhi aaya hi nahi.
-- --------------------------------------------------------------
-- name: q1_funnel_overall
SELECT
    COUNT(*)                                              AS total_logins,
    SUM(is_sanctioned)                                    AS sanctioned,
    SUM(is_disbursed)                                     AS disbursed,
    ROUND(100.0 * SUM(is_sanctioned) / COUNT(*), 1)       AS sanction_rate_pct,
    ROUND(100.0 * SUM(is_disbursed)  / COUNT(*), 1)       AS disbursal_rate_pct
FROM applications
WHERE status <> 'In Process';

-- name: q1_funnel_stages
-- Har stage ko kitni files ne PAAR kiya (dashboard funnel chart ke liye)
-- UNION ALL: alag-alag SELECT ke results ko ek ke neeche ek jodta hai
SELECT 1 AS step, 'Logged in' AS stage, COUNT(*) AS files
  FROM applications WHERE status <> 'In Process'
UNION ALL
SELECT 2, 'FI cleared', SUM(fi_status = 'Positive')
  FROM applications WHERE status <> 'In Process'
UNION ALL
SELECT 3, 'Legal/Technical cleared', SUM(legal_technical_status = 'Positive')
  FROM applications WHERE status <> 'In Process'
UNION ALL
SELECT 4, 'FCU cleared', SUM(fcu_status = 'Positive')
  FROM applications WHERE status <> 'In Process'
UNION ALL
SELECT 5, 'Sanctioned', SUM(is_sanctioned)
  FROM applications WHERE status <> 'In Process'
UNION ALL
SELECT 6, 'Disbursed', SUM(is_disbursed)
  FROM applications WHERE status <> 'In Process'
ORDER BY step;

-- name: kpi_summary
-- Dashboard ke upar wale headline numbers (poore 2 saal)
SELECT
    COUNT(*)                                                         AS total_logins,
    SUM(is_disbursed)                                                AS disbursed_files,
    ROUND(SUM(CASE WHEN is_disbursed = 1 THEN sanctioned_amount ELSE 0 END) / 1e7, 2)
                                                                     AS disbursed_crore,
    ROUND(SUM(payout_amount) / 1e5, 2)                               AS payout_lakh,
    ROUND(AVG(CASE WHEN is_disbursed = 1 THEN sanctioned_amount END) / 1e5, 1)
                                                                     AS avg_ticket_lakh,
    ROUND(AVG(days_login_to_sanction), 1)                            AS avg_days_to_sanction,
    SUM(status = 'In Process') + SUM(status = 'Sanctioned - Disbursement Pending')
                                                                     AS files_in_pipeline
FROM applications;

-- name: q1_dropoff_by_stage
SELECT
    rejection_stage,
    SUM(CASE WHEN status = 'Rejected'  THEN 1 ELSE 0 END) AS rejected,
    SUM(CASE WHEN status = 'Withdrawn' THEN 1 ELSE 0 END) AS withdrawn,
    COUNT(*)                                              AS total_lost
FROM applications
WHERE rejection_stage IS NOT NULL
GROUP BY rejection_stage
ORDER BY total_lost DESC;

-- name: q1_top_rejection_reasons
SELECT rejection_stage, rejection_reason, COUNT(*) AS files
FROM applications
WHERE status = 'Rejected'
GROUP BY rejection_stage, rejection_reason
ORDER BY files DESC
LIMIT 8;


-- --------------------------------------------------------------
-- Q2. LENDER-WISE PERFORMANCE: kis lender ke saath kaam karna
--     sabse faydemand hai?
-- Kyun: sirf payout % dekhna kaafi nahi. Payout zyada ho lekin
--       aadhi files reject ho jayein, to fayda kam. Isliye
--       "per login kitna payout mila" (expected value) nikalte hain.
-- JOIN: applications + lenders (lender ka naam aur type laane ke liye)
-- --------------------------------------------------------------
-- name: q2_lender_performance
SELECT
    l.lender_name,
    l.lender_type,
    l.payout_pct,
    COUNT(*)                                                    AS logins,
    ROUND(100.0 * SUM(a.is_sanctioned) / COUNT(*), 1)           AS sanction_rate_pct,
    ROUND(100.0 * SUM(a.is_disbursed)  / COUNT(*), 1)           AS disbursal_rate_pct,
    ROUND(AVG(a.days_login_to_sanction), 1)                     AS avg_days_to_sanction,
    ROUND(AVG(CASE WHEN a.is_sanctioned = 1 THEN a.roi_pct END), 2) AS avg_roi_pct,
    ROUND(SUM(CASE WHEN a.is_disbursed = 1 THEN a.sanctioned_amount ELSE 0 END) / 1e7, 2)
                                                                AS disbursed_crore,
    ROUND(SUM(a.payout_amount) / 1e5, 2)                        AS payout_lakh,
    ROUND(SUM(a.payout_amount) / COUNT(*), 0)                   AS payout_per_login_rs
FROM applications a
JOIN lenders l ON a.lender_id = l.lender_id
WHERE a.status <> 'In Process'
GROUP BY l.lender_name, l.lender_type, l.payout_pct
ORDER BY payout_per_login_rs DESC;


-- --------------------------------------------------------------
-- Q3. SOURCING CHANNEL: kaunse channel se aayi files sabse
--     achhi convert hoti hain?
-- Kyun: team ka time limited hai. Jo channel zyada files laata
--       hai lekin reject zyada hoti hain, uspe dhyan dena padega.
-- FCU rejection alag se dekha - ye document / fraud issue dikhata hai.
-- --------------------------------------------------------------
-- name: q3_channel_quality
SELECT
    sourcing_channel,
    COUNT(*)                                                         AS logins,
    ROUND(100.0 * SUM(is_disbursed) / COUNT(*), 1)                   AS disbursal_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN rejection_stage = 'FCU' AND status = 'Rejected'
                           THEN 1 ELSE 0 END) / COUNT(*), 1)         AS fcu_reject_pct,
    ROUND(100.0 * SUM(CASE WHEN rejection_stage = 'Legal/Technical' AND status = 'Rejected'
                           THEN 1 ELSE 0 END) / COUNT(*), 1)         AS legal_tech_reject_pct,
    ROUND(SUM(payout_amount) / 1e5, 2)                               AS payout_lakh
FROM applications
WHERE status <> 'In Process'
GROUP BY sourcing_channel
ORDER BY disbursal_rate_pct DESC;


-- --------------------------------------------------------------
-- Q4. MONTHLY TREND: business badh raha hai ya nahi? Kaunse
--     mahine strong hain?
-- Kyun: festive season / year-end ke liye pehle se planning
--       (staff, builder events) kar sakte hain.
-- Disbursement ko disbursement_date ke month se ginte hain (login month se nahi).
-- --------------------------------------------------------------
-- name: q4_monthly_logins
SELECT login_month AS month, COUNT(*) AS logins
FROM applications
GROUP BY login_month
ORDER BY login_month;

-- name: q4_monthly_disbursements
SELECT
    substr(disbursement_date, 1, 7)                  AS month,
    COUNT(*)                                         AS disbursed_files,
    ROUND(SUM(sanctioned_amount) / 1e7, 2)           AS disbursed_crore,
    ROUND(SUM(payout_amount) / 1e5, 2)               AS payout_lakh
FROM applications
WHERE is_disbursed = 1
GROUP BY substr(disbursement_date, 1, 7)
ORDER BY month;

-- name: q4_year_on_year
-- FY = Indian financial year (Apr-Mar). Hamare paas Oct-Sep ke 2 poore saal hain,
-- isliye "Year 1" = Oct 2024-Sep 2025, "Year 2" = Oct 2025-Sep 2026
SELECT
    CASE WHEN login_date < '2025-10-01' THEN 'Year 1 (Oct24-Sep25)'
         ELSE 'Year 2 (Oct25-Sep26)' END             AS period,
    COUNT(*)                                         AS logins,
    SUM(is_disbursed)                                AS disbursed_files,
    ROUND(SUM(payout_amount) / 1e5, 2)               AS payout_lakh
FROM applications
GROUP BY period;


-- --------------------------------------------------------------
-- Q5. REVENUE LEAKAGE: kitna paisa "haath aate aate" chhoot gaya?
-- Kyun: sanction ho chuki file ka customer chala gaya = sabse
--       sasta recovery mauka (mehnat already ho chuki hai).
-- Expected payout = sanctioned amount x lender payout %
-- --------------------------------------------------------------
-- name: q5_leakage
SELECT
    a.status,
    COUNT(*)                                                     AS files,
    ROUND(SUM(a.sanctioned_amount) / 1e7, 2)                     AS sanctioned_crore,
    ROUND(SUM(a.sanctioned_amount * l.payout_pct / 100) / 1e5, 2) AS payout_missed_lakh
FROM applications a
JOIN lenders l ON a.lender_id = l.lender_id
WHERE a.status = 'Sanctioned - Not Disbursed'
GROUP BY a.status;

-- name: q5_property_approval_effect
-- Kya pehle se approved project wali files zyada pass hoti hain?
-- LEFT JOIN nahi, INNER JOIN: sirf wo files jinka property_id hai
SELECT
    p.approval_status                                            AS project_status,
    COUNT(*)                                                     AS logins,
    ROUND(100.0 * SUM(a.is_disbursed) / COUNT(*), 1)             AS disbursal_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN a.rejection_stage = 'Legal/Technical' AND a.status = 'Rejected'
                           THEN 1 ELSE 0 END) / COUNT(*), 1)     AS legal_tech_reject_pct
FROM applications a
JOIN properties p ON a.property_id = p.property_id
WHERE a.status <> 'In Process'
GROUP BY p.approval_status
ORDER BY disbursal_rate_pct DESC;


-- --------------------------------------------------------------
-- EXTRA: product + segment mix, aur insurance cross-sell
-- --------------------------------------------------------------
-- name: x_product_segment
SELECT
    product,
    segment,
    COUNT(*)                                                         AS logins,
    ROUND(100.0 * SUM(is_disbursed) / COUNT(*), 1)                   AS disbursal_rate_pct,
    ROUND(AVG(CASE WHEN is_disbursed = 1 THEN sanctioned_amount END) / 1e5, 1) AS avg_ticket_lakh,
    ROUND(AVG(CASE WHEN is_sanctioned = 1 THEN roi_pct END), 2)      AS avg_roi_pct
FROM applications
WHERE status <> 'In Process'
GROUP BY product, segment
ORDER BY product, segment;

-- name: x_insurance_attach
SELECT
    l.lender_type,
    COUNT(*)                                                             AS sanctioned_files,
    ROUND(100.0 * SUM(CASE WHEN a.life_insurance_premium > 0 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                         AS insurance_attach_pct
FROM applications a
JOIN lenders l ON a.lender_id = l.lender_id
WHERE a.is_sanctioned = 1
GROUP BY l.lender_type;

-- name: x_repeat_customers
-- Window function: har customer ki kitni files hain
SELECT files_per_customer, COUNT(*) AS customers
FROM (
    SELECT customer_id, COUNT(*) AS files_per_customer
    FROM applications
    GROUP BY customer_id
)
GROUP BY files_per_customer
ORDER BY files_per_customer;

-- name: x_lender_rank_by_month
-- Window function RANK(): har mahine top lender kaun tha (disbursed amount se)
SELECT month, lender_name, disbursed_lakh
FROM (
    SELECT
        substr(a.disbursement_date, 1, 7)  AS month,
        l.lender_name,
        ROUND(SUM(a.sanctioned_amount) / 1e5, 1) AS disbursed_lakh,
        RANK() OVER (PARTITION BY substr(a.disbursement_date, 1, 7)
                     ORDER BY SUM(a.sanctioned_amount) DESC) AS rnk
    FROM applications a
    JOIN lenders l ON a.lender_id = l.lender_id
    WHERE a.is_disbursed = 1
    GROUP BY month, l.lender_name
)
WHERE rnk = 1
ORDER BY month;

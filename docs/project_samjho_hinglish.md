# Project samjho (Deep ke liye, interview prep)

Ye file GitHub pe chali bhi jaaye toh koi problem nahi hai, lekin ye mainly tumhare padhne ke liye hai.

## Ek line mein project
"Meri brother ki loan DSA firm hai. Unke liye maine loan pipeline analytics banaya: Python se data cleaning, SQL se analysis, aur dashboard. Client data confidential tha, isliye real sanction letters ka structure study karke synthetic data banaya."

## DSA kya hota hai (analogy)
DSA ek property dealer jaisa hai. Ghar builder (bank) deta hai, dealer customer laata hai aur commission (payout) leta hai. **Payout sirf disbursed loan pe milta hai.** Isliye poora project ek sawaal ke around hai: zyada files disbursement tak kaise pahunchein?

## Har step ka "kyun"

| Step | Kya kiya | Kyun |
|---|---|---|
| Synthetic data | Real letters ke fields dekhe, values fake banayi | Privacy. Interview mein ise plus point ki tarah bolo. |
| EMI formula | EMI = P·r·(1+r)^n / ((1+r)^n − 1) | Do bank letters se ₹1 ke andar match hua (₹16 lakh, 9.25%, 180 mahine → formula ₹16,467, letter ₹16,468, kyunki bank upar round karta hai). Ek HFC letter mein ~0.8% ka farak tha, matlab har lender ka method thoda alag ho sakta hai. Interview mein ye detail bolna, isse lagta hai ki tumne khud check kiya. |
| Explore (02) | Pehle sirf problems ki list banayi | Doctor pehle diagnosis karta hai, phir dawai deta hai. |
| Clean (03) | 6 problems fix ki | Ganda data matlab galat answer. "Indore" 4 tarah likha ho toh count 4 hisson mein bant jaata hai. |
| Outlier logic | sanctioned > requested = typo | Business rule se outlier pakda, statistics se nahi. Interviewers ko ye bahut pasand aata hai. |
| SQLite | CSV ko database mein daala | Office mein data database mein hi hota hai. SQL har Data Analyst job mein maanga jaata hai. |
| Funnel | Stage-wise kitni files bachi | Pata chalta hai ki leak kahan hai, jaise paani ki pipe mein. |
| Payout per login | Payout % × approval, dono saath | Sirf payout % dekhoge toh galat lender chunoge. 1% payout aur 50% reject, 0.5% payout aur 10% reject se kharab ho sakta hai. |

## Interview mein aane wale sawaal

**Q: Data fake hai, toh insights ka kya matlab?**
A: "Insights ka pattern maine assumptions se design kiya tha. Project ka point ye dikhana hai ki pipeline ye patterns pakad leti hai. Firm apne real data pe same pipeline chalati hai aur unke real numbers wahan nikalte hain." Ye seedha aur honest jawab hai. Kabhi mat bolna ki synthetic numbers firm ke asli results hain.

**Q: Sabse interesting cheez kya mili?**
A: Do caveats.
1. Year 2 mein logins 13.5% badhe, lekin disbursements sirf 1%. Iski wajah ye hai ki recent files abhi pipeline mein hain, unka result aaya hi nahi (right-censoring). Recent period hamesha kharab dikhta hai.
2. "Not approved" projects ka result ulta aaya, lekin woh sirf 48 files pe based tha. Itne kam data pe conclusion nahi nikalte.

**Q: Missing values kaise handle kiye?**
A: "Pehle dekha ki missing hai *kyun*. Rejected file ka sanction date khaali hona galti nahi hai. Asli missing sirf channel aur ROI mein tha. Channel ko 'Unknown' kiya, aur ROI mein usi lender aur segment ka median bhara."

**Q: Window function kahan use kiya?**
A: "Har mahine ka top lender nikalne ke liye `RANK() OVER (PARTITION BY month ORDER BY disbursed DESC)`."

## Bhai ke liye recommendations (simple bhasha mein)
1. **Login se pehle CIBIL aur FOIR check karo.** Sabse zyada files credit stage pe girti hain.
2. **Achhe profile wale customer bank ko bhejo, borderline wale NBFC/HFC ko.** Sirf payout % dekh ke lender mat chuno, customer ka rate bhi dekho.
3. **Connector wali files ke liye document checklist banao.** FCU mein yahi files sabse zyada fail hoti hain.
4. **Sanction ke 7 din ke andar customer ko follow-up karo.** Sanctioned file chhootna sabse mehenga nuksaan hai.
5. **September mein festive season ki taiyaari karo.** Builder events aur staff pehle se plan karo.

(Ye sab synthetic data ke patterns hain. Bhai apne asli data pe dashboard chala ke check karein.)

## Ek baat yaad rakhna
Bhai ka official email **tab** lena jab unhone tool sach mein use kar liya ho, aur email mein wahi likha ho jo hua: "Deep built a loan pipeline analytics tool and dashboard for our firm, which we use internally."

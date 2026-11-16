# Abandoned-application reminder: keep day 3 for now

**To:** Head of Operations · **From:** Gana Cariappa · **Date:** 16 November 2026
*Portfolio project. All data is simulated for a fictional SME lender.*

## Verdict
1. **Keep the reminder at day 3 for now.** Day 1 brings in more customers, but it pushed unsubscribes past the limit we agreed before the test.
2. **Don't move Micro businesses to day 1.** For them it raised unsubscribes by 2.2 points (4.3% vs 2.2%) and made each customer worth less.
3. **Re-test day 1 for Small and Medium businesses only.** It looks promising there, but this test can't prove it.
4. **Don't extend the re-engagement email to the lowest-scoring 10%.** In the random sample that was emailed, it gained no customers and 4.6% unsubscribed.

## Key numbers
*5,512 customers who abandoned an application, randomly split between a day 1 and a day 3 reminder. Ranges are 95% confidence intervals.*

| | Day 1 vs day 3 | Range |
| --- | --- | --- |
| Conversion | **+4.0 points** (21.3% vs 17.3%) | +1.9 to +6.1 |
| Unsubscribes | **+1.1 points** (limit was +1.0) | +0.3 to +2.0 |
| Value per customer, overall | +£14 | −£56 to +£84: too uncertain to call |
| Micro: unsubscribes | **+2.2 points** | +0.7 to +3.7 |
| Micro: value per customer | **−£51** | −£93 to −£10 |
| Small: conversion | +4.7 points | +1.5 to +7.9 |
| Small: unsubscribes | +0.5 points | −0.6 to +1.5 |

## Re-engagement email (a separate email, to sign-ups who never applied)
- **The model picks the right people.** For the top 40% it emails, conversion rises by **5.8 points** (3.4 to 7.8), almost twice the effect of emailing everyone.
- **The lowest 10% would get nothing from it.** Among the few emailed as a random check: no extra conversions, and 4.6% unsubscribed.
- **The middle group (deciles 3–6) may be worth emailing.** It isn't emailed today, but a small sample suggests about +2 points (0.5 to 3.8). That's a lead, not a proven result.

## Risks
- The unsubscribe breach is marginal (1.1 against 1.0), so a re-test is justified, not a rollout.
- Segment samples are small, so the Small and Medium case for day 1 is promising but not proven.
- Value depends on assumed margins and costs. Repayment also takes months to observe, so a live test would judge value on an early signal, such as the first two repayments.

## Next tests
1. **Day 1 vs day 3 for Small and Medium only, for 6 months,** with the same limits. At about 500 abandoned applications a month, that gives about 1,500 customers per arm, enough to detect a conversion lift of about 4 points. Settling the value question outright would need about 9,600 per arm, roughly 3 years at current volumes, so value should be judged on a faster, less noisy signal, such as the first two repayments.
2. **Email vs no email for deciles 3–6,** randomised, to confirm whether extending the model's reach adds customers without extra unsubscribes.

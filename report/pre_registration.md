# Pre-registration: abandoned-application reminder, day 1 vs day 3

*Locked 16 November 2026, before the results were analysed. All data is simulated for a fictional SME lender.*

## The question
When an SME customer abandons a loan application, should the reminder email go out after 1 day or after 3 days?

- **Control:** day 3 (assumed current practice)
- **Treatment:** day 1
- **Who:** every customer who abandoned an application, randomised 50/50 to an arm when they abandoned

## Hypothesis
A day 1 reminder catches customers while the application is still fresh, so it raises conversion. It may also feel pushy, raising unsubscribes and complaints, and it may pull in customers who are less ready to borrow. So the extra conversions could be worth less.

## Decision metric: conversion
The share of randomised customers who complete their application.

## Value check (non-inferiority): value per customer
Day 1 must not be meaningfully worse on value. Measured per **customer randomised**, not per conversion, so both arms are compared on the same base (intention to treat).

> **Value = (loan value × 12%) if the loan is repaid on time, or (loan value × −20%) if it isn't, minus the contact cost**
>
> Contact cost: **£100 if the customer complained**; otherwise **£40 if they unsubscribed**; otherwise £0. A complaint replaces the unsubscribe cost; the two are never added together.

| Assumption | Value | What it represents |
| --- | --- | --- |
| Margin on a loan repaid on time | 12% of loan value | Simplified lifetime margin |
| Cost of a loan not repaid on time | −20% of loan value | **Assumption:** a blended cost of late payment and default, covering collections effort and losses |
| Cost of an unsubscribe | £40 | Lost future value of being able to email the customer |
| Cost of a complaint | £100 | Handling time and reputational cost |

These are illustrative assumptions, not real figures, which is why the sensitivity check below matters.

## Guardrail metrics
Day 1 must not breach either guardrail, overall or in any segment:

A breach is judged on the **point estimate** of the difference.

- **Unsubscribe rate:** no more than **1.0 percentage point** higher than day 3
- **Complaint rate:** no more than **0.3 percentage points** higher than day 3

## Pre-specified segments
Only three segments are analysed, chosen in advance: **Micro, Small and Medium** (by annual turnover). Sectors aren't analysed, to avoid fishing for a result.

## Power and minimum detectable effect
Expected sample: about 5,500 abandoned applications, so about 2,750 per arm. Day 3 conversion is assumed to be about 17.5%. Significance level 5% (two-sided), power 80%.

| Comparison | Customers per arm | Smallest conversion difference we can reliably detect |
| --- | --- | --- |
| Overall | ~2,750 | **2.9 percentage points** |
| Micro or Small | ~1,100 | 4.6 pp (5.3 pp after correcting for multiple segments) |
| Medium | ~550 | 6.0 pp |

**What this means:** the test is powered for an **overall** decision. Segment results are **directional** unless they're very large. Value per customer is noisier still, because loan sizes vary a lot, so segment-level value results will be reported with their uncertainty, not treated as proven.

## Analysis plan
1. **Clean:** count only each customer's **first** abandonment; remove duplicate reminder sends; exclude reminders with no recorded test arm; treat conversions with a missing loan value as missing (counted in conversion, excluded from value), reporting the count **by arm**.
2. **Check randomisation:** a chi-square **sample-ratio mismatch** test on arm sizes against the planned 50/50 split, plus the segment mix by arm.
3. **Conversion:** rate per arm with 95% confidence intervals, and a two-proportion z-test on the difference.
4. **Value per customer:** mean per arm, with a **bootstrap** 95% confidence interval on the difference (2,000 resamples, fixed seed). The bootstrap is used because value is heavily skewed: most customers are worth £0 and a few are worth thousands.
5. **Guardrails:** unsubscribe and complaint rates per arm.
6. **Segments:** repeat steps 3–5 for Micro, Small and Medium, applying a Bonferroni correction (three segments, so 0.05 ÷ 3 ≈ 0.017) to any segment-level claim of significance.
7. **No peeking:** the analysis runs once, on the full planned sample.

## Decision rule
**Value check outcome** (on the bootstrap 95% CI of day 1 minus day 3):
- **FAIL** if the upper bound is below £0 (day 1 clearly worse). FAIL takes precedence if both conditions hold.
- **PASS** if the lower bound is above −£50 (a loss of more than £50 per customer, about 19% of expected value, is ruled out).
- **INCONCLUSIVE** otherwise.

A −£50 margin was chosen because a tighter one cannot be tested at this sample size: a −£5 margin would need about 957,000 customers per arm. At about 2,750 per arm, a PASS is unlikely even if day 1 is truly as good, so INCONCLUSIVE is the expected outcome and is planned for.

**Overall decision**
- **Roll out day 1** if conversion is significantly higher (p < 0.05), no guardrail is breached, and the value check PASSES.
- **If the value check is INCONCLUSIVE:** roll out day 1 only where conversion and guardrails pass, keep a **15% day 3 holdout**, and size a follow-up test for value (about 9,600 per arm).
- **If the value check FAILS, or conversion isn't significantly higher:** keep day 3.

**Segments** (Micro, Small, Medium) can only veto. Keep day 3 in any segment where day 1 breaches a guardrail or its value check FAILS.

## Sensitivity check
The verdict depends on the four assumptions, so the decision is re-run with **each assumption at 0.5× and 2×, one at a time** (8 runs). For each run, report whether the verdict changes, overall and for each segment. If a verdict flips under any single change, it is reported as **fragile**, and the assumption that flips it is named.

## Known limitation
Repayment outcomes take months to observe in reality. A live test couldn't wait that long, so it would need an early proxy, such as whether the **first two repayments** were made on time. This simulated test assumes repayment is already known.

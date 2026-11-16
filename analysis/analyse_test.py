"""
Split-test analysis: abandoned-application reminder, day 1 vs day 3. Follows report/pre_registration.md.
SIMULATED data. Run from the project folder:  python3 analysis/analyse_test.py
Needs numpy (pip3 install numpy matplotlib).
"""
import math, os, sqlite3
from statistics import NormalDist
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "lender.db"))
con.executescript(open(os.path.join(ROOT, "sql", "01_test_population.sql")).read().split("SELECT * FROM test_population")[0])
rows = con.execute("SELECT test_arm, segment, converted, loan_value, repaid_on_time, unsubscribed, complained FROM test_population").fetchall()

BASE = dict(margin=0.12, late_cost=0.20, unsub_cost=40.0, complaint_cost=100.0)   # pre-registered assumptions
GUARD = dict(unsub=0.010, complaint=0.003)                                       # max allowed increase (day 1 - day 3)
NI_MARGIN, B, ALPHA = -50.0, 2000, 0.05
Z = NormalDist()
rng = np.random.default_rng(2030)


def value(r, a):
    """Value of one customer under assumptions a. None if converted but loan value is missing."""
    arm, seg, conv, loan, repaid, unsub, compl = r
    if conv == 1 and loan is None:
        return None
    v = 0.0
    if conv == 1:
        v = loan * (a["margin"] if repaid == 1 else -a["late_cost"])
    v -= a["complaint_cost"] if compl else (a["unsub_cost"] if unsub else 0.0)
    return v


def two_prop(x1, n1, x0, n0):
    """Difference in proportions (day1 - day3), 95% CI, two-sided z-test p-value."""
    p1, p0 = x1 / n1, x0 / n0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)            # for the CI
    pp = (x1 + x0) / (n1 + n0)
    se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n0))                  # pooled, for the test
    p = 2 * (1 - Z.cdf(abs((p1 - p0) / se0)))
    return p1, p0, p1 - p0, (p1 - p0 - 1.96 * se, p1 - p0 + 1.96 * se), p


def boot_diff(v1, v0):
    """Bootstrap 95% CI for mean(v1) - mean(v0): resample each arm with replacement, 2,000 times."""
    v1, v0 = np.array(v1), np.array(v0)
    d = rng.choice(v1, (B, len(v1))).mean(1) - rng.choice(v0, (B, len(v0))).mean(1)
    return v1.mean() - v0.mean(), np.percentile(d, 2.5), np.percentile(d, 97.5)


def value_outcome(lo, hi):
    if hi < 0:
        return "FAIL"
    return "PASS" if lo > NI_MARGIN else "INCONCLUSIVE"


def analyse(subset, a, alpha):
    d1 = [r for r in subset if r[0] == "day1"]; d3 = [r for r in subset if r[0] == "day3"]
    conv = two_prop(sum(r[2] for r in d1), len(d1), sum(r[2] for r in d3), len(d3))
    unsub = np.mean([r[5] for r in d1]) - np.mean([r[5] for r in d3])
    compl = np.mean([r[6] for r in d1]) - np.mean([r[6] for r in d3])
    v1 = [v for v in (value(r, a) for r in d1) if v is not None]
    v0 = [v for v in (value(r, a) for r in d3) if v is not None]
    diff, lo, hi = boot_diff(v1, v0)
    return dict(n1=len(d1), n0=len(d3), conv=conv, conv_sig=conv[4] < alpha, unsub=unsub, compl=compl,
                guard_ok=unsub <= GUARD["unsub"] and compl <= GUARD["complaint"],
                v1=np.mean(v1), v0=np.mean(v0), vdiff=diff, vlo=lo, vhi=hi, vout=value_outcome(lo, hi))


def decide(a):
    overall = analyse(rows, a, ALPHA)
    segs = {s: analyse([r for r in rows if r[1] == s], a, ALPHA / 3) for s in ["Micro", "Small", "Medium"]}
    if not overall["conv_sig"] or not overall["guard_ok"] or overall["vout"] == "FAIL":
        verdict = {s: "day 3" for s in segs}
    else:
        verdict = {s: ("day 3" if (not r["guard_ok"] or r["vout"] == "FAIL")
                       else ("day 1" if overall["vout"] == "PASS" else "day 1 + 15% holdout"))
                   for s, r in segs.items()}
    return overall, segs, verdict


if __name__ == "__main__":
    # Sample-ratio mismatch: chi-square test of arm sizes against a 50/50 plan (1 degree of freedom)
    n1 = sum(r[0] == "day1" for r in rows); n0 = len(rows) - n1
    chi2 = (n1 - len(rows) / 2) ** 2 / (len(rows) / 2) * 2
    print(f"Randomised customers: {len(rows):,}  (day 1: {n1:,}, day 3: {n0:,})")
    print(f"Sample-ratio check: chi-square {chi2:.2f}, p = {2 * (1 - Z.cdf(math.sqrt(chi2))):.3f}  (p < 0.01 would signal a broken split)")
    for arm in ("day1", "day3"):
        c = [r for r in rows if r[0] == arm and r[2] == 1]
        print(f"  {arm}: {len(c)} conversions, {sum(r[3] is None for r in c)} missing loan value")

    overall, segs, verdict = decide(BASE)
    print("\n            n(d1/d3)   conv d1   conv d3   diff [95% CI]            p      unsub+   compl+   value d1/d3   value diff [95% CI]   value")
    for name, r in [("Overall", overall)] + list(segs.items()):
        p1, p0, d, ci, p = r["conv"]
        print(f"{name:<8} {r['n1']:>5}/{r['n0']:<5}  {p1:7.1%}  {p0:7.1%}  {d:+6.1%} [{ci[0]:+.1%}, {ci[1]:+.1%}]  {p:6.3f}  "
              f"{r['unsub']:+6.1%}  {r['compl']:+6.1%}   £{r['v1']:>4.0f}/£{r['v0']:<4.0f}   £{r['vdiff']:+5.0f} [£{r['vlo']:+.0f}, £{r['vhi']:+.0f}]   {r['vout']}")
    print("\nVerdict by segment:", verdict)

    print("\nSensitivity: each assumption at 0.5x and 2x, one at a time")
    for k in BASE:
        for mult in (0.5, 2):
            a = dict(BASE, **{k: BASE[k] * mult})
            o, s, v = decide(a)
            flag = "" if v == verdict else "   <-- VERDICT CHANGES"
            print(f"  {k:<15} x{mult:<3} overall value {o['vout']:<12} verdict {v}{flag}")

"""
Model check chart: conversion uplift from the re-engagement email vs unsubscribe rate, by model-score decile.
SIMULATED data. Run from the project folder:  python3 analysis/model_check_chart.py
"""
import math, os, sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "lender.db"))
con.executescript(open(os.path.join(ROOT, "sql", "05_score_deciles.sql")).read().split("SELECT * FROM")[0])
rows = con.execute("""SELECT decile,
       SUM(emailed), SUM(emailed * converted), SUM(1 - emailed), SUM((1 - emailed) * converted),
       AVG(CASE WHEN emailed = 1 THEN unsubscribed END)
FROM reengagement_deciles GROUP BY decile ORDER BY decile""").fetchall()

dec, up, err, unsub, targeted = [], [], [], [], []
for d, n1, x1, n0, x0, u in rows:
    p1, p0 = x1 / n1, x0 / n0
    # Agresti-Caffo 95% CI: add one success and one failure to each group, so a group
    # with zero conversions doesn't produce a falsely narrow interval
    a1, a0 = (x1 + 1) / (n1 + 2), (x0 + 1) / (n0 + 2)
    se = math.sqrt(a1 * (1 - a1) / (n1 + 2) + a0 * (1 - a0) / (n0 + 2))
    centre = a1 - a0
    dec.append(d); up.append(100 * (p1 - p0)); unsub.append(100 * u)
    err.append([100 * ((p1 - p0) - (centre - 1.96 * se)), 100 * ((centre + 1.96 * se) - (p1 - p0))])
    targeted.append(n1 / (n1 + n0) > 0.5)

INK, MUTED, GRID = "#1f2933", "#6b7280", "#e5e7eb"
TARGET, EXPLORE, UNSUB = "#1d4e89", "#9db4d3", "#c2410c"

fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
ax.bar(dec, up, color=[TARGET if t else EXPLORE for t in targeted], width=0.62, zorder=2)
ax.errorbar(dec, up, yerr=[[e[0] for e in err], [e[1] for e in err]], fmt="none", ecolor=INK, elinewidth=1, capsize=3, zorder=3)
ax.plot(dec, unsub, color=UNSUB, marker="o", linewidth=2, zorder=4)
ax.axhline(0, color=INK, linewidth=0.8, zorder=1)

ax.set_xticks(dec)
ax.set_xticklabels([str(d) for d in dec])
ax.set_xlabel("Model score decile (1 = lowest score, 10 = highest)", color=INK)
ax.set_ylabel("Percentage points", color=INK)
ax.grid(axis="y", color=GRID, zorder=0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(colors=MUTED)

ax.text(1.25, unsub[0] + 0.6, "Unsubscribe rate\namong those emailed", color=UNSUB, fontsize=9, ha="left", va="bottom")
ax.text(4.5, 11.3, "Mostly not emailed\n(15% random sample)", color=MUTED, fontsize=9, ha="center")
ax.text(8.5, 11.3, "Emailed by the model\n(10% random hold-out)", color=TARGET, fontsize=9, ha="center")
ax.axvline(6.5, color=GRID, linewidth=1, linestyle="--", zorder=1)
ax.set_ylim(-3, 13)

fig.suptitle("The email lifts conversion most for high scorers; in the lowest decile it only adds unsubscribes",
             x=0.02, ha="left", fontsize=12, fontweight="bold", color=INK)
ax.set_title("Re-engagement email to customers who never started an application (not the day 1 vs day 3 test).\nBars: conversion uplift, emailed minus not emailed, with 95% CI. Simulated data.",
             loc="left", fontsize=9, color=MUTED, pad=8)
fig.tight_layout()
out = os.path.join(ROOT, "report", "model_check_chart.png")
fig.savefig(out, facecolor="white")
print("Saved", out)

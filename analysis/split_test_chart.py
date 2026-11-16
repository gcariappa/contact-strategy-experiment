"""
Headline chart: day 1 vs day 3 reminder, by segment. Conversion uplift next to the extra unsubscribes,
with the pre-registered unsubscribe guardrail marked. SIMULATED data.
Run from the project folder:  python3 analysis/split_test_chart.py
"""
import math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyse_test import rows, GUARD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
groups = ["Overall", "Micro", "Small", "Medium"]


def diff_ci(subset, col):
    """Day 1 minus day 3 for a 0/1 column, with a 95% CI (percentage points)."""
    a = [r[col] for r in subset if r[0] == "day1"]; b = [r[col] for r in subset if r[0] == "day3"]
    p1, p0 = sum(a) / len(a), sum(b) / len(b)
    se = math.sqrt(p1 * (1 - p1) / len(a) + p0 * (1 - p0) / len(b))
    return 100 * (p1 - p0), 100 * 1.96 * se


conv, unsub = [], []
for g in groups:
    sub = rows if g == "Overall" else [r for r in rows if r[1] == g]
    conv.append(diff_ci(sub, 2)); unsub.append(diff_ci(sub, 5))

INK, MUTED, GRID = "#1f2933", "#6b7280", "#e5e7eb"
CONV, UNSUB_OK, UNSUB_BAD = "#1d4e89", "#b8bec7", "#c2410c"
limit = 100 * GUARD["unsub"]

x = np.arange(len(groups)); w = 0.36
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
ax.bar(x - w / 2, [c[0] for c in conv], w, yerr=[c[1] for c in conv], color=CONV,
       capsize=3, error_kw=dict(ecolor=INK, elinewidth=1), label="Conversion uplift", zorder=2)
ax.bar(x + w / 2, [u[0] for u in unsub], w, yerr=[u[1] for u in unsub],
       color=[UNSUB_BAD if u[0] > limit else UNSUB_OK for u in unsub],
       capsize=3, error_kw=dict(ecolor=INK, elinewidth=1), label="Extra unsubscribes", zorder=2)
ax.axhline(limit, color=UNSUB_BAD, linestyle="--", linewidth=1.2, zorder=3,
           label=f"Unsubscribe limit (+{limit:.1f} pp, set in advance)")
ax.axhline(0, color=INK, linewidth=0.8, zorder=1)

ax.set_xticks(x)
names = ["All customers"] + [f"{g} businesses" for g in groups[1:]]
ax.set_xticklabels([f"{n}\n+{c[0]:.1f} conv / +{u[0]:.1f} unsub" for n, c, u in zip(names, conv, unsub)], color=INK)
ax.set_ylabel("Day 1 minus day 3, percentage points", color=INK)
ax.set_ylim(-3, 12)
ax.grid(axis="y", color=GRID, zorder=0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(colors=MUTED)
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
ax.legend(handles=[Patch(color=CONV, label="Conversion uplift"),
                   Patch(color=UNSUB_BAD, label="Extra unsubscribes, over the limit"),
                   Patch(color=UNSUB_OK, label="Extra unsubscribes, within the limit"),
                   Line2D([0], [0], color=UNSUB_BAD, linestyle="--", label=f"Unsubscribe limit (+{limit:.1f} pp, set in advance)")],
          frameon=False, loc="upper right", fontsize=9)

fig.suptitle("Day 1 lifts conversion, but Micro pushes unsubscribes over the limit",
             x=0.02, ha="left", fontsize=12, fontweight="bold", color=INK)
ax.set_title("Abandoned-application reminder, day 1 vs day 3. Bars show 95% CIs. Simulated data.",
             loc="left", fontsize=9, color=MUTED, pad=8)
fig.tight_layout()
out = os.path.join(ROOT, "report", "split_test_chart.png")
fig.savefig(out, facecolor="white")
print("Saved", out)

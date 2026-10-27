#!/usr/bin/env python3
"""Draw img/scores.png: a histogram of every team's total from the final leaderboard.

Totals transcribed from the leaderboard photo (img/leaderboard.jpg), in rank order. Their mean, 2301.35, matches the
average the leaderboard showed.
"""
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

TOTALS = [
    3987.89, 3636.04, 3590.67, 3466.88, 3433.81, 3428.61, 3394.79, 3321.44, 3174.02, 3167.09, 3164.87, 3136.90,
    3100.65, 3003.41, 2964.81, 2929.14, 2900.76, 2887.13, 2880.85, 2877.43, 2875.51, 2873.37, 2865.93, 2747.40,
    2736.19, 2725.23, 2714.83, 2711.63, 2703.86, 2630.00, 2624.96, 2564.31, 2555.30, 2520.98, 2454.56, 2426.67,
    2413.52, 2405.58, 2376.16, 2280.88, 2271.79, 2239.33, 2237.73, 2122.63, 2120.76, 2018.93, 1956.15, 1937.60,
    1905.55, 1817.55, 1812.11, 1686.36, 1674.14, 1580.46, 1562.87, 1442.81, 1406.88, 1379.71, 1195.93, 1180.79,
    1030.75, 994.33, 761.51, 661.77, 352.40, 289.11, 148.99, 48.76,
]
assert len(TOTALS) == 68 and round(sum(TOTALS) / 68, 2) == 2301.35

BG, INK, MUTED, GRID, BAR, ACCENT = "#121418", "#e7e9ee", "#9aa1ad", "#2e333c", "#7a8394", "#8ea5ff"
WIDTH, MAX = 250, 4300
mean, median, mite = statistics.mean(TOTALS), statistics.median(TOTALS), TOTALS[0]

plt.rcParams.update({"text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

edges = list(range(0, MAX + WIDTH, WIDTH))
_, _, bars = ax.hist(TOTALS, bins=edges, color=BAR, edgecolor=BG, linewidth=1.5, zorder=2)
for bar in bars:
    if bar.get_x() <= mite < bar.get_x() + WIDTH:
        bar.set_facecolor(ACCENT)  # the bin holding Mite's score, which no other team reached

ax.axvline(mean, color=INK, lw=1.2, ls="--", zorder=3)
ax.axvline(median, color=INK, lw=1.2, ls=":", zorder=3)
ax.legend(handles=[
    Patch(color=BAR, label="Other teams"),
    Patch(color=ACCENT, label=f"Mite (me), 1st: {mite:.2f}"),
    plt.Line2D([], [], color=INK, lw=1.2, ls="--", label=f"Mean: {mean:.2f}"),
    plt.Line2D([], [], color=INK, lw=1.2, ls=":", label=f"Median: {median:.2f}"),
], loc="upper left", frameon=True, facecolor=BG, edgecolor=GRID, labelcolor=INK, fontsize=10)

ax.set_xlim(0, MAX)
ax.set_xticks(range(0, MAX + 1, 500))
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(MUTED)
ax.set_xlabel(f"Total score (out of {MAX}), bins of {WIDTH} points", fontsize=11)
ax.set_ylabel("Number of teams", fontsize=11)
ax.set_title("Distribution of total scores, all 68 teams", fontsize=13, pad=12)
fig.tight_layout()
fig.savefig("img/scores.png", facecolor=BG)

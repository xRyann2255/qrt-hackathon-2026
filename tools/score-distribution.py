#!/usr/bin/env python3
"""Draw img/scores.png: every team's total from the final leaderboard, one dot per team.

Totals transcribed from the leaderboard photo (img/leaderboard.jpg), in rank order. Their mean, 2301.35, matches the
average the leaderboard showed.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TOTALS = [
    3987.89, 3636.04, 3590.67, 3466.88, 3433.81, 3428.61, 3394.79, 3321.44, 3174.02, 3167.09, 3164.87, 3136.90,
    3100.65, 3003.41, 2964.81, 2929.14, 2900.76, 2887.13, 2880.85, 2877.43, 2875.51, 2873.37, 2865.93, 2747.40,
    2736.19, 2725.23, 2714.83, 2711.63, 2703.86, 2630.00, 2624.96, 2564.31, 2555.30, 2520.98, 2454.56, 2426.67,
    2413.52, 2405.58, 2376.16, 2280.88, 2271.79, 2239.33, 2237.73, 2122.63, 2120.76, 2018.93, 1956.15, 1937.60,
    1905.55, 1817.55, 1812.11, 1686.36, 1674.14, 1580.46, 1562.87, 1442.81, 1406.88, 1379.71, 1195.93, 1180.79,
    1030.75, 994.33, 761.51, 661.77, 352.40, 289.11, 148.99, 48.76,
]
assert len(TOTALS) == 68 and round(sum(TOTALS) / 68, 2) == 2301.35

BG, INK, MUTED, RULE, DOT, ACCENT = "#121418", "#e7e9ee", "#9aa1ad", "#2e333c", "#6b7280", "#8ea5ff"
BIN, MAX = 200, 4300

# Stack the dots in each 200 point bin, lowest score at the bottom
height = {}
xs, ys = [], []
for t in sorted(TOTALS):
    b = int(t // BIN)
    height[b] = height.get(b, 0) + 1
    xs.append(b * BIN + BIN / 2)
    ys.append(height[b])

fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.scatter(xs[:-1], ys[:-1], s=150, color=DOT, linewidths=0, zorder=2)
ax.scatter(xs[-1], ys[-1], s=150, color=ACCENT, linewidths=0, zorder=3)  # the top score is last after sorting

mean = sum(TOTALS) / len(TOTALS)
ax.axvline(mean, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.text(mean - 40, 9.3, f"Average {mean:.2f}", color=MUTED, fontsize=10, va="top", ha="right")
ax.text(xs[-1], ys[-1] + 0.8, "Mite (me)\n1st, 3987.89", color=ACCENT, fontsize=10.5, fontweight="bold",
        ha="center", va="bottom", linespacing=1.3)

ax.set_xlim(0, MAX)
ax.set_ylim(0.3, 9.6)
ax.set_xticks(range(0, MAX + 1, 500))
ax.set_yticks([])
ax.tick_params(colors=MUTED, labelsize=9.5, length=0, pad=6)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(RULE)
ax.set_xlabel("Total score, out of a possible 4300", color=MUTED, fontsize=10, labelpad=8)
fig.text(0.03, 0.93, "Total scores of all 68 teams", color=INK, fontsize=13, fontweight="bold")
fig.text(0.03, 0.865, "Each dot is one team, grouped in steps of 200 points.", color=MUTED, fontsize=10)
fig.subplots_adjust(left=0.03, right=0.97, top=0.8, bottom=0.17)
fig.savefig("img/scores.png", facecolor=BG)

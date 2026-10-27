#!/usr/bin/env python3
"""Recreate the final leaderboard as shown on screen at the event: leaderboard.json -> leaderboard.html -> img/leaderboard.png.

leaderboard.json is a transcription of a photo of the screen at the event, with names cut off where the screen cut
them. Needs google-chrome; optipng is used if installed.
"""
import html
import json
import shutil
import statistics
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PNG = HERE.parents[1] / "img" / "leaderboard.png"
W, H = 1920, 1064  # CSS px; rendered at device scale 2

# Totals checked earlier against the average the leaderboard showed (git show 9c5a2c4:tools/score-distribution.py).
TOTALS = [
    3987.89, 3636.04, 3590.67, 3466.88, 3433.81, 3428.61, 3394.79, 3321.44, 3174.02, 3167.09, 3164.87, 3136.90,
    3100.65, 3003.41, 2964.81, 2929.14, 2900.76, 2887.13, 2880.85, 2877.43, 2875.51, 2873.37, 2865.93, 2747.40,
    2736.19, 2725.23, 2714.83, 2711.63, 2703.86, 2630.00, 2624.96, 2564.31, 2555.30, 2520.98, 2454.56, 2426.67,
    2413.52, 2405.58, 2376.16, 2280.88, 2271.79, 2239.33, 2237.73, 2122.63, 2120.76, 2018.93, 1956.15, 1937.60,
    1905.55, 1817.55, 1812.11, 1686.36, 1674.14, 1580.46, 1562.87, 1442.81, 1406.88, 1379.71, 1195.93, 1180.79,
    1030.75, 994.33, 761.51, 661.77, 352.40, 289.11, 148.99, 48.76,
]

data = json.loads((HERE / "leaderboard.json").read_text())
hdr, rows = data["header"], data["rows"]

assert [r["rank"] for r in rows] == list(range(1, 69))
totals = [r["total"] for r in rows]
assert totals == TOTALS and totals == sorted(totals, reverse=True)
assert hdr["teams"] == len(rows) and hdr["average"] == round(statistics.mean(totals), 2) == 2301.35
assert hdr["highest"] == totals[0]
bad = []
for r in rows:
    shown = [s for s in r["scores"] if s is not None]
    assert len(r["scores"]) == 5 and all(0 <= s <= m for s, m in zip(shown, hdr["maxima"]))
    if abs(sum(shown) - r["total"]) > 0.5 * len(shown):  # cells are rounded to integers
        bad.append((r["rank"], sum(shown), r["total"]))
assert not bad, bad

# The page shows the best score on each question in bold.
best = [max(r["scores"][q] or 0 for r in rows) for q in range(5)]


def row(r):
    cells = "".join(
        f'<span{" class=best" if s is not None and s == best[q] else ""}>{"" if s is None else s}</span>'
        for q, s in enumerate(r["scores"])
    )
    medal = {1: " gold", 2: " silver", 3: " bronze"}.get(r["rank"], "")
    return (
        f'<div class=row><span class="rank{medal}">{r["rank"]}</span>'
        f'<div class=who><b>{html.escape(r["team"])}</b><small>{html.escape(r["members"])}</small></div>'
        f'<div class=pts><b>{r["total"]:.2f}</b><div class=q>{cells}</div></div></div>'
    )


maxima = "".join(f"<span>{m}</span>" for m in hdr["maxima"])
columns = "".join(
    f'<section><header><span>Rank</span><span>Team</span><div class=pts><span>Score</span>'
    f'<div class=q>{maxima}</div></div></header>{"".join(row(r) for r in rows[c:c + 17])}</section>'
    for c in range(0, 68, 17)
)
page = f"""<!doctype html>
<meta charset=utf-8>
<title>{html.escape(hdr["title"])}: {hdr["subtitle"]}</title>
<style>
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: {W}px; height: {H}px; padding: 8px; background: #f1f2f0; color: #2a2a2a;
  font-family: "Noto Sans", "Segoe UI", sans-serif; }}
.bar {{ display: flex; align-items: center; height: 48px; padding: 0 10px 0 18px; border-radius: 6px;
  background: #3a3530; color: #f4f2ef; }}
.logo {{ width: 30px; font-size: 8px; font-weight: 700; line-height: 1; text-align: center; color: #b9c6e8; }}
.logo::before {{ content: ""; display: block; width: 9px; height: 9px; margin: 0 auto 2px; border-radius: 50%;
  background: #7e95d6; }}
h1 {{ margin-left: 10px; font-size: 19px; }}
.sub {{ margin: 3px auto 0 14px; font-size: 13px; color: #b4ada5; }}
.stat {{ margin-left: 26px; font-size: 16px; font-weight: 700; }}
.stat small {{ margin-right: 8px; font-size: 12px; font-weight: 400; letter-spacing: .04em; color: #8c857d;
  text-transform: uppercase; }}
.refresh {{ display: grid; place-items: center; width: 38px; height: 32px; margin-left: 22px; border-radius: 7px;
  background: #4c9a6f; }}
main {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 10px; }}
section {{ height: 990px; border: 1px solid #cdd3d6; border-radius: 6px; background: #e6eaec; overflow: hidden; }}
header {{ display: flex; height: 46px; padding: 10px 12px 0 13px; background: #3a3530; color: #ece8e3;
  font-size: 11px; font-weight: 700; letter-spacing: .03em; text-transform: uppercase; }}
header > span:nth-child(2) {{ margin-left: 17px; }}
header .pts {{ margin-left: auto; text-align: left; }}
header .q {{ margin-top: 3px; font-size: 10.5px; font-weight: 400; color: #d2ccc5; }}
.row {{ display: flex; align-items: center; height: 55px; padding: 0 12px 0 8px; }}
.row:first-of-type {{ margin-top: 3px; }}
.rank {{ display: grid; place-items: center; flex: none; width: 34px; height: 34px; border-radius: 50%;
  background: #d9dfe2; color: #5b6166; font-size: 13px; font-weight: 700; }}
.gold {{ background: #d6a81d; color: #fff; }}
.silver {{ background: #9da1a4; color: #fff; }}
.bronze {{ background: #b2672b; color: #fff; }}
.who {{ flex: 1; min-width: 0; margin-left: 15px; white-space: nowrap; }}
.who b {{ display: block; font-size: 16px; line-height: 21px; }}
.who small {{ display: block; font-size: 12px; line-height: 17px; color: #868c91; }}
.pts {{ text-align: right; white-space: nowrap; }}
.pts > b {{ display: block; font-size: 20px; line-height: 24px; color: #3f8d69; }}
.q {{ display: flex; justify-content: flex-end; font-size: 11.5px; line-height: 16px; color: #6f7478; }}
.q span {{ width: 36.5px; text-align: right; }}
.q .best {{ font-weight: 700; color: #1d1d1d; }}
</style>
<div class=bar><span class=logo>QRT</span><h1>{html.escape(hdr["title"])}</h1><span class=sub>{hdr["subtitle"]}</span>
<span class=stat><small>Teams</small>{hdr["teams"]}</span><span class=stat><small>Average</small>{hdr["average"]:.2f}</span>
<span class=stat><small>Highest</small>{hdr["highest"]:.2f}</span>
<span class=refresh><svg width=18 height=18 viewBox="0 0 24 24" fill=none stroke=#e8f5ec stroke-width=2.6
stroke-linecap=round stroke-linejoin=round><path d="M20 11a8 8 0 0 0-14.3-4.5M4 13a8 8 0 0 0 14.3 4.5"/>
<path d="M5 3v4h4M19 21v-4h-4"/></svg></span></div>
<main>{columns}</main>
"""
(HERE / "leaderboard.html").write_text(page)

# Headless Chrome paints only its viewport, which is shorter than --window-size, so shoot taller and crop.
subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={W},{H + 200}", f"--screenshot={PNG}", (HERE / "leaderboard.html").as_uri()],
               check=True, capture_output=True)
Image.open(PNG).crop((0, 0, 2 * W, 2 * H)).save(PNG)
if shutil.which("optipng"):
    subprocess.run(["optipng", "-quiet", "-o2", str(PNG)], check=True)
print(PNG)

"""Q5 demo: cut the visitor's text into pages and pieces as the problem describes, run the general solver, score it.

solver.py and generator.py are the team's general heuristic and test generator, copied unchanged apart from
renaming identifiers. make_case follows generator.generate_case, with the visitor's paragraphs as the pages.
"""
import json
import random
import re
import time

import generator as g
import solver


def make_case(text, seed, extras):
    rng = random.Random(seed)
    docs = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text) if p.strip()][:3]
    pages, records = [], []
    for page_id, doc in enumerate(docs):  # one paragraph per page, own width and height, text past the height dropped
        rows = g.wrap_page(doc, rng.randint(40, 60), rng.randint(10, 14), rng)
        pages.append(rows)
        cut = rng.choice([g._band_rectangles, g._guillotine_rectangles])
        for row, col, ph, pw in cut(len(rows[0]), len(rows), rng):
            piece = [line[col:col + pw] for line in rows[row:row + ph]]
            if any(ch != " " for line in piece for ch in line):
                records.append((g.encode(piece), page_id, row, col))
    other = g.make_page(rng)  # extra pieces come from another document
    for _ in range(extras):
        while True:
            ph, pw = rng.randint(1, 3), rng.randint(3, 10)
            row, col = rng.randrange(len(other) - ph + 1), rng.randrange(len(other[0]) - pw + 1)
            piece = [line[col:col + pw] for line in other[row:row + ph]]
            if any(ch != " " for line in piece for ch in line):
                records.append((g.encode(piece), None, row, col))
                break
    rng.shuffle(records)
    return {"pieces": [r[0] for r in records], "pages": pages,
            "truth": [[i, r[1], r[2], r[3]] for i, r in enumerate(records) if r[1] is not None],
            "extras": [i for i, r in enumerate(records) if r[1] is None]}


def run(text, seed, extras):
    case = make_case(text, int(seed), int(extras))
    if not case["pages"]:
        return json.dumps({"error": "no text"})
    t = time.time()
    placements = solver._assemble_greedy(case["pieces"])
    elapsed = time.time() - t
    score = g.score_prediction(case, placements)
    # Rebuild each output page; a character is correct if the matched original page has it at the best shift.
    match = {m["predicted_page"]: (m["true_page"], m["shift"]) for m in score["character_matches"]}
    chars = {}
    for pid, page, row, col in placements:
        for dr, line in enumerate(g.decode(case["pieces"][pid])):
            for dc, ch in enumerate(line):
                chars.setdefault(page, {})[row + dr, col + dc] = ch
    out = []
    for page, cells in chars.items():
        r0, c0 = min(r for r, _ in cells), min(c for _, c in cells)
        r1, c1 = max(r for r, _ in cells), max(c for _, c in cells)
        rows, ok = [], []
        for r in range(r0, r1 + 1):
            line, flags = "", ""
            for c in range(c0, c1 + 1):
                ch = cells.get((r, c), " ")
                line += ch
                if page in match:
                    true_page, (sr, sc) = match[page]
                    orig = case["pages"][true_page]
                    good = 0 <= r + sr < len(orig) and 0 <= c + sc < len(orig[0]) and orig[r + sr][c + sc] == ch
                else:
                    good = False
                flags += "1" if good or ch == " " else "0"
            rows.append(line)
            ok.append(flags)
        out.append({"rows": rows, "ok": ok, "matched": page in match, "size": sum(ch != " " for ch in cells.values())})
    out.sort(key=lambda p: -p["size"])
    return json.dumps({"pieces": case["pieces"], "extras": case["extras"], "pages": case["pages"], "out": out,
                       "score": score["character_score"], "seconds": elapsed})


if __name__ == "__main__":
    text = "\n\n".join(g.PARAGRAPHS[:2])
    r = json.loads(run(text, 1, 2))
    assert len(r["pages"]) == 2 and len(r["extras"]) == 2 and 0 <= r["score"] <= 100
    print(len(r["pieces"]), "pieces,", round(r["score"], 1), "%,", round(r["seconds"], 2), "s")

#!/usr/bin/env python3
"""Independent Document Lego fixtures, exact reconstruction scoring, and benchmark CLI.

Stdlib only.  ``generate_case`` returns encoded pieces and their original positions.
``score_prediction`` reports both piece-position and literal-character accuracy;
identical pieces can legitimately differ in the first measure.  The prose below is
an independent, original test corpus and must not be imported by a solver.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import re
import time


CORPUS = r"""
The keeper of the northern lighthouse rose before sunrise and carried a kettle to the small kitchen. Beyond the window, pale waves moved across the harbour. A fishing boat returned with its lamps still burning. She checked the weather instruments, wrote a careful entry in the log, and climbed the narrow stairs. The lamp had turned throughout the night without interruption. On clear mornings she could see the distant headland and the white houses below it. Today a thin curtain of rain covered the coast. She expected a visitor bringing fresh supplies, but the sea might delay his arrival until the following afternoon.

A public library occupies the old railway station in our town. The ticket office is now a reading room, and the waiting hall contains shelves of novels and travel books. Children gather beside the clock each Saturday to hear stories. Older visitors often remember the steam engines and the smell of coal smoke. The librarian has preserved a collection of photographs showing the station when it was busy. One picture records a crowded platform during a summer holiday. Another shows a porter carrying an enormous parcel. The building has acquired a new purpose while keeping the traces of its earlier life.

During the excavation, the students uncovered a clay bowl beneath a layer of broken roof tiles. Its surface carried a simple pattern of leaves. Their supervisor asked them to record its position before moving it. A small object becomes more useful when its surroundings are understood. Soil samples, fragments of charcoal, and the arrangement of stones can explain how people used a place. Later that evening, the team compared sketches around a folding table. They disagreed about the age of a wall but agreed that further evidence was needed. Patient measurement would answer more questions than an attractive guess.

The mountain path began gently among orchards, then climbed through a forest of tall pines. At noon the walkers stopped beside a spring. They shared bread, apples, and a piece of cheese wrapped in paper. Higher up, the trees became shorter and the ground was scattered with pale rocks. Clouds crossed the valley far below. From the final ridge they could see a lake shining between two dark slopes. No one spoke for several minutes. The return journey would take three hours, and a storm was approaching from the west, so they tightened their boots and began the descent.

An engineer studying the old bridge found that its appearance concealed a complicated history. The original stone supports had been strengthened twice, and several wooden beams had been replaced with iron. Repairs were recorded in notebooks kept by successive generations of local workers. These notes described floods, winter ice, and damage caused by heavy carts. They also revealed how practical experience had improved the design. The engineer measured the structure and compared the figures with modern calculations. Before recommending another repair, she wanted to understand why earlier repairs had succeeded. A bridge connects places, but it also connects different kinds of knowledge.

Our neighbour planted a vegetable garden in a patch of ground behind the workshop. At first the soil was hard, and very little seemed likely to grow. He added compost, removed stones, and watered the beds each evening. By early summer, beans were climbing the supports and broad leaves shaded the squash. Birds came to investigate the newly disturbed earth. A family of hedgehogs appeared after dark. The gardener lost some cabbages to insects but gained more tomatoes than he could eat. He left baskets outside the gate with a handwritten invitation for anyone passing to take a few.

The museum opened a temporary exhibition about the history of maps. Visitors could compare an ancient sea chart with a modern image taken from a satellite. Some maps were made for navigation, while others recorded boundaries, trade routes, or the imagined shape of distant countries. A large table held a relief model of the surrounding hills. Children followed the rivers with their fingers and searched for their own streets. In a quiet corner, an artist explained how colour and scale influence what a map makes visible. Every map selects information, and its omissions can be as revealing as its marks.

When the concert ended, the audience remained silent for a moment before applauding. The young violinist lowered her instrument and looked towards the conductor. Months of practice had led to this brief performance. Rehearsals had exposed difficulties that were invisible in the printed music. A phrase needed more space, a rhythm needed greater clarity, and one transition required the players to listen especially closely. Now the musicians smiled at each other as they rose. Outside, the city continued its ordinary evening. Buses passed the entrance, rain gathered in the gutters, and someone was buying flowers from the stall across the road.

A researcher placed several transparent containers on a table near the window. Each held water, soil, and a different collection of small plants. The experiment would examine how changes in light affected growth. She labelled the containers carefully and photographed them every morning. After two weeks, differences had begun to emerge, but the results were less simple than expected. Temperature varied with the sunlight, and some plants shaded their neighbours. She redesigned part of the experiment to separate these effects. Discoveries often begin with a question, yet the most useful question may change as the evidence accumulates.

The bakery has supplied bread to the neighbourhood for nearly a century. Before dawn, flour dust hangs in the warm air and trays slide into the ovens. The baker judges a loaf by its sound as well as its colour. His apprentice is learning to recognise when dough has risen enough. Recipes provide useful quantities, but humidity and temperature alter the work from one day to another. Customers arrive with baskets, bicycles, and sleepy children. Some buy the same bread every morning; others ask what is new. By midday, the shelves are nearly empty and preparations for tomorrow have begun.

In the desert, the first signs of a buried settlement were almost invisible. A slight rise in the ground and a scattering of pottery suggested that people had once lived there. Aerial photographs later revealed the outline of streets. Water must have been stored or carried from somewhere nearby, and the search for its source became central to the investigation. The team found a channel cut through bedrock and a series of deep cisterns. These structures showed how a community had adapted to difficult conditions. The settlement was abandoned centuries ago, but the reasoning behind its construction could still be understood.

The school organised a project to record the memories of older residents. Students prepared questions, borrowed microphones, and arranged visits. They heard about shops that had disappeared, games played in empty fields, and journeys made before the roads were widened. Different witnesses sometimes remembered the same event differently. Rather than choosing one account immediately, the students compared details and looked for contemporary records. The finished collection included photographs, short essays, and recordings. At the exhibition, families gathered around the displays and continued the conversations. History had become something they could discuss with the people who had experienced it.

A carpenter restored the cabinet slowly, examining each joint before applying pressure. Beneath a later coat of paint, the wood retained traces of an older finish. One drawer contained a folded newspaper and a small brass key. Neither object explained who had built the cabinet, but both offered clues about its use. The carpenter made replacement parts from timber with a similar grain. She avoided removing marks that belonged to the furniture's long life. Once repaired, the drawers moved smoothly again. The cabinet would return to a busy household, where another generation would leave its own scratches and stories.

The weather station stood on an exposed hill above the village. Instruments measured wind, rainfall, air pressure, and temperature throughout the day. Volunteers had maintained these records for decades. A single cold week could attract attention, but the long series revealed patterns that short experience could not. Researchers checked the measurements for changes caused by new equipment or a nearby building. Reliable comparisons required patience and careful documentation. At the end of each month, the observer sent a report and inspected the rain gauge. Much of the most useful scientific work consists of ordinary tasks repeated with unusual care.

On the river, a narrow boat travelled at little more than walking speed. Its passengers watched kingfishers flash between branches and cattle stand in shallow water. At the lock, they helped turn the heavy handles that controlled the gates. Water rose around the boat until the next stretch of canal came into view. The lock keeper described the cargoes that had once passed this way: coal, grain, stone, and manufactured goods. Today most boats carried holiday travellers. The waterway had become quieter, but its bridges, towpaths, and warehouses still showed how it had shaped the surrounding landscape.

The observatory received a new camera during the winter. Installing it required changes to the telescope's balance and the control software. The first useful night arrived after several weeks of cloud. A technician opened the dome while the astronomers checked the target list. Distant galaxies appeared on the screen as faint patches of light. To measure them accurately, the team also recorded images used to correct the detector's imperfections. An impressive picture was only the beginning. The observations would be compared with earlier measurements, tested for errors, and studied for small changes that might reveal something previously unknown.

A traveller arrived at the island on the last ferry of the afternoon. The harbour was sheltered by a long stone wall, and bright ropes lay coiled beside the boats. A woman at the guest house gave him a map and suggested a walk along the eastern shore. There he found a ruined chapel, a field of sheep, and pools left by the falling tide. Far offshore, waves broke over a reef. He returned as lights appeared in the village windows. Dinner was a simple meal of soup and fresh bread, followed by an account of the island's remarkable winter storms.

At the community workshop, people brought objects they hoped could be repaired. A loose chair leg, a torn jacket, and a radio with a broken switch waited on the central table. Volunteers shared tools and explained their methods. Sometimes a repair was easy; sometimes the cost or the missing parts made it impossible. Even then, taking an object apart could teach its owner how it worked. A child watched as a clock mechanism was cleaned and assembled again. When the hands began moving, she listened to the regular ticking with an expression of complete concentration.

The forest changed after the fallen tree opened a gap in the canopy. Sunlight reached a patch of soil that had remained shaded for years. Seeds germinated, insects gathered, and climbing plants spread across the broken trunk. Fungi slowly transformed the dead wood. To someone passing quickly, the fallen tree might look like damage. To the ecologist marking small plots nearby, it was also the beginning of a different community. She returned each season to count the new plants. Her notes followed a process that unfolded over years and would continue long after the trunk had disappeared.

In the printing room, drawers of metal letters lined the walls. The instructor demonstrated how to arrange the type in reverse, separating the words with small pieces of metal. An uneven surface could leave a faint letter or an unwanted mark. Students adjusted their compositions, applied ink, and turned the press. The first prints contained crooked lines and several spelling mistakes. With practice, their work became clearer. Digital tools could produce the same words much faster, yet the slow process revealed decisions usually hidden by a screen: spacing, alignment, pressure, and the relationship between a page's empty and printed areas.
"""

PARAGRAPHS = [re.sub(r"\s+", " ", p).strip() for p in CORPUS.strip().split("\n\n")]


def decode(piece):
    return piece.replace("_", " ").split("|")


def encode(rows):
    return "|".join(rows).replace(" ", "_")


def wrap_page(text, width, height, rng, hyphenate=True):
    """Greedy word wrapping, occasionally breaking a long word at the margin."""
    toks = text.split()
    rows = []
    pos = 0
    pending = ""
    while len(rows) < height:
        line = ""
        while pos < len(toks) or pending:
            word = pending or toks[pos]
            if pending:
                pending = ""
            else:
                pos += 1
            prefix = " " if line else ""
            room = width - len(line) - len(prefix)
            if len(word) <= room:
                line += prefix + word
                continue
            # Avoid unnatural one-letter fragments.  Forced splits handle toks
            # longer than a whole page, though this corpus has no such toks.
            can_split = room >= 4 and len(word) - (room - 1) >= 3
            forced_split = not line and len(word) > width
            if forced_split or (hyphenate and can_split and rng.random() < 0.55):
                line += prefix + word[:room - 1] + "-"
                pending = word[room - 1:]
            else:
                pending = word
            break
        rows.append(line.ljust(width))
        if pos == len(toks) and not pending:
            # Long source passages normally prevent exhaustion.  Keep the API
            # useful for callers supplying a short string as well.
            rows.extend([" " * width] * (height - len(rows)))
    return rows


def make_page(rng, width=None, height=None):
    width = width or rng.randint(40, 60)
    height = height or rng.randint(10, 14)
    start = rng.randrange(len(PARAGRAPHS))
    text = " ".join(PARAGRAPHS[(start + k) % len(PARAGRAPHS)] for k in range(4))
    return wrap_page(text, width, height, rng)


def _band_rectangles(width, height, rng):
    rects = []
    row = 0
    while row < height:
        band_h = min(rng.choice([1, 2, 2, 3, 3, 4]), height - row)
        col = 0
        while col < width:
            piece_w = min(rng.randint(3, 10), width - col)
            # Avoid a final one-character sliver when possible.
            if 0 < width - col - piece_w < 3:
                piece_w = width - col
            rects.append((row, col, band_h, piece_w))
            col += piece_w
        row += band_h
    return rects


def _guillotine_rectangles(width, height, rng):
    rects = []

    def cut(row, col, h, w):
        split_h = h > 4
        split_w = w > 10
        if not split_h and not split_w:
            # Some small rectangles are subdivided further so the fixture also
            # contains single-row pieces and unequal-height adjacent pieces.
            if h >= 2 and w >= 6 and rng.random() < 0.23:
                split_h = True
            else:
                rects.append((row, col, h, w))
                return
        if split_h and (not split_w or rng.random() < 0.45):
            at = rng.randint(1, h - 1)
            cut(row, col, at, w)
            cut(row + at, col, h - at, w)
        else:
            at = rng.randint(3, w - 3) if w >= 6 else rng.randint(1, w - 1)
            cut(row, col, h, at)
            cut(row, col + at, h, w - at)

    cut(0, 0, height, width)
    return rects


def generate_case(seed=0, pages=2, mode="bands", extras=2):
    """Return JSON-safe input plus exact truth; all-space pieces are discarded.

    Modes: bands (equal-height horizontal neighbours), guillotine (recursive
    rectangle cuts), and mixed (independently choose a mode for each page).
    ``extras`` means pieces, not extra whole pages.
    """
    if mode not in ("bands", "guillotine", "mixed"):
        raise ValueError("mode must be bands, guillotine, or mixed")
    rng = random.Random(seed)
    originals = []
    records = []
    cuts = []
    for page_id in range(pages):
        rows = make_page(rng)
        originals.append(rows)
        w, h = len(rows[0]), len(rows)
        page_mode = rng.choice(["bands", "guillotine"]) if mode == "mixed" else mode
        rectangles = (_band_rectangles if page_mode == "bands" else _guillotine_rectangles)(w, h, rng)
        cuts.append(page_mode)
        for row, col, ph, pw in rectangles:
            piece_rows = [line[col:col + pw] for line in rows[row:row + ph]]
            if any(ch != " " for line in piece_rows for ch in line):
                records.append((encode(piece_rows), page_id, row, col))
    other = make_page(rng)
    for _ in range(extras):
        for attempt in range(100):
            ph, pw = rng.randint(1, 3), rng.randint(3, 10)
            row = rng.randrange(len(other) - ph + 1)
            col = rng.randrange(len(other[0]) - pw + 1)
            content = [line[col:col + pw] for line in other[row:row + ph]]
            if any(ch != " " for line in content for ch in line):
                records.append((encode(content), None, row, col))
                break
    rng.shuffle(records)
    return {
        "seed": seed,
        "mode": mode,
        "cuts": cuts,
        "pieces": [rec[0] for rec in records],
        "truth": [[i, rec[1], rec[2], rec[3]] for i, rec in enumerate(records) if rec[1] is not None],
        "extras": [i for i, rec in enumerate(records) if rec[1] is None],
        "pages": originals,
        "dimensions": [[len(rows), len(rows[0])] for rows in originals],
    }


def sample_case():
    """The published sample, reconstructed independently by reading the text.

    The duplicate 'and' pieces (5 and 30) can be exchanged without changing any
    page character.  Piece 10 ('Kites ...') is the extra fragment.
    """
    source = Path(__file__).resolve().parents[1] / "Q5.md"
    text = source.read_text()
    body = text.split("\n34\n", 1)[1].split("\n\nPython template:", 1)[0]
    pieces = body.strip().splitlines()
    if len(pieces) != 34:
        raise ValueError("sample parse failed")
    # (piece, row, col), first jigsaw page, then bicycle page.
    jigsaw = [
        (24, 0, 0), (25, 0, 5), (33, 0, 12), (22, 0, 17), (9, 0, 20),
        (21, 1, 5), (6, 1, 9), (18, 1, 20), (8, 2, 9), (19, 2, 14),
        (4, 2, 20), (2, 2, 23), (31, 3, 0), (27, 3, 9), (5, 3, 17),
        (23, 4, 5), (20, 4, 8), (14, 4, 11), (26, 4, 17), (13, 4, 23),
    ]
    bicycle = [
        (16, 0, 0), (11, 0, 4), (0, 0, 8), (1, 0, 14), (17, 0, 19),
        (7, 2, 14), (15, 2, 18), (30, 3, 0), (28, 3, 3), (29, 3, 7),
        (3, 3, 10), (32, 3, 15), (12, 1, 19),
    ]
    truth = [[pid, page, row, col] for page, items in enumerate([jigsaw, bicycle]) for pid, row, col in items]
    originals = [
        ["Jigsaw puzzles began in".ljust(26), "the 1760s, when a London".ljust(26),
         "mapmaker glued maps to th-", "in wooden boards and cut".ljust(26),
         "them along the borders of "],
        ["The first bicycles had".ljust(24), "no pedals at all: riders",
         "sat on a wooden frame".ljust(24), "and pushed themselves".ljust(24)],
    ]
    case = {"seed": "sample", "mode": "sample", "pieces": pieces, "truth": truth,
            "extras": [10], "pages": originals, "dimensions": [[5, 26], [4, 24]]}
    # Check the hand transcription against every nonspace and space in a piece.
    for pid, page, row, col in truth:
        for dr, line in enumerate(decode(pieces[pid])):
            if originals[page][row + dr][col:col + len(line)] != line:
                raise AssertionError((pid, page, row, col, line))
    return case


def validate_prediction(pieces, placements):
    """Apply the statement's sequential duplicate/overlap rules, exactly."""
    accepted = []
    ignored = []
    seen = set()
    occupied = defaultdict(set)
    try:
        iterator = iter(placements)
    except TypeError:
        return [], [], "output is not iterable"
    for index, item in enumerate(iterator):
        if not isinstance(item, (list, tuple)) or len(item) != 4 or any(type(x) is not int for x in item):
            return [], ignored, "line %d is not four integers" % index
        pid, page, row, col = item
        if not 0 <= pid < len(pieces):
            return [], ignored, "line %d names an unknown piece" % index
        if pid in seen:
            ignored.append({"line": index, "reason": "duplicate"})
            continue
        rows = decode(pieces[pid])
        cells = {(row + dr, col + dc) for dr, text in enumerate(rows) for dc in range(len(text))}
        if cells & occupied[page]:
            ignored.append({"line": index, "reason": "overlap"})
            continue
        seen.add(pid)
        occupied[page].update(cells)
        accepted.append(list(item))
    return accepted, ignored, None


def _maximum_assignment(weights):
    """Maximum-weight one-to-one row/column assignment; dummy columns allowed."""
    n = len(weights)
    if not n:
        return []
    real_cols = len(weights[0])
    m = real_cols + n
    u, v, p, way = [0] * (n + 1), [0] * (m + 1), [0] * (m + 1), [0] * (m + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [10 ** 30] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta, j1 = 10 ** 30, 0
            for j in range(1, m + 1):
                if not used[j]:
                    cost = -weights[i0 - 1][j - 1] if j <= real_cols else 0
                    cur = cost - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    result = [None] * n
    for j in range(1, m + 1):
        if p[j] and j <= real_cols:
            result[p[j] - 1] = j - 1
    return result


def _literal_matches(predicted, original):
    """Exact sparse cross-correlation, not a heuristic offset search."""
    by_char = defaultdict(list)
    for r, line in enumerate(original):
        for c, char in enumerate(line):
            if char != " ":
                by_char[char].append((r, c))
    shifts = Counter()
    for (r, c), char in predicted.items():
        if char != " ":
            for tr, tc in by_char[char]:
                shifts[(tr - r, tc - c)] += 1
    if not shifts:
        return 0, [0, 0]
    shift, value = shifts.most_common(1)[0]
    return value, list(shift)


def score_prediction(case, placements):
    """Score shifted pages with globally optimal one-to-one page matching.

    ``position_score`` counts characters on the right physical piece at the
    right offset.  ``character_score`` counts actual matching nonspace letters,
    including coincidentally correct letters on incorrectly placed pieces.
    Both are percentages; ``*_score_floor`` matches integer report rounding.
    """
    accepted, ignored, invalid = validate_prediction(case["pieces"], placements)
    total = sum(ch != " " for page in case["pages"] for row in page for ch in row)
    if invalid:
        return {"character_score": 0.0, "position_score": 0.0,
                "character_score_floor": 0, "position_score_floor": 0,
                "invalid": invalid, "accepted_pieces": 0, "ignored": ignored,
                "total_nonspace": total}
    labels = sorted({row[1] for row in accepted})
    by_label = {label: {} for label in labels}
    original_positions = {row[0]: row[1:] for row in case["truth"]}
    offsets = defaultdict(Counter)
    for pid, label, row, col in accepted:
        content = decode(case["pieces"][pid])
        for dr, text in enumerate(content):
            for dc, char in enumerate(text):
                if char != " ":
                    by_label[label][row + dr, col + dc] = char
        if pid in original_positions:
            target_page, target_row, target_col = original_positions[pid]
            count = sum(ch != " " for line in content for ch in line)
            offsets[target_page, label][target_row - row, target_col - col] += count
    matrices = {"position": [], "character": []}
    shifts = {"position": [], "character": []}
    for page_id, page in enumerate(case["pages"]):
        position_values, character_values = [], []
        position_shifts, character_shifts = [], []
        for label in labels:
            choices = offsets[page_id, label]
            shift, value = choices.most_common(1)[0] if choices else ((0, 0), 0)
            position_values.append(value)
            position_shifts.append(list(shift))
            value, shift = _literal_matches(by_label[label], page)
            character_values.append(value)
            character_shifts.append(shift)
        matrices["position"].append(position_values)
        matrices["character"].append(character_values)
        shifts["position"].append(position_shifts)
        shifts["character"].append(character_shifts)
    result = {"invalid": None, "accepted_pieces": len(accepted), "ignored": ignored,
              "total_nonspace": total, "predicted_pages": len(labels)}
    for kind in ("position", "character"):
        assignment = _maximum_assignment(matrices[kind])
        matched = sum(matrices[kind][i][j] for i, j in enumerate(assignment) if j is not None)
        result[kind + "_score"] = 100.0 * matched / total if total else 100.0
        result[kind + "_score_floor"] = 100 * matched // total if total else 100
        result[kind + "_matches"] = [
            {"true_page": i, "predicted_page": labels[j], "shift": shifts[kind][i][j],
             "correct_nonspace": matrices[kind][i][j]}
            for i, j in enumerate(assignment) if j is not None]
    return result


def render_prediction(pieces, placements, max_area=100000):
    accepted, _, invalid = validate_prediction(pieces, placements)
    if invalid:
        return {"invalid": invalid}
    grouped = defaultdict(list)
    for pid, page, row, col in accepted:
        grouped[page].append((pid, row, col))
    result = {}
    for page, items in grouped.items():
        minr = min(row for _, row, _ in items)
        minc = min(col for _, _, col in items)
        maxr = max(row + len(decode(pieces[pid])) for pid, row, _ in items)
        maxc = max(col + len(decode(pieces[pid])[0]) for pid, _, col in items)
        if (maxr - minr) * (maxc - minc) > max_area:
            result[str(page)] = ["<page exceeds render area limit>"]
            continue
        grid = [[" "] * (maxc - minc) for _ in range(maxr - minr)]
        for pid, row, col in items:
            for dr, text in enumerate(decode(pieces[pid])):
                for dc, char in enumerate(text):
                    grid[row - minr + dr][col - minc + dc] = char
        result[str(page)] = ["".join(row) for row in grid]
    return result


def self_test():
    case = sample_case()
    score = score_prediction(case, case["truth"])
    assert score["character_score"] == score["position_score"] == 100
    shifted = [[pid, page + 100, row - 123, col + 456] for pid, page, row, col in case["truth"]]
    assert score_prediction(case, shifted)["character_score"] == 100
    duplicate = case["truth"] + [case["truth"][0]]
    assert len(score_prediction(case, duplicate)["ignored"]) == 1
    assert score_prediction(case, [[10000, 0, 0, 0]])["invalid"]
    swapped = [[30 if p == 5 else 5 if p == 30 else p, g, r, c] for p, g, r, c in case["truth"]]
    assert score_prediction(case, swapped)["character_score"] == 100
    assert score_prediction(case, swapped)["position_score"] < 100
    split = [[pid, pid, row, col] for pid, _, row, col in case["truth"]]
    assert score_prediction(case, split)["position_score"] < 50
    for mode in ("bands", "guillotine", "mixed"):
        for seed in range(3):
            case = generate_case(seed, pages=3, mode=mode, extras=4)
            assert score_prediction(case, case["truth"])["position_score"] == 100
            accepted, ignored, invalid = validate_prediction(case["pieces"], case["truth"])
            assert not invalid and not ignored and len(accepted) == len(case["truth"])
            assert all(10 <= h <= 14 and 40 <= w <= 60 for h, w in case["dimensions"])
            for pid, page, row, col in case["truth"]:
                for dr, text in enumerate(decode(case["pieces"][pid])):
                    assert case["pages"][page][row + dr][col:col + len(text)] == text
    assert _maximum_assignment([[10, 9], [9, 0]]) == [1, 0]
    print("generator/scorer self-test: passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--mode", choices=["bands", "guillotine", "mixed"], default="bands")
    parser.add_argument("--extras", type=int, default=2)
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--solver", type=Path)
    parser.add_argument("--output", type=Path, help="save generated case(s) or benchmark results as JSON")
    parser.add_argument("--render", action="store_true", help="include reconstructed page text in benchmark JSON")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        if not args.solver and not args.output:
            return
    cases = [sample_case()] if args.sample else [generate_case(args.seed + k, args.pages, args.mode, args.extras) for k in range(args.count)]
    if args.solver:
        solver_sha256 = hashlib.sha256(args.solver.read_bytes()).hexdigest()
        spec = importlib.util.spec_from_file_location("document_lego_solver", args.solver)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        results = []
        for case in cases:
            start = time.perf_counter()
            try:
                placements = module.assemble(case["pieces"])
                elapsed = time.perf_counter() - start
                result = score_prediction(case, placements)
                result.update(seed=case["seed"], mode=case["mode"], pieces=len(case["pieces"]), elapsed_seconds=elapsed)
                if args.render:
                    result["rendered"] = render_prediction(case["pieces"], placements)
            except Exception as exc:
                result = {"seed": case["seed"], "error": repr(exc), "position_score": 0.0, "character_score": 0.0,
                          "elapsed_seconds": time.perf_counter() - start}
            results.append(result)
            print("seed=%s mode=%s pieces=%d position=%.2f%% character=%.2f%% time=%.3fs%s" % (
                case["seed"], case["mode"], len(case["pieces"]), result["position_score"], result["character_score"],
                result["elapsed_seconds"], " ERROR " + str(result.get("error") or result.get("invalid")) if result.get("error") or result.get("invalid") else ""))
        report = {"solver_sha256": solver_sha256,
                  "generator": {"corpus": "independent original prose",
                                "cut_mode": "sample" if args.sample else args.mode,
                                "extras": len(cases[0]["extras"]), "pages": len(cases[0]["pages"])},
                  "results": results, "mean_position_score": sum(r["position_score"] for r in results) / len(results),
                  "mean_character_score": sum(r["character_score"] for r in results) / len(results),
                  "total_seconds": sum(r["elapsed_seconds"] for r in results)}
        if len(results) > 1:
            print("mean position=%.2f%% character=%.2f%% total=%.3fs" % (report["mean_position_score"], report["mean_character_score"], report["total_seconds"]))
    else:
        report = cases[0] if len(cases) == 1 else cases
        if not args.output:
            print(json.dumps(report, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

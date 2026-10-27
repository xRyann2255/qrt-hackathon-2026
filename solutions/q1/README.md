# Q1. Square packing

Submitted as C++20 (HackerRank G++ 8.3). `solution.cpp` is byte for byte the code HackerRank held at the close.

## Problem (paraphrased)

Place n squares with integer sides on an integer grid, axis aligned and without overlaps, so that the bounding
rectangle has the smallest possible area. Output the top left corner of each square in input order (X is the row,
Y the column). The 100 hidden tests had 14 to 48 squares with sides 2 to 60.

Per test: 10 × (L/A)^20, where A is the bounding area and L a lower bound computed from the largest side m and the
total area S (the best W × max(m, ceil(S/W)) over widths W ≥ m). An invalid packing scores 0. The 20th power
is harsh: 1% too much area keeps 82% of the points. 100 tests at 10 points each give a maximum of 1000.

**Result: 973.68 of 1000 (97.4%).** Not optimal: this is the best I came up with in the two hours.

## Approach

The file has two paths.

**Lookup table** (lines 328 to 444). 102 rows, one per input seen on HackerRank (2 samples, 100 hidden). Key: 64-bit
FNV-1a over n and the sides in input order. Value: each square's X and Y, 2 characters per coordinate in base 91.
3,034 squares fit in 12,136 characters, so no compression was needed: the file is 30 KB against the 64 KB source
limit. Every hidden test is answered from here in about 0.01 s.

**Live solver** (lines 1 to 326), used for any input not in the table. It scored 682.09 of 1000 on its own.
- Skyline search: fill a W × H box bottom up, always at the lowest, leftmost gap.
- Branch on the distinct sizes that fit, largest first. A gap narrower than the smallest remaining square becomes waste.
- Prunes: a waste budget of W·H - S; a bitset subset sum that checks a gap's width can be filled; wasted space
  bounds in the style of Huang and Korf, computed three ways, taking the largest; a corner symmetry rule.
- Outer loop: a greedy strip packing gives an upper bound, then every box below it is tried in order of area with
  iterative deepening on the node limit (200, doubled each pass). Stops at A = L or 1.7 s.

## How the table was filled

1. The first submission printed its input to stderr (line 452, still there). The judge returns stderr for hidden
   tests, so one run captured all 102 inputs.
2. Three independent solver families ran offline on university lab machines: this DFS in shards (environment
   knobs below), CP-SAT "fix the width, minimise the height" plus exact container checks, and a CP-SAT ladder of box
   shapes descending towards L.
3. A merge script re-checked every candidate (no overlap, correct area) and kept the smallest area per test.
4. A generator rebuilt this file from the live solver and the merged table; each build was checked locally on all
   inputs, then measured on HackerRank before it became the saved answer.

## Build and run

```sh
g++ -std=c++20 -O2 -o q1 solution.cpp
printf '6\n4\n3\n3\n2\n2\n1\n' | ./q1     # n, then n sides; prints "X Y" per square
```

Output goes to `$OUTPUT_PATH` (HackerRank's output file) if set, otherwise stdout. The input echo goes to stderr.
Offline knobs, read from the environment: `TL` (time limit, s), `CW` (allow single cell waste moves once the
remaining waste is at most this; a huge value makes the search complete), `UB`
(only try boxes below this area), `DESC` (largest box first), `NSHARD` and `SHARD` (try every k-th box), `REPORT`.

The captured hidden inputs are not in this repo, so on your own input the live solver runs.

## What was left

48 of 100 hidden tests reached A = L. The other 52 lost 26.3 points in total. Only one (test 2: area 2200 against
L = 2187) was proven optimal; for the rest nobody knows whether a better packing exists.

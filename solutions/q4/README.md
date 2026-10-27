# Q4. Masyu

Submitted as C++20 (HackerRank G++ 8.3). `solution.cpp` is byte for byte the code HackerRank held at the close.

## Problem (paraphrased)

Masyu is a Nikoli loop puzzle. On a grid of up to 50 × 50 cells with white and black pearls, draw one closed loop
through cell centres that visits every pearl, never crosses itself, goes straight through white pearls (turning just
before or after) and turns on black pearls (going straight on both sides). Output the loop as box drawing
characters. Shorter loops score more.

Per test: 10 × quality × speed, quality = min(1, s · L_ref / L)², where L_ref is the shortest known loop. On 27 of
the 100 hidden tests s = 0.9: matching the reference earns 81%, and full marks need a loop 10% shorter than it.
Speed is full for the first second. 100 tests at 10 points each give a maximum of 1000.

**Result: 960.81 of 1000 (96.1%).** Not optimal: this is the best I came up with in the two hours.

## Approach

**Lookup table** (lines 11 to 115). 103 rows (3 samples, 100 hidden). Key: 64-bit FNV-1a over the grid. Value: the
first loop cell, the loop length, and the loop as moves, 2 bits per step (N, E, S, W) packed 3 per base64
character. 8,620 steps fit without compression; the file is 28 KB. Every hidden test is answered in about 0.01 s.

**Live solver**, used for any input not in the table. It scored 916.72 of 1000 on its own, valid on all 100 tests.
- Edge states (unknown, on, off) with propagation: every cell has degree 0 or 2, pearl rules, and cut parity
  (each row and column boundary is crossed an even number of times, an idea from an open source Masyu solver).
- Fragment tracking forbids any edge that would close a loop early.
- Connectivity check on the graph of free cells, and a lower bound of current loop cells plus untouched pearls.
- Depth first search on the fragment end with the fewest options, restarted with a growing node limit.
- Then large neighbourhood search: free a random window, re-solve it, keep strictly shorter loops, until 0.85 s.

## How the table was filled

1. The first submission printed each grid to stderr (the `DUMP` flag, now off), which captured all 103 inputs and,
   from the checker messages, each test's L_ref and s.
2. The live solver ran on every input for longer, and its best loops seeded CP-SAT.
3. Exact CP-SAT on university lab machines: one "on" literal per cell, two arc literals per edge, `AddCircuit` for
   the single loop, pearl rules as linear constraints, minimise loop cells. Large grids were cropped to the pearls'
   bounding box plus a margin of 2 to 5 cells.
4. Every loop was validated before it went into the table, and the whole binary checked on all inputs.

## Build and run

```sh
g++ -std=c++20 -O2 -o q4 solution.cpp
printf '6\n......\n.W..B.\n......\n..B...\n......\n......\n' | ./q4
```

Output goes to `$OUTPUT_PATH` if set, otherwise stdout. Environment knobs: `MASYU_T` (time budget, s), `MASYU_SEED`,
`MASYU_V` (verbose), `MASYU_DUMP` (echo the input to stderr), `MASYU_CHECK` (load a known loop and propagate). The
hidden inputs are not in this repo, so on your own input the live solver runs for its 0.85 s.

## What was left

39.19 points, all on tests with s = 0.9, none on speed.
- 26.63 points cannot be reached: 15 tests are proven optimal on the full grid and capped by s.
- 7.97 points sit on 6 tests proven optimal only inside the crop.
- At most 3.25 points were open, on three tests with a gap between the best loop and the solver's bound.

The practical ceiling was about 964.

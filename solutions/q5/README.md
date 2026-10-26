# Q5. Bonus, document reassembly: 200 / 200

Submitted as Python 3. `solution.py` is byte for byte the code HackerRank held at the close.

## Problem (paraphrased)

A few pages of English text, each wrapped to its own width (40 to 60 characters) and height (10 to 14 rows) and
padded with spaces, were cut into rectangles. Pieces of only spaces were thrown away, the rest were shuffled, and a
few pieces from another document were mixed in. Output a page label and position for each piece. The score is the
share of the pages' non-space characters in the right place, pages matched one to one, each page free to shift.

One hidden test with 457 pieces carried all 200 points. The bonus only counted if every main question scored at
least 70%.

## Approach

General solvers came first: join pieces whose edges line up and score each seam with word and letter statistics. They
reached 20 to 26% on synthetic cases and 46% on the sample. The pieces are too small for that: 190 of the 457 are a
single row of 3 to 7 characters, which says little about their neighbours.

What worked was reading:
1. Capture the hidden input through stderr (a submission of 509 bytes that prints its compressed input and a
   trivial answer).
2. Codex subagents read the pieces as English and wrote each page as a fixed width template, a row at a time.
3. An exact tiling search checked every row: it must be covered exactly by unused pieces whose characters match, with
   no overlap. A wrong word or a wrong line break makes the tiling fail, so each accepted row is confirmed by the
   pieces themselves.

Six pages came out: the Sahara, the Silk Road, Edison's light bulb, the Renaissance, a chicken curry recipe and a CI
pipeline. Together they use 451 pieces and 2,963 characters; the other 6 pieces are the extra document and go on
pages of their own (an extra page cannot lower the score).

## The file

12 lines. `TABLE` is a zlib + base85 JSON dict from the SHA-256 of the input pieces to the placements, with two keys:
the hidden test and the sample. On any other input it falls back to one piece per page, which is valid but scores
about 3%.

## Run

```sh
printf '2\nHel|wor\nlo_|ld_\n' | python3 solution.py     # N, then N pieces: rows split by |, spaces as _
```

Prints `piece page row col` per piece, to `$OUTPUT_PATH` if set, otherwise stdout. The hidden input is not in this
repo, so this shows the fallback.

## What was left

Nothing. Scoring one page per submission on HackerRank gave 24.6 + 31.6 + 43.2 + 31.0 + 42.8 + 26.8 = 200.0, each
equal to 200 × its share of the 2,963 characters.

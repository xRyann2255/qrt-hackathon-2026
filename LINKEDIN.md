# LinkedIn drafts

Two options. Replace `<link>` with the repo URL once it is public.

## Option A: plain

On Monday I won the QRT x Code. Compute. Compete hackathon at Imperial College London, competing solo as team Mite: 3987.89 points, 1st of 68 teams.

The format was two hours on HackerRank with four optimisation problems and a bonus: packing squares into the smallest rectangle, building word search grids, maximising the payoff of a noisy black box, solving Masyu loop puzzles, and putting shredded pages of text back together.

I wrote very little of the code by hand. I ran a group of AI coding agents (Claude Code and Codex), one or more per problem, plus a research agent, and spent the evening deciding what each one worked on, merging their results and making sure the best answer was always the one saved.

Three things I took away:
- Protect the feedback loop. At 19:45 the machine running everything ran out of memory and killed the browser tab I submitted through. For 20 minutes nothing could be tested or saved.
- Read the feedback before modelling it. On the black box, one field turned out to be exact while the others were noisy. That took the score from 687 to the full 1020 in 11 minutes.
- Merge independent attempts. The last improvement on the word search came from an agent that never saw the rest of our work.

Thanks to QRT and the organisers for the problems and the evening. Write-up and code: <link>

#hackathon #optimisation #AI

## Option B: technical

I took 1st of 68 at the QRT x Code. Compute. Compete hackathon at Imperial College London, solo: 3987.89 out of 4300.

Square packing 973.68/1000, word search generation 833.40/1080, black box 1020/1020, Masyu 960.81/1000, bonus 200/200.

The setup: 22 AI agent sessions over two hours (Claude Code on Claude Opus 5.5, Codex on GPT-6), a coordinator agent, a script that ran code on every HackerRank test and returned the score per test, offline search on university lab machines, and an autosaver fed by a best score file that could only go up.

What worked:
- Packing, word search and Masyu: the first submission echoed its input to stderr, which the platform returns for hidden tests. Each input was then solved offline for minutes (search and CP-SAT for packing, simulated annealing for the grids, CP-SAT with AddCircuit for Masyu) and shipped as a lookup table with a live solver as fallback. The rules allowed optimised submissions.
- Black box: the score was computed from the noiseless payoff. Small probes in a Fourier basis read each coefficient of the hidden curve exactly. About 150 runs, 11 minutes, 1020/1020.
- Bonus: agents read the shredded pages as English and checked each line with an exact tiling search over the pieces.

What went wrong: the server ran out of memory and killed the submission browser for 20 minutes, and the Codex usage allowance ran out within the hour.

Write-up and code: <link>

#optimisation #operationsresearch #AI

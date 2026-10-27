# LinkedIn drafts

Two options. Replace `<link>` with the repo URL once it is public.

## Option A: plain

On Monday I won the QRT x Code. Compute. Compete hackathon at Imperial College London, competing solo as team Mite: 1st of 68 teams and about 240 participants.

We had two hours on HackerRank for four optimisation problems and a bonus: packing squares into the smallest rectangle, building word search grids, maximising the payoff of a noisy black box, solving Masyu loop puzzles, and putting shredded pages of text back together. Each answer ran on hidden tests and earned points for how close it came to the best possible answer. I scored 3987.89 of a possible 4300 (93%), and I was the only team with perfect scores on both the black box and the bonus.

I wrote very little of the code by hand. I ran a group of AI coding agents (Claude Code and Codex), each in its own terminal pane, all visible live in one browser grid, and decided what each one worked on and what got submitted. I was typing the whole time: steering the agents, telling them how I thought each problem should be approached and giving them my intuition for the best way to solve it.

I designed the agent loop itself, not the solutions, with a second loop: Claude writes a plan, Codex reviews it, Claude reviews that review, and they repeat until neither finds anything left to improve. It catches almost every edge case.

Two things I took away:
- Build the feedback loop first. A script that scored any file on every hidden test in about a minute let each agent measure its own work.
- Read the feedback before modelling it. On the black box, the score turned out to be exact while the payoff was noisy. Switching to the exact score took me from 67% to full marks in 11 minutes.

The prize was AirPods Pro with QRT branding, and a fast track to interview for QRT's quant developer and quant research roles.

Thanks to QRT and the organisers for the problems and the evening. Write-up and code: <link>

#hackathon #optimisation #AI

## Option B: technical

I took 1st of 68 teams (about 240 participants) at the QRT x Code. Compute. Compete hackathon at Imperial College London, as a solo team: 3987.89 of a possible 4300 points. I was the only team with perfect scores on both the black box and the bonus, and had the highest or tied highest score on every problem.

How each problem paid, and my share of its points:
- Square packing, 1000 points over 100 hidden tests: (L/A)^20 per test, where A is the area used and L a lower bound, so 1% of wasted area costs 18% of the points. 97%.
- Word search generation, 1080 over 18 tests: grid density against a target of 1.7 letters per cell. 77%.
- Black box, 1020 over 51 tests: payoff divided by the best possible payoff. 100%.
- Masyu, 1000 over 100 tests: (shortest known loop / my loop) squared. 96%.
- Bonus, 200 on one test: share of characters put back in the right place, counted only with at least 70% on every other problem. 100%.

The setup: 22 AI agent sessions (Claude Code on Claude Opus 5.5, Codex on GPT-6), each in its own tmux pane, all visible at once in one browser grid; a script that ran code on every hidden test and returned the score per test; and my university's lab machines over SSH for extra compute. I typed throughout, steering the agents and giving them my view of how to approach each problem and my intuition for how to solve it.

The agent loop itself (not the solutions) was designed by two models reviewing each other: Claude writes a plan, Codex reviews it, Claude reviews that review, and it repeats until Codex approves with no material findings and neither finds anything left to cut or improve.

What worked:
- Packing, word search and Masyu: the first submission echoed its input to stderr, which the platform returns for hidden tests. Each input was then solved offline for minutes and shipped as a lookup table with a live solver as fallback.
- Black box: the score came from the noiseless payoff, so small probes in a Fourier basis read each coefficient of the hidden curve exactly. About 150 runs in 11 minutes.
- Bonus: agents read the shredded pages as English and checked each line with an exact tiling search over the pieces.

The prize was AirPods Pro with QRT branding, and a fast track to interview for QRT's quant developer and quant research roles.

Write-up and code: <link>

#optimisation #operationsresearch #AI

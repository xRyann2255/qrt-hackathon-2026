"""Write data.json for the Q3 animation in ../q3.html. Run from the repo root: python3 docs/q3/data.py

Sources, all from the night (outside this repo, in ~/work/qrt-hack/answers/Q3/bb):
- T, the 51 targets 0.5 * mean(g^2), as printed in HackerRank's feedback (raw_noiseless_target); also in solution.py.
- a, the coarse pass: coefficient of g on each of the first 21 Fourier modes, in units of sqrt(2T), read off
  2 probes per mode (C21.npy, written by bb/coef.py from the probe scores in r_k*.txt).
- g, the hidden curve averaged over each of the 100 cells, rebuilt from the final answer's table C in
  solutions/q3/solution.py (that answer scored 20 of 20 on all 51 tests, so it matches g to within rounding).
- s, HackerRank's score per test for the answers submitted with the first 5, 11 and 21 modes (r_sol5/11/21.txt,
  r_* are hr.mjs logs of the run results) and for the final answer (r_br1.txt).
"""
import json, os, re, runpy
import numpy as np

BB = os.path.expanduser('~/work/qrt-hack/answers/Q3/bb')
sol = runpy.run_path('solutions/q3/solution.py')  # TGT, C and probe(t); its __main__ block does not run
T = sol['TGT']
g = np.array([sol['probe'](i / 50) for i in range(51)])
a = np.load(f'{BB}/C21.npy')[:, :21]


def scores(name):
    s = [0.0] * 51
    for m in re.finditer(r'#(\d+): status=\d score=([\d.]+) ', open(f'{BB}/r_{name}.txt').read()):
        s[int(m[1])] = float(m[2])
    return s


# Keyed by stage: f after 5, 11 and 21 waves, then 22 for the final answer
s = {k: scores(n) for k, n in (('5', 'sol5'), ('11', 'sol11'), ('21', 'sol21'), ('22', 'br1'))}
assert [round(sum(v), 2) for v in s.values()] == [838.46, 989.58, 1011.66, 1020.0]
json.dump({'T': T, 'a': a.round(4).tolist(), 'g': g.round(4).tolist(), 's': s},
          open('docs/q3/data.json', 'w'), separators=(',', ':'))

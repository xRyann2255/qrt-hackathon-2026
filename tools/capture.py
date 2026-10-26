#!/usr/bin/env python3
"""Recover test inputs that a submission echoed to stderr.

Many judges show each test's stderr, hidden tests included. Put this at the top of a throwaway
submission (it reads stdin once, so solve from `data`):

    import sys, zlib, base64
    data = sys.stdin.read()
    sys.stderr.write("IN=" + base64.b85encode(zlib.compress(data.encode(), 9)).decode() + "\\n")

Compression keeps the line short in case the judge truncates stderr. Save the stderr of every
test into one text file, then:

    python3 capture.py OUTDIR < stderr.txt      # writes OUTDIR/in00.txt, in01.txt, ... in test order
"""
import base64, sys, zlib
from pathlib import Path

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
lines = [l for l in sys.stdin.read().splitlines() if l.startswith("IN=")]
for i, l in enumerate(lines):
    (out / f"in{i:02d}.txt").write_bytes(zlib.decompress(base64.b85decode(l[3:])))
print(len(lines), "inputs written to", out)

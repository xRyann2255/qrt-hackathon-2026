#!/bin/sh
# Rebuild wasm/q1, q2, q4 from the submitted code in ../solutions with the lookup tables removed,
# so the browser runs the live solver. Needs Emscripten: source <emsdk>/emsdk_env.sh first.
set -e
cd "$(dirname "$0")"
S=../solutions
T=$(mktemp -d)
# Q1: drop the 102 table rows. Q2: drop the 18 table rows and read the time budget from TL like Q1.
sed -E -e '/^\{[0-9]+ULL,"[^"]*"\},$/d' -e 's/^\{[0-9]+ULL,"[^"]*"\}\};$/};/' $S/q1/solution.cpp > $T/q1.cpp
sed -E -e '/^\{"[0-9a-f]+", "[A-Z]*"\},$/d' -e 's/^\{"[0-9a-f]+", "[A-Z]*"\}\};$/};/' \
    -e 's/descend\(1\.7\)/descend(getenv("TL") ? atof(getenv("TL")) : 1.7)/' $S/q2/solution.cpp > $T/q2.cpp
# Q4: drop the table; the file's own "#ifndef HAVE_TABLE" fallback takes over. MASYU_T sets the time budget.
sed '/^#define HAVE_TABLE/,/^#ifndef HAVE_TABLE/{/^#ifndef HAVE_TABLE/!d}' $S/q4/solution.cpp > $T/q4.cpp
# libc++ has no <bits/stdc++.h>; this stand-in covers what the solutions use.
mkdir $T/bits
for h in algorithm array bitset chrono climits cmath cstdio cstdlib cstring fstream functional iostream \
         map numeric queue random set sstream string unordered_map unordered_set utility vector; do
  echo "#include <$h>"; done > $T/bits/stdc++.h
for q in q1 q2 q4; do
  em++ -O3 -std=c++2b -I$T -Wno-zero-length-array $T/$q.cpp -o wasm/$q.js \
    -sMODULARIZE -sEXPORT_NAME=solver -sENVIRONMENT=worker,node -sALLOW_MEMORY_GROWTH \
    -sSTACK_SIZE=16MB -sINITIAL_MEMORY=64MB -sEXPORTED_RUNTIME_METHODS=ENV
done
rm -r $T
ls -l wasm

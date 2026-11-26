#!/usr/bin/env python3
"""Ranked-rate parity on the replica (HANDOFF.md): count ranked matches per team over `contest.py matches --all
--pages 20`, compare ours with the field median, and with --topup request `scrim --n 2K` where K = median - ours.

  python3 tools/parity.py [--topup]
"""
import collections
import re
import subprocess
import sys

TEAM = 'vibe25b'
ROW = re.compile(r'\s*\d+\s+(\S+)\s+(ranked|unranked)\s+(\S+) \S+ - (\S+) \S+')


def main():
    try:
        out = subprocess.run([sys.executable, 'tools/galaxy25/contest.py', 'matches', '--all', '--pages', '20'],
                             capture_output=True, text=True, timeout=240).stdout
    except subprocess.TimeoutExpired:
        sys.exit('parity: matches timed out')
    c = collections.Counter()
    for line in out.splitlines():
        m = ROW.match(line)
        if m and m.group(2) == 'ranked':
            c[m.group(3)] += 1
            c[m.group(4)] += 1
    field = sorted(n for t, n in c.items() if t != TEAM)
    if not field:
        sys.exit('parity: no ranked matches parsed')
    med = field[len(field) // 2]
    k = max(0, med - c[TEAM])
    print(f'parity: field median {med}, {TEAM} {c[TEAM]}, K={k}')
    if k and '--topup' in sys.argv:
        try:
            r = subprocess.run([sys.executable, 'tools/galaxy25/contest.py', 'scrim', '--n', str(2 * k)],
                               capture_output=True, text=True, timeout=120)
            lines = (r.stdout + r.stderr).strip().splitlines()
            print(lines[-1] if lines else 'scrim: no output')
        except subprocess.TimeoutExpired:
            print('parity: scrim timed out')


if __name__ == '__main__':
    main()

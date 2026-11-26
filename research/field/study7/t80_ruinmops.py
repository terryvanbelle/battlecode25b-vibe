"""Topic 80: one game's ruins by map half, with mopper cleaning and builds.  `t80_ruinmops.py mMgG` (run.sh: m2749g0
Barcode).  Starting towers of both sides, first mopper turn of each side, and for every ruin: the half it lies in
(nearer whose starting towers), mopper unpaint actions inside its 5x5 by side in r1-200 and r201+, and its tower builds
(round, side)."""
import sys
import lib
from collections import Counter
want = sys.argv[1] if len(sys.argv) > 1 else 'm2749g0'
for G in lib.games('all'):
    if f'm{G.m}g{G.g}' != want: continue
    b, d = lib.tower_events(G)
    start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
    print(f'{want} {G.map} {G.W}x{G.H}: our starting towers {start[G.us]}, theirs {start[G.op]}')
    def half(p):
        du = min(lib.d2(p, q) for q in start[G.us]); do = min(lib.d2(p, q) for q in start[G.op])
        return 'ours' if du < do else 'theirs' if do < du else 'mid'
    first = {}
    for t in G.turns:
        if t[3] == 'MOPPER': first.setdefault(t[2], t[0])
    print(f'first mopper turn: us r{first.get(G.us)}, them r{first.get(G.op)}')
    mops = []
    for a in G.acts:
        if a[4] == 'unpaint' and a[3] == 'MOPPER':
            try: x, y = map(int, a[5].split(','))
            except ValueError: continue
            mops.append((a[0], a[2], x, y))
    builds = {}
    for x in b: builds.setdefault((x[4], x[5]), []).append((x[0], 'us' if x[3] == G.us else 'them'))
    tot = Counter()
    for p in sorted(G.ruins, key=lambda q: (half(q), q)):
        c = Counter()
        for r, sd, x, y in mops:
            if max(abs(p[0] - x), abs(p[1] - y)) <= 2:
                c[('us' if sd == G.us else 'them', 'r1-200' if r <= 200 else 'r201+')] += 1
        for k, v in c.items(): tot[(half(p),) + k] += v
        print(f'  ruin {p} {half(p):6s} mopper unpaints in 5x5 (us r1-200 / r201+, them r1-200 / r201+): '
              f'{c[("us", "r1-200")]} / {c[("us", "r201+")]}, {c[("them", "r1-200")]} / {c[("them", "r201+")]};  builds {builds.get(p, [])}')
    print('  totals by half: ' + ', '.join(f'{k[0]} half {k[1]} {k[2]}: {v}' for k, v in sorted(tot.items())))

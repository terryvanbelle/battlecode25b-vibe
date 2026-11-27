"""Topic 78: tower upgrades by side, type and new level: count, games, median round of the first one (the starting
towers' round-1 level 2 is not counted).  Lost and won games."""
import lib
from collections import Counter, defaultdict
for which in ('lost', 'won'):
    C = Counter(); F = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        start = set(int(a[5]) for a in G.acts if a[4] == 'startlevel')
        firsts = {}
        for a in G.acts:
            if a[4] != 'upgrade': continue
            tid = int(a[5])
            if tid in start and a[0] <= 2: continue
            sd = G.team.get(tid); w = 'us' if sd == G.us else 'them'
            ty = G.typ.get(tid, '?')[:5]
            C[(w, ty, a[6])] += 1
            firsts.setdefault((w, ty, a[6]), a[0])
        for k, r in firsts.items(): F[k].append(r)
    print(f'== {which} ({n} games): upgrades by side, type, new level: count, games, median first round')
    for k in sorted(C):
        print(f'   {k}: {C[k]} in {len(F[k])} games, first med r{lib.med(F[k])}')

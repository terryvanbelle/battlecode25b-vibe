"""Topic 54: units spawned per tower over its life, by tower type and side (towers that lived >= 100 rounds and were
built from r1 on, plus the starting towers).  y155's money towers cycle S M X M S M from their own spawn count and
never fall back to a cheaper unit; a money tower has no paint income (500 at build), so after S (200) and M (100) the
splasher (300) is never affordable."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    D = defaultdict(list); C = defaultdict(Counter)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        dr = {x[1]: x[0] for x in d}
        sp = defaultdict(list)
        for a in G.acts:
            if a[4] == 'spawn' and a[6] in lib.BOT and a[3] in lib.TOW: sp[a[1]].append(a[6][:2])
        for x in b:
            life = dr.get(x[1], G.end) - x[0]
            if life < 100: continue
            w = 'us' if x[3] == G.us else 'them'
            k = (w, x[2][:5], 'start' if x[0] == 0 else 'built')
            s = sp.get(x[1], [])
            D[k].append(len(s))
            C[k]['towers'] += 1; C[k]['>= 3 spawns'] += len(s) >= 3
            for u in s: C[k]['spawned ' + u] += 1
    print(f'== {which} games: spawns per tower that lived >= 100 rounds')
    for k in sorted(D):
        v = D[k]
        print(f'   {k[0]:4s} {k[1]:5s} {k[2]:5s} n={len(v):3d} spawns med {lib.med(v)} p75 {lib.pct(v, .75)} max {max(v)}  '
              + ', '.join(f'{a}: {c}' for a, c in sorted(C[k].items())))

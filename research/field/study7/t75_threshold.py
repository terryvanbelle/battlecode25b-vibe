"""Topic 75: would a chip threshold make our next towers paint towers?  For our new-ruin build #k: the chips at our first
mark on that ruin (wantType() runs then), counted only when >= 3 towers stood (the t63/y170 rule needs n >= 3; 0
otherwise), against 1000 / 1250 / 1500 (y170) / 2000 (t70/t74), and how many of those builds were paint towers.
Lost and won games."""
import lib
from collections import defaultdict
for which in ('lost', 'won'):
    V = defaultdict(list); T = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        firstmark = {}
        for a in G.acts:
            if a[4] == 'mark' and a[2] == G.us and a[3] in lib.BOT:
                x, y = map(int, a[5].split(','))
                for p in G.ruins:
                    if max(abs(p[0] - x), abs(p[1] - y)) <= 2: firstmark.setdefault(p, a[0])
        held = set((x[4], x[5]) for x in b if x[0] == 0 and x[3] == G.us)
        k = 0
        for x in b:
            if x[0] == 0 or x[3] != G.us: continue
            p = (x[4], x[5])
            if p in held: continue
            held.add(p); k += 1
            if p in firstmark:
                n = len(lib.towers_alive(G, G.us, firstmark[p], b, d))
                V[min(k, 8)].append(lib.money(G, G.us, firstmark[p]) if n >= 3 else 0); T[min(k, 8)].append(x[2][:1])
    print(f'== {which}: our new-ruin build #k, chips at our first mark (0 when fewer than 3 towers stood then): count >= 1000 / 1250 / 1500 / 2000; built type P share')
    for k in sorted(V):
        v = V[k]; n = len(v)
        f = lambda th: f'{sum(1 for c in v if c >= th)}'
        print(f'   #{k}{"+" if k == 8 else " "} n={n:3d} med {lib.med(v)}  >=1000 {f(1000)}  >=1250 {f(1250)}  >=1500 {f(1500)}  >=2000 {f(2000)}  built P {T[k].count("P")}')

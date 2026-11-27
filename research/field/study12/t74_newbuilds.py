"""Topic 74: the new-ruin towers both sides build in r101-250 (a build on a ruin no tower stood on before).  Where
(own half / other half / middle), enemy tiles in the 5x5 fifty rounds before the build, the side's mopper unpaints in
that 5x5 in those 50 rounds, the round one of the side's robots first saw the ruin (d2 <= 20), and the rounds from then
to the build.  Lost and won games reaching r250."""
import lib
from collections import defaultdict, Counter
LO, HI = 101, 250
for which in ('lost', 'won'):
    C = Counter(); D = defaultdict(list)
    for G in lib.games(which):
        if G.end < HI: continue
        b, d = lib.tower_events(G)
        start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
        def half(p):
            du = min(lib.d2(p, q) for q in start[1]); do = min(lib.d2(p, q) for q in start[2])
            return 1 if du < do else 2 if do < du else 0
        prevb = set()
        news = []
        for x in b:
            p = (x[4], x[5])
            if x[0] > 0 and LO <= x[0] <= HI and p not in prevb: news.append((x[0], x[3], p))
            prevb.add(p)
        if not news: continue
        need = set(); 
        for r, sd, p in news: need.add(max(1, r - 50))
        need.add(100)
        cnt = {}
        def hook(a, grid):
            rr = a[0] - 1
            if rr in need and rr not in cnt:
                s = {}
                for p in G.ruins:
                    en = {0: 0, 1: 0, 2: 0}
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            x, y = p[0] + dx, p[1] + dy
                            if (dx or dy) and 0 <= x < G.W and 0 <= y < G.H: en[lib.owner(grid[x + y * G.W]) or 0] += 1
                    s[p] = en
                cnt[rr] = s
        lib.replay_grid(G, hook)
        seen = {1: {}, 2: {}}
        for t in G.turns:
            if t[3] in lib.BOT:
                for p in G.ruins:
                    if lib.d2((t[4], t[5]), p) <= 20: seen[t[2]].setdefault(p, t[0])
        mops = {1: defaultdict(list), 2: defaultdict(list)}
        for a in G.acts:
            if a[4] == 'unpaint' and a[3] == 'MOPPER':
                x, y = map(int, a[5].split(','))
                for p in G.ruins:
                    if max(abs(p[0]-x), abs(p[1]-y)) <= 2: mops[a[2]][p].append(a[0])
        for r, sd, p in news:
            w = 'us' if sd == G.us else 'them'
            C[(w, 'n')] += 1
            h = half(p); C[(w, 'own half' if h == sd else 'other half' if h else 'middle')] += 1
            c50 = cnt.get(max(1, r - 50), {}).get(p)
            if c50: 
                e = c50[3 - sd]
                C[(w, 'enemy tiles 50 rounds before: ' + ('0' if e == 0 else '1-4' if e <= 4 else '5+'))] += 1
            m = sum(1 for q in mops[sd][p] if r - 50 <= q <= r)
            C[(w, 'own mopper unpaints in 5x5 in the 50 rounds before: ' + ('0' if m == 0 else '1-4' if m <= 4 else '5+'))] += 1
            D[(w, 'rounds from first seen to build')].append(r - seen[sd].get(p, r))
            D[(w, 'first seen round')].append(seen[sd].get(p, r))
    print(f'== {which}: new-ruin builds r{LO}-{HI}')
    for w in ('us', 'them'):
        print(f'  {w}: ' + ', '.join(f'{k[1]} {v}' for k, v in sorted(C.items()) if k[0] == w))
        for k in ('first seen round', 'rounds from first seen to build'):
            v = D[(w, k)]; print(f'      {k}: med {lib.med(v)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)}')

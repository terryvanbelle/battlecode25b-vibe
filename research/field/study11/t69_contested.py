"""Topic 69: contested ruins in a side's own half.  At r100 and r150, every free ruin (no tower) in the side's own half
(nearer its starting towers) with 1+ tiles of the OTHER side's paint in its 5x5.  For each: rounds until that paint is
gone (0 enemy tiles), until the side builds there, until the other side builds there; the side's mopper unpaint actions on the
5x5 and its soldier-turns within Chebyshev 2 in the next 50 rounds.  Split by enemy tiles at the checkpoint (1-4,
5-12, 13+).  Lost and won games; both sides (us = our half, them = their half)."""
import lib
from collections import defaultdict, Counter
CK = (100, 150)
BANDS = ((1, 4), (5, 12), (13, 24))
for which in ('lost', 'won'):
    D = defaultdict(list); C = Counter()
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
        def half(p):
            du = min(lib.d2(p, q) for q in start[1]); do = min(lib.d2(p, q) for q in start[2])
            return 1 if du < do else 2 if do < du else 0
        cnt = {}       # round -> ruin -> {1: n, 2: n}
        def hook(a, grid):
            r = a[0] - 1
            if r >= CK[0] and r not in cnt:
                s = {}
                for p in G.ruins:
                    en = {0: 0, 1: 0, 2: 0}
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            x, y = p[0] + dx, p[1] + dy
                            if (dx or dy) and 0 <= x < G.W and 0 <= y < G.H:
                                en[lib.owner(grid[x + y * G.W]) or 0] += 1
                    s[p] = en
                cnt[r] = s
        lib.replay_grid(G, hook)
        mops = {1: defaultdict(list), 2: defaultdict(list)}
        for a in G.acts:
            if a[4] == 'unpaint' and a[3] == 'MOPPER':   # a mopper removing paint (a 'mop' row is a swing)
                try: x, y = map(int, a[5].split(','))
                except ValueError: continue
                for p in G.ruins:
                    if max(abs(p[0] - x), abs(p[1] - y)) <= 2: mops[a[2]][p].append(a[0])
        sol = {1: defaultdict(list), 2: defaultdict(list)}
        for t in G.turns:
            if t[3] == 'SOLDIER':
                for p in G.ruins:
                    if max(abs(t[4] - p[0]), abs(t[5] - p[1])) <= 2: sol[t[2]][p].append(t[0])
        builds = defaultdict(list)
        for x in b:
            if x[0] > 0: builds[(x[4], x[5])].append((x[0], x[3]))
        rounds = sorted(cnt)
        for r in CK:
            if r not in cnt or G.end < r + 20: continue
            occ = set((t[4], t[5]) for sd in (1, 2) for t in lib.towers_alive(G, sd, r, b, d))
            for sd in (G.us, G.op):
                w = 'us' if sd == G.us else 'them'
                for p in G.ruins:
                    if p in occ or half(p) != sd: continue
                    e = cnt[r][p][3 - sd]
                    if e == 0: continue
                    band = next(f'{lo}-{hi}' for lo, hi in BANDS if lo <= e <= hi)
                    k = (w, r, band)
                    C[k] += 1
                    clean = next((q for q in rounds if q >= r and cnt[q][p][3 - sd] == 0), None)
                    D[(k, 'rounds until clean (999 never)')].append(clean - r if clean is not None else 999)
                    nb = [x for x in builds.get(p, ()) if x[0] >= r]
                    own = next((x[0] for x in nb if x[1] == sd), None)
                    oth = next((x[0] for x in nb if x[1] != sd), None)
                    C[(k, 'first built by own')] += bool(nb) and nb[0][1] == sd
                    C[(k, 'first built by other')] += bool(nb) and nb[0][1] != sd
                    D[(k, 'rounds until built by own (999)')].append(own - r if own else 999)
                    D[(k, 'own mop actions in 5x5, next 50')].append(sum(1 for q in mops[sd][p] if r <= q < r + 50))
                    D[(k, 'own soldier-turns cheb<=2, next 50')].append(sum(1 for q in sol[sd][p] if r <= q < r + 50))
                    D[(k, 'own tiles in 5x5')].append(cnt[r][p][sd])
    print(f'== {which} games: free ruins in the side\'s own half with the other side\'s paint in the 5x5')
    for r in CK:
        for w in ('us', 'them'):
            for lo, hi in BANDS:
                k = (w, r, f'{lo}-{hi}')
                if not C[k]: continue
                print(f'  r{r} {w:4s} {lo:2d}-{hi:<2d} enemy tiles: {C[k]:3d} ruins; first built by own {C[(k, "first built by own")]}, by other {C[(k, "first built by other")]}')
                print('        ' + '; '.join(f'{m} med {lib.med(D[(k, m)])}' for m in
                      ('own tiles in 5x5', 'rounds until clean (999 never)', 'rounds until built by own (999)',
                       'own mop actions in 5x5, next 50', 'own soldier-turns cheb<=2, next 50')))

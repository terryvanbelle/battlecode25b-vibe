"""Topic 64: do we know the free ruins we ignore?  For every CLEAN free ruin (no tower, no enemy tile in its 5x5) at
r100 and r150 in our half of the map: was it ever seen before that round (one of our robots or towers within
vision, d2 <= 20, robots only for 'robots'), distance to our nearest standing tower, rounds until the first of
our soldiers comes within d2 <= 20 after the checkpoint, and until we mark it / build it.  The same for THEIR
clean free ruins in their half (their soldiers).  Lost and won games."""
import lib
from collections import defaultdict, Counter
CK = (100, 150)
for which in ('lost', 'won'):
    D = defaultdict(list); C = Counter()
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
        def half(p):
            du = min(lib.d2(p, q) for q in start[1]); do = min(lib.d2(p, q) for q in start[2])
            return 1 if du < do else 2 if do < du else 0
        want = set(CK); snaps = {}
        def hook(a, grid):
            r = a[0] - 1
            if r in want and r not in snaps:
                s = {}
                for p in G.ruins:
                    en = {1: 0, 2: 0}
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            x, y = p[0] + dx, p[1] + dy
                            if (dx or dy) and 0 <= x < G.W and 0 <= y < G.H:
                                o = lib.owner(grid[x + y * G.W])
                                if o: en[o] += 1
                    s[p] = en
                snaps[r] = s
        lib.replay_grid(G, hook)
        seen = {1: {}, 2: {}}      # side -> ruin -> first round a robot of side was within d2 <= 20
        solnear = {1: defaultdict(list), 2: defaultdict(list)}
        for t in G.turns:
            if t[3] not in lib.BOT: continue
            for p in G.ruins:
                if lib.d2((t[4], t[5]), p) <= 20:
                    seen[t[2]].setdefault(p, t[0])
                    if t[3] == 'SOLDIER': solnear[t[2]][p].append(t[0])
        marks = {1: defaultdict(list), 2: defaultdict(list)}
        for a in G.acts:
            if a[4] == 'mark' and a[3] in lib.BOT:
                x, y = map(int, a[5].split(','))
                for p in G.ruins:
                    if max(abs(p[0] - x), abs(p[1] - y)) <= 2: marks[a[2]][p].append(a[0])
        nextb = defaultdict(list)
        for x in b:
            if x[0] > 0: nextb[(x[4], x[5])].append((x[0], x[3]))
        for r in CK:
            if G.end < r + 10 or r not in snaps: continue
            occ = set((t[4], t[5]) for sd in (1, 2) for t in lib.towers_alive(G, sd, r, b, d))
            for sd in (G.us, G.op):
                w = 'us' if sd == G.us else 'them'
                mine = [(t[4], t[5]) for t in lib.towers_alive(G, sd, r, b, d)]
                for p in G.ruins:
                    if p in occ or half(p) != sd or snaps[r][p][3 - sd] > 0: continue
                    k = (w, r)
                    C[k] += 1
                    known = p in seen[sd] and seen[sd][p] <= r
                    C[(k, 'known')] += known
                    D[(k, 'cheb to nearest own tower')].append(min((max(abs(p[0] - q[0]), abs(p[1] - q[1])) for q in mine), default=None))
                    nxt = next((q for q in solnear[sd][p] if q >= r), None)
                    D[(k, 'rounds to soldier within d2 20')].append(nxt - r if nxt is not None else 999)
                    mk = next((q for q in sorted(marks[sd][p]) if q >= r), None)
                    D[(k, 'rounds to our mark')].append(mk - r if mk is not None else 999)
                    nb = [x for x in nextb.get(p, ()) if x[0] >= r]
                    who = 'none' if not nb else ('own' if nb[0][1] == sd else 'enemy')
                    C[(k, 'next built by ' + who)] += 1
                    if nb: D[(k, 'rounds to next build (any side)')].append(nb[0][0] - r)
                    D[(k, 'own paint tiles in 5x5')].append(snaps[r][p][sd])
    print(f'== {which} games: clean free ruins in the side\'s own half')
    for r in CK:
        for w in ('us', 'them'):
            k = (w, r)
            if not C[k]: continue
            print(f'  r{r} {w:4s} {C[k]:3d} ruins: seen before {C[(k, "known")]}; next built by own {C[(k, "next built by own")]}, enemy {C[(k, "next built by enemy")]}, never {C[(k, "next built by none")]}')
            for m in ('cheb to nearest own tower', 'rounds to soldier within d2 20', 'rounds to our mark', 'rounds to next build (any side)', 'own paint tiles in 5x5'):
                v = D[(k, m)]
                print(f'        {m:32s} med {lib.med(v)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)}')

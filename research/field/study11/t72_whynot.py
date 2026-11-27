"""Topic 72: why we stop taking new ruins after r100, game by game.  For every lost game: our and their new-ruin builds
in r101-250, and the free ruins (no tower) in OUR half at r100 by state: not yet seen by our robots (d2 <= 20 of an
end-of-turn position), seen and clean (no enemy tile in the 5x5), seen with 1-4 enemy tiles, seen with 5+.  For each
state also how many we built later, and how many they did.  Then the same totals for won games."""
import lib
from collections import Counter
ST = ('unseen', 'clean', 'enemy 1-4', 'enemy 5+')


def scan(G):
    b, d = lib.tower_events(G)
    start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
    def half(p):
        du = min(lib.d2(p, q) for q in start[1]); do = min(lib.d2(p, q) for q in start[2])
        return 1 if du < do else 2 if do < du else 0
    snap = {}
    def hook(a, grid):
        if a[0] - 1 == 100 and not snap:
            for p in G.ruins:
                e = 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        x, y = p[0] + dx, p[1] + dy
                        if (dx or dy) and 0 <= x < G.W and 0 <= y < G.H and lib.owner(grid[x + y * G.W]) == G.op: e += 1
                snap[p] = e
    lib.replay_grid(G, hook)
    seen = {}
    for t in G.turns:
        if t[0] > 100: break
        if t[3] in lib.BOT and t[2] == G.us:
            for p in G.ruins:
                if lib.d2((t[4], t[5]), p) <= 20: seen.setdefault(p, t[0])
    occ = set((t[4], t[5]) for sd in (1, 2) for t in lib.towers_alive(G, sd, 100, b, d))
    prev = set(); new = Counter(); nextb = {}
    for x in b:
        p = (x[4], x[5])
        if x[0] > 0 and 101 <= x[0] <= 250 and p not in prev: new[x[3]] += 1
        if x[0] > 100 and p not in nextb: nextb[p] = x[3]
        prev.add(p)
    c = Counter()
    for p in G.ruins:
        if p in occ or half(p) != G.us: continue
        s = 'unseen' if p not in seen else 'clean' if snap.get(p, 0) == 0 else 'enemy 1-4' if snap[p] <= 4 else 'enemy 5+'
        c[s] += 1
        if p in nextb: c[(s, 'us' if nextb[p] == G.us else 'them')] += 1
    return new, c


for which in ('lost', 'won'):
    T = Counter(); NU = []; NT = []
    if which == 'lost':
        print('== lost games: new-ruin builds r101-250 (us/them); free ruins in our half at r100 by state, (later built by us/them)')
    for G in lib.games(which):
        if G.end < 150: continue
        new, c = scan(G)
        NU.append(new[G.us]); NT.append(new[G.op])
        for k, v in c.items(): T[k] += v
        if which == 'lost':
            print(f'   m{G.m}g{G.g} {G.map[:14]:14s} {G.W}x{G.H} end {G.end:4d}  new {new[G.us]}/{new[G.op]}   ' +
                  '  '.join(f'{s} {c[s]} ({c[(s, "us")]}/{c[(s, "them")]})' for s in ST))
    print(f'== {which} totals ({len(NU)} games reaching r150): new-ruin builds r101-250 us {sum(NU)} (med {lib.med(NU)}) | them {sum(NT)} (med {lib.med(NT)});  ' +
          '  '.join(f'{s} {T[s]} ({T[(s, "us")]}/{T[(s, "them")]})' for s in ST))

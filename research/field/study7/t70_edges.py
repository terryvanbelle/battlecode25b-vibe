"""Topic 70: where exploration does not reach.  Unit.exploreTarget picks a uniformly random tile and walks there, which
(as any random-waypoint walk) visits the middle of the map more than its edges and corners.  Per side: the share of
passable tiles in the side's OWN half seen by r100 / r150 (a tile within d2 <= 20 of one of its robots' end-of-turn
positions), by distance to the nearest map border (Chebyshev 0-4, 5-9, 10+), and the same for the ruins there.
Lost and won games on maps with min side >= 30 (where exploration matters), and the top-5 reference set."""
import lib, os
from collections import defaultdict
CK = (100, 150)
OFF = [(dx, dy) for dx in range(-4, 5) for dy in range(-4, 5) if dx * dx + dy * dy <= 20]
RING = ((0, 4), (5, 9), (10, 99))


def run(label, GS):
    D = defaultdict(list); n = 0
    for G in GS:
        if min(G.W, G.H) < 30: continue
        n += 1
        b, d = lib.tower_events(G)
        start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
        W, H = G.W, G.H
        half = [0] * (W * H); ring = [0] * (W * H)
        for y in range(H):
            for x in range(W):
                du = min(lib.d2((x, y), q) for q in start[1]); do = min(lib.d2((x, y), q) for q in start[2])
                half[x + y * W] = 1 if du < do else 2 if do < du else 0
                e = min(x, y, W - 1 - x, H - 1 - y)
                ring[x + y * W] = next(i for i, (lo, hi) in enumerate(RING) if lo <= e <= hi)
        seen = {1: bytearray(W * H), 2: bytearray(W * H)}
        bt = lib.by_round_turns(G)
        ruinidx = set(p[0] + p[1] * W for p in G.ruins)
        for r in range(1, min(G.end, max(CK)) + 1):
            for t in bt.get(r, ()):
                if t[3] not in lib.BOT: continue
                s = seen[t[2]]
                for dx, dy in OFF:
                    x, y = t[4] + dx, t[5] + dy
                    if 0 <= x < W and 0 <= y < H: s[x + y * W] = 1
            if r in CK and G.end >= r:
                for sd in (G.us, G.op):
                    w = 'us' if sd == G.us else 'them'
                    for k in range(len(RING)):
                        tiles = [i for i in range(W * H) if half[i] == sd and ring[i] == k and i not in G.walls]
                        if tiles: D[(w, r, k, 'tiles')].append(100 * sum(seen[sd][i] for i in tiles) / len(tiles))
                        rr = [i for i in tiles if i in ruinidx] + [i for i in ruinidx if half[i] == sd and ring[i] == k and i in G.walls]
                        if rr: D[(w, r, k, 'ruins')].append(100 * sum(seen[sd][i] for i in rr) / len(rr))
    print(f'== {label}: {n} games with min side >= 30; median % of the side\'s own half seen, by distance to the border; us | them')
    for r in CK:
        print(f'  r{r}: ' + '   '.join(f'border {lo}-{hi if hi < 99 else "+"}: tiles {lib.med(D[("us", r, k, "tiles")]):.0f} | {lib.med(D[("them", r, k, "tiles")]):.0f}, ruins {lib.med(D[("us", r, k, "ruins")])} | {lib.med(D[("them", r, k, "ruins")])} (n {len(D[("us", r, k, "ruins")])})'
                                for k, (lo, hi) in enumerate(RING)))


run('lost', list(lib.games('lost')))
run('won', list(lib.games('won')))
os.environ['S7SET'] = 'ref5'
run('top-5 reference', list(lib.games('all')))

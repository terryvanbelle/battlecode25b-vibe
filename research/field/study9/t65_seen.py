"""Topic 65: exploration.  The share of the map's passable tiles and of its ruins that each side has seen (a tile
within d2 <= 20 of one of its robots' end-of-turn positions; towers' own vision is ignored) by r25/50/100/150/200,
split into the side's own half and the other half; and soldier-turns per newly seen tile.  Lost and won games and
the top-5 reference set.  Our Unit.exploreTarget is a uniformly random map tile, renewed on arrival (d2 <= 8),
after 60 rounds, or when known to be a wall."""
import lib, os
from collections import defaultdict
CK = (25, 50, 100, 150, 200)
OFF = [(dx, dy) for dx in range(-4, 5) for dy in range(-4, 5) if dx * dx + dy * dy <= 20]


def run(label, GS):
    D = defaultdict(list); n = 0
    for G in GS:
        n += 1
        b, d = lib.tower_events(G)
        start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
        W, H = G.W, G.H
        half = [0] * (W * H)
        for y in range(H):
            for x in range(W):
                du = min(lib.d2((x, y), q) for q in start[1]); do = min(lib.d2((x, y), q) for q in start[2])
                half[x + y * W] = 1 if du < do else 2 if do < du else 0
        passable = [i for i in range(W * H) if i not in G.walls]
        seen = {1: bytearray(W * H), 2: bytearray(W * H)}
        newc = {1: 0, 2: 0}; sturns = {1: 0, 2: 0}
        bt = lib.by_round_turns(G)
        ruinidx = [p[0] + p[1] * W for p in G.ruins]
        for r in range(1, min(G.end, max(CK)) + 1):
            for t in bt.get(r, ()):
                if t[3] not in lib.BOT: continue
                sd = t[2]; s = seen[sd]
                if t[3] == 'SOLDIER': sturns[sd] += 1
                for dx, dy in OFF:
                    x, y = t[4] + dx, t[5] + dy
                    if 0 <= x < W and 0 <= y < H:
                        i = x + y * W
                        if not s[i]: s[i] = 1; newc[sd] += 1
            if r in CK and G.end >= r:
                for sd in (G.us, G.op):
                    w = 'us' if sd == G.us else 'them'
                    s = seen[sd]
                    for h, nm in ((sd, 'own half'), (3 - sd, 'other half')):
                        pp = [i for i in passable if half[i] == h]
                        D[(w, r, 'tiles seen % ' + nm)].append(100 * sum(s[i] for i in pp) / max(1, len(pp)))
                        rr = [i for i, p in zip(ruinidx, G.ruins) if half[i] == h]
                        D[(w, r, 'ruins seen % ' + nm)].append(100 * sum(s[i] for i in rr) / max(1, len(rr)))
    print(f'== {label}: {n} games; medians, us | them')
    for r in CK:
        print(f'  r{r:<4}' + '  '.join(f'{k} {lib.med(D[("us", r, k)])} | {lib.med(D[("them", r, k)])}'
                                    for k in ('tiles seen % own half', 'ruins seen % own half', 'tiles seen % other half', 'ruins seen % other half')))


run('lost', lib.games('lost'))
run('won', lib.games('won'))
os.environ['S9SET'] = 'prev'
run("study 8's lost games (2873-3201)", lib.games('lost'))

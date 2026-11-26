"""Topic 34: why our splashers sit with paint.  For splasher turns stuck (5x5 box for 25 turns, as t16) with >= 150
paint and no own tower adjacent: the ground around them at that round (replayed grid): ally / empty / enemy tiles
within d2<=20 (vision), walls within d2<=20, nearest non-ally passable tile distance, enemy tower within d2<=20,
and a 'best splash score' as Splasher.splash computes it (empty +1 in r2<=4, enemy +2 in r2<=2 ... approx.)."""
import lib, sys
from collections import defaultdict, Counter
which = sys.argv[1] if len(sys.argv) > 1 else 'us'
agg = Counter(); n = 0; ex = []
for G in lib.games():
    sd = G.us if which == 'us' else G.op
    b, d = lib.tower_events(G)
    pos = defaultdict(list)
    for t in G.turns:
        if t[2] == sd and t[3] == 'SPLASHER': pos[t[1]].append(t)
    want = defaultdict(list)   # round -> stuck turns
    for i, L in pos.items():
        j = 0
        for k in range(len(L)):
            while max(abs(L[k][4] - L[j][4]), abs(L[k][5] - L[j][5])) > 2 or k - j > 25: j += 1
            if k - j < 25 or L[k][7] < 150: continue
            want[L[k][0]].append(L[k])
    if not want: continue
    W, H = G.W, G.H
    snap = {}
    def hook(a, grid):
        r = a[0]
        while hook.next and hook.next[0] < r:
            snap[hook.next.pop(0)] = list(grid)
    hook.next = sorted(want)
    g = lib.replay_grid(G, hook)
    for r in hook.next: snap[r] = list(g)
    for r, ts in want.items():
        grid = snap[r]
        et = [(x[4], x[5]) for x in lib.towers_alive(G, 3 - sd, r, b, d)]
        ot = [(x[4], x[5]) for x in lib.towers_alive(G, sd, r, b, d)]
        for t in ts:
            if any(max(abs(t[4] - x), abs(t[5] - y)) <= 1 for x, y in ot): continue
            n += 1
            c = Counter(); near = 99
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    q = dx * dx + dy * dy
                    if q > 20: continue
                    x, y = t[4] + dx, t[5] + dy
                    if not (0 <= x < W and 0 <= y < H): c['offmap'] += 1; continue
                    i = x + y * W
                    if i in G.walls or (x, y) in G.ruins: c['wall/ruin'] += 1; continue
                    o = lib.owner(grid[i])
                    c['ally' if o == sd else ('empty' if o == 0 else 'enemy')] += 1
                    if o != sd and q >= 5: near = min(near, q)
            agg['turns'] += 1
            for k, v in c.items(): agg[k] += v
            agg['non-ally tile at d2>=5 visible'] += near < 99
            agg['enemy tower d2<=20'] += any(lib.d2((t[4], t[5]), e) <= 20 for e in et)
            agg['enemy tower d2<=36'] += any(lib.d2((t[4], t[5]), e) <= 36 for e in et)
            if len(ex) < 12 and (not ex or ex[-1][0] != (G.m, t[1])):
                ex.append(((G.m, t[1]), G.map, r, t[4], t[5], t[7], dict(c), near))
print(which, 'stuck splasher turns analysed', n)
for k, v in agg.items(): print(f'  {k:32s} {v if k == "turns" else round(v / max(1, agg["turns"]), 2)}  (mean per turn)')
for e in ex: print('  e.g.', e)

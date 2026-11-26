"""Topic 18: rounds a fully painted ruin waits for chips.  'Ready' = first round end at which all 24 tiles around an
empty ruin are painted by side X with at least one X robot within Chebyshev 2... simplified: all 24 own-painted.
Wait = build round - ready round (or game end / enemy takeover / repaint if never built).  Spawns by X during the wait
and chips they cost; chips at ready."""
import lib
from collections import defaultdict
S = defaultdict(lambda: defaultdict(list))
COSTC = {'SOLDIER': 250, 'SPLASHER': 400, 'MOPPER': 300}
for G in lib.games():
    b, d = lib.tower_events(G)
    W = G.W
    bl = defaultdict(list)
    for x in b:
        if x[0] > 0: bl[(x[3], (x[4], x[5]))].append(x[0])
    ready = {}   # (side, ruin) -> list of ready rounds (start of a ready spell)
    state = {}
    def hook(a, grid, cur=[0]):
        if a[0] == cur[0]: return
        r = cur[0]; cur[0] = a[0]
        for q in G.ruins:
            cnt = {1: 0, 2: 0}
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == dy == 0: continue
                    x, y = q[0] + dx, q[1] + dy
                    if 0 <= x < W and 0 <= y < G.H:
                        v = grid[x + y * W]
                        if v: cnt[lib.owner(v)] += 1
                    else: cnt[1] += 0
            inb = sum(1 for dx in range(-2, 3) for dy in range(-2, 3) if (dx or dy) and 0 <= q[0]+dx < W and 0 <= q[1]+dy < G.H)
            for sd in (1, 2):
                full = cnt[sd] >= inb and inb == 24
                k = (sd, q)
                if full and not state.get(k): ready.setdefault(k, []).append(r)
                state[k] = full
    lib.replay_grid(G, hook)
    sp = [a for a in G.acts if a[4] == 'spawn' and a[3] in lib.TOW]
    for (sd, q), rs in ready.items():
        nm = 'US' if sd == G.us else 'TH'
        for r0 in rs:
            # skip if a tower already stands there (pattern stays painted after build)
            al = lib.towers_alive(G, 1, r0, b, d) + lib.towers_alive(G, 2, r0, b, d)
            if any((x[4], x[5]) == q for x in al): continue
            nb = [z for z in bl[(sd, q)] if z >= r0]
            end = nb[0] if nb else None
            if end is None:
                S[nm]['ready never built'].append(r0); continue
            w = end - r0
            S[nm]['wait rounds ready->build'].append(w)
            s_ = [a for a in sp if a[2] == sd and r0 <= a[0] < end]
            S[nm]['chips spent on units during wait'].append(sum(COSTC.get(a[6], 0) for a in s_))
            S[nm]['chips at ready'].append(lib.money(G, sd, r0))
            S[nm]['waits >= 10 rounds'].append(1 if w >= 10 else 0)
    for nm in ('US', 'TH'):
        w = [v for v in S[nm]['wait rounds ready->build']]
for nm in ('US', 'TH'):
    print(nm)
    for k, v in S[nm].items():
        print(f'   {k:<34} n={len(v)} med {lib.med(v)} mean {sum(v)/max(1,len(v)):.1f} p75 {lib.pct(v,.75)} p90 {lib.pct(v,.9)} sum {sum(v)}')

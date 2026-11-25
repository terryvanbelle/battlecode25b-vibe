"""Topic 3: ruin building. For every ruin the top team built (first build there): start = first op mark on its
5x5 (or first op paint on a pattern tile if never marked), workers = distinct op units painting its pattern tiles
in [start, build], time to completion, colour correctness, whether builders paint off-pattern tiles meanwhile,
mopper cleaning of our paint on the pattern; unfinished ruins (worked >= 5 tiles but never built)."""
import lib
from collections import Counter, defaultdict
P = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    W = G.W; tn = G.team_name
    b, d = lib.tower_events(G)
    builtat = {}
    for x in b:
        if x[3] == G.op and x[0] > 0 and (x[4], x[5]) not in builtat: builtat[(x[4], x[5])] = (x[0], x[2])
    ours = {}
    for x in b:
        if x[3] == G.us and (x[4], x[5]) not in ours: ours[(x[4], x[5])] = x[0]
    ruinset = set(G.ruins)
    t2r = defaultdict(list)
    for (rx, ry) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy: t2r[(rx + dx, ry + dy)].append((rx, ry))
    marks = defaultdict(list); paints = defaultdict(list); unp = defaultdict(list); ourp = defaultdict(list)
    solpaint = []  # (round, id, tile)
    rt = lib.by_round_turns(G)
    pos = {}
    for t in G.turns: pos[(t[0], t[1])] = (t[4], t[5])
    def hook(a, grid):
        k = a[4]
        if k not in ('paint', 'mark', 'unpaint'): return
        x, y = map(int, a[5].split(','))
        rs = t2r.get((x, y), [])
        for r in rs:
            if k == 'mark' and a[2] == G.op: marks[r].append((a[0], a[1], a[6] == '1'))
            elif k == 'paint' and a[2] == G.op: paints[r].append((a[0], a[1], a[3], a[6] == '1', (x, y)))
            elif k == 'paint' and a[2] == G.us: ourp[r].append(a[0])
            elif k == 'unpaint' and a[2] == G.op: unp[r].append((a[0], a[3]))
        if k == 'paint' and a[2] == G.op and a[3] == 'SOLDIER': solpaint.append((a[0], a[1], (x, y), bool(rs)))
    lib.replay_grid(G, hook)
    nm = 0
    for r in G.ruins:
        if r in builtat and builtat[r][0] > 0:
            br, ty = builtat[r]
            mk = [m for m in marks[r] if m[0] <= br]
            pp = [p for p in paints[r] if p[0] <= br]
            if not pp: continue
            st = mk[0][0] if mk else None
            # start without marks: first round from which >=3 op pattern paints occur within 8 rounds
            if st is None:
                rs = sorted(p[0] for p in pp)
                st = next((rs[i] for i in range(len(rs) - 2) if rs[i + 2] - rs[i] <= 8), rs[0])
            win = [p for p in pp if p[0] >= st]
            ws = set(p[1] for p in win)
            P[tn]['marked before build (frac)'].append(1 if mk else 0)
            P[tn]['rounds start->build'].append(br - st)
            P[tn]['workers (distinct units painting pattern)'].append(len(ws))
            P[tn]['soldier workers'].append(len(set(p[1] for p in win if p[2] == 'SOLDIER')))
            P[tn]['splasher paints in pattern window'].append(sum(1 for p in win if p[2] == 'SPLASHER'))
            # correctness vs final type pattern
            ok = sum(1 for p in win if lib.secondary(ty, p[4][0] - r[0], p[4][1] - r[1]) == p[3] and max(abs(p[4][0] - r[0]), abs(p[4][1] - r[1])) <= 2)
            P[tn]['correct-colour frac of pattern paints'].append(round(ok / len(win), 2))
            P[tn]['pattern paints per completed ruin'].append(len(win))
            P[tn]['rounds last pattern paint -> build (waiting for chips)'].append(br - max(p[0] for p in win))
            P[tn]['chips before build'].append(lib.money(G, G.op, br - 1))
            P[tn]['rounds first mark -> 12th pattern paint'].append((sorted(p[0] for p in win)[11] - st) if len(win) >= 12 else None)
            P[tn]['our paints on the pattern during window'].append(sum(1 for q in ourp[r] if st <= q <= br))
            P[tn]['op mopper unpaints on pattern during window'].append(sum(1 for q in unp[r] if st <= q[0] <= br and q[1] == 'MOPPER'))
            # builders' off-pattern soldier paints within Chebyshev 4 of this ruin during window
            on = off = 0
            for (rr, i, tile, inpat) in solpaint:
                if i in ws and st <= rr <= br:
                    p0 = pos.get((rr, i))
                    if p0 and max(abs(p0[0] - r[0]), abs(p0[1] - r[1])) <= 3:
                        if inpat: on += 1
                        else: off += 1
            if on + off: P[tn]['builder soldier paints (within Cheb3 of ruin) that are on pattern tiles'].append(round(on / (on + off), 2))
            # concurrency: number of workers present (Cheb<=3) per round, max
            mx = 0
            for rr in range(st, br + 1):
                n = sum(1 for t in rt[rr] if t[2] == G.op and t[3] in lib.BOT and max(abs(t[4] - r[0]), abs(t[5] - r[1])) <= 3)
                mx = max(mx, n)
            P[tn]['max op robots within Cheb3 during build'].append(mx)
        else:
            pp = paints[r]; mk = marks[r]
            if len(set(p[4] for p in pp)) >= 5 or mk:
                nm += 1
                last = max([p[0] for p in pp] + [m[0] for m in mk])
                first = min([p[0] for p in pp] + [m[0] for m in mk])
                P[tn]['unfinished: (first, last op work, we built it at, our paints on it, op mopper unpaints)'].append(
                    (first, last, ours.get(r), len(ourp[r]), len(unp[r])))
    P[tn]['unfinished ruins per game'].append(nm)
for tn, D in P.items():
    print(' ', tn)
    for k, v in D.items():
        if k.startswith('unfinished:'): print(f'     {k}: {v[:14]}')
        else: print(f'     {k:<75} med {lib.med(v)}  p10 {lib.pct(v, .1)} p90 {lib.pct(v, .9)} n={len(v)}')

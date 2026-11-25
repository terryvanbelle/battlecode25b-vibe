"""Topic 9: early exploration. Soldiers the top team spawns by r50: distance from spawn point by age, paints per turn
by age bucket, share of paints on pattern (ruin 5x5) tiles, direction (toward map centre / toward our start),
coverage curve r10..r100 (both sides), first enemy contact."""
import lib
from collections import Counter, defaultdict
P = defaultdict(lambda: defaultdict(list)); COV = defaultdict(lambda: defaultdict(list))
AG = (5, 10, 20, 30, 40, 60, 80)
for G in lib.games():
    tn = G.team_name; W, H = G.W, G.H
    diag = (W * W + H * H) ** .5
    b, d = lib.tower_events(G)
    ustart = [(x[4], x[5]) for x in b if x[3] == G.us and x[0] == 0]
    rtiles = set((rx + dx, ry + dy) for (rx, ry) in G.ruins for dx in range(-2, 3) for dy in range(-2, 3))
    hist = defaultdict(dict)
    for t in G.turns: hist[t[1]][t[0]] = t
    paints = defaultdict(list)
    for a in G.acts:
        if a[4] == 'paint' and a[2] == G.op and a[3] == 'SOLDIER':
            paints[a[1]].append((a[0], tuple(map(int, a[5].split(',')))))
    for a in G.acts:
        if a[4] != 'spawn' or a[6] != 'SOLDIER' or a[2] != G.op or a[0] > 50: continue
        i = int(a[5]); r0 = a[0]; sp = tuple(map(int, a[7].split(','))); h = hist[i]
        for ag in AG:
            if r0 + ag in h:
                p = (h[r0 + ag][4], h[r0 + ag][5])
                P[tn][f'dist from spawn at age {ag}'].append(round(lib.d2(p, sp) ** .5, 1))
                P[tn][f'dist from spawn at age {ag} (% map diag)'].append(round(100 * lib.d2(p, sp) ** .5 / diag))
                du0 = min(lib.d2(sp, u) for u in ustart) ** .5; du = min(lib.d2(p, u) for u in ustart) ** .5
                if ag == 40: P[tn]['closer to our start at age 40 (frac)'].append(1 if du < du0 - 3 else 0)
        for lo, hi in ((0, 10), (10, 30), (30, 60)):
            nt = sum(1 for q in range(r0 + lo, r0 + hi) if q in h)
            if nt >= (hi - lo) * 0.8:
                npaint = sum(1 for (q, _) in paints[i] if r0 + lo <= q < r0 + hi)
                P[tn][f'paints/turn age {lo}-{hi}'].append(round(npaint / nt, 2))
        pp = [x for (q, x) in paints[i] if q < r0 + 60]
        if pp: P[tn]['share of first-60-round paints on ruin 5x5 tiles'].append(round(sum(1 for x in pp if x in rtiles) / len(pp), 2))
        # paint level over time
        for ag in (10, 30, 60):
            if r0 + ag in h: P[tn][f'paint at age {ag}'].append(h[r0 + ag][7])
    ca = 'covA' if G.op == 1 else 'covB'; cu = 'covB' if G.op == 1 else 'covA'
    for R in (10, 20, 30, 40, 50, 60, 80, 100):
        COV[tn][R].append((int(G.rounds[R - 1][ca]), int(G.rounds[R - 1][cu]), round(100 * int(G.rounds[R - 1][ca]) / G.sm['paintable'])))
for tn, D in P.items():
    print(' ', tn)
    for k, v in D.items(): print(f'     {k:<50} med {lib.med(v)} p10 {lib.pct(v, .1)} p90 {lib.pct(v, .9)} n={len(v)}')
    print('     coverage (them, us, them % paintable) medians:', {R: (lib.med([x[0] for x in L]), lib.med([x[1] for x in L]), lib.med([x[2] for x in L])) for R, L in COV[tn].items()})

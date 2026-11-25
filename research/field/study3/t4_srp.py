"""Topic 4: special resource patterns (SRPs) of the top teams: timing, count, placement (lattice, distance to
towers/ruins), who paints the tiles, marking, batching, conflicts with tower patterns."""
import lib
from collections import Counter, defaultdict
P = defaultdict(lambda: defaultdict(list)); LAT = defaultdict(Counter); OFF = defaultdict(Counter)
for G in lib.games():
    W = G.W; tn = G.team_name
    b, d = lib.tower_events(G)
    last = {}  # tile -> (type, id, round) of last op painter
    marks = defaultdict(list)
    ev = []
    def hook(a, grid):
        if a[2] != G.op: return
        if a[4] == 'paint':
            x, y = map(int, a[5].split(',')); last[(x, y)] = (a[3], a[1], a[0])
        elif a[4] == 'mark':
            x, y = map(int, a[5].split(',')); marks[(x, y)].append(a[0])
        elif a[4] == 'srp':
            x, y = map(int, a[5].split(','))
            tiles = [(x + dx, y + dy) for dx in range(-2, 3) for dy in range(-2, 3)]
            pt = Counter(last[t][0] for t in tiles if t in last)
            pr = [last[t][2] for t in tiles if t in last]
            painters = set(last[t][1] for t in tiles if t in last)
            mk = [min(marks[(x, y)])] if marks[(x, y)] else []
            ev.append((a[0], (x, y), a[3], pt, min(pr) if pr else None, len(painters), mk[0] if mk else None))
    lib.replay_grid(G, hook)
    centers = []
    for (r, c, actor, pt, firstp, npaint, mk) in ev:
        al = lib.towers_alive(G, G.op, r, b, d)
        dt = min((lib.d2(c, (t[4], t[5])) ** .5 for t in al), default=None)
        dr = min(max(abs(c[0] - q[0]), abs(c[1] - q[1])) for q in G.ruins)
        rebuilt = c in centers
        centers.append(c)
        P[tn]['completer type'].append(actor[:3])
        P[tn]['dist to nearest own tower'].append(round(dt, 1) if dt else None)
        P[tn]['Chebyshev dist to nearest ruin'].append(dr)
        P[tn]['last-painter types of the 25 tiles (summed)'].append(dict(pt))
        P[tn]['distinct painters of the 25 tiles'].append(npaint)
        P[tn]['marked centre? (rounds mark->complete)'].append(r - mk if mk else None)
        P[tn]['re-completion at same centre'].append(1 if rebuilt else 0)
        LAT[tn][(c[0] % 4, c[1] % 4)] += 1
    uniq = sorted(set(centers))
    for i, c in enumerate(uniq):
        for e in uniq[i + 1:]:
            dx, dy = abs(c[0] - e[0]), abs(c[1] - e[1])
            if max(dx, dy) <= 6: OFF[tn][tuple(sorted((dx, dy)))] += 1
    rs = [e[0] for e in ev]
    P[tn]['SRP completions per game'].append(len(ev))
    P[tn]['distinct SRP centres per game'].append(len(uniq))
    P[tn]['first SRP round'].append(rs[0] if rs else None)
    P[tn]['towers alive at first SRP'].append(len(lib.towers_alive(G, G.op, rs[0], b, d)) if rs else None)
    P[tn]['chips at first SRP'].append(lib.money(G, G.op, rs[0] - 1) if rs else None)
    P[tn]['completions by r150'].append(sum(1 for r in rs if r <= 150))
    P[tn]['completions by r250'].append(sum(1 for r in rs if r <= 250))
    gaps = [rs[i + 1] - rs[i] for i in range(len(rs) - 1)]
    P[tn]['gap between completions (all)'] += gaps
    sc = 'srpA' if G.op == 1 else 'srpB'
    for R in (100, 150, 200, 300):
        if R <= G.end: P[tn][f'active SRPs r{R}'].append(int(G.rounds[R - 1][sc]))
    print(f'm{G.m} g{G.g} {tn} {G.map}: SRPs (round,centre,actor) {[(e[0], e[1], e[2][:2]) for e in ev][:20]}')
print()
for tn, D in P.items():
    print(' ', tn)
    for k, v in D.items():
        if v and isinstance(v[0], dict):
            s = Counter()
            for x in v: s.update(x)
            print(f'     {k:<45} {dict(s)}')
        elif v and isinstance(v[0], str): print(f'     {k:<45} {dict(Counter(v))}')
        else: print(f'     {k:<45} med {lib.med(v)} p10 {lib.pct(v, .1)} p90 {lib.pct(v, .9)} n={len([x for x in v if x is not None])}')
    print('     centre (x%4,y%4):', LAT[tn].most_common(6))
    print('     offsets between nearby distinct centres (Cheb<=6):', OFF[tn].most_common(8))

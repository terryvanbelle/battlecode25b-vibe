"""Topic 3b: fate of ruins the top team MARKED (first mark round per ruin; marks within the ruin's 5x5, while the
ruin has no tower). Outcome: built <=30 rounds after the mark / built later / never built (ours at some point, or
neutral). For never-built neutral ones: our paint on the pattern while they worked it, and rounds of work."""
import lib
from collections import Counter, defaultdict
OUT = defaultdict(Counter); NB = defaultdict(list)
for G in lib.games():
    b, d = lib.tower_events(G)
    tn = G.team_name
    occ = defaultdict(list)  # ruin -> [(built, died, team)]
    dd = {x[1]: x[0] for x in d}
    for x in b: occ[(x[4], x[5])].append((x[0], dd.get(x[1], 10 ** 6), x[3]))
    def occupied(r, q):
        return any(s <= q < e for (s, e, t) in occ[r])
    marks = defaultdict(list); ourp = defaultdict(list)
    t2r = defaultdict(list)
    for (rx, ry) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy: t2r[(rx + dx, ry + dy)].append((rx, ry))
    for a in G.acts:
        if a[4] in ('mark', 'paint'):
            x, y = map(int, a[5].split(','))
            for r in t2r.get((x, y), []):
                if a[4] == 'mark' and a[2] == G.op and not occupied(r, a[0]): marks[r].append(a[0])
                if a[4] == 'paint' and a[2] == G.us: ourp[r].append(a[0])
    for r, L in marks.items():
        # split into campaigns: marks separated by >= 40 rounds
        L.sort(); camps = [[L[0], L[0]]]
        for q in L[1:]:
            if q - camps[-1][1] >= 40: camps.append([q, q])
            else: camps[-1][1] = q
        for s, e in camps:
            nb = [x for x in occ[r] if x[2] == G.op and x[0] >= s]
            ub = [x for x in occ[r] if x[2] == G.us and x[0] >= s]
            if nb and nb[0][0] - s <= 30: OUT[tn]['built <=30r'] += 1
            elif nb and (not ub or nb[0][0] < ub[0][0]): OUT[tn]['built later'] += 1
            elif ub: OUT[tn]['we built it instead'] += 1
            else:
                OUT[tn]['never built (neutral)'] += 1
                NB[tn].append((s, e, sum(1 for q in ourp[r] if s <= q <= e + 5), G.end))
for tn in OUT:
    tot = sum(OUT[tn].values())
    print(tn, dict(OUT[tn]), {k: round(v / tot, 2) for k, v in OUT[tn].items()})
    print('   never-built (first mark, last mark, our paints on pattern meanwhile, game end):', NB[tn][:12])

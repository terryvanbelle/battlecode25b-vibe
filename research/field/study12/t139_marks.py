"""Topic 139: marks after t135 / t140 (did study 11 2.1 work, and what do the top teams' marks do?).
Part A, ours, per version (t122 / t135 / t140), losses and wins together: pattern marks (20+ mark rows by one robot
in a turn, 25 paint each) and single marks per game, the paint spent on pattern marks in r1-100 and overall; marks
that spell both tower types on one ruin (a ring mark agrees with only one of the paint / money patterns; a ruin whose
marks include both kinds = conflict).
Part B, our pattern work on ruins, per version: on each ruin's 5x5 (centre left out) before a tower stood on it,
our re-colour rows (a paint row on a tile that was already ours, in the other colour): the paint and actions that
two different targets on one ruin cost; tiles re-coloured two or more times (flip-flops); and of the towers we
completed, how many rounds from our first paint row on the 5x5 to the completion (median).
Part C, theirs, per team: marks per game; where they sit (Chebyshev distance to the nearest ruin: 1 = beside it);
the share unmarked later; for marks beside a ruin, when the unmark comes relative to the tower built there
(before / within 2 rounds after / later / never) and whether the ruin was built at all; and for marks 3+ tiles from
any ruin, the distance to the nearest of that team's completed SRP centres (0 = on the centre)."""
from collections import defaultdict
import lib

PP, MP = lib.PAT['PAINT_TOWER'], lib.PAT['MONEY_TOWER']


def bit(pat, dx, dy):
    return bool((pat >> (5 * (dx + 2) + dy + 2)) & 1)


def kind_of_mark(dx, dy, sec):
    """'P' if the mark agrees only with the paint pattern, 'M' only with money, '' both/neither."""
    p = bit(PP, dx, dy) == sec; m = bit(MP, dx, dy) == sec
    return 'P' if p and not m else 'M' if m and not p else ''


A = defaultdict(lambda: defaultdict(float))
B = defaultdict(lambda: defaultdict(list))
C = defaultdict(lambda: defaultdict(float))
CL = defaultdict(lambda: defaultdict(list))
for G in lib.games('all'):
    v = G.ver
    ruins = G.ruins
    rset = set(ruins)
    # towers on ruins: first build row (round, team, type)
    built_at = {}
    tpos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in tpos: tpos[t[1]] = (t[4], t[5])
    tower_rounds = defaultdict(list)   # ruin -> [(build round, team, death round or None)]
    deaths = {}
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.TOW: deaths[int(a[5])] = a[0]
        if a[4] == 'died' and a[6] in lib.TOW: deaths[int(a[5])] = a[0]
    for a in G.acts:
        if a[4] == 'build':
            tid = int(a[5]); p = tpos.get(tid)
            if p: tower_rounds[p].append((a[0], a[2], deaths.get(tid), a[6]))
    for t in G.turns:
        if t[0] == 1 and t[3] in lib.TOW: tower_rounds[(t[4], t[5])].append((0, t[2], deaths.get(t[1]), t[3]))

    def standing(rn, r):
        """team of the tower standing on ruin rn at round r, else None"""
        for b, team, d, ty in tower_rounds.get(rn, ()):
            if b <= r and (d is None or r < d): return team
        return None

    def nearest_ruin(x, y):
        best = None; bd = 99
        for (rx, ry) in ruins:
            d = max(abs(rx - x), abs(ry - y))
            if d < bd: bd = d; best = (rx, ry)
        return best, bd

    marks = defaultdict(list)
    for a in G.acts:
        if a[4] == 'mark': marks[(a[0], a[1])].append(a)
    # part A
    D = A[v]; D['games'] += 1
    conflict = defaultdict(set)
    for (r, i), L in marks.items():
        if G.team.get(i) != G.us: continue
        if len(L) >= 20:
            D['pattern'] += 1
            if r <= 100: D['pattern_r100'] += 1
        else:
            D['single'] += len(L)
            for a in L:
                x, y = map(int, a[5].split(','))
                rn, d = nearest_ruin(x, y)
                if rn is None or d != 2: continue
                k = kind_of_mark(x - rn[0], y - rn[1], a[6] == '1')
                if k: conflict[(rn, standing(rn, r))].add(k)
    D['ruins_marked'] += len(conflict)
    D['ruins_conflict'] += sum(1 for s in conflict.values() if len(s) == 2)
    # part B: replay the grid; re-colour rows by us on unbuilt ruins' 5x5
    first_paint = {}
    recol = defaultdict(int); flips = defaultdict(int)

    def hook(a, grid):
        if a[4] != 'paint' or a[2] != G.us or a[3] != 'SOLDIER': return
        x, y = map(int, a[5].split(','))
        for (rx, ry) in ruins:
            if max(abs(rx - x), abs(ry - y)) > 2: continue
            if standing((rx, ry), a[0]) is not None: continue
            first_paint.setdefault((rx, ry), a[0])
            v0 = grid[x + y * G.W]
            if lib.owner(v0) == G.us:
                sec0 = v0 in (2, 4); sec1 = a[6] == '1'
                if sec0 != sec1:
                    B[v]['recolour'].append(1)
                    recol[(x, y)] += 1
                    if recol[(x, y)] == 2: flips[(rx, ry)] += 1

    lib.replay_grid(G, hook)
    B[v]['games'].append(1)
    B[v]['flip_tiles'].append(sum(flips.values()))
    for rn, L in tower_rounds.items():
        for b, team, d, ty in L:
            if team == G.us and b > 0 and rn in first_paint and first_paint[rn] <= b:
                B[v]['build_time'].append(b - first_paint[rn])
    # part C: opponents' marks
    if True:
        tm = G.team_name
        E = C[tm]; E['games'] += 1
        srp_c = [tuple(map(int, a[5].split(','))) for a in G.acts if a[4] == 'srp' and a[2] == G.op]
        unm = defaultdict(list)
        for a in G.acts:
            if a[4] == 'unmark' and a[2] == G.op: unm[a[5]].append(a[0])
        for (r, i), L in marks.items():
            if G.team.get(i) != G.op: continue
            for a in L:
                E['marks'] += 1
                x, y = map(int, a[5].split(','))
                rn, d = nearest_ruin(x, y)
                E['d%d' % min(d, 6)] += 1
                later = [u for u in unm.get(a[5], ()) if u >= r]
                if later: E['unmarked'] += 1
                if d == 1:
                    bl = [b for b, team, dd, ty in tower_rounds.get(rn, ()) if team == G.op and b >= r]
                    if bl:
                        E['beside_built'] += 1
                        b = min(bl)
                        if later:
                            u = min(later)
                            if u < b: E['un_before'] += 1
                            elif u <= b + 2: E['un_at'] += 1
                            else: E['un_after'] += 1
                        else: E['un_never'] += 1
                        CL[tm]['mark_to_build'].append(b - r)
                    else:
                        E['beside_unbuilt'] += 1
                        if later: CL[tm]['mark_to_unmark_unbuilt'].append(min(later) - r)
                elif d >= 3:
                    E['far'] += 1
                    if srp_c:
                        dd = min(max(abs(cx - x), abs(cy - y)) for cx, cy in srp_c)
                        CL[tm]['far_to_srp'].append(dd)

print('Part A, our marks per game, by version (losses and wins together):')
for v in ('t122', 't135', 't140'):
    D = A[v]; n = max(1, D['games'])
    print(f'   {v}: {int(D["games"])} games; pattern marks {D["pattern"] / n:5.2f} per game ({D["pattern_r100"] / n:5.2f} in r1-100 = {25 * D["pattern_r100"] / n:5.0f} paint;'
          f' {25 * D["pattern"] / n:5.0f} paint overall); single marks {D["single"] / n:6.1f};'
          f' ruins with ring marks {D["ruins_marked"] / n:4.1f}, spelling both types {int(D["ruins_conflict"])}')
print('\nPart B, our soldiers\' re-colour rows on unbuilt ruins\' 5x5, by version:')
for v in ('t122', 't135', 't140'):
    D = B[v]; n = max(1, len(D['games']))
    print(f'   {v}: {len(D["recolour"]) / n:5.1f} re-colour rows per game ({5 * len(D["recolour"]) / n:4.0f} paint); tiles re-coloured twice or more'
          f' {sum(D["flip_tiles"]) / n:4.1f} per game; rounds from first paint to completion: median {lib.med(D["build_time"])}, p75 {lib.pct(D["build_time"], .75)} ({len(D["build_time"])} towers)')
print('\nPart C, opponents\' marks (all games against them):')
print('   team                     games  marks/g  beside ruin  2 away  3+ away  unmarked  | beside a ruin later built: unmark before / at / after / never  | unbuilt')
for tm in sorted(C, key=lambda k: -C[k]['marks'] / max(1, C[k]['games'])):
    E = C[tm]; n = max(1, E['games']); m = max(1, E['marks'])
    bb = max(1, E['beside_built'])
    print(f'   {tm[:24]:24s} {int(E["games"]):5d}  {E["marks"] / n:7.1f}  {100 * E["d1"] / m:9.0f}%  {100 * E["d2"] / m:5.0f}%  {100 * (E["d3"] + E["d4"] + E["d5"] + E["d6"]) / m:6.0f}%  {100 * E["unmarked"] / m:7.0f}%'
          f'  | {int(E["beside_built"]):4d}: {100 * E["un_before"] / bb:3.0f}% / {100 * E["un_at"] / bb:3.0f}% / {100 * E["un_after"] / bb:3.0f}% / {100 * E["un_never"] / bb:3.0f}%'
          f'  mark -> build median {lib.med(CL[tm]["mark_to_build"])} rounds  | {int(E["beside_unbuilt"])} (unmark after {lib.med(CL[tm]["mark_to_unmark_unbuilt"])})'
          f'  far marks to nearest SRP centre: median {lib.med(CL[tm]["far_to_srp"])}, on it {sum(1 for x in CL[tm]["far_to_srp"] if x == 0)} of {len(CL[tm]["far_to_srp"])}')

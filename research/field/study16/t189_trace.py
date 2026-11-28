"""Topic 189 (new; illustrates t183): traces of our robots trapped at a drained level-2 money tower (the starting money
tower) while we hold 2000+ chips.  For the three longest such stays in our losses (a stay = consecutive rounds a soldier
or splasher of ours ends within Chebyshev 2 of the tower with under 100 / 150 paint, the tower under 10 paint, chips
2000+), print per round: the robot's position, Chebyshev distance to the tower, paint, HP, and any withdrawal; plus the
nearest own tower holding 60+ paint at the start."""
from collections import defaultdict
import lib

LOW = {'SOLDIER': 100, 'SPLASHER': 150}


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


stays = []
NG = 0
for G in lib.games('lost'):
    NG += 1
    start = {}
    for a in G.acts:
        if a[4] == 'startlevel' and a[3] == 'MONEY_TOWER' and a[2] == G.us: start[int(a[5])] = True
    tp, tpaint, others = {}, defaultdict(dict), defaultdict(dict)
    rob = defaultdict(dict)
    for t in G.turns:
        if t[3] in lib.TOW and t[2] == G.us:
            tpaint[t[1]][t[0]] = t[7]; tp[t[1]] = (t[4], t[5])
        elif t[2] == G.us and t[3] in LOW: rob[t[1]][t[0]] = (t[4], t[5], t[7], t[6], t[3])
    wd = defaultdict(dict)
    for a in G.acts:
        if a[4] == 'transfer' and a[2] == G.us and a[6] and int(a[6]) < 0: wd[a[1]][a[0]] = (int(a[5]), -int(a[6]))
    for tid in start:
        if tid not in tp: continue
        pos = tp[tid]
        for i, tr in rob.items():
            run = []
            for r in sorted(tr):
                x, y, p, hp, typ = tr[r]
                ok = (cheb((x, y), pos) <= 2 and p < LOW[typ] and tpaint[tid].get(r, tpaint[tid].get(r - 1, 999)) < 10
                      and lib.money(G, G.us, r - 1) >= 2000)
                if ok and (not run or run[-1] == r - 1): run.append(r)
                elif ok:
                    if len(run) >= 10: stays.append((len(run), G.m, G.g, G.map, G.team_name, i, tid, pos, run[0], run[-1], max(tr) <= run[-1] + 5 and max(tr) < G.end))
                    run = [r]
                else:
                    if len(run) >= 10: stays.append((len(run), G.m, G.g, G.map, G.team_name, i, tid, pos, run[0], run[-1], max(tr) <= run[-1] + 5 and max(tr) < G.end))
                    run = []
            if len(run) >= 10: stays.append((len(run), G.m, G.g, G.map, G.team_name, i, tid, pos, run[0], run[-1], max(tr) <= run[-1] + 5 and max(tr) < G.end))
    G.turns = G.acts = None
stays.sort(reverse=True)
print(f'stays of 10+ rounds in our losses: {len(stays)}; lengths: ' + ' '.join(str(s[0]) for s in stays[:40]))
print('per game: ' + ', '.join(f'm{s[1]}g{s[2]}' for s in stays[:40]))
for lo, hi in ((1, 100), (101, 200), (201, 300), (301, 2000)):
    S = [x for x in stays if lo <= x[8] <= hi]
    print(f'stays starting in r{lo}-{hi}: {len(S)} in {NG} losses ({len(set((x[1], x[2]) for x in S))} games), {sum(x[0] for x in S) / NG:.0f} robot-rounds per loss, '
          f'median length {lib.med([x[0] for x in S])}; the robot died in the stay or within 5 rounds after it: {sum(1 for x in S if x[10])}')
# re-load the top three games for the traces
for s in stays[:3]:
    n, m, g, mp, opp, i, tid, pos, r0, r1, _d = s
    G = lib.load(m, g)
    rob = defaultdict(dict); tpaint = defaultdict(dict); tp = {}
    for t in G.turns:
        if t[1] == i: rob[i][t[0]] = (t[4], t[5], t[7], t[6], t[3])
        if t[3] in lib.TOW and t[2] == G.us: tpaint[t[1]][t[0]] = t[7]; tp[t[1]] = (t[4], t[5])
    wd = {}
    for a in G.acts:
        if a[4] == 'transfer' and a[1] == i and a[6] and int(a[6]) < 0: wd[a[0]] = (int(a[5]), -int(a[6]))
    alt = []
    for t2, pp in tpaint.items():
        if t2 == tid: continue
        v = pp.get(r0, pp.get(r0 - 1))
        if v is not None and v >= 60: alt.append((cheb(rob[i][r0][:2], tp[t2]), tp[t2], v))
    alt.sort()
    print(f'\nm{m}g{g} {mp} vs {opp}: robot {i} ({rob[i][r0][4]}) at our starting money tower {pos} (L2), r{r0}-r{r1} ({n} rounds); '
          f'chips at r{r0} {lib.money(G, G.us, r0)}; nearest own tower with 60+ paint then: ' + (f'Chebyshev {alt[0][0]} at {alt[0][1]} ({alt[0][2]} paint)' if alt else 'none'))
    line = []
    for r in range(r0 - 5, min(r1 + 15, max(rob[i]) + 1)):
        if r not in rob[i]: continue
        x, y, p, hp, typ = rob[i][r]
        w = f' W{wd[r][1]}' if r in wd else ''
        line.append(f'r{r}:({x},{y}) d{cheb((x, y), pos)} p{p} hp{hp}{w}')
    for k in range(0, len(line), 6): print('   ' + '   '.join(line[k:k + 6]))
    last = max(rob[i])
    print(f'   last turn r{last} (game end r{G.end})')
    G.turns = G.acts = None

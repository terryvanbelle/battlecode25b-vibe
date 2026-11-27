"""Topic 90: the early rush, all games.  Per side and window (r1-50, r51-100): soldier-turns spent in the other half
(nearer the other side's starting towers than to its own), soldier hits on towers, enemy towers killed, and own
robots killed by towers.  Then the result table by who lost the starting paint tower by r100 (and by r150), and the
first mopper round per side."""
import lib
from collections import defaultdict, Counter


def info(G):
    b, d = lib.tower_events(G)
    start = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    spt = {s: next((x[1] for x in b if x[0] == 0 and x[3] == s and x[2] == 'PAINT_TOWER'), None) for s in (1, 2)}
    kills = {int(a[5]): a[0] for a in G.acts if a[4] == 'die' and a[7] in lib.TOW}
    o = {}
    for s in (1, 2):
        side = 'us' if s == G.us else 'them'
        o[(side, 'start PT killed')] = kills.get(spt[s])
        fm = next((a[0] for a in G.acts if a[4] == 'spawn' and a[2] == s and a[6] == 'MOPPER'), None)
        o[(side, 'first mopper')] = fm
    for lo, hi in ((1, 50), (51, 100)):
        cnt = Counter()
        for t in G.turns:
            if t[0] < lo: continue
            if t[0] > hi: break
            if t[3] != 'SOLDIER': continue
            s = t[2]; p = (t[4], t[5])
            own = min(lib.d2(p, q) for q in start[s]); oth = min(lib.d2(p, q) for q in start[3 - s])
            cnt[(s, 'turns')] += 1
            if oth < own: cnt[(s, 'away')] += 1
        for a in G.acts:
            if a[0] < lo: continue
            if a[0] > hi: break
            if a[4] == 'damage' and a[3] == 'SOLDIER' and G.typ.get(int(a[5]), '') in lib.TOW: cnt[(a[2], 'hits')] += 1
            elif a[4] == 'die':
                if a[7] in lib.TOW and a[3] in lib.BOT: cnt[(a[2], 'tower kills')] += 1
                elif a[7] in lib.BOT and a[3] in lib.TOW: cnt[(G.team.get(int(a[5])), 'robots lost to towers')] += 1
        for s in (1, 2):
            side = 'us' if s == G.us else 'them'
            o[(side, lo, 'away %')] = round(100 * cnt[(s, 'away')] / max(1, cnt[(s, 'turns')]))
            for k in ('hits', 'tower kills', 'robots lost to towers'): o[(side, lo, k)] = cnt[(s, k)]
    return o


rows = []
for G in lib.games('all'):
    rows.append((G.won_op, lib.cls(G), f'm{G.m}g{G.g}', G.map, G.team_name, info(G)))
    lib.lite(G)
for lab, sel in (('lost', lambda r: r[0]), ('won', lambda r: not r[0])):
    R = [r for r in rows if sel(r)]
    print(f'== {lab} ({len(R)}): medians per game, us / them')
    for lo in (1, 51):
        print(f'   r{lo}-{lo + 49}: ' + '  '.join(f'{k} {lib.med([r[5][("us", lo, k)] for r in R])}/{lib.med([r[5][("them", lo, k)] for r in R])}'
                                         for k in ('away %', 'hits', 'tower kills', 'robots lost to towers')))
    print(f'   first mopper: us med r{lib.med([r[5][("us", "first mopper")] for r in R])} (none in {sum(r[5][("us", "first mopper")] is None for r in R)}), '
          f'them med r{lib.med([r[5][("them", "first mopper")] for r in R])} (none in {sum(r[5][("them", "first mopper")] is None for r in R)})')
print()
print('== result by the starting paint towers: (our start PT killed by rN?, theirs killed by rN?) -> won / lost')
for N in (100, 150):
    T = defaultdict(lambda: [0, 0])
    for r in rows:
        u = r[5][('us', 'start PT killed')]; t = r[5][('them', 'start PT killed')]
        k = (u is not None and u <= N, t is not None and t <= N)
        T[k][1 if r[0] else 0] += 1
    for k in ((False, False), (True, False), (False, True), (True, True)):
        print(f'   by r{N}: ours killed {str(k[0]):5s} theirs killed {str(k[1]):5s}: won {T[k][0]:2d} lost {T[k][1]:2d}')
print()
print('== games where our starting paint tower fell by r150: round, map, opponent, result, their start PT fell')
for r in rows:
    u = r[5][('us', 'start PT killed')]
    if u is not None and u <= 150:
        print(f'   {r[2]:9s} r{u:<4} {r[3][:13]:13s} {r[4][:12]:12s} {"LOST" if r[0] else "won "}  theirs: r{r[5][("them", "start PT killed")]}')

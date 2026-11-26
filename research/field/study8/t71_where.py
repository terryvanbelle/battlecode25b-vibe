"""Topic 71: where the soldiers are.  Share of each side's soldier-turns (end-of-turn positions) in its own half, the
middle band (distance to both sides' starting towers within 15%), and the other half, by phase; and the share of
the side's soldier deaths that happened in the other half.  Lost and won games."""
import lib
from collections import defaultdict
PH = ((1, 100), (101, 200), (201, 300))
for which in ('lost', 'won'):
    D = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
        cache = {}
        def zone(x, y, sd):
            k = (x, y)
            if k not in cache:
                du = min(lib.d2(k, q) for q in start[1]) ** .5; do = min(lib.d2(k, q) for q in start[2]) ** .5
                cache[k] = (du, do)
            du, do = cache[k]
            own, oth = (du, do) if sd == 1 else (do, du)
            if abs(own - oth) <= 0.15 * (own + oth): return 'mid'
            return 'own' if own < oth else 'other'
        last = {}
        for t in G.turns:
            if t[3] == 'SOLDIER': last[t[1]] = t
        deaths = defaultdict(lambda: defaultdict(int))
        for a in G.acts:
            if a[4] in ('die', 'died') and a[7] == 'SOLDIER':
                tid = int(a[5])
                if tid in last:
                    t = last[tid]
                    deaths[t[2]][zone(t[4], t[5], t[2])] += 1
        for lo, hi in PH:
            if G.end < hi: continue
            cnt = {1: defaultdict(int), 2: defaultdict(int)}
            for t in G.turns:
                if t[3] == 'SOLDIER' and lo <= t[0] <= hi: cnt[t[2]][zone(t[4], t[5], t[2])] += 1
            for sd in (G.us, G.op):
                w = 'us' if sd == G.us else 'them'
                n = sum(cnt[sd].values())
                if n: 
                    for z in ('own', 'mid', 'other'): D[(w, lo, z)].append(100 * cnt[sd][z] / n)
        for sd in (G.us, G.op):
            w = 'us' if sd == G.us else 'them'
            n = sum(deaths[sd].values())
            if n: D[(w, 'deaths other')].append(100 * deaths[sd]['other'] / n)
    print(f'== {which}: soldier-turns by zone, % (median over games), us | them')
    for lo, hi in PH:
        print(f'  r{lo}-{hi}: ' + '  '.join(f'{z} {lib.med(D[("us", lo, z)]):.0f} | {lib.med(D[("them", lo, z)]):.0f}' for z in ('own', 'mid', 'other')))
    print(f'  soldier deaths in the other half: {lib.med(D[("us", "deaths other")]):.0f}% | {lib.med(D[("them", "deaths other")]):.0f}%')

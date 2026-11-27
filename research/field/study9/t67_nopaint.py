"""Topic 67: life without a paint tower.  Per side: rounds with 0 paint towers standing (after r10), how the last paint
tower died (killed / churned), the towers BUILT while none stood (by type), and the round the next paint tower came.
Soldier.wantType returns PAINT with no paint tower only when the soldier's own tower list (G.towerLoc, which forgets
a dead tower only when a refill walks up to it) covers every tower the team has (pt + mt >= n) - otherwise money
while n < 6 (or paint once chips >= 2000 with n >= 3).  Also: paint held by the side's robots + towers during those
rounds, and robots alive.  Lost and won games, all opponents."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    C = defaultdict(Counter); D = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        for sd in (G.us, G.op):
            w = 'us' if sd == G.us else 'them'
            nopt = []
            for r in range(10, G.end + 1):
                if not any(t[2] == 'PAINT_TOWER' for t in lib.towers_alive(G, sd, r, b, d)): nopt.append(r)
            C[w]['games'] += 1
            if not nopt: continue
            C[w]['games with a no-paint-tower spell'] += 1
            D[(w, 'rounds without a paint tower')].append(len(nopt))
            D[(w, 'first such round')].append(nopt[0])
            # builds during the spells
            ns = set(nopt)
            for x in b:
                if x[3] == sd and x[0] in ns:
                    C[w]['built while none: ' + x[2][:5]] += 1
            # spells: next paint tower after the first spell start
            nxt = next((x[0] for x in b if x[3] == sd and x[2] == 'PAINT_TOWER' and x[0] >= nopt[0]), None)
            D[(w, 'rounds from first spell to the next paint tower (9999 never)')].append((nxt - nopt[0]) if nxt else 9999)
            D[(w, 'robots alive during spells (mean)')].append(sum(lib.rv(G, sd, r, 'units') for r in nopt) / len(nopt))
            D[(w, 'paint held during spells (mean)')].append(sum(lib.rv(G, sd, r, 'paint') for r in nopt) / len(nopt))
            if sd == G.us: C[w]['lost games with spell' if G.won_op else 'won games with spell'] += 1
    print(f'== {which} games')
    for w in ('us', 'them'):
        print(f'  {w}: ' + ', '.join(f'{k}: {v}' for k, v in sorted(C[w].items())))
        for k in sorted(set(k for (ww, k) in D if ww == w)):
            v = D[(w, k)]
            print(f'      {k:60s} n={len(v):3d} med {lib.med(v)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)}')

# Each tower we completed while we had no paint tower: on a new ruin or on a ruin an earlier tower of ours stood on
# (marks left by a money tower make workRuin rebuild money; Unit.rebuild and churn rebuild only money)
print('== our towers completed while no paint tower of ours stood (lost games)')
C = Counter()
for G in lib.games('lost'):
    b, d = lib.tower_events(G)
    sd = G.us
    nopt = set(r for r in range(10, G.end + 1) if not any(t[2] == 'PAINT_TOWER' for t in lib.towers_alive(G, sd, r, b, d)))
    if not nopt: continue
    held = {}
    for x in b:
        if x[3] != sd: continue
        p = (x[4], x[5])
        kind = 'new ruin' if p not in held else 'old ' + held[p][:5].lower() + ' ruin'
        if x[0] in nopt:
            C[(x[2][:5], kind)] += 1
            print(f'   m{G.m}g{G.g} {G.map[:12]:12s} r{x[0]:<4d} {x[2][:5]} on {kind} {p}, chips {lib.money(G, sd, x[0] - 1)}, towers {len(lib.towers_alive(G, sd, x[0] - 1, b, d))}')
        held[p] = x[2]
print('   totals: ' + ', '.join(f'{t} on {k}: {v}' for (t, k), v in sorted(C.items())))

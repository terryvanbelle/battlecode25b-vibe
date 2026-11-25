"""Topic 2: towers. Build order (excluding churn rebuilds on the same ruin), rounds, type ratio over time,
upgrades (round, chips, type, level), ruin distance from the team's start."""
import lib
from collections import Counter, defaultdict
P = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    b, d = lib.tower_events(G)
    tn = G.team_name
    start = [x for x in b if x[3] == G.op and x[0] == 0]
    seen = set(); order = []
    for x in b:
        if x[3] != G.op or x[0] == 0: continue
        first = (x[4], x[5]) not in seen; seen.add((x[4], x[5]))
        if first: order.append(x)
    ds = lambda x: min(lib.d2((x[4], x[5]), (s[4], s[5])) for s in start) ** .5
    print(f'== m{G.m} g{G.g} {tn} {G.map} {G.W}x{G.H} ruins={len(G.ruins)}  first builds per ruin (round type distFromStart chipsBefore):')
    print('   ', ' '.join(f'{x[0]}{x[2][0]}({ds(x):.0f},{lib.money(G, G.op, x[0] - 1)})' for x in order[:16]))
    for i, x in enumerate(order[:8]): P[tn][f'build#{i+1} round'].append(x[0])
    for k in range(1, 6):
        P[tn][f'type of build#{k}'].append(order[k - 1][2][0] if len(order) >= k else None)
    for R in (50, 100, 150, 200, 300):
        if R > G.end: continue
        al = lib.towers_alive(G, G.op, R, b, d)
        c = Counter(x[2][0] for x in al)
        P[tn][f'alive r{R} P/M/D'].append(f"{c['P']}/{c['M']}/{c['D']}")
    # upgrades (skip round-1 artefacts)
    ups = [a for a in G.acts if a[4] == 'upgrade' and a[0] > 1 and a[2] == G.op]
    L = []
    for a in ups:
        tid = int(a[5]); hp = int(a[7])
        L.append((a[0], G.typ.get(tid, '?')[:2], 'L2' if hp in (1500, 2500) else 'L3', lib.money(G, G.op, a[0] - 1)))
    print('    upgrades (round type level chipsBefore):', L[:12], 'total', len(L))
    P[tn]['first upgrade round'].append(L[0][0] if L else None)
    P[tn]['first upgrade type'].append(L[0][1] if L else None)
    P[tn]['chips before upgrade'] += [x[3] for x in L]
    P[tn]['upgrades per game'].append(len(L))
    P[tn]['upgrades <= r200'].append(sum(1 for x in L if x[0] <= 200))
    P[tn]['upgrade type mix'].append(dict(Counter(x[1] + x[2] for x in L)))
print('\n== per team')
for tn, D in P.items():
    print(' ', tn)
    for k, v in D.items():
        if isinstance(v[0], (int, float)) or v[0] is None and any(isinstance(z, (int, float)) for z in v):
            print(f'     {k:<24} med {lib.med(v)}  all {v}')
        else:
            print(f'     {k:<24} {v}')

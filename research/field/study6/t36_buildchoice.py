"""Topic 36: tower type chosen vs the state at the time.  For every tower build (incl. churn rebuilds) by each side:
type, chips just before, paint towers standing, and the side's paint-blocked state (share of its towers with
paint < 200 in that round).  Splits: money builds made while chips >= 2000 ('chips already idle'), and builds by
ordinal (1st..8th non-churn build) type mix."""
import lib
from collections import defaultdict, Counter
S = defaultdict(Counter); ordmix = defaultdict(lambda: defaultdict(Counter)); second_pt = defaultdict(list)
for G in lib.games():
    b, d = lib.tower_events(G)
    died_pos = defaultdict(list)
    for a in G.acts:
        if a[4] == 'died' and a[3] in lib.TOW: died_pos[a[1]].append(a[0])
    posd = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in posd: posd[t[1]] = (t[4], t[5])
    churn_spots = defaultdict(list)
    for tid, rs in died_pos.items():
        for r in rs: churn_spots[posd.get(tid)].append(r)
    for sd in (G.us, G.op):
        w = 'us' if sd == G.us else 'them'; k = 0; got2 = None
        for x in b:
            if x[3] != sd or x[0] == 0: continue
            r, typ = x[0], x[2]
            chips = lib.money(G, sd, r - 1)
            churn = any(0 <= r - q <= 5 for q in churn_spots.get((x[4], x[5]), ()))
            al = lib.towers_alive(G, sd, r - 1, b, d)
            npt = sum(1 for t in al if t[2] == 'PAINT_TOWER')
            S[w]['builds'] += 1
            S[w]['churn rebuilds'] += churn
            if churn: continue
            k += 1
            if k <= 10: ordmix[w][k][typ[0]] += 1
            if typ == 'MONEY_TOWER':
                S[w]['money builds'] += 1
                if chips >= 2000: S[w]['money builds with chips>=2000'] += 1
                if npt <= 1: S[w]['money builds with <=1 paint tower'] += 1
            if typ == 'PAINT_TOWER': S[w]['paint builds'] += 1
            if typ == 'PAINT_TOWER' and npt >= 1 and got2 is None: got2 = r
        second_pt[w].append(got2 if got2 else 9999)
for w in ('us', 'them'):
    print(w, dict(S[w]))
    print('   non-churn build k: type mix', {k: dict(v) for k, v in sorted(ordmix[w].items())})
    print('   round of the first paint tower built while one already stands (9999 = never):', sorted(second_pt[w]), 'med', lib.med(second_pt[w]))

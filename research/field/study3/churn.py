"""Tower self-destruction ('churn'): towers of the top team that vanish without enemy damage. Lifetime, paint at
death, chips, what is rebuilt on the same ruin and how soon, withdrawals from it before death."""
import lib
from collections import Counter, defaultdict
P = defaultdict(list); TEAMS = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    b, d = lib.tower_events(G)
    dmg = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.BOT: dmg[int(a[5])].append(a[0])
    tl = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.TOW: tl[t[1]].append(t)
    wd = defaultdict(list)
    for a in G.acts:
        if a[4] == 'transfer' and int(a[6]) < 0: wd[int(a[5])].append((a[0], -int(a[6])))
    bl = {x[1]: x for x in b}
    selfd = []
    for x in d:
        if x[3] != G.op: continue
        if any(x[0] - 5 <= r <= x[0] for r in dmg[x[1]]): continue
        selfd.append(x)
        T = tl[x[1]]; br = bl[x[1]][0] if x[1] in bl else 0
        life = x[0] - br
        nxt = [y for y in b if y[4:6] == x[4:6] and y[0] >= x[0]]
        reb = (nxt[0][0] - x[0], nxt[0][2][:2]) if nxt else None
        taken = sum(v for r, v in wd[x[1]])
        rec = dict(life=life, paint_last=T[-1][7], chips=lib.money(G, G.op, x[0] - 1), rebuild=reb, taken=taken, r=x[0],
                   paint_max=max(t[7] for t in T), nwd=len(wd[x[1]]))
        TEAMS[G.team_name]['n'].append(1); TEAMS[G.team_name]['rec'].append(rec)
    nb = sum(1 for y in b if y[3] == G.op and y[0] > 0)
    P[G.team_name].append((G.m, G.g, G.map, nb, len(selfd), selfd[0][0] if selfd else None))
for tm, L in P.items():
    print(tm, 'games (m,g,map,builds,self-destroyed,first round):', L)
    R = TEAMS[tm]['rec']
    if not R: continue
    print('   lifetime med', lib.med([r['life'] for r in R]), 'p10/p90', lib.pct([r['life'] for r in R], .1), lib.pct([r['life'] for r in R], .9),
          '| paint at last turn med', lib.med([r['paint_last'] for r in R]), '| max paint ever med', lib.med([r['paint_max'] for r in R]),
          '| paint withdrawn from it med', lib.med([r['taken'] for r in R]), '| withdrawals', lib.med([r['nwd'] for r in R]),
          '| chips at death med', lib.med([r['chips'] for r in R]))
    rb = [r['rebuild'] for r in R]
    print('   rebuilt on same ruin:', sum(1 for x in rb if x), '/', len(rb), 'as', Counter(x[1] for x in rb if x),
          'delay med', lib.med([x[0] for x in rb if x]), '| first examples', [(r['r'], r['life'], r['paint_last'], r['taken'], r['chips'], r['rebuild']) for r in R[:8]])

"""Topic 26: where towers are built.  f = d(own start towers) / (d(own) + d(enemy start towers)); f<0.5 = our half.
Per side: f of builds before r100, and kill rate by r150 for builds with f<0.4, 0.4-0.5, >=0.5."""
import lib
from collections import defaultdict
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    b, d = lib.tower_events(G); dead = {x[1]: x[0] for x in d}
    st = {sd: [(x[4], x[5]) for x in b if x[3] == sd and x[0] == 0] for sd in (1, 2)}
    killed_ids = set()
    for x in d: killed_ids.add(x[1])
    for x in b:
        if x[0] == 0 or x[0] > 120: continue
        sd = x[3]; nm = 'US' if sd == G.us else 'TH'
        do = min(lib.d2((x[4], x[5]), p) for p in st[sd]) ** .5; de = min(lib.d2((x[4], x[5]), p) for p in st[3 - sd]) ** .5
        f = do / (do + de)
        S[nm]['f of builds r1-120'].append(round(f, 2))
        k = 'f<0.4' if f < .4 else ('0.4-0.5' if f < .5 else 'f>=0.5')
        lost = x[1] in dead and dead[x[1]] - x[0] <= 60
        S[nm][f'died within 60 rds | {k}'].append(int(lost))
for nm in ('US', 'TH'):
    print(nm)
    for k, v in sorted(S[nm].items()):
        if k.startswith('f of'): print(f'   {k}: med {lib.med(v)} p75 {lib.pct(v,.75)} share>=0.5 {sum(1 for z in v if z>=.5)}/{len(v)}')
        else: print(f'   {k}: {sum(v)}/{len(v)}')

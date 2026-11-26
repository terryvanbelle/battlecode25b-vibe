"""Topic 15: where the paint sits.  At r50/100/150/200: paint held by towers vs robots (from turns.tsv, last turn
of each unit in that round), towers' mean paint, share of towers with >=300 paint, and robots' mean paint fraction."""
import lib
from collections import defaultdict
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    rt = lib.by_round_turns(G)
    line = []
    for R in (50, 100, 150, 200):
        if R > G.end: break
        for sd in (G.us, G.op):
            nm = 'US' if sd == G.us else 'TH'
            ts = {t[1]: t for t in rt[R] if t[2] == sd}
            tw = [t for t in ts.values() if t[3] in lib.TOW]; rb = [t for t in ts.values() if t[3] in lib.BOT]
            tp = sum(t[7] for t in tw); rp = sum(t[7] for t in rb)
            frac = sum(t[7] / lib.CAP[t[3]] for t in rb) / max(1, len(rb))
            S[nm][f'r{R} tower paint'].append(tp); S[nm][f'r{R} robot paint'].append(rp)
            S[nm][f'r{R} robot fill %'].append(round(100 * frac))
            S[nm][f'r{R} towers >=300 paint'].append(f'{sum(1 for t in tw if t[7] >= 300)}/{len(tw)}')
for nm in ('US', 'TH'):
    print(nm)
    for k, v in S[nm].items():
        print(f'   {k:<24} med {lib.med(v) if not isinstance(v[0], str) else ""}  {v}')

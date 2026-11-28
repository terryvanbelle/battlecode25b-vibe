"""Topic 187 (new): the losses per opponent of the brief (TOP7), from rounds.tsv only: games, how they ended (median end
round; eliminations), and at r100 / r200 / r300 the medians us / them of coverage %, towers, paint towers, chips,
paint held, soldiers, splashers and moppers.  Also the same over our wins against these teams."""
from collections import defaultdict
import lib

KS = (('covpct', 'cov%'), ('tow', 'towers'), ('pt', 'paint t.'), ('money', 'chips'), ('paint', 'paint'), ('sol', 'sold.'),
      ('spl', 'splash.'), ('mop', 'mopp.'))
R = defaultdict(list)
for G in lib.games('all'):
    if G.team_name not in lib.TOP7: continue
    o = {'end': G.end, 'elim': 1 if G.wintype and 'DESTROY' in str(G.wintype).upper() else 0, 'wt': G.wintype}
    for r in (100, 200, 300):
        if G.end < r: continue
        for k, _ in KS: o[(r, k)] = (lib.rv(G, G.us, r, k), lib.rv(G, G.op, r, k))
    R[(G.team_name, 'lost' if G.won_op else 'won')].append(o)
    G.turns = G.acts = None
for res in ('lost', 'won'):
    print(f'\n== {res}, per opponent (medians us / them; a checkpoint counts the games that reached it)')
    for tm in lib.TOP7:
        OS = R.get((tm, res), [])
        if not OS: print(f'  {tm}: none'); continue
        wts = defaultdict(int)
        for o in OS: wts[o['wt']] += 1
        print(f'  {tm}: {len(OS)} games, end median r{lib.med([o["end"] for o in OS])}; ' + ', '.join(f'{k} {v}' for k, v in sorted(wts.items())))
        for r in (100, 200, 300):
            v = [o for o in OS if (r, 'tow') in o]
            if not v: continue
            print(f'     r{r} ({len(v)}): ' + '  '.join(f'{nm} {lib.med([o[(r, k)][0] for o in v])}/{lib.med([o[(r, k)][1] for o in v])}' for k, nm in KS))

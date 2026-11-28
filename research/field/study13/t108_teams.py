"""Topic 108: each strong opponent's signature, our losses next to our wins against the same team.  Per opponent with
at least 3 losses (and lib.TOP), lost and won games separately, medians us / them at r50 / r100 / r200 / r300:
towers (paint towers), robots S / X / M, coverage %, chips; the round of the first tower kill each way; and how
the losses ended.  Reads rounds.tsv and the tower events only."""
import lib
from collections import defaultdict

CK = (50, 100, 200, 300)
by = defaultdict(lambda: {'lost': [], 'won': []})
for G in lib.games('all'):
    b, d = lib.tower_events(G)
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    fk = {s: min([x[0] for x in d if x[3] == s and x[1] in killed] or [None], key=lambda v: v or 9999) for s in (1, 2)}
    row = {'G': lib.lite(G), 'first_kill_on_us': fk[G.us], 'first_kill_on_them': fk[G.op]}
    by[G.team_name]['lost' if G.won_op else 'won'].append(row)


def cell(gs, r, side_of, k):
    v = [lib.rv(x['G'], side_of(x['G']), r, k) for x in gs if x['G'].end >= r]
    return lib.med(v)


for team in sorted(by, key=lambda t: -len(by[t]['lost'])):
    L, Wn = by[team]['lost'], by[team]['won']
    if len(L) < 3 and team not in lib.TOP: continue
    print(f'\n== {team}: we lost {len(L)}, won {len(Wn)}')
    for name, gs in (('lost', L), ('won', Wn)):
        if not gs: continue
        ends = [x['G'].end for x in gs]
        el = sum(1 for x in gs if x['G'].wintype.startswith('ALL'))
        print(f'  {name}: {len(gs)} games, median end r{lib.med(ends)}, eliminations {el}; maps: '
              + ', '.join(f'{x["G"].map}({x["G"].wintype[:3]}{x["G"].end})' for x in gs))
        print(f'     first tower kill on us r{lib.med([x["first_kill_on_us"] for x in gs])}, on them r{lib.med([x["first_kill_on_them"] for x in gs])}'
              f'  (games with a kill on us by r100: {sum(1 for x in gs if x["first_kill_on_us"] and x["first_kill_on_us"] <= 100)},'
              f' on them: {sum(1 for x in gs if x["first_kill_on_them"] and x["first_kill_on_them"] <= 100)})')
        for r in CK:
            n = sum(1 for x in gs if x['G'].end >= r)
            if n == 0: continue
            us = lambda G: G.us; op = lambda G: G.op
            s = []
            for k, lab in (('tow', 'T'), ('pt', 'P'), ('sol', 'S'), ('spl', 'X'), ('mop', 'M'), ('covpct', 'cov'), ('money', '$')):
                s.append(f'{lab} {cell(gs, r, us, k)}/{cell(gs, r, op, k)}')
            print(f'     r{r:<3} ({n:2d}) ' + '  '.join(s))

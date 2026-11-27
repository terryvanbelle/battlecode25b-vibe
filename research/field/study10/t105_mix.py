"""Topic 105: what each side built over the whole game, from summary.json only (no turn data).  Per game: towers built
after the start by type (paint / money / defense; churn rebuilds included, so ours run high), robots spawned by type,
towers and robots standing at the end.  Medians per game and sums, lost vs won games, all opponents and the top teams
(lib.TOP), and per opponent for the losses.  The point: how lopsided our tower mix is next to theirs."""
import json, os
from collections import defaultdict
import lib

rows = []
for m in lib.MAIN:
    d = lib.DUMPS[m]
    for g in range(3):
        if (m, g) in lib.DUP: continue
        p = f'{d}/g{g}.summary.json'
        if not os.path.exists(p): continue
        sm = json.load(open(p))
        us = 'A' if sm['teamA'] == lib.US else 'B'; op = 'B' if us == 'A' else 'A'
        opp = sm['teamB'] if us == 'A' else sm['teamA']
        def side(s):
            sp = sm['spawned' + s]
            return dict(P=sp.get('PAINT_TOWER', 0), M=sp.get('MONEY_TOWER', 0), D=sp.get('DEFENSE_TOWER', 0),
                        S=sp.get('SOLDIER', 0), X=sp.get('SPLASHER', 0), Mo=sp.get('MOPPER', 0),
                        removed=sm['towersRemoved' + s], lost=sm['towersLost' + s], tw=sm['towers' + s], un=sm['units' + s])
        rows.append(dict(m=m, g=g, opp=opp, ver=lib.VER[m], map=sm['map'], lost=sm['winner'] != us, end=sm['rounds'],
                         wt=sm['winType'][:3], us=side(us), op=side(op)))

KEYS = ('P', 'M', 'D', 'removed', 'S', 'X', 'Mo', 'tw', 'un')
LAB = {'P': 'paint towers built', 'M': 'money towers built', 'D': 'defense towers built', 'removed': 'towers disintegrated (churn)',
       'S': 'soldiers spawned', 'X': 'splashers spawned', 'Mo': 'moppers spawned', 'tw': 'towers at the end', 'un': 'robots at the end'}


def table(name, rs):
    if not rs: return
    print(f'\n{name}: {len(rs)} games')
    print(f'   {"":30s} {"median us/them":>15s} {"sum us/them":>13s} {"per 100 rounds us/them":>24s}')
    T = sum(r['end'] for r in rs)
    for k in KEYS:
        a = [r['us'][k] for r in rs]; b = [r['op'][k] for r in rs]
        per = '' if k in ('tw', 'un') else f'{100 * sum(a) / T:5.2f} / {100 * sum(b) / T:5.2f}'
        print(f'   {LAB[k]:30s} {str(lib.med(a)) + " / " + str(lib.med(b)):>15s} {str(sum(a)) + " / " + str(sum(b)):>13s} {per:>24s}')
    # paint-tower share of new towers (churn rebuilds of money towers excluded: one money build per disintegration)
    pa = sum(r['us']['P'] for r in rs); ma = sum(r['us']['M'] - r['us']['removed'] for r in rs)
    pb = sum(r['op']['P'] for r in rs); mb = sum(r['op']['M'] - r['op']['removed'] for r in rs)
    print(f'   paint share of non-churn tower builds: us {100 * pa / max(1, pa + ma):.0f}% ({pa} P / {ma} M), '
          f'them {100 * pb / max(1, pb + mb):.0f}% ({pb} P / {mb} M)')


L = [r for r in rows if r['lost']]; Wn = [r for r in rows if not r['lost']]
table('LOST games, all opponents', L)
table('WON games, all opponents', Wn)
table('LOST games, top teams', [r for r in L if r['opp'] in lib.TOP])
table('WON games, top teams', [r for r in Wn if r['opp'] in lib.TOP])
print('\nper opponent (lost games): paint/money towers built us vs them, splashers+moppers spawned us vs them')
by = defaultdict(list)
for r in L: by[r['opp']].append(r)
for o, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    f = lambda s, k: sum(r[s][k] for r in rs)
    print(f'   {o:26s} {len(rs):2d} lost: towers P/M us {f("us", "P")}/{f("us", "M") - f("us", "removed")} them {f("op", "P")}/{f("op", "M") - f("op", "removed")};'
          f' X+M spawned us {f("us", "X") + f("us", "Mo")} them {f("op", "X") + f("op", "Mo")}; soldiers us {f("us", "S")} them {f("op", "S")}')
print('\nper game (lost):')
for r in L:
    u, o = r['us'], r['op']
    print(f'   m{r["m"]}g{r["g"]} {r["ver"]:5s} {r["opp"][:12]:12s} {r["map"][:14]:14s} {r["wt"]}{r["end"]:<5d} built P/M/D us {u["P"]}/{u["M"]}/{u["D"]} '
          f'(churn {u["removed"]}) them {o["P"]}/{o["M"]}/{o["D"]}; spawned S/X/M us {u["S"]}/{u["X"]}/{u["Mo"]} them {o["S"]}/{o["X"]}/{o["Mo"]}')

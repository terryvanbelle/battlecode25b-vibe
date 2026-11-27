"""Topic 136: who drains our paint towers (t120: robots take 43% of our paint towers' outflow in r101-200 of the losses,
15% of theirs; t130: 4.9 paint withdrawn per paint-tower turn against their 2.7).  Every withdrawal ('transfer' row
by a robot with a negative amount on a tower) is classed by the robot's paint at the end of its previous turn:
'low' (under half its capacity: a refill) or 'half+' (half full or more: a top-up, e.g. Unit.topUp, which fills any
robot beside a tower that holds paint).  Per side, phase (r1-100 / r101-200 / r201-400) and tower kind (paint /
money): paint withdrawn, withdrawals, the share of the paint taken by half+ robots, withdrawals of 10 paint or less,
and the robot types.  Sums over the games, lost and won."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 400))


def analyse(G, S):
    pt = {}
    for t in G.turns:
        if t[3] in lib.BOT: pt[(t[0], t[1])] = t[7]
    for a in G.acts:
        if a[4] != 'transfer' or a[3] not in lib.BOT or a[0] > 400: continue
        try: tgt = int(a[5]); amt = int(a[6])
        except ValueError: continue
        tk = G.typ.get(tgt)
        if amt >= 0 or tk not in lib.TOW: continue
        amt = -amt
        j = next(i for i, (lo, hi) in enumerate(PH) if lo <= max(1, a[0]) <= hi)
        who = 'us' if a[2] == G.us else 'them'
        kind = 'P' if tk == 'PAINT_TOWER' else 'M'
        before = pt.get((a[0] - 1, a[1]))
        cls = 'half+' if before is not None and before * 2 >= lib.CAP[a[3]] else 'low'
        m = S[(who, j, kind)]
        m['paint'] += amt; m['n'] += 1
        m['paint ' + cls] += amt; m['n ' + cls] += 1
        m['tiny'] += amt <= 10
        m['paint ' + a[3][:2]] += amt


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); n = 0
    for G in lib.games(which):
        n += 1
        analyse(G, S)
        lib.lite(G)
    print(f'\n== {which} games ({n}): paint withdrawn from towers by robots (sums)')
    for j, (lo, hi) in enumerate(PH):
        for kind in ('P', 'M'):
            for who in ('us', 'them'):
                m = S[(who, j, kind)]; p = max(1, m['paint'])
                print(f'   r{lo}-{hi} {"paint" if kind == "P" else "money"} towers {who:4s}: {int(m["paint"]):6d} paint in '
                      f'{int(m["n"]):5d} withdrawals; by half+ robots {100 * m["paint half+"] / p:4.1f}% of the paint '
                      f'({int(m["n half+"])} withdrawals), 10 or less: {int(m["tiny"])};  by S/X/M '
                      f'{100 * m["paint SO"] / p:.0f}/{100 * m["paint SP"] / p:.0f}/{100 * m["paint MO"] / p:.0f}%')

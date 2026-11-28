"""Topic 185 (new; follows t183): money towers of level 2+ (they never churn: Tower.turn churns only an L1 money tower)
as refill targets.  Per side, per game: the rounds in r101-300 in which a money tower of level 2+ stands with under 10
paint while the side holds 2000+ chips (for us: the condition under which Unit.refill ignores its dry flag); the
distinct own soldiers and splashers that end a turn adjacent to it in those rounds with under 100 / 150 paint, and
their robot-rounds within Chebyshev 2 of it; split by the starting money tower (startlevel 2) and upgraded ones.
Also our money-tower upgrades to L2 per game and the round of the first."""
from collections import defaultdict
import lib

R0, R1 = 101, 300
LOW = {'SOLDIER': 100, 'SPLASHER': 150}


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def analyse(G):
    lv = {}; start = set(); upg = defaultdict(list)
    for a in G.acts:
        if a[4] == 'startlevel': lv[int(a[5])] = [(0, int(a[6]))]; start.add(int(a[5]))
        elif a[4] == 'upgrade': lv.setdefault(int(a[5]), [(0, 1)]).append((a[0], int(a[6]))); upg[G.team.get(int(a[5]))].append((a[0], G.typ.get(int(a[5]))))

    def level(tid, r):
        v = 1
        for q, l in lv.get(tid, [(0, 1)]):
            if q <= r: v = l
        return v
    mt = defaultdict(dict)   # round -> tower id -> (x, y, team, paint)
    rob = defaultdict(list)
    for t in G.turns:
        if not (R0 <= t[0] <= R1): continue
        if t[3] == 'MONEY_TOWER': mt[t[0]][t[1]] = (t[4], t[5], t[2], t[7])
        elif t[3] in LOW: rob[t[0]].append((t[1], t[4], t[5], t[2], t[7], t[3]))
    out = {}
    for sd, team in (('us', G.us), ('them', G.op)):
        o = defaultdict(float)
        vis = defaultdict(set)
        for r in range(R0, min(R1, G.end) + 1):
            if lib.money(G, team, r - 1) < 2000: continue
            for tid, (x, y, tm, p) in mt.get(r, {}).items():
                if tm != team or p >= 10 or level(tid, r) < 2: continue
                k = 'start' if tid in start else 'upgraded'
                o[k + ' rounds'] += 1
                for (i, rx, ry, rtm, rp, typ) in rob.get(r, []):
                    if rtm != team: continue
                    c = cheb((rx, ry), (x, y))
                    if c <= 2 and rp < LOW[typ]: o[k + ' near'] += 1
                    if c == 1 and rp < LOW[typ]: vis[k].add(i)
        for k in ('start', 'upgraded'): o[k + ' robots'] = len(vis[k])
        ups = sorted(r for r, ty in upg[team] if ty == 'MONEY_TOWER')
        o['mt upgrades'] = len(ups); o['first upgrade'] = ups[0] if ups else None
        out[sd] = o
    return out


def report(tag, OS):
    if not OS: return
    n = len(OS)
    print(f'\n== {tag}: {n} games; r{R0}-{R1}, per game (means); a dead money tower = L2+, under 10 paint, side at 2000+ chips')
    for sd in ('us', 'them'):
        for k in ('start', 'upgraded'):
            print(f'   {sd:4s} {k:9s} money tower: dead-and-churnable-looking rounds {sum(o[sd][k + " rounds"] for o in OS) / n:.0f}, '
                  f'own low robots that came adjacent {sum(o[sd][k + " robots"] for o in OS) / n:.1f}, their robot-rounds within Chebyshev 2 {sum(o[sd][k + " near"] for o in OS) / n:.0f}; '
                  f'games with any such round {sum(1 for o in OS if o[sd][k + " rounds"] > 0)}')
        print(f'   {sd:4s} money-tower upgrades (all rounds) {sum(o[sd]["mt upgrades"] for o in OS) / n:.2f} per game, first at median r{lib.med([o[sd]["first upgrade"] for o in OS])}')


RES = defaultdict(list)
for G in lib.games('all'):
    o = analyse(G)
    RES['lost' if G.won_op else 'won'].append(o)
    RES['ver ' + G.ver].append(o)
    G.turns = G.acts = None
for k in ['lost', 'won'] + sorted(k for k in RES if k.startswith('ver ')): report(k, RES[k])

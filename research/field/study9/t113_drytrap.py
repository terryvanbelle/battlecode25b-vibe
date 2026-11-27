"""Topic 113: the drained money tower trap.  Unit.refill (Unit.java:23) ignores a money tower's dry flag whenever the
team holds >= 2000 chips (churnable()), so a robot below its refill threshold keeps walking to the nearest drained
money tower.  Only an L1 money tower can churn (Tower.java:25); Tower.upgrade (Tower.java:109) upgrades money towers
once chips reach cost + 1200 + 2500, which is exactly when chips sit idle, and an upgraded money tower never regains
paint (RULES 7) and never churns.  Per side, lost and won games:
  - money tower-rounds (r50+) by level, and the share with < 10 paint; the starting money tower is L2 from round 1
  - robot-turns ending within d2 <= 2 of a drained (< 10 paint) money tower of the own side, by the tower's level,
    by robot type, with the side's chips >= 2000 that round, and the share in which the robot gained no paint
  - money tower upgrades (count, first round) and churns (disintegrations of L1 money towers)
  - per lost game: our drained L2/L3 money tower-rounds, robot-turns beside them, upgrades, churns."""
import lib
from collections import Counter, defaultdict


def analyse(G):
    b, d = lib.tower_events(G)
    lvl = {}
    for x in b:
        lvl[x[1]] = 2 if x[0] == 0 else 1     # the starting towers are L2 (RULES 7)
    ups = defaultdict(list)
    churn = Counter()
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    for x in d:
        if x[2] == 'MONEY_TOWER' and x[1] not in killed: churn[x[3]] += 1
    up_by_round = defaultdict(list)
    for a in G.acts:
        if a[4] == 'upgrade':
            tid = int(a[5])
            up_by_round[a[0]].append((tid, int(a[6])))
            if G.typ.get(tid) == 'MONEY_TOWER': ups[G.team.get(tid, a[2])].append(a[0])
    pos = {x[1]: (x[4], x[5]) for x in b}
    c = {1: Counter(), 2: Counter()}
    cur = dict(lvl)
    turns_by_round = defaultdict(list)
    for t in G.turns: turns_by_round[t[0]].append(t)
    prev_paint = {}
    for r in range(1, G.end + 1):
        for (tid, L) in up_by_round.get(r, ()): cur[tid] = L
        T = turns_by_round.get(r, ())
        drained = {1: [], 2: []}
        for t in T:
            if t[3] == 'MONEY_TOWER' and r >= 50:
                L = cur.get(t[1], 1)
                c[t[2]][f'money tower-rounds L{"1" if L == 1 else "2+"}'] += 1
                if t[7] < 10:
                    c[t[2]][f'drained money tower-rounds L{"1" if L == 1 else "2+"}'] += 1
                    drained[t[2]].append(((t[4], t[5]), L))
        for t in T:
            if t[3] not in lib.BOT: continue
            pp = prev_paint.get(t[1]); prev_paint[t[1]] = t[7]
            if r < 50: continue
            s = t[2]
            for (p, L) in drained[s]:
                if lib.d2((t[4], t[5]), p) <= 2:
                    k = 'L1' if L == 1 else 'L2+'
                    rich = lib.money(G, s, r) >= 2000
                    c[s][f'robot-turns beside a drained {k} money tower'] += 1
                    c[s][f'  {t[3][:2]} beside drained {k}'] += 1
                    if rich: c[s][f'  ... with chips >= 2000 ({k})'] += 1
                    if pp is not None and t[7] <= pp: c[s][f'  ... gained no paint ({k})'] += 1
                    break
    for s in (1, 2):
        c[s]['money tower upgrades'] = len(ups[s])
        c[s]['churns (money towers disintegrated)'] = churn[s]
    return c, {s: (min(ups[s]) if ups[s] else None) for s in (1, 2)}


KEYS = ('money tower-rounds L1', 'drained money tower-rounds L1', 'money tower-rounds L2+', 'drained money tower-rounds L2+',
        'robot-turns beside a drained L1 money tower', '  SO beside drained L1', '  SP beside drained L1', '  MO beside drained L1',
        '  ... with chips >= 2000 (L1)', '  ... gained no paint (L1)',
        'robot-turns beside a drained L2+ money tower', '  SO beside drained L2+', '  SP beside drained L2+', '  MO beside drained L2+',
        '  ... with chips >= 2000 (L2+)', '  ... gained no paint (L2+)', 'money tower upgrades', 'churns (money towers disintegrated)')
for which in ('lost', 'won'):
    tot = {'us': Counter(), 'them': Counter()}; n = 0; per = []; fu = {'us': [], 'them': []}
    games_with = {'us': 0, 'them': 0}
    for G in lib.games(which):
        c, first = analyse(G); n += 1
        tot['us'].update(c[G.us]); tot['them'].update(c[G.op])
        fu['us'].append(first[G.us]); fu['them'].append(first[G.op])
        for k, s in (('us', G.us), ('them', G.op)):
            if c[s]['robot-turns beside a drained L2+ money tower'] >= 50: games_with[k] += 1
        if which == 'lost':
            u = c[G.us]
            per.append(f'   m{G.m}g{G.g} {G.ver:5s} {G.team_name[:12]:12s} {G.map[:14]:14s} {G.wintype[:3]}{G.end:<5d} drained L2+ tower-rounds {u["drained money tower-rounds L2+"]:5d}, '
                       f'robot-turns beside them {u["robot-turns beside a drained L2+ money tower"]:5d}; L1 {u["drained money tower-rounds L1"]:5d} / {u["robot-turns beside a drained L1 money tower"]:5d}; '
                       f'upgrades {u["money tower upgrades"]}, churns {u["churns (money towers disintegrated)"]}')
        lib.lite(G)
    print(f'\n== {which.upper()} games: {n}  (sums; r50 on)')
    for k in KEYS: print(f'   {k:46s} us {tot["us"][k]:8d}   them {tot["them"][k]:8d}')
    print(f'   games with >= 50 robot-turns beside a drained L2+ money tower: us {games_with["us"]}, them {games_with["them"]}')
    print(f'   first money tower upgrade, median round: us r{lib.med(fu["us"])} ({sum(1 for v in fu["us"] if v)} games), them r{lib.med(fu["them"])} ({sum(1 for v in fu["them"] if v)} games)')
    if per:
        print('   per lost game (ours):')
        for p in per: print(p)

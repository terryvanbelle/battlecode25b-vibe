"""Topic 44: what moppers do, both sides, lost vs won games.  Per 100 mopper-turns: mop attacks on a robot ('attack'
by a mopper: -10 paint to the target, +5 to the mopper), swings ('mop' rows come in pairs per swing; ids hit),
robots hit per swing, tiles mopped ('unpaint' by a mopper), paint given to allies (positive transfers) and taken
from towers (negative), turns with no action at all.  Where they stand: share of turns within d2<=20 of an own
tower, within cheb 2 of an unbuilt ruin's 5x5 that the side is building (own marks... approximated as a ruin with
no tower), and within d2<=8 of an enemy robot.  Targets of mop attacks/swings by enemy type.  Spawn rounds."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    S = defaultdict(Counter); first = defaultdict(list); per = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        acted = set()
        C = defaultdict(Counter)
        for a in G.acts:
            if a[3] != 'MOPPER': continue
            w = 'us' if a[2] == G.us else 'them'
            acted.add((a[0], a[1]))
            k = a[4]
            if k == 'attack': C[w]['mop-attack on robot'] += 1; C[w]['target ' + G.typ.get(int(a[5]), '?')[:3]] += 1
            elif k == 'mop':
                ids = [int(x) for x in (a[5], a[6], a[7]) if x not in ('', '0')]
                C[w]['swing rows'] += 1; C[w]['robots hit by swings'] += len(ids)
                for i in ids: C[w]['swing target ' + G.typ.get(i, '?')[:3]] += 1
            elif k == 'unpaint': C[w]['tiles mopped'] += 1
            elif k == 'transfer':
                v = int(a[6])
                if v > 0: C[w]['paint given'] += v; C[w]['gives'] += 1
                else: C[w]['paint withdrawn'] -= v
            elif k == 'build': C[w]['towers completed'] += 1
        bt = lib.by_round_turns(G)
        ruins = G.ruins
        for r, ts in bt.items():
            towers = defaultdict(list)
            for t in ts:
                if t[3] in lib.TOW: towers[t[2]].append((t[4], t[5]))
            standing = set(p for v in towers.values() for p in v)
            enemies = defaultdict(list)
            for t in ts:
                if t[3] in lib.BOT: enemies[t[2]].append((t[4], t[5]))
            for t in ts:
                if t[3] != 'MOPPER': continue
                w = 'us' if t[2] == G.us else 'them'
                p = (t[4], t[5])
                C[w]['turns'] += 1
                if (r, t[1]) not in acted: C[w]['turns without action'] += 1
                if any(lib.d2(p, q) <= 20 for q in towers[t[2]]): C[w]['turns near own tower (d2<=20)'] += 1
                if any(max(abs(p[0] - x), abs(p[1] - y)) <= 3 and (x, y) not in standing for (x, y) in ruins): C[w]['turns at an open ruin (cheb<=3)'] += 1
                if any(lib.d2(p, q) <= 8 for q in enemies[3 - t[2]]): C[w]['turns with enemy robot d2<=8'] += 1
        for a in G.acts:
            if a[4] == 'spawn' and a[6] == 'MOPPER':
                w = 'us' if a[2] == G.us else 'them'
                first[(G.m, G.g, w)].append(a[0])
        for w in ('us', 'them'):
            c = C[w]; n = max(1, c['turns'])
            for k in list(c):
                S[w][k] += c[k]
            per[w + ' turns'].append(c['turns'])
            per[w + ' swings/100t'].append(round(100 * c['swing rows'] / 2 / n, 1))
            per[w + ' mop-attacks on robots/100t'].append(round(100 * c['mop-attack on robot'] / n, 1))
            per[w + ' tiles mopped/100t'].append(round(100 * c['tiles mopped'] / n, 1))
    print(f'== {which} games: totals per 100 mopper-turns (sum over games)')
    keys = sorted(set(S['us']) | set(S['them']))
    for k in keys:
        if k == 'turns': continue
        print(f'   {k:36s} us {100 * S["us"][k] / max(1, S["us"]["turns"]):8.1f}   them {100 * S["them"][k] / max(1, S["them"]["turns"]):8.1f}')
    print(f'   mopper-turns                         us {S["us"]["turns"]}  them {S["them"]["turns"]}')
    print('   swings: robots hit per swing         us', round(S['us']['robots hit by swings'] / max(1, S['us']['swing rows'] / 2), 2), ' them', round(S['them']['robots hit by swings'] / max(1, S['them']['swing rows'] / 2), 2))
    for k in ('swings/100t', 'mop-attacks on robots/100t', 'tiles mopped/100t'):
        print(f'   per game median {k:28s} us {lib.med(per["us " + k])}  them {lib.med(per["them " + k])}')
    f_us = [min(v) for (m, g, w), v in first.items() if w == 'us']; f_th = [min(v) for (m, g, w), v in first.items() if w == 'them']
    n2_us = [sum(1 for x in v if x <= 100) for (m, g, w), v in first.items() if w == 'us']
    n2_th = [sum(1 for x in v if x <= 100) for (m, g, w), v in first.items() if w == 'them']
    print(f'   first mopper spawn round: us med {lib.med(f_us)}  them med {lib.med(f_th)};  moppers spawned by r100: us med {lib.med(n2_us)} them med {lib.med(n2_th)}')

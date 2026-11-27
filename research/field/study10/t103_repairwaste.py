"""Topic 103: soldiers that burn paint beside a drained money tower.  Unit.refill makes a soldier wait beside one of
our L1 money towers holding < 10 paint (to churn it) and calls Unit.repairPattern, which attacks the first tile of
the money pattern that is not our right colour using rc.canAttack.  canAttack is true on enemy paint, where a soldier
attack spends 5 paint and paints nothing, and every such 'repair' restarts the wait.  For every soldier turn that ends
within d2 2 of one of the side's money towers with < 10 paint: did the soldier lose 5-7 paint (attack cost plus the
passive drain) with no paint, mark, transfer, srp or attack row of its own that round and no enemy mopper within d2 8?
Both sides (the opponents serve as the control), lost and won games."""
import lib
from collections import defaultdict, Counter


def scan(G):
    acted, attacked, damaged = set(), set(), set()
    for a in G.acts:
        if a[4] in ('paint', 'mark', 'transfer', 'srp', 'build', 'unpaint'): acted.add((a[0], a[1]))
        elif a[4] == 'attack': attacked.add((a[0], a[1]))
        elif a[4] == 'damage': damaged.add((a[0], a[1]))
    rounds = defaultdict(list)
    for t in G.turns: rounds[t[0]].append(t)
    last = {}
    C = defaultdict(Counter)
    eps = defaultdict(set)
    for r in sorted(rounds):
        T = rounds[r]
        towers = [t for t in T if t[3] == 'MONEY_TOWER' and t[7] < 10]
        mops = defaultdict(list)
        for t in T:
            if t[3] == 'MOPPER': mops[t[2]].append((t[4], t[5]))
        for t in T:
            if t[3] != 'SOLDIER': continue
            prev = last.get(t[1]); last[t[1]] = t[7]
            if prev is None: continue
            side = t[2]
            tw = [w for w in towers if w[2] == side and lib.d2((w[4], w[5]), (t[4], t[5])) <= 2]
            if not tw: continue
            key = 'us' if side == G.us else 'them'
            C[key]['turns beside a drained money tower'] += 1
            drop = prev - t[7]
            if (r, t[1]) in acted or (r, t[1]) in damaged:
                C[key]['with an action of its own'] += 1
                continue
            if (r, t[1]) in attacked:
                C[key]['attack row without damage or paint (a blank attack)'] += 1
                eps[key].add((t[1], tw[0][1]))
                continue
            if any(lib.d2(m, (t[4], t[5])) <= 8 for m in mops[3 - side]):
                C[key]['no action, enemy mopper near'] += 1
                continue
            if 5 <= drop <= 7:
                C[key]['no action, paint -5..-7 (a blank attack)'] += 1
                eps[key].add((t[1], tw[0][1]))
            else:
                C[key]['no action, other paint change'] += 1
    return C, eps


for which in ('lost', 'won'):
    tot = defaultdict(Counter); E = Counter(); games = Counter()
    for G in lib.games(which):
        C, eps = scan(G)
        for k in C: tot[k].update(C[k])
        for k in eps:
            E[k] += len(eps[k])
            if eps[k]: games[k] += 1
    print(f'== {which} games')
    for side in ('us', 'them'):
        c = tot[side]
        print(f'   {side}: ' + ', '.join(f'{k} {v}' for k, v in c.most_common()))
        print(f'        (soldier, tower) pairs with a blank attack: {E[side]} in {games[side]} games')
    print()

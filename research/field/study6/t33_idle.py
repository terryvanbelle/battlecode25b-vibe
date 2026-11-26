"""Topic 33: idle robots with paint, and trickle refills.
(a) robot turns adjacent (cheb<=1) to an own tower, per side/type, and the paint the robot held then;
(b) withdrawals (transfer with negative amount) by size: trickle <= 15 paint vs real; robots doing >= 5 trickles
    in a row from the same tower (queueing on a drained tower);
(c) stuck turns (5x5 for 25 turns, as t16) while holding >= 150 paint (splasher/soldier) not adjacent to a tower."""
import lib
from collections import defaultdict, Counter
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    b, d = lib.tower_events(G)
    tpos = defaultdict(set)   # round -> own tower positions per side (approx: towers alive)
    for sd in (G.us, G.op):
        w = 'us' if sd == G.us else 'them'
        alive_cache = {}
        def towers(r):
            k = r // 5
            if k not in alive_cache: alive_cache[k] = [(x[4], x[5]) for x in lib.towers_alive(G, sd, r, b, d)]
            return alive_cache[k]
        tot = Counter(); adj = Counter(); adjfull = Counter()
        pos = defaultdict(list)
        for t in G.turns:
            if t[2] != sd or t[3] not in lib.BOT: continue
            pos[t[1]].append(t); ty = t[3][:2]; tot[ty] += 1
            if any(max(abs(t[4] - x), abs(t[5] - y)) <= 1 for x, y in towers(t[0])):
                adj[ty] += 1
                if t[7] >= lib.CAP[t[3]] // 2: adjfull[ty] += 1
        # withdrawals
        wd = [a for a in G.acts if a[2] == sd and a[4] == 'transfer' and a[3] in lib.BOT and int(a[6]) < 0]
        trick = [a for a in wd if -int(a[6]) <= 15]
        seq = defaultdict(list)
        for a in trick: seq[(a[1], a[5])].append(a[0])
        runs = 0
        for k, rs in seq.items():
            rs.sort(); n = 1
            for i in range(1, len(rs)):
                n = n + 1 if rs[i] - rs[i - 1] <= 2 else 1
                if n == 5: runs += 1
        stuckfull = Counter()
        for i, L in pos.items():
            j = 0
            for k in range(len(L)):
                while max(abs(L[k][4] - L[j][4]), abs(L[k][5] - L[j][5])) > 2 or k - j > 25: j += 1
                if k - j < 25: continue
                t = L[k]
                if t[7] >= 150 and t[3] != 'MOPPER' and not any(max(abs(t[4] - x), abs(t[5] - y)) <= 1 for x, y in towers(t[0])):
                    stuckfull[t[3][:2]] += 1
        for ty in ('SO', 'SP', 'MO'):
            S[w][f'{ty} turns adj own tower %'].append(round(100 * adj[ty] / max(1, tot[ty]), 1))
            S[w][f'{ty} adj with >=half paint %'].append(round(100 * adjfull[ty] / max(1, tot[ty]), 1))
        for ty in ('SO', 'SP'):
            S[w][f'{ty} stuck >=150 paint, away from towers %'].append(round(100 * stuckfull[ty] / max(1, tot[ty]), 1))
        S[w]['withdrawals'].append(len(wd)); S[w]['trickle (<=15) %'].append(round(100 * len(trick) / max(1, len(wd)), 1))
        S[w]['trickle runs of 5+'].append(runs)
        S[w]['mean withdrawal'].append(round(-sum(int(a[6]) for a in wd) / max(1, len(wd)), 1))
for k in S['us']:
    print(f'{k:40s} us med {lib.med(S["us"][k])}  them med {lib.med(S["them"][k])}   us {S["us"][k]}')

"""Topic 16: our robots that stay put.  A robot-turn is 'stuck' if the robot was within a 5x5 box for the last 25 of
its turns.  Classify stuck turns: near an own tower (d2<=9) / near a ruin (cheb<=3) / paint==0 / paint<cost-ish (<40)
/ other; per type.  Both sides for comparison."""
import lib
from collections import defaultdict, Counter
for G in lib.games():
    b, d = lib.tower_events(G)
    out = []
    for sd in (G.us, G.op):
        pos = defaultdict(list)
        for t in G.turns:
            if t[2] == sd and t[3] in lib.BOT: pos[t[1]].append(t)
        C = Counter(); tot = Counter(); ex = []
        for i, L in pos.items():
            j = 0
            for k in range(len(L)):
                tot[L[k][3][:3]] += 1
                while max(abs(L[k][4] - L[j][4]), abs(L[k][5] - L[j][5])) > 2 or k - j > 25: j += 1
                if k - j < 25: continue
                t = L[k]; r = t[0]
                al = lib.towers_alive(G, sd, r, b, d)
                if any(lib.d2((t[4], t[5]), (x[4], x[5])) <= 9 for x in al): c = 'nearOwnTower'
                elif any(max(abs(t[4] - q[0]), abs(t[5] - q[1])) <= 3 for q in G.ruins): c = 'nearRuin'
                elif t[7] == 0: c = 'paint0'
                elif t[7] < 40: c = 'paint<40'
                else: c = 'other'
                C[(t[3][:3], c)] += 1
                if c == 'other' and len(ex) < 4 and (not ex or ex[-1][0] != i): ex.append((i, t[3][:3], r, t[4], t[5], t[7]))
        nm = 'US' if sd == G.us else 'TH'
        out.append(f'  {nm} stuck turns by (type,why): {dict(C.most_common(8))}  of turns {dict(tot)}  other e.g. {ex}')
    print(f'== m{G.m} g{G.g} {G.team_name} {G.map}'); print('\n'.join(out))

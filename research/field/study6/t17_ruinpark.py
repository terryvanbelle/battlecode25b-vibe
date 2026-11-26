"""Topic 17: our soldiers parked at ruins (stuck-in-5x5 for 25 turns, within Chebyshev 3 of a ruin, not near own tower).
State of that ruin then: ENEMY_TOWER (standing enemy tower), or empty with (enemy tiles in 5x5 > 0) / (own pattern
complete-ish >= 20 own tiles and chips < 1000) / other.  Also soldier paint."""
import lib
from collections import defaultdict, Counter
TOT = Counter()
for G in lib.games():
    b, d = lib.tower_events(G)
    W = G.W
    sd = G.us
    pos = defaultdict(list)
    for t in G.turns:
        if t[2] == sd and t[3] == 'SOLDIER': pos[t[1]].append(t)
    want = defaultdict(list)   # round -> list of (turn, ruin)
    for i, L in pos.items():
        j = 0
        for k in range(len(L)):
            while max(abs(L[k][4] - L[j][4]), abs(L[k][5] - L[j][5])) > 2 or k - j > 25: j += 1
            if k - j < 25: continue
            t = L[k]
            q = min(G.ruins, key=lambda q: max(abs(t[4] - q[0]), abs(t[5] - q[1])))
            if max(abs(t[4] - q[0]), abs(t[5] - q[1])) <= 3: want[t[0]].append((t, q))
    C = Counter(); pa = defaultdict(list)
    def hook(a, grid, cur=[0]):
        if a[0] == cur[0]: return
        r = cur[0]; cur[0] = a[0]
        for t, q in want.get(r, []):
            al_us = lib.towers_alive(G, sd, r, b, d); al_th = lib.towers_alive(G, 3 - sd, r, b, d)
            if any((x[4], x[5]) == q for x in al_us): c = 'own tower'
            elif any((x[4], x[5]) == q for x in al_th): c = 'ENEMY tower'
            else:
                en = own = 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx == dy == 0: continue
                        x, y = q[0] + dx, q[1] + dy
                        if not (0 <= x < W and 0 <= y < G.H): continue
                        v = grid[x + y * W]
                        if v and lib.owner(v) != sd: en += 1
                        elif v: own += 1
                ch = lib.money(G, sd, r)
                if en: c = 'empty, enemy paint in 5x5'
                elif own >= 24 and ch < 1000: c = 'empty, pattern painted, chips<1000'
                elif own >= 24: c = 'empty, painted, chips>=1000 (wrong colours?)'
                else: c = f'empty, incomplete (paint<{"40" if t[7] < 40 else "200"})'
            C[c] += 1; pa[c].append(t[7])
    lib.replay_grid(G, hook)
    print(f'm{G.m} g{G.g} {G.map:<13}', dict(C.most_common()), ' paint med', {k: lib.med(v) for k, v in pa.items()})
    TOT.update(C)
print('TOTAL', dict(TOT.most_common()))

"""Topic 4b: SRP / tower-pattern conflicts. For each SRP completion: status of ruins whose 5x5 overlaps the SRP 5x5
(Chebyshev <= 4): op tower standing / unbuilt / ours; and whether the overlapping tiles agree with the tower pattern."""
import lib
from collections import Counter, defaultdict
S = defaultdict(Counter); AG = defaultdict(lambda: [0, 0])
for G in lib.games():
    b, d = lib.tower_events(G)
    for a in G.acts:
        if a[4] != 'srp' or a[2] != G.op: continue
        x, y = map(int, a[5].split(',')); r = a[0]
        alive = {(t[4], t[5]): t for t in lib.towers_alive(G, G.op, r, b, d)}
        aliveu = {(t[4], t[5]) for t in lib.towers_alive(G, G.us, r, b, d)}
        near = [q for q in G.ruins if max(abs(q[0] - x), abs(q[1] - y)) <= 4]
        if not near: S[G.team_name]['no overlapping ruin'] += 1
        for q in near:
            if q in alive:
                S[G.team_name]['overlaps OWN tower'] += 1
                ty = alive[q][2]
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        tx, ty2 = x + dx, y + dy
                        ox, oy = tx - q[0], ty2 - q[1]
                        if max(abs(ox), abs(oy)) <= 2 and (ox or oy):
                            AG[G.team_name][0 if lib.secondary('SRP', dx, dy) == lib.secondary(ty, ox, oy) else 1] += 1
            elif q in aliveu: S[G.team_name]['overlaps OUR tower'] += 1
            else: S[G.team_name]['overlaps UNBUILT ruin'] += 1
for tn in S:
    print(tn, dict(S[tn]), 'overlap tiles agreeing with own tower pattern (agree, disagree):', AG[tn])

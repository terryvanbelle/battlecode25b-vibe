"""Topic 157: why our SRPs disagree with our own money towers (follows t154: 4.3 of our 11.3 SRPs a loss sit beside a
money tower of ours whose pattern disagrees on the shared tiles).  Soldier.pickSrp (t158 Soldier.java:328) rules out a
centre that disagrees with a money tower it KNOWS within Chebyshev 4; Soldier.workSrp (403-416) only asks that a ruin
within Chebyshev 4 hold one of our towers.  So a disagreeing SRP can only come from a pick made before the soldier
knew the tower (not seen, or not built yet), unless the check is broken.
For each of our SRPs with one of our money towers at Chebyshev 3-4 of the centre at completion: does it agree; had
the completing soldier been within r2 20 of the tower's tile by its pick round (the start of its last unbroken stretch
within r2 50 of the centre: SRP_PICK_R2); was the tower already built at the pick.  The soldier's memory is not in the
replay, so 'seen' is the soldier's own sight only (towers learnt from other sources are not counted)."""
from collections import defaultdict, Counter
import lib


def agrees(c, t, kind):
    cx, cy = c
    for x in range(max(cx, t[0]) - 2, min(cx, t[0]) + 3):
        for y in range(max(cy, t[1]) - 2, min(cy, t[1]) + 3):
            if lib.secondary(kind, x - t[0], y - t[1]) != lib.secondary('SRP', x - cx, y - cy): return False
    return True


res = Counter(); ex = []; per_ver = Counter(); per_ver_dis = Counter()
for G in lib.games('all'):
    built, died = lib.tower_events(G)

    def tower_at(q, r):
        for b in built:
            if (b[4], b[5]) == q and b[0] <= r:
                d = [x for x in died if x[1] == b[1]]
                if not d or d[0][0] > r: return (b[2], b[3], b[0])
        return None
    path = defaultdict(list)
    for t in G.turns:
        if t[2] == G.us and t[3] == 'SOLDIER': path[t[1]].append((t[0], t[4], t[5]))
    for a in G.acts:
        if a[4] != 'srp' or a[2] != G.us: continue
        x, y = map(int, a[5].split(',')); c = (x, y)
        for q in G.ruins:
            ch = max(abs(q[0] - x), abs(q[1] - y))
            if not 3 <= ch <= 4: continue
            t = tower_at(q, a[0])
            if not t or t[1] != G.us or t[0] != 'MONEY_TOWER': continue
            ok = agrees(c, q, 'MONEY_TOWER')
            per_ver[G.ver] += 1
            if not ok: per_ver_dis[G.ver] += 1
            P = [p for p in path[a[1]] if p[0] <= a[0]]
            k = len(P) - 1
            while k > 0 and (P[k - 1][1] - x) ** 2 + (P[k - 1][2] - y) ** 2 <= 50: k -= 1
            pick = P[k][0] if P else a[0]
            seen = any((px - q[0]) ** 2 + (py - q[1]) ** 2 <= 20 for (r, px, py) in P if r <= pick)
            res[('agrees' if ok else 'DISAGREES', 'tower seen by the pick' if seen else 'tower NOT seen by the pick',
                 'built before the pick' if t[2] <= pick else 'built after the pick')] += 1
            if not ok and seen and t[2] <= pick and len(ex) < 8: ex.append((G.m, G.g, a[0], a[1], c, q, pick))
print('our SRPs with one of our money towers at Chebyshev 3-4 at completion (an SRP beside two counts twice):')
for v in sorted(per_ver): print(f'   {v}: {per_ver[v]}, of them disagreeing {per_ver_dis[v]} ({100 * per_ver_dis[v] / per_ver[v]:.0f}%)')
for k, v in sorted(res.items()): print(f'   {v:5d}  {k[0]:9s}  {k[1]:28s}  {k[2]}')
print('disagreeing although seen and built before the pick (m, g, round, soldier, centre, tower, pick):')
for e in ex: print('  ', e)

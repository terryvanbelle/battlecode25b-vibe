"""Topic 52: why our killed towers are not rebuilt (lost games; them for comparison).  For each killed tower not
rebuilt by its owner within 50 rounds vs those rebuilt: the owner's soldier-turns within Chebyshev 4 of the ruin in
the 50 rounds after death, the owner's robots alive at death, the owner's chips at death, and enemy tiles in the 5x5
10 and 30 rounds after death (contested ruins are skipped by our Soldier.pickRuin for 50 rounds)."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    D = defaultdict(list); C = Counter()
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        pos = {x[1]: (x[4], x[5]) for x in b}
        builds_at = defaultdict(list)
        for x in b:
            if x[0] > 0: builds_at[(x[4], x[5])].append((x[0], x[3]))
        deaths = [(a[0], int(a[5])) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW]
        want = {}   # round -> list of (tid, tag)
        for (r, tid) in deaths:
            for k in (10, 30): want.setdefault(r + k, []).append((tid, k))
        enemy_at = {}
        def hook(a, grid):
            for (tid, k) in want.pop(a[0], ()):
                p = pos.get(tid); side = G.team.get(tid)
                if p is None: continue
                en = 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        x, y = p[0] + dx, p[1] + dy
                        if (dx or dy) and 0 <= x < G.W and 0 <= y < G.H:
                            o = lib.owner(grid[x + y * G.W])
                            if o and o != side: en += 1
                enemy_at[(tid, k)] = en
        lib.replay_grid(G, hook)
        bt = lib.by_round_turns(G)
        for (r, tid) in deaths:
            side = G.team.get(tid); p = pos.get(tid)
            if p is None: continue
            w = 'us' if side == G.us else 'them'
            nxt = [q for q in builds_at.get(p, ()) if q[0] >= r]
            reb = bool(nxt) and nxt[0][1] == side and nxt[0][0] - r <= 50
            if G.end - r < 50 and not reb: continue          # too close to the end to judge
            tag = (w, 'rebuilt<=50' if reb else 'not rebuilt<=50')
            C[tag] += 1
            near = 0
            for q in range(r, min(G.end, r + 50) + 1):
                for t in bt.get(q, ()):
                    if t[2] == side and t[3] == 'SOLDIER' and max(abs(t[4] - p[0]), abs(t[5] - p[1])) <= 4: near += 1
            D[tag + ('own soldier-turns within 4, next 50r',)].append(near)
            D[tag + ('own robots alive at death',)].append(sum(1 for t in bt.get(r, ()) if t[2] == side and t[3] in lib.BOT))
            D[tag + ('own chips at death',)].append(lib.money(G, side, r))
            for k in (10, 30):
                if (tid, k) in enemy_at: D[tag + (f'enemy tiles in 5x5 at +{k}',)].append(enemy_at[(tid, k)])
    print(f'== {which} games: ' + ', '.join(f'{k[0]} {k[1]}: {v}' for k, v in sorted(C.items())))
    for k in sorted(D):
        v = D[k]
        print(f'   {k[0]:4s} {k[1]:16s} {k[2]:38s} n={len(v):3d} med {lib.med(v)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)}  zero {sum(1 for x in v if x == 0)}')

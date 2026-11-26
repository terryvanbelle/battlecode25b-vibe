"""Topic 23: ground under tower attackers.  For every turn of a robot that damaged an enemy tower that round, the paint
of the tile it ended the turn on (own / empty / tower-owner's), approx. by the grid at round end.  Plus the paint
of the ring of tiles at Chebyshev distance 3-4 around each side's towers at r100 (defensive carpet)."""
import lib
from collections import Counter, defaultdict
C = defaultdict(Counter); RING = defaultdict(Counter)
for G in lib.games():
    W = G.W
    b, d = lib.tower_events(G)
    atk = defaultdict(set)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.BOT:
            tid = int(a[5])
            if G.typ.get(tid) in lib.TOW and G.team.get(tid) != a[2]: atk[a[0]].add(a[1])
    rt = lib.by_round_turns(G)
    def hook(a, grid, cur=[0]):
        if a[0] == cur[0]: return
        r = cur[0]; cur[0] = a[0]
        for t in rt.get(r, []):
            if t[1] in atk.get(r, ()):
                v = grid[t[4] + t[5] * W]; o = lib.owner(v)
                nm = 'US attacker' if t[2] == G.us else 'TH attacker'
                C[nm]['own' if o == t[2] else ('empty' if o == 0 else 'defender')] += 1
        if r == 100:
            for sd in (G.us, G.op):
                nm = 'US towers' if sd == G.us else 'TH towers'
                for x in lib.towers_alive(G, sd, 100, b, d):
                    for dx in range(-4, 5):
                        for dy in range(-4, 5):
                            if max(abs(dx), abs(dy)) < 3: continue
                            X, Y = x[4] + dx, x[5] + dy
                            if 0 <= X < W and 0 <= Y < G.H and (X + Y * W) not in G.walls:
                                o = lib.owner(grid[X + Y * W]); RING[nm]['own' if o == sd else ('empty' if o == 0 else 'enemy')] += 1
    lib.replay_grid(G, hook)
for k, v in C.items():
    n = sum(v.values()); print(k, 'stands on', {a: f'{100*b/n:.0f}%' for a, b in v.items()}, 'n', n)
for k, v in RING.items():
    n = sum(v.values()); print(k, 'ring d3-4 at r100', {a: f'{100*b/n:.0f}%' for a, b in v.items()}, 'n', n)

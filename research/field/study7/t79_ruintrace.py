"""Topic 79: one game's free ruins, one by one.  `t79_ruintrace.py mMgG LO HI` (run.sh: m2749g0 Barcode, r50-r300): for each
ruin with no tower at LO, our soldier-turns that could see it (d2 <= 20), within Chebyshev 2, our marks on it, and its
5x5 tiles (empty / ours / theirs) every 25 rounds."""
import sys
import lib
from collections import defaultdict
want = sys.argv[1] if len(sys.argv) > 3 else 'm2749g0'; lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (50, 300)
for G in lib.games('all'):
    if f'm{G.m}g{G.g}' != want: continue
    b, d = lib.tower_events(G)
    snaps = {}
    def hook(a, grid):
        r = a[0] - 1
        if lo <= r <= hi and r not in snaps:
            s = {}
            for p in G.ruins:
                en = {0: 0, 1: 0, 2: 0}
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        x, y = p[0] + dx, p[1] + dy
                        if (dx or dy) and 0 <= x < G.W and 0 <= y < G.H:
                            en[lib.owner(grid[x + y * G.W]) or 0] += 1
                s[p] = en
            snaps[r] = s
    lib.replay_grid(G, hook)
    vis = defaultdict(list); adj = defaultdict(list)
    for t in G.turns:
        if t[3] == 'SOLDIER' and t[2] == G.us and lo <= t[0] <= hi:
            for p in G.ruins:
                dd = lib.d2((t[4], t[5]), p)
                if dd <= 20: vis[p].append(t[0])
                if max(abs(t[4]-p[0]), abs(t[5]-p[1])) <= 2: adj[p].append(t[0])
    marks = defaultdict(list)
    for a in G.acts:
        if a[4] == 'mark' and a[2] == G.us and lo <= a[0] <= hi:
            x, y = map(int, a[5].split(','))
            for p in G.ruins:
                if max(abs(p[0]-x), abs(p[1]-y)) <= 2: marks[p].append(a[0])
    for p in sorted(G.ruins):
        occ = [ (sd) for sd in (1, 2) for t in lib.towers_alive(G, sd, lo, b, d) if (t[4], t[5]) == p]
        if occ: continue
        st = [snaps[r][p] for r in sorted(snaps)[::25]]
        print(f'ruin {p}: our soldier-turns seeing it {len(vis[p])} (first r{min(vis[p]) if vis[p] else None}), within cheb2 {len(adj[p])}, our marks {len(marks[p])} (first r{min(marks[p]) if marks[p] else None}); tiles (empty/us/them) every 25 rounds: ' +
              ' '.join(f"{s[0]}/{s[G.us]}/{s[G.op]}" for s in st))

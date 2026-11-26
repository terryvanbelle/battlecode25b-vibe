"""Topic 13: our never-built ruin attempts in detail: enemy tiles at first mark, whether the enemy built there later,
soldier-turns we spent within Chebyshev 2 of it during the attempt, and paint we put into it.  Also counts of
completed ruins that had enemy paint during the attempt, and mops spent on them, per side."""
import lib
from collections import defaultdict
S = defaultdict(list)
for G in lib.games():
    W = G.W
    near = lambda x, y: next((r for r in G.ruins if max(abs(r[0] - x), abs(r[1] - y)) <= 2), None)
    first = {}; last = {}
    for a in G.acts:
        if a[4] == 'mark':
            x, y = map(int, a[5].split(',')); r = near(x, y)
            if r: first.setdefault((a[2], r), a[0])
    b, d = lib.tower_events(G)
    bl = defaultdict(list)
    for x in b:
        if x[0] > 0: bl[(x[3], (x[4], x[5]))].append(x[0])
    snap = {}
    want = set((r, k) for (s, r), k in first.items())
    cur = [0]
    def hook(a, grid):
        if (a[0]) != cur[0]:
            cur[0] = a[0]
            for (s, r), k in first.items():
                if k == a[0]:
                    snap[(s, r)] = sum(1 for dx in range(-2, 3) for dy in range(-2, 3)
                                       if 0 <= r[0]+dx < W and 0 <= r[1]+dy < G.H and grid[r[0]+dx+(r[1]+dy)*W] > 0 and lib.owner(grid[r[0]+dx+(r[1]+dy)*W]) != s)
    lib.replay_grid(G, hook)
    tot_sold = sum(1 for t in G.turns if t[2] == G.us and t[3] == 'SOLDIER')
    wasted = 0; npaint = 0; n = 0; taken = 0; contested0 = 0
    for (s, r), f in first.items():
        if s != G.us: continue
        own = [z for z in bl[(s, r)] if z >= f]
        if own: continue
        n += 1
        end = G.end
        # attempt ends when enemy builds there, or 60 rounds after our last mark/paint in the 5x5
        acts = [a[0] for a in G.acts if a[2] == s and a[4] in ('mark', 'paint') and a[0] >= f and near(*map(int, a[5].split(','))) == r]
        end = max(acts) if acts else f
        en = [z for z in bl[(3 - s, r)] if z >= f]
        if en: taken += 1
        if snap.get((s, r), 0) > 0: contested0 += 1
        wasted += sum(1 for t in G.turns if t[2] == s and t[3] == 'SOLDIER' and f <= t[0] <= end and max(abs(t[4]-r[0]), abs(t[5]-r[1])) <= 3)
        npaint += sum(1 for a in G.acts if a[2] == s and a[4] == 'paint' and f <= a[0] <= end and near(*map(int, a[5].split(','))) == r)
    print(f'm{G.m} g{G.g} {G.team_name:<25} {G.map:<13} our failed ruins {n}: enemy paint at first mark {contested0}, later built by enemy {taken}; soldier-turns within 3 of them {wasted} = {100*wasted/max(1,tot_sold):.0f}% of soldier turns; paints into them {npaint}')
    S['failed'].append(n); S['contested at mark'].append(contested0); S['taken by enemy'].append(taken); S['wasted %'].append(round(100*wasted/max(1,tot_sold))); S['paints'].append(npaint)
    for sd in (G.us, G.op):
        c = [(r, f) for (s, r), f in first.items() if s == sd and snap.get((s, r), 0) > 0]
        ok = [(r, f) for (r, f) in c if any(z >= f for z in bl[(sd, r)])]
        S[('US' if sd == G.us else 'TH') + ' ruins marked with enemy paint: built/total'].append(f'{len(ok)}/{len(c)}')
for k, v in S.items(): print(k, v, 'sum', sum(v) if not isinstance(v[0], str) else '')

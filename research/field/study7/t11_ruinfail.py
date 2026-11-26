"""Topic 11: why marked ruins are not completed.  For every ruin a side marked (mark within the 5x5), follow the 24
pattern tiles each round from the first mark: own-painted (any colour), own-correct (matching the marked colours),
enemy-painted, empty.  Report peak correct, enemy tiles at that time, chips while stalled, outcome."""
import lib
from collections import defaultdict
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    W = G.W
    marks = defaultdict(dict)   # (side, ruin) -> {(x,y): sec}
    first = {}
    rr_of = {}
    for a in G.acts:
        if a[4] == 'mark':
            x, y = map(int, a[5].split(','))
            rr = min(G.ruins, key=lambda r: (r[0] - x) ** 2 + (r[1] - y) ** 2)
            if max(abs(rr[0] - x), abs(rr[1] - y)) <= 2:
                marks[(a[2], rr)][(x, y)] = a[6] == '1'; first.setdefault((a[2], rr), a[0])
    b, d = lib.tower_events(G)
    builds = defaultdict(list)
    for x in b:
        if x[0] > 0: builds[(x[3], (x[4], x[5]))].append(x[0])
    # per round snapshots of every ruin 5x5
    snaps = defaultdict(dict)  # ruin -> round -> grid tuple
    cur = [None]
    def hook(a, grid):
        if cur[0] != a[0]:
            if cur[0] is not None:
                for r in G.ruins:
                    snaps[r][cur[0]] = tuple(grid[(r[0] + dx) + (r[1] + dy) * W] if 0 <= r[0] + dx < W and 0 <= r[1] + dy < G.H else -1
                                             for dx in range(-2, 3) for dy in range(-2, 3))
            cur[0] = a[0]
    lib.replay_grid(G, hook)
    print(f'== m{G.m} g{G.g} {G.team_name} {G.map}')
    for (sd, rr), mk in sorted(marks.items(), key=lambda z: first[z[0]]):
        nm = 'US' if sd == G.us else 'TH'
        f = first[(sd, rr)]
        bl = [r for r in builds[(sd, rr)] if r >= f]
        end = bl[0] if bl else G.end
        best = (-1, 0, 0, f); maxen = 0
        mops = sum(1 for a in G.acts if a[4] == 'unpaint' and a[2] == sd and f <= a[0] <= end and max(abs(int(a[5].split(',')[0]) - rr[0]), abs(int(a[5].split(',')[1]) - rr[1])) <= 2)
        for r in range(f, end + 1):
            s = snaps[rr].get(r)
            if not s: continue
            own = enemy = corr = 0
            for k, v in enumerate(s):
                dx, dy = k // 5 - 2, k % 5 - 2
                if dx == 0 and dy == 0: continue
                o = lib.owner(v) if v > 0 else 0
                if o == 0: continue
                if o == sd:
                    own += 1
                    want = mk.get((rr[0] + dx, rr[1] + dy))
                    if want is not None and (v in (2, 4)) == want: corr += 1
                else: enemy += 1
            if corr > best[0]: best = (corr, own, enemy, r)
            maxen = max(maxen, enemy)
        # enemy tiles at end of attempt
        s = snaps[rr].get(min(end, G.end - 1)) or ()
        en_end = sum(1 for k, v in enumerate(s) if k != 12 and v > 0 and lib.owner(v) != sd)
        outcome = f'built r{bl[0]} after {bl[0]-f}' if bl else 'NEVER'
        if nm == 'US' or not bl:
            print(f'  {nm} ruin {rr} marked r{f} ({len(mk)} marks): peak correct {best[0]}/24 at r{best[3]} (enemy tiles then {best[2]}), enemy tiles at end {en_end}, chips@peak {lib.money(G, sd, best[3])}  -> {outcome}')
        if not bl:
            S[nm]['never: peak correct'].append(best[0]); S[nm]['never: enemy tiles at end'].append(en_end)
            S[nm]['never: enemy tiles at peak'].append(best[2])
            S[nm]['never: chips at peak'].append(lib.money(G, sd, best[3]))
        else:
            S[nm]['built: rounds mark->build'].append(bl[0] - f)
            S[nm]['built: max enemy tiles during'].append(maxen)
            S[nm]['built: own mops in 5x5 during'].append(mops)
            S[nm]['built with enemy>0: mops'].append(mops if maxen else None)
        if not bl:
            S[nm]['never: own mops in 5x5'].append(mops)
            S[nm]['never: max enemy tiles'].append(maxen)
print('\n== summary')
for nm in ('US', 'TH'):
    print(' ', nm)
    for k, v in S[nm].items(): print(f'     {k:<30} n={len(v)} med {lib.med(v)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)}')

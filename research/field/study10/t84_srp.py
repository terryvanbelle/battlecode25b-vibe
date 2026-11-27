"""Topic 84: special resource patterns (SRPs), both sides, lost vs won games.  An 'srp' row is a completeResourcePattern
call at a centre.  For each completed SRP, the replayed paint grid tells how long its 25 tiles kept the owner's pattern
(RULES 6.3: any wrong tile at a round start deregisters it; this replay checks after every action, so it may call a
break that was repaired within the round) and what broke it: enemy paint, a tile mopped to empty, or the owner's own
paint in the wrong colour.  Per side: SRPs completed by phase, the share that reached 50 rounds intact (the bonus
starts then), median life, break causes, distance from the centre to the nearest own tower at completion, and the
side's active-SRP count (rounds.tsv) at r150 / r200 / r300 / r400."""
import lib
from collections import defaultdict, Counter

PH = ((1, 150), (151, 300), (301, 2000))
def ph(r):
    return 0 if r <= 150 else 1 if r <= 300 else 2


for which in ('lost', 'won'):
    S = defaultdict(list); C = defaultdict(Counter); n = 0
    for G in lib.games(which):
        n += 1
        W = G.W
        b, d = lib.tower_events(G)
        live = {}     # centre index -> (side, round completed, set of tile indices, wanted colour per tile)
        cnt = Counter()
        grid = list(G.paint0)
        done = []
        def want(cx, cy, x, y):
            return lib.secondary('SRP', x - cx, y - cy)
        for a in G.acts:
            k = a[4]
            if k == 'srp' and a[3] in lib.BOT:
                cx, cy = map(int, a[5].split(','))
                side = 'us' if a[2] == G.us else 'them'
                tiles = {}
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        tiles[(cx + dx) + (cy + dy) * W] = want(cx, cy, cx + dx, cy + dy)
                key = (cx, cy, a[2])
                if key in live: continue
                tw = lib.towers_alive(G, a[2], a[0], b, d)
                dist = min((max(abs(t[4] - cx), abs(t[5] - cy)) for t in tw), default=99)
                live[key] = (side, a[0], tiles, dist)
                C[side]['completed ' + ('r1-150' if a[0] <= 150 else 'r151-300' if a[0] <= 300 else 'r301+')] += 1
                S[(side, 'cheb to own tower')].append(dist)
            elif k in ('paint', 'unpaint'):
                x, y = map(int, a[5].split(',')); i = x + y * W
                if k == 'paint':
                    sec = a[6] == '1'
                    grid[i] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
                else:
                    grid[i] = 0
                # check live SRPs touching this tile
                for key in [kk for kk, v in live.items() if i in v[2]]:
                    side, r0, tiles, dist = live[key]
                    team = key[2]; v = grid[i]
                    ok = v != 0 and lib.owner(v) == (1 if team == 1 else 2) and ((v in (2, 4)) == tiles[i])
                    if ok: continue
                    cause = 'mopped' if k == 'unpaint' else ('enemy paint' if a[2] != team else 'own wrong colour')
                    life = a[0] - r0
                    done.append((side, r0, life, cause))
                    del live[key]
        for key, (side, r0, tiles, dist) in live.items():
            done.append((side, r0, G.end - r0, 'intact at end'))
        for side, r0, life, cause in done:
            C[side]['ended: ' + cause] += 1
            C[side]['reached 50 rounds'] += life >= 50
            C[side]['total'] += 1
            S[(side, 'life')].append(life)
        for side, sd in (('us', G.us), ('them', G.op)):
            for r in (150, 200, 300, 400):
                if G.end >= r: S[(side, f'active r{r}')].append(lib.rv(G, sd, r, 'srp'))
            S[(side, 'completed per game')].append(sum(1 for x in done if x[0] == side))
    print(f'== {which} games ({n})')
    for side in ('us', 'them'):
        print(f'   {side}: {dict(C[side])}')
        print(f'      completed per game med {lib.med(S[(side, "completed per game")])}; life med {lib.med(S[(side, "life")])}; '
              f'Chebyshev from centre to nearest own tower med {lib.med(S[(side, "cheb to own tower")])}; '
              + '; '.join(f'active r{r} med {lib.med(S[(side, f"active r{r}")])}' for r in (150, 200, 300, 400)))
    print()

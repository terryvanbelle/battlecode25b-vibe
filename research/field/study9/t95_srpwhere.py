"""Topic 95: where SRPs are made and where they break, both sides, lost vs won games.  Each completion ('srp' action,
a = centre) is placed by zone: 'home' (nearer the side's own starting towers by more than 15% of the distance between
the two sides' starting towers), 'middle', or 'away'.  Its life comes from the replayed grid: it ends at the first
round start where one of its 25 tiles is not the right colour of the completing side (as t84).  Per side and zone:
completions, share reaching 50 rounds (active), share broken by enemy paint or mops, median life; and the median
Chebyshev distance from the centre to the nearest enemy-painted tile at completion (from the replayed grid, capped
at 8 = none within 8)."""
import lib
from collections import defaultdict, Counter




def srp_events(G):
    b, d = lib.tower_events(G)
    start = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    gap = min(lib.d2(p, q) for p in start[1] for q in start[2]) ** 0.5 if start[1] and start[2] else 1
    W, H = G.W, G.H
    grid = list(G.paint0)
    live = {}      # (side, cx, cy) -> dict
    out = []
    acts = G.acts; ai = 0
    def check(r):
        # round-start check of every live SRP against the grid
        for k in list(live):
            e = live[k]; s, cx, cy = k
            bad = None
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    v = grid[cx + dx + (cy + dy) * W]
                    sec = lib.secondary('SRP', dx, dy)
                    want = (2 if sec else 1) if s == 1 else (4 if sec else 3)
                    if v != want:
                        o = lib.owner(v)
                        bad = 'enemy' if (o != 0 and o != s) else ('mopped' if v == 0 else 'own')
                        break
                if bad: break
            if bad:
                e['life'] = r - e['r0']; e['end'] = bad; out.append(e); del live[k]
    last_r = 0
    for a in acts:
        r = a[0]
        if r != last_r:
            check(r); last_r = r
        k = a[4]
        if k == 'paint':
            x, y = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        elif k == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
        elif k == 'srp':
            cx, cy = map(int, a[5].split(','))
            s = a[2]
            if not start.get(s) or not start.get(3 - s): continue
            p = (cx, cy)
            own = min(lib.d2(p, q) for q in start[s]) ** 0.5; oth = min(lib.d2(p, q) for q in start[3 - s]) ** 0.5
            zone = 'home' if oth - own > 0.15 * gap else ('away' if own - oth > 0.15 * gap else 'middle')
            en = 8
            for dx in range(-8, 9):
                for dy in range(-8, 9):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < W and 0 <= y < H:
                        o = lib.owner(grid[x + y * W])
                        if o != 0 and o != s: en = min(en, max(abs(dx), abs(dy)))
            live[(s, cx, cy)] = dict(side='us' if s == G.us else 'them', zone=zone, r0=r, enemy_cheb=en)
    for k, e in live.items():
        e['life'] = G.end - e['r0']; e['end'] = 'intact'; out.append(e)
    return out


for which in ('lost', 'won'):
    S = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        for e in srp_events(G):
            S[(e['side'], e['zone'])].append(e); S[(e['side'], 'all')].append(e)
    print(f'== {which} games ({n}): SRP completions by zone')
    print('   side zone     done  active(50r)%  broken by enemy paint/mops %  own wrong colour %  life med  enemy tile within (Chebyshev) med')
    for side in ('us', 'them'):
        for z in ('home', 'middle', 'away', 'all'):
            L = S[(side, z)]
            if not L: continue
            c = Counter(e['end'] for e in L)
            print(f'   {side:4s} {z:7s} {len(L):5d}   {100 * sum(e["life"] >= 50 for e in L) / len(L):5.0f}%       '
                  f'{100 * (c["enemy"] + c["mopped"]) / len(L):5.0f}%                      {100 * c["own"] / len(L):5.0f}%         {lib.med([e["life"] for e in L]):5}     {lib.med([e["enemy_cheb"] for e in L])}')
        L = S[(side, 'all')]
        for lab, f in (('enemy paint within 4 at completion', lambda e: e['enemy_cheb'] <= 4), ('none within 4', lambda e: e['enemy_cheb'] > 4)):
            M = [e for e in L if f(e)]
            if M:
                c = Counter(e['end'] for e in M)
                print(f'      {side}: {lab}: {len(M)}, active {100 * sum(e["life"] >= 50 for e in M) / len(M):.0f}%, broken by enemy {100 * (c["enemy"] + c["mopped"]) / len(M):.0f}%')
    print()

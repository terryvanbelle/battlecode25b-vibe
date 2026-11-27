"""Topic 97: who breaks the SRPs.  Replays the grid as t95 and keeps, per tile, the last paint/unpaint action (round,
actor team, actor type, the tile value before it).  At the round-start check where an SRP fails, the first wrong tile
is attributed:
  enemy   - the tile holds enemy paint: by the enemy robot type that painted it
  mopped  - the tile is empty: by the type that unpainted it
  own     - our other colour: by our robot type that painted it, split by what the tile held before that paint
            (our right colour = an overwrite of a good tile; enemy or empty = a repair in the wrong colour after the
            enemy got there first), and by whether the tile lies in the 5x5 of a ruin (tower-pattern work).
Both sides, lost and won games."""
import lib
from collections import defaultdict, Counter


def breaks(G):
    W, H = G.W, G.H
    ruin5 = set()
    for (rx, ry) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3): ruin5.add((rx + dx, ry + dy))
    grid = list(G.paint0)
    last = [None] * (W * H)      # (round, team, type, prev value)
    live = {}
    out = []

    def check(r):
        for k in list(live):
            s, cx, cy = k
            bad = None
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    i = cx + dx + (cy + dy) * W
                    v = grid[i]
                    sec = lib.secondary('SRP', dx, dy)
                    want = (2 if sec else 1) if s == 1 else (4 if sec else 3)
                    if v != want:
                        o = lib.owner(v)
                        kind = 'enemy' if (o != 0 and o != s) else ('mopped' if v == 0 else 'own')
                        L = last[i]
                        who = L[2][:2] if L and isinstance(L[2], str) else '?'
                        prev = '?'
                        if L:
                            po = lib.owner(L[3])
                            pw = L[3] == want
                            prev = 'right' if pw else ('enemy' if (po != 0 and po != s) else ('empty' if L[3] == 0 else 'other'))
                        bad = (kind, who, prev, (cx + dx, cy + dy) in ruin5, r - live[k])
                        break
                if bad: break
            if bad:
                out.append(('us' if s == G.us else 'them',) + bad); del live[k]

    last_r = 0
    for a in G.acts:
        r = a[0]
        if r != last_r:
            check(r); last_r = r
        k = a[4]
        if k == 'paint' or k == 'unpaint':
            x, y = map(int, a[5].split(',')); i = x + y * W
            old = grid[i]
            if k == 'paint':
                sec = a[6] == '1'
                grid[i] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
            else:
                grid[i] = 0
            if grid[i] != old: last[i] = (r, a[2], a[3], old)
        elif k == 'srp':
            cx, cy = map(int, a[5].split(','))
            live[(a[2], cx, cy)] = r
    return out


for which in ('lost', 'won'):
    C = defaultdict(Counter); n = 0; tot = Counter()
    for G in lib.games(which):
        n += 1
        for (side, kind, who, prev, inruin, life) in breaks(G):
            tot[side] += 1
            C[(side, kind)][(who, prev if kind == 'own' else '', inruin if kind == 'own' else '')] += 1
            C[(side, kind, 'n')]['n'] += 1
            if life < 50: C[(side, kind, 'early')]['n'] += 1
    print(f'== {which} games ({n}): SRP breaks (first wrong tile at the failing round-start check)')
    for side in ('us', 'them'):
        print(f'   {side}: {tot[side]} breaks')
        for kind in ('enemy', 'mopped', 'own'):
            m = C[(side, kind, 'n')]['n']
            if not m: continue
            print(f'      {kind:6s} {m:5d} ({100 * m / max(1, tot[side]):.0f}%), before 50 rounds {C[(side, kind, "early")]["n"]}')
            for (who, prev, inruin), c in C[(side, kind)].most_common(8):
                lab = f'by {who}' + (f', tile before: {prev}, in a ruin 5x5: {inruin}' if kind == 'own' else '')
                print(f'          {c:5d}  {lab}')
    print()

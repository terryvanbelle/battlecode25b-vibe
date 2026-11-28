"""Topic 168 (question 2b): did t188's Soldier.colourAt do what it was meant to?  t188 = t186 + colourAt: paintHere and
paintNear paint an empty tile inside a KNOWN own paint/money tower's 5x5 in that pattern's colour (before: always
primary).  Study 14 t154: in our drained-money-tower turns with 2000+ chips the money pattern was intact 17% of the time
(theirs 41%), and own paint in the other colour outside any SRP blocked it in 59% (theirs 24%).
Per version, every game (wins and losses; repeats left out); the paint grid is replayed in file order:
  soldier paints  own soldiers' 'paint' rows on a tile of a standing own paint/money tower's 5x5 (centre excluded):
                  share in the pattern's colour, split by the tile's wanted colour (primary / secondary)
  tower-rounds    every standing own paint/money tower (starting towers too), every round end: the share with the
                  pattern intact, and with at least one own tile in the other colour; tiles of each kind per
                  tower-round (own wrong colour, enemy, empty)
  drained         an own L1 money tower's turn with paint < 10 while we hold 2000+ chips (Tower.turn's churn gate), judged
                  on the grid at that round's end: pattern intact, own other colour on a tile, enemy, empty
  churns          own money towers removed without a kill ('died') and rebuilt on the same tile within 2 rounds, per game
Both sides are counted the same way, so 'them' is the yardstick."""
from collections import defaultdict
import os
import lib

SETS = (('prev', ('t160', 'y316', 'y323')), ('main', ('y328', 't186', 't188')))
RING = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if dx or dy]


def analyse(G, S):
    W, H = G.W, G.H
    built, died = lib.tower_events(G)
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    level = {}
    for a in G.acts:
        if a[4] == 'startlevel': level[int(a[5])] = [(0, int(a[6]))]
        elif a[4] == 'build': level[int(a[5])] = [(a[0], 1)]
        elif a[4] == 'upgrade': level.setdefault(int(a[5]), []).append((a[0], int(a[6])))

    def lvl(i, r):
        L = 1
        for rr, l in level.get(i, ()):
            if rr <= r: L = l
        return L
    life = []   # (tid, type, team, x, y, r0, r1)
    for (r, tid, ty, team, x, y) in built:
        if ty not in ('PAINT_TOWER', 'MONEY_TOWER') or not (2 <= x < W - 2 and 2 <= y < H - 2): continue
        end = min([d[0] for d in died if d[1] == tid] or [G.end + 1])
        life.append((tid, ty, team, x, y, r, end))
    tile_tw = defaultdict(list)
    for L in life:
        for dx, dy in RING: tile_tw[(L[3] + dx, L[4] + dy)].append(L)
    drained = defaultdict(list)   # round -> [(tid, team, x, y)]
    for t in G.turns:
        if t[3] == 'MONEY_TOWER' and t[7] < 10 and lvl(t[1], t[0]) == 1 and lib.money(G, t[2], t[0]) >= 2000:
            drained[t[0]].append((t[1], t[2], t[4], t[5]))
    cur = [0]

    def want(ty, team, dx, dy):
        sec = lib.secondary(ty, dx, dy)
        return (2 if sec else 1) if team == 1 else (4 if sec else 3)

    def classify(grid, ty, team, x, y):
        ow = en = em = 0
        for dx, dy in RING:
            g = grid[(x + dx) + (y + dy) * W]
            if g == want(ty, team, dx, dy): continue
            if g == 0: em += 1
            elif lib.owner(g) == team: ow += 1
            else: en += 1
        return ow, en, em

    def end_of_round(r, grid):
        for (tid, ty, team, x, y, r0, r1) in life:
            if not (r0 <= r < r1): continue
            sd = 'us' if team == G.us else 'them'
            ow, en, em = classify(grid, ty, team, x, y)
            k = (sd, ty)
            S[k, 'tr'] += 1
            S[k, 'intact'] += (ow + en + em) == 0
            S[k, 'ownwrong_any'] += ow > 0
            S[k, 'ownwrong_only'] += ow > 0 and en == 0 and em == 0
            S[k, 'ow'] += ow; S[k, 'en'] += en; S[k, 'em'] += em
        for (tid, team, x, y) in drained.get(r, ()):
            if not (2 <= x < W - 2 and 2 <= y < H - 2): continue
            sd = 'us' if team == G.us else 'them'
            ow, en, em = classify(grid, 'MONEY_TOWER', team, x, y)
            S[sd, 'dr'] += 1
            S[sd, 'dr_intact'] += (ow + en + em) == 0
            S[sd, 'dr_own'] += ow > 0
            S[sd, 'dr_ownonly'] += ow > 0 and en == 0 and em == 0
            S[sd, 'dr_enemy'] += en > 0
            S[sd, 'dr_empty'] += em > 0

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0], a[0]):
                if r >= 1: end_of_round(r, grid)
            cur[0] = a[0]
        if a[4] == 'paint' and a[3] == 'SOLDIER':
            x, y = map(int, a[5].split(','))
            for (tid, ty, team, tx, tyy, r0, r1) in tile_tw.get((x, y), ()):
                if team != a[2] or not (r0 <= a[0] < r1): continue
                sd = 'us' if team == G.us else 'them'
                dx, dy = x - tx, y - tyy
                sec = lib.secondary(ty, dx, dy)
                prev = grid[x + y * W]
                k = (sd, 'sp', 'sec' if sec else 'pri', 'empty' if prev == 0 else 'own')
                S[k] += 1
                if (a[6] == '1') == sec: S[k + ('right',)] += 1
    grid = lib.replay_grid(G, hook)
    for r in range(cur[0], G.end + 1):
        if r >= 1: end_of_round(r, grid)
    pos2 = pos
    bl = [(a[0], a[2], pos2.get(int(a[5]))) for a in G.acts if a[4] == 'build']
    for a in G.acts:
        if a[4] == 'died' and a[3] == 'MONEY_TOWER':
            q = pos2.get(a[1]); side = a[2]
            if q and any(b[1] == side and b[2] == q and 0 <= b[0] - a[0] <= 2 for b in bl):
                S['us' if side == G.us else 'them', 'churn'] += 1
    S['games'] += 1


def show(tag, S):
    ng = max(1, S['games'])
    lines = []
    for sd in ('us', 'them'):
        sp = []
        for wc in ('pri', 'sec'):
            for pv in ('empty', 'own'):
                n = S[sd, 'sp', wc, pv]
                sp.append(f'{wc}/{pv} {n / ng:5.1f}/g {100 * S[sd, "sp", wc, pv, "right"] / max(1, n):3.0f}%')
        lines.append(f'  {tag:18s} {sd:4s} {int(S["games"]):3d} g  soldier paints on own pattern tiles (wanted/before, per game, right colour): ' + '  '.join(sp))
        for ty in ('MONEY_TOWER', 'PAINT_TOWER'):
            k = (sd, ty); tr = max(1, S[k, 'tr'])
            lines.append(f'  {"":18s} {"":4s}        {ty[:5].lower()} tower-rounds {S[k, "tr"] / ng:6.0f}/g  intact {100 * S[k, "intact"] / tr:3.0f}%  '
                         f'own other colour on a tile {100 * S[k, "ownwrong_any"] / tr:3.0f}% (the only fault {100 * S[k, "ownwrong_only"] / tr:3.0f}%)  '
                         f'tiles per tower-round: own wrong {S[k, "ow"] / tr:4.2f}, enemy {S[k, "en"] / tr:4.2f}, empty {S[k, "em"] / tr:4.2f}')
        dr = max(1, S[sd, 'dr'])
        lines.append(f'  {"":18s} {"":4s}        drained money turns (2000+ chips) {S[sd, "dr"] / ng:5.1f}/g: intact {100 * S[sd, "dr_intact"] / dr:3.0f}%  '
                     f'own other colour {100 * S[sd, "dr_own"] / dr:3.0f}% (only fault {100 * S[sd, "dr_ownonly"] / dr:3.0f}%)  enemy {100 * S[sd, "dr_enemy"] / dr:3.0f}%  '
                     f'empty {100 * S[sd, "dr_empty"] / dr:3.0f}%;  churns {S[sd, "churn"] / ng:4.2f}/g')
    return '\n'.join(lines)


ALL = {}
for st, vers in SETS:
    os.environ['S15SET'] = st
    for v in vers:
        for which in ('all', 'lost', 'won'):
            S = defaultdict(int)
            for G in lib.games(which, vers=[v]):
                analyse(G, S)
            ALL[v, which] = S
os.environ.pop('S15SET', None)
for which in ('all', 'lost', 'won'):
    print(f'\n== {which}')
    for v in ('t160', 'y316', 'y323', 'y328', 't186', 't188'):
        print(show(v, ALL[v, which]))

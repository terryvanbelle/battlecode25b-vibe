"""Topic 146: before r101, when one of our soldiers walks (moved this turn), is the tile it ends on already its own
paint, painted by itself this turn, neutral or enemy?  Split: walking near a free ruin (Chebyshev 3) or elsewhere,
and by round band r1-50 / r51-80 / r81-100 (our soldiers paint no cover before r80, Soldier.java:34-36).  Also the
share of walk turns with a paint row on another tile, and the mean paint held.  Replay as t145."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
NB = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
CL = ('ruin', 'siege', 'tower', 'walk', 'still')
CTX = ('tower zone', 'splash', 'low paint', 'other')


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def disk(r2):
    k = int(r2 ** 0.5)
    return [(dx, dy) for dx in range(-k, k + 1) for dy in range(-k, k + 1) if dx * dx + dy * dy <= r2]


D16, D2, D36 = disk(16), disk(2), disk(36)


def run(G, S):
    W = G.W
    grid = list(G.paint0)
    acts = defaultdict(list)
    for a in G.acts: acts[(a[0], a[1])].append(a)
    tpos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in tpos: tpos[t[1]] = (t[4], t[5], t[2])
    near_ruin = defaultdict(list)
    for (rx, ry) in G.ruins:
        for dx in range(-3, 4):
            for dy in range(-3, 4): near_ruin[(rx + dx, ry + dy)].append((rx, ry))
    zone = {k: {1: defaultdict(int), 2: defaultdict(int)} for k in (2, 16, 36)}
    occ = {}; pos = {}; towers = {}
    lastpos = {}; hit = {}; trail = {}; spl = {}

    def tz(i, x, y, team, d):
        for k, D in ((2, D2), (16, D16), (36, D36)):
            Z = zone[k][team]
            for dx, dy in D: Z[(x + dx, y + dy)] += d

    def place(i, team, x, y, tower):
        old = pos.get(i)
        if old is not None and occ.get(old, (None,))[0] == i: del occ[old]
        pos[i] = (x, y); occ[(x, y)] = (i, team, tower)
        if tower and i not in towers: towers[i] = (x, y, team); tz(i, x, y, team, 1)

    def remove(i):
        old = pos.pop(i, None)
        if old is not None and occ.get(old, (None,))[0] == i: del occ[old]
        if i in towers:
            x, y, team = towers.pop(i); tz(i, x, y, team, -1)

    def apply(a):
        k = a[4]
        if k == 'paint':
            x, y = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        elif k == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
        elif k == 'spawn':
            i = int(a[5]); x, y = map(int, a[7].split(',')); place(i, a[2], x, y, a[6] in lib.TOW)
        elif k == 'build':
            q = tpos.get(int(a[5]))
            if q: place(int(a[5]), q[2], q[0], q[1], True)
        elif k in ('die', 'died'):
            remove(int(a[5]))

    turn_keys = set((t[0], t[1]) for t in G.turns)
    pending = defaultdict(list)
    for k, L in acts.items():
        if k not in turn_keys: pending[k[0]].extend(L)
    cur = None
    for t in G.turns:
        r, i, team, typ, x, y, hp, paint = t
        if r > 100: break
        if cur is not None and r != cur:
            for a in pending.get(cur, ()): apply(a)
        cur = r
        L = acts.get((r, i), ())
        before_owner = lib.owner(grid[x + y * W])
        for a in L: apply(a)
        if typ in lib.TOW:
            if i not in pos: place(i, team, x, y, True)
            continue
        place(i, team, x, y, False)
        if r > 100 or typ != 'SOLDIER':
            lastpos[i] = (x, y)
            continue
        moved = lastpos.get(i) not in (None, (x, y))
        lastpos[i] = (x, y)
        side = 'us' if team == G.us else 'them'
        if not moved: continue
        free_ruin = any(rn not in occ for rn in near_ruin.get((x, y), ()))
        band = 0 if r <= 50 else 1 if r <= 80 else 2
        o_after = lib.owner(grid[x + y * W])
        o_before = before_owner
        own_rows = [a for a in L if a[4] == 'paint']
        under = any(a[5] == f'{x},{y}' for a in own_rows)
        k = ('ruin' if free_ruin else 'walk', side, band)
        D = S[k]; D['n'] += 1
        if o_before == team: D['already own'] += 1
        elif under and o_after == team: D['painted under'] += 1
        elif o_after == 0: D['neutral'] += 1
        else: D['enemy'] += 1
        if any(a[5] != f'{x},{y}' for a in own_rows): D['painted elsewhere'] += 1
        D['paint'] += paint


BANDS = ('r1-50', 'r51-80', 'r81-100')
for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); ng = 0
    for G in lib.games(which):
        run(G, S); ng += 1
    print(f'== {which} games: {ng}; soldier walk turns: % already own / painted under / neutral / enemy, % painting another tile, mean paint')
    for cls in ('walk', 'ruin'):
        for b in range(3):
            for side in ('us', 'them'):
                D = S[(cls, side, b)]; n = D['n']
                if not n: continue
                print(f'   {cls:4s} {BANDS[b]:8s} {side:4s} {int(n):6d}  own {100*D["already own"]/n:5.1f}  under {100*D["painted under"]/n:5.1f}  neutral {100*D["neutral"]/n:5.1f}  enemy {100*D["enemy"]/n:5.1f}   elsewhere {100*D["painted elsewhere"]/n:5.1f}   paint {D["paint"]/n:5.1f}')

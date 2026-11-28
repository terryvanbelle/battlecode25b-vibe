"""Topic 145: what our robots are doing when they stand on unpainted or enemy ground, or beside allies (follows t140),
and in what situation our splashers step back and forth (follows t141).
Same replay as t140 (turn order, live positions, the robot's own paint rows applied first).  Every soldier- and
splasher-turn is put in the first matching class:
  ruin       within Chebyshev 3 of a free ruin (no tower on it): working it, or walking past it
  siege      the robot hit an enemy tower this turn or last turn, or stands within r2 16 of a living enemy tower
  tower      within r2 2 of an own tower (refill, churn waits)
  walk       moved this turn
  still      everything else (did not move)
and per class: the share of robot-turns, the share on own / neutral / enemy paint, the share with 1+ allies within
r2 2, and the end-of-turn paint loss per 100 turns of the class (uncapped).  Per side and phase (r1-100 / r101-200 /
r201+), losses then wins.
Splashers: moves and A-B-A reversals (back on the tile of two turns before) by context, first match: 'tower zone'
(an enemy tower within r2 36, where Splasher.standOff works), 'splash' (splashed this turn or last), 'low paint'
(under 50: cannot splash), 'other'."""
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
        if cur is not None and r != cur:
            for a in pending.get(cur, ()): apply(a)
        cur = r
        L = acts.get((r, i), ())
        for a in L: apply(a)
        if typ in lib.TOW:
            if i not in pos: place(i, team, x, y, True)
            continue
        place(i, team, x, y, False)
        p = ph(r)
        moved = lastpos.get(i) not in (None, (x, y))
        hist = trail.setdefault(i, [])
        rev = moved and len(hist) >= 2 and hist[-1][0] == r - 1 and hist[-2][0] == r - 2 and hist[-2][1] == (x, y)
        hist.append((r, (x, y)))
        if len(hist) > 2: hist.pop(0)
        lastpos[i] = (x, y)
        h = any(a[4] == 'attack' and G.typ.get(int(a[5])) in lib.TOW for a in L)
        prev_hit = hit.get(i) == r - 1
        if h: hit[i] = r
        if any(a[4] in ('die', 'died') and a[5] == str(i) for a in L): remove(i)
        if p is None or typ == 'MOPPER': continue
        side = 'us' if team == G.us else 'them'
        enemy = 3 - team
        if typ == 'SPLASHER':
            sp = any(a[4] == 'splash' for a in L); last_sp = spl.get(i) == r - 1
            if sp: spl[i] = r
            ctx = 'tower zone' if zone[36][enemy].get((x, y), 0) > 0 else 'splash' if (sp or last_sp) else 'low paint' if paint < 50 else 'other'
            R = S[(side, 'SPLREV', p, ctx)]
            R['turns'] += 1
            if moved: R['moves'] += 1
            if rev: R['rev'] += 1
        c = None
        for rn in near_ruin.get((x, y), ()):
            if rn not in occ: c = 'ruin'; break
        if c is None and (h or prev_hit or zone[16][enemy].get((x, y), 0) > 0): c = 'siege'
        if c is None and zone[2][team].get((x, y), 0) > 0: c = 'tower'
        if c is None: c = 'walk' if moved else 'still'
        o = lib.owner(grid[x + y * W])
        kind = 'own' if o == team else 'neutral' if o == 0 else 'enemy'
        allies = 0
        for dx, dy in NB:
            q = occ.get((x + dx, y + dy))
            if q is not None and q[1] == team and q[0] != i: allies += 1
        base = 0 if kind == 'own' else 1 if kind == 'neutral' else 2
        pen = base + (2 * allies if kind == 'enemy' else allies)
        D = S[(side, typ, p, c)]
        D['n'] += 1; D[kind] += 1; D['pen'] += pen
        if allies: D['crowd'] += 1
        S[(side, typ, p, 'all')]['n'] += 1


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); ng = 0
    for G in lib.games(which):
        run(G, S); ng += 1
    print(f'== {which} games: {ng}')
    for typ in ('SOLDIER', 'SPLASHER'):
        print(f'  {typ}: class: share of turns (on own / neutral / enemy %, 1+ allies %, paint lost to the rule per 100 turns)')
        for p in range(3):
            for side in ('us', 'them'):
                tot = S[(side, typ, p, 'all')]['n']
                if not tot: continue
                cells = []
                for c in CL:
                    D = S[(side, typ, p, c)]; n = D['n']
                    if not n: cells.append(f'{c} 0%'); continue
                    cells.append(f'{c} {100 * n / tot:4.1f}% ({100 * D["own"] / n:3.0f}/{100 * D["neutral"] / n:3.0f}/{100 * D["enemy"] / n:3.0f}, {100 * D["crowd"] / n:3.0f}%, {100 * D["pen"] / n:5.1f})')
                print(f'     {PHN[p]:9s} {side:4s} {int(tot):7d}t  ' + ' | '.join(cells))
    print('  SPLASHER by context: share of splasher-turns | moves per 100 turns | A-B-A reversals per 100 moves')
    for p in range(3):
        for side in ('us', 'them'):
            tot = sum(S[(side, 'SPLREV', p, c)]['turns'] for c in CTX)
            if not tot: continue
            cells = []
            for c in CTX:
                R = S[(side, 'SPLREV', p, c)]
                cells.append(f'{c} {100 * R["turns"] / tot:4.1f}% | {100 * R["moves"] / max(1, R["turns"]):4.1f} | {100 * R["rev"] / max(1, R["moves"]):4.1f}')
            print(f'     {PHN[p]:9s} {side:4s} ' + '   '.join(cells))

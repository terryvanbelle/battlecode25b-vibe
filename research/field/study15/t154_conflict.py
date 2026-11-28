"""Topic 154: our SRPs against our own tower patterns (follows t152: our own soldiers' paint is a top breaker of our
SRPs).  Soldier.pickSrp rules out a centre whose 5x5 disagrees with a KNOWN money tower within Chebyshev 4
(Pattern.agreesWithMoney), but Soldier.workSrp only asks that a ruin within Chebyshev 4 hold one of our towers, so a
money tower first seen after the pick is painted over; paint towers are never checked.  Churn.repairPattern then
repaints the money pattern (to churn the tower) and breaks the SRP, and an SRP soldier repaints the SRP...
Per side, every SRP completion is classed by the own towers standing within Chebyshev 3-4 of its centre at that
moment: a money tower whose pattern disagrees on the shared tiles, a paint tower that disagrees, only agreeing towers,
no tower.  Per class: completions per game; share broken by own paint (the first wrong-making row in the round before
the failed check is ours); median rounds active.
Churn (study 3 tactic 4: a drained L1 money tower disintegrates and the robot beside it re-completes it for a fresh
500 paint): churns per game (an own money tower 'died' and an own build on the same ruin within 2 rounds); and the
drained rounds (an own L1 money tower's turn with paint < 10 while the team holds 2000+ chips: Tower.turn's churn
gate), with the share in which its money pattern was intact (Churn.towerTurn's check) and the share in which an own
registered SRP held one of its tiles in the other colour.
The replay rules are t152's (SRP checks at round start, the grid after the previous round)."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3)]
RING = [o for o in OFFS if o != (0, 0)]
CLS = ('money disagrees', 'paint disagrees (no money)', 'agreeing towers only', 'no own tower in 3-4')


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def agrees(c, t, kind):
    cx, cy = c
    for x in range(max(cx, t[0]) - 2, min(cx, t[0]) + 3):
        for y in range(max(cy, t[1]) - 2, min(cy, t[1]) + 3):
            if lib.secondary(kind, x - t[0], y - t[1]) != lib.secondary('SRP', x - cx, y - cy): return False
    return True


def val(side, sec):
    return (2 if sec else 1) if side == 1 else (4 if sec else 3)


def analyse(G, S, P):
    W, H = G.W, G.H
    built, died = lib.tower_events(G)
    alive_by_pos = {}

    def tower_at(q, r):
        for b in built:
            if (b[4], b[5]) == q and b[0] <= r:
                d = [x for x in died if x[1] == b[1]]
                if not d or d[0][0] > r: return b
        return None
    # tower turns: (round, id, team, type, x, y, paint)
    tturns = defaultdict(list)
    level = {}
    for a in G.acts:
        if a[4] == 'startlevel': level[int(a[5])] = [(0, int(a[6]))]
        elif a[4] == 'build': level[int(a[5])] = [(a[0], 1)]
        elif a[4] == 'upgrade': level.setdefault(int(a[5]), []).append((a[0], int(a[6])))
    for t in G.turns:
        if t[3] == 'MONEY_TOWER': tturns[t[0]].append(t)
    srps = []
    by_tile = defaultdict(list)
    cur = [0]

    def lvl(i, r):
        L = 1
        for rr, l in level.get(i, ()):
            if rr <= r: L = l
        return L

    def start_of_round(r, grid):
        for s in srps:
            if s['end'] is not None or s['r0'] >= r: continue
            cx, cy = s['c']
            if all(grid[(cx + dx) + (cy + dy) * W] == val(s['side'], lib.secondary('SRP', dx, dy)) for dx, dy in OFFS):
                s['life'] += 1
                if s['life'] == 50: s['act'] = r
            else:
                s['end'] = r
                bad = set((cx + dx) + (cy + dy) * W for dx, dy in OFFS
                          if grid[(cx + dx) + (cy + dy) * W] != val(s['side'], lib.secondary('SRP', dx, dy)))
                why = [w for w in s['wr'] if w[0] == r - 1 and w[1] in bad]
                s['own'] = bool(why) and why[-1][2]
            s['wr'] = [w for w in s['wr'] if w[0] >= r - 1]
        # drained money towers (turn rows of round r-1, judged on the grid after round r-1)
        for t in tturns.get(r - 1, ()):
            side = t[2]
            if t[7] >= 10 or lvl(t[1], r - 1) != 1 or lib.money(G, side, r - 1) < 2000: continue
            D = S[('us' if side == G.us else 'them', ph(r - 1))]
            D['drained'] += 1
            x, y = t[4], t[5]
            intact = True; srp_bad = False; enemy = empty = other = 0
            for dx, dy in RING:
                xx, yy = x + dx, y + dy
                if not (0 <= xx < W and 0 <= yy < H): intact = False; continue
                g = grid[xx + yy * W]
                if g != val(side, lib.secondary('MONEY_TOWER', dx, dy)):
                    intact = False
                    held = False
                    for k in by_tile.get(xx + yy * W, ()):
                        s = srps[k]
                        if s['side'] == side and s['end'] is None and g == val(side, lib.secondary('SRP', xx - s['c'][0], yy - s['c'][1])):
                            srp_bad = True; held = True
                    if g == 0: empty += 1
                    elif lib.owner(g) != side: enemy += 1
                    elif not held: other += 1
            if intact: D['drained_intact'] += 1
            if srp_bad: D['drained_srp'] += 1
            if enemy: D['drained_enemy'] += 1
            if empty: D['drained_empty'] += 1
            if other: D['drained_other'] += 1
            if srp_bad and not (enemy or empty or other): D['drained_srp_only'] += 1

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0] + 1, a[0] + 1):
                if r >= 1: start_of_round(r, grid)
            cur[0] = a[0]
        k = a[4]
        if k == 'srp':
            x, y = map(int, a[5].split(',')); side = a[2]
            tags = set()
            for q in G.ruins:
                ch = max(abs(q[0] - x), abs(q[1] - y))
                if not 3 <= ch <= 4: continue
                b = tower_at(q, a[0])
                if not b or b[3] != side or b[2] not in ('MONEY_TOWER', 'PAINT_TOWER'): continue
                tags.add((b[2], agrees((x, y), q, b[2])))
            if ('MONEY_TOWER', False) in tags: cl = CLS[0]
            elif ('PAINT_TOWER', False) in tags: cl = CLS[1]
            elif tags: cl = CLS[2]
            else: cl = CLS[3]
            srps.append(dict(side=side, c=(x, y), r0=a[0], life=0, end=None, act=None, wr=[], own=False, cl=cl))
            for dx, dy in OFFS: by_tile[(x + dx) + (y + dy) * W].append(len(srps) - 1)
        elif k in ('paint', 'unpaint'):
            x, y = map(int, a[5].split(',')); i = x + y * W
            nv = val(a[2], a[6] == '1') if k == 'paint' else 0
            for j in by_tile.get(i, ()):
                s = srps[j]
                if s['end'] is not None: continue
                if nv != val(s['side'], lib.secondary('SRP', x - s['c'][0], y - s['c'][1])):
                    s['wr'].append((a[0], i, a[2] == s['side']))

    grid = lib.replay_grid(G, hook)
    for r in range(cur[0] + 1, G.end + 1): start_of_round(r, grid)
    # churns: an own money tower disintegrated ('died') and an own build on its ruin within 2 rounds
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    bl = [(a[0], a[2], pos.get(int(a[5]))) for a in G.acts if a[4] == 'build']
    for a in G.acts:
        if a[4] == 'died' and a[3] == 'MONEY_TOWER':
            q = pos.get(a[1]); side = a[2]
            if q and any(b[1] == side and b[2] == q and 0 <= b[0] - a[0] <= 2 for b in bl):
                S[('us' if side == G.us else 'them', ph(a[0]))]['churn'] += 1
    for s in srps:
        side = 'us' if s['side'] == G.us else 'them'
        D = S[(side, ph(s['r0']))]
        D['n'] += 1; D['n_' + s['cl']] += 1
        if s['end'] is not None and s['own']: D['own_' + s['cl']] += 1
        if s['end'] is not None: D['broke_' + s['cl']] += 1
        paid = ((s['end'] if s['end'] is not None else G.end + 1) - s['act']) if s['act'] else 0
        D['paid_' + s['cl']] += paid
        D['paid'] += paid
    P['games'] += 1


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); P = defaultdict(int)
    for G in lib.games(which):
        analyse(G, S, P)
    ng = P['games']
    print(f'\n== {which}: {ng} games; SRPs by the phase of completion, churns and drained money towers by the phase of the round')
    print(f'   {"":56s}' + ''.join(f'{PHN[p] + " us":>14s}{"them":>8s}' for p in range(3)) + f'{"all us":>14s}{"them":>8s}')

    def row(name, f):
        cells = ''
        for p in list(range(3)) + ['all']:
            for side in ('us', 'them'):
                if p == 'all':
                    D = defaultdict(float)
                    for q in range(3):
                        for k, v in S[(side, q)].items(): D[k] += v
                else: D = S[(side, p)]
                try: s = f(D)
                except ZeroDivisionError: s = '-'
                cells += f'{s:>14s}' if side == 'us' else f'{s:>8s}'
        print(f'   {name:56s}' + cells)
    row('SRPs completed per game', lambda D: f'{D["n"] / ng:.2f}')
    for c in CLS:
        row(f'  {c}: per game', lambda D, c=c: f'{D["n_" + c] / ng:.2f}')
        row(f'    broken by own paint', lambda D, c=c: f'{100 * D["own_" + c] / D["n_" + c]:.0f}%')
        row(f'    broken (any cause)', lambda D, c=c: f'{100 * D["broke_" + c] / D["n_" + c]:.0f}%')
        row(f'    rounds active per SRP', lambda D, c=c: f'{D["paid_" + c] / D["n_" + c]:.0f}')
    row('SRP-rounds active per game (all SRPs)', lambda D: f'{D["paid"] / ng:.0f}')
    row('churns per game', lambda D: f'{D["churn"] / ng:.2f}')
    row('drained L1 money tower turns (chips 2000+) per game', lambda D: f'{D["drained"] / ng:.1f}')
    row('  money pattern intact (churnable)', lambda D: f'{100 * D["drained_intact"] / D["drained"]:.0f}%')
    row('  a tile held by an own SRP in the other colour', lambda D: f'{100 * D["drained_srp"] / D["drained"]:.0f}%')
    row('    and nothing else wrong (the SRP alone blocks the churn)', lambda D: f'{100 * D["drained_srp_only"] / D["drained"]:.0f}%')
    row('  a tile with enemy paint', lambda D: f'{100 * D["drained_enemy"] / D["drained"]:.0f}%')
    row('  an empty tile (mopped, or never painted)', lambda D: f'{100 * D["drained_empty"] / D["drained"]:.0f}%')
    row('  own paint in the other colour, no SRP', lambda D: f'{100 * D["drained_other"] / D["drained"]:.0f}%')

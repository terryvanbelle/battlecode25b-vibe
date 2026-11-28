"""Topic 150: what happens to a ruin after its tower is killed (follows t149: they rebuild 77-86% of their killed
towers' ruins in our losses, we 27-58%).  Every tower killed by damage ('die' row; churn disintegrations are left out).
The paint grid is replayed (lib.replay_grid) so the ruin's 5x5 is known at the death and at every later round end.
Per side whose tower fell, phase of the death, losses then wins:
  rebuilt     the same side completes a tower on the ruin again (any type) before the game ends; median delay; the
              unit that completed it (soldier / mopper / splasher); same type as before
  taken       the killers complete a tower there
  vacant      neither, to the end of the game (and the rounds it stayed vacant)
  at death    tiles of the dead tower's pattern still right (of 24), enemy tiles (from the dead side's view) in the 5x5,
              the dead side's chips, own robots within r2 8 of the ruin
  after       share of the vacant rounds (up to 100 after the death) in which the 5x5 holds enemy paint (our
              Pattern.contested is true: Soldier.pickRuin skips the ruin for 50 rounds), and in which the pattern is
              still 20+ / 24 right; median rounds until the 5x5 is free of enemy paint
Per game counts are means over the games of the set."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if dx or dy]


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def analyse(G, S, P):
    W = G.W
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    builds = defaultdict(list)   # (x, y) -> [(round, side, type, builder type)]
    for a in G.acts:
        if a[4] == 'build':
            q = pos.get(int(a[5]))
            if q: builds[q].append((a[0], a[2], a[6], a[3]))
    robots = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.BOT: robots[t[0]].append((t[2], t[4], t[5]))
    deaths = []   # (round, x, y, side, type)
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.TOW:
            v = int(a[5]); q = pos.get(v); s = G.team.get(v)
            if q and s: deaths.append((a[0], q[0], q[1], s, a[7]))
    if not deaths: P['games'] += 1; return
    watch = {}   # index -> state
    by_round = defaultdict(list)
    for k, d in enumerate(deaths): by_round[d[0]].append(k)
    cur = [0]

    def snapshot(grid, d):
        r, x, y, s, ty = d
        pat = ty
        right = enemy = 0
        for dx, dy in OFFS:
            xx, yy = x + dx, y + dy
            if not (0 <= xx < W and 0 <= yy < G.H): continue
            v = grid[xx + yy * W]
            o = lib.owner(v)
            if o != 0 and o != s: enemy += 1
            elif o == s and ((v in (2, 4)) == lib.secondary(pat, dx, dy)): right += 1
        return right, enemy

    def end_of_round(r, grid):
        for k in by_round.get(r, ()):
            d = deaths[k]
            right, enemy = snapshot(grid, d)
            near = sum(1 for (tm, xx, yy) in robots.get(r, ()) if tm == d[3] and (xx - d[1]) ** 2 + (yy - d[2]) ** 2 <= 8)
            watch[k] = dict(right0=right, enemy0=enemy, chips=lib.money(G, d[3], r), near=near, rounds=0, contested=0,
                            intact=0, clear_at=None)
        for k, w in list(watch.items()):
            d = deaths[k]
            if r <= d[0] or w.get('done'): continue
            nxt = [b for b in builds.get((d[1], d[2]), ()) if b[0] > d[0]]
            if (nxt and nxt[0][0] <= r) or r - d[0] > 100:
                w['done'] = True; continue
            right, enemy = snapshot(grid, d)
            w['rounds'] += 1
            if enemy: w['contested'] += 1
            elif w['clear_at'] is None: w['clear_at'] = r - d[0]
            if right >= 20: w['intact'] += 1

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0], a[0]):
                if r >= 1: end_of_round(r, grid)
            cur[0] = a[0]

    grid = lib.replay_grid(G, hook)
    for r in range(cur[0], G.end + 1): end_of_round(r, grid)
    for k, d in enumerate(deaths):
        p = ph(d[0])
        side = 'us' if d[3] == G.us else 'them'
        D = S[(side, p)]
        w = watch.get(k, {})
        D['n'] += 1
        nxt = [b for b in builds.get((d[1], d[2]), ()) if b[0] > d[0]]
        if nxt and nxt[0][1] == d[3]:
            D['rebuilt'] += 1; D['delays'].append(nxt[0][0] - d[0])
            D['by_' + nxt[0][3]] += 1
            if nxt[0][2] == d[4]: D['same_type'] += 1
        elif nxt:
            D['taken'] += 1; D['tdelays'].append(nxt[0][0] - d[0])
        else:
            D['vacant'] += 1; D['vac_rounds'].append(G.end - d[0])
        D['right0'].append(w.get('right0')); D['enemy0'].append(w.get('enemy0')); D['chips'].append(w.get('chips'))
        D['near'].append(w.get('near'))
        if w.get('rounds'):
            D['w_rounds'] += w['rounds']; D['w_contested'] += w['contested']; D['w_intact'] += w['intact']
            D['clear'].append(w['clear_at'] if w['clear_at'] is not None else 101)
    P['games'] += 1


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(lambda: 0)); P = defaultdict(int)
    for k in ('delays', 'tdelays', 'vac_rounds', 'right0', 'enemy0', 'chips', 'near', 'clear'):
        pass
    S = defaultdict(lambda: defaultdict(float))
    for G in lib.games(which):
        for key in [(s, p) for s in ('us', 'them') for p in range(3)]:
            for k in ('delays', 'tdelays', 'vac_rounds', 'right0', 'enemy0', 'chips', 'near', 'clear'):
                if k not in S[key]: S[key][k] = []
        analyse(G, S, P)
    print(f'\n== {which}: {P["games"]} games; towers killed by damage, by the side that lost them and the phase of the death')
    print(f'   {"":44s}' + ''.join(f'{PHN[p] + " us":>14s}{"them":>8s}' for p in range(3)))
    rows = (('n', 'killed (per game)'), ('rebuilt', 'rebuilt by the same side'), ('delays', '  median delay, rounds'),
            ('by_SOLDIER', '  completed by a soldier'), ('by_MOPPER', '  by a mopper'), ('by_SPLASHER', '  by a splasher'),
            ('same_type', '  same type as before'), ('taken', 'taken by the killers'), ('tdelays', '  median delay'),
            ('vacant', 'vacant to the end'), ('vac_rounds', '  median rounds vacant'),
            ('right0', 'at death: pattern tiles right (of 24)'), ('enemy0', 'at death: enemy tiles in the 5x5'),
            ('chips', 'at death: chips'), ('near', 'at death: own robots within r2 8'),
            ('w_contested', 'vacant rounds with enemy paint in the 5x5'), ('w_intact', 'vacant rounds with 20+ tiles right'),
            ('clear', 'rounds until the 5x5 is clear (101 = never)'))
    for k, name in rows:
        cells = ''
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, p)]
                n = D['n'] if isinstance(D['n'], float) else 0
                if k == 'n': s = f'{n / max(1, P["games"]):.2f}'
                elif k in ('delays', 'tdelays', 'vac_rounds', 'right0', 'enemy0', 'chips', 'near', 'clear'): s = f'{lib.med(D[k])}'
                elif k in ('w_contested', 'w_intact'): s = f'{100 * D[k] / max(1, D["w_rounds"]):.0f}%'
                else: s = f'{100 * D[k] / max(1, n):.0f}%'
                cells += f'{s:>14s}' if side == 'us' else f'{s:>8s}'
        print(f'   {name:44s}' + cells)

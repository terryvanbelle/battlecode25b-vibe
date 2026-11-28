"""Topic 159: could the fallen tower have been rebuilt at once?  (follows t150: at the death the dead tower's pattern
is still intact, 24 of 24 tiles in r1-200, yet we rebuild 61 / 52% of those ruins and they 91 / 91%.)
RULES 4.7: completeTowerPattern needs a robot of the side within d2 2 of the ruin, 1000 chips and the 24 tiles in the
pattern's colours; no paint, no cooldown.  In y328 two code paths complete a tower:
  Churn.rebuild (every robot, after its turn): money towers only (canCompleteTowerPattern(LEVEL_ONE_MONEY_TOWER)),
      with 1000+ chips (Tune.REBUILD_CHIPS);
  Soldier.workRuin: a soldier that picked the ruin (Soldier.pickRuin: no robot on it, not contested, not marked bad,
      helper rules) completes ruinType, which comes from the ruin's marks (Pattern.readMarks) or, with no mark,
      from wantType().  The starting towers were never marked.
Every tower killed by damage ('die' row), both sides.  The paint grid and each side's marks are replayed in file
order; robot positions are the end-of-turn rows.  From the death round until the side rebuilds there, the killers take
it, 100 rounds pass or the game ends, at each round end:
  intact      every tile of the dead tower's pattern in the side's colours (exactly right)
  adjacent    a robot of the side within d2 2 of the ruin at the end of its turn that round
  chips       the side's chips at the end of the previous round >= 1000 (completing happens mid-round)
  ready       all three
Per side and phase of the death, losses then wins:
  ready ever / first ready round (after the death) / rebuilt within 1 round of the first ready round ('at once') /
  ready rounds before the rebuild ('missed') / never ready, and why (never adjacent while intact, never 1000 chips
  while intact and adjacent, pattern broken before any own robot came)
  own paint on a right tile: rows of the side's own paint that turned a right tile of the dead pattern wrong, between
      the death and the rebuild (a soldier repainting the ruin for another type), per death
  marks: what readMarks would say from the side's marks in the 5x5 at the death: same type / other type / no mark;
      and the rebuild rate of each class
  by type: paint / money towers, and starting towers (id < 10000) against built ones"""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if dx or dy]
PATS = ('PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER')


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def read_marks(marks, x, y):
    """Pattern.readMarks over a dict (x, y) -> secondary: the type with the fewest disagreements, ties paint < money <
    defense; None when nothing is marked."""
    dis = [0, 0, 0]; n = 0
    for dx, dy in OFFS:
        m = marks.get((x + dx, y + dy))
        if m is None: continue
        n += 1
        for i, p in enumerate(PATS):
            if lib.secondary(p, dx, dy) != m: dis[i] += 1
    if n == 0: return None
    if dis[0] <= dis[1] and dis[0] <= dis[2]: return PATS[0]
    return PATS[1] if dis[1] <= dis[2] else PATS[2]


def analyse(G, S):
    W, H = G.W, G.H
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    builds = defaultdict(list)
    for a in G.acts:
        if a[4] == 'build':
            q = pos.get(int(a[5]))
            if q: builds[q].append((a[0], a[2], a[6], a[3]))
    robots = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.BOT: robots[t[0]].append((t[2], t[4], t[5], t[3]))
    deaths = []
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.TOW:
            v = int(a[5]); q = pos.get(v); s = G.team.get(v)
            if q and s: deaths.append(dict(r=a[0], x=q[0], y=q[1], s=s, ty=a[7], start=v < 10000))
    if not deaths: return
    marks = {1: {}, 2: {}}
    by_round = defaultdict(list)
    for d in deaths: by_round[d['r']].append(d)
    live = []
    cur = [0]

    def right_count(grid, d):
        n = 0
        for dx, dy in OFFS:
            xx, yy = d['x'] + dx, d['y'] + dy
            if not (0 <= xx < W and 0 <= yy < H): return -1
            v = grid[xx + yy * W]
            if lib.owner(v) == d['s'] and (v in (2, 4)) == lib.secondary(d['ty'], dx, dy): n += 1
        return n

    def end_of_round(r, grid):
        for d in by_round.get(r, ()):
            d['marks'] = read_marks(marks[d['s']], d['x'], d['y'])
            nxt = [b for b in builds.get((d['x'], d['y']), ()) if b[0] >= d['r']]
            d['next'] = nxt[0] if nxt else None
            d['ready'] = []; d['why'] = set(); d['selfbreak'] = 0; d['intact_rounds'] = 0
            live.append(d)
        for d in list(live):
            nb = d['next']
            if (nb and nb[0] <= r) or r - d['r'] > 100:
                live.remove(d); continue
            rc = right_count(grid, d)
            intact = rc == 24
            adj = [ty for (tm, xx, yy, ty) in robots.get(r, ()) if tm == d['s'] and (xx - d['x']) ** 2 + (yy - d['y']) ** 2 <= 2]
            chips = lib.money(G, d['s'], r - 1) >= 1000
            if intact:
                d['intact_rounds'] += 1
                if adj and chips: d['ready'].append((r, tuple(adj)))
                elif adj: d['why'].add('adj_no_chips')
                else: d['why'].add('intact_not_adj')

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0], a[0]):
                if r >= 1: end_of_round(r, grid)
            cur[0] = a[0]
        k = a[4]
        if k == 'mark':
            x, y = map(int, a[5].split(',')); marks[a[2]][(x, y)] = a[6] == '1'
        elif k == 'unmark':
            x, y = map(int, a[5].split(',')); marks[a[2]].pop((x, y), None)
        elif k == 'paint' and live:
            x, y = map(int, a[5].split(','))
            for d in live:
                dx, dy = x - d['x'], y - d['y']
                if a[2] != d['s'] or max(abs(dx), abs(dy)) > 2 or (dx == 0 and dy == 0) or a[0] <= d['r']: continue
                v = grid[x + y * W]
                was_right = lib.owner(v) == d['s'] and (v in (2, 4)) == lib.secondary(d['ty'], dx, dy)
                if was_right and (a[6] == '1') != lib.secondary(d['ty'], dx, dy): d['selfbreak'] += 1

    grid = lib.replay_grid(G, hook)
    for r in range(cur[0], G.end + 1): end_of_round(r, grid)
    for d in deaths:
        side = 'us' if d['s'] == G.us else 'them'
        p = ph(d['r'])
        for key in ((side, p), (side, 'all'), (side, d['ty'] + (' start' if d['start'] else ' built'))):
            D = S[key]
            for k in ('first_ready', 'missed', 'selfbreak'): D.setdefault(k, [])
            D['n'] += 1
            nb = d.get('next')
            reb = nb is not None and nb[1] == d['s']
            if reb: D['rebuilt'] += 1
            elif nb is not None: D['taken'] += 1
            rd = d.get('ready', [])
            if rd:
                D['ready'] += 1
                D['first_ready'].append(rd[0][0] - d['r'])
                if reb and nb[0] - rd[0][0] <= 1: D['at_once'] += 1
                D['missed'].append(len([x for x in rd if not reb or x[0] < nb[0] - 1]))
                for (r, adj) in rd[:1]:
                    for ty in set(adj): D['adj_' + ty] += 1
            else:
                w = d.get('why', set())
                if d.get('intact_rounds', 0) == 0: D['never_intact'] += 1
                elif 'adj_no_chips' in w: D['no_chips'] += 1
                else: D['never_adj'] += 1
            D['selfbreak'].append(d.get('selfbreak', 0))
            mk = d.get('marks')
            c = 'nomark' if mk is None else ('same' if mk == d['ty'] else 'other')
            D['mk_' + c] += 1
            if reb: D['mkreb_' + c] += 1


ROWS = (
    ('killed (towers)', lambda D: f"{int(D['n'])}"),
    ('rebuilt by the same side', lambda D: f"{100 * D['rebuilt'] / max(1, D['n']):.0f}%"),
    ('taken by the killers', lambda D: f"{100 * D['taken'] / max(1, D['n']):.0f}%"),
    ('ready at some round (intact+adj+chips)', lambda D: f"{100 * D['ready'] / max(1, D['n']):.0f}%"),
    ('  first ready, rounds after death (med)', lambda D: f"{lib.med(D['first_ready'])}"),
    ('  rebuilt at once (<= 1 round of it)', lambda D: f"{100 * D['at_once'] / max(1, D['ready']):.0f}%"),
    ('  ready rounds missed (mean)', lambda D: f"{lib.mean(D['missed'])}"),
    ('  first ready: a soldier adjacent', lambda D: f"{100 * D['adj_SOLDIER'] / max(1, D['ready']):.0f}%"),
    ('  first ready: a mopper adjacent', lambda D: f"{100 * D['adj_MOPPER'] / max(1, D['ready']):.0f}%"),
    ('  first ready: a splasher adjacent', lambda D: f"{100 * D['adj_SPLASHER'] / max(1, D['ready']):.0f}%"),
    ('never ready: broken before any robot', lambda D: f"{100 * D['never_intact'] / max(1, D['n']):.0f}%"),
    ('never ready: intact, never adjacent', lambda D: f"{100 * D['never_adj'] / max(1, D['n']):.0f}%"),
    ('never ready: adjacent, no 1000 chips', lambda D: f"{100 * D['no_chips'] / max(1, D['n']):.0f}%"),
    ('own paint turning a right tile wrong', lambda D: f"{lib.mean(D['selfbreak'])}"),
    ('marks say the same type', lambda D: f"{100 * D['mk_same'] / max(1, D['n']):.0f}% (reb {100 * D['mkreb_same'] / max(1, D['mk_same']):.0f}%)"),
    ('marks say another type', lambda D: f"{100 * D['mk_other'] / max(1, D['n']):.0f}% (reb {100 * D['mkreb_other'] / max(1, D['mk_other']):.0f}%)"),
    ('no mark in the 5x5', lambda D: f"{100 * D['mk_nomark'] / max(1, D['n']):.0f}% (reb {100 * D['mkreb_nomark'] / max(1, D['mk_nomark']):.0f}%)"),
)

for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(int))
    ng = 0
    for G in lib.games(which):
        ng += 1
        analyse(G, S)
    print(f'\n== {which}: {ng} games; towers killed by damage, by the side that lost them')
    cols = [('us', 0), ('them', 0), ('us', 1), ('them', 1), ('us', 2), ('them', 2), ('us', 'all'), ('them', 'all')]
    print(f'{"":42s}' + ''.join(f'{(PHN[p] if p != "all" else "all") + " " + s:>14s}' for s, p in cols))
    for name, f in ROWS:
        print(f'{name:42s}' + ''.join(f'{f(S[c]) if S[c]["n"] else "-":>14s}' for c in cols))
    print('  by tower type and origin (all phases)')
    keys = sorted(k for k in S if isinstance(k[1], str) and k[1] != 'all')
    print(f'{"":42s}' + ''.join(f'{k[0] + " " + k[1].replace("_TOWER", "").lower():>20s}' for k in keys))
    for name, f in ROWS:
        print(f'{name:42s}' + ''.join(f'{f(S[k]):>20s}' for k in keys))

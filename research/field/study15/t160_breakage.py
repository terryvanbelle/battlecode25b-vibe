"""Topic 160: the race at a fallen tower (follows t159: in our losses 75% of our killed towers' patterns are broken
before any robot of ours stands beside the ruin, theirs 43%).  Every tower killed by damage ('die' row), both sides.
The paint grid is replayed in file order; robot positions are the end-of-turn rows.
For each death, from the death round on (until the side rebuilds there, the killers take it, 100 rounds, or the end):
  break       the first paint change that turns a tile of the dead tower's pattern wrong: rounds after the death,
              and by what: an enemy mopper's mop (unpaint), an enemy splash, an enemy soldier's paint, own paint
  first adj   the first round end with a robot of the side within d2 2 of the ruin (completing needs that)
  first near  the first round end with a robot of the side within d2 8 (the 5x5 in paint reach)
  race        an own robot was adjacent before the break (or no break), with 1000+ chips then
At the death: pattern intact, chips >= 1000, own robots within d2 2 / 8 / 20 (the 'guard' a rule could post), enemy
robots within d2 20, and the side's robots in d2 20 during the 10 rounds before the death (mean per round).
Before the death (the assault): the rounds from the tower's first damage of its final assault (hits with gaps under
15 rounds) to the death, and whether a robot of the side stood within d2 2 of the tower at any round end in it.
Per side and phase of the death, losses then wins."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if dx or dy]


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def analyse(G, S):
    W, H = G.W, G.H
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    builds = defaultdict(list)
    for a in G.acts:
        if a[4] == 'build':
            q = pos.get(int(a[5]))
            if q: builds[q].append((a[0], a[2]))
    robots = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.BOT: robots[t[0]].append((t[2], t[4], t[5], t[3]))
    # damage to towers: tower id -> rounds hit
    hits = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage':
            v = int(a[5])
            if G.typ.get(v) in lib.TOW: hits[v].append(a[0])
    deaths = []
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.TOW:
            v = int(a[5]); q = pos.get(v); s = G.team.get(v)
            if not (q and s): continue
            hs = sorted(h for h in hits.get(v, ()) if h <= a[0])
            start = a[0]
            for h in reversed(hs):
                if start - h < 15: start = h
                else: break
            nb = [b for b in builds.get(q, ()) if b[0] >= a[0]]
            deaths.append(dict(r=a[0], x=q[0], y=q[1], s=s, ty=a[7], start=start, nb=nb[0] if nb else None))
    if not deaths: return
    by_round = defaultdict(list)
    for d in deaths: by_round[d['r']].append(d)
    live = []
    cur = [0]

    def intact(grid, d):
        for dx, dy in OFFS:
            xx, yy = d['x'] + dx, d['y'] + dy
            if not (0 <= xx < W and 0 <= yy < H): return False
            v = grid[xx + yy * W]
            if not (lib.owner(v) == d['s'] and (v in (2, 4)) == lib.secondary(d['ty'], dx, dy)): return False
        return True

    def near(r, d, r2):
        return sum(1 for (tm, xx, yy, ty) in robots.get(r, ()) if tm == d['s'] and (xx - d['x']) ** 2 + (yy - d['y']) ** 2 <= r2)

    def end_of_round(r, grid):
        for d in by_round.get(r, ()):
            d['intact0'] = intact(grid, d)
            d['chips0'] = lib.money(G, d['s'], r) >= 1000
            d['n2'], d['n8'], d['n20'] = near(r, d, 2), near(r, d, 8), near(r, d, 20)
            d['e20'] = sum(1 for (tm, xx, yy, ty) in robots.get(r, ()) if tm != d['s'] and (xx - d['x']) ** 2 + (yy - d['y']) ** 2 <= 20)
            d['pre20'] = sum(near(rr, d, 20) for rr in range(max(1, r - 10), r)) / 10
            d['guard'] = any(near(rr, d, 2) for rr in range(d['start'], r + 1))
            d['assault'] = r - d['start']
            d['adj'] = r if d['n2'] else None
            d['near'] = r if d['n8'] else None
            d['brk'] = None if d['intact0'] else (r, 'before')
            live.append(d)
        for d in list(live):
            nb = d['nb']
            if (nb and nb[0] <= r) or r - d['r'] > 100:
                live.remove(d); continue
            if r > d['r']:
                if d['adj'] is None and near(r, d, 2): d['adj'] = r; d['adj_chips'] = lib.money(G, d['s'], r - 1) >= 1000
                if d['near'] is None and near(r, d, 8): d['near'] = r

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0], a[0]):
                if r >= 1: end_of_round(r, grid)
            cur[0] = a[0]
        k = a[4]
        if (k == 'paint' or k == 'unpaint') and live:
            x, y = map(int, a[5].split(','))
            for d in live:
                if d['brk'] is not None or a[0] < d['r']: continue
                dx, dy = x - d['x'], y - d['y']
                if max(abs(dx), abs(dy)) > 2 or (dx == 0 and dy == 0): continue
                v = grid[x + y * W]
                if not (lib.owner(v) == d['s'] and (v in (2, 4)) == lib.secondary(d['ty'], dx, dy)): continue
                if k == 'unpaint': cause = 'enemy mop' if a[2] != d['s'] else 'own mop'
                elif a[2] == d['s']:
                    if (a[6] == '1') == lib.secondary(d['ty'], dx, dy): continue
                    cause = 'own paint'
                else: cause = 'enemy splash' if a[3] == 'SPLASHER' else 'enemy soldier'
                d['brk'] = (a[0], cause)

    grid = lib.replay_grid(G, hook)
    for r in range(cur[0], G.end + 1): end_of_round(r, grid)
    for d in deaths:
        side = 'us' if d['s'] == G.us else 'them'
        for key in ((side, ph(d['r'])), (side, 'all')):
            D = S[key]
            for k in ('brk_t', 'adj_t', 'near_t', 'n2', 'n8', 'n20', 'e20', 'pre20', 'assault'): D.setdefault(k, [])
            D['n'] += 1
            reb = d['nb'] is not None and d['nb'][1] == d['s']
            if reb: D['reb'] += 1
            if 'intact0' not in d: continue
            if d['intact0']: D['intact0'] += 1
            if d['intact0'] and d['chips0']: D['instant_ok'] += 1
            for k in ('n2', 'n8', 'n20', 'e20', 'pre20', 'assault'): D[k].append(d[k])
            if d['guard']: D['guard'] += 1
            b = d['brk']
            if b is None: D['nobreak'] += 1
            elif b[1] == 'before': D['brk_before'] += 1
            else:
                D['brk_t'].append(b[0] - d['r']); D['cause_' + b[1]] += 1
                if b[0] - d['r'] <= 3: D['brk3'] += 1
                if b[0] - d['r'] <= 10: D['brk10'] += 1
            if d['adj'] is not None: D['adj_t'].append(d['adj'] - d['r'])
            if d['near'] is not None: D['near_t'].append(d['near'] - d['r'])
            won_race = d['intact0'] and d['adj'] is not None and (b is None or d['adj'] < b[0])
            if won_race: D['race'] += 1
            if won_race and (d['chips0'] if d['adj'] == d['r'] else d.get('adj_chips')): D['race_chips'] += 1


ROWS = (
    ('killed (towers)', lambda D: f"{int(D['n'])}"),
    ('rebuilt by the same side', lambda D: f"{100 * D['reb'] / max(1, D['n']):.0f}%"),
    ('at death: pattern intact (24/24)', lambda D: f"{100 * D['intact0'] / max(1, D['n']):.0f}%"),
    ('at death: intact and 1000+ chips', lambda D: f"{100 * D['instant_ok'] / max(1, D['n']):.0f}%"),
    ('at death: own robots d2<=2 (mean)', lambda D: f"{lib.mean(D['n2'])}"),
    ('at death: own robots d2<=8 (mean)', lambda D: f"{lib.mean(D['n8'])}"),
    ('at death: own robots d2<=20 (mean)', lambda D: f"{lib.mean(D['n20'])}"),
    ('  same, mean over the 10 rounds before', lambda D: f"{lib.mean(D['pre20'])}"),
    ('at death: enemy robots d2<=20 (mean)', lambda D: f"{lib.mean(D['e20'])}"),
    ('final assault, rounds (median)', lambda D: f"{lib.med(D['assault'])}"),
    ('own robot beside the tower in the assault', lambda D: f"{100 * D['guard'] / max(1, D['n']):.0f}%"),
    ('pattern broken already at death', lambda D: f"{100 * D['brk_before'] / max(1, D['n']):.0f}%"),
    ('broken after: rounds after death (med)', lambda D: f"{lib.med(D['brk_t'])}"),
    ('  within 3 rounds of the death', lambda D: f"{100 * D['brk3'] / max(1, D['n']):.0f}%"),
    ('  within 10 rounds', lambda D: f"{100 * D['brk10'] / max(1, D['n']):.0f}%"),
    ('  by an enemy mop', lambda D: f"{100 * D['cause_enemy mop'] / max(1, D['n']):.0f}%"),
    ('  by an enemy splash', lambda D: f"{100 * D['cause_enemy splash'] / max(1, D['n']):.0f}%"),
    ('  by an enemy soldier', lambda D: f"{100 * D['cause_enemy soldier'] / max(1, D['n']):.0f}%"),
    ('  by own paint', lambda D: f"{100 * D['cause_own paint'] / max(1, D['n']):.0f}%"),
    ('never broken (in the window)', lambda D: f"{100 * D['nobreak'] / max(1, D['n']):.0f}%"),
    ('first own robot adjacent, rounds (med)', lambda D: f"{lib.med(D['adj_t'])} ({100 * len(D['adj_t']) / max(1, D['n']):.0f}%)"),
    ('first own robot within d2 8 (med)', lambda D: f"{lib.med(D['near_t'])} ({100 * len(D['near_t']) / max(1, D['n']):.0f}%)"),
    ('own robot adjacent before the break', lambda D: f"{100 * D['race'] / max(1, D['n']):.0f}%"),
    ('  and 1000+ chips then', lambda D: f"{100 * D['race_chips'] / max(1, D['n']):.0f}%"),
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

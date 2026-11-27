"""Topic 98: where the opening time goes.  For each side's first three towers built (new builds, starting towers
excluded), split the time to the build into
  seen     first round a robot of the side stood within d2 20 of the ruin
  start    first round the side painted a tile of the ruin's 5x5
  ready    first round all 24 tiles held the side's colours of the built type's pattern (from the replayed grid)
  built    the build round
and report: the ruin's distance from the side's nearer starting tower, the robots of the side that painted in the
5x5, the side's chips at the end of the round before 'ready' and before 'built', and what the ruin held at 'start'
(enemy tiles in the 5x5).  Groups: lost games behind at r100 (fewer towers than them), other lost games, won games.
Only new ruins count (no tower of either side stood there before), and 'ready' is the start of the final unbroken
streak of a complete pattern (a first version counted rebuilds, whose pattern was complete around the old tower)."""
import lib
from collections import defaultdict


def first_builds(G, k=3, stop=200):
    b, d = lib.tower_events(G)
    start = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    out = {1: [], 2: []}
    used = set()
    for x in sorted(b):
        loc = (x[4], x[5])
        if x[0] == 0 or x[0] > stop or loc in used: used.add(loc); continue
        used.add(loc)
        s = x[3]
        if len(out[s]) < k and x[2] in lib.TOW:
            out[s].append(dict(r=x[0], loc=(x[4], x[5]), typ=x[2], dist=min(lib.d2((x[4], x[5]), q) for q in start[s]) ** 0.5 if start[s] else 0))
    W = G.W
    want = {}
    for s in (1, 2):
        for e in out[s]:
            e.update(seen=None, start=None, ready=None, painters=set(), enemy_at_start=None)
            cx, cy = e['loc']
            cells = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == 0 and dy == 0: continue
                    sec = lib.secondary(e['typ'], dx, dy)
                    cells.append(((cx + dx) + (cy + dy) * W, (2 if sec else 1) if s == 1 else (4 if sec else 3)))
            e['cells'] = cells
            e['cellset'] = set(i for i, _ in cells)
    # seen: positions from turns
    for t in G.turns:
        if t[0] > stop: break
        s = t[2]
        if s not in out or t[3] not in lib.BOT: continue
        for e in out[s]:
            if e['seen'] is None and t[0] <= e['r'] and lib.d2((t[4], t[5]), e['loc']) <= 20: e['seen'] = t[0]
    grid = list(G.paint0)
    for a in G.acts:
        r = a[0]
        if r > stop: break
        if a[4] not in ('paint', 'unpaint'): continue
        x, y = map(int, a[5].split(',')); i = x + y * W
        if a[4] == 'paint':
            grid[i] = (2 if a[6] == '1' else 1) if a[2] == 1 else (4 if a[6] == '1' else 3)
        else:
            grid[i] = 0
        for s in (1, 2):
            for e in out[s]:
                if r > e['r'] or i not in e['cellset']: continue
                if a[2] == s and a[4] == 'paint':
                    e['painters'].add(a[1])
                    if e['start'] is None:
                        e['start'] = r
                        e['enemy_at_start'] = sum(1 for j, _ in e['cells'] if lib.owner(grid[j]) not in (0, s))
                ok = all(grid[j] == w for j, w in e['cells'])
                if ok and e['ready'] is None: e['ready'] = r
                elif not ok: e['ready'] = None
    for s in (1, 2):
        for e in out[s]:
            e['chips_ready'] = lib.money(G, s, (e['ready'] or e['r']) - 1)
            e['chips_built'] = lib.money(G, s, e['r'] - 1)
    return out


def row(L, key):
    v = [e[key] for e in L if e.get(key) is not None]
    if not v: return '-'
    m = lib.med(v)
    return round(m) if isinstance(m, float) else m


groups = defaultdict(lambda: defaultdict(list))
for which in ('lost', 'won'):
    for G in lib.games(which):
        if which == 'lost':
            grp = 'lost, behind at r100' if lib.rv(G, G.us, 100, 'tow') < lib.rv(G, G.op, 100, 'tow') else 'lost, level or ahead at r100'
        else:
            grp = 'won'
        fb = first_builds(G)
        for side, s in (('us', G.us), ('them', G.op)):
            for j, e in enumerate(fb[s]):
                e['travel'] = e['seen']
                e['to_start'] = (e['start'] - e['seen']) if e['start'] is not None and e['seen'] is not None else None
                e['painting'] = (e['ready'] - e['start']) if e['ready'] is not None and e['start'] is not None else None
                e['chipwait'] = (e['r'] - e['ready']) if e['ready'] is not None else None
                e['npaint'] = len(e['painters'])
                groups[grp][(side, j)].append(e)
        groups[grp]['n'].append(1)

for grp in ('lost, behind at r100', 'lost, level or ahead at r100', 'won'):
    D = groups[grp]
    print(f'== {grp}: {len(D["n"])} games; medians, us / them, for the 1st / 2nd / 3rd new tower')
    print('   build  n     built r    dist   seen r    seen->start  start->ready  ready->built  painters  chips@ready  chips@built  enemy tiles@start')
    for j in range(3):
        U, T = D[('us', j)], D[('them', j)]
        f = lambda k: f'{row(U, k)}/{row(T, k)}'
        print(f'   #{j + 1}   {len(U):2d}/{len(T):2d}  {f("r"):>10s}  {f("dist")}  {f("seen"):>9s}  {f("to_start"):>11s}  {f("painting"):>12s}  {f("chipwait"):>12s}  {f("npaint"):>8s}  {f("chips_ready"):>11s}  {f("chips_built"):>11s}  {f("enemy_at_start"):>8s}')
    print()

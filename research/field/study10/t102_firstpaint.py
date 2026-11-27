"""Topic 102: why our first tower pattern takes longer to paint (t98: 'start -> ready' is 17 rounds for our first
new-ruin tower against their 13-14, in won and lost games alike).  For each side's first new-ruin tower (t98's
definition), from the round the side first saw it (a robot within d2 20) to the build, per side:
  mark     rounds from seen to the side's first mark action in the 5x5 (if any)
  start    rounds from seen to the first paint in the 5x5
  paints   paint actions by the side on the 24 pattern tiles up to the build; 'wasted' = paints that were not the
           built type's colour, or repaints of a tile already right
  idle     rounds between start and ready in which the side painted no pattern tile
  2nd      rounds from start until a second robot of the side painted a pattern tile
  near     soldiers of the side within d2 8 of the ruin, median over the start..ready rounds
Medians; all games, then lost and won."""
import lib
from collections import defaultdict


def first(G):
    W = G.W
    b, d = lib.tower_events(G)
    start = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    used = set(); out = {}
    for x in sorted(b):
        loc = (x[4], x[5])
        if x[0] == 0 or loc in used: used.add(loc); continue
        used.add(loc)
        s = x[3]
        if s not in out and x[2] in lib.TOW:
            out[s] = dict(r=x[0], loc=loc, typ=x[2])
        if len(out) == 2: break
    for s, e in out.items():
        cx, cy = e['loc']
        cells = {}
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0: continue
                sec = lib.secondary(e['typ'], dx, dy)
                cells[(cx + dx) + (cy + dy) * W] = (2 if sec else 1) if s == 1 else (4 if sec else 3)
        e.update(cells=cells, seen=None, mark=None, start=None, ready=None, paints=0, wasted=0, painters=[], prounds=set(), near=defaultdict(int))
    stop = max([e['r'] for e in out.values()] + [0])
    for t in G.turns:
        if t[0] > stop: break
        e = out.get(t[2])
        if not e or t[3] not in lib.BOT or t[0] > e['r']: continue
        dd = lib.d2((t[4], t[5]), e['loc'])
        if e['seen'] is None and dd <= 20: e['seen'] = t[0]
        if t[3] == 'SOLDIER' and dd <= 8: e['near'][t[0]] += 1
    grid = list(G.paint0)
    for a in G.acts:
        r = a[0]
        if r > stop: break
        k = a[4]
        if k == 'mark':
            e = out.get(a[2])
            if e and r <= e['r'] and e['mark'] is None:
                x, y = map(int, a[5].split(','))
                if max(abs(x - e['loc'][0]), abs(y - e['loc'][1])) <= 2: e['mark'] = r
            continue
        if k != 'paint' and k != 'unpaint': continue
        x, y = map(int, a[5].split(',')); i = x + y * W
        old = grid[i]
        new = ((2 if a[6] == '1' else 1) if a[2] == 1 else (4 if a[6] == '1' else 3)) if k == 'paint' else 0
        grid[i] = new
        for s, e in out.items():
            if r > e['r'] or i not in e['cells']: continue
            if k == 'paint' and a[2] == s:
                e['paints'] += 1
                if new != e['cells'][i] or old == e['cells'][i]: e['wasted'] += 1
                if e['start'] is None: e['start'] = r
                if a[1] not in [p for p, _ in e['painters']]: e['painters'].append((a[1], r))
                e['prounds'].add(r)
            ok = all(grid[j] == w for j, w in e['cells'].items())
            if ok and e['ready'] is None: e['ready'] = r
            elif not ok: e['ready'] = None
    res = {}
    for s, e in out.items():
        if e['seen'] is None or e['start'] is None or e['ready'] is None: continue
        st, rd = e['start'], e['ready']
        res[s] = dict(seen=e['seen'], mark=(e['mark'] - e['seen']) if e['mark'] is not None else None, start=st - e['seen'],
                      paint=rd - st, paints=e['paints'], wasted=e['wasted'],
                      idle=sum(1 for r in range(st, rd + 1) if r not in e['prounds']),
                      second=(e['painters'][1][1] - st) if len(e['painters']) > 1 else None,
                      near=lib.med([e['near'].get(r, 0) for r in range(st, rd + 1)]), built=e['r'])
    return res


rows = defaultdict(list)
for which in ('lost', 'won'):
    for G in lib.games(which):
        for s, v in first(G).items():
            rows[(which, 'us' if s == G.us else 'them')].append(v)
keys = ('seen', 'mark', 'start', 'paint', 'paints', 'wasted', 'idle', 'second', 'near', 'built')
print('medians for the first new-ruin tower; seen = round, mark/start = rounds after seen, paint = start -> ready rounds')
print('group      side  n    ' + '  '.join(f'{k:>6s}' for k in keys))
for which in ('lost', 'won', 'all'):
    for side in ('us', 'them'):
        L = rows[(which, side)] if which != 'all' else rows[('lost', side)] + rows[('won', side)]
        vals = []
        for k in keys:
            v = [x[k] for x in L if x[k] is not None]
            m = lib.med(v) if v else '-'
            vals.append(f'{m:>6}' if not isinstance(m, float) else f'{m:6.1f}')
        print(f'{which:9s}  {side:4s}  {len(L):3d}  ' + '  '.join(vals))
L = rows[('lost', 'us')] + rows[('won', 'us')]
print(f'us: no second painter in {sum(1 for x in L if x["second"] is None)} of {len(L)}; no mark in {sum(1 for x in L if x["mark"] is None)}')
L = rows[('lost', 'them')] + rows[('won', 'them')]
print(f'them: no second painter in {sum(1 for x in L if x["second"] is None)} of {len(L)}; no mark in {sum(1 for x in L if x["mark"] is None)}')

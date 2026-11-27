"""Topic 101: why finished tower patterns wait (t98's first version showed our 3rd tower waiting a median 36 rounds
from 'pattern ready' to 'built' in the lost games that were behind at r100, theirs 4; that version counted rebuilds,
whose pattern was already complete around the old tower, and t98 now takes new ruins only).  For every tower each side built in r1-300, find the
start of the final unbroken streak in which all 24 tiles held the side's colours of the built type (replayed grid),
and class every round of the wait (streak start .. build round - 1):
  chips      the side had < 1000 chips at the end of the previous round
  nobody     chips >= 1000 but no robot of the side took a turn within d2 2 of the ruin that round
  adjacent   chips >= 1000 and a robot of the side stood within d2 2 (by the adjacent robot's type)
For 'nobody' rounds: the side's nearest soldier (d2, paint).  Builds are split into new ruins and rebuilds (a tower
of the same side stood there before; the wait then starts no earlier than the last tower death on the ruin).  Groups: lost games behind at r100, other lost games, won games."""
import lib
from collections import defaultdict, Counter


def waits(G, stop=300):
    W = G.W
    b, d = lib.tower_events(G)
    builds = [x for x in sorted(b) if 0 < x[0] <= stop]
    pend = []
    seen_before = set((x[3], x[4], x[5]) for x in b if x[0] == 0)
    order = defaultdict(int)
    for x in builds:
        s, loc = x[3], (x[4], x[5])
        rebuild = (s, loc[0], loc[1]) in seen_before
        seen_before.add((s, loc[0], loc[1]))
        order[s] += 1
        cells = {}
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0: continue
                sec = lib.secondary(x[2], dx, dy)
                cells[(loc[0] + dx) + (loc[1] + dy) * W] = (2 if sec else 1) if s == 1 else (4 if sec else 3)
        right = sum(1 for i, w in cells.items() if G.paint0[i] == w)
        pend.append(dict(r=x[0], s=s, loc=loc, typ=x[2][0], cells=cells, right=right,
                         streak=0 if right == 24 else None, rebuild=rebuild, n=order[s]))
    by_cell = defaultdict(list)
    for e in pend:
        for i in e['cells']: by_cell[i].append(e)
    grid = list(G.paint0)
    for a in G.acts:
        r = a[0]
        if r > stop: break
        if a[4] != 'paint' and a[4] != 'unpaint': continue
        x, y = map(int, a[5].split(',')); i = x + y * W
        old = grid[i]
        new = ((2 if a[6] == '1' else 1) if a[2] == 1 else (4 if a[6] == '1' else 3)) if a[4] == 'paint' else 0
        if new == old: continue
        grid[i] = new
        for e in by_cell.get(i, ()):
            if r > e['r']: continue
            w = e['cells'][i]
            if old == w: e['right'] -= 1
            if new == w: e['right'] += 1
            if e['right'] == 24 and e['streak'] is None: e['streak'] = r
            elif e['right'] < 24: e['streak'] = None
    # a pattern can only be built once the ruin is free: the wait starts no earlier than the last tower death there
    for e in pend:
        dd = [x[0] for x in d if (x[4], x[5]) == e['loc'] and x[0] <= e['r']]
        if dd and e['streak'] is not None: e['streak'] = max(e['streak'], max(dd))
    # positions per round for the rounds we need
    need = defaultdict(list)
    for e in pend:
        if e['streak'] is not None and e['r'] - e['streak'] > 2:
            for r in range(e['streak'] + 1, e['r']): need[r].append(e)
    near = defaultdict(lambda: defaultdict(list))   # id(e) -> r -> [(d2, type, paint)]
    for t in G.turns:
        r = t[0]
        if r not in need or t[3] not in lib.BOT: continue
        for e in need[r]:
            if t[2] != e['s']: continue
            near[id(e)][r].append((lib.d2((t[4], t[5]), e['loc']), t[3], t[7]))
    for e in pend:
        e['cls'] = Counter(); e['nob'] = []
        if e['streak'] is None or e['r'] - e['streak'] <= 2: continue
        for r in range(e['streak'] + 1, e['r']):
            if lib.money(G, e['s'], r - 1) < 1000: e['cls']['chips'] += 1; continue
            L = near[id(e)].get(r, [])
            adj = [z for z in L if z[0] <= 2]
            if adj: e['cls']['adjacent ' + adj[0][1][:2]] += 1; continue
            e['cls']['nobody'] += 1
            sol = sorted(z for z in L if z[1] == 'SOLDIER')
            e['nob'].append(sol[0] if sol else None)
    return pend


groups = defaultdict(list)
for which in ('lost', 'won'):
    for G in lib.games(which):
        if which == 'lost':
            grp = 'lost, behind at r100' if lib.rv(G, G.us, 100, 'tow') < lib.rv(G, G.op, 100, 'tow') else 'lost, level or ahead at r100'
        else:
            grp = 'won'
        for e in waits(G):
            e['side'] = 'us' if e['s'] == G.us else 'them'
            groups[grp].append(e)

for grp in ('lost, behind at r100', 'lost, level or ahead at r100', 'won'):
    print(f'== {grp}')
    for side in ('us', 'them'):
        for kind in ('new ruin, builds #1-3', 'new ruin, later builds', 'rebuild'):
            L = [e for e in groups[grp] if e['side'] == side and (e['rebuild'] if kind == 'rebuild' else (not e['rebuild'] and ((e['n'] <= 3) == (kind.endswith('#1-3')))))]
            if not L: continue
            wt = [e['r'] - e['streak'] for e in L if e['streak'] is not None]
            long = [e for e in L if e['streak'] is not None and e['r'] - e['streak'] > 2]
            C = Counter()
            for e in long: C.update(e['cls'])
            tot = sum(C.values())
            nob = [z for e in long for z in e['nob']]
            nsol = [z for z in nob if z is not None]
            low = sum(1 for z in nsol if z[2] < 10)
            print(f'   {side:4s} {kind:24s} builds {len(L):4d}, wait med {lib.med(wt)}, >2 rounds {len(long):3d}, wait rounds {tot:5d}: '
                  + ', '.join(f'{k} {100 * v / max(1, tot):.0f}%' for k, v in C.most_common()))
            if nob:
                print(f'        {"":24s} nobody rounds: no soldier of the side seen {len(nob) - len(nsol)}, nearest soldier d2 med {lib.med([z[0] for z in nsol])}, '
                      f'its paint < 10 in {low} of {len(nsol)}')
    print()

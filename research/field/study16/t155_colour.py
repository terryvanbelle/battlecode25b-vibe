"""Topic 155: in what colour each side paints open ground, and what an SRP costs to finish (new: t152/t154 show SRPs and
tower patterns fighting over colours).  Soldier.paintNear / paintHere paint primary only (rc.attack(l, false)), so in
our territory an SRP needs its 13 secondary tiles repainted.  RESOURCE_PATTERN folds to a period-4 lattice, so a side
that paints open ground in lattice colours gets SRPs that only need completing.
Per side, losses then wins, by phase:
  A. soldier paint rows on an EMPTY tile at Chebyshev 3+ from every ruin ("open ground"): share in the secondary colour;
     share in the colour of the SRP lattice, for the best of the 16 lattice alignments of that side in that game (a
     side that ignores the lattice scores about 50% on its best alignment by chance, ~52% if all primary)
  B. per SRP completed: the side's paint rows inside its 5x5 during the 60 rounds before completion, split into fresh
     (empty -> right colour), repaint (own wrong colour -> right) and other; and the side's tiles that were already
     right 60 rounds before (the head start)
  C. all paint rows of the side on its own paint (a colour change: pattern work), per 100 soldier-turns"""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3)]
SRP = {o: lib.secondary('SRP', *o) for o in OFFS}


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def lat(x, y, ax, ay):
    """SRP lattice colour (True = secondary) at (x, y) for centres at x = ax, y = ay (mod 4)."""
    dx = (x - ax + 2) % 4 - 2; dy = (y - ay + 2) % 4 - 2
    return SRP[(dx, dy)]


def analyse(G, S):
    W, H = G.W, G.H
    near_ruin = set()
    for q in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3): near_ruin.add((q[0] + dx, q[1] + dy))
    nturn = defaultdict(int)
    for t in G.turns:
        if t[3] == 'SOLDIER':
            p = ph(t[0])
            if p is not None: nturn[(t[2], p)] += 1
    open_rows = defaultdict(list)   # (team, phase) -> [(x, y, sec)]
    srps = [(a[0], a[2], tuple(map(int, a[5].split(',')))) for a in G.acts if a[4] == 'srp']
    # per SRP: rows inside its 5x5 in the 60 rounds before completion
    watch = defaultdict(list)
    for k, (r0, side, c) in enumerate(srps):
        for dx, dy in OFFS: watch[(c[0] + dx, c[1] + dy)].append(k)
    work = [defaultdict(int) for _ in srps]
    head = [None] * len(srps)
    recol = defaultdict(int)
    starts = defaultdict(list)
    for k, (r0, side, c) in enumerate(srps): starts[max(1, r0 - 60)].append(k)
    cur = [0]

    def snap(grid, r):
        for k in starts.get(r, ()):
            r0, side, c = srps[k]
            right = 0
            for dx, dy in OFFS:
                g = grid[(c[0] + dx) + (c[1] + dy) * W]
                if lib.owner(g) == side and (g in (2, 4)) == SRP[(dx, dy)]: right += 1
            head[k] = right

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0] + 1, a[0] + 1): snap(grid, r)
            cur[0] = a[0]
        if a[4] != 'paint': return
        x, y = map(int, a[5].split(',')); g = grid[x + y * W]; sec = a[6] == '1'; side = a[2]
        p = ph(a[0])
        if a[3] == 'SOLDIER' and g == 0 and (x, y) not in near_ruin and p is not None:
            open_rows[(side, p)].append((x, y, sec))
        if a[3] == 'SOLDIER' and lib.owner(g) == side and p is not None: recol[(side, p)] += 1
        for k in watch.get((x, y), ()):
            r0, s, c = srps[k]
            if s != side or not (r0 - 60 <= a[0] <= r0): continue
            want = SRP[(x - c[0], y - c[1])]
            if sec == want:
                if g == 0: work[k]['fresh'] += 1
                elif lib.owner(g) == side: work[k]['repaint'] += 1
                else: work[k]['over_enemy'] += 1
            else: work[k]['wrong'] += 1

    lib.replay_grid(G, hook)
    for (side, p), rows in open_rows.items():
        sd = 'us' if side == G.us else 'them'
        D = S[(sd, p)]
        D['open'] += len(rows); D['open_sec'] += sum(1 for r in rows if r[2])
        best = max(sum(1 for x, y, s in rows if lat(x, y, ax, ay) == s) for ax in range(4) for ay in range(4)) if rows else 0
        D['open_lat'] += best
    for (side, p), n in nturn.items():
        sd = 'us' if side == G.us else 'them'
        S[(sd, p)]['sturns'] += n; S[(sd, p)]['recol'] += recol.get((side, p), 0)
    for k, (r0, side, c) in enumerate(srps):
        sd = 'us' if side == G.us else 'them'
        D = S[(sd, ph(r0))]
        D['srp'] += 1
        for kk, v in work[k].items(): D['w_' + kk] += v
        if head[k] is not None: D['head'] += head[k]; D['head_n'] += 1


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); ng = 0
    for G in lib.games(which):
        analyse(G, S); ng += 1
    print(f'\n== {which}: {ng} games')
    print(f'   {"":58s}' + ''.join(f'{PHN[p] + " us":>14s}{"them":>8s}' for p in range(3)))

    def row(name, f):
        cells = ''
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, p)]
                try: s = f(D)
                except ZeroDivisionError: s = '-'
                cells += f'{s:>14s}' if side == 'us' else f'{s:>8s}'
        print(f'   {name:58s}' + cells)
    row('A. soldier paint rows on open empty ground, per game', lambda D: f'{D["open"] / ng:.0f}')
    row('   in the secondary colour', lambda D: f'{100 * D["open_sec"] / D["open"]:.0f}%')
    row('   in the SRP lattice colour (best alignment)', lambda D: f'{100 * D["open_lat"] / D["open"]:.0f}%')
    row('B. SRPs completed per game', lambda D: f'{D["srp"] / ng:.2f}')
    row('   tiles already right 60 rounds before (of 25)', lambda D: f'{D["head"] / D["head_n"]:.1f}')
    row('   own rows in its 5x5 in those 60 rounds: fresh', lambda D: f'{D["w_fresh"] / D["srp"]:.1f}')
    row('     repaint (own wrong colour -> right)', lambda D: f'{D["w_repaint"] / D["srp"]:.1f}')
    row('     over enemy paint (splash) -> right', lambda D: f'{D["w_over_enemy"] / D["srp"]:.1f}')
    row('     in the wrong colour', lambda D: f'{D["w_wrong"] / D["srp"]:.1f}')
    row('C. soldier paint rows on own paint per 100 soldier-turns', lambda D: f'{100 * D["recol"] / D["sturns"]:.1f}')

"""Topic 112: splashers repainting their own side's tower patterns.  A splash paints every empty or own tile in r2 4
in ONE colour (our Splasher.splash calls rc.attack(t): primary), so an own secondary tile in a ruin's 5x5 turns
primary and the pattern is wrong again (RULES 5.2; the SRP lattice is guarded in G.remember, tower patterns are not).
Replays the grid and counts, per side, splasher paints that flip an own tile's colour (secondary -> primary or back):
  in a FREE ruin's 5x5 (a pattern being painted: the soldier must repaint it),
  in the 5x5 of a STANDING own tower (breaks the pattern a churn rebuild needs; money towers only matter),
  elsewhere (SRPs and plain ground: harmless unless an SRP sits there).
Also soldier paints in free ruins that RE-paint a tile the side's own splasher flipped (the repair cost), and the
same flips by the other side's splashers for comparison.  Lost and won games."""
import lib
from collections import Counter, defaultdict


def analyse(G):
    b, d = lib.tower_events(G)
    died = {x[1]: x[0] for x in d}
    iv = defaultdict(list)
    for x in b: iv[(x[4], x[5])].append((x[0], died.get(x[1], 10 ** 6), x[3], x[2]))
    ruin_of = {}
    for (rx, ry) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy: ruin_of[(rx + dx, ry + dy)] = (rx, ry)
    grid = list(G.paint0); W = G.W
    c = {1: Counter(), 2: Counter()}
    flipped = {}   # tile -> (side, round) flipped by own splasher
    for a in G.acts:
        if a[4] == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0; flipped.pop((x, y), None); continue
        if a[4] != 'paint': continue
        x, y = map(int, a[5].split(',')); sec = a[6] == '1'; s = a[2]
        new = (2 if sec else 1) if s == 1 else (4 if sec else 3)
        old = grid[x + y * W]
        grid[x + y * W] = new
        if a[3] == 'SPLASHER':
            c[s]['splasher paints'] += 1
            if old and lib.owner(old) == s and old != new:
                ru = ruin_of.get((x, y))
                where = 'elsewhere'
                if ru is not None:
                    st = [t for t in iv.get(ru, ()) if t[0] <= a[0] < t[1]]
                    if not st: where = 'free ruin'
                    elif st[0][2] == s: where = 'own ' + st[0][3][:5].lower() + ' tower'
                    else: where = 'enemy tower'
                c[s]['flip ' + where] += 1
                if where == 'free ruin': flipped[(x, y)] = (s, a[0])
        elif a[3] == 'SOLDIER' and (x, y) in flipped:
            fs, fr = flipped.pop((x, y))
            if fs == s and old and lib.owner(old) == s and a[0] - fr <= 50: c[s]['soldier repaints a flipped ruin tile'] += 1
    return c


for which in ('lost', 'won'):
    tot = {'us': Counter(), 'them': Counter()}; n = 0; per = []
    for G in lib.games(which):
        c = analyse(G); n += 1
        tot['us'].update(c[G.us]); tot['them'].update(c[G.op])
        per.append(c[G.us]['flip free ruin'])
        lib.lite(G)
    print(f'\n== {which.upper()} games: {n}')
    keys = ['splasher paints', 'flip free ruin', 'flip own money tower', 'flip own paint tower', 'flip own defen tower', 'flip enemy tower',
            'flip elsewhere', 'soldier repaints a flipped ruin tile']
    for k in keys:
        print(f'   {k:40s} us {tot["us"][k]:7d}   them {tot["them"][k]:7d}')
    print(f'   per game, flips in free ruins (ours): median {lib.med(per)}, p75 {lib.pct(per, .75)}, games with any {sum(1 for v in per if v)}')

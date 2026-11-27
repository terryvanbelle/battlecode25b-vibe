"""Topic 53: does ruin denial work?  For each side's marked ruins (first mark per side and ruin), whether the marker
completed a tower there afterwards, split by whether the OTHER side painted into the ruin's 5x5 (denial: paint
actions by soldiers/splashers of a side that had not marked that ruin itself) between the mark and the marker's next
build.  Lost and won games."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    C = Counter()
    for G in lib.games(which):
        near = lambda x, y: next((r for r in G.ruins if max(abs(r[0] - x), abs(r[1] - y)) <= 2 and (r[0], r[1]) != (x, y)), None)
        first = {}
        for a in G.acts:
            if a[4] == 'mark':
                x, y = map(int, a[5].split(',')); r = near(x, y)
                if r: first.setdefault((a[2], r), a[0])
        b, dd = lib.tower_events(G)
        bl = defaultdict(list)
        for x in b:
            if x[0] > 0: bl[(x[3], (x[4], x[5]))].append(x[0])
        def nextbuild(sd, r, t0):
            z = [q for q in bl.get((sd, r), ()) if q >= t0]
            return min(z) if z else None
        hit = defaultdict(int)
        for a in G.acts:
            if a[4] != 'paint' or a[3] not in lib.BOT: continue
            x, y = map(int, a[5].split(',')); r = near(x, y)
            if not r: continue
            other = 3 - a[2]
            if (other, r) not in first or (a[2], r) in first: continue
            t0 = first[(other, r)]; nb = nextbuild(other, r, t0)
            if a[0] >= t0 and (nb is None or a[0] <= nb): hit[(other, r)] += 1
        for (sd, r), t0 in first.items():
            w = 'us' if sd == G.us else 'them'
            h = 'denied' if hit.get((sd, r), 0) > 0 else 'clean'
            nb = nextbuild(sd, r, t0)
            C[(w, h, 'n')] += 1
            C[(w, h, 'built')] += nb is not None
            if nb is not None and nb - t0 <= 50: C[(w, h, 'built<=50')] += 1
    print(f'== {which} games: marked ruins completed by the marker, by whether the other side painted into the 5x5')
    for w in ('us', 'them'):
        for h in ('clean', 'denied'):
            n = C[(w, h, 'n')]
            print(f'   {w:4s} {h:7s} marked {n:3d}  completed {C[(w, h, "built")]:3d} ({round(100 * C[(w, h, "built")] / max(1, n))}%)  within 50 rounds {C[(w, h, "built<=50")]:3d} ({round(100 * C[(w, h, "built<=50")] / max(1, n))}%)')

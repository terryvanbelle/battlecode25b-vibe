"""Topic 83: what splashers do, both sides, lost vs won games, by phase (r1-150, r151-300, r301+).
A splash is a 'splash' row followed by one 'paint' row per tile the engine set (RULES 4.1: empty or own tiles within
d2 <= 4 of the centre, enemy tiles only within d2 <= 2).  Replaying the paint grid gives each splash's yield:
new tiles (empty -> ours), flipped tiles (theirs -> ours) and repaints (already ours, wasted).  Also: splashes per
100 splasher-turns; splasher-turns that ended ready to splash (action cooldown < 10, paint >= 50) without having
splashed; tower damage dealt by splashes; where splashes land (own half / other half, by distance to the nearest
starting tower of each side); splasher deaths per 100 splasher-turns.  Medians per game; sums in brackets."""
import lib, csv
from collections import defaultdict

PH = ((1, 150), (151, 300), (301, 2000))
def ph(r):
    return 0 if r <= 150 else 1 if r <= 300 else 2


def sides(G):
    b, d = lib.tower_events(G)
    st = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    def f(p, side):
        du = min(lib.d2(p, q) for q in st[side]); dt = min(lib.d2(p, q) for q in st[3 - side])
        return 'own' if du < dt else 'other' if dt < du else 'mid'
    return f


def acd_ready(G):
    """(round, id) of splasher turns that ended with action cooldown < 10 (read from turns.tsv directly)."""
    out = set()
    with open(f'{lib.DUMPS[G.m]}/g{G.g}.turns.tsv') as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); it = h.index('type'); ia = h.index('acd')
        for t in r:
            if t[it] == 'SPLASHER' and int(t[ia]) < 10: out.add((int(t[0]), int(t[1])))
    return out


for which in ('lost', 'won'):
    S = defaultdict(list); T = defaultdict(int); n = 0
    for G in lib.games(which):
        n += 1
        where = sides(G)
        C = defaultdict(int)
        grid = list(G.paint0); W = G.W
        cur = {}   # splasher id -> (round, side) of its current splash
        splashed = set()
        for a in G.acts:
            k = a[4]
            if k == 'splash':
                side = 'us' if a[2] == G.us else 'them'
                cur[a[1]] = a[0]; splashed.add((a[0], a[1]))
                C[(side, ph(a[0]), 'splashes')] += 1
                x, y = map(int, a[5].split(','))
                C[(side, ph(a[0]), 'in ' + where((x, y), a[2]) + ' half')] += 1
            elif k == 'paint':
                x, y = map(int, a[5].split(',')); i = x + y * W
                old = grid[i]
                if a[3] == 'SPLASHER' and cur.get(a[1]) == a[0]:
                    side = 'us' if a[2] == G.us else 'them'
                    o = lib.owner(old); me = 1 if a[2] == 1 else 2
                    C[(side, ph(a[0]), 'new tiles' if o == 0 else 'repaints' if o == me else 'flipped tiles')] += 1
                sec = a[6] == '1'
                grid[i] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
            elif k == 'unpaint':
                x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
            elif k == 'damage' and a[3] == 'SPLASHER':
                side = 'us' if a[2] == G.us else 'them'
                C[(side, ph(a[0]), 'tower damage')] += int(a[6])
            elif k == 'die' and a[7] == 'SPLASHER':
                vid = int(a[5]); side = 'us' if G.team.get(vid) == G.us else 'them'
                C[(side, ph(a[0]), 'deaths')] += 1
        ready = acd_ready(G)
        for t in G.turns:
            if t[3] != 'SPLASHER': continue
            side = 'us' if t[2] == G.us else 'them'; p = ph(t[0])
            C[(side, p, 'turns')] += 1
            if t[7] < 50: C[(side, p, 'turns below 50 paint')] += 1
            elif (t[0], t[1]) in ready and (t[0], t[1]) not in splashed: C[(side, p, 'ready, no splash')] += 1
        for side in ('us', 'them'):
            for p in range(3):
                if PH[p][0] > G.end: continue
                tu = C[(side, p, 'turns')]
                if tu < 30: continue
                sp = C[(side, p, 'splashes')]
                S[(side, p, 'splasher-turns')].append(tu)
                S[(side, p, 'splashes per 100 turns')].append(round(100 * sp / tu, 1))
                S[(side, p, '% turns below 50 paint')].append(round(100 * C[(side, p, 'turns below 50 paint')] / tu, 1))
                S[(side, p, '% turns ready, no splash')].append(round(100 * C[(side, p, 'ready, no splash')] / tu, 1))
                if sp:
                    for m in ('new tiles', 'flipped tiles', 'repaints'):
                        S[(side, p, m + ' per splash')].append(round(C[(side, p, m)] / sp, 2))
                    S[(side, p, '% splashes in other half')].append(round(100 * C[(side, p, 'in other half')] / sp))
                    S[(side, p, 'tower damage per splash')].append(round(C[(side, p, 'tower damage')] / sp, 1))
                S[(side, p, 'deaths per 100 turns')].append(round(100 * C[(side, p, 'deaths')] / tu, 2))
                for m in ('splashes', 'new tiles', 'flipped tiles', 'repaints', 'tower damage', 'deaths'):
                    T[(side, p, m)] += C[(side, p, m)]
    print(f'== {which} games ({n}); medians over games with >= 30 splasher-turns in the phase, us / them')
    ms = ('splasher-turns', 'splashes per 100 turns', '% turns below 50 paint', '% turns ready, no splash', 'new tiles per splash',
          'flipped tiles per splash', 'repaints per splash', '% splashes in other half', 'tower damage per splash', 'deaths per 100 turns')
    print('   ' + 'metric'.ljust(28) + ''.join(f'r{a}-{b}'.rjust(20) for a, b in PH))
    print('   ' + 'games'.ljust(28) + ''.join(f'{len(S[("us", p, "splasher-turns")])} / {len(S[("them", p, "splasher-turns")])}'.rjust(20) for p in range(3)))
    for m in ms:
        print('   ' + m.ljust(28) + ''.join(f'{lib.med(S[("us", p, m)])} / {lib.med(S[("them", p, m)])}'.rjust(20) for p in range(3)))
    print('   sums ' + '; '.join(f'r{PH[p][0]}-{PH[p][1]}: ' + ', '.join(f'{m} {T[("us", p, m)]}/{T[("them", p, m)]}' for m in
          ('splashes', 'new tiles', 'flipped tiles', 'repaints', 'tower damage', 'deaths')) for p in range(3)))
    print()

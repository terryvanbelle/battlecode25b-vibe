"""Topic 96: where the opponents put their defense towers.  For every defense tower built (both result groups): was the
ruin new or did a tower of the same side stand there before (and of which type, killed or churned), were enemy robots
(soldiers / splashers / moppers) within d2 <= 20 of the ruin at the end of the round before the build, how many of
the side's towers within d2 <= 100 had been killed in the 50 rounds before, and the side's tower count and defense
tower count at the build.  Compared with the same side's paint and money towers built after r100."""
import lib
from collections import defaultdict, Counter


def builds(G):
    b, d = lib.tower_events(G)
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    hist = defaultdict(list)    # (x, y) -> [(round, side, type, 'built'/'killed'/'gone')]
    for x in b: hist[(x[4], x[5])].append((x[0], x[3], x[2], 'built', x[1]))
    for x in d: hist[(x[4], x[5])].append((x[0], x[3], x[2], 'killed' if x[1] in killed else 'gone', x[1]))
    for k in hist: hist[k].sort()
    want = defaultdict(list)
    out = []
    for x in b:
        if x[0] <= 100 or x[3] != G.op: continue
        prev = [h for h in hist[(x[4], x[5])] if h[0] <= x[0] and h[4] != x[1] and h[3] != 'built']
        last = prev[-1] if prev else None
        if last is None: origin = 'new ruin'
        elif last[1] != x[3]: origin = 'taken from the other side'
        else: origin = ('after a kill of its ' if last[3] == 'killed' else 'after a churn of its ') + last[2][0]
        near_k = sum(1 for y in d if y[3] == x[3] and y[1] in killed and x[0] - 50 <= y[0] <= x[0] and lib.d2((y[4], y[5]), (x[4], x[5])) <= 100)
        alive = lib.towers_alive(G, x[3], x[0] - 1, b, d)
        e = dict(typ=x[2][0], r=x[0], origin=origin, near_kills=near_k, n=len(alive), nd=sum(1 for t in alive if t[2] == 'DEFENSE_TOWER'), loc=(x[4], x[5]))
        out.append(e); want[x[0] - 1].append(e)
    for e in out: e['enemies'] = Counter()
    for t in G.turns:
        if t[0] in want and t[3] in lib.BOT and t[2] == G.us:
            for e in want[t[0]]:
                if lib.d2((t[4], t[5]), e['loc']) <= 20: e['enemies'][t[3][:2]] += 1
    return out


for which in ('lost', 'won'):
    S = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        for e in builds(G): S[e['typ']].append(e)
    print(f'== {which} games ({n}): THEIR towers built after r100, by type')
    for ty in ('D', 'P', 'M'):
        L = S[ty]
        if not L: continue
        o = Counter(e['origin'] for e in L)
        en = [sum(e['enemies'].values()) for e in L]
        print(f'   {ty}: {len(L)} built; origin {dict(o.most_common())}')
        print(f'      our robots within d2 20 the round before: none {sum(1 for v in en if v == 0)}, 1 {sum(1 for v in en if v == 1)}, 2+ {sum(1 for v in en if v >= 2)}'
              f' (soldiers among them in {sum(1 for e in L if e["enemies"]["SO"])})')
        print(f'      own towers killed within d2 100 in the 50 rounds before: med {lib.med([e["near_kills"] for e in L])}, 1+ in {sum(1 for e in L if e["near_kills"] > 0)}'
              f'; own towers standing med {lib.med([e["n"] for e in L])}; defense towers standing med {lib.med([e["nd"] for e in L])}')
    print()

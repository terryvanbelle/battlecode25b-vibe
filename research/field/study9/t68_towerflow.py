"""Topic 68: the tower flow between r100 and r250 (where the curves part).  Per side and game: towers standing at r100 and
r250, towers built on new ruins, rebuilt on own old ruins (after a kill), churn rebuilds, taken from the other side
(built on a ruin the other side held before), killed by the other side, and lost to churn.  Medians and sums over
lost and won games (games that reached r250)."""
import lib
from collections import defaultdict, Counter
LO, HI = 101, 250
for which in ('lost', 'won'):
    S = defaultdict(list); T = Counter(); n = 0
    for G in lib.games(which):
        if G.end < HI: continue
        n += 1
        b, d = lib.tower_events(G)
        killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
        history = defaultdict(list)   # ruin -> [(round, side, event)]
        for x in b: history[(x[4], x[5])].append((x[0], x[3], 'b'))
        for x in d: history[(x[4], x[5])].append((x[0], x[3], 'k' if x[1] in killed else 'c'))
        for sd in (G.us, G.op):
            w = 'us' if sd == G.us else 'them'
            c = Counter()
            for p, ev in history.items():
                ev.sort(key=lambda q: (q[0], q[2] == 'b'))   # a death before a build in the same round
                for i, (r, s, e) in enumerate(ev):
                    if not (LO <= r <= HI): continue
                    prev = [q for q in ev[:i] if q[2] == 'b']
                    if e == 'b' and s == sd:
                        if not prev: c['new ruin'] += 1
                        elif prev[-1][1] != sd: c['taken from them'] += 1
                        else:
                            last_end = [q for q in ev[:i] if q[2] in 'kc']
                            # no end event before it: a churn rebuild in the round of the churn (a churned tower's death is dated
                            # last turn + 1 by lib.tower_events, after the same-round rebuild)
                            c['churn rebuild' if not last_end or last_end[-1][2] == 'c' else 'rebuilt after kill'] += 1
                    elif e == 'k' and s == sd: c['killed'] += 1
                    elif e == 'c' and s == sd: c['churned'] += 1
            c['at r100'] = len(lib.towers_alive(G, sd, 100, b, d)); c['at r250'] = len(lib.towers_alive(G, sd, 250, b, d))
            for k in ('at r100', 'new ruin', 'rebuilt after kill', 'taken from them', 'churn rebuild', 'killed', 'churned', 'at r250'):
                S[(w, k)].append(c[k]); T[(w, k)] += c[k]
    print(f'== {which} games reaching r{HI}: {n}.  r{LO}-{HI} per game: median (sum) us | them')
    for k in ('at r100', 'new ruin', 'rebuilt after kill', 'taken from them', 'churn rebuild', 'killed', 'churned', 'at r250'):
        print(f'   {k:20s} {lib.med(S[("us", k)])} ({T[("us", k)]}) | {lib.med(S[("them", k)])} ({T[("them", k)]})')

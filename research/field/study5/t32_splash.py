"""Topic 32: splashers.  Per side: splashers spawned, splash actions, splashes per splasher, tiles gained per splash
(new + flipped, from the replayed grid), share of splashes that hit an enemy tower, splasher lifetime (rounds) and
share of splasher turns spent at < 50 paint (cannot splash: 50 per splash)."""
import lib
from collections import defaultdict, Counter
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    C = {1: Counter(), 2: Counter()}; W = G.W
    def hook(a, grid):
        if a[4] == 'paint' and a[3] == 'SPLASHER':
            x, y = map(int, a[5].split(',')); o = lib.owner(grid[x + y * W])
            if o != a[2]: C[a[2]]['gain'] += 1
    lib.replay_grid(G, hook)
    born, last = {}, {}
    for a in G.acts:
        if a[4] == 'spawn' and a[6] == 'SPLASHER': born[int(a[5])] = a[0]; C[a[2]]['spawned'] += 1
        if a[4] == 'splash': C[a[2]]['splash'] += 1
        if a[4] == 'damage' and a[3] == 'SPLASHER' and G.typ.get(int(a[5])) in lib.TOW: C[a[2]]['towhit'] += 1
    for t in G.turns:
        if t[3] == 'SPLASHER':
            last[t[1]] = t[0]; C[t[2]]['turns'] += 1
            if t[7] < 50: C[t[2]]['low'] += 1
    for side in (G.us, G.op):
        w = 'us' if side == G.us else 'them'; c = C[side]
        life = [last[i] - born[i] for i in born if G.team.get(i) == side and i in last]
        S[w]['spawned'].append(c['spawned']); S[w]['splashes'].append(c['splash'])
        S[w]['splash/splasher'].append(round(c['splash'] / max(1, c['spawned']), 1))
        S[w]['tiles gained/splash'].append(round(c['gain'] / max(1, c['splash']), 2))
        S[w]['tower hits'].append(c['towhit'])
        S[w]['lifetime'].append(lib.med(life) if life else None)
        S[w]['turns <50 paint %'].append(round(100 * c['low'] / max(1, c['turns']), 1))
        S[w]['splashes per 100 turns'].append(round(100 * c['splash'] / max(1, c['turns']), 1))
for k in S['us']:
    print(f'{k:24s} us med {lib.med(S["us"][k])}  them med {lib.med(S["them"][k])}   us {S["us"][k]}  them {S["them"][k]}')

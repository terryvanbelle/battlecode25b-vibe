"""Topic 24: starvation.  Robot deaths where the robot's last turn had paint 0 (starved / drained) vs >0, per side and
type; share of own robot-turns ending on enemy paint; soldiers that sat >= 10 turns on enemy paint below 50% paint
without heading home."""
import lib
from collections import Counter, defaultdict
S = defaultdict(Counter); EN = defaultdict(Counter)
for G in lib.games():
    W = G.W
    last = {}
    for t in G.turns:
        if t[3] in lib.BOT: last[t[1]] = t
    died = set(int(a[5]) for a in G.acts if a[4] == 'die')
    for i, t in last.items():
        if t[0] >= G.end - 1: continue
        nm = 'US' if t[2] == G.us else 'TH'
        S[nm][(t[3][:3], 'paint0' if t[7] == 0 else 'paint>0')] += 1
    rt = lib.by_round_turns(G)
    def hook(a, grid, cur=[0]):
        if a[0] == cur[0]: return
        r = cur[0]; cur[0] = a[0]
        for t in rt.get(r, []):
            if t[3] in lib.BOT:
                v = grid[t[4] + t[5] * W]; o = lib.owner(v)
                nm = 'US' if t[2] == G.us else 'TH'
                EN[nm]['enemy' if o and o != t[2] else ('own' if o else 'empty')] += 1
    lib.replay_grid(G, hook)
for nm in ('US', 'TH'):
    print(nm, 'robot deaths by last paint', dict(S[nm]))
    n = sum(EN[nm].values()); print('   robot turns ending on', {k: f'{100*v/n:.1f}%' for k, v in EN[nm].items()})

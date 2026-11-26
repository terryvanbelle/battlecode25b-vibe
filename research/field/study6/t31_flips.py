"""Topic 31: who takes tiles from whom.  Replays the paint grid; each paint action by side X on a tile the other side
owned is a 'flip', each unpaint of the other side's tile a 'mop-clear'.  Per phase and actor type, both directions.
Also tiles painted on empty ground per actor type (expansion)."""
import lib
from collections import defaultdict, Counter
PH = ((1, 100), (101, 200), (201, 300), (301, 400), (401, 9999))
def ph(r):
    for i, p in enumerate(PH):
        if p[0] <= r <= p[1]: return i
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    C = {s: [Counter() for _ in PH] for s in (1, 2)}
    W = G.W
    def hook(a, grid):
        k = a[4]
        if k not in ('paint', 'unpaint'): return
        x, y = map(int, a[5].split(',')); o = lib.owner(grid[x + y * W]); X = a[2]; i = ph(a[0])
        if k == 'paint':
            if o == 0: C[X][i]['new_' + a[3][:2]] += 1
            elif o != X: C[X][i]['flip_' + a[3][:2]] += 1
        elif o != 0 and o != X: C[X][i]['mopclr'] += 1
    lib.replay_grid(G, hook)
    for i, p in enumerate(PH):
        if G.end < p[0]: continue
        for side in (G.us, G.op):
            who = 'us' if side == G.us else 'them'
            for k in ('new_SO', 'new_SP', 'new_MO', 'flip_SO', 'flip_SP', 'mopclr'):
                S[(who, i)][k].append(C[side][i][k])
print('median per game; us | them   (new_ = painted on empty, flip_ = painted over enemy, mopclr = enemy tile mopped empty)')
print(f'{"metric":10s}' + ''.join(f'{f"r{a}-{b}":>16s}' for a, b in PH))
print(f'{"games":10s}' + ''.join(f'{len(S[("us", i)]["new_SO"]):>16d}' for i in range(len(PH))))
for k in ('new_SO', 'new_SP', 'new_MO', 'flip_SO', 'flip_SP', 'mopclr'):
    print(f'{k:10s}' + ''.join(f'{str(lib.med(S[("us", i)][k])) + " | " + str(lib.med(S[("them", i)][k])):>16s}' for i in range(len(PH))))

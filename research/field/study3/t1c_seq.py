"""Topic 1c: spawn sequence structure r50-250: transitions between consecutive spawns of the same tower and of the
whole team; mopper spawns vs enemy proximity (nearest of our robots d2 to the spawning tower)."""
import lib
from collections import Counter, defaultdict
TR = defaultdict(Counter); TT = defaultdict(Counter); NEAR = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
for G in lib.games():
    tn = G.team_name
    rt = lib.by_round_turns(G)
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW: pos[t[1]] = (t[4], t[5])
    sp = [a for a in G.acts if a[4] == 'spawn' and a[6] in lib.BOT and a[2] == G.op and 50 <= a[0] <= 250]
    last = {}; prevteam = None
    for a in sp:
        ty = a[6][:3]
        if a[1] in last: TR[tn][last[a[1]] + '>' + ty] += 1
        if prevteam: TT[tn][prevteam + '>' + ty] += 1
        last[a[1]] = ty; prevteam = ty
        T = pos.get(a[1])
        ds = [lib.d2((u[4], u[5]), T) for u in rt[a[0] - 1] if u[2] == G.us and u[3] in lib.BOT]
        m = min(ds) if ds else 9999
        NEAR[tn]['enemy within d2<=20' if m <= 20 else 'enemy d2 21-80' if m <= 80 else 'no enemy within 80'][ty].append(1)
for tn in TR:
    print(tn, ' per-tower transitions', dict(TR[tn].most_common()))
    print('    team transitions', dict(TT[tn].most_common()))
    for k, v in NEAR[tn].items():
        tot = sum(len(x) for x in v.values())
        print(f'    {k:<20} n={tot:<4}', {t: round(len(x) / tot, 2) for t, x in v.items()})

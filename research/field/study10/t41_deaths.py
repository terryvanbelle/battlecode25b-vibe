"""Topic 41: how robots die, both sides, lost vs won games.  A 'die' row's actor is the killer (an enemy tower) or the
victim itself (0-paint HP loss).  Per side and type: deaths, share killed by towers vs starved, mean age at death,
deaths per 100 robot-turns, paint drained from the victim by enemy moppers in its last 10 rounds (drain rows),
and whether the victim's last turn ended on enemy paint (from the replayed grid)."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    S = defaultdict(Counter); ages = defaultdict(list); drained = defaultdict(list)
    for G in lib.games(which):
        born = {}; last = {}; turns = Counter()
        for a in G.acts:
            if a[4] == 'spawn': born[int(a[5])] = a[0]
        for t in G.turns:
            if t[3] in lib.BOT: last[t[1]] = t; turns[(t[2], t[3])] += 1
        drains = defaultdict(list)
        for a in G.acts:
            if a[4] == 'drain': drains[int(a[5])].append((a[0], int(a[6])))
        # paint grid at each robot's last turn: replay with a hook keyed on rounds
        need = defaultdict(list)   # round -> [(victim id, x, y)]
        deaths = []
        for a in G.acts:
            if a[4] == 'die' and a[7] in lib.BOT:
                v = int(a[5]); lt = last.get(v)
                if lt is None: continue
                cause = 'starved' if a[1] == v else ('tower' if G.typ.get(a[1], '') in lib.TOW else 'other')
                deaths.append((a[0], v, G.team.get(v), a[7], cause, lt))
                need[lt[0]].append(v)
        side_of = {}
        tile = {}
        cur = [0]
        def hook(a, grid):
            # before applying round r's first action, record tiles for robots whose last turn was in round r-1
            if a[0] != cur[0]:
                for r in range(cur[0], a[0]):
                    for v in need.get(r, ()):
                        lt = last[v]; tile[v] = lib.owner(grid[lt[4] + lt[5] * G.W])
                cur[0] = a[0]
        lib.replay_grid(G, hook)
        for (r, v, team, typ, cause, lt) in deaths:
            w = 'us' if team == G.us else 'them'
            k = (w, typ[:2])
            S[k]['deaths'] += 1; S[k][cause] += 1
            if born.get(v) is not None: ages[k].append(r - born[v])
            dr = sum(x for (q, x) in drains.get(v, ()) if r - 10 <= q <= r)
            drained[k].append(dr)
            if dr > 0: S[k]['drained before death'] += 1
            tl = tile.get(v)
            if tl is not None and tl != 0 and tl != team: S[k]['died on enemy paint'] += 1
            if lt[7] == 0: S[k]['last paint 0'] += 1
        for (team, typ), n in turns.items():
            w = 'us' if team == G.us else 'them'
            S[(w, typ[:2])]['turns'] += n
    print(f'== {which} games')
    print(f'{"side type":10s} {"deaths":>6s} {"/100 turns":>10s} {"tower-killed":>12s} {"starved":>8s} {"drained<=10r":>12s} {"mean drain":>10s} {"on enemy paint":>14s} {"med age":>7s}')
    for k in sorted(S):
        s = S[k]; d = max(1, s['deaths'])
        print(f'{k[0]:4s} {k[1]:5s} {s["deaths"]:6d} {100 * s["deaths"] / max(1, s["turns"]):10.2f} {100 * s["tower"] / d:11.0f}% {100 * s["starved"] / d:7.0f}% '
              f'{100 * s["drained before death"] / d:11.0f}% {sum(drained[k]) / d:10.1f} {100 * s["died on enemy paint"] / d:13.0f}% {lib.med(ages[k]):>7}')

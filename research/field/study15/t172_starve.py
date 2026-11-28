"""Topic 172: where our soldiers starve (t156: 13.4 of our soldiers a loss die at 0 paint, theirs 8.8; 60% of ours hit 0
paint with no own tower in sight; t170: 71-75% of our soldiers that leave a siege alive starve within 40 rounds).
RULES 2.1/5.3: a robot at 0 paint can neither move nor act and loses 20 HP a turn; on enemy paint it loses 2 paint a
turn (+2 per adjacent ally), 1 on neutral ground, and below half paint its cooldowns grow.
For every soldier that starved (a 'die' row whose actor is the soldier itself), from R0, the first round of its last
0-paint stretch: what it did in the 30 rounds before R0 (hit an enemy tower; its paint at its last hit; painted
tiles; marked/completed a pattern), the 30-round paint drop without its own attacks (passive drain), the d2 to the
nearest own tower alive and to the nearest own paint tower at R0, and the paint of that nearest own tower.
Also, per game, the defense towers each side built and our soldiers killed with a defense tower among the damage
dealers in their last 10 rounds, per opponent."""
from collections import defaultdict
import lib


def analyse(G, S, per):
    life = defaultdict(dict); tw = defaultdict(list)
    for t in G.turns:
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7])
        elif t[3] in lib.TOW: tw[t[0]].append((t[1], t[2], t[3], t[4], t[5], t[7]))
    acts = defaultdict(list)
    for a in G.acts:
        if a[3] == 'SOLDIER': acts[a[1]].append(a)
    tt = {}
    for t in G.turns:
        if t[3] in lib.TOW: tt[t[1]] = t[3]
    for a in G.acts:
        if a[4] == 'die' and a[1] == int(a[5]) and a[7] == 'SOLDIER':
            sid = a[1]; L = life[sid]
            side = G.team.get(sid); sd = 'us' if side == G.us else 'them'
            rs = sorted(L)
            r0 = None
            for r in reversed(rs):
                if L[r][3] == 0: r0 = r
                else: break
            if r0 is None: continue
            A = [x for x in acts[sid] if r0 - 30 <= x[0] <= r0]
            hits = [x for x in A if x[4] == 'damage' and tt.get(int(x[5])) in lib.TOW]
            pts = sum(1 for x in A if x[4] == 'paint')
            wrk = sum(1 for x in A if x[4] in ('mark', 'srp', 'build'))
            S[sd, 'n'] += 1
            S[sd, 'sieged'] += bool(hits)
            if hits:
                hr = max(x[0] for x in hits)
                S.setdefault((sd, 'paint_at_hit'), []).append(L.get(hr, (0, 0, 0, 0))[3])
                S.setdefault((sd, 'rounds_from_hit'), []).append(r0 - hr)
            S[sd, 'painted'] += pts > 0; S[sd, 'worked'] += wrk > 0
            S[sd, 'idle'] += not hits and pts == 0 and wrk == 0
            p30 = L.get(r0 - 30, L.get(min(rs), (0, 0, 0, 0)))[3]
            S.setdefault((sd, 'paint30'), []).append(p30)
            x, y = L[r0][0], L[r0][1]
            best = None; bestp = None
            for (tid, tm, ty, tx, ty_, tp) in tw.get(r0, ()):
                if tm != side: continue
                d = (tx - x) ** 2 + (ty_ - y) ** 2
                if best is None or d < best[0]: best = (d, tp, ty)
                if ty == 'PAINT_TOWER' and (bestp is None or d < bestp): bestp = d
            if best:
                S.setdefault((sd, 'd_tower'), []).append(best[0]); S.setdefault((sd, 'tower_paint'), []).append(best[1])
                S[sd, 'near_money'] += best[2] == 'MONEY_TOWER'
                S[sd, 'in_sight'] += best[0] <= 20
            if bestp is not None: S.setdefault((sd, 'd_paint'), []).append(bestp)
            else: S[sd, 'no_paint_tower'] += 1
            S[sd, 'age'] += r0 - min(rs)
    # defense towers
    dmg = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.TOW: dmg[int(a[5])].append((a[0], a[1]))
    seen = set()
    for t in G.turns:
        if t[3] == 'DEFENSE_TOWER' and t[1] not in seen:
            seen.add(t[1]); per[G.team_name, 'def_' + ('us' if t[2] == G.us else 'them')] += 1
    for a in G.acts:
        if a[4] == 'die' and a[3] in lib.TOW and a[7] == 'SOLDIER' and G.team.get(int(a[5])) == G.us:
            rows = [x for x in dmg.get(int(a[5]), ()) if a[0] - 10 <= x[0] <= a[0]]
            per[G.team_name, 'killed'] += 1
            per[G.team_name, 'killed_def'] += any(tt.get(x[1]) == 'DEFENSE_TOWER' for x in rows)
    per[G.team_name, 'games'] += 1
    S['games'] += 1


per = defaultdict(int)
for which in ('lost', 'won'):
    S = defaultdict(int)
    for G in lib.games(which):
        analyse(G, S, per)
    ng = S['games']
    print(f'\n== {which}: {ng} games; soldiers that starved')
    for sd in ('us', 'them'):
        n = max(1, S[sd, 'n'])
        print(f'  {sd}: {S[sd, "n"] / ng:4.1f}/g; in the 30 rounds before 0 paint: hit a tower {100 * S[sd, "sieged"] / n:3.0f}% '
              f'(paint at its last hit med {lib.med(S.get((sd, "paint_at_hit"), []))}, rounds from it to 0 paint med {lib.med(S.get((sd, "rounds_from_hit"), []))}), '
              f'painted {100 * S[sd, "painted"] / n:3.0f}%, marked/completed {100 * S[sd, "worked"] / n:3.0f}%, none of these {100 * S[sd, "idle"] / n:3.0f}%; paint 30 rounds before med {lib.med(S.get((sd, "paint30"), []))}')
        print(f'      at 0 paint: nearest own tower d2 med {lib.med(S.get((sd, "d_tower"), []))} (in sight {100 * S[sd, "in_sight"] / n:3.0f}%, a money tower {100 * S[sd, "near_money"] / n:3.0f}%, its paint med {lib.med(S.get((sd, "tower_paint"), []))}); '
              f'nearest own paint tower d2 med {lib.med(S.get((sd, "d_paint"), []))}, none alive {100 * S[sd, "no_paint_tower"] / n:3.0f}%; age at 0 paint {S[sd, "age"] / n:5.1f} rounds')
print('\n== defense towers built per game (us / them) and our soldiers killed by towers with a defense tower among the damage dealers, per opponent')
for o in sorted({k[0] for k in per}):
    g = max(1, per[o, 'games'])
    print(f'  {o:26s} {per[o, "games"]:3d} g  defense towers {per[o, "def_us"] / g:4.2f} / {per[o, "def_them"] / g:4.2f}   our soldiers killed by towers {per[o, "killed"] / g:5.1f}/g, '
          f'with a defense tower {100 * per[o, "killed_def"] / max(1, per[o, "killed"]):3.0f}%')

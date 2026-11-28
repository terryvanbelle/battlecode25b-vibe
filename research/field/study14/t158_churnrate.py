"""Topic 158: did the churn-wait starvation of study 13 2.1 shrink?  (t156's events, normalised and split by version.)
y323 = y316 + Tune.CHURN_WAIT_ROUNDS 2 (was 3); y328 = y323 + DRY_ROUNDS 60 (no replay of y328 yet).  t160 added the
Nav ally term (Nav.tileCost counts our robots and towers within d2 2 of a tile), which may also keep robots off a
tower's side.  Every game of every version, wins and losses together (the counts grow with game length, so they are
given per 1000 of our robot-turns), repeats left out.  Study 13's t140 / t158 games come from S14SET=prev.
Per version:
  hit0 beside       our robots that hit 0 paint (0 now, > 0 on the previous turn) within d2 2 of an own tower
  ... churn case    of them, beside a money tower holding < 10 paint (Tune.CHURN_PAINT) while we held 2000+ chips
                    (Churn.churnable: the churn wait of Unit.refill)
  turns beside dry  our robot-turns within d2 2 of an own money tower holding < 10 paint, 2000+ chips
  stay              runs of consecutive turns a robot spends beside the same drained money tower (2000+ chips):
                    median length, share of runs of 3+ turns, share of runs that end with the robot at 0 paint
  churns            own money towers removed without a kill ('died' row) and rebuilt on the same tile within 2 rounds,
                    per 1000 rounds of game
  arrive            paint of the robot on its first turn of a stay (median)
Per opponent too (all versions with 3+ games against it), so a version is compared with the others on the same team."""
from collections import defaultdict, Counter
import os
import lib

SETS = (('prev', ('t140', 't158')), ('main', ('t158', 't160', 'y316', 'y323')))


def analyse(G, S):
    tow = defaultdict(list); bots = defaultdict(list)
    for t in G.turns:
        (tow if t[3] in lib.TOW else bots)[t[0]].append(t)
    prev = {}; run = {}
    for r in sorted(bots):
        rich = lib.money(G, G.us, r) >= 2000
        tw = [u for u in tow.get(r, ()) if u[2] == G.us]
        for t in bots[r]:
            if t[2] != G.us: continue
            S['turns'] += 1
            own = [u for u in tw if (u[4] - t[4]) ** 2 + (u[5] - t[5]) ** 2 <= 2]
            dry = [u for u in own if u[3] == 'MONEY_TOWER' and u[7] < 10]
            if dry and rich: S['adjdry'] += 1
            q = (dry[0][4], dry[0][5]) if dry and rich else None
            rr = run.get(t[1])
            if q and rr and rr[0] == q:
                run[t[1]] = (q, rr[1] + 1, rr[2])
            else:
                if rr: S.setdefault('runs', []).append((rr[1], prev.get(t[1], 1) == 0, rr[2]))
                run[t[1]] = (q, 1, t[7]) if q else None
            p0 = prev.get(t[1]); prev[t[1]] = t[7]
            if t[7] == 0 and p0:
                S['hit0'] += 1
                if own: S['hit0_beside'] += 1
                if q: S['hit0_churn'] += 1
    for rid, rr in run.items():
        if rr: S.setdefault('runs', []).append((rr[1], prev.get(rid, 1) == 0, rr[2]))
    # churns: an own money tower 'died' (no kill) and an own build on the same tile within 2 rounds
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    builds = defaultdict(list)
    for a in G.acts:
        if a[4] == 'build' and a[2] == G.us:
            p = pos.get(int(a[5]))
            if p: builds[p].append(a[0])
    for a in G.acts:
        if a[4] == 'died' and a[2] == G.us and a[3] == 'MONEY_TOWER':
            p = pos.get(a[1])
            if p and any(0 <= b - a[0] <= 2 for b in builds.get(p, ())): S['churns'] += 1
    S['rounds'] += G.end
    S['games'] += 1


def line(tag, S):
    k = 1000 / max(1, S['turns'])
    runs = S.get('runs', [])
    n = max(1, len(runs))
    return (f'{tag:34s} {int(S["games"]):3d} g  hit0 beside {S["hit0_beside"] * k:5.2f}  churn case {S["hit0_churn"] * k:5.2f}  '
            f'(of all hit0 {100 * S["hit0_churn"] / max(1, S["hit0"]):3.0f}%)  turns beside dry {S["adjdry"] * k:5.1f}  '
            f'stay med {lib.med([x[0] for x in runs])} 3+ {100 * sum(1 for x in runs if x[0] >= 3) / n:3.0f}% '
            f'end at 0 {100 * sum(1 for x in runs if x[1]) / n:3.0f}%  arrive {lib.med([x[2] for x in runs])}  '
            f'churns/1000r {1000 * S["churns"] / max(1, S["rounds"]):4.1f}')


print('per 1000 of our robot-turns, all games (wins + losses), repeats left out')
allS = {}
for st, vers in SETS:
    os.environ['S14SET'] = st
    for v in vers:
        for which in ('all', 'lost', 'won'):
            S = defaultdict(float)
            byteam = defaultdict(lambda: defaultdict(float))
            for G in lib.games(which, vers=[v]):
                analyse(G, S)
                if which == 'all': analyse(G, byteam[G.team_name])
            print(line(f'{v} ({"study 13" if st == "prev" else "study 14"}) {which}', S))
            if which == 'all': allS[(st, v)] = byteam
    print()
print('per opponent, all games: churn case per 1000 robot-turns (games)')
teams = sorted(set(t for d in allS.values() for t in d))
print(f'{"":26s}' + ''.join(f'{v + ("/13" if st == "prev" else ""):>16s}' for (st, v) in allS))
for tm in teams:
    cells = []
    for key, d in allS.items():
        S = d.get(tm)
        cells.append(f'{S["hit0_churn"] * 1000 / max(1, S["turns"]):6.2f} ({int(S["games"]):2d})' if S and S['games'] else '-')
    print(f'{tm:26s}' + ''.join(f'{c:>16s}' for c in cells))

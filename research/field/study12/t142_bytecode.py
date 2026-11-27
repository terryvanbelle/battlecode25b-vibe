"""Topic 142: how much computation each side uses (new).  turns.tsv 'bc' = bytecodes used in the turn (robot limit
17500, tower limit 20000; GameConstants).  A turn at the limit was cut off mid-turn (the engine resumes the robot's
code next turn: whatever it was doing is late by a turn).  Per side, type and phase, losses and wins together: mean
and median bytecodes, the 90th percentile, the share of turns over 50% / 90% of the limit and at the limit; and per
opponent the mean robot bytecodes (who computes more than us) with the game summary's exceptions and atLimit counts."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
LIM = {'SOLDIER': 17500, 'SPLASHER': 17500, 'MOPPER': 17500, 'PAINT_TOWER': 20000, 'MONEY_TOWER': 20000, 'DEFENSE_TOWER': 20000}


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


S = defaultdict(list)
per_team = defaultdict(lambda: defaultdict(list))
summ = defaultdict(lambda: defaultdict(int))
ng = 0
for G in lib.games('all'):
    ng += 1
    X = lib.extra(G)
    for t, e in zip(G.turns, X):
        p = ph(t[0])
        if p is None: continue
        side = 'us' if t[2] == G.us else 'them'
        typ = t[3] if t[3] in lib.BOT else 'TOWER'
        S[(side, typ, p)].append(e[2] / LIM[t[3]])
        if t[3] in lib.BOT:
            per_team[G.team_name]['us' if side == 'us' else 'them'].append(e[2])
    o = 'A' if G.op == 1 else 'B'; u = 'B' if o == 'A' else 'A'
    summ[G.team_name]['games'] += 1
    for k in ('exceptions', 'atLimit'):
        summ[G.team_name][k + '_us'] += G.sm.get(k + u, 0) or 0
        summ[G.team_name][k + '_them'] += G.sm.get(k + o, 0) or 0
print(f'{ng} games (wins and losses).  Share of the type\'s limit:')
print('   type      phase     side      turns   mean   median   p90    >50%    >90%   at limit')
for typ in lib.BOT + ('TOWER',):
    for p in range(3):
        for side in ('us', 'them'):
            L = sorted(S[(side, typ, p)])
            if not L: continue
            n = len(L)
            print(f'   {typ:9s} {PHN[p]:9s} {side:4s} {n:10d}  {100 * sum(L) / n:5.1f}%  {100 * L[n // 2]:5.1f}%  {100 * L[int(.9 * n)]:5.1f}%  {100 * sum(1 for v in L if v > .5) / n:5.1f}%  {100 * sum(1 for v in L if v > .9) / n:5.1f}%  {100 * sum(1 for v in L if v >= .999) / n:6.2f}%')
print('\nper opponent: mean robot bytecodes per turn (us / them), exceptions and at-limit turns per game (us / them)')
for team in sorted(per_team, key=lambda k: -sum(per_team[k]['them']) / max(1, len(per_team[k]['them']))):
    D = per_team[team]; s = summ[team]; n = s['games']
    print(f'   {team[:24]:24s} {n:3d} games  bytecodes {sum(D["us"]) / max(1, len(D["us"])):6.0f} / {sum(D["them"]) / max(1, len(D["them"])):6.0f}'
          f'   exceptions {s["exceptions_us"] / n:5.1f} / {s["exceptions_them"] / n:5.1f}   at limit {s["atLimit_us"] / n:6.1f} / {s["atLimit_them"] / n:6.1f}')

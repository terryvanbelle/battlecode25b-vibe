"""Topic 156: robots that run out of paint (new: t106 has us famine-bound with chips banked, and the t143 counts show
three top teams disintegrating robots).  RULES 3: a robot at 0 paint can neither act nor move, so it cannot withdraw
from a tower again; only a mopper can save it.  RULES 5.3: it then loses 20 HP a turn (a soldier lives 13 more turns,
a splasher 8, a mopper 3), and every ally within r2 2 of it pays 1 paint a turn for it (2 on enemy paint).  An ally
TOWER counts as an adjacent ally, so a robot waiting beside a tower pays 1 a turn on its own paint.
Per side, losses then wins (turn rows are end-of-turn state):
  A. robot-turns per game; turns spent at 0 paint (stuck) by type; own robots within r2 2 of a stuck robot
  B. robots that hit 0 paint (0 now, more than 0 on their previous turn), by type, and where: beside an own tower
     (r2 2), the tower's type, our chips then (2000+ = Churn.churnable, the churn wait of Unit.refill); an own tower in
     sight (r2 20); none in sight.  For the ones beside a tower: rounds already spent beside it, paint on arrival
  C. robot-turns spent beside an own money tower holding under 10 paint (Tune.CHURN_PAINT: drained) per game
  D. deaths without an attacker: starved (a die row whose actor is the victim: the 0-paint damage) and disintegrated
     (a died row: rc.disintegrate); per type, and the disintegrations per opponent"""
from collections import defaultdict, Counter
import lib


def analyse(G, S, C, stay, arr, DIS):
    tow = defaultdict(list); bots = defaultdict(list)
    for t in G.turns:
        (tow if t[3] in lib.TOW else bots)[t[0]].append(t)
    prev = {}; run = {}
    for r in sorted(bots):
        ts = bots[r]
        tw = tow.get(r, ())
        for t in ts:
            side = 'us' if t[2] == G.us else 'them'
            S[(side, 'turns')] += 1
            own = [u for u in tw if u[2] == t[2] and (u[4] - t[4]) ** 2 + (u[5] - t[5]) ** 2 <= 2]
            if own and own[0][3] == 'MONEY_TOWER' and own[0][7] < 10: S[(side, 'adj_dry_money')] += 1
            q = (own[0][4], own[0][5]) if own else None
            rr = run.get(t[1])
            if q and rr and rr[0] == q: run[t[1]] = (q, rr[1] + 1, rr[2])
            elif q: run[t[1]] = (q, 1, prev.get(t[1], t[7]))
            else: run[t[1]] = None
            p0 = prev.get(t[1]); prev[t[1]] = t[7]
            if t[7] == 0:
                S[(side, 'stuck')] += 1; S[(side, 'stuck', t[3])] += 1
                S[(side, 'stuck_adj')] += sum(1 for u in ts if u is not t and u[2] == t[2]
                                              and (u[4] - t[4]) ** 2 + (u[5] - t[5]) ** 2 <= 2)
            if t[7] != 0 or p0 is None or p0 == 0: continue
            S[(side, 'hit')] += 1; S[(side, 'hit', t[3])] += 1
            if own:
                u = own[0]
                S[(side, 'beside')] += 1
                if u[7] >= 50: S[(side, 'beside50')] += 1
                C[(side, u[3], '2000+' if lib.money(G, t[2], r) >= 2000 else 'under 2000')] += 1
                stay[side].append(run[t[1]][1]); arr[side].append(run[t[1]][2])
            else:
                see = [u[7] for u in tw if u[2] == t[2] and (u[4] - t[4]) ** 2 + (u[5] - t[5]) ** 2 <= 20]
                if see:
                    S[(side, 'sight')] += 1
                    if max(see) >= 50: S[(side, 'sight50')] += 1
                else: S[(side, 'far')] += 1
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.BOT and int(a[5]) == a[1]:
            S[('us' if a[2] == G.us else 'them', 'starved', a[7])] += 1
        elif a[4] == 'died' and a[3] in lib.BOT:
            side = 'us' if a[2] == G.us else 'them'
            S[(side, 'disint', a[3])] += 1
            if side == 'them': DIS[G.team_name] += 1


for which in ('lost', 'won'):
    S = defaultdict(float); C = Counter(); stay = defaultdict(list); arr = defaultdict(list); DIS = Counter()
    ng = 0; per_team = Counter()
    for G in lib.games(which):
        analyse(G, S, C, stay, arr, DIS); ng += 1; per_team[G.team_name] += 1
    print(f'\n== {which}: {ng} games')
    for side in ('us', 'them'):
        n = max(1, S[(side, 'hit')])
        print(f'  {side}:')
        print(f'    A. robot-turns per game {S[(side, "turns")] / ng:.0f}; at 0 paint {S[(side, "stuck")] / ng:.1f} '
              f'({100 * S[(side, "stuck")] / max(1, S[(side, "turns")]):.1f}%): '
              + ', '.join(f'{ty.lower()} {S[(side, "stuck", ty)] / ng:.1f}' for ty in lib.BOT)
              + f'; own robots within r2 2 of a stuck robot {S[(side, "stuck_adj")] / max(1, S[(side, "stuck")]):.2f}')
        print(f'    B. hit 0 paint per game {S[(side, "hit")] / ng:.1f} ('
              + ', '.join(f'{ty.lower()} {S[(side, "hit", ty)] / ng:.1f}' for ty in lib.BOT) + ')')
        print(f'       beside an own tower {100 * S[(side, "beside")] / n:.0f}% ({S[(side, "beside")] / ng:.1f} a game; '
              f'that tower holding 50+ paint {100 * S[(side, "beside50")] / n:.0f}%); own tower in sight '
              f'{100 * S[(side, "sight")] / n:.0f}% (50+ paint {100 * S[(side, "sight50")] / n:.0f}%); none in sight '
              f'{100 * S[(side, "far")] / n:.0f}%')
        tot = sum(v for k, v in C.items() if k[0] == side)
        print('       beside: ' + ', '.join(f'{k[1].lower()} with chips {k[2]} {100 * v / max(1, tot):.0f}%'
                                           for k, v in sorted(C.items()) if k[0] == side))
        print(f'       beside: rounds already beside it (median) {lib.med(stay[side])}, paint on arrival (median) {lib.med(arr[side])}')
        print(f'    C. robot-turns beside an own drained money tower (< 10 paint) per game {S[(side, "adj_dry_money")] / ng:.0f}')
        print(f'    D. starved per game: ' + ', '.join(f'{ty.lower()} {S[(side, "starved", ty)] / ng:.2f}' for ty in lib.BOT)
              + '; disintegrated per game: ' + ', '.join(f'{ty.lower()} {S[(side, "disint", ty)] / ng:.2f}' for ty in lib.BOT))
    print('  their disintegrated robots per game, by opponent: '
          + ', '.join(f'{tm} {DIS[tm] / per_team[tm]:.1f} ({per_team[tm]} g)' for tm in sorted(per_team) if DIS[tm]))

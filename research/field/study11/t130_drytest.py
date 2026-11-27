"""Topic 130: what t122's dry-flag change did.  t122 (Unit.java:23-30) lets a PAINT tower's dry flag expire after 10
rounds (was 40) and drops a flag when the flagged tower is in sight holding 50+ paint, so robots come back to a paint
tower sooner.  Per our version (t111 / t118 in study 10's set, t122 now) and the opponents (all versions pooled),
lost and won games, phases r1-100 / r101-200 / r201-400, from turns.tsv and actions.tsv:
  PT-turns         paint-tower turns; share ending with < 50 / < 200 / >= 900 paint
  wd/PT-turn       paint robots withdrew from paint towers, per paint-tower turn ('transfer' rows with a negative amount
                   whose target is a paint tower); and withdrawals from money towers per money-tower turn
  spawn/PT-turn    paint spent on spawns by paint towers per paint-tower turn (S 200, X 300, M 100)
  wait-dry         robot-turns ending within d2 2 of an own paint tower that ended its last turn with < 50 paint, per 100
                   robot-turns of the side (robots queueing at an empty paint tower)
  leave            the robot's paint after a withdrawal from a paint tower, as a share of its capacity (median)
Sums over the games (rates from the sums)."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 400))
SC = {'SOLDIER': 200, 'SPLASHER': 300, 'MOPPER': 100}


def analyse(G, S):
    last_tp = {}   # tower id -> (paint, type, team, x, y) at its latest turn
    ph_of = lambda r: next((i for i, (lo, hi) in enumerate(PH) if lo <= r <= hi), None)
    acts = defaultdict(list)
    for a in G.acts:
        if a[4] in ('transfer', 'spawn'): acts[a[0]].append(a)
    rt = lib.by_round_turns(G)
    for r in range(1, min(G.end, 400) + 1):
        j = ph_of(r)
        ptpos = defaultdict(list)   # paint towers alive this round (they take a turn every round), end-of-turn paint
        for t in rt.get(r, ()):
            if t[3] == 'PAINT_TOWER': ptpos[t[2]].append((t[4], t[5], t[7]))
        for t in rt.get(r, ()):
            side = t[2]; k = (side, j)
            if t[3] == 'PAINT_TOWER':
                S[k]['pt_turns'] += 1; S[k]['pt<50'] += t[7] < 50; S[k]['pt<200'] += t[7] < 200; S[k]['pt>=900'] += t[7] >= 900
            elif t[3] == 'MONEY_TOWER':
                S[k]['mt_turns'] += 1
            elif t[3] in lib.BOT:
                S[k]['robot_turns'] += 1
                for (x, y, p) in ptpos.get(side, ()):
                    if p < 50 and (x - t[4]) ** 2 + (y - t[5]) ** 2 <= 2: S[k]['wait_dry'] += 1; break
        for a in acts.get(r, ()):
            side = a[2]; k = (side, j)
            if a[4] == 'transfer':
                amt = int(a[6] or 0); tgt = int(a[5])
                if amt < 0 and G.typ.get(tgt) == 'PAINT_TOWER':
                    S[k]['wd_pt'] += -amt; S[k]['wd_pt_n'] += 1
                elif amt < 0 and G.typ.get(tgt) == 'MONEY_TOWER':
                    S[k]['wd_mt'] += -amt
            elif a[4] == 'spawn' and a[3] == 'PAINT_TOWER' and a[6] in SC:
                S[k]['spawn_pt'] += SC[a[6]]
    # paint left after a paint-tower withdrawal (robot's end-of-turn paint / capacity)
    endp = {(t[0], t[1]): (t[7], t[3]) for t in G.turns if t[3] in lib.BOT}
    for a in G.acts:
        if a[4] == 'transfer' and int(a[6] or 0) < 0 and G.typ.get(int(a[5])) == 'PAINT_TOWER' and a[0] <= 400:
            e = endp.get((a[0], a[1]))
            if e and e[1] in SC: S[(a[2], ph_of(a[0]))]['leave'].append(100 * e[0] / SC[e[1]])


for which in ('lost', 'won'):
    print(f'\n== {which} games')
    for label, ms, vers in (('t111', lib.PREV, ['t111']), ('t118', lib.PREV, ['t118']), ('t122', lib.MAIN, ['t122'])):
        S = defaultdict(lambda: defaultdict(float)); n = 0
        for k in list(S): pass
        for G in lib.games(which, matches=ms, vers=vers):
            n += 1
            T = defaultdict(lambda: defaultdict(float))
            for j in range(len(PH)):
                for sd in (1, 2): T[(sd, j)]['leave'] = []
            analyse(G, T)
            for (sd, j), m in T.items():
                who = 'us' if sd == G.us else 'them'
                for kk, v in m.items():
                    if kk == 'leave':
                        S[(who, j)].setdefault('leave_l', []); S[(who, j)]['leave_l'] += v
                    else: S[(who, j)][kk] += v
            lib.lite(G)
        print(f'   {label} ({n} games)')
        for who in ('us', 'them'):
            cells = []
            for j, (lo, hi) in enumerate(PH):
                m = S[(who, j)]; pt = max(1, m['pt_turns']); mt = max(1, m['mt_turns']); rb = max(1, m['robot_turns'])
                cells.append(f'r{lo}-{hi}: PT<50 {100 * m["pt<50"] / pt:4.1f}% <200 {100 * m["pt<200"] / pt:4.1f}% >=900 {100 * m["pt>=900"] / pt:4.1f}%  '
                             f'wd/PT-turn {m["wd_pt"] / pt:4.1f} (n {int(m["wd_pt_n"])})  wd/MT-turn {m["wd_mt"] / mt:4.1f}  spawn/PT-turn {m["spawn_pt"] / pt:4.1f}  '
                             f'wait-dry {100 * m["wait_dry"] / rb:4.2f}/100rt  leave {lib.med(m.get("leave_l", []))}%')
            print(f'      {who:4s} ' + '\n           '.join(cells))

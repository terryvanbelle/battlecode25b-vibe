"""Topic 117: robots that sit with almost no paint while an own tower near them holds paint.  Unit.refill
(Unit.java:23) skips a tower for 40 rounds after it was seen with little paint (markDry at Unit.java:47 and :52), even a
PAINT tower, which regains 5-10 paint a round (RULES 7), and even when the tower is in sight with paint again; with no
other tower left, refill returns false and Soldier.workRuin (Soldier.java:214-218) still ends the turn, so a soldier with
< 10 paint on a ruin stands still.  Per robot-turn of each side (turns.tsv, end of turn):
  low      paint below 10% of capacity (soldier < 20, splasher < 30, mopper < 10)
  stuck    low, on the same tile as at its previous turn, and no paint gained since then
  with an own tower holding >= 50 paint (its latest turn row) within d2 <= 20 (in sight) / within d2 <= 100 (near)
Shares of the side's robot-turns, by phase; lost and won games; and stuck spells (>= 10 consecutive stuck turns of one
robot with a paint-holding own tower in sight), with the tower's type."""
import lib
from collections import Counter, defaultdict

PH = ((1, 100, 'r1-100'), (101, 200, 'r101-200'), (201, 400, 'r201-400'), (401, 2000, 'r401+'))
CAP = {'SOLDIER': 200, 'SPLASHER': 300, 'MOPPER': 100}


def analyse(G):
    bt = lib.by_round_turns(G)
    tpaint = {}                     # tower id -> (pos, paint, type, side), latest row
    dead = set(int(a[5]) for a in G.acts if a[4] == 'die')
    died_round = {}
    for a in G.acts:
        if a[4] == 'die': died_round[int(a[5])] = a[0]
    b, d = lib.tower_events(G)
    gone = {x[1]: x[0] for x in d}
    last = {}
    C = {1: defaultdict(Counter), 2: defaultdict(Counter)}
    spell = {}                      # robot id -> (start round, length, tower type)
    spells = {1: [], 2: []}
    for r in range(1, G.end + 1):
        ph = next(p[2] for p in PH if p[0] <= r <= p[1])
        T = bt.get(r, ())
        for t in T:
            if t[3] in lib.TOW: tpaint[t[1]] = ((t[4], t[5]), t[7], t[3], t[2])
        for tid in [k for k, v in tpaint.items() if gone.get(k, 10 ** 6) <= r]: del tpaint[tid]
        for t in T:
            if t[3] not in lib.BOT: continue
            s = t[2]; c = C[s][ph]
            c['turns'] += 1
            prev = last.get(t[1]); last[t[1]] = ((t[4], t[5]), t[7])
            low = t[7] < CAP[t[3]] // 10
            if not low:
                if t[1] in spell:
                    st = spell.pop(t[1])
                    if st[1] >= 10: spells[s].append(st)
                continue
            c['low'] += 1
            stuck = prev is not None and prev[0] == (t[4], t[5]) and t[7] <= prev[1]
            near = sight = None
            for (pos, p, ty, side) in tpaint.values():
                if side != s or p < 50: continue
                dd = lib.d2(pos, (t[4], t[5]))
                if dd <= 20: sight = ty; break
                if dd <= 100 and near is None: near = ty
            if sight: c['low, paint-holding own tower in sight'] += 1
            elif near: c['low, paint-holding own tower within d2 100'] += 1
            if stuck:
                c['stuck'] += 1
                if sight:
                    c['stuck, paint-holding own tower in sight'] += 1
                    c[f'stuck in sight of a {sight[:5]}'] += 1
                    c[f'stuck in sight, {t[3][:2]}'] += 1
                    st = spell.get(t[1])
                    spell[t[1]] = (st[0], st[1] + 1, st[2]) if st else (r, 1, sight)
                elif near: c['stuck, paint-holding own tower within d2 100'] += 1
                if not sight and t[1] in spell:
                    st = spell.pop(t[1])
                    if st[1] >= 10: spells[s].append(st)
            elif t[1] in spell:
                st = spell.pop(t[1])
                if st[1] >= 10: spells[s].append(st)
    for rid, st in spell.items():
        s = next((t[2] for t in G.turns if t[1] == rid), None)
        if s and st[1] >= 10: spells[s].append(st)
    return C, spells


KEYS = ('low', 'low, paint-holding own tower in sight', 'low, paint-holding own tower within d2 100', 'stuck',
        'stuck, paint-holding own tower in sight', 'stuck in sight of a PAINT', 'stuck in sight of a MONEY', 'stuck in sight of a DEFEN',
        'stuck in sight, SO', 'stuck in sight, SP', 'stuck in sight, MO', 'stuck, paint-holding own tower within d2 100')
for which in ('lost', 'won'):
    T = {'us': defaultdict(Counter), 'them': defaultdict(Counter)}; n = 0
    SP = {'us': [], 'them': []}; per = []
    for G in lib.games(which):
        C, spells = analyse(G); n += 1
        for k, s in (('us', G.us), ('them', G.op)):
            for ph, c in C[s].items(): T[k][ph].update(c)
            SP[k] += spells[s]
        if which == 'lost':
            u = sum((C[G.us][p[2]] for p in PH), Counter())
            per.append((u['stuck, paint-holding own tower in sight'], f'   m{G.m}g{G.g} {G.ver:5s} {G.team_name[:12]:12s} {G.map[:14]:14s} {G.wintype[:3]}{G.end:<5d} '
                        f'stuck in sight {u["stuck, paint-holding own tower in sight"]:4d} (PT {u["stuck in sight of a PAINT"]}, MT {u["stuck in sight of a MONEY"]}), '
                        f'spells >= 10 {len(spells[G.us])} (longest {max([x[1] for x in spells[G.us]], default=0)})'))
        lib.lite(G)
    print(f'\n== {which.upper()} games: {n}; robot-turns, us / them (share of the side\'s robot-turns in the phase)')
    for k in KEYS:
        row = ''
        for p in PH:
            u = T['us'][p[2]]; t = T['them'][p[2]]
            row += f'{u[k]:7d} ({100 * u[k] / max(1, u["turns"]):4.1f}%) / {t[k]:6d} ({100 * t[k] / max(1, t["turns"]):4.1f}%) '
        print(f'   {k:46s}{row}')
    print('   robot-turns: ' + ', '.join(f'{p[2]} us {T["us"][p[2]]["turns"]} them {T["them"][p[2]]["turns"]}' for p in PH))
    for k in ('us', 'them'):
        S = SP[k]
        print(f'   {k}: stuck spells of >= 10 turns in sight of a paint-holding own tower: {len(S)}, robot-turns {sum(x[1] for x in S)}, '
              f'median length {lib.med([x[1] for x in S])}, median start r{lib.med([x[0] for x in S])}, tower types {dict(Counter(x[2][:5] for x in S))}')
    if per:
        per.sort(key=lambda x: -x[0])
        print('   lost games with the most stuck turns in sight (ours):')
        for x in per[:15]: print(x[1])

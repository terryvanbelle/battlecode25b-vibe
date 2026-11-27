"""Topic 120: where each side's paint goes through its towers.  Money towers make no paint: the 500 they are built
with is all they ever hold unless a robot gives them some (RULES 7), and it is also the only paint they can spawn
from.  So a robot that refills at a money tower takes paint the tower could have turned into a unit.
Per side and phase (r1-100, r101-200, r201-400), medians per game and sums, lost and won games:
  wd P / wd M        paint withdrawn by robots from paint / money towers ('transfer' rows with a negative amount)
  give T             paint robots gave to towers (positive transfers to a tower)
  give R             paint robots gave to robots (moppers feeding)
  spawn P / spawn M  paint spent on spawns by paint / money towers (S 200, X 300, M 100)
  M spawns           units spawned by money towers
and per money tower built after r0 that lived 60+ rounds: where its first 500 paint went in its first 60 rounds
(spawns / withdrawals), and the share of paint-tower turns at 900+ paint (income lost at the 1000 cap) and below 200."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 400))
PAINT = {'SOLDIER': 200, 'SPLASHER': 300, 'MOPPER': 100}


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def analyse(G):
    out = {s: defaultdict(float) for s in (1, 2)}
    tt = lambda i: G.typ.get(i, '')
    spawner = {}
    for a in G.acts:
        k = a[4]
        if k == 'transfer':
            p = ph(a[0])
            if p is None: continue
            tgt = int(a[5]); amt = int(a[6])
            if amt == 0: continue   # amount 0 = completeResourcePattern (RULES schema note)
            ty = tt(tgt)
            if amt < 0 and ty in lib.TOW:
                out[a[2]][(p, 'wd ' + ty[0])] += -amt
                out[a[2]][(p, 'wd by ' + a[3][:3])] += -amt
            elif amt > 0 and ty in lib.TOW:
                out[a[2]][(p, 'give T')] += amt
            elif amt > 0:
                out[a[2]][(p, 'give R')] += amt
        elif k == 'spawn':
            p = ph(a[0])
            if p is None: continue
            if a[3] in lib.TOW and a[6] in PAINT:
                out[a[2]][(p, 'spawn ' + a[3][0])] += PAINT[a[6]]
                out[a[2]][(p, a[3][0] + ' spawns')] += 1
    # paint-tower turns near the cap / low
    for t in G.turns:
        if t[3] == 'PAINT_TOWER':
            p = ph(t[0])
            if p is None: continue
            out[t[2]][(p, 'pt turns')] += 1
            if t[7] >= 900: out[t[2]][(p, 'pt 900+')] += 1
            if t[7] < 200: out[t[2]][(p, 'pt <200')] += 1
    return out


def money_towers(G):
    """Per money tower built after r0 that lived 60+ rounds: paint spent on spawns and withdrawn in its first 60 rounds."""
    b, d = lib.tower_events(G)
    died = {x[1]: x[0] for x in d}
    res = []
    born = {x[1]: (x[0], x[3]) for x in b if x[0] > 0 and x[2] == 'MONEY_TOWER'}
    if not born: return res
    sp = defaultdict(int); wd = defaultdict(int)
    for a in G.acts:
        if a[4] == 'spawn' and a[1] in born and a[0] - born[a[1]][0] <= 60:
            sp[a[1]] += PAINT.get(a[6], 0)
        elif a[4] == 'transfer':
            tgt = int(a[5]); amt = int(a[6])
            if tgt in born and amt < 0 and a[0] - born[tgt][0] <= 60: wd[tgt] += -amt
    for i, (r0, side) in born.items():
        if died.get(i, 10 ** 6) - r0 < 60 or G.end - r0 < 60: continue
        res.append((side, sp[i], wd[i]))
    return res


KEYS = ('wd P', 'wd M', 'wd by SOL', 'wd by SPL', 'wd by MOP', 'give T', 'give R', 'spawn P', 'spawn M', 'M spawns',
        'P spawns')
for which in ('lost', 'won'):
    per = defaultdict(list)
    mts = []
    n = 0
    for G in lib.games(which):
        n += 1
        o = analyse(G)
        for side, who in ((G.us, 'us'), (G.op, 'them')):
            for p in range(3):
                if G.end < PH[p][0]: continue
                for k in KEYS + ('pt turns', 'pt 900+', 'pt <200'):
                    per[(who, p, k)].append(o[side].get((p, k), 0))
        for side, s, w in money_towers(G):
            mts.append(('us' if side == G.us else 'them', s, w))
        lib.lite(G)
    print(f'\n== {which} games ({n}): medians per game (sums), us | them')
    for p in range(3):
        print(f'   r{PH[p][0]}-{PH[p][1]}  ({len(per[("us", p, "wd P")])} games)')
        for k in KEYS:
            u = per[('us', p, k)]; t = per[('them', p, k)]
            print(f'      {k:10s} {lib.med(u)!s:>7} ({int(sum(u)):7d}) | {lib.med(t)!s:>7} ({int(sum(t)):7d})')
        for who in ('us', 'them'):
            tt = sum(per[(who, p, 'pt turns')]); hi = sum(per[(who, p, 'pt 900+')]); lo = sum(per[(who, p, 'pt <200')])
            print(f'      {who:4s} paint-tower turns {int(tt)}: at 900+ paint {100 * hi / max(1, tt):.1f}%, below 200 {100 * lo / max(1, tt):.1f}%')
    for who in ('us', 'them'):
        M = [x for x in mts if x[0] == who]
        if not M: continue
        print(f'   {who}: {len(M)} money towers built after r0 that lived 60+ rounds; in their first 60 rounds, paint spent on '
              f'spawns med {lib.med([x[1] for x in M])} (sum {sum(x[1] for x in M)}), withdrawn by robots med {lib.med([x[2] for x in M])} '
              f'(sum {sum(x[2] for x in M)}); towers that spawned nothing {sum(1 for x in M if x[1] == 0)}')

"""Topic 93: which enemy towers each side attacks.  Robot HP damage on towers ('damage' rows by soldiers and splashers)
split by the target's type (paint / money / defense), next to the share of the target side's standing towers of
that type (tower-rounds), per phase r1-150 / r151+; and the type of the first enemy tower each side killed.  A side
that puts more of its damage on paint towers than their share of the standing towers prefers them."""
import lib
from collections import defaultdict, Counter


for which in ('lost', 'won'):
    D = defaultdict(Counter); A = defaultdict(Counter); F = defaultdict(Counter); n = 0
    for G in lib.games(which):
        n += 1
        b, d = lib.tower_events(G)
        dead = {x[1]: x[0] for x in d}
        for x in b:
            r1 = dead.get(x[1], G.end)
            for lo, hi, ph in ((1, 150, 'r1-150'), (151, 99999, 'r151+')):
                k = max(0, min(r1, hi) - max(x[0], lo) + 1)
                if k: A[('us' if x[3] == G.us else 'them', ph)][x[2][0]] += k
        first = {}
        for a in G.acts:
            if a[4] == 'damage' and a[3] in ('SOLDIER', 'SPLASHER'):
                t = G.typ.get(int(a[5]), '?')
                if t not in lib.TOW: continue
                side = 'us' if a[2] == G.us else 'them'
                D[(side, 'r1-150' if a[0] <= 150 else 'r151+')][t[0]] += int(a[6])
            elif a[4] == 'die' and a[7] in lib.TOW and a[3] in lib.BOT:
                side = 'us' if a[2] == G.us else 'them'
                if side not in first: first[side] = a[7][0]
        for side, t in first.items(): F[side][t] += 1
    print(f'== {which} games ({n})')
    for side, other in (('us', 'them'), ('them', 'us')):
        for ph in ('r1-150', 'r151+'):
            dd = D[(side, ph)]; aa = A[(other, ph)]
            td = sum(dd.values()); ta = sum(aa.values())
            print(f'   {side:4s} {ph:7s}: damage on P/M/D {dd["P"]}/{dd["M"]}/{dd["D"]} = {100 * dd["P"] / max(1, td):.0f}% on paint towers; '
                  f'paint towers are {100 * aa["P"] / max(1, ta):.0f}% of {other}\'s standing tower-rounds (defense {100 * aa["D"] / max(1, ta):.0f}%)')
        print(f'   {side:4s} first tower kill by type: {dict(F[side])}')
    print()

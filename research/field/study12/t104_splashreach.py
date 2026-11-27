"""Topic 104: from where splashers hit towers.  A splash centre lies within d2 4 of the splasher and damages towers
within d2 4 of the centre, so a splasher can hit a tower from up to d2 16 (4 tiles in a straight line), while paint
and money towers shoot only to d2 9 (defense towers d2 16).  For every 'damage' row by a splasher on a tower: the
splasher's position that round (its turn row) and the tower's, by d2 band (<= 9 = inside the tower's own range for
paint and money towers, 10-16 = outside it), the tower type, and the share of all splasher damage dealt from outside.
Both sides, lost and won games."""
import lib
from collections import defaultdict, Counter


for which in ('lost', 'won'):
    C = defaultdict(Counter)
    for G in lib.games(which):
        pos = {}
        for t in G.turns: pos[(t[0], t[1])] = (t[4], t[5])
        tpos = {}
        for t in G.turns:
            if t[3] in lib.TOW and t[1] not in tpos: tpos[t[1]] = (t[4], t[5])
        for a in G.acts:
            if a[4] != 'damage' or a[3] != 'SPLASHER': continue
            tid = int(a[5])
            if tid not in tpos: continue
            p = pos.get((a[0], a[1]))
            if p is None: continue
            d = lib.d2(p, tpos[tid])
            side = 'us' if a[2] == G.us else 'them'
            typ = G.typ.get(tid, '?')[:1]
            band = 'd2 <= 9' if d <= 9 else ('d2 10-16' if d <= 16 else 'd2 > 16')
            C[side][(band, typ)] += int(a[6] or 0)
            C[side][('all', typ)] += int(a[6] or 0)
    print(f'== {which} games: splasher damage on towers (HP) by the splasher\'s distance from the tower (attacker side)')
    for side in ('us', 'them'):
        c = C[side]
        tot = sum(v for (b, t), v in c.items() if b == 'all')
        parts = []
        for band in ('d2 <= 9', 'd2 10-16', 'd2 > 16'):
            v = sum(x for (b, t), x in c.items() if b == band)
            parts.append(f'{band}: {v} ({100 * v / max(1, tot):.0f}%)')
        print(f'   {side:4s} total {tot}: ' + ', '.join(parts))
        for typ in ('P', 'M', 'D'):
            tt = c[('all', typ)]
            if tt:
                o = c[('d2 10-16', typ)] + c[('d2 > 16', typ)]
                print(f'        on {typ} towers {tt}: from outside d2 9: {o} ({100 * o / tt:.0f}%)')
    print()

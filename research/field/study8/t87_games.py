"""Topic 87: game timelines.  `t87_games.py mMgG [mMgG ...]` (run.sh: every lost game that did NOT end by elimination;
t81 has those) prints every 50 rounds: towers (P/M/D), robots S/X/M, chips, coverage, robot+tower paint and active
SRPs for us and them; then every tower of ours killed (round, type, damage by unit type in its last 20 rounds) and
every tower of theirs we killed."""
import sys
import lib
from collections import defaultdict, Counter
want = set(sys.argv[1:])


def rows(G):
    b, d = lib.tower_events(G)
    out = [f'== m{G.m}g{G.g} {G.map} ({G.W}x{G.H}, {G.sm["paintable"]} paintable) vs {G.team_name}, {G.ver}, '
           f'{"LOST" if G.won_op else "WON"} {G.wintype} r{G.end}']
    for r in list(range(50, G.end, 50)) + [G.end]:
        cells = []
        for s in (G.us, G.op):
            tw = lib.towers_alive(G, s, r, b, d)
            pt = sum(1 for t in tw if t[2] == 'PAINT_TOWER'); mt = sum(1 for t in tw if t[2] == 'MONEY_TOWER')
            R = G.rounds[min(r, len(G.rounds)) - 1]; k = 'A' if s == 1 else 'B'
            cells.append(f'T{len(tw):2d}(P{pt}M{mt}D{len(tw) - pt - mt}) S{R["sol" + k]:>2} X{R["spl" + k]:>2} M{R["mop" + k]:>2} '
                         f'${int(R["money" + k]):5d} cov{lib.rv(G, s, r, "covpct"):5.1f} p{int(R["paint" + k]):5d} srp{R["srp" + k]:>2}')
        out.append(f'   r{r:<4} us {cells[0]} | them {cells[1]}')
    dmg = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.BOT: dmg[int(a[5])].append((a[0], a[3], int(a[6])))
    for who, side in (('ours', G.us), ('theirs', G.op)):
        ks = []
        for a in G.acts:
            if a[4] != 'die' or a[7] not in lib.TOW: continue
            tid = int(a[5])
            if G.team.get(tid) != side: continue
            by = Counter()
            for h in dmg.get(tid, ()):
                if h[0] >= a[0] - 20: by[h[1][:2]] += h[2]
            ks.append(f'r{a[0]} {a[7][0]}' + ('' if set(by) <= {'SO'} else '(' + ','.join(f'{k}{v}' for k, v in by.items()) + ')'))
        out.append(f'   {who} killed ({len(ks)}): ' + ' '.join(ks))
    return out


for G in lib.games('lost' if not want else 'all'):
    name = f'm{G.m}g{G.g}'
    if want and name not in want: continue
    if not want and G.wintype.startswith('ALL'): continue
    for line in rows(G): print(line)
    print()

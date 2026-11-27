"""Topic 131: the robot ledger by phase (robots at r200 are 12 / 20 in the losses while r100 was 9 / 10).  Per side and
phase (r1-100, r101-200, r201-300): robots spawned (S / X / M), robots lost by cause ('die' row whose actor is a tower
= shot by a tower; actor = the victim = starved at 0 paint, robots deal no HP damage to robots; 'died' row =
disintegrated), the starved ones that an enemy mopper drained in their last 15 rounds, and the net change.  Medians per
game [sums]; lost games split into behind / level-or-ahead in towers at r100, and won games."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 300))
KEYS = ('spawn S', 'spawn X', 'spawn M', 'spawned', 'shot', 'starved', 'starved+drained', 'disint', 'lost', 'net',
        'alive end')


def analyse(G):
    drained = defaultdict(list)
    for a in G.acts:
        if a[4] == 'drain': drained[int(a[5])].append(a[0])
    out = {}
    for s in (G.us, G.op):
        for j, (lo, hi) in enumerate(PH):
            if G.end < hi: continue
            m = defaultdict(int)
            for a in G.acts:
                if not lo <= a[0] <= hi: continue
                if a[4] == 'spawn' and a[2] == s and a[6] in lib.BOT:
                    m['spawn ' + {'SOLDIER': 'S', 'SPLASHER': 'X', 'MOPPER': 'M'}[a[6]]] += 1; m['spawned'] += 1
                elif a[4] == 'die' and a[7] in lib.BOT and G.team.get(int(a[5])) == s:
                    v = int(a[5])
                    if a[3] in lib.TOW: m['shot'] += 1
                    elif int(a[1]) == v:
                        m['starved'] += 1
                        if any(a[0] - 15 <= x <= a[0] for x in drained.get(v, ())): m['starved+drained'] += 1
                    m['lost'] += 1
                elif a[4] == 'died' and a[7] in lib.BOT and a[2] == s:
                    m['disint'] += 1; m['lost'] += 1
            m['net'] = m['spawned'] - m['lost']
            m['alive end'] = lib.rv(G, s, hi, 'units')
            out[(s == G.us, j)] = m
    return out


groups = defaultdict(list)
for G in lib.games('all'):
    o = analyse(G)
    if G.won_op:
        grp = 'lost, behind at r100' if lib.rv(G, G.us, 100, 'tow') < lib.rv(G, G.op, 100, 'tow') else 'lost, level/ahead at r100'
        groups['all lost'].append(o); groups[grp].append(o)
    else: groups['won'].append(o)
    lib.lite(G)
for grp in ('all lost', 'lost, behind at r100', 'lost, level/ahead at r100', 'won'):
    L = groups[grp]
    print(f'\n== {grp}: {len(L)} games; medians per game [sums], us | them')
    print(f'{"":16s}' + ''.join(f'{f"r{lo}-{hi}":>30s}' for lo, hi in PH))
    for k in KEYS:
        cells = []
        for j in range(len(PH)):
            u = [o[(True, j)][k] for o in L if (True, j) in o]; t = [o[(False, j)][k] for o in L if (False, j) in o]
            cells.append(f'{lib.med(u)} | {lib.med(t)} [{sum(u)}|{sum(t)}]')
        print(f'{k:16s}' + ''.join(f'{c:>30s}' for c in cells))

"""Topic 35: money-tower upgrades switch off our churn.  Tower.churn() only disintegrates LEVEL_ONE money towers, and
Tower.upgrade() lifts money towers to L2/L3 once chips >= cost + 1200 + 2500.  Per lost game: our churns
(died rows of money towers) before/after our first money-tower upgrade, rounds from that upgrade to the end, chips
and paint-blocked tower turns (paint < 200, chips >= 1250) after it, and our L1 money towers alive at the end."""
import lib
from collections import defaultdict
rows = []
for G in lib.games():
    us = G.us; s = 'A' if us == 1 else 'B'
    up = [a for a in G.acts if a[2] == us and a[4] == 'upgrade' and a[3] == 'MONEY_TOWER']
    ch = [a[0] for a in G.acts if a[2] == us and a[4] == 'died' and a[3] == 'MONEY_TOWER']
    if not up:
        rows.append((G.m, G.g, G.map, None, len(ch), 0, None, None)); continue
    r0 = up[0][0]
    lvl = defaultdict(lambda: 1)
    for a in G.acts:
        if a[4] == 'upgrade': lvl[int(a[5])] = int(a[6])
    after = [R for R in G.rounds[r0:]]
    mchips = lib.med([int(R['money' + s]) for R in after])
    pt = lib.med([int(R['pt' + s]) for R in after])
    rows.append((G.m, G.g, G.map, r0, sum(1 for r in ch if r < r0), sum(1 for r in ch if r >= r0), mchips, pt, G.end))
print('match game map | first money upgrade r | churns before | churns after | median chips after | median paint towers after | end')
for r in rows: print(' ', r)

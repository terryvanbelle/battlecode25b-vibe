"""Topic 166: early signals per game (the per-game table behind the opening bullets of the report): opponent, result,
map, size class, end round; coverage % at r50 and r75, towers at r100 and r150, moppers at r100 (us / them), the round
of the first tower kill on us, and our version.  Then medians of the r75 coverage gap and the tower differences by
result and size class.  All games, repeats left out."""
import lib
rows = []
for G in lib.games('all'):
    built, died = lib.tower_events(G)
    def kills(side, r0, r1): return sum(1 for d in died if d[3] == side and r0 <= d[0] <= r1 and d[1] not in ())
    dk = [d for d in died if d[3] == G.us]
    firstk = min([d[0] for d in dk], default=None)
    rows.append((G.team_name[:10], 'L' if G.won_op else 'W', G.map[:12], lib.cls(G)[:1], G.end,
                 lib.rv(G, G.us, 50, 'covpct'), lib.rv(G, G.op, 50, 'covpct'), lib.rv(G, G.us, 75, 'covpct'), lib.rv(G, G.op, 75, 'covpct'),
                 lib.rv(G, G.us, 100, 'tow'), lib.rv(G, G.op, 100, 'tow'), lib.rv(G, G.us, 150, 'tow'), lib.rv(G, G.op, 150, 'tow'),
                 lib.rv(G, G.us, 100, 'mop'), lib.rv(G, G.op, 100, 'mop'), firstk, G.ver))
rows.sort()
print('opp        res map          c  end | cov50 us/them | cov75 us/them | tow100 | tow150 | mop100 | 1st kill on us | ver')
for r in rows:
    print(f'{r[0]:10s} {r[1]}   {r[2]:12s} {r[3]} {r[4]:4d} | {r[5]:5.1f}/{r[6]:5.1f} | {r[7]:5.1f}/{r[8]:5.1f} | {r[9]:2d}/{r[10]:2d} | {r[11]:2d}/{r[12]:2d} | {r[13]}/{r[14]} | {r[15]} | {r[16]}')
import collections
for res in 'LW':
    for c in 'sml':
        sel = [r for r in rows if r[1] == res and r[3] == c]
        print(res, c, len(sel), 'cov75 gap (them-us) med', lib.med([r[8]-r[7] for r in sel]), 'tow100 diff', lib.med([r[9]-r[10] for r in sel]), 'tow150 diff', lib.med([r[11]-r[12] for r in sel]))

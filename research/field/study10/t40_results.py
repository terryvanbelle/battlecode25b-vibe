"""Topic 40: the data set.  Every game vs a team that took a game from us (lib.STRONG), with our version, map size,
result, end round and win type; loss rate by opponent, by our version, by map area class and by win type; and the
same split of how many towers each side had at r100 (the clearest single predictor in t37)."""
import lib
from collections import defaultdict
rows = []
for G in lib.games('all'):
    R = G.rounds[min(100, G.end) - 1]
    s, o = ('A', 'B') if G.us == 1 else ('B', 'A')
    tw = lambda x: sum(int(R[k + x]) for k in ('pt', 'mt', 'dt'))
    area = G.sm['paintable']
    rows.append((G.m, G.g, G.ver, G.team_name, G.map, G.W, G.H, area, 'L' if G.won_op else 'W', G.end, G.wintype[:3], tw(s), tw(o)))
print('match g ver   opponent        map              WxH    paintable res end  type  towers@r100 us/them')
for r in rows:
    print(f'{r[0]} {r[1]} {r[2]:5s} {r[3]:15s} {r[4]:16s} {r[5]}x{r[6]:<3d} {r[7]:5d}     {r[8]}  {r[9]:4d} {r[10]}   {r[11]}/{r[12]}')
def split(name, key):
    d = defaultdict(lambda: [0, 0])
    for r in rows: d[key(r)][r[8] == 'L'] += 1
    print(f'\nby {name}: (won, lost, loss%)')
    for k in sorted(d): w, l = d[k]; print(f'   {str(k):22s} {w:3d} {l:3d}  {round(100 * l / (w + l))}%')
split('opponent', lambda r: r[3])
split('our version', lambda r: r[2])
def cls(a):
    return '1: <=500' if a <= 500 else '2: 501-900' if a <= 900 else '3: 901-1600' if a <= 1600 else '4: 1601-2500' if a <= 2500 else '5: >2500'
split('paintable area', lambda r: cls(r[7]))
split('min side', lambda r: '<=25' if min(r[5], r[6]) <= 25 else '26-35' if min(r[5], r[6]) <= 35 else '>35')
print('\ntowers at r100 (us - them) vs result:')
d = defaultdict(lambda: [0, 0])
for r in rows:
    k = r[11] - r[12]; k = max(-3, min(3, k)); d[k][r[8] == 'L'] += 1
for k in sorted(d): w, l = d[k]; print(f'   diff {k:+d}: won {w:2d} lost {l:2d}')
print('\nwin types of losses:', {t: sum(1 for r in rows if r[8] == 'L' and r[10] == t) for t in set(r[10] for r in rows)})
print('median end of losses on maps <= 900 paintable:', lib.med([r[9] for r in rows if r[8] == 'L' and r[7] <= 900]),
      ' > 900:', lib.med([r[9] for r in rows if r[8] == 'L' and r[7] > 900]))

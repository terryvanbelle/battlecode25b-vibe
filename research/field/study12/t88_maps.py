"""Topic 88: the record per map, study 11's set (t122, 4661-5012) next to study 10's (3999-4602: t111, t118).
Reads only summary.json and meta.json.  Per map: size, paintable tiles, games and losses in each set, the opponents
that beat us there, how the losses ended (MAJ / ALL with the round), then the maps we lost at least twice since
3999, and the record by map class (short side <= 25 or <= 600 paintable / short side <= 35 / larger)."""
import json, os
from collections import defaultdict
import lib

R = defaultdict(lambda: {'main': [0, 0], 'prev': [0, 0], 'size': None, 'loss': []})
for which, ms in (('main', lib.MAIN), ('prev', lib.PREV)):
    for m in ms:
        d = lib.DUMPS[m]
        for g in range(3):
            if (m, g) in lib.DUP: continue
            p = f'{d}/g{g}.summary.json'
            if not os.path.exists(p): continue
            sm = json.load(open(p)); meta = json.load(open(f'{d}/g{g}.meta.json'))
            us = 'A' if sm['teamA'] == lib.US else 'B'
            lost = sm['winner'] != us
            opp = sm['teamB'] if us == 'A' else sm['teamA']
            e = R[meta['map']]
            e['size'] = (meta['width'], meta['height'], sm['paintable'])
            e[which][0] += 1; e[which][1] += lost
            if lost: e['loss'].append(f'{which[0]}:{opp[:8]} {lib.VER[m]} {sm["winType"][:3]}{sm["rounds"]}')
print('map               size      paintable | t122 games/lost | study 10 games/lost | losses (m = t122, p = study 10)')
for name, e in sorted(R.items(), key=lambda kv: (-kv[1]['main'][1], -kv[1]['prev'][1], kv[0])):
    W, H, P = e['size']
    print(f'{name[:17]:17s} {W:2d}x{H:<2d}     {P:5d}     |   {e["main"][0]:2d} / {e["main"][1]:<2d}               |   {e["prev"][0]:2d} / {e["prev"][1]:<2d}           | '
          + ', '.join(e['loss']))
print()
cl = defaultdict(lambda: [0, 0, 0, 0])
for name, e in R.items():
    W, H, P = e['size']
    c = 'small' if (min(W, H) <= 25 or P <= 600) else 'medium' if min(W, H) <= 35 else 'large'
    cl[c][0] += e['main'][0]; cl[c][1] += e['main'][1]; cl[c][2] += e['prev'][0]; cl[c][3] += e['prev'][1]
for c in ('small', 'medium', 'large'):
    v = cl[c]
    print(f'{c:6s}: t122 lost {v[1]} of {v[0]} ({100 * v[1] / max(1, v[0]):.0f}%); study 10 lost {v[3]} of {v[2]} ({100 * v[3] / max(1, v[2]):.0f}%)')

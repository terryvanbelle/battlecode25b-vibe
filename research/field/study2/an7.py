"""Study 2: why our marked ruins fail. For each (ruin, side) first marked: tiles of the 5x5 holding enemy paint /
own paint at mark+10, mark+30, and whether a mopper of that side came within r^2<=8 of the ruin within 40 rounds.
Usage: python3 -I an7.py [DUMPDIR] [study2|study1]."""
import json, csv, os, sys, ast, statistics as st
from collections import defaultdict
S = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else S
GR = {'study2': (([608, 609, 610, 611], 'LOST'), ([642, 593, 546, 521], 'WON')),
      'study1': (([8, 9, 10, 11, 13, 27, 28], 'LOST'), ([12, 14, 6, 7], 'WON'))}[sys.argv[2] if len(sys.argv) > 2 else 'study2']


def rd(p):
    with open(p) as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); return [dict(zip(h, x)) for x in r]


def med(x):
    x = [v for v in x if v is not None]; return round(st.median(x), 1) if x else '-'


for grp, name in GR:
    out = defaultdict(lambda: defaultdict(list))
    for m in grp:
        for g in range(3):
            d = f'{D}/m{m}'
            sm = json.load(open(f'{d}/g{g}.summary.json')); meta = json.load(open(f'{d}/g{g}.meta.json'))
            us = 1 if sm['teamA'] == 'vibe25b' else 2
            ruins = [tuple(r) for r in (meta['ruins'] if isinstance(meta['ruins'], list) else ast.literal_eval(meta['ruins']))]
            acts = rd(f'{d}/g{g}.actions.tsv'); turns = rd(f'{d}/g{g}.turns.tsv')
            firstmark = {}; built = {}
            for a in acts:
                if a['action'] == 'mark':
                    x, y = map(int, a['a'].split(','))
                    for r in ruins:
                        if max(abs(r[0] - x), abs(r[1] - y)) <= 2: firstmark.setdefault((r, int(a['team'])), int(a['round']))
                if a['action'] == 'spawn' and 'TOWER' in a['b']:
                    x, y = map(int, a['c'].split(','))
                    if (x, y) in ruins: built.setdefault((x, y), []).append((int(a['round']), int(a['team'])))
            # paint ownership snapshots per round needed: process actions in order
            want = defaultdict(list)
            for (r, tm), fr in firstmark.items():
                want[fr + 10].append((r, tm, 10)); want[fr + 30].append((r, tm, 30))
            own = {}; res = defaultdict(dict); ai = 0
            pa = [(int(a['round']), int(a['team']), a['action'], a['a']) for a in acts if a['action'] in ('paint', 'unpaint')]
            for R in sorted(want):
                while ai < len(pa) and pa[ai][0] <= R:
                    rr, tm, k, loc = pa[ai]; ai += 1
                    if k == 'paint': own[loc] = tm
                    else: own.pop(loc, None)
                for r, tm, off in want[R]:
                    en = ow = 0
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            if dx == 0 and dy == 0: continue
                            v = own.get(f'{r[0]+dx},{r[1]+dy}')
                            if v == tm: ow += 1
                            elif v: en += 1
                    res[(r, tm)][off] = (en, ow)
            mop = defaultdict(set)
            for t in turns:
                if t['type'] == 'MOPPER':
                    x, y, rr, tm = int(t['x']), int(t['y']), int(t['round']), int(t['team'])
                    for (r, s), fr in firstmark.items():
                        if s == tm and fr <= rr <= fr + 40 and (x - r[0]) ** 2 + (y - r[1]) ** 2 <= 8: mop[(r, s)].add(1)
            for (r, tm), fr in firstmark.items():
                k = 'us' if tm == us else 'op'
                b = [x for x in built.get(r, []) if x[0] >= fr]
                outc = 'built' if b and b[0][1] == tm else ('stolen' if b else 'never')
                e10, o10 = res[(r, tm)].get(10, (None, None)); e30, o30 = res[(r, tm)].get(30, (None, None))
                out[(k, outc)]['n'].append(1)
                out[(k, outc)]['enemy tiles @+10'].append(e10); out[(k, outc)]['enemy tiles @+30'].append(e30)
                out[(k, outc)]['own tiles @+30'].append(o30)
                out[(k, outc)]['mopper came (frac)'].append(1 if mop[(r, tm)] else 0)
    print('==', name, '(per marked ruin; outcome built / stolen = enemy built it / never)')
    for (k, oc), v in sorted(out.items()):
        print(f"  {k} {oc:<7} n={len(v['n']):<3} enemy tiles in 5x5 @mark+10 med {med(v['enemy tiles @+10'])} @+30 med {med(v['enemy tiles @+30'])}"
              f"  own tiles @+30 med {med(v['own tiles @+30'])}  mopper within r2 8 in 40r: {round(sum(v['mopper came (frac)'])/len(v['n']),2)}")

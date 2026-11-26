#!/usr/bin/env python3
"""Turn-by-turn modes of an instrumented bot (bots/d16: t16 + indicator tags S:/M:/X:) in local dumps.

  python3 tags.py TEAM DUMPDIR...

For each unit type: the share of its turns in each mode, and for each mode the share of turns that changed nothing
(no tile turned ours, no enemy tile cleaned, no drain, no damage, no paint given, no build)."""
import csv, json, sys, os, collections, glob

def rd(p):
    with open(p) as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); return [dict(zip(h, x)) for x in r]

def main():
    team, dirs = sys.argv[1], sys.argv[2:]
    mode_n = collections.defaultdict(collections.Counter)
    mode_dead = collections.defaultdict(collections.Counter)
    mode_paint = collections.defaultdict(lambda: collections.defaultdict(list))
    for d in dirs:
        for mp in sorted(glob.glob(f'{d}/g*.meta.json')):
            g = mp.split('/g')[-1].split('.')[0]
            meta = json.load(open(mp))
            me = '1' if meta['teamA'] == team else '2' if meta['teamB'] == team else None
            if not me: continue
            W = meta['width']; paint = [int(c) for c in meta['paint']]
            mine = (lambda v: v in (1, 2)) if me == '1' else (lambda v: v in (3, 4))
            acts = rd(f'{d}/g{g}.actions.tsv'); turns = rd(f'{d}/g{g}.turns.tsv')
            by = collections.defaultdict(list)
            for a in acts: by[(a['round'], a['id'])].append(a)
            for t in turns:
                prod = False
                for a in by.get((t['round'], t['id']), []):
                    k = a['action']
                    if k == 'paint':
                        x, y = map(int, a['a'].split(',')); i = x + y * W
                        if t['team'] == me and not mine(paint[i]): prod = True
                        paint[i] = (1 if a['team'] == '1' else 3) + int(a['b'])
                    elif k == 'unpaint':
                        x, y = map(int, a['a'].split(',')); paint[x + y * W] = 0; prod = True
                    elif k in ('drain', 'damage', 'build') or (k == 'transfer' and int(a['b']) > 0): prod = True
                if t['team'] != me or t['type'] not in ('SOLDIER', 'SPLASHER', 'MOPPER'): continue
                tags = [w for w in t['ind'].split() if ':' in w and w[0] in 'SMX']
                # the soldier's ruin/refill/siege branches carry their own non-prefixed tags
                if not tags:
                    w = t['ind'].split()
                    tags = ['S:' + w[0].rstrip('0123456789(), ').split('(')[0]] if w else ['?:none']
                m = '+'.join(sorted(set(tags)))
                mode_n[t['type']][m] += 1
                if not prod: mode_dead[t['type']][m] += 1
                mode_paint[t['type']][m].append(int(t['paint']))
    for ty in ('SOLDIER', 'SPLASHER', 'MOPPER'):
        n = mode_n[ty]; T = sum(n.values())
        if not T: continue
        dead = sum(mode_dead[ty].values())
        print(f'\n{ty}: {T} turns, {100*dead/T:.0f}% changed nothing')
        for m, c in n.most_common(12):
            ps = sorted(mode_paint[ty][m])
            print(f'  {m:42s} {100*c/T:5.1f}% of turns   nothing in {100*mode_dead[ty][m]/c:5.1f}%   median paint {ps[len(ps)//2]}')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""bcdiff.py BASE_GAMEDIR NEW_GAMEDIR TEAM [TYPE] : turns where bc differs (team/type), with ind, and a summary."""
import sys, glob, os, collections
def gd(d): return d if os.path.exists(os.path.join(d, 'g0.turns.tsv')) else glob.glob(os.path.join(d, '*/'))[0]
b, n, team = gd(sys.argv[1]), gd(sys.argv[2]), sys.argv[3]; ty = sys.argv[4] if len(sys.argv) > 4 else None
R = lambda p: [l.rstrip('\n').split('\t') for l in open(os.path.join(p, 'g0.turns.tsv'))]
tb, tn = R(b), R(n); h = tb[0]; ib, ii = h.index('bc'), h.index('ind')
c = collections.Counter(); shown = 0; first = {}
for x, y in zip(tb[1:], tn[1:]):
    if x[2] != team or (ty and x[3] != ty): continue
    d = int(y[ib]) - int(x[ib])
    if d:
        c[(x[3], d)] += 1
        if shown < int(os.environ.get('SHOW', 15)): print(x[0], x[1], x[3], 'bc', x[ib], '->', y[ib], 'paint', x[7], 'ind', x[ii][:60], '|', y[ii][:60]); shown += 1
print(dict(c))

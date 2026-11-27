#!/usr/bin/env python3
"""cmp.py DIR_X DIR_Y [--team A|B]: compare two tsv dumps (game dirs holding g0.*.tsv, or a label dir containing one).
actions.tsv: every column; turns.tsv: all but bc and ind. Prints IDENTICAL or the first divergence, plus bc stats
for our team (--team) on identical rows."""
import sys, os, glob
def gdir(d):
    if os.path.exists(os.path.join(d, 'g0.turns.tsv')): return d
    c = [x for x in glob.glob(os.path.join(d, '*')) if os.path.isdir(x)]
    assert len(c) == 1, (d, c); return c[0]
def load(p, drop=()):
    rows = [l.rstrip('\n').split('\t') for l in open(p)]
    h = rows[0]; keep = [i for i, c in enumerate(h) if c not in drop]
    return h, [[r[i] for i in keep] for r in rows[1:]], rows[1:]
x, y = gdir(sys.argv[1]), gdir(sys.argv[2])
team = None
if '--team' in sys.argv: team = {'A': '1', 'B': '2'}[sys.argv[sys.argv.index('--team') + 1]]
ok = True; out = []
for f, drop in (('g0.actions.tsv', ()), ('g0.turns.tsv', ('bc', 'ind'))):
    hx, a, ra = load(os.path.join(x, f), drop); hy, b, rb = load(os.path.join(y, f), drop)
    n = min(len(a), len(b)); i = next((i for i in range(n) if a[i] != b[i]), None)
    if i is None and len(a) == len(b):
        out.append(f'{f}: identical ({len(a)} rows)')
        if f == 'g0.turns.tsv':
            ib = hx.index('bc'); it = hx.index('team'); ity = hx.index('type')
            diffs = {}
            for r1, r2 in zip(ra, rb):
                if team and r1[it] != team: continue
                d = int(r2[ib]) - int(r1[ib]); t = r1[ity]
                lo, hi, nz = diffs.get(t, (0, 0, 0)); diffs[t] = (min(lo, d), max(hi, d), nz + (d != 0))
            out.append('  bc delta (Y-X) by type: ' + ', '.join(f'{t} [{lo},{hi}] nz={nz}' for t, (lo, hi, nz) in sorted(diffs.items())))
        continue
    ok = False
    if i is None: i = n
    out.append(f'{f}: DIFFER at row {i + 2} (rows {len(a)} vs {len(b)})')
    for j in range(max(0, i - 2), min(i + 3, n)):
        out.append(('  X ' if j != i else '> X ') + '\t'.join(ra[j])[:200])
        out.append(('  Y ' if j != i else '> Y ') + '\t'.join(rb[j])[:200])
print('IDENTICAL' if ok else 'DIVERGED'); print('\n'.join(out))
sys.exit(0 if ok else 1)

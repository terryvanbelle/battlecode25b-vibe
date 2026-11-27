"""Topic 127: is t122 weaker than t111 / t118, or was its schedule harder?  The opponents' bots are fixed (pkgs.txt:
the same package names as in study 10), so a pairing on the same map differs only by our version and by which side
we play.  Reads summary.json only.  For every (opponent, map) played by t122 (study 11's set) and by t111 or t118
(study 10's set), the results of each version; then the record over those common pairings only, by version, and
the same restricted to the top teams.  Repeats (lib.DUP) are left out."""
import json, os
from collections import defaultdict
import lib


def rows(ms):
    out = []
    for m in ms:
        for g in range(3):
            if (m, g) in lib.DUP: continue
            p = f'{lib.DUMPS[m]}/g{g}.summary.json'
            if not os.path.exists(p): continue
            s = json.load(open(p))
            us = 'A' if s['teamA'] == lib.US else 'B'
            opp = s['teamB'] if us == 'A' else s['teamA']
            out.append((lib.VER[m], opp, s['map'], s['winner'] == us, m, g, us))
    return out


R = rows(lib.MAIN) + rows(lib.PREV)
by = defaultdict(lambda: defaultdict(list))
for v, opp, mp, won, m, g, us in R: by[(opp, mp)][v].append((won, m, g, us))
common = {k: d for k, d in by.items() if 't122' in d and ('t111' in d or 't118' in d)}
print(f'{len(common)} (opponent, map) pairings played by t122 and by t111 / t118')
print('opponent                 map              t122            t111            t118')
tot = defaultdict(lambda: [0, 0]); totop = defaultdict(lambda: [0, 0])
for (opp, mp), d in sorted(common.items()):
    cells = []
    for v in ('t122', 't111', 't118'):
        L = d.get(v, [])
        cells.append(''.join('W' if w else 'L' for w, *_ in L) or '-')
        for w, *_ in L:
            tot[v][0 if w else 1] += 1
            if opp in lib.TOP: totop[v][0 if w else 1] += 1
    print(f'{opp[:24]:24s} {mp[:16]:16s} {cells[0]:15s} {cells[1]:15s} {cells[2]:15s}')
for name, T in (('all', tot), ('top teams', totop)):
    print(f'\ncommon pairings, {name}: ' + '; '.join(f'{v} {T[v][0]}-{T[v][1]} ({100 * T[v][0] / max(1, sum(T[v])):.0f}%)' for v in ('t122', 't111', 't118')))
# pairings where the result flipped between t122 and the older versions (all older games agree)
flip_bad = [(k, d) for k, d in common.items() if all(not w for w, *_ in d['t122']) and all(w for v in ('t111', 't118') for w, *_ in d.get(v, []))]
flip_good = [(k, d) for k, d in common.items() if all(w for w, *_ in d['t122']) and all(not w for v in ('t111', 't118') for w, *_ in d.get(v, []))]
print(f'\npairings t122 lost that every older game won: {len(flip_bad)}: ' + ', '.join(f'{k[0][:10]}/{k[1]}' for k, d in flip_bad))
print(f'pairings t122 won that every older game lost: {len(flip_good)}: ' + ', '.join(f'{k[0][:10]}/{k[1]}' for k, d in flip_good))
# whole-set record per opponent by version
print('\nwhole sets, per opponent: t122 | t111 | t118')
opps = sorted(set(r[1] for r in R))
for o in opps:
    cells = []
    for v in ('t122', 't111', 't118'):
        L = [r for r in R if r[1] == o and r[0] == v]
        w = sum(1 for r in L if r[3])
        cells.append(f'{w}-{len(L) - w}' if L else '-')
    print(f'   {o[:24]:24s} {cells[0]:>7s} | {cells[1]:>7s} | {cells[2]:>7s}')

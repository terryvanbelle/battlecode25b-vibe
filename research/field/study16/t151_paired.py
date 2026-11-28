"""Topic 151 (y360 and y374 added: lib.NEW, the matches fetched during the study): did y358 change the results against t188?  (study 15's t151 on study 16's set.)  The opponents' bots are
fixed (pkgs.txt: the same package names as in studies 10-15), so a pairing on the same map differs only by our
version and by which side we play.  Reads summary.json only.
For every (opponent, map) played by two or more of our versions, the results of each version (W / L; lower case = we
were team B); then the record over the pairings two versions share, version against version.  t188 = both sets'
t188 games (study 15's 7 matches and this set's 8); 't188new' = this set's only, 't188old' = study 15's only.
Repeats (lib.DUP) are left out, but a game equal to one of another version is kept (it is that version's result too)."""
import json, os
from collections import defaultdict
import lib

VERS = ("y374", "y360", "y358", "t188", "t186", "y328", "y323", "y316", "t160", "t158", "t140")


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
            out.append((lib.VER[m], opp, s['map'], s['winner'] == us, m, g, us, s['rounds']))
    return out


R = rows(lib.NEW) + rows(lib.MAIN) + rows(lib.PREV) + rows(lib.PREV2) + rows(lib.PREV3)
by = defaultdict(lambda: defaultdict(list))
for v, opp, mp, won, m, g, us, rnd in R:
    by[(opp, mp)][v].append((won, m, g, us, rnd))
    if v == 't188': by[(opp, mp)]['t188new' if m in lib.MAIN else 't188old'].append((won, m, g, us, rnd))
common = {k: d for k, d in by.items() if sum(1 for v in d if v in VERS) >= 2 and any(v in d for v in ('y374', 'y360', 'y358', 't188'))}
print(f'{len(common)} (opponent, map) pairings played by y374, y360, y358 or t188 and by at least one other version')
print('opponent                 map              ' + ''.join(f'{v:10s}' for v in VERS))


def cell(L):
    return ''.join(('W' if w else 'L') if us == 'A' else ('w' if w else 'l') for w, m, g, us, rnd in L) or '-'


for (opp, mp), d in sorted(common.items()):
    print(f'{opp[:24]:24s} {mp[:16]:16s} ' + ''.join(f'{cell(d.get(v, [])):10s}' for v in VERS))


def h2h(a, b, top=None):
    """Record of a and of b over the pairings both played (each version's games on those pairings)."""
    ra, rb, n = [0, 0], [0, 0], 0
    for (opp, mp), d in by.items():
        if a not in d or b not in d: continue
        if top is not None and (opp in lib.TOP7) != top: continue
        n += 1
        for w, *_ in d[a]: ra[0 if w else 1] += 1
        for w, *_ in d[b]: rb[0 if w else 1] += 1
    return n, ra, rb


print('\nversion against version, over the pairings both played (all opponents | the seven teams of the brief, TOP7):')
for a, b in (('y360', 'y358'), ('y360', 't188'), ('y360', 'y328'), ('y360', 't140'), ('y374', 'y360'), ('y374', 'y358'), ('y358', 't188'), ('y358', 't188new'), ('y358', 't188old'), ('t188new', 't188old'), ('y358', 'y328'),
             ('t188', 'y328'), ('y358', 'y316'), ('t188', 'y316'), ('y358', 't140'), ('t188', 't140')):
    n, ra, rb = h2h(a, b)
    nt, rat, rbt = h2h(a, b, True)
    print(f'   {a} vs {b}: {n:2d} pairings: {a} {ra[0]}-{ra[1]}, {b} {rb[0]}-{rb[1]}   | TOP7: {nt:2d} pairings: {a} {rat[0]}-{rat[1]}, {b} {rbt[0]}-{rbt[1]}')
print('\nflips (every game of the first version lost / won while every game of the second won / lost):')
for a, b in (('y360', 'y358'), ('y360', 't188'), ('y358', 't188'), ('y358', 'y328'), ('t188', 'y328'), ('t188new', 't188old')):
    bad = [k for k, d in by.items() if a in d and b in d and all(not w for w, *_ in d[a]) and all(w for w, *_ in d[b])]
    good = [k for k, d in by.items() if a in d and b in d and all(w for w, *_ in d[a]) and all(not w for w, *_ in d[b])]
    print(f'   {a} lost, {b} won: {len(bad)}: ' + ', '.join(f'{o[:10]}/{mp}' for o, mp in sorted(bad)))
    print(f'   {a} won, {b} lost: {len(good)}: ' + ', '.join(f'{o[:10]}/{mp}' for o, mp in sorted(good)))
print('\nwhole sets, per opponent: ' + ' | '.join(VERS))
for o in sorted(set(r[1] for r in R)):
    cells = []
    for v in VERS:
        L = [r for r in R if r[1] == o and r[0] == v]
        w = sum(1 for r in L if r[3])
        cells.append(f'{w}-{len(L) - w}' if L else '-')
    print(f'   {o[:24]:24s} ' + ' | '.join(f'{c:>6s}' for c in cells))
print('\nwhole sets: ' + ', '.join(f'{v} {sum(1 for r in R if r[0] == v and r[3])}-{sum(1 for r in R if r[0] == v and not r[3])}' for v in VERS))
print('TOP7 only: ' + ', '.join(f'{v} {sum(1 for r in R if r[0] == v and r[3] and r[1] in lib.TOP7)}-{sum(1 for r in R if r[0] == v and not r[3] and r[1] in lib.TOP7)}' for v in VERS))

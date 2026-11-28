"""Topic 147: the data set and its exact repeats (study 13's t147 on study 14's set).  Reads summary.json only.
Lists every game of the main set (6515-6860: t158, t160, y316, y323) with ranked or not, opponent, map, result, end round,
and flags a game that repeats an earlier one exactly: same map and opponent, same end round, same coverage and the same
spawn counts for each side (from our side's point of view; the replica sometimes swaps sides).  The engine is
deterministic, so a pairing with unchanged bots on the same map replays the same game.  Earlier games are searched in
this set, in study 13's (5572-6493: t140, t158), study 12's (5067-5557: t122, t135, t140) and study 11's (4661-5012).
A repeat across our versions (a y316 game equal to a t160 game) means the version change did not touch that game."""
import json, os
from collections import Counter
import lib


def key_of(p):
    if not os.path.exists(p): return None
    s = json.load(open(p))
    us = 'A' if s['teamA'] == lib.US else 'B'; op = 'B' if us == 'A' else 'A'
    opp = s['team' + op]
    won = s['winner'] == us
    k = (s['map'], opp, s['rounds'], s['cov' + us], s['cov' + op], won,
         tuple(sorted(s['spawned' + us].items())), tuple(sorted(s['spawned' + op].items())))
    return k, s, us, op, opp, won


seen = {}
for m in sorted(lib.OLD + lib.PREV2 + lib.PREV):
    for g in range(3):
        r = key_of(f'{lib.DUMPS[m]}/g{g}.summary.json')
        if r: seen.setdefault(r[0], (m, g, lib.VER[m]))
rows = []
dups = []
for m in sorted(lib.MAIN):
    for g in range(3):
        r = key_of(f'{lib.DUMPS[m]}/g{g}.summary.json')
        if r is None: continue
        k, s, us, op, opp, won = r
        first = seen.get(k)
        if first: dups.append(((m, g, lib.VER[m]), first))
        else: seen[k] = (m, g, lib.VER[m])
        rows.append((m, g, lib.VER[m], 'R' if m not in lib.UNRANKED else 'u', opp, s['map'], 'W' if won else 'L', s['rounds'],
                     s['winType'][:3], s['covPct' + us], s['covPct' + op], first, s['width'], s['height'], s['paintable']))
VERS = ('t158', 't160', 'y316', 'y323')
print(f'{len(rows)} games in the main set ({len(set(r[0] for r in rows))} matches)')
print('match g ver  rk opponent                 map              size   tiles res  end  how  cov% us/them   repeat of')
for r in rows:
    print(f'm{r[0]} g{r[1]} {r[2]:5s} {r[3]}  {r[4]:24s} {r[5]:16s} {r[12]:2d}x{r[13]:<2d} {r[14]:5d} {r[6]}  {r[7]:5d} {r[8]}  {r[9]:5.1f}/{r[10]:5.1f}   '
          + (f'm{r[11][0]}g{r[11][1]} ({r[11][2]})' if r[11] else ''))
print(f'\nexact repeats ({len(dups)}): ' + ', '.join(f'm{a[0]}g{a[1]} ({a[2]}) = m{b[0]}g{b[1]} ({b[2]})' for a, b in dups))
print('DUP set for lib.py: {' + ', '.join(f'({a[0]}, {a[1]})' for a, b in dups) + '}')
dset = set((a[0], a[1]) for a, b in dups)
print('\nper match (repeats left out): won-lost')
by = {}
for r in rows:
    if (r[0], r[1]) in dset: continue
    by.setdefault(r[0], [r[2], r[3], r[4], 0, 0, []])
    if r[6] == 'W': by[r[0]][3] += 1
    else: by[r[0]][4] += 1
for r in rows:
    if (r[0], r[1]) in dset and r[0] in by: by[r[0]][5].append(r[1])
    elif (r[0], r[1]) in dset: by.setdefault(r[0], [r[2], r[3], r[4], 0, 0, [r[1]]])
for m, v in by.items():
    print(f'm{m} {v[0]:5s} {v[1]} {v[2]:24s} {v[3]}-{v[4]}' + (f'  (dup g{",".join(map(str, v[5]))})' if v[5] else ''))
for ver in VERS + (None,):
    print(f'\n== {ver or "all versions"}')
    for top in (True, False, None):
        sel = [r for r in rows if (r[0], r[1]) not in dset and (top is None or (r[4] in lib.TOP) == top) and (ver is None or r[2] == ver)]
        w = sum(1 for r in sel if r[6] == 'W'); l = len(sel) - w
        print(f'   {"top 7" if top else "rest" if top is False else "all":5s}: {w}-{l}' + (f' ({100 * w / len(sel):.0f}%)' if sel else ''))
    for rk in ('R', 'u'):
        sel = [r for r in rows if (r[0], r[1]) not in dset and r[3] == rk and (ver is None or r[2] == ver)]
        w = sum(1 for r in sel if r[6] == 'W')
        print(f'   {"ranked" if rk == "R" else "unranked"}: {w}-{len(sel) - w}')
print('\nper opponent (repeats left out): ' + ' | '.join(VERS) + ' | all')
for opp in sorted(set(r[4] for r in rows)):
    cells = []
    for ver in VERS + (None,):
        sel = [r for r in rows if (r[0], r[1]) not in dset and r[4] == opp and (ver is None or r[2] == ver)]
        w = sum(1 for r in sel if r[6] == 'W')
        cells.append(f'{w}-{len(sel) - w}' if sel else '-')
    print(f'   {opp:24s} ' + ' | '.join(f'{c:>6s}' for c in cells))
print('\nwin types (repeats left out):', Counter((r[6], r[8]) for r in rows if (r[0], r[1]) not in dset))
print('loss end rounds by version:')
for ver in VERS:
    e = [r[7] for r in rows if (r[0], r[1]) not in dset and r[2] == ver and r[6] == 'L']
    print(f'   {ver}: {len(e)} losses, median end r{lib.med(e)}, eliminations {sum(1 for r in rows if (r[0], r[1]) not in dset and r[2] == ver and r[6] == "L" and r[8] == "ALL")}')
print('\nper map (repeats left out): ' + ' | '.join(v + ' W-L' for v in VERS))
for mp in sorted(set(r[5] for r in rows)):
    cells = []
    for ver in VERS:
        sel = [r for r in rows if (r[0], r[1]) not in dset and r[5] == mp and r[2] == ver]
        w = sum(1 for r in sel if r[6] == 'W')
        cells.append(f'{w}-{len(sel) - w}' if sel else '-')
    print(f'   {mp:18s} ' + ' | '.join(f'{c:>5s}' for c in cells))

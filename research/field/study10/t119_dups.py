"""Topic 119: the data set and its exact repeats.  Reads summary.json only (no turn data).
Lists every game of the main set (3999-4602) with our version, ranked or not, opponent, map, result, end round, and
flags a game that repeats an earlier one exactly: same map and opponent, same end round, same coverage and the same
spawn counts for each side (from our side's point of view; the replica sometimes swaps sides).  The engine is
deterministic, so a pairing with unchanged bots on the same map replays the same game.  Earlier games are searched in
this set and in study 9's (3211-3951)."""
import json, os
import lib


def key(m, g):
    d = lib.DUMPS[m]
    p = f'{d}/g{g}.summary.json'
    if not os.path.exists(p): return None
    s = json.load(open(p))
    us = 'A' if s['teamA'] == lib.US else 'B'; op = 'B' if us == 'A' else 'A'
    opp = s['team' + op]
    won = s['winner'] == us
    k = (s['map'], opp, s['rounds'], s['cov' + us], s['cov' + op], won,
         tuple(sorted(s['spawned' + us].items())), tuple(sorted(s['spawned' + op].items())))
    return k, s, us, op, opp, won


seen = {}
for m in sorted(lib.PREV):
    for g in range(3):
        r = key(m, g)
        if r: seen.setdefault(r[0], (m, g))
rows = []
dups = []
tot = {'won': 0, 'lost': 0, 'draw_dup': 0}
for m in sorted(lib.MAIN):
    for g in range(3):
        r = key(m, g)
        if r is None: continue
        k, s, us, op, opp, won = r
        first = seen.get(k)
        if first: dups.append(((m, g), first))
        else: seen[k] = (m, g)
        rows.append((m, g, lib.VER[m], 'R' if m not in lib.UNRANKED else 'u', opp, s['map'], 'W' if won else 'L', s['rounds'],
                     s['winType'][:3], s['covPct' + us], s['covPct' + op], first))
print(f'{len(rows)} games in the main set ({len(set(r[0] for r in rows))} matches)')
print('match g ver  rk opponent                 map              res  end  how  cov% us/them   repeat of')
for r in rows:
    print(f'm{r[0]} g{r[1]} {r[2]:5s} {r[3]}  {r[4]:24s} {r[5]:16s} {r[6]}  {r[7]:5d} {r[8]}  {r[9]:5.1f}/{r[10]:5.1f}   '
          + (f'm{r[11][0]}g{r[11][1]}' if r[11] else ''))
print(f'\nexact repeats ({len(dups)}): ' + ', '.join(f'm{a[0]}g{a[1]} = m{b[0]}g{b[1]}' for a, b in dups))
print('DUP set for lib.py: {' + ', '.join(f'({a[0]}, {a[1]})' for a, b in dups) + '}')
# results per match (repeats left out)
dset = set(a for a, b in dups)
print('\nper match (repeats left out): won-lost')
by = {}
for r in rows:
    if (r[0], r[1]) in dset: continue
    by.setdefault(r[0], [r[2], r[3], r[4], 0, 0])
    if r[6] == 'W': by[r[0]][3] += 1
    else: by[r[0]][4] += 1
for m, v in by.items():
    print(f'm{m} {v[0]:5s} {v[1]} {v[2]:24s} {v[3]}-{v[4]}')
for ver in ('t111', 't118', None):
    for top in (True, False, None):
        sel = [r for r in rows if (r[0], r[1]) not in dset and (ver is None or r[2] == ver)
               and (top is None or (r[4] in lib.TOP) == top)]
        w = sum(1 for r in sel if r[6] == 'W'); l = len(sel) - w
        print(f'{ver or "all":5s} {"top" if top else "rest" if top is False else "all":4s}: {w}-{l}'
              + (f' ({100 * w / len(sel):.0f}%)' if sel else ''))
for rk in ('R', 'u'):
    sel = [r for r in rows if (r[0], r[1]) not in dset and r[3] == rk]
    w = sum(1 for r in sel if r[6] == 'W')
    print(f'{"ranked" if rk == "R" else "unranked"}: {w}-{len(sel) - w}')
print('\nper opponent (repeats left out), t111 | t118:')
for opp in sorted(set(r[4] for r in rows)):
    s = []
    for ver in ('t111', 't118'):
        sel = [r for r in rows if (r[0], r[1]) not in dset and r[2] == ver and r[4] == opp]
        w = sum(1 for r in sel if r[6] == 'W')
        s.append(f'{w}-{len(sel) - w}' if sel else '  -  ')
    print(f'   {opp:24s} {s[0]:>6s} | {s[1]:>6s}')

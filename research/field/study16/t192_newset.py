"""Topic 192 (new): the 15 matches fetched during the study (7490-7636; lib.NEW, S16SET=y360): y360 (submission 87) in
14, y374 (submission 88, the champion) in 1.  Reads summary.json only.  Every game (ranked or not, opponent, map,
result, end round, how it ended, coverage) and its exact repeats of any earlier game of studies 13-16 (same key as
t147_dups: map, opponent, end round, coverage each side, result, spawn counts each side).  Then the record per version,
per opponent, ranked / unranked and TOP7, and the losses' median end and eliminations."""
import json, os
from collections import defaultdict
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
for m in sorted(lib.PREV3 + lib.PREV2 + lib.PREV + lib.MAIN):
    for g in range(3):
        r = key_of(f'{lib.DUMPS[m]}/g{g}.summary.json')
        if r: seen.setdefault(r[0], (m, g, lib.VER[m]))
rows, dups = [], []
for m in sorted(lib.NEW):
    for g in range(3):
        r = key_of(f'{lib.DUMPS[m]}/g{g}.summary.json')
        if r is None: continue
        k, s, us, op, opp, won = r
        first = seen.get(k)
        if first: dups.append(((m, g, lib.VER[m]), first))
        else: seen[k] = (m, g, lib.VER[m])
        rows.append(dict(m=m, g=g, ver=lib.VER[m], rk='u' if m in lib.UNRANKED else 'R', opp=opp, map=s['map'], won=won,
                         end=s['rounds'], how=s['winType'][:3], cu=s['covPct' + us], co=s['covPct' + op], first=first))
print(f'{len(rows)} games ({len(set(r["m"] for r in rows))} matches)')
for r in rows:
    print(f'm{r["m"]} g{r["g"]} {r["ver"]:5s} {r["rk"]}  {r["opp"]:14s} {r["map"]:16s} {"W" if r["won"] else "L"} {r["end"]:5d} {r["how"]}'
          f'  {r["cu"]:5.1f}/{r["co"]:5.1f}  ' + (f'repeat of m{r["first"][0]}g{r["first"][1]} ({r["first"][2]})' if r['first'] else ''))
print(f'\nexact repeats ({len(dups)}): ' + ', '.join(f'm{a[0]}g{a[1]} = m{b[0]}g{b[1]} ({b[2]})' for a, b in dups))


def rec(xs):
    w = sum(1 for r in xs if r['won']); return f'{w}-{len(xs) - w}'


for v in ('y360', 'y374', None):
    xs = [r for r in rows if v is None or r['ver'] == v]
    po = defaultdict(list)
    for r in xs: po[r['opp']].append(r)
    L = [r for r in xs if not r['won']]
    print(f'\n{v or "both"}: {rec(xs)}; TOP7 {rec([r for r in xs if r["opp"] in lib.TOP7])}; ranked {rec([r for r in xs if r["rk"] == "R"])}, '
          f'unranked {rec([r for r in xs if r["rk"] == "u"])}; losses {len(L)}, median end r{lib.med([r["end"] for r in L])}, '
          f'eliminations {sum(1 for r in L if r["how"] == "ALL")} ({", ".join(sorted(set(r["opp"] for r in L if r["how"] == "ALL")))})')
    print('   ' + ', '.join(f'{o} {rec(p)}' for o, p in sorted(po.items())))

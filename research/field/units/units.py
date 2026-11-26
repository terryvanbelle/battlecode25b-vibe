#!/usr/bin/env python3
"""Per-unit output for one team in ReplayDump v3 dumps (owner prompt #15: which units are not pulling their weight).

  python3 units.py TEAM DUMPDIR...      each DUMPDIR holds g<i>.{meta.json,turns.tsv,actions.tsv}

Per unit: turns alive, and what its turns produced:
  own     tiles turned to our paint (paint rows of the unit on tiles not already ours; splasher paint rows included)
  pat     of those, inside the 5x5 of a ruin (pattern work)
  unp     enemy tiles it cleaned (mopper unpaint)
  drain   paint it drained from enemies (mopper)
  dmg     hp damage it dealt (to robots and towers)   twr: of that, to towers
  give    paint it gave to allies                     build: towers it completed
  idle    turns with no action row and no move
Output: per type, the share of units and turns that produced nothing, and the turn-weighted output; then the list
of the least productive long-lived units with what they were doing (position, paint) for a closer look."""
import csv, json, sys, os, collections, statistics as st

def rd(p):
    with open(p) as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); return [dict(zip(h, x)) for x in r]

def game(d, g, team):
    meta = json.load(open(f'{d}/g{g}.meta.json'))
    if meta['teamA'] == team: me = '1'
    elif meta['teamB'] == team: me = '2'
    else: return None
    W = meta['width']
    paint = [int(c) for c in meta['paint']]
    ruins = [tuple(r) for r in meta['ruins']]
    nearruin = set()
    for (rx, ry) in ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3): nearruin.add((rx + dx, ry + dy))
    acts = rd(f'{d}/g{g}.actions.tsv'); turns = rd(f'{d}/g{g}.turns.tsv')
    byturn = collections.defaultdict(list)
    for a in acts: byturn[(a['round'], a['id'])].append(a)
    U = {}
    last = {}
    mine = lambda v: (v in (1, 2)) if me == '1' else (v in (3, 4))
    # walk turns in order, applying each turn's paint actions to the grid as we go
    for t in turns:
        if t['team'] != me or t['type'] in ('PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER'):
            for a in byturn.get((t['round'], t['id']), []):
                if a['action'] == 'paint':
                    x, y = map(int, a['a'].split(',')); paint[x + y * W] = (1 if a['team'] == '1' else 3) + int(a['b'])
                elif a['action'] == 'unpaint':
                    x, y = map(int, a['a'].split(',')); paint[x + y * W] = 0
            continue
        i = t['id']
        u = U.get(i)
        if u is None:
            u = U[i] = dict(id=i, type=t['type'], born=int(t['round']), turns=0, own=0, pat=0, unp=0, drain=0, dmg=0,
                            twr=0, give=0, build=0, idle=0, zero=0, enemyTile=0, lastpos=None, trace=[])
        u['turns'] += 1; u['died'] = int(t['round'])
        pos = (int(t['x']), int(t['y']))
        acted = False
        for a in byturn.get((t['round'], i), []):
            k = a['action']
            if k == 'paint':
                x, y = map(int, a['a'].split(',')); idx = x + y * W
                if not mine(paint[idx]): u['own'] += 1; u['pat'] += (x, y) in nearruin
                paint[idx] = (1 if me == '1' else 3) + int(a['b']); acted = True
            elif k == 'unpaint':
                x, y = map(int, a['a'].split(',')); paint[x + y * W] = 0; u['unp'] += 1; acted = True
            elif k == 'drain': u['drain'] += int(a['b']); acted = True
            elif k == 'damage':
                u['dmg'] += int(a['b']); acted = True
            elif k == 'attack': acted = True
            elif k == 'transfer':
                if int(a['b']) > 0: u['give'] += int(a['b'])
                acted = True
            elif k == 'build': u['build'] += 1; acted = True
            elif k in ('mark', 'splash', 'mop', 'srp'): acted = True
        # tower damage: damage rows whose target is a tower
        for a in byturn.get((t['round'], i), []):
            if a['action'] == 'damage' and a['a'] in towers_of(acts, cache=d + str(g)): u['twr'] += int(a['b'])
        moved = u['lastpos'] is not None and pos != u['lastpos']
        if not acted and not moved: u['idle'] += 1
        if int(t['paint']) == 0: u['zero'] += 1
        here = paint[pos[0] + pos[1] * W]
        if here and not mine(here): u['enemyTile'] += 1
        if len(u['trace']) < 400: u['trace'].append((int(t['round']), pos, int(t['paint']), acted, moved))
        u['lastpos'] = pos
    return meta, list(U.values())

_tw = {}
def towers_of(acts, cache):
    if cache not in _tw:
        s = set()
        for a in acts:
            if a['action'] == 'spawn' and a['b'] in ('PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER'): s.add(a['a'])
        s |= {str(i) for i in range(1, 5)}     # starting towers (ids 1-4 in 3.1.0 replays; also see meta bodies)
        _tw[cache] = s
    return _tw[cache]

def main():
    team, dirs = sys.argv[1], sys.argv[2:]
    allu = []
    for d in dirs:
        g = 0
        while os.path.exists(f'{d}/g{g}.meta.json'):
            r = game(d, g, team)
            if r:
                meta, us = r
                for u in us: u['game'] = f'{os.path.basename(d)}/g{g} {meta["map"]}'
                allu += us
            g += 1
    print(f'{len(allu)} units of {team}')
    for ty in ('SOLDIER', 'SPLASHER', 'MOPPER'):
        us = [u for u in allu if u['type'] == ty]
        if not us: continue
        T = sum(u['turns'] for u in us)
        def per100(k): return 100.0 * sum(u[k] for u in us) / T
        nothing = [u for u in us if u['own'] + u['unp'] + u['drain'] + u['dmg'] + u['give'] + u['build'] == 0]
        print(f'\n{ty}: {len(us)} units, {T} unit-turns, median life {st.median(u["turns"] for u in us)}')
        print(f'  per 100 turns: own {per100("own"):.1f} (pattern {per100("pat"):.1f}), unpaint {per100("unp"):.1f}, '
              f'drain {per100("drain"):.1f}, dmg {per100("dmg"):.1f} (towers {per100("twr"):.1f}), give {per100("give"):.1f}, '
              f'build {per100("build"):.2f}')
        print(f'  idle turns {per100("idle"):.0f}%, at 0 paint {per100("zero"):.0f}%, ending on enemy paint {per100("enemyTile"):.0f}%')
        print(f'  produced nothing at all: {len(nothing)} units ({100*len(nothing)/len(us):.0f}%), '
              f'{sum(u["turns"] for u in nothing)} turns ({100*sum(u["turns"] for u in nothing)/T:.0f}%)')
        # output distribution
        out = sorted(us, key=lambda u: (u['own'] + u['unp'] + u['drain'] / 10 + u['dmg'] / 20 + u['give'] / 20 + 20 * u['build']) / max(1, u['turns']))
        print('  least productive with >= 30 turns:')
        for u in [u for u in out if u['turns'] >= 30][:6]:
            print(f"    {u['game']} id {u['id']} r{u['born']}-{u['died']} turns {u['turns']} own {u['own']} unp {u['unp']} drain {u['drain']} "
                  f"dmg {u['dmg']} give {u['give']} idle {u['idle']} zero {u['zero']} enemyTile {u['enemyTile']}")

if __name__ == '__main__':
    main()

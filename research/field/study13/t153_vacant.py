"""Topic 153: who comes to a fallen tower's ruin while it stands empty (follows t150: in our losses we rebuild 60 / 50 /
34% of our killed towers' ruins against their 91 / 92 / 80%, and the killers take 19-27% of ours).
Every tower killed by damage; the window is the death round + 1 until the ruin is built again (by anyone), 100 rounds,
or the game's end.  The paint grid is replayed (lib.replay_grid); robot positions are the turn rows of each round.
Per side whose tower fell and phase of the death, losses then wins:
  window        rounds in the window (median); share of window rounds with enemy paint in the 5x5 (our
                Pattern.contested: Soldier.pickRuin skips the ruin for SOL_CONTESTED_BAD = 50 rounds)
  visitors      own soldiers / moppers / splashers within r2 20 of the ruin (in sight of most of the 5x5), per window
                round, split into contested and clean rounds; enemy robots likewise
  seen, left    deaths whose ruin had an own soldier in sight in 5+ window rounds and got no own paint row in its 5x5
                in the window (seen and not worked), and of those how many were contested when seen
  work          own paint rows / own mop rows (unpaint) in the 5x5 per death; enemy paint rows in it
  outcome       rebuilt by the same side / taken by the killers / still empty when the window closed
  rebuilt ones  rounds contested before the rebuild; own mop rows in the 5x5 before it; the type (same / other)"""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if dx or dy]


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def analyse(G, S, P):
    W, H = G.W, G.H
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    builds = defaultdict(list)
    for a in G.acts:
        if a[4] == 'build':
            q = pos.get(int(a[5]))
            if q: builds[q].append((a[0], a[2], a[6]))
    robots = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.BOT: robots[t[0]].append((t[2], t[3], t[4], t[5]))
    deaths = []
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.TOW:
            v = int(a[5]); q = pos.get(v); s = G.team.get(v)
            if q and s: deaths.append(dict(r=a[0], q=q, side=s, ty=a[7]))
    if not deaths: P['games'] += 1; return
    for d in deaths:
        nxt = [b for b in builds.get(d['q'], ()) if b[0] > d['r']]
        d['next'] = nxt[0] if nxt else None
        d['close'] = min(nxt[0][0] if nxt else 10 ** 6, d['r'] + 100, G.end)
        d.update(rounds=0, cont=0, vis=defaultdict(int), own_paint=0, own_mop=0, en_paint=0, seen=0, seen_cont=0,
                 mop_before=0)
    tile_deaths = defaultdict(list)
    for k, d in enumerate(deaths):
        for dx, dy in OFFS: tile_deaths[(d['q'][0] + dx, d['q'][1] + dy)].append(k)
    cur = [0]

    def end_of_round(r, grid):
        for d in deaths:
            if not (d['r'] < r <= d['close']): continue
            if d['next'] and r >= d['next'][0]: continue
            x, y = d['q']; s = d['side']
            cont = False
            for dx, dy in OFFS:
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H:
                    o = lib.owner(grid[xx + yy * W])
                    if o and o != s: cont = True; break
            d['rounds'] += 1
            if cont: d['cont'] += 1
            tag = 'c' if cont else 'k'
            own_sol = 0
            for tm, ty, xx, yy in robots.get(r, ()):
                if (xx - x) ** 2 + (yy - y) ** 2 > 20: continue
                who = 'own' if tm == s else 'enemy'
                d['vis'][(who, ty, tag)] += 1
                if who == 'own' and ty == 'SOLDIER': own_sol += 1
            if own_sol:
                d['seen'] += 1
                if cont: d['seen_cont'] += 1

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0], a[0]):
                if r >= 1: end_of_round(r, grid)
            cur[0] = a[0]
        if a[4] in ('paint', 'unpaint'):
            x, y = map(int, a[5].split(','))
            for k in tile_deaths.get((x, y), ()):
                d = deaths[k]
                if not (d['r'] < a[0] <= d['close']) or (d['next'] and a[0] >= d['next'][0]): continue
                if a[2] == d['side']:
                    if a[4] == 'paint': d['own_paint'] += 1
                    else: d['own_mop'] += 1
                elif a[4] == 'paint': d['en_paint'] += 1

    grid = lib.replay_grid(G, hook)
    for r in range(cur[0], G.end + 1): end_of_round(r, grid)
    for d in deaths:
        p = ph(d['r'])
        side = 'us' if d['side'] == G.us else 'them'
        D = S[(side, p)]
        D['n'] += 1
        D['win_rounds'].append(d['rounds'])
        D['rounds'] += d['rounds']; D['cont'] += d['cont']
        for (who, ty, tag), v in d['vis'].items(): D[f'vis_{who}_{ty}_{tag}'] += v
        D['rounds_c'] += d['cont']; D['rounds_k'] += d['rounds'] - d['cont']
        D['own_paint'] += d['own_paint']; D['own_mop'] += d['own_mop']; D['en_paint'] += d['en_paint']
        if d['seen'] >= 5:
            D['seen5'] += 1
            if d['own_paint'] == 0:
                D['seen_left'] += 1
                if d['seen_cont'] >= 0.5 * d['seen']: D['seen_left_cont'] += 1
        nb = d['next']
        if nb and nb[0] <= d['close']:
            if nb[1] == d['side']:
                D['rebuilt'] += 1
                D['reb_cont'].append(d['cont'])
                D['reb_mop'].append(d['own_mop'])
                if nb[2] == d['ty']: D['reb_same'] += 1
            else: D['taken'] += 1
        else: D['empty'] += 1
    P['games'] += 1


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float))
    for key in [(s, p) for s in ('us', 'them') for p in range(3)]:
        for k in ('win_rounds', 'reb_cont', 'reb_mop'): S[key][k] = []
    P = defaultdict(int)
    for G in lib.games(which):
        analyse(G, S, P)
    ng = P['games']
    print(f'\n== {which}: {ng} games; towers killed by damage, by the side that lost them and the phase of the death')
    print(f'   {"":50s}' + ''.join(f'{PHN[p] + " us":>14s}{"them":>8s}' for p in range(3)))

    def row(name, f):
        cells = ''
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, p)]
                try: s = f(D)
                except ZeroDivisionError: s = '-'
                cells += f'{s:>14s}' if side == 'us' else f'{s:>8s}'
        print(f'   {name:50s}' + cells)
    row('killed (per game)', lambda D: f'{D["n"] / max(1, ng):.2f}')
    row('window rounds (median; until rebuilt, 100, end)', lambda D: f'{lib.med(D["win_rounds"])}')
    row('window rounds with enemy paint in the 5x5', lambda D: f'{100 * D["cont"] / D["rounds"]:.0f}%')
    for ty in ('SOLDIER', 'MOPPER', 'SPLASHER'):
        row(f'own {ty.lower()}s in r2 20, per contested round', lambda D, ty=ty: f'{D[f"vis_own_{ty}_c"] / D["rounds_c"]:.2f}')
        row(f'own {ty.lower()}s in r2 20, per clean round', lambda D, ty=ty: f'{D[f"vis_own_{ty}_k"] / D["rounds_k"]:.2f}')
    row('enemy robots in r2 20, per contested round', lambda D: f'{sum(D[f"vis_enemy_{t}_c"] for t in lib.BOT) / D["rounds_c"]:.2f}')
    row('enemy robots in r2 20, per clean round', lambda D: f'{sum(D[f"vis_enemy_{t}_k"] for t in lib.BOT) / D["rounds_k"]:.2f}')
    row('own soldier in sight 5+ rounds', lambda D: f'{100 * D["seen5"] / D["n"]:.0f}%')
    row('  and no own paint in the 5x5 (seen, left)', lambda D: f'{100 * D["seen_left"] / D["n"]:.0f}%')
    row('    contested on most of the rounds seen', lambda D: f'{100 * D["seen_left_cont"] / D["n"]:.0f}%')
    row('own paint rows in the 5x5 per death', lambda D: f'{D["own_paint"] / D["n"]:.1f}')
    row('own mop rows in the 5x5 per death', lambda D: f'{D["own_mop"] / D["n"]:.1f}')
    row('enemy paint rows in the 5x5 per death', lambda D: f'{D["en_paint"] / D["n"]:.1f}')
    row('rebuilt by the same side in the window', lambda D: f'{100 * D["rebuilt"] / D["n"]:.0f}%')
    row('  contested rounds before the rebuild (median)', lambda D: f'{lib.med(D["reb_cont"])}')
    row('  own mop rows in the 5x5 before it (median)', lambda D: f'{lib.med(D["reb_mop"])}')
    row('  same type as before', lambda D: f'{100 * D["reb_same"] / max(1, D["rebuilt"]):.0f}%')
    row('taken by the killers in the window', lambda D: f'{100 * D["taken"] / D["n"]:.0f}%')
    row('still empty when the window closed', lambda D: f'{100 * D["empty"] / D["n"]:.0f}%')

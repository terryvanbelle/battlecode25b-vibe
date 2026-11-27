"""Topic 110: survival on one tower.  An episode starts in a round (r10+) in which a side stands on at most one tower
(each side starts on two) and ends when it stands on two again (recovered), at elimination, or at the game end.
Two views per side and game: the FIRST episode (how often a side recovers from it) and the LAST episode when it runs
to the game end (the one that ends the game).  Per episode, both sides (ours mostly in lost games, theirs mostly in
our wins):
  start state     round, chips, robots S/X/M, the soldiers' paint, the tower left (type)
  ruins           free ruins (no tower of either side) at the start: how many have no enemy paint in their 5x5, and the
                  distance (d2) from the nearest soldier of the side to the nearest such clean ruin
  soldier-turns   during the episode (first 60 rounds): build / mark / ruin paint / siege / refill / cover / none and
                  'at 0 paint', as in t109
  outcome         recovered (rounds to it) / eliminated / still on <= 1 at the end; towers built during the episode
Lost and won games of all opponents."""
import lib
from collections import Counter, defaultdict

LABS = ('build', 'mark', 'ruin', 'siege', 'refill', 'cover', 'none')


def grid_at(G, r):
    grid = list(G.paint0); W = G.W
    for a in G.acts:
        if a[0] > r: break
        if a[4] == 'paint':
            x, y = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        elif a[4] == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
    return grid


def episodes(G, side):
    out = []; r = 10; tow = lambda rr: lib.rv(G, side, rr, 'tow')
    while r <= G.end:
        if tow(r) <= 1:
            r0 = r
            while r <= G.end and tow(r) <= 1: r += 1
            out.append((r0, r))   # r = first round back at >= 2 towers, or G.end + 1
        r += 1
    return out


def study(G, side, r0, r1, b, d):
    k = 'A' if side == 1 else 'B'
    R = G.rounds[r0 - 1]
    st = dict(r0=r0, chips=int(R['money' + k]), S=int(R['sol' + k]), X=int(R['spl' + k]), M=int(R['mop' + k]))
    sol = [t for t in G.turns if t[0] == r0 and t[2] == side and t[3] == 'SOLDIER']
    st['sol_paint'] = lib.med([t[7] for t in sol]) if sol else None
    left = lib.towers_alive(G, side, r0, b, d)
    st['left'] = left[0][2][:1] if left else '-'
    standing = set((t[4], t[5]) for s in (1, 2) for t in lib.towers_alive(G, s, r0, b, d))
    grid = grid_at(G, r0); W = G.W
    enemy = (3, 4) if side == 1 else (1, 2)
    free = [ru for ru in G.ruins if ru not in standing]
    clean = []
    for (rx, ry) in free:
        e = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x, y = rx + dx, ry + dy
                if 0 <= x < G.W and 0 <= y < G.H and grid[x + y * W] in enemy: e += 1
        if e == 0: clean.append((rx, ry))
    st['free'] = len(free); st['clean'] = len(clean)
    st['near_clean'] = min([lib.d2((t[4], t[5]), c) for t in sol for c in clean] or [None], key=lambda v: 10 ** 9 if v is None else v)
    # outcome
    if r1 > G.end:
        lost_side = (side == G.us and G.won_op) or (side == G.op and not G.won_op)
        st['out'] = 'elim' if (lost_side and G.wintype.startswith('ALL')) else 'held<=1'
    else: st['out'] = 'recovered'
    st['dur'] = min(r1, G.end + 1) - r0
    st['built'] = Counter(x[2][:1] for x in b if x[3] == side and r0 <= x[0] < r1)
    # soldier-turn labels, first 60 rounds of the episode
    tower_ids = set(x[1] for x in b)
    ruin_of = {}
    for (rx, ry) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3): ruin_of.setdefault((rx + dx, ry + dy), (rx, ry))
    hi = min(r1, r0 + 60)
    acts = defaultdict(list)
    for a in G.acts:
        if a[0] < r0: continue
        if a[0] >= hi: break
        if a[2] == side and a[3] == 'SOLDIER': acts[(a[0], a[1])].append(a)
    c = Counter()
    for t in G.turns:
        if not (r0 <= t[0] < hi) or t[2] != side or t[3] != 'SOLDIER': continue
        A = acts.get((t[0], t[1]), ()); kinds = [a[4] for a in A]
        lab = 'none'
        if 'build' in kinds: lab = 'build'
        elif 'mark' in kinds: lab = 'mark'
        else:
            paints = [a for a in A if a[4] == 'paint']
            att = [a for a in A if a[4] == 'attack' and a[5].isdigit() and int(a[5]) in tower_ids]
            tr = [a for a in A if a[4] == 'transfer' and a[6].lstrip('-').isdigit() and int(a[6]) < 0]
            if paints:
                p = tuple(map(int, paints[0][5].split(',')))
                lab = 'ruin' if (p in ruin_of and ruin_of[p] != p) else 'cover'
            elif att: lab = 'siege'
            elif tr: lab = 'refill'
        c[lab] += 1; c['_turns'] += 1
        if t[7] == 0: c['_zero'] += 1
    st['labs'] = c
    return st


def run(name, rows):
    print(f'\n== {name}: {len(rows)} episodes')
    if not rows: return
    oc = Counter(s['out'] for s in rows)
    print(f'   outcome: {dict(oc)}; median start r{lib.med([s["r0"] for s in rows])}, duration {lib.med([s["dur"] for s in rows])} rounds')
    for o in ('recovered', 'elim', 'held<=1'):
        rs = [s for s in rows if s['out'] == o]
        if not rs: continue
        print(f'   {o:9s} {len(rs):3d}: start r{lib.med([s["r0"] for s in rs])}, chips {lib.med([s["chips"] for s in rs])}, robots S/X/M '
              f'{lib.med([s["S"] for s in rs])}/{lib.med([s["X"] for s in rs])}/{lib.med([s["M"] for s in rs])}, soldier paint {lib.med([s["sol_paint"] for s in rs if s["sol_paint"] is not None])}, '
              f'tower left {dict(Counter(s["left"] for s in rs))}; free ruins {lib.med([s["free"] for s in rs])} of which clean {lib.med([s["clean"] for s in rs])}; '
              f'nearest clean ruin d2 {lib.med([s["near_clean"] for s in rs if s["near_clean"] is not None])} '
              f'(none clean: {sum(1 for s in rs if s["clean"] == 0)}); duration {lib.med([s["dur"] for s in rs])}; towers built during: {dict(sum((s["built"] for s in rs), Counter()))}')
    tot = sum((s['labs'] for s in rows), Counter())
    T = max(1, tot['_turns'])
    print('   soldier-turns, first 60 rounds of the episode: ' + ', '.join(f'{l} {100 * tot[l] / T:.1f}%' for l in LABS)
          + f', at 0 paint {100 * tot["_zero"] / T:.1f}% ({tot["_turns"]} turns)')
    for o in ('recovered', 'elim', 'held<=1'):
        rs = [s for s in rows if s['out'] == o]
        if not rs: continue
        t2 = sum((s['labs'] for s in rs), Counter()); T2 = max(1, t2['_turns'])
        print(f'      {o:9s}: ' + ', '.join(f'{l} {100 * t2[l] / T2:.1f}%' for l in LABS) + f', at 0 paint {100 * t2["_zero"] / T2:.1f}% ({t2["_turns"]} turns)')


F = {k: [] for k in ('ours_l', 'theirs_l', 'ours_w', 'theirs_w')}
L = {k: [] for k in F}
per = []
tot_low = {k: [] for k in F}
for G in lib.games('all'):
    b, d = lib.tower_events(G)
    for side in (G.us, G.op):
        key = ('ours_' if side == G.us else 'theirs_') + ('l' if G.won_op else 'w')
        ep = episodes(G, side)
        tot_low[key].append(sum(min(r1, G.end + 1) - r0 for r0, r1 in ep))
        if not ep: continue
        st = study(G, side, ep[0][0], ep[0][1], b, d)
        st['n_ep'] = len(ep)
        F[key].append(st)
        if ep[-1][1] > G.end:
            stl = st if len(ep) == 1 else study(G, side, ep[-1][0], ep[-1][1], b, d)
            stl['n_ep'] = len(ep)
            L[key].append(stl)
            if key == 'ours_l':
                per.append((f'm{G.m}g{G.g} {G.ver:5s} {G.team_name[:12]:12s} {G.map[:14]:14s} {G.wintype[:3]}{G.end:<5d}', stl))
    lib.lite(G)

for key, name in (('ours_l', 'OURS in lost games'), ('theirs_l', 'THEIRS in lost games'), ('ours_w', 'OURS in won games'), ('theirs_w', 'THEIRS in won games')):
    n = len(tot_low[key])
    print(f'\n######## {name}: {n} games; games with an episode {sum(1 for v in tot_low[key] if v > 0)}; '
          f'rounds at <= 1 tower, median where > 0: {lib.med([v for v in tot_low[key] if v > 0])}')
    run(name + ', FIRST episode', F[key])
    run(name + ', LAST episode that runs to the end', L[key])
print('\nper lost game whose last episode of ours runs to the end:')
for s0, st in per:
    lb = st['labs']; T = max(1, lb['_turns'])
    print(f'   {s0} r{st["r0"]:<4d} {st["out"]:9s} dur {st["dur"]:4d} ${st["chips"]:5d} S/X/M {st["S"]}/{st["X"]}/{st["M"]} paint {st["sol_paint"]} left {st["left"]} '
          f'clean {st["clean"]}/{st["free"]} near {st["near_clean"]} built {dict(st["built"])} | siege {100 * lb["siege"] / T:.0f}% ruin {100 * (lb["ruin"] + lb["mark"]) / T:.0f}% '
          f'cover {100 * lb["cover"] / T:.0f}% none {100 * lb["none"] / T:.0f}% zero {100 * lb["_zero"] / T:.0f}% (eps {st["n_ep"]})')

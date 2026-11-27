"""Topic 111: tower patterns that never get finished, both sides.  A soldier cannot paint over enemy paint (RULES 5.2):
one enemy tile in a ruin's 5x5 blocks the pattern until a mopper or a splasher's inner 3x3 clears it.
An ATTEMPT is a side's painting on a free ruin: 8 or more paints by the side inside the 5x5 while no tower stands on
the ruin, gaps of at most 30 rounds.  It is COMPLETED when the side builds a tower there within 10 rounds of its last
paint, TAKEN when the other side builds there first, otherwise ABANDONED.  For abandoned attempts the replayed grid
at the side's last paint tells how many enemy tiles sat in the 5x5 (blocked = 1 or more), and how many tiles the side
had there.  Per side, lost and won games and phase of the attempt's start: attempts, completed %, abandoned blocked %,
paint spent on abandoned attempts (5 per paint), abandoned attempts the side still built on later (a wait for chips or
a return), paint spent after the first enemy tile appeared in blocked abandoned attempts, the completion rate of attempts that met
an enemy tile with and without an own splasher / mopper within d2 20 after that, and who cleared enemy tiles inside the side's attempts (the side's
moppers: unpaint rows; splashers: paint over enemy tiles)."""
import lib
from collections import defaultdict, Counter

PH = ((1, 100, 'r1-100'), (101, 250, 'r101-250'), (251, 2000, 'r251+'))


def analyse(G):
    b, d = lib.tower_events(G)
    W = G.W
    ruin_of = {}
    for (rx, ry) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy: ruin_of[(rx + dx, ry + dy)] = (rx, ry)
    # standing intervals per ruin
    died = {x[1]: x[0] for x in d}
    iv = defaultdict(list)
    for x in b: iv[(x[4], x[5])].append((x[0], died.get(x[1], 10 ** 6), x[3]))
    builds = defaultdict(list)
    for x in b:
        if x[0] > 0: builds[(x[4], x[5])].append((x[0], x[3]))

    def standing(ru, r):
        return any(f <= r < t for (f, t, s) in iv.get(ru, ()))
    # replay the grid; record per (side, ruin) the paint events on free ruins with the enemy-tile count after each
    grid = list(G.paint0)
    who = {}                   # tile index -> type of the robot that last painted it
    ev = defaultdict(list)     # (side, ruin) -> [(round, enemy tiles in 5x5, own tiles in 5x5, enemy painter types)]
    clears = defaultdict(Counter)   # (side) -> clearing of enemy tiles inside ruins the side is attempting: by type
    def count(ru, side):
        e = o = 0; ty = Counter()
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if not (dx or dy): continue
                x, y = ru[0] + dx, ru[1] + dy
                if 0 <= x < G.W and 0 <= y < G.H:
                    v = grid[x + y * W]
                    if v and lib.owner(v) == side: o += 1
                    elif v: e += 1; ty[who.get(x + y * W, 'map')] += 1
        return e, o, ty
    for a in G.acts:
        k = a[4]
        if k not in ('paint', 'unpaint'): continue
        x, y = map(int, a[5].split(','))
        ru = ruin_of.get((x, y))
        before = grid[x + y * W]
        if k == 'paint':
            sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
            who[x + y * W] = a[3]
        else:
            grid[x + y * W] = 0
        if ru is None or standing(ru, a[0]): continue
        if k == 'paint' and a[3] == 'SOLDIER':
            e, o, ty = count(ru, a[2])
            ev[(a[2], ru)].append((a[0], e, o, ty))
        # an enemy tile in this free ruin cleared by side s (unpaint by a mopper, or a splasher painting over it)
        if before and lib.owner(before) != a[2] and (k == 'unpaint' or a[3] == 'SPLASHER'):
            clears[a[2]][a[3]] += 1
    out = []
    bt = lib.by_round_turns(G)
    def helpers(side, ru, r0, r1):
        # rounds in [r0, r1] with an own splasher / mopper within d2 <= 20 (in view) of the ruin
        sp = mo = 0
        for r in range(r0, r1 + 1):
            ts = [t for t in bt.get(r, ()) if t[2] == side and lib.d2((t[4], t[5]), ru) <= 20]
            if any(t[3] == 'SPLASHER' for t in ts): sp += 1
            if any(t[3] == 'MOPPER' for t in ts): mo += 1
        return sp, mo
    for (side, ru), es in ev.items():
        # split into attempts at gaps > 30 rounds
        cur = [es[0]]
        groups = []
        for e in es[1:]:
            if e[0] - cur[-1][0] > 30: groups.append(cur); cur = [e]
            else: cur.append(e)
        groups.append(cur)
        for gp in groups:
            if len(gp) < 8: continue
            r0, rl = gp[0][0], gp[-1][0]
            nb = [x for x in builds.get(ru, ()) if x[0] >= r0]
            res = 'abandoned'
            if nb and nb[0][0] <= rl + 10: res = 'completed' if nb[0][1] == side else 'taken'
            elif nb and nb[0][1] != side and nb[0][0] <= rl + 60: res = 'taken'
            later = res == 'abandoned' and any(x[1] == side for x in nb)
            fb = next((i for i, e in enumerate(gp) if e[1] > 0), None)
            hs = helpers(side, ru, gp[fb][0], rl) if fb is not None else (0, 0)
            out.append(dict(side=side, ruin=ru, r0=r0, rl=rl, n=len(gp), res=res, enemy=gp[-1][1], own=gp[-1][2], ty=gp[-1][3],
                            later=later, after_block=0 if fb is None else len(gp) - fb, sp=hs[0], mo=hs[1], dur=rl - r0 + 1,
                            met=fb is not None))
    return out, clears


def table(name, rows, clears, games):
    print(f'\n== {name}: {games} games')
    for who in ('us', 'them'):
        R = [x for x in rows if x['who'] == who]
        print(f'   {who}: {len(R)} attempts; ' + '; '.join(
            f'{p[2]} {len([x for x in R if p[0] <= x["r0"] <= p[1]])}' for p in PH))
        for p in PH + ((1, 2000, 'all'),):
            S = [x for x in R if p[0] <= x['r0'] <= p[1]]
            if not S: continue
            c = Counter(x['res'] for x in S)
            ab = [x for x in S if x['res'] == 'abandoned']
            bl = [x for x in ab if x['enemy'] > 0]
            print(f'      {p[2]:9s} n {len(S):4d}: completed {100 * c["completed"] / len(S):3.0f}%, taken by the other side {100 * c["taken"] / len(S):3.0f}%, '
                  f'abandoned {100 * c["abandoned"] / len(S):3.0f}% (of those blocked by enemy paint {100 * len(bl) / max(1, len(ab)):3.0f}%, '
                  f'median enemy tiles {lib.med([x["enemy"] for x in bl])}, own tiles {lib.med([x["own"] for x in ab])}); '
                  f'paint spent on abandoned {5 * sum(x["n"] for x in ab)}; abandoned but built by the side later {sum(1 for x in ab if x["later"])}; '
                  f'paint spent after the first enemy tile, blocked abandoned {5 * sum(x["after_block"] for x in bl)}')
        bl = [x for x in R if x['res'] == 'abandoned' and x['enemy'] > 0]
        print(f'      enemy tiles in the blocked 5x5s, by the type that painted them: {dict(sum((x["ty"] for x in bl), Counter()))}')
        M = [x for x in R if x['met']]
        if M:
            def cp(S): return f'{100 * sum(1 for x in S if x["res"] == "completed") / len(S):.0f}% of {len(S)}' if S else '-'
            print(f'      attempts that met an enemy tile in the 5x5 ({len(M)}, {100 * len(M) / len(R):.0f}% of all): completed {cp(M)}; '
                  f'with an own splasher in view after the first enemy tile {cp([x for x in M if x["sp"]])}, a mopper {cp([x for x in M if x["mo"]])}, '
                  f'neither {cp([x for x in M if not x["sp"] and not x["mo"]])}')
        if bl:
            print(f'      blocked abandoned attempts ({len(bl)}): an own splasher in view of the ruin after the first enemy tile {sum(1 for x in bl if x["sp"])} '
                  f'({100 * sum(1 for x in bl if x["sp"]) / len(bl):.0f}%), an own mopper {sum(1 for x in bl if x["mo"])} ({100 * sum(1 for x in bl if x["mo"]) / len(bl):.0f}%); '
                  f'median attempt length {lib.med([x["dur"] for x in bl])} rounds, splasher-rounds in view {lib.med([x["sp"] for x in bl])}')
        cl = clears[who]
        print(f'      enemy tiles cleared inside free ruins: {dict(cl)}')


rows_l, rows_w = [], []
cl_l = {'us': Counter(), 'them': Counter()}; cl_w = {'us': Counter(), 'them': Counter()}
n_l = n_w = 0
per = []
for G in lib.games('all'):
    out, clears = analyse(G)
    for x in out: x['who'] = 'us' if x['side'] == G.us else 'them'
    if G.won_op:
        rows_l += out; n_l += 1
        cl_l['us'].update(clears[G.us]); cl_l['them'].update(clears[G.op])
        us = [x for x in out if x['who'] == 'us']
        per.append((f'm{G.m}g{G.g} {G.ver:5s} {G.team_name[:12]:12s} {G.map[:14]:14s} {G.wintype[:3]}{G.end:<5d}',
                    len(us), sum(1 for x in us if x['res'] == 'completed'), sum(1 for x in us if x['res'] == 'abandoned' and x['enemy'] > 0),
                    sum(1 for x in out if x['who'] == 'them'), sum(1 for x in out if x['who'] == 'them' and x['res'] == 'completed'),
                    sum(1 for x in us if x['met']), 5 * sum(x['after_block'] for x in us if x['res'] == 'abandoned' and x['enemy'] > 0)))
    else:
        rows_w += out; n_w += 1
        cl_w['us'].update(clears[G.us]); cl_w['them'].update(clears[G.op])
    lib.lite(G)

table('LOST games', rows_l, cl_l, n_l)
table('WON games', rows_w, cl_w, n_w)
print('\nper lost game: our attempts / completed / abandoned-blocked / met an enemy tile / paint after the first enemy tile (blocked abandoned) | their attempts / completed')
for p in per: print(f'   {p[0]} us {p[1]:3d} / {p[2]:3d} / {p[3]:3d} / {p[6]:3d} / {p[7]:5d} | them {p[4]:3d} / {p[5]:3d}')

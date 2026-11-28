"""Topic 191 (new; follows t183 and t157): do our own SRPs break the patterns of our drained L1 money towers?  t183: 30 /
36% of our soldiers' dry money-tower visits in r101-200 / r201-300 of our losses are at towers whose 5x5 holds no
enemy paint but empty or wrong-colour tiles ('pattern wrong'), so the tower cannot churn; t157: 74-82% of our SRPs
beside one of our money towers disagree with its pattern, nearly all picked before the soldier had seen the tower.
For every dry visit (t183's definition) by a soldier or splasher at an L1 money tower of its side while the side
holds 2000+ chips and the 5x5 holds no enemy paint: the wrong tiles, split into empty tiles and own paint of the
wrong colour; and of the latter, those inside the 5x5 of an SRP the side completed before the arrival whose colour
there matches the SRP pattern (the SRP put it there, or kept it).  Per side and phase; losses and wins.
Also, for soldiers at a broken pattern with 1-3 wrong tiles (Churn.repairPattern repaints one wrong tile in attack
range, r2 9, per turn of the churn wait and does not move): was a wrong tile within r2 9 of the soldier at its arrival
turn, at any turn of its stay beside the tower, and did it hold 5+ paint then."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 300), (301, 2000))
PHN = ('r1-100', 'r101-200', 'r201-300', 'r301+')
UT = ('SOLDIER', 'SPLASHER')
LOW = {'SOLDIER': 100, 'SPLASHER': 150}
FULL = {'SOLDIER': 150, 'SPLASHER': 225}
WHY = ('L2+', 'chips < 2000', 'enemy paint', 'pattern wrong', 'enemy in view', 'none')


def ph(r):
    for j, (lo, hi) in enumerate(PH):
        if lo <= r <= hi: return j
    return None


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def analyse(G):
    side = lambda team: 'us' if team == G.us else 'them'
    tpos, tkind, tteam, tpaint = {}, {}, {}, defaultdict(dict)
    traj = defaultdict(list)
    rr = defaultdict(int)
    for t in G.turns:
        if t[3] in lib.TOW:
            tpos[t[1]] = (t[4], t[5]); tkind[t[1]] = t[3]; tteam[t[1]] = t[2]; tpaint[t[1]][t[0]] = t[7]
        elif t[3] in UT:
            traj[t[1]].append((t[0], t[4], t[5], t[7]))
            rr[(side(t[2]), ph(t[0]), t[3])] += 1
    level = defaultdict(lambda: [(0, 1)])   # tower id -> [(round, level)]
    wd = defaultdict(list)                  # robot -> [(round, tower, amount)]
    paints = defaultdict(set)
    removed = {}
    builds = defaultdict(list)
    for a in G.acts:
        k = a[4]
        if k == 'startlevel': level[int(a[5])] = [(0, int(a[6]))]
        elif k == 'upgrade': level[int(a[5])].append((a[0], int(a[6])))
        elif k == 'transfer' and a[3] in UT:
            amt = int(a[6]) if a[6] else 0
            if amt < 0: wd[a[1]].append((a[0], int(a[5]), -amt))
        elif k in ('paint', 'splash') and a[3] in UT: paints[a[1]].add(a[0])
        elif k == 'died' and a[7] in lib.TOW: removed[int(a[5])] = a[0]
        elif k == 'build':
            tid = int(a[5])
            if tid in tpos: builds[tpos[tid]].append(a[0])

    def lvl(tid, r):
        v = 1
        for q, l in level[tid]:
            if q <= r: v = l
        return v
    alive = {tid: set(d) for tid, d in tpaint.items()}
    visits = []
    for i, tr in traj.items():
        typ = G.typ.get(i); team = G.team.get(i)
        own = [tid for tid in tpos if tteam[tid] == team]
        wds = wd.get(i, [])
        k = 1
        while k < len(tr):
            r, x, y, p = tr[k]
            if tr[k - 1][3] >= LOW[typ]: k += 1; continue
            hit = None
            for tid in own:
                tp = tpos[tid]
                if (r in alive[tid] or r - 1 in alive[tid]) and cheb((x, y), tp) == 1 and cheb(tr[k - 1][1:3], tp) > 1:
                    hit = tid; break
            if hit is None: k += 1; continue
            tid = hit; tp = tpos[tid]
            e = k
            while e + 1 < len(tr) and cheb(tr[e + 1][1:3], tp) <= 1 and tr[e + 1][0] == tr[e][0] + 1: e += 1
            r0, r1 = tr[k][0], tr[e][0]
            taken = sum(w[2] for w in wds if w[1] == tid and r0 <= w[0] <= r1)
            ch = tid in removed and r0 <= removed[tid] <= r1 + 2 and any(removed[tid] <= b <= removed[tid] + 5 for b in builds[tp])
            dry = not ch and taken == 0 and tr[e][3] < FULL[typ]
            v = dict(i=i, typ=typ, team=team, side=side(team), r0=r0, r1=r1, k=k, e=e, tid=tid, tp=tp, kind=tkind[tid], dry=dry,
                     lvl=lvl(tid, r0), chips=lib.money(G, team, r0 - 1))
            visits.append(v)
            k = e + 1
    # grid state (enemy / wrong tiles of the money pattern) and enemy robots in view, at each dry money visit's arrival
    need = defaultdict(list)
    for v in visits:
        if v['dry'] and v['kind'] == 'MONEY_TOWER': need[v['r0']].append(v)
    rounds_sorted = sorted(need)
    st = {'ix': 0}

    def check(grid, upto):
        while st['ix'] < len(rounds_sorted) and rounds_sorted[st['ix']] <= upto:
            for v in need[rounds_sorted[st['ix']]]:
                tx, ty = v['tp']; en = wr = 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx == 0 and dy == 0: continue
                        xx, yy = tx + dx, ty + dy
                        if not (0 <= xx < G.W and 0 <= yy < G.H): wr += 1; continue
                        g = grid[xx + yy * G.W]
                        o = lib.owner(g)
                        if o and o != v['team']: en += 1; continue
                        want = (2 if lib.secondary('MONEY_TOWER', dx, dy) else 1) + (2 if v['team'] == 2 else 0)
                        if g != want: wr += 1; v.setdefault('wt', []).append((xx, yy, g))
                v['en'], v['wr'] = en, wr
            st['ix'] += 1
    last = {'r': 0}

    def hook(a, grid):
        if a[0] != last['r']:
            check(grid, a[0] - 1); last['r'] = a[0]
    if rounds_sorted:
        g = lib.replay_grid(G, hook); check(g, 10 ** 9)
        want_r = set(r - 1 for r in rounds_sorted) | set(rounds_sorted)
        pos_r = defaultdict(list)
        for t in G.turns:
            if t[0] in want_r and t[3] in lib.BOT: pos_r[t[0]].append((t[4], t[5], t[2]))
        for r0, vs in need.items():
            for v in vs:
                tx, ty = v['tp']
                v['env'] = any(tm != v['team'] and (x - tx) ** 2 + (y - ty) ** 2 <= 20 for x, y, tm in pos_r.get(r0 - 1, []) + pos_r.get(r0, []))
    for v in visits:
        if not (v['dry'] and v['kind'] == 'MONEY_TOWER'): continue
        if v['lvl'] >= 2: v['why'] = 'L2+'
        elif v['chips'] < 2000: v['why'] = 'chips < 2000'
        elif v.get('en', 0) > 0: v['why'] = 'enemy paint'
        elif v.get('wr', 0) > 0: v['why'] = 'pattern wrong'
        elif v.get('env'): v['why'] = 'enemy in view'
        else: v['why'] = 'none'
    # episodes: from a dry money visit to the next withdrawal of 30+ (any tower) or the robot's last turn
    eps = []
    byrob = defaultdict(list)
    for v in visits: byrob[v['i']].append(v)
    for i, vs in byrob.items():
        tr = traj[i]; wds = sorted(wd.get(i, []))
        open_until = -1
        for v in vs:
            if v['r0'] <= open_until or not (v['dry'] and v['kind'] == 'MONEY_TOWER'): continue
            nxt = [w[0] for w in wds if w[0] > v['r0'] and w[2] >= 30]
            r_end = nxt[0] if nxt else tr[-1][0]
            died = not nxt and tr[-1][0] < G.end
            open_until = r_end
            seg = [t for t in tr if v['r0'] <= t[0] <= r_end]
            tp = v['tp']
            reent = 0
            for a, b in zip(seg, seg[1:]):
                if cheb(b[1:3], tp) == 1 and cheb(a[1:3], tp) > 1: reent += 1
            near = sum(1 for t in seg if cheb(t[1:3], tp) <= 3)
            zero = sum(1 for t in seg if t[3] == 0)
            pnt = sum(1 for q in paints.get(i, ()) if v['r0'] <= q <= r_end)
            # nearest own tower holding 60+ paint at the arrival
            best = None
            for tid in tpos:
                if tteam[tid] != v['team'] or tid == v['tid']: continue
                pp = tpaint[tid].get(v['r0'] - 1, tpaint[tid].get(v['r0']))
                if pp is None or pp < 60: continue
                d = cheb(tr[v['k']][1:3], tpos[tid])
                if best is None or d < best: best = d
            eps.append(dict(side=v['side'], typ=v['typ'], ph=ph(v['r0']), why=v['why'], n=r_end - v['r0'], reent=reent, near=near,
                            zero=zero, died=died, refilled=bool(nxt), pnt=pnt, alt=best, lvl=v['lvl']))
    return visits, eps, rr


def report(tag, V, ng):
    print(f'\n== {tag}: {ng} games; dry visits at L1 money towers with 2000+ chips and no enemy paint in the 5x5 (us / them)')
    print(f'     {"":58s}' + ''.join(f'{n:>16s}' for n in PHN))

    def row(name, fn):
        cells = ''
        for j in range(len(PH)):
            c = []
            for sd in ('us', 'them'):
                E = [v for v in V if v['side'] == sd and ph(v['r0']) == j]
                c.append(fn(E))
            cells += f'{c[0] + " / " + c[1]:>16s}'
        print(f'     {name:58s}' + cells)
    row('visits', lambda E: str(len(E)))
    row('  pattern intact (%)', lambda E: f'{100 * sum(not v.get("wt") for v in E) / len(E):.0f}' if E else '-')
    W = lambda E: [v for v in E if v.get('wt')]
    row('  wrong tiles per broken pattern (median)', lambda E: str(lib.med([len(v['wt']) for v in W(E)])))
    row('    empty (% of wrong tiles)', lambda E: f'{100 * sum(t[3] == "empty" for v in W(E) for t in v["wt2"]) / max(1, sum(len(v["wt2"]) for v in W(E))):.0f}' if W(E) else '-')
    row('    own wrong colour, SRP-coloured (% of wrong tiles)', lambda E: f'{100 * sum(t[3] == "srp" for v in W(E) for t in v["wt2"]) / max(1, sum(len(v["wt2"]) for v in W(E))):.0f}' if W(E) else '-')
    row('    own wrong colour, other (% of wrong tiles)', lambda E: f'{100 * sum(t[3] == "own" for v in W(E) for t in v["wt2"]) / max(1, sum(len(v["wt2"]) for v in W(E))):.0f}' if W(E) else '-')
    row('  broken patterns with an SRP-coloured tile (%)', lambda E: f'{100 * sum(any(t[3] == "srp" for t in v["wt2"]) for v in W(E)) / len(W(E)):.0f}' if W(E) else '-')
    S = lambda E: [v for v in W(E) if v['typ'] == 'SOLDIER' and len(v['wt']) <= 3]
    row('  soldiers at 1-3 wrong tiles: visits', lambda E: str(len(S(E))))
    row('    a wrong tile in r2 9 at the arrival (%)', lambda E: f'{100 * sum(v["reach0"] for v in S(E)) / len(S(E)):.0f}' if S(E) else '-')
    row('    ... at any turn of the stay (%)', lambda E: f'{100 * sum(v["reach"] for v in S(E)) / len(S(E)):.0f}' if S(E) else '-')
    row('    ... with 5+ paint then (%)', lambda E: f'{100 * sum(v["reachp"] for v in S(E)) / len(S(E)):.0f}' if S(E) else '-')
    row('    stay beside the tower, rounds (median)', lambda E: str(lib.med([v['r1'] - v['r0'] + 1 for v in S(E)])))
    row('  broken patterns whose only wrong tiles are SRP-coloured (%)', lambda E: f'{100 * sum(all(t[3] == "srp" for t in v["wt2"]) for v in W(E)) / len(W(E)):.0f}' if W(E) else '-')


AGG = {'lost': [[], 0], 'won': [[], 0]}
for G in lib.games('all'):
    srps = [(a[0], a[2], tuple(map(int, a[5].split(',')))) for a in G.acts if a[4] == 'srp']
    V, EP, rr = analyse(G)
    pos = defaultdict(dict)
    for t in G.turns:
        if t[3] == 'SOLDIER': pos[t[1]][t[0]] = (t[4], t[5], t[7])
    keep = []
    for v in V:
        if not (v['dry'] and v['kind'] == 'MONEY_TOWER' and v['lvl'] == 1 and v['chips'] >= 2000 and v.get('en', 1) == 0): continue
        cs = [c for (r, tm, c) in srps if tm == v['team'] and r < v['r0']]
        wt2 = []
        for (xx, yy, g) in v.get('wt', []):
            o = lib.owner(g)
            if not o: wt2.append((xx, yy, g, 'empty')); continue
            sec = g in (2, 4)
            hit = any(max(abs(xx - c[0]), abs(yy - c[1])) <= 2 and lib.secondary('SRP', xx - c[0], yy - c[1]) == sec for c in cs)
            wt2.append((xx, yy, g, 'srp' if hit else 'own'))
        v['wt2'] = wt2
        v['reach0'] = v['reach'] = v['reachp'] = False
        if v['typ'] == 'SOLDIER' and v.get('wt'):
            for r in range(v['r0'], v['r1'] + 1):
                q = pos[v['i']].get(r)
                if not q: continue
                ok = any((q[0] - w[0]) ** 2 + (q[1] - w[1]) ** 2 <= 9 for w in v['wt'])
                if ok:
                    v['reach'] = True
                    if r == v['r0']: v['reach0'] = True
                    if q[2] >= 5: v['reachp'] = True
        keep.append(v)
    k = 'lost' if G.won_op else 'won'
    AGG[k][0].extend(keep); AGG[k][1] += 1
    G.turns = G.acts = None
for k in ('lost', 'won'): report(k, *AGG[k])

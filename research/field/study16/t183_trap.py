"""Topic 183 (new): the dry-money-tower trap.  Unit.refill (bots/y360/Unit.java:19-33) skips a tower flagged dry,
except a MONEY-kind tower while chips >= CHURN_CHIPS (2000): then the flag is ignored and the nearest money tower stays
the refill target, on the bet that it will churn.  It churns only if it is L1, its whole money pattern is ours and
right, no enemy is in its view (Tower.turn) and a robot is adjacent; a soldier can repaint empty or wrong-colour tiles
(Churn.repairPattern) but not enemy paint (RULES 4.1: such an attack does nothing and still costs 5 paint).  The
starting towers are L2 (RULES 7), so the starting money tower never churns.
A visit (as t182): a soldier or splasher ends a turn adjacent to an own standing tower it was not adjacent to the turn
before, with paint under 100 (soldier) / 150 (splasher).  Dry: it took nothing and the tower did not churn.
For each dry visit at a money tower: why it could not churn, first match of
  L2+                  the tower's level was 2 or 3 at the arrival
  chips < 2000         the side held fewer than 2000 chips (our bot then respects the dry flag)
  enemy paint          the 5x5 held enemy paint (a soldier cannot repair it)
  pattern wrong        the 5x5 held empty or wrong-colour tiles only (a soldier can repair them, a splasher cannot)
  enemy in view        an enemy robot within r2 20 of the tower
  none                 nothing blocked it (timing)
and the episode it starts: from the arrival to the robot's next withdrawal of 30+ paint (or its last turn), not counting
visits inside an episode already open: rounds, re-entries next to the same tower, rounds within Chebyshev 3 of it,
rounds at 0 paint, died inside it, tiles painted, and at the arrival the Chebyshev distance to the nearest own tower
holding 60+ paint.  Per side and arrival phase; losses, wins and ours by version."""
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
                        if g != want: wr += 1
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


def summarize(tag, V, EP, RR, ng):
    print(f'\n== {tag}: {ng} games')
    for typ in UT:
        print(f'  {typ}  (us / them)')
        print(f'     {"":50s}' + ''.join(f'{n:>18s}' for n in PHN))

        def row(name, fn, src):
            cells = ''
            for j in range(len(PH)):
                c = []
                for sd in ('us', 'them'):
                    E = [v for v in src if v['side'] == sd and v['typ'] == typ and (v['ph'] if 'ph' in v else ph(v['r0'])) == j]
                    c.append(fn(E, RR[(sd, j, typ)]))
                cells += f'{c[0] + " / " + c[1]:>18s}'
            print(f'     {name:50s}' + cells)
        DM = [v for v in V if v['dry'] and v['kind'] == 'MONEY_TOWER']
        row('dry money-tower visits per 100 robot-rounds', lambda E, rr: f'{100 * len(E) / rr:.1f}' if rr else '-', DM)
        for w in WHY:
            row(f'  blocked by {w} (%)', lambda E, rr, w=w: f'{100 * sum(v["why"] == w for v in E) / len(E):.0f}' if E else '-', DM)
        row('episodes per 100 robot-rounds', lambda E, rr: f'{100 * len(E) / rr:.1f}' if rr else '-', EP)
        row('episode rounds per 100 robot-rounds', lambda E, rr: f'{100 * sum(e["n"] for e in E) / rr:.1f}' if rr else '-', EP)
        row('  of these with chips 2000+ (not L2+), per 100 r-r', lambda E, rr: f'{100 * sum(e["n"] for e in E if e["why"] in ("enemy paint", "pattern wrong", "enemy in view", "none")) / rr:.1f}' if rr else '-', EP)
        row('  of these at L2+ towers, per 100 r-r', lambda E, rr: f'{100 * sum(e["n"] for e in E if e["why"] == "L2+") / rr:.1f}' if rr else '-', EP)
        row('episode length, rounds (median)', lambda E, rr: str(lib.med([e['n'] for e in E])), EP)
        row('  ends with a refill (%)', lambda E, rr: f'{100 * sum(e["refilled"] for e in E) / len(E):.0f}' if E else '-', EP)
        row('  ends with the robot dead (%)', lambda E, rr: f'{100 * sum(e["died"] for e in E) / len(E):.0f}' if E else '-', EP)
        row('  re-entries next to the same tower (mean)', lambda E, rr: f'{sum(e["reent"] for e in E) / len(E):.1f}' if E else '-', EP)
        row('  share of rounds within Chebyshev 3 of it (%)', lambda E, rr: f'{100 * sum(e["near"] for e in E) / max(1, sum(e["n"] + 1 for e in E)):.0f}' if E else '-', EP)
        row('  share of rounds at 0 paint (%)', lambda E, rr: f'{100 * sum(e["zero"] for e in E) / max(1, sum(e["n"] + 1 for e in E)):.0f}' if E else '-', EP)
        row('  tiles painted per 10 episode rounds', lambda E, rr: f'{10 * sum(e["pnt"] for e in E) / max(1, sum(e["n"] + 1 for e in E)):.1f}' if E else '-', EP)
        row('  nearest own tower with 60+ paint, Chebyshev (median)', lambda E, rr: str(lib.med([e['alt'] for e in E])), EP)
        row('  none exists (%)', lambda E, rr: f'{100 * sum(e["alt"] is None for e in E) / len(E):.0f}' if E else '-', EP)
        for w in ('L2+', 'enemy paint', 'pattern wrong'):
            row(f'  {w}: episode length (median)', lambda E, rr, w=w: str(lib.med([e['n'] for e in E if e['why'] == w])), EP)
            row(f'  {w}: re-entries (mean)', lambda E, rr, w=w: (f'{sum(e["reent"] for e in E if e["why"] == w) / max(1, sum(e["why"] == w for e in E)):.1f}' if any(e['why'] == w for e in E) else '-'), EP)


AGG = {}
for G in lib.games('all'):
    V, EP, rr = analyse(G)
    for k in ('lost' if G.won_op else 'won', 'ver ' + G.ver, 'ver ' + G.ver + (' lost' if G.won_op else ' won')):
        A = AGG.setdefault(k, [[], [], defaultdict(int), 0])
        A[0].extend(V); A[1].extend(EP)
        for kk, x in rr.items(): A[2][kk] += x
        A[3] += 1
    G.turns = G.acts = None
for k in ('lost', 'won'):
    if k in AGG: summarize(k, *AGG[k])
for k in sorted(AGG):
    if k.startswith('ver'): summarize(k, *AGG[k])

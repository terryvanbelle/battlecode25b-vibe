"""Topic 182 (new): refill visits.  A visit = a run of consecutive turns a soldier or splasher ends adjacent
(Chebyshev 1) to the same standing own tower, entered from farther away with paint under LOW (soldier 100,
splasher 150): a robot that came for paint.  Per visit:
  outcome   filled (took 50+ in all, or left the visit at 150+ / 225+), partial (took 1-49), churn (the tower was
            disintegrated during the visit or the 2 rounds after and a tower was completed on that ruin within 5
            rounds), dry (took nothing, no churn)
  the tower: kind, its paint at the robot's arrival (its last turn record), the side's chips then (2000+ = our churn
            gate, Tune.CHURN_CHIPS), and whether its 5x5 held the full money pattern in the side's colours then
  approach  rounds of the run before arriving over which the distance to the tower never grew (as t179)
  wait      rounds adjacent
  after     what the robot did in the 10 rounds after leaving: painted (any tile paint or splash), withdrew elsewhere,
            or hit 0 paint
Per side and phase, losses and wins (and ours by version): visits per 100 robot-rounds, outcome shares overall and per
tower class (paint tower; money tower with chips 2000+ and the pattern intact; money 2000+ broken; money under 2000),
median approach and wait, and the rounds lost to dry visits (approach + wait) per 100 robot-rounds."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 300), (301, 2000))
PHN = ('r1-100', 'r101-200', 'r201-300', 'r301+')
UT = ('SOLDIER', 'SPLASHER')
LOW = {'SOLDIER': 100, 'SPLASHER': 150}
FULL = {'SOLDIER': 150, 'SPLASHER': 225}
MP = lib.PAT['MONEY_TOWER']


def ph(r):
    for j, (lo, hi) in enumerate(PH):
        if lo <= r <= hi: return j
    return None


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def analyse(G):
    side = lambda team: 'us' if team == G.us else 'them'
    tpos, tkind, tpaint, tteam = {}, {}, defaultdict(dict), {}
    traj = defaultdict(list)
    rr = defaultdict(int)
    for t in G.turns:
        if t[3] in lib.TOW:
            tpos[t[1]] = (t[4], t[5]); tkind[t[1]] = t[3]; tpaint[t[1]][t[0]] = t[7]; tteam[t[1]] = t[2]
        elif t[3] in UT:
            traj[t[1]].append((t[0], t[4], t[5], t[7]))
            rr[(side(t[2]), ph(t[0]), t[3])] += 1
    alive = defaultdict(set)   # tower id -> rounds with a turn
    for tid, d in tpaint.items(): alive[tid] = set(d)
    wd = defaultdict(lambda: defaultdict(int))   # robot -> round -> taken (any tower)
    wdt = defaultdict(lambda: defaultdict(int))  # (robot, tower) -> round -> taken
    acts_r = defaultdict(set)                    # robot -> rounds with a paint/splash
    removed = {}                                 # tower id -> round disintegrated
    builds = defaultdict(list)                   # ruin pos -> build rounds
    for a in G.acts:
        if a[4] == 'transfer' and a[3] in UT:
            amt = int(a[6]) if a[6] else 0
            if amt < 0:
                wd[a[1]][a[0]] += -amt; wdt[(a[1], int(a[5]))][a[0]] += -amt
        elif a[4] in ('paint', 'splash') and a[3] in UT: acts_r[a[1]].add(a[0])
        elif a[4] == 'died' and a[7] in lib.TOW: removed[int(a[5])] = a[0]
        elif a[4] == 'build':
            tid = int(a[5])
            if tid in tpos: builds[tpos[tid]].append(a[0])
    # money pattern intact per tower per round: needs the grid; track at visit arrivals only (collect queries first)
    visits = []
    for i, tr in traj.items():
        typ = G.typ.get(i); team = G.team.get(i); sd = side(team)
        own = [tid for tid in tpos if tteam.get(tid) == team]
        k = 1
        while k < len(tr):
            r, x, y, p = tr[k]
            hit = None
            for tid in own:
                if (r in alive[tid] or r - 1 in alive[tid]) and cheb((x, y), tpos[tid]) == 1 and cheb(tr[k - 1][1:3], tpos[tid]) > 1:
                    hit = tid; break
            if hit is None or tr[k - 1][3] >= LOW[typ]:
                k += 1; continue
            tid = hit; tp = tpos[tid]
            e = k
            while e + 1 < len(tr) and cheb(tr[e + 1][1:3], tp) <= 1 and tr[e + 1][0] == tr[e][0] + 1: e += 1
            r0, r1 = tr[k][0], tr[e][0]
            taken = sum(v for q, v in wdt[(i, tid)].items() if r0 <= q <= r1)
            # a churn of this tower during the visit (+2 rounds) with a rebuild within 5 rounds
            ch = tid in removed and r0 <= removed[tid] <= r1 + 2 and any(removed[tid] <= b <= removed[tid] + 5 for b in builds[tp])
            if ch: out = 'churn'
            elif taken >= 50 or tr[e][3] >= FULL[typ]: out = 'filled'
            elif taken > 0: out = 'partial'
            else: out = 'dry'
            # approach run
            j = k - 1
            while j > 0 and cheb(tr[j - 1][1:3], tp) >= cheb(tr[j][1:3], tp) and r0 - tr[j - 1][0] <= 80: j -= 1
            d0 = cheb(tr[j][1:3], tp)
            while j < k - 1 and cheb(tr[j + 1][1:3], tp) == d0: j += 1
            appr = r0 - tr[j][0]
            tpa = None
            for q in range(r0 - 1, r0 - 4, -1):
                if q in tpaint[tid]: tpa = tpaint[tid][q]; break
            sk = 'A' if team == 1 else 'B'
            chips = lib.money(G, team, r0 - 1)
            # after: 10 rounds after leaving
            after_paint = any(r1 < q <= r1 + 10 for q in acts_r[i])
            after_wd = any(r1 < q <= r1 + 10 for q in wd[i])
            after_zero = any(r1 < tt[0] <= r1 + 10 and tt[3] == 0 for tt in tr[e + 1:e + 12])
            visits.append(dict(side=sd, typ=typ, ph=ph(r0), r0=r0, out=out, kind=tkind[tid], tpa=tpa, chips=chips, appr=appr,
                               wait=r1 - r0 + 1, tid=tid, tp=tp, team=team, ap=after_paint, aw=after_wd, az=after_zero,
                               p_arr=tr[k - 1][3], taken=taken))
            k = e + 1
    # money pattern intact at arrival: replay the grid, checking at each visit's arrival round
    need = defaultdict(list)
    for v in visits:
        if v['kind'] == 'MONEY_TOWER': need[v['r0']].append(v)
    if need:
        rounds_sorted = sorted(need)
        st = {'ix': 0}
        def check(grid, upto):
            while st['ix'] < len(rounds_sorted) and rounds_sorted[st['ix']] <= upto:
                for v in need[rounds_sorted[st['ix']]]:
                    tx, ty = v['tp']; ok = True
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            if dx == 0 and dy == 0: continue
                            xx, yy = tx + dx, ty + dy
                            if not (0 <= xx < G.W and 0 <= yy < G.H): ok = False; break
                            g = grid[xx + yy * G.W]
                            want = 2 if lib.secondary('MONEY_TOWER', dx, dy) else 1
                            if v['team'] == 2: want += 2
                            if g != want: ok = False; break
                        if not ok: break
                    v['intact'] = ok
                st['ix'] += 1
        last = {'r': 0}
        def hook(a, grid):
            if a[0] != last['r']:
                check(grid, a[0] - 1)
                last['r'] = a[0]
        g = lib.replay_grid(G, hook)
        check(g, 10 ** 9)
    for v in visits:
        if v['kind'] == 'PAINT_TOWER': v['cls'] = 'paint tower'
        elif v['kind'] == 'MONEY_TOWER':
            v['cls'] = ('money, chips 2000+, ' + ('intact' if v.get('intact') else 'broken')) if v['chips'] >= 2000 else 'money, chips < 2000'
        else: v['cls'] = 'defense'
    return visits, rr


CLS = ('paint tower', 'money, chips 2000+, intact', 'money, chips 2000+, broken', 'money, chips < 2000', 'defense')


def summarize(tag, V, RR, ng):
    print(f'\n== {tag}: {ng} games')
    for typ in UT:
        print(f'  {typ}  (us / them; visits = refill arrivals under {LOW[typ]} paint)')
        print(f'     {"":46s}' + ''.join(f'{n:>18s}' for n in PHN))
        def row(name, fn):
            cells = ''
            for j in range(len(PH)):
                c = []
                for sd in ('us', 'them'):
                    E = [v for v in V if v['side'] == sd and v['typ'] == typ and v['ph'] == j]
                    c.append(fn(E, RR[(sd, j, typ)]))
                cells += f'{c[0] + " / " + c[1]:>18s}'
            print(f'     {name:46s}' + cells)
        row('visits per 100 robot-rounds', lambda E, rr: f'{100 * len(E) / rr:.1f}' if rr else '-')
        for o in ('filled', 'partial', 'churn', 'dry'):
            row(f'  {o} (% of visits)', lambda E, rr, o=o: f'{100 * sum(v["out"] == o for v in E) / len(E):.0f}' if E else '-')
        for c in CLS:
            row(f'  at {c} (% of visits)', lambda E, rr, c=c: f'{100 * sum(v["cls"] == c for v in E) / len(E):.0f}' if E else '-')
            row(f'    of these dry (%)', lambda E, rr, c=c: (f'{100 * sum(v["out"] == "dry" for v in E if v["cls"] == c) / max(1, sum(v["cls"] == c for v in E)):.0f}' if any(v['cls'] == c for v in E) else '-'))
        row('paint on arrival (median)', lambda E, rr: str(lib.med([v['p_arr'] for v in E])))
        row('tower paint on arrival (median)', lambda E, rr: str(lib.med([v['tpa'] for v in E])))
        row('approach rounds (median)', lambda E, rr: str(lib.med([v['appr'] for v in E])))
        row('wait rounds adjacent (median)', lambda E, rr: str(lib.med([v['wait'] for v in E])))
        row('  dry visits: wait (median)', lambda E, rr: str(lib.med([v['wait'] for v in E if v['out'] == 'dry'])))
        row('rounds in dry visits per 100 robot-rounds', lambda E, rr: f'{100 * sum(v["appr"] + v["wait"] for v in E if v["out"] == "dry") / rr:.1f}' if rr else '-')
        row('after a dry visit: painted in 10 rounds (%)', lambda E, rr: (f'{100 * sum(v["ap"] for v in E if v["out"] == "dry") / max(1, sum(v["out"] == "dry" for v in E)):.0f}' if any(v['out'] == 'dry' for v in E) else '-'))
        row('after a dry visit: withdrew elsewhere (%)', lambda E, rr: (f'{100 * sum(v["aw"] for v in E if v["out"] == "dry") / max(1, sum(v["out"] == "dry" for v in E)):.0f}' if any(v['out'] == 'dry' for v in E) else '-'))
        row('after a dry visit: hit 0 paint (%)', lambda E, rr: (f'{100 * sum(v["az"] for v in E if v["out"] == "dry") / max(1, sum(v["out"] == "dry" for v in E)):.0f}' if any(v['out'] == 'dry' for v in E) else '-'))


AGG = {}
for G in lib.games('all'):
    V, rr = analyse(G)
    for k in ('lost' if G.won_op else 'won', 'ver ' + G.ver, 'ver ' + G.ver + (' lost' if G.won_op else ' won')):
        A = AGG.setdefault(k, [[], defaultdict(int), 0])
        A[0].extend(V)
        for kk, v in rr.items(): A[1][kk] += v
        A[2] += 1
    G.turns = G.acts = None
for k in ('lost', 'won'):
    if k in AGG: summarize(k, *AGG[k])
for k in sorted(AGG):
    if k.startswith('ver'): summarize(k, *AGG[k])

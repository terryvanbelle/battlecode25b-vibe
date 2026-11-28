"""Topic 179 (new): refill trips.  Every withdrawal of a soldier or splasher from an own tower (transfer with a negative
amount), both sides:
  before     the robot's paint at its previous turn (what it had left when it got there)
  amount     what it took; the tower's kind, and the tower's paint at its previous turn
  approach   the run of turns before the withdrawal over which the robot's Chebyshev distance to that tower never grew,
             starting where it first shrank (leading turns at the same distance are trimmed): its length in rounds,
             the distance at its start, the robot's paint at its start, and the tiles it painted on the way
  return     rounds from the withdrawal to the robot's next tile paint (any tile; a splash counts)
Dry arrivals: a robot under 100 paint (soldier; 150 splasher) that ends a turn adjacent (Chebyshev 1) to an own tower
it was not adjacent to the turn before, and withdraws nothing from any tower that turn or the next two.
Rates per 100 robot-rounds of that type.  Losses and wins, us / them; ours by version.  Phases as t178."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 300), (301, 2000))
PHN = ('r1-100', 'r101-200', 'r201-300', 'r301+')
UT = ('SOLDIER', 'SPLASHER')
LOW = {'SOLDIER': 100, 'SPLASHER': 150}


def ph(r):
    for j, (lo, hi) in enumerate(PH):
        if lo <= r <= hi: return j
    return None


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def analyse(G):
    side = lambda team: 'us' if team == G.us else 'them'
    tpos, tkind, tpaint = {}, {}, defaultdict(dict)
    traj = defaultdict(list)       # robot id -> [(round, x, y, paint)]
    rr = defaultdict(int)          # (side, phase, type) -> robot-rounds
    for t in G.turns:
        if t[3] in lib.TOW:
            tpos[t[1]] = (t[4], t[5]); tkind[t[1]] = t[3]; tpaint[t[1]][t[0]] = t[7]
        elif t[3] in UT:
            traj[t[1]].append((t[0], t[4], t[5], t[7]))
            rr[(side(t[2]), ph(t[0]), t[3])] += 1
    wd = defaultdict(list)         # robot id -> [(round, tower id, amount)]
    paints = defaultdict(list)     # robot id -> rounds with a tile paint / splash
    for a in G.acts:
        if a[3] not in UT: continue
        if a[4] == 'transfer':
            amt = int(a[6]) if a[6] else 0
            if amt < 0: wd[a[1]].append((a[0], int(a[5]), -amt))
        elif a[4] == 'paint' and a[3] == 'SOLDIER': paints[a[1]].append(a[0])
        elif a[4] == 'splash': paints[a[1]].append(a[0])
    ev = []    # one row per withdrawal
    dry = defaultdict(int)
    for i, tr in traj.items():
        typ = G.typ.get(i); team = G.team.get(i); sd = side(team)
        idx = {r: k for k, (r, *_x) in enumerate(tr)}
        ps = paints.get(i, [])
        for (r, tid, amt) in wd.get(i, ()):
            if tid not in tpos or r not in idx: continue
            k = idx[r]
            before = tr[k - 1][3] if k > 0 else lib.CAP[typ]
            tp = tpos[tid]
            # approach run
            j = k
            while j > 0 and cheb(tr[j - 1][1:3], tp) >= cheb(tr[j][1:3], tp) and tr[k][0] - tr[j - 1][0] <= 80: j -= 1
            d0 = cheb(tr[j][1:3], tp)
            while j < k and cheb(tr[j + 1][1:3], tp) == d0: j += 1
            run = tr[k][0] - tr[j][0]
            dist = cheb(tr[j][1:3], tp)
            p_start = tr[j][3]
            on_way = sum(1 for q in ps if tr[j][0] < q < r)
            nxt = [q for q in ps if q > r]
            ret = (nxt[0] - r) if nxt else None
            tpb = None
            for q in range(r - 1, r - 4, -1):
                if q in tpaint[tid]: tpb = tpaint[tid][q]; break
            ev.append(dict(side=sd, typ=typ, ph=ph(r), before=before, amt=amt, kind=tkind[tid], tp=tpb, run=run,
                           dist=dist, pstart=p_start, onway=on_way, ret=ret))
        # dry arrivals
        wr = set(r for r, *_x in wd.get(i, ()))
        own = [tid for tid in tpos if G.team.get(tid) == team]
        for k in range(1, len(tr)):
            r, x, y, p = tr[k]
            if p >= LOW[typ]: continue
            for tid in own:
                tp = tpos[tid]
                if cheb((x, y), tp) == 1 and cheb(tr[k - 1][1:3], tp) > 1:
                    # was the tower standing then?  (it had a turn record within 1 round)
                    if r not in tpaint[tid] and r - 1 not in tpaint[tid]: continue
                    if not any(q in wr for q in (r, r + 1, r + 2)):
                        dry[(sd, ph(r), typ)] += 1
                    break
    return ev, rr, dry


def summarize(tag, EV, RR, DRY, ng):
    print(f'\n== {tag}: {ng} games')
    for typ in UT:
        print(f'  {typ}   (us / them)')
        print(f'     {"":44s}' + ''.join(f'{n:>18s}' for n in PHN))
        rows = (('withdrawals per 100 robot-rounds', lambda E, rr, d: f'{100 * len(E) / rr:.1f}' if rr else '-'),
                ('paint withdrawn per 100 robot-rounds', lambda E, rr, d: f'{100 * sum(e["amt"] for e in E) / rr:.0f}' if rr else '-'),
                ('paint left at the withdrawal (median)', lambda E, rr, d: str(lib.med([e['before'] for e in E]))),
                ('  under 50 / 100 (% of withdrawals)', lambda E, rr, d: f'{100 * sum(e["before"] < 50 for e in E) / len(E):.0f}/{100 * sum(e["before"] < 100 for e in E) / len(E):.0f}' if E else '-'),
                ('amount taken (median)', lambda E, rr, d: str(lib.med([e['amt'] for e in E]))),
                ('  from a paint tower (% of paint taken)', lambda E, rr, d: f'{100 * sum(e["amt"] for e in E if e["kind"] == "PAINT_TOWER") / max(1, sum(e["amt"] for e in E)):.0f}'),
                ('  the tower held (median, before)', lambda E, rr, d: str(lib.med([e['tp'] for e in E]))),
                ('approach rounds (median)', lambda E, rr, d: str(lib.med([e['run'] for e in E]))),
                ('approach distance, Chebyshev (median)', lambda E, rr, d: str(lib.med([e['dist'] for e in E]))),
                ('paint at the approach start (median)', lambda E, rr, d: str(lib.med([e['pstart'] for e in E]))),
                ('tiles painted on the approach (mean)', lambda E, rr, d: f'{sum(e["onway"] for e in E) / len(E):.1f}' if E else '-'),
                ('rounds to the next paint after (median)', lambda E, rr, d: str(lib.med([e['ret'] for e in E]))),
                ('approach rounds per 100 robot-rounds', lambda E, rr, d: f'{100 * sum(e["run"] for e in E) / rr:.1f}' if rr else '-'),
                ('dry arrivals per 100 robot-rounds', lambda E, rr, d: f'{100 * d / rr:.1f}' if rr else '-'),
                ('dry arrivals per withdrawal', lambda E, rr, d: f'{d / len(E):.2f}' if E else '-'))
        for name, fn in rows:
            cells = ''
            for j in range(len(PH)):
                v = []
                for sd in ('us', 'them'):
                    E = [e for e in EV if e['side'] == sd and e['typ'] == typ and e['ph'] == j]
                    v.append(fn(E, RR[(sd, j, typ)], DRY[(sd, j, typ)]))
                cells += f'{v[0] + " / " + v[1]:>18s}'
            print(f'     {name:44s}' + cells)


AGG = {}
for G in lib.games('all'):
    ev, rr, dry = analyse(G)
    keys = ['lost' if G.won_op else 'won', G.ver, G.ver + (':lost' if G.won_op else ':won')]
    for k in keys:
        A = AGG.setdefault(k, [[], defaultdict(int), defaultdict(int), 0])
        A[0].extend(ev)
        for kk, v in rr.items(): A[1][kk] += v
        for kk, v in dry.items(): A[2][kk] += v
        A[3] += 1
    G.turns = G.acts = None
for k in ('lost', 'won'):
    if k in AGG: summarize(k, *AGG[k])
for k in sorted(AGG):
    if k in ('lost', 'won'): continue
    summarize('our version ' + k, *AGG[k])

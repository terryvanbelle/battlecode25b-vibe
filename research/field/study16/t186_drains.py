"""Topic 186 (new; follows t178: in our losses enemy moppers drain our soldiers 59 / 67 paint per 100 soldier-rounds in
r101-200 / r201-300, ours drain theirs 20 / 23).  Every drain row (a mopper's mop attack, 10, or swing, 5) on a
soldier or splasher, both sides.  Where the drained robot was at the end of the previous round (its last turn row
before the drain), first match of:
  ruin       within Chebyshev 2 of a ruin with no tower (working a pattern)
  own tower  within Chebyshev 2 of one of its own standing towers (refill, waiting)
  siege      within r2 9 of a standing enemy tower
  other      anywhere else (exploring, travelling, SRP work)
and its paint then.  Per side and phase: drains and paint drained per 100 robot-rounds of the victim type; the share by
place; attack (10) vs swing (5); distinct victims; drains per victim (repeat drains of the same robot within 10
rounds); and the victim's paint (median).  Also the moppers: robot-rounds per game and drains per 100 mopper-rounds,
per side.  Losses and wins."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 300), (301, 2000))
PHN = ('r1-100', 'r101-200', 'r201-300', 'r301+')
VT = ('SOLDIER', 'SPLASHER')
PL = ('ruin', 'own tower', 'siege', 'other')


def ph(r):
    for j, (lo, hi) in enumerate(PH):
        if lo <= r <= hi: return j
    return None


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def analyse(G):
    side = lambda team: 'us' if team == G.us else 'them'
    rr = defaultdict(int)
    last = {}            # robot id -> (round, x, y, paint) of its latest turn row (updated in round order below)
    towers = defaultdict(dict)   # round -> pos -> team
    for t in G.turns:
        if t[3] in lib.TOW: towers[t[0]][(t[4], t[5])] = t[2]
        else: rr[(side(t[2]), ph(t[0]), t[3])] += 1
    ruins = list(G.ruins)
    # position of each robot at the end of each of its turns
    pos = defaultdict(dict)
    for t in G.turns:
        if t[3] in VT: pos[t[1]][t[0]] = (t[4], t[5], t[7])
    ev = []
    for a in G.acts:
        if a[4] != 'drain': continue
        tgt = int(a[5]); amt = int(a[6]) if a[6] else 0
        typ = G.typ.get(tgt)
        if typ not in VT: continue
        r = a[0]
        p = pos[tgt].get(r - 1) or pos[tgt].get(r)
        if p is None: continue
        x, y, paint = p
        tw = towers.get(r - 1) or towers.get(r, {})
        team = G.team.get(tgt)
        place = 'other'
        if any(ru not in tw and cheb((x, y), ru) <= 2 for ru in ruins): place = 'ruin'
        elif any(tm == team and cheb((x, y), q) <= 2 for q, tm in tw.items()): place = 'own tower'
        elif any(tm != team and (x - q[0]) ** 2 + (y - q[1]) ** 2 <= 9 for q, tm in tw.items()): place = 'siege'
        ev.append(dict(side=side(team), typ=typ, ph=ph(r), r=r, tgt=tgt, amt=amt, place=place, paint=paint, mop=a[1]))
    return ev, rr


def report(tag, EV, RR, n):
    print(f'\n== {tag}: {n} games; drains on soldiers and splashers, by the side drained (us / them)')
    print(f'     {"":48s}' + ''.join(f'{x:>16s}' for x in PHN))
    for typ in VT:
        print(f'  {typ}')

        def row(name, fn):
            cells = ''
            for j in range(len(PH)):
                c = []
                for sd in ('us', 'them'):
                    E = [e for e in EV if e['side'] == sd and e['typ'] == typ and e['ph'] == j]
                    c.append(fn(E, RR[(sd, j, typ)]))
                cells += f'{c[0] + " / " + c[1]:>16s}'
            print(f'     {name:48s}' + cells)
        row('drains per 100 robot-rounds', lambda E, rr: f'{100 * len(E) / rr:.1f}' if rr else '-')
        row('paint drained per 100 robot-rounds', lambda E, rr: f'{100 * sum(e["amt"] for e in E) / rr:.0f}' if rr else '-')
        row('  mop attacks (10) (% of drains)', lambda E, rr: f'{100 * sum(e["amt"] >= 10 for e in E) / len(E):.0f}' if E else '-')
        for pl in PL:
            row(f'  at {pl} (% of paint drained)', lambda E, rr, pl=pl: f'{100 * sum(e["amt"] for e in E if e["place"] == pl) / max(1, sum(e["amt"] for e in E)):.0f}' if E else '-')
        row('  victim paint before (median)', lambda E, rr: str(lib.med([e['paint'] for e in E])))
        row('  distinct victims per game', lambda E, rr: f'{len(set(e["tgt"] for e in E)) / n:.1f}')
        row('  drains per victim (mean)', lambda E, rr: f'{len(E) / max(1, len(set(e["tgt"] for e in E))):.1f}' if E else '-')

        def rep(E, rr):
            if not E: return '-'
            byt = defaultdict(list)
            for e in E: byt[e['tgt']].append(e['r'])
            k = 0
            for rs in byt.values():
                rs.sort(); k += sum(1 for a, b in zip(rs, rs[1:]) if b - a <= 10)
            return f'{100 * k / len(E):.0f}'
        row('  repeat drains within 10 rounds (%)', rep)
    print('  MOPPER robot-rounds per game (us / them): ' + '   '.join(f'{PHN[j]} {RR[("us", j, "MOPPER")] / n:.0f} / {RR[("them", j, "MOPPER")] / n:.0f}' for j in range(len(PH))))


AGG = {}
for G in lib.games('all'):
    ev, rr = analyse(G)
    for k in ('lost' if G.won_op else 'won',):
        A = AGG.setdefault(k, [[], defaultdict(int), 0])
        A[0].extend(ev)
        for kk, v in rr.items(): A[1][kk] += v
        A[2] += 1
    G.turns = G.acts = None
for k in ('lost', 'won'):
    if k in AGG: report(k, *AGG[k])

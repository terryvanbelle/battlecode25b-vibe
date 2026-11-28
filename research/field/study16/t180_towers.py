"""Topic 180 (new): tower builds, paint towers and ruins, per side.
Every 'build' row (a completed tower) is classed by what stood on that ruin before:
  churn    an own tower there was removed (disintegrated, a 'died' row) within the 5 rounds before
  rebuild  an own tower there was destroyed earlier (or removed longer ago)
  taken    an enemy tower stood there before
  new      no tower ever stood there
Per side and phase: builds by class and type; the order of the first 8 non-churn builds (M money, P paint, D defense);
the round the side first holds 2, 3 and 4 paint towers (rounds.tsv); paint-tower upgrades (to L2 / L3) and paint
towers lost; and the map's ruins at r100 / r150 / r200 / r300: held by us, by them, free (no tower).  Losses and
wins; ours by version."""
from collections import defaultdict, Counter
import lib

PH = ((1, 100), (101, 200), (201, 300), (301, 2000))
PHN = ('r1-100', 'r101-200', 'r201-300', 'r301+')
SH = {'PAINT_TOWER': 'P', 'MONEY_TOWER': 'M', 'DEFENSE_TOWER': 'D'}


def ph(r):
    for j, (lo, hi) in enumerate(PH):
        if lo <= r <= hi: return j
    return None


def analyse(G):
    side = lambda team: 'us' if team == G.us else 'them'
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    hist = defaultdict(list)   # ruin pos -> [(round, event, team, type)]  events: start, build, die, died
    for t in G.turns:
        if t[0] == 1 and t[3] in lib.TOW: hist[pos[t[1]]].append((0, 'start', t[2], t[3]))
    starts = set(p for p, h in hist.items())
    hist = defaultdict(list, {p: [(0, 'start', h[0][2], h[0][3])] for p, h in hist.items()})
    up = []
    for a in G.acts:
        k = a[4]
        if k == 'build':
            tid = int(a[5]); p = pos.get(tid)
            if p: hist[p].append((a[0], 'build', a[2], a[6]))
        elif k in ('die', 'died') and a[7] in lib.TOW:
            tid = int(a[5]); p = pos.get(tid)
            if p: hist[p].append((a[0], k, G.team.get(tid), a[7]))
        elif k == 'upgrade':
            tid = int(a[5])
            up.append((a[0], G.team.get(tid), G.typ.get(tid), int(a[6])))
    builds = []   # (round, side, type, class)
    for p, h in hist.items():
        h.sort(key=lambda e: (e[0], 0 if e[1] in ('die', 'died') else 1))
        for n, e in enumerate(h):
            if e[1] != 'build': continue
            prev = h[:n]
            cls = 'new'
            if prev:
                last_end = [x for x in prev if x[1] in ('die', 'died')]
                owners = [x[2] for x in prev if x[1] in ('start', 'build')]
                if last_end and last_end[-1][1] == 'died' and last_end[-1][2] == e[2] and e[0] - last_end[-1][0] <= 5: cls = 'churn'
                elif owners and owners[-1] != e[2]: cls = 'taken'
                elif owners: cls = 'rebuild'
            builds.append((e[0], side(e[2]), e[3], cls))
    builds.sort()
    out = {'builds': builds, 'up': [(r, side(tm), ty, lv) for r, tm, ty, lv in up]}
    # first round with 2, 3, 4 paint towers
    for sd, s in (('us', G.us), ('them', G.op)):
        sk = 'A' if s == 1 else 'B'
        for n in (2, 3, 4):
            out[(sd, 'pt', n)] = next((int(R['round']) for R in G.rounds if int(R['pt' + sk]) >= n), None)
    # ruins held / free at checkpoints
    alive = {}
    for t in G.turns:
        if t[3] in lib.TOW: alive.setdefault(t[0], {})[pos[t[1]]] = t[2]
    for r in (100, 150, 200, 300):
        if G.end < r: continue
        a = alive.get(r, {})
        n_us = sum(1 for v in a.values() if v == G.us); n_th = sum(1 for v in a.values() if v == G.op)
        out[('ruins', r)] = (n_us, n_th, len(G.ruins) - n_us - n_th)
    # paint towers lost per phase
    for p, h in hist.items():
        for e in h:
            if e[1] == 'die' and e[3] == 'PAINT_TOWER':
                out.setdefault(('ptlost', side(e[2]), ph(e[0])), 0)
                out[('ptlost', side(e[2]), ph(e[0]))] += 1
    out['end'] = G.end
    return out


def summarize(tag, OS):
    n = len(OS)
    if not n: return
    print(f'\n== {tag}: {n} games (means per game; a phase counts games that reached its start)')
    print(f'   {"":40s}' + ''.join(f'{x:>16s}' for x in PHN))
    for cls in ('new', 'taken', 'rebuild', 'churn'):
        for ty in ('PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER'):
            cells = ''
            for j, (lo, hi) in enumerate(PH):
                gs = [o for o in OS if o['end'] >= lo]
                v = [sum(1 for b in o['builds'] if b[1] == sd and b[2] == ty and b[3] == cls and lo <= b[0] <= hi) for sd in ('us', 'them') for o in gs]
                k = len(gs)
                cells += f'{sum(v[:k]) / max(1, k):.2f}/{sum(v[k:]) / max(1, k):.2f}'.rjust(16)
            print(f'   {cls + " " + ty.split("_")[0].lower() + " towers built":40s}' + cells)
    for ty in ('PAINT_TOWER', 'MONEY_TOWER'):
        for lv in (2, 3):
            cells = ''
            for j, (lo, hi) in enumerate(PH):
                gs = [o for o in OS if o['end'] >= lo]
                u = sum(1 for o in gs for x in o['up'] if x[1] == 'us' and x[2] == ty and x[3] == lv and lo <= x[0] <= hi)
                t = sum(1 for o in gs for x in o['up'] if x[1] == 'them' and x[2] == ty and x[3] == lv and lo <= x[0] <= hi)
                cells += f'{u / max(1, len(gs)):.2f}/{t / max(1, len(gs)):.2f}'.rjust(16)
            print(f'   {ty.split("_")[0].lower() + " tower upgrades to L" + str(lv):40s}' + cells)
    cells = ''
    for j, (lo, hi) in enumerate(PH):
        gs = [o for o in OS if o['end'] >= lo]
        u = sum(o.get(('ptlost', 'us', j), 0) for o in gs); t = sum(o.get(('ptlost', 'them', j), 0) for o in gs)
        cells += f'{u / max(1, len(gs)):.2f}/{t / max(1, len(gs)):.2f}'.rjust(16)
    print(f'   {"paint towers destroyed":40s}' + cells)
    for k in (2, 3, 4):
        u = [o[('us', 'pt', k)] for o in OS]; t = [o[('them', 'pt', k)] for o in OS]
        print(f'   first round with {k} paint towers: us median r{lib.med(u)} (in {sum(x is not None for x in u)} games; by r200 in {sum(1 for x in u if x and x <= 200)}, by r300 in {sum(1 for x in u if x and x <= 300)}) | '
              f'them r{lib.med(t)} ({sum(x is not None for x in t)}; by r200 {sum(1 for x in t if x and x <= 200)}, by r300 {sum(1 for x in t if x and x <= 300)})')
    for r in (100, 150, 200, 300):
        v = [o[('ruins', r)] for o in OS if ('ruins', r) in o]
        if not v: continue
        print(f'   ruins at r{r} ({len(v)} games): held by us {lib.med([x[0] for x in v])} / them {lib.med([x[1] for x in v])} / free {lib.med([x[2] for x in v])} (medians); '
              f'games with 0 free: {sum(1 for x in v if x[2] == 0)}, with 2+ free: {sum(1 for x in v if x[2] >= 2)}; mean free {sum(x[2] for x in v) / len(v):.1f}')
    # build order of the first 8 non-churn builds after the start
    for sd in ('us', 'them'):
        seqs = [''.join(SH[b[2]] for b in o['builds'] if b[1] == sd and b[3] != 'churn')[:8] for o in OS]
        pos2 = []
        for s in seqs:
            ps = [i + 1 for i, c in enumerate(s) if c == 'P']
            pos2.append(ps[0] if ps else None)
        print(f'   {sd}: first built paint tower is build no. median {lib.med(pos2)} (none among the first 8 in {sum(x is None for x in pos2)} games); orders: ' + ' '.join(seqs))


OS = defaultdict(list)
for G in lib.games('all'):
    o = analyse(G)
    OS['lost' if G.won_op else 'won'].append(o)
    OS['ver ' + G.ver + (' lost' if G.won_op else ' won')].append(o)
    G.turns = G.acts = None
for k in ('lost', 'won'): summarize(k, OS[k])
for k in sorted(OS):
    if k.startswith('ver'): summarize(k, OS[k])

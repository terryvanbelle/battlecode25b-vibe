"""Topic 5: paint logistics. Withdrawals (paint before, amount, % capacity, distance and paint at the turn-around
point), tower paint levels, robot->robot transfers (moppers), deposits."""
import lib
from collections import Counter, defaultdict
P = defaultdict(lambda: defaultdict(list)); TT = defaultdict(Counter)
for G in lib.games():
    tn = G.team_name
    hist = defaultdict(dict)  # id -> round -> (x,y,paint)
    for t in G.turns: hist[t[1]][t[0]] = (t[4], t[5], t[7])
    tpos = {}
    for t in G.turns:
        if t[3] in lib.TOW: tpos[t[1]] = (t[4], t[5])
    def prev(i, r):
        h = hist[i]
        for rr in range(r - 1, r - 4, -1):
            if rr in h: return h[rr]
        return None
    nwd = Counter()
    for a in G.acts:
        if a[4] != 'transfer' or a[2] != G.op: continue
        tgt = int(a[5]); amt = int(a[6]); tt = G.typ.get(tgt, '?'); src = a[3]
        TT[tn][(src[:3], tt[:3], 'take' if amt < 0 else 'give')] += 1
        if amt < 0 and tt in lib.TOW and src in lib.BOT:
            p = prev(a[1], a[0])
            if not p: continue
            nwd[src] += 1
            P[tn][f'{src[:3]} paint before withdraw'].append(p[2])
            P[tn][f'{src[:3]} paint before withdraw (% cap)'].append(round(100 * p[2] / lib.CAP[src]))
            P[tn][f'{src[:3]} amount taken'].append(-amt)
            P[tn][f'{src[:3]} after (% cap)'].append(round(100 * (p[2] - amt) / lib.CAP[src]))
            big = -amt >= 0.25 * lib.CAP[src]
            P[tn][f'{src[:3]} share of withdrawals that are top-ups (<10% cap)'].append(1 if -amt < 0.1 * lib.CAP[src] else 0)
            if big:
                P[tn][f'BIG(>=25%cap) {src[:3]} paint before (% cap)'].append(round(100 * p[2] / lib.CAP[src]))
                P[tn][f'BIG(>=25%cap) {src[:3]} amount'].append(-amt)
            tp = prev(tgt, a[0] + 1)
            if tp: P[tn][f'tower paint before withdraw ({tt[:2]})'].append(tp[2] + 0)
            # turn-around: walk back while distance to the tower is non-decreasing (going back), max 40
            T = tpos.get(tgt)
            if not T: continue
            r = a[0]; h = hist[a[1]]
            best = r; dcur = lib.d2(h[r][:2], T) if r in h else 0
            rr = r - 1
            while rr >= r - 40 and rr in h:
                dd = lib.d2(h[rr][:2], T)
                if dd + 0 < dcur: break
                dcur = dd; best = rr; rr -= 1
            P[tn][f'{src[:3]} dist at turn-around'].append(round(dcur ** .5, 1))
            if big:
                P[tn][f'BIG {src[:3]} dist at turn-around'].append(round(dcur ** .5, 1))
                P[tn][f'BIG {src[:3]} paint at turn-around (% cap)'].append(round(100 * h[best][2] / lib.CAP[src]))
            P[tn][f'{src[:3]} paint at turn-around'].append(h[best][2])
            P[tn][f'{src[:3]} rounds turn-around->withdraw'].append(r - best)
        elif amt > 0 and tt in lib.BOT:
            p = prev(tgt, a[0] + 1)
            P[tn][f'{src[:3]}->{tt[:3]} give amount'].append(amt)
            if p: P[tn][f'{src[:3]}->{tt[:3]} recipient paint after (% cap)'].append(round(100 * p[2] / lib.CAP[tt]))
    for k, v in nwd.items(): P[tn][f'withdrawals per game {k[:3]}'].append(v)
    P[tn]['robot->robot gives per game'].append(sum(1 for a in G.acts if a[4] == 'transfer' and a[2] == G.op and int(a[6]) > 0 and G.typ.get(int(a[5])) in lib.BOT))
    # tower paint levels
    for t in G.turns:
        if t[2] == G.op and t[3] in lib.TOW and t[0] in (50, 100, 150, 200, 300):
            P[tn][f'{t[3][:2]} tower paint at r{t[0]}'].append(t[7])
print()
for tn, D in P.items():
    print(' ', tn, '  transfer kinds (actor, target, dir):', dict(TT[tn]))
    for k in sorted(D):
        v = D[k]; print(f'     {k:<45} med {lib.med(v)} p10 {lib.pct(v, .1)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)} p90 {lib.pct(v, .9)} n={len(v)}')

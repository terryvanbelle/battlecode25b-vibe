"""Topic 50: did study 5's diagnoses move with our version?  Versions: t47 (study 5's bot), t58 (+ splasher explores
after 8 rounds without a splash), t61/y155 (+ paint tower among builds 5-7: money for builds 1-4/1-5).  Per version,
all games vs lib.STRONG and the lost ones: loss rate, median loss round, splasher idle rate (study 5 2.3 metric:
splasher turns inside a 5x5 box for 25 turns with >= 150 paint and no own tower adjacent), splasher splashes per
100 turns, paint-blocked share of tower-turns (r40+, paint < 200 with chips >= 1250), paint towers standing at r150
and r300, the round of our first paint tower built while one stands, and our non-churn paint-tower builds share."""
import lib
from collections import defaultdict
GROUP = {'t47': 't47', 't58': 't58', 't61': 't61+y155', 'y155': 't61+y155'}
S = defaultdict(list)
for G in lib.games('all'):
    v = GROUP[G.ver]
    b, d = lib.tower_events(G)
    keys = [(v, 'all')] + ([(v, 'lost')] if G.won_op else [(v, 'won')])
    # splasher idle (as study 5 t33)
    towers_cache = {}
    def towers(r):
        k = r // 5
        if k not in towers_cache: towers_cache[k] = [(x[4], x[5]) for x in lib.towers_alive(G, G.us, r, b, d)]
        return towers_cache[k]
    pos = defaultdict(list); spl_turns = 0
    for t in G.turns:
        if t[2] == G.us and t[3] == 'SPLASHER': pos[t[1]].append(t); spl_turns += 1
    stuck = 0
    for i, L in pos.items():
        j = 0
        for k in range(len(L)):
            while max(abs(L[k][4] - L[j][4]), abs(L[k][5] - L[j][5])) > 2 or k - j > 25: j += 1
            if k - j < 25: continue
            t = L[k]
            if t[7] >= 150 and not any(max(abs(t[4] - x), abs(t[5] - y)) <= 1 for x, y in towers(t[0])): stuck += 1
    splashes = sum(1 for a in G.acts if a[2] == G.us and a[4] == 'splash')
    # paint-blocked (r40+)
    bt = lib.by_round_turns(G); pb = n = 0
    for r in range(40, G.end + 1):
        chips = lib.money(G, G.us, r - 1)
        for t in bt.get(r, ()):
            if t[2] == G.us and t[3] in lib.TOW:
                n += 1
                if t[7] < 200 and chips >= 1250: pb += 1
    def pts(r):
        if G.end < r: return None
        return sum(1 for t in lib.towers_alive(G, G.us, r, b, d) if t[2] == 'PAINT_TOWER')
    # second paint tower / paint share of non-churn builds
    churn_r = defaultdict(list)
    posd = {x[1]: (x[4], x[5]) for x in b}
    for a in G.acts:
        if a[4] == 'died' and a[3] in lib.TOW and a[2] == G.us: churn_r[posd.get(a[1])].append(a[0])
    got2 = None; nb = npb = 0
    for x in b:
        if x[3] != G.us or x[0] == 0: continue
        if any(0 <= x[0] - q <= 5 for q in churn_r.get((x[4], x[5]), ())): continue
        nb += 1; npb += x[2] == 'PAINT_TOWER'
        if x[2] == 'PAINT_TOWER' and got2 is None and pts(x[0] - 1) and pts(x[0] - 1) >= 1: got2 = x[0]
    for k in keys:
        S[k + ('n',)].append(1)
        S[k + ('lost',)].append(1 if G.won_op else 0)
        if G.won_op: S[k + ('loss round',)].append(G.end)
        S[k + ('splasher idle %',)].append(round(100 * stuck / spl_turns, 1) if spl_turns else None)
        S[k + ('splashes/100 splasher turns',)].append(round(100 * splashes / spl_turns, 1) if spl_turns else None)
        S[k + ('paint-blocked %',)].append(round(100 * pb / max(1, n), 1))
        S[k + ('paint towers r150',)].append(pts(150)); S[k + ('paint towers r300',)].append(pts(300))
        S[k + ('2nd paint tower round (9999 never)',)].append(got2 or 9999)
        S[k + ('paint share of non-churn builds %',)].append(round(100 * npb / max(1, nb), 1))
        S[k + ('splasher turns',)].append(spl_turns)
for v in ('t47', 't58', 't61+y155'):
    for w in ('all', 'lost', 'won'):
        k = (v, w)
        if not S[k + ('n',)]: continue
        n = len(S[k + ('n',)])
        line = f'{v:9s} {w:4s} games {n:2d}'
        if w == 'all': line += f'  lost {sum(S[k + ("lost",)])} ({round(100 * sum(S[k + ("lost",)]) / n)}%)'
        if w == 'lost': line += f'  median loss round {lib.med(S[k + ("loss round",)])}'
        print(line)
        for m in ('splasher idle %', 'splashes/100 splasher turns', 'paint-blocked %', 'paint towers r150', 'paint towers r300',
                  '2nd paint tower round (9999 never)', 'paint share of non-churn builds %'):
            vals = S[k + (m,)]
            print(f'      {m:38s} med {lib.med(vals)}  mean {round(sum(x for x in vals if x is not None) / max(1, sum(1 for x in vals if x is not None)), 1)}')
        if w == 'all':
            tot = sum(S[k + ('splasher turns',)])
            print(f'      splasher turns total {tot}')

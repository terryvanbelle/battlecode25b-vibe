"""Topic 6b: per-turn pattern of top-team soldiers attacking our towers: for each soldier turn from its first hit on a
tower to its last hit (same tower): state = (attacked this turn?, ended inside range?). Counts of states and of
consecutive pairs; damage taken per turn from towers is not in the dump, so HP drop is used."""
import lib
from collections import Counter, defaultdict
ST = defaultdict(Counter); PR = defaultdict(Counter); HP = defaultdict(list)
for G in lib.games():
    tn = G.team_name
    b, d = lib.tower_events(G)
    tpos = {x[1]: (x[4], x[5]) for x in b}; trng = {x[1]: (16 if x[2] == 'DEFENSE_TOWER' else 9) for x in b}
    hist = defaultdict(dict)
    for t in G.turns: hist[t[1]][t[0]] = t
    att = defaultdict(set)
    for a in G.acts:
        if a[4] == 'attack' and a[3] == 'SOLDIER' and a[2] == G.op and G.typ.get(int(a[5])) in lib.TOW and G.team.get(int(a[5])) == G.us:
            att[(a[1], int(a[5]))].add(a[0])
    for (i, tid), rs in att.items():
        T = tpos[tid]; R = trng[tid]; h = hist[i]
        seq = []
        for q in range(min(rs), max(rs) + 1):
            if q not in h: continue
            ins = lib.d2((h[q][4], h[q][5]), T) <= R
            seq.append(('A' if q in rs else '-') + ('in' if ins else 'out'))
        for s in seq: ST[tn][s] += 1
        for x, y in zip(seq, seq[1:]): PR[tn][x + '>' + y] += 1
        HP[tn].append(h[max(rs)][6] if max(rs) in h else None)
for tn in ST:
    tot = sum(ST[tn].values())
    print(tn, {k: round(v / tot, 2) for k, v in ST[tn].most_common()}, 'n', tot)
    print('    pairs', PR[tn].most_common(6))
    print('    soldier HP at last hit med', lib.med(HP[tn]))

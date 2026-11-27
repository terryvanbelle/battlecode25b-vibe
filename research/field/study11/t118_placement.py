"""Topic 118: where each side puts its towers, and how long they live there.  For every tower built after r0 (starting
towers left out): its 'front' f = e_own / (e_own + e_enemy), with e = Euclidean distance to the centroid of that side's
two starting towers (f < 0.5 = the builder's own half), and d2 to the nearest standing enemy tower at the build round.
By side, type and band of f: towers built, share killed (a 'die' row; churns don't count), median life, and the share of
each band's builds that are paint towers.  Our wantType (Soldier.java:135-151) picks the type from tower counts and
chips only, never from the ruin's position; Sym (Sym.java) can mirror our starting towers to the enemy's."""
import lib, math
from collections import Counter, defaultdict

BANDS = ((0, 0.35, 'deep <0.35'), (0.35, 0.5, 'own 0.35-0.5'), (0.5, 0.65, 'their 0.5-0.65'), (0.65, 9, 'far >0.65'))


def analyse(G):
    b, d = lib.tower_events(G)
    kills = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    gone = {x[1]: x[0] for x in d}
    start = {1: [], 2: []}
    for x in b:
        if x[0] == 0 and x[3] in (1, 2): start[x[3]].append((x[4], x[5]))
    if not start[1] or not start[2]: return []
    cen = {s: (sum(p[0] for p in start[s]) / len(start[s]), sum(p[1] for p in start[s]) / len(start[s])) for s in (1, 2)}
    out = []
    for x in b:
        r, tid, typ, side, X, Y = x
        if r == 0 or side not in (1, 2): continue
        eo = math.hypot(X - cen[side][0], Y - cen[side][1]); ee = math.hypot(X - cen[3 - side][0], Y - cen[3 - side][1])
        f = eo / max(1e-9, eo + ee)
        en = [y for y in b if y[3] == 3 - side and y[0] <= r < gone.get(y[1], 10 ** 6)]
        dn = min((lib.d2((X, Y), (y[4], y[5])) for y in en), default=None)
        end = gone.get(tid, G.end)
        out.append(dict(side=side, typ=typ, f=f, dn=dn, killed=tid in kills, life=end - r, r=r))
    return out


for which in ('lost', 'won'):
    R = {'us': [], 'them': []}; n = 0
    for G in lib.games(which):
        n += 1
        for x in analyse(G): R['us' if x['side'] == G.us else 'them'].append(x)
        lib.lite(G)
    print(f'\n== {which.upper()} games: {n}; towers built after r0, by the builder\'s front band (f = share of the way to the enemy start)')
    for who in ('us', 'them'):
        rows = R[who]
        print(f'   {who}: {len(rows)} towers; median f: paint {lib.med([x["f"] for x in rows if x["typ"] == "PAINT_TOWER"])}, '
              f'money {lib.med([x["f"] for x in rows if x["typ"] == "MONEY_TOWER"])}, defense {lib.med([x["f"] for x in rows if x["typ"] == "DEFENSE_TOWER"])}')
        for lo, hi, lab in BANDS:
            B = [x for x in rows if lo <= x['f'] < hi]
            if not B: continue
            line = f'      {lab:15s} n {len(B):4d}  paint share {100 * sum(1 for x in B if x["typ"] == "PAINT_TOWER") / len(B):4.0f}%  '
            for typ in ('PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER'):
                T = [x for x in B if x['typ'] == typ]
                if not T: continue
                line += f'| {typ[:5]} {len(T):4d} killed {100 * sum(1 for x in T if x["killed"]) / len(T):3.0f}% life {lib.med([x["life"] for x in T])} '
            print(line)
        for typ in ('PAINT_TOWER', 'MONEY_TOWER'):
            T = [x for x in rows if x['typ'] == typ and x['dn'] is not None]
            line = f'      {typ[:5]} by d2 to the nearest enemy tower at build: '
            for lo, hi in ((0, 50), (51, 150), (151, 400), (401, 10 ** 6)):
                S = [x for x in T if lo <= x['dn'] <= hi]
                if S: line += f'{lo}-{hi if hi < 10 ** 6 else "+"}: n {len(S)} killed {100 * sum(1 for x in S if x["killed"]) / len(S):.0f}%; '
            print(line)

"""Topic 125: the starting towers.  Each side starts with one L2 paint tower and one L2 money tower (1500 HP) and no
pattern around them (RULES 4.6: the 5x5 is unpainted at r0).  t124: 83% of the empty tiles in our killed paint
towers' 5x5 had never been painted since r0, which points at the starting paint tower.
Per side and result:
  killed       how many starting paint / money towers die, median death round, by r100 / r200
  attackers    distinct enemy robots that hit it in the 40 rounds before death, by type; HP damage by type
  defenders    own moppers within d2 20 of it during those 40 rounds (robot-rounds), own robots that died nearby
  pattern      its 24 pattern tiles at death: ok / wrong colour / empty / enemy (as t124), and the same count at r80
               for every starting tower (the first ruin-free rounds of the opening)
  rebuilt      a tower of the side on its ruin within 50 rounds, and of which type
And for killed paint towers built later (not starting), the same pattern numbers for comparison."""
import lib
from collections import Counter, defaultdict

PAT = lib.PAT


def state(grid, W, H, x, y, side, typ):
    pat = PAT[typ]
    c = Counter()
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if not (dx or dy): continue
            X, Y = x + dx, y + dy
            if not (0 <= X < W and 0 <= Y < H): continue
            v = grid[X + Y * W]
            if v == 0: c['empty'] += 1
            elif lib.owner(v) != side: c['enemy'] += 1
            elif (v in (2, 4)) == bool((pat >> (5 * (dx + 2) + dy + 2)) & 1): c['ok'] += 1
            else: c['wrongc'] += 1
    return c


def analyse(G):
    b, d = lib.tower_events(G)
    died = {x[1]: x[0] for x in d}
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    start = [x for x in b if x[0] == 0 and x[2] in ('PAINT_TOWER', 'MONEY_TOWER')]
    later_pt = [x for x in b if x[0] > 0 and x[2] == 'PAINT_TOWER' and x[1] in killed]
    # snapshots: at r80 for starting towers, at death for killed ones
    want = defaultdict(list)
    for x in start:
        want[80].append(('r80', x))
        if x[1] in killed: want[died[x[1]]].append(('death', x))
    for x in later_pt: want[died[x[1]]].append(('death_built', x))
    snaps = {}
    grid = list(G.paint0); W = G.W
    rounds = sorted(want); ri = 0
    for a in G.acts:
        while ri < len(rounds) and a[0] > rounds[ri]:
            for (k, x) in want[rounds[ri]]: snaps[(k, x[1])] = state(grid, G.W, G.H, x[4], x[5], x[3], x[2])
            ri += 1
        if a[4] == 'paint':
            px, py = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[px + py * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        elif a[4] == 'unpaint':
            px, py = map(int, a[5].split(',')); grid[px + py * W] = 0
    while ri < len(rounds):
        for (k, x) in want[rounds[ri]]: snaps[(k, x[1])] = state(grid, G.W, G.H, x[4], x[5], x[3], x[2])
        ri += 1
    # attackers and defenders of killed starting towers
    hits = defaultdict(list)    # tower id -> [(round, attacker id, type, amount)]
    for a in G.acts:
        if a[4] == 'damage':
            tid = int(a[5])
            if G.typ.get(tid) in lib.TOW: hits[tid].append((a[0], a[1], a[3], int(a[6] or 0)))
    mops = defaultdict(list)
    for t in G.turns:
        if t[3] == 'MOPPER': mops[t[0]].append((t[2], t[4], t[5]))
    rebuilt = {}
    for x in start:
        if x[1] not in killed: continue
        r = died[x[1]]
        nxt = [y for y in b if y[0] > r and (y[4], y[5]) == (x[4], x[5])]
        rebuilt[x[1]] = (nxt[0][0] - r, nxt[0][2], nxt[0][3] == x[3]) if nxt else None
    out = []
    for x in start:
        tid = x[1]; r = died.get(tid)
        rec = dict(side=x[3], typ=x[2], killed=tid in killed, r=r if tid in killed else None,
                   r80=snaps.get(('r80', tid)), atdeath=snaps.get(('death', tid)))
        if tid in killed:
            H_ = [h for h in hits[tid] if r - 40 <= h[0] <= r]
            rec['att'] = Counter(); rec['dmg'] = Counter()
            for typ in lib.BOT:
                rec['att'][typ] = len(set(h[1] for h in H_ if h[2] == typ))
                rec['dmg'][typ] = sum(h[3] for h in H_ if h[2] == typ)
            rec['mopr'] = sum(1 for rr in range(r - 40, r + 1) for (s, mx, my) in mops.get(rr, ()) if s == x[3] and lib.d2((mx, my), (x[4], x[5])) <= 20)
            rec['reb'] = rebuilt.get(tid)
        out.append(rec)
    built = [dict(side=x[3], st=snaps.get(('death_built', x[1]))) for x in later_pt]
    return out, built


for which in ('lost', 'won'):
    S = defaultdict(list); B = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        o, bl = analyse(G)
        for rec in o: S[('us' if rec['side'] == G.us else 'them', rec['typ'])].append(rec)
        for rec in bl: B['us' if rec['side'] == G.us else 'them'].append(rec)
        lib.lite(G)
    print(f'\n== {which} games ({n})')
    for key in sorted(S):
        R = S[key]; K = [x for x in R if x['killed']]
        avg = lambda L, k: (sum(c[k] for c in L) / len(L)) if L else 0
        r80 = [x['r80'] for x in R if x['r80'] is not None]
        print(f'   {key[0]:4s} start {key[1]:12s}: {len(R)} towers, killed {len(K)} (by r100 {sum(1 for x in K if x["r"] <= 100)}, '
              f'by r200 {sum(1 for x in K if x["r"] <= 200)}), median death r{lib.med([x["r"] for x in K])}; '
              f'pattern at r80 per tower ok {avg(r80, "ok"):.1f} wrong {avg(r80, "wrongc"):.1f} empty {avg(r80, "empty"):.1f} enemy {avg(r80, "enemy"):.1f}')
        if K:
            ad = [x['atdeath'] for x in K if x['atdeath'] is not None]
            att = Counter(); dmg = Counter()
            for x in K: att.update(x['att']); dmg.update(x['dmg'])
            reb = [x['reb'] for x in K]
            print(f'        killed: attackers in its last 40 rounds per tower S {att["SOLDIER"] / len(K):.1f} X {att["SPLASHER"] / len(K):.1f} '
                  f'M {att["MOPPER"] / len(K):.1f}; damage share S {100 * dmg["SOLDIER"] / max(1, sum(dmg.values())):.0f}% X {100 * dmg["SPLASHER"] / max(1, sum(dmg.values())):.0f}%; '
                  f'own mopper-rounds within d2 20 in those 40 rounds med {lib.med([x["mopr"] for x in K])} (zero in {sum(1 for x in K if x["mopr"] == 0)}); '
                  f'pattern at death ok {avg(ad, "ok"):.1f} wrong {avg(ad, "wrongc"):.1f} empty {avg(ad, "empty"):.1f} enemy {avg(ad, "enemy"):.1f}; '
                  f'no enemy tile at death {sum(1 for c in ad if c["enemy"] == 0)}, at most 2 {sum(1 for c in ad if c["enemy"] <= 2)}; '
                  f'rebuilt by the side within 50 rounds {sum(1 for x in reb if x and x[2] and x[0] <= 50)} '
                  f'(as {dict(Counter(x[1][:5] for x in reb if x and x[2] and x[0] <= 50))}), taken by the other side {sum(1 for x in reb if x and not x[2])}, never {sum(1 for x in reb if x is None)}')
    for who in ('us', 'them'):
        L = [x['st'] for x in B[who] if x['st'] is not None]
        if L:
            print(f'   {who:4s} killed paint towers built after r0: {len(L)}; pattern at death ok {sum(c["ok"] for c in L) / len(L):.1f} '
                  f'wrong {sum(c["wrongc"] for c in L) / len(L):.1f} empty {sum(c["empty"] for c in L) / len(L):.1f} enemy {sum(c["enemy"] for c in L) / len(L):.1f}; '
                  f'24 ok {sum(1 for c in L if c["ok"] >= 24)}')

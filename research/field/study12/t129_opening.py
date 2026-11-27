"""Topic 129: the opening, r1-150, pieces study 9/10 did not measure.  Per side, medians per game (sums in brackets):
  spawns     round of spawn #1-#8 (robots), robots spawned by r25 / r50, first mopper / splasher round, and the robots
             spawned in r1-100 by the starting paint tower, the starting money tower and built towers
  builds     for new-ruin builds #1-#5 (no tower of either side stood on the ruin before): round, share paint, d2 from
             the side's nearer starting tower, 'rank' = the ruin's place among the free ruins of the map ordered by
             distance from the side's nearer starting tower at the build round (1 = the nearest free ruin), and the
             front f = e_own / (e_own + e_enemy) (Euclidean distance to the nearer starting tower of each side;
             f < 0.5 = own half)
  painters   distinct robots of the side that painted the ruin's 5x5 in the 60 rounds before a new-ruin build in
             r1-150, and the paint they put there (5 per paint action)
  parallel   free ruins the side painted in the last 10 rounds, mean over r20-150 and max
  marks      per side in r1-150: 24-tile pattern marks (>= 20 mark rows by one robot in one round), single marks, unmarks
  SRPs       first SRP round, SRPs completed by r150 / r200; first defense tower round
  fights     towers killed each way by r150, robots killed by towers by r150 (actor of the die row is a tower)
Lost games split into behind at r100 (fewer towers than them) and level/ahead; won games."""
import lib, math
from collections import defaultdict, Counter


def analyse(G):
    b, d = lib.tower_events(G)
    W, H = G.W, G.H
    start = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    startkind = {x[1]: ('sP' if x[2] == 'PAINT_TOWER' else 'sM') for x in b if x[0] == 0}
    life = defaultdict(list)    # ruin -> [(from, to, side)]
    dr = {x[1]: x[0] for x in d}
    for x in b: life[(x[4], x[5])].append((x[0], dr.get(x[1], 10 ** 6), x[3]))
    ruins = list(G.ruins)
    def free(p, r): return not any(lo <= r < hi for lo, hi, s in life.get(p, ()))
    def ever_before(p, r): return any(lo < r for lo, hi, s in life.get(p, ()))
    def dmin(p, s): return min(math.dist(p, q) for q in start[s]) if start[s] else 99
    # tile -> ruins whose 5x5 holds it
    t2r = defaultdict(list)
    for p in ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy:
                    X, Y = p[0] + dx, p[1] + dy
                    if 0 <= X < W and 0 <= Y < H: t2r[(X, Y)].append(p)
    out = {}
    for s in (1, 2):
        o = s % 2 + 1
        rec = {}
        sp = [a for a in G.acts if a[4] == 'spawn' and a[2] == s and a[3] in lib.TOW and a[6] in lib.BOT]
        for i in range(8): rec[f'spawn #{i + 1}'] = sp[i][0] if len(sp) > i else None
        rec['spawned r25'] = sum(1 for a in sp if a[0] <= 25)
        rec['spawned r50'] = sum(1 for a in sp if a[0] <= 50)
        rec['first mopper'] = next((a[0] for a in sp if a[6] == 'MOPPER'), None)
        rec['first splasher'] = next((a[0] for a in sp if a[6] == 'SPLASHER'), None)
        for k in ('sP', 'sM', 'built'):
            rec[f'r1-100 spawns by {k}'] = sum(1 for a in sp if a[0] <= 100 and startkind.get(a[1], 'built') == k)
        # new-ruin builds
        nb = [x for x in b if x[3] == s and x[0] > 0 and not ever_before((x[4], x[5]), x[0])]
        for i in range(5):
            if len(nb) > i:
                x = nb[i]; p = (x[4], x[5])
                fr = sorted((dmin(q, s), q) for q in ruins if free(q, x[0] - 1) or q == p)
                rank = 1 + [q for _, q in fr].index(p) if p in [q for _, q in fr] else None
                rec[f'build #{i + 1} round'] = x[0]
                rec[f'build #{i + 1} paint'] = 100 if x[2] == 'PAINT_TOWER' else 0
                rec[f'build #{i + 1} d2 own'] = round(dmin(p, s) ** 2)
                rec[f'build #{i + 1} rank'] = rank
                eo, ee = dmin(p, s), dmin(p, o)
                rec[f'build #{i + 1} front'] = round(eo / (eo + ee), 2) if eo + ee else None
            else:
                for k in ('round', 'paint', 'd2 own', 'rank', 'front'): rec[f'build #{i + 1} {k}'] = None
        # painters and paint per new-ruin build in r1-150
        painters, paints = [], []
        acts_s = [a for a in G.acts if a[4] == 'paint' and a[2] == s and a[0] <= 150]
        for x in nb:
            if x[0] > 150: break
            p = (x[4], x[5])
            ids = set(); n = 0
            for a in acts_s:
                if x[0] - 60 <= a[0] <= x[0]:
                    X, Y = map(int, a[5].split(','))
                    if max(abs(X - p[0]), abs(Y - p[1])) <= 2 and (X, Y) != p: ids.add(a[1]); n += 1
            painters.append(len(ids)); paints.append(5 * n)
        rec['painters per build'] = lib.med(painters) if painters else None
        rec['paint per build'] = lib.med(paints) if paints else None
        # parallel attempts
        recent = defaultdict(dict)   # ruin -> last round painted
        conc = []
        byr = defaultdict(list)
        for a in acts_s:
            X, Y = map(int, a[5].split(','))
            for p in t2r.get((X, Y), ()): byr[a[0]].append(p)
        last = {}
        for r in range(1, 151):
            for p in byr.get(r, ()): last[p] = r
            if r >= 20: conc.append(sum(1 for p, lr in last.items() if r - lr < 10 and free(p, r)))
        rec['parallel mean'] = round(sum(conc) / len(conc), 2) if conc else None
        rec['parallel max'] = max(conc) if conc else None
        # marks
        mk = Counter((a[0], a[1]) for a in G.acts if a[4] == 'mark' and a[2] == s and a[0] <= 150)
        rec['pattern marks r150'] = sum(1 for v in mk.values() if v >= 20)
        rec['single marks r150'] = sum(v for v in mk.values() if v < 20)
        rec['unmarks r150'] = sum(1 for a in G.acts if a[4] == 'unmark' and a[2] == s and a[0] <= 150)
        srp = [a[0] for a in G.acts if a[4] == 'srp' and a[2] == s]
        rec['first SRP'] = srp[0] if srp else None
        rec['SRPs r150'] = sum(1 for r in srp if r <= 150)
        rec['SRPs r200'] = sum(1 for r in srp if r <= 200)
        rec['first defense'] = next((x[0] for x in b if x[3] == s and x[0] > 0 and x[2] == 'DEFENSE_TOWER'), None)
        kills = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
        rec['towers killed r150'] = sum(1 for x in d if x[3] == o and x[0] <= 150 and x[1] in kills)
        rec['robots killed by towers r150'] = sum(1 for a in G.acts if a[4] == 'die' and a[0] <= 150 and a[3] in lib.TOW
                                                  and a[2] == s and a[7] in lib.BOT)
        out[s] = rec
    return out


groups = defaultdict(list)
for G in lib.games('all'):
    tw_u, tw_o = lib.rv(G, G.us, 100, 'tow'), lib.rv(G, G.op, 100, 'tow')
    grp = ('lost, behind at r100' if tw_u < tw_o else 'lost, level/ahead at r100') if G.won_op else 'won'
    o = analyse(G)
    groups[grp].append((o[G.us], o[G.op]))
    groups['all lost' if G.won_op else 'all won'].append((o[G.us], o[G.op]))
    lib.lite(G)
for grp in ('all lost', 'lost, behind at r100', 'lost, level/ahead at r100', 'won'):
    L = groups[grp]
    print(f'\n== {grp}: {len(L)} games; medians per game (means for shares), us / them')
    for k in L[0][0]:
        u = [x[0][k] for x in L]; t = [x[1][k] for x in L]
        if k.endswith(' paint'):
            fu = [v for v in u if v is not None]; ft = [v for v in t if v is not None]
            print(f'   {k:28s} {lib.mean(fu)}% / {lib.mean(ft)}%  (n {len(fu)} / {len(ft)})')
        elif k.startswith(('spawned', 'r1-100', 'pattern', 'single', 'unmarks', 'SRPs', 'towers killed', 'robots killed')):
            print(f'   {k:28s} {lib.med(u)} / {lib.med(t)}   [{sum(v for v in u if v)} / {sum(v for v in t if v)}]')
        else:
            print(f'   {k:28s} {lib.med(u)} / {lib.med(t)}' + (f'   (reached {sum(1 for v in u if v is not None)} / {sum(1 for v in t if v is not None)})' if any(v is None for v in u + t) else ''))

"""Topics 7+8: moppers and splashers of the top teams.
Moppers (sampled every 2nd round): distance to own nearest tower, to nearest of OUR painted tiles (frontier), to
nearest of our robots; action mix per turn; what single mops hit (robot / tile); where mopped tiles are.
Splashers: paint before each splash, composition of the 13 tiles in r^2<=4 before the splash (ours/empty/own/
unpaintable), tiles changed, distance of splasher to nearest of our painted tiles, enemy towers in the splash."""
import lib
from collections import Counter, defaultdict
P = defaultdict(lambda: defaultdict(list)); MIX = defaultdict(Counter); SPL = defaultdict(Counter)
AOE = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if dx * dx + dy * dy <= 4]
for G in lib.games():
    tn = G.team_name; W, H = G.W, G.H
    b, d = lib.tower_events(G)
    rt = lib.by_round_turns(G)
    hist = defaultdict(dict)
    for t in G.turns: hist[t[1]][t[0]] = t
    ruinset = set(G.ruins)
    rtiles = set((rx + dx, ry + dy) for (rx, ry) in G.ruins for dx in range(-2, 3) for dy in range(-2, 3))
    turnacts = defaultdict(list)
    for a in G.acts: turnacts[(a[0], a[1])].append(a)
    usv = (1, 2) if G.us == 1 else (3, 4); opv = (3, 4) if G.us == 1 else (1, 2)
    state = {'r': 0}
    towers_at = {}
    def process_round(r, grid):
        # grid = state at end of round r
        if r % 2: return
        ours = [(i % W, i // W) for i, v in enumerate(grid) if v in usv]
        al = lib.towers_alive(G, G.op, r, b, d)
        usr = [(t[4], t[5]) for t in rt[r] if t[2] == G.us and t[3] in lib.BOT]
        for t in rt[r]:
            if t[2] != G.op or t[3] not in ('MOPPER', 'SPLASHER'): continue
            p = (t[4], t[5])
            dt = min((lib.d2(p, (q[4], q[5])) for q in al), default=None)
            df = min((lib.d2(p, q) for q in ours), default=None)
            de = min((lib.d2(p, q) for q in usr), default=None)
            k = t[3][:3]
            P[tn][f'{k} dist to own tower'].append(round(dt ** .5, 1) if dt is not None else None)
            P[tn][f'{k} dist to our paint (frontier)'].append(round(df ** .5, 1) if df is not None else None)
            P[tn][f'{k} dist to our robot'].append(round(de ** .5, 1) if de is not None else None)
            if k == 'MOP':
                acts = turnacts[(r, t[1])]
                kinds = Counter(a[4] for a in acts)
                if kinds['mop']: kind = 'swing'
                elif kinds['attack']: kind = 'mop robot'
                elif kinds['unpaint']: kind = 'mop tile'
                elif any(a[4] == 'transfer' and int(a[6]) > 0 for a in acts): kind = 'give paint'
                elif kinds['transfer']: kind = 'withdraw'
                else: kind = 'none'
                MIX[tn][kind] += 1
                P[tn]['MOP paint'].append(t[7])
                if kind == 'none': P[tn]['MOP idle: dist to our paint'].append(round(df ** .5, 1) if df is not None else None)
    def hook(a, grid):
        if a[0] != state['r']:
            process_round(state['r'], grid); state['r'] = a[0]
        if a[2] != G.op: return
        if a[4] == 'splash':
            x, y = map(int, a[5].split(','))
            c = Counter()
            for dx, dy in AOE:
                X, Y = x + dx, y + dy
                if not (0 <= X < W and 0 <= Y < H) or X + Y * W in G.walls or (X, Y) in ruinset: c['unpaintable'] += 1; continue
                v = grid[X + Y * W]
                c['ours(enemy to them)' if v in usv else 'own' if v in opv else 'empty'] += 1
            SPL[tn].update(c)
            gain = c['empty'] + sum(1 for dx, dy in AOE if dx * dx + dy * dy <= 2 and 0 <= x + dx < W and 0 <= y + dy < H and grid[x + dx + (y + dy) * W] in usv)
            P[tn]['SPL tiles gained per splash (empty + ours within r2<=2)'].append(gain)
            P[tn]['SPL our tiles in aoe'].append(c['ours(enemy to them)'])
            P[tn]['SPL empty tiles in aoe'].append(c['empty'])
            h = hist[a[1]]
            pp = next((h[q][7] for q in range(a[0] - 1, a[0] - 4, -1) if q in h), None)
            P[tn]['SPL paint before splash'].append(pp)
            P[tn]['SPL splash in ruin 5x5 area (frac)'].append(1 if (x, y) in rtiles else 0)
        if a[4] == 'unpaint' and a[3] == 'MOPPER':
            x, y = map(int, a[5].split(','))
            P[tn]['MOP mopped tile within a ruin 5x5 (frac)'].append(1 if (x, y) in rtiles else 0)
            al = lib.towers_alive(G, G.op, a[0], b, d) if a[0] % 5 == 0 else None
        if a[4] == 'mop':
            P[tn]['MOP robots hit per swing record'].append(sum(1 for z in a[5:8] if z not in ('0', '')))
    lib.replay_grid(G, hook)
    nsp = sum(1 for a in G.acts if a[4] == 'splash' and a[2] == G.op)
    P[tn]['splashes per game'].append(nsp)
    P[tn]['splashes per splasher-turn'].append(round(nsp / max(1, sum(1 for t in G.turns if t[2] == G.op and t[3] == 'SPLASHER')), 2))
for tn, D in P.items():
    print(' ', tn)
    tot = sum(MIX[tn].values()); print('     mopper turn mix (sampled):', {k: round(v / tot, 2) for k, v in MIX[tn].most_common()}, 'n', tot)
    tot = sum(SPL[tn].values()); print('     splash aoe composition:', {k: round(v / tot, 2) for k, v in SPL[tn].most_common()})
    for k in sorted(D):
        v = D[k]; print(f'     {k:<58} med {lib.med(v)} mean {round(sum(x for x in v if x is not None)/max(1,len([x for x in v if x is not None])),2)} p10 {lib.pct(v, .1)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)} p90 {lib.pct(v, .9)} n={len(v)}')

"""Topic 73: where our moppers clean since t74 (study 6 2.1c: Mopper.nearRuin() adds 40 for enemy paint within d2 <= 8 of
ANY visible ruin - G.ruins is senseNearbyRuins(-1), which includes ruins with a tower on them, the enemy's too).
Per version (y155 / t70: weight 10 and 6, t74: 40), all games: our mopper unpaint actions by the nearest ruin within
d2 <= 8 of the tile - none, a free ruin, our standing tower, their standing tower - and our mopper deaths within
d2 <= 9 of a standing enemy tower (its attack range), per 100 mopper-turns.  Their moppers for comparison."""
import lib, os
from collections import defaultdict, Counter
os.environ.setdefault('S7SET', 'main')
C = defaultdict(Counter); T = Counter(); DT = Counter()
for G in lib.games('all'):
    v = G.ver
    b, d = lib.tower_events(G)
    alive = {}            # round -> {(x, y): side}
    ev = sorted([(x[0], 1, x) for x in b] + [(x[0], 0, x) for x in d])
    cur = {}; k = 0
    acts = sorted((a for a in G.acts if a[4] == 'unpaint' and a[3] == 'MOPPER'), key=lambda a: a[0])
    deaths = [a for a in G.acts if a[4] in ('die', 'died') and a[7] == 'MOPPER']
    last = {}
    for t in G.turns:
        if t[3] == 'MOPPER': last[t[1]] = t; T[(v, 'us' if t[2] == G.us else 'them')] += 1
    need = sorted(set([a[0] for a in acts] + [a[0] for a in deaths]))
    snap = {}
    i = 0
    for r in need:
        while i < len(ev) and ev[i][0] <= r:
            _, isb, x = ev[i]
            if isb: cur[(x[4], x[5])] = x[3]
            else: cur.pop((x[4], x[5]), None)
            i += 1
        snap[r] = dict(cur)
    ruins = [tuple(p) for p in G.ruins]
    for a in acts:
        x, y = map(int, a[5].split(','))
        w = 'us' if a[2] == G.us else 'them'
        near = [p for p in ruins if lib.d2(p, (x, y)) <= 8]
        if not near: cls = 'no ruin near'
        else:
            occ = [snap[a[0]].get(p) for p in near]
            if any(o == a[2] for o in occ): cls = 'own tower'
            elif any(o is None for o in occ): cls = 'free ruin'
            else: cls = 'enemy tower'
        C[(v, w)][cls] += 1
    for a in deaths:
        tid = int(a[5])
        if tid not in last: continue
        t = last[tid]
        w = 'us' if t[2] == G.us else 'them'
        if any(s != t[2] and lib.d2(p, (t[4], t[5])) <= 9 for p, s in snap.get(a[0], {}).items()): DT[(v, w, 'by tower')] += 1
        DT[(v, w, 'all')] += 1
print('version side | mopper unpaints by nearest ruin (d2 <= 8 of the tile): no ruin / free ruin / own tower / enemy tower | mopper deaths per 100 mopper-turns (within an enemy tower\'s range)')
for v in sorted(set(k[0] for k in C)):
    for w in ('us', 'them'):
        c = C[(v, w)]; n = sum(c.values()) or 1
        print(f'  {v:5s} {w:4s} | n {n:5d}: ' + ' / '.join(f'{100 * c[k] / n:4.1f}%' for k in ('no ruin near', 'free ruin', 'own tower', 'enemy tower')) +
              f' | deaths {100 * DT[(v, w, "all")] / max(1, T[(v, w)]):.2f} ({100 * DT[(v, w, "by tower")] / max(1, T[(v, w)]):.2f} near an enemy tower), mopper-turns {T[(v, w)]}')

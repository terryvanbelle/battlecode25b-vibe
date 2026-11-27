"""Topic 51: what happens to a ruin after its tower is KILLED (churn excluded), us vs them, lost vs won games.
For each killed tower: was its 24-tile pattern still intact (owner's colours, right primary/secondary) at death, how
many enemy tiles sat in its 5x5, and the next build on that ruin: by the owner (delay, same type or not), by the
killer (stolen), or none before the game ended.  Rebuilding an intact pattern needs only an adjacent robot and 1000
chips (Unit.rebuild() in our bot tries only a MONEY tower on an adjacent ruin)."""
import lib
from collections import defaultdict, Counter
BIN = (5, 20, 50, 100)
for which in ('lost', 'won'):
    C = defaultdict(Counter); D = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        pos = {x[1]: (x[4], x[5]) for x in b}
        typ = {x[1]: x[2] for x in b}
        builds_at = defaultdict(list)
        for x in b:
            if x[0] > 0: builds_at[(x[4], x[5])].append((x[0], x[3], x[2]))
        deaths = {}
        for a in G.acts:
            if a[4] == 'die' and a[7] in lib.TOW: deaths[(a[0], int(a[5]))] = a[7]
        snap = {}
        def hook(a, grid):
            if a[4] == 'die' and a[7] in lib.TOW:
                tid = int(a[5]); p = pos.get(tid)
                if p is None: return
                side = G.team.get(tid); pat = a[7]
                ok = 0; en = 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx == 0 and dy == 0: continue
                        x, y = p[0] + dx, p[1] + dy
                        if not (0 <= x < G.W and 0 <= y < G.H): continue
                        v = grid[x + y * G.W]; o = lib.owner(v)
                        if o and o != side: en += 1
                        sec = v in (2, 4)
                        if o == side and sec == lib.secondary(pat, dx, dy): ok += 1
                snap[tid] = (ok, en)
        lib.replay_grid(G, hook)
        for (r, tid), tp in deaths.items():
            side = G.team.get(tid); p = pos.get(tid)
            if p is None: continue
            w = 'us' if side == G.us else 'them'
            ok, en = snap.get(tid, (0, 0))
            intact = ok >= 24
            C[w]['killed'] += 1; C[w]['intact at death'] += intact
            D[(w, 'enemy tiles in 5x5 at death')].append(en)
            nxt = [q for q in builds_at.get(p, ()) if q[0] >= r]
            if not nxt:
                C[w]['never rebuilt'] += 1
                D[(w, 'rounds left when never rebuilt')].append(G.end - r)
                continue
            rr, bside, btype = nxt[0]
            if bside != side:
                C[w]['taken by the killer'] += 1; D[(w, 'delay to steal')].append(rr - r); continue
            dl = rr - r
            C[w]['rebuilt by owner'] += 1
            C[w]['rebuilt same type'] += btype == tp
            D[(w, 'rebuild delay (owner)')].append(dl)
            D[(w, 'rebuild delay, intact' if intact else 'rebuild delay, broken')].append(dl)
            if tp == 'PAINT_TOWER': D[(w, 'rebuild delay, paint tower')].append(dl); C[w]['paint tower rebuilt as ' + btype[:5]] += 1
            for bn in BIN:
                if dl <= bn: C[w][f'rebuilt within {bn}'] += 1
        for tid in [t for (r, t) in deaths]:
            pass
    print(f'== {which} games')
    for w in ('us', 'them'):
        c = C[w]; n = max(1, c['killed'])
        print(f'  {w:4s} killed {c["killed"]}: intact at death {c["intact at death"]} ({round(100 * c["intact at death"] / n)}%), rebuilt by owner {c["rebuilt by owner"]} '
              f'({round(100 * c["rebuilt by owner"] / n)}%; same type {c["rebuilt same type"]}), taken by the killer {c["taken by the killer"]}, never {c["never rebuilt"]}')
        print('       rebuilt within ' + ', '.join(f'{bn}: {c[f"rebuilt within {bn}"]} ({round(100 * c[f"rebuilt within {bn}"] / n)}%)' for bn in BIN))
        print('       ' + ', '.join(f'{k}: {v}' for k, v in sorted(c.items()) if k.startswith('paint tower rebuilt')))
        for k in ('rebuild delay (owner)', 'rebuild delay, intact', 'rebuild delay, broken', 'rebuild delay, paint tower', 'delay to steal',
                  'enemy tiles in 5x5 at death', 'rounds left when never rebuilt'):
            v = D[(w, k)]
            if v: print(f'       {k:34s} n={len(v):3d} med {lib.med(v)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)}')

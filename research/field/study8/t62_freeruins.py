"""Topic 62: the free ruins we leave alone.  At r100 / r150 / r200, every ruin with no tower on it, in lost and won
games: enemy and own tiles in its 5x5 (replayed grid), our soldier-turns within Chebyshev 4 in the next 50 rounds,
whether we marked it in the next 50 rounds, and who built on it next (and when).  Split by side of the map (nearer
to our starting towers or to theirs).  Our Soldier.pickRuin drops a ruin with ANY visible enemy tile in its 5x5 for
50 rounds; workRuin drops it after 25 blocked rounds."""
import lib
from collections import defaultdict, Counter
CK = (100, 150, 200)
for which in ('lost', 'won'):
    C = defaultdict(Counter); D = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
        def half(p):
            du = min(lib.d2(p, q) for q in start[G.us]); do = min(lib.d2(p, q) for q in start[G.op])
            return 'ours' if du < do else 'theirs'
        snaps = {}
        want = set(CK)
        def hook(a, grid):
            r = a[0] - 1
            if r in want and r not in snaps:
                s = {}
                for p in G.ruins:
                    en = own = 0
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            x, y = p[0] + dx, p[1] + dy
                            if (dx or dy) and 0 <= x < G.W and 0 <= y < G.H:
                                o = lib.owner(grid[x + y * G.W])
                                if o == G.us: own += 1
                                elif o == G.op: en += 1
                    s[p] = (en, own)
                snaps[r] = s
        lib.replay_grid(G, hook)
        marks = defaultdict(list)
        for a in G.acts:
            if a[4] == 'mark' and a[2] == G.us and a[3] in lib.BOT:
                x, y = map(int, a[5].split(','))
                for p in G.ruins:
                    if max(abs(p[0] - x), abs(p[1] - y)) <= 2: marks[p].append(a[0])
        sol = defaultdict(list)
        for t in G.turns:
            if t[2] == G.us and t[3] == 'SOLDIER': sol[t[0]].append((t[4], t[5]))
        nextb = defaultdict(list)
        for x in b:
            if x[0] > 0: nextb[(x[4], x[5])].append((x[0], x[3]))
        for r in CK:
            if G.end < r + 10 or r not in snaps: continue
            occ = set((t[4], t[5]) for sd in (1, 2) for t in lib.towers_alive(G, sd, r, b, d))
            for p in G.ruins:
                if p in occ: continue
                h = half(p)
                en, own = snaps[r][p]
                k = (r, h)
                C[k]['free'] += 1
                cls = 'clean' if en == 0 else ('1-4 enemy' if en <= 4 else '5+ enemy')
                C[k][cls] += 1
                vis = sum(1 for q in range(r, min(G.end, r + 50) + 1) for s in sol.get(q, ()) if max(abs(s[0] - p[0]), abs(s[1] - p[1])) <= 4)
                mk = any(r <= q <= r + 50 for q in marks.get(p, ()))
                nb = [x for x in nextb.get(p, ()) if x[0] >= r]
                who = 'none' if not nb else ('us' if nb[0][1] == G.us else 'them')
                C[k][f'{cls}: next built by {who}'] += 1
                if nb and nb[0][0] <= r + 50: C[k][f'{cls}: built <=50 by {who}'] += 1
                C[k][f'{cls}: we marked <=50'] += mk
                D[(k, cls, 'soldier-turns cheb<=4 next 50')].append(vis)
    print(f'== {which} games: free ruins at r100/150/200, by map half (ours = nearer our starting towers)')
    for r in CK:
        for h in ('ours', 'theirs'):
            k = (r, h); c = C[k]
            if not c['free']: continue
            print(f'  r{r} {h:6s} free {c["free"]}: clean {c["clean"]}, 1-4 enemy {c["1-4 enemy"]}, 5+ enemy {c["5+ enemy"]}')
            for cls in ('clean', '1-4 enemy', '5+ enemy'):
                if not c[cls]: continue
                print(f'      {cls:9s} we marked within 50: {c[cls + ": we marked <=50"]}/{c[cls]}; built within 50 by us {c[cls + ": built <=50 by us"]}, by them {c[cls + ": built <=50 by them"]};'
                      f' next built by us {c[cls + ": next built by us"]}, them {c[cls + ": next built by them"]}, never {c[cls + ": next built by none"]};'
                      f' our soldier-turns cheb<=4 (next 50) med {lib.med(D[(k, cls, "soldier-turns cheb<=4 next 50")])}')

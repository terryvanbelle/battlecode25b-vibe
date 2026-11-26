"""Topic 100: our SRPs broken by our own tower-pattern painting (t97: the biggest single cause).  For each SRP of the
side whose first wrong tile at the failing check was painted by one of its own soldiers over a right tile inside a
ruin's 5x5, look at that ruin: what stood there when the SRP was completed (own tower of type P/M/D, empty, enemy
tower), what happened to it before the break (own tower killed, churned, nothing), and what the side built there
next (type, rounds after the break).  Also: how many of the side's SRPs had a ruin within Chebyshev 4 of the centre
at completion, by the ruin's state, and their activation rate (50 rounds intact)."""
import lib
from collections import defaultdict, Counter


def analyse(G):
    W = G.W
    b, d = lib.tower_events(G)
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    ev = defaultdict(list)    # loc -> [(round, kind 'b'/'d', side, type, killed?)]
    for x in b: ev[(x[4], x[5])].append((x[0], 'b', x[3], x[2][0], False))
    for x in d: ev[(x[4], x[5])].append((x[0], 'd', x[3], x[2][0], x[1] in killed))
    for k in ev: ev[k].sort()

    def state(loc, r):
        """('own'|'enemy'|'empty', type) of the tower on loc after round r's events, from side s's view (filled later)."""
        st = None
        for e in ev.get(loc, ()):
            if e[0] > r: break
            st = (e[2], e[3]) if e[1] == 'b' else None
        return st

    ruins = list(G.ruins)
    grid = list(G.paint0)
    last = [None] * (W * G.H)
    live = {}
    out_breaks, out_srps = [], []
    ends = {}

    def check(r):
        for k in list(live):
            s, cx, cy = k
            for dx in range(-2, 3):
                bad = None
                for dy in range(-2, 3):
                    i = cx + dx + (cy + dy) * W
                    sec = lib.secondary('SRP', dx, dy)
                    want = (2 if sec else 1) if s == 1 else (4 if sec else 3)
                    if grid[i] != want:
                        bad = (i, cx + dx, cy + dy, want); break
                if bad: break
            if not bad: continue
            r0 = live.pop(k)
            ends[(s, cx, cy, r0)] = r
            i, tx, ty, want = bad
            L = last[i]
            v = grid[i]
            if lib.owner(v) == s and L and L[1] == s and L[2] == 'SOLDIER' and L[3] == want:
                # the ruins whose 5x5 holds the tile
                for (rx, ry) in ruins:
                    if abs(rx - tx) <= 2 and abs(ry - ty) <= 2:
                        st0 = state((rx, ry), r0)
                        at = 'empty' if st0 is None else (('own ' if st0[0] == s else 'enemy ') + st0[1])
                        between = [e for e in ev.get((rx, ry), ()) if r0 < e[0] <= r]
                        what = 'nothing'
                        for e in between:
                            if e[1] == 'd' and e[2] == s: what = 'own tower killed' if e[4] else 'own tower churned/gone'
                            if e[1] == 'd' and e[2] != s: what = 'enemy tower killed'
                        nxt = [e for e in ev.get((rx, ry), ()) if e[0] >= r - 3 and e[1] == 'b' and e[2] == s]
                        built = (nxt[0][3], nxt[0][0] - r) if nxt else ('-', None)
                        out_breaks.append(dict(side=s, at=at, what=what, built=built[0], after=built[1], age=r - r0))
                        break

    last_r = 0
    for a in G.acts:
        r = a[0]
        if r != last_r:
            check(r); last_r = r
        k = a[4]
        if k == 'paint' or k == 'unpaint':
            x, y = map(int, a[5].split(',')); i = x + y * W
            old = grid[i]
            if k == 'paint':
                grid[i] = (2 if a[6] == '1' else 1) if a[2] == 1 else (4 if a[6] == '1' else 3)
            else:
                grid[i] = 0
            if grid[i] != old: last[i] = (r, a[2], a[3], old)
        elif k == 'srp':
            cx, cy = map(int, a[5].split(','))
            s = a[2]
            live[(s, cx, cy)] = r
            near = []
            for (rx, ry) in ruins:
                ch = max(abs(rx - cx), abs(ry - cy))
                if ch <= 4:
                    st0 = state((rx, ry), r)
                    near.append('empty' if st0 is None else (('own ' if st0[0] == s else 'enemy ') + st0[1]))
            out_srps.append(dict(side=s, r0=r, near=near, key=(s, cx, cy, r)))
    for e in out_srps:
        e['life'] = ends.get(e['key'], G.end) - e['r0']
    return out_breaks, out_srps


for which in ('lost', 'won'):
    B = defaultdict(Counter); S = defaultdict(Counter); n = 0; ages = defaultdict(list)
    for G in lib.games(which):
        n += 1
        br, srps = analyse(G)
        for e in br:
            side = 'us' if e['side'] == G.us else 'them'
            B[side][(e['at'], e['what'], e['built'])] += 1
            ages[side].append(e['age'])
        for e in srps:
            side = 'us' if e['side'] == G.us else 'them'
            act = e['life'] >= 50
            cats = ['all'] + (['no ruin within Chebyshev 4'] if not e['near'] else ['ruin within 4: ' + st for st in set(e['near'])])
            for c in cats:
                S[side][c] += 1
                if act: S[side][c + ' (active)'] += 1
    print(f'== {which} games ({n})')
    for side in ('us', 'them'):
        tot = sum(B[side].values())
        print(f'   {side}: SRPs broken by own soldier tower-pattern paint: {tot}, SRP age at the break med {lib.med(ages[side])}')
        print('      ruin at SRP completion | what happened to it before the break | built there next by the side')
        for (at, what, built), c in B[side].most_common(10):
            print(f'      {c:5d}  {at:9s} | {what:24s} | {built}')
        print(f'   {side}: SRP completions {S[side]["all"]} ({100 * S[side]["all (active)"] / max(1, S[side]["all"]):.0f}% reach 50 rounds), by ruins within Chebyshev 4 of the centre at completion:')
        for k in sorted(k for k in S[side] if k != 'all' and not k.endswith('(active)')):
            print(f'         {k:34s} {S[side][k]:5d}  active {100 * S[side][k + " (active)"] / S[side][k]:3.0f}%')
    print()

"""Topic 124: why a killed paint tower of ours is so rarely rebuilt (t114: in the losses 21% of our killed paint towers
still held 20+ of their pattern tiles with no enemy tile at death, theirs 55%; we rebuilt 38 of 155 as paint, they 76
of 100).  A tower pattern needs all 24 tiles in the side's exact colours (RULES 6.1).  A soldier can paint over its own
wrong colour but not over enemy paint; a splash repaints own tiles with the splash colour (RULES 5.2).
Per killed tower (a 'die' row of a tower), at the end of its death round, its 24 pattern tiles by state:
  ok      own paint in the pattern's colour
  wrongc  own paint in the other colour
  empty
  enemy
and for the tiles that are not ok, who wrote them last (side + robot type + action), since the tower was built
(r0 towers: since round 0).  Lost and won games, side, tower type."""
import lib
from collections import Counter, defaultdict

PATS = {'PAINT_TOWER': lib.PAT['PAINT_TOWER'], 'MONEY_TOWER': lib.PAT['MONEY_TOWER'], 'DEFENSE_TOWER': lib.PAT['DEFENSE_TOWER']}


def analyse(G):
    b, d = lib.tower_events(G)
    kills = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    ev = sorted(x for x in d if x[1] in kills and x[3] in (1, 2))
    grid = list(G.paint0); W = G.W
    last = {}                       # tile -> (team, type, action, round)
    out = []
    i = 0

    def snap(e):
        r, tid, typ, side, x, y = e
        pat = PATS.get(typ)
        c = Counter(); who = Counter()
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if not (dx or dy): continue
                X, Y = x + dx, y + dy
                if not (0 <= X < G.W and 0 <= Y < G.H): continue
                k = X + Y * W
                v = grid[k]
                if v == 0: st = 'empty'
                elif lib.owner(v) != side: st = 'enemy'
                else:
                    sec = v in (2, 4)
                    st = 'ok' if pat is not None and sec == bool((pat >> (5 * (dx + 2) + dy + 2)) & 1) else 'wrongc'
                c[st] += 1
                if st != 'ok':
                    lw = last.get(k)
                    if lw is None: who[(st, 'initial')] += 1
                    else:
                        t, ty, act, rr = lw
                        who[(st, ('own ' if t == side else 'enemy ') + ty[:3] + ' ' + act)] += 1
        out.append((side, typ, c, who))

    for a in G.acts:
        while i < len(ev) and a[0] > ev[i][0]:
            snap(ev[i]); i += 1
        k = a[4]
        if k == 'paint':
            x, y = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
            last[x + y * W] = (a[2], a[3], 'paint', a[0])
        elif k == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
            last[x + y * W] = (a[2], a[3], 'unpaint', a[0])
    while i < len(ev):
        snap(ev[i]); i += 1
    return out


for which in ('lost', 'won'):
    agg = defaultdict(lambda: [0, Counter(), Counter(), []])
    for G in lib.games(which):
        for side, typ, c, who in analyse(G):
            key = ('us' if side == G.us else 'them', typ)
            A = agg[key]
            A[0] += 1; A[1].update(c); A[2].update(who); A[3].append(c['ok'])
        lib.lite(G)
    print(f'\n== {which} games')
    for key in sorted(agg):
        n, c, who, oks = agg[key]
        tot = sum(c.values())
        print(f'   {key[0]:4s} {key[1]:13s} killed {n}: tiles per tower ok {c["ok"] / n:.1f}, wrong colour {c["wrongc"] / n:.1f}, '
              f'empty {c["empty"] / n:.1f}, enemy {c["enemy"] / n:.1f}; ok median {lib.med(oks)}; 24 ok {sum(1 for x in oks if x >= 24)}')
        for st in ('wrongc', 'empty', 'enemy'):
            W_ = Counter({k[1]: v for k, v in who.items() if k[0] == st})
            t = sum(W_.values())
            if t:
                print(f'        {st:7s} last written by: ' + ', '.join(f'{k} {100 * v / t:.0f}%' for k, v in W_.most_common(5)))

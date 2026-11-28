"""Topic 178 (new): the paint ledger of each side's robots, per phase and unit type.  Where the paint goes once it
leaves the towers.  Per robot and round (r = the round of its turn record; end-of-turn paint p):
    p(r) = p(r-1) + W + R - S - D - pen
  W   withdrawn from own towers (transfer with a negative amount, by the robot)
  R   received from own moppers (transfer with a positive amount to the robot; a mopper's own gains from mopping enemy
      robots, +5 per drained robot, are counted here for moppers)
  S   spent: soldier 5 per tile paint or tower attack, splasher 50 per splash, mopper 0
  D   drained by enemy moppers (drain rows on the robot; mop swings 5 each, mop attacks 10)
  pen the residual: the end-of-turn ground penalty (RULES 5.3: neutral 1, enemy 2, x2 for moppers, plus 1 or 2 per
      adjacent ally), and any paint a capped transfer destroyed.  A robot's first turn starts from full paint.
Also counted per paint action, from the replayed paint grid: tiles turned ours from empty ('new') or from enemy
('flip'), and tiles repainted that were ours already ('re').  Per phase (r1-100, r101-200, r201-300, r301+), per side,
medians and means per game of the sums, and the per-100-robot-round rates.  Losses and wins; ours by version too."""
import os
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 300), (301, 2000))
PHN = ('r1-100', 'r101-200', 'r201-300', 'r301+')
UT = ('SOLDIER', 'SPLASHER', 'MOPPER')


def ph(r):
    for j, (lo, hi) in enumerate(PH):
        if lo <= r <= hi: return j
    return None


def analyse(G):
    """out[(side, phase, type)][key] = sum; side 'us'/'them'."""
    out = defaultdict(lambda: defaultdict(float))
    side = lambda team: 'us' if team == G.us else 'them'
    W = defaultdict(int); R = defaultdict(int); S = defaultdict(int); D = defaultdict(int)   # (id, round) -> paint
    for a in G.acts:
        r, i, team, typ, k = a[0], a[1], a[2], a[3], a[4]
        if k == 'transfer':
            amt = int(a[6]) if a[6] not in ('', None) else 0
            other = int(a[5])
            if amt < 0: W[(i, r)] += -amt
            elif amt > 0:
                R[(other, r)] += amt
                if typ == 'MOPPER': out[(side(team), ph(r), 'MOPPER')]['given'] += amt
        elif k == 'paint' and typ == 'SOLDIER': S[(i, r)] += 5
        elif k == 'attack' and typ == 'SOLDIER': S[(i, r)] += 5
        elif k == 'splash': S[(i, r)] += 50
        elif k == 'drain':
            tgt = int(a[5]); amt = int(a[6])
            D[(tgt, r)] += amt
            if typ == 'MOPPER' and amt == 10: R[(i, r)] += 5   # the mopper's gain from a mop attack on a robot
    # tile gains per paint action (replayed grid; hook sees the grid before each action)
    def hook(a, grid):
        if a[4] != 'paint' or a[3] not in UT: return
        x, y = map(int, a[5].split(',')); v = grid[x + y * G.W]
        o = lib.owner(v); me = 1 if a[2] == 1 else 2
        D2 = out[(side(a[2]), ph(a[0]), a[3])]
        if o == 0: D2['new'] += 1
        elif o == me: D2['re'] += 1
        else: D2['flip'] += 1
    lib.replay_grid(G, hook)
    last = {}
    for t in G.turns:
        r, i, team, typ, p = t[0], t[1], t[2], t[3], t[7]
        if typ not in UT: continue
        j = ph(r)
        D2 = out[(side(team), j, typ)]
        D2['rr'] += 1
        p0 = last.get(i, lib.CAP[typ])
        w, rc, s, d = W.get((i, r), 0), R.get((i, r), 0), S.get((i, r), 0), D.get((i, r), 0)
        pen = p0 + w + rc - s - d - p
        D2['W'] += w; D2['R'] += rc; D2['S'] += s; D2['D'] += d; D2['pen'] += pen
        D2['p'] += p
        if p < 100: D2['lt100'] += 1
        if p < 50: D2['lt50'] += 1
        if p == 0: D2['zero'] += 1
        last[i] = p
    return out


KEYS = (('rr', 'robot-rounds', None), ('p', 'mean paint held', 'rr'), ('lt100', '% of turns under 100 paint', 'rr%'),
        ('lt50', '% of turns under 50 paint', 'rr%'), ('zero', '% of turns at 0 paint', 'rr%'),
        ('W', 'withdrawn from towers', 'rate'), ('R', 'received from moppers', 'rate'), ('S', 'spent (paint + attacks)', 'rate'),
        ('D', 'drained by enemy moppers', 'rate'), ('pen', 'ground penalty (residual)', 'rate'),
        ('new', 'tiles painted from empty', 'rate'), ('flip', 'tiles flipped from enemy', 'rate'),
        ('re', 'tiles repainted (ours already)', 'rate'), ('given', 'given by moppers', 'rate'))


def report(tag, GS):
    if not GS: return
    print(f'\n== {tag}: {len(GS)} games.  Per 100 robot-rounds of that type (rates), or as marked; sums over the games, us / them')
    for typ in UT:
        print(f'  {typ}')
        print(f'     {"":36s}' + ''.join(f'{n:>20s}' for n in PHN))
        for k, name, how in KEYS:
            if k == 'given' and typ != 'MOPPER': continue
            cells = ''
            for j in range(len(PH)):
                vals = []
                for sd in ('us', 'them'):
                    tot = sum(o[(sd, j, typ)][k] for o in GS); rr = sum(o[(sd, j, typ)]['rr'] for o in GS)
                    if how is None: vals.append(f'{tot / len(GS):.0f}')
                    elif how == 'rr': vals.append(f'{tot / rr:.0f}' if rr else '-')
                    elif how == 'rr%': vals.append(f'{100 * tot / rr:.0f}' if rr else '-')
                    else: vals.append(f'{100 * tot / rr:.0f}' if rr else '-')
                cells += f'{vals[0] + " / " + vals[1]:>20s}'
            print(f'     {name:36s}' + cells)
    # team-level: robot paint flows per game (sums over unit types), means per game
    print('  all robot types, means per game (paint): withdrawn W, received R, spent S, drained D, penalty pen; spent share on tiles')
    for j in range(len(PH)):
        n = sum(1 for o in GS if any(o[(sd, j, t)]['rr'] for sd in ('us', 'them') for t in UT))
        if not n: continue
        row = []
        for sd in ('us', 'them'):
            v = {k: sum(o[(sd, j, t)][k] for o in GS for t in UT) / n for k in ('W', 'R', 'S', 'D', 'pen')}
            row.append(f'{sd}: W {v["W"]:.0f} R {v["R"]:.0f} S {v["S"]:.0f} D {v["D"]:.0f} pen {v["pen"]:.0f}')
        print(f'     {PHN[j]:9s} ({n:2d} games) ' + ' | '.join(row))


RES = {'lost': [], 'won': []}
BYV = defaultdict(list)
for G in lib.games('all'):
    o = analyse(G)
    RES['won' if not G.won_op else 'lost'].append(o)
    BYV[G.ver].append(o)
    BYV[G.ver + (':lost' if G.won_op else ':won')].append(o)
    G.turns = G.acts = None
report('lost', RES['lost'])
report('won', RES['won'])
for v in sorted(BYV):
    if ':' in v: continue
    report(f'all games of {v}', BYV[v])

"""Topic 175 (t152 with the own-soldier breaker split by where the tile lies): ruin 5x5 = the tile is within Chebyshev 2
of a ruin (tower-pattern work: workRuin / prePaint / Churn.repairPattern); other SRP 5x5 = within Chebyshev 2 of
another centre our side completes in the game (srpPaint of an overlapping SRP); other = neither.
Topic 152: the life of an SRP (new: t148 found their SRP income 3-5x ours after r200 in our losses, with active
SRPs 2.1 / 3.4 and 3.5 / 6.6 while both sides complete about as many in r101-300; what happens between completing
and paying?).  RULES 6.3: completeResourcePattern in round R registers the centre with lifetime 0; at every round
start the engine re-checks the 25 tiles: exact colours add 1, anything else (enemy paint, a mopped tile, our other
colour) deregisters it; it pays from lifetime 50.  The paint grid is replayed (lib.replay_grid) and every 'srp' row is
followed with that rule.  Check: the replayed active count against rounds.tsv's srp column (the engine's count).
Per side whose SRP it is, phase of completion (r1-100 / r101-200 / r201+), losses then wins:
  done        SRPs completed per game
  active      share that reached lifetime 50; median rounds intact of the ones that broke; broke before 50
  paid        rounds active per SRP until it broke or the game ended (each active round pays 3 x paint towers paint
              and 3 x money towers chips)
  breaker     what made the tile wrong in the round before the failed check: enemy paint by a soldier / splasher,
              an enemy mopper's mop, our own paint in the wrong colour (soldier / splasher), or our own mopper
  where       at completion: Chebyshev distance to the nearest enemy-painted tile, enemy robots within r2 20 of
              the centre, own towers within Chebyshev 4; and the round of completion
  redone      the same side completes the same centre again after a break (share of breaks)
Per game counts are means over the games of the set."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3)]
SEC = {o: lib.secondary('SRP', *o) for o in OFFS}


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def want(side, dx, dy):
    """grid value the SRP of side wants at offset (dx, dy)."""
    s = SEC[(dx, dy)]
    return (2 if s else 1) if side == 1 else (4 if s else 3)


def analyse(G, S, P, CHK):
    W, H = G.W, G.H
    live = []          # dicts: side, c, r0, life, done (broken / ended), wrong-makers this round
    tiles = defaultdict(list)   # tile index -> [srp index]
    srps = []
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    tw_ev = lib.tower_events(G)
    robots = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.BOT: robots[t[0]].append((t[2], t[4], t[5]))
    cur = [0]

    def start_of_round(r, grid):
        """The engine's updateResourcePatterns at the start of round r (grid = after every action of r-1)."""
        for k, s in enumerate(srps):
            if s['end'] is not None or s['r0'] >= r: continue
            side = s['side']; cx, cy = s['c']
            ok = all(grid[(cx + dx) + (cy + dy) * W] == want(side, dx, dy) for dx, dy in OFFS)
            if ok:
                s['life'] += 1
                if s['life'] == 50: s['active_at'] = r
            else:
                s['end'] = r
                # the rows of round r-1 that left a tile wrong (still wrong now)
                bad = set((cx + dx) + (cy + dy) * W for dx, dy in OFFS if grid[(cx + dx) + (cy + dy) * W] != want(side, dx, dy))
                why = [w for w in s['wrongs'] if w[0] == r - 1 and w[1] in bad]
                s['why'] = why[-1][2] if why else 'unknown'
            s['wrongs'] = [w for w in s['wrongs'] if w[0] >= r - 1]
        for side in (1, 2):
            n = sum(1 for s in srps if s['side'] == side and s['end'] is None and s['life'] >= 50)
            eng = int(G.rounds[r - 1]['srp' + ('A' if side == 1 else 'B')]) if r <= len(G.rounds) else None
            if eng is not None:
                CHK['rounds'] += 1
                if eng == n: CHK['match'] += 1

    own_c = {1: set(), 2: set()}
    for a in G.acts:
        if a[4] == 'srp': own_c[a[2]].add(tuple(map(int, a[5].split(','))))

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0] + 1, a[0] + 1):
                if r >= 1: start_of_round(r, grid)
            cur[0] = a[0]
        k = a[4]
        if k == 'srp':
            x, y = map(int, a[5].split(','))
            side = a[2]
            # where: nearest enemy-painted tile (Chebyshev, up to 10), enemy robots in r2 20, own towers in Chebyshev 4
            near_e = 11
            for dx in range(-10, 11):
                for dy in range(-10, 11):
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < W and 0 <= yy < H): continue
                    o = lib.owner(grid[xx + yy * W])
                    if o and o != side:
                        c = max(abs(dx), abs(dy))
                        if c < near_e: near_e = c
            er = sum(1 for (tm, xx, yy) in robots.get(a[0], ()) if tm != side and (xx - x) ** 2 + (yy - y) ** 2 <= 20)
            alive = lib.towers_alive(G, side, a[0], *tw_ev)
            ot = sum(1 for t in alive if max(abs(t[4] - x), abs(t[5] - y)) <= 4)
            prev = [s for s in srps if s['side'] == side and s['c'] == (x, y)]
            srps.append(dict(side=side, c=(x, y), r0=a[0], life=0, end=None, wrongs=[], why=None, active_at=None,
                             near_e=near_e, er=er, ot=ot, redo=bool(prev)))
            idx = len(srps) - 1
            for dx, dy in OFFS: tiles[(x + dx) + (y + dy) * W].append(idx)
        elif k in ('paint', 'unpaint'):
            x, y = map(int, a[5].split(',')); i = x + y * W
            if k == 'paint':
                sec = a[6] == '1'
                nv = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
            else:
                nv = 0
            for idx in tiles.get(i, ()):
                s = srps[idx]
                if s['end'] is not None: continue
                dx, dy = x - s['c'][0], y - s['c'][1]
                if nv != want(s['side'], dx, dy):
                    rel = 'own' if a[2] == s['side'] else 'enemy'
                    why = f'{rel} {a[3].lower()} {k}'
                    if rel == 'own' and a[3] == 'SOLDIER':
                        if any(max(abs(x - rx), abs(y - ry)) <= 2 for (rx, ry) in G.ruins): why += ' (ruin 5x5)'
                        elif any(c != s['c'] and max(abs(x - c[0]), abs(y - c[1])) <= 2 for c in own_c[s['side']]): why += ' (other SRP 5x5)'
                        else: why += ' (other)'
                    s['wrongs'].append((a[0], i, why))

    grid = lib.replay_grid(G, hook)
    for r in range(cur[0] + 1, G.end + 1): start_of_round(r, grid)   # rounds after the last action row
    P['games'] += 1
    for s in srps:
        side = 'us' if s['side'] == G.us else 'them'
        p = ph(s['r0'])
        D = S[(side, p)]
        D['n'] += 1
        end = s['end'] if s['end'] is not None else G.end + 1
        if s['active_at'] is not None:
            D['active'] += 1
            D['paid'].append(end - s['active_at'])
        if s['end'] is not None:
            D['broke'] += 1
            D['life_broken'].append(s['life'])
            if s['life'] < 50: D['broke_early'] += 1
            D['why_' + (s['why'] or 'unknown')] += 1
            later = [t for t in srps if t is not s and t['side'] == s['side'] and t['c'] == s['c'] and t['r0'] >= s['end'] - 1]
            if later: D['redone'] += 1
        D['near_e'].append(s['near_e']); D['er'].append(s['er']); D['ot'].append(s['ot']); D['r0'].append(s['r0'])
        if s['redo']: D['is_redo'] += 1


CAUSES = ('enemy soldier paint', 'enemy splasher paint', 'enemy mopper unpaint', 'own soldier paint (ruin 5x5)', 'own soldier paint (other SRP 5x5)', 'own soldier paint (other)', 'own soldier paint',
          'own splasher paint', 'own mopper unpaint', 'unknown')
CHK = defaultdict(int)
for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float))
    for key in [(s, p) for s in ('us', 'them') for p in range(3)]:
        for k in ('paid', 'life_broken', 'near_e', 'er', 'ot', 'r0'): S[key][k] = []
    P = defaultdict(int)
    for G in lib.games(which):
        analyse(G, S, P, CHK)
    ng = P['games']
    print(f'\n== {which}: {ng} games; SRPs by the side that completed them and the phase of completion')
    print(f'   {"":44s}' + ''.join(f'{PHN[p] + " us":>14s}{"them":>8s}' for p in range(3)))
    rows = [('n', 'completed per game'), ('is_redo', '  of them a centre completed before (redo)'),
            ('active', 'reached lifetime 50 (active)'), ('paid', '  median rounds active (until broken / end)'),
            ('broke', 'broke (deregistered) before the end'), ('broke_early', '  broke before 50'),
            ('life_broken', '  median rounds intact when it broke'), ('redone', '  completed again later (of breaks)')]
    rows += [('why_' + c, f'  breaker: {c}') for c in CAUSES]
    rows += [('near_e', 'at completion: Chebyshev to enemy paint (11 = none in 10)'),
             ('er', 'at completion: enemy robots within r2 20'), ('ot', 'at completion: own towers within Chebyshev 4'),
             ('r0', 'round of completion (median)')]
    for k, name in rows:
        cells = ''
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, p)]
                n = D['n']
                if k == 'n': s = f'{n / max(1, ng):.2f}'
                elif k in ('paid', 'life_broken', 'near_e', 'er', 'ot', 'r0'): s = f'{lib.med(D[k])}'
                elif k.startswith('why_'): s = f'{100 * D[k] / max(1, D["broke"]):.0f}%'
                elif k == 'redone': s = f'{100 * D[k] / max(1, D["broke"]):.0f}%'
                else: s = f'{100 * D[k] / max(1, n):.0f}%'
                cells += f'{s:>14s}' if side == 'us' else f'{s:>8s}'
        print(f'   {name:52s}'[:52] + cells)
    # per game: SRP-rounds paid (sum over SRPs of active rounds), us / them
print(f'\ncheck: replayed active SRP count = rounds.tsv srp column in {CHK["match"]} of {CHK["rounds"]} side-rounds '
      f'({100 * CHK["match"] / max(1, CHK["rounds"]):.2f}%)')

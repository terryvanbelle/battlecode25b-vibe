"""Topic 161: what breaks the pattern of a STANDING tower (follows t160: the dead tower's pattern is already broken at
its death in 39 / 55 / 88% of our losses' tower deaths, theirs 37 / 43 / 79%; and study 13 t154: a drained money
tower of ours can churn, pattern intact, in 17% of its drained turns, theirs 39%).  While the tower stands its pattern
does nothing, but it decides two things: Churn.towerTurn disintegrates a drained L1 money tower only with every tile
of its money pattern right (the churn's fresh 500 paint), and a killed tower can be completed again at once only
with its pattern intact.  RULES 4.1: an enemy soldier cannot paint over our paint, so the enemy breaks a standing
tower's pattern only by a mop (unpaint) or a splash (inner 3x3 overwrite); our own robots break it by repainting a
tile in the other colour: a splash paints every own or empty tile in its 13 tiles with the splasher's colour
(Splasher.splash: rc.attack(t), primary), a soldier's SRP work or pattern repair paints the colour its own pattern
wants.  Splasher.sense guards only SRP-lattice secondary tiles (SPL_SRP_GUARD).
Every tower that was completed in the game (not the starting towers, whose 5x5 was never painted), both sides, from
its completion to its death or the end.  The paint grid is replayed in file order.
Per side and tower type, losses then wins:
  tower-rounds          rounds standing; share of them with the pattern intact (24 right at the round end)
  breaks                paint changes that turn a right tile wrong, per 100 tower-rounds, by cause: own splash, own
                        soldier, enemy mop, enemy splash, other; and repairs (wrong -> right) by own soldier / splash
  first break           rounds from completion to the first break (median), and its cause
  splash damage         own splashes (splash rows) whose 13 tiles include a right secondary tile of a standing own
                        tower's pattern, per 100 own splashes"""
from collections import defaultdict, Counter
import lib

OFFS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if dx or dy]


def analyse(G, S, C):
    W, H = G.W, G.H
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    built, died = lib.tower_events(G)
    # live towers keyed by tile; only completed towers (build rows), not the starting ones
    born = {}
    for (r, tid, ty, team, x, y) in built:
        if r > 0 and team: born.setdefault(r, []).append((tid, ty, team, x, y))
    dead = defaultdict(list)
    for (r, tid, ty, team, x, y) in died: dead[r].append(tid)
    tiles = defaultdict(list)    # (x, y) -> [tower state dict]
    live = {}
    cur = [0]

    def right(grid, T, dx, dy):
        v = grid[(T['x'] + dx) + (T['y'] + dy) * W]
        return lib.owner(v) == T['team'] and (v in (2, 4)) == lib.secondary(T['ty'], dx, dy)

    def end_of_round(r, grid):
        for tid in dead.get(r, ()):
            T = live.pop(tid, None)
            if T:
                for dx, dy in OFFS: tiles[(T['x'] + dx, T['y'] + dy)].remove(T)
        for T in live.values():
            ok = all(right(grid, T, dx, dy) for dx, dy in OFFS)
            T['rounds'] += 1
            if ok: T['intact'] += 1
        for (tid, ty, team, x, y) in born.get(r, ()):
            if not (2 <= x < W - 2 and 2 <= y < H - 2): continue
            T = dict(tid=tid, ty=ty, team=team, x=x, y=y, r0=r, rounds=0, intact=0, first=None, br=Counter(), rep=Counter())
            live[tid] = T
            for dx, dy in OFFS: tiles[(x + dx, y + dy)].append(T)
            S['towers', 'us' if team == G.us else 'them', ty].append(T)

    def hook(a, grid):
        if a[0] != cur[0]:
            for r in range(cur[0], a[0]):
                if r >= 1: end_of_round(r, grid)
            cur[0] = a[0]
        k = a[4]
        if k == 'splash':
            x, y = map(int, a[5].split(','))
            side = 'us' if a[2] == G.us else 'them'
            C['splashes', side] += 1
            hit = False
            for ddx in range(-2, 3):
                for ddy in range(-2, 3):
                    if ddx * ddx + ddy * ddy > 4: continue
                    for T in tiles.get((x + ddx, y + ddy), ()):
                        if T['team'] != a[2]: continue
                        dx, dy = x + ddx - T['x'], y + ddy - T['y']
                        if lib.secondary(T['ty'], dx, dy) and right(grid, T, dx, dy): hit = True
            if hit: C['splash_hits', side] += 1
        if k not in ('paint', 'unpaint'): return
        x, y = map(int, a[5].split(','))
        for T in tiles.get((x, y), ()):
            dx, dy = x - T['x'], y - T['y']
            was = right(grid, T, dx, dy)
            own = a[2] == T['team']
            if k == 'unpaint':
                now = False
                cause = 'own mop' if own else 'enemy mop'
            else:
                sec = a[6] == '1'
                # the tile after the row: own colour if the actor is the tower's team; an enemy can only overwrite by splash
                now = own and sec == lib.secondary(T['ty'], dx, dy)
                cause = ('own ' if own else 'enemy ') + ('splash' if a[3] == 'SPLASHER' else a[3].lower())
            if was and not now:
                T['br'][cause] += 1
                if T['first'] is None: T['first'] = (a[0] - T['r0'], cause)
            elif not was and now:
                T['rep'][cause] += 1

    grid = lib.replay_grid(G, hook)
    for r in range(cur[0], G.end + 1): end_of_round(r, grid)


CAUSES = ('own splash', 'own soldier', 'enemy mop', 'enemy splash', 'own mop', 'enemy soldier', 'own mopper')
for which in ('lost', 'won'):
    S = defaultdict(list)
    cnt = Counter()
    ng = 0
    for G in lib.games(which):
        ng += 1
        analyse(G, S, cnt)
    print(f'\n== {which}: {ng} games; towers completed in the game (starting towers left out)')
    for side in ('us', 'them'):
        for ty in ('MONEY_TOWER', 'PAINT_TOWER', 'DEFENSE_TOWER'):
            Ts = S.get(('towers', side, ty), [])
            if not Ts: continue
            rounds = sum(T['rounds'] for T in Ts); intact = sum(T['intact'] for T in Ts)
            br = Counter(); rep = Counter()
            for T in Ts: br.update(T['br']); rep.update(T['rep'])
            k = 100 / max(1, rounds)
            firsts = [T['first'] for T in Ts if T['first']]
            fc = Counter(f[1] for f in firsts)
            print(f'  {side:4s} {ty.lower():13s} {len(Ts):4d} towers, {rounds:6d} tower-rounds, intact {100 * intact / max(1, rounds):3.0f}% of them')
            print(f'       breaks per 100 tower-rounds {sum(br.values()) * k:5.2f}: ' + ', '.join(f'{c} {br[c] * k:.2f}' for c in CAUSES if br[c]))
            print(f'       repairs per 100 tower-rounds {sum(rep.values()) * k:5.2f}: ' + ', '.join(f'{c} {rep[c] * k:.2f}' for c in rep))
            print(f'       first break: {100 * len(firsts) / len(Ts):.0f}% of towers, median {lib.med([f[0] for f in firsts])} rounds after completion; cause '
                  + ', '.join(f'{c} {100 * v / max(1, len(firsts)):.0f}%' for c, v in fc.most_common()))
    for side in ('us', 'them'):
        print(f'  {side}: splashes {cnt[("splashes", side)] / ng:.1f} a game; {100 * cnt[("splash_hits", side)] / max(1, cnt[("splashes", side)]):.1f}% '
              f'of them cover a right secondary tile of a standing own tower\'s pattern')

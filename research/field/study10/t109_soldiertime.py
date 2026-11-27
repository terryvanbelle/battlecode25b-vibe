"""Topic 109: what soldiers spend their turns on, both sides, lost vs won games, by phase (r1-100, r101-200, r201-400).
Each soldier-turn gets the first matching label from its actions that round (actions.tsv, same robot and round):
  build      completed a tower                      srp-done   completed an SRP
  mark       marked a tower pattern (mark rows on a ruin's 5x5)
  ruin       painted a tile of a free ruin's 5x5 (no tower of the painter's side on it that round)
  repair     painted a tile of the 5x5 of one of the side's own standing towers (our churn repair, their upkeep)
  srp        painted a tile of a 5x5 where the same side completed an SRP at some point in the game
  siege      attacked an enemy tower                refill     withdrew paint from a tower
  cover      any other paint                        none       no action (moving or waiting)
plus 'at 0 paint' (the turn ended with 0 paint) and the soldiers' mean paint.  Shares of soldier-turns, then the
same counts per game (medians)."""
import lib
from collections import defaultdict, Counter

PH = ((1, 100, 'r1-100'), (101, 200, 'r101-200'), (201, 400, 'r201-400'))
LABS = ('build', 'srp-done', 'mark', 'ruin', 'repair', 'srp', 'siege', 'refill', 'cover', 'none')


def per_game(G):
    b, d = lib.tower_events(G)
    # tower standing per (ruin) and round: intervals per side
    iv = defaultdict(list)   # pos -> [(side, from, to)]
    died = {x[1]: x[0] for x in d}
    for x in b:
        iv[(x[4], x[5])].append((x[3], x[0], died.get(x[1], 10 ** 6)))
    ruin_of = {}
    for (rx, ry) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                ruin_of.setdefault((rx + dx, ry + dy), (rx, ry))
    srp_tiles = {1: set(), 2: set()}
    for a in G.acts:
        if a[4] == 'srp':
            cx, cy = map(int, a[5].split(','))
            for dx in range(-2, 3):
                for dy in range(-2, 3): srp_tiles[a[2]].add((cx + dx, cy + dy))
    tower_ids = set(x[1] for x in b)
    acts = defaultdict(list)
    for a in G.acts:
        if a[3] == 'SOLDIER': acts[(a[0], a[1])].append(a)
    out = {s: {p[2]: Counter() for p in PH} for s in (1, 2)}
    paint_sum = {s: {p[2]: [0, 0] for p in PH} for s in (1, 2)}

    def standing(pos, side, r):
        for (s, f, t) in iv.get(pos, ()):
            if s == side and f <= r < t: return True
        return False

    for t in G.turns:
        if t[3] != 'SOLDIER': continue
        r, rid, side = t[0], t[1], t[2]
        ph = next((p[2] for p in PH if p[0] <= r <= p[1]), None)
        if ph is None: continue
        lab = 'none'
        A = acts.get((r, rid), ())
        kinds = [a[4] for a in A]
        if 'build' in kinds: lab = 'build'
        elif 'srp' in kinds: lab = 'srp-done'
        else:
            marks = [a for a in A if a[4] == 'mark']
            paints = [a for a in A if a[4] == 'paint']
            att = [a for a in A if a[4] == 'attack' and a[5].isdigit() and int(a[5]) in tower_ids]
            tr = [a for a in A if a[4] == 'transfer' and a[6].lstrip('-').isdigit() and int(a[6]) < 0]
            if marks and any(tuple(map(int, m[5].split(','))) in ruin_of for m in marks): lab = 'mark'
            elif paints:
                p = tuple(map(int, paints[0][5].split(',')))
                ru = ruin_of.get(p)
                if ru is not None and ru != p:
                    lab = 'repair' if standing(ru, side, r) else 'ruin'
                elif p in srp_tiles[side]: lab = 'srp'
                else: lab = 'cover'
            elif att: lab = 'siege'
            elif tr: lab = 'refill'
        out[side][ph][lab] += 1
        out[side][ph]['_turns'] += 1
        if t[7] == 0: out[side][ph]['_zero'] += 1
        paint_sum[side][ph][0] += t[7]; paint_sum[side][ph][1] += 1
    return out, paint_sum


def run(name, gs):
    tot = {k: {p[2]: Counter() for p in PH} for k in ('us', 'them')}
    psum = {k: {p[2]: [0, 0] for p in PH} for k in ('us', 'them')}
    pg = {k: {p[2]: defaultdict(list) for p in PH} for k in ('us', 'them')}
    n = 0
    for G in gs:
        n += 1
        o, ps = per_game(G)
        for k, s in (('us', G.us), ('them', G.op)):
            for p in PH:
                tot[k][p[2]].update(o[s][p[2]])
                psum[k][p[2]][0] += ps[s][p[2]][0]; psum[k][p[2]][1] += ps[s][p[2]][1]
                T = o[s][p[2]]['_turns']
                if T >= 50:
                    for lab in LABS: pg[k][p[2]][lab].append(100 * o[s][p[2]][lab] / T)
    print(f'\n== {name}: {n} games; share of soldier-turns % (all turns pooled), us | them')
    print('   ' + f'{"":10s}' + ''.join(f'{p[2]:>22s}' for p in PH))
    for lab in LABS + ('_zero',):
        cells = []
        for p in PH:
            a = tot['us'][p[2]]; b = tot['them'][p[2]]
            cells.append(f'{100 * a[lab] / max(1, a["_turns"]):6.1f} | {100 * b[lab] / max(1, b["_turns"]):6.1f}')
        print(f'   {("at 0 paint" if lab == "_zero" else lab):10s}' + ''.join(f'{c:>22s}' for c in cells))
    print(f'   {"turns":10s}' + ''.join(f'{str(tot["us"][p[2]]["_turns"]) + " | " + str(tot["them"][p[2]]["_turns"]):>22s}' for p in PH))
    print(f'   {"mean paint":10s}' + ''.join(f'{psum["us"][p[2]][0] / max(1, psum["us"][p[2]][1]):8.0f} | {psum["them"][p[2]][0] / max(1, psum["them"][p[2]][1]):<8.0f}    ' for p in PH))
    print('   per-game medians of the shares (games with >= 50 soldier-turns in the phase), us | them:')
    for lab in ('ruin', 'srp', 'srp-done', 'siege', 'cover', 'none'):
        print(f'   {lab:10s}' + ''.join(f'{str(lib.med(pg["us"][p[2]][lab])) + " | " + str(lib.med(pg["them"][p[2]][lab])):>22s}' for p in PH))


run('LOST games', lib.games('lost'))
run('LOST games to the top teams', lib.games('lost', teams=lib.TOP))
run('WON games', lib.games('won'))

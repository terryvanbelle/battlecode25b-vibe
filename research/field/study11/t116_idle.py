"""Topic 116: soldier turns with no action at all (t109's 'none'), both sides, lost vs won games, r101-200 and r201-400.
A soldier-turn with no row in actions.tsv for that robot and round.  Split by:
  moved      the soldier stands on another tile than at its previous turn (walking) or the same tile (waiting)
  paint      the soldier's paint at the end of the turn: 0, 1-49, 50-99, 100+
  tower      within d2 <= 8 of a standing tower of its side (refill area) / not
  ground     the tile it stands on (grid at the end of the previous round): own paint, empty, enemy paint
Shares of all soldier-turns of the side in the phase, plus the 'walking with 100+ paint over own paint, away from
towers' share (a soldier with paint and nothing to do), and the 'waiting beside a tower with < 50 paint' share."""
import lib
from collections import Counter, defaultdict

PH = ((101, 200, 'r101-200'), (201, 400, 'r201-400'))


def pb(p):
    return '0' if p == 0 else ('1-49' if p < 50 else ('50-99' if p < 100 else '100+'))


def analyse(G):
    b, d = lib.tower_events(G)
    died = {x[1]: x[0] for x in d}
    tw = [(x[3], x[0], died.get(x[1], 10 ** 6), (x[4], x[5])) for x in b]
    acted = set((a[0], a[1]) for a in G.acts if a[3] == 'SOLDIER')
    acts_by_round = defaultdict(list)
    for a in G.acts:
        if a[4] in ('paint', 'unpaint'): acts_by_round[a[0]].append(a)
    bt = lib.by_round_turns(G)
    grid = list(G.paint0); W = G.W
    last = {}
    C = {1: defaultdict(Counter), 2: defaultdict(Counter)}
    hi = min(G.end, 400)
    for r in range(1, hi + 1):
        ph = next((p[2] for p in PH if p[0] <= r <= p[1]), None)
        if ph:
            stand = {s: [t[3] for t in tw if t[0] == s and t[1] <= r < t[2]] for s in (1, 2)}
            for t in bt.get(r, ()):
                if t[3] != 'SOLDIER': continue
                s = t[2]; c = C[s][ph]
                c['turns'] += 1
                if (r, t[1]) in acted: last[t[1]] = (t[4], t[5]); continue
                c['none'] += 1
                moved = last.get(t[1]) != (t[4], t[5])
                last[t[1]] = (t[4], t[5])
                p = pb(t[7])
                near = any(lib.d2((t[4], t[5]), q) <= 8 for q in stand[s])
                v = grid[t[4] + t[5] * W]
                gr = 'empty' if v == 0 else ('own' if lib.owner(v) == s else 'enemy')
                c['moved' if moved else 'waited'] += 1
                c['paint ' + p] += 1
                c['near tower' if near else 'away'] += 1
                c['on ' + gr] += 1
                if moved and p == '100+' and gr == 'own' and not near: c['walking, 100+ paint, own ground, away from towers'] += 1
                if not moved and near and t[7] < 50: c['waiting beside a tower, < 50 paint'] += 1
                if not moved and not near and t[7] == 0: c['stuck at 0 paint away from towers'] += 1
        else:
            for t in bt.get(r, ()):
                if t[3] == 'SOLDIER': last[t[1]] = (t[4], t[5])
        for a in acts_by_round.get(r, ()):
            x, y = map(int, a[5].split(','))
            if a[4] == 'paint':
                sec = a[6] == '1'; grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
            else: grid[x + y * W] = 0
    return C


KEYS = ('none', 'moved', 'waited', 'paint 0', 'paint 1-49', 'paint 50-99', 'paint 100+', 'near tower', 'away', 'on own', 'on empty',
        'on enemy', 'walking, 100+ paint, own ground, away from towers', 'waiting beside a tower, < 50 paint', 'stuck at 0 paint away from towers')
for which in ('lost', 'won'):
    T = {'us': defaultdict(Counter), 'them': defaultdict(Counter)}; n = 0
    for G in lib.games(which):
        C = analyse(G); n += 1
        for k, s in (('us', G.us), ('them', G.op)):
            for ph, c in C[s].items(): T[k][ph].update(c)
        lib.lite(G)
    print(f'\n== {which.upper()} games: {n}; shares of all soldier-turns in the phase, us / them')
    print('   ' + ' ' * 52 + ''.join(f'{p[2]:>22s}' for p in PH))
    for k in KEYS:
        row = ''
        for p in PH:
            u = T['us'][p[2]]; t = T['them'][p[2]]
            row += f'{100 * u[k] / max(1, u["turns"]):9.1f}% /{100 * t[k] / max(1, t["turns"]):6.1f}%  '
        print(f'   {k:52s}{row}')
    print('   soldier-turns: ' + ', '.join(f'{p[2]} us {T["us"][p[2]]["turns"]} them {T["them"][p[2]]["turns"]}' for p in PH))

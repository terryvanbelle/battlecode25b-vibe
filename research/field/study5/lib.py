"""Study 5 loader (copy of study 4 lib, new dumps; games() yields only our LOSSES by default): one game of a ReplayDump tsv dump, seen from the ENEMY (top team) side.
Replays only.  Usage from the topic scripts:  for G in games(): ...  (G.op = top team side 1/2, G.us = ours).
Dump dirs: S1/m<id> and S2/m<id> (see REPORT.md for rebuilding them)."""
import csv, json, os, pickle, ast
from collections import defaultdict

SP = '/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad'
# ranked matches vs the strong teams from id 2120 on (t36..t47 era); UNRANKED is a supplementary set
RANKED = (2120, 2150, 2169, 2176, 2178, 2254, 2256, 2292, 2298)
UNRANKED = (2177, 2179, 2255, 2293)
DUMPS = {m: f'{SP}/study5/dump/m{m}' for m in RANKED + UNRANKED}
CACHE = f'{SP}/study5/cache'
STRONG = ('placeholder-name-2', 'geesegeesego', 'lobster-roll', 'varunvejalla', 'angtn', 'podemice')
US = 'vibe25b'
TOW = ('PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER')
BOT = ('SOLDIER', 'SPLASHER', 'MOPPER')
COST = {'SOLDIER': (200, 250), 'SPLASHER': (300, 400), 'MOPPER': (100, 300)}  # (paint, chips)
CAP = {'SOLDIER': 200, 'SPLASHER': 300, 'MOPPER': 100}
PAT = {'PAINT_TOWER': 18157905, 'MONEY_TOWER': 15583086, 'DEFENSE_TOWER': 4685252, 'SRP': 28873275}


def secondary(pat, dx, dy):
    """True if the pattern wants the secondary colour at offset (dx, dy) from the centre."""
    return bool((PAT[pat] >> (5 * (dx + 2) + dy + 2)) & 1)


def rd(p):
    with open(p) as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); return [dict(zip(h, x)) for x in r]


class Game:
    pass


def load(m, g):
    cp = f'{CACHE}/m{m}g{g}.pkl'
    if os.path.exists(cp):
        return pickle.load(open(cp, 'rb'))
    d = DUMPS[m]
    if not os.path.exists(f'{d}/g{g}.summary.json'):
        return None
    G = Game()
    G.m, G.g = m, g
    sm = json.load(open(f'{d}/g{g}.summary.json')); meta = json.load(open(f'{d}/g{g}.meta.json'))
    G.sm, G.map, G.W, G.H = sm, meta['map'], meta['width'], meta['height']
    G.us = 1 if sm['teamA'] == US else 2
    G.op = 3 - G.us
    G.team_name = sm['teamB'] if G.us == 1 else sm['teamA']
    G.won_op = sm['winner'] == ('A' if G.op == 1 else 'B')
    G.wintype, G.end = sm['winType'], sm['rounds']
    G.walls = set(i for i, c in enumerate(meta['walls']) if c == '1')
    G.paint0 = [int(c) for c in meta['paint']]
    G.ruins = [tuple(r) for r in meta['ruins']]
    G.rounds = rd(f'{d}/g{g}.rounds.tsv')
    acts = rd(f'{d}/g{g}.actions.tsv')
    G.acts = [(int(a['round']), int(a['id']), int(a['team']), a['type'], a['action'], a['a'], a['b'], a['c']) for a in acts]
    turns = rd(f'{d}/g{g}.turns.tsv')
    G.turns = [(int(t['round']), int(t['id']), int(t['team']), t['type'], int(t['x']), int(t['y']), int(t['hp']), int(t['paint']))
               for t in turns]
    G.team, G.typ = {}, {}
    try:
        for b in ast.literal_eval(meta['bodies']):
            G.team[b['id']] = b['team']; G.typ[b['id']] = b['type']
    except Exception:
        pass
    for t in G.turns:
        G.team[t[1]] = t[2]; G.typ[t[1]] = t[3]
    for a in G.acts:
        if a[4] == 'spawn':
            G.team[int(a[5])] = a[2]; G.typ[int(a[5])] = a[6]
    pickle.dump(G, open(cp, 'wb'))
    return G


def games(which='lost', matches=RANKED):
    """which: 'lost' (default: games the top team won), 'won' (games we won), 'all'."""
    import os as _o
    sel = _o.environ.get('S5SET')
    if sel == 'all': matches = RANKED + UNRANKED
    elif sel == 'unranked': matches = UNRANKED
    for m in matches:
        for g in range(3):
            G = load(m, g)
            if G is None or G.team_name not in STRONG: continue
            if which == 'lost' and not G.won_op: continue
            if which == 'won' and G.won_op: continue
            yield G


def money(G, side, r):
    """Chips of side at the end of round r (r >= 1); r = 0 -> 2500."""
    if r < 1: return 2500
    row = G.rounds[min(r, len(G.rounds)) - 1]
    return int(row['money' + ('A' if side == 1 else 'B')])


def by_round_turns(G):
    """dict round -> list of turn tuples in order."""
    out = defaultdict(list)
    for t in G.turns: out[t[0]].append(t)
    return out


def replay_grid(G, hook=None):
    """Replays paint/unpaint actions in file order.  grid[i] in 0..4 (1/2 = team A, 3/4 = team B).
    hook(action_tuple, grid) is called BEFORE each action is applied.  Returns the final grid."""
    grid = list(G.paint0); W = G.W
    for a in G.acts:
        if hook: hook(a, grid)
        k = a[4]
        if k == 'paint':
            x, y = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        elif k == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
    return grid


def owner(v):
    return 0 if v == 0 else (1 if v <= 2 else 2)


def tower_events(G):
    """Lists of (round, tower_id, type, team, x, y) for builds and deaths (incl. starting towers as builds at r0)."""
    built, died = [], []
    pos = {}
    for t in G.turns:
        if t[3] in TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    first = {}
    for t in G.turns:
        if t[3] in TOW and t[1] not in first: first[t[1]] = t[0]
    bset = set()
    for a in G.acts:
        if a[4] == 'build':
            tid = int(a[5]); bset.add(tid)
            built.append((a[0], tid, G.typ.get(tid, a[6]), G.team.get(tid), *pos.get(tid, (-1, -1))))
        elif a[4] == 'die' and a[7] in TOW:
            tid = int(a[5]); died.append((a[0], tid, a[7], G.team.get(tid), *pos.get(tid, (-1, -1))))
    for tid, r in first.items():
        if tid not in bset and r <= 1:
            built.append((0, tid, G.typ[tid], G.team[tid], *pos[tid]))
    # towers that vanish without a die action (disintegrate / round-level death): last turn round + 1
    last = {}
    for t in G.turns:
        if t[3] in TOW: last[t[1]] = t[0]
    dset = set(x[1] for x in died)
    for tid, r in last.items():
        if tid not in dset and r < G.end:
            died.append((r + 1, tid, G.typ[tid], G.team[tid], *pos[tid]))
    built.sort(); died.sort()
    return built, died


def towers_alive(G, side, r, built=None, died=None):
    if built is None: built, died = tower_events(G)
    dead = set(t[1] for t in died if t[0] <= r)
    return [t for t in built if t[3] == side and t[0] <= r and t[1] not in dead]


def med(x):
    x = sorted(v for v in x if v is not None)
    if not x: return '-'
    n = len(x); v = x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2
    return round(v, 1)


def pct(x, q):
    x = sorted(v for v in x if v is not None)
    if not x: return '-'
    return round(x[min(len(x) - 1, int(q * len(x)))], 1)


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

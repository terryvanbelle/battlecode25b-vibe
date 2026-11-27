"""Study 11 loader (study 10's lib, new dumps).  One game of a ReplayDump tsv dump, seen from the ENEMY side.
Replays only.  Usage:  for G in games(): ...  (G.op = their side 1/2, G.us = ours, G.ver = our package in that replay
(t122 here; t111 / t118 in study 10's set), read from the replay header by pkgs.py), G.team_name = the opponent,
G.ranked).
games() yields our LOSSES by default, from the main set: every t122 match fetched (submission 76), ids 4661-5012.
The caller listed 32 of them (4692-5012, LISTED); 4661, 4662, 4663, 4664 and 4682 are t122 too (pkgs.txt) and were in
no study, so they are in the main set as well (S11SET=listed leaves them out).
Env filters (S11* names; the S10* / S9* / S8* names of the older scripts are accepted too):
  S11VER=t122,t118   our versions (default: all)
  S11TEAMS=a,b       opponents (S11TEAMS=top: the eight top teams of study 10)
  S11RANKED=1        ranked matches only
  S11SET=main|listed|prev|all   prev = study 10's main set (3999-4602: t111, t118), dumps in study10/dump
  S11DUP=1           keep games that repeat an earlier game exactly (skipped by default; see DUP)
Dumps: SP/study11/dump/m<id> (main) and SP/study10/dump/m<id> (prev); see REPORT.md for rebuilding them.
Pickle cache: SP/study11/cache (main) and SP/study10/cache (prev)."""
import csv, json, os, pickle, ast, sys
from collections import defaultdict

SP = '/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad'
# our package per match, from the replay headers (pkgs.py, pkgs.txt)
_V = {'t122': (4661, 4662, 4663, 4664, 4682, 4692, 4699, 4716, 4725, 4726, 4765, 4766, 4787, 4800, 4805, 4806, 4841,
               4842, 4878, 4879, 4880, 4881, 4916, 4917, 4918, 4919, 4920, 4921, 4954, 4955, 4956, 4957, 4981, 4992,
               4993, 5010, 5012)}
LISTED = (4692, 4699, 4716, 4725, 4726, 4765, 4766, 4787, 4800, 4805, 4806, 4841, 4842, 4878, 4879, 4880, 4881, 4916,
          4917, 4918, 4919, 4920, 4921, 4954, 4955, 4956, 4957, 4981, 4992, 4993, 5010, 5012)
# study 10's set (prev): t111 = submission 74, t118 = submission 75
_P = {'t111': (3999, 4001, 4002, 4003, 4004, 4005, 4006, 4055, 4056, 4057, 4058, 4099, 4127, 4150, 4151, 4152, 4153,
               4154, 4155, 4160, 4222, 4223, 4224, 4225, 4226, 4227, 4250, 4251, 4286, 4287, 4288, 4289, 4309, 4325,
               4331, 4366, 4367, 4368, 4369, 4370, 4371, 4393),
      't118': (4440, 4441, 4442, 4443, 4448, 4471, 4515, 4516, 4517, 4518, 4519, 4520, 4523, 4542, 4569, 4579, 4594,
               4602)}
VER = {}
for _k, _ms in list(_V.items()) + list(_P.items()):
    for _m in _ms: VER[_m] = _k
MAIN = tuple(m for m in VER if m > 4602)
PREV = tuple(m for m in VER if 3999 <= m <= 4602)
UNRANKED = (4662, 4664, 4726, 4766, 4806, 4842, 4879, 4881, 4917, 4919, 4921, 4955, 4957, 4993,
            4002, 4004, 4006, 4056, 4058, 4151, 4153, 4155, 4223, 4225, 4227, 4251, 4287, 4289, 4367, 4369, 4371,
            4441, 4443, 4516, 4518, 4520)
DUMPS = {m: (f'{SP}/study10/dump/m{m}' if m in PREV else f'{SP}/study11/dump/m{m}') for m in VER}
# exact repeats of an earlier game (same map, opponent, rounds, coverage each side, result and spawn counts): the engine
# is deterministic, so the replica replays some pairings.  Kept: the first occurrence.  Study 10's five stay out of its
# set; study 11's are found by t126_dups.py (t126.txt).  Skipped unless S11DUP=1.
DUP = {(4152, 0), (4288, 2), (4309, 0), (4325, 0), (4325, 1)}
DUP |= {(4842, 2), (4955, 0), (5012, 1)}   # study 11 (t126.txt): m4842g2 = m4682g2 (walalilongla), m4955g0 = m4841g0 (Crab), m5012g1 = m4726g1 (Jail)
CACHE = f'{SP}/study11/cache'
CACHE_PREV = f'{SP}/study10/cache'
STRONG = None   # every opponent in the set (lib.games(teams=...) or S11TEAMS narrows it)
# the teams the study was asked about (study 9's six + confused and just-woke-up, new on our schedule)
TOP = ('spaark', 'subscribe-to-caterpillow', 'gone-whalin', 'immutable', 'scienceqiu', 'om-nom', 'confused', 'just-woke-up')
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
    cdir = CACHE_PREV if m in PREV else CACHE
    os.makedirs(cdir, exist_ok=True)
    cp = f'{cdir}/m{m}g{g}.pkl'
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
    G.ruins = [tuple(r) for r in (meta['ruins'] if isinstance(meta['ruins'], list) else ast.literal_eval(meta['ruins']))]
    G.rounds = rd(f'{d}/g{g}.rounds.tsv')
    # streamed, with shared strings: the big games (1900 rounds, 700k turns) would not fit in memory otherwise
    I = sys.intern
    with open(f'{d}/g{g}.actions.tsv') as f:
        r = csv.reader(f, delimiter='\t'); h = next(r)
        ix = [h.index(k) for k in ('round', 'id', 'team', 'type', 'action', 'a', 'b', 'c')]
        G.acts = [(int(a[ix[0]]), int(a[ix[1]]), int(a[ix[2]]), I(a[ix[3]]), I(a[ix[4]]), I(a[ix[5]]), I(a[ix[6]]), I(a[ix[7]]))
                  for a in r]
    with open(f'{d}/g{g}.turns.tsv') as f:
        r = csv.reader(f, delimiter='\t'); h = next(r)
        ix = [h.index(k) for k in ('round', 'id', 'team', 'type', 'x', 'y', 'hp', 'paint')]
        G.turns = [(int(t[ix[0]]), int(t[ix[1]]), int(t[ix[2]]), I(t[ix[3]]), int(t[ix[4]]), int(t[ix[5]]), int(t[ix[6]]), int(t[ix[7]]))
                   for t in r]
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
    G.ver = VER[m]
    G.ranked = m not in UNRANKED
    pickle.dump(G, open(cp, 'wb'))
    return G


def lite(G):
    """Drop the per-turn and per-action lists (scripts that keep every game in a list need only rounds.tsv)."""
    G.turns = G.acts = None
    return G


def _env(k):
    return os.environ.get('S11' + k) or os.environ.get('S10' + k) or os.environ.get('S9' + k) or os.environ.get('S8' + k)


def games(which='lost', matches=None, teams=STRONG, vers=None, ranked=None):
    """which: 'lost' (default: games the opponent won), 'won' (games we won), 'all'.
    Env: S11VER=t122,... (our versions), S11TEAMS=a,b|top (opponents), S11RANKED=1, S11SET=main|listed|prev|all,
    S11DUP=1."""
    if matches is None:
        s = _env('SET') or 'main'
        matches = MAIN if s == 'main' else LISTED if s == 'listed' else PREV if s == 'prev' else MAIN + PREV
    if _env('VER'): vers = _env('VER').split(',')
    if _env('TEAMS'): teams = TOP if _env('TEAMS') == 'top' else tuple(_env('TEAMS').split(','))
    if _env('RANKED'): ranked = True
    for m in sorted(matches):
        if vers and VER[m] not in vers: continue
        if ranked and m in UNRANKED: continue
        for g in range(3):
            if (m, g) in DUP and not _env('DUP'): continue
            G = load(m, g)
            if G is None: continue
            if teams and G.team_name not in teams: continue
            if which == 'lost' and not G.won_op: continue
            if which == 'won' and G.won_op: continue
            yield G


def small(G):
    return min(G.W, G.H) <= 25 or G.sm['paintable'] <= 600


def cls(G):
    return 'small' if small(G) else ('medium' if min(G.W, G.H) <= 35 else 'large')


def money(G, side, r):
    """Chips of side at the end of round r (r >= 1); r = 0 -> 2500."""
    if r < 1: return 2500
    row = G.rounds[min(r, len(G.rounds)) - 1]
    return int(row['money' + ('A' if side == 1 else 'B')])


def rv(G, side, r, k):
    """A rounds.tsv value of side at the end of round r (clamped to the last round).  k: a column stem
    ('cov', 'money', 'paint', 'srp', 'sol', 'spl', 'mop', 'pt', 'mt', 'dt') or 'tow' / 'units' / 'covpct'."""
    R = G.rounds[min(r, len(G.rounds)) - 1]; s = 'A' if side == 1 else 'B'
    if k == 'tow': return sum(int(R[x + s]) for x in ('pt', 'mt', 'dt'))
    if k == 'units': return sum(int(R[x + s]) for x in ('sol', 'spl', 'mop'))
    if k == 'covpct': return round(100 * int(R['cov' + s]) / G.sm['paintable'], 1)
    return int(R[k + s])


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


def mean(x):
    x = [v for v in x if v is not None]
    return round(sum(x) / len(x), 2) if x else '-'


def pct(x, q):
    x = sorted(v for v in x if v is not None)
    if not x: return '-'
    return round(x[min(len(x) - 1, int(q * len(x)))], 1)


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

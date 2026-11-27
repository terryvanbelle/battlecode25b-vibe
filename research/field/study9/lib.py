"""Study 9 loader (study 8's lib, new dumps).  One game of a ReplayDump tsv dump, seen from the ENEMY side.
Replays only.  Usage:  for G in games(): ...  (G.op = their side 1/2, G.us = ours, G.ver = our package in that replay
(t91 / y195 / y197 / y211 / y221, read from the replay header by pkgs.py), G.team_name = the opponent, G.ranked).
games() yields our LOSSES by default, from the main set (every match after study 8's last, 3201: ids 3211-3951).
3211-3214 were still t91 (submission 69) but came after study 8's set; y195 = submission 70, y197 = 71, y211 = 72,
y221 = 73.  t111 (submission 74) has no fetched games yet.
Env filters (S9* names; the S8* names of study 8's scripts are accepted too):
  S9VER=y211,y221    our versions (default: all)
  S9TEAMS=a,b        opponents (S9TEAMS=top: the five teams above us the study was asked about + om-nom)
  S9RANKED=1         ranked matches only
  S9SET=main|prev|all   prev = study 8's main set (2873-3201: t74, y170, t85, t91), dumps in study8/dump
  S9DUP=1            keep games that repeat an earlier game exactly (skipped by default; see DUP)
Dumps: SP/study9/dump/m<id> (main) and SP/study8/dump/m<id> (prev); see REPORT.md for rebuilding them.
Pickle cache: SP/study9/cache (main) and SP/study8/cache (prev)."""
import csv, json, os, pickle, ast, sys
from collections import defaultdict

SP = '/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad'
# our package per match, from the replay headers (pkgs.py)
_V = {'t91': (3211, 3212, 3213, 3214),
      'y195': (3289, 3294, 3304, 3305, 3306, 3307, 3312, 3323, 3324),
      'y197': (3340, 3347, 3400, 3409, 3410, 3426, 3449, 3450, 3467),
      'y211': (3479, 3512, 3513, 3514, 3515, 3544, 3545, 3546, 3547, 3548, 3549, 3575, 3583, 3584, 3632, 3655, 3659,
               3684, 3698, 3702, 3721, 3735, 3742),
      'y221': (3771, 3772, 3773, 3774, 3785, 3789, 3790, 3829, 3830, 3899, 3914, 3931, 3943, 3944, 3945, 3946, 3947,
               3948, 3951)}
# study 8's set (prev): t74 = submission 66, y170 = 67, t85 = 68, t91 = 69
_P = {'t74': (2873, 2888, 2897, 2919, 2920, 2921, 2922),
      'y170': (2969, 2970, 2971, 2972, 2973, 2974, 2979, 2990, 2998, 3004, 3006),
      't85': (3067, 3080, 3103, 3111, 3127),
      't91': (3185, 3186, 3187, 3188, 3189, 3190, 3195, 3201)}
VER = {}
for _k, _ms in list(_V.items()) + list(_P.items()):
    for _m in _ms: VER[_m] = _k
MAIN = tuple(m for m in VER if m > 3201)
PREV = tuple(m for m in VER if 2873 <= m <= 3201)
UNRANKED = (3212, 3214, 3305, 3307, 3410, 3450, 3513, 3515, 3545, 3547, 3549, 3584, 3772, 3774, 3944, 3946, 3948,
            2920, 2922, 2970, 2972, 2974, 3186, 3188, 3190)
DUMPS = {m: (f'{SP}/study8/dump/m{m}' if m in PREV else f'{SP}/study9/dump/m{m}') for m in VER}
# exact repeats of an earlier game (same map, opponent, rounds, coverage each side, result and spawn counts; sides
# swapped or our version changed in between): the engine is deterministic, so the replica replays some pairings.
# Kept: the first occurrence.  m3546g0 = m3514g1 (Restart, placeholder-name-2), m3547g1 = m3449g0 (Portal, angtn,
# y211 = y197), m3632g2 = m3347g2 (shell, angtn), m3659g2 = m3467g1 (Money, lobster-roll, y211 = y197), m3721g0 =
# m3512g1 (Gears, angtn), m3830g1 = m3789g1 (TargetPractice, gone-whalin), m3931g0 = m3899g1 (Filter,
# subscribe-to-caterpillow); m3189g1 = m3067g0 (study 8).  Skipped unless S9DUP=1.
DUP = {(3546, 0), (3547, 1), (3632, 2), (3659, 2), (3721, 0), (3830, 1), (3931, 0), (3189, 1)}
CACHE = f'{SP}/study9/cache'
CACHE_PREV = f'{SP}/study8/cache'
STRONG = None   # every opponent in the set (lib.games(teams=...) or S9TEAMS narrows it)
# the teams above us on the replica ladder the study was asked about (ranks 1-7), plus om-nom (0-3 in 3213)
TOP = ('subscribe-to-caterpillow', 'gone-whalin', 'immutable', 'spaark', 'scienceqiu', 'om-nom')
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
    return os.environ.get('S9' + k) or os.environ.get('S8' + k)


def games(which='lost', matches=None, teams=STRONG, vers=None, ranked=None):
    """which: 'lost' (default: games the opponent won), 'won' (games we won), 'all'.
    Env: S9VER=y195,... (our versions), S9TEAMS=a,b|top (opponents), S9RANKED=1, S9SET=main|prev|all, S9DUP=1."""
    if matches is None:
        s = _env('SET') or 'main'
        matches = MAIN if s == 'main' else PREV if s == 'prev' else MAIN + PREV
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

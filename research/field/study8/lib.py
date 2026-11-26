"""Study 8 loader (study 7's lib, new dumps).  One game of a ReplayDump tsv dump, seen from the ENEMY side.
Replays only.  Usage:  for G in games(): ...  (G.op = their side 1/2, G.us = ours, G.ver = our package in that replay
(t74 / y170 / t85 / t91, read from the replay header by pkgs.py), G.team_name = the opponent, G.ranked).
games() yields our LOSSES by default, from the main set (every match since submission 66, t74: 2873-3201).
Env filters:
  S8VER=t85,t91      our versions (default: all four)
  S8TEAMS=a,b        opponents
  S8RANKED=1         ranked matches only
  S8SET=ref5         the top-5 reference set instead (1390-1395, our t16 against the 5 teams that beat us 0-3)
  S8SET=prev         study 7's main set (2641-2807: y155 and t70), for the before/after tables
  S8SET=all          main + ref5
  S8DUP=1            keep m3189g1, a repeat of m3067g0 (skipped by default)
Dumps: SP/study8/dump/m<id> (main, ref5) and SP/study7/dump/m<id> (prev); see REPORT.md for rebuilding them.
Pickle cache: SP/study8/cache."""
import csv, json, os, pickle, ast, sys
from collections import defaultdict

SP = '/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad'
# our package per match, from the replay headers (pkgs.py); t74 = submission 66, y170 = 67, t85 = 68, t91 = 69
VER = {2873: 't74', 2888: 't74', 2897: 't74', 2919: 't74', 2920: 't74', 2921: 't74', 2922: 't74',
       2969: 'y170', 2970: 'y170', 2971: 'y170', 2972: 'y170', 2973: 'y170', 2974: 'y170', 2979: 'y170',
       2990: 'y170', 2998: 'y170', 3004: 'y170', 3006: 'y170',
       3067: 't85', 3080: 't85', 3103: 't85', 3111: 't85', 3127: 't85',
       3185: 't91', 3186: 't91', 3187: 't91', 3188: 't91', 3189: 't91', 3190: 't91', 3195: 't91', 3201: 't91',
       # top-5 reference set: their bots are fixed benchmarks; ours was t16 (submission 51)
       1390: 't16', 1391: 't16', 1392: 't16', 1393: 't16', 1395: 't16',
       # study 7's main set (y155 = submission 64, t70 = 65), dumps in study7/dump
       2641: 'y155', 2642: 'y155', 2643: 'y155', 2644: 'y155', 2645: 'y155', 2646: 'y155',
       2681: 't70', 2682: 't70', 2683: 't70', 2684: 't70', 2685: 't70', 2686: 't70', 2702: 't70', 2712: 't70',
       2715: 't70', 2716: 't70', 2723: 't70', 2729: 't70', 2749: 't70', 2753: 't70', 2768: 't70', 2783: 't70',
       2804: 't70', 2807: 't70'}
MAIN = tuple(m for m in VER if m >= 2873)
REF5 = (1390, 1391, 1392, 1393, 1395)
PREV = tuple(m for m in VER if 2600 <= m < 2873)
UNRANKED = (2920, 2922, 2970, 2972, 2974, 3186, 3188, 3190) + REF5 + (2642, 2644, 2646, 2682, 2684, 2686, 2716)
DUMPS = {m: (f'{SP}/study7/dump/m{m}' if m in PREV else f'{SP}/study8/dump/m{m}') for m in VER}
# m3189g1 is m3067g0 again (Flower vs gone-whalin, sides swapped, same 1307 rounds and coverage: t85 and t91 played it
# identically); skipped unless S8DUP=1
DUP = {(3189, 1)}
CACHE = f'{SP}/study8/cache'
STRONG = None   # study 8: every opponent in the set (lib.games(teams=...) or S8TEAMS narrows it)
TOP5 = ('old-but-gold', 'just-woke-up', 'om-nom', 'confused', 'subscribe-to-caterpillow')
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
    os.makedirs(CACHE, exist_ok=True)
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


def games(which='lost', matches=None, teams=STRONG, vers=None, ranked=None):
    """which: 'lost' (default: games the opponent won), 'won' (games we won), 'all'.
    Env: S8VER=t74,y170,t85,t91 (our versions), S8TEAMS=a,b (opponents), S8RANKED=1, S8SET=main|ref5|prev|all."""
    import os as _o
    if matches is None:
        s = _o.environ.get('S8SET', 'main')
        matches = MAIN if s == 'main' else REF5 if s == 'ref5' else PREV if s == 'prev' else MAIN + REF5
    if _o.environ.get('S8VER'): vers = _o.environ['S8VER'].split(',')
    if _o.environ.get('S8TEAMS'): teams = tuple(_o.environ['S8TEAMS'].split(','))
    if _o.environ.get('S8RANKED'): ranked = True
    for m in sorted(matches):
        if vers and VER[m] not in vers: continue
        if ranked and m in UNRANKED: continue
        for g in range(3):
            if (m, g) in DUP and not _o.environ.get('S8DUP'): continue
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

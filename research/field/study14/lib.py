"""Study 14 loader (study 13's lib, new dumps).  One game of a ReplayDump tsv dump, seen from the ENEMY side.
Replays only.  Usage:  for G in games(): ...  (G.op = their side 1/2, G.us = ours, G.ver = our package in that replay
(read from the replay header by pkgs.py, pkgs.txt), G.team_name = the opponent, G.ranked).
games() yields our LOSSES by default, from the main set: every match fetched after study 13's last (6493), ids
6515-6860, 29 matches:
  t158 (submission 79)  6515, 1 match
  t160 (submission 80)  6592-6598, 7 matches (t158 + Nav.tileCost ally term + moppers swing at a single robot)
  y316 (submission 81)  6635-6796, 19 matches (t160 + NAV_PAINT_WEIGHT 8)
  y323 (submission 82)  6816, 6860, 2 matches (y316 + CHURN_WAIT_ROUNDS 2)
  y328 (submission 83, the champion) has no replay in this window.
Env filters (S14* names; the S13* .. S8* names of the older scripts are accepted too):
  S14VER=y316,y323   our versions (default: all)
  S14TEAMS=a,b       opponents (S14TEAMS=top: study 12's seven top teams, TOP)
  S14RANKED=1        ranked matches only
  S14SET=main|prev|prev2|old|all   prev = study 13's main set (t140 / t158, 5572-6493; dumps in study13/dump),
                     prev2 = study 12's (t122 / t135 / t140, 5067-5557; turns and actions only in the study12 pickle
                     cache), old = study 11's (t122, 4661-5012), all = main + prev
  S14DUP=1           keep games that repeat an earlier game exactly (skipped by default; see DUP)
Dumps: SP/study14/dump/m<id> (main), SP/study13/dump/m<id> (prev), SP/study12/dump/m<id> (prev2), SP/study11/dump (old).
Pickle cache: SP/study14/cache (main), SP/study13/cache (prev), SP/study12/cache (prev2), SP/study11/cache (old).
extra(G) reads the turns' movement cooldown, action cooldown and bytecodes (mcd, acd, bc), aligned with G.turns, from
the dump (not cached; main and prev sets only)."""
import csv, json, os, pickle, ast, sys
from collections import defaultdict

SP = '/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad'
# our package per match, from the replay headers (pkgs.py, pkgs.txt)
_V = {'t158': (6515,),
      't160': (6592, 6593, 6594, 6595, 6596, 6597, 6598),
      'y316': (6635, 6662, 6663, 6664, 6665, 6666, 6667, 6678, 6706, 6707, 6708, 6709, 6710, 6711, 6748, 6774, 6776,
               6777, 6796),
      'y323': (6816, 6860)}
# study 13's main set (prev): t140 = submission 78, t158 = 79
_P = {'t140': (5572, 5573, 5602, 5620, 5638, 5681, 5683, 5700, 5701, 5702, 5703, 5704, 5705, 5718, 5742, 5751, 5787,
               5788, 5789, 5790, 5812, 5822, 5861, 5880, 5889, 5890, 5897, 5903, 5921, 5930, 5934, 5948, 5977, 6055,
               6056, 6057, 6058, 6059, 6060, 6067, 6088, 6101, 6106, 6119, 6120, 6124, 6150, 6151, 6152, 6153, 6154,
               6155, 6186, 6196, 6208, 6283, 6306, 6307, 6308, 6309, 6310, 6311, 6328, 6331, 6332),
      't158': (6370, 6383, 6384, 6385, 6386, 6387, 6388, 6411, 6412, 6413, 6414, 6415, 6442, 6447, 6478, 6483, 6493)}
# study 12's main set (prev2): t122 = submission 76, t135 = 77, t140 = 78
_P2 = {'t122': (5067, 5068, 5069, 5070, 5089, 5124, 5125, 5126, 5127, 5128, 5129, 5156, 5164, 5165),
       't135': (5202, 5203, 5204, 5205, 5216, 5259, 5277, 5278, 5279, 5281, 5282, 5283, 5284, 5287, 5316, 5356, 5366,
                5368, 5369, 5375, 5393),
       't140': (5450, 5458, 5467, 5492, 5493, 5494, 5495, 5496, 5497, 5530, 5537, 5553, 5557)}
# study 11's main set (old): t122 = submission 76
_O = {'t122': (4661, 4662, 4663, 4664, 4682, 4692, 4699, 4716, 4725, 4726, 4765, 4766, 4787, 4800, 4805, 4806, 4841,
               4842, 4878, 4879, 4880, 4881, 4916, 4917, 4918, 4919, 4920, 4921, 4954, 4955, 4956, 4957, 4981, 4992,
               4993, 5010, 5012)}
VER = {}
for _d in (_V, _P, _P2, _O):
    for _k, _ms in _d.items():
        for _m in _ms: VER[_m] = _k
MAIN = tuple(sorted(m for ms in _V.values() for m in ms))
PREV = tuple(sorted(m for ms in _P.values() for m in ms))
PREV2 = tuple(sorted(m for ms in _P2.values() for m in ms))
OLD = tuple(sorted(m for ms in _O.values() for m in ms))
UNRANKED = (6593, 6595, 6597, 6663, 6665, 6667, 6707, 6709, 6711,
            5573, 5701, 5703, 5705, 5788, 5790, 5890, 6056, 6058, 6060, 6120, 6151, 6153, 6155, 6307, 6309, 6311, 6332,
            6384, 6386, 6388, 6411, 6413, 6415,
            5068, 5070, 5125, 5127, 5129, 5165, 5203, 5205, 5278, 5281, 5283, 5369, 5493, 5495, 5497,
            4662, 4664, 4726, 4766, 4806, 4842, 4879, 4881, 4917, 4919, 4921, 4955, 4957, 4993)


def _dir(m):
    return 'study11' if m in OLD else 'study12' if m in PREV2 else 'study13' if m in PREV else 'study14'


DUMPS = {m: f'{SP}/{_dir(m)}/dump/m{m}' for m in VER}
# exact repeats of an earlier game (same map, opponent, rounds, coverage each side, result and spawn counts): the engine
# is deterministic, so the replica replays some pairings.  Kept: the first occurrence.  Study 11's and 12's stay out
# of their sets; study 13's are found by t147_dups.py (t147.txt).  Skipped unless S13DUP=1.
DUP = {(4842, 2), (4955, 0), (5012, 1)}
DUP |= {(5067, 0), (5067, 2), (5070, 2), (5156, 2), (5164, 2), (5369, 2), (5495, 0), (5553, 1)}
# study 13 (t147.txt): 26 t140 games repeat an earlier t140 game (22 inside this set, 4 from study 12's t140 set:
# m5787g1 = m5492g0, m5897g0 = m5492g1, m6106g1 = m5497g2, m6124g1 = m5492g2).  Kept, as t158's results: m6415g1 =
# m5572g1 and m6447g0 = m6331g0, two t158 games identical to t140 games (the hit and run never changed them).
DUP |= {(5751, 2), (5787, 1), (5812, 0), (5822, 2), (5897, 0), (5897, 1), (5921, 2), (5948, 1), (6056, 1), (6057, 0),
        (6067, 0), (6067, 1), (6067, 2), (6088, 1), (6106, 1), (6120, 0), (6124, 0), (6124, 1), (6186, 0), (6186, 2),
        (6208, 1), (6283, 2), (6307, 2), (6308, 0), (6331, 2), (6332, 0)}
# study 14 (t147.txt): 5 games repeat an earlier game of this set exactly (all y316/y323 on y316/y323; none repeats a
# study 13 game: t160's Nav change touched every game)
DUP |= {(6708, 0), (6774, 2), (6776, 2), (6796, 0), (6860, 0)}
CACHES = {'study11': f'{SP}/study11/cache', 'study12': f'{SP}/study12/cache', 'study13': f'{SP}/study13/cache',
          'study14': f'{SP}/study14/cache'}
CACHE = CACHES['study14']
STRONG = None   # every opponent in the set (lib.games(teams=...) or S13TEAMS narrows it)
# study 12's top teams (owner prompt #55: "the 8 bots above us"); kept for comparison.  We are #5 of 30 now.
TOP = ('om-nom', 'spaark', 'subscribe-to-caterpillow', 'immutable', 'scienceqiu', 'lobster-roll', 'gone-whalin')
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
    cdir = CACHES[_dir(m)]
    os.makedirs(cdir, exist_ok=True)
    cp = f'{cdir}/m{m}g{g}.pkl'
    if os.path.exists(cp):
        G = pickle.load(open(cp, 'rb'))
        G.ver = VER[m]; G.ranked = m not in UNRANKED
        return G
    d = DUMPS[m]
    if not os.path.exists(f'{d}/g{g}.summary.json') or not os.path.exists(f'{d}/g{g}.turns.tsv'):
        return None
    G = Game()
    G.m, G.g = m, g
    sm = json.load(open(f'{d}/g{g}.summary.json')); meta = json.load(open(f'{d}/g{g}.meta.json'))
    G.sm, G.map, G.W, G.H = sm, meta['map'], meta['width'], meta['height']
    G.W, G.H = int(G.W), int(G.H)
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


def extra(G):
    """(mcd, acd, bc) per turn, aligned with G.turns (read from the dump's turns.tsv; not cached)."""
    d = DUMPS[G.m]
    out = []
    with open(f'{d}/g{G.g}.turns.tsv') as f:
        r = csv.reader(f, delimiter='\t'); h = next(r)
        ix = [h.index(k) for k in ('mcd', 'acd', 'bc')]
        for t in r: out.append((int(t[ix[0]]), int(t[ix[1]]), int(t[ix[2]])))
    return out


def lite(G):
    """Drop the per-turn and per-action lists (scripts that keep every game in a list need only rounds.tsv)."""
    G.turns = G.acts = None
    return G


def _env(k):
    for p in ('S14', 'S13', 'S12', 'S11', 'S10', 'S9', 'S8'):
        v = os.environ.get(p + k)
        if v: return v
    return None


_SUMM = {}


def _summ(p):
    if p not in _SUMM: _SUMM[p] = json.load(open(p))
    return _SUMM[p]


def games(which='lost', matches=None, teams=STRONG, vers=None, ranked=None):
    """which: 'lost' (default: games the opponent won), 'won' (games we won), 'all'.
    Env: S14VER=y316,... (our versions), S14TEAMS=a,b|top (opponents), S14RANKED=1,
    S14SET=main|prev|prev2|old|all, S14DUP=1."""
    if matches is None:
        s = _env('SET') or 'main'
        matches = {'main': MAIN, 'prev': PREV, 'prev2': PREV2, 'old': OLD, 'all': MAIN + PREV}.get(s, MAIN)
    if _env('VER'): vers = _env('VER').split(',')
    if _env('TEAMS'): teams = TOP if _env('TEAMS') == 'top' else tuple(_env('TEAMS').split(','))
    if _env('RANKED'): ranked = True
    for m in sorted(matches):
        if vers and VER[m] not in vers: continue
        if ranked and m in UNRANKED: continue
        for g in range(3):
            if (m, g) in DUP and not _env('DUP'): continue
            # filter on the small summary.json first (opponent, result), so a filtered run loads only its games
            sp = f'{DUMPS[m]}/g{g}.summary.json'
            if not os.path.exists(sp): continue
            sm = _summ(sp)
            us = 'A' if sm['teamA'] == US else 'B'
            opp = sm['teamB'] if us == 'A' else sm['teamA']
            if teams and opp not in teams: continue
            if which == 'lost' and sm['winner'] == us: continue
            if which == 'won' and sm['winner'] != us: continue
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

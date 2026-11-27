"""Topic 128: what each side turns its chips into.  Chips buy only four things (RULES 1, 4.7-4.9): towers (1000 each,
which bring 500 paint), robots (S 250, X 400, M 300; the tower also needs the paint), upgrades (2500 to L2, 5000 to L3)
and SRPs (200).  Per side and phase (r1-100, r101-200, r201-300, r301-400), from actions.tsv and rounds.tsv:
  spent      chips spent per category (towers split into new ruins / rebuilt own / taken / churn rebuilds; a churn
             rebuild is a build on a ruin where the same side's tower disintegrated ('died' row) in the 10 rounds before)
  income     inferred: chips(r) - chips(r-1) + spent(r), summed
  held       mean chips at round end; share of rounds ending with >= 1500 / >= 2500 chips
  churns     tower disintegrations ('died' rows of towers) and how many were rebuilt by the side within 10 rounds
  rate       chips spent per round in rounds that began with >= 2000 chips vs < 2000 (the conversion speed of a surplus)
Medians per game (sums in brackets), lost and won games, us / them."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 300), (301, 400))
UCOST = {'SOLDIER': 250, 'SPLASHER': 400, 'MOPPER': 300}


def analyse(G):
    b, d = lib.tower_events(G)
    pos = {x[1]: (x[4], x[5]) for x in b}
    # tower history per ruin position: list of (round, side, event)
    hist = defaultdict(list)
    for x in b: hist[(x[4], x[5])].append((x[0], x[3], 'build', x[1]))
    died_rm = {}
    for a in G.acts:
        if a[4] == 'died' and a[7] in lib.TOW: died_rm[int(a[5])] = a[0]
    for x in d: hist[(x[4], x[5])].append((died_rm.get(x[1], x[0]), x[3], 'churn' if x[1] in died_rm else 'kill', x[1]))   # a churn dies in the 'died' row's round
    for k in hist: hist[k].sort(key=lambda h: (h[0], h[2] == 'build'))   # a death precedes a build in the same round
    spent = defaultdict(lambda: defaultdict(int))   # (side, round) -> category -> chips
    for a in G.acts:
        r, side, k = a[0], a[2], a[4]
        if k == 'spawn' and a[3] in lib.TOW and a[6] in UCOST:
            spent[(side, r)]['units'] += UCOST[a[6]]; spent[(side, r)]['n_' + a[6][:2]] += 1
        elif k == 'build':
            tid = int(a[5]); p = pos.get(tid)
            prev = [h for h in hist.get(p, ()) if h[0] < r or (h[0] == r and h[2] != 'build')]
            cat = 'tow_new'
            if prev:
                last = prev[-1]
                if last[2] == 'churn' and last[1] == side and r - last[0] <= 10: cat = 'tow_churn'
                elif any(h[1] == side and h[2] == 'build' for h in prev): cat = 'tow_rebuilt'
                else: cat = 'tow_taken'
            spent[(side, r)][cat] += 1000
            spent[(side, r)]['n_' + cat[4:] + '_' + a[6][:1]] += 1   # build counts by category and type (n_new_P ...)
        elif k == 'upgrade':
            lvl = int(a[6]) if a[6].isdigit() else 2
            spent[(side, r)]['upgrades'] += 2500 if lvl == 2 else 5000
        elif k == 'srp':
            spent[(side, r)]['srps'] += 200
    churn = defaultdict(lambda: [0, 0])
    for p, H in hist.items():
        for i, h in enumerate(H):
            if h[2] != 'churn': continue
            nxt = [y for y in H[i + 1:] if y[2] == 'build']
            ph = next((j for j, (lo, hi) in enumerate(PH) if lo <= h[0] <= hi), None)
            if ph is None: continue
            churn[(h[1], ph)][0] += 1
            if nxt and nxt[0][1] == h[1] and nxt[0][0] - h[0] <= 10: churn[(h[1], ph)][1] += 1
    out = {}
    for side in (G.us, G.op):
        for j, (lo, hi) in enumerate(PH):
            if G.end < hi: continue
            m = defaultdict(float)
            rich_sp, rich_n, poor_sp, poor_n = 0, 0, 0, 0
            for r in range(lo, hi + 1):
                sp = spent.get((side, r), {})
                tot = sum(v for kk, v in sp.items() if not kk.startswith('n_'))
                for kk, v in sp.items(): m[kk] += v
                c0 = lib.money(G, side, r - 1); c1 = lib.money(G, side, r)
                m['income'] += c1 - c0 + tot
                m['held'] += c1
                m['r1500'] += c1 >= 1500; m['r2500'] += c1 >= 2500
                if c0 >= 2000: rich_sp += tot; rich_n += 1
                else: poor_sp += tot; poor_n += 1
            n = hi - lo + 1
            m['held'] /= n; m['r1500'] = 100 * m['r1500'] / n; m['r2500'] = 100 * m['r2500'] / n
            m['rate_rich'] = rich_sp / rich_n if rich_n else None
            m['rate_poor'] = poor_sp / poor_n if poor_n else None
            m['rich_rounds'] = rich_n
            m['churns'], m['churn_rebuilt'] = churn.get((side, j), (0, 0))
            m['towers_all'] = sum(m[k] for k in ('tow_new', 'tow_rebuilt', 'tow_taken', 'tow_churn'))
            out[(side == G.us, j)] = m
    return out


KEYS = ('income', 'towers_all', 'tow_new', 'tow_rebuilt', 'tow_taken', 'tow_churn', 'n_new_P', 'n_new_M', 'n_new_D',
        'n_rebuilt_P', 'n_rebuilt_M', 'n_taken_P', 'n_taken_M', 'n_churn_P', 'n_churn_M', 'units', 'n_SO', 'n_SP', 'n_MO',
        'upgrades', 'srps', 'held', 'r1500', 'r2500', 'rich_rounds', 'rate_rich', 'rate_poor', 'churns', 'churn_rebuilt')
for which in ('lost', 'won'):
    V = defaultdict(lambda: defaultdict(list)); n = 0
    for G in lib.games(which):
        n += 1
        for (isus, j), m in analyse(G).items():
            for k in KEYS: V[(isus, j)][k].append(m.get(k, 0) if m.get(k) is not None or k.startswith('rate') else 0)
        lib.lite(G)
    print(f'\n== {which} games ({n}); medians per game [sums], us | them')
    print(f'{"":14s}' + ''.join(f'{f"r{lo}-{hi}":>32s}' for lo, hi in PH))
    for k in KEYS:
        cells = []
        for j in range(len(PH)):
            u = V[(True, j)][k]; t = V[(False, j)][k]
            su = sum(x for x in u if x is not None); st = sum(x for x in t if x is not None)
            if k in ('held', 'r1500', 'r2500', 'rate_rich', 'rate_poor', 'rich_rounds'):
                cells.append(f'{lib.med(u)} | {lib.med(t)}')
            else:
                cells.append(f'{lib.med(u)} | {lib.med(t)} [{int(su)}|{int(st)}]')
        print(f'{k:14s}' + ''.join(f'{c:>32s}' for c in cells))

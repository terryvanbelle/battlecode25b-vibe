"""Topic 107: when a lost game turns for good.  Per lost game (rounds.tsv):
  towlead  first round from which their tower count stays above ours to the end
  covlead  first round from which their coverage share stays >= 10 points above ours to the end
and, in the 50 rounds before towlead, the events that moved the tower count: towers built (new ruins / rebuilt on
an own old ruin / taken over from the other side; churn rebuilds left out), towers killed, per side.  Lost games of
all opponents, of the top teams (lib.TOP), and the won games' reverse (the round from which OUR tower count stays
above theirs)."""
import lib
from collections import Counter


def lead_round(G, a, b, key, margin):
    """First round from which side a's value minus side b's stays >= margin to the end (None if never)."""
    last_bad = 0
    for r in range(1, G.end + 1):
        if key == 'tow': da = lib.rv(G, a, r, 'tow') - lib.rv(G, b, r, 'tow')
        else: da = lib.rv(G, a, r, 'covpct') - lib.rv(G, b, r, 'covpct')
        if da < margin: last_bad = r
    return None if last_bad >= G.end else last_bad + 1


def events(G, lo, hi):
    """Tower builds and kills per side in rounds lo..hi; builds classified by the ruin's history (churn rebuilds out)."""
    b, d = lib.tower_events(G)
    # churned towers: 'died' rows (disintegrate) -> tower_events puts them in d with round last+1; tell them apart by a
    # 'die' action: towers killed have a die row
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    hist = {}
    ev = sorted([(x[0], 'b', x) for x in b] + [(x[0], 'd', x) for x in d], key=lambda e: (e[0], e[1] != 'd'))
    c = {s: Counter() for s in (G.us, G.op)}
    for r, kind, x in ev:
        p = (x[4], x[5]); s = x[3]
        if kind == 'b':
            h = hist.get(p)
            cat = 'new ruin' if h is None else ('rebuilt own' if h[0] == s and h[1] == 'killed' else
                                                 'churn' if h[0] == s else 'taken')
            if lo <= r <= hi and r > 0 and cat != 'churn': c[s]['built ' + cat] += 1
            hist[p] = (s, 'standing')
        else:
            k = 'killed' if x[1] in killed else 'churned'
            if lo <= r <= hi and k == 'killed': c[s]['lost to kills'] += 1
            hist[p] = (s, k)
    return c


def run(name, gs, a_is_them=True):
    rows = []; tot = {'lead': Counter(), 'trail': Counter()}
    for G in gs:
        a, b = (G.op, G.us) if a_is_them else (G.us, G.op)
        tl = lead_round(G, a, b, 'tow', 1); cl = lead_round(G, a, b, 'cov', 10)
        if tl is not None:
            c = events(G, max(1, tl - 50), tl)
            tot['lead'].update(c[a]); tot['trail'].update(c[b])
        rows.append((lib.lite(G), tl, cl))
    print(f'\n== {name}: {len(rows)} games')
    tls = [r[1] for r in rows if r[1] is not None]; cls = [r[2] for r in rows if r[2] is not None]
    print(f'   tower lead for good: {len(tls)} of {len(rows)} games, median r{lib.med(tls)} (p25 r{lib.pct(tls, .25)}, p75 r{lib.pct(tls, .75)});'
          f' by r100: {sum(1 for t in tls if t <= 100)}, r101-200: {sum(1 for t in tls if 100 < t <= 200)}, later: {sum(1 for t in tls if t > 200)}')
    print(f'   coverage lead >= 10 points for good: {len(cls)} games, median r{lib.med(cls)}; rounds from the tower lead to it: '
          f'{lib.med([r[2] - r[1] for r in rows if r[1] and r[2]])}')
    print(f'   in the 50 rounds before the tower lead (sums over {len(tls)} games): leader {dict(tot["lead"])} | trailer {dict(tot["trail"])}')
    return rows


rows = run('LOST games: their lead', lib.games('lost'))
run('LOST games to the top teams: their lead', lib.games('lost', teams=lib.TOP))
run('WON games: our lead', lib.games('won'), a_is_them=False)
print('\nper lost game: tower lead r / coverage lead r')
for G, tl, cl in rows:
    print(f'   m{G.m}g{G.g} {G.ver:5s} {G.team_name[:12]:12s} {G.map[:14]:14s} {G.wintype[:3]}{G.end:<5d} towlead r{tl} covlead r{cl}')

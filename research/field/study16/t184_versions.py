"""Topic 184 (new): question 2 of the brief.  Did y358 (Tune.SOL_REFILL 100 -> 120) and y360 (Tune.SOL_PAINT_NEAR
50 -> 40) do what they meant: fewer starved soldiers, more coverage early?  y360's games are the 14 matches fetched
during the study (lib.NEW; y374's one match is left out).  The size of y360's window is measured too: soldier turns that end with 40-49 paint and no tile painted (paintNear
stops below SOL_PAINT_NEAR; y360 lets these paint).  Our soldiers, per version (t188: this study's and study 15's games;
y358: this study's), over
  all       every game
  shared    the (opponent, map) pairings both versions played
  top7      the seven teams of the brief
Per phase (r1-100, r101-200, r201-300): soldier-rounds, shares of turns ending under 120 / 100 / 50 paint and at 0;
soldiers starved per game (last turn at 0 paint, before the end) and killed per game; tiles painted per 100
soldier-rounds; withdrawals per 100 soldier-rounds; the y360 window (turns ending at 40-49 paint with no paint action
that turn, per 100 soldier-rounds); coverage (% of paintable tiles, medians) at r100 / r150 / r200, us and them, and
the game result."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 300))
PHN = ('r1-100', 'r101-200', 'r201-300')


def ph(r):
    for j, (lo, hi) in enumerate(PH):
        if lo <= r <= hi: return j
    return None


def analyse(G):
    o = defaultdict(float)
    paint_r = defaultdict(set); wd = defaultdict(int)
    for a in G.acts:
        if a[2] != G.us or a[3] != 'SOLDIER': continue
        if a[4] == 'paint': paint_r[a[1]].add(a[0])
        elif a[4] == 'transfer' and a[6] and int(a[6]) < 0:
            j = ph(a[0])
            if j is not None: o[('wd', j)] += 1
        elif a[4] == 'attack': paint_r[a[1]].add(a[0])
    last = {}
    for t in G.turns:
        if t[2] != G.us or t[3] != 'SOLDIER': continue
        last[t[1]] = t
        j = ph(t[0])
        if j is None: continue
        p = t[7]
        o[('rr', j)] += 1
        if p < 120: o[('lt120', j)] += 1
        if p < 100: o[('lt100', j)] += 1
        if p < 50: o[('lt50', j)] += 1
        if p == 0: o[('zero', j)] += 1
        if 40 <= p < 50 and t[0] not in paint_r[t[1]]: o[('win360', j)] += 1
    for i, s in paint_r.items():
        for r in s:
            j = ph(r)
            if j is not None: o[('paint', j)] += 1
    for i, t in last.items():
        if t[0] >= G.end: continue
        j = ph(t[0])
        if j is None: continue
        o[('starved' if t[7] == 0 else 'killed', j)] += 1
    for r in (100, 150, 200):
        if G.end >= r:
            o[('cov', r, 'us')] = lib.rv(G, G.us, r, 'covpct'); o[('cov', r, 'them')] = lib.rv(G, G.op, r, 'covpct')
    o['won'] = 0 if G.won_op else 1
    return o


def report(tag, OS):
    if not OS: return
    n = len(OS)
    print(f'\n  {tag}: {n} games, won {sum(o["won"] for o in OS)}')
    print(f'     {"":44s}' + ''.join(f'{x:>12s}' for x in PHN))

    def row(name, fn):
        print(f'     {name:44s}' + ''.join(f'{fn(j):>12s}' for j in range(len(PH))))
    rr = lambda j: sum(o[('rr', j)] for o in OS)
    row('soldier-rounds per game', lambda j: f'{rr(j) / n:.0f}')
    for k, nm in (('lt120', 'turns ending under 120 paint (%)'), ('lt100', 'under 100 (%)'), ('lt50', 'under 50 (%)'), ('zero', 'at 0 (%)')):
        row(nm, lambda j, k=k: f'{100 * sum(o[(k, j)] for o in OS) / max(1, rr(j)):.1f}')
    row('starved soldiers per game', lambda j: f'{sum(o[("starved", j)] for o in OS) / n:.2f}')
    row('other soldier deaths per game', lambda j: f'{sum(o[("killed", j)] for o in OS) / n:.2f}')
    row('tiles painted + attacks per 100 soldier-rounds', lambda j: f'{100 * sum(o[("paint", j)] for o in OS) / max(1, rr(j)):.1f}')
    row('withdrawals per 100 soldier-rounds', lambda j: f'{100 * sum(o[("wd", j)] for o in OS) / max(1, rr(j)):.2f}')
    row('y360 window: 40-49 paint, no paint (/100 s-r)', lambda j: f'{100 * sum(o[("win360", j)] for o in OS) / max(1, rr(j)):.2f}')
    for r in (100, 150, 200):
        u = [o[('cov', r, 'us')] for o in OS if ('cov', r, 'us') in o]; t = [o[('cov', r, 'them')] for o in OS if ('cov', r, 'them') in o]
        print(f'     coverage at r{r} (median %): us {lib.med(u)} / them {lib.med(t)}  ({len(u)} games)')


ms = tuple(sorted(set(lib.T188) | set(m for m in lib.MAIN if lib.VER[m] == 'y358') | set(m for m in lib.NEW if lib.VER[m] == 'y360')))
R = defaultdict(list)
pairs = defaultdict(set)
for G in lib.games('all', matches=ms):
    o = analyse(G)
    o['pair'] = (G.team_name, G.map)
    R[G.ver].append(o)
    pairs[G.ver].add((G.team_name, G.map))
    G.turns = G.acts = None
shared = pairs['t188'] & pairs['y358']
print('shared pairings:', ', '.join(f'{a}/{b}' for a, b in sorted(shared)))
for v in ('t188', 'y358', 'y360'):
    print(f'\n== {v}')
    report('all', R[v])
    if v != 'y360': report('shared pairings', [o for o in R[v] if o['pair'] in shared])
    report('top7', [o for o in R[v] if o['pair'][0] in lib.TOP7])
    report('top7 lost', [o for o in R[v] if o['pair'][0] in lib.TOP7 and not o['won']])

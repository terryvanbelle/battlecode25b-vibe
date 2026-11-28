"""Topic 165: lone sieges against sieges in company (follows t163/t164).  An attack run = one soldier's damage rows on
one tower, grouped while the gap is under 15 rounds.  Company = other soldiers and splashers of the same side with a
damage row on the same tower from 3 rounds before the run's first hit to 3 rounds after its last.  Per side and
company size (0, 1, 2+): runs per game, the share whose tower fell during the run (or within a round after it), the
share whose soldier died to that tower within 5 rounds after its last hit, and the same two for runs against a side
with a defense tower standing (t164: +5 to every tower's single shot each).  Losses then wins."""
from collections import defaultdict
import lib


def analyse(G, S):
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1])
    built, died = lib.tower_events(G)
    dt = []
    for (r, tid, ty, team, x, y) in built:
        if ty == 'DEFENSE_TOWER':
            dt.append((team, r, min([d[0] for d in died if d[1] == tid] or [10 ** 6])))
    hits = defaultdict(list)           # tower -> [(round, attacker, type)]
    for a in G.acts:
        if a[4] == 'damage' and a[3] in ('SOLDIER', 'SPLASHER'):
            v = int(a[5])
            if G.typ.get(v) in lib.TOW: hits[v].append((a[0], a[1], a[3]))
    for v, hs in hits.items():
        hs.sort()
        per = defaultdict(list)
        for h in hs:
            if h[2] == 'SOLDIER': per[h[1]].append(h[0])
        td = deaths.get(v)
        side_t = G.team.get(v)
        for rid, rs in per.items():
            groups = []
            for r in rs:
                if groups and r - groups[-1][-1] < 15: groups[-1].append(r)
                else: groups.append([r])
            for g in groups:
                r0, r1 = g[0], g[-1]
                comp = {h[1] for h in hs if h[1] != rid and r0 - 3 <= h[0] <= r1 + 3}
                c = min(2, len(comp))
                fell = td is not None and r0 <= td[0] <= r1 + 1
                d = deaths.get(rid)
                dead = bool(d and d[1] == v and r0 <= d[0] <= r1 + 5)
                buff = any(tm == side_t and a <= r0 < b for (tm, a, b) in dt)
                sd = 'us' if G.team.get(rid) == G.us else 'them'
                S[sd, c, 'n'] += 1; S[sd, c, 'fell'] += fell; S[sd, c, 'dead'] += dead
                if buff: S[sd, c, 'bn'] += 1; S[sd, c, 'bfell'] += fell; S[sd, c, 'bdead'] += dead


for which in ('lost', 'won'):
    S = defaultdict(int)
    ng = 0
    for G in lib.games(which):
        ng += 1
        analyse(G, S)
    print(f'\n== {which}: {ng} games; soldier attack runs on towers by company size')
    for sd in ('us', 'them'):
        for c in (0, 1, 2):
            n = max(1, S[sd, c, 'n']); bn = max(1, S[sd, c, 'bn'])
            print(f'  {sd:4s} company {c}{"+" if c == 2 else " "}  runs {S[sd, c, "n"] / ng:5.1f}/game  tower fell {100 * S[sd, c, "fell"] / n:3.0f}%  '
                  f'soldier died to it {100 * S[sd, c, "dead"] / n:3.0f}%   | vs a defense-buffed side: runs {S[sd, c, "bn"] / ng:4.1f}/game, '
                  f'fell {100 * S[sd, c, "bfell"] / bn:3.0f}%, died {100 * S[sd, c, "bdead"] / bn:3.0f}%')

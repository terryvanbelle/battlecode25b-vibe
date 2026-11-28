"""Topic 173: does the siege kite break down at low paint?  RULES 3: below half paint (100 for a soldier) both
cooldowns grow, cd = 10 + round(10 (100 - 2 pct) / 100): 13 at 70 paint, 15 at 50, 17 at 30.  The kite (step in and
hit; next turn hit and step out) needs the move and the attack ready on consecutive turns, which holds only at cd 10;
with cd 15-17 the soldier sits in range for an extra turn (an exposure with no hit).  t163: our sieges start at a median
114 paint and our soldiers that live leave at 34-38 paint (SOL_SIEGE_PAINT 30), theirs at 48-55.
Per soldier hit on a paint/money tower that stood a round after, by the hitter's paint at the end of the previous turn
(>=100, 70-99, 50-69, 30-49, <30): hits per game, the tower's shots that hit the soldier from this hit to just before
its next hit on that tower (at most 4 rounds; exposures per hit), the share followed by death to that tower within 5
rounds, and the in->in share.  Our versions apart (y328 = before the step-out; new = t186 + t188); all games.
Then split by opponent: def = immutable and spaark (they build 1.6 defense towers a game, t172), nodef = the rest."""
from collections import defaultdict
import os
import lib

BANDS = ((100, '>=100'), (70, '70-99'), (50, '50-69'), (30, '30-49'), (0, '<30'))


def analyse(G, S, tag):
    pos = {}; tt = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    life = defaultdict(dict)
    for t in G.turns:
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7])
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1])
    shots = defaultdict(set)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.TOW and a[3] != 'DEFENSE_TOWER': shots[(a[1], int(a[5]))].add(a[0])
    hits = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] == 'SOLDIER' and tt.get(int(a[5])) in ('PAINT_TOWER', 'MONEY_TOWER'):
            hits[(a[1], int(a[5]))].append((a[0], a[2]))
    for (sid, tid), L in hits.items():
        L.sort()
        td = deaths.get(tid); d = deaths.get(sid)
        for i, (r, team) in enumerate(L):
            if td and td[0] <= r + 1: continue
            now = life[sid].get(r); bef = life[sid].get(r - 1)
            if not now or not bef: continue
            sd = tag if team == G.us else 'them(' + tag + ')'
            q = pos[tid]
            d1 = (now[0] - q[0]) ** 2 + (now[1] - q[1]) ** 2; d0 = (bef[0] - q[0]) ** 2 + (bef[1] - q[1]) ** 2
            nxt = L[i + 1][0] if i + 1 < len(L) else r + 5
            end = min(nxt, r + 5)
            sh = sum(1 for x in shots.get((tid, sid), ()) if r <= x < end)
            # a tower that acts before the soldier shoots it at round r+1 for being in range at the end of round r
            b = next(n for (lo, n) in BANDS if bef[3] >= lo)
            dead = bool(d and d[1] == tid and d[0] - r <= 5)
            S[sd, b] += 1; S[sd, b, 'sh'] += sh; S[sd, b, 'dead'] += dead; S[sd, b, 'inin'] += d0 <= 9 and d1 <= 9
    S[tag, 'games'] += 1


S = defaultdict(int)
for st, vers in (('main', ('y328', 't186', 't188')),):
    os.environ['S15SET'] = st
    for v in vers:
        for G in lib.games('all', vers=[v]):
            analyse(G, S, 'y328' if v == 'y328' else 'new')
            analyse(G, S, ('def:' if G.team_name in ('immutable', 'spaark') else 'nodef:') + ('y328' if v == 'y328' else 'new'))
for tag in ('y328', 'new', 'def:y328', 'def:new', 'nodef:y328', 'nodef:new'):
    ng = max(1, S[tag, 'games'])
    print(f'\n== {tag}: {S[tag, "games"]} games; soldier hits on standing paint/money towers by the hitter\'s paint')
    for sd in (tag, 'them(' + tag + ')'):
        tot = sum(S[sd, b] for _, b in BANDS)
        print(f'  {sd:10s} ' + '  '.join(f'{b:>5s}: {S[sd, b] / ng:5.1f}/g ({100 * S[sd, b] / max(1, tot):2.0f}%) shots/hit {S[sd, b, "sh"] / max(1, S[sd, b]):4.2f} dies {100 * S[sd, b, "dead"] / max(1, S[sd, b]):3.0f}% in->in {100 * S[sd, b, "inin"] / max(1, S[sd, b]):3.0f}%' for _, b in BANDS))

"""Topic 176: defense towers by opponent (follows t172: 36-46% of our soldiers killed by towers against immutable and
spaark had a defense tower among the damage dealers).  Per opponent that builds them: defense towers built per game
and the median round of their first turn; our soldier and splasher hits on them; defense towers we destroyed; our
robots killed by defense towers per game; damage their defense towers and their paint+money towers deal our robots."""
from collections import defaultdict
import lib
S = defaultdict(int)
for G in lib.games('all', teams=('immutable', 'spaark', 'subscribe-to-caterpillow')):
    tt = {}; first = {}
    for t in G.turns:
        if t[3] in lib.TOW:
            tt[t[1]] = t[3]
            if t[1] not in first: first[t[1]] = (t[0], t[2])
    k = G.team_name
    S[k, 'g'] += 1
    for tid, (r, tm) in first.items():
        if tt[tid] == 'DEFENSE_TOWER' and tm != G.us and r > 1: S[k, 'built'] += 1; S.setdefault((k, 'r'), []).append(r)
    for a in G.acts:
        if a[4] == 'damage' and a[2] == G.us and tt.get(int(a[5])) == 'DEFENSE_TOWER': S[k, 'hits_' + a[3]] += 1
        if a[4] == 'die' and a[3] == 'DEFENSE_TOWER' and a[2] != G.us: S[k, 'killed_' + a[7]] += 1
        if a[4] == 'die' and tt.get(int(a[5])) == 'DEFENSE_TOWER' and a[2] == G.us: S[k, 'def_killed_by_us'] += 1
        if a[4] == 'damage' and a[3] == 'DEFENSE_TOWER' and a[2] != G.us: S[k, 'def_dmg'] += int(a[6])
        if a[4] == 'damage' and a[3] in ('PAINT_TOWER', 'MONEY_TOWER') and a[2] != G.us: S[k, 'pm_dmg'] += int(a[6])
for k in ('immutable', 'spaark', 'subscribe-to-caterpillow'):
    g = max(1, S[k, 'g'])
    print(f"{k:26s} {S[k,'g']} g: their defense towers built {S[k,'built']/g:4.2f}/g (first-turn round med {lib.med(S.get((k,'r'),[]))}); our hits on them: soldier {S[k,'hits_SOLDIER']/g:5.1f}/g splasher {S[k,'hits_SPLASHER']/g:4.1f}/g; "
          f"defense towers we killed {S[k,'def_killed_by_us']/g:4.2f}/g; our robots killed by defense towers: S {S[k,'killed_SOLDIER']/g:4.2f} X {S[k,'killed_SPLASHER']/g:4.2f} M {S[k,'killed_MOPPER']/g:4.2f} per game; "
          f"their tower damage on our robots: defense {S[k,'def_dmg']/g:5.0f}/g, paint+money {S[k,'pm_dmg']/g:5.0f}/g")

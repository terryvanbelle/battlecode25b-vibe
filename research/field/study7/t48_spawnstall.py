"""Topic 48: our towers stalled on an unaffordable unit.  Tower.choose() picks by the tower's own spawn count
(r<80 soldier; money towers S M X M S M; paint towers S X X M S X) and build() returns when the tower's paint is below
that unit's cost - it never falls back to a cheaper unit.  Simulating the choice from each tower's spawn history,
count our tower-turns from r80 with chips >= cost + 1000 (the reserve) where the chosen unit is unaffordable in
paint but a cheaper one is affordable (mopper >= 100, soldier >= 200), and how long such stalls last.
For comparison: the same tower-turns' share for the opponent (their spawns are unknown policy; we only count
tower-turns with paint 100-199 and chips >= 1300 and no spawn that round = 'could have spawned a mopper')."""
import lib
from collections import defaultdict, Counter
COST = {'SOLDIER': (200, 250), 'SPLASHER': (300, 400), 'MOPPER': (100, 300)}
for which in ('lost', 'won'):
    S = defaultdict(list); T = Counter()
    for G in lib.games(which):
        spawned = defaultdict(int)
        spawn_r = defaultdict(set)
        for a in G.acts:
            if a[4] == 'spawn' and a[6] in lib.BOT: spawn_r[a[0]].add(a[1])
        bt = lib.by_round_turns(G)
        sp_by = defaultdict(list)
        for a in G.acts:
            if a[4] == 'spawn' and a[6] in lib.BOT: sp_by[a[1]].append(a[0])
        c = Counter()
        for r in range(80, G.end + 1):
            chips = lib.money(G, G.us, r - 1)
            ts = bt.get(r, ())
            enemy_near = defaultdict(bool)
            for t in ts:
                if t[3] not in lib.TOW or t[2] not in (G.us, G.op): continue
                n_before = sum(1 for q in sp_by.get(t[1], ()) if q < r)
                if t[2] == G.us:
                    k = n_before % 6
                    if t[3] == 'PAINT_TOWER': ch = 'MOPPER' if k % 4 == 3 else ('SOLDIER' if k % 4 == 0 else 'SPLASHER')
                    else: ch = ('SOLDIER', 'MOPPER', 'SPLASHER', 'MOPPER', 'SOLDIER', 'MOPPER')[k]
                    cp, cc = COST[ch]
                    c['tower-turns r80+'] += 1
                    if chips < cc + 1000: continue
                    c['tower-turns with chips >= cost+1000'] += 1
                    p = t[7]
                    # paint shown is end-of-turn (after a spawn); a spawn this round means it was not stalled
                    if r in spawn_r and t[1] in spawn_r[r]: c['spawned'] += 1; continue
                    if p < cp:
                        c['stalled: chosen unit unaffordable'] += 1
                        if p >= 100: c['  ... but a mopper was affordable'] += 1
                        if ch == 'SPLASHER' and p >= 200: c['  ... a soldier was affordable (splasher due)'] += 1
                        c['  stalled on ' + ch] += 1
                else:
                    if chips >= 1300 and 100 <= t[7] < 200 and not (r in spawn_r and t[1] in spawn_r[r]):
                        c['them: tower-turns paint 100-199, chips >= 1300, no spawn'] += 1
                    if chips >= 1300: c['them: tower-turns chips >= 1300'] += 1
        for k, v in c.items(): T[k] += v
        S['stall %'].append(round(100 * c['stalled: chosen unit unaffordable'] / max(1, c['tower-turns with chips >= cost+1000']), 1))
        S['mopper-affordable stall %'].append(round(100 * c['  ... but a mopper was affordable'] / max(1, c['tower-turns with chips >= cost+1000']), 1))
    print(f'== {which} games, totals: ' + ', '.join(f'{k}: {v}' for k, v in sorted(T.items())))
    print(f'   per game: stalled share of tower-turns with chips for the unit + reserve: med {lib.med(S["stall %"])}%;'
          f' of those with >= 100 paint (a mopper possible): med {lib.med(S["mopper-affordable stall %"])}%')

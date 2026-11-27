"""Topic 49: why our towers do not spawn, per tower-turn (r40+, the 1000-chip reserve is active from r40):
spawned / chip-blocked (paint >= 200 i.e. a soldier's paint, chips < 1250 = soldier + reserve) / paint-blocked
(paint < 200, chips >= 1250) / both short / other (both available but no spawn: cycle waits for a dearer unit or the
action was not ready).  Paint towers at the 1000-paint cap (income wasted).  Same buckets for the opponent (whose
own reserve is unknown; buckets use the same thresholds).  Per game medians, lost vs won, and the per-game list."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    S = defaultdict(list); rows = []
    for G in lib.games(which):
        spawn_r = defaultdict(set)
        for a in G.acts:
            if a[4] == 'spawn' and a[6] in lib.BOT: spawn_r[a[0]].add(a[1])
        bt = lib.by_round_turns(G)
        c = defaultdict(Counter)
        for r in range(40, G.end + 1):
            for sd in (G.us, G.op):
                chips = lib.money(G, sd, r - 1)
                for t in bt.get(r, ()):
                    if t[2] != sd or t[3] not in lib.TOW: continue
                    w = 'us' if sd == G.us else 'them'
                    c[w]['n'] += 1
                    if t[1] in spawn_r.get(r, ()): c[w]['spawned'] += 1; continue
                    pa = t[7] >= 200; ch = chips >= 1250
                    if pa and not ch: c[w]['chip-blocked'] += 1
                    elif ch and not pa: c[w]['paint-blocked'] += 1
                    elif not ch and not pa: c[w]['both short'] += 1
                    else: c[w]['both ok, no spawn'] += 1
                    if t[3] == 'PAINT_TOWER' and t[7] >= 990: c[w]['paint tower at cap'] += 1
                    if t[3] == 'PAINT_TOWER': c[w]['paint tower turns'] += 1
        for w in ('us', 'them'):
            n = max(1, c[w]['n'])
            for k in ('spawned', 'chip-blocked', 'paint-blocked', 'both short', 'both ok, no spawn'):
                S[(w, k)].append(round(100 * c[w][k] / n, 1))
            S[(w, 'paint tower at cap')].append(round(100 * c[w]['paint tower at cap'] / max(1, c[w]['paint tower turns']), 1))
        rows.append((G.m, G.g, G.map, {k: round(100 * c['us'][k] / max(1, c['us']['n'])) for k in ('spawned', 'chip-blocked', 'paint-blocked', 'both short', 'both ok, no spawn')},
                     round(100 * c['us']['paint tower at cap'] / max(1, c['us']['paint tower turns']))))
    print(f'== {which} games: share of tower-turns from r40 (median per game), us | them')
    for k in ('spawned', 'chip-blocked', 'paint-blocked', 'both short', 'both ok, no spawn', 'paint tower at cap'):
        print(f'   {k:22s} {lib.med(S[("us", k)])} | {lib.med(S[("them", k)])}     us p75 {lib.pct(S[("us", k)], .75)}  them p75 {lib.pct(S[("them", k)], .75)}')
    for r in rows: print(f'   m{r[0]}g{r[1]} {r[2]:15s} us {r[3]}  paint tower at cap {r[4]}%')

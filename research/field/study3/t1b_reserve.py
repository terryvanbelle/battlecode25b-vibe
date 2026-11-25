"""Topic 1b: chip/paint reserve rule. For spawns after r20: chips before spawn; low-chip spawns and enemy proximity;
2D spawn rate table (tower paint x chips) for paint towers vs money towers, r20-200."""
import lib
from collections import Counter, defaultdict
CH = defaultdict(list); LOW = defaultdict(list); TAB = defaultdict(lambda: [0, 0])
def pb(p): return '200-299' if p < 300 else '300-449' if p < 450 else '450-699' if p < 700 else '700+'
def cb(c): return '<900' if c < 900 else '900-1099' if c < 1100 else '1100-1499' if c < 1500 else '1500-2499' if c < 2500 else '2500+'
for G in lib.games():
    rt = lib.by_round_turns(G)
    sp = {(a[0], a[1]): a[6] for a in G.acts if a[4] == 'spawn' and a[6] in lib.BOT and a[2] == G.op}
    for t in G.turns:
        if t[2] != G.op or t[3] not in lib.TOW or not (20 <= t[0] <= 200): continue
        ch = lib.money(G, G.op, t[0] - 1)
        ty = sp.get((t[0], t[1]))
        p = t[7] + (lib.COST[ty][0] if ty else 0)
        if ty:
            CH[G.team_name].append(ch)
            if ch < 900:
                ds = [lib.d2((u[4], u[5]), (t[4], t[5])) for u in rt[t[0] - 1] if u[2] == G.us and u[3] in lib.BOT]
                LOW[G.team_name].append((t[0], ty[:3], ch, min(ds) if ds else 999))
        if p >= 200:
            TAB[(t[3][:2], pb(p), cb(ch))][0 if ty else 1] += 1
for tm in CH:
    print(tm, 'chips before spawn (r20-200): p5', lib.pct(CH[tm], .05), 'p10', lib.pct(CH[tm], .1), 'med', lib.med(CH[tm]), 'p90', lib.pct(CH[tm], .9))
    print('   spawns with chips<900 (round,type,chips,nearest enemy d2):', len(LOW[tm]), LOW[tm][:12])
print('\nspawn rate per tower-turn, r20-200, by tower type x paint x chips: (spawned, idle) rate')
for k in sorted(TAB): print('  ', k, TAB[k], round(TAB[k][0] / sum(TAB[k]), 2))

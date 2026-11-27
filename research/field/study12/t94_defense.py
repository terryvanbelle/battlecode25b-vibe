"""Topic 94: tower types at work, both sides, all games.  Per side and tower type (P / M / D): towers built (starting
towers included), tower-rounds alive, towers killed by robots per 100 tower-rounds, robots the towers killed and the
HP damage they dealt per 100 tower-rounds.  The same split by where the tower stood: 'front' = nearer the other
side's starting towers than to its own (the other half), else 'home'.  Then the defense towers one by one by
opponent: build round, front/home, life, robots killed."""
import lib
from collections import defaultdict, Counter


def tower_stats(G):
    b, d = lib.tower_events(G)
    start = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    dead = {x[1]: x[0] for x in d}
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW and a[3] in lib.BOT)
    kills = Counter(); dmg = Counter()
    for a in G.acts:
        if a[3] not in lib.TOW: continue
        if a[4] == 'damage': dmg[a[1]] += int(a[6])
        elif a[4] == 'die' and a[7] in lib.BOT: kills[a[1]] += 1
    out = []
    for x in b:
        s = x[3]; p = (x[4], x[5])
        if not start.get(s) or not start.get(3 - s): continue
        own = min(lib.d2(p, q) for q in start[s]); oth = min(lib.d2(p, q) for q in start[3 - s])
        life = dead.get(x[1], G.end) - x[0]
        out.append(dict(side='us' if s == G.us else 'them', typ=x[2][0], where='front' if oth < own else 'home', r0=x[0], life=max(1, life),
                        killed=x[1] in killed, kills=kills[x[1]], dmg=dmg[x[1]]))
    return out


for which in ('lost', 'won'):
    S = defaultdict(list); n = 0; D = []
    for G in lib.games(which):
        n += 1
        for t in tower_stats(G):
            S[(t['side'], t['typ'])].append(t); S[(t['side'], t['typ'], t['where'])].append(t)
            if t['typ'] == 'D': D.append((G, t))
    print(f'== {which} games ({n}): per 100 tower-rounds')
    print('   side type where   towers  tower-rounds  killed/100r  robots killed/100r  damage/100r')
    for side in ('us', 'them'):
        for ty in ('P', 'M', 'D'):
            for wh in (None, 'home', 'front'):
                L = S[(side, ty) if wh is None else (side, ty, wh)]
                if not L: continue
                tr = sum(t['life'] for t in L)
                print(f'   {side:4s}  {ty}   {wh or "all":5s}  {len(L):6d}  {tr:12d}  {100 * sum(t["killed"] for t in L) / tr:10.2f}  '
                      f'{100 * sum(t["kills"] for t in L) / tr:18.2f}  {100 * sum(t["dmg"] for t in L) / tr:11.0f}')
    print(f'   defense towers: {len(D)}; by opponent: {dict(Counter(G.team_name for G, t in D))}')
    for G, t in D[:60]:
        print(f'      m{G.m}g{G.g} {G.map[:12]:12s} {G.team_name[:12]:12s} {t["side"]:4s} built r{t["r0"]:<4} {t["where"]:5s} life {t["life"]:4d} '
              f'{"KILLED" if t["killed"] else "      "} robots killed {t["kills"]} damage {t["dmg"]}')
    print()

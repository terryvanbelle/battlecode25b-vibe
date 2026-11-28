"""Topic 177: siege traces (illustration for t174).  Part 1: the first three of our soldiers killed by a paint/money
tower in t188 games against opponents without defense towers, their last 15 rounds (d2 to the tower, HP, paint, the
tower's shots on it, its hits).  Part 2: per top-5 opponent, their longest run of 8+ hits on one of our towers in a
t186/t188 game that ended with the soldier alive and the tower standing."""
import os, sys
from collections import defaultdict
import lib
os.environ['S15SET'] = 'main'


def part1():
    n_show = 0
    for G in lib.games('all', vers=['t188']):
        if G.team_name in ('immutable', 'spaark'): continue
        pos = {}; tt = {}
        for t in G.turns:
            if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
        life = defaultdict(dict)
        for t in G.turns:
            if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7])
        shots = defaultdict(list)
        for a in G.acts:
            if a[4] == 'damage' and a[3] in lib.TOW: shots[int(a[5]), a[0]].append((a[1], a[6]))
        hits = defaultdict(list)
        for a in G.acts:
            if a[4] == 'damage' and a[3] == 'SOLDIER': hits[a[1], a[0]].append(int(a[5]))
        for a in G.acts:
            if a[4] == 'die' and a[3] in ('PAINT_TOWER', 'MONEY_TOWER') and a[7] == 'SOLDIER':
                v = int(a[5]); r = a[0]
                sd = 'us' if G.team.get(v) == G.us else 'them'
                if sd != 'us': continue
                q = pos[a[1]]
                print(f'm{G.m}g{G.g} {G.team_name} soldier {v} killed r{r} by {tt[a[1]]} {a[1]} at {q}')
                for rr in range(r - 14, r + 1):
                    p = life[v].get(rr)
                    if not p: continue
                    d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                    print(f'   r{rr} at ({p[0]},{p[1]}) d2 {d:2d} hp {p[2]:3d} paint {p[3]:3d}  shot by {shots.get((v, rr), [])}  hit {hits.get((v, rr), [])}')
                n_show += 1
                if n_show >= 3: return


part1()
print()
shown = defaultdict(int)
for G in lib.games('all', vers=['t188', 't186']):
    if shown[G.team_name] >= 1 or G.team_name not in lib.TOP5: continue
    pos = {}; tt = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    life = defaultdict(dict)
    for t in G.turns:
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7])
    shots = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.TOW: shots[int(a[5]), a[0]].append(a[6])
    hits = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] == 'SOLDIER' and a[2] != G.us and tt.get(int(a[5])) in ('PAINT_TOWER', 'MONEY_TOWER'): hits[a[1], int(a[5])].append(a[0])
    # pick their longest run that ended with the soldier alive and the tower standing
    deaths = {int(a[5]): a[0] for a in G.acts if a[4] == 'die'}
    best = None
    for (sid, tid), rs in hits.items():
        rs.sort()
        if deaths.get(tid, 9999) <= rs[-1] + 2 or deaths.get(sid, 9999) <= rs[-1] + 10: continue
        if len(rs) >= 8 and (best is None or len(rs) > len(best[2])): best = (sid, tid, rs)
    if not best: continue
    sid, tid, rs = best; q = pos[tid]
    shown[G.team_name] += 1
    print(f'm{G.m}g{G.g} {G.team_name} their soldier {sid} on our {tt[tid]} at {q}, hits r{rs[0]}-r{rs[-1]} ({len(rs)})')
    for rr in range(rs[0] - 2, rs[-1] + 6):
        p = life[sid].get(rr)
        if not p: continue
        d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
        print(f'   r{rr} d2 {d:2d} hp {p[2]:3d} paint {p[3]:3d} shot {shots.get((sid, rr), [])} hit {"Y" if rr in rs else ""}')

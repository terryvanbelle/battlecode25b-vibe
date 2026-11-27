"""Topic 77: a map picture.  `python3 -I t77_mapview.py mMgG ROUND` (with this directory on sys.path; run.sh draws
m2641g1 at r200) prints the map with north on top: U our standing tower, T theirs, r a free ruin one of our robots
has seen by ROUND (d2 <= 20 of an end-of-turn position), R a free ruin we have not seen, '.' a seen tile, '#' a wall."""
import sys
import lib, os
want = sys.argv[1] if len(sys.argv) > 2 else 'm2641g1'; upto = int(sys.argv[2]) if len(sys.argv) > 2 else 200
for G in lib.games('all'):
    if f'm{G.m}g{G.g}' != want: continue
    b, d = lib.tower_events(G)
    W, H = G.W, G.H
    seen = set()
    for t in G.turns:
        if t[0] > upto: break
        if t[3] in lib.BOT and t[2] == G.us:
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    if dx*dx+dy*dy <= 20: seen.add((t[4]+dx, t[5]+dy))
    occ = {}
    for sd in (1, 2):
        for t in lib.towers_alive(G, sd, upto, b, d): occ[(t[4], t[5])] = 'U' if sd == G.us else 'T'
    start = [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == G.us]
    rows = []
    for y in range(H - 1, -1, -1):
        row = ''
        for x in range(W):
            p = (x, y)
            if p in occ: c = occ[p]
            elif p in set(map(tuple, G.ruins)): c = 'R' if p not in seen else 'r'
            elif (x + y * W) in G.walls: c = '#'
            elif p in seen: c = '.'
            else: c = ' '
            row += c
        rows.append(row)
    print(f'm{G.m}g{G.g} {G.map} at r{upto}: U our tower, T theirs, r seen free ruin, R unseen free ruin, . seen tile, # wall; our start {start}')
    print('\n'.join(rows))

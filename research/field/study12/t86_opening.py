"""Topic 86: the opening (r1-100), both sides.  Lost games split by the tower count at r100 (behind = ours minus theirs
<= -1, level or ahead >= 0), and won games.  Per side, medians per game: towers built by r50 / r100 (new ruins and
rebuilds), towers lost to kills by r50 / r100 (and how many were the starting paint tower), the round of the 1st / 2nd
/ 3rd build, robots spawned by type by r100, soldier-turns by r100, and our first soldiers' first marks.  Then, per
lost game behind at r100, one line: map, opponent, our and their builds and losses by r100, and the round our starting
paint tower died (if it did)."""
import lib
from collections import defaultdict, Counter


def opening(G, sd):
    b, d = lib.tower_events(G)
    o = {}
    builds = [x for x in b if x[3] == sd and x[0] > 0]
    kills = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    lost = [x for x in d if x[3] == sd and x[1] in kills]
    start_pt = [x for x in b if x[3] == sd and x[0] == 0 and x[2] == 'PAINT_TOWER']
    spt_death = next((x[0] for x in d if start_pt and x[1] == start_pt[0][1]), None)
    o['built r50'] = sum(1 for x in builds if x[0] <= 50)
    o['built r100'] = sum(1 for x in builds if x[0] <= 100)
    o['killed r50'] = sum(1 for x in lost if x[0] <= 50)
    o['killed r100'] = sum(1 for x in lost if x[0] <= 100)
    o['start PT killed by r100'] = int(spt_death is not None and spt_death <= 100 and start_pt[0][1] in kills)
    o['start PT death'] = spt_death if (spt_death and start_pt and start_pt[0][1] in kills) else None
    for k in (1, 2, 3):
        o[f'build #{k} round'] = builds[k - 1][0] if len(builds) >= k else None
    sp = Counter(a[6][:2] for a in G.acts if a[2] == sd and a[4] == 'spawn' and a[0] <= 100 and a[6] in lib.BOT)
    o['spawned S r100'] = sp['SO']; o['spawned M r100'] = sp['MO']; o['spawned X r100'] = sp['SP']
    o['soldier-turns r100'] = sum(1 for t in G.turns if t[0] <= 100 and t[2] == sd and t[3] == 'SOLDIER')
    o['soldier dmg to towers r100'] = sum(int(a[6]) for a in G.acts if a[0] <= 100 and a[2] == sd and a[4] == 'damage' and a[3] == 'SOLDIER')
    o['towers r100'] = lib.rv(G, sd, 100, 'tow')
    return o


KS = ('towers r100', 'built r50', 'built r100', 'killed r50', 'killed r100', 'start PT killed by r100', 'build #1 round', 'build #2 round',
      'build #3 round', 'spawned S r100', 'spawned M r100', 'spawned X r100', 'soldier-turns r100', 'soldier dmg to towers r100')
groups = defaultdict(list)
for G in lib.games('all'):
    diff = lib.rv(G, G.us, 100, 'tow') - lib.rv(G, G.op, 100, 'tow')
    g = ('lost' if G.won_op else 'won') + (', behind at r100' if diff <= -1 else ', level or ahead at r100')
    groups[g].append((G, opening(G, G.us), opening(G, G.op)))
    lib.lite(G)
for g in sorted(groups):
    rows = groups[g]
    print(f'== {g}: {len(rows)} games; medians (sums for counts in brackets), us / them')
    for k in KS:
        u = [r[1][k] for r in rows]; t = [r[2][k] for r in rows]
        extra = f'   [{sum(x or 0 for x in u)} / {sum(x or 0 for x in t)}]' if not k.endswith('round') else \
            f'   (reached in {sum(x is not None for x in u)} / {sum(x is not None for x in t)})'
        print(f'   {k:28s} {lib.med(u)} / {lib.med(t)}{extra}')
    print()
print('== lost games behind at r100, one by one: our built/killed by r100, theirs; our starting paint tower death')
for G, u, t in groups['lost, behind at r100']:
    print(f'   m{G.m}g{G.g} {G.map[:13]:13s} {G.team_name[:10]:10s} {G.wintype[:3]} r{G.end:<4} towers r100 {u["towers r100"]}/{t["towers r100"]}: '
          f'us built {u["built r100"]} lost {u["killed r100"]} | them built {t["built r100"]} lost {t["killed r100"]} | '
          f'our start PT died r{u["start PT death"]}, theirs r{t["start PT death"]} | spawns S/M/X {u["spawned S r100"]}/{u["spawned M r100"]}/{u["spawned X r100"]} vs '
          f'{t["spawned S r100"]}/{t["spawned M r100"]}/{t["spawned X r100"]}')

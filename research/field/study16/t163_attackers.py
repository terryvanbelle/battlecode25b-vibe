"""Topic 163: why their towers kill twice as many of our attackers (t162: attackers killed by the tower per assault,
ours 0.24 / theirs 0.55 in losses, 0.30 / 0.57 in wins).  Soldier.siege kites: step in (d2 <= 9), hit, step out when
the attack is spent and the move is still free; there is no hit-point rule.
An attack run = one robot's damage rows on one tower, grouped while the gap is under 15 rounds.  From the turns rows:
the robot's hit points and paint at its first and last hit, whether it died within 5 rounds after its last hit and to
what (the tower it hit / another tower / a robot / starved), and, when it lived, its hit points at the last hit (where
it gave up or the tower fell).  Runs that end with the tower's death are counted apart ('tower fell').
Also: our robots and theirs killed by tower fire per game (a 'die' row whose actor is a tower), and the turns a robot
of each side spends ending its turn inside an enemy tower's range (d2 <= 9 of a standing enemy tower; turns rows).
Per side of the attacker, losses then wins."""
from collections import defaultdict
import lib


def analyse(G, S):
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    life = defaultdict(dict)    # robot id -> round -> (hp, paint, x, y)
    towers_at = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.BOT: life[t[1]][t[0]] = (t[6], t[7], t[4], t[5])
        else: towers_at[t[0]].append((t[2], t[4], t[5]))
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1], a[3])
    runs = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.BOT:
            v = int(a[5])
            if G.typ.get(v) in lib.TOW: runs[(a[1], v)].append(a[0])
    for (rid, tid), rs in runs.items():
        rs.sort()
        groups = []
        for r in rs:
            if groups and r - groups[-1][-1] < 15: groups[-1].append(r)
            else: groups.append([r])
        side = 'us' if G.team.get(rid) == G.us else 'them'
        typ = G.typ.get(rid)
        td = deaths.get(tid)
        for g in groups:
            r0, r1 = g[0], g[-1]
            L = life[rid]
            a0 = L.get(r0) or L.get(r0 - 1); a1 = L.get(r1) or L.get(r1 - 1)
            if not a0 or not a1: continue
            fell = td is not None and r0 <= td[0] <= r1 + 1
            d = deaths.get(rid)
            if d and r0 <= d[0] <= r1 + 5:
                if d[1] == tid: how = 'tower'
                elif d[1] == rid: how = 'starved'
                elif d[2] in lib.TOW: how = 'other tower'
                else: how = 'robot'
            else: how = None
            e = dict(typ=typ, hits=len(g), hp0=a0[0], hp1=a1[0], p0=a0[1], p1=a1[1], how=how, fell=fell)
            S[side].append(e)
    for a in G.acts:
        if a[4] == 'die' and a[3] in lib.TOW and a[7] in lib.BOT:
            v = int(a[5])
            S['killed_' + ('us' if G.team.get(v) == G.us else 'them')].append(a[7])
    # robot turns ending inside a standing enemy tower's range
    for rid, L in life.items():
        tm = G.team.get(rid)
        sd = 'us' if tm == G.us else 'them'
        for r, (hp, p, x, y) in L.items():
            S['turns_' + sd].append(0)
            if any(tt != tm and (x - tx) ** 2 + (y - ty) ** 2 <= 9 for (tt, tx, ty) in towers_at.get(r, ())):
                S['inrange_' + sd].append(hp)


for which in ('lost', 'won'):
    S = defaultdict(list)
    ng = 0
    for G in lib.games(which):
        ng += 1
        analyse(G, S)
    print(f'\n== {which}: {ng} games; attack runs on towers by robots of each side')
    for side in ('us', 'them'):
        es = S[side]
        for typ in ('SOLDIER', 'SPLASHER'):
            E = [e for e in es if e['typ'] == typ]
            if not E: continue
            for sub, cond in (('tower stood', False), ('tower fell', True)):
                F = [e for e in E if e['fell'] == cond]
                if not F: continue
                n = len(F)
                died = [e for e in F if e['how']]
                lived = [e for e in F if not e['how']]
                print(f'  {side:4s} {typ.lower():8s} {sub:11s} runs {n / ng:5.1f}/game  hits {lib.med([e["hits"] for e in F])}  '
                      f'hp at first hit {lib.med([e["hp0"] for e in F])}  paint at first {lib.med([e["p0"] for e in F])} last {lib.med([e["p1"] for e in F])}')
                print(f'       died after it {100 * len(died) / n:3.0f}% (tower {100 * sum(1 for e in died if e["how"] == "tower") / n:.0f}%, '
                      f'other tower {100 * sum(1 for e in died if e["how"] == "other tower") / n:.0f}%, robot {100 * sum(1 for e in died if e["how"] == "robot") / n:.0f}%, '
                      f'starved {100 * sum(1 for e in died if e["how"] == "starved") / n:.0f}%);  lived: hp at last hit med {lib.med([e["hp1"] for e in lived])}, '
                      f'under 100 {100 * sum(1 for e in lived if e["hp1"] < 100) / max(1, len(lived)):.0f}%, paint at last hit med {lib.med([e["p1"] for e in lived])}')
    for side in ('us', 'them'):
        k = S['killed_' + side]
        ir = S['inrange_' + side]
        print(f'  {side}: robots killed by tower fire {len(k) / ng:.1f}/game (S {sum(1 for x in k if x == "SOLDIER") / ng:.1f}, '
              f'X {sum(1 for x in k if x == "SPLASHER") / ng:.1f}, M {sum(1 for x in k if x == "MOPPER") / ng:.1f});  turns ending in enemy tower range '
              f'{len(ir) / ng:.0f}/game = {100 * len(ir) / max(1, len(S["turns_" + side])):.1f}% of robot-turns, hp then med {lib.med(ir)}')


# hit points at each hit of a run on a tower that stood: does the attacker keep hitting at low hit points?
print('\n== soldiers\' hits on towers that stood, by the attacker\'s hit points at the hit (turn row of that round)')
for which in ('lost', 'won'):
    C = {'us': defaultdict(int), 'them': defaultdict(int)}
    D = {'us': defaultdict(int), 'them': defaultdict(int)}
    ng = 0
    for G in lib.games(which):
        ng += 1
        life = defaultdict(dict)
        for t in G.turns:
            if t[3] == 'SOLDIER': life[t[1]][t[0]] = t[6]
        deaths = {}
        for a in G.acts:
            if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1])
        last = {}
        for a in G.acts:
            if a[4] == 'damage' and a[3] == 'SOLDIER' and G.typ.get(int(a[5])) in lib.TOW:
                v = int(a[5]); td = deaths.get(v)
                if td and td[0] <= a[0] + 1: continue
                hp = life[a[1]].get(a[0])
                if hp is None: continue
                sd = 'us' if a[2] == G.us else 'them'
                b = min(250, (hp // 50) * 50)
                C[sd][b] += 1
                d = deaths.get(a[1])
                if d and d[1] == v and d[0] - a[0] <= 5: D[sd][b] += 1
    print(f'  {which}: hits per game in each hit-point band (share of them followed by the soldier\'s death to that tower within 5 rounds)')
    for sd in ('us', 'them'):
        print(f'    {sd:4s} ' + '  '.join(f'{b:3d}-{b + 49:3d}: {C[sd][b] / ng:5.1f} ({100 * D[sd][b] / max(1, C[sd][b]):2.0f}%)' for b in (0, 50, 100, 150, 200, 250)))

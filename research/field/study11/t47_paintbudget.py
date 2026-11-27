"""Topic 47: the paint budget per side and phase (median per game), lost vs won games.
IN:  paint-tower income (5/10/15 by level + 3 per SRP, per tower turn), 500 per completed tower (incl. churn
     rebuilds), +5 per mopper attack on an enemy robot.
UNIT SPENDING: spawn cost moved into new robots (S 200, X 300, M 100); soldier tile paints x5, soldier hits on
     towers x5, tower-pattern marks x25 (one per 24-tile mark burst), splashes x50.
LOSSES: drained by enemy moppers (drain rows), passive end-of-turn drain approximated from the tile under the robot at
     round end (neutral 1, enemy 2), paint still held by robots when they died.
Also tiles painted per 100 paint spent by robots (soldier + splasher), and tiles held at the phase end."""
import lib
from collections import defaultdict, Counter
PH = ((1, 100), (101, 200), (201, 300))
PR = {1: 5, 2: 10, 3: 15}
COSTP = {'SOLDIER': 200, 'SPLASHER': 300, 'MOPPER': 100}
for which in ('lost', 'won'):
    S = defaultdict(list)
    for G in lib.games(which):
        lvl = defaultdict(lambda: 1)
        for a in G.acts:
            if a[4] == 'startlevel': lvl[int(a[5])] = 2
        M = defaultdict(Counter)    # (side, phase) -> metric
        def ph_of(r):
            for i, (lo, hi) in enumerate(PH):
                if lo <= r <= hi: return i
            return None
        srp = {i + 1: (int(R['srpA']), int(R['srpB'])) for i, R in enumerate(G.rounds)}
        # income from paint towers (level tracked through upgrades in file order by round)
        ups = defaultdict(list)
        for a in G.acts:
            if a[4] == 'upgrade': ups[a[0]].append((int(a[5]), int(a[6])))
        bt = lib.by_round_turns(G)
        for r in range(1, G.end + 1):
            for (tid, L) in ups.get(r, ()): lvl[tid] = L
            p = ph_of(r)
            if p is None: continue
            for t in bt.get(r, ()):
                if t[3] == 'PAINT_TOWER': M[(t[2], p)]['in: paint towers'] += PR[lvl[t[1]]] + 3 * srp[r][t[2] - 1]
        markburst = Counter()
        last = {}
        for t in G.turns:
            if t[3] in lib.BOT: last[t[1]] = t
        for a in G.acts:
            p = ph_of(a[0])
            if p is None: continue
            sd, k = a[2], a[4]
            if k == 'build': M[(sd, p)]['in: new towers x500'] += 500
            elif k == 'spawn' and a[6] in COSTP: M[(sd, p)]['spawned into robots'] += COSTP[a[6]]
            elif k == 'attack' and a[3] == 'MOPPER': M[(sd, p)]['in: mopper +5'] += 5
            elif k == 'paint' and a[3] == 'SOLDIER': M[(sd, p)]['spent: soldier tiles'] += 5; M[(sd, p)]['tiles painted'] += 1
            elif k == 'paint' and a[3] == 'SPLASHER': M[(sd, p)]['tiles painted'] += 1
            elif k == 'attack' and a[3] == 'SOLDIER': M[(sd, p)]['spent: soldier tower hits'] += 5
            elif k == 'mark' and a[3] in lib.BOT: markburst[(a[0], a[1])] += 1
            elif k == 'splash': M[(sd, p)]['spent: splashes'] += 50
            elif k == 'drain':
                v = int(a[5]); vs = G.team.get(v)
                if vs: M[(vs, p)]['lost: drained by enemy moppers'] += int(a[6])
            elif k == 'die' and a[7] in lib.BOT:
                v = int(a[5]); vs = G.team.get(v); lt = last.get(v)
                if vs and lt: M[(vs, p)]['lost: paint held at death'] += lt[7]
        for (r, i), n in markburst.items():
            p = ph_of(r)
            if n >= 20 and p is not None: M[(G.team.get(i), p)]['spent: pattern marks'] += 25
        # passive drain from the tile under each robot at round end
        cur = [0]; grid_at = {}
        def hook(a, grid):
            if a[0] != cur[0]:
                for r in range(cur[0], a[0]):
                    for t in bt.get(r, ()):
                        if t[3] not in lib.BOT: continue
                        o = lib.owner(grid[t[4] + t[5] * G.W]); p = ph_of(r)
                        if p is None: continue
                        if o == 0: M[(t[2], p)]['lost: passive (neutral 1, enemy 2)'] += 1
                        elif o != t[2]: M[(t[2], p)]['lost: passive (neutral 1, enemy 2)'] += 2
                cur[0] = a[0]
        lib.replay_grid(G, hook)
        for i, (lo, hi) in enumerate(PH):
            if G.end < hi: continue
            for sd in (G.us, G.op):
                w = 'us' if sd == G.us else 'them'
                m = M[(sd, i)]
                spent = m['spent: soldier tiles'] + m['spent: splashes']
                m['tiles painted per 100 paint (S+X)'] = round(100 * m['tiles painted'] / max(1, spent), 1)
                for k in set(m) | {'in: paint towers', 'in: new towers x500', 'in: mopper +5', 'spawned into robots', 'spent: soldier tiles',
                                   'spent: soldier tower hits', 'spent: pattern marks', 'spent: splashes', 'lost: drained by enemy moppers',
                                   'lost: passive (neutral 1, enemy 2)', 'lost: paint held at death', 'tiles painted'}:
                    S[(w, i, k)].append(m[k])
    print(f'== {which} games: medians per game, us | them')
    keys = sorted(set(k for (_, _, k) in S))
    print(f'{"":42s}' + ''.join(f'{f"r{lo}-{hi}":>20s}' for lo, hi in PH))
    for k in keys:
        print(f'{k:42s}' + ''.join(f'{str(lib.med(S[("us", i, k)])) + " | " + str(lib.med(S[("them", i, k)])):>20s}' for i in range(len(PH))))

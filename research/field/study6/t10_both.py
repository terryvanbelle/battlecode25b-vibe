"""Topic 10: both sides side by side.  Tower builds/losses (killed by enemy damage vs vanished w/o enemy damage),
soldier paint state, idle/stuck robots, spawns by phase, paint actions & transfers, marks that never completed."""
import lib
from collections import Counter, defaultdict
PH = ((1, 50), (51, 100), (101, 150), (151, 200), (201, 300), (301, 999))
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    b, d = lib.tower_events(G)
    side = {G.us: 'US', G.op: 'TH'}
    print(f'== m{G.m} g{G.g} {G.team_name} {G.map} end r{G.end}')
    # damage on towers by enemy robots
    lastdmg = {}
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.BOT:
            tid = int(a[5])
            if G.typ.get(tid) in lib.TOW and G.team.get(tid) != a[2]:
                lastdmg.setdefault(tid, []).append(a[0])
    for sd in (G.us, G.op):
        nm = side[sd]
        bl = [x for x in b if x[3] == sd and x[0] > 0]
        dl = [x for x in d if x[3] == sd]
        killed = [x for x in dl if any(x[0] - 6 <= r <= x[0] for r in lastdmg.get(x[1], []))]
        vanished = [x for x in dl if x not in killed]
        cb = lambda R: sum(1 for x in bl if x[0] <= R)
        print(f'  {nm} builds by r50/100/150/200: {cb(50)}/{cb(100)}/{cb(150)}/{cb(200)} total {len(bl)} types {dict(Counter(x[2][0] for x in bl))}')
        print(f'     killed by enemy: {len(killed)} at {[(x[0], x[2][0]) for x in killed][:14]}')
        print(f'     vanished w/o enemy damage (disintegrate): {len(vanished)} at {[(x[0], x[2][0]) for x in vanished][:14]}')
        S[nm]['first tower killed'].append(killed[0][0] if killed else None)
        S[nm]['towers killed by r150'].append(sum(1 for x in killed if x[0] <= 150))
        S[nm]['builds by r100'].append(cb(100)); S[nm]['builds by r200'].append(cb(200))
        S[nm]['disintegrations'].append(len(vanished))
        # soldier paint state
        st = [t for t in G.turns if t[2] == sd and t[3] == 'SOLDIER']
        if st:
            z = sum(1 for t in st if t[7] == 0) / len(st); lo = sum(1 for t in st if t[7] < 40) / len(st)
            S[nm]['soldier turns paint==0 %'].append(round(100 * z)); S[nm]['soldier turns paint<40 %'].append(round(100 * lo))
            S[nm]['soldier median paint'].append(lib.med([t[7] for t in st]))
        # stuck: robot whose position over 25 consecutive own turns stays within chebyshev 2 (not adjacent to own tower ignored)
        pos = defaultdict(list)
        for t in G.turns:
            if t[2] == sd and t[3] in lib.BOT: pos[t[1]].append((t[0], t[4], t[5], t[7], t[3]))
        stuck = 0; stuckturns = 0; tot = 0; samp = []
        for i, L in pos.items():
            tot += len(L)
            j = 0
            for k in range(len(L)):
                while max(abs(L[k][1] - L[j][1]), abs(L[k][2] - L[j][2])) > 2 or k - j > 25: j += 1
                if k - j == 25:
                    stuckturns += 1
                    if len(samp) < 6 and (not samp or samp[-1][0] != i): samp.append((i, L[k][4][:3], L[k][0], L[k][1], L[k][2], L[k][3]))
            # count robots
        S[nm]['robot-turns in a 25-turn 5x5 box %'].append(round(100 * stuckturns / max(1, tot), 1))
        print(f'     stuck robot-turns (25 turns within 5x5): {stuckturns}/{tot}  e.g. (id type round x y paint) {samp[:5]}')
        # spawns by phase
        sp = [a for a in G.acts if a[4] == 'spawn' and a[2] == sd]
        row = []
        for lo_, hi in PH:
            if lo_ > G.end: break
            c = Counter(a[6] for a in sp if lo_ <= a[0] <= hi); row.append(f"{lo_}-{hi}:{c['SOLDIER']}/{c['SPLASHER']}/{c['MOPPER']}")   # study 6: exact names (MO also matched MONEY_TOWER builds)
        print('     spawns S/X/M by phase:', ' '.join(row))
        S[nm]['soldiers spawned r1-100'].append(sum(1 for a in sp if a[0] <= 100 and a[6] == 'SOLDIER'))
        S[nm]['moppers spawned r1-100'].append(sum(1 for a in sp if a[0] <= 100 and a[6] == 'MOPPER'))
        # paint actions & transfers (tower->robot withdrawal = robot transfer negative amount)
        pa = [a for a in G.acts if a[4] == 'paint' and a[2] == sd]
        S[nm]['paint actions r1-100'].append(sum(1 for a in pa if a[0] <= 100))
        S[nm]['paint actions r101-200'].append(sum(1 for a in pa if 100 < a[0] <= 200))
        wd = [a for a in G.acts if a[4] == 'transfer' and a[2] == sd and a[3] in lib.BOT and int(a[6]) < 0]
        S[nm]['paint withdrawn r1-200'].append(-sum(int(a[6]) for a in wd if a[0] <= 200))
        # marks per ruin & completion
        mk = defaultdict(set)
        for a in G.acts:
            if a[4] == 'mark' and a[2] == sd:
                x, y = map(int, a[5].split(','))
                rr = min(G.ruins, key=lambda r: (r[0] - x) ** 2 + (r[1] - y) ** 2)
                if max(abs(rr[0] - x), abs(rr[1] - y)) <= 2: mk[rr].add(a[0])
        built_at = set((x[4], x[5]) for x in bl)
        never = [(r, min(v)) for r, v in mk.items() if r not in built_at]
        S[nm]['ruins marked'].append(len(mk)); S[nm]['marked never built'].append(len(never))
        print(f'     ruins marked {len(mk)}, never built {len(never)}: {sorted(never, key=lambda z: z[1])[:8]}')
print('\n== summary (med, all games)')
for nm in ('US', 'TH'):
    print(' ', nm)
    for k, v in S[nm].items(): print(f'     {k:<36} med {lib.med(v)}  {v}')

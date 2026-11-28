"""Topic 149: how towers fall (new angle on study 12's "towers destroyed: ours 11.7 a loss, theirs 6.1").
Every tower killed by damage (a 'die' row whose victim is a tower; the actor is the killer).  Per side whose tower
fell, phase (r1-100 / r101-200 / r201+), losses then wins:
  killed            towers killed per game; by paint / money / defense; mean level
  killer            the killing blow by soldier / splasher (robots are the only tower killers besides towers)
  attackers         distinct enemy robots that damaged the tower in its last 30 rounds, and their types
  siege length      rounds from the first hit of the final assault (hits with gaps under 15 rounds) to the death
  hp share          the share of the damage done by soldiers / splashers in that assault
  defenders         own robots (and own moppers) within r2 20 of the tower when it died; enemy robots there
  tower fire        hits the tower itself landed in that assault (its single + area attacks with a damage row),
                    robots it killed in it
  age               rounds from completion (or r0 for the starting towers) to death
  retaken           ruins of the killed towers rebuilt later by the same side / by the killers (by the game's end)
Also the first kill each way (median round) and how many games had a kill on us by r100."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def analyse(G, S, P):
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    lev = defaultdict(list)
    born = {}
    for a in G.acts:
        if a[4] == 'startlevel': lev[int(a[5])].append((0, int(a[6]))); born[int(a[5])] = 0
        elif a[4] == 'build': lev[int(a[5])].append((a[0], 1)); born[int(a[5])] = a[0]
        elif a[4] == 'upgrade': lev[int(a[5])].append((a[0], int(a[6])))
    dmg = defaultdict(list)    # tower id -> [(round, attacker id, attacker type, hp)]
    tfire = defaultdict(list)  # tower id -> [(round, victim id)] hits by the tower
    kills_by = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage':
            tgt = int(a[5])
            if G.typ.get(tgt) in lib.TOW and a[3] in lib.BOT: dmg[tgt].append((a[0], a[1], a[3], int(a[6] or 0)))
            elif a[3] in lib.TOW: tfire[a[1]].append((a[0], tgt))
        elif a[4] == 'die' and a[3] in lib.TOW and a[7] in lib.BOT:
            kills_by[a[1]].append(a[0])
    byround = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.BOT: byround[t[0]].append(t)
    builds = [(a[0], int(a[5]), a[2]) for a in G.acts if a[4] == 'build']
    first = {G.us: None, G.op: None}
    for a in G.acts:
        if a[4] != 'die' or a[7] not in lib.TOW: continue
        r, killer, kt = a[0], a[1], a[3]
        v = int(a[5]); vt = a[7]; side_of_tower = G.team.get(v)
        if side_of_tower is None: continue
        if first[side_of_tower] is None: first[side_of_tower] = r
        p = ph(r)
        if p is None: continue
        side = 'us' if side_of_tower == G.us else 'them'
        D = S[(side, p)]
        D['killed'] += 1
        D['kind_' + vt] += 1
        L = 1
        for rr, l in sorted(lev.get(v, ())):
            if rr <= r: L = l
        D['level'] += L
        D['killer_' + kt] += 1
        hits = [h for h in dmg.get(v, ()) if r - 30 <= h[0] <= r]
        D['attackers'] += len(set(h[1] for h in hits))
        for ty in lib.BOT: D['att_' + ty] += len(set(h[1] for h in hits if h[2] == ty))
        # final assault: walk back from the death while the gap between hits stays under 15 rounds
        allh = sorted(dmg.get(v, ()))
        start = r
        for h in reversed(allh):
            if h[0] > r: continue
            if start - h[0] < 15: start = h[0]
            else: break
        D['siege_len'] += r - start
        ass = [h for h in allh if start <= h[0] <= r]
        tot = sum(h[3] for h in ass) or 1
        D['hp_SOLDIER'] += sum(h[3] for h in ass if h[2] == 'SOLDIER') / tot
        D['hp_SPLASHER'] += sum(h[3] for h in ass if h[2] == 'SPLASHER') / tot
        D['tfire'] += sum(1 for f in tfire.get(v, ()) if start <= f[0] <= r)
        D['tkills'] += sum(1 for k in kills_by.get(v, ()) if start <= k <= r)
        tx, ty_ = pos.get(v, (-99, -99))
        own = opp = ownm = 0
        for t in byround.get(r, ()):
            if (t[4] - tx) ** 2 + (t[5] - ty_) ** 2 <= 20:
                if t[2] == side_of_tower:
                    own += 1
                    if t[3] == 'MOPPER': ownm += 1
                else: opp += 1
        D['defenders'] += own; D['def_moppers'] += ownm; D['enemies_near'] += opp
        if own == 0: D['undefended'] += 1
        D['age'] += r - born.get(v, 0)
        later = [b for b in builds if b[0] > r and pos.get(b[1]) == (tx, ty_)]
        if later:
            if later[0][2] == side_of_tower: D['retaken_own'] += 1
            else: D['taken_enemy'] += 1
    P['games'] += 1
    P['first_us'].append(first[G.us]); P['first_them'].append(first[G.op])
    P['kill_us_by100'] += 1 if first[G.us] and first[G.us] <= 100 else 0
    P['kill_them_by100'] += 1 if first[G.op] and first[G.op] <= 100 else 0


ROWS = (('killed', 'towers killed per game', 'g'), ('kind_PAINT_TOWER', '  paint towers', 'g'), ('kind_MONEY_TOWER', '  money towers', 'g'),
        ('kind_DEFENSE_TOWER', '  defense towers', 'g'), ('level', 'mean level', 'k'),
        ('killer_SOLDIER', 'killing blow by a soldier', 'k%'), ('killer_SPLASHER', 'killing blow by a splasher', 'k%'),
        ('attackers', 'distinct attackers, last 30 rounds', 'k'), ('att_SOLDIER', '  soldiers', 'k'), ('att_SPLASHER', '  splashers', 'k'),
        ('siege_len', 'final assault, rounds', 'k'), ('hp_SOLDIER', 'damage share: soldiers', 'k%'), ('hp_SPLASHER', 'damage share: splashers', 'k%'),
        ('tfire', 'hits by the tower in the assault', 'k'), ('tkills', 'robots it killed in the assault', 'k'),
        ('defenders', 'own robots within r2 20 at death', 'k'), ('def_moppers', '  of them moppers', 'k'),
        ('undefended', 'no own robot within r2 20', 'k%'), ('enemies_near', 'enemy robots within r2 20 at death', 'k'),
        ('age', 'age at death, rounds', 'k'), ('retaken_own', 'ruin rebuilt later by the same side', 'k%'),
        ('taken_enemy', 'ruin taken later by the killers', 'k%'))

for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); P = defaultdict(int); P['first_us'] = []; P['first_them'] = []
    for G in lib.games(which):
        analyse(G, S, P)
    n = P['games']
    print(f'\n== {which}: {n} games.  First tower kill on us: median r{lib.med(P["first_us"])} (by r100 in {P["kill_us_by100"]} games); '
          f'on them: r{lib.med(P["first_them"])} (by r100 in {P["kill_them_by100"]})')
    print(f'   {"towers of":40s}' + ''.join(f'{PHN[p] + " us":>14s}{"them":>8s}' for p in range(3)))
    for k, name, how in ROWS:
        cells = ''
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, p)]
                if how == 'g': v = D[k] / max(1, n); s = f'{v:.2f}'
                elif how == 'k': v = D[k] / max(1, D['killed']); s = f'{v:.2f}'
                else: v = 100 * D[k] / max(1, D['killed']); s = f'{v:.0f}%'
                cells += f'{s:>14s}' if side == 'us' else f'{s:>8s}'
        print(f'   {name:40s}' + cells)

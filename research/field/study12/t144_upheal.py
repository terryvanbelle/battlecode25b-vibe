"""Topic 144: tower upgrades as a heal, and the towers we lose while rich (new).  An upgrade keeps the damage taken
(new hp = new max - (old max - old hp)), so on a damaged tower it is +500 hp for 2500 (L2) or 5000 (L3) chips, done by
the tower itself or by any allied robot within r2 2, in a turn, with no cooldown.
Part 1, every upgrade (not the starting towers' 'startlevel'): who did it (the tower / a robot), the level, the hp
before it (hp after - 500), whether the tower had been hit in the 10 rounds before ('under fire'), per side; and the
upgraded towers' fate (destroyed later / alive at the end).
Part 2, every tower destroyed by damage: its side, type and level at death; its final siege (the run of damage rows
with gaps under 10 rounds that ended in its death): length in rounds, damage, number of distinct attackers; the
owner's chips at the siege start and the most it held during the siege; whether an upgrade was affordable at some
point of the siege (chips >= the next level's cost, L1 -> L2 2500, L2 -> L3 5000, and the tower not yet L3), and
how many rounds the +500 hp would have bought at the siege's damage rate.
Losses then wins, our towers and theirs."""
from collections import defaultdict
import lib

UPC = {1: 2500, 2: 5000}


def run(G, U, K):
    side = lambda team: 'us' if team == G.us else 'them'
    dmg = defaultdict(list)    # tower id -> [(round, amount, attacker id)]
    for a in G.acts:
        if a[4] == 'damage' and G.typ.get(int(a[5])) in lib.TOW:
            dmg[int(a[5])].append((a[0], int(a[6] or 0), a[1]))
    level = {}
    lastr = {}
    for t in G.turns:
        if t[3] in lib.TOW: lastr[t[1]] = t[0]
    died = {}
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.TOW: died[int(a[5])] = a[0]
    for a in G.acts:
        if a[4] == 'startlevel': level[int(a[5])] = 2
        elif a[4] == 'build': level[int(a[5])] = 1
        elif a[4] == 'upgrade':
            tid = int(a[5]); r = a[0]
            lv = int(a[6]) if a[6] else level.get(tid, 1) + 1
            level[tid] = lv
            s = side(G.team.get(tid))
            U[(s, 'n')] += 1
            U[(s, 'by_' + ('tower' if a[1] == tid else 'robot'))] += 1
            U[(s, 'to_L%d' % lv)] += 1
            fire = sum(x[1] for x in dmg.get(tid, ()) if r - 10 <= x[0] <= r)
            if fire > 0: U[(s, 'under_fire')] += 1
            if tid in died: U[(s, 'died_later')] += 1
    # hp before each upgrade: the tower's hp at the end of its previous turn (lib.load keeps no column d)
    hp_by = {}
    for t in G.turns:
        if t[3] in lib.TOW: hp_by[(t[0], t[1])] = t[6]
    for a in G.acts:
        if a[4] == 'upgrade':
            tid = int(a[5]); r = a[0]; s = side(G.team.get(tid))
            lv = int(a[6]) if a[6] else 2
            mx_before = {2: 1000, 3: 1500}.get(lv, 1000)
            hp_prev = hp_by.get((r - 1, tid))
            if hp_prev is not None:
                U[(s, 'hp_known')] += 1
                if hp_prev < mx_before: U[(s, 'damaged')] += 1
                U[(s, 'missing_hp')] += mx_before - hp_prev
    # part 2: towers destroyed
    for tid, rd in died.items():
        team = G.team.get(tid); s = side(team)
        L = sorted(dmg.get(tid, ()))
        if not L: continue
        start = L[-1][0]
        for j in range(len(L) - 1, 0, -1):
            if L[j][0] - L[j - 1][0] < 10: start = L[j - 1][0]
            else: break
        siege = [x for x in L if x[0] >= start]
        n = rd - start + 1
        total = sum(x[1] for x in siege)
        att = len(set(x[2] for x in siege))
        lv = level.get(tid, 1)
        chips = [lib.money(G, team, r) for r in range(max(1, start - 1), rd)]
        afford = lv < 3 and any(c >= UPC[lv] for c in chips)
        D = K[s]
        D['n'] += 1; D['L%d' % lv] += 1
        D['len'].append(n); D['dmg'].append(total); D['att'].append(att)
        D['chips0'].append(chips[0] if chips else 0); D['chipsmax'].append(max(chips) if chips else 0)
        if afford:
            D['afford'] += 1
            rate = total / max(1, n)
            D['bought'].append(500 / max(1, rate))
        D['type_' + G.typ.get(tid, '?')] += 1


for which in ('lost', 'won'):
    U = defaultdict(int); K = defaultdict(lambda: defaultdict(lambda: 0))
    for s in ('us', 'them'):
        for k in ('len', 'dmg', 'att', 'chips0', 'chipsmax', 'bought'): K[s][k] = []
    ng = 0
    for G in lib.games(which):
        run(G, U, K); ng += 1
    print(f'== {which} games: {ng}')
    print('   part 1, upgrades per game:')
    for s in ('us', 'them'):
        n = U[(s, 'n')]
        print(f'      {s:4s}: {n / max(1, ng):5.2f} per game; by the tower {U[(s, "by_tower")]}, by a robot {U[(s, "by_robot")]};'
              f' to L2 {U[(s, "to_L2")]}, to L3 {U[(s, "to_L3")]}; under fire (hit in the 10 rounds before) {U[(s, "under_fire")]};'
              f' damaged before ({U[(s, "damaged")]} of {U[(s, "hp_known")]}, mean missing hp {U[(s, "missing_hp")] / max(1, U[(s, "hp_known")]):.0f});'
              f' destroyed later {U[(s, "died_later")]}')
    print('   part 2, towers destroyed by damage:')
    for s in ('us', 'them'):
        D = K[s]
        if not D['n']: continue
        print(f'      {s:4s} towers: {D["n"]} ({D["n"] / ng:.2f} per game); level at death L1 {D["L1"]}, L2 {D["L2"]}, L3 {D["L3"]};'
              f' types paint {D["type_PAINT_TOWER"]}, money {D["type_MONEY_TOWER"]}, defense {D["type_DEFENSE_TOWER"]}')
        print(f'            final siege: median {lib.med(D["len"])} rounds, {lib.med(D["dmg"])} damage, {lib.med(D["att"])} attackers;'
              f' owner chips at its start median {lib.med(D["chips0"])}, max during it {lib.med(D["chipsmax"])}')
        print(f'            an upgrade was affordable during the siege for {D["afford"]} of {D["n"]} ({100 * D["afford"] / D["n"]:.0f}%);'
              f' +500 hp would have bought a median {lib.med(D["bought"])} rounds (p25 {lib.pct(D["bought"], .25)}, p75 {lib.pct(D["bought"], .75)})')

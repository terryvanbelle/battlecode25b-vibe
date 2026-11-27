"""Topic 82: the exchange between towers and robots, both sides, lost vs won games, by phase.
Robots deal HP damage only to towers; towers deal HP damage only to robots (RULES 4.1).  Per side and phase, medians per
game: enemy robots killed by the side's towers ('die' rows whose actor is a tower), own robots dead at 0 paint (actor =
victim), HP damage the side's towers dealt to robots, HP damage the side's robots dealt to towers (soldier / splasher),
enemy towers killed, and the side's tower-turns with an enemy robot within d2 <= 9 (in a L1 tower's attack range)
on which the tower dealt no damage.  Also: robots killed per tower killed, and per game the round of the side's first
tower kill and first tower loss."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 300), (301, 2000))
def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return 3

for which in ('lost', 'won'):
    S = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        C = defaultdict(int)
        for a in G.acts:
            k = a[4]; r = a[0]; p = ph(r)
            if a[2] not in (1, 2): continue
            side = 'us' if a[2] == G.us else 'them'
            if k == 'damage':
                if a[3] in lib.TOW: C[(side, p, 'tower dmg to robots')] += int(a[6])
                elif a[3] == 'SOLDIER': C[(side, p, 'soldier dmg to towers')] += int(a[6])
                elif a[3] == 'SPLASHER': C[(side, p, 'splasher dmg to towers')] += int(a[6])
            elif k == 'die':
                vt = a[7]; vid = int(a[5])
                if vt in lib.BOT:
                    if a[1] == vid: C[('us' if G.team.get(vid) == G.us else 'them', p, 'robots dead at 0 paint')] += 1
                    elif a[3] in lib.TOW: C[(side, p, 'robots killed by towers')] += 1
                elif vt in lib.TOW and a[3] in lib.BOT:
                    C[(side, p, 'towers killed')] += 1
        # idle tower-turns with an enemy robot in range
        bt = lib.by_round_turns(G)
        dealt = set((a[0], a[1]) for a in G.acts if a[4] == 'damage' and a[3] in lib.TOW)
        for r, ts in bt.items():
            bots = defaultdict(list)
            for t in ts:
                if t[3] in lib.BOT: bots[t[2]].append((t[4], t[5]))
            for t in ts:
                if t[3] not in lib.TOW: continue
                side = 'us' if t[2] == G.us else 'them'
                en = bots[3 - t[2]]
                if any(lib.d2((t[4], t[5]), q) <= 9 for q in en):
                    C[(side, ph(r), 'tower-turns enemy in range')] += 1
                    if (r, t[1]) not in dealt: C[(side, ph(r), '... of which no damage dealt')] += 1
        for side in ('us', 'them'):
            for p in range(4):
                if PH[p][0] > G.end: continue
                for m in ('robots killed by towers', 'robots dead at 0 paint', 'tower dmg to robots', 'soldier dmg to towers',
                          'splasher dmg to towers', 'towers killed', 'tower-turns enemy in range', '... of which no damage dealt'):
                    S[(side, p, m)].append(C[(side, p, m)])
    print(f'== {which} games ({n}); medians per game (games that reached the phase), us / them')
    ms = ('robots killed by towers', 'robots dead at 0 paint', 'tower dmg to robots', 'soldier dmg to towers',
          'splasher dmg to towers', 'towers killed', 'tower-turns enemy in range', '... of which no damage dealt')
    print('   ' + 'metric'.ljust(32) + ''.join(f'r{a}-{b}'.rjust(16) for a, b in PH))
    for m in ms:
        print('   ' + m.ljust(32) + ''.join(f'{lib.med(S[("us", p, m)])} / {lib.med(S[("them", p, m)])}'.rjust(16) for p in range(4)))
    print('   sums: ' + '; '.join(f'{m}: {sum(S[("us", p, m)][i] for p in range(4) for i in range(len(S[("us", p, m)])))} / '
                               f'{sum(S[("them", p, m)][i] for p in range(4) for i in range(len(S[("them", p, m)])))}' for m in ms[:6]))
    print()

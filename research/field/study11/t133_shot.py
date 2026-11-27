"""Topic 133: what our robots are doing when enemy towers shoot them (t131: in r1-200 of the losses their towers kill
262 of our robots and ours 138 of theirs; t129: by r150 their towers have killed a median 3 of ours, ours 1 of theirs).
Every HP 'damage' row by a tower on a robot is charged to what the victim did that round or the round before (first
match): 'hit tower' (an 'attack' row: soldiers attack only towers), 'splash', 'mop/drain', 'ruin paint' (a paint row on
a tile within Chebyshev 2 of a ruin), 'paint' (other paint rows), 'withdraw' (a transfer), else 'move only' (walked or
stood).  Per side whose robots are hit, phase r1-100 / r101-200 / r201-400 and robot type: HP taken (sum), share by
activity, and robots that died within 3 rounds of a tower hit ('die' by a tower, or starved).  Lost and won games."""
import lib
from collections import defaultdict, Counter

PH = ((1, 100), (101, 200), (201, 400))
ACTS = ('hit tower', 'splash', 'mop/drain', 'ruin paint', 'paint', 'withdraw', 'move only')


def analyse(G, HP, DEAD, ACT):
    near = set()
    for (x, y) in G.ruins:
        for dx in range(-2, 3):
            for dy in range(-2, 3): near.add((x + dx, y + dy))
    did = defaultdict(set)
    for a in G.acts:
        k = a[4]
        if k == 'attack' and a[3] in lib.BOT: did[(a[0], a[1])].add('hit tower')
        elif k == 'splash': did[(a[0], a[1])].add('splash')
        elif k in ('mop', 'drain'): did[(a[0], a[1])].add('mop/drain')
        elif k == 'paint' and a[3] in lib.BOT:
            x, y = map(int, a[5].split(','))
            did[(a[0], a[1])].add('ruin paint' if (x, y) in near else 'paint')
        elif k == 'transfer': did[(a[0], a[1])].add('withdraw')
    lasthit = {}
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.TOW:
            v = int(a[5]); vt = G.typ.get(v)
            if vt not in lib.BOT or a[0] > 400: continue
            side = G.team.get(v); who = 'us' if side == G.us else 'them'
            ph = next(j for j, (lo, hi) in enumerate(PH) if lo <= a[0] <= hi)
            s = did.get((a[0], v), set()) | did.get((a[0] - 1, v), set())
            act = next((x for x in ACTS if x in s), 'move only')
            dmg = int(a[6] or 0)
            HP[(who, ph, vt)] += dmg; ACT[(who, ph)][act] += dmg
            lasthit[v] = (a[0], act)
        elif a[4] == 'die' and a[7] in lib.BOT and a[0] <= 400:
            v = int(a[5])
            if v in lasthit and a[0] - lasthit[v][0] <= 3:
                side = G.team.get(v); who = 'us' if side == G.us else 'them'
                ph = next(j for j, (lo, hi) in enumerate(PH) if lo <= a[0] <= hi)
                DEAD[(who, ph)][lasthit[v][1]] += 1


for which in ('lost', 'won'):
    HP = Counter(); DEAD = defaultdict(Counter); ACT = defaultdict(Counter); n = 0
    for G in lib.games(which):
        n += 1; analyse(G, HP, DEAD, ACT); lib.lite(G)
    print(f'\n== {which} games ({n}): tower HP damage on the side\'s robots, by what the robot did (sums)')
    for j, (lo, hi) in enumerate(PH):
        for who in ('us', 'them'):
            tot = sum(ACT[(who, j)].values()) or 1
            byt = ' '.join(f'{t[:3]} {HP[(who, j, t)]}' for t in ('SOLDIER', 'SPLASHER', 'MOPPER'))
            acts = ', '.join(f'{k} {100 * ACT[(who, j)][k] / tot:.0f}%' for k in ACTS)
            dead = sum(DEAD[(who, j)].values())
            dd = ', '.join(f'{k} {v}' for k, v in DEAD[(who, j)].most_common())
            print(f'   r{lo}-{hi} {who:4s} HP {tot:6d} per game {tot / n:5.0f} ({byt}) | {acts}\n               died within 3 rounds of a tower hit: {dead} ({dd})')

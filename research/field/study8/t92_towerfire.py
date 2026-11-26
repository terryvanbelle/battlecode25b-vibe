"""Topic 92: what towers shoot, both sides, lost vs won games.  A tower's single-target attack is an 'attack' row by a
tower followed by a 'damage' row on the same target (the AoE is a second attack row on each robot it hits, one 'damage'
of 10 / 20 each; a single-target hit deals 20 + defense buff for paint / money towers, 40+ for defense towers).  Per
side: single-target hits by victim type, kills by victim type (die rows whose actor is a tower), and, on tower-turns
where an enemy mopper AND an enemy soldier or splasher stood within d2 <= 9 at the end of the previous round, the
share of single-target hits that went to the mopper.  Also the HP of the victim when the hit landed (turns.tsv of the
previous round), to see who finishes the weakest first."""
import lib
from collections import defaultdict, Counter

for which in ('lost', 'won'):
    C = defaultdict(Counter); hp_at = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        # positions and hp at the end of each round (for 'previous round' lookups)
        pos = defaultdict(dict)      # round -> id -> (x, y, hp, type, team)
        for t in G.turns:
            if t[3] in lib.BOT: pos[t[0]][t[1]] = (t[4], t[5], t[6], t[3], t[2])
        tpos = {}
        for t in G.turns:
            if t[3] in lib.TOW: tpos[t[1]] = (t[4], t[5])
        acts = G.acts
        i = 0
        while i < len(acts):
            a = acts[i]
            if a[4] == 'attack' and a[3] in lib.TOW and i + 1 < len(acts) and acts[i + 1][4] == 'damage' and acts[i + 1][1] == a[1]:
                dmg = int(acts[i + 1][6]); tgt = int(a[5]); r = a[0]
                side = 'us' if a[2] == G.us else 'them'
                vt = G.typ.get(tgt, '?')
                single = dmg not in (10, 20) or (a[3] != 'DEFENSE_TOWER' and dmg == 20) or (a[3] == 'DEFENSE_TOWER' and dmg >= 40)
                if a[3] != 'DEFENSE_TOWER' and dmg == 10: single = False
                if a[3] == 'DEFENSE_TOWER' and dmg in (20, 25, 30): single = False
                if single:
                    C[side]['single on ' + vt[:2]] += 1
                    prev = pos.get(r - 1, {})
                    if tgt in prev: hp_at[(side, vt[:2])].append(prev[tgt][2])
                    tp = tpos.get(a[1])
                    if tp:
                        near = Counter(v[3][:2] for k, v in prev.items() if v[4] != a[2] and lib.d2(tp, (v[0], v[1])) <= 9)
                        if near['MO'] and (near['SO'] or near['SP']):
                            C[side]['mixed turns'] += 1
                            C[side]['mixed: hit mopper'] += vt == 'MOPPER'
                i += 2
                continue
            if a[4] == 'die' and a[3] in lib.TOW and a[7] in lib.BOT:
                C['us' if a[2] == G.us else 'them']['kill ' + a[7][:2]] += 1
            i += 1
        del pos
    print(f'== {which} games ({n})')
    for side in ('us', 'them'):
        c = C[side]
        tot = sum(v for k, v in c.items() if k.startswith('single on'))
        print(f'   {side:4s}: single-target hits {tot}: ' + ', '.join(f'{k[-2:]} {c[k]} ({100 * c[k] / max(1, tot):.0f}%)' for k in ('single on SO', 'single on SP', 'single on MO'))
              + f' | kills SO {c["kill SO"]} SP {c["kill SP"]} MO {c["kill MO"]}'
              + f' | turns with a mopper and a soldier/splasher in range: {c["mixed turns"]}, mopper hit on {100 * c["mixed: hit mopper"] / max(1, c["mixed turns"]):.0f}%')
        print(f'         victim HP at the hit, median: ' + ', '.join(f'{t} {lib.med(hp_at[(side, t)])}' for t in ('SO', 'SP', 'MO')))
    print()

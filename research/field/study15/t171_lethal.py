"""Topic 171: at the same hit points, why our siege soldiers die more (t170: at 50-99 HP 45% of our hits are followed by
death to that tower within 5 rounds, theirs 15%; at 0-49 HP 73% against 40%; both sides keep hitting at low HP about
as often).  A paint/money tower's turn deals at most single 20 + defense buff (5 per L1 defense tower of its side,
RULES 9) plus AoE 10 to one robot, so a soldier at or below L = 30 + buff dies to one exposure (ending a turn in range).
Per soldier hit on a paint/money tower that stood a round after (t167's classes: out->in = stepped in to hit, ends in
range; in->out = hit then left; in->in = stayed in range), by the hitter's HP at the end of the previous turn against
L of the tower's side that round (defense towers alive x 5 + 30): share of the side's hits in each class, and deaths
to that tower within 5 rounds.  Then, for soldiers killed by a tower: distinct enemy towers that damaged it in its
last 10 rounds, and the killer's share of that damage.  Losses, then wins."""
from collections import defaultdict
import lib


def analyse(G, S):
    pos = {}; tt = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    life = defaultdict(dict); ndef = defaultdict(int)
    for t in G.turns:
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7])
        elif t[3] == 'DEFENSE_TOWER': ndef[t[0], t[2]] += 1
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1], a[3])
    dmg = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.TOW: dmg[int(a[5])].append((a[0], a[1], int(a[6])))
    for a in G.acts:
        if a[4] != 'damage' or a[3] != 'SOLDIER': continue
        v = int(a[5])
        if tt.get(v) not in ('PAINT_TOWER', 'MONEY_TOWER'): continue
        td = deaths.get(v)
        if td and td[0] <= a[0] + 1: continue
        now = life[a[1]].get(a[0]); bef = life[a[1]].get(a[0] - 1)
        if not now or not bef: continue
        q = pos[v]
        d1 = (now[0] - q[0]) ** 2 + (now[1] - q[1]) ** 2
        d0 = (bef[0] - q[0]) ** 2 + (bef[1] - q[1]) ** 2
        mv = 'in->in' if d0 <= 9 and d1 <= 9 else ('in->out' if d0 <= 9 else 'out->in')
        sd = 'us' if a[2] == G.us else 'them'
        L = 30 + 5 * ndef[a[0], G.team.get(v)]
        hp = bef[2]
        band = 'hp<=L' if hp <= L else ('L<hp<=2L' if hp <= 2 * L else ('2L<hp<=3L' if hp <= 3 * L else 'hp>3L'))
        d = deaths.get(a[1])
        dead = bool(d and d[1] == v and d[0] - a[0] <= 5)
        S[sd, band] += 1; S[sd, band, mv] += 1; S[sd, band, mv, 'dead'] += dead; S[sd, band, 'dead'] += dead
        S[sd, 'buffed'] += L > 30
    for a in G.acts:
        if a[4] == 'die' and a[3] in lib.TOW and a[7] == 'SOLDIER':
            v = int(a[5]); r = a[0]
            rows = [x for x in dmg.get(v, ()) if r - 10 <= x[0] <= r]
            if not rows: continue
            sd = 'us' if G.team.get(v) == G.us else 'them'
            tws = {x[1] for x in rows}
            tot = sum(x[2] for x in rows); mine = sum(x[2] for x in rows if x[1] == a[1])
            S[sd, 'kills'] += 1; S[sd, 'kills_multi'] += len(tws) > 1; S[sd, 'kill_share'] += mine / max(1, tot)
            S[sd, 'kill_def'] += any(tt.get(x[1]) == 'DEFENSE_TOWER' for x in rows)
    S['games'] += 1


for which in ('lost', 'won'):
    S = defaultdict(int)
    for G in lib.games(which):
        analyse(G, S)
    ng = S['games']
    print(f'\n== {which}: {ng} games; soldier hits on standing paint/money towers by HP at the hit against L = 30 + defense buff')
    for sd in ('us', 'them'):
        tot = sum(S[sd, b] for b in ('hp<=L', 'L<hp<=2L', '2L<hp<=3L', 'hp>3L'))
        print(f'  {sd}: {tot / ng:5.1f} hits a game, {100 * S[sd, "buffed"] / max(1, tot):3.0f}% against a defense-buffed side')
        for b in ('hp<=L', 'L<hp<=2L', '2L<hp<=3L', 'hp>3L'):
            n = max(1, S[sd, b])
            cls = '  '.join(f'{mv} {100 * S[sd, b, mv] / n:3.0f}% (dies {100 * S[sd, b, mv, "dead"] / max(1, S[sd, b, mv]):3.0f}%)' for mv in ('out->in', 'in->out', 'in->in'))
            print(f'     {b:10s} {S[sd, b] / ng:5.1f}/g ({100 * S[sd, b] / max(1, tot):3.0f}%), dies {100 * S[sd, b, "dead"] / n:3.0f}%:  {cls}')
        k = max(1, S[sd, 'kills'])
        print(f'     soldiers of this side killed by towers {S[sd, "kills"] / ng:4.1f}/g: damaged by 2+ towers in the last 10 rounds {100 * S[sd, "kills_multi"] / k:3.0f}%, '
              f'killer\'s share of that damage {100 * S[sd, "kill_share"] / k:3.0f}%, a defense tower among them {100 * S[sd, "kill_def"] / k:3.0f}%')

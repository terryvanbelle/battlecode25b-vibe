"""Topic 164: how the attackers die (follows t163: at the same hit points our soldiers die to the tower they hit
1.6-3x as often as theirs, 85 / 53% after a hit at 0-49 HP, 56 / 27% at 50-99).  Study 11 2.2's siege HP exit was
tried (t141 -53, t142 -92), so this looks at the mechanics, not at a threshold.
Per soldier hit on a tower that did not fall within a round of it (damage row), from the turns rows:
  entered    the soldier ended its previous turn outside the tower's attack range (d2 > 9; > 16 for a defense
             tower) and this one inside it (it stepped in to hit)
  ends in    it ends the turn of the hit inside that range (the tower shoots it before its next turn)
  shots      the hits of one approach (entry to exit) and the rounds it stays in range
  buff       the defending side's defense towers standing that round (each adds +5 to every tower's single shot,
             RULES 5): hits made against a buffed side, and the death rate after them
Per opponent: defense towers each side completes per game, our robots and theirs killed by tower fire per game.
Losses then wins."""
from collections import defaultdict
import lib


def analyse(G, S):
    pos = {}; tt = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    life = defaultdict(dict)
    for t in G.turns:
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6])
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1])
    # defense towers standing per round per team
    built, died = lib.tower_events(G)
    dt = []
    for (r, tid, ty, team, x, y) in built:
        if ty == 'DEFENSE_TOWER':
            end = min([d[0] for d in died if d[1] == tid] or [10 ** 6])
            dt.append((team, r, end))
            S['dt_built_' + ('us' if team == G.us else 'them')] += 1

    def buffs(team, r): return sum(1 for (tm, a, b) in dt if tm == team and a <= r < b)

    for a in G.acts:
        if a[4] != 'damage' or a[3] != 'SOLDIER': continue
        v = int(a[5])
        if tt.get(v) not in lib.TOW: continue
        td = deaths.get(v)
        if td and td[0] <= a[0] + 1: continue
        q = pos[v]; rng = 16 if tt[v] == 'DEFENSE_TOWER' else 9
        L = life[a[1]]
        now = L.get(a[0]); before = L.get(a[0] - 1)
        if not now: continue
        sd = 'us' if a[2] == G.us else 'them'
        ins = (now[0] - q[0]) ** 2 + (now[1] - q[1]) ** 2 <= rng
        ent = before is not None and (before[0] - q[0]) ** 2 + (before[1] - q[1]) ** 2 > rng
        d = deaths.get(a[1])
        dead = bool(d and d[1] == v and d[0] - a[0] <= 5)
        b = buffs(G.team.get(v), a[0])
        S[sd, 'hits'] += 1
        S[sd, 'ins'] += ins
        S[sd, 'ent'] += ent
        S[sd, 'ent_lowhp'] += ent and now[2] < 100
        S[sd, 'ent_lowhp_dead'] += ent and now[2] < 100 and dead
        S[sd, 'stay_lowhp'] += (not ent) and now[2] < 100
        S[sd, 'stay_lowhp_dead'] += (not ent) and now[2] < 100 and dead
        S[sd, 'ins_dead'] += ins and dead
        S[sd, 'out_dead'] += (not ins) and dead
        S[sd, 'buffed'] += b > 0
        S[sd, 'buffed_dead'] += b > 0 and dead
        S[sd, 'unbuffed_dead'] += b == 0 and dead
        S[sd, 'deftower'] += tt[v] == 'DEFENSE_TOWER'
    for a in G.acts:
        if a[4] == 'die' and a[3] in lib.TOW and a[7] in lib.BOT:
            S['towerkills_' + ('us' if G.team.get(int(a[5])) == G.us else 'them')] += 1


for which in ('lost', 'won'):
    S = defaultdict(int)
    per = defaultdict(lambda: defaultdict(int))
    ng = 0
    for G in lib.games(which):
        ng += 1
        T = defaultdict(int)
        analyse(G, T)
        for k, v in T.items(): S[k] += v; per[G.team_name][k] += v
        per[G.team_name]['games'] += 1
    print(f'\n== {which}: {ng} games; soldier hits on towers that stood')
    for sd in ('us', 'them'):
        h = max(1, S[sd, 'hits'])
        print(f'  {sd:4s} hits {S[sd, "hits"] / ng:5.1f}/game; ends the turn in the tower\'s range {100 * S[sd, "ins"] / h:3.0f}% '
              f'(death within 5 rounds after: in range {100 * S[sd, "ins_dead"] / max(1, S[sd, "ins"]):3.0f}%, out {100 * S[sd, "out_dead"] / max(1, h - S[sd, "ins"]):3.0f}%); '
              f'stepped in to hit {100 * S[sd, "ent"] / h:3.0f}%')
        print(f'       under 100 HP: stepped in {S[sd, "ent_lowhp"] / ng:4.1f}/game (then died {100 * S[sd, "ent_lowhp_dead"] / max(1, S[sd, "ent_lowhp"]):3.0f}%), '
              f'already in range {S[sd, "stay_lowhp"] / ng:4.1f}/game (died {100 * S[sd, "stay_lowhp_dead"] / max(1, S[sd, "stay_lowhp"]):3.0f}%);  '
              f'hits on a defense-buffed side {100 * S[sd, "buffed"] / h:3.0f}% (died {100 * S[sd, "buffed_dead"] / max(1, S[sd, "buffed"]):3.0f}% vs '
              f'{100 * S[sd, "unbuffed_dead"] / max(1, h - S[sd, "buffed"]):3.0f}% unbuffed); on defense towers {100 * S[sd, "deftower"] / h:3.0f}%')
    print('  per opponent: defense towers completed per game (us / them); robots killed by tower fire per game (ours / theirs)')
    for tm in sorted(per):
        P = per[tm]; g = P['games']
        print(f'    {tm:26s} {g:2d} g  defense {P["dt_built_us"] / g:4.1f} / {P["dt_built_them"] / g:4.1f}   tower kills of ours {P["towerkills_us"] / g:5.1f}, of theirs {P["towerkills_them"] / g:5.1f}')


# where the hitter stands: its d2 to the tower at the end of the hit turn and at the end of its previous turn
print('\n== soldier hits on L1/L2 paint and money towers that stood: d2 to the tower at the end of the hit turn (share of hits; '
      'death to that tower within 5 rounds after)')
for which in ('lost', 'won'):
    C = {'us': defaultdict(int), 'them': defaultdict(int)}
    D = {'us': defaultdict(int), 'them': defaultdict(int)}
    MV = {'us': defaultdict(int), 'them': defaultdict(int)}
    ng = 0
    for G in lib.games(which):
        ng += 1
        pos = {}; tt = {}
        for t in G.turns:
            if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
        life = defaultdict(dict)
        for t in G.turns:
            if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5])
        deaths = {}
        for a in G.acts:
            if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1])
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
            sd = 'us' if a[2] == G.us else 'them'
            k = 'out (>9)' if d1 > 9 else ('edge 8-9' if d1 >= 8 else ('5' if d1 == 5 else ('4' if d1 == 4 else '1-2')))
            C[sd][k] += 1
            d = deaths.get(a[1])
            if d and d[1] == v and d[0] - a[0] <= 5: D[sd][k] += 1
            mv = 'in->in' if d0 <= 9 and d1 <= 9 else ('in->out' if d0 <= 9 else ('out->in' if d1 <= 9 else 'out->out'))
            MV[sd][mv] += 1
            if mv == 'in->in' and now != bef: MV[sd]['in->in, moved'] += 1
    print(f'  {which}:')
    for sd in ('us', 'them'):
        n = max(1, sum(C[sd].values()))
        print(f'    {sd:4s} ' + '  '.join(f'{k}: {100 * C[sd][k] / n:3.0f}% ({100 * D[sd][k] / max(1, C[sd][k]):2.0f}%)' for k in ('1-2', '4', '5', 'edge 8-9', 'out (>9)'))
              + '   |  ' + '  '.join(f'{k} {100 * MV[sd][k] / n:3.0f}%' for k in ('out->in', 'in->out', 'in->in', 'in->in, moved', 'out->out')))

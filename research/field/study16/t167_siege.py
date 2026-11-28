"""Topic 167 (question 2a): did t186's Soldier.stepOut do what it was meant to?  t186 = y328 + stepOut (after a hit, of
the 8 moves take one that ends beyond the tower's reach, r2 9 / 16 for a defense tower, own paint first then the
largest r2; else the largest r2 if it gains distance); t188 = t186 + colourAt (no siege change).  Study 14 2.1 (t164):
14% of our tower hits were in->in (theirs 4%), 8% were followed by a step that stayed in range (theirs 1%), and tower
fire killed 12.8 of our robots a loss against 6.4 of theirs.
Per version, every game (wins and losses; repeats left out), soldier hits ('damage' rows by a soldier) on enemy paint
and money towers that stood at least a round after the hit (t164's set):
  class        d2 to the tower at the end of the previous turn and of the hit turn: out->in (stepped in to hit),
               in->out (hit, then left), in->in (stayed in range), out->out (cannot happen for a soldier, r2 9)
  in->in moved the soldier moved during the hit turn and still ended in range (t164's 'step that stays in range')
  in->in still the soldier did not move: split by whether its movement cooldown at the end of the turn was >= 10
               (it could not have moved: the low-paint multiplier, RULES 3) or < 10 (it could have moved and did not)
  died         the soldier's death to that tower within 5 rounds after the hit
Also per game: robots of each side killed by tower fire ('die' rows whose actor is a tower), soldiers among them, and
soldier hits on towers per soldier killed by a tower.  Then the same over the (opponent, map) pairings that both
'new' (t186 + t188) and an older version played, so the comparison holds the pairing fixed."""
from collections import defaultdict
import os
import lib

SETS = (('prev', ('t160', 'y316', 'y323')), ('main', ('y328', 't186', 't188')))


def hits_of(G, S, mcd=None):
    pos = {}; tt = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    life = defaultdict(dict)
    for i, t in enumerate(G.turns):
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7], mcd[i][0] if mcd else None)
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
        mv = 'in->in' if d0 <= 9 and d1 <= 9 else ('in->out' if d0 <= 9 else ('out->in' if d1 <= 9 else 'out->out'))
        d = deaths.get(a[1])
        dead = bool(d and d[1] == v and d[0] - a[0] <= 5)
        S[sd, 'hits'] += 1
        S[sd, mv] += 1; S[sd, mv, 'dead'] += dead
        if mv == 'in->in':
            moved = (now[0], now[1]) != (bef[0], bef[1])
            k = 'moved' if moved else ('still-cd' if (now[4] is not None and now[4] >= 10) else 'still-free')
            S[sd, 'inin', k] += 1; S[sd, 'inin', k, 'dead'] += dead
            S[sd, 'inin', 'lowpaint'] += now[3] < 100
        S[sd, 'dead'] += dead
    for a in G.acts:
        if a[4] == 'die' and a[3] in lib.TOW and a[7] in lib.BOT:
            sd = 'us' if G.team.get(int(a[5])) == G.us else 'them'
            S[sd, 'towerkills'] += 1
            if a[7] == 'SOLDIER': S[sd, 'towerkills_sol'] += 1
    for t in G.turns:
        if t[3] == 'SOLDIER': S['us' if t[2] == G.us else 'them', 'solturns'] += 1
    S['games'] += 1


def show(tag, S):
    ng = max(1, S['games'])
    out = []
    for sd in ('us', 'them'):
        h = max(1, S[sd, 'hits'])
        ii = max(1, S[sd, 'in->in'])
        out.append(f'  {tag:22s} {sd:4s} {int(S["games"]):3d} g  hits {S[sd, "hits"] / ng:5.1f}/g  out->in {100 * S[sd, "out->in"] / h:3.0f}%  '
                   f'in->out {100 * S[sd, "in->out"] / h:3.0f}%  in->in {100 * S[sd, "in->in"] / h:3.0f}% '
                   f'(moved {100 * S[sd, "inin", "moved"] / h:3.1f}%, still with cd {100 * S[sd, "inin", "still-cd"] / h:3.1f}%, '
                   f'still free {100 * S[sd, "inin", "still-free"] / h:3.1f}%; under 100 paint {100 * S[sd, "inin", "lowpaint"] / ii:3.0f}% of in->in)')
        out.append(f'  {"":22s} {"":4s}        died to it after: out->in {100 * S[sd, "out->in", "dead"] / max(1, S[sd, "out->in"]):3.0f}%  '
                   f'in->out {100 * S[sd, "in->out", "dead"] / max(1, S[sd, "in->out"]):3.0f}%  in->in {100 * S[sd, "in->in", "dead"] / ii:3.0f}%   '
                   f'all {100 * S[sd, "dead"] / h:4.1f}%;  killed by towers {S[sd, "towerkills"] / ng:5.1f}/g (soldiers {S[sd, "towerkills_sol"] / ng:4.1f}); '
                   f'soldier-turns per soldier killed by a tower {S[sd, "solturns"] / max(1, S[sd, "towerkills_sol"]):5.0f}; '
                   f'hits per soldier killed by a tower {S[sd, "hits"] / max(1, S[sd, "towerkills_sol"]):4.1f}')
    return '\n'.join(out)


ALL = {}
PAIR = defaultdict(set)      # version -> set of (opp, map)
GAMES = defaultdict(list)    # version -> [(opp, map, S)]
for st, vers in SETS:
    os.environ['S15SET'] = st
    for v in vers:
        for which in ('all', 'lost', 'won'):
            S = defaultdict(int)
            for G in lib.games(which, vers=[v]):
                T = defaultdict(int)
                hits_of(G, T, lib.extra(G))
                for k, x in T.items(): S[k] += x
                if which == 'all':
                    GAMES[v].append((G.team_name, G.map, T))
                    PAIR[v].add((G.team_name, G.map))
            ALL[v, which] = S
os.environ.pop('S15SET', None)
print('soldier hits on enemy paint/money towers that stood; all games, then losses, then wins')
for which in ('all', 'lost', 'won'):
    print(f'\n== {which}')
    for v in ('t160', 'y316', 'y323', 'y328', 't186', 't188'):
        print(show(v, ALL[v, which]))
    N = defaultdict(int)
    for v in ('t186', 't188'):
        for k, x in ALL[v, which].items(): N[k] += x
    print(show('new = t186 + t188', N))


def pooled(vs, keep):
    S = defaultdict(int)
    for v in vs:
        for (o, m, T) in GAMES[v]:
            if (o, m) in keep:
                for k, x in T.items(): S[k] += x
    return S


newp = PAIR['t186'] | PAIR['t188']
for old in (('y328',), ('y316', 'y323', 't160')):
    oldp = set().union(*[PAIR[v] for v in old])
    keep = newp & oldp
    print(f'\n== pairings played by new (t186 + t188) and by {"+".join(old)}: {len(keep)}: ' + ', '.join(f'{o[:8]}/{m}' for o, m in sorted(keep)))
    print(show('new', pooled(('t186', 't188'), keep)))
    print(show('+'.join(old), pooled(old, keep)))

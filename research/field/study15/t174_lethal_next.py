"""Topic 174: what a soldier does once a tower it is sieging has shot it down to lethal HP (follows t171: our hits at
HP <= L = 30 + defense buff are 97% step-ins and 99% end in death; theirs come half as often).  For every tower shot
(the tower's damage row) that leaves a soldier of the attacking side at HP <= L while it is in a run on that tower (it
hit the tower within the 3 rounds before), the soldier's next 5 turns: it ends a turn inside the tower's reach again
(r2 9; 'back in'), and among those it hit the tower from there; it dies to that tower within 5 rounds; it left and
lived 20+ more rounds; its paint at the shot.  The next turns start at the soldier's first turn after the shot
(round r if the tower moved before it in r, from turns.tsv order, else r+1); 'could not move' = its movement cooldown
at the end of the turn before that was 20+ (RULES 3: it drops by 10 at the turn start, a move needs < 10).  Also the same for shots that leave it at L < HP <= 2L.
Per side, losses then wins, then our versions (all games)."""
from collections import defaultdict
import os
import lib


def analyse(G, S, tag):
    pos = {}; tt = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    life = defaultdict(dict); ndef = defaultdict(int); idx = {}
    try: mcd = lib.extra(G)
    except Exception: mcd = None
    for i, t in enumerate(G.turns):
        idx[t[0], t[1]] = i
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7], mcd[i][0] if mcd else 0)
        elif t[3] == 'DEFENSE_TOWER': ndef[t[0], t[2]] += 1
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1])
    dmg_at = defaultdict(int)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.TOW: dmg_at[int(a[5]), a[1], a[0]] += int(a[6])
    hitr = defaultdict(set)
    for a in G.acts:
        if a[4] == 'damage' and a[3] == 'SOLDIER': hitr[a[1], int(a[5])].add(a[0])
    seen = set()
    for a in G.acts:
        if a[4] != 'damage' or tt.get(a[1]) not in ('PAINT_TOWER', 'MONEY_TOWER'): continue
        sid = int(a[5]); r = a[0]
        if G.typ.get(sid) != 'SOLDIER' or (sid, a[1], r) in seen: continue
        if not any((r - k) in hitr[sid, a[1]] for k in range(0, 4)): continue
        p = life[sid].get(r)
        if not p: continue
        L = 30 + 5 * ndef[r, G.team.get(a[1])]
        # HP after this round's shots by that tower: the soldier's row at r already has them if the tower moved first
        before = idx.get((r, a[1]), 1 << 30) < idx.get((r, sid), -1)
        hp = p[2] if before else p[2] - dmg_at[sid, a[1], r]
        if hp <= 0: continue
        band = 'hp<=L' if hp <= L else ('L<hp<=2L' if hp <= 2 * L else None)
        if band is None: continue
        seen.add((sid, a[1], r))
        sd = tag + ':' + ('us' if G.team.get(sid) == G.us else 'them')
        q = pos[a[1]]
        td = deaths.get(a[1])
        if td and td[0] <= r + 1: continue
        back = hitback = False
        # the soldier's first turn after the shot: round r if the tower's turn came first in r, else r+1
        r1 = r if before else r + 1
        prev = life[sid].get(r1 - 1)
        stuck = bool(prev and prev[4] >= 20)
        S[(tag + ':' + ('us' if G.team.get(sid) == G.us else 'them'), band), 'stuck'] += stuck
        for rr in range(r1, r1 + 5):
            pp = life[sid].get(rr)
            if not pp: break
            if (pp[0] - q[0]) ** 2 + (pp[1] - q[1]) ** 2 <= 9:
                back = True
                if rr in hitr[sid, a[1]]: hitback = True
        d = deaths.get(sid)
        dead = bool(d and d[1] == a[1] and d[0] - r <= 5)
        lived = max(life[sid]) - r >= 20
        K = (sd, band)
        S[K] += 1; S[K, 'back'] += back; S[K, 'hitback'] += hitback; S[K, 'dead'] += dead; S[K, 'lived'] += lived
        S.setdefault((K, 'paint'), []).append(p[3])
    S[tag, 'games'] += 1


S = defaultdict(int)
for which in ('lost', 'won'):
    for G in lib.games(which): analyse(G, S, which)
for st, vers in (('prev', ('y316',)), ('main', ('y328', 't186', 't188'))):
    os.environ['S15SET'] = st
    for v in vers:
        for G in lib.games('all', vers=[v]): analyse(G, S, 'new' if v in ('t186', 't188') else v)
print('tower shots that leave a sieging soldier at HP <= L (30 + defense buff) or L < HP <= 2L; its next 5 turns')
for tag in ('lost', 'won', 'y316', 'y328', 'new'):
    ng = max(1, S[tag, 'games'])
    print(f'\n== {tag}: {S[tag, "games"]} games')
    for side in ('us', 'them'):
        for band in ('hp<=L', 'L<hp<=2L'):
            K = (tag + ':' + side, band); n = max(1, S[K])
            print(f'  {side:4s} {band:9s} {S[K] / ng:4.1f}/g  could not move on its next turn {100 * S[K, "stuck"] / n:3.0f}%  ends a turn in range in its next 5 {100 * S[K, "back"] / n:3.0f}% (hit from there {100 * S[K, "hitback"] / n:3.0f}%)  '
                  f'died to that tower {100 * S[K, "dead"] / n:3.0f}%  lived 20+ rounds {100 * S[K, "lived"] / n:3.0f}%  paint then med {lib.med(S.get((K, "paint"), []))}')

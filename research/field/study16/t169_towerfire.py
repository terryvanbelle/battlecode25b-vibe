"""Topic 169: why our siege soldiers still die at twice their rate after t186's step-out (t167: in->in hits fell from
14% to 5%, but hits per soldier killed by a tower stayed at 18 against their 37).  A paint/money tower's single shot is
20 (+5 per defense tower of its side) and its AoE 10, whatever its level (RULES 1), so 30 a shot round: a 250-HP soldier
that takes every single shot lasts about 9 exposures, i.e. 18 hits of a perfect in/out kite.  Theirs last twice as long.
Per attack run (one soldier's damage rows on one paint/money tower, grouped while the gap is under 15 rounds), from the
tower's damage rows (single = the 20+ row, AoE = the 10 row; defense towers' runs are left out) during the run:
  exposures       rounds in which the tower hit the soldier (single or AoE)
  single share    of the tower's single shots in those rounds, the share that hit this soldier (the rest went to
                  another robot of the soldier's side: an escort mopper, another attacker, a passer-by)
  damage taken    from that tower during the run, per hit the soldier made
  company         other robots of the soldier's side within the tower's reach (r2 9) at the end of the rounds in which
                  the tower shot this soldier: soldiers, splashers, moppers (mean)
  outcome         the soldier died to that tower within 5 rounds of its last hit; the tower fell
And per side: where the towers' single shots go (the share of single-shot damage on soldiers, splashers, moppers),
and the soldiers' hit points at the start of runs that end in their death.  Losses, then wins; then by version
(all games) for ours."""
from collections import defaultdict
import os
import lib


def analyse(G, S, tag):
    tt = {}; pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    where = defaultdict(dict)    # round -> id -> (x, y, type, team)
    for t in G.turns:
        if t[3] in lib.BOT: where[t[0]][t[1]] = (t[4], t[5], t[3], t[2], t[6])
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1])
    shots = defaultdict(lambda: defaultdict(list))   # tower -> round -> [(victim, amount, kind)]
    hits = defaultdict(list)                         # (soldier, tower) -> [round]
    for a in G.acts:
        if a[4] != 'damage': continue
        if a[3] in lib.TOW:
            if a[3] == 'DEFENSE_TOWER': continue
            amt = int(a[6]); v = int(a[5])
            shots[a[1]][a[0]].append((v, amt, 'aoe' if amt == 10 else 'single'))
            vt = G.typ.get(v)
            sd = 'us' if a[2] == G.us else 'them'     # the TOWER's side
            if amt != 10: S[tag, sd, 'single_on', vt] += amt
        elif a[3] == 'SOLDIER':
            v = int(a[5])
            if tt.get(v) in ('PAINT_TOWER', 'MONEY_TOWER'): hits[(a[1], v)].append(a[0])
    for (sid, tid), rs in hits.items():
        rs.sort()
        groups = []
        for r in rs:
            if groups and r - groups[-1][-1] < 15: groups[-1].append(r)
            else: groups.append([r])
        side = G.team.get(sid)
        sd = 'us' if side == G.us else 'them'
        q = pos[tid]
        td = deaths.get(tid)
        for g in groups:
            r0, r1 = g[0], g[-1]
            exp = 0; dmg = 0; sing_me = 0; sing_all = 0; comp = defaultdict(int); comp_n = 0
            for r in range(r0, r1 + 2):
                sh = shots[tid].get(r, ())
                if not sh: continue
                mine = [x for x in sh if x[0] == sid]
                for (v, amt, k) in sh:
                    if k == 'single' and G.team.get(v) == side: sing_all += 1
                if mine:
                    exp += 1
                    dmg += sum(x[1] for x in mine)
                    sing_me += sum(1 for x in mine if x[2] == 'single')
                    W = where.get(r, {})
                    comp_n += 1
                    for rid, (x, y, ty, tm, hp) in W.items():
                        if rid != sid and tm == side and (x - q[0]) ** 2 + (y - q[1]) ** 2 <= 9: comp[ty] += 1
            d = deaths.get(sid)
            dead = bool(d and d[1] == tid and r0 <= d[0] <= r1 + 5)
            fell = td is not None and r0 <= td[0] <= r1 + 1
            hp0 = where.get(r0, {}).get(sid, (0, 0, 0, 0, None))[4]
            K = (tag, sd)
            S[K, 'runs'] += 1; S[K, 'hits'] += len(g); S[K, 'exp'] += exp; S[K, 'dmg'] += dmg
            S[K, 'sing_me'] += sing_me; S[K, 'sing_all'] += sing_all
            S[K, 'dead'] += dead; S[K, 'fell'] += fell
            S[K, 'comp_n'] += comp_n
            for ty in lib.BOT: S[K, 'comp', ty] += comp[ty]
            if dead:
                S[K, 'dead_hits'] += len(g); S[K, 'dead_exp'] += exp; S[K, 'dead_dmg'] += dmg
                S[K, 'dead_sing_me'] += sing_me; S[K, 'dead_sing_all'] += sing_all
                if hp0 is not None: S.setdefault((K, 'dead_hp0'), []).append(hp0)
            if exp == 0: S[K, 'noexp'] += 1
    S[tag, 'games'] += 1


def show(tag, S):
    ng = max(1, S[tag, 'games'])
    out = []
    for sd in ('us', 'them'):
        K = (tag, sd)
        n = max(1, S[K, 'runs']); nd = max(1, S[K, 'dead'])
        cn = max(1, S[K, 'comp_n'])
        out.append(f'  {tag:14s} {sd:4s} runs {S[K, "runs"] / ng:5.1f}/g  hits/run {S[K, "hits"] / n:4.1f}  exposures/run {S[K, "exp"] / n:4.1f}  '
                   f'hits per exposure {S[K, "hits"] / max(1, S[K, "exp"]):4.2f}  dmg taken per hit {S[K, "dmg"] / max(1, S[K, "hits"]):5.1f}  '
                   f'single shots on it {100 * S[K, "sing_me"] / max(1, S[K, "sing_all"]):3.0f}% of the tower\'s singles on its side  '
                   f'runs never shot {100 * S[K, "noexp"] / n:3.0f}%  died {100 * S[K, "dead"] / n:3.0f}%  fell {100 * S[K, "fell"] / n:3.0f}%')
        out.append(f'  {"":14s} {"":4s} company in reach when shot (per exposure): S {S[K, "comp", "SOLDIER"] / cn:4.2f} X {S[K, "comp", "SPLASHER"] / cn:4.2f} '
                   f'M {S[K, "comp", "MOPPER"] / cn:4.2f};  runs ending in death: hits {S[K, "dead_hits"] / nd:4.1f}, exposures {S[K, "dead_exp"] / nd:4.1f}, '
                   f'singles on it {100 * S[K, "dead_sing_me"] / max(1, S[K, "dead_sing_all"]):3.0f}%, hp at first hit med {lib.med(S.get((K, "dead_hp0"), []))}')
        tot = sum(S[tag, sd, 'single_on', ty] for ty in lib.BOT)
        out.append(f'  {"":14s} {"":4s} this side\'s paint/money towers: single-shot damage on soldiers {100 * S[tag, sd, "single_on", "SOLDIER"] / max(1, tot):3.0f}% '
                   f'splashers {100 * S[tag, sd, "single_on", "SPLASHER"] / max(1, tot):3.0f}% moppers {100 * S[tag, sd, "single_on", "MOPPER"] / max(1, tot):3.0f}% '
                   f'({tot / ng:5.0f} a game)')
    return '\n'.join(out)


S = defaultdict(int)
for which in ('lost', 'won'):
    for G in lib.games(which):
        analyse(G, S, which)
print('soldier attack runs on paint/money towers (main set: y328, t186, t188; repeats left out)')
for which in ('lost', 'won'):
    print(f'\n== {which}')
    print(show(which, S))
print('\n== by version, all games (study 14 versions from its set)')
for st, vers in (('prev', ('y316',)), ('main', ('y328', 't186', 't188'))):
    os.environ['S15SET'] = st
    for v in vers:
        for G in lib.games('all', vers=[v]):
            analyse(G, S, v)
            if v in ('t186', 't188'): analyse(G, S, 'new')
os.environ.pop('S15SET', None)
for v in ('y316', 'y328', 't186', 't188', 'new'):
    print(show(v, S))

"""Topic 42: tower churn (disintegrate + rebuild = a fresh 500 paint for 1000 chips), both sides.  For every tower
'died' row: type, the tower's paint at its last turn, team chips that round, enemy robots within d2<=20, own robots
adjacent (cheb 1), rounds until a tower stands again on that ruin (rebuild delay) and its type.  Per game: churns,
churns per 100 rounds after the first one, and the paint they bring (500 each) vs the paint towers' own income.
Also: our drained L1 money towers (paint < 10) with chips >= 2000 that did NOT churn that round, by the blocking
condition in Tower.churn() (enemy in view, no adjacent ally, pattern not intact is not visible -> 'other')."""
import lib
from collections import defaultdict, Counter
for which in ('lost', 'won'):
    S = defaultdict(list); C = defaultdict(Counter); per_game = []
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        pos = {}; lastt = {}
        for t in G.turns:
            if t[3] in lib.TOW:
                pos.setdefault(t[1], (t[4], t[5])); lastt[t[1]] = t
        bt = lib.by_round_turns(G)
        lvl = {}
        for a in G.acts:
            if a[4] == 'upgrade': lvl[int(a[5])] = int(a[6])
        builds_at = defaultdict(list)
        for x in b: builds_at[(x[4], x[5])].append((x[0], x[2], x[3]))
        churns = Counter(); first = {}
        for a in G.acts:
            if a[4] != 'died' or a[3] not in lib.TOW: continue
            r, tid, side = a[0], a[1], a[2]
            w = 'us' if side == G.us else 'them'
            p = pos.get(tid); lt = lastt.get(tid)
            chips = lib.money(G, side, r - 1)
            near = [t for t in bt.get(r, ()) if t[3] in lib.BOT]
            en = sum(1 for t in near if t[2] != side and lib.d2((t[4], t[5]), p) <= 20)
            adj = sum(1 for t in near if t[2] == side and max(abs(t[4] - p[0]), abs(t[5] - p[1])) <= 1)
            reb = [x for x in builds_at.get(p, ()) if x[0] >= r and x[2] == side]
            delay = reb[0][0] - r if reb else None
            churns[w] += 1; first.setdefault(w, r)
            S[(w, 'paint at last turn')].append(lt[7] if lt else None)
            S[(w, 'chips')].append(chips)
            S[(w, 'enemy robots d2<=20')].append(en)
            S[(w, 'own robots adjacent')].append(adj)
            S[(w, 'rebuild delay')].append(delay if delay is not None else 999)
            C[w]['type ' + a[3][:1] + ' L' + str(lvl.get(tid, 1))] += 1
            C[w]['rebuilt as ' + (reb[0][1][:1] if reb else 'never')] += 1
        # our blocked churn opportunities: L1 money tower, paint < 10, chips >= 2000 at round start
        blk = Counter()
        for r in range(1, G.end + 1):
            chips = lib.money(G, G.us, r - 1)
            if chips < 2000: continue
            ts = bt.get(r, ())
            for t in ts:
                if t[2] != G.us or t[3] != 'MONEY_TOWER' or lvl.get(t[1], 1) != 1 or t[7] >= 10: continue
                p = (t[4], t[5])
                en = any(u[2] != G.us and u[3] in lib.BOT + lib.TOW and lib.d2((u[4], u[5]), p) <= 20 for u in ts)
                adj = any(u[2] == G.us and u[3] in lib.BOT and max(abs(u[4] - p[0]), abs(u[5] - p[1])) <= 1 for u in ts)
                blk['drained L1 money tower-rounds'] += 1
                if en: blk['enemy in view'] += 1
                elif not adj: blk['no adjacent ally'] += 1
                else: blk['other (pattern broken / churned)'] += 1
        for k, v in blk.items(): C['us blocked'][k] += v
        per_game.append((G.m, G.g, G.map, churns['us'], churns['them'], G.end))
    print(f'== {which} games: churns per game (us, them):', [(f'{m}g{g}', u, t) for m, g, _, u, t, e in per_game])
    print('   total churns us', sum(x[3] for x in per_game), ' them', sum(x[4] for x in per_game),
          '  games with >= 10 churns: us', sum(x[3] >= 10 for x in per_game), ' them', sum(x[4] >= 10 for x in per_game))
    for w in ('us', 'them'):
        print(f'   {w}: ' + '  '.join(f'{k[1]} med {lib.med(v)} p25 {lib.pct(v, .25)} p75 {lib.pct(v, .75)}' for k, v in S.items() if k[0] == w))
        print(f'        {dict(C[w])}')
    print('   our churn blockers (tower-rounds):', dict(C['us blocked']))

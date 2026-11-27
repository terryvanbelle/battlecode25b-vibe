"""Topic 46: how towers die (killed by enemy damage; churn 'died' rows excluded), both directions, lost vs won games.
Per killed tower: phase, type, age, distinct attackers that damaged it in its last 20 rounds by type, the damage
share of soldiers vs splashers, siege length (first damage of the final episode -> death, gaps <= 10 rounds), own
robots within d2<=20 at death (defenders) and own moppers among them, whether it was the side's last paint tower,
and the map class.  Also towers lost per game by r100/r200 and the first loss round."""
import lib
from collections import defaultdict, Counter
def cls(G): return 'small' if min(G.W, G.H) <= 25 or G.sm['paintable'] <= 600 else ('medium' if min(G.W, G.H) <= 35 else 'large')
for which in ('lost', 'won'):
    S = defaultdict(list); C = defaultdict(Counter); per = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        born = {x[1]: x[0] for x in b}
        pos = {x[1]: (x[4], x[5]) for x in b}
        dmg = defaultdict(list)      # tower id -> [(round, attacker id, attacker type, amount)]
        for a in G.acts:
            if a[4] == 'damage' and a[3] in lib.BOT: dmg[int(a[5])].append((a[0], a[1], a[3], int(a[6])))
        bt = lib.by_round_turns(G)
        killed = [a for a in G.acts if a[4] == 'die' and a[7] in lib.TOW]
        lost_by = Counter()
        for a in killed:
            r, tid = a[0], int(a[5]); side = G.team.get(tid); w = 'us' if side == G.us else 'them'
            hits = sorted(dmg.get(tid, ()))
            # final episode
            start = r
            for h in reversed(hits):
                if start - h[0] <= 10: start = min(start, h[0])
                else: break
            last20 = [h for h in hits if h[0] >= r - 20]
            att = {h[1]: h[2] for h in last20}
            tot = sum(h[3] for h in last20) or 1
            ph = 'r1-100' if r <= 100 else 'r101-200' if r <= 200 else 'r201+'
            k = (w, ph)
            C[k]['killed'] += 1; C[k]['type ' + a[7][:1]] += 1
            S[(w, ph, 'age')].append(r - born.get(tid, 0))
            S[(w, ph, 'attackers')].append(len(att))
            S[(w, ph, 'soldier attackers')].append(sum(1 for t in att.values() if t == 'SOLDIER'))
            S[(w, ph, 'splasher attackers')].append(sum(1 for t in att.values() if t == 'SPLASHER'))
            S[(w, ph, 'splasher dmg %')].append(round(100 * sum(h[3] for h in last20 if h[2] == 'SPLASHER') / tot))
            S[(w, ph, 'siege rounds')].append(r - start)
            p = pos.get(tid)
            ts = bt.get(r, ())
            de = [t for t in ts if t[2] == side and t[3] in lib.BOT and p and lib.d2((t[4], t[5]), p) <= 20]
            S[(w, ph, 'defenders d2<=20')].append(len(de))
            S[(w, ph, 'defending moppers')].append(sum(1 for t in de if t[3] == 'MOPPER'))
            if a[7] == 'PAINT_TOWER':
                alive_pt = [t for t in lib.towers_alive(G, side, r, b, d) if t[2] == 'PAINT_TOWER' and t[1] != tid]
                if not alive_pt: C[k]['was the last paint tower'] += 1
            C[(w, 'all')]['map ' + cls(G)] += 1
            if r <= 100: lost_by[(w, 100)] += 1
            if r <= 200: lost_by[(w, 200)] += 1
        for w in ('us', 'them'):
            per[(w, 100)].append(lost_by[(w, 100)]); per[(w, 200)].append(lost_by[(w, 200)])
    print(f'== {which} games ({len(per[("us", 100)])}); "us" = our towers killed by them, "them" = theirs killed by us')
    for w in ('us', 'them'):
        print(f'   {w}: towers killed by r100 per game med {lib.med(per[(w, 100)])} mean {sum(per[(w, 100)]) / max(1, len(per[(w, 100)])):.2f};'
              f' by r200 med {lib.med(per[(w, 200)])} mean {sum(per[(w, 200)]) / max(1, len(per[(w, 200)])):.2f}')
        for ph in ('r1-100', 'r101-200', 'r201+'):
            k = (w, ph)
            if not C[k]['killed']: continue
            print(f'      {ph:9s} {dict(C[k])}')
            print('                ' + '  '.join(f'{m} {lib.med(S[(w, ph, m)])}' for m in ('age', 'attackers', 'soldier attackers', 'splasher attackers', 'splasher dmg %', 'siege rounds', 'defenders d2<=20', 'defending moppers')))
        print(f'      by map class: {dict(C[(w, "all")])}')

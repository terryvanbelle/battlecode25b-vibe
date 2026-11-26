"""Topic 25: moppers vs tower attackers.  For each siege episode (as in t14), mop actions by the defending side that
target an attacker (mop a = target robot id; 0 = tile-only), and the tower kill rate with/without such mops.
Also: who the defender's mops hit overall (robot targets vs tile-only) per side."""
import lib
from collections import defaultdict, Counter
S = defaultdict(lambda: defaultdict(list)); MT = defaultdict(Counter)
for G in lib.games():
    b, d = lib.tower_events(G); dead = {x[1]: x[0] for x in d}
    mops = defaultdict(list)
    for a in G.acts:
        if a[4] == 'mop':
            tgt = int(a[5]) if a[5].lstrip('-').isdigit() else 0
            mops[a[0]].append((a[2], tgt))
            MT['US' if a[2] == G.us else 'TH']['robot' if tgt else 'tile'] += 1
    hits = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.BOT:
            tid = int(a[5])
            if G.typ.get(tid) in lib.TOW and G.team.get(tid) != a[2]: hits[tid].append((a[0], a[1]))
    for tid, L in hits.items():
        L.sort(); eps = [[L[0]]]
        for h in L[1:]:
            if h[0] - eps[-1][-1][0] <= 10: eps[-1].append(h)
            else: eps.append([h])
        ds = G.team.get(tid); nm = 'TH defends' if ds == G.op else 'US defends'
        for ep in eps:
            s, e = ep[0][0], ep[-1][0]; att = set(h[1] for h in ep)
            m = sum(1 for r in range(s - 3, e + 2) for (sd, tg) in mops.get(r, []) if sd == ds and tg in att)
            kill = tid in dead and s <= dead[tid] <= e + 3
            S[nm]['mops on attackers'].append(m)
            S[nm]['kill rate when mops>=3' if m >= 3 else 'kill rate when mops<3'].append(int(kill))
for nm, D in S.items():
    print(nm, {k: (f'n={len(v)} mean {sum(v)/len(v):.2f}' ) for k, v in D.items()})
print('mop targets', dict(MT))

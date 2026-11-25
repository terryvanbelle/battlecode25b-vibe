"""Topic 6: top-team attacks on our towers. Episodes = damage on one of our towers by op robots with gaps <= 10
rounds. Per episode: attackers, arrival spread, staging outside range before the first hit, paint at first hit,
kiting (attack turns that end outside the tower's range), splashers/moppers present, kill."""
import lib
from collections import Counter, defaultdict
P = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    tn = G.team_name
    b, d = lib.tower_events(G)
    tpos = {x[1]: (x[4], x[5]) for x in b}
    trng = {x[1]: (16 if x[2] == 'DEFENSE_TOWER' else 9) for x in b}
    dead = {x[1]: x[0] for x in d}
    hist = defaultdict(dict)
    for t in G.turns: hist[t[1]][t[0]] = t
    rt = lib.by_round_turns(G)
    hits = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[2] == G.op and a[3] in lib.BOT and G.team.get(int(a[5])) == G.us and G.typ.get(int(a[5])) in lib.TOW:
            hits[int(a[5])].append((a[0], a[1], a[3]))
    allfirst = []
    for tid, L in hits.items():
        L.sort(); eps = [[L[0]]]
        for h in L[1:]:
            if h[0] - eps[-1][-1][0] <= 10: eps[-1].append(h)
            else: eps.append([h])
        T = tpos[tid]; R = trng[tid]
        for ep in eps:
            s, e = ep[0][0], ep[-1][0]
            allfirst.append(s)
            ids = {}
            for (r, i, ty) in ep: ids.setdefault(i, (r, ty))
            kill = tid in dead and s <= dead[tid] <= e + 3
            P[tn]['attackers per episode'].append(len(ids))
            P[tn]['episode kills'].append(1 if kill else 0)
            P[tn]['episode length (rounds)'].append(e - s + 1)
            if kill: P[tn]['attackers in KILLING episodes'].append(len(ids)); P[tn]['length of killing episodes'].append(e - s + 1)
            P[tn]['arrival spread (first hits, rounds)'].append(max(v[0] for v in ids.values()) - min(v[0] for v in ids.values()) if len(ids) > 1 else None)
            P[tn]['attacker types'].append(dict(Counter(v[1][:3] for v in ids.values())))
            for i, (r0, ty) in ids.items():
                h = hist[i]
                pp = next((h[q][7] for q in range(r0 - 1, r0 - 4, -1) if q in h), None)
                P[tn][f'{ty[:3]} paint at first hit'].append(pp)
                # staging: rounds in the 12 before first hit spent at R < d2 <= 25 (outside range, inside vision)
                stg = sum(1 for q in range(r0 - 12, r0) if q in h and R < lib.d2((h[q][4], h[q][5]), T) <= 25)
                P[tn][f'{ty[:3]} rounds staged outside range (of 12 before 1st hit)'].append(stg)
            # robots of op within d2<=25 when the first hit lands
            n = sum(1 for t in rt[s] if t[2] == G.op and t[3] in lib.BOT and lib.d2((t[4], t[5]), T) <= 25)
            P[tn]['op robots within d2<=25 at first hit'].append(n)
            mp = max((sum(1 for t in rt[q] if t[2] == G.op and t[3] == 'MOPPER' and lib.d2((t[4], t[5]), T) <= 20) for q in range(s, e + 1)), default=0)
            P[tn]['max op moppers within d2<=20 during episode'].append(mp)
            # kiting: soldier attack turns ending outside range
            att = set((r, i) for (r, i, ty) in ep if ty == 'SOLDIER')
            out = sum(1 for (r, i) in att if r in hist[i] and lib.d2((hist[i][r][4], hist[i][r][5]), T) > R)
            if att: P[tn]['soldier attack turns ending OUTSIDE range (frac)'].append(round(out / len(att), 2))
            # soldiers' turns in the episode: fraction of turns inside range with no attack (idle in range)
            inr = 0; tot = 0
            for i, (r0, ty) in ids.items():
                if ty != 'SOLDIER': continue
                for q in range(r0, e + 1):
                    if q in hist[i]:
                        tot += 1
                        if lib.d2((hist[i][q][4], hist[i][q][5]), T) <= R: inr += 1
            if tot: P[tn]['soldier end-of-turn inside range during episode (frac)'].append(round(inr / tot, 2))
            P[tn]['splasher hits share of episode damage events'].append(round(sum(1 for x in ep if x[2] == 'SPLASHER') / len(ep), 2))
            P[tn]['target tower type'].append(G.typ[tid][:2])
    P[tn]['first attack round on our towers'].append(min(allfirst) if allfirst else None)
    P[tn]['our towers killed per game'].append(sum(1 for x in d if x[3] == G.us))
    P[tn]['episodes per game'].append(sum(1 for _ in allfirst))
for tn, D in P.items():
    print(' ', tn)
    for k, v in D.items():
        if v and isinstance(v[0], dict):
            s = Counter()
            for x in v: s.update(x)
            print(f'     {k:<62} {dict(s)}')
        elif v and isinstance(v[0], str): print(f'     {k:<62} {dict(Counter(v))}')
        else: print(f'     {k:<62} med {lib.med(v)} mean {round(sum(x for x in v if x is not None)/max(1,len([x for x in v if x is not None])),2)} p10 {lib.pct(v, .1)} p90 {lib.pct(v, .9)} n={len([x for x in v if x is not None])}')

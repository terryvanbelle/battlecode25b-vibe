"""Topic 14: tower attacks, both directions.  Episode = enemy robot damage on one tower with gaps <= 10 rounds.
Per episode: attackers, kill, defenders (robots of the tower's side within d2<=20 of the tower, max over the episode),
defender moppers, defender damage dealt to the attackers during the episode (attacks by tower + robots), attacker deaths."""
import lib
from collections import defaultdict, Counter
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    b, d = lib.tower_events(G)
    tpos = {x[1]: (x[4], x[5]) for x in b}
    dead = {x[1]: x[0] for x in d}
    rt = lib.by_round_turns(G)
    hits = defaultdict(list); dmg_to = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage':
            tid = int(a[5])
            if a[3] in lib.BOT and G.typ.get(tid) in lib.TOW and G.team.get(tid) != a[2]:
                hits[tid].append((a[0], a[1], a[3]))
            dmg_to[tid].append((a[0], a[1], int(a[6]) if a[6].lstrip('-').isdigit() else 0))
    rdie = {}
    for a in G.acts:
        if a[4] == 'die': rdie[int(a[5])] = a[0]
    for tid, L in hits.items():
        L.sort(); eps = [[L[0]]]
        for h in L[1:]:
            if h[0] - eps[-1][-1][0] <= 10: eps[-1].append(h)
            else: eps.append([h])
        T = tpos.get(tid); dside = G.team.get(tid); nm = 'TH attacks US' if dside == G.us else 'US attacks TH'
        if T is None: continue
        for ep in eps:
            s, e = ep[0][0], ep[-1][0]
            att = set(h[1] for h in ep)
            kill = tid in dead and s <= dead[tid] <= e + 3
            mdef = mmop = 0
            for r in range(s, e + 1):
                ds = [t for t in rt.get(r, []) if t[2] == dside and t[3] in lib.BOT and lib.d2((t[4], t[5]), T) <= 20]
                mdef = max(mdef, len(ds)); mmop = max(mmop, sum(1 for t in ds if t[3] == 'MOPPER'))
            adead = sum(1 for i in att if i in rdie and s <= rdie[i] <= e + 3)
            S[nm]['episodes'].append(1); S[nm]['kill'].append(int(kill)); S[nm]['attackers'].append(len(att))
            S[nm]['defenders within d2<=20 (max)'].append(mdef); S[nm]['defending moppers (max)'].append(mmop)
            S[nm]['attackers killed in episode'].append(adead)
            S[nm]['episode start round'].append(s)
            if kill: S[nm]['defenders when tower killed'].append(mdef); S[nm]['round of kill'].append(dead[tid])
            else: S[nm]['defenders when tower survived'].append(mdef)
for nm, D in S.items():
    print(nm)
    for k, v in D.items():
        if k == 'episodes': print(f'   episodes {len(v)}'); continue
        print(f'   {k:<36} med {lib.med(v)} mean {sum(v)/len(v):.2f} n={len(v)}')

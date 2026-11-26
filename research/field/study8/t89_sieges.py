"""Topic 89: sieges on towers, both directions, lost vs won games.  A siege is an episode of robot damage to one tower
(HP 'damage' rows by soldiers / splashers, gaps <= 10 rounds) totalling >= 300.  It falls if the tower dies within 3
rounds of the last hit.  Per siege: phase of its first hit, tower type, distinct attackers, the defender's robots
within d2 <= 20 of the tower during the siege (distinct ids; moppers separately), paint the defender's moppers
drained from the attackers during the siege, the robots the tower spawned during the siege by type, and the
attackers' fate within 10 rounds of the end (killed by a tower / dead at 0 paint).  Medians per (defender, phase),
lost and won games; then our starting paint tower's sieges one by one in the lost games."""
import lib
from collections import defaultdict, Counter

PHN = ('r1-100', 'r101-200', 'r201+')
def ph(r): return 0 if r <= 100 else 1 if r <= 200 else 2


def sieges(G):
    b, d = lib.tower_events(G)
    pos = {x[1]: (x[4], x[5]) for x in b}
    start_pt = {x[1] for x in b if x[0] == 0 and x[2] == 'PAINT_TOWER'}
    death = {x[1]: x[0] for x in d}
    hits = defaultdict(list)
    drains = defaultdict(list)    # target id -> [(round, amount, mopper team)]
    deaths = {}                   # robot id -> (round, 'tower' | 'starved')
    spawns = defaultdict(list)    # tower id -> [(round, type)]
    for a in G.acts:
        k = a[4]
        if k == 'damage' and a[3] in ('SOLDIER', 'SPLASHER'):
            hits[int(a[5])].append((a[0], a[1], a[3], int(a[6])))
        elif k == 'drain':
            drains[int(a[5])].append((a[0], int(a[6]) if a[6].lstrip('-').isdigit() else 0))
        elif k == 'die' and a[7] in lib.BOT:
            deaths[int(a[5])] = (a[0], 'starved' if a[1] == int(a[5]) else 'tower')
        elif k == 'spawn' and a[3] in lib.TOW:
            spawns[a[1]].append((a[0], a[6]))
    near = defaultdict(set)       # (tower id, round) filled lazily below
    out = []
    eps = []
    for tid, hs in hits.items():
        hs.sort()
        cur = [hs[0]]
        for h in hs[1:]:
            if h[0] - cur[-1][0] <= 10: cur.append(h)
            else: eps.append((tid, cur)); cur = [h]
        eps.append((tid, cur))
    eps = [(tid, e) for tid, e in eps if sum(h[3] for h in e) >= 300 and tid in pos]
    if not eps: return out
    # defenders within d2 <= 20 per siege: one pass over the turns
    want = defaultdict(list)
    for i, (tid, e) in enumerate(eps):
        for r in range(e[0][0], e[-1][0] + 1): want[r].append(i)
    dfd = defaultdict(set); dmop = defaultdict(set)
    for t in G.turns:
        if t[0] not in want or t[3] not in lib.BOT: continue
        for i in want[t[0]]:
            tid = eps[i][0]
            if G.team.get(tid) != t[2]: continue
            if lib.d2(pos[tid], (t[4], t[5])) <= 20:
                dfd[i].add(t[1])
                if t[3] == 'MOPPER': dmop[i].add(t[1])
    for i, (tid, e) in enumerate(eps):
        r0, r1 = e[0][0], e[-1][0]
        att = set(h[1] for h in e)
        fell = tid in death and r1 - 3 <= death[tid] <= r1 + 3
        drained = sum(amt for a_ in att for (r, amt) in drains.get(a_, ()) if r0 <= r <= r1 + 3)
        fate = Counter(deaths[a_][1] for a_ in att if a_ in deaths and r0 <= deaths[a_][0] <= r1 + 10)
        sp = Counter(t[:2] for (r, t) in spawns.get(tid, ()) if r0 <= r <= r1)
        # a defense tower of the defender standing within d2 <= 25 of the besieged tower when the siege began
        dnear = any(x[2] == 'DEFENSE_TOWER' and x[3] == G.team.get(tid) and x[1] != tid and x[0] <= r0 < death.get(x[1], 99999)
                    and lib.d2((x[4], x[5]), pos[tid]) <= 25 for x in b)
        out.append(dict(dnear=dnear, side='us' if G.team.get(tid) == G.us else 'them', ph=ph(r0), r0=r0, r1=r1, typ=G.typ.get(tid, '?')[:1],
                        start_pt=tid in start_pt, fell=fell, att=len(att), atype=Counter(h[2][:2] for h in e),
                        dmg=sum(h[3] for h in e), dfd=len(dfd[i]), dmop=len(dmop[i]), drained=drained,
                        killed=fate['tower'], starved=fate['starved'], spawn=sp))
    return out


for which in ('lost', 'won'):
    S = defaultdict(list); n = 0; first_pt = []
    for G in lib.games(which):
        n += 1
        for s in sieges(G):
            S[(s['side'], s['ph'])].append(s)
            if which == 'lost' and s['side'] == 'us' and s['start_pt'] and s['ph'] == 0:
                first_pt.append((G, s))
    print(f'== {which} games ({n}): sieges (>= 300 robot damage on one tower, gaps <= 10 rounds) by the DEFENDING side; medians')
    print('   defender phase    sieges fell%  attackers  defenders(moppers)  drained-from-attackers  attackers killed/starved  tower spawned S/M/X during siege (sums)')
    for side in ('us', 'them'):
        for p in range(3):
            L = S[(side, p)]
            if not L: continue
            sp = Counter()
            for s in L: sp.update(s['spawn'])
            print(f'   {side:4s}     {PHN[p]:9s} {len(L):5d} {100 * sum(s["fell"] for s in L) / len(L):5.0f}%   {lib.med([s["att"] for s in L]):5}     '
                  f'{lib.med([s["dfd"] for s in L]):5} ({lib.med([s["dmop"] for s in L])})            {lib.med([s["drained"] for s in L]):6}'
                  f'                 {sum(s["killed"] for s in L):4d}/{sum(s["starved"] for s in L):<4d}                 '
                  f'{sp["SO"]}/{sp["MO"]}/{sp["SP"]}')
        # fell vs held, by defenders present
        L = [s for p in range(3) for s in S[(side, p)]]
        for lab, f in (('no mopper of the defender within d2 20', lambda s: s['dmop'] == 0), ('1+ defender moppers', lambda s: s['dmop'] >= 1),
                       ('a defense tower of the defender within d2 25', lambda s: s['dnear']), ('no defense tower near', lambda s: not s['dnear'])):
            M = [s for s in L if f(s)]
            if M: print(f'      {side}: {lab}: {len(M)} sieges, fell {100 * sum(s["fell"] for s in M) / len(M):.0f}%, drained med {lib.med([s["drained"] for s in M])}')
    print()
    if which == 'lost':
        print('   our starting paint tower under siege in r1-100 (lost games): game, rounds, attackers by type, damage, fell, defenders (moppers), drained, our spawns S/M/X meanwhile')
        for G, s in first_pt:
            print(f'      m{G.m}g{G.g} {G.map[:12]:12s} {G.team_name[:10]:10s} r{s["r0"]}-{s["r1"]} {dict(s["atype"])} dmg {s["dmg"]} '
                  f'{"FELL" if s["fell"] else "held"} defenders {s["dfd"]} ({s["dmop"]}) drained {s["drained"]} '
                  f'spawned {s["spawn"]["SO"]}/{s["spawn"]["MO"]}/{s["spawn"]["SP"]}')
        print()

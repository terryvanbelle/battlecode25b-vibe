"""Topic 148: where each side's paint and chips come from (new: no study split the income into its sources).
RULES 2.1 / 6.3 / 7: at the start of every round each paint tower gains 5 / 10 / 15 paint (L1 / L2 / L3) plus 3 per
ACTIVE SRP of its team (lifetime 50+), capped at 1000; each money tower adds 20 / 30 / 40 chips plus 3 per active SRP;
a completed tower starts with 500 paint.  rounds.tsv's srp column is the active count (GameWorld.getNumResourcePatterns).
Per game and side, rounds summed over a phase (r1-100, r101-200, r201-300, r301-400; a phase counts only if the game
reached its end):
  PT / MT       mean paint / money towers standing (towers with a turn that round), and their mean level
  base paint    paint-tower income from the level alone
  SRP paint     3 x active SRPs x paint towers (the SRP share of paint income)
  new towers    500 x towers completed by the side (new ruins, retaken ruins and churn rebuilds alike)
  capped        income lost because a paint tower was at 1000 already (estimate: the tower's paint at its previous
                turn + its income > 1000)
  base chips, SRP chips   the same for money towers
  spawn paint   paint the side's towers spent on spawns (S 200, X 300, M 100)
  SRPs active   mean active SRPs over the phase; SRPs completed (srp rows) and SRPs that broke (active count drops)
Medians per game, us / them, lost games then won games."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 300), (301, 400))
PHN = ('r1-100', 'r101-200', 'r201-300', 'r301-400')
PBASE = {1: 5, 2: 10, 3: 15}
MBASE = {1: 20, 2: 30, 3: 40}
SPAWNP = {'SOLDIER': 200, 'SPLASHER': 300, 'MOPPER': 100}


def analyse(G):
    level = {}
    lev_ev = defaultdict(list)   # tower id -> [(round, level)]
    builds = defaultdict(int)    # (side, phase) -> towers completed
    spawnp = defaultdict(int)
    srpdone = defaultdict(int)
    for a in G.acts:
        k = a[4]
        if k == 'startlevel': lev_ev[int(a[5])].append((0, int(a[6])))
        elif k == 'build': lev_ev[int(a[5])].append((a[0], 1))
        elif k == 'upgrade': lev_ev[int(a[5])].append((a[0], int(a[6])))
    for a in G.acts:
        for j, (lo, hi) in enumerate(PH):
            if lo <= a[0] <= hi:
                if a[4] == 'build': builds[(a[2], j)] += 1
                elif a[4] == 'spawn' and a[6] in SPAWNP: spawnp[(a[2], j)] += SPAWNP[a[6]]
                elif a[4] == 'srp': srpdone[(a[2], j)] += 1
    for i in lev_ev: lev_ev[i].sort()

    def lvl(i, r):
        L = 1
        for rr, l in lev_ev.get(i, ()):
            if rr <= r: L = l
        return L
    # towers standing per round: from tower turn rows
    tw = defaultdict(list)   # round -> [(team, kind, id, paint)]
    for t in G.turns:
        if t[3] in lib.TOW: tw[t[0]].append((t[2], t[3], t[1], t[7]))
    lastp = {}
    out = {}
    for s in (G.us, G.op):
        sk = 'A' if s == 1 else 'B'
        for j, (lo, hi) in enumerate(PH):
            if G.end < hi: continue
            D = defaultdict(float)
            prev_srp = int(G.rounds[lo - 2]['srp' + sk]) if lo >= 2 else 0
            for r in range(lo, hi + 1):
                srp = int(G.rounds[r - 1]['srp' + sk])
                if srp < prev_srp: D['srp_broke'] += prev_srp - srp
                prev_srp = srp
                D['srp_active'] += srp
                for team, kind, i, paint in tw.get(r, ()):
                    if team != s: continue
                    L = lvl(i, r)
                    if kind == 'PAINT_TOWER':
                        D['pt'] += 1; D['pt_level'] += L
                        inc = PBASE[L] + 3 * srp
                        D['base_paint'] += PBASE[L]; D['srp_paint'] += 3 * srp
                        p0 = lastp.get(i)
                        if p0 is not None and p0 + inc > 1000: D['capped'] += min(inc, p0 + inc - 1000)
                    elif kind == 'MONEY_TOWER':
                        D['mt'] += 1; D['mt_level'] += L
                        D['base_chips'] += MBASE[L]; D['srp_chips'] += 3 * srp
                    lastp[i] = paint
            n = hi - lo + 1
            D['pt_level'] = D['pt_level'] / D['pt'] if D['pt'] else 0
            D['mt_level'] = D['mt_level'] / D['mt'] if D['mt'] else 0
            D['pt'] /= n; D['mt'] /= n; D['srp_active'] /= n
            D['new_tower_paint'] = 500 * builds[(s, j)]
            D['spawn_paint'] = spawnp[(s, j)]
            D['srp_done'] = srpdone[(s, j)]
            D['paint_total'] = D['base_paint'] + D['srp_paint'] + D['new_tower_paint'] - D['capped']
            out[('us' if s == G.us else 'them', j)] = D
    return out


KEYS = (('pt', 'paint towers (mean)', 1), ('pt_level', '  their mean level', 2), ('base_paint', 'base paint income', 0),
        ('srp_paint', 'SRP paint income', 0), ('capped', 'income lost at the 1000 cap', 0),
        ('new_tower_paint', 'new towers x 500', 0), ('paint_total', 'paint in (base + SRP + new - capped)', 0),
        ('spawn_paint', 'spawn paint', 0), ('mt', 'money towers (mean)', 1), ('mt_level', '  their mean level', 2),
        ('base_chips', 'base chip income', 0), ('srp_chips', 'SRP chip income', 0), ('srp_active', 'active SRPs (mean)', 1),
        ('srp_done', 'SRPs completed', 1), ('srp_broke', 'SRPs that broke', 1))

for which in ('lost', 'won'):
    R = defaultdict(list); ng = 0
    for G in lib.games(which):
        ng += 1
        for k, D in analyse(G).items(): R[k].append(D)
    print(f'\n== {which}: {ng} games; medians per game us / them [means], per phase (games reaching its end)')
    print(f'   {"":40s}' + ''.join(f'{PHN[j] + " (" + str(len(R[("us", j)])) + ")":>24s}' for j in range(len(PH))))
    for k, name, dp in KEYS:
        cells = ''
        for j in range(len(PH)):
            u = [D[k] for D in R[('us', j)]]; t = [D[k] for D in R[('them', j)]]
            if not u: cells += f'{"-":>24s}'; continue
            mu, mt = lib.med(u), lib.med(t)
            au, at = sum(u) / len(u), sum(t) / len(t)
            if dp == 0: c = f'{mu:.0f}/{mt:.0f} [{au:.0f}/{at:.0f}]'
            else: c = f'{au:.{dp}f}/{at:.{dp}f}'
            cells += f'{c:>24s}'
        print(f'   {name:40s}' + cells)

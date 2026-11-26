"""Topic 30: the economy after the opening, per side and phase (r1-100, 101-200, 201-300, 301-400).
Income: paint from paint towers (5/10/15 per level + 3 per active SRP, per tower turn), 500 paint per new tower
(builds, incl. churn rebuilds), chips from money towers (20/30/40 + 3*SRP).  Spending: spawns, SRPs, upgrades, builds.
Bottleneck: tower turns with paint < 200 (no soldier possible) while team chips >= 1250 = 'paint-blocked';
tower turns with paint >= 300 but chips < 250 = 'chip-blocked'.  Also churn (disintegrations) and mean chips."""
import lib
from collections import defaultdict, Counter
PH = ((1, 100), (101, 200), (201, 300), (301, 400))
PR = {1: 5, 2: 10, 3: 15}; MR = {1: 20, 2: 30, 3: 40}
S = defaultdict(lambda: defaultdict(list))   # (side, phase) -> metric -> per-game values
for G in lib.games():
    lvl = defaultdict(lambda: 1)
    acts_by_r = defaultdict(list)
    for a in G.acts: acts_by_r[a[0]].append(a)
    srp = {i + 1: (int(R['srpA']), int(R['srpB'])) for i, R in enumerate(G.rounds)}
    turns_by_r = lib.by_round_turns(G)
    for ph in PH:
        if G.end < ph[1]: continue
        for side in (G.us, G.op):
            m = Counter()
            for r in range(1, ph[1] + 1):
                for a in acts_by_r.get(r, ()):
                    if a[4] in ('startlevel', 'upgrade'): lvl[int(a[5])] = int(a[6]) if a[4] == 'upgrade' else 2
                if r < ph[0]: continue
                chips = lib.money(G, side, r - 1)
                ns = srp[r][side - 1]
                for t in turns_by_r.get(r, ()):
                    if t[2] != side or t[3] not in lib.TOW: continue
                    L = lvl[t[1]]
                    m['tturns'] += 1
                    if t[3] == 'PAINT_TOWER': m['paint_inc'] += PR[L] + 3 * ns; m['pt_turns'] += 1
                    if t[3] == 'MONEY_TOWER': m['chip_inc'] += MR[L] + 3 * ns
                    if t[7] < 200 and chips >= 1250: m['paint_blocked'] += 1
                    if t[7] >= 300 and chips < 250: m['chip_blocked'] += 1
                m['chips_sum'] += lib.money(G, side, r)
                for a in acts_by_r.get(r, ()):
                    if a[2] != side: continue
                    k = a[4]
                    if k == 'build': m['builds'] += 1; m['build_' + a[6][:1]] += 1
                    elif k == 'spawn': m['spawn_' + a[6][:2]] += 1
                    elif k == 'srp': m['srp_done'] += 1
                    elif k == 'upgrade': m['upg_' + a[3][:1] + a[6]] += 1
                    elif k == 'died' and a[3] in lib.TOW: m['churn'] += 1
                    elif k == 'die' and a[7] in lib.TOW: pass
            n = ph[1] - ph[0] + 1
            m['paint_new'] = 500 * m['builds']
            S[('us' if side == G.us else 'them', ph)]['_n'].append(1)
            for k in ('paint_inc', 'paint_new', 'chip_inc', 'builds', 'build_P', 'build_M', 'build_D', 'churn', 'srp_done',
                      'spawn_SO', 'spawn_SP', 'spawn_MO', 'upg_P2', 'upg_P3', 'upg_M2', 'upg_M3', 'upg_D2'):
                S[('us' if side == G.us else 'them', ph)][k].append(m[k])
            S[('us' if side == G.us else 'them', ph)]['mean_chips'].append(m['chips_sum'] / n)
            S[('us' if side == G.us else 'them', ph)]['paint_blocked%'].append(100 * m['paint_blocked'] / max(1, m['tturns']))
            S[('us' if side == G.us else 'them', ph)]['chip_blocked%'].append(100 * m['chip_blocked'] / max(1, m['tturns']))
            S[('us' if side == G.us else 'them', ph)]['pt_share%'].append(100 * m['pt_turns'] / max(1, m['tturns']))
keys = [k for k in S[('us', PH[0])] if k != '_n']
print('medians per game (sum over the phase unless %/mean); us | them')
print(f'{"metric":15s}' + ''.join(f'{f"r{a}-{b}":>18s}' for a, b in PH))
print(f'{"games":15s}' + ''.join(f'{len(S[("us", ph)]["_n"]):>18d}' for ph in PH))
for k in keys:
    print(f'{k:15s}' + ''.join(f'{str(lib.med(S[("us", ph)][k])) + " | " + str(lib.med(S[("them", ph)][k])):>18s}' for ph in PH))

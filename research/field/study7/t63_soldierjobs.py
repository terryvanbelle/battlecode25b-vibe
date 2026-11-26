"""Topic 63: what soldiers do after r100, both sides, by position at the end of each turn (indicator strings are not
recorded on the replica).  Classes, first match wins:
  siege   within d2 <= 20 of a standing enemy tower,
  ruin    within Chebyshev 2 of a ruin with no tower (working a pattern),
  refill  adjacent (Chebyshev 1) to an own tower,
  other   exploring / painting / SRPs.
Also soldier attacks on towers per 100 soldier-turns, paint marks, and soldier deaths by class.  Phases r101-200 and
r201-300; lost and won games; medians of per-game shares."""
import lib
from collections import defaultdict, Counter
PH = ((1, 100), (101, 200), (201, 300))
for which in ('lost', 'won'):
    S = defaultdict(list)
    for G in lib.games(which):
        b, d = lib.tower_events(G)
        bt = lib.by_round_turns(G)
        att = Counter(); dies = Counter()
        for a in G.acts:
            if a[3] == 'SOLDIER' and a[4] == 'damage': att[(a[2], a[0])] += 1
        for lo, hi in PH:
            if G.end < hi: continue
            C = {1: Counter(), 2: Counter()}
            for r in range(lo, hi + 1):
                tw = {sd: [(t[4], t[5]) for t in lib.towers_alive(G, sd, r, b, d)] for sd in (1, 2)} if r % 5 == 0 or r == lo else tw
                occ = set(tw[1]) | set(tw[2])
                free = [p for p in G.ruins if p not in occ]
                for t in bt.get(r, ()):
                    if t[3] != 'SOLDIER': continue
                    sd = t[2]; p = (t[4], t[5])
                    if any(lib.d2(p, q) <= 20 for q in tw[3 - sd]): k = 'siege'
                    elif any(max(abs(p[0] - q[0]), abs(p[1] - q[1])) <= 2 for q in free): k = 'ruin'
                    elif any(max(abs(p[0] - q[0]), abs(p[1] - q[1])) <= 1 for q in tw[sd]): k = 'refill'
                    else: k = 'other'
                    C[sd][k] += 1; C[sd]['n'] += 1
            for sd in (G.us, G.op):
                w = 'us' if sd == G.us else 'them'
                n = max(1, C[sd]['n'])
                for k in ('siege', 'ruin', 'refill', 'other'):
                    S[(w, lo, k)].append(100 * C[sd][k] / n)
                S[(w, lo, 'soldier-turns/round')].append(C[sd]['n'] / (hi - lo + 1))
                S[(w, lo, 'tower hits /100 turns')].append(100 * sum(att[(sd, r)] for r in range(lo, hi + 1)) / n)
    print(f'== {which} games: soldier turns by class (% of soldier-turns, median over games), us | them')
    for lo, hi in PH:
        print(f'  r{lo}-{hi}: ' + '  '.join(f'{k} {lib.med(S[("us", lo, k)])} | {lib.med(S[("them", lo, k)])}'
                                          for k in ('soldier-turns/round', 'siege', 'ruin', 'refill', 'other', 'tower hits /100 turns')))

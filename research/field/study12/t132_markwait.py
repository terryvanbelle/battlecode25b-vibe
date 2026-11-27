"""Topic 132: soldiers that wait beside an unmarked ruin because they cannot pay for the mark.  In t122
Soldier.workRuin (Soldier.java:221-229) a soldier with no type for its ruin walks next to it and marks the pattern;
markTowerPattern needs 25 paint (RULES 4.6), so with 10-24 paint it can neither mark nor go for paint (the refill
branch is for paint < 10) and returns true every turn until another soldier marks the ruin, its paint decays below
10, or 150 rounds pass.  Per side (the opponents' code differs; their numbers are a reference only), r1-400:
  wait-turns   soldier-turns ending with 10-24 paint within d2 2 of a free ruin (no tower) none of whose 24 tiles
               carried a mark of the side (from the replay's mark rows; t122 never removes marks), with no action row
               that turn and the same position as the turn before
  episodes     runs of 3+ consecutive such turns by one soldier; their length (median, max)
Also: pattern marks (>= 20 mark rows by one robot in one round) and single marks per game, and the paint the 25-paint
pattern marks cost, by phase.  Medians per game [sums]."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 400))


def analyse(G):
    b, d = lib.tower_events(G)
    life = defaultdict(list)
    dr = {x[1]: x[0] for x in d}
    for x in b: life[(x[4], x[5])].append((x[0], dr.get(x[1], 10 ** 6)))
    ruins = list(G.ruins)
    def free(p, r): return not any(lo <= r < hi for lo, hi in life.get(p, ()))
    acted = set((a[0], a[1]) for a in G.acts)
    marks = defaultdict(list)   # side -> list of (round, (x, y))
    nmark = defaultdict(int)
    for a in G.acts:
        if a[4] == 'mark':
            x, y = map(int, a[5].split(',')); marks[a[2]].append((a[0], (x, y))); nmark[(a[0], a[1])] += 1
    out = {}
    for s in (1, 2):
        M = sorted(marks[s]); mi = 0; seen = set()
        prev = {}
        wait = defaultdict(int); runs = []; cur = {}
        turns = [t for t in G.turns if t[2] == s and t[3] == 'SOLDIER' and t[0] <= 400]
        byr = defaultdict(list)
        for t in turns: byr[t[0]].append(t)
        for r in range(1, min(G.end, 400) + 1):
            while mi < len(M) and M[mi][0] <= r: seen.add(M[mi][1]); mi += 1
            ph = next(j for j, (lo, hi) in enumerate(PH) if lo <= r <= hi)
            for t in byr.get(r, ()):
                rid, x, y, p = t[1], t[4], t[5], t[7]
                ok = False
                if 10 <= p <= 24 and (r, rid) not in acted and prev.get(rid) == (x, y):
                    for q in ruins:
                        if (q[0] - x) ** 2 + (q[1] - y) ** 2 <= 2 and free(q, r):
                            if not any((q[0] + dx, q[1] + dy) in seen for dx in range(-2, 3) for dy in range(-2, 3)):
                                ok = True; break
                if ok:
                    wait[ph] += 1; cur[rid] = cur.get(rid, 0) + 1
                elif cur.get(rid):
                    if cur[rid] >= 3: runs.append(cur[rid])
                    cur[rid] = 0
                prev[rid] = (x, y)
        runs += [v for v in cur.values() if v >= 3]
        pm = defaultdict(int); sm = defaultdict(int)
        for (r, rid), n in nmark.items():
            if G.team.get(rid) != s or r > 400: continue
            ph = next(j for j, (lo, hi) in enumerate(PH) if lo <= r <= hi)
            if n >= 20: pm[ph] += 1
            else: sm[ph] += n
        rec = {}
        for j in range(len(PH)):
            rec[f'wait-turns {j}'] = wait[j]; rec[f'pattern marks {j}'] = pm[j]; rec[f'single marks {j}'] = sm[j]
        rec['episodes'] = len(runs); rec['ep len med'] = lib.med(runs) if runs else None; rec['ep len max'] = max(runs) if runs else None
        out[s] = rec
    return out


for which in ('lost', 'won'):
    L = []
    for G in lib.games(which):
        o = analyse(G); L.append((o[G.us], o[G.op], G)); lib.lite(G)
    print(f'\n== {which} games ({len(L)}); medians per game [sums], us | them')
    for k in L[0][0]:
        u = [x[0][k] for x in L]; t = [x[1][k] for x in L]
        fu = [v for v in u if v is not None]; ft = [v for v in t if v is not None]
        lab = k.replace(' 0', ' r1-100').replace(' 1', ' r101-200').replace(' 2', ' r201-400')
        print(f'   {lab:28s} {lib.med(fu)} | {lib.med(ft)}   [{sum(fu)} | {sum(ft)}]   games with any: {sum(1 for v in fu if v)} | {sum(1 for v in ft if v)}')
    pm_us = sum(x[0][f'pattern marks {j}'] for x in L for j in range(3))
    print(f'   paint on 25-paint pattern marks, us: {25 * pm_us} over {len(L)} games = {25 * pm_us / max(1, len(L)):.0f} per game')

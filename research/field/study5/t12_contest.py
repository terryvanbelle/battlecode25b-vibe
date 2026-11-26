"""Topic 12: contested ruins.  (a) Ruin denial: paint actions by side X inside the 5x5 of a ruin the OTHER side marked
(and X never marked), after the other side's first mark, before any build.  (b) Cleaning: for each side's completed
ruins, max enemy tiles in the 5x5 during the attempt and unpaint (mop) actions by that side inside the 5x5."""
import lib
from collections import defaultdict
S = defaultdict(lambda: defaultdict(list))
for G in lib.games():
    W = G.W
    near = lambda x, y: next((r for r in G.ruins if max(abs(r[0] - x), abs(r[1] - y)) <= 2 and (r[0], r[1]) != (x, y)), None)
    first = {}
    for a in G.acts:
        if a[4] == 'mark':
            x, y = map(int, a[5].split(',')); r = near(x, y)
            if r: first.setdefault((a[2], r), a[0])
    b, dd = lib.tower_events(G)
    bfirst = {}
    for x in b:
        if x[0] > 0: bfirst.setdefault((x[3], (x[4], x[5])), []).append(x[0])
    deny = defaultdict(int); denyt = defaultdict(list); clean = defaultdict(int)
    for a in G.acts:
        if a[4] not in ('paint', 'unpaint') or a[3] not in lib.BOT: continue
        x, y = map(int, a[5].split(',')); r = near(x, y)
        if not r: continue
        other = 3 - a[2]
        if (other, r) in first and a[0] >= first[(other, r)] and not any(first[(other, r)] <= z <= a[0] for z in bfirst.get((other, r), [])):
            k = (a[2], r)
            if a[4] == 'paint' and (a[2], r) not in first:
                deny[k] += 1; denyt[k].append((a[0], a[3][:3]))
        if a[4] == 'unpaint' and (a[2], r) in first and a[0] >= first[(a[2], r)]:
            clean[(a[2], r)] += 1
    print(f'== m{G.m} g{G.g} {G.team_name} {G.map}')
    for sd in (G.op, G.us):
        nm = 'TH' if sd == G.op else 'US'
        ks = [k for k in deny if k[0] == sd]
        tot = sum(deny[k] for k in ks)
        # how many of the other side's marked ruins got >= 1 denial paint, and their completion
        om = [r for (s, r) in first if s == 3 - sd]
        hit = [r for r in om if deny.get((sd, r), 0) > 0]
        hit_built = [r for r in hit if any(z >= first[(3 - sd, r)] for z in bfirst.get((3 - sd, r), []))]
        print(f'  {nm} paints into opponent-marked ruins: {tot} paints on {len(hit)}/{len(om)} of their marked ruins; those later built by them: {len(hit_built)}  types {sorted(set(t for k in ks for _, t in denyt[k]))}')
        S[nm]['opp marked ruins hit by our paint %'].append(round(100 * len(hit) / max(1, len(om))))
        S[nm]['denial paints'].append(tot)
        S[nm]['opp ruins hit later built'].append(f'{len(hit_built)}/{len(hit)}')
        mine = [r for (s, r) in first if s == sd]
        S[nm]['own marked ruins with own unpaint (mop) %'].append(round(100 * sum(1 for r in mine if clean.get((sd, r), 0)) / max(1, len(mine))))
        S[nm]['own-ruin mops'].append(sum(clean.get((sd, r), 0) for r in mine))
print('\n== summary')
for nm in ('TH', 'US'):
    print(' ', nm)
    for k, v in S[nm].items(): print(f'     {k:<44} {v}  med {lib.med([z for z in v if not isinstance(z, str)]) if not isinstance(v[0], str) else ""}')

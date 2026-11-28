"""Topic 193 (new): how the eliminations happen (om-nom eliminated y360 four times in nine games, two before r210).
Every loss by ALL_UNITS_DESTROYED in the main set and the set fetched during the study (lib.MAIN + lib.NEW).  Per game:
towers, robots and soldiers each side at r50 / r100 / r150 / r200; then every death of one of our towers: round, type,
the tower's paint at the end of the round before the final assault's first hit (an assault = damage rows on the tower
grouped while the gap is under 15 rounds), the assault's length, its distinct attackers by type, the robots the tower
spawned during it, and our own robots within d2 20 of it at the first hit; then the round our last tower fell and the
robots alive then (their paint, median), and how many of them starved (last turn at 0 paint).  Our own churns (a tower
that vanishes with no damage rows) are listed but left out of the totals.  At the end, totals over
the games: tower deaths by phase, attackers by type, the tower's paint at the first hit (median), spawns per assault."""
from collections import defaultdict
import lib


def analyse(G):
    built, died = lib.tower_events(G)
    pos = {}
    for t in G.turns:
        if t[1] not in pos: pos[t[1]] = (t[4], t[5])
    tpaint = {}
    by_round = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.TOW: tpaint[(t[1], t[0])] = t[7]
        else: by_round[t[0]].append((t[1], t[2], t[3], t[4], t[5], t[7]))
    hits = defaultdict(list); spawns = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage':
            v = int(a[5])
            if G.typ.get(v) in lib.TOW and a[3] in lib.BOT: hits[v].append((a[0], a[1], a[3]))
        elif a[4] == 'spawn': spawns[a[1]].append((a[0], a[6]))
    out = []
    for (r, tid, typ, team, x, y) in died:
        if team != G.us: continue
        hs = sorted(h for h in hits.get(tid, ()) if h[0] <= r)
        ep = []
        for h in reversed(hs):
            if not ep or ep[-1][0] - h[0] < 15: ep.append(h)
            else: break
        ep.reverse()
        r0 = ep[0][0] if ep else r
        att = defaultdict(set)
        for h in ep: att[h[2]].add(h[1])
        own = [u for u in by_round.get(r0, ()) if u[1] == G.us and (u[3] - x) ** 2 + (u[4] - y) ** 2 <= 20]
        sp = [s for s in spawns.get(tid, ()) if r0 <= s[0] <= r]
        out.append(dict(r=r, typ=typ, xy=(x, y), paint=tpaint.get((tid, r0 - 1)), len=r - r0, att={k: len(v) for k, v in att.items()},
                        spawned=len(sp), own=len(own), hit=bool(ep)))
    alive = defaultdict(int)
    for (r, tid, typ, team, x, y) in built:
        if team == G.us: alive[r] += 1
    for (r, tid, typ, team, x, y) in died:
        if team == G.us: alive[r] -= 1
    n = 0; last = None
    for r in sorted(alive):
        n += alive[r]
        if n <= 0 and r > 0: last = r; break
    lastrob = {}
    for t in G.turns:
        if t[2] == G.us and t[3] in lib.BOT: lastrob[t[1]] = t
    rob = [t for t in lastrob.values() if last is not None and t[0] >= last]
    return out, last, rob


tot = defaultdict(list)
for G in lib.games('lost', matches=lib.MAIN + lib.NEW):
    if 'DESTROY' not in str(G.wintype).upper(): continue
    deaths, last, rob = analyse(G)
    print(f'\nm{G.m}g{G.g} {G.ver} vs {G.team_name} on {G.map} ({G.W}x{G.H}), eliminated r{G.end}')
    print('   ' + '   '.join(f'r{r}: towers {lib.rv(G, G.us, r, "tow")}/{lib.rv(G, G.op, r, "tow")} robots {lib.rv(G, G.us, r, "units")}/{lib.rv(G, G.op, r, "units")} '
                             f'sold. {lib.rv(G, G.us, r, "sol")}/{lib.rv(G, G.op, r, "sol")}' for r in (50, 100, 150, 200) if r <= G.end))
    for d in deaths:
        if not d['hit']:
            print(f'   r{d["r"]:4d} {d["typ"]:13s} at {d["xy"]}: disintegrated (no damage rows; our churn)'); continue
        print(f'   r{d["r"]:4d} {d["typ"]:13s} at {d["xy"]}: paint before the assault {d["paint"]}, assault {d["len"]} rounds, attackers '
              + (', '.join(f'{k.lower()} {v}' for k, v in sorted(d['att'].items())) or 'none (no damage rows)') + f', spawned {d["spawned"]}, own robots near {d["own"]}')
        if d['hit']: tot['deaths'].append((G.m, G.g, d))
    st = sum(1 for t in rob if t[7] == 0)
    print(f'   last tower fell r{last}; robots alive then {len(rob)}, paint median {lib.med([t[7] for t in rob])}, of them starved (last turn at 0 paint) {st}')
    tot['games'].append(G.m)
    G.turns = G.acts = None
D = [x[2] for x in tot['deaths']]
print(f'\n== {len(tot["games"])} eliminations, {len(D)} of our towers killed (churns left out)')
for lo, hi in ((1, 100), (101, 200), (201, 300), (301, 2000)):
    E = [d for d in D if lo <= d['r'] <= hi]
    if not E: continue
    at = defaultdict(int)
    for d in E:
        for k, v in d['att'].items(): at[k] += v
    print(f'   r{lo}-{hi}: {len(E)} deaths; paint before the assault (median) {lib.med([d["paint"] for d in E if d["paint"] is not None])}; '
          f'assault rounds (median) {lib.med([d["len"] for d in E])}; attackers per death: ' + ', '.join(f'{k.lower()} {v / len(E):.1f}' for k, v in sorted(at.items()))
          + f'; spawned during it {sum(d["spawned"] for d in E) / len(E):.2f}; own robots near at the first hit (median) {lib.med([d["own"] for d in E])}')

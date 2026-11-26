"""Topic 91: robots that ran dry.  For every robot that ended a turn at 0 paint (both sides, lost and won games): its
type, the phase, whether an enemy mopper drained it in the 10 rounds before, the distance (Chebyshev) to the side's
nearest standing tower at that moment, the paint it held 10 rounds earlier, whether its tile was own / neutral / enemy
paint (replayed grid), whether it got paint again (an ally transfer or a refill) and how it ended (died starved,
killed, alive at the end).  Medians and shares per side and type; then the same for the robots that were never
drained (they ran dry on their own)."""
import lib
from collections import defaultdict, Counter


def dry_events(G):
    b, d = lib.tower_events(G)
    drained = defaultdict(list)
    died = {}
    for a in G.acts:
        if a[4] == 'drain': drained[int(a[5])].append(a[0])
        elif a[4] == 'die' and a[7] in lib.BOT: died[int(a[5])] = (a[0], 'starved' if a[1] == int(a[5]) else 'killed')
    # towers alive per round per side (positions), refreshed when the tower set changes
    ev = sorted([(x[0], 1, x) for x in b] + [(x[0], -1, x) for x in d], key=lambda e: (e[0], -e[1]))
    alive = {1: {}, 2: {}}
    ei = 0
    hist = defaultdict(list)       # id -> [(round, paint)]
    first0 = {}
    grid = list(G.paint0); W = G.W
    ai = 0; acts = G.acts
    out = []
    for t in G.turns:
        r = t[0]
        while ei < len(ev) and ev[ei][0] <= r:
            _, s, x = ev[ei]
            if s > 0: alive[x[3]][x[1]] = (x[4], x[5])
            else: alive[x[3]].pop(x[1], None)
            ei += 1
        while ai < len(acts) and acts[ai][0] <= r:
            a = acts[ai]; ai += 1
            if a[4] == 'paint':
                x, y = map(int, a[5].split(',')); sec = a[6] == '1'
                grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
            elif a[4] == 'unpaint':
                x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
        if t[3] not in lib.BOT: continue
        h = hist[t[1]]; h.append((r, t[7]))
        if t[7] == 0 and t[1] not in first0:
            first0[t[1]] = r
            tw = alive[t[2]].values()
            dist = min((max(abs(p[0] - t[4]), abs(p[1] - t[5])) for p in tw), default=99)
            before = next((p for (rr, p) in reversed(h) if rr <= r - 10), None)
            o = lib.owner(grid[t[4] + t[5] * W]); me = 1 if t[2] == 1 else 2
            tile = 'own' if o == me else 'neutral' if o == 0 else 'enemy'
            dr = any(r - 10 <= x <= r for x in drained.get(t[1], ()))
            out.append(dict(id=t[1], side='us' if t[2] == G.us else 'them', typ=t[3][:2], r=r, dist=dist, before=before, tile=tile, drained=dr))
    for e in out:
        h = hist[e['id']]
        e['recovered'] = any(p > 0 for (rr, p) in h if rr > e['r'])
        e['end'] = died.get(e['id'], (None, 'alive'))[1]
    return out


for which in ('lost', 'won'):
    S = defaultdict(list); n = 0; turns = Counter()
    for G in lib.games(which):
        n += 1
        for t in G.turns:
            if t[3] in lib.BOT: turns[('us' if t[2] == G.us else 'them', t[3][:2])] += 1
        for e in dry_events(G): S[(e['side'], e['typ'])].append(e)
    print(f'== {which} games ({n}): robots that ran dry (first turn ending at 0 paint)')
    print('   side type  dry  per100turns  drained%  dist-to-tower med (p75)  paint 10r before med  tile own/neutral/enemy %  got paint again%  then died starved%')
    for side in ('us', 'them'):
        for ty in ('SO', 'SP', 'MO'):
            L = S[(side, ty)]
            if not L: continue
            tl = Counter(e['tile'] for e in L)
            print(f'   {side:4s} {ty}  {len(L):5d}     {100 * len(L) / max(1, turns[(side, ty)]):5.2f}     {100 * sum(e["drained"] for e in L) / len(L):4.0f}%     '
                  f'{lib.med([e["dist"] for e in L])} ({lib.pct([e["dist"] for e in L], 0.75)})               {lib.med([e["before"] for e in L])}         '
                  f'{100 * tl["own"] // len(L)}/{100 * tl["neutral"] // len(L)}/{100 * tl["enemy"] // len(L)}                 '
                  f'{100 * sum(e["recovered"] for e in L) / len(L):4.0f}%            {100 * sum(e["end"] == "starved" for e in L) / len(L):4.0f}%')
    print('   never drained in the 10 rounds before (ran dry on their own):')
    for side in ('us', 'them'):
        for ty in ('SO', 'SP', 'MO'):
            L = [e for e in S[(side, ty)] if not e['drained']]
            if not L: continue
            far = sum(e['dist'] >= 8 for e in L)
            print(f'      {side:4s} {ty}: {len(L)} ({100 * len(L) / max(1, turns[(side, ty)]):.2f} per 100 turns); distance to our nearest tower med {lib.med([e["dist"] for e in L])}, '
                  f'>= 8 tiles in {100 * far // len(L)}%; paint 10 rounds before med {lib.med([e["before"] for e in L])}')
    print()

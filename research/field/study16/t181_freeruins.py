"""Topic 181 (new): why free ruins stay free in r101-300 (t180: in our losses 8 ruins are free at r100 and 4.5 at r200,
yet we build 0.43 new paint and 1.04 new money towers in r101-200 against 2.08 and 1.49 in our wins).
For every ruin and every round of r101-300 (sampled every 2nd round) in which no tower stands on it (a 'free round'):
  contested   the 5x5 holds enemy paint (Soldier.pickRuin skips it: Pattern.contested, then markBad for 50 rounds)
  seen        one of our soldiers ends its turn within r2 20 of the ruin (pickRuin iterates the ruins in sight)
  seen, able  ... a soldier of ours with 60+ paint
  worked      one of our soldiers ends its turn within Chebyshev 2 of the ruin's centre
Free rounds are split into: contested; clean and seen by an able soldier; clean and seen only by soldiers under 60
paint; clean and unseen.  Also per ruin free at r101: the Chebyshev distance to our nearest standing tower and to
theirs, and what became of it by r300 (built by us, by them, still free) and when.  The same for them (their
soldiers, our paint).  Losses and wins; ours by version."""
from collections import defaultdict
import lib

R0, R1, STEP = 101, 300, 2


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def analyse(G):
    if G.end < R0: return None
    ruins = list(G.ruins)
    rset = set(ruins)
    # towers standing per round (by position) and their team
    stand = defaultdict(dict)
    for t in G.turns:
        if t[3] in lib.TOW and R0 - 1 <= t[0] <= R1 and (t[4], t[5]) in rset: stand[t[0]][(t[4], t[5])] = t[2]
    sold = defaultdict(list)
    for t in G.turns:
        if t[3] == 'SOLDIER' and R0 <= t[0] <= R1 and (t[0] - R0) % STEP == 0: sold[t[0]].append((t[4], t[5], t[2], t[7]))
    towers_at = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.TOW and t[0] == R0: towers_at[t[2]].append((t[4], t[5]))
    # enemy paint in each ruin's 5x5, sampled at the round boundaries
    samp = list(range(R0, min(R1, G.end) + 1, STEP))
    cont = {}   # (round, ruin, side) -> enemy paint in the 5x5 against side
    st = {'ix': 0}

    def check(grid, upto):
        while st['ix'] < len(samp) and samp[st['ix']] <= upto:
            r = samp[st['ix']]
            for (x, y) in ruins:
                c1 = c2 = False
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < G.W and 0 <= yy < G.H:
                            o = lib.owner(grid[xx + yy * G.W])
                            if o == 2: c1 = True
                            elif o == 1: c2 = True
                cont[(r, (x, y), 1)] = c1; cont[(r, (x, y), 2)] = c2
            st['ix'] += 1
    last = {'r': 0}

    def hook(a, grid):
        if a[0] != last['r']:
            check(grid, a[0] - 1); last['r'] = a[0]
    g = lib.replay_grid(G, hook); check(g, 10 ** 9)
    out = {}
    for sd, team in (('us', G.us), ('them', G.op)):
        c = defaultdict(int)
        for r in samp:
            for ru in ruins:
                if ru in stand.get(r, {}): continue
                c['free'] += 1
                if cont.get((r, ru, team)): c['contested'] += 1; continue
                near = [s for s in sold.get(r, []) if s[2] == team and (s[0] - ru[0]) ** 2 + (s[1] - ru[1]) ** 2 <= 20]
                if any(s[3] >= 60 for s in near): c['able'] += 1
                elif near: c['weak'] += 1
                else: c['unseen'] += 1
                if any(cheb(s[:2], ru) <= 2 for s in near): c['worked'] += 1
        out[sd] = c
        # ruins free at R0: distance to the nearest standing tower of each side, fate by R1
        fate = []
        for ru in ruins:
            if ru in stand.get(R0, {}) or ru in stand.get(R0 - 1, {}): continue
            dm = min((cheb(ru, p) for p in towers_at[team]), default=None)
            do = min((cheb(ru, p) for p in towers_at[3 - team]), default=None)
            f = ('free', None)
            for r in range(R0, min(R1, G.end) + 1):
                if ru in stand.get(r, {}):
                    f = ('ours' if stand[r][ru] == team else 'theirs', r); break
            fate.append((dm, do, f))
        out[sd + 'fate'] = fate
    return out


def report(tag, OS):
    OS = [o for o in OS if o]
    if not OS: return
    print(f'\n== {tag}: {len(OS)} games (r{R0}-{R1}, every {STEP}nd round; ruin-rounds per game)')
    for sd in ('us', 'them'):
        tot = defaultdict(int)
        for o in OS:
            for k, v in o[sd].items(): tot[k] += v
        f = max(1, tot['free'])
        print(f'   {sd:4s}: free ruin-rounds {tot["free"] / len(OS) * STEP:.0f}/game;  contested {100 * tot["contested"] / f:.0f}%,  '
              f'clean & seen by a soldier with 60+ paint {100 * tot["able"] / f:.0f}%,  clean & seen only under 60 {100 * tot["weak"] / f:.0f}%,  '
              f'clean & unseen {100 * tot["unseen"] / f:.0f}%;  a soldier within Chebyshev 2 {100 * tot["worked"] / f:.0f}%')
        fates = [x for o in OS for x in o[sd + 'fate']]
        n = len(fates)
        if not n: continue
        mine = [x for x in fates if x[0] is not None and x[1] is not None and x[0] < x[1]]
        theirs = [x for x in fates if x[0] is not None and x[1] is not None and x[0] > x[1]]
        def fl(xs):
            if not xs: return '-'
            k = len(xs)
            return (f'{k} ruins: built by {sd} {100 * sum(x[2][0] == "ours" for x in xs) / k:.0f}% (med r{lib.med([x[2][1] for x in xs if x[2][0] == "ours"])}), '
                    f'by the other side {100 * sum(x[2][0] == "theirs" for x in xs) / k:.0f}%, free at r{R1} {100 * sum(x[2][0] == "free" for x in xs) / k:.0f}%')
        print(f'         ruins free at r{R0}: {n / len(OS):.1f}/game, Chebyshev to own nearest tower med {lib.med([x[0] for x in fates])}, to the other side\'s {lib.med([x[1] for x in fates])}')
        print(f'           nearer to {sd}: {fl(mine)}')
        print(f'           nearer to the other side: {fl(theirs)}')


RES = defaultdict(list)
for G in lib.games('all'):
    o = analyse(G)
    RES['lost' if G.won_op else 'won'].append(o)
    RES['ver ' + G.ver + (' lost' if G.won_op else ' won')].append(o)
    G.turns = G.acts = None
for k in ('lost', 'won'): report(k, RES[k])
for k in sorted(RES):
    if k.startswith('ver'): report(k, RES[k])

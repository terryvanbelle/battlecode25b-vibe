"""Topic 188 (new; follows t181): clean spells of free ruins in r101-300.  Sampled every 2nd round as t181.  A clean
spell (for a side) = a maximal run of samples in which a ruin has no tower and no enemy paint (of the other side) in
its 5x5.  Per spell: its length; whether it began right after a contested sample (the ruin was cleaned) or at r101;
whether one of the side's soldiers came within Chebyshev 2 of the ruin during it and after how many rounds; and how it
ended: the side built there, the other side built there, enemy paint came back, or r300.  Per side, losses and wins,
split by the ruin being nearer (Chebyshev, at r101) to the side's own towers or to the other side's.  Soldier.pickRuin
marks a contested ruin bad for 50 rounds (Tune.SOL_CONTESTED_BAD), so a soldier that saw it contested skips it for 50
rounds even when it is cleaned."""
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
        # clean spells
        spells = []
        for ru in ruins:
            dm = min((cheb(ru, p) for p in towers_at[team]), default=99)
            do = min((cheb(ru, p) for p in towers_at[3 - team]), default=99)
            cur = None; prev = None
            for r in samp:
                tw = stand.get(r, {}).get(ru)
                if tw is not None:
                    st_ = 'own' if tw == team else 'other'
                elif cont.get((r, ru, team)): st_ = 'cont'
                else: st_ = 'clean'
                if st_ == 'clean':
                    if cur is None: cur = dict(r0=r, after=(prev == 'cont'), seen=None, near=dm < do)
                    if cur['seen'] is None and any(s[2] == team and cheb(s[:2], ru) <= 2 for s in sold.get(r, [])): cur['seen'] = r - cur['r0']
                    cur['r1'] = r
                elif cur is not None:
                    cur['end'] = {'own': 'built by the side', 'other': 'built by the other side', 'cont': 'enemy paint back'}[st_]
                    spells.append(cur); cur = None
                prev = st_
            if cur is not None: cur['end'] = 'r300 / end'; spells.append(cur)
        out[sd + 'spells'] = spells
    return out


def report(tag, OS):
    OS = [o for o in OS if o]
    if not OS: return
    print(f'\n== {tag}: {len(OS)} games; clean spells of free ruins in r{R0}-{R1}')
    for sd in ('us', 'them'):
        for near in (True, False):
            S = [s for o in OS for s in o[sd + 'spells'] if s['near'] == near]
            if not S: continue
            n = len(S)
            ends = defaultdict(int)
            for s in S: ends[s['end']] += 1
            cl = [s for s in S if s['after']]
            print(f'   {sd:4s} ruins nearer to {"own" if near else "the other side"} towers: {n / len(OS):.1f} spells/game, length med {lib.med([s["r1"] - s["r0"] + STEP for s in S])} rounds; '
                  f'began by a cleaning {100 * len(cl) / n:.0f}%; a soldier of the side within Chebyshev 2 during it {100 * sum(s["seen"] is not None for s in S) / n:.0f}% '
                  f'(after med {lib.med([s["seen"] for s in S])} rounds; after a cleaning {100 * sum(s["seen"] is not None for s in cl) / max(1, len(cl)):.0f}%)')
            print('        ended: ' + ', '.join(f'{k} {100 * v / n:.0f}%' for k, v in sorted(ends.items())) +
                  ' | after a cleaning: ' + ', '.join(f'{k} {100 * sum(1 for s in cl if s["end"] == k) / max(1, len(cl)):.0f}%' for k in sorted(ends)))


RES = defaultdict(list)
for G in lib.games('all'):
    o = analyse(G)
    RES['lost' if G.won_op else 'won'].append(o)
    RES['ver ' + G.ver + (' lost' if G.won_op else ' won')].append(o)
    G.turns = G.acts = None
for k in ('lost', 'won'): report(k, RES[k])

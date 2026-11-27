"""Topic 135: why our siege episodes die (t134: in r101-200 of the losses 36% of our soldier siege episodes end with the
soldier dead and the tower standing, theirs 20%; 62% of ours are alone, 53% of theirs).  Same episodes as t134 (one
soldier's 'attack' rows on enemy towers, gaps <= 5 rounds, same target).  Per side and phase (r1-100 / r101-200 /
r201-400), sums over the games:
  alone / group   episodes and outcome shares (killed / died / left) for lone and accompanied episodes
  paint           the soldier's paint at the end of its first and last hit turns (medians), by outcome
  dry             episodes whose soldier was at <= 5 paint at the end of its last hit turn, and their outcomes
  cause           died episodes: shot by a tower ('die' actor is a tower) or starved (actor = the soldier itself)
  drained         episodes in which an enemy mopper drained the soldier ('drain' row on it) during the episode
  target          the tower's HP at the end of the round before the first hit (median), by outcome; share of episodes
                  on a tower at <= 500 HP; share on defense towers; hits per episode
Lost and won games."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 400))


def analyse(G, T):
    hp, pt, thp = {}, {}, {}
    for t in G.turns:
        if t[3] == 'SOLDIER': hp[(t[0], t[1])] = t[6]; pt[(t[0], t[1])] = t[7]
        elif t[3] in lib.TOW: thp[(t[0], t[1])] = t[6]
    tdie, sdie, cause = {}, {}, {}
    drains = defaultdict(list)
    for a in G.acts:
        k = a[4]
        if k == 'die':
            v = int(a[5])
            if a[7] in lib.TOW: tdie[v] = a[0]
            elif a[7] == 'SOLDIER':
                sdie[v] = a[0]; cause[v] = 'starved' if a[1] == v else 'shot'
        elif k == 'died' and G.typ.get(int(a[5])) in lib.TOW:
            tdie.setdefault(int(a[5]), a[0])
        elif k == 'drain' and a[3] == 'MOPPER':
            try: drains[int(a[5])].append(a[0])
            except ValueError: pass
    hits = defaultdict(list); bytower = defaultdict(list)
    for a in G.acts:
        if a[4] == 'attack' and a[3] == 'SOLDIER' and a[0] <= 400:
            tgt = int(a[5]) if a[5].lstrip('-').isdigit() else None
            if tgt is None or G.typ.get(tgt) not in lib.TOW: continue
            hits[a[1]].append((a[0], tgt)); bytower[(a[2], tgt)].append((a[0], a[1]))
    for sid, H in hits.items():
        side = G.team.get(sid); who = 'us' if side == G.us else 'them'
        eps = []
        for (r, tg) in H:
            if eps and r - eps[-1][-1][0] <= 5 and eps[-1][-1][1] == tg: eps[-1].append((r, tg))
            else: eps.append([(r, tg)])
        for E in eps:
            r0, tg = E[0]; r1 = E[-1][0]
            j = next(i for i, (lo, hi) in enumerate(PH) if lo <= r0 <= hi)
            m = T[(who, j)]
            dr = tdie.get(tg)
            if dr is not None and r0 <= dr <= r1 + 2: out = 'killed'
            elif sid in sdie and r1 <= sdie[sid] <= r1 + 3: out = 'died'
            else: out = 'left'
            others = [s for (r, s) in bytower[(side, tg)] if s != sid and any(abs(r - rr) <= 3 for (rr, _) in E)]
            grp = 'group' if others else 'alone'
            m[grp + ' n'] += 1; m[grp + ' ' + out] += 1
            m['n'] += 1; m['hits'] += len(E)
            p0 = pt.get((r0, sid)); p1 = pt.get((r1, sid))
            if p0 is not None: m.setdefault('p0 ' + out, []).append(p0)
            if p1 is not None:
                m.setdefault('p1 ' + out, []).append(p1)
                if p1 <= 5: m['dry n'] += 1; m['dry ' + out] += 1
            if out == 'died': m['cause ' + cause.get(sid, '?')] += 1
            if any(r0 <= r <= r1 + 1 for r in drains.get(sid, ())): m['drained n'] += 1; m['drained ' + out] += 1
            h = thp.get((r0 - 1, tg))
            if h is not None:
                m.setdefault('thp ' + out, []).append(h)
                m['tlow'] += h <= 500; m['thp n'] += 1
            m['def'] += G.typ.get(tg) == 'DEFENSE_TOWER'


def sh(m, pre):
    n = m[pre + ' n']
    if not n: return f'{pre} 0'
    return (f'{pre} {int(n)} (killed {100 * m[pre + " killed"] / n:.0f}% died {100 * m[pre + " died"] / n:.0f}% '
            f'left {100 * m[pre + " left"] / n:.0f}%)')


for which in ('lost', 'won'):
    T = defaultdict(lambda: defaultdict(float)); n = 0
    for G in lib.games(which):
        n += 1
        analyse(G, T)
        lib.lite(G)
    print(f'\n== {which} games ({n}): soldier siege episodes on enemy towers (sums; medians)')
    for j, (lo, hi) in enumerate(PH):
        for who in ('us', 'them'):
            m = T[(who, j)]; e = max(1, m['n'])
            print(f'   r{lo}-{hi} {who:4s} episodes {int(m["n"])}, {m["hits"] / e:.1f} hits each, '
                  f'defense-tower targets {100 * m["def"] / e:.0f}%')
            print(f'      {sh(m, "alone")}; {sh(m, "group")}')
            print(f'      paint at first hit: killed {lib.med(m.get("p0 killed", []))} died {lib.med(m.get("p0 died", []))} '
                  f'left {lib.med(m.get("p0 left", []))};  at last hit: killed {lib.med(m.get("p1 killed", []))} '
                  f'died {lib.med(m.get("p1 died", []))} left {lib.med(m.get("p1 left", []))}')
            print(f'      {sh(m, "dry")} [<= 5 paint after the last hit];  died episodes: shot {int(m["cause shot"])}, '
                  f'starved {int(m["cause starved"])};  {sh(m, "drained")} [drained by a mopper]')
            print(f'      target HP before the first hit: killed {lib.med(m.get("thp killed", []))} '
                  f'died {lib.med(m.get("thp died", []))} left {lib.med(m.get("thp left", []))}; '
                  f'at <= 500 HP {100 * m["tlow"] / max(1, m["thp n"]):.0f}%')

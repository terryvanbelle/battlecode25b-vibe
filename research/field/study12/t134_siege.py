"""Topic 134: siege efficiency, both sides (t133: 89-99% of the tower damage our robots take in r1-200 comes in rounds
they hit a tower, and 93 of our 98 r1-100 deaths after a tower hit were sieging soldiers, theirs 46 of 57).
A SIEGE EPISODE is one soldier's run of 'attack' rows on enemy towers with gaps of at most 5 rounds.  Its outcome:
'killed' (the target tower died during the episode or within 2 rounds of its end), 'died' (the soldier died within 3
rounds of its last hit and the tower stood), else 'left' (the soldier walked away alive).  Per side, phase of the
episode start (r1-100 / r101-200 / r201-400): episodes, hits, outcome shares, the soldier's HP at the first hit (end
of that turn) and at the last hit, alone (no other soldier of the side hit that tower within 3 rounds of any of its
hits), towers killed by soldier hits ('die' rows by a soldier on a tower), soldiers lost per tower killed, and how
often a soldier kept hitting at 60 HP or less (3 tower shots from death).  Lost and won games."""
import lib
from collections import defaultdict

PH = ((1, 100), (101, 200), (201, 400))


def analyse(G, S):
    hp = {}
    for t in G.turns:
        if t[3] == 'SOLDIER': hp[(t[0], t[1])] = t[6]
    tdie = {}   # tower id -> death round
    sdie = {}   # soldier id -> death round
    tkills = defaultdict(int)
    for a in G.acts:
        if a[4] == 'die':
            v = int(a[5]); vt = a[7]
            if vt in lib.TOW:
                tdie[v] = a[0]
                if a[3] == 'SOLDIER' and a[0] <= 400:
                    j = next(i for i, (lo, hi) in enumerate(PH) if lo <= max(1, a[0]) <= hi)
                    tkills[(a[2], j)] += 1
            elif vt == 'SOLDIER':
                sdie[v] = a[0]
        elif a[4] == 'died' and G.typ.get(int(a[5])) in lib.TOW:
            tdie.setdefault(int(a[5]), a[0])
    for k, v in tkills.items(): S[k]['tower kills'] += v
    hits = defaultdict(list)       # soldier -> [(round, target)]
    bytower = defaultdict(list)    # (side, target) -> [(round, soldier)]
    for a in G.acts:
        if a[4] == 'attack' and a[3] == 'SOLDIER' and a[0] <= 400:
            tgt = int(a[5]) if a[5].lstrip('-').isdigit() else None
            if tgt is None or G.typ.get(tgt) not in lib.TOW: continue
            hits[a[1]].append((a[0], tgt)); bytower[(a[2], tgt)].append((a[0], a[1]))
    for sid, H in hits.items():
        side = G.team.get(sid)
        eps = []
        for (r, tg) in H:
            if eps and r - eps[-1][-1][0] <= 5 and eps[-1][-1][1] == tg: eps[-1].append((r, tg))
            else: eps.append([(r, tg)])
        for E in eps:
            r0, tg = E[0]; r1 = E[-1][0]
            j = next(i for i, (lo, hi) in enumerate(PH) if lo <= r0 <= hi)
            m = S[(side, j)]
            m['episodes'] += 1; m['hits'] += len(E)
            dr = tdie.get(tg)
            if dr is not None and r0 <= dr <= r1 + 2: out = 'killed'
            elif sid in sdie and r1 <= sdie[sid] <= r1 + 3: out = 'died'
            else: out = 'left'
            m['out ' + out] += 1
            h0 = hp.get((r0, sid)); h1 = hp.get((r1, sid))
            if h0 is not None: m.setdefault('hp0', []).append(h0)
            if h1 is not None: m.setdefault('hp1 ' + out, []).append(h1)
            low = sum(1 for (r, _) in E if hp.get((r, sid), 999) <= 60)
            m['hits at <=60 HP'] += low
            others = [s for (r, s) in bytower[(side, tg)] if s != sid and any(abs(r - rr) <= 3 for (rr, _) in E)]
            m['alone'] += not others


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); n = 0
    T = defaultdict(lambda: defaultdict(float))
    for G in lib.games(which):
        n += 1
        U = defaultdict(lambda: defaultdict(float))
        analyse(G, U)
        for (sd, j), m in U.items():
            who = 'us' if sd == G.us else 'them'
            for k, v in m.items():
                if isinstance(v, list): T[(who, j)].setdefault(k, []); T[(who, j)][k] += v
                else: T[(who, j)][k] += v
        lib.lite(G)
    print(f'\n== {which} games ({n}): soldier siege episodes on enemy towers (sums; HP medians)')
    for j, (lo, hi) in enumerate(PH):
        for who in ('us', 'them'):
            m = T[(who, j)]; e = max(1, m['episodes'])
            print(f'   r{lo}-{hi} {who:4s} episodes {int(m["episodes"]):4d} hits {int(m["hits"]):5d} '
                  f'killed {100 * m["out killed"] / e:4.1f}% died {100 * m["out died"] / e:4.1f}% left {100 * m["out left"] / e:4.1f}% '
                  f'alone {100 * m["alone"] / e:4.1f}%  HP first hit {lib.med(m.get("hp0", []))}  last hit: died {lib.med(m.get("hp1 died", []))} '
                  f'left {lib.med(m.get("hp1 left", []))} killed {lib.med(m.get("hp1 killed", []))}  hits at <=60 HP {int(m["hits at <=60 HP"])}  '
                  f'tower kills by soldiers {int(m["tower kills"])}  soldiers died per kill {m["out died"] / max(1, m["tower kills"]):.2f}')

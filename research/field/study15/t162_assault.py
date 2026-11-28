"""Topic 162: which tower assaults a tower survives (follows t149/t160: our towers die with fewer own robots around in
r1-200, and their towers kill 0.44 / 0.64 attackers per final assault in r101+, ours 0.25 / 0.27).
An assault = the damage rows on one tower, grouped while the gap between hits is under 15 rounds.  It is 'lost' when
the tower dies ('die' row) in it, else 'held'.  Both sides; per side and phase of the assault's first hit.
Per assault:
  length          rounds from the first to the last hit; damage taken; distinct attackers (enemy robots with a
                  damage row on the tower)
  tower paint     the tower's paint at the end of the round before the first hit (turns rows)
  spawns          robots the tower spawned during the assault, and of them moppers (Tower.choose: OPENING is all
                  soldiers before r80; a mopper is due on cycle slots only)
  own robots      own robots within d2 20 of the tower, mean per round end; of them moppers; 'alone' = none at any
                  round end of the assault
  mops            'drain' rows by own moppers standing within d2 20 of the tower (mop and swing hits on robots)
  attackers out   attackers that died during the assault or within 5 rounds after: killed by the tower, by another
                  robot or tower, or starved (their own 'die' row); attackers alive whose last turn row in the assault
                  shows 0 paint
Losses then wins."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def analyse(G, S):
    pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5])
    by_round = defaultdict(list)       # round -> (id, team, type, x, y, paint)
    for t in G.turns: by_round[t[0]].append((t[1], t[2], t[3], t[4], t[5], t[7]))
    tpaint = {}                        # (tower id, round) -> paint
    for t in G.turns:
        if t[3] in lib.TOW: tpaint[(t[1], t[0])] = t[7]
    hits = defaultdict(list)           # tower id -> [(round, attacker id, attacker type, amount)]
    deaths = {}                        # victim id -> (round, killer id)
    spawns = defaultdict(list)         # tower id -> [(round, type)]
    drains = defaultdict(list)         # round -> [(mopper id, team)]
    for a in G.acts:
        k = a[4]
        if k == 'damage':
            v = int(a[5])
            if G.typ.get(v) in lib.TOW and a[3] in lib.BOT: hits[v].append((a[0], a[1], a[3], int(a[6] or 0)))
        elif k == 'die':
            deaths[int(a[5])] = (a[0], a[1])
        elif k == 'spawn':
            spawns[a[1]].append((a[0], a[6]))
        elif k == 'drain' and a[3] == 'MOPPER':
            drains[a[0]].append((a[1], a[2]))
    for tid, hs in hits.items():
        side = G.team.get(tid); q = pos.get(tid)
        if not side or not q: continue
        hs.sort()
        eps = []
        for h in hs:
            if eps and h[0] - eps[-1][-1][0] < 15: eps[-1].append(h)
            else: eps.append([h])
        dr = deaths.get(tid)
        for ep in eps:
            r0, r1 = ep[0][0], ep[-1][0]
            lost = dr is not None and r0 <= dr[0] <= r1 + 1
            att = {h[1] for h in ep}
            near = []; mops = []; alone = True; drn = 0
            for r in range(r0, r1 + 1):
                own = [u for u in by_round.get(r, ()) if u[1] == side and u[2] in lib.BOT and (u[3] - q[0]) ** 2 + (u[4] - q[1]) ** 2 <= 20]
                near.append(len(own)); mops.append(sum(1 for u in own if u[2] == 'MOPPER'))
                if own: alone = False
                ids = {u[0] for u in own if u[2] == 'MOPPER'}
                drn += sum(1 for (m, tm) in drains.get(r, ()) if tm == side and m in ids)
            sp = [s for s in spawns.get(tid, ()) if r0 <= s[0] <= r1]
            out_t = out_o = out_s = 0
            for a_ in att:
                d = deaths.get(a_)
                if d and r0 <= d[0] <= r1 + 5:
                    if d[1] == tid: out_t += 1
                    elif d[1] == a_: out_s += 1
                    else: out_o += 1
            zero = 0
            for a_ in att:
                if deaths.get(a_) and deaths[a_][0] <= r1 + 5: continue
                last = None
                for r in range(r1, r0 - 1, -1):
                    for u in by_round.get(r, ()):
                        if u[0] == a_: last = u; break
                    if last: break
                if last and last[5] == 0: zero += 1
            e = dict(lost=lost, len=r1 - r0 + 1, dmg=sum(h[3] for h in ep), att=len(att),
                     paint=tpaint.get((tid, r0 - 1), tpaint.get((tid, r0))), sp=len(sp),
                     spm=sum(1 for s in sp if s[1] == 'MOPPER'), near=sum(near) / len(near), mop=sum(mops) / len(mops),
                     alone=alone, drn=drn, out_t=out_t, out_o=out_o, out_s=out_s, zero=zero)
            sd = 'us' if side == G.us else 'them'
            for key in ((sd, ph(r0)), (sd, 'all')):
                S[key].append(e)


def row(name, f, sel=None):
    return name, f, sel


def fmt(es, f):
    return f(es) if es else '-'


def pct(es, k): return f"{100 * sum(1 for e in es if e[k]) / len(es):.0f}%"
def mean(es, k): return f"{sum(e[k] for e in es) / len(es):.2f}"
def med(es, k): return f"{lib.med([e[k] for e in es if e[k] is not None])}"


ROWS = (
    ('assaults', lambda es: f'{len(es)}'),
    ('  lost (the tower died)', lambda es: pct(es, 'lost')),
    ('length, rounds (median)', lambda es: med(es, 'len')),
    ('damage taken (median)', lambda es: med(es, 'dmg')),
    ('distinct attackers (mean)', lambda es: mean(es, 'att')),
    ('tower paint before the first hit (median)', lambda es: med(es, 'paint')),
    ('spawns during it (mean)', lambda es: mean(es, 'sp')),
    ('  of them moppers (mean)', lambda es: mean(es, 'spm')),
    ('own robots d2<=20, mean per round', lambda es: mean(es, 'near')),
    ('  of them moppers', lambda es: mean(es, 'mop')),
    ('alone (no own robot at any round end)', lambda es: pct(es, 'alone')),
    ('mop hits by own moppers near it (mean)', lambda es: mean(es, 'drn')),
    ('attackers killed by the tower (mean)', lambda es: mean(es, 'out_t')),
    ('attackers killed by others (mean)', lambda es: mean(es, 'out_o')),
    ('attackers starved (mean)', lambda es: mean(es, 'out_s')),
    ('attackers alive at 0 paint (mean)', lambda es: mean(es, 'zero')),
)

for which in ('lost', 'won'):
    S = defaultdict(list)
    ng = 0
    for G in lib.games(which):
        ng += 1
        analyse(G, S)
    print(f'\n== {which}: {ng} games; tower assaults (hits < 15 rounds apart), by the side whose tower was hit')
    cols = [('us', 0), ('them', 0), ('us', 1), ('them', 1), ('us', 2), ('them', 2), ('us', 'all'), ('them', 'all')]
    print(f'{"":44s}' + ''.join(f'{(PHN[p] if p != "all" else "all") + " " + s:>14s}' for s, p in cols))
    for name, f in ROWS:
        print(f'{name:44s}' + ''.join(f'{fmt(S[c], f):>14s}' for c in cols))
    for sub, cond in (('held', False), ('lost', True)):
        print(f'  -- {sub} assaults only (all phases), us / them')
        for name, f in ROWS[2:]:
            a = [e for e in S[('us', 'all')] if e['lost'] == cond]
            b = [e for e in S[('them', 'all')] if e['lost'] == cond]
            print(f'  {name:42s}{fmt(a, f):>14s}{fmt(b, f):>14s}')

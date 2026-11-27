"""Topic 121: did the splasher stand-off (t111, study 8 2.4) change the tower exchange?  Same measures on study 10's
set (t111 / t118) and study 9's (y195-y221, no stand-off), lost and won games, per side, phase r1-200 / r201+:
  X-turns        splasher-turns
  X dmg          splasher HP damage on enemy towers ('damage' rows by splashers on a tower), per 100 splasher-turns
  out%           share of it dealt from d2 10-16 of the tower (outside a paint / money tower's d2 9 reach)
  S dmg          soldier HP damage on enemy towers per 100 soldier-turns
  kills          enemy towers killed (die rows of the other side's towers; actor = the killer), by killer type
  X deaths       splasher deaths per 100 splasher-turns, and the share killed by a tower (actor is a tower)
  standoff       share of the side's splasher-turns ending at d2 10-16 from an enemy paint/money tower standing then
                 with no enemy tower at d2 <= 9
Medians per game for the rates, sums for counts."""
import lib
from collections import defaultdict

PH = ((1, 200, 'r1-200'), (201, 3000, 'r201+'))


def phase(r):
    return 0 if r <= 200 else 1


def analyse(G):
    o = {s: defaultdict(float) for s in (1, 2)}
    pos = {}
    for t in G.turns:
        pos[(t[0], t[1])] = (t[4], t[5])
        if t[3] in lib.BOT: o[t[2]][(phase(t[0]), 'turns ' + t[3][:3])] += 1
    b, d = lib.tower_events(G)
    died = {x[1]: x[0] for x in d}
    alive = [(x[0], died.get(x[1], 10 ** 6), x[3], x[2], (x[4], x[5])) for x in b]
    for a in G.acts:
        k = a[4]
        if k == 'damage' and a[3] in ('SPLASHER', 'SOLDIER'):
            tid = int(a[5])
            if G.typ.get(tid, '') not in lib.TOW: continue
            amt = int(a[6] or 0)
            p = phase(a[0])
            o[a[2]][(p, 'dmg ' + a[3][:3])] += amt
        if k == 'die':
            vic = int(a[5]); vt = a[7]
            p = phase(a[0])
            if vt in lib.TOW and a[2] != G.team.get(vic, a[2]):
                o[a[2]][(p, 'kill by ' + a[3][:3])] += 1
                o[a[2]][(p, 'kills')] += 1
            if vt == 'SPLASHER':
                side = G.team.get(vic)
                if side is None: continue
                o[side][(p, 'X deaths')] += 1
                if a[3] in lib.TOW: o[side][(p, 'X killed by tower')] += 1
    return o, pos, alive


def outside_share(G, pos):
    """splasher damage on towers from d2 10-16 of the tower, per side and phase"""
    tpos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in tpos: tpos[t[1]] = (t[4], t[5])
    res = {s: defaultdict(float) for s in (1, 2)}
    for a in G.acts:
        if a[4] != 'damage' or a[3] != 'SPLASHER': continue
        tid = int(a[5])
        if tid not in tpos: continue
        p = pos.get((a[0], a[1]))
        if p is None: continue
        dd = lib.d2(p, tpos[tid])
        if 10 <= dd <= 16: res[a[2]][(phase(a[0]), 'out')] += int(a[6] or 0)
    return res


def standoff_turns(G, alive):
    res = {s: defaultdict(float) for s in (1, 2)}
    for t in G.turns:
        if t[3] != 'SPLASHER': continue
        r = t[0]; me = (t[4], t[5])
        best = None; near = False
        for (r0, r1, side, typ, p) in alive:
            if side == t[2] or not (r0 <= r < r1): continue
            dd = lib.d2(me, p)
            if dd <= 9: near = True; break
            if typ != 'DEFENSE_TOWER' and 10 <= dd <= 16: best = dd
        if best is not None and not near: res[t[2]][(phase(r), 'standoff')] += 1
    return res


def run(label, matches):
    for which in ('lost', 'won'):
        per = defaultdict(list); sums = defaultdict(float); n = 0
        for G in lib.games(which, matches=matches):
            n += 1
            o, pos, alive = analyse(G)
            out = outside_share(G, pos)
            so = standoff_turns(G, alive)
            for side, who in ((G.us, 'us'), (G.op, 'them')):
                for p in (0, 1):
                    if p == 1 and G.end <= 200: continue
                    x = o[side]
                    xt = x[(p, 'turns SPL')]; st = x[(p, 'turns SOL')]
                    xd = x[(p, 'dmg SPL')]; sd = x[(p, 'dmg SOL')]
                    for k in ('turns SPL', 'turns SOL', 'dmg SPL', 'dmg SOL', 'kills', 'kill by SPL', 'kill by SOL',
                              'kill by MOP', 'X deaths', 'X killed by tower'):
                        sums[(who, p, k)] += x[(p, k)]
                    sums[(who, p, 'out')] += out[side][(p, 'out')]
                    sums[(who, p, 'standoff')] += so[side][(p, 'standoff')]
                    if xt >= 50:
                        per[(who, p, 'xdmg100')].append(100 * xd / xt)
                        per[(who, p, 'xdeath100')].append(100 * x[(p, 'X deaths')] / xt)
                        per[(who, p, 'standoff%')].append(100 * so[side][(p, 'standoff')] / xt)
                    if st >= 50: per[(who, p, 'sdmg100')].append(100 * sd / st)
                    per[(who, p, 'kills')].append(x[(p, 'kills')])
            lib.lite(G)
        print(f'\n== {label}, {which} games ({n})')
        for p in (0, 1):
            print(f'   {PH[p][2]}')
            for who in ('us', 'them'):
                S = lambda k: sums[(who, p, k)]
                xt = S('turns SPL'); st = S('turns SOL')
                print(f'      {who:4s} X-turns {int(xt):6d}  X dmg {int(S("dmg SPL")):6d} = {100 * S("dmg SPL") / max(1, xt):5.1f}/100t '
                      f'(med/game {lib.med(per[(who, p, "xdmg100")])}), from d2 10-16 {100 * S("out") / max(1, S("dmg SPL")):3.0f}%;  '
                      f'S dmg {int(S("dmg SOL")):6d} = {100 * S("dmg SOL") / max(1, st):4.1f}/100t;  '
                      f'kills {int(S("kills"))} (X {int(S("kill by SPL"))}, S {int(S("kill by SOL"))}, M {int(S("kill by MOP"))}; med/game {lib.med(per[(who, p, "kills")])});  '
                      f'X deaths {int(S("X deaths"))} = {100 * S("X deaths") / max(1, xt):4.2f}/100t, by towers {100 * S("X killed by tower") / max(1, S("X deaths")):3.0f}%;  '
                      f'X-turns at a stand-off spot {100 * S("standoff") / max(1, xt):4.1f}%')


run("study 10's set (t111, t118)", lib.MAIN)
run("study 9's set (y195-y221 and 4 t91 matches; no stand-off)", lib.PREV)

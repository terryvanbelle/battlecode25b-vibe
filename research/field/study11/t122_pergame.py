"""Topic 122: one line per lost game (rounds.tsv and the tower events only), to read how each was lost:
opponent, map (short side, paintable tiles), end and how; towers us/them at r50 / r100 / r200; robots us/them at
r100 / r200 / r300; the round their tower count goes above ours for good (towlead); the first tower kill each way;
our towers killed by r100 / r200 and theirs; the round our last paint tower died for good (PTdead, '-' = never);
our chips at r200 and our max chips; splasher / mopper counts at r200.  Then the same columns as medians, by
opponent group (TOP teams vs the rest) and by map class."""
import lib
from collections import defaultdict


def towlead(G):
    last = None
    for r in range(1, G.end + 1):
        if lib.rv(G, G.op, r, 'tow') > lib.rv(G, G.us, r, 'tow'):
            if last is None: last = r
        else:
            last = None
    return last


def ptdead(G):
    if lib.rv(G, G.us, G.end, 'pt') > 0: return None
    r = G.end
    while r > 1 and lib.rv(G, G.us, r - 1, 'pt') == 0: r -= 1
    return r


rows = []
for G in lib.games('lost'):
    # killed towers: die rows on towers (churn 'died' rows excluded)
    kill_r = defaultdict(list)
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.TOW:
            vic = G.team.get(int(a[5]))
            kill_r[vic].append(a[0])
    fk_them = min(kill_r[G.us]) if kill_r[G.us] else None   # their first kill on our towers
    fk_us = min(kill_r[G.op]) if kill_r[G.op] else None
    R = lambda r, k, s: lib.rv(G, s, r, k) if G.end >= r else None
    rows.append(dict(
        name=f'm{G.m}g{G.g} {G.ver:4s} {G.team_name[:12]:12s} {G.map[:14]:14s} {min(G.W, G.H):2d}/{G.sm["paintable"]:<4d} {G.wintype[:3]}{G.end:<4d}',
        top=G.team_name in lib.TOP, cls=lib.cls(G),
        t50=(R(50, 'tow', G.us), R(50, 'tow', G.op)), t100=(R(100, 'tow', G.us), R(100, 'tow', G.op)),
        t200=(R(200, 'tow', G.us), R(200, 'tow', G.op)),
        u100=(R(100, 'units', G.us), R(100, 'units', G.op)), u200=(R(200, 'units', G.us), R(200, 'units', G.op)),
        u300=(R(300, 'units', G.us), R(300, 'units', G.op)),
        lead=towlead(G), fk_them=fk_them, fk_us=fk_us,
        k100=(sum(1 for r in kill_r[G.us] if r <= 100), sum(1 for r in kill_r[G.op] if r <= 100)),
        k200=(sum(1 for r in kill_r[G.us] if r <= 200), sum(1 for r in kill_r[G.op] if r <= 200)),
        ptdead=ptdead(G), chips200=R(200, 'money', G.us), maxchips=max(lib.money(G, G.us, r) for r in range(1, G.end + 1)),
        x200=(R(200, 'spl', G.us), R(200, 'spl', G.op)), m200=(R(200, 'mop', G.us), R(200, 'mop', G.op)),
        pt200=(R(200, 'pt', G.us), R(200, 'pt', G.op))))
    lib.lite(G)


def f(p):
    return '-/-' if p[0] is None else f'{p[0]}/{p[1]}'


print(f'{len(rows)} lost games.  towers r50 r100 r200 | robots r100 r200 r300 | towlead | first tower kill them->us, us->them | '
      f'our/their towers killed by r100, r200 | PT dead | paint towers r200 | X r200 | M r200 | chips r200 / max')
for x in rows:
    print(f'{x["name"]} {f(x["t50"]):>5} {f(x["t100"]):>5} {f(x["t200"]):>5} | {f(x["u100"]):>5} {f(x["u200"]):>5} {f(x["u300"]):>5} | '
          f'{str(x["lead"]):>4} | {str(x["fk_them"]):>4} {str(x["fk_us"]):>4} | {f(x["k100"]):>5} {f(x["k200"]):>5} | '
          f'{str(x["ptdead"]):>4} | {f(x["pt200"]):>4} | {f(x["x200"]):>5} | {f(x["m200"]):>5} | {x["chips200"]} / {x["maxchips"]}')


def summ(label, S):
    if not S: return
    m = lambda k, i: lib.med([x[k][i] for x in S])
    print(f'\n{label} ({len(S)}): towers r100 {m("t100", 0)}/{m("t100", 1)}, r200 {m("t200", 0)}/{m("t200", 1)}; robots r100 '
          f'{m("u100", 0)}/{m("u100", 1)}, r200 {m("u200", 0)}/{m("u200", 1)}, r300 {m("u300", 0)}/{m("u300", 1)}; towlead '
          f'{lib.med([x["lead"] for x in S])}; first kill them->us {lib.med([x["fk_them"] for x in S])}, us->them '
          f'{lib.med([x["fk_us"] for x in S])}; killed by r200 {m("k200", 0)}/{m("k200", 1)}; PT dead for good in '
          f'{sum(1 for x in S if x["ptdead"])} (med r{lib.med([x["ptdead"] for x in S])}); chips r200 {lib.med([x["chips200"] for x in S])}')


summ('all losses', rows)
summ('top teams', [x for x in rows if x['top']])
summ('the rest', [x for x in rows if not x['top']])
for c in ('small', 'medium', 'large'):
    summ(f'{c} maps', [x for x in rows if x['cls'] == c])

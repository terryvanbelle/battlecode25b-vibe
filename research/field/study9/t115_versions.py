"""Topic 115: what changed version by version (rounds.tsv only).  Per our version (t91 in study 8's set and in this one,
y195, y197, y211, y221) and result: games, the share of games that reach r200 / r300, our paint towers / towers at r150
and r250, rounds (r10+) with no paint tower of ours, games whose last paint tower died for good (no paint tower from
some round to the end), mean chips held in r101-300, soldiers at r200, active SRPs at r300; us / them medians.
Rows for all opponents and for the top teams only."""
import lib
from collections import defaultdict

VERS = ('t74', 'y170', 't85', 't91', 'y195', 'y197', 'y211', 'y221')


def stats(G, s):
    e = G.end
    nopt = sum(1 for r in range(10, e + 1) if lib.rv(G, s, r, 'pt') == 0)
    dead = 0
    if lib.rv(G, s, e, 'pt') == 0:
        r = e
        while r > 1 and lib.rv(G, s, r - 1, 'pt') == 0: r -= 1
        dead = r
    ch = [lib.money(G, s, r) for r in range(101, min(e, 300) + 1)]
    return dict(pt150=lib.rv(G, s, 150, 'pt') if e >= 150 else None, t150=lib.rv(G, s, 150, 'tow') if e >= 150 else None,
                pt250=lib.rv(G, s, 250, 'pt') if e >= 250 else None, t250=lib.rv(G, s, 250, 'tow') if e >= 250 else None,
                nopt=nopt, dead=dead, chips=sum(ch) / len(ch) if ch else None,
                sol200=lib.rv(G, s, 200, 'sol') if e >= 200 else None, srp300=lib.rv(G, s, 300, 'srp') if e >= 300 else None)


rows = defaultdict(list)
for G in lib.games('all', matches=lib.MAIN + lib.PREV):
    v = G.ver + ('(s8)' if G.m in lib.PREV and G.ver == 't91' else '')
    res = 'lost' if G.won_op else 'won'
    top = G.team_name in lib.TOP
    rec = (G.end, stats(G, G.us), stats(G, G.op))
    rows[(v, res, 'all')].append(rec)
    if top: rows[(v, res, 'top')].append(rec)
    lib.lite(G)

order = ['t74', 'y170', 't85', 't91(s8)', 't91', 'y195', 'y197', 'y211', 'y221']
for grp in ('all', 'top'):
    print(f'\n== opponents: {grp}.  us / them medians; "dead" = games whose last paint tower died for good (median round)')
    print('   version res   n  won%  pt/tow r150    pt/tow r250    rounds no PT (games)   last PT dead for good   mean chips r101-300   soldiers r200   SRPs r300')
    for v in order:
        nl = len(rows[(v, 'lost', grp)]); nw = len(rows[(v, 'won', grp)])
        if nl + nw == 0: continue
        for res in ('lost', 'won'):
            R = rows[(v, res, grp)]
            if not R: continue
            def m(side, k): return lib.med([x[side][k] for x in R])
            def nz(side): return sum(1 for x in R if x[side]['nopt'] > 0)
            def dd(side): return sum(1 for x in R if x[side]['dead']), lib.med([x[side]['dead'] for x in R if x[side]['dead']])
            du, dt = dd(1), dd(2)
            print(f'   {v:8s} {res:4s} {len(R):3d} {100 * nw / (nl + nw):4.0f}%  {m(1, "pt150")}/{m(1, "t150")} | {m(2, "pt150")}/{m(2, "t150")}   '
                  f'{m(1, "pt250")}/{m(1, "t250")} | {m(2, "pt250")}/{m(2, "t250")}   {m(1, "nopt")} ({nz(1)}) | {m(2, "nopt")} ({nz(2)})   '
                  f'{du[0]} r{du[1]} | {dt[0]} r{dt[1]}   {m(1, "chips")} | {m(2, "chips")}   {m(1, "sol200")} | {m(2, "sol200")}   {m(1, "srp300")} | {m(2, "srp300")}')

"""Topic 37: the same medians for the games we WON against the same teams in the same matches (control group):
coverage %, towers, paint towers, chips, paint, units at r100/200/300, and the second-paint-tower round."""
import lib
CK = (100, 150, 200, 300)
for which in ('won', 'lost'):
    GS = [lib.lite(G) for G in lib.games(which)]
    print(f'== {which}: {len(GS)} games: ' + ', '.join(f'm{G.m}g{G.g} {G.map}' for G in GS))
    for r in CK:
        gs = [G for G in GS if G.end >= r]
        def v(G, sd, k):
            R = G.rounds[r - 1]; s = 'A' if sd == 1 else 'B'
            if k == 'tow': return sum(int(R[x + s]) for x in ('pt', 'mt', 'dt'))
            if k == 'units': return sum(int(R[x + s]) for x in ('sol', 'spl', 'mop'))
            if k == 'cov%': return round(100 * int(R['cov' + s]) / G.sm['paintable'], 1)
            return int(R[k + s])
        print(f'  r{r} n={len(gs)} ' + '  '.join(f'{k} {lib.med([v(G, G.us, k) for G in gs])}/{lib.med([v(G, G.op, k) for G in gs])}'
              for k in ('cov%', 'tow', 'pt', 'money', 'paint', 'units', 'srp')))

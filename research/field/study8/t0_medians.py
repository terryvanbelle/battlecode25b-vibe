"""Topic 0b: median timeline over the lost games (us vs them), with tower types, SRPs, unit mix and coverage share.
Env S8VER / S8TEAMS filter (lib.games)."""
import lib
CK = (25, 50, 75, 100, 150, 200, 300, 400)
GS = [lib.lite(G) for G in lib.games()]
print(f'{len(GS)} lost games: ' + ', '.join(f'm{G.m}g{G.g} {G.map}({G.team_name[:6]},{G.wintype[:3]}{G.end})' for G in GS))
print('wintypes:', {w: sum(G.wintype == w for G in GS) for w in set(G.wintype for G in GS)}, ' median end round', lib.med([G.end for G in GS]))
def v(G, side, r, k):
    R = G.rounds[min(r, len(G.rounds)) - 1]; s = 'A' if side == 1 else 'B'
    if k == 'tow': return sum(int(R[x + s]) for x in ('pt', 'mt', 'dt'))
    if k == 'units': return sum(int(R[x + s]) for x in ('sol', 'spl', 'mop'))
    if k == 'covpct': return round(100 * int(R['cov' + s]) / G.sm['paintable'], 1)
    return int(R[k + s])
KS = ('covpct', 'cov', 'tow', 'pt', 'mt', 'dt', 'money', 'paint', 'srp', 'units', 'sol', 'spl', 'mop')
print('round  n | ' + '  '.join(f'{k:>11}' for k in KS) + '   (us/them)')
for r in CK:
    gs = [G for G in GS if G.end >= r]
    print(f'r{r:<4} {len(gs):2d} | ' + '  '.join(f'{str(lib.med([v(G, G.us, r, k) for G in gs])) + "/" + str(lib.med([v(G, G.op, r, k) for G in gs])):>11}' for k in KS))
# per game: max towers, rounds where chips >= 3000 (banked), when they lead in cov by 50
print()
for G in GS:
    s = 'A' if G.us == 1 else 'B'; o = 'A' if G.op == 1 else 'B'
    bank = sum(1 for R in G.rounds[100:400] if int(R['money' + s]) >= 3000)
    bank_o = sum(1 for R in G.rounds[100:400] if int(R['money' + o]) >= 3000)
    print(f'm{G.m}g{G.g} {G.map:14s} rounds r101-400 with chips>=3000: us {bank:3d} them {bank_o:3d}; max srp us {max(int(R["srp"+s]) for R in G.rounds)} them {max(int(R["srp"+o]) for R in G.rounds)}')

"""Topic 0: how each game was lost + divergence timeline (both sides) from rounds.tsv.
Columns per checkpoint: cov, towers P/M/D, chips, paint(total, units+towers), units S/X/M.  us | them."""
import lib
CK = (25, 50, 75, 100, 150, 200, 300)
def row(G, side, r):
    R = G.rounds[min(r, len(G.rounds)) - 1]; s = 'A' if side == 1 else 'B'
    g = lambda k: int(R[k + s])
    return f"{g('cov'):4d} {g('pt')}/{g('mt')}/{g('dt')} {g('money'):5d} {g('paint'):5d} {g('sol')}/{g('spl')}/{g('mop')}"
for G in lib.games():
    print(f'== m{G.m} g{G.g} vs {G.team_name}  {G.map} {G.W}x{G.H}  lost r{G.end} {G.wintype}')
    print('   round |  US: cov P/M/D chips paint S/X/M        | THEM: cov P/M/D chips paint S/X/M')
    for r in CK:
        if r > G.end: break
        print(f'   r{r:<4} | {row(G, G.us, r):<36} | {row(G, G.op, r)}')
    print(f'   end   | {row(G, G.us, G.end):<36} | {row(G, G.op, G.end)}')
    # first round our tower count drops; max towers
    s = 'A' if G.us == 1 else 'B'; o = 'A' if G.op == 1 else 'B'
    tw = [int(R['pt' + s]) + int(R['mt' + s]) + int(R['dt' + s]) for R in G.rounds]
    two = [int(R['pt' + o]) + int(R['mt' + o]) + int(R['dt' + o]) for R in G.rounds]
    mx = max(tw); rmx = tw.index(mx) + 1
    covu = [int(R['cov' + s]) for R in G.rounds]; covo = [int(R['cov' + o]) for R in G.rounds]
    cross = next((i + 1 for i in range(len(covu)) if covo[i] > covu[i] + 50), None)
    print(f'   our max towers {mx} at r{rmx}; their max {max(two)}; our peak cov {max(covu)} at r{covu.index(max(covu))+1}; they lead by 50+ from r{cross}')

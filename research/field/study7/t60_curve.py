"""Topic 60: the economy curve, both sides, every 25 rounds: towers held (paint / money), chips, paint held (units +
towers, rounds.tsv), robots alive, active SRPs, and the paint income per round from paint towers (5/10/15 by level
+ 3 per active SRP each).  Lost games, won games, and the top-5 reference set (S7SET=ref5: their bots against our
t16, 1390-1395).  Medians over the games still running at that round (n)."""
import lib, os
from collections import defaultdict
CK = (25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400)
PR = {1: 5, 2: 10, 3: 15}


def pinc(G):
    """per side: list over rounds (index r) of paint-tower income that round."""
    lvl = {}
    for a in G.acts:
        if a[4] == 'startlevel': lvl[int(a[5])] = 2
    ups = defaultdict(list)
    for a in G.acts:
        if a[4] == 'upgrade': ups[a[0]].append((int(a[5]), int(a[6])))
    out = {1: [0] * (G.end + 2), 2: [0] * (G.end + 2)}
    bt = lib.by_round_turns(G)
    for r in range(1, G.end + 1):
        for tid, L in ups.get(r, ()): lvl[tid] = L
        R = G.rounds[r - 1]
        for t in bt.get(r, ()):
            if t[3] == 'PAINT_TOWER':
                out[t[2]][r] += PR[lvl.get(t[1], 1)] + 3 * int(R['srpA' if t[2] == 1 else 'srpB'])
    return out


def table(label, GS):
    print(f'== {label}: {len(GS)} games')
    print('round  n |  towers  paintT  moneyT     chips      paint    robots   SRPs  paint-inc/rd (us/them)')
    inc = {(G.m, G.g): pinc(G) for G in GS}
    for r in CK:
        gs = [G for G in GS if G.end >= r]
        if not gs: break
        f = lambda k: f"{lib.med([lib.rv(G, G.us, r, k) for G in gs])}/{lib.med([lib.rv(G, G.op, r, k) for G in gs])}"
        pi = lambda sd: lib.med([sum(inc[(G.m, G.g)][sd(G)][max(1, r - 24):r + 1]) / 25 for G in gs])
        print(f'r{r:<4} {len(gs):2d} | {f("tow"):>7s} {f("pt"):>7s} {f("mt"):>7s} {f("money"):>11s} {f("paint"):>11s} {f("units"):>9s} {f("srp"):>6s}  {pi(lambda G: G.us)}/{pi(lambda G: G.op)}')


for which in ('lost', 'won'):
    GS = list(lib.games(which))
    table(which, GS)
    for c in ('small', 'medium', 'large'):
        gs = [G for G in GS if lib.cls(G) == c]
        if gs: table(f'{which}, {c} maps', gs)
os.environ['S7SET'] = 'ref5'
table('top-5 reference (1390-1395, our t16; all 15 games, we lost 15)', list(lib.games('all')))

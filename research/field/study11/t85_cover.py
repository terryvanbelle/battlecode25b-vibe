"""Topic 85: the paint war, both sides, per 100-round window.  From the replayed grid: tiles each side painted from empty,
tiles it flipped from the other side (only a splash can do that, inside the inner 3x3), and tiles it mopped from the
other side to empty; by unit type.  Lost games ending after r450 one by one (the slow losses), then medians over all
lost and won games for r101-200 / r201-300 / r301-400.  Also the robots alive by type at each window end."""
import lib
from collections import defaultdict, Counter

def windows(G):
    return [(lo, min(lo + 99, G.end)) for lo in range(1, G.end + 1, 100)]


def war(G):
    """per (side, window start): Counter of 'empty->own by X', 'flip by X', 'mop by X'."""
    W = G.W; grid = list(G.paint0)
    C = defaultdict(Counter)
    for a in G.acts:
        k = a[4]
        if k not in ('paint', 'unpaint'): continue
        x, y = map(int, a[5].split(',')); i = x + y * W
        side = 'us' if a[2] == G.us else 'them'; me = 1 if a[2] == 1 else 2
        lo = (a[0] - 1) // 100 * 100 + 1
        o = lib.owner(grid[i])
        t = a[3][:2]
        if k == 'paint':
            if o == 0: C[(side, lo)]['new ' + t] += 1
            elif o != me: C[(side, lo)]['flip ' + t] += 1
            sec = a[6] == '1'
            grid[i] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        else:
            if o != 0 and o != me: C[(side, lo)]['mop ' + t] += 1
            grid[i] = 0
    return C


print('== lost games ending after r450, per 100 rounds: coverage % at the window end us/them; tiles from empty (S/X), '
      'flipped by splash, mopped (us | them); robots alive S/X/M at the window end')
for G in lib.games('lost'):
    if G.end <= 450: continue
    C = war(G)
    print(f'-- m{G.m}g{G.g} {G.map} ({G.W}x{G.H}, {G.sm["paintable"]}) vs {G.team_name} {G.ver} end r{G.end}')
    for lo, hi in windows(G):
        u, t = C[('us', lo)], C[('them', lo)]
        R = G.rounds[hi - 1]; s, o = ('A', 'B') if G.us == 1 else ('B', 'A')
        print(f'   r{lo:<4}-{hi:<4} cov {lib.rv(G, G.us, hi, "covpct"):5.1f}/{lib.rv(G, G.op, hi, "covpct"):5.1f} | '
              f'new S{u["new SO"]:4d} X{u["new SP"]:4d} flip {u["flip SP"]:4d} mop {u["mop MO"]:4d} | '
              f'new S{t["new SO"]:4d} X{t["new SP"]:4d} flip {t["flip SP"]:4d} mop {t["mop MO"]:4d} | '
              f'alive {R["sol" + s]}/{R["spl" + s]}/{R["mop" + s]} vs {R["sol" + o]}/{R["spl" + o]}/{R["mop" + o]}, towers {lib.rv(G, G.us, hi, "tow")}/{lib.rv(G, G.op, hi, "tow")}')
print()
for which in ('lost', 'won'):
    S = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        C = war(G)
        for lo in (101, 201, 301):
            if G.end < lo + 99: continue
            for side in ('us', 'them'):
                c = C[(side, lo)]
                for m in ('new SO', 'new SP', 'flip SP', 'mop MO'):
                    S[(side, lo, m)].append(c[m])
                other = C[('them' if side == 'us' else 'us', lo)]
                S[(side, lo, 'lost to flips+mops')].append(other['flip SP'] + other['mop MO'])
    print(f'== {which} games ({n}), medians per game, us / them (games that reached the window end)')
    for lo in (101, 201, 301):
        print(f'   r{lo}-{lo + 99} (n={len(S[("us", lo, "new SO")])}): ' + '  '.join(
            f'{m} {lib.med(S[("us", lo, m)])}/{lib.med(S[("them", lo, m)])}' for m in ('new SO', 'new SP', 'flip SP', 'mop MO', 'lost to flips+mops')))

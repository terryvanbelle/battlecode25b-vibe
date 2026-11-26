"""Topic 66: the tower mix by build number.  Per side, the type of each new-ruin build #1..#10 (a rebuild on a ruin the
side held before is not counted; churn rebuilds neither), with its round, the side's chips one round before it and
how many paint towers the side then stood with.  For us also the chips at our first mark on that ruin (wantType()
picks the type then: paint when chips >= 2000 with >= 3 towers, else money while < 6 towers).  Lost / won / ref5."""
import lib, os
from collections import defaultdict, Counter


def seq(G, sd, b, d):
    held = set((x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd)
    out = []
    for x in b:
        if x[0] == 0 or x[3] != sd: continue
        p = (x[4], x[5])
        if p in held: continue
        held.add(p)
        npt = sum(1 for t in lib.towers_alive(G, sd, x[0] - 1, b, d) if t[2] == 'PAINT_TOWER')
        out.append((x[0], x[2][:1], lib.money(G, sd, x[0] - 1), npt, p))
    return out


def run(label, GS):
    C = defaultdict(Counter); R = defaultdict(list); M = defaultdict(list); n = 0
    for G in GS:
        n += 1
        b, d = lib.tower_events(G)
        firstmark = {}
        for a in G.acts:
            if a[4] == 'mark' and a[2] == G.us and a[3] in lib.BOT:
                x, y = map(int, a[5].split(','))
                for p in G.ruins:
                    if max(abs(p[0] - x), abs(p[1] - y)) <= 2: firstmark.setdefault(p, a[0])
        for sd in (G.us, G.op):
            w = 'us' if sd == G.us else 'them'
            for k, (r, t, ch, npt, p) in enumerate(seq(G, sd, b, d)[:10]):
                C[(w, k + 1)][t] += 1; R[(w, k + 1)].append(r)
                if t == 'P': C[(w, k + 1)]['P with 1 PT standing'] += npt == 1
                if sd == G.us and p in firstmark: M[k + 1].append(lib.money(G, sd, firstmark[p]))
    print(f'== {label}: {n} games.  build #k: type counts (P/M/D), median round; us | them')
    for k in range(1, 11):
        f = lambda w: f"P{C[(w, k)]['P']} M{C[(w, k)]['M']} D{C[(w, k)]['D']} r{lib.med(R[(w, k)])}"
        print(f'   #{k:<2d} us {f("us"):>18s}  chips at our mark med {lib.med(M[k])} (>= 2000 in {sum(1 for v in M[k] if v >= 2000)}/{len(M[k])})  | them {f("them")}')


run('lost', lib.games('lost'))
run('won', lib.games('won'))
os.environ['S8SET'] = 'ref5'
run('top-5 reference', lib.games('all'))

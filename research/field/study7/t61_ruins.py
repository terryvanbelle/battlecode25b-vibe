"""Topic 61: the ruin supply.  Per game and checkpoint: ruins on the map, towers standing (ours / theirs) and free ruins
(no tower), split by side of the map (nearer to our starting towers or to theirs, by distance to the nearest starting
tower).  Plus, per side, the round of the k-th tower BUILT (new ruin; a rebuild on a ruin the side held before is not
counted) and of the 2nd / 3rd paint tower standing.  Lost and won games, and the top-5 reference set."""
import lib, os
from collections import defaultdict
CK = (50, 100, 150, 200, 300)


def info(G):
    b, d = lib.tower_events(G)
    start = {sd: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == sd] for sd in (1, 2)}
    def half(p):
        du = min(lib.d2(p, q) for q in start[G.us]); do = min(lib.d2(p, q) for q in start[G.op])
        return 'ours' if du < do else 'theirs' if do < du else 'mid'
    ruins = G.ruins
    out = {'n': len(ruins), 'half': {h: sum(1 for r in ruins if half(r) == h) for h in ('ours', 'theirs', 'mid')}}
    for r in CK:
        al = {sd: lib.towers_alive(G, sd, r, b, d) for sd in (1, 2)}
        occ = {(t[4], t[5]): sd for sd in (1, 2) for t in al[sd]}
        free = [p for p in ruins if p not in occ]
        out[r] = dict(us=len(al[G.us]), them=len(al[G.op]), free=len(free),
                      free_ours=sum(1 for p in free if half(p) == 'ours'), free_theirs=sum(1 for p in free if half(p) == 'theirs'),
                      us_in_theirs=sum(1 for t in al[G.us] if half((t[4], t[5])) == 'theirs'),
                      them_in_ours=sum(1 for t in al[G.op] if half((t[4], t[5])) == 'ours'))
    # k-th new-ruin build and 2nd/3rd paint tower standing
    held = {1: set(), 2: set()}
    for x in b:
        if x[0] == 0: held[x[3]].add((x[4], x[5]))
    kth = {1: [], 2: []}
    for x in b:
        if x[0] == 0: continue
        p = (x[4], x[5])
        if p in held[x[3]]: continue
        held[x[3]].add(p); kth[x[3]].append(x[0])
    pt = {}
    for sd in (1, 2):
        rr = []
        for k in (2, 3):
            got = next((r for r in range(1, G.end + 1) if sum(1 for t in lib.towers_alive(G, sd, r, b, d) if t[2] == 'PAINT_TOWER') >= k), None)
            rr.append(got)
        pt[sd] = rr
    out['kth'] = kth; out['pt'] = pt
    return out


def report(label, GS):
    print(f'== {label}: {len(GS)} games')
    I = [(G, info(G)) for G in GS]
    print(f'   ruins per map: med {lib.med([i["n"] for _, i in I])}; in our half {lib.med([i["half"]["ours"] for _, i in I])}, theirs {lib.med([i["half"]["theirs"] for _, i in I])}')
    print('   round  n | towers us/them | free ruins (in our half / their half) | our towers in their half, theirs in ours')
    for r in CK:
        ii = [i for G, i in I if G.end >= r]
        if not ii: break
        m = lambda k: lib.med([i[r][k] for i in ii])
        print(f'   r{r:<4} {len(ii):2d} | {m("us")}/{m("them")} | {m("free")} ({m("free_ours")} / {m("free_theirs")}) | {m("us_in_theirs")}, {m("them_in_ours")}')
    for k in range(1, 9):
        u = [i['kth'][G.us][k - 1] if len(i['kth'][G.us]) >= k else None for G, i in I]
        t = [i['kth'][G.op][k - 1] if len(i['kth'][G.op]) >= k else None for G, i in I]
        print(f'   new-ruin build #{k}: us med r{lib.med(u)} (reached in {sum(x is not None for x in u)}), them r{lib.med(t)} (in {sum(x is not None for x in t)})')
    for j, k in enumerate((2, 3)):
        u = [i['pt'][G.us][j] for G, i in I]; t = [i['pt'][G.op][j] for G, i in I]
        print(f'   paint towers >= {k}: us in {sum(x is not None for x in u)} games, med r{lib.med(u)}; them in {sum(x is not None for x in t)}, med r{lib.med(t)}')
    return I


for which in ('lost', 'won'):
    I = report(which, list(lib.games(which)))
    if which == 'lost':
        print('   per game: map, end, r150 towers us/them, free ruins r150 (ours/theirs), our 2nd paint tower round, theirs')
        for G, i in I:
            print(f'      m{G.m}g{G.g} {G.map[:14]:14s} {G.end:4d}  {i[150]["us"]}/{i[150]["them"]}  free {i[150]["free"]} ({i[150]["free_ours"]}/{i[150]["free_theirs"]})  '
                  f'2nd PT us r{i["pt"][G.us][0]} them r{i["pt"][G.op][0]}')
os.environ['S7SET'] = 'ref5'
report('top-5 reference (all games)', list(lib.games('all')))

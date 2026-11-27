"""Topic 99: ruins that keep getting killed.  For each side's towers (starting towers included), by the number of the
side's towers already killed on the same ruin before this one was built (0, 1, 2+): towers built, share killed,
median life (rounds from build to death, or to the game end when it survived), and the robots of the other side the
tower killed.  Shows whether a tower rebuilt where one of ours died lives as long as a tower on a fresh ruin, and how
much of all tower loss happens on such repeat ruins.  Lost and won games."""
import lib
from collections import defaultdict


def towers(G):
    b, d = lib.tower_events(G)
    killed = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    death = {x[1]: x[0] for x in d}
    kills_by = defaultdict(int)
    for a in G.acts:
        if a[4] == 'die' and a[7] in lib.BOT and a[3] in lib.TOW and a[1] != int(a[5]): kills_by[a[1]] += 1
    prior = defaultdict(int)   # (side, loc) -> towers of that side killed there so far
    out = []
    for x in sorted(b):
        r, tid, typ, side, px, py = x
        loc = (px, py)
        n_before = prior[(side, loc)]
        dead = tid in death
        life = (death[tid] if dead else G.end) - r
        k = tid in killed
        out.append(dict(side='us' if side == G.us else 'them', prior=min(n_before, 2), killed=k, life=life, kills=kills_by[tid], typ=typ[0], r=r))
        if k: prior[(side, loc)] += 1
    return out


for which in ('lost', 'won'):
    S = defaultdict(list); n = 0
    for G in lib.games(which):
        n += 1
        for e in towers(G): S[(e['side'], e['prior'])].append(e)
    print(f'== {which} games ({n}): towers by the number of the same side\'s towers already killed on that ruin')
    print('   side  prior kills  towers  killed%  life med  robots killed per tower  share of the side\'s tower kills')
    for side in ('us', 'them'):
        allk = sum(1 for p in range(3) for e in S[(side, p)] if e['killed'])
        for p in range(3):
            L = S[(side, p)]
            if not L: continue
            k = sum(1 for e in L if e['killed'])
            print(f'   {side:4s}  {("0", "1", "2+")[p]:3s}         {len(L):5d}   {100 * k / len(L):5.0f}%   {lib.med([e["life"] for e in L]):6}      '
                  f'{sum(e["kills"] for e in L) / len(L):5.2f}                  {100 * k / max(1, allk):5.0f}%')
        L = [e for p in (1, 2) for e in S[(side, p)] if e['r'] > 0]
        if L:
            from collections import Counter
            print(f'      {side}: towers on repeat ruins by type {dict(Counter(e["typ"] for e in L))}')
            for ty in ('D', 'P', 'M'):
                for lab, LL in (('repeat ruins', L), ('all ruins', [e for p in range(3) for e in S[(side, p)] if e['r'] > 0])):
                    T = [e for e in LL if e['typ'] == ty]
                    if T:
                        print(f'         {ty} on {lab:12s}: {len(T):4d} built, killed {100 * sum(1 for e in T if e["killed"]) / len(T):3.0f}%, '
                              f'life med {lib.med([e["life"] for e in T])}, robots killed per tower {sum(e["kills"] for e in T) / len(T):.2f}')
    print()

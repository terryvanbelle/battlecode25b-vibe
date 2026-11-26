"""Topic 76: idle chips.  Share of rounds r101-400 (or to the end) in which a side held >= 3000 and >= 5000 chips;
medians over games, lost and won; per lost game for us and them."""
import lib
for which in ('lost', 'won'):
    S = {('us', 3000): [], ('them', 3000): [], ('us', 5000): [], ('them', 5000): []}
    per = []
    for G in lib.games(which):
        lo, hi = 101, min(G.end, 400)
        if hi - lo < 50: continue
        for sd in (G.us, G.op):
            w = 'us' if sd == G.us else 'them'
            for th in (3000, 5000):
                S[(w, th)].append(100 * sum(1 for r in range(lo, hi + 1) if lib.money(G, sd, r) >= th) / (hi - lo + 1))
        per.append((G.m, G.g, G.map[:12], round(S[('us', 3000)][-1]), round(S[('them', 3000)][-1])))
    print(which, ' '.join(f'{k}: med {lib.med(v):.0f}% p75 {lib.pct(v, .75):.0f}%' for k, v in S.items()))
    if which == 'lost': print('   per game (m, g, map, us % rounds >= 3000, them):', per)

"""Topic 45: unit mix by phase, both sides, lost vs won games, and by map class.  Robot-turns per type per phase
(r1-50, 51-100, 101-200, 201-300) as a share and as a count (median per game), robots alive at r50/100/200 (rounds.tsv),
spawns by type per phase (robots only), and the soldier : mopper : splasher ratio of spawns."""
import lib
from collections import defaultdict, Counter
PH = ((1, 50), (51, 100), (101, 200), (201, 300))
def cls(G): return 'small' if min(G.W, G.H) <= 25 or G.sm['paintable'] <= 600 else ('medium' if min(G.W, G.H) <= 35 else 'large')
for sel in ('lost', 'won', 'lost-small', 'lost-medium', 'lost-large', 'won-medium', 'won-large'):
    which = sel.split('-')[0]; c = sel.split('-')[1] if '-' in sel else None
    GS = [G for G in lib.games(which) if c is None or cls(G) == c]
    if not GS: continue
    T = defaultdict(list); SP = defaultdict(list); AL = defaultdict(list)
    for G in GS:
        for (lo, hi) in PH:
            if G.end < hi: continue
            for sd in (G.us, G.op):
                w = 'us' if sd == G.us else 'them'
                cnt = Counter(t[3][:2] for t in G.turns if t[2] == sd and t[3] in lib.BOT and lo <= t[0] <= hi)
                sp = Counter(a[6][:2] for a in G.acts if a[2] == sd and a[4] == 'spawn' and a[6] in lib.BOT and lo <= a[0] <= hi)
                for k in ('SO', 'MO', 'SP'):
                    T[(w, lo, k)].append(cnt[k] / (hi - lo + 1)); SP[(w, lo, k)].append(sp[k])
        for r in (50, 100, 200):
            if G.end < r: continue
            R = G.rounds[r - 1]
            for sd in (G.us, G.op):
                w = 'us' if sd == G.us else 'them'; s = 'A' if sd == 1 else 'B'
                for k, col in (('SO', 'sol'), ('MO', 'mop'), ('SP', 'spl')):
                    AL[(w, r, k)].append(int(R[col + s]))
    print(f'== {sel}: {len(GS)} games')
    print('   mean robots per round by phase (median over games), us | them:  S / M / X')
    for (lo, hi) in PH:
        n = len(T[('us', lo, 'SO')])
        if not n: continue
        f = lambda w: '/'.join(str(lib.med(T[(w, lo, k)])) for k in ('SO', 'MO', 'SP'))
        g = lambda w: '/'.join(str(lib.med(SP[(w, lo, k)])) for k in ('SO', 'MO', 'SP'))
        print(f'   r{lo}-{hi} (n={n:2d}): alive {f("us"):>16s} | {f("them"):<16s}   spawned {g("us"):>10s} | {g("them")}')

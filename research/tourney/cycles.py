"""How transitive is the local tournament? Fit Bradley-Terry on games among a bot set, then test whether pairwise
results depart from it (chi-square), and list intransitive triangles where each edge is clear on its own."""
import glob, json, math, itertools, sys
S = sys.argv[1].split(',')
W = {}   # W[(a,b)] = wins of a over b
for f in glob.glob('runs/*/results.jsonl'):
    for line in open(f):
        if not line.startswith('{'): continue
        try: g = json.loads(line)
        except ValueError: continue
        a, b, w = g.get('a'), g.get('b'), g.get('winner')
        if a in S and b in S and a != b and w in ('A', 'B'):
            win, lose = (a, b) if w == 'A' else (b, a)
            W[(win, lose)] = W.get((win, lose), 0) + 1
pairs = [(a, b) for a, b in itertools.combinations(S, 2) if W.get((a, b), 0) + W.get((b, a), 0) >= 30]
bots = sorted({x for p in pairs for x in p})
# Bradley-Terry by the MM algorithm
s = {b: 1.0 for b in bots}
for _ in range(2000):
    new = {}
    for i in bots:
        wins = sum(W.get((i, j), 0) for j in bots if j != i and ((i, j) in pairs or (j, i) in pairs))
        den = sum((W.get((i, j), 0) + W.get((j, i), 0)) / (s[i] + s[j]) for j in bots if j != i and ((i, j) in pairs or (j, i) in pairs))
        new[i] = wins / den if den else s[i]
    g = math.exp(sum(math.log(v) for v in new.values()) / len(new)); s = {k: v / g for k, v in new.items()}
elo = {b: 400 * math.log10(s[b]) for b in bots}
chi, rows = 0.0, []
for a, b in pairs:
    n = W.get((a, b), 0) + W.get((b, a), 0); obs = W.get((a, b), 0) / n
    exp = s[a] / (s[a] + s[b]); z = (obs - exp) / math.sqrt(exp * (1 - exp) / n)
    chi += z * z; rows.append((abs(z), a, b, n, obs, exp, z))
df = len(pairs) - (len(bots) - 1)
# chi-square upper tail via the Wilson-Hilferty normal approximation
zwh = ((chi / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
p = 0.5 * math.erfc(zwh / math.sqrt(2))
print(f'{len(bots)} bots, {len(pairs)} pairs with 30+ games, {sum(W.values())} games')
print(f'chi-square vs Bradley-Terry {chi:.1f} on {df} df (expected {df} if transitive), p = {p:.2g}; dispersion {chi/df:.2f}')
print('largest departures (observed vs BT-expected score of the first bot):')
for _, a, b, n, o, e, z in sorted(rows, reverse=True)[:8]: print(f'  {a:>5} vs {b:<5} n={n:4d}  {o:.3f} vs {e:.3f}  z={z:+.1f}')
tri = []
for a, b, c in itertools.permutations(bots, 3):
    def beats(x, y):
        n = W.get((x, y), 0) + W.get((y, x), 0)
        if n < 30: return False
        o = W.get((x, y), 0) / n
        return (o - 0.5) / math.sqrt(0.25 / n) > 2
    if a < b and a < c and beats(a, b) and beats(b, c) and beats(c, a): tri.append((a, b, c))
print(f'intransitive triangles with each edge > 2 SE from 50%: {len(tri)}', tri[:6])

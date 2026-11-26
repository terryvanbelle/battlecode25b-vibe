"""Test: moderate positive local gains (1 <= dL <= U) are followed by replica losses (owner prompt #38).

Windows as on the dashboard: dL = local champion change over [t-120, t-60], dR = replica change over [t-60, t].
Usage: python3 research/replica/deltatest.py BOARD.json [SINCE]   (BOARD from `tools/prod.sh board`)

The hypothesis and its cutoff (U = 44) were chosen on 2026-11-26 after looking at the windows up to 16:07 PDT, so
p-values on those windows are optimistic. Confirmatory run, fixed in advance: pass SINCE = '2026-11-26 16:07' to use
only later windows, and read the primary line (G = +1..+44; relative test, rotation p; absolute test, NW p)."""
import json, math, sys
from datetime import datetime, timedelta

b = json.load(open(sys.argv[1]))
P = lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M')
CUT, H = P('2026-11-25 12:25'), timedelta(minutes=60)
champs = sorted((P(r['when_pdt']), r['rating'], r['bot']) for r in b['local'] if r['kind'] == 'champion')
reps = sorted((P(r['when_pdt']), int(r['our_rating'])) for r in b['replica'] if r.get('our_rating'))
def champ_at(t):
    c = None
    for w, rt, bot in champs:
        if w <= t: c = (rt, bot, w)
        else: break
    return c
def rep_near(t):
    x = min(reps, key=lambda r: abs(r[0] - t))
    return x[1] if abs(x[0] - t) <= timedelta(minutes=20) else None
W = []
for t, v in reps:
    if t - H < CUT: continue
    r0, a, c = rep_near(t - H), champ_at(t - H), champ_at(t - 2 * H)
    if r0 is None or a is None or c is None: continue
    W.append(dict(t=t, dL=a[0] - c[0], dR=v - r0, ev=(c[1], a[1])))
if len(sys.argv) > 2:
    W = [w for w in W if w['t'] > P(sys.argv[2])]
n = len(W)
t0 = W[0]['t']
mean = lambda xs: sum(xs) / len(xs)

def tcdf(x, df):   # Student t CDF via the regularized incomplete beta function
    def betacf(a, b_, x_):
        qab, qap, qam, c, d = a + b_, a + 1, a - 1, 1.0, 1 - (a + b_) * x_ / (a + 1)
        d = 1 / (d if abs(d) > 1e-30 else 1e-30); h = d
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b_ - m) * x_ / ((qam + m2) * (a + m2))
            d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-30 else 1e-30); c = 1 + aa / c if abs(1 + aa / c) > 1e-30 else 1e-30; h *= d * c
            aa = -(a + m) * (qab + m) * x_ / ((a + m2) * (qap + m2))
            d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-30 else 1e-30); c = 1 + aa / c if abs(1 + aa / c) > 1e-30 else 1e-30
            de = d * c; h *= de
            if abs(de - 1) < 1e-12: break
        return h
    def ibeta(a, b_, x_):
        if x_ <= 0: return 0.0
        if x_ >= 1: return 1.0
        lb = math.lgamma(a + b_) - math.lgamma(a) - math.lgamma(b_) + a * math.log(x_) + b_ * math.log(1 - x_)
        if x_ < (a + 1) / (a + b_ + 2): return math.exp(lb) * betacf(a, b_, x_) / a
        return 1 - math.exp(lb) * betacf(b_, a, 1 - x_) / b_
    p = 0.5 * ibeta(df / 2, 0.5, df / (df + x * x))
    return p if x < 0 else 1 - p

def ols_nw(y, X, L=2):
    """OLS with Newey-West (Bartlett, lag L) covariance; X rows include the intercept."""
    k = len(X[0])
    XtX = [[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)]
    inv = matinv(XtX)
    Xty = [sum(r[i] * yy for r, yy in zip(X, y)) for i in range(k)]
    beta = [sum(inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]
    e = [yy - sum(bb * xx for bb, xx in zip(beta, r)) for r, yy in zip(X, y)]
    S = [[sum(e[t] ** 2 * X[t][i] * X[t][j] for t in range(len(y))) for j in range(k)] for i in range(k)]
    for l in range(1, L + 1):
        w = 1 - l / (L + 1)
        for i in range(k):
            for j in range(k):
                S[i][j] += w * sum(e[t] * e[t - l] * (X[t][i] * X[t - l][j] + X[t - l][i] * X[t][j]) for t in range(l, len(y)))
    V = matmul(matmul(inv, S), inv)
    return beta, V
def matmul(A, B): return [[sum(A[i][m] * B[m][j] for m in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def matinv(A):
    k = len(A); M = [row[:] + [float(i == j) for j in range(k)] for i, row in enumerate(A)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [v / pv for v in M[c]]
        for r in range(k):
            if r != c: f = M[r][c]; M[r] = [a - f * bb for a, bb in zip(M[r], M[c])]
    return [row[k:] for row in M]

def analyse(U, lo=1, verbose=False):
    g = [1.0 if lo <= w['dL'] <= U else 0.0 for w in W]
    y = [w['dR'] for w in W]
    inG = [yy for yy, gg in zip(y, g) if gg]; out = [yy for yy, gg in zip(y, g) if not gg]
    diff = mean(inG) - mean(out)
    # NW regression dR = a + b G: mean in G = a + b, relative effect = b
    beta, V = ols_nw(y, [[1.0, gg] for gg in g])
    se_b = math.sqrt(V[1][1]); se_ab = math.sqrt(V[0][0] + V[1][1] + 2 * V[0][1])
    df = len(inG) / 3 - 1   # about a third of the windows are independent
    p_rel = tcdf(beta[1] / se_b, max(df, 1)); p_abs = tcdf((beta[0] + beta[1]) / se_ab, max(df, 1))
    # rotation test: shift the G series against dR; keeps each series' own autocorrelation, breaks their link
    rot = []
    for k in range(4, n - 3):
        gs = g[k:] + g[:k]
        a = [yy for yy, gg in zip(y, gs) if gg]; o = [yy for yy, gg in zip(y, gs) if not gg]
        if a and o: rot.append(mean(a) - mean(o))
    p_rot = (sum(1 for d in rot if d <= diff) + 1) / (len(rot) + 1)
    return dict(U=U, nG=len(inG), mG=mean(inG), mO=mean(out), diff=diff, b=beta[1], se_b=se_b, p_rel=p_rel,
                mean_G=beta[0] + beta[1], se_G=se_ab, p_abs=p_abs, p_rot=p_rot, g=g)

print(f'{n} windows, {W[0]["t"]:%m-%d %H:%M} to {W[-1]["t"]:%m-%d %H:%M} PDT')
r = analyse(44)
print(f"\nPrimary, G = local change +1..+44: {r['nG']} windows, mean replica change {r['mG']:+.1f} vs {r['mO']:+.1f} in the other {n - r['nG']}")
print(f"  relative (G below the rest): diff {r['diff']:+.1f}, NW SE {r['se_b']:.1f}, one-sided p = {r['p_rel']:.3f}; rotation test p = {r['p_rot']:.3f}")
print(f"  absolute (G mean below 0): {r['mean_G']:+.1f} ± {r['se_G']:.1f} (NW), one-sided p = {r['p_abs']:.3f}")

# events: the distinct crownings behind the G windows
ev = {}
for w, gg in zip(W, r['g']):
    if gg: ev.setdefault(w['ev'], []).append(w['dR'])
em = [(k, mean(v), len(v)) for k, v in ev.items()]
neg = sum(1 for _, m_, _ in em if m_ < 0)
pb = sum(math.comb(len(em), i) for i in range(neg, len(em) + 1)) / 2 ** len(em)
print(f"\nEvent level: {len(em)} distinct champion changes; {neg} followed by a mean replica loss; sign test one-sided p = {pb:.3f}")
for (a, c), m_, k in sorted(em, key=lambda e: e[1]): print(f"   {a:>5} -> {c:<5} mean dR {m_:+6.1f} over {k} windows")

# time confound: add a linear time trend (hours since the first window)
g = r['g']; y = [w['dR'] for w in W]; th = [(w['t'] - t0).total_seconds() / 3600 for w in W]
beta, V = ols_nw(y, [[1.0, gg, tt] for gg, tt in zip(g, th)])
print(f"\nWith a time trend: G effect {beta[1]:+.1f} ± {math.sqrt(V[1][1]):.1f}, trend {beta[2]:+.2f}/h ± {math.sqrt(V[2][2]):.2f}, one-sided p(G) = {tcdf(beta[1] / math.sqrt(V[1][1]), max(r['nG'] / 3 - 1, 1)):.3f}")
half = n // 2
for nm, sl in (('first half', slice(0, half)), ('second half', slice(half, n))):
    a = [yy for yy, gg in zip(y[sl], g[sl]) if gg]; o = [yy for yy, gg in zip(y[sl], g[sl]) if not gg]
    print(f"  {nm} ({W[sl][0]['t']:%m-%d %H:%M} on): G {len(a)} windows mean {mean(a):+.1f}; rest {len(o)} mean {mean(o):+.1f}" if a and o else f"  {nm}: too few")

print('\nUpper cutoff sensitivity (lower bound +1):')
for U in (10, 19, 30, 44, 60, 100, 200):
    s = analyse(U)
    print(f"  U={U:>3}: nG={s['nG']:2d}  G {s['mG']:+5.1f}  rest {s['mO']:+5.1f}  diff {s['diff']:+5.1f}  NW p={s['p_rel']:.3f}  rotation p={s['p_rot']:.3f}  abs p={s['p_abs']:.3f}")

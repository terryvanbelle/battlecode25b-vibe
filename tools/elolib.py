"""Bradley-Terry ratings on the Elo scale from game counts (standard library only).

fit(games) takes (playerA, playerB, winsA, winsB) tuples and returns {player: Rating}. The fit is the MM
iteration of Hunter (2004) for P(i beats j) = r_i / (r_i + r_j), with a weak prior: every player gets PRIOR virtual
wins and PRIOR virtual losses against an anchor fixed at strength 1, so players with all wins or all losses stay finite.
PRIOR was 1 until 2026-11-26 19:20 PDT (owner prompt #51). Far above the anchor, the prior pulls each player down by
about PRIOR wins, whatever the distance. Each champion's era of ~10 bots is tied to the era before it by only a few
hundred games, so with PRIOR = 1 every era sank 20-40 points against the one it beat, and the history showed champions
declining where every head-to-head said they improved. The MM steps are accelerated with SQUAREM (Varadhan & Roland
2008), since the weak prior leaves the chain of eras slow to converge; without keys the fit uses Newton steps with a
conjugate-gradient solve instead (newton()), which settles the whole history in seconds.
A pair's games are capped at PAIR_CAP (scaled down keeping its win share), so one heavily repeated pairing cannot
dominate. Ratings are 400*log10(r), shifted so the mean over all players is 1500. se is the standard error from
the diagonal of the information matrix (each other rating taken as known), so it is a little optimistic.

A game may carry a fifth element k, a handicap key (e.g. the map): playerA then plays at strength r_A * h_k, with h_k
fitted alongside the ratings (Hunter's home-advantage model, one advantage per key). fit_h(games) returns
(ratings, {k: h_k in Elo points}). When every keyed player (an A of a keyed game) meets unkeyed players only in keyed
games, the h_k are normalized to a game-weighted mean of 0 by moving the keyed players' ratings the other way (the
likelihood is unchanged), so a keyed player's rating is its strength on an average key of the mix it was fitted on.
"""
import collections, math, os

PAIR_CAP = 200
PRIOR = float(os.environ.get('BC_ELO_PRIOR', '0.01'))   # BC_ELO_PRIOR=1: the old fit (pre-registered test)
SCALE = 400 / math.log(10)


class Rating:
    __slots__ = ('rating', 'se', 'games', 'wins', 'losses')

    def __init__(self, rating, se, games, wins, losses):
        self.rating, self.se, self.games, self.wins, self.losses = rating, se, games, wins, losses

    def __repr__(self):
        return f'Rating({self.rating:.0f}+-{self.se:.0f}, {self.wins:g}-{self.losses:g})'


def pair_table(games):
    """{(i, j): [wins_i, wins_j]} with i < j, capped at PAIR_CAP games per pair (unkeyed games only; see key_table)."""
    return {(i, j): w for (i, j, k), w in key_table(games).items()}


def key_table(games):
    """{(i, j, k): [wins_i, wins_j]}: k None with i < j, else i the keyed player. Each pair of players (whatever the
    keys) is capped at PAIR_CAP games, every entry scaled down by the same factor."""
    t = collections.defaultdict(lambda: [0.0, 0.0])
    for g in games:
        a, b, wa, wb = g[:4]
        k = g[4] if len(g) > 4 else None
        if a == b:
            continue
        if k is not None or a < b:
            t[(a, b, k)][0] += wa; t[(a, b, k)][1] += wb
        else:
            t[(b, a, k)][0] += wb; t[(b, a, k)][1] += wa
    pair = collections.defaultdict(float)
    for (i, j, k), (x, y) in t.items():
        pair[min(i, j), max(i, j)] += x + y
    for (i, j, k), (x, y) in t.items():
        n = pair[min(i, j), max(i, j)]
        if n > PAIR_CAP:
            t[(i, j, k)] = [x * PAIR_CAP / n, y * PAIR_CAP / n]
    return dict(t)


def fit(games, iters=2000, tol=1e-9, prior=PRIOR):
    return fit_h(games, iters, tol, prior)[0]


def fit_h(games, iters=2000, tol=1e-9, prior=PRIOR):
    t = key_table(games)
    opp = collections.defaultdict(list)     # player -> [(other, n_games, key, keyed side?)]
    wins = collections.defaultdict(float)
    hw, hn = collections.defaultdict(float), collections.defaultdict(float)   # key -> keyed side's wins, games
    by_key = collections.defaultdict(list)                                     # key -> [(keyed i, j, n)]
    raw = collections.defaultdict(lambda: [0.0, 0.0])
    for (i, j, k), (wi, wj) in t.items():
        n = wi + wj
        opp[i].append((j, n, k, True)); opp[j].append((i, n, k, False))
        wins[i] += wi; wins[j] += wj
        if k is not None:
            hw[k] += wi; hn[k] += n; by_key[k].append((i, j, n))
    for g in games:
        a, b, wa, wb = g[:4]
        if a != b:
            raw[a][0] += wa; raw[a][1] += wb
            raw[b][0] += wb; raw[b][1] += wa
    players = sorted(opp)
    keys = sorted(hn, key=str)
    r = newton(t, players, prior, tol) if not hn else {p: 1.0 for p in players}
    h = {k: 1.0 for k in keys}

    def m(k):
        return 1.0 if k is None else h[k]

    def p_win(p, q, k, keyed):   # (strength of p, strength of q) in a game keyed k, p on the keyed side or not
        return (r[p] * m(k), r[q]) if keyed else (r[p], r[q] * m(k))

    def sweep():   # one MM step (Gauss-Seidel) over the ratings, then the key advantages
        for p in players:
            # prior: PRIOR wins + PRIOR losses vs the anchor (strength 1)
            den = 2.0 * prior / (r[p] + 1.0)
            for q, n, k, keyed in opp[p]:
                sp, sq = p_win(p, q, k, keyed)
                den += n * (m(k) if keyed else 1.0) / (sp + sq)
            r[p] = (wins[p] + prior) / den
        for k in keys:
            den = 2.0 * prior / (h[k] + 1.0)
            for i, j, n in by_key[k]:
                den += n * r[i] / (r[i] * h[k] + r[j])
            h[k] = (hw[k] + prior) / den

    def get():
        return [math.log(r[p]) for p in players] + [math.log(h[k]) for k in keys]

    def put(x):
        for p, v in zip(players, x):
            r[p] = math.exp(v)
        for k, v in zip(keys, x[len(players):]):
            h[k] = math.exp(v)

    def step(x):
        put(x); sweep(); return get()

    def loglik():
        ll = 0.0
        for (i, j, k), (wi, wj) in t.items():
            si, sj = (r[i] * m(k), r[j])
            ll += wi * math.log(si / (si + sj)) + wj * math.log(sj / (si + sj))
        for v in list(r.values()) + list(h.values()):
            ll += prior * (math.log(v) - 2.0 * math.log(v + 1.0))
        return ll

    # SQUAREM: two MM steps, extrapolate along them, one more step; keep it only if the likelihood rose
    x0 = get()
    for _ in range(max(1, iters // 3) if hn else 0):
        x1 = step(x0); x2 = step(x1)
        dr = [b - a for a, b in zip(x0, x1)]
        dv = [c - 2 * b + a for a, b, c in zip(x0, x1, x2)]
        vv = sum(v * v for v in dv)
        xn = x2
        if vv > 0:
            alpha = min(-1.0, -math.sqrt(sum(d * d for d in dr) / vv))
            if alpha < -1.0:
                xa = step([a - 2 * alpha * d + alpha * alpha * v for a, d, v in zip(x0, dr, dv)])
                put(xa); la = loglik(); put(x2)
                if la >= loglik():
                    xn = xa
        delta = max(abs(a - b) for a, b in zip(x0, xn)) if xn else 0.0
        x0 = xn
        if delta < tol:
            break
    put(x0)
    keyed = {i for (i, j, k) in t if k is not None}
    if keys and not any(k is None and ((i in keyed) != (j in keyed)) for (i, j, k) in t):
        mu = sum(hn[k] * math.log(h[k]) for k in keys) / sum(hn.values())
        for k in keys:
            h[k] /= math.exp(mu)
        for p in keyed:
            r[p] *= math.exp(mu)
    logs = {p: math.log(r[p]) for p in players}
    mean = sum(logs.values()) / max(1, len(logs))
    out = {}
    for p in players:
        info = 2.0 * prior * r[p] / (r[p] + 1.0) ** 2
        for q, n, k, kd in opp[p]:
            sp, sq = p_win(p, q, k, kd)
            info += n * sp * sq / (sp + sq) ** 2
        w, l = raw[p]
        out[p] = Rating(1500 + SCALE * (logs[p] - mean), SCALE / math.sqrt(info), w + l, w, l)
    return out, {k: SCALE * math.log(h[k]) for k in keys}


def newton(t, players, prior, tol=1e-9, steps=60):
    """Strengths {player: r} maximizing the likelihood of the unkeyed table t with the anchor prior: Newton steps on
    log strengths, each solved by Jacobi-preconditioned conjugate gradients, with a backtracking line search."""
    idx = {p: i for i, p in enumerate(players)}
    pairs = [(idx[i], idx[j], wi, wj) for (i, j, k), (wi, wj) in t.items()]
    n = len(players)
    x = [0.0] * n
    sig = lambda z: 1.0 / (1.0 + math.exp(-z)) if z > -700 else 0.0

    def ll(x):
        v = 0.0
        for i, j, wi, wj in pairs:
            d = x[i] - x[j]
            v -= wi * math.log1p(math.exp(-d)) if d > -700 else wi * -d
            v -= wj * math.log1p(math.exp(d)) if d < 700 else wj * d
        for z in x:
            v -= prior * (math.log1p(math.exp(-z)) + math.log1p(math.exp(z)))
        return v

    cur = ll(x)
    for _ in range(steps):
        g = [prior * (1.0 - 2.0 * sig(z)) for z in x]
        dg = [2.0 * prior * sig(z) * (1.0 - sig(z)) + 1e-12 for z in x]
        hw = []
        for i, j, wi, wj in pairs:
            q = sig(x[i] - x[j]); m = wi + wj
            g[i] += wi - m * q; g[j] += wj - m * (1.0 - q)
            w = m * q * (1.0 - q); hw.append(w); dg[i] += w; dg[j] += w

        def hv(v):
            out = [a * b for a, b in zip(dg, v)]   # H = diag(dg) - offdiag(w): (Hv)_i = dg_i v_i - sum_j w_ij v_j
            for (i, j, _, _), w in zip(pairs, hw):
                out[i] -= w * v[j]; out[j] -= w * v[i]
            return out

        d = [0.0] * n; res = g[:]; z = [a / b for a, b in zip(res, dg)]; pv = z[:]
        rz = sum(a * b for a, b in zip(res, z)); g0 = math.sqrt(sum(a * a for a in g))
        for _ in range(4 * n):
            hp = hv(pv); a = rz / max(1e-300, sum(u * v for u, v in zip(pv, hp)))
            d = [u + a * v for u, v in zip(d, pv)]
            res = [u - a * v for u, v in zip(res, hp)]
            if math.sqrt(sum(u * u for u in res)) <= 1e-10 * max(g0, 1e-300):
                break
            z = [u / v for u, v in zip(res, dg)]; rz2 = sum(u * v for u, v in zip(res, z))
            pv = [u + (rz2 / rz) * v for u, v in zip(z, pv)]; rz = rz2
        step = 1.0
        while step > 1e-6:
            xn = [u + step * v for u, v in zip(x, d)]
            new = ll(xn)
            if new >= cur - 1e-12:
                break
            step /= 2
        x, cur = xn, new
        if max(abs(step * v) for v in d) < tol:
            break
    return {p: math.exp(x[idx[p]]) for p in players}


def expected(ra, rb):
    """P(a beats b) for Elo-scale ratings."""
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))


def field_score(ratings, player, field):
    """Mean expected score of player against each field player (one game each)."""
    xs = [expected(ratings[player].rating, ratings[f].rating) for f in field if f in ratings and f != player]
    return sum(xs) / len(xs) if xs else float('nan')

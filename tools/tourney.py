#!/usr/bin/env python3
"""Continuous local tournament of our own bots, ranked by Bradley-Terry (the 26b setup; owner prompt #2).

The pool is research/tourney/pool.txt (one bot per line; '# NAME (why)' = retired: unscheduled and unlisted,
but its games still count in the fit). Every local game in runs/*/results.jsonl between two pool
bots on the local map set (tools/maps-local.txt) counts (any seat, any map seed), so earlier screens and calibration runs seed the ladder.
The leader qualifies once it has MIN_GAMES games and leads the champion by one combined SE, and becomes the local champion after CONFIRM_GAMES fresh games in which it still leads (owner #46); research/tourney/champion.txt holds the current one,
and a change is submitted to the replica without any gate (prod does the submit).

  tourney.py rank [--runs-root DIR]        ladder with SE, games; flags a new champion
  tourney.py plan RUN [--games N]          write runs/RUN/cells.tsv: N games chosen where the ladder is least sure
  tourney.py add BOT                       enter BOT into the pool (it is scheduled first until it has NEW_MIN games)
  tourney.py chart                         progress/local-elo.png + local-elo.md: every champion and candidate on a
                                           wall-clock axis (owner 11-21: kept current at every prod)

research/tourney/champions.csv is the champion history (time PDT, bot, base, change, submission); when champion.txt
names a bot that is not its last row, chart appends it at champion.txt's modification time.

Pairing: bots with fewer than NEW_MIN games get half the run, weighted by their missing games, half of those games
against the champion and the rest against the current top TOP bots (TOP 20 covers the whole pool); the rest
goes to pairs among the top TOP, weighted toward close ratings and large standard errors (the places that decide
first place). Each game: a random map of the local set, a random map seed in 0..SEEDS-1, random seats.
"""
import json, os, random, re, sys, glob, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elolib

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(R, 'research', 'tourney', 'pool.txt')
CHAMP = os.path.join(R, 'research', 'tourney', 'champion.txt')
MAPS = open(os.path.join(R, 'tools', 'maps-local.txt')).read().split()
MIN_GAMES, NEW_MIN, TOP, SEEDS = 200, 40, 20, 10   # TOP 6 -> 10 (11-22 10:55): with a ~10-bot pool every bot keeps getting games
# TOP 10 -> 20 (11-24 13:33): with 11 pool bots the lowest-rated bot past NEW_MIN (played + planned) fell out of the top 10
# and got no games at all (yl53 none in tr623-tr625, sw77 none in tr626-tr628), so it could never reach MIN_GAMES


def pool():
    return [l.split('#')[0].strip() for l in open(POOL) if l.split('#')[0].strip()]


def retired():
    # '# NAME  (why)' lines: no longer scheduled or listed, but their games still anchor the fit (11-21 15:07)
    out = []
    for l in open(POOL):
        t = l.strip()
        if t.startswith('#') and len(t.split()) > 1:
            out.append(t.split()[1])
    return out


def run_num(path):
    """tr257 -> 257; study and calibration runs -> 0 (never fresh for the confirmation stage)."""
    m = re.search(r'/tr(\d+)/', path)
    return int(m[1]) if m else 0


def refs():
    """The replica reference bots (owner #35/#45): active pool lines whose comment says 'replica record' or
    'replica reference'."""
    return [l.split('#')[0].strip() for l in open(POOL)
            if l.split('#')[0].strip() and re.search('replica (record|reference)', l.split('#', 1)[-1])]


def last_run(root=R):
    """The highest tr run with any results: games after it are fresh."""
    fs = glob.glob(os.path.join(root, 'runs', 'tr*', 'results.jsonl'))
    return max([run_num(f) for f in fs if os.path.getsize(f)] or [0])


def games(root=R, runs=False):
    """(a, b, a_won, b_won) per game; with runs=True, (run number, that tuple)."""
    P, ms = set(pool()) | set(retired()), set(MAPS)
    out = []
    for f in glob.glob(os.path.join(root, 'runs', '*', 'results.jsonl')):
        rn = run_num(f)
        for line in open(f):
            if not line.startswith('{'):
                continue
            try:
                g = json.loads(line)
            except ValueError:
                continue
            if g.get('map') not in ms or g['a'] not in P or g['b'] not in P or g['a'] == g['b']:
                continue
            if g.get('winner') not in ('A', 'B'):
                continue
            t = (g['a'], g['b'], g['winner'] == 'A', g['winner'] == 'B')
            out.append((rn, t) if runs else t)
    return out


# Confirmation stage (owner #46, option 3 of the literature answer to #43): the bot that first clears the lead bar is
# partly lucky (winner's curse: over the 16 crownings before y221's, the lead shrank from +39 at crowning to +28), so a qualifier
# is crowned only after CONFIRM_GAMES fresh games (runs started after it qualified) in which it still leads the
# champion (> 0, a deliberately mild bar). A bot that fails is not retired: its window restarts, and it keeps playing
# under the usual pool rules. research/tourney/confirm.txt holds 'BOT RUN' per qualifier (fresh = runs after RUN).
CONFIRM = os.path.join(R, 'research', 'tourney', 'confirm.txt')
CONFIRM_GAMES = 150


def read_confirm():
    if not os.path.exists(CONFIRM):
        return {}
    return {p[0]: int(p[1]) for p in (l.split() for l in open(CONFIRM)) if len(p) >= 2 and not p[0].startswith('#')}


def write_confirm(state):
    with open(CONFIRM, 'w') as f:
        f.write('# BOT RUN: qualified for the crown; games in runs after RUN confirm it (tourney.py, owner #46)\n')
        for b, rn in sorted(state.items()):
            f.write(f'{b} {rn}\n')


def fresh(bot, since, ch, root=R):
    """bot's lead over the champion counting only its games in runs after `since`: (lead, se, fresh games)."""
    gr = games(root, runs=True)
    keep = [g for rn, g in gr if not (bot in g[:2] and rn <= since)]
    n = sum(1 for rn, g in gr if bot in g[:2] and rn > since)
    if not n:
        return 0.0, 400.0, 0
    rt = elolib.fit(keep)
    if bot not in rt or ch not in rt:
        return 0.0, 400.0, n
    return rt[bot].rating - rt[ch].rating, math.hypot(rt[bot].se, rt[ch].se), n


def ladder(root=R):
    gs = games(root)
    rt = elolib.fit(gs) if gs else {}
    P = pool()
    for b in P:
        if b not in rt:
            rt[b] = elolib.Rating(1500, 400, 0, 0, 0)
    return sorted(((b, rt[b]) for b in P), key=lambda x: -x[1].rating), len(gs)


def champion():
    return open(CHAMP).read().split()[0] if os.path.exists(CHAMP) else None


def cmd_rank(root):
    lad, n = ladder(root)
    print(f'{n} games among {len(lad)} pool bots ({len(retired())} retired; {len(lad) + len(retired())} entered in all)')
    ch = champion()
    rc0 = dict(lad).get(ch)
    for i, (b, r) in enumerate(lad, 1):
        tail = ''
        if rc0 is not None and b != ch:   # vs champion: lead, and the lead needed to replace it (one combined SE)
            need = math.hypot(r.se, rc0.se)
            gl = max(0, MIN_GAMES - r.games)
            tail = f'  vs {ch} {r.rating - rc0.rating:+5.0f} (needs > +{need:.0f}' + (f', {gl:.0f} more games)' if gl else ')')
        elif b == ch:
            tail = '  CHAMPION'
        print(f'{i:2d}. {b:6s} {r.rating:6.0f} +-{r.se:3.0f}  games {r.games:5.0f}  ({r.wins:g}-{r.losses:g}){tail}')
    elig = [(b, r) for b, r in lad if r.games >= MIN_GAMES]
    rc = dict(lad).get(ch)
    if elig and elig[0][0] != ch and rc is not None:
        # hysteresis (11-21 10:13): lead the champion by one combined SE; then the confirmation stage (owner #46)
        qual = [(b, r) for b, r in elig if b != ch and r.rating - rc.rating > math.hypot(r.se, rc.se)]
        old, last, crown = read_confirm(), last_run(root), None
        state = {b: old.get(b, last) for b, _ in qual}   # a new qualifier's window opens now; non-qualifiers drop out
        for b, r in qual:
            margin = math.hypot(r.se, rc.se)
            lead, se, n = fresh(b, state[b], ch, root)
            if n >= CONFIRM_GAMES and lead > 0:
                print(f'confirmed {b}: leads {ch} by {r.rating - rc.rating:.0f} > {margin:.0f}, and by {lead:+.0f} '
                      f'+-{se:.0f} in its {n} fresh games (runs after tr{state[b]})')
                crown = crown or (b, r, margin)
            elif n >= CONFIRM_GAMES:
                print(f'NOT CONFIRMED {b}: {lead:+.0f} +-{se:.0f} vs {ch} in its {n} fresh games (runs after '
                      f'tr{state[b]}); not retired, its window restarts after tr{last}')
                state[b] = last
            else:
                print(f'CONFIRMING {b}: leads {ch} by {r.rating - rc.rating:.0f} > {margin:.0f}; fresh {lead:+.0f} '
                      f'+-{se:.0f} in {n} of {CONFIRM_GAMES} games (runs after tr{state[b]})')
        if root == R and state != old:
            write_confirm(state)
        if crown:
            b, r, margin = crown
            print(f'NEW CHAMPION {b} (was {ch}): leads the bots with >= {MIN_GAMES} games by '
                  f'{r.rating - rc.rating:.0f} > {margin:.0f}, confirmed on fresh games')
        elif qual:
            print(f'champion {ch} (held: {", ".join(b for b, _ in qual)} confirming)')
        else:
            b, r = elig[0]
            print(f'champion {ch} (held: {b} leads it by {r.rating - rc.rating:.0f}, '
                  f'needs > {math.hypot(r.se, rc.se):.0f})')
    elif elig and elig[0][0] != ch:
        print(f'NEW CHAMPION {elig[0][0]} (was {ch}): leads the bots with >= {MIN_GAMES} games')
    else:
        print(f'champion {ch}')
    gs = games(root)
    guardrail(gs, ch)
    if root == R:   # keep progress/local-elo.md current every prod, not only at crownings
        import datetime as dt
        from zoneinfo import ZoneInfo
        write_md(gs, elolib.fit(gs), champ_history(), dt.datetime.now(ZoneInfo('America/Vancouver')))


def guardrail(gs, ch):
    """Owner #59/#60: the replica slots guard against behavioural regression. Report each slot's head-to-head record
    against the champion from the games already played (no extra games), and raise an alarm when a slot wins
    significantly more than half (by 2 SE, with 50+ games): a regression the local pool can see."""
    parts, alarms = [], []
    for s in refs():
        if s == ch:
            continue
        w = sum(1 for a, b, aw, bw in gs if (a, b) == (s, ch) and aw or (a, b) == (ch, s) and bw)
        l = sum(1 for a, b, aw, bw in gs if (a, b) == (s, ch) and bw or (a, b) == (ch, s) and aw)
        n = w + l
        if not n:
            parts.append(f'{s} no games')
            continue
        p = w / n
        se = math.sqrt(max(p * (1 - p), 0.25 / n) / n)
        parts.append(f'{s} {w}-{l} {100 * p:.1f}% +-{100 * se:.1f}')
        if n >= 50 and p - 0.5 > 2 * se:
            alarms.append(f'GUARDRAIL ALARM: {s} beats the champion {ch} head-to-head, {w}-{l} ({100 * p:.1f}% +-'
                          f'{100 * se:.1f}): look for a behavioural regression since {s}')
    if parts:
        print(f'guardrail (replica slots vs {ch}, head-to-head): ' + ', '.join(parts))
    for a in alarms:
        print(a)


def pending():
    """bot -> games planned in runs/*/cells.tsv but not yet in their results (unfinished runs), so consecutive plans
    do not each give a newcomer its full NEW_MIN (11-22 11:15: sw15 got 60 games in each of five plans)."""
    out = collections.Counter()
    for c in glob.glob(os.path.join(R, 'runs', 'tr*', 'cells.tsv')):
        d = os.path.dirname(c)
        if os.path.exists(os.path.join(d, 'DONE')):
            continue
        cells = [l.split('\t')[:2] for l in open(c) if l.strip()]
        rf = os.path.join(d, 'results.jsonl')
        done = sum(1 for _ in open(rf)) if os.path.exists(rf) else 0
        left = max(0.0, 1 - done / len(cells)) if cells else 0
        for a, b in cells:
            for x in (a, b):
                out[x.split('/')[-1]] += left
    return out


def cmd_plan(run, n):
    lad, _ = ladder()
    rate = {b: r for b, r in lad}
    pend = pending()
    have = {b: r.games + pend[b] for b, r in lad}   # games played + games already planned
    top = [b for b, r in lad if have[b] >= NEW_MIN][:TOP] or [b for b, _ in lad[:TOP]]
    new = [b for b, r in lad if have[b] < NEW_MIN and b not in top]
    pairs = []
    ch = champion()
    if new:   # weight by missing games (a fresh bot outweighs a half-rated one); half its games vs the champion
        nw = [max(NEW_MIN - have[b], NEW_MIN // 4) for b in new]   # floor: a bot 2 games short still plays (11-21 21:15)
        for k in range(n // 2 if len(top) >= 3 else n * 5 // 6):   # few rated bots: newcomers take most of the run
            b = random.choices(new, nw)[0]
            opp = [t for t in top if t != b] or [x for x, _ in lad if x != b]
            pairs.append((b, ch if ch in rate and ch != b and random.random() < 0.5 else random.choice(opp)))
    # a quarter of the run: the champion against the rated bots, weighted by their SE. Pair weights below decay with
    # the rating gap, and bots whose games are all planned among themselves sit at the 1500 prior, far from the
    # champion, so they never met it (11-26 09:30: y110-y115 played t36 once in 1000+ planned games, rated -340)
    if ch in rate:
        others = [b for b in top if b != ch]
        if others:
            sw = [min(rate[b].se, 350 / math.sqrt(max(have[b], 1))) + 10 for b in others]
            for k in range(n // 4):
                pairs.append((random.choices(others, sw)[0], ch))
    # owner #47: the replica references are regular (permanent) entrants: no extra games for them (the fifth of each
    # run that owner #45's vs refs column took, tr261-tr264 as first planned, was dropped)
    # owner #46: a bot in its confirmation window plays the champion more, so confirming costs about one prod
    for b in read_confirm():
        if b in rate and ch in rate and b != ch:
            pairs += [(b, ch)] * (n // 10)
    cand = [(a, b) for i, a in enumerate(top) for b in top[i + 1:]]
    # SE expected once the planned games are in (~350/sqrt(games)): an unplayed bot's prior SE of 400 would otherwise
    # pull every top-pair game in each of several consecutive plans (11-22 11:20)
    se = {x: min(rate[x].se, 350 / math.sqrt(max(have[x], 1))) for x in top}
    w = [(se[a] + se[b] + 10) * math.exp(-abs(rate[a].rating - rate[b].rating) / 100) for a, b in cand]
    while len(pairs) < n and cand:
        pairs.append(random.choices(cand, w)[0])
    os.makedirs(os.path.join(R, 'runs', run), exist_ok=True)
    with open(os.path.join(R, 'runs', run, 'cells.tsv'), 'w') as f:
        for a, b in pairs:
            if random.random() < 0.5:
                a, b = b, a
            f.write(f'bots/{a}\tbots/{b}\t{random.choice(MAPS)}\t{random.randrange(SEEDS)}\n')
    c = collections.Counter(x for p in pairs for x in p)
    print(f'{run}: {len(pairs)} games; ' + ' '.join(f'{b}:{k}' for b, k in c.most_common()))


CHAMPS = os.path.join(R, 'research', 'tourney', 'champions.csv')


def champ_history():
    import csv, datetime as dt
    from zoneinfo import ZoneInfo
    pdt = ZoneInfo('America/Vancouver')
    rows = list(csv.DictReader(open(CHAMPS)))
    ch = champion()
    if ch and (not rows or rows[-1]['bot'] != ch):   # a promotion not yet recorded: stamp it with champion.txt's mtime
        when = dt.datetime.fromtimestamp(os.path.getmtime(CHAMP), pdt)
        rows.append({'when_pdt': f'{when:%Y-%m-%d %H:%M}', 'bot': ch, 'base': rows[-1]['bot'] if rows else '',
                     'change': '', 'submission': ''})
        with open(CHAMPS, 'a') as f:
            f.write(f"{rows[-1]['when_pdt']},{ch},{rows[-1]['base']},,\n")
    for r in rows:
        r['when'] = dt.datetime.strptime(r['when_pdt'], '%Y-%m-%d %H:%M').replace(tzinfo=pdt)
    return rows


def entry_times():
    """bot -> when its snapshot was first committed (PDT), from one git log pass; uncommitted bots: directory mtime."""
    import subprocess, datetime as dt
    from zoneinfo import ZoneInfo
    pdt = ZoneInfo('America/Vancouver')
    out, t = {}, None
    log = subprocess.run(['git', '-C', R, 'log', '--diff-filter=A', '--name-only', '--format=@%ct', '--',
                          'bots/*/SNAPSHOT'], capture_output=True, text=True).stdout
    for l in log.splitlines():
        if l.startswith('@'):
            t = dt.datetime.fromtimestamp(int(l[1:]), pdt)
        elif l.startswith('bots/') and t:
            out[l.split('/')[1]] = t   # git log is newest first: the last seen is the first add
    for b in pool() + retired():
        if b not in out and os.path.isdir(os.path.join(R, 'bots', b)):
            out[b] = dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(R, 'bots', b)), pdt)
    return out


def write_md(gs, rt, hist, now, out=os.path.join(R, 'progress')):
    """progress/local-elo.md: every champion at its current rating. `rank` rewrites it each prod so it never goes
    stale between crownings; `chart` also redraws the PNG it embeds."""
    L = ['# Local tournament Elo', '',
         f'Bradley-Terry ratings of our own bots in the local tournament (`tools/tourney.py`), all {len(gs)} games in '
         f'one fit as of {now:%Y-%m-%d %H:%M} PDT, so every point is on the same scale; earlier champions are '
         'shown at their current rating, and "Gain" is the rating over the champion it replaced. `tools/tourney.py '
         'rank` rewrites this table; `tools/tourney.py chart` also redraws the chart.', '',
         '![local elo](local-elo.png)', '',
         '| Champion from (PDT) | Bot | Change on base | Submission | Rating +- SE | Gain | Games |',
         '|---|---|---|---:|---:|---:|---:|']
    for r in hist:
        x, y = rt.get(r['bot']), rt.get(r['base'])
        gain = f'{x.rating - y.rating:+.0f}' if x and y else ''
        L.append(f"| {r['when_pdt']} | {r['bot']} | {r['change'] + (' on ' + r['base'] if r['base'] else '')} | "
                 f"{('#' + r['submission']) if r['submission'] else ''} | "
                 f"{f'{x.rating:.0f} +- {x.se:.0f}' if x else '-'} | {gain} | {f'{x.games:.0f}' if x else '-'} |")
    open(os.path.join(out, 'local-elo.md'), 'w').write('\n'.join(L) + '\n')


def cmd_chart(out=os.path.join(R, 'progress')):
    import datetime as dt
    from zoneinfo import ZoneInfo
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import milestones as MS
    pdt = ZoneInfo('America/Vancouver')
    gs = games()
    rt = elolib.fit(gs) if gs else {}
    hist = champ_history()
    start, now = hist[0]['when'], dt.datetime.now(pdt)
    ent = entry_times()
    champs = {r['bot'] for r in hist}
    cand = [(ent[b], rt[b]) for b in set(pool()) | set(retired())
            if b in rt and b in ent and b not in champs and ent[b] >= start and rt[b].games >= 10]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter([w for w, _ in cand], [r.rating for _, r in cand], s=[8 + r.games / 8 for _, r in cand],
               color='#adb5bd', alpha=0.7, label='candidates (at entry; size = games)', zorder=2)
    xs, ys, labels = [], [], []
    for i, r in enumerate(hist):
        b = r['bot']
        if b not in rt:
            continue
        end = hist[i + 1]['when'] if i + 1 < len(hist) else now
        xs += [r['when'], end]
        ys += [rt[b].rating, rt[b].rating]
        ax.errorbar([r['when']], [rt[b].rating], yerr=[rt[b].se], fmt='o', color='#2a6fdb', ms=6, capsize=3, zorder=4)
        labels.append((r['when'], rt[b].rating, rt[b].se, ys[-3] if len(ys) > 2 else rt[b].rating, b))
    ax.plot(xs, ys, color='#2a6fdb', lw=1.8, label='local champion (rating +- SE, current fit)', zorder=3)
    for i, (when, label) in enumerate(m for m in MS.read() if m[0] >= start - dt.timedelta(hours=1)):
        ax.axvline(when, color=MS.COLOR, ls='--', lw=1.3)
    ax.set_xlim(start - dt.timedelta(minutes=30), now + dt.timedelta(minutes=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M', tz=pdt))
    ax.set_xlabel('time (PDT)')
    ax.set_ylabel('Bradley-Terry rating (local tournament)')
    ax.set_title(f'Local tournament: champions and candidates ({len(gs)} games, {now:%m-%d %H:%M} PDT)')
    ax.grid(color='#e9ecef')
    ax.legend(loc='lower right', fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    # Champion labels: the bot name only (local-elo.md's table gives each change and submission). They are placed
    # after the layout, so they never shrink the plot: owner 11-23, the full change text beside every point squeezed
    # the axes to half the figure. Each name takes the first spot beside its point that stays inside the axes and
    # clear of the legend, of every champion's marker, error bar and step up, and of the names already placed.
    import matplotlib.patheffects as pe
    from matplotlib.transforms import Bbox
    rend = fig.canvas.get_renderer()
    box = ax.get_window_extent(rend)
    taken = [ax.get_legend().get_window_extent(rend)]
    for when, rating, se, prev, _ in labels:
        x = mdates.date2num(when)
        (x0, y0), (_, y1) = ax.transData.transform([(x, min(rating - se, prev)), (x, max(rating + se, prev))])
        taken.append(Bbox([[x0 - 5, y0 - 5], [x0 + 5, y1 + 5]]))   # 5 px: the 3 pt caps and the 6 pt marker
    spots = [((5, 4), 'left', 'bottom'), ((5, -4), 'left', 'top'), ((-5, 4), 'right', 'bottom'),
             ((-5, -4), 'right', 'top'), ((0, 9), 'center', 'bottom'), ((0, -9), 'center', 'top')]
    halo = [pe.withStroke(linewidth=2.5, foreground='white')]
    for when, rating, se, prev, b in labels:
        for k, (off, ha, va) in enumerate(spots):
            t = ax.annotate(b, (when, rating), xytext=off, textcoords='offset points', ha=ha, va=va, fontsize=8,
                            color='#212529', zorder=5, path_effects=halo)
            bb = t.get_window_extent(rend)
            inside = box.x0 <= bb.x0 and bb.x1 <= box.x1 and box.y0 <= bb.y0 and bb.y1 <= box.y1
            if inside and not any(bb.overlaps(o) for o in taken) or k == len(spots) - 1:
                taken.append(bb)
                break
            t.remove()
    fig.savefig(os.path.join(out, 'local-elo.png'), dpi=110)
    plt.close(fig)
    write_md(gs, rt, hist, now, out)
    print(f'local-elo.png: {len(hist)} champions, {len(cand)} candidates')


def cmd_add(bot):
    if bot in pool():
        print(f'{bot} already in pool'); return
    with open(POOL, 'a') as f:
        f.write(bot + '\n')
    print(f'added {bot}')


if __name__ == '__main__':
    a = sys.argv[1:]
    root = a[a.index('--runs-root') + 1] if '--runs-root' in a else R
    if not a or a[0] == 'rank':
        cmd_rank(root)
    elif a[0] == 'plan':
        if a[1].startswith('-'):
            sys.exit('plan: RUN must be a run name, not an option')
        cmd_plan(a[1], int(a[a.index('--games') + 1]) if '--games' in a else 120)
    elif a[0] == 'add':
        cmd_add(a[1])
    elif a[0] == 'chart':
        cmd_chart()
    else:
        print(__doc__)

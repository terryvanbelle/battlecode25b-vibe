"""Topic 114: what happens on the ruin of a KILLED tower, both sides, paint towers above all.  Completing a tower needs
only an adjacent robot, 1000 chips and the 24 pattern tiles in the side's colours (RULES 4.6, 5.3); no paint, no
cooldown.  Our Unit.rebuild (Unit.java:74-83), which every robot runs every turn, re-completes only a MONEY tower; a
killed paint tower comes back only if a soldier picks the ruin (Soldier.pickRuin, readMarks).  Per killed tower (a
'die' row; churns have none) at the end of its death round: how many of the 24 tiles still hold its own pattern in
the side's colours, enemy tiles in the 5x5, the side's chips, whether a robot of the side stands within d2 2 of the
ruin in the next 5 rounds, and the next tower built on the ruin (round, type, side).  Lost and won games, by side and
by the killed tower's type; and the subset where the tower was the side's last paint tower."""
import lib
from collections import Counter, defaultdict

PATS = {'PAINT_TOWER': lib.PAT['PAINT_TOWER'], 'MONEY_TOWER': lib.PAT['MONEY_TOWER'], 'DEFENSE_TOWER': lib.PAT['DEFENSE_TOWER']}


def analyse(G):
    b, d = lib.tower_events(G)
    kills = set(int(a[5]) for a in G.acts if a[4] == 'die' and a[7] in lib.TOW)
    ev = [x for x in d if x[1] in kills and x[3] in (1, 2)]
    ev.sort()
    builds_at = defaultdict(list)
    for x in b:
        if x[0] > 0: builds_at[(x[4], x[5])].append(x)
    grid = list(G.paint0); W = G.W
    out = []
    i = 0
    def snap(e):
        r, tid, typ, side, x, y = e
        pat = PATS.get(typ)
        ok = en = emp = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if not (dx or dy): continue
                X, Y = x + dx, y + dy
                if not (0 <= X < G.W and 0 <= Y < G.H): continue
                v = grid[X + Y * W]
                if v == 0: emp += 1; continue
                if lib.owner(v) != side: en += 1; continue
                sec = v in (2, 4)
                if pat is not None and sec == bool((pat >> (5 * (dx + 2) + dy + 2)) & 1): ok += 1
        return ok, en, emp
    acts = G.acts
    for a in acts:
        while i < len(ev) and a[0] > ev[i][0]:
            out.append((ev[i], snap(ev[i]))); i += 1
        if a[4] == 'paint':
            x, y = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        elif a[4] == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
    while i < len(ev):
        out.append((ev[i], snap(ev[i]))); i += 1
    bt = lib.by_round_turns(G)
    rows = []
    for (e, (ok, en, emp)) in out:
        r, tid, typ, side, x, y = e
        nxt = [z for z in builds_at.get((x, y), ()) if z[0] >= r]
        nb = nxt[0] if nxt else None
        adj = None
        for rr in range(r, min(G.end, r + 5) + 1):
            for t in bt.get(rr, ()):
                if t[2] == side and t[3] in lib.BOT and lib.d2((t[4], t[5]), (x, y)) <= 2:
                    adj = rr; break
            if adj is not None: break
        alive = lib.towers_alive(G, side, r, b, d)
        last_pt = typ == 'PAINT_TOWER' and not any(t[2] == 'PAINT_TOWER' for t in alive)
        rows.append(dict(r=r, typ=typ, side=side, ok=ok, en=en, emp=emp, chips=lib.money(G, side, r), adj=adj, last=last_pt,
                         nb=None if nb is None else (nb[0] - r, nb[2], nb[3])))
    return rows


def table(title, rows):
    print(f'\n== {title}: {len(rows)} killed towers')
    if not rows: return
    n = len(rows)
    intact = [x for x in rows if x['ok'] == 24]
    near = [x for x in rows if x['ok'] >= 20 and x['en'] == 0]
    ready = [x for x in intact if x['chips'] >= 1000 and x['adj'] is not None]
    print(f'   pattern at death: all 24 tiles {len(intact)} ({100 * len(intact) / n:.0f}%), 20+ and no enemy tile {len(near)} ({100 * len(near) / n:.0f}%), '
          f'median own-pattern tiles {lib.med([x["ok"] for x in rows])}, enemy tiles {lib.med([x["en"] for x in rows])}')
    print(f'   intact + chips >= 1000 + a robot of the side within d2 2 in the next 5 rounds: {len(ready)} ({100 * len(ready) / n:.0f}%)')
    def nxt(S, lab):
        c = Counter()
        for x in S:
            if x['nb'] is None: c['never rebuilt'] += 1; continue
            dt, ty, sd = x['nb']
            who = 'same side' if sd == x['side'] else 'OTHER side'
            when = '<=5r' if dt <= 5 else ('6-50r' if dt <= 50 else '>50r')
            c[f'{who} {ty[:5]} {when}'] += 1
        print(f'      next tower on the ruin, {lab} ({len(S)}): ' + ', '.join(f'{k} {v}' for k, v in sorted(c.items(), key=lambda kv: -kv[1])))
    nxt(rows, 'all')
    nxt(intact, 'pattern intact')
    nxt(ready, 'intact + chips + helper adjacent')


R = {k: [] for k in ('lost', 'won')}
for G in lib.games('all'):
    k = 'lost' if G.won_op else 'won'
    for x in analyse(G):
        x['who'] = 'us' if x['side'] == G.us else 'them'
        x['game'] = f'm{G.m}g{G.g}'
        R[k].append(x)
    lib.lite(G)

for k in ('lost', 'won'):
    for who in ('us', 'them'):
        for typ in ('PAINT_TOWER', 'MONEY_TOWER'):
            table(f'{k.upper()} games, {who}: killed {typ}s', [x for x in R[k] if x['who'] == who and x['typ'] == typ])
        table(f'{k.upper()} games, {who}: killed LAST paint towers', [x for x in R[k] if x['who'] == who and x['last']])
print('\nour killed paint towers in lost games with the pattern intact, chips and a helper adjacent (missed instant rebuilds):')
for x in R['lost']:
    if x['who'] == 'us' and x['typ'] == 'PAINT_TOWER' and x['ok'] == 24 and x['chips'] >= 1000 and x['adj'] is not None:
        print(f'   {x["game"]} r{x["r"]} last={x["last"]} chips {x["chips"]} helper r{x["adj"]} next {x["nb"]}')

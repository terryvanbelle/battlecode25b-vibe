"""Topic 123: robots that die of paint starvation, splashers above all (t121: in r201+ of the losses our splashers
die 0.99 times per 100 splasher-turns, theirs 0.27, and only 8% of ours are killed by a tower).  A robot at 0 paint
can neither act nor move and loses 20 HP a turn (RULES 3, 5.3); only a mopper can save it.  A 'die' row whose actor
is the victim itself is a starvation death (robots deal no HP damage to robots).
Per side, type and result, r101+:
  deaths, starved share, deaths per 100 turns
  for starved robots: paint 10 / 20 turns before death, the turn it last held 50+ paint and how far it walked
  after that, drained by enemy moppers in the last 15 rounds, ended on enemy / neutral / own paint (replayed grid),
  d2 to the nearest own tower holding 50+ paint at its last turn with 50+ paint (end-of-turn rows), and whether a
  side's mopper was within d2 8 in its last 5 turns.
Splash discipline: for every splash, the splasher's end-of-turn paint that round (after the 50 it cost), by band.
And splashers' refill behaviour: the paint with which a splasher ends a withdrawal ('transfer' from a tower)."""
import lib
from collections import defaultdict, Counter


def run(which):
    S = defaultdict(list)          # (who, type) -> starved records
    D = Counter()                  # (who, type, cause) -> deaths
    T = Counter()                  # (who, type) -> robot-turns r101+
    SPL = defaultdict(Counter)     # who -> band of end-of-turn paint after a splash
    WD = defaultdict(list)         # who -> paint after a splasher's withdrawal
    n = 0
    for G in lib.games(which):
        n += 1
        side = lambda s: 'us' if s == G.us else 'them'
        life = defaultdict(list)   # robot id -> [(round, x, y, paint)]
        towers = defaultdict(list)  # round -> [(team, x, y, paint)]
        for t in G.turns:
            if t[3] in lib.BOT:
                life[t[1]].append((t[0], t[4], t[5], t[7]))
                if t[0] > 100: T[(side(t[2]), t[3])] += 1
            elif t[3] in lib.TOW:
                towers[t[0]].append((t[2], t[4], t[5], t[7]))
        drained = defaultdict(list)
        splash_r = set(); wd_r = set()
        for a in G.acts:
            if a[4] == 'drain': drained[int(a[5])].append(a[0])
            elif a[4] == 'splash': splash_r.add((a[0], a[1]))
            elif a[4] == 'transfer' and a[3] == 'SPLASHER' and int(a[6]) < 0: wd_r.add((a[0], a[1]))
        # end-of-turn paint after splashes / withdrawals
        for rid, L in life.items():
            if G.typ.get(rid) != 'SPLASHER': continue
            who = side(G.team[rid])
            for (r, x, y, p) in L:
                if (r, rid) in splash_r:
                    SPL[who]['<50' if p < 50 else '50-99' if p < 100 else '100-149' if p < 150 else '150+'] += 1
                if (r, rid) in wd_r: WD[who].append(p)
        # deaths
        dead = {}
        for a in G.acts:
            if a[4] == 'die' and a[7] in lib.BOT and a[0] > 100:
                vic = int(a[5])
                dead[vic] = (a[0], 'starved' if int(a[1]) == vic else ('tower' if a[3] in lib.TOW else 'other'))
        # grid at each death (only for starved): replay paints, check at the death round
        want = {v: d[0] for v, d in dead.items() if d[1] == 'starved'}
        tile_at = {}
        if want:
            byr = defaultdict(list)
            for v, r in want.items():
                L = life.get(v)
                if L: byr[r].append((v, L[-1][1], L[-1][2]))
            grid = list(G.paint0); W = G.W
            cur = 0
            rounds = sorted(byr)
            ri = 0
            for a in G.acts:
                while ri < len(rounds) and a[0] > rounds[ri]:
                    for (v, x, y) in byr[rounds[ri]]: tile_at[v] = grid[x + y * W]
                    ri += 1
                k = a[4]
                if k == 'paint':
                    x, y = map(int, a[5].split(',')); sec = a[6] == '1'
                    grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
                elif k == 'unpaint':
                    x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
            while ri < len(rounds):
                for (v, x, y) in byr[rounds[ri]]: tile_at[v] = grid[x + y * W]
                ri += 1
        # mopper positions per round (for 'a mopper of the side near in the last 5 turns')
        mop = defaultdict(list)
        for t in G.turns:
            if t[3] == 'MOPPER': mop[(t[0], t[2])].append((t[4], t[5]))
        for v, (r, cause) in dead.items():
            ty = G.typ.get(v); tm = G.team.get(v)
            if ty not in lib.BOT or tm is None: continue
            who = side(tm)
            D[(who, ty, cause)] += 1
            if cause != 'starved': continue
            L = life.get(v)
            if not L: continue
            p10 = next((p for (rr, x, y, p) in reversed(L) if rr <= r - 10), None)
            p20 = next((p for (rr, x, y, p) in reversed(L) if rr <= r - 20), None)
            last50 = next(((rr, x, y) for (rr, x, y, p) in reversed(L) if p >= 50), None)
            walked = None; tdist = None
            if last50:
                walked = len([1 for (rr, x, y, p) in L if rr > last50[0]])
                best = None
                for (tt, tx, ty2, tp) in towers.get(last50[0], ()):
                    if tt == tm and tp >= 50:
                        dd = lib.d2((last50[1], last50[2]), (tx, ty2))
                        if best is None or dd < best: best = dd
                tdist = best
            dr = sum(1 for x in drained.get(v, ()) if r - 15 <= x <= r)
            tile = tile_at.get(v)
            tl = None if tile is None else ('own' if tile and lib.owner(tile) == tm else 'enemy' if tile else 'neutral')
            mnear = any(lib.d2((L[-1][1], L[-1][2]), m) <= 8 for rr in range(r - 5, r + 1) for m in mop.get((rr, tm), ()))
            S[(who, ty)].append(dict(p10=p10, p20=p20, walked=walked, tdist=tdist, dr=dr, tile=tl, mnear=mnear,
                                     rounds50=(r - last50[0]) if last50 else None))
        lib.lite(G)
    print(f'\n== {which} games ({n}), deaths in r101+')
    for ty in lib.BOT:
        for who in ('us', 'them'):
            tot = sum(D[(who, ty, c)] for c in ('starved', 'tower', 'other'))
            if not tot: continue
            st = D[(who, ty, 'starved')]
            R = S[(who, ty)]
            tiles = Counter(x['tile'] for x in R)
            print(f'   {ty:8s} {who:4s}: deaths {tot} = {100 * tot / max(1, T[(who, ty)]):.2f}/100 turns ({T[(who, ty)]} turns), '
                  f'starved {st} ({100 * st / tot:.0f}%) = {100 * st / max(1, T[(who, ty)]):.2f}/100 turns')
            if R:
                print(f'        starved: paint 10 turns before med {lib.med([x["p10"] for x in R])}, 20 before {lib.med([x["p20"] for x in R])}; '
                      f'last 50+ paint {lib.med([x["rounds50"] for x in R])} rounds before death (p25 {lib.pct([x["rounds50"] for x in R], .25)}, p75 {lib.pct([x["rounds50"] for x in R], .75)}); '
                      f'nearest own tower holding 50+ paint then: d2 med {lib.med([x["tdist"] for x in R])} (none known: {sum(1 for x in R if x["tdist"] is None)}); '
                      f'drained by enemy moppers in its last 15 rounds {100 * sum(1 for x in R if x["dr"]) / len(R):.0f}%; '
                      f'died on {dict(tiles)}; own mopper within d2 8 in its last 5 turns {100 * sum(1 for x in R if x["mnear"]) / len(R):.0f}%')
    for who in ('us', 'them'):
        c = SPL[who]; t = sum(c.values())
        if t:
            print(f'   splashes by {who}: {t}; the splasher\'s paint at the end of that turn: ' +
                  ', '.join(f'{b} {100 * c[b] / t:.0f}%' for b in ('<50', '50-99', '100-149', '150+')))
        if WD[who]:
            print(f'   splasher withdrawals by {who}: {len(WD[who])}, paint at the end of that turn med {lib.med(WD[who])} (p25 {lib.pct(WD[who], .25)})')


run('lost')
run('won')

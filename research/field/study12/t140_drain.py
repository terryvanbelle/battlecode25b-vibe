"""Topic 140: the passive paint drain and silent attacks (new).
1. At the end of every robot turn the engine takes paint for the tile the robot stands on and for every ALLIED unit,
   robots and towers, within r2 2 of it (RULES 5.3):
       own paint: allies        neutral: 1*mult + allies        enemy: 2*mult + 2*allies        (mult 2 for moppers)
   No study measured it.
2. A soldier attack on a tile it cannot paint (enemy paint, a ruin, our own tower) costs 5 paint and leaves NO row in
   the replay (InternalRobot.soldierAttack records only a tower hit or a paint).  It shows up only in the paint ledger.
Exact replay, per game: turns in file order (the engine's order within a round); each robot's own actions of the turn
applied first (paint / unpaint on the grid, kills remove the victim, spawns add the new robot); positions live (a
robot that has had its turn this round stands where its record says, the others where their last record says,
towers fixed).  Ledger per robot turn: expected = max(0, min(cap, prev + own) - penalty), own = -5 per soldier
attack or paint row, -50 per splash, -25 per pattern mark (20+ mark rows in one turn), +withdrawn, -given, +5 per
mopper drain row; turns on which someone else touched the robot's paint since its previous turn (a drain, a swing or a
transfer on it) are left out of the check.  On the other turns: residual 0 = the rule holds exactly; a soldier with
residual 5 made an attack that did nothing ('silent'); anything else is a mismatch (printed with a few examples).
Per side, unit type and phase (losses, then wins): paint lost per 100 robot-turns, split into the tile part (1*mult on
neutral, 2*mult on enemy) and the crowding part (allies, x2 on enemy paint); the share of turns with 1+ / 2+ / 3+
allies within r2 2; how much of the crowding cost has a tower among those allies (refill queues, churn waits); the
tile under the robot; and, for scale, the paint the robots spent on actions and withdrew from towers."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')
NB = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def run(G, S, CHK):
    W = G.W
    grid = list(G.paint0)
    acts = defaultdict(list)
    for a in G.acts: acts[(a[0], a[1])].append(a)
    touched = set()
    occ = {}            # (x, y) -> (id, team, is_tower)
    pos = {}
    last_paint = {}
    rounds = defaultdict(list)
    for t in G.turns: rounds[t[0]].append(t)
    turn_keys = set((t[0], t[1]) for t in G.turns)
    tpos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in tpos: tpos[t[1]] = (t[4], t[5], t[2])
    pending_end = defaultdict(list)
    for k, L in acts.items():
        if k not in turn_keys: pending_end[k[0]].extend(L)

    def place(i, team, x, y, tower):
        old = pos.get(i)
        if old is not None and occ.get(old, (None,))[0] == i: del occ[old]
        pos[i] = (x, y); occ[(x, y)] = (i, team, tower)

    def remove(i):
        old = pos.pop(i, None)
        if old is not None and occ.get(old, (None,))[0] == i: del occ[old]

    def apply(a):
        k = a[4]
        if k == 'paint':
            x, y = map(int, a[5].split(',')); sec = a[6] == '1'
            grid[x + y * W] = (2 if sec else 1) if a[2] == 1 else (4 if sec else 3)
        elif k == 'unpaint':
            x, y = map(int, a[5].split(',')); grid[x + y * W] = 0
        elif k == 'spawn':
            i = int(a[5]); x, y = map(int, a[7].split(',')); place(i, a[2], x, y, a[6] in lib.TOW)
        elif k == 'build':
            q = tpos.get(int(a[5]))
            if q: place(int(a[5]), q[2], q[0], q[1], True)
        elif k in ('die', 'died'):
            remove(int(a[5]))
        elif k == 'drain':
            touched.add(int(a[5]))
        elif k == 'mop':
            for v in (a[5], a[6], a[7]):
                if v and v != '0': touched.add(int(v))
        elif k == 'transfer':
            if a[5] and int(a[6] or 0) > 0: touched.add(int(a[5]))   # a mopper gave paint to it

    for r in sorted(rounds):
        p = ph(r)
        for t in rounds[r]:
            _, i, team, typ, x, y, hp, paint = t
            L = acts.get((r, i), ())
            for a in L: apply(a)
            if typ in lib.TOW:
                if i not in pos: place(i, team, x, y, True)
                continue
            place(i, team, x, y, False)
            own = 0; nmark = 0; natk = 0; withdrew = 0
            for a in L:
                k = a[4]
                if k == 'mark': nmark += 1
                elif k == 'attack' and typ == 'SOLDIER': natk += 1
                elif k == 'paint' and typ == 'SOLDIER': natk += 1
                elif k == 'splash': own -= 50
                elif k == 'drain' and typ == 'MOPPER' and a[6] == '10': own += 5   # a single-target drain gives the mopper 5; a swing gives nothing
                elif k == 'transfer' and a[6]:
                    amt = int(a[6])
                    if amt < 0: own += -amt; withdrew += -amt
                    elif amt > 0 and a[5] and int(a[5]) != i: own -= amt
            own -= 5 * natk
            if nmark >= 20: own -= 25
            spent = 5 * natk + (50 if any(a[4] == 'splash' for a in L) else 0) + (25 if nmark >= 20 else 0)
            v = grid[x + y * W]
            o = lib.owner(v)
            allies = 0; tow = False
            for dx, dy in NB:
                q = occ.get((x + dx, y + dy))
                if q is not None and q[1] == team and q[0] != i:
                    allies += 1
                    if q[2]: tow = True
            mult = 2 if typ == 'MOPPER' else 1
            if o == team: base, crowd, kind = 0, allies, 'own'
            elif o == 0: base, crowd, kind = mult, allies, 'neutral'
            else: base, crowd, kind = 2 * mult, 2 * allies, 'enemy'
            pen = base + crowd
            prev = last_paint.get(i)
            cap = lib.CAP[typ]
            if paint > 0 or prev is None: lost = pen
            else: lost = max(0, min(pen, min(cap, prev + own)))
            frac = lost / pen if pen else 0
            if p is not None:
                side = 'us' if team == G.us else 'them'
                D = S[(side, typ, p)]
                D['turns'] += 1
                D['base'] += base * frac; D['crowd'] += crowd * frac
                if tow: D['crowd_tower'] += crowd * frac
                D['tile_' + kind] += 1
                if allies >= 1: D['a1'] += 1
                if allies >= 2: D['a2'] += 1
                if allies >= 3: D['a3'] += 1
                D['spent'] += spent; D['withdrew'] += withdrew
                if prev is not None and i not in touched:
                    exp = max(0, min(cap, prev + own) - pen)
                    res = exp - paint
                    C = CHK[(side, typ)]
                    C['n'] += 1
                    if res == 0: C['ok'] += 1
                    elif typ == 'SOLDIER' and res == 5 and prev + own - 5 - pen >= 0:
                        C['silent'] += 1; D['silent'] += 1
                        D['silent_' + kind] += 1
                    else:
                        C['bad'] += 1
                        if len(CHK['ex']) < 10: CHK['ex'].append((G.m, G.g, r, i, side, typ, prev, own, pen, kind, allies, paint, [a[4] for a in L]))
            last_paint[i] = paint
            touched.discard(i)
            if any(a[4] in ('die', 'died') and a[5] == str(i) for a in L): remove(i)   # died in its own turn
        for a in pending_end.get(r, ()): apply(a)


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); CHK = defaultdict(lambda: defaultdict(int)); CHK['ex'] = []
    ng = 0
    for G in lib.games(which):
        run(G, S, CHK); ng += 1
    print(f'== {which} games: {ng}')
    print('   ledger check on untouched turns (exact / silent soldier attack / other):')
    for side in ('us', 'them'):
        for typ in lib.BOT:
            C = CHK[(side, typ)]
            if C['n']: print(f'      {side:4s} {typ:8s} {C["n"]:8d} turns: exact {100 * C["ok"] / C["n"]:5.1f}%  silent {100 * C["silent"] / C["n"]:5.2f}%  other {100 * C["bad"] / C["n"]:5.2f}%')
    for b in CHK['ex']: print('      example', b)
    for typ in lib.BOT:
        print(f'  {typ}')
        print('     phase      side  robot-turns  lost/100t  tile  crowd (tower)  1+ allies  2+    3+    on own / neutral / enemy   spent/100t  withdrawn/100t  silent attacks/100t')
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, typ, p)]
                n = D['turns']
                if not n: continue
                f = 100 / n
                print(f'     {PHN[p]:9s}  {side:4s}  {int(n):11d}  {f * (D["base"] + D["crowd"]):9.1f}  {f * D["base"]:4.1f}  {f * D["crowd"]:5.1f} ({f * D["crowd_tower"]:4.1f})'
                      f'  {f * D["a1"]:8.1f}%  {f * D["a2"]:4.1f}% {f * D["a3"]:4.1f}%   {f * D["tile_own"]:5.1f} / {f * D["tile_neutral"]:5.1f} / {f * D["tile_enemy"]:5.1f}'
                      f'   {f * D["spent"]:9.1f}  {f * D["withdrew"]:9.1f}   {f * D["silent"]:6.2f} (on own {f * D["silent_own"]:4.2f}, neutral {f * D["silent_neutral"]:4.2f}, enemy {f * D["silent_enemy"]:4.2f})')
    print('  ALL ROBOTS, per game (sums / games):')
    for p in range(3):
        for side in ('us', 'them'):
            tot = sum(S[(side, t, p)]['base'] + S[(side, t, p)]['crowd'] for t in lib.BOT)
            crowd = sum(S[(side, t, p)]['crowd'] for t in lib.BOT)
            ctow = sum(S[(side, t, p)]['crowd_tower'] for t in lib.BOT)
            sp = sum(S[(side, t, p)]['spent'] for t in lib.BOT)
            wd = sum(S[(side, t, p)]['withdrew'] for t in lib.BOT)
            sil = 5 * S[(side, 'SOLDIER', p)]['silent']
            print(f'     {PHN[p]:9s} {side:4s}: lost {tot / max(1, ng):7.0f} (crowding {crowd / max(1, ng):6.0f}, beside a tower {ctow / max(1, ng):6.0f});'
                  f' spent on actions {sp / max(1, ng):7.0f} (of it silent soldier attacks {sil / max(1, ng):5.0f}); withdrawn {wd / max(1, ng):7.0f}; lost / spent {100 * tot / max(1, sp):5.1f}%')

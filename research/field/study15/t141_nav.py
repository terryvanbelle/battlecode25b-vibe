"""Topic 141: how robots move and wait (new: no study looked at movement quality or the low-paint cooldown tax).
From turns.tsv with the cooldown columns (lib.extra: movement cooldown mcd and action cooldown acd at the END of each
turn; a turn starts with max(0, cd - 10), and a robot can move / act when that is < 10, RULES 3).  Per robot, turn k:
  moved      its tile differs from turn k-1
  reversal   moved back to the tile of turn k-2 (A-B-A); classed by what it did: 'siege' (it hit an enemy tower at
             k or k-1: the step-in / step-out kite), 'tower' (within r2 2 of an own tower at k-1, k or k+1: refill
             queues, churn waits), 'free' (everything else)
  could move start-of-turn mcd < 10 and paint > 0 at the end of turn k-1 (a 0-paint robot cannot move)
  idle       could move, did not move, and no action row at all this turn ('free idle': not beside an own tower)
  move tax   the movement cooldown a move added beyond the base 10: the low-paint multiplier (paint under 50% of
             capacity, RULES 3); summed and divided by 10 = moves lost
  act tax    the same for soldier attacks / paints (base 10), splashes (base 50) and mopper actions (base 30), on
             turns without a transfer; 'acts lost' = tax / base, i.e. the share of an action lost
  stuck      a window of 10 turns with 6+ moves but at most 3 distinct tiles (oscillating in place)
Per side, unit type and phase, losses then wins; per 100 robot-turns unless noted."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def run(G, S):
    X = lib.extra(G)
    acts = defaultdict(list)
    for a in G.acts: acts[(a[0], a[1])].append(a[4])
    towers_at = defaultdict(set)   # round -> set of (x, y, team) of towers alive (from tower turn rows)
    seq = defaultdict(list)
    for t, e in zip(G.turns, X):
        if t[3] in lib.TOW:
            towers_at[t[0]].add((t[4], t[5], t[2]))
        else:
            seq[t[1]].append((t[0], t[4], t[5], t[7], e[0], e[1], t[2], t[3]))
    for i, L in seq.items():
        team, typ = L[0][6], L[0][7]
        side = 'us' if team == G.us else 'them'
        cap = lib.CAP[typ]
        win = []
        for k in range(1, len(L)):
            r, x, y, paint, mcd, acd = L[k][:6]
            pr, px, py, ppaint, pmcd, pacd = L[k - 1][:6]
            if r != pr + 1: win = []; continue
            p = ph(r)
            if p is None: continue
            D = S[(side, typ, p)]
            D['turns'] += 1
            A = acts.get((r, i), [])
            moved = (x, y) != (px, py)
            smcd = max(0, pmcd - 10); sacd = max(0, pacd - 10)
            could = smcd < 10 and ppaint > 0
            near_t = False
            for rr in (r - 1, r, r + 1):
                for (tx, ty, tt) in towers_at.get(rr, ()):
                    if tt == team and (tx - x) ** 2 + (ty - y) ** 2 <= 2: near_t = True; break
                if near_t: break
            if moved:
                D['moves'] += 1
                tax = mcd - smcd - 10
                if tax > 0: D['mtax'] += tax; D['taxed_moves'] += 1
                if k >= 2 and L[k - 2][0] == pr - 1 and (x, y) == (L[k - 2][1], L[k - 2][2]):
                    siege = 'attack' in A and typ == 'SOLDIER' or 'attack' in acts.get((pr, i), []) and typ == 'SOLDIER'
                    ctx = 'siege' if siege else 'tower' if near_t else 'free'
                    D['rev_' + ctx] += 1
            if could:
                D['could'] += 1
                if not moved:
                    D['could_stay'] += 1
                    if not A:
                        D['idle'] += 1
                        if not near_t: D['idle_free'] += 1
                        if ppaint * 2 < cap: D['idle_low'] += 1
            if ppaint == 0: D['zero'] += 1
            if ppaint * 2 < cap: D['low'] += 1
            # action tax (soldier attack / paint, splasher splash)
            base = None
            if 'transfer' in A: base = None   # a transfer adds its own cooldown: left out
            elif typ == 'SOLDIER' and ('attack' in A or 'paint' in A): base = 10
            elif typ == 'SPLASHER' and 'splash' in A: base = 50
            elif typ == 'MOPPER' and ('unpaint' in A or 'drain' in A or 'mop' in A): base = 30
            if base is not None and sacd < 10:
                tax = acd - sacd - base
                D['acts'] += 1
                if tax > 0: D['atax'] += tax / base * 10   # in units of a 10-cooldown turn
            win.append((x, y, moved))
            if len(win) > 10: win.pop(0)
            if len(win) == 10 and sum(1 for w in win if w[2]) >= 6 and len(set((w[0], w[1]) for w in win)) <= 3:
                D['stuck'] += 1


for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); ng = 0
    for G in lib.games(which):
        run(G, S); ng += 1
    print(f'== {which} games: {ng}; per 100 robot-turns (moves lost / acts lost = tax / 10)')
    print('   type     phase     side  robot-turns  moves  rev siege/tower/free  could-move  stayed  idle (free, low paint)  stuck  below 50%  at 0   moves lost  taxed moves  acts lost')
    for typ in lib.BOT:
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, typ, p)]
                n = D['turns']
                if not n: continue
                f = 100 / n
                print(f'   {typ:8s} {PHN[p]:9s} {side:4s} {int(n):11d}  {f * D["moves"]:5.1f}  {f * D["rev_siege"]:4.1f}/{f * D["rev_tower"]:4.1f}/{f * D["rev_free"]:4.1f}'
                      f'     {f * D["could"]:6.1f}  {f * D["could_stay"]:6.1f}  {f * D["idle"]:5.1f} ({f * D["idle_free"]:4.1f}, {f * D["idle_low"]:4.1f})'
                      f'          {f * D["stuck"]:5.1f}  {f * D["low"]:8.1f}  {f * D["zero"]:5.1f}   {f * D["mtax"] / 10:8.1f}  {100 * D["taxed_moves"] / max(1, D["moves"]):6.1f}% of moves  {f * D["atax"] / 10:6.1f}  (per 100 actions {100 * D["atax"] / 10 / max(1, D["acts"]):5.1f})')
    # free reversals per 100 MOVES (the nav signature)
    print('   free reversals per 100 moves (A-B-A, not siege, not beside an own tower):')
    for typ in lib.BOT:
        cells = []
        for p in range(3):
            for side in ('us', 'them'):
                D = S[(side, typ, p)]
                cells.append(f'{side} {100 * D["rev_free"] / max(1, D["moves"]):4.1f}')
        print(f'      {typ:8s} ' + ' | '.join(f'{PHN[p]}: {cells[2 * p]} {cells[2 * p + 1]}' for p in range(3)))

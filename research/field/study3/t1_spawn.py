"""Topic 1: spawning policy of the top teams. First 25 spawns per game with tower type/paint/chips; phase mix;
reserve analysis (tower turns where a spawn was affordable but none happened); mopper/splasher triggers."""
import lib, sys
from collections import Counter, defaultdict
VERB = '-v' in sys.argv
pool = defaultdict(lambda: defaultdict(list))
mix = defaultdict(Counter)
CB = defaultdict(lambda: [0, 0])
for G in lib.games():
    b, d = lib.tower_events(G)
    born = {x[1]: x[0] for x in b}
    tp = {}  # (round, tower id) -> end-of-turn paint
    for t in G.turns:
        if t[3] in lib.TOW: tp[(t[0], t[1])] = t[7]
    rt = lib.by_round_turns(G)
    sp = [a for a in G.acts if a[4] == 'spawn' and a[6] in lib.BOT and a[2] == G.op]
    spawned_turn = set((a[0], a[1]) for a in sp)
    tn = G.team_name
    rows = []
    for i, a in enumerate(sp):
        r, tid, ty = a[0], a[1], a[6]
        pb = tp.get((r, tid), 0) + lib.COST[ty][0]
        ch = lib.money(G, G.op, r - 1)
        # nearest enemy robot to the tower that round
        tx = [t for t in rt[r] if t[1] == tid]
        near = None
        if tx:
            ds = [lib.d2((t[4], t[5]), (tx[0][4], tx[0][5])) for t in rt[r - 1] if t[2] == G.us and t[3] in lib.BOT]
            near = min(ds) if ds else 999
        rows.append((r, {'SOLDIER':'S','SPLASHER':'X','MOPPER':'M'}[ty], G.typ[tid][:2], pb, ch, near, r - born.get(tid, 0)))
        ph = 'r1-50' if r <= 50 else 'r51-100' if r <= 100 else 'r101-200' if r <= 200 else 'r201+'
        mix[(tn, ph)][ty[:3]] += 1; mix[('ALL', ph)][ty[:3]] += 1
        pool[tn]['paint_after_' + ty[:3]].append(pb - lib.COST[ty][0])
        pool[tn]['paint_before_' + ty[:3]].append(pb)
        pool[tn]['enemy_d2_' + ty[:3]].append(near)
        pool[tn]['tower_age_' + ty[:3]].append(r - born.get(tid, 0))
    first = {k: next((x[0] for x in rows if x[1] == c), None) for k, c in (('SOL', 'S'), ('SPL', 'X'), ('MOP', 'M'))}
    fx = next((x for x in rows if x[1] == 'X'), None)
    if fx: pool[tn]['chips at first splasher'].append(fx[4]); pool[tn]['towers alive at first splasher'].append(len(lib.towers_alive(G, G.op, fx[0], b, d)))
    for k, v in first.items(): pool[tn]['first_' + k].append(v)
    # spawn from freshly built towers (age <= 3)
    pool[tn]['frac spawns from towers aged<=3 rounds'].append(round(sum(1 for x in rows if x[6] <= 3 and x[6] < x[0]) / max(1, len(rows)), 2))
    # reserve: tower turns (paint tower or any) where paint >= 200+X and chips>=250 and no spawn
    idle = Counter(); idleN = 0; tt = 0
    for t in G.turns:
        if t[2] != G.op or t[3] not in lib.TOW or t[0] < 2 or t[0] > 200: continue
        if (t[0], t[1]) in spawned_turn:
            ch = lib.money(G, G.op, t[0] - 1); pb = t[7] + 100
            if t[0] >= 20 and pb >= 200:
                bk = '<500' if ch < 500 else '<1000' if ch < 1000 else '<1250' if ch < 1250 else '<1500' if ch < 1500 else '<2500' if ch < 2500 else '>=2500'
                CB[(tn, bk)][0] += 1; CB[('ALL', bk)][0] += 1
            continue
        tt += 1
        ch = lib.money(G, G.op, t[0] - 1)
        if t[7] >= 200 and ch >= 250 + 0: idleN += 1
        if t[0] >= 20 and t[7] >= 200:
            bk = '<500' if ch < 500 else '<1000' if ch < 1000 else '<1250' if ch < 1250 else '<1500' if ch < 1500 else '<2500' if ch < 2500 else '>=2500'
            CB[(tn, bk)][1] += 1; CB[('ALL', bk)][1] += 1
    pool[tn]['idle tower turns r2-200 with paint>=200 & chips>=250 (frac of non-spawn tower turns)'].append(round(idleN / max(1, tt), 2))
    print(f'== m{G.m} g{G.g} {tn} {G.map} {G.W}x{G.H}  first 25 spawns: (round type tower paintBefore chipsBefore nearestEnemyD2 towerAge)')
    print('  ', ' '.join(f'{x[0]}{x[1]}@{x[2]}:{x[3]}/{x[4]}' for x in rows[:25]))
    if VERB:
        for x in rows[:25]: print('   ', x)
print('\n== spawn mix by phase (counts)')
for k in sorted(mix): print('  ', k, dict(mix[k]), {t: round(v / sum(mix[k].values()), 2) for t, v in mix[k].items()})
print('\n== r20-200 tower turns with paint>=200: spawn rate by chips bucket (spawned, idle, rate)')
for k in sorted(CB): print('  ', k, CB[k], round(CB[k][0] / max(1, sum(CB[k])), 2))
print('\n== per team medians')
for tn, D in pool.items():
    print(' ', tn)
    for k, v in D.items(): print(f'     {k:<70} med {lib.med(v)}  p10 {lib.pct(v, .1)} p90 {lib.pct(v, .9)}  n={len([x for x in v if x is not None])}')

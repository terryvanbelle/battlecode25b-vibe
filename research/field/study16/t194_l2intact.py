"""Topic 194 (new; follows t190): which level-2+ money towers have an intact money pattern when a robot of ours arrives
dry.  t190's visits (its analyse(), loaded from t190_l2churn.py without its report), our soldiers' dry visits at our L2+
money towers; per game and tower: the visits per phase, how many found the pattern intact (every tile ours and right)
and with no enemy robot in view, the tower's start level (a starting tower) or its upgrade round, and the chips then.
Losses and wins of the chosen set (S16SET)."""
import os
from collections import defaultdict
import lib

_src = open(os.path.join(os.path.dirname(os.path.abspath(lib.__file__)), 't190_l2churn.py')).read()
exec(compile(_src.split('\nAGG = ')[0], 't190_l2churn.py', 'exec'))

for res in ('lost', 'won'):
    print(f'\n== {res}')
    tot = defaultdict(int)
    for G in lib.games(res):
        V, EP, rr = analyse(G)
        start = {int(a[5]): int(a[6]) for a in G.acts if a[4] == 'startlevel'}
        upg = defaultdict(list)
        for a in G.acts:
            if a[4] == 'upgrade': upg[int(a[5])].append((a[0], int(a[6])))
        per = defaultdict(lambda: defaultdict(int))
        for v in V:
            if v['side'] != 'us' or v['typ'] != 'SOLDIER' or not v['dry'] or v['kind'] != 'MONEY_TOWER' or v['lvl'] < 2: continue
            j = ph(v['r0'])
            if j is None: continue
            ok = v.get('en', 0) == 0 and v.get('wr', 0) == 0
            per[v['tid']][(j, 'n')] += 1
            if ok: per[v['tid']][(j, 'ok')] += 1
            tot[(j, 'n', 'start' if v['tid'] in start else 'upg')] += 1
            if ok: tot[(j, 'ok', 'start' if v['tid'] in start else 'upg')] += 1
        for tid, d in sorted(per.items()):
            how = f'start L{start[tid]}' if tid in start else 'upgraded ' + ', '.join(f'r{r} to L{l}' for r, l in upg.get(tid, []))
            print(f'   m{G.m}g{G.g} {G.team_name[:12]:12s} {G.map[:14]:14s} tower {tid} ({how}): ' + '  '.join(
                f'{PHN[j]} {d[(j, "ok")]}/{d[(j, "n")]}' for j in range(len(PH)) if d[(j, 'n')]) + '  (intact / visits)')
        G.turns = G.acts = None
    for k in ('start', 'upg'):
        print(f'   {k:5s} towers: ' + '  '.join(f'{PHN[j]} intact {tot[(j, "ok", k)]} of {tot[(j, "n", k)]}' for j in range(len(PH))))

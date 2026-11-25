"""Study 2: siege shape. Episode = hits by one side's soldiers/splashers on one enemy tower with gaps <= 10 rounds.
Reports distinct attackers, max attackers hitting in one round, damage, kill, and what the attackers held in paint
when they last hit (did they run dry?). Usage: python3 -I an8.py [DUMPDIR] [study2|study1]."""
import json, csv, os, sys, statistics as st
from collections import defaultdict, Counter
S = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else S
GR = {'study2': (([608, 609, 610, 611], 'LOST'), ([642, 593, 546, 521], 'WON')),
      'study1': (([8, 9, 10, 11, 13, 27, 28], 'LOST'), ([12, 14, 6, 7], 'WON'))}[sys.argv[2] if len(sys.argv) > 2 else 'study2']
TOW = {'PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER'}
def rd(p):
    with open(p) as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); return [dict(zip(h, x)) for x in r]
def med(x):
    x = [v for v in x if v is not None]; return round(st.median(x), 1) if x else '-'
for grp, name in GR:
    E = defaultdict(list)
    for m in grp:
        for g in range(3):
            d = f'{D}/m{m}'; sm = json.load(open(f'{d}/g{g}.summary.json'))
            us = 1 if sm['teamA'] == 'vibe25b' else 2
            acts = rd(f'{d}/g{g}.actions.tsv'); turns = rd(f'{d}/g{g}.turns.tsv')
            team = {}; typ = {}; paint = {}
            for t in turns: team[t['id']] = int(t['team']); typ[t['id']] = t['type']; paint[(t['id'], int(t['round']))] = int(t['paint'])
            hits = defaultdict(list); died = {}
            for a in acts:
                r = int(a['round'])
                if a['action'] == 'damage' and a['type'] in ('SOLDIER', 'SPLASHER') and typ.get(a['a']) in TOW and team.get(a['a']) != int(a['team']):
                    hits[a['a']].append((r, a['id'], int(a['b'])))
                if a['action'] == 'die': died.setdefault(a['a'], r)
            for vid, L in hits.items():
                k = 'us' if team[vid] != us else 'op'
                L.sort(); eps = [[L[0]]]
                for h in L[1:]:
                    if h[0] - eps[-1][-1][0] <= 10: eps[-1].append(h)
                    else: eps.append([h])
                for ep in eps:
                    s, e = ep[0][0], ep[-1][0]
                    ids = {h[1] for h in ep}; per = Counter(h[0] for h in ep)
                    kill = vid in died and s <= died[vid] <= e + 3
                    lastp = [paint.get((i, max(h[0] for h in ep if h[1] == i)), None) for i in ids]
                    dry = sum(1 for p in lastp if p is not None and p < 10)
                    attdied = sum(1 for i in ids if i in died and s <= died[i] <= e + 10)
                    E[k].append((len(ids), max(per.values()), sum(h[2] for h in ep), kill, dry, attdied, e - s + 1))
    print('==', name)
    for k in ('us', 'op'):
        L = E[k]; K = [x for x in L if x[3]]; N = [x for x in L if not x[3]]
        print(f"  {k}: episodes {len(L)}, killed {len(K)} ({round(len(K)/max(1,len(L)),2)})")
        for lab, LL in (('killing', K), ('failed', N)):
            if not LL: continue
            print(f"    {lab:<8} n={len(LL):<4} med attackers {med([x[0] for x in LL])}, med max-simultaneous {med([x[1] for x in LL])}, "
                  f"med dmg {med([x[2] for x in LL])}, med length {med([x[6] for x in LL])}, attackers <10 paint at last hit {sum(x[4] for x in LL)}/{sum(x[0] for x in LL)}, "
                  f"attackers dead within 10r {sum(x[5] for x in LL)}/{sum(x[0] for x in LL)}")
        print(f"    episodes with 1 attacker: {sum(1 for x in L if x[0]==1)}, >=3 attackers: {sum(1 for x in L if x[0]>=3)} (kill rate {round(sum(1 for x in L if x[0]>=3 and x[3])/max(1,sum(1 for x in L if x[0]>=3)),2)})")

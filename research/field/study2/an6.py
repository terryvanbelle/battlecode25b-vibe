"""Study 2 extras: spawns by type over time, sieges (soldier/splasher attacks on enemy towers and whether they
kill), death causes (killer type, 0 paint), tower counts alive, moppers near our towers when they fall,
loss timing.  Usage: python3 -I an6.py [DUMPDIR] [study2|study1]  (default: this folder, study2 groups)."""
import json, csv, os, sys, statistics as st
from collections import Counter, defaultdict
S = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else S
GR = {'study2': (([608, 609, 610, 611], 'LOST'), ([642, 593, 546, 521], 'WON')),
      'study1': (([8, 9, 10, 11, 13, 27, 28], 'LOST'), ([12, 14, 6, 7], 'WON'))}[sys.argv[2] if len(sys.argv) > 2 else 'study2']
TOW = {'PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER'}
BOT = ('SOLDIER', 'SPLASHER', 'MOPPER')


def rd(p):
    with open(p) as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); return [dict(zip(h, x)) for x in r]


def med(x):
    x = [v for v in x if v is not None]; return round(st.median(x), 1) if x else '-'


for grp, name in GR:
    A = defaultdict(lambda: defaultdict(list)); per = []
    for m in grp:
        for g in range(3):
            d = f'{D}/m{m}'
            if not os.path.exists(f'{d}/g{g}.summary.json'): continue
            sm = json.load(open(f'{d}/g{g}.summary.json'))
            us = 1 if sm['teamA'] == 'vibe25b' else 2
            win = sm['winner'] == ('A' if us == 1 else 'B')
            acts = rd(f'{d}/g{g}.actions.tsv'); turns = rd(f'{d}/g{g}.turns.tsv'); rounds = rd(f'{d}/g{g}.rounds.tsv')
            team = {}; typ = {}
            for t in turns: team[t['id']] = int(t['team']); typ[t['id']] = t['type']
            for a in acts:
                if a['action'] == 'spawn': team[a['a']] = int(a['team']); typ[a['a']] = a['b']
            # per-robot positions by round (for mopper-near-tower)
            pos = defaultdict(dict)
            lastrec = {}
            for t in turns:
                pos[int(t['round'])][t['id']] = (int(t['x']), int(t['y']))
                lastrec[t['id']] = t
            spawnb = defaultdict(Counter)
            att = Counter(); attT = defaultdict(set); tdmg = Counter(); hits = defaultdict(list)
            cause = defaultdict(Counter); zero = defaultdict(Counter)
            tkill = defaultdict(list); tdie = defaultdict(list)
            for a in acts:
                r = int(a['round']); tm = int(a['team']); k = a['action']
                if k == 'spawn' and a['b'] in BOT:
                    spawnb[tm][(min(r // 100, 4), a['b'])] += 1
                elif k == 'attack' and a['type'] in ('SOLDIER',) and typ.get(a['a']) in TOW and team.get(a['a']) != tm:
                    att[tm] += 1; attT[tm].add(a['a'])
                elif k == 'damage' and a['type'] in ('SOLDIER', 'SPLASHER') and typ.get(a['a']) in TOW and team.get(a['a']) != tm:
                    tdmg[tm] += int(a['b']); hits[a['a']].append(r)
                elif k == 'die':
                    vid, vt = a['a'], a['c']
                    vtm = team.get(vid)
                    if vtm is None: continue
                    if vt in TOW:
                        tdie[vtm].append((r, vid))
                        if a['type'] in BOT and tm != vtm: tkill[tm].append(r)
                    elif vt in BOT:
                        kt = 'EXC' if a['b'] == 'EXCEPTION' else ('self' if a['id'] == vid else ('tower' if a['type'] in TOW else a['type']))
                        cause[vtm][(vt, kt)] += 1
                        lr = lastrec.get(vid)
                        if lr and int(lr['paint']) == 0: zero[vtm][vt] += 1
            # sieges: an enemy tower hit by side t; episode = hits with gaps <= 10 rounds
            sieges = Counter(); siegekill = Counter()
            for vid, L in hits.items():
                atk = 3 - team[vid]
                L.sort(); eps = [[L[0], L[0]]]
                for r in L[1:]:
                    if r - eps[-1][1] <= 10: eps[-1][1] = r
                    else: eps.append([r, r])
                dr = [x for x, v in tdie[team[vid]] if v == vid]
                for s, e in eps:
                    sieges[atk] += 1
                    if dr and s <= dr[0] <= e + 3: siegekill[atk] += 1
            end = len(rounds)
            for side in (1, 2):
                k = 'us' if side == us else 'op'
                T = 'A' if side == 1 else 'B'
                for b in range(4):
                    for ty in BOT:
                        if b * 100 < end: A[f'spawn {ty[:3]} r{b*100}-{b*100+99}'][k].append(spawnb[side][(b, ty)])
                A['soldier attacks on enemy towers'][k].append(att[side])
                A['distinct enemy towers attacked'][k].append(len(attT[side]))
                A['dmg to enemy towers (sol+spl)'][k].append(tdmg[side])
                A['siege episodes'][k].append(sieges[side])
                A['siege episodes that killed'][k].append(siegekill[side])
                A['enemy towers killed'][k].append(len(tkill[side]))
                A['enemy towers killed <=200'][k].append(sum(1 for r in tkill[side] if r <= 200))
                c = cause[side]
                A['robot deaths: by tower'][k].append(sum(v for (vt, kt), v in c.items() if kt == 'tower'))
                A['robot deaths: self (no killer)'][k].append(sum(v for (vt, kt), v in c.items() if kt == 'self'))
                A['robot deaths: exception'][k].append(sum(v for (vt, kt), v in c.items() if kt == 'EXC'))
                for ty in BOT:
                    A[f'{ty[:3]} deaths (at 0 paint)'][k].append(f"{sum(v for (vt, kt), v in c.items() if vt == ty)}({zero[side][ty]})")
                A['towers alive r100'][k].append(sum(int(rounds[min(100, end) - 1][f'{x}{T}']) for x in ('pt', 'mt', 'dt')))
                A['towers alive r200'][k].append(sum(int(rounds[min(200, end) - 1][f'{x}{T}']) for x in ('pt', 'mt', 'dt')) if end >= 200 else None)
                A['towers lost <=100'][k].append(sum(1 for r, v in tdie[side] if r <= 100))
                A['towers lost <=200'][k].append(sum(1 for r, v in tdie[side] if r <= 200))
                A['moppers alive r100'][k].append(int(rounds[min(100, end) - 1]['mop' + T]))
                A['moppers alive r200'][k].append(int(rounds[199]['mop' + T]) if end >= 200 else None)
                # our moppers within dist^2<=20 of our tower when it dies
                near = []
                for r, vid in tdie[side]:
                    tp = None
                    for rr in range(r, max(0, r - 5), -1):
                        if vid in pos[rr]: tp = pos[rr][vid]; break
                    if tp is None: continue
                    n = sum(1 for i, p in pos[r - 1].items() if team.get(i) == side and typ.get(i) == 'MOPPER' and (p[0] - tp[0]) ** 2 + (p[1] - tp[1]) ** 2 <= 20)
                    near.append(n)
                A['own moppers within r^2 20 of a falling tower (mean)'][k].append(round(st.mean(near), 2) if near else None)
                cov = [int(x['cov' + T]) for x in rounds]
                A['peak coverage round'][k].append(cov.index(max(cov)) + 1)
                A['peak coverage'][k].append(max(cov))
            per.append((m, g, sm['map'], 'W' if win else 'L', sm['winType'], sm['rounds'],
                        [r for r, v in tdie[us]], [r for r, v in tdie[3 - us]], att[us], sieges[us], siegekill[us]))
    print('==', name)
    for kk, v in A.items():
        if 'paint)' in kk:
            print(f"{kk:<52} us {v['us']}\n{'':<52} op {v['op']}")
        else:
            print(f"{kk:<52} us {med(v['us']):>7} op {med(v.get('op', [])):>7}  us{v['us']} op{v.get('op')}")
    print('per game: m g map W/L wintype rounds | our towers lost (rounds) | enemy towers lost | our sol attacks on towers, sieges, sieges that killed')
    for p in per: print(' ', *p)

import json, csv, sys, os, statistics as st
from collections import defaultdict, Counter
S = os.path.dirname(os.path.abspath(__file__))
DUMP = os.environ.get('DUMP', S)  # ReplayDump tsv output dirs m<match>/
US = 'vibe25b'
LOST = [608, 609, 610, 611]
WON = [642, 593, 546, 521]
CK = [50, 100, 150, 200, 300, 500]
TOW = {'PAINT_TOWER', 'MONEY_TOWER', 'DEFENSE_TOWER'}


def rd(p):
    with open(p) as f:
        r = csv.reader(f, delimiter='\t')
        h = next(r)
        return [dict(zip(h, x)) for x in r]


def game(m, g):
    d = f'{DUMP}/m{m}'
    summ = json.load(open(f'{d}/g{g}.summary.json'))
    meta = json.load(open(f'{d}/g{g}.meta.json'))
    W, H = meta['width'], meta['height']
    us = 1 if summ['teamA'] == US else 2
    op = 3 - us
    opn = summ['teamB'] if us == 1 else summ['teamA']
    rounds = rd(f'{d}/g{g}.rounds.tsv')
    acts = rd(f'{d}/g{g}.actions.tsv')
    turns = rd(f'{d}/g{g}.turns.tsv')
    L = 'A' if True else ''
    res = {'m': m, 'g': g, 'map': meta['map'], 'W': W, 'H': H, 'opp': opn, 'rounds': summ['rounds'], 'win': (summ['winner'] == ('A' if us == 1 else 'B')), 'wintype': summ['winType']}
    T = {1: 'A', 2: 'B'}
    end = int(rounds[-1]['round'])

    def snap(r):
        row = rounds[min(r, end) - 1]
        o = {}
        for t in (1, 2):
            s = T[t]
            o[t] = dict(cov=int(row['cov' + s]), money=int(row['money' + s]), srp=int(row['srp' + s]),
                        sol=int(row['sol' + s]), spl=int(row['spl' + s]), mop=int(row['mop' + s]),
                        pt=int(row['pt' + s]), mt=int(row['mt' + s]), dt=int(row['dt' + s]), upaint=int(row['paint' + s]))
        return o
    res['snap'] = {r: snap(r) for r in CK if r <= end}
    res['snap']['end'] = snap(end)
    # id info
    team = {}; typ = {}
    for t in turns:
        team[t['id']] = int(t['team']); typ[t['id']] = t['type']
    spawn = defaultdict(list); spawnc = defaultdict(Counter)
    srp = defaultdict(list); upg = defaultdict(list); unpaint = Counter(); paintact = defaultdict(Counter)
    dmg_to = defaultdict(list)  # target id -> (round, attacker type, attacker team, dmg)
    deaths = []
    built = defaultdict(list)
    marks = Counter()
    transfers_out = Counter()
    for a in acts:
        r = int(a['round']); tm = int(a['team']); k = a['action']
        if k == 'spawn':
            spawn[tm].append((r, a['b'])); spawnc[tm][a['b']] += 1
            team[a['a']] = tm; typ[a['a']] = a['b']
        elif k == 'srp': srp[tm].append(r)
        elif k == 'upgrade' and r > 1: upg[team.get(a['a'], tm)].append((r, typ.get(a['a']), a['b']))
        elif k == 'unpaint' and a['type'] == 'MOPPER': unpaint[tm] += 1
        elif k == 'damage':
            dmg_to[a['a']].append((r, a['type'], tm, int(a['b'])))
        elif k == 'die': deaths.append((r, a['a'], a['c']))
        elif k == 'build': built[tm].append((r, a['b']))
        elif k == 'mark': marks[tm] += 1
        if a['type'] in ('SOLDIER', 'SPLASHER', 'MOPPER') and k in ('paint', 'attack', 'splash', 'mop', 'unpaint'):
            paintact[(tm, a['type'])][k] += 1
    # last paint before death
    last = {}
    for t in turns: last[t['id']] = (int(t['round']), int(t['paint']), int(t['hp']))
    res['spawn'] = {t: dict(spawnc[t]) for t in (1, 2)}
    res['open'] = {t: [x[1][:3] for x in spawn[t][:10]] for t in (1, 2)}
    res['srp_first'] = {t: (srp[t][0] if srp[t] else None) for t in (1, 2)}
    res['srp_n'] = {t: len(srp[t]) for t in (1, 2)}
    res['srp_by200'] = {t: sum(1 for x in srp[t] if x <= 200) for t in (1, 2)}
    res['upg'] = {t: upg[t] for t in (1, 2)}
    res['built'] = {t: built[t] for t in (1, 2)}
    res['first_build'] = {t: (built[t][0][0] if built[t] else None) for t in (1, 2)}
    res['built_by'] = {t: {r: sum(1 for x in built[t] if x[0] <= r) for r in (100, 200, 300)} for t in (1, 2)}
    res['unpaint'] = dict(unpaint)
    res['pa'] = {f'{t}{k[0:3]}': dict(v) for (t, k), v in paintact.items()}
    res['marks'] = dict(marks)
    # deaths
    tdeath = defaultdict(list); zero = Counter(); died = Counter()
    for r, vid, vt in deaths:
        vtm = team.get(vid)
        if vtm is None: continue
        if vt in TOW:
            killers = Counter()
            for (dr, at, atm, dd) in dmg_to.get(vid, []):
                if atm != vtm and dr >= r - 40: killers[at] += dd
            tdeath[vtm].append((r, vt[:2], dict(killers)))
        else:
            died[vtm] += 1
            lp = last.get(vid)
            if lp and lp[1] == 0: zero[vtm] += 1
    res['tdeath'] = {t: tdeath[t] for t in (1, 2)}
    res['zero'] = dict(zero); res['died'] = dict(died)
    # rush: enemy robots within r2<=64 of initial towers of team t in rounds<=100
    init = defaultdict(list)
    for t in turns:
        if t['round'] == '1' and t['type'] in TOW: init[int(t['team'])].append((int(t['x']), int(t['y'])))
    rush = {}; rushfirst = {}
    for t in (1, 2):
        ids = set(); first = None; urounds = 0
        for x in turns:
            r = int(x['round'])
            if r > 100: break
            if int(x['team']) == 3 - t and x['type'] not in TOW:
                px, py = int(x['x']), int(x['y'])
                if any((px - a) ** 2 + (py - b) ** 2 <= 64 for a, b in init[t]):
                    ids.add(x['id']); urounds += 1
                    if first is None: first = r
        rush[t] = (len(ids), urounds, first)
    res['rush'] = rush
    res['init'] = dict(init)
    # tower damage taken in first 150 by team
    res['tdmg150'] = {}
    for t in (1, 2):
        s = Counter()
        for vid, L in dmg_to.items():
            if team.get(vid) == t and typ.get(vid) in TOW:
                for (dr, at, atm, dd) in L:
                    if dr <= 150 and atm != t: s[at] += dd
        res['tdmg150'][t] = dict(s)
    # territory: paint ownership replay
    own = {}
    terr = {}
    cx, cy = (W - 1) / 2, (H - 1) / 2
    ai = 0
    acts_paint = [(int(a['round']), int(a['team']), a['action'], a['a']) for a in acts if a['action'] in ('paint', 'unpaint')]
    for R in (50, 100, 200, 400):
        while ai < len(acts_paint) and acts_paint[ai][0] <= R:
            r, tm, k, loc = acts_paint[ai]; ai += 1
            if k == 'paint': own[loc] = tm
            else: own.pop(loc, None)
        o = {}
        for t in (1, 2):
            pts = [tuple(map(int, l.split(','))) for l, v in own.items() if v == t]
            if not pts: o[t] = None; continue
            sx, sy = st.mean(a for a, b in init[t]), st.mean(b for a, b in init[t])
            dspawn = st.median(((a - sx) ** 2 + (b - sy) ** 2) ** .5 for a, b in pts)
            dcen = st.median(((a - cx) ** 2 + (b - cy) ** 2) ** .5 for a, b in pts)
            # fraction of tiles closer to own spawn than enemy spawn
            ex, ey = st.mean(a for a, b in init[3 - t]), st.mean(b for a, b in init[3 - t])
            near = sum(1 for a, b in pts if (a - sx) ** 2 + (b - sy) ** 2 <= (a - ex) ** 2 + (b - ey) ** 2) / len(pts)
            o[t] = (len(pts), round(dspawn, 1), round(dcen, 1), round(near, 2))
        terr[R] = o
    res['terr'] = terr
    res['us'] = us
    return res


out = []
for m in LOST + WON:
    for g in range(3):
        try:
            out.append(game(m, g))
        except Exception as e:
            print('ERR', m, g, e, file=sys.stderr)
json.dump(out, open(f'{S}/res.json', 'w'), default=str)
print(len(out))

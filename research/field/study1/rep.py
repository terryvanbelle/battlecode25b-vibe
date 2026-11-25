import json, statistics as st, os, sys
S = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(f'{S}/res.json'))
LOST = {8, 9, 10, 11, 13, 27, 28}
def k(t): return str(t)
def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else '-'

for grp, name in ((LOST, 'LOST matches (strong field)'), ({12, 14, 6, 7}, 'WON matches')):
    G = [g for g in R if g['m'] in grp]
    print('=====', name, len(G), 'games')
    print('per game: m g map opp rounds win wintype')
    for g in G:
        u, o = k(g['us']), k(3 - g['us'])
        print(f"{g['m']:>2} {g['g']} {g['map']:<13} {g['opp']:<15} {g['rounds']:>4} {'W' if g['win'] else 'L'} {g['wintype']:<20} {g['W']}x{g['H']}")
    print('snapshot medians  us | opp   (n games reaching round)')
    for R_ in ['50', '100', '150', '200', '300', '500', 'end']:
        rows = [g for g in G if R_ in g['snap']]
        if not rows: continue
        line = f"r{R_:<4} n={len(rows):<2}"
        for f in ['cov', 'money', 'srp', 'pt', 'mt', 'dt', 'sol', 'spl', 'mop', 'upaint']:
            a = med([g['snap'][R_][k(g['us'])][f] for g in rows]); b = med([g['snap'][R_][k(3 - g['us'])][f] for g in rows])
            line += f" {f}:{a}|{b}"
        print(line)
    def both(fn, label):
        a = [fn(g, k(g['us'])) for g in G]; b = [fn(g, k(3 - g['us'])) for g in G]
        print(f"{label:<28} us med {med(a):>7}  opp med {med(b):>7}   us:{a}\n{'':<28} opp:{b}")
    both(lambda g, t: g['srp_first'][t], 'first SRP round')
    both(lambda g, t: g['srp_n'][t], 'SRP completions total')
    both(lambda g, t: g['srp_by200'][t], 'SRP completions <=200')
    both(lambda g, t: g['first_build'][t], 'first tower build round')
    both(lambda g, t: g['built_by'][t]['100'], 'towers built by 100')
    both(lambda g, t: g['built_by'][t]['200'], 'towers built by 200')
    both(lambda g, t: len(g['upg'][t]), 'upgrades')
    both(lambda g, t: (g['upg'][t][0][0] if g['upg'][t] else None), 'first upgrade round')
    both(lambda g, t: sum(g['spawn'][t].get(x, 0) for x in ('SOLDIER', 'SPLASHER', 'MOPPER')), 'robots spawned')
    for ty in ('SOLDIER', 'SPLASHER', 'MOPPER'):
        both(lambda g, t, ty=ty: g['spawn'][t].get(ty, 0), 'spawned ' + ty)
    both(lambda g, t: len(g['tdeath'][t]), 'towers lost')
    both(lambda g, t: g['unpaint'].get(t, 0), 'mopper unpaint (enemy paint mopped)')
    both(lambda g, t: g['died'].get(t, 0), 'robots died')
    both(lambda g, t: g['zero'].get(t, 0), 'robots died at 0 paint')
    both(lambda g, t: g['marks'].get(t, 0), 'mark actions')
    def frac(g, t, ty, kk):
        d = g['pa'].get(t + ty[:3], {})
        s = sum(d.values())
        return round(d.get(kk, 0) / s, 2) if s else None
    both(lambda g, t: frac(g, t, 'SOLDIER', 'attack'), 'soldier attack frac')
    both(lambda g, t: g['pa'].get(t + 'SOL', {}).get('attack', 0), 'soldier attacks n')
    both(lambda g, t: g['pa'].get(t + 'SOL', {}).get('paint', 0), 'soldier paints n')
    both(lambda g, t: g['pa'].get(t + 'SPL', {}).get('splash', 0), 'splashes n')
    both(lambda g, t: g['pa'].get(t + 'MOP', {}).get('mop', 0), 'mop swings/attacks n')
    # rush: enemy near t's towers
    both(lambda g, t: g['rush'][t][0], 'enemy units near MY towers<=100')
    both(lambda g, t: g['rush'][t][2], 'first enemy near MY towers')
    both(lambda g, t: sum(g['tdmg150'][t].values()), 'dmg taken by my towers<=150')
    print('tower deaths (victim side: round, type, killers dmg by type):')
    for g in G:
        print(' ', g['m'], g['g'], 'us lost:', g['tdeath'][k(g['us'])], ' opp lost:', g['tdeath'][k(3 - g['us'])])
    print('opening (first 10 spawns):')
    for g in G:
        print(' ', g['m'], g['g'], 'us:', ' '.join(g['open'][k(g['us'])]), ' | opp:', ' '.join(g['open'][k(3 - g['us'])]))
    print('upgrades:')
    for g in G:
        print(' ', g['m'], g['g'], 'us:', g['upg'][k(g['us'])][:6], '| opp:', g['upg'][k(3 - g['us'])][:6])
    print('territory (n tiles, med dist to own spawn, med dist to center, frac on own half):')
    for R_ in ('100', '200'):
        for g in G:
            tr = g['terr'][R_]
            print(f"  r{R_} {g['m']} {g['g']} us {tr[k(g['us'])]}  opp {tr[k(3 - g['us'])]}")

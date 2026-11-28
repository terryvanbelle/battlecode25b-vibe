"""Topic 143: what each side's units do, per 100 unit-turns (new: the whole action repertoire side by side, with the
tile each paint row lands on).  Replays the paint grid (lib.replay_grid hook: the tile's state BEFORE each row).
Per side, unit type and phase, losses then wins:
  SOLDIER   tower hits; paint rows on a neutral tile (new coverage) / on an own tile (re-colour: a pattern fix);
            single marks (turns with < 20 mark rows) and pattern marks (20+ rows in a turn), unmarks;
            withdrawals from towers (count, paint, trickles under 10), paint given (to towers / to robots);
            tower upgrades done by the robot; towers completed; SRPs completed; robots killed
  SPLASHER  splashes, and per splash the tiles it turned: neutral -> own, enemy -> own, own re-coloured; splashes
            that changed nothing ('empty'); tower hits; withdrawals; paint given
  MOPPER    tiles mopped (unpaint), single-target drains, swings and swing victims; paint given to robots / towers;
            withdrawals; towers completed
  TOWERS    spawns by type, attacks (rows), upgrades (by the tower itself)
  all       disintegrations (died rows) per 100 unit-turns of that type
Also, per game: towers completed by moppers or splashers, towers disintegrated (towers removed) and robots
disintegrated, us against them."""
from collections import defaultdict
import lib

PH = ((1, 100), (101, 200), (201, 2000))
PHN = ('r1-100', 'r101-200', 'r201+')


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return None


def run(G, S, P):
    nturn = defaultdict(int)
    for t in G.turns:
        p = ph(t[0])
        if p is None: continue
        side = 'us' if t[2] == G.us else 'them'
        typ = t[3] if t[3] in lib.BOT else 'TOWER'
        nturn[(side, typ, p)] += 1
    for k, v in nturn.items(): S[k]['turns'] += v
    marks = defaultdict(int)
    for a in G.acts:
        if a[4] == 'mark': marks[(a[0], a[1])] += 1
    splash_turn = {}

    def hook(a, grid):
        r, i, team, typ, k = a[0], a[1], a[2], a[3], a[4]
        p = ph(r)
        if p is None: return
        side = 'us' if team == G.us else 'them'
        T = typ if typ in lib.BOT else 'TOWER'
        D = S[(side, T, p)]
        if k == 'paint':
            x, y = map(int, a[5].split(','))
            o = lib.owner(grid[x + y * G.W])
            st = 'neutral' if o == 0 else 'own' if o == team else 'enemy'
            D['paint_' + st] += 1
            if T == 'SPLASHER':
                key = (r, i)
                splash_turn.setdefault(key, defaultdict(int))[st] += 1
        elif k == 'splash':
            D['splash'] += 1
            splash_turn.setdefault((r, i), defaultdict(int))
        elif k == 'attack':
            tt = G.typ.get(int(a[5]))
            if tt in lib.TOW: D['hit_tower'] += 1
            else: D['hit_robot'] += 1
        elif k == 'mark':
            if marks[(r, i)] >= 20: D['pattern_mark'] += 1 / marks[(r, i)]   # one per pattern mark
            else: D['single_mark'] += 1
        elif k == 'unmark': D['unmark'] += 1
        elif k == 'transfer':
            amt = int(a[6] or 0); tgt = G.typ.get(int(a[5])) if a[5] else None
            if amt < 0:
                D['withdraw'] += 1; D['withdraw_paint'] += -amt
                if -amt < 10: D['trickle'] += 1
            elif amt > 0:
                if tgt in lib.TOW: D['give_tower'] += 1; D['give_tower_paint'] += amt
                else: D['give_robot'] += 1; D['give_robot_paint'] += amt
        elif k == 'upgrade':
            if T == 'TOWER': D['upgrade_self'] += 1
            else: D['upgrade_by_robot'] += 1
        elif k == 'build':
            D['build'] += 1
            P[(side, 'built_by_' + T)] += 1
        elif k == 'srp': D['srp'] += 1
        elif k == 'die':
            if a[6] != 'EXCEPTION' and int(a[5]) != i: D['kill'] += 1
        elif k == 'died':
            D['disintegrate'] += 1
            P[(side, 'disintegrated_' + (T if T != 'TOWER' else 'tower'))] += 1
        elif k == 'unpaint': D['unpaint'] += 1
        elif k == 'drain':
            if a[6] == '10': D['drain'] += 1
            else: D['swing_victim'] += 1
        elif k == 'mop': D['swing'] += 0.5   # a swing writes two mop rows
        elif k == 'spawn' and T == 'TOWER':
            D['spawn_' + a[6]] += 1

    lib.replay_grid(G, hook)
    for (r, i), c in splash_turn.items():
        p = ph(r)
        side = 'us' if G.team.get(i) == G.us else 'them'
        D = S[(side, 'SPLASHER', p)]
        tot = sum(c.values())
        if tot == 0: D['splash_empty'] += 1
        elif c['neutral'] + c['enemy'] == 0: D['splash_recolour_only'] += 1
        D['splash_tiles'] += tot
    P['games'] += 1


ROWS = {
    'SOLDIER': [('hit_tower', 'tower hits'), ('paint_neutral', 'paint on neutral'), ('paint_own', 'paint on own (recolour)'),
                ('paint_enemy', 'paint on enemy (impossible)'), ('single_mark', 'single marks'), ('pattern_mark', 'pattern marks (25 paint)'),
                ('unmark', 'unmarks'), ('withdraw', 'withdrawals'), ('withdraw_paint', 'paint withdrawn'), ('trickle', 'trickles < 10'),
                ('give_tower_paint', 'paint given to towers'), ('give_robot_paint', 'paint given to robots'),
                ('upgrade_by_robot', 'upgrades done by the robot'), ('build', 'towers completed'), ('srp', 'SRPs completed'),
                ('kill', 'kills'), ('disintegrate', 'disintegrations')],
    'SPLASHER': [('splash', 'splashes'), ('splash_tiles', 'tiles painted'), ('paint_neutral', 'tiles neutral -> own'),
                 ('paint_enemy', 'tiles enemy -> own'), ('paint_own', 'own tiles re-coloured'), ('splash_empty', 'splashes changing nothing'),
                 ('splash_recolour_only', 'splashes only re-colouring'), ('hit_tower', 'tower hits'),
                 ('withdraw', 'withdrawals'), ('withdraw_paint', 'paint withdrawn'), ('give_tower_paint', 'paint given to towers'),
                 ('give_robot_paint', 'paint given to robots'), ('upgrade_by_robot', 'upgrades done'), ('build', 'towers completed'),
                 ('srp', 'SRPs completed'), ('kill', 'kills'), ('disintegrate', 'disintegrations')],
    'MOPPER': [('unpaint', 'tiles mopped'), ('drain', 'single drains (10)'), ('hit_robot', 'attack rows on robots'), ('swing', 'swings'),
               ('swing_victim', 'swing victims (5 each)'), ('give_robot', 'gives to robots'), ('give_robot_paint', 'paint given to robots'),
               ('give_tower_paint', 'paint given to towers'), ('withdraw', 'withdrawals'), ('withdraw_paint', 'paint withdrawn'),
               ('upgrade_by_robot', 'upgrades done'), ('build', 'towers completed'), ('srp', 'SRPs completed'), ('kill', 'kills'),
               ('disintegrate', 'disintegrations')],
    'TOWER': [('spawn_SOLDIER', 'soldiers spawned'), ('spawn_SPLASHER', 'splashers spawned'), ('spawn_MOPPER', 'moppers spawned'),
              ('hit_robot', 'attack rows'), ('upgrade_self', 'upgrades'), ('kill', 'kills'), ('disintegrate', 'disintegrations')],
}

for which in ('lost', 'won'):
    S = defaultdict(lambda: defaultdict(float)); P = defaultdict(int)
    for G in lib.games(which):
        run(G, S, P)
    print(f'== {which} games: {P["games"]}; per 100 unit-turns of that type (unit-turns in brackets)')
    for typ, rows in ROWS.items():
        hdr = '   ' + f'{typ:36s}' + ''.join(f'{PHN[p] + " us":>12s}{"them":>8s}' for p in range(3))
        print(hdr)
        print('   ' + f'{"(unit-turns)":36s}' + ''.join(f'{int(S[("us", typ, p)]["turns"]):12d}{int(S[("them", typ, p)]["turns"]):8d}' for p in range(3)))
        for k, name in rows:
            cells = ''
            for p in range(3):
                for side in ('us', 'them'):
                    D = S[(side, typ, p)]
                    v = 100 * D[k] / max(1, D['turns'])
                    cells += f'{v:12.2f}' if side == 'us' else f'{v:8.2f}'
            print(f'   {name:36s}' + cells)
    print('   per game, us / them:')
    for k in sorted(set(k[1] for k in P if isinstance(k, tuple))):
        print(f'      {k:32s} {P[("us", k)] / max(1, P["games"]):6.2f} / {P[("them", k)] / max(1, P["games"]):6.2f}')

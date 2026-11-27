"""Topic 106: paint famine.  A tower can only spawn with paint (S 200, X 300, M 100) and only a paint tower makes
paint; money towers start with 500 and never regain it (RULES 7).  Chips cannot buy paint except through a new tower
(500 paint, needs a robot to complete it).  Per side and game, from turns.tsv (towers' end-of-turn paint) and
rounds.tsv:
  nopt     rounds (r20+) with no paint tower standing
  famine   rounds (r20+) where every standing tower of the side holds < 200 paint (no soldier can be spawned)
  dead     rounds where the side has towers but no robot at all
  chips    median chips held in the famine rounds
  lastpt   round the side's last paint tower died (when no paint tower stood again before the end), robots alive then
Lost games split into eliminations and the rest; won games; and per opponent for the losses."""
import lib
from collections import defaultdict


def side_stats(G, side):
    b, d = lib.tower_events(G)
    # tower paint by round (end of turn); a tower missing in a round keeps no entry
    tp = defaultdict(dict)
    for t in G.turns:
        if t[2] == side and t[3] in lib.TOW: tp[t[0]][t[1]] = t[7]
    k = 'A' if side == 1 else 'B'
    nopt = famine = dead = 0; fam_chips = []
    for r in range(20, G.end + 1):
        R = G.rounds[r - 1]
        units = int(R['sol' + k]) + int(R['spl' + k]) + int(R['mop' + k])
        tw = int(R['pt' + k]) + int(R['mt' + k]) + int(R['dt' + k])
        if tw and int(R['pt' + k]) == 0: nopt += 1
        if tw and tp.get(r) and max(tp[r].values()) < 200:
            famine += 1; fam_chips.append(int(R['money' + k]))
        if tw and units == 0: dead += 1
    # last paint tower death with no paint tower again
    pts = [x for x in b if x[3] == side and x[2] == 'PAINT_TOWER']
    deaths = sorted(x[0] for x in d if x[3] == side and x[2] == 'PAINT_TOWER')
    lastpt = None; units_then = None
    if pts and deaths:
        last_build = max(x[0] for x in pts)
        alive_end = [x for x in pts if x[1] not in set(y[1] for y in d)]
        if not alive_end and deaths[-1] >= last_build:
            lastpt = deaths[-1]
            R = G.rounds[min(lastpt, G.end) - 1]
            units_then = int(R['sol' + k]) + int(R['spl' + k]) + int(R['mop' + k])
    return dict(nopt=nopt, famine=famine, dead=dead, chips=lib.med(fam_chips), lastpt=lastpt, units_then=units_then,
                rounds=G.end - 19)


def report(name, pairs):
    """pairs: list of (G-lite, us stats, them stats)."""
    if not pairs: return
    print(f'\n== {name}: {len(pairs)} games')
    U = [p[1] for p in pairs]; T = [p[2] for p in pairs]
    for key, lab in (('nopt', 'rounds without a paint tower'), ('famine', 'rounds every tower < 200 paint'),
                     ('dead', 'rounds with towers but no robot')):
        gu = sum(1 for u in U if u[key] > 0); gt = sum(1 for t in T if t[key] > 0)
        su = sum(u[key] for u in U); st = sum(t[key] for t in T); tot = sum(u['rounds'] for u in U)
        print(f'   {lab:34s} games us {gu:2d} / them {gt:2d};  share of all rounds us {100 * su / tot:4.1f}% / them {100 * st / tot:4.1f}%;'
              f'  median where > 0: us {lib.med([u[key] for u in U if u[key] > 0])} / them {lib.med([t[key] for t in T if t[key] > 0])}')
    print(f'   median chips held in famine rounds: us {lib.med([u["chips"] for u in U if u["famine"] > 0])} / them {lib.med([t["chips"] for t in T if t["famine"] > 0])}')
    lu = [u for u in U if u['lastpt']]; lt = [t for t in T if t['lastpt']]
    print(f'   games where the last paint tower died for good: us {len(lu)} (median r{lib.med([u["lastpt"] for u in lu])}, '
          f'robots alive then {lib.med([u["units_then"] for u in lu])}) / them {len(lt)}')


def collect(which):
    out = []
    for G in lib.games(which):
        u = side_stats(G, G.us); t = side_stats(G, G.op)
        out.append((lib.lite(G), u, t))
    return out


lost = collect('lost')
won = collect('won')
report('eliminations (lost ALL_UNITS_DESTROYED)', [p for p in lost if p[0].wintype.startswith('ALL')])
report('other losses', [p for p in lost if not p[0].wintype.startswith('ALL')])
report('all losses', lost)
report('losses to the top teams', [p for p in lost if p[0].team_name in lib.TOP])
report('won games', won)
print('\nper lost game: us nopt/famine/dead (lastpt r, robots then) | them nopt/famine/dead')
for G, u, t in lost:
    print(f'   m{G.m}g{G.g} {G.ver:5s} {G.team_name[:12]:12s} {G.map[:14]:14s} {G.wintype[:3]}{G.end:<5d} us {u["nopt"]:4d}/{u["famine"]:4d}/{u["dead"]:4d}'
          f' (lastpt {u["lastpt"]}, robots {u["units_then"]}, famine chips {u["chips"]}) | them {t["nopt"]:4d}/{t["famine"]:4d}/{t["dead"]:4d}')

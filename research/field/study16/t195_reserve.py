"""Topic 195 (new; m7565g0: after r69 our last paint tower holds 286-712 paint and we 990 chips, yet it never spawns
again and the game is lost to a single soldier at r207).  Tower.build waits while chips < unit cost + min(reserve,
SPAWN_ANYWAY_CHIPS): from round SPAWN_RESERVE_FROM (40) with under SPAWN_RESERVE_TOWERS (25) towers the reserve is 1000,
so a soldier needs 1250 chips.  With no chip income the wait never ends.  Per game, from r40, the rounds in which
  held    one of our towers holds 200+ paint (a soldier's paint) and our chips are in [250, 1250) (a soldier's chips, under
          cost + reserve), i.e. a soldier is affordable but the reserve blocks it
  dead    ... and no money tower of ours stands (no chip income at all: an SRP adds chips only per money tower), so
          the wait can never end
and the spawns by our towers in held rounds; the robots we have then (median); our towers then (median).  Losses and
wins, us and them (their bots have other rules; shown for scale only), main set and the set fetched during the study."""
from collections import defaultdict
import lib


def analyse(G):
    tp = defaultdict(lambda: defaultdict(int))     # round -> side -> max tower paint
    mt = defaultdict(lambda: defaultdict(int))     # round -> side -> money towers standing
    units = defaultdict(lambda: defaultdict(int)); tows = defaultdict(lambda: defaultdict(int))
    for t in G.turns:
        if t[3] in lib.TOW:
            tows[t[0]][t[2]] += 1
            if t[3] == 'MONEY_TOWER': mt[t[0]][t[2]] += 1
            if t[7] > tp[t[0]][t[2]]: tp[t[0]][t[2]] = t[7]
        else: units[t[0]][t[2]] += 1
    spawn_r = defaultdict(set)
    for a in G.acts:
        if a[4] == 'spawn' and a[6] in lib.BOT: spawn_r[a[2]].add(a[0])
    out = {}
    for sd, team in (('us', G.us), ('them', G.op)):
        o = defaultdict(float); u = []; tw = []; first = None
        for r in range(40, G.end + 1):
            c = lib.money(G, team, r - 1)
            if c is None: continue
            if tp[r - 1][team] >= 200 and 250 <= c < 1250:
                o['held'] += 1
                if r in spawn_r[team]: o['held spawn'] += 1
                if mt[r - 1][team] == 0:
                    o['flat'] += 1; u.append(units[r - 1][team]); tw.append(tows[r - 1][team])
                    if first is None: first = r
        o['units'] = lib.med(u); o['towers'] = lib.med(tw); o['first'] = first
        out[sd] = o
    return out


for tag, ms in (('main set', lib.MAIN), ('set fetched during the study', lib.NEW)):
    for res in ('lost', 'won'):
        OS = []
        for G in lib.games(res, matches=ms):
            o = analyse(G); o['id'] = f'm{G.m}g{G.g} {G.team_name[:12]} {G.map[:14]} end r{G.end} {G.wintype[:3]}'
            OS.append(o); G.turns = G.acts = None
        n = len(OS)
        if not n: continue
        print(f'\n== {tag}, {res}: {n} games; rounds from r40, per game (means)')
        for sd in ('us', 'them'):
            print(f'   {sd:4s}: soldier affordable but held back {sum(o[sd]["held"] for o in OS) / n:.1f} rounds (spawned in {sum(o[sd]["held spawn"] for o in OS) / n:.1f}); '
                  f'with no money tower standing {sum(o[sd]["flat"] for o in OS) / n:.1f}; games with 20+ such rounds {sum(1 for o in OS if o[sd]["flat"] >= 20)}')
        for o in OS:
            if o['us']['flat'] >= 20:
                print(f'      {o["id"]}: rounds held back with no money tower {o["us"]["flat"]:.0f} from r{o["us"]["first"]}, our robots then (median) {o["us"]["units"]}, towers {o["us"]["towers"]}')

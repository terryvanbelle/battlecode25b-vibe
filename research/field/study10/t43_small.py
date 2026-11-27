"""Topic 43: small maps (a side <= 25 or <= 600 paintable tiles), where 11 of 13 games were lost.  Per game, both sides:
first enemy robot within d2<=20 of one of the side's towers ('contact'), first hp damage dealt to an enemy tower,
first enemy tower killed (and its type), towers standing and units spawned by type at r50/r100, moppers' first spawn,
and the round the side's last paint tower died (0 = never had one after it).  Also the same for the medium maps
(26-35 side) as a contrast, summarised."""
import lib
from collections import defaultdict
def small(G): return min(G.W, G.H) <= 25 or G.sm['paintable'] <= 600
def summary(G):
    b, d = lib.tower_events(G)
    out = {}
    tpos = defaultdict(dict)
    bt = lib.by_round_turns(G)
    for sd in (G.us, G.op):
        o = 3 - sd
        first_contact = first_dmg = first_kill = None; kill_type = ''
        for r in range(1, G.end + 1):
            ts = bt.get(r, ())
            mine = [(t[4], t[5]) for t in ts if t[2] == sd and t[3] in lib.TOW]
            if first_contact is None and any(t[2] == o and t[3] in lib.BOT and any(lib.d2((t[4], t[5]), p) <= 20 for p in mine) for t in ts):
                first_contact = r
            if first_contact: break
        for a in G.acts:
            if a[2] == sd and a[4] == 'damage' and a[3] in lib.BOT and first_dmg is None: first_dmg = a[0]
        for x in d:
            if x[3] == o:
                # killed (not churned)
                if any(a[4] == 'die' and int(a[5]) == x[1] for a in G.acts if a[0] == x[0]):
                    first_kill = x[0]; kill_type = x[2][:1]; break
        sp = defaultdict(lambda: defaultdict(int)); mop1 = None
        for a in G.acts:
            if a[2] == sd and a[4] == 'spawn':
                for ck in (50, 100):
                    if a[0] <= ck and a[6] in lib.BOT: sp[ck][a[6][:2]] += 1
                if a[6] == 'MOPPER' and mop1 is None: mop1 = a[0]
        def tw(r): return len(lib.towers_alive(G, sd, r, b, d))
        def ptw(r): return sum(1 for t in lib.towers_alive(G, sd, r, b, d) if t[2] == 'PAINT_TOWER')
        nopt = next((r for r in range(1, G.end + 1) if ptw(r) == 0), None)
        out[sd] = dict(contact=first_contact, dmg=first_dmg, kill=f'{first_kill}{kill_type}' if first_kill else '-',
                       tw=f'{tw(25)}/{tw(50)}/{tw(100)}', sp50='S{SO}M{MO}X{SP}'.format(**{k: sp[50].get(k, 0) for k in ('SO', 'MO', 'SP')}),
                       sp100='S{SO}M{MO}X{SP}'.format(**{k: sp[100].get(k, 0) for k in ('SO', 'MO', 'SP')}), mop1=mop1, nopt=nopt)
    return out
for which in ('lost', 'won'):
    print(f'== small maps, {which}')
    print('   game           map            end  | US: contact dmg kill  towers r25/50/100  spawns<=r50 <=r100  1st mop  no-PT-from | THEM: same')
    for G in lib.games(which):
        if not small(G): continue
        s = summary(G); u, t = s[G.us], s[G.op]
        f = lambda x: f"{str(x['contact']):>4} {str(x['dmg']):>4} {x['kill']:>5} {x['tw']:>8} {x['sp50']:>9} {x['sp100']:>9} {str(x['mop1']):>5} {str(x['nopt']):>5}"
        print(f'   m{G.m}g{G.g} {G.team_name[:8]:8s} {G.map[:13]:13s} {G.end:4d} | {f(u)} | {f(t)}')

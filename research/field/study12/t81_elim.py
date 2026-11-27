"""Topic 81: the elimination games (ALL_UNITS_DESTROYED), both directions.  Per game, every 25 rounds up to the end:
towers standing (paint / money / defense) and robots alive (S / X / M) for us and them; when each of our towers
was killed, by which enemy unit types (damage in the tower's last 20 rounds), and how many of our robots stood within
d2 <= 20 of it; robots spawned by type up to r50 / r100; the first enemy robot within d2 <= 20 of one of our towers
('contact').  Then the same summary for the games WE won by elimination, and a table of how the opponents' units in
our half grew in the elimination losses vs our other losses (robot-turns of theirs within our half, per 100 rounds)."""
import lib
from collections import defaultdict, Counter


def half(G):
    """tile -> 'us' / 'them' / 'mid' by distance to the nearest starting tower of each side."""
    b, d = lib.tower_events(G)
    st = {s: [(x[4], x[5]) for x in b if x[0] == 0 and x[3] == s] for s in (1, 2)}
    def f(p):
        du = min(lib.d2(p, q) for q in st[G.us]); dt = min(lib.d2(p, q) for q in st[G.op])
        return 'us' if du < dt else 'them' if dt < du else 'mid'
    return f


def game_rows(G, focus):
    b, d = lib.tower_events(G)
    bt = lib.by_round_turns(G)
    dmg = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.BOT: dmg[int(a[5])].append((a[0], a[1], a[3], int(a[6])))
    pos = {x[1]: (x[4], x[5]) for x in b}
    out = []
    out.append(f'== m{G.m}g{G.g} {G.map} ({G.W}x{G.H}, {G.sm["paintable"]} paintable) vs {G.team_name}, {G.ver}, '
               f'{"LOST" if G.won_op else "WON"} {G.wintype} r{G.end}')
    for r in list(range(25, G.end, 25)) + [G.end]:
        cells = []
        for s in (G.us, G.op):
            tw = lib.towers_alive(G, s, r, b, d)
            pt = sum(1 for t in tw if t[2] == 'PAINT_TOWER'); mt = sum(1 for t in tw if t[2] == 'MONEY_TOWER'); dt = len(tw) - pt - mt
            R = G.rounds[min(r, len(G.rounds)) - 1]; k = 'A' if s == 1 else 'B'
            cells.append(f'T{len(tw):2d}(P{pt}M{mt}D{dt}) S{R["sol" + k]:>2} X{R["spl" + k]:>2} M{R["mop" + k]:>2} ${int(R["money" + k]):5d} cov{lib.rv(G, s, r, "covpct"):5.1f}')
        out.append(f'   r{r:<4} us {cells[0]} | them {cells[1]}')
    # our towers killed
    for a in G.acts:
        if a[4] != 'die' or a[7] not in lib.TOW: continue
        tid = int(a[5]); side = G.team.get(tid)
        if side != focus: continue
        r = a[0]
        last20 = [h for h in dmg.get(tid, ()) if h[0] >= r - 20]
        by = Counter()
        for h in last20: by[h[2][:2]] += h[3]
        att = len(set(h[1] for h in last20))
        p = pos.get(tid)
        de = [t for t in bt.get(r, ()) if t[2] == side and t[3] in lib.BOT and p and lib.d2((t[4], t[5]), p) <= 20]
        en = [t for t in bt.get(r, ()) if t[2] != side and t[3] in lib.BOT and p and lib.d2((t[4], t[5]), p) <= 20]
        out.append(f'   killed r{r:<4} {"ours" if side == G.us else "theirs"} {a[7][:5]} at {p}: damage last 20 rounds {dict(by)} '
                   f'from {att} robots; at death own robots d2<=20: {len(de)} ({"".join(t[3][:1] for t in de)}), '
                   f'enemy robots d2<=20: {len(en)} ({"".join(t[3][:1] for t in en)})')
    return out


def spawns(G, side, upto):
    c = Counter()
    for a in G.acts:
        if a[2] == side and a[4] == 'spawn' and a[0] <= upto and a[6] in lib.BOT: c[a[6][:2]] += 1
    return f'S{c["SO"]}X{c["SP"]}M{c["MO"]}'


def contact(G, side):
    bt = lib.by_round_turns(G)
    for r in range(1, G.end + 1):
        ts = bt.get(r, ())
        mine = [(t[4], t[5]) for t in ts if t[2] == side and t[3] in lib.TOW]
        if any(t[2] != side and t[3] in lib.BOT and any(lib.d2((t[4], t[5]), p) <= 20 for p in mine) for t in ts):
            return r
    return None


elim_l = [G for G in lib.games('lost') if G.wintype.startswith('ALL')]
elim_w = [G for G in lib.games('won') if G.wintype.startswith('ALL')]
print(f'{len(elim_l)} elimination losses, {len(elim_w)} elimination wins\n')
print('summary: game map opp ver end | contact on our towers / theirs | spawns <=r50 us / them | <=r100 us / them | '
      'towers r50, r100 us/them | robots r50, r100 us/them')
for G in elim_l + elim_w:
    print(f'   m{G.m}g{G.g} {G.map:12s} {G.team_name[:10]:10s} {G.ver:4s} {"L" if G.won_op else "W"} r{G.end:<4} | '
          f'{contact(G, G.us)} / {contact(G, G.op)} | {spawns(G, G.us, 50)} / {spawns(G, G.op, 50)} | '
          f'{spawns(G, G.us, 100)} / {spawns(G, G.op, 100)} | '
          f'{lib.rv(G, G.us, 50, "tow")}/{lib.rv(G, G.op, 50, "tow")}, {lib.rv(G, G.us, 100, "tow")}/{lib.rv(G, G.op, 100, "tow")} | '
          f'{lib.rv(G, G.us, 50, "units")}/{lib.rv(G, G.op, 50, "units")}, {lib.rv(G, G.us, 100, "units")}/{lib.rv(G, G.op, 100, "units")}')
print()
for G in elim_l:
    for line in game_rows(G, G.us): print(line)
    print()
print('#### elimination wins (their towers killed)')
for G in elim_w:
    for line in game_rows(G, G.op): print(line)
    print()

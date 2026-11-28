"""Topic 170: what their soldiers do at low hit points (follows t169: our siege runs end in death 25-27% of the time,
theirs 12-16%, at every company size (t165), with the same ~9 hits and ~6 exposures in the runs that end in death; and
t163: their soldiers that live stop hitting at a median 70 HP with 55 paint, ours at 140 HP with 34 paint).
Study 11 2.2's HP exit (t141 at 70 HP -53, t142 at 100 HP -92) was tried before t186's step-out, with siege() returning
false so that the turn went on to SRP/refill/explore (Nav does not avoid tower ranges).
Per soldier hit on an enemy paint/money tower (the tower stood a round after), by the hitter's HP at the hit (its turn
row) and by the exposures it already took from that tower in the run: the share of runs that continue (another hit
within 3 rounds) and the share that end with the soldier's death to that tower.  Then, per run that ends with the
soldier alive and the tower standing, the HP at the last hit (histogram), and what the soldier does in the 40 rounds
after: re-enters that tower's reach (r2 9) / any enemy tower's reach, dies (to a tower / starved / robot), paints
tiles (paint rows), completes towers or SRPs, its rounds alive.  Per side, losses then wins."""
from collections import defaultdict, Counter
import lib

BANDS = (0, 50, 100, 150, 200, 250)


def analyse(G, S):
    tt = {}; pos = {}
    for t in G.turns:
        if t[3] in lib.TOW and t[1] not in pos: pos[t[1]] = (t[4], t[5]); tt[t[1]] = t[3]
    life = defaultdict(dict)
    for t in G.turns:
        if t[3] == 'SOLDIER': life[t[1]][t[0]] = (t[4], t[5], t[6], t[7])
    towers_at = defaultdict(list)
    for t in G.turns:
        if t[3] in lib.TOW: towers_at[t[0]].append((t[1], t[2], t[4], t[5], t[3]))
    deaths = {}
    for a in G.acts:
        if a[4] == 'die': deaths[int(a[5])] = (a[0], a[1], G.typ.get(a[1]))
    shot = defaultdict(set)    # (tower, victim) -> rounds the tower hit the victim
    for a in G.acts:
        if a[4] == 'damage' and a[3] in lib.TOW: shot[(a[1], int(a[5]))].add(a[0])
    paints = defaultdict(list); builds = defaultdict(list)
    for a in G.acts:
        if a[4] == 'paint' and a[3] == 'SOLDIER': paints[a[1]].append(a[0])
        elif a[4] in ('build', 'srp') and a[3] == 'SOLDIER': builds[a[1]].append(a[0])
    hits = defaultdict(list)
    for a in G.acts:
        if a[4] == 'damage' and a[3] == 'SOLDIER' and tt.get(int(a[5])) in ('PAINT_TOWER', 'MONEY_TOWER'): hits[(a[1], int(a[5]))].append(a[0])
    for (sid, tid), rs in hits.items():
        rs = sorted(set(rs))
        sd = 'us' if G.team.get(sid) == G.us else 'them'
        side = G.team.get(sid)
        groups = []
        for r in rs:
            if groups and r - groups[-1][-1] < 15: groups[-1].append(r)
            else: groups.append([r])
        td = deaths.get(tid); d = deaths.get(sid)
        for g in groups:
            exp = 0
            for i, r in enumerate(g):
                hp = life[sid].get(r, (0, 0, None))[2]
                if hp is None: continue
                exp = sum(1 for x in shot.get((tid, sid), ()) if g[0] <= x <= r)
                cont = i + 1 < len(g) and g[i + 1] - r <= 3
                dead = bool(d and d[1] == tid and d[0] - r <= 5)
                b = min(250, (hp // 50) * 50)
                S[sd, 'hp', b, 'n'] += 1; S[sd, 'hp', b, 'cont'] += cont; S[sd, 'hp', b, 'dead'] += dead
                e = min(exp, 6)
                S[sd, 'exp', e, 'n'] += 1; S[sd, 'exp', e, 'cont'] += cont; S[sd, 'exp', e, 'dead'] += dead
            r1 = g[-1]
            fell = td is not None and g[0] <= td[0] <= r1 + 1
            died_here = bool(d and d[1] == tid and d[0] <= r1 + 5)
            if fell or died_here: continue
            L = life[sid]
            hp1 = L.get(r1, (0, 0, None))[2]
            if hp1 is None: continue
            k = 'low' if hp1 < 100 else 'high'
            S[sd, 'left', k] += 1
            S.setdefault((sd, 'left_hp'), []).append(hp1)
            # the 40 rounds after
            reent = reany = False
            q = pos[tid]
            for r in range(r1 + 1, r1 + 41):
                p = L.get(r)
                if not p: continue
                if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 <= 9 and not (td and td[0] <= r): reent = True
                for (oid, tm, x, y, ty) in towers_at.get(r, ()):
                    if tm != side and (p[0] - x) ** 2 + (p[1] - y) ** 2 <= (16 if ty == 'DEFENSE_TOWER' else 9): reany = True
            S[sd, 'left', k, 'reenter_same'] += reent
            S[sd, 'left', k, 'reenter_any'] += reany
            if d and d[0] <= r1 + 40:
                how = 'tower' if d[2] in lib.TOW else ('starved' if d[1] == sid else 'robot')
                S[sd, 'left', k, 'died_' + how] += 1
            S[sd, 'left', k, 'paints'] += sum(1 for x in paints.get(sid, ()) if r1 < x <= r1 + 40)
            S[sd, 'left', k, 'builds'] += sum(1 for x in builds.get(sid, ()) if r1 < x <= r1 + 40)
            alive = sum(1 for r in range(r1 + 1, r1 + 41) if r in L)
            S[sd, 'left', k, 'alive'] += alive
            S[sd, 'left', k, 'paint_at'] += L.get(r1, (0, 0, 0, 0))[3]
    S['games'] += 1


for which in ('lost', 'won'):
    S = defaultdict(int)
    for G in lib.games(which):
        analyse(G, S)
    ng = S['games']
    print(f'\n== {which}: {ng} games')
    for sd in ('us', 'them'):
        print(f'  {sd}: hits by HP band: per game, the run goes on (another hit within 3 rounds), the soldier dies to that tower within 5 rounds')
        print('     ' + '  '.join(f'{b:3d}-{b + 49:3d}: {S[sd, "hp", b, "n"] / ng:5.1f} ({100 * S[sd, "hp", b, "cont"] / max(1, S[sd, "hp", b, "n"]):3.0f}% / {100 * S[sd, "hp", b, "dead"] / max(1, S[sd, "hp", b, "n"]):3.0f}%)' for b in BANDS))
        print(f'  {sd}: hits by exposures already taken in the run (0..6+): per game (goes on / dies)')
        print('     ' + '  '.join(f'{e}{"+" if e == 6 else ""}: {S[sd, "exp", e, "n"] / ng:5.1f} ({100 * S[sd, "exp", e, "cont"] / max(1, S[sd, "exp", e, "n"]):3.0f}% / {100 * S[sd, "exp", e, "dead"] / max(1, S[sd, "exp", e, "n"]):3.0f}%)' for e in range(7)))
        h = S.get((sd, 'left_hp'), [])
        hist = Counter(min(250, (x // 30) * 30) for x in h)
        print(f'  {sd}: runs that end alive with the tower standing: {len(h) / ng:4.1f}/game; HP at the last hit: ' + ' '.join(f'{b}-{b + 29}:{100 * hist[b] / max(1, len(h)):.0f}%' for b in range(0, 251, 30)))
        for k in ('low', 'high'):
            n = max(1, S[sd, 'left', k])
            print(f'     left at {"<100" if k == "low" else ">=100"} HP: {S[sd, "left", k] / ng:4.1f}/game, paint then {S[sd, "left", k, "paint_at"] / n:5.1f}; in the next 40 rounds: re-enters that tower\'s reach {100 * S[sd, "left", k, "reenter_same"] / n:3.0f}%, '
                  f'any enemy tower\'s {100 * S[sd, "left", k, "reenter_any"] / n:3.0f}%; dies to a tower {100 * S[sd, "left", k, "died_tower"] / n:3.0f}%, starves {100 * S[sd, "left", k, "died_starved"] / n:3.0f}%, '
                  f'to a robot {100 * S[sd, "left", k, "died_robot"] / n:3.0f}%; rounds alive {S[sd, "left", k, "alive"] / n:4.1f}/40; paints {S[sd, "left", k, "paints"] / n:4.1f} tiles; towers+SRPs {S[sd, "left", k, "builds"] / n:4.2f}')

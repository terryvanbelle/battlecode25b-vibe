#!/usr/bin/env python3
"""Our replica (galaxy) rating against wall-clock time, with the ratings at places 1, 5, 10 and 15 (owner prompt #6).
There is no data before the first sample, taken 2026-11-25 ~10:30 PDT.

  python3 tools/replica_elo.py sample     append one row to progress/replica-elo.csv (the prod runs this every cycle)
  ~/.venv-bc25b/bin/python tools/replica_elo.py chart   progress/replica-elo.png from that file

The CSV columns are when_pdt, our_rank, our_rating, teams, p1, p5, p10, p15 (galaxy's displayed rating at those
places; empty if the ladder is shorter), and champion (our active local champion, from research/tourney/champion.txt).
"""
import csv
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'tools', 'galaxy25'))
CSV = os.path.join(REPO, 'progress', 'replica-elo.csv')
PNG = os.path.join(REPO, 'progress', 'replica-elo.png')
PDT = ZoneInfo('America/Vancouver')
PLACES = (1, 5, 10, 15)
HEADER = ['when_pdt', 'our_rank', 'our_rating', 'teams'] + [f'p{p}' for p in PLACES] + ['champion']
TEAM = 'vibe25b'


def sample():
    import client as cl
    c = cl.Client(None)
    acc = cl.load_accounts()
    my_id = acc[TEAM]['team_id']
    ladder = [t for t in cl.rankings(c) if t['rating'] is not None]
    ladder.sort(key=lambda t: -t['rating'])
    rank = next((i for i, t in enumerate(ladder, 1) if t['id'] == my_id), None)
    if rank is None:
        sys.exit('replica_elo: vibe25b not on the ladder')
    champ = open(os.path.join(REPO, 'research', 'tourney', 'champion.txt')).read().strip()
    row = [datetime.now(PDT).strftime('%Y-%m-%d %H:%M'), rank, f'{ladder[rank - 1]["rating"]:.0f}', len(ladder)]
    row += [f'{ladder[p - 1]["rating"]:.0f}' if len(ladder) >= p else '' for p in PLACES] + [champ]
    new = not os.path.exists(CSV)
    with open(CSV, 'a', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerow(row)
    print('replica-elo:', dict(zip(HEADER, row)))


BIG_GAIN = 40   # local Elo a new champion must gain over the one it replaced to get a vertical line


def big_crownings():
    """(crowned at, bot, local gain) for each champion whose current local rating beats its predecessor's by
    BIG_GAIN or more, from research/tourney/champions.csv and the tournament's present fit."""
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import tourney as T
    import elolib
    rt = elolib.fit(T.games())
    out = []
    for r in T.champ_history():
        b, a = r['bot'], r['base']
        if b in rt and a in rt and rt[b].rating - rt[a].rating >= BIG_GAIN:
            out.append((r['when'], b, rt[b].rating - rt[a].rating))
    return out


def chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    rows = list(csv.DictReader(open(CSV)))
    if not rows:
        sys.exit('replica_elo: no samples yet')
    t = [datetime.strptime(r['when_pdt'], '%Y-%m-%d %H:%M').replace(tzinfo=PDT) for r in rows]
    fig, (ax, gx) = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True, gridspec_kw={'height_ratios': [3, 2]})
    greys = {1: '#444444', 5: '#777777', 10: '#9a9a9a', 15: '#bdbdbd'}
    for p in PLACES:
        pts = [(ti, float(r[f'p{p}'])) for ti, r in zip(t, rows) if r[f'p{p}']]
        if pts:
            ax.plot([a for a, _ in pts], [b for _, b in pts], color=greys[p], lw=1.3, ls='--', marker='.', ms=3,
                    label=f'#{p} place')
    ax.plot(t, [float(r['our_rating']) for r in rows], color='#2a6fdb', lw=2.4, marker='o', ms=4, label='vibe25b (us)')
    last = rows[-1]
    ax.annotate(f"#{last['our_rank']} of {last['teams']}", (t[-1], float(last['our_rating'])), textcoords='offset points',
                xytext=(6, 6), fontsize=9, color='#2a6fdb')
    # mark the crownings with an especially large local gain over the champion they replaced (owner prompt #10)
    for when, bot, gain in big_crownings():
        if t[0] <= when <= t[-1] + (t[-1] - t[0]) * 0.05:
            for a in (ax, gx):
                a.axvline(when, color='#2a6fdb', alpha=0.35, lw=1.2)
            ax.text(when, ax.get_ylim()[1], f" {bot} +{gain:.0f}", fontsize=8, color='#2a6fdb', va='top', rotation=90)
    # lower panel: our rating minus the rating at each place (owner prompt #7); above 0 means we are ahead of it
    gap_col = {1: '#c0392b', 5: '#e67e22', 10: '#27ae60', 15: '#8e44ad'}
    for p in PLACES:
        pts = [(ti, float(r['our_rating']) - float(r[f'p{p}'])) for ti, r in zip(t, rows) if r[f'p{p}']]
        if pts:
            gx.plot([a for a, _ in pts], [b for _, b in pts], color=gap_col[p], lw=1.8, marker='o', ms=3,
                    label=f'us - #{p}')
            gx.annotate(f'{pts[-1][1]:+.0f}', pts[-1], textcoords='offset points', xytext=(6, -3), fontsize=8,
                        color=gap_col[p])
    gx.axhline(0, color='black', lw=0.8)
    gx.set_ylabel('our rating minus place')
    gx.grid(alpha=0.3)
    gx.legend(loc='best', fontsize=9, ncol=4)
    gx.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M', tz=PDT))
    fig.autofmt_xdate()
    gx.set_xlabel('time (PDT)')
    ax.set_ylabel('replica rating (galaxy Elo)')
    ax.set_title(f'Replica ladder: vibe25b vs places 1/5/10/15 ({len(rows)} samples, last {last["when_pdt"]} PDT)')
    ax.grid(alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    fig.tight_layout()
    fig.savefig(PNG, dpi=110)
    print(f'{os.path.relpath(PNG, REPO)}: {len(rows)} samples')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'sample':
        sample()
    elif cmd == 'chart':
        chart()
    else:
        print(__doc__)
        sys.exit(2)

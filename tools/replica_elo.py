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


def chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    rows = list(csv.DictReader(open(CSV)))
    if not rows:
        sys.exit('replica_elo: no samples yet')
    t = [datetime.strptime(r['when_pdt'], '%Y-%m-%d %H:%M').replace(tzinfo=PDT) for r in rows]
    fig, ax = plt.subplots(figsize=(11, 5.5))
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
    # mark changes of the active local champion
    prev = None
    for ti, r in zip(t, rows):
        if r['champion'] != prev and prev is not None:
            ax.axvline(ti, color='#2a6fdb', alpha=0.25, lw=1)
            ax.text(ti, ax.get_ylim()[1], f" {r['champion']}", fontsize=8, color='#2a6fdb', va='top', rotation=90)
        prev = r['champion']
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M', tz=PDT))
    fig.autofmt_xdate()
    ax.set_xlabel('time (PDT)')
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

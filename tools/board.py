#!/usr/bin/env python3
"""Export the training dashboard's data (https://claude.ai/artifact/DstLySDMnQvBtaAszuM2nB) as one JSON file:
{pool, status, replica, champions, local}, each a list of row objects. The prod uploads it and points the dashboard's
five datasets at the new file. `local` holds the points of progress/local-elo.png.

  python3 tools/board.py OUT.json
Change descriptions for pool bots come from research/tourney/notes.tsv (bot<TAB>change).
"""
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'tools'))
import tourney  # noqa: E402
ROW = re.compile(r'\s*(\d+)\.\s+(\S+)\s+(\d+)\s+\+-\s*(\d+)\s+games\s+(\d+)\s+\((\d+)-(\d+)\)\s+(.*)')
VS = re.compile(r'vs \S+\s+([+-]\d+) \(needs > \+(\d+)(?:, (\d+) more games)?\)')
SUM = re.compile(r'(\d+) games among (\d+) pool bots \((\d+) retired; (\d+) entered')


def num(s):
    try:
        return int(s) if re.fullmatch(r'-?\d+', s) else float(s)
    except (TypeError, ValueError):
        return None


def main(out):
    os.chdir(REPO)
    notes = {}
    if os.path.exists('research/tourney/notes.tsv'):
        for r in csv.DictReader(open('research/tourney/notes.tsv'), delimiter='\t'):
            notes[r['bot']] = r['change']
    rank = subprocess.run([sys.executable, 'tools/tourney.py', 'rank'], capture_output=True, text=True).stdout
    pool, status = [], {}
    for line in rank.splitlines():
        m = SUM.search(line)
        if m:
            status.update(games=int(m[1]), active=int(m[2]), retired=int(m[3]), entered=int(m[4]))
        m = ROW.match(line)
        if not m:
            continue
        rest = m[8]
        r = dict(place=int(m[1]), bot=m[2], rating=int(m[3]), se=int(m[4]), games=int(m[5]), wins=int(m[6]),
                 losses=int(m[7]), champion='CHAMPION' in rest, vs_champion=None, lead_needed=None,
                 games_needed=0, change=notes.get(m[2], ''))
        v = VS.search(rest)
        if v:
            r['vs_champion'], r['lead_needed'] = int(v[1]), int(v[2])
            r['games_needed'] = int(v[3]) if v[3] else 0
        if r['games'] == 0:
            r['rating'] = r['se'] = r['vs_champion'] = None
        pool.append(r)
    # owner #35/#40: the pool line marked 'replica record' holds the permanent slot; the dashboard shows it as Best Replica
    record = {l.split('#')[0].strip() for l in open('research/tourney/pool.txt')
              if l.split('#')[0].strip() and 'replica record' in l.split('#', 1)[-1]}
    for r in pool:
        r['replica_record'] = r['bot'] in record
    # owner #45/#47: the replica references are permanent, otherwise regular entrants (shown as Replica Ref)
    refs = sorted(tourney.refs(), key=lambda b: b not in record)   # the record holder first
    champ_name = next((r['bot'] for r in pool if r['champion']), None)
    confirm = tourney.read_confirm()
    for r in pool:
        r['replica_ref'] = r['bot'] in refs and not r['replica_record']
        # owner #46: a qualifier in its confirmation window
        # flat fields: the dashboard's datasets do not keep nested objects (owner 17:30: the pill read NaN/NaN)
        r['confirm'] = r['bot'] in confirm and champ_name is not None
        r['confirm_games'] = r['confirm_lead'] = r['confirm_se'] = r['confirm_since'] = None
        r['confirm_need'] = tourney.CONFIRM_GAMES
        if r['confirm']:
            lead, se, n = tourney.fresh(r['bot'], confirm[r['bot']], champ_name)
            r['confirm_games'], r['confirm_lead'], r['confirm_se'] = n, round(lead), round(se)
            r['confirm_since'] = confirm[r['bot']]
    status['refs'] = ', '.join(refs)
    status['confirm_games'] = tourney.CONFIRM_GAMES
    champ = open('research/tourney/champion.txt').read().strip()
    status['champion'] = champ
    status['updated_pdt'] = datetime.now(ZoneInfo('America/Vancouver')).strftime('%Y-%m-%d %H:%M')
    try:
        q = subprocess.run(['tools/box.sh', 'status'], capture_output=True, text=True, timeout=60).stdout.splitlines()
        status['queued'] = q[0].replace('queue:', '').strip() if q else ''
        last = [l for l in q[1:4] if ' start ' in l or ' end ' in l]
        status['box_last'] = last[-1] if last else ''
    except subprocess.TimeoutExpired:
        status['queued'] = status['box_last'] = ''
    cols = ['when_pdt', 'our_rank', 'our_rating', 'teams', 'p1', 'p5', 'p10', 'p15', 'champion', 'p20', 'orig']
    replica = []
    for r in csv.DictReader(open('progress/replica-elo.csv')):
        replica.append({c: (r.get(c) if c in ('when_pdt', 'champion') else num(r.get(c))) for c in cols})
    champions = []
    with open('research/tourney/champions.csv') as f:
        next(f)
        for line in f:
            p = line.rstrip('\n').split(',')
            if len(p) < 5:
                continue
            champions.append(dict(when_pdt=p[0], bot=p[1], base=p[2], change=','.join(p[3:-1]),
                                  submission=num(p[-1])))
    local = local_chart(notes)
    json.dump(dict(pool=pool, status=[status], replica=replica, champions=champions, local=local), open(out, 'w'))
    print(f'board: {len(pool)} pool bots, {len(replica)} replica samples, {len(champions)} champions, '
          f'{len(local)} local-chart points -> {out}')


def local_chart(notes):
    """The points of progress/local-elo.png (tourney.py chart) as rows: kind 'champion' (crowned at when_pdt, held
    until the next champion's when_pdt) or 'candidate' (entered at when_pdt; 10+ games, never champion), each with its
    current Bradley-Terry rating, SE and games."""
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import tourney
    gs = tourney.games()
    rt = tourney.elolib.fit(gs) if gs else {}
    hist = tourney.champ_history()
    if not hist:
        return []
    start, ent = hist[0]['when'], tourney.entry_times()
    rows, champs = [], set()
    for r in hist:
        b = r['bot']
        champs.add(b)
        if b in rt:
            rows.append(dict(kind='champion', bot=b, when_pdt=r['when_pdt'], rating=round(rt[b].rating),
                             se=round(rt[b].se), games=int(rt[b].games), change=r.get('change') or notes.get(b, '')))
    for b in sorted(set(tourney.pool()) | set(tourney.retired())):
        if b in champs or b not in rt or b not in ent or ent[b] < start or rt[b].games < 10:
            continue
        rows.append(dict(kind='candidate', bot=b, when_pdt=f'{ent[b]:%Y-%m-%d %H:%M}', rating=round(rt[b].rating),
                         se=round(rt[b].se), games=int(rt[b].games), change=notes.get(b, '')))
    return rows


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])

"""The replica record and its permanent pool slot (owner prompt #35).

The record is the highest rating in progress/replica-elo.csv (the earliest sample on a tie). Its holder is the
champion submitted 15 minutes before that sample, so a bot crowned just before a sample is not credited with its
predecessor's matches. The holder keeps a permanent slot in the local pool: an active line in
research/tourney/pool.txt whose comment says 'replica record'. No extra slot is needed when the holder is the
champion or already active. Prints what to do, changes nothing."""
import csv
import os
import sys
from datetime import datetime, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'tools'))
import tourney  # noqa: E402


def holder():
    rows = list(csv.DictReader(open(os.path.join(REPO, 'progress/replica-elo.csv'))))
    best = max(rows, key=lambda r: int(r['our_rating']))
    hist = tourney.champ_history()
    t = datetime.strptime(best['when_pdt'], '%Y-%m-%d %H:%M').replace(tzinfo=hist[0]['when'].tzinfo)
    before = [h['bot'] for h in hist if h['when'] <= t - timedelta(minutes=15)]
    return (before[-1] if before else best['champion']), best


def main():
    bot, best = holder()
    champ = tourney.champion()
    active = tourney.pool()
    slots = [l.split('#')[0].strip() for l in open(tourney.POOL)
             if l.split('#')[0].strip() and 'replica record' in l.split('#', 1)[-1]]
    print(f"replica record: {best['our_rating']} at #{best['our_rank']} on {best['when_pdt']} PDT, held by {bot}")
    if bot == champ:
        print('  the holder is the champion: no extra slot')
    elif bot in slots:
        print('  the holder has its permanent slot')
    elif bot in active:
        print('  the holder is already active; mark its pool.txt line "replica record" so no crowning retires it')
    else:
        print(f'  ADD {bot} to research/tourney/pool.txt, its comment saying "replica record" (owner #35)')
    for b in slots:
        if b != bot:
            print(f'  {b} has the replica-record slot but no longer holds the record: retire it unless it earns its place')


if __name__ == '__main__':
    main()

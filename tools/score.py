"""Game scores from a result row (tools/arena.py rows).

Battlecode 2025 games are plain win/loss: every win type (70% painted, all units destroyed, or the round-2000
tiebreaks: area painted, towers, money, stored paint, robots, coin flip) gives the winner the whole game.
cell(row): (100, 0) or (0, 100); (0, 0) when the row has no result (missing(row) says why).
TIEBREAK_TYPES are the round-limit win types, which a tiebreak-scripted bot can steer.
"""

VERSION = 1
TIEBREAK_TYPES = ('AREA_PAINTED', 'MORE_TOWERS', 'MORE_MONEY', 'MORE_STORED_PAINT', 'MORE_ROBOTS', 'COIN_FLIP')


def missing(row):
    """Why cell(row) has no score ('' when it has one)."""
    return '' if row.get('winner') in ('A', 'B') else 'no result'


def cell(row):
    if missing(row):
        return 0.0, 0.0
    return (100.0, 0.0) if row['winner'] == 'A' else (0.0, 100.0)

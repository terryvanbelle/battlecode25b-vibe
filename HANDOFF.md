# HANDOFF.md

Where everything is for the Battlecode 2025 redo. The method is `TRAINING_ALGORITHM.md`; this file maps it onto this
season's tools. Times are the owner's zone: `TZ=America/Vancouver` (UTC-7, "PDT"); the driver's clock is UTC.

## Ground rules (owner prompt #1, `PROMPTS.md`)
- Nothing from the original battlecode25-vibe (`~/projects/vibe/reference/battlecode25-vibe`, `~/projects/vibe/2025`)
  except its final bot as a benchmark (replica team `bc25-vibe-orig`).
- No 2025 post-mortems. Other years only through `~/projects/vibe/reference/readroom-no2025`
  (digests in `research/readings/`).
- Competitor code is security-scanned only, never read. Benchmarks play only on the replica.
- Nothing touches the official Battlecode infrastructure.

## Machines
| machine | role | how |
|---|---|---|
| driver (this VM) | editing, single study games, ranking, replica client | `~/projects/vibe/2025b` |
| Windows box (WSL2, 20 threads) | all tournament games, screen queue of 16 jobs | `tools/box.sh`; checkout `~/projects/vibe/b25b` |
| replica VM `battlecode-dev` | private galaxy ladder | `ACCESS.md`, `tools/galaxy25/README.md` |

## Instruments
- `RULES.md`: rules digest from the 3.1.0 engine source, cited.
- Map census: `tools/java/bc25tools/MapCensus.java`; the maps are in `maps/` (75, all public).
- `tools/arena.py`:
  - `game A B MAP [--seed --out --tsv]` plays one game.
  - `matrix CELLS --run DIR` plays a batch.
  - Results go to `runs/RUN/results.jsonl`.
- `tools/java/bc25tools/ReplayDump.java`: `summary`, `tsv` (rounds/turns/actions) and `board FILE GAME ROUND`.
  Units' indicator strings appear in `turns.tsv`.
- Unit tests: `tools/unit-tests.sh`, fake controller `test/vibe/World.java`, checks in `test/vibe/BotTest.java`.
  Run them after every change.
- Snapshots: `tools/snapshot.sh NAME [SRCDIR]` (the source is the **second argument**). For a variant: copy
  `bots/CHAMP` to a scratch directory, edit it, then `snapshot.sh NEW scratch/CHAMP`.

## Tournament (`tools/tourney.py`)
- `rank`, `plan RUN --games 200`, `add BOT`, `chart` (the chart needs `~/.venv-bc25b/bin/python`).
- State lives in `research/tourney/`: `pool.txt`, `champion.txt`, `champions.csv`.
- Queue a run with `tools/box.sh queue RUN`, collect it with `tools/box.sh pull RUN`. Before re-planning a queued
  run, check `tools/box.sh status`: never re-plan one that has started.
- Crowning:
  1. `contest.py submit bots/NAME`.
  2. Update `champion.txt`, and add a row to `champions.csv` with its submission number.
  3. Copy the champion into `src/vibe`.
  4. Regenerate `progress/local-elo.png` (owner prompt #5).
  5. Commit.

## Replica (`tools/galaxy25/contest.py`)
- Commands:
  - `submit`, `ladder`, `matches --all`, `results`;
  - `scrim --n N` (ranked upward, unranked downward), `scrim --vs A,B`;
  - `fetch --new` (replays go to `~/projects/vibe/bc25b-galaxy-replays/`).
- Field bots: 27 teams, listed in `~/projects/vibe/bc25b-benchmarks/MANIFEST.tsv` and
  `tools/galaxy25/field-teams.tsv`.
- Timers: field activity is on, and so is autoscrim (8-hourly ranked round), since 2026-11-25 09:30 PDT.

## Prod
A session cron fires every 20 minutes (owner prompt #3). It follows TRAINING_ALGORITHM §7.1 and reports on the
tournament, the replica and disk on the driver, the VM and the box.

## State at hand-off time
See the head of `research/tourney/champions.csv` and `tools/tourney.py rank`. Shelved code: `research/shelved/srp-src`
(the first SRP implementation, as in y03/sw01).

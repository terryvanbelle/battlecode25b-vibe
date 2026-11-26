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
- Only the local champion is ever submitted to the replica (owner prompt #8). To get past a plateau, learn the top
  teams' tactics from replays (field studies in `research/field/`) and build them into candidates.

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
  Units' indicator strings appear in `turns.tsv`. Dump version 3 (audit, owner prompt #14, `research/replaydump-audit.md`)
  reads every field the 3.1.0 replay schema holds except profiler data: disintegrations are `died` rows, mopper paint
  drains are `drain` (not `damage`), and round-1 starting-tower levels are `startlevel`.
- Unit tests: `tools/unit-tests.sh`, fake controller `test/vibe/World.java`, checks in `test/vibe/BotTest.java`.
  Run them after every change.
- Bot names: `yNN` tunings, `swNN` swings, `tNN` bots that imitate an enemy tactic seen in replays (owner prompt
  #12, from 2026-11-25 18:15 PDT; numbered t01, t02, ...). Earlier tactic copies kept their y/sw names: y44 (refill,
  champion), sw26-sw29 (economy, spawn cycle), y47/y49 (SRPs), y53, sw30-sw37 and y56-y59 (churn, moppers, opening,
  upgrades); `champions.csv` and `pool.txt` say which study tactic each copies.
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
- Ranked-rate parity: field activity uses only field teams as challengers (`OUR_TEAMS` in `field.py`), so we get
  matches only as an opponent, about half a field team's rate. Every prod tops us up with
  `contest.py scrim --n K` until our ranked-match count matches the field median.
- Timers: field activity is on, and so is autoscrim (8-hourly ranked round), since 2026-11-25 09:30 PDT.

## Replica progress chart
`python3 tools/replica_elo.py sample`, run every prod, appends our rank and rating and the ratings at places 1, 5, 10
and 15 (and 20, plus our previous attempt bc25-vibe-orig, from owner prompt #13) to `progress/replica-elo.csv`. `~/.venv-bc25b/bin/python tools/replica_elo.py chart` redraws
`progress/replica-elo.png` from it (owner prompt #6). The data starts at 2026-11-25 10:44 PDT. Vertical lines mark crownings whose
champion beats the one it replaced by `BIG_GAIN` (40) or more local Elo in the present fit (owner prompt #10).

## Automation (2026-11-26)
- `tools/prod.sh pull|queue [N]|replica|disk|commit MSG PATH...`: the mechanical prod steps.
- `tools/crown.sh NEW OLD "desc"`: the whole crowning (champion.txt first, submit, champions.csv, src/vibe, retire OLD,
  chart, audit diff, unit tests).
- `tools/variant.py NEW BASE FILE OLD NEW ...` builds a candidate from exact single-occurrence edits;
  `tools/variant.py port NEW BASE VAR VARBASE` re-applies a variant's change onto a new base.
- `tools/parity.py [--topup]`: ranked-rate parity.
- `.claude/skills/prod`: the prod procedure as a Claude Code skill. `.claude/agents/field-study.md`: a subagent with
  the field-study ground rules built in (it can write its own REPORT.md).
- `.claude/settings.json` runs `tools/hooks/guard.py` before every Bash command: it blocks git commands that touch the
  replica secrets, `git add -A/./--all` and `commit -a`, and submitting any bot other than champion.txt's.

## Prod
A session cron fires every 20 minutes (owner prompt #3). It follows TRAINING_ALGORITHM §7.1 and reports on the
tournament, the replica and disk on the driver, the VM and the box.

## State at hand-off time
See the head of `research/tourney/champions.csv` and `tools/tourney.py rank`. Shelved code: `research/shelved/srp-src`
(the first SRP implementation, as in y03/sw01).

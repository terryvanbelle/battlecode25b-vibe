---
name: prod
description: Run one bc25b prod cycle (TRAINING_ALGORITHM.md §7.1) - pull and rank the local tournament, crown, keep runs queued, retire/build candidates, replica sample/parity/fetch, disk, commit, report. Use whenever the recurring PROD prompt fires or the owner asks for a prod.
effort: high
---

# Prod (bc25b)

Repo: `~/projects/vibe/2025b`. Method: `TRAINING_ALGORITHM.md` §7.1; machine map: `HANDOFF.md`. Times in PDT
(`TZ=America/Vancouver`); the box's clock is UTC.

## Standing rules (owner prompts, `PROMPTS.md`)
- ONLY the local champion is ever submitted to the replica (#8). Crown with `tools/crown.sh`; the guard hook blocks
  any other submit.
- A copied tactic must win the local tournament before it counts (#9). Get past plateaus by learning the top teams'
  tactics from replays (field studies, `research/field/`); never read competitor code or 2025 post-mortems.
- Never commit or share `~/.bc25b-replica-password` or `~/.bc25b-galaxy-team`. Commit explicit paths only.
- Never stop to wait for the owner's ideas. The driver has 2 cores: never run parallel games on it.
- Save any new owner prompt in `PROMPTS.md` as `## #N (YYYY-MM-DD HH:MM PDT)`.

## Steps
1. `tools/prod.sh pull` - status, pulls every unfinished run, ranks.
2. Confirmation stage (owner #46): a bot that clears the lead bar prints `CONFIRMING X` and is crowned only after 150
   fresh games (runs after it qualified, `research/tourney/confirm.txt`) in which it still leads (> 0). `NOT CONFIRMED`
   restarts its window; never retire a bot for failing it (owner: don't throw away possible improvements).
   If rank prints `NEW CHAMPION X (was Y)`: `tools/crown.sh X Y "what X changes (study/tactic)"`. Check the audit
   diff is only the intended change. If the unit tests fail on a spawn-mix check, update `test/vibe/BotTest.java`.
   Then retire bots built on the old champion (`# NAME (retired: reason)` in `research/tourney/pool.txt`), never the
   replica slots (pool lines whose comment says `replica record`, owner #35, or `replica reference`, owner #45), and
   rebuild the promising ones on the new champion with `variant.py port`.
3. Pool upkeep, about 10 active besides the 3 replica slots, half tunings (`yNN`) and half tactic copies (`tNN`, #12).
   The replica slots are regular entrants that are never retired; they get no extra games (owner #47). Upkeep:
   - retire bots clearly behind (about -20 or worse after 200+ games, or flat after 500);
   - build candidates: `python3 tools/variant.py NEW BASE FILE 'OLD' 'NEW' [...]` (exact, single-occurrence
     replacements; snapshots and adds) or `python3 tools/variant.py port NEW BASE VAR VARBASE`; then
     `bash tools/unit-tests.sh`. Comment each change with its source (e.g. `// study 5 2.3: ...`).
   - when progress stalls, start a field study with the `field-study` agent on recent replica losses.
4. `tools/prod.sh queue 5` - plans new run numbers until 5 are queued (never re-plans a started run).
   A newly added bot only enters runs planned after it: if the queue holds only runs planned before it, that's fine;
   it gets games from the next ones.
5. `tools/prod.sh replica` - replica Elo sample and chart, local chart, parity top-up, fetch, recent matches.
   Its `tools/record.py` line names the replica record holder (owner #35: a permanent pool slot unless it is the
   champion or already active) and the two replica references (owner #45: the next best replica peaks, skipping the
   champion and the holder's direct parent and children). Act on an `ADD` or retire line it prints.
   At the first prod on or after 2026-11-29 16:07 PDT, run the pre-registered test once (`research/replica/PREREG.md`,
   owner #39) and report it; never look at it earlier.
6. `tools/prod.sh disk`.
6b. Dashboard (https://claude.ai/artifact/DstLySDMnQvBtaAszuM2nB, a Data-type artifact): `tools/prod.sh board
   SCRATCH/board.json`, upload it with the Artifact tool (`url` above, `asset: true`), then one ArtifactData batch
   `update` of `datasets/pool`, `status`, `replica`, `champions`, `local` setting `source.url` to the new `/_blob/<id>` and
   `updated.at` (pin each with `if_version`). Delete the previous board asset once nothing names it. Keep
   `research/tourney/notes.tsv` (bot<TAB>change) current for new bots: the pool table shows it.
7. `BC_SESSION=<this session's URL> tools/prod.sh commit "prod: ..." bots/NEW1 bots/NEW2 ...` (src/vibe after a crowning).
8. Report to the owner, concisely:
   - tournament size: games total and added since the last prod, active and retired bots, running/queued runs;
   - one pool table sorted by rating, champion marked: rating ± SE, games, lead vs champion, lead needed, games needed,
     and what each bot changes;
   - changes since the last prod (crownings, retirements with their score, new bots);
   - replica: rank/rating, places 1/5/10/15 (and 20, bc25-vibe-orig), our ranked matches vs the field median,
     recent matches;
   - disk free on driver/VM/box and machine state.

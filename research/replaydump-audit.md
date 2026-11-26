# ReplayDump audit (2026-11-25, owner prompt #14)

**Question:** can `tools/java/bc25tools/ReplayDump.java` extract everything a `.bc25` replay holds?

**Method:**
1. Listed every accessor in the replay schema (`battlecode.schema.*` in battlecode25-java-3.1.0.jar).
2. Read the engine code that writes each one (`build/src/battlecode/server/GameMaker.java` and its callers in
   `battlecode/world/`).
3. Checked the findings on replica match 1357 and on a local tournament replay (tr092, BatSignal).

## Answer
Before the fix, no. The dumper missed some data and mislabelled or misattributed some rows. Dump version 3 now
covers every field except profiler data:
- **Profiler data:** written only when profiling is enabled, and that is never the case for our runs. The summary
  reports `profilerFiles` (a count) so that a replay containing it would be noticed.

| schema data | before | now |
|---|---|---|
| `Round.diedIds`: robots removed without damage (`rc.disintegrate()`, resign, terminated player) | counted only, no ids | a `died` row against the robot itself |
| mopper paint drain: the engine writes it as `DamageAction` | logged as `damage`, mixed in with hp damage | `drain` |
| round-1 `UpgradeAction` for the 4 starting towers: written before any turn runs, so it lands in robot 1's first Turn | logged as 4 upgrades by robot 1; level shown as 3 | `startlevel` against each tower, level 2, not counted as an upgrade |
| `UpgradeAction.newHealth`, `newPaint`, `newMaxPaint` | dropped | column `d` |
| `IndicatorDotAction`, `IndicatorLineAction` | dropped | `dot` and `line` rows |
| `MatchFooter.timelineMarkers` | dropped | in the summary JSON |
| `GameHeader.specVersion`, `robotTypeMetadata` (per-type cooldowns, hp, paint, radii, bytecode limit) | dropped | in `meta.json` |
| `MatchFooter.profilerFiles` | dropped | count in the summary |
| summary `towersLost` | included disintegrations (our churn showed up as tower losses) | `towersLost` is destroyed towers only; `towersRemoved` counts disintegrations |

Already complete before the fix:
- every `Turn` field;
- every `GameMap` field;
- the `Round` team aggregates;
- every other action type.

The paint-grid check (`covMismatch`) is still 0 on both replays.

## What a replay cannot tell us (engine 3.1.0)
- **Messages.** `addMessageAction` is commented out in `RobotControllerImpl`.
- **Indicators and timeline markers on the replica.** Indicator strings, dots and lines, and timeline markers are
  written only with show-indicators on. That covers local games only, never the replica.
- **Anything inside a turn.** A robot's state is its end-of-turn record: hp, paint, cooldowns, bytecodes and
  position. It moves at most once a turn.
- **What a robot sees or knows.** Its vision, its decisions and its internal state are not recorded.
- **Exact chips.** Team chips are an end-of-round total. Per-tower income has to be inferred.

## Reading notes
- **The actor on a `die` row is the robot whose turn the death happened in.**
  - For a kill by attack, that is the killer.
  - For death from 0-paint damage, or from an exception, that is the dead robot itself.
  - Column `a` is the victim. Column `c` is the victim's type, not the killer.
- **`transfer` amounts are signed.** A negative amount means the actor withdrew paint from the other robot.
- **Every robot's life is accounted for.**
  - Every robot in `turns.tsv` has a spawn: a `spawn` row, or it is a starting tower.
  - Every robot that disappears before the end has a `die` or `died` row.
  - This was checked on both test replays.

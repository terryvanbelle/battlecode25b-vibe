# Unit audit (2026-11-25, owner prompt #15): which of our units are not pulling their weight, and why

**Data:**
- 18 replica games of the champion t16 against the top 6 teams, all unranked: matches 1390-1395. t16 won 2 of 18.
- 12 local games of `bots/d16` against t12. d16 is t16 plus an indicator tag on every branch of every unit's turn:
  `S:` soldier, `M:` mopper, `X:` splasher.
- All games dumped with ReplayDump v3.

**Scripts:**
- `units.py TEAM DUMPS...` gives per-unit output: tiles turned ours, enemy tiles cleaned, paint drained, damage,
  paint given, builds, idle turns, and turns ended at 0 paint or on enemy paint.
- `tags.py TEAM DUMPS...` gives the share of turns in each mode, and how often each mode changed nothing.
- Replays only. No competitor code was read.

## Our units against the top 6 teams' units, same 18 games

| per 100 unit-turns | our soldiers | their soldiers | our splashers | their splashers | our moppers | their moppers |
|---|---|---|---|---|---|---|
| tiles turned ours | 24.7 | 19.3 | 20.2 | 16.7 | – | – |
| tower damage | 210 | 174 | 19 | 70 | – | – |
| enemy tiles cleaned | – | – | – | – | 13.0 | 9.0 |
| paint drained from enemies | – | – | – | – | 50 | 66 |
| paint given to allies | – | – | – | – | 23 | 62 |
| turns ended on enemy paint | 18% | 6% | 15% | 2% | 20% | 2% |
| turns ended at 0 paint | 5% | 1% | 3% | 1% | 3% | 1% |
| units fielded | 488 | 616 | **51** | **662** | 335 | 701 |

Per turn, our soldiers and splashers do as much as theirs. Three things differ:
- **Unit mix:** they field 13 times as many splashers.
- **Paint drain:** our units end turns on enemy paint 3 to 10 times as often as theirs.
- **Mopper support:** our moppers give allies about a third as much paint.

## Findings (local d16 games, every turn tagged)

### 1. Money towers stop spawning after round 80 (production bug, since the S-M-X-M-S-M cycle)
- **Spawns:** money towers spawned 355 soldiers, 249 moppers and **0 splashers**. Paint towers spawned all 43
  splashers.
- **Cause:** after round 80 the cycle reaches the splasher slot on its third spawn. A splasher costs 300 paint.
  - Money towers make no paint, and our units' refills drain them.
  - So they sit below 300 paint on 96% of their turns after round 80, and `Tower.build` returns without spawning.
- **Effect:** each money tower spawns one soldier and one mopper after round 80, then nothing until it is churned
  (a fresh tower restarts the cycle) or destroyed. This is also why our army is soldier- and mopper-heavy and has
  almost no splashers.

### 2. Splashers mostly fail to splash (bug in the scoring grid, present since the first commit)
- **The bug:** `G.remember` scores a tile only `if (old == 1)`, where `old` is the remembered tile word including its
  last-seen paint bits.
  - A tile last seen as enemy paint therefore never scores.
  - Enemy tiles count for one turn at most, when first seen.
- **Effect:** splashers sent to the frontier, which steers them toward enemy paint, find no splash worth the
  minimum score.
- **Tagged turns:**
  - splashes on 1.4% of turns (the cooldown allows up to 20%);
  - frontier and wander turns change nothing in 99.7-100% of cases;
  - median paint carried while doing nothing: 208.
- **Fix:** test `(old & 0xF) == SEEN`. With it (d17), splashes rise to 2.4% of turns and tiles per 100 turns from
  11.7 to 14.5.
- **What is left:** 37% of splasher turns wander inside our own territory with nothing in view to paint, and 24%
  are refills.

### 3. Moppers chase enemy paint by standing on it
- **Turns:** 85% of mopper turns change nothing.
  - 25% are refills, 25% walk toward enemy paint, 24% wander, and 12% walk toward an enemy robot.
- **Cause:** `Mopper.turn` walks onto the enemy tile it targets, though a mop reaches 1 tile away (r² 2).
  - 44% of `M:targetpaint` turns end on enemy paint, which drains moppers at double the rate.
  - That is 88% of all mopper turns ending on enemy paint.
  - This drives the refill trips, and leaves little spare paint to give: 23 against their 62.

### 4. Soldiers
- **Turns:** 55% explore. 78% of explore turns change nothing: inside our own territory there is nothing empty
  within reach.
- **Refills:** 20% of turns, 97% of them unproductive.
- **Enemy paint:** soldiers end turns on it during exploring (13%), refills (21%) and sieges (47%).
- **Comparison:** per turn, our soldiers still match theirs. No single bug here; the refill and explore time is a
  tuning target.

## Candidates (on t16, in the pool from 2026-11-25 21:35 PDT)

| bot | change |
|---|---|
| y72 | the splash-grid bug fix (finding 2) |
| y73 | y72, plus a tower that can't afford a splasher's paint spawns a soldier in that slot (finding 1) |
| y74 | y72, plus moppers stop once their target is in reach (finding 3) |
| y75 | all three |

y75 won 10 of 11 local games against t12, and ended games sooner than d16 did: Gears in 491 rounds against 664,
walalilongla in 480 against 691.

## Next
- **More splashers.** If y73 or y75 wins, try the top teams' mix: about one splasher per soldier after round 100.
  Give money towers a splasher only when their paint allows.
- **Splasher movement:** a splasher with nothing in view should head for the nearest known non-ally region, not a
  random tile.
- **Soldier exploring:** steer it toward the frontier, not random tiles.

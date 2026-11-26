# Field study 4 (2026-11-25): y58 against the top 5, what still separates us

**Data:**
- 15 lost games, 0-3 in each match: 1178 old-but-gold, 1179 confused, 1180 just-woke-up, 1181 om-nom, 1182 subscribe-to-caterpillow.
- Replays only; no competitor code or write-ups were read.

**Files:**
- `lib.py` is a copy of study 3's loader, pointed at the new dumps.
- `run3.sh X.py` reruns a study 3 script; its outputs are `s3_*.txt`.
- The new scripts are `t0_timeline.py` and `t10`..`t28`. Each `tNN_*.py` writes `tNN.txt`.
- Dumps live outside the repo. To rebuild one:
  `java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv ~/projects/vibe/bc25b-galaxy-replays/M/replay.bc25 DIR/mM`
- Gotchas:
  - A disintegrated tower is not logged as `die`. (Fixed in dump version 3: it is now a `died` row.)
  - A rebuilt tower gets a new id.
  - The column after `die` is not the killer.

## 1. How the games were lost
**Outcomes:**
- 11 of 15 losses were by MAJORITY_PAINTED and 4 by ALL_UNITS_DESTROYED.
- The median loss came at r304.
- On Barcode we built **0** towers; on SandyBeach we built 2.

**Median timeline** (`t0_medians.txt`):

| round | coverage, us / them | towers, us / them | chips, us / them | paint, us / them | units, us / them |
|---|---|---|---|---|---|
| r50 | 211 / 219 | 4 / 4 | 700 / 770 | 1406 / 1667 | 8 / 7 |
| r100 | 294 / 306 | **3 / 6** | 800 / 1040 | 1422 / 2625 | 11 / 11 |
| r150 | 303 / 399 | **3 / 7** | 890 / 2050 | 1254 / 2125 | 10 / 19 |
| r200 | 361 / 566 | 5 / 8 | 850 / 2080 | 1499 / 3232 | 10 / 20 |
| r300 (8 games) | 239 / 1016 | 2.5 / 13 | 1865 / 1435 | 710 / 6743 | 7 / 50 |

**Where the gap opens:**
- The gap is in tower count, from r60 to r150.
- Build timing is the same: builds 1-6 come at r17, 36, 63, 88, 119, 151 for us and r17, 36, 60, 81, 94, 138 for them.
- **Tower losses:** by r150 we have lost a median of 3 towers and they have lost 0. Our first loss comes at r79, theirs at r145.
- **Snowball:** their mostly-money economy gives them about twice our chips, and each new tower adds 500 paint.

## 2. Differences, as codeable rules

### 2.1 Patterns wait for chips (very high)
**Evidence** (t17, t18):
- **Wait time:** from pattern ready to build takes a median of 17 rounds for us, 3 for them.
- **Chips at ready:** 735 for us, 1059 for them.
- **What the wait costs:**
  - While we wait, the towers spend a median 500 chips on units.
  - 3401 soldier-turns were spent parked beside a finished pattern with under 1000 chips.
  - 38 of our "ready" spells never led to a build.
- **Chips ≥ 1000 in r40-200:** we never reached it in 7 of 15 games. They held it for 60-94% of that window.

**Cause:** `Tower.build` spawns down to a 600-chip reserve. With 40-60 chips of income a round, chips rarely reach 1000.

**Rule:**
- Reserve chips for a pattern that is actually ready. Either:
  - a soldier sends a READY message, and towers freeze spawns until the tower is built (moppers still spawn when an enemy is within d² 20; the flag expires after 15 rounds), or
  - without messages: spawn only when chips ≥ 1000 + cost, or when `round%20 >= 8` and chips ≥ 600 + cost.
- A soldier waiting below 50% paint goes to refill and comes back.

### 2.2 Contested ruins (very high)
**Evidence:**
- **Failed attempts:** 86 of our marked ruins were never built, against 39 of theirs.
  - Ours were real attempts: a median peak of 14 of 24 tiles correct, with 7.5 enemy tiles.
  - 56 of the 86 had enemy paint in the 5x5 when we marked them.
  - The enemy later built on 46 of them.
- **Contested ruins built:** we built 2 of 58; they built 29 of 43, using a median 8.5 mops each. We made a median of 0 mops on ours.
- **Wasted turns:** a median 21% of our soldier turns were spent within 3 tiles of ruins we never completed.
- **Barcode:** the ruins near our base were pre-painted in enemy colours. We built 0 towers all game while holding 2000+ chips, and had no mopper before r101.

**Rule:**
- Before marking, count the enemy tiles `e` in the pattern.
- If `e > 0`, work the ruin only when a mopper is near or can be called in; a tower spawns one even below the reserve.
- The mopper's first job is to unpaint enemy tiles inside our marked 5x5s.
- The soldier paints the non-enemy tiles, then leaves.
- If `e >= 8` and no mopper arrives within 15 rounds, mark the ruin bad for 100 rounds.

### 2.3 Sieges (high)
**Evidence:**
- Enemy robots killed 97 of our towers; we killed 35 of theirs.
- In 12 of 15 games we lost a tower before r100.
- They send more attackers, earlier and more effectively:

  | | us | them |
  |---|---|---|
  | robot turns in the other team's half, r40-150 | 13% | 23% |
  | first damage to a tower | r68 | r42 |
  | attackers per siege | 1.38 | 1.90 |
  | sieges that killed the tower | 32% | 51% |

- Their splashers deal 18% of their tower damage. Ours hit towers 7 times in 15 games.
- When their moppers drained our attackers, the tower still fell 33% of the time against 31% without. Moppers don't decide sieges, so don't retry defensive moppers.

**Rule:**
- Commit to a tower only when a second ally attacker is within d² 36 or already attacking.
- Kite from 20 paint while attacking.
- Splashers in reach of a tower splash the tower first.

**Defence:** the data offers no cheap fix.

### 2.4 Build order (high, after 2.1 and 2.2)
**Evidence:**
- Their builds 1-8 are nearly all money, and they keep one paint tower past r100 in 13 of 15 games. We build 2 paint towers per money tower.
- Income over r1-200:

  | source | us | them |
  |---|---|---|
  | paint from paint towers | 1470 | 1090 |
  | paint from new towers | 3000 | 4500 |
  | chips (estimated) | 7480 | 15260 |

- Their robots hold 60-68% of their paint capacity; ours hold 47-57%.

**Why money-first lost for us:** money pays only when chips quickly become new towers, which needs 2.1 and 2.2 in place.

**Rule:**
- Build money towers for builds 1-6.
- Build a paint tower only when there are 0 paint towers, or when ≥ 6 towers stand and paint towers < money towers / 4.
- Test this on top of 2.1 and 2.2.

### 2.5 Soldiers starve on enemy paint (medium-high)
**Evidence:**
- 17.9% of our robot turns end on enemy paint, against 5.8% of theirs.
- 90% of our soldier deaths come at 0 paint, against 64% of theirs.

**Cause:** `workRuin` refills only when paint < 10.

**Rule:**
- In `workRuin`, refill below 40% paint whenever the pattern can't be completed this turn.
- Don't end a turn on enemy paint when a neutral tile within one step is as good.
- Drop the ruin when below 40% paint and more than 15 tiles from a tower.

### 2.6 SRPs work for them because they start late (medium, after 2.1 and 2.2)
**Evidence:**
- First SRP:

  | team | round | towers standing |
  |---|---|---|
  | confused | median r182 | 16 |
  | old-but-gold | r73-98 | 8 |
  | just-woke-up | r64 | 5 |

- Active SRPs: about 0 at r100 and 4-8 at r200.

**Rule:** start SRPs only when round ≥ 100, chips ≥ 1000, there is no READY flag, and either ≥ 6 towers stand or no uncontested ruin is known nearby.

### 2.7 Painting into enemy ruins (low-medium)
**Evidence:**
- They painted inside 29 ruins we had marked; we completed none of those 29.
- We never paint into theirs.

**Rule:**
- Splashers give +4 to splashes that cover an enemy-marked, untowered ruin.
- A passing soldier paints one empty pattern tile of such a ruin.

### 2.8 Not worth chasing
- Mopper garrisons and defensive moppers.
- A splasher-heavy late mix: their late splashers are a consequence of their tower count.
- The opening: build timing is the same as theirs.

## 3. Broken in our bot
1. **No recovery after losing a tower type.**
   - With 0 paint towers we stall for 100+ rounds (SandyBeach, Snowman).
   - With 0 money towers, box sat at 10 chips for 158 rounds.
   - Fix: if paint towers = 0, build paint; if money towers = 0, build money.
2. The 600-chip reserve starves pattern completion (2.1).
3. Refill doesn't work during ruin work (2.5).
4. No moppers for contested ruins: we spawn 0-1 moppers before r100 in 13 of 15 games.
5. **Churn sometimes loses the tower:** 3 of 22 disintegrations on shell were not rebuilt.
   - Fix: require the adjacent helper to be a soldier that is itself in churn-wait.
6. Early tower losses (2.3).

## 4. Suggested test order
1. Refill at 40% in `workRuin` and avoid enemy paint.
2. The ready-pattern spawn freeze (2.1).
3. A mopper for contested ruins, with the give-up rule (2.2).
4. Recovery after losing a tower type (3.1).
5. On top of 1-4, retry money-first (2.4) and late SRPs (2.6).
6. Sieges with 2+ attackers, and splashers hitting towers (2.3).

The study's full text was returned to the parent session; this is a faithful condensation.

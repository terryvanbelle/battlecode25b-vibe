# Field study 5 (2026-11-26): t36-t47 against the strong teams, what still separates us

Replays only (no competitor code or write-ups). 16 lost games from 9 ranked matches, ids 2120-2298: 2120 angtn (Oasis),
2150 placeholder-name-2 (Snowman, sayhi), 2169 angtn (Flower), 2176 geesegeesego (Bunny, Castle), 2178 lobster-roll
(Snowman, defensetower), 2254 placeholder-name-2 (Crab, SMILE), 2256 varunvejalla (gardenworld), 2292 placeholder-name-2
(DefaultHuge, Leaf, windmill), 2298 geesegeesego (Bread, Leaf). Supplementary: 5 unranked losses (`S5SET=all`) and 11
won games from the same matches as a control (`t37`). `lib.py` is study 4's loader; `t0_medians.py` and `t30`..`t37` are
new; each `tNN_*.py` writes `tNN.txt`. Dumps live in the scratchpad (`study5/dump/mM`), rebuilt with
`java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`.

## 1. How the games were lost
- 13 of 16 by MAJORITY_PAINTED, 2 by ALL_UNITS_DESTROYED (Snowman, windmill), 1 by AREA_PAINTED at r2000 (SMILE).
  Median loss **r480** (study 4: r304). The early game is no longer where we lose.

| round | cov%, us / them | towers | paint towers | chips | paint | units | SRPs |
|---|---|---|---|---|---|---|---|
| r50 | 9.2 / 14.8 | 4 / 4 | 1 / 1 | 830 / 805 | 1437 / 1741 | 8 / 7 | 0 / 0 |
| r100 | 16.7 / 20.6 | **6 / 5** | 1 / 1 | 885 / 1025 | 1763 / 2285 | 10 / 9 | 0 / 0 |
| r150 | 23.9 / 23.8 | 6 / 6 | **1 / 2** | **1450 / 1016** | 1607 / 2845 | 13.5 / 12 | 0 / 1 |
| r200 | 30.3 / 33.4 | 6.5 / 7 | 1 / 2 | 1615 / 1164 | 2098 / 3319 | 16 / 22 | 1 / 3 |
| r300 (14) | 36.1 / 43.5 | 7.5 / 10.5 | **1 / 4** | 1847 / 1057 | 2847 / 5081 | 24.5 / 38 | 4 / 5.5 |
| r400 (11) | 36.0 / 53.5 | 7 / 15 | 1 / 5 | 2268 / 884 | 4064 / 9364 | 28 / 74 | 5 / 9 |

- From r150 we are paint-bound and they are not: 1 paint tower all game against their 2, 4, 5; chips pile up (>= 3000
  for 50+ rounds of r101-400 in 9 of 16 games, theirs 4).
- Control (`t37`): in our 11 wins against the same teams we have 2.5 paint towers at r300 (them 1.5).

Economy by phase (`t30`, medians, us / them):

| | r1-100 | r101-200 | r201-300 | r301-400 |
|---|---|---|---|---|
| paint from paint towers | 1000 / 1153 | **1144 / 1983** | **2024 / 6606** | 3006 / 11137 |
| chips from money towers | 6885 / 6450 | 13392 / 11723 | 17524 / 25197 | 18972 / 40847 |
| mean chips held | 935 / 868 | 1319 / 1039 | 2282 / 1264 | 3411 / 1375 |
| tower turns paint-blocked\* | 15.6% / 10.1% | **46.1% / 21.6%** | **80.1% / 31.6%** | 87.1% / 40.1% |
| mopper spawns | 6.5 / 5.5 | 10 / 13.5 | 12.5 / 18 | 14 / 36 |
| splasher spawns | 0 / 0 | 2 / 3.5 | 3.5 / 7.5 | 6 / 15 |

\* tower < 200 paint while the team holds >= 1250 chips. Chip-blocked is <= 2% for both.

Flower (m2169): we led coverage 955 to 464 at r450 with 7 money towers and 1 paint tower; money towers were then
upgraded (13 upgrades), churn stopped, units fell 22 -> 7, and we ended with 117,847 chips, losing at r871.

## 2. Differences, as codeable rules
### 2.1 Build paint towers when paint is the limit (very high)
- Our non-churn builds 1-6: 89 of 89 money. Theirs: money for builds 1-2, then about a third paint (build 5: 9 paint, 7 money).
- Second paint tower: theirs at median r95; we never build one in 10 of 16 games. 54 money towers built at >= 2000 chips.
- Cause: `Soldier.wantType()` returns MONEY for n < 8 (study 4 2.4 overshot).
- Rule: money for towers 1-3; then paint when paint towers < 1 + (towers - 3) / 3, or chips >= 2000, or the last refill
  found a dry tower with chips >= 1250.

### 2.2 Money upgrades switch off churn (very high; a bug)
- `Tower.churn()` fires only on an L1 money tower; `Tower.upgrade()` lifts money towers at chips >= cost + 3700
  (8 of 16 games, first at r329-384). Churns: 74 before the first money upgrade, 10 after (7 games).
- After it: median chips 4.6k-42k, 1 paint tower, 87% paint-blocked. Peaks: Flower 117,847, SMILE 234,885, Bread 33,183.
- 173 of our 561 builds were churn rebuilds (theirs 55 of many more): churn was our main paint source.
- Rule: no money upgrades while paint towers < money towers / 2 or > 30% paint-blocked; with chips >= 5000 churn a
  money tower of any level; better, rebuild a drained money tower as a paint tower.

### 2.3 Splashers parked with full paint (high; a bug)
- Splasher-turns spent 25 turns inside a 5x5, >= 150 paint, no own tower adjacent: median **8.6%** of ours vs **0.1%**
  (11,559 vs 699). Bread 43%, Castle 22%, Flower 17.5%. Mostly ally ground, ~1.6 empty tiles in view, often at the edge.
- Cause: `Splasher.frontier()` targets the nearest non-ally tile at d2 >= 5, a lone empty tile that never reaches the
  splash threshold (9 before, 6 after the move).
- Per splash we match them (7.0 vs 6.9 tiles gained); their edge is numbers.
- Rule: the frontier target must score >= 6 as a centre or be enemy paint; after 8 turns without a splash, explore.

### 2.4 Trickle refills (medium-high)
- 51.6% of our withdrawals take <= 15 paint (theirs 6.6%); mean 42 vs 74. Turns beside an own tower: splashers 11.5% vs
  5.2%, moppers 12.3% vs 5.2%, soldiers 9.2% vs 7.0%.
- Cause: `refillAt` clears only at 75% of capacity, so a unit siphons a 5-15/round tower every turn.
- Rule: withdraw only if the tower holds >= min(needed, 50) or the unit can't act; else mark it dry and go back to work.

### 2.5 Splashers hit towers (medium; open since study 4)
- Splasher hits on towers: median 2 per game vs 13 (188 vs 663 total). +12 per tower in `towersIntoGrid` is too weak.

### 2.6 More moppers late (low; a consequence of 2.1)
- Mopper spawns 13.5 / 18 / 36 vs our 10 / 12.5 / 14 in r101-200 / r201-300 / r301-400.

## 3. What changed since study 4
| study 4 gap | then (us / them) | now (us / them) | status |
|---|---|---|---|
| towers at r100 / r150 | 3 / 6, 3 / 7 | 6 / 5, 6 / 6 | closed |
| towers killed by r150 | 3 / 0 | 1 / 1 | closed |
| pattern ready to build | 17 / 3 rounds | 8 / 4 | mostly closed |
| failed ruin attempts | 86 in 15 games | 36 in 16; 3% soldier turns wasted (was 21%) | closed |
| mops on our ruins | median 0 | 49 / 27 | closed (ahead) |
| attackers per siege, kill rate | 1.38 / 1.90, 32% / 51% | 2.27 / 2.43, 43% / 45% | closed |
| splashers hitting towers | 7 in 15 games | median 2 / 13 per game | open |
| money first | 2 paint per money | 0 paint in builds 1-6 | overshot (2.1) |
| turns ending on enemy paint | 17.9% / 5.8% | 8.8% / 11.4% | closed |
| SRPs | about 0 | 4 / 5.5 at r300 | mostly closed |
| recovery after losing a tower type | stalls | none seen | closed |

## 4. Broken in our bot
1. Money upgrades switch off churn (2.2). 2. The splasher frontier trap (2.3). 3. Refill trickle (2.4).
4. `wantType()` money below 8 towers (2.1). 5. Small maps (Snowman, windmill): early tower losses, not covered here.

## 5. Suggested test order
2.2, then 2.1, 2.3, 2.4, then 2.5. Candidates: t54 (no money upgrades), t55 (churn at any level with >= 5000 chips),
t56 (paint-tower build rule), t57 (no trickle refills), t58 (splasher explores after 8 rounds without a splash).

The study's full text was returned to the parent session; this is a faithful condensation.

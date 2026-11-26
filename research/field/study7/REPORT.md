# Field study 7 (2026-11-26): y155, t70 and t74 on the replica since submission 64

Replays only (no competitor code, no write-ups).

The data is 27 matches (81 games) since submission 64 (y155), ids 2641-2897 (\* = unranked):

| match | opponent | result | | match | opponent | result |
|---|---|---|---|---|---|---|
| 2641 | slifland | L 1-2 | | 2715 | angtn | L 1-2 |
| 2642 | podemice | W 2-1\* | | 2716 | slifland | W 2-1\* |
| 2643 | geesegeesego | L 1-2 | | 2723 | the-kragle | W 3-0 |
| 2644 | ryanaspen | W 3-0\* | | 2729 | slifland | W 3-0 |
| 2645 | gone-whalin | W 2-1 | | 2749 | slifland | L 1-2 |
| 2646 | the-kragle | W 3-0\* | | 2753 | placeholder-name-2 | L 1-2 |
| 2681 | geesegeesego | W 2-1 | | 2768 | lobster-roll | L 1-2 |
| 2682 | the-kragle | W 3-0\* | | 2783 | angtn | W 3-0 |
| 2683 | slifland | W 2-1 | | 2804 | geesegeesego | W 3-0 |
| 2684 | ryanaspen | W 3-0\* | | 2807 | varunvejalla | W 3-0 |
| 2685 | gone-whalin | L 0-3 | | 2873 | placeholder-name-2 | W 2-1 |
| 2686 | podemice | W 3-0\* | | 2888 | gone-whalin | W 3-0 |
| 2702 | ryanaspen | W 3-0 | | 2897 | immutable | W 2-1 |
| 2712 | ryanaspen | W 3-0 | | | | |

That makes **22 lost games**: 20 ranked, plus 2642g0 and 2716g0, which were unranked. The 59 won games serve as the control.

Our bot version comes from each replay's header (`pkgs.py`):

| version | matches | games |
|---|---|---|
| y155 | 2641-2646 | 18 |
| t70 | 2681-2807 | 54 |
| t74 | 2873-2897 | 9 |

None of these games was against the current top 5. For their curves I reuse matches 1390-1393 and 1395, our t16 against old-but-gold, just-woke-up, om-nom, confused and subscribe-to-caterpillow. That is 15 games, all lost (`S7SET=ref5`), and it shows those bots as they were then.

y170 was crowned while this study was running: t74 plus a paint tower at 1500+ chips, submission 67. There are no replays of it yet. The candidates below are written against y170, which equals t74 apart from that one line (`Soldier.java:112`).

How to run:
- `lib.py` is study 6's loader, adapted. It reads the environment variables `S7VER`, `S7TEAMS`, `S7RANKED=1` and `S7SET=main|ref5|all`, and sets `G.ranked`.
- t0-t54 are study 6's scripts, rerun (t12, t13 and t48 were copied but not rerun). t60-t80 are new.
- Each `tNN_*.py` writes `tNN.txt` through `./run.sh tNN_x.py [outfile]`.
- `t67_ranked.txt` and `t68_ranked.txt` are ranked-only reruns, and they agree with the full set.
- t77, t79 and t80 take a game as arguments (`python3 t79_ruintrace.py m2749g0 50 300`). run.sh passes no arguments, so it runs their defaults: mit at r200, Barcode r50-300, and Barcode.
- The dumps are in the session scratchpad (`study7/dump/mM`); `dumpall.sh` there made them one at a time. Rebuild one with `java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`.

## 1. How the games were lost

### Overview
- **How they ended.** 19 of 22 by MAJORITY_PAINTED, 2 by ALL_UNITS_DESTROYED (boxofchocolates r161, MoneyTower r444) and 1 by AREA_PAINTED at r2000 (maze). The median loss came at **r396** (study 6: r370). By version: y155 r358 (6 games), t70 r395 (14), t74 r422 (2).
- **Games won and lost by opponent** (`t40`):
  - slifland 9-6, gone-whalin 5-4, geesegeesego 6-3, placeholder-name-2 3-3, angtn 4-2, lobster-roll 1-2, immutable 2-1, podemice 5-1.
  - Against ryanaspen we went 12-0, against the-kragle 9-0 and against varunvejalla 3-0.
- **Map size** (`t40`): with the short side at most 25 we lost 4 of 10 (study 6: 11 of 13). 26-35: lost 10 of 24. Over 35: lost 8 of 47. With at most 500 paintable tiles: lost 3 of 4.
- **Towers at r100, ours minus theirs:**

  | difference | won | lost |
  |---|---|---|
  | +3 or more | 22 | 3 |
  | +1 or +2 | 24 | 6 |
  | 0 | 12 | 7 |
  | -1 or less | 1 | 6 |

  We open well. **The losses are decided after r100.**

### Median timeline of the 22 losses
From `t0_medians`. Each cell is us / them. S / X / M = soldiers / splashers / moppers.

| round | cov % | towers | paint towers | chips | paint | units | S / X / M |
|---|---|---|---|---|---|---|---|
| r50 | 13.6 / 16.2 | 4 / 4 | 1 / 1 | 935 / 650 | 1405 / 1770 | 7.5 / 7 | 7.5/0/0 vs 5/0/1 |
| r100 | 21.3 / 22.1 | **6 / 5** | 1 / 1 | 1155 / 561 | 1801 / 2104 | 9.5 / 10 | 8/0/1.5 vs 7/0/2.5 |
| r150 | 31.4 / 28.3 | 6 / 6.5 | **1 / 2** | **1830 / 1059** | 1695 / 2902 | 12.5 / 16 | 7.5/1/3 vs 8/0.5/6 |
| r200 (21) | 31.4 / 35.5 | 6 / 7 | 1 / 2 | 2410 / 890 | 1594 / 2555 | 12 / 21 | 6/1/4 vs 10/2/9 |
| r300 (17) | 31.8 / 49.1 | **5 / 9** | 1 / 2 | **3525 / 1577** | 1367 / 4328 | **13 / 34** | 6/3/4 vs 14/7/12 |
| r400 (10) | 27.0 / 55.7 | 4.5 / 11 | 1 / 4 | 5671 / 1516 | 1028 / 4502 | 10 / 44.5 | 5.5/3.5/2 vs 13.5/12.5/16.5 |

### The economy curve
Paint income per round from paint towers, including +3 per active SRP. Medians, us / them (`t60`):

| paint income per round | r100 | r150 | r200 | r250 | r300 | r400 |
|---|---|---|---|---|---|---|
| losses | 10 / 10 | 10 / 15 | 14.3 / 21 | 15.7 / **44** | 21.1 / **56.7** | 22.5 / 61.5 |
| wins | 10 / 10 | 10 / 14 | 26 / 15 | 43.6 / 16 | 62.6 / 15 | 65.5 / 20.9 |
| top-5 ref. (t16 / them) | 10 / 10 | 10 / 13.1 | 10 / 23.9 | 10 / 25.8 | 10 / 45 | 15 / 68.3 |

- **Wins.** We stand on 7 / 5 towers at r100, 9 / 6 at r200 and 10 / 7 at r300. We reach 2 paint towers at r175, 3 at r250 and 4 at r300.
- **The top 5** (against t16) follow the same curve: 8 towers at r175-r200, 11 at r300, the 2nd paint tower at r175 and the 3rd at r250.
- **Losses.** We never go past 1 paint tower (median, up to r400).

### What goes wrong after r100
- **The curves split in r101-250, and kills don't explain it.**
  - In the 18 losses that reached r250 (`t68`), they built towers on **71 new ruins in that window (median 4 per game); we built on 24 (median 1)**.
  - Kills are even: they killed 38 of our towers, we killed 33 of theirs.
  - We go from 6 towers to 6, they go from 5 to 9.5.
  - In our wins it is the other way round: 244 new ruins (median 4) for us, 166 (2) for them.
  - Ranked games only: 20 against 67 (`t68_ranked`).
- **We stop expanding with chips in the bank.**
  - In a median loss we hold at least 3000 chips in 40% of the rounds from r101 to r400. They do in 1%, and we do in 5% in our wins (`t76`).
  - We reach our 7th new-ruin tower in 8 of 22 losses (they do in 18), and our 8th in 4 (they do in 17) (`t61`).
- **No paint tower at all.** 10 of the 22 losses have rounds with no paint tower of ours standing, and in none of the 10 did we build one again (`t67`; see 2.2).
- **Paint is the limit, not chips** (`t30`, `t49`).
  - Our towers are paint-blocked on 66.9% / 89.6% / 94.8% of tower-turns in r101-200 / r201-300 / r301-400. Theirs: 19.9 / 44.9 / 56.9.
  - Across the 22 losses, their built paint towers that lived at least 100 rounds number 54 and spawned 1707 units. Ours number 21 and spawned 378 (`t54`).
- **Units** (`t45`; soldiers / moppers / splashers alive per round):
  - r101-200: 8.1 / 2.9 / 0.9 against 8.1 / 5.8 / 0.8.
  - r201-300: 7.5 / 4.5 / 1.9 against 10.7 / 10.8 / 4.7.
  - Their first mopper comes at a median r34, ours at r89 (`t44`), because `Tower.choose` spawns only soldiers before r80.
- **Deaths per 100 robot-turns** (`t41`): soldiers 0.59 against 0.28, moppers 0.81 against 0.49, splashers 0.66 against 0.21.
  - 72% of our dead soldiers ran out of paint rather than being shot by a tower.
  - 49% of our dead soldiers had been drained by an enemy mopper in their last 10 rounds (theirs: 29%).
  - Only 27% of our soldier deaths happen in their half; 65% of theirs happen in ours (`t71`). We die defending.

### Economy by phase
From `t30` and `t47`. Medians per game, us / them.

| | r1-100 | r101-200 | r201-300 | r301-400 |
|---|---|---|---|---|
| paint from paint towers | 1000 / 1000 | **1117 / 1802** | **1662 / 4395** | 2130 / 5581 |
| new towers (any type) | 4 / 4 | 4 / 4 | 4 / 5 | 1 / 3.5 |
| of which paint towers | 0 / 0 | **0 / 2** | 0 / 0 | 0 / 1 |
| churns | 0 / 0 | 2 / 0 | 2 / 0 | 0 / 0 |
| SRPs completed | 0 / 1 | 2 / 4 | 0 / 4 | 0 / 2 |
| paint spawned into robots | 2250 / 2300 | 1800 / 2500 | 2800 / 3700 | |
| paint drained by enemy moppers | 50 / 0 | 240 / 190 | 515 / 380 | |
| mean chips held | 1053 / 923 | **1888 / 927** | **2840 / 1680** | 4458 / 1760 |
| tower-turns paint-blocked\* | 23.9% / 12.4% | **66.9% / 19.9%** | 89.6% / 44.9% | 94.8% / 56.9% |

\* the tower holds less than 200 paint while the team holds at least 1250 chips.

### Small maps
Short side at most 25: 4 losses and 6 wins (`t43`, `t60`, `t79`, `t80`). Each loss has its own cause, and each one maps to a rule below.
- **Filter** (gone-whalin, ended r242). Our paint tower died at r27. In the 216 rounds that followed we built 6 towers, all money towers (2.2).
- **Barcode** (slifland, ended r660). They came to us (2.3):
  - They built their first tower in our half at r43 and ended up on 7 ruins of our half, plus one of our starting towers' ruins at r468.
  - At r50 the other free ruins in our half held 6-24 of their tiles.
  - We put 14-20 of our tiles on three ruins in their half, each still holding 3-5 of theirs, and marked none of them.
  - Their first mopper came at r16, ours at r137. Our moppers mopped 0 tiles inside any ruin's 5x5 before r201. Theirs mopped 29 in our half's ruins before r200 and 570 after.
  - We marked one ruin in r50-r300 (at r269), stood on 3 towers at r150 (they on 4), and held at least 3000 chips in 84% of r101-400.
- **Justice** (lobster-roll, ended r395). There was no free ruin from r100 on, and we stood on 1 paint and 5 money towers. Our chips stood at 3080 at r150, 6060 at r300 and 6870 at the end. At r200 we had 5 soldiers and no other units (2.4).
- **Paintball** (gone-whalin, ended r245). Our soldiers fell from 7 to 1 between r100 and r150, against their 5 moppers. This is study 6 rule 2.5 territory.

Their first mopper came at r15-r43 in 3 of these 4 losses; ours came at r80-r136. But in our 6 small-map wins their first mopper also came early (r2-r60). Early moppers alone don't separate the wins from the losses.

## 2. Differences, as codeable rules
Line numbers refer to `bots/y170`.

### 2.1 Find the ruins: explore unseen ground first, and go back to remembered free ruins (high; new)

**Evidence.**
- **Where their new ruins come from.** This is the expansion gap from section 1 (24 new-ruin towers for us against 71 for them in r101-250). Their robots first saw those 71 ruins at a median r101, and they built on them 42 rounds later. 54 of the 71 lie in their own half, and 57 were clean 50 rounds before the build (`t74`). Our 24 were first seen at a median r84 and built 54.5 rounds later.
- **Free ruins in our half at r100.** In the losses there were 96 (`t72`):

  | state at r100 | ruins | later built by us / by them |
  |---|---|---|
  | **never seen by any of our robots** | **43** | 17 / 15 |
  | seen and clean | 14 | 11 / 3 |
  | seen, 1-4 enemy tiles | 21 | 5 / 6 |
  | seen, 5+ enemy tiles | 18 | 3 / 14 |

  In our wins, 176 of these ruins were unseen at r100, and we built 137 of them.
- **Where the unseen ruins are.** They sit in 9 games, 7 of them on maps of 50x50 or larger:
  - mit: 7, of which 5 were never seen in 411 rounds. They built all 7.
  - giver: 10, never seen in 261 rounds. They built 6.
  - maze: 7, and we built all 7 later. That game went to r2000.
  - Oasis: 4 in one game (we built all 4 later) and 5 in the other.
  - Gears: 4, which we first saw at r228-r378. Their own unseen ruins on that map were seen by r120.
  - boxofchocolates: 3. DefaultMedium: 2. Bunny: 1.

  In the other 13 losses, every free ruin in our half had been seen by r100.
- **How slowly we get there.**
  - For a clean free ruin in our half at r100, our first soldier came within d2 20 a median **172 rounds** later (p25: 15). Only 14 of those 55 ruins had been seen before r100.
  - For their clean ruins in their half it took 48.5 rounds, and for ours in our wins 44.5 (`t64`).
  - We marked 5 of the 55 within 50 rounds (`t62`).
- **It is not exploration in general.**
  - By r100 we had seen 92.5% of our half's tiles, and they 88.5% of theirs (`t65`).
  - Within 4 tiles of the border it was 64% against 63%; inside, 99-100% (`t70`).
  - What we miss are walled pockets and the far corners of big maps. On mit that is the whole top band beyond the wall line (`t77` draws mit at r200); on giver, the two far corners.

**Code.**
- `Unit.exploreTarget()` (Unit.java:113) draws one uniformly random tile. It renews the target on arrival (d2 at most 8), after 60 rounds, or when the tile is a known wall. A random-waypoint walk favours the middle of the map and rarely enters walled pockets.
- `Soldier.pickRuin()` (Soldier.java:80) looks only at `G.ruins`, which is `rc.senseNearbyRuins(-1)`, the ruins in view.
- `G.ruinList` holds every ruin ever seen (up to 64; filled at G.java:113, and never by splashers), but only `pickSrp` reads it. A soldier that walks away from a free ruin forgets it.

**Rule.**
- (a) Explore targets: draw up to 8 random tiles and take the first whose `G.mem` SEEN bit (`G.SEEN`, bit 0) is 0. If none is unseen, keep the last draw. Prefer our own half while it still has unseen tiles. Give an unseen target 30 rounds instead of 60, in case `Nav` can't reach a walled pocket.
- (b) Memory walk: at the end of `Soldier.turn` (Soldier.java:34), in place of `Nav.moveTo(Unit.exploreTarget())`, walk to the nearest `G.ruinList` entry that:
  - is not known to hold a tower;
  - is not `isBad`;
  - shows no enemy paint in its remembered 5x5 (paint ordinal 3 or higher in `G.mem` bits 4-6).

  Track towers on ruins with the unused bit 3 of `G.mem` (mask 8). In `G.remember`, set it for each ruin in view with a tower on it, and clear it when the ruin is in view and empty. `pickRuin` takes over once the ruin is in view.

**Candidates.** Try (a) and (b) separately, (a) first, because unseen ruins are the bigger share. Test on giver, mit, Gears, Oasis, maze, boxofchocolates and DefaultMedium, if the local map set has them.

### 2.2 Never sit without a paint tower (high; a bug)

**Evidence.**
- **10 of 22 losses** have rounds with no paint tower of ours standing (`t67`).
  - Each such stretch lasts a median 67 rounds.
  - The first one starts at a median r297 (p25: r89; Filter r27, Fossil r36, boxofchocolates r89).
  - **We never got a paint tower back in any of the 10.**
- **Against the other cases:**
  - The opponents had such a stretch in 1 of the 22 losses, for 14 rounds.
  - In our wins we had one in 2 of 59 games. The opponents had one in 19 of 59, and they mostly never recovered either (median: never).
  - With such a stretch we lost 10 of 12 games; without one, 12 of 69.
  - A median of 5.1 of our robots were alive during these stretches.
  - Ranked games only: 10 of 20 losses (`t67_ranked`).
- **What we built meanwhile.** During those stretches we completed **18 towers, all money towers**, at 950-4733 chips (`t67`, second table):
  - 6 on new ruins: Filter r31 and r146; Fossil r36, r51, r62 and r88.
  - 12 rebuilt on ruins where our money towers had stood: Filter 4, Fossil 4, MoneyTower 2 (one at r298 with 1 tower and 3690 chips) and Piglets2 2.

**Why it happens.**
- **Tower memory only grows.** `G.remember` calls `noteTower` for every ally tower in view (G.java:118-121). A dead tower is dropped (`G.forgetTower`, G.java:137) only in `Unit.refill` (Unit.java:32), when the robot walks up to it for paint, and in `Tower.churn`. So soldiers keep counting a dead paint tower.
- **`Soldier.wantType`** (Soldier.java:102-118) returns PAINT for `pt == 0` only when the soldier knows every tower (`pt + mt >= n`); otherwise `n < 6` returns MONEY. A soldier that remembers the dead paint tower also gets MONEY. Either way the answer is money.
- **A rebuild repeats the old type.** `workRuin` reads the old money marks (`readMarks`, Soldier.java:165), and `Unit.rebuild` (Unit.java:74-84) and `Tower.churn` complete money only. `wantType` isn't even consulted for the 12 rebuilds.

**Rule.**
- (a) `G.remember`: forget a remembered tower whose tile is in view and holds no ally tower. Note the round a paint tower was found gone (`G.lostPaint`).
- (b) `wantType`: with `pt == 0`, return PAINT once the soldier has seen a paint tower die (narrow), or also from r100 on (broad). Keep the `pt + mt >= n` guard only for the opening.
- (c) `workRuin`: if `wantType()` says PAINT for that reason, the ruin's marks read MONEY, and the soldier holds at least 100 paint, re-mark the ruin as a paint tower (`markTowerPattern` overwrites marks and costs 25 paint).
- Leave `Unit.rebuild` alone, because a money rebuild still brings 500 paint at once. One option to test later: skip it while `G.lostPaint` is set.

**Candidates.** (a)+(b) narrow first, then broad, then add (c). This is the cheapest rule here. A side effect of (a): robots stop walking to dead towers for paint.

### 2.3 Moppers clean contested ruins (medium-high; extends study 6 rule 2.1c)

**Evidence.**
- **Our half at r100** (`t69`, losses). 22 free ruins held 1-4 enemy tiles:
  - Of the 24 tiles in each 5x5, **we already had a median of 19.5**.
  - The enemy paint never went away (median: never clean).
  - Over the next 50 rounds our moppers mopped inside the 5x5 a median of 0 times, while our soldiers spent a median of 19 turns within Chebyshev 2. They wait beside these ruins.
  - We built 5 of the 22 later, they built 6.
- **More enemy paint.** With 5-12 enemy tiles at r100 there were 12 such ruins, and they built 10 of them. At r150 our half had 37 contested free ruins in all: we built 4, they built 25.
- **The other way round.** On 10 ruins in their half, our paint covered 1-4 tiles at r100. It was gone after a median of 83.5 rounds, and they built 7 of the 10. In our wins we had 54 ruins of the 1-4 kind; they were clean after a median of 123 rounds, and we built 36.
- **Study 6 rule 2.1c (t74) works where the moppers are.** Mopping next to a free ruin went from 28.9% of all our mopper cleaning (t70) to 39.6% (t74) (`t73`). But:
  - we field half their moppers (2.9 against 5.8 alive in r101-200);
  - our first mopper comes at r89 against their r34 (`Tower.choose`: `if (r < 80) return UnitType.SOLDIER;`);
  - our moppers spend 12.3 of every 100 turns at an open ruin (Chebyshev at most 3), theirs 16.2 (`t44`).
- **Barcode** is the clearest case (`t79`, `t80`; slifland, a t70 game):
  - Ruin (34,13), in their half, sat at 20 of our tiles and 4 of theirs from r50 to r150. Our soldiers saw it on 66 turns and never marked it, because `pickRuin` drops contested ruins.
  - We had no mopper before r137. Theirs mopped 24 of our tiles there before r200, and they built the ruin at r377.
  - In our half, they built on 7 ruins, and our moppers mopped there 0 times before r201.

**Rule.**
- `Mopper.target` gets a new fallback before `Unit.exploreTarget()` (Mopper.java:17). The mopper goes to the nearest `G.ruinList` ruin that:
  - has no tower (bit 3 from 2.1b);
  - holds 1-8 enemy tiles in its remembered 5x5 (`G.mem` paint ordinal 3 or higher);
  - holds at least as many of our tiles as theirs.

  Our half first, meaning near one of our known towers. Once it arrives, t74's +40 does the rest. Scan a few `ruinList` entries per turn and cache the best, to save bytecode.
- Optional: a soldier blocked at a ruin (`ruinBlocked > 5`) sends the ruin's location to the tower it refills at (robot to tower is allowed). The tower's next unit is then a mopper, told the location when it spawns. Today we use no messages at all.
- Optional: splashers take the same target, since a splash overwrites enemy paint within d2 2 of its centre.

**Candidates.** Start with the mopper memory fallback alone. Two earlier versions failed locally: study 6 2.1b (soldiers keep ruins with at most 4 enemy tiles, t73) and 2.2 (ruin denial, t80). This rule changes only where idle moppers go.

### 2.4 Turn idle chips into paint towers (medium)

**Evidence.**
- Study 5's gap is still open. In the losses we stand on 1 paint tower from r25 to r400, while they reach 2 at r150 and 4 at r400. We hold at least 3000 chips in 40% of r101-400; they do in 1% (`t60`, `t76`). The worst games:

  | game | rounds r101-400 at 3000+ chips |
  |---|---|
  | boxofchocolates | 100% |
  | Barcode | 84% |
  | Justice | 77% |
  | Crab | 75% |
  | lighthouse | 73% |
  | DefaultMedium | 72% |
  | mit | 65% |

- **The chip rule doesn't reach this.**
  - At our first mark on new-ruin builds #3-#7, median chips were 820-1180 (`t66`).
  - With at least 3 towers standing at the mark, 1500+ chips (y170's rule) held on only 1-3 marks per build index, and 2000+ (the t70/t74 rule) on 0-3 (`t75`).
  - The chips pile up later, once no new ruin gets marked (2.1, 2.3). By then `wantType` is no longer called.
- **Churns.** We churn 227 times in the losses (they churn 45) and rebuild 223 of those towers as money towers (`t42`). A churn turns 1000 chips into 500 paint, once. A money tower rebuilt as a paint tower turns the same 1000 chips into 500 paint plus 5 a round, plus 3 per active SRP.
- **Justice shows the endgame:** no free ruin, 1 paint and 5 money towers, and 3000-6870 chips from r150 on.

**Rule.**
- Trigger: chips at least 3000 and fewer known paint towers than one per 3 towers.
- A soldier with at least 100 paint and no ruin repaints the 5x5 of a standing L1 money tower to the paint pattern. 16 of the 24 tiles differ, so that costs about 80 paint.
- `Tower.churn` (Tower.java:23-40): an L1 money tower disintegrates when the paint pattern around it is complete and an ally is adjacent. It doesn't need to be drained first.
- `Unit.rebuild` (Unit.java:74-84) completes PAINT when the paint pattern is intact.

**Code:** `Soldier.turn` (a new step before `srpTurn`, Soldier.java:29), `Tower.churn`, `Unit.rebuild`.

**Candidate:** as above. Study 6 2.1a (rebuild any type, t72/t79) failed. Here the paint rebuild fires only on a pattern we painted on purpose.

### 2.5 Lower priority
- **`Mopper.nearRuin`** (Mopper.java:66) counts every ruin in view, including those under enemy towers, because `G.ruins` is `senseNearbyRuins(-1)`. With t74:
  - mopping next to enemy towers rose from 2.2% of our mopping to 3.9%;
  - mopper deaths inside an enemy tower's range rose from 0.08 to 0.23 per 100 mopper-turns;
  - all mopper deaths stayed at 0.59-0.62 (`t73`; only 9 t74 games).

  A cheap variant: skip ruins with an enemy tower on them.
- **Upgrade timing is not a gap** (`t78`). Our first paint-tower upgrade to L2 comes at a median r247 and to L3 at r210 (the L3 ones are upgrades of the starting tower). Theirs come at r214 and r315. They upgrade more paint towers only because they have more.

## 3. What changed since study 6

| study 6 item | then (us / them) | now (us / them) | status |
|---|---|---|---|
| median loss round | r370 | r396 (y155 r358, t70 r395, t74 r422) | later |
| small maps (short side 25 or less) | lost 11 of 13 | lost 4 of 10 | better; each loss has its own cause (section 1) |
| towers at r100: ahead (+1 or more) / behind (-1 or less) | 28 W 12 L / 2 W 11 L | 46 W 9 L / 1 W 6 L | we open well |
| rebuild after a kill (2.1) | 47% / 96% | 30% (39 of 130) / 95% (110 of 116); median 7 / 20 rounds | open |
| our ruins not rebuilt within 50 rounds: enemy tiles 10 rounds after the kill | median 4 | median 6 (11 after 30 rounds) | open (2.3) |
| mopper turns at an open ruin (Chebyshev 3 or less) | 17-19% / 32% | 12.3% / 16.2% | gap smaller |
| mopping next to free ruins (2.1c) | - | t70 28.9%, t74 39.6% of our mopper cleaning | t74 works where the moppers are |
| first mopper (2.3) | r81 / r50 | r89 / r34 | open |
| money towers stop after 2 units (2.3) | 378 of 378 | 141 of 141 (122 built + 19 starting) | open (t81 is level with t74) |
| paint-blocked tower-turns r101-200 / r201-300 | 78.8 / 16.2, 90.5 / 44.6 | 66.9 / 19.9, 89.6 / 44.9 | paint is still the limit |
| mean chips held r101-200 | 2306 / 943 | 1888 / 927 | the 2000-chip rule spends some |
| churns (2.4) | 188 / 234 | 227 / 45 | open |
| churn blocked (tower-rounds) | | by a visible enemy 2057, by no adjacent ally 2483 | |
| deaths per 100 turns (2.5) | 0.88-0.89 / 0.42-0.54 | soldiers 0.59 / 0.28, moppers 0.81 / 0.49, splashers 0.66 / 0.21 | lower for both; the gap remains |
| soldier deaths drained within 10 rounds | 54% / 40% | 49% / 29% | |
| robot turns ending on enemy paint | 13.9% / 9.6% | 11.1% / 4.9% | |
| paint towers in the losses at r300 | 1 / 1 | 1 / 2 (r400: 1 / 4) | they build paint towers again |
| SRPs in the losses | 0 / 0 up to r300 | 2 / 4 at r300 | they lead |

The study 6 rules that failed locally (2.1a, 2.1b, 2.2, 2.3 for every tower, 2.4 and 2.5) are not proposed again. Rule 2.3 here goes the same way as 2.1c (moppers to ruins), but uses memory instead of sight.

## 4. Broken in our bot (t74; y170 differs only in the chip threshold)
1. **Tower memory never drops a dead tower except through `Unit.refill`.** `G.remember` only adds. Together with the `pt + mt >= n` guard in `wantType`, this made all 18 towers we built with no paint tower standing money towers (2.2).
2. **Rebuilds repeat the old type.** Leftover marks (`readMarks`), `Unit.rebuild` and churn all rebuild money towers. With no paint tower standing, the churn loop keeps rebuilding money: 12 of those 18 towers (2.2).
3. **`Soldier.pickRuin` uses only the ruins in view.** `G.ruinList` is filled (but never by splashers), and only `pickSrp` reads it (2.1).
4. **`Unit.exploreTarget` picks a uniformly random tile.** On big walled maps whole regions of our own half stay unseen for 100-400 rounds (mit, Gears, giver) (2.1).
5. **`Mopper.nearRuin` counts the ruins under enemy towers** (2.5; low confidence).
6. **Still open from study 6:**
   - money towers stop after 2 units (141 of 141);
   - we never build defense towers;
   - `Sym` is computed but only shows up in the tower's indicator string;
   - robots and towers exchange no messages;
   - `Tower.choose` spawns only soldiers before r80. The small-map data does not support changing that.

## 5. Suggested test order
1. 2.2 (a)+(b). It is a bug, a few lines, and doesn't touch the opening. Then add 2.2 (c).
2. 2.1 (a), then 2.1 (b).
3. 2.3, the mopper memory fallback.
4. 2.4, the conversion. It goes last because it is the largest change and touches churn.
5. 2.5, if a slot is free.

Build on y170. Suggested candidates:
- Forget dead towers on sight. With no paint tower known, after seeing one die (and in a second version also from r100 on), the next new tower is a paint tower (2.2 a+b).
- The same, plus re-marking money-marked ruins as paint while no paint tower stands (2.2 c).
- Explore targets prefer unseen tiles, our own half first (2.1 a).
- Soldiers with nothing to do walk to the nearest remembered free, clean ruin (2.1 b).
- Moppers with nothing in view walk to the nearest remembered contested free ruin that we mostly hold, our half first (2.3).
- With 3000+ chips and too few paint towers, soldiers repaint an L1 money tower to the paint pattern, and it is churned and rebuilt as a paint tower (2.4).
- `Mopper.nearRuin` ignores ruins with an enemy tower (2.5).

Maps to test each rule on, if the local map set has them:
- 2.1: big walled maps (mit, giver, Gears, Oasis, maze, boxofchocolates).
- 2.3: Barcode, Money, Fossil, lighthouse and Paintball.
- 2.2 and 2.4: Filter, Fossil, MoneyTower, Piglets2 and Justice.

Study 6's small maps (CastleDefense, DefaultSmall, FourCorners) also belong in the pool.

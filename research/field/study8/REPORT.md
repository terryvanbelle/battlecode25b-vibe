# Field study 8 (2026-11-26): t74, y170, t85 and t91 on the replica since submission 66

This study uses replays only: no competitor code and no write-ups. There was no `contest.py` call. The replays had already been fetched to `~/projects/vibe/bc25b-galaxy-replays/<match>/replay.bc25`, and this study uses those up to match 3201.

The data is 31 matches since submission 66 (t74), ids 2873-3201 (\* = unranked):

| match | opponent | result | | match | opponent | result |
|---|---|---|---|---|---|---|
| 2873 | placeholder-name-2 | W 2-1 | | 3006 | geesegeesego | W 2-1 |
| 2888 | gone-whalin | W 3-0 | | 3067 | gone-whalin | L 0-3 |
| 2897 | immutable | W 2-1 | | 3080 | lobster-roll | L 0-3 |
| 2919 | immutable | L 1-2 | | 3103 | placeholder-name-2 | W 2-1 |
| 2920 | gone-whalin | W 2-1\* | | 3111 | varunvejalla | W 3-0 |
| 2921 | spaark | W 2-1 | | 3127 | scienceqiu | W 2-1 |
| 2922 | scienceqiu | L 0-3\* | | 3185 | immutable | W 2-1 |
| 2969 | spaark | W 2-1 | | 3186 | lobster-roll | W 2-1\* |
| 2970 | gone-whalin | L 1-2\* | | 3187 | spaark | W 3-0 |
| 2971 | immutable | W 2-1 | | 3188 | scienceqiu | L 1-2\* |
| 2972 | scienceqiu | W 2-1\* | | 3189 | gone-whalin | W 2-1 (g1 duplicate) |
| 2973 | subscribe-to-caterpillow | L 0-3 | | 3190 | slifland | L 1-2\* |
| 2974 | lobster-roll | L 1-2\* | | 3195 | immutable | W 3-0 |
| 2979 | scienceqiu | L 0-3 | | 3201 | immutable | L 1-2 |
| 2990 | gone-whalin | L 1-2 | | | | |
| 2998 | lobster-roll | W 3-0 | | | | |
| 3004 | lobster-roll | W 3-0 | | | | |

Game 1 of match 3189 repeats m3067g0 and is left out (`S8DUP`), so 3189 counts as 2-0 here. That makes **92 games: 51 won and 41 lost**. 27 of the losses came in ranked matches and 14 in unranked ones. The won games serve as the control.

Our bot version comes from each replay's header (`pkgs.py`):

| version | submission | matches | games | won-lost |
|---|---|---|---|---|
| t74 | 66 | 2873-2922 (7) | 21 | 12-9 |
| y170 | 67 | 2969-3006 (11) | 33 | 17-16 |
| t85 | 68 | 3067-3127 (5) | 15 | 7-8 |
| t91 | 69 | 3185-3201 (8) | 23 | 15-8 |

Two newer versions have no replica games yet:
- y195 (submission 70) is t91 plus study 7's 2.1a (explore unseen tiles first).
- y197 is y195 with ruin denial stopping at 2 of our tiles. It was crowned while this study ran and is now `src/vibe`; the rules below are written against it.

None of these games has 2.1a, the denial tuning, or study 7's 2.3 (t98/t100).

How to run:
- `lib.py` is study 7's loader, adapted. It reads these environment variables:
  - `S8VER` and `S8TEAMS` (versions and opponents);
  - `S8RANKED=1` (ranked matches only);
  - `S8SET=main|ref5|prev|all` (`prev` is study 7's set, 2641-2807, for before/after numbers);
  - `S8DUP=1` (keep m3189g1).
- t0-t78 are study 7's scripts, rerun on this set; t77 was copied but not rerun. t81-t104 are new.
- Each `tNN_*.py` writes `tNN.txt` through `./run.sh tNN_x.py`. t98 was revised to count only new ruins (see t101).
- The dumps are in the session scratchpad: `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study8/dump/mM`, with study 7's set in `.../study7/dump` and a parsed cache in `.../study8/cache`. `lib.py` points there (`SP`).
- The scratchpad can be cleared. Rebuild a dump with `~/opt/jdk21/bin/java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`, one java process at a time.

## 1. How the games were lost

### Overview
- **How they ended.** 32 of 41 by MAJORITY_PAINTED and 9 by ALL_UNITS_DESTROYED. The median loss came at **r412** (study 7: r396). By version: t74 r412 (9 games), y170 r460.5 (16), t85 r438 (8), t91 r351 (8).
- **All 9 eliminations were behind on towers at r100:**
  - Paintball r138 (spaark) and r110 (slifland);
  - Bunny r235 and r282 (gone-whalin), and r323 (scienceqiu);
  - BunnyGame r229 and Filter r230 (scienceqiu);
  - FourCorners r285 (slifland);
  - UglySweater r482 (gone-whalin).
- **Games won and lost by opponent** (`t40`): scienceqiu 5-10, gone-whalin 9-8, immutable 11-7, lobster-roll 9-6, spaark 7-2, placeholder-name-2 4-2, slifland 1-2, geesegeesego 2-1, subscribe-to-caterpillow 0-3, varunvejalla 3-0.
- **Map size** (`t40`, `t88`):
  - By short side: at most 25, we lost 7 of 9 (study 7: 4 of 10); 26-35, 16 of 35; over 35, 18 of 48.
  - By paintable area: at most 500 tiles, we lost 4 of 4; over 2500, 3 of 18.
  - Maps lost at least twice: Bunny (3 of 4); Paintball, giver, sierpinski and walalilongla (2 of 2 each); SandyBeach, UnderTheSea and rain (2 of 3 each).
- **Towers at r100, ours minus theirs** (`t40`):

  | difference | won | lost |
  |---|---|---|
  | +3 or more | 13 | 0 |
  | +1 or +2 | 28 | 14 |
  | 0 | 6 | 6 |
  | -1 or less | 4 | 21 |

  - Study 7 had 22/3, 24/6, 12/7 and 1/6. **Half the losses (21 of 41) are now behind at r100**, against 6 of 22 then.
  - When behind at r100 we went 4-21: t74 0-5, y170 2-7, t85 0-5, t91 2-4.
  - Most of those games were against scienceqiu (1-7), gone-whalin (0-5), lobster-roll (1-4) and slifland (0-2).

### Median timeline of the 41 losses
From `t0_medians`. Each cell is us / them. S / X / M = soldiers / splashers / moppers.

| round | cov % | towers | paint towers | chips | paint | units | S / X / M |
|---|---|---|---|---|---|---|---|
| r50 | 13.9 / 18.4 | 3 / 4 | 1 / 1 | 920 / 780 | 1477 / 1487 | 7 / 7 | 7/0/0 vs 6/0/1 |
| r100 | 20.8 / 24.7 | 5 / 5 | 1 / 1 | 1150 / 940 | 1332 / 2146 | 8 / 10 | 7/0/1 vs 6/0/3 |
| r150 (39) | 25.5 / 29.5 | 5 / 6 | 1 / 2 | 1540 / 1062 | 1447 / 2873 | 9 / 13 | 7/0/3 vs 8/0/5 |
| r200 (39) | 30.2 / 37.5 | 6 / 8 | 1 / 2 | 2040 / 1152 | 1485 / 3282 | 10 / 18 | 7/1/3 vs 9/1/7 |
| r300 (30) | 31.1 / 46.4 | **6.5 / 11** | 2 / 3 | 1826 / 1189 | 1971 / 4897 | **15 / 32.5** | 7/3/5 vs 12.5/7/13 |
| r400 (22) | 27.8 / 52.0 | 6 / 11.5 | 2.5 / 3.5 | 1748 / 1808 | 1856 / 7382 | 13 / 48.5 | 6.5/4.5/3 vs 15.5/13.5/17 |

### The economy curve
Paint income per round from paint towers, including +3 per active SRP. Medians, us / them (`t60`):

| paint income per round | r100 | r150 | r200 | r250 | r300 | r400 |
|---|---|---|---|---|---|---|
| losses | 10 / 10 | 10 / 12.4 | 14.3 / 20.6 | 19.8 / **36.5** | 25.4 / **50.0** | 29.2 / 68.3 |
| study 7 losses | 10 / 10 | 10 / 15 | 14.3 / 21 | 15.7 / 44 | 21.1 / 56.7 | 22.5 / 61.5 |
| wins | 10 / 10 | 12 / 10.4 | 21 / 13 | 50.6 / 14.4 | 75.1 / 14.8 | 151.6 / 25 |

- **Wins.**
  - Towers: 7 / 5 at r100, 9 / 6 at r200, 11.5 / 6 at r300.
  - Our 2nd paint tower comes at r150 and the 3rd at r250; we have 4.5 at r300.
  - SRPs: 4 / 0.5 at r300 and 8 / 1 at r400.
- **Losses.**
  - Towers: 5 / 5 at r100, 6 / 8 at r200, 6.5 / 11 at r300.
  - We have one paint tower until r250 and two at r300. They have two from r150 and three at r300.
  - The paint gap is narrower than in study 7, but it still opens at r200.

### What goes wrong
The losses split into two kinds of about equal size.

**(a) Behind at r100: 21 losses, including all 9 eliminations.**
- **The opening is slower** (`t98`).
  - Our first three new-ruin towers come at r27 / r40 / r76, theirs at r19 / r34 / r56.
  - We reach a third new-ruin tower in only 9 of the 21 games; they reach one in 18.
  - By r100 they had built 87 towers in these games, we 61 (`t86`).
- **Our first pattern is slow in every kind of game** (`t102`, all 92 games).
  - Our first new-ruin tower is built at a median r25, theirs at r19 (wins r24 / r18, losses r25 / r19.5).
  - It takes us 17 rounds from the first paint to a complete pattern; it takes them 13.
  - We start painting 3 rounds after our first robot comes within d2 20, because the soldier walks up and marks first. They start after 1 round, and in 43 of 91 games they never mark at all.
  - Our first pattern gets no second painter in 35 of 89 games, theirs in 16 of 91. While it is painted, a median 1 soldier of ours stands within d2 8, against 2 of theirs.
  - Neither side wastes paint or sits idle once painting has started (median 0 and 0).
- **Completing is not the problem.** Once a new-ruin pattern is complete, both sides build within a median 0-1 rounds, and every longer wait is a wait for chips (`t101`). The first version of `t98` showed a 36-round wait, but that was an artefact: it counted rebuilds, whose pattern was already complete around the old tower.
- **Their soldiers come for our starting paint tower.**
  - By r100 they had killed it in 9 of these 21 games; we had killed theirs in 2 (`t86`).
  - Over all 41 losses, by r100 our starting paint tower had died while theirs still stood in 8 games. That happened in 2 of our wins (`t90`).
  - In r1-100 they killed 39 of our towers, 10 of them our last paint tower (`t46`).
- **How the early sieges go** (`t89`, all losses).
  - In r1-100 our towers fell in 51% of the sieges on them, theirs in 38%.
  - While besieged, their towers spawned 73 moppers among 91 units; ours spawned 3 among 26.
  - Our attackers lost a median 30 paint per siege to their moppers; theirs lost 0 to ours.
  - 10 of the 20 sieges on our starting paint tower in r1-100 ended with its death, and none had a mopper of ours defending.
- **Our first mopper comes at a median r92, theirs at r44** (`t44`), because `Tower.choose` spawns only soldiers before r80. In these 21 games we spawned 17 moppers by r100 and they spawned 76 (sums, `t86`).

**(b) Level or ahead at r100: 20 losses.** The curves split after r100.
- **Expansion** (`t68`).
  - In the 34 losses that reach r250, they built 142 towers on new ruins in r101-250 (median 4 per game) and we built 64 (median 1.5). Study 7 had 71 against 24.
  - In that window we lost 109 towers and they lost 67. At r250 we stand on 7 towers, they on 10.
  - In our wins it is the other way round: 250 new-ruin towers for us, 137 for them.
- **Their new-ruin builds are not faster than ours** (`t74`).
  - They first see those ruins at a median r83 (we at r83.5) and build 74 rounds later (we 62.5).
  - They simply have more ruins to build on: 28 of their 142 lie in our half, against 9 of ours in theirs.
- **Unseen ruins.** At r100 our half held 86 free ruins that no robot of ours had seen; we built 42 of them later and they built 31 (`t72`). y195's unseen-first exploration targets exactly these, but no game here has it.
- **Our towers keep dying on the same ruins** (`t99`, all losses).
  - 345 of our 940 towers stood on a ruin where one of ours had already been killed, and 54-75% of them died again.
  - These repeat ruins hold **half of all our tower losses**.
  - We rebuild them as money towers. They rebuild theirs as defense towers, which kill our robots (2.1).
- **Their splashers hit our towers from out of reach** (`t104`).
  - 67% of the 53000 HP their splashers took off our towers came from d2 10 or more, outside the r²9 range of a paint or money tower.
  - For our splashers it was 47% of 12800.
  - In our wins: 70% of theirs, 45% of ours.
- **Chips sit idle less than before** (`t76`).
  - In a median loss we hold at least 3000 chips in 21% of the rounds from r101 to r400 (p75 54%); they do in 7%. Study 7 had 40% against 1%.
  - In our wins: 5% against 17%.

**In both kinds of loss:**
- **Deaths per 100 robot-turns** (`t41`): soldiers 0.71 against 0.45, moppers 0.95 against 0.48, splashers 0.71 against 0.36. 50% of our dead soldiers had been drained by an enemy mopper in their last 10 rounds; for theirs it was 28%.
- **Where the fighting is** (`t71`).
  - In r101-300 their soldiers spend 26-30% of their turns in our half; ours spend 11% in theirs.
  - 72% of their soldier deaths happen in our half; 29% of ours happen in theirs.
- **The exchange** (`t82`, sums over the losses).
  - Towers killed 627 of our robots and 622 of theirs.
  - They killed 445 of our towers; we killed 256 of theirs.
  - Their splashers did 53000 damage to our towers, ours 12800 to theirs.
- **Their defense towers** (`t94`).
  - There were 53 in our losses: 36 built by immutable and 11 by scienceqiu.
  - Per 100 tower-rounds they killed 2.75 of our robots; their paint towers killed 0.22 and their money towers 0.21.
  - Per 100 tower-rounds, our money towers were killed 0.44 times and theirs 0.13 times.
- **SRPs** (`t95`, `t97`, `t100`).
  - They complete about twice as many as we do (1046 against our 534), and about the same share reaches 50 rounds (41% against 42-43%).
  - 40% of ours are completed with enemy paint within Chebyshev 4 of the centre.
  - 37% of our SRP breaks come from our own tower painting (2.3).
- **Not gaps:**
  - targeting: the share of damage on paint towers follows their share of tower-rounds (`t93`, `t92`);
  - exploration by r100: 88.3% / 88.2% of our own half seen (`t65`);
  - finishing a completed pattern (`t101`);
  - upgrades: they upgraded money towers to L2 110 times in 19 losses, we 23 times in 12 (`t78`), but at +10 chips a round for 2500 chips that pays back slowly.

### Economy by phase
From `t30`. Medians per game over the losses, us / them.

| | r1-100 | r101-200 | r201-300 | r301-400 |
|---|---|---|---|---|
| games | 41 | 39 | 30 | 22 |
| paint from paint towers | 1000 / 1000 | **1117 / 1649** | **2223 / 4360** | 3078 / 5609 |
| chip income | 5720 / 6330 | 9280 / 11135 | **11707 / 17880** | 10271 / 21388 |
| new towers (any type) | 4 / 4 | 4 / 6 | 5 / 5 | 3 / 4 |
| of which paint towers | 0 / 0 | 0 / 1 | 0.5 / 1 | 0.5 / 1 |
| churns | 0 / 0 | 2 / 0 | 1.5 / 0 | 1 / 0 |
| SRPs completed | 0 / 0 | 1 / 2 | 1 / 2 | 1 / 4 |
| units spawned S / X / M | 10/0/1 vs 8/0/3 | 5/2/4 vs 6/1/5 | 6/3/4 vs 9/5/11 | 6/5/3 vs 7/10.5/10 |
| mean chips held | 1081 / 936 | 1604 / 1078 | 1881 / 1612 | 1797 / 2091 |
| tower-turns paint-blocked\* | 29.1% / 15.2% | **60.2% / 19.6%** | 69.7% / 44.2% | 67.9% / 60.8% |

\* the tower holds less than 200 paint while the team holds at least 1250 chips.

### Small maps
Short side at most 25: 7 losses and 2 wins (`t43`).
- **The losses:**
  - Paintball twice (spaark r138, slifland r110), both eliminations;
  - Filter (scienceqiu, r230) and FourCorners (slifland, r285), both eliminations;
  - DefaultSmall (lobster-roll, r203), Snowman (scienceqiu, r387) and Barcode (immutable, r409).
- **What happened:**
  - In 6 of the 7, their robots reached us by r14-r39 and killed one of our towers; in 5 of those the kill came at r32-r51 (DefaultSmall: r192).
  - At r100 we stood on 1-3 towers against their 2-6.
  - Their first mopper came at r15-r70. Ours came at r80-r184, or never (3 games).
  - By r100 we had spawned 7-10 soldiers and 0-1 moppers; they had spawned 6-10 soldiers and 1-6 moppers.
- **In our 2 small-map wins** (Circuit, and Barcode against varunvejalla) their first mopper also came early (r15, r50).
- Our early-mopper variants have all lost locally (t11 -59, t51 -131, sw31 -135). No small-map rule is proposed beyond 2.2 and 2.5b.

## 2. Differences, as codeable rules
Line numbers refer to `src/vibe` (= `bots/y197`). The rules are ranked by expected gain per unit of code risk.

### 2.1 Defense towers on ruins where our towers keep dying (high; new)

**Evidence.**
- **Repeat ruins** (`t99`, 41 losses). Of our 940 towers (starting towers included), 345 stood on a ruin where one of ours had already been killed:

  | earlier kills of ours on the ruin | towers | killed | median life (rounds) | share of our tower losses |
  |---|---|---|---|---|
  | 0 | 595 | 38% | 86 | 51% |
  | 1 | 181 | 54% | 40 | 22% |
  | 2 or more | 164 | 75% | 29.5 | 28% |

  - We built 308 money towers and 37 paint towers on these ruins, and **no defense tower**. We built no defense tower anywhere in the losses (`t94`, `t30`), and `notes.tsv` records no defense-tower test.
  - Our money towers on repeat ruins were killed 62% of the time, after a median 33.5 rounds, and killed 0.86 enemy robots each. At 20 chips a round, 33.5 rounds earn 670 chips; the tower cost 1000.
  - Their towers on repeat ruins were killed only 29-30% of the time.
- **Where they put defense towers** (`t96`).
  - 51 of their 53 defense towers in our losses came after r100.
  - 40 of those 51 came right after one of their towers was killed on that ruin: 19 after a defense tower, 13 after a paint tower, 8 after a money tower. Another 8 went on new ruins, 2 on ruins taken from us, and 1 followed a churn.
  - In 26 of the 51, one of our robots stood within d2 20 the round before. For their paint towers that was 48 of 190, and for their money towers 96 of 643.
  - In our wins, all 50 of their defense towers followed a kill on the ruin.
- **What their defense towers do** (`t94`, `t99`).
  - On repeat ruins they lived a median 112 rounds (48% were killed) and **killed 4.62 of our robots each**. Their money towers on repeat ruins killed 0.32 each; ours killed 0.86.
  - In our wins their 50 defense towers still killed 8.30 robots each (72% were killed, after a median 93 rounds).
  - Per 100 tower-rounds: 2.75 robots killed and 741 damage, against 0.22 / 101 for their paint towers and 0.21 / 81 for their money towers.
- **Why they work** (RULES.md).
  - An L1 defense tower costs the same 1000 chips as a money tower and starts with the same 500 paint.
  - It has 2000 HP instead of 1000, shoots to r²16 instead of r²9, and hits for 40 single / 20 AoE instead of 20 / 10.
  - It earns 20 chips per hit.
  - Each one adds +5 to the single attack of every allied tower while it stands.
  - **A splasher can hit a tower from d2 16**: the splash centre may be up to d2 4 away, and it damages towers within d2 4 of the centre. That is outside a paint or money tower's r²9, but inside a defense tower's r²16. 67% of their splasher damage on our towers comes from beyond d2 9 (`t104`).

**Code.**
- `Unit.rebuild` (Unit.java:73-83) runs for every robot every turn (RobotPlayer.java:19). It re-completes a MONEY tower on any adjacent empty ruin whose money pattern is intact, so a killed money tower comes back as money at once.
- `Soldier.workRuin` (Soldier.java:196) takes the old type from the leftover marks (`readMarks`, 163-183).
- `wantType` (133-149) never returns DEFENSE. It also counts only paint and money towers (137-139), so a known defense tower would break its `pt + mt >= n` checks.
- `Tower.choose` (58-77) treats a defense tower like a money tower for spawns, and `Tower.upgrade` (102-110) never upgrades one. That can stay.

**Rule.**
- **Hot ruin:** a free ruin where one of our towers stood (our tower memory `G.towerKind` still lists it, or `readMarks` finds our leftover marks), with an enemy soldier or splasher in view. A hot ruin almost always held a tower that was killed:
  - churned towers are rebuilt at once by the adjacent helper (114 of 119 churns in r101-250 of the losses, `t68`);
  - churn needs no enemy in view (Tower.java:26).
- **`workRuin`:** after `readMarks` (196), re-mark a hot ruin as DEFENSE when all of these hold:
  - `readMarks` says MONEY or PAINT;
  - we stand on at least 4 towers;
  - we know fewer than `1 + n / 5` defense towers.

  `markTowerPattern` costs 25 paint and needs d2 ≤ 2. Set `ruinType = DEFENSE`. The defense pattern differs from both the money and the paint pattern on 12 of the 24 tiles, so the existing loop (207-228) paints 12 tiles (60 paint) and completes the tower.
- **`Unit.rebuild`:** a soldier doesn't complete money when an enemy soldier or splasher is in view and the 5x5 holds no enemy paint; it takes the ruin instead. Keep the instant money rebuild in every other case:
  - for moppers and splashers, which can't repaint;
  - for churns, which happen only with no enemy in view;
  - for ruins with enemy paint in the 5x5, which `pickRuin` drops as contested (Soldier.java:118).
- **`wantType`:** count defense towers as known (`pt + mt + dt >= n`).

**Candidates.**
- Narrow: the hot-ruin defense rebuild as above.
- Broad: from 5 towers on, every rebuild that is not a churn becomes a defense tower (same cap), whether or not an enemy is in view.

The risk is the repaint. A defense rebuild needs 6-12 rounds of painting where a money rebuild is instant, and an empty ruin can be lost meanwhile: they took 91 of the 445 ruins where our towers were killed (`t51`). Maps to test on:
- the maps lost twice or more: Bunny, walalilongla, giver, sierpinski, UnderTheSea;
- Portal, where we rebuilt ruin (29,14) as money 6 times in r139-r294 (`t67`).

### 2.2 The first tower: paint before the mark, and two painters (medium-high; new, cheap)

**Evidence.**
- **We are 6 rounds late with our first tower in every kind of game** (`t102`, 89 and 91 first towers). It is built at a median r25 against their r19 (wins r24 / r18, losses r25 / r19.5).

  | first new-ruin tower, medians | us | them |
  |---|---|---|
  | first robot within d2 20 | r3 | r3 |
  | first paint, rounds later | 3 | 1 |
  | first paint to complete pattern, rounds | 17 | 13 |
  | pattern paints | 24 | 24 |
  | games without a second painter | 35 of 89 | 16 of 91 |
  | soldiers within d2 8 while painting | 1 | 2 |
  | games without a mark | 0 of 89 | 43 of 91 |

- **It compounds** in the losses that were behind at r100 (`t98`):
  - our first three new-ruin towers came at r27 / r40 / r76, theirs at r19 / r34 / r56;
  - 9 of the 21 games got a third, against 18;
  - by r100 they had built 87 towers and we 61 (`t86`).
- **It isn't chips or completion.** For both sides the first pattern completes with 1715-1955 chips in the bank and is built within a round (`t98`, `t101`).

**Code.**
- `Soldier.workRuin` (Soldier.java:198-205): with no marks yet, the soldier walks until d2 ≤ 2, marks, and paints nothing before that (`if (ruinType == null) return true;` at 204).
- `Soldier.pickRuin` (119-122): a second soldier joins only if it already stands adjacent (`helpers >= 1 && d2 > 2` skips the ruin). The comment on 119 says two per ruin.

**Rule.**
- (a) In `workRuin`, while `ruinType == null` and d2 > 2: take `t = wantType()`, paint the nearest wrong tile of t's pattern within r²9 (as the loop at 206-228 does), and mark t once adjacent.
  - For the first tower `wantType()` is MONEY (n = 2, line 144), so the type can't change on the way.
  - Limit it to n ≤ 3 to be safe.
- (b) In `pickRuin`, while `rc.getNumberTowers() == 2`, a soldier may join a ruin that has one helper from d2 ≤ 20 (skip at 2 helpers).
  - From the third tower on, keep the adjacent-only rule. "At most 1 helper soldier per ruin" (sw11) and "join only when adjacent" (y19) both won locally for the general case.

**Candidates.** (a) alone, then (a)+(b). Both change only the first one or two towers. Test on every map, including the small ones (Paintball, Filter, FourCorners, DefaultSmall, Snowman).

### 2.3 SRPs: clear ground, and never against a money pattern (medium; new, cheap)

**Evidence.**
- **SRPs next to enemy paint mostly die** (`t95`).
  - In the losses, 216 of our 534 SRPs (40%) were completed with enemy paint within Chebyshev 4 of the centre. 23% of those reached 50 rounds; 70% were broken by the enemy.
  - The 318 with no enemy paint within 4: 56% reached 50 rounds.
  - In our wins: 438 near enemy paint, 26% reached 50 rounds; 821 clear, 64%.
  - Each SRP costs 200 chips and up to 125 paint (25 tiles at 5).
- **We break our own SRPs** (`t97`, `t100`). Of our 474 SRP breaks in the losses (counting the first wrong tile at the failing round-start check):
  - 165 (35%) were enemy paint, 163 of them from splashers;
  - 100 (21%) were tiles mopped clean by enemy moppers;
  - **175 (37%) were our own soldiers painting a tower pattern over a correct SRP tile**, at a median SRP age of 25 rounds. Of these 175:
    - 97 were beside one of our money towers that stood throughout;
    - 42 were beside a ruin that was empty when the SRP was completed and was later rebuilt as money (38 of them);
    - 20 followed the death of our money tower there, and 12 the death of our paint tower.
- **This is free SRP time, not a gap to them.** Their SRPs break the same way, only worse: 571 of their 696 breaks are their own paint.
- **Placement matters.** SRPs within Chebyshev 4 of one of our paint towers last best: 61% reach 50 rounds, against 43% next to a money tower and 33% with no ruin near (`t100`).

**Code.**
- `Soldier.pickSrp` (Soldier.java:318-333) checks the ruins within Chebyshev 4 from memory, and calls `agreesWithMoney` only for a ruin it remembers as our money tower (331). Three things slip through:
  - memory never forgets a dead tower (`G.remember` only adds, G.java:118-121);
  - `G.ruinList` lacks ruins the soldier never saw;
  - dead paint towers come back as money (`Unit.rebuild`).
- `Soldier.workSrp` (412-420) only re-checks that a ruin in view within Chebyshev 4 holds a tower of ours, of any kind.
- A soldier waiting to churn a drained money tower repaints that tower's money pattern (`Unit.repairPattern`, Unit.java:90-104, called from `Unit.refill` at 44). It paints over any SRP tile that disagrees.
- The only check for enemy paint is the 5x5 scan (`pickSrp` 336-343, `srpScan` 369).

**Rule.**
- (a) `pickSrp`: also sample the remembered paint of the ring at Chebyshev 3-4 around the centre. Sixteen tiles at even offsets keep the bytecode down; a paint ordinal of 3 or more in `G.mem` bits 4-6 is enemy paint. If any is enemy paint, skip the centre for 60 rounds. `srpScan` does the same for the ring in view.
- (b) `pickSrp`: call `agreesWithMoney` for every ruin within Chebyshev 4, whatever stands there, since any tower can come back as money. `workSrp`: do the same for a ruin in view within Chebyshev 4 that holds our money tower.
- (c) `Unit.repairPattern` (Unit.java:101): skip tiles with enemy paint, using `rc.canPaint(l)` or `!rc.senseMapInfo(l).getPaint().isEnemy()`, instead of testing only `rc.canAttack(l)` (see section 4).

**Candidates.** (b)+(c) first, because they are bug-level, then add (a). (b) gives up some SRP sites next to paint towers, which are the best ones (61%), so measure it alone.

### 2.4 Splashers hit towers from out of reach (medium-low; new)

**Evidence** (`t104`). A splash damages towers within d2 4 of a centre that lies within d2 4 of the splasher. So a splasher reaches a tower from up to d2 16, while paint and money towers shoot only to d2 9.

| splasher damage on towers (HP), by the splasher's position at the end of its turn | d2 ≤ 9 | d2 10-16 | d2 > 16 |
|---|---|---|---|
| theirs on ours, our losses (53000) | 33% | 59% | 8% |
| ours on theirs, our losses (12800) | 53% | 27% | 20% |
| theirs on ours, our wins (31400) | 30% | 64% | 6% |
| ours on theirs, our wins (45600) | 55% | 32% | 13% |

- Past d2 16 means the splasher moved after splashing.
- In the losses their splashes also did more tower damage each: a median 6.6 and 7.7 HP per splash in r151-300 and r301+, against our 0 and 1.5 (`t83`).

**Code.** `Splasher.turn` (Splasher.java:13-32) adds +30 to the splash score of a tile with an enemy tower (`towersIntoGrid`, 40-46). But it moves toward the frontier or an explore target (27) with no regard for towers. So it splashes a tower only when one happens to be in reach, and about half the time from inside the tower's range.

**Rule.** Before the move at line 27, when an enemy paint or money tower is in view (`G.enemies`) and we have at least 50 paint:
- Move to the nearest free firing tile at d2 10 or 16 from the tower: (±4, 0), (0, ±4), (±3, ±1) or (±1, ±3). The splash centre is then (±2, 0) or (0, ±2) from the tower.
- Skip tiles within r²9 of any other known enemy paint or money tower, and within r²16 of a defense tower.
- Splash when ready, and step back out of r²9 while the cooldown runs.

**Candidate.** As above. It only matters where our splashers meet enemy towers, and in the losses that is rare: 79-85% of our splashes are in our own half (`t83`). So expect a small gain. It is also the attacking side of 2.1, since their splashers do exactly this to us.

### 2.5 Lower priority
- **(a) No paint tower: the rebuild path** (`t67`).
  - 18 of the 41 losses have rounds with no paint tower of ours. The first such spell starts at a median r95 and lasts a median 148 rounds, and we never get a paint tower back (median).
  - We built 66 towers during those spells, all money: 52 on ruins where our money tower had stood, 2 on old paint-tower ruins and 12 on new ruins. Portal ruin (29,14) came back as money 6 times in r139-r294.
  - Study 7's 2.2 (a)+(b) (t86 -2, t87 -26) changed only `wantType`, so it reached only the 12 new-ruin builds. Its part (c) and the rebuild path were never tested.
  - Rule: with no paint tower known (after forgetting dead towers on sight), `Unit.rebuild` doesn't complete money, and `workRuin` re-marks money-marked ruins as paint.
  - Study 7's 2.4 (t96, -69) suggests that repainting for a paint tower costs more than it brings, so this stays low.
- **(b) A defensive mopper on damage, not on sight.**
  - In r1-100, their besieged towers spawned 73 moppers among 91 units, ours 3 among 26 (`t89`).
  - Every earlier version spawned moppers when an enemy came into sight, and all lost locally: t51 (-131), sw31 (-135), t11 (-59).
  - Narrower trigger: a tower that lost HP to a soldier or splasher this round or last, and holds at least 100 paint, spawns a mopper as its next unit, at most once per 15 rounds, also before r80. Code: `Tower.turn` / `Tower.choose` (Tower.java:10-17, 58-77); remember the last HP.
- **(c) The dry-money-tower loop.**
  - `Unit.refill` ignores a money tower's dry flag while chips ≥ 2000 (Unit.java:23). With idle chips, soldiers keep walking back to a drained money tower whose churn is blocked, either by an enemy in view (Tower.java:26) or by a broken pattern (Tower.java:31-37).
  - Our soldiers spent 11397 turns next to a drained money tower of ours in the losses and 13743 in our wins; theirs spent 8370 and 1802 (`t103`).
  - Rule: after a failed 3-round churn wait at a tower (Unit.java:42-47), honour its dry flag for 20 rounds even when churnable.

## 3. What changed since study 7

| item | study 7 (us / them) | now (us / them) | status |
|---|---|---|---|
| median loss round | r396 | r412 (t74 r412, y170 r460.5, t85 r438, t91 r351) | about the same |
| losses behind on towers at r100 | 6 of 22 | 21 of 41 (4-21 when behind) | worse: half the losses are decided by r100 (2.2) |
| small maps (short side ≤ 25) | lost 4 of 10 | lost 7 of 9 | worse |
| new-ruin towers in r101-250, losses reaching r250 | 24 / 71 (18 games) | 64 / 142 (34 games) | open; none of these bots has 2.1a |
| clean free ruin in our half at r100: rounds until a soldier comes within d2 20 | 172 | 51 (`t64`) | better |
| our own half seen by r100 | 92.5% / 88.5% | 88.3% / 88.2% (`t65`) | same |
| rounds in r101-400 with 3000+ chips, median loss | 40% / 1% | 21% / 7% (`t76`) | narrower |
| paint towers in the losses at r300 / r400 | 1 / 2, 1 / 4 | 2 / 3, 2.5 / 3.5 | narrower |
| paint income per round at r300, losses | 21.1 / 56.7 | 25.4 / 50.0 | narrower |
| losses with a spell without a paint tower | 10 of 22, first at r297 | 18 of 41, first at r95 | open, and earlier (2.5a) |
| towers built during those spells | 18, all money | 66, all money (52 on old money ruins) | open |
| tower-turns paint-blocked r101-200 / r201-300 / r301-400 | 66.9/19.9, 89.6/44.9, 94.8/56.9 | 60.2/19.6, 69.7/44.2, 67.9/60.8 | better |
| first mopper | r89 / r34 | r92 / r44 | open |
| deaths per 100 turns: soldiers / moppers / splashers | 0.59/0.28, 0.81/0.49, 0.66/0.21 | 0.71/0.45, 0.95/0.48, 0.71/0.36 | both higher; the ratio is narrower |
| soldier deaths drained in their last 10 rounds | 49% / 29% | 50% / 28% | same |
| SRPs standing at r300, losses | 2 / 4 | 1 / 3 | open (2.3) |
| defense towers | 0 / not measured | 0 / 53 in our losses, 50 in our wins | new (2.1) |
| splasher damage on towers from beyond d2 9, losses | not measured | 47% / 67% | new (2.4) |

Study 7's rules in the local tournament:
- 2.1a, explore unseen tiles first: won (y195, 16 draws), crowned.
- 2.1b, memory walk to free ruins: -88 (t89).
- 2.2, never without a paint tower: -2 narrow (t86), -26 broad (t87). Part (c) was not tested; 2.5a here takes it up.
- 2.3, moppers clean contested ruins: +32 (t98), now running as t100 on y197.
- 2.4, idle chips into paint towers: -69 (t96).
- 2.5, `Mopper.nearRuin` skips ruins under enemy towers: won (t91), crowned.
- Ruin denial stopping at 2 of our tiles: won (y197), crowned.

None of them is proposed again unchanged.

## 4. Broken in our bot (y197)
1. **No code path ever builds a defense tower.**
   - `Unit.rebuild` (Unit.java:73-83), the leftover marks (`readMarks`) and churn all rebuild money.
   - `wantType` (Soldier.java:133-149) never returns DEFENSE, and it counts only paint and money towers (2.1).
2. **SRPs get placed against money patterns.**
   - `pickSrp` checks `agreesWithMoney` only for ruins it remembers as money towers (Soldier.java:331), and `workSrp` never checks it.
   - Memory keeps dead towers, and `G.ruinList` misses ruins the soldier never saw.
   - As a result, our own tower painting causes 37% of our SRP breaks in the losses (2.3).
3. **`Unit.repairPattern` uses `rc.canAttack`** (Unit.java:101). canAttack is true on enemy paint, where a soldier attack spends 5 paint and paints nothing, and each such "repair" restarts the churn wait (Unit.java:44). Measured, the waste is small: 435 such turns in 41 losses (`t103`).
4. **`G.forgetTower` loses track of dry flags.** It moves the last tower into the freed slot (G.java:137-141) without its `Unit.towerDry` flag (Unit.java:10), and `noteTower` doesn't reset the flag of a reused slot. After any forget, dry flags belong to the wrong towers.
5. **Comments that don't match the code.**
   - `pickRuin` says two soldiers per ruin; the code allows one, plus any already adjacent (Soldier.java:119-121).
   - `Tower.choose` says "S X X M"; the paint-tower cycle is S X X M S X (Tower.java:62-66).
   - `enemyNear` (Tower.java:60-61) is computed and never used.
6. **Still open from studies 6 and 7:**
   - tower memory drops a dead tower only in `Unit.refill` and churn, so `wantType` counts dead towers;
   - money towers spawn 2 units and stop, because the third, a splasher, needs 300 paint and only 200 is left;
   - `Sym` only shows in the tower's indicator string;
   - robots and towers exchange no messages;
   - no mopper before r80.

## 5. Suggested test order
1. 2.2 (a), painting before the mark. A few lines, and only the opening. It goes first because it is the smallest change; 2.1 has the larger expected gain.
2. 2.1, the hot-ruin defense rebuild (narrow), then the broad version.
3. 2.3 (b)+(c), then (a).
4. 2.2 (b), a second painter on the first tower.
5. 2.4, the splasher stand-off.
6. 2.5, if a slot is free.

Build on y197. Suggested candidates:
- Soldiers paint the first tower's pattern while walking up to mark it (2.2a).
- Killed towers rebuilt with an enemy soldier or splasher in view become defense towers, from 4 towers on and up to 1 + n/5 of them (2.1 narrow). Every non-churn rebuild from 5 towers becomes one (2.1 broad).
- SRP centres agree with the money pattern of every ruin within Chebyshev 4, and `repairPattern` paints only paintable tiles (2.3 b+c). Then also no enemy paint within Chebyshev 4 (2.3a).
- With 2 towers, a second soldier joins the first ruin from d2 20 (2.2b).
- Splashers hit enemy paint and money towers from d2 10-16 (2.4).

Maps to test each rule on, if the local set has them:
- 2.1: Bunny, walalilongla, giver, sierpinski, UnderTheSea, Portal.
- 2.2: all maps, including Paintball, Filter, FourCorners, DefaultSmall and Snowman.
- 2.3: headphones, UnderTheSea, giver, TheBest, walalilongla (the losses with the most SRPs, `t0`).

## Summary: the top three
1. **Defense towers on hot ruins (2.1).**
   - Half our tower losses happen on ruins where we had already lost a tower. We put money towers back there, and they die 62% of the time after a median 33.5 rounds.
   - The opponents put defense towers on exactly such ruins (40 of 51 after a kill). Those killed 4.6 of our robots each in our losses and 8.3 in our wins, against 0.3-0.9 for money towers.
   - Two-thirds of their splasher damage on our towers comes from d2 10-16, which only a defense tower covers.
   - Rule: a free ruin where our tower stood, with an enemy soldier or splasher in view, is re-marked and rebuilt as a defense tower (`Soldier.workRuin`, `Unit.rebuild`, `wantType`).
2. **The first tower 4-6 rounds sooner (2.2).**
   - We build our first tower at r25, they at r19, in won and lost games alike.
   - We mark before we paint (starting 3 rounds after first sight, against 1), and we paint alone in 39% of games (them 18%).
   - Rule: paint the pattern while walking up to mark it; with 2 towers, let a second soldier join from d2 20 (`Soldier.workRuin` 198-205, `pickRuin` 119-122).
3. **SRPs that last (2.3).**
   - 40% of our SRPs are completed near enemy paint; 23% of those reach 50 rounds, against 56% on clear ground.
   - 37% of our SRP breaks are our own tower painting, because `pickSrp` checks money-pattern agreement only for towers it remembers as money.
   - Rule: check agreement for every ruin within Chebyshev 4, re-check it in `workSrp`, skip enemy-painted tiles in `repairPattern`, then skip centres with enemy paint within Chebyshev 4 (`Soldier.pickSrp`, `workSrp`, `srpScan`, `Unit.repairPattern`).

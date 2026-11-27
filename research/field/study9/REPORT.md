# Field study 9 (2026-11-27): y195, y197, y211 and y221 on the replica since submission 70

This study uses replays only: no competitor code and no write-ups. No `contest.py` call was made. The caller suggested `contest.py fetch --new`, but the study's ground rules forbid touching the replica, and the replays had already been fetched to `~/projects/vibe/bc25b-galaxy-replays/<match>/replay.bc25`. No game was run.

**t111 (submission 74, now the champion and `src/vibe`) has no games here.** The newest fetched match is 3951, played by y221. So nothing below measures the splasher stand-off. The rules are written against t111's code, and its line numbers are used throughout.

The data is the 64 matches after study 8's last (3201), ids 3211-3951 (\* = unranked):
- the 4 late t91 matches 3211-3214;
- then y195 (submission 70), y197 (71), y211 (72) and y221 (73).

| match | ver | opponent | result | | match | ver | opponent | result |
|---|---|---|---|---|---|---|---|---|
| 3211 | t91 | subscribe-to-caterpillow | L 0-3 | | 3549 | y211 | slifland | W 3-0\* |
| 3212 | t91 | gone-whalin | L 1-2\* | | 3575 | y211 | gone-whalin | L 1-2 |
| 3213 | t91 | om-nom | L 0-3 | | 3583 | y211 | gone-whalin | L 1-2 |
| 3214 | t91 | immutable | L 1-2\* | | 3584 | y211 | placeholder-name-2 | L 1-2\* |
| 3289 | y195 | gone-whalin | L 0-3 | | 3632 | y211 | angtn | D 1-1 (g2 dup) |
| 3294 | y195 | placeholder-name-2 | L 1-2 | | 3655 | y211 | slifland | W 3-0 |
| 3304 | y195 | gone-whalin | W 2-1 | | 3659 | y211 | lobster-roll | D 1-1 (g2 dup) |
| 3305 | y195 | immutable | W 2-1\* | | 3684 | y211 | scienceqiu | L 1-2 |
| 3306 | y195 | scienceqiu | L 0-3 | | 3698 | y211 | gone-whalin | W 3-0 |
| 3307 | y195 | placeholder-name-2 | W 2-1\* | | 3702 | y211 | angtn | L 1-2 |
| 3312 | y195 | slifland | W 2-1 | | 3721 | y211 | angtn | W 2-0 (g0 dup) |
| 3323 | y195 | varunvejalla | L 0-3 | | 3735 | y211 | slifland | W 2-1 |
| 3324 | y195 | varunvejalla | L 0-3 | | 3742 | y211 | immutable | W 2-1 |
| 3340 | y197 | geesegeesego | W 3-0 | | 3771 | y221 | gone-whalin | W 3-0 |
| 3347 | y197 | angtn | W 3-0 | | 3772 | y221 | immutable | W 2-1\* |
| 3400 | y197 | lobster-roll | L 1-2 | | 3773 | y221 | spaark | L 1-2 |
| 3409 | y197 | lobster-roll | L 0-3 | | 3774 | y221 | subscribe-to-caterpillow | L 1-2\* |
| 3410 | y197 | placeholder-name-2 | L 1-2\* | | 3785 | y221 | immutable | W 2-1 |
| 3426 | y197 | angtn | W 2-1 | | 3789 | y221 | gone-whalin | W 2-1 |
| 3449 | y197 | angtn | L 1-2 | | 3790 | y221 | gone-whalin | L 1-2 |
| 3450 | y197 | varunvejalla | W 2-1\* | | 3829 | y221 | immutable | L 1-2 |
| 3467 | y197 | lobster-roll | L 0-3 | | 3830 | y221 | gone-whalin | D 1-1 (g1 dup) |
| 3479 | y211 | podemice | W 3-0 | | 3899 | y221 | subscribe-to-caterpillow | L 1-2 |
| 3512 | y211 | angtn | W 3-0 | | 3914 | y221 | subscribe-to-caterpillow | W 2-1 |
| 3513 | y211 | varunvejalla | L 0-3\* | | 3931 | y221 | subscribe-to-caterpillow | L 0-2 (g0 dup) |
| 3514 | y211 | placeholder-name-2 | L 1-2 | | 3943 | y221 | gone-whalin | W 3-0 |
| 3515 | y211 | slifland | W 2-1\* | | 3944 | y221 | scienceqiu | L 0-3\* |
| 3544 | y211 | gone-whalin | W 3-0 | | 3945 | y221 | immutable | L 1-2 |
| 3545 | y211 | varunvejalla | W 3-0\* | | 3946 | y221 | varunvejalla | W 2-1\* |
| 3546 | y211 | placeholder-name-2 | W 2-0 (g0 dup) | | 3947 | y221 | lobster-roll | W 2-1 |
| 3547 | y211 | angtn | D 1-1\* (g1 dup) | | 3948 | y221 | geesegeesego | W 3-0\* |
| 3548 | y211 | scienceqiu | W 2-1 | | 3951 | y221 | varunvejalla | W 2-1 |

Seven games repeat an earlier game exactly and are left out (`S9DUP`): m3546g0, m3547g1, m3632g2, m3659g2, m3721g0, m3830g1 and m3931g0. Each matches the earlier game in map, opponent, length, coverage, spawns and result; the engine is deterministic, and the replica replays some pairings.

That leaves **185 games: 96 won and 89 lost**.
- Ranked: 69-66. Unranked: 27-23.
- Against the six teams the study was asked about (subscribe-to-caterpillow, gone-whalin, immutable, spaark, scienceqiu and om-nom; `S9TEAMS=top`): 40-48. Against the rest: 56-41.
- y221 against those six: 21-22.

Our version comes from each replay's header (`pkgs.py`):

| version | submission | change | matches | games | won-lost |
|---|---|---|---|---|---|
| t91 | 69 | study 8's champion | 3211-3214 (4) | 12 | 2-10 |
| y195 | 70 | study 7 2.1a: explore unseen tiles first (16 draws) | 3289-3324 (9) | 27 | 9-18 |
| y197 | 71 | ruin denial stops at 2 of our tiles | 3340-3467 (9) | 27 | 13-14 |
| y211 | 72 | 128 draws for an unseen explore target | 3479-3742 (23) | 64 | 42-22 |
| y221 | 73 | study 8 2.2 (paint the first pattern on the way in, a second painter) + explore timeout 90 | 3771-3951 (19) | 55 | 30-25 |

How to run:
- `lib.py` is study 8's loader with the new dumps. It reads these environment variables:
  - `S9VER` and `S9TEAMS` (versions and opponents; `S9TEAMS=top` = the six teams above);
  - `S9RANKED=1` (ranked matches only);
  - `S9SET=main|prev|all` (`prev` is study 8's set, 2873-3201, for before/after numbers);
  - `S9DUP=1` (keep the seven repeats).
- t0-t104 are study 8's scripts, rerun on this set; those without a `.txt` were not rerun. t105-t118 are new.
- Each `tNN_*.py` writes `tNN.txt` through `./run.sh tNN_x.py`. `S9SET=prev ./run.sh t111_denied.py t111_prev.txt` writes study 8's set to a separate file (done here for t106, t110, t111 and t117).
- The dumps are in the session scratchpad: `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study9/dump/mM`. Study 8's set is in `.../study8/dump`, and the parsed caches are in `.../study9/cache` and `.../study8/cache`. `lib.py` points there (`SP`).
- The scratchpad can be cleared. Rebuild a dump with `~/opt/jdk21/bin/java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`, one java process at a time.

## 1. How the games were lost

### Overview
- **How they ended.** 69 of the 89 losses ended by MAJORITY_PAINTED and 20 by ALL_UNITS_DESTROYED (study 8: 32 and 9 of 41).
  - The median loss came at **r400** (study 8: r412).
  - On maps of up to 900 paintable tiles it came at r307; on larger maps at r446.
- **Games won and lost by opponent** (`t40`): angtn 14-7, geesegeesego 6-0, gone-whalin 21-14, immutable 11-10, lobster-roll 4-10, om-nom 0-3, placeholder-name-2 8-9, podemice 3-0, scienceqiu 3-9, slifland 12-3, spaark 1-2, subscribe-to-caterpillow 4-10, varunvejalla 9-12.
- **Map size** (`t40`), won-lost:

  | paintable tiles | won-lost | | short side | won-lost |
  |---|---|---|---|---|
  | up to 500 | 6-16 | | up to 25 | 9-23 |
  | 501-900 | 12-23 | | 26-35 | 24-39 |
  | 901-1600 | 23-25 | | over 35 | 63-27 |
  | 1601-2500 | 25-17 | | | |
  | over 2500 | 30-8 | | | |

- **Towers at r100, ours minus theirs** (`t40`):

  | difference | won | lost |
  |---|---|---|
  | +3 or more | 18 | 8 |
  | +1 or +2 | 51 | 26 |
  | 0 | 13 | 23 |
  | -1 or less | 14 | 32 |

  - **57 of the 89 losses were level or ahead at r100.** In study 8, 21 of 41 were already behind then. The opening is no longer where most games are lost.
  - Their tower lead for good comes at a median **r173** (p25 r99, p75 r270). It comes by r100 in 25 losses, in r101-200 in 25 and later in 38 (`t107`).
  - In the 50 rounds before that lead, they built 161 towers and lost 71 to kills; we built 105 and lost 105 (`t107`).

### Median timeline of the 89 losses
From `t0_medians`. Each cell is us / them. S / X / M = soldiers / splashers / moppers.

| round | cov % | towers | paint towers | chips | units | S / X / M | SRPs |
|---|---|---|---|---|---|---|---|
| r50 | 16.3 / 17.4 | 4 / 4 | 1 / 1 | 920 / 830 | 7 / 7 | 7/0/0 vs 5/0/1 | 0 / 0 |
| r100 | 22.5 / 24.9 | 5 / 4 | 1 / 1 | 1190 / 920 | 8 / 10 | 7/0/1 vs 6/0/3 | 0 / 0 |
| r150 (85) | 28.2 / 31.3 | 5 / 6 | 1 / 2 | 1950 / 1075 | 9 / 14 | 6/1/2 vs 7/1/5 | 0 / 0 |
| r200 (82) | 29.3 / 37.5 | 5 / 6 | 1 / 2 | 2179 / 1315 | 8.5 / 18 | 5/1/3 vs 8/2/7 | 0 / 0 |
| r300 (63) | 31.2 / 45.0 | 6 / 9 | 1 / 3 | 2580 / 1580 | **11 / 28** | 5/2/3 vs 8/5/11 | 0 / 2 |
| r400 (45) | 27.0 / 54.8 | 6 / 10 | 2 / 3 | 2810 / 1458 | **9 / 45** | 4/3/2 vs 10/12/17 | 0 / 4 |

From r100 to r400 our robot count stays at 8-11 while theirs goes from 10 to 45. Meanwhile our chips climb from 1190 to 2810, and theirs stay at 900-1600.

### The economy curve
Paint income per round from paint towers, including +3 per active SRP for each paint tower. Medians, us / them (`t60`):

| paint income per round | r100 | r150 | r200 | r250 | r300 | r400 |
|---|---|---|---|---|---|---|
| losses | 10 / 10 | 10 / 12.8 | 11.7 / 15 | 15 / 21.1 | **15.8 / 35.3** | 19.8 / 74 |
| study 8 losses | 10 / 10 | 10 / 12.4 | 14.3 / 20.6 | 19.8 / 36.5 | 25.4 / 50.0 | 29.2 / 68.3 |
| wins | 10 / 10 | 10.2 / 10 | 23.9 / 11 | 48.1 / 11.2 | 64.9 / 15 | 83.3 / 35.9 |

- **Losses.**
  - We have one paint tower up to r300 and two from r350, with no active SRP at any checkpoint.
  - They have two paint towers from r150 and three from r300, and 2-4 SRPs from r300.
  - Past r150 our income is lower than in study 8's losses at every checkpoint.
- **Wins.**
  - We have 2 paint towers at r150, 3 at r250 and 5 at r300.
  - SRPs: 1 / 2 / 3 at r200 / r250 / r300.
  - Their income stays at 10-15 until r300.

### What goes wrong
Most losses are level at r100 and slip away in r100-300. Four things go wrong, and they feed each other.

**(a) Our tower patterns get blocked, and nobody clears them** (`t111`, `t69`, `t44`).
- **Attempts.** In the losses we started 1008 tower attempts (median 8 per game); they started 1391 (12).
  - We completed 42%, they 66%.
  - We abandoned 52%, they 34%. 70% of our abandoned attempts were blocked by enemy paint, with a median 4.5 enemy and 20 own tiles in the 5x5; 49% of theirs were.
- **Attempts that met enemy paint.** 523 of ours (52%) met an enemy tile in the 5x5, and we completed 16% of them. 603 of theirs (43%) did, and they completed 52%.
- **A cleaner in view decides it.** No attempt of either side that met enemy paint was completed without an own mopper or splasher in view of the ruin after the first enemy tile.
  - 252 of our 523 had neither (48%); 56 of their 603 had neither (9%).
  - With a splasher in view we completed 29% (of 192), and with a mopper 34% (of 235). They completed 59% (of 406) and 58% (of 535).
- **Cleaning.** Their moppers and splashers removed 26440 enemy tiles inside free ruins, moppers 13145 of them. Ours removed 15089, moppers 4547.
  - Their moppers had 382586 turns in these games, ours 89804.
  - Per 100 turns our moppers mop as many tiles as theirs (14.3 against 10.7).
- **Paint.** 52955 paint went into our abandoned attempts (theirs 43270).
  - 31225 of it was spent after the first enemy tile, on attempts we then gave up: a median 255 per game (theirs 17855).
- **Contested ruins at r100** (`t69`). 209 free ruins in our half had enemy paint in the 5x5.
  - We built 47 of them first, they 92.
  - The 103 with 1-4 enemy tiles held a median 20 of our tiles, and more than half were never cleaned. Our mop actions in their 5x5 over the next 50 rounds: a median 0, while our soldiers spent a median 8 turns beside them.
  - In their half of the same games, 177 free ruins had our paint in the 5x5. They built 115, we 20. The 63 with 1-4 of our tiles were clean after a median 74 rounds.

**(b) Our last paint tower dies, and we never build another** (`t106`, `t67`, `t114`, `t51`, `t46`).
- **Last paint tower lost for good.** In 43 of 89 losses our last paint tower died for good, at a median r173 with 5 of our robots alive. That happened in **0 of our 96 wins**. Their last paint tower died for good in 4 of our losses.
  - All 20 eliminations lost it first, at a median r138.
- **Spells without a paint tower.** 48 losses had one (study 8: 18 of 41), against 10 for them (`t67`).
  - Ours began at a median r138.5, and in the median such game we never had a paint tower again.
  - Their spells ended after a median 69 rounds.
- **What we built in those spells.** We built 91 towers, **all money**:
  - 69 on ruins where our money tower had stood (churns and `Unit.rebuild`);
  - 21 on new ruins;
  - 1 on an old paint-tower ruin.
- **What is left on the ruin.** When our last paint tower was killed, its ruin still held a median 9.5 of its 24 pattern tiles, with no enemy tile (`t114`).
  - 31 of those 58 ruins were never built on again, and 13 went to them.
- **Rebuilds overall.** They rebuilt 86% of their 390 killed towers; we rebuilt 44% of our 743. They took 154 of our ruins, at a median 83.5 rounds after the kill; we took 2 of theirs (`t51`).
- **When it is killed.** Our last paint tower was killed 14 / 18 / 26 times in r1-100 / r101-200 / r201+. Theirs was killed 8 / 2 / 1 times (`t46`).

**(c) Chips without paint, and robots stuck at low paint** (`t30`, `t76`, `t106`, `t110`, `t116`, `t117`).
- **Paint-blocked towers.** Our towers hold less than 200 paint while we hold 1250+ chips in 67% / 84% / 85% of tower-turns in r101-200 / r201-300 / r301-400 (study 8: 60 / 70 / 68%). Theirs: 32 / 44 / 52%.
  - Every tower of ours holds under 200 paint in 55% of all rounds of the losses (theirs 30%). We hold a median 2310 chips in those rounds.
- **Idle chips** (`t76`).
  - In a median loss we hold 3000+ chips in 35% of the rounds from r101 to r400 (p75 63%); they do in 2%. Study 8 had 21% against 7%.
  - In our wins: 4% against 14%.
- **Stuck robots** (`t117`).
  - In r101-200 / r201-400, 11.5% / 13.3% of our robot-turns were low on paint (below 10% of capacity), against 6.4% / 8.3% of theirs.
  - 8.4% / 9.7% of ours were stuck (low, on the same tile, no paint gained), against 3.8% / 5.2%.
  - A paint-holding (50+) own tower was in sight for 0.7% / 1.0% of our robot-turns (theirs 0.6% / 0.6%), and within d2 100 for 2.5% / 3.5% (1.3% / 1.5%). Most of our stuck turns have no tower with paint anywhere near: it is famine, not routing.
  - In r201-400 we had 186898 robot-turns, they 460953.
- **Soldier activity** (`t116`). Soldier-turns at 0 paint: 5.3% / 6.5% against 1.5% / 2.5%. The share of soldier-turns with no action at all is about the same on both sides (57-75%).
- **Towers with no robot.** 22 losses have rounds in which we stand on towers with no robot at all; they have none (`t106`).
- **On one tower we stop building** (`t110`).
  - 46 losses had an episode on one tower or none; they had 5 in those games.
  - The 13 first episodes that ended in elimination began at a median r170, with 1720 chips and 3 soldiers holding 74 paint. We knew 7 free ruins, 2 of them clean, the nearest clean one at d2 26.
  - **We built nothing in the median 80 rounds that followed.** In the first 60 rounds, 75% of the soldier-turns had no action and 15.5% were at 0 paint; 9.9% were spent on a ruin.
  - Their 5 episodes all recovered, within a median 6 rounds; their remaining tower was a paint tower in all 5.
- **Example: m3790g2** (gone-whalin, defensetower). Our last tower fell at r88. At r90 we had no tower, 2640 chips and 4 soldiers holding 48-112 paint, 245 in all; one pattern needs at most 120. 11 clean free ruins stood on the map. The soldiers kept painting ground until they ran dry, and the last one died at r142.
- **Example: m3450g1** (varunvejalla, catface, eliminated at r246). Soldiers at 3-7 paint stood still for 30+ rounds at d2 17-34 from our paint tower, which held 100-250 paint (section 4).

**(d) They outnumber us and fight in our half** (`t45`, `t41`, `t47`, `t71`, `t82`, `t89`, `t91`, `t94`, `t95`, `t104`, `t118`).
- **Robots alive per round, r201-300** (S/M/X): 5.3/3.7/1.9 against 8.2/9.7/3.8 (`t45`).
  - In the losses our soldier count falls from 7.1 (r51-100) to 5.3 (r201-300). In our wins it rises from 8.0 to 12.8.
- **Paint drain** (`t47`, `t41`, `t91`).
  - Their moppers drain 420 / 750 paint per game from our robots in r101-200 / r201-300; ours drain 130 / 255 from theirs.
  - 58% of our dead soldiers had been drained in their last 10 rounds, against 27% of theirs.
  - Our soldiers ran dry 0.66 times per 100 turns, theirs 0.37. 74% of ours had been drained in the 10 rounds before, against 29% of theirs.
  - Deaths per 100 robot-turns: soldiers 0.83 against 0.47, moppers 0.93 against 0.67, splashers 0.91 against 0.44.
- **Where they fight** (`t71`).
  - In r101-300 their soldiers spend 22-25% of their turns in our half; ours spend 12-15% in theirs.
  - 67% of their soldier deaths happen in our half, against 36% of ours in theirs.
- **The exchange** (`t82`, `t104`).
  - They killed 743 of our towers; we killed 390 of theirs.
  - Their splashers took 117400 HP off our towers and ours took 22500 off theirs. 69% of theirs came from d2 10-16, outside a paint or money tower's reach, against 28% of ours.
- **Sieges** (`t89`).
  - Our towers fell in 50 / 47 / 55% of the sieges on them (r1-100 / r101-200 / r201+); theirs in 39 / 36 / 30%.
  - Their defenders drained a median 25 / 35 / 55 paint from each attacker; ours drained 0 / 0 / 5.
  - Even with a mopper of ours in reach, our towers fell in 54% of the sieges.
- **Kill rates** (`t94`). Per 100 tower-rounds, our paint towers were killed 0.34 times and theirs 0.08 times. For money towers it was 0.43 against 0.18.
- **SRPs** (`t95`). Enemy paint or mops broke 52% of our SRPs in our own half, against 7% of theirs in theirs.
- **Placement is not the cause** (`t118`). Here f = the share of the way from our start towers to theirs.
  - 92% of the towers we built in the losses stood in our own half (1096 of 1185; f < 0.5).
  - Deep in our half (f < 0.35), our paint towers were killed 67% of the time and money towers 47%. Theirs: 10% and 22%.
  - They built 510 of their 1657 towers (31%) past the midline, in our half, and those were killed 7-22% of the time.
  - Our paint towers built 401+ d2 from any enemy tower were still killed 56% of the time (theirs 6%).
  - Our towers die where they stand: the cause is raids, not where we put them.

### How the top teams beat us
From `t108`. Medians for the lost games against each team, us / them.
- **subscribe-to-caterpillow (4-10).**
  - Their first kill on our towers comes at r49.5 (ours on theirs at r72), and 4 of the 10 losses were eliminations.
  - At r100 we stand on 2 towers to their 4. At r300 they field 13 splashers and 11 moppers to our 3 and 2.
- **gone-whalin (21-14).** A mopper swarm on a single paint tower.
  - Moppers: 5.5 at r100, 9.5 at r200, 12 at r300; ours 0, 2 and 2.5.
  - They killed one of our towers by r100 in 13 of the 14 losses, and our soldiers fell from 6 to 3.5 by r200.
- **immutable (11-10).**
  - At r100 we lead on towers (6 / 4) but trail on coverage (26.0% / 37.0%).
  - By r200 our soldiers drop from 8.5 to 3.5 while theirs rise from 7.5 to 10.
  - They built 13 defense towers in those 10 losses.
- **scienceqiu (3-9).** Their first kill on us comes at r44, and 5 of the 9 losses were eliminations. At r300 we stand on 1 tower to their 9.5.
- **om-nom (0-3).** Long games (median r536). SRP-heavy, up to 28 SRPs; coverage is level until r300.
- **spaark (1-2).** Too few games.

### Economy by phase
From `t30`. Medians per game over the losses, us / them.

| | r1-100 | r101-200 | r201-300 | r301-400 |
|---|---|---|---|---|
| games | 89 | 82 | 63 | 45 |
| paint from paint towers | 1000 / 1000 | **1043 / 1500** | **1505 / 2718** | 2110 / 6788 |
| chip income | 6140 / 5980 | 9111 / 9390 | 10180 / 14855 | 10927 / 21022 |
| new towers (any type, churn rebuilds included) | 4 / 4 | 4 / 4 | 3 / 4 | 2 / 3 |
| of which paint towers | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 |
| churns | 0 / 0 | 1 / 0 | 1 / 0 | 0 / 0 |
| SRPs completed | 0 / 0 | 1 / 1 | 1 / 3 | 1 / 3 |
| units spawned S / X / M | 10/0/1 vs 8/0/3 | 4.5/1/3 vs 5/2/6 | 5/2/3 vs 4/4/7 | 4/4/2 vs 7/9/10 |
| mean chips held | 984 / 930 | 1891 / 1228 | 2464 / 1419 | 3028 / 1714 |
| tower-turns paint-blocked\* | 19.0% / 15.0% | **67.4% / 31.9%** | **83.5% / 44.3%** | 84.6% / 52.3% |

\* the tower holds less than 200 paint while the team holds at least 1250 chips.

- **Spawns per tower** (`t54`, towers that lived 100+ rounds, losses).
  - Our money towers spawn 2 units at most, then stall at the splasher slot with 200 paint left. Theirs spawn up to 5, mostly moppers (329 of 674).
  - Our paint towers spawn a median 11-13.5 units, theirs 20.5-21.5.
- **New-ruin towers in r101-250** (`t68`, the 71 losses that reached r250): we built 134, they built 223. We lost 222 towers to kills, they lost 123.

### Small maps
Short side at most 25, or at most 600 paintable tiles: 23 losses and 9 wins (`t43`; study 8: 7 and 2).
- **Their first tower kill on us** came by r60 in 16 of the 23 losses.
- **First moppers.**
  - Theirs came at r4-r67 in 22 of the 23 losses.
  - Ours came at r80-r201 in 16, and never in 7.
  - By r100 we had spawned 5-13 soldiers and 0-2 moppers; they had spawned 4-12 soldiers and 0-10 moppers.
- **In our 9 small-map wins** their first mopper came early too (r10-r47 in 8), so an early mopper alone doesn't decide these games.
- Early moppers have lost locally many times (t11 -59, t51 -131, sw31 -135, t109 -38). y238, y239, y241 and y242 (longer or shorter soldier-only openings) are in the pool now. No small-map rule is proposed beyond 2.3.

## 2. Differences, as codeable rules
Ranked by the expected size on the replica, weighed by how often a rule fires in local games. The local tourney is the judge, and a rule that fires only when we are nearly dead will look flat there.

### 2.1 Blocked patterns: bring a cleaner, or let the soldier go (high; new)

**Evidence** (`t111`, `t69`, `t44`).
- **Blocked attempts.** In the losses, 523 of our 1008 tower attempts (52%) met an enemy tile in the 5x5, and we completed 16% of them. They met one in 603 of 1391 (43%) and completed 52%. In our wins we completed 38% of 887.
- **No cleaner, no tower.** No attempt that met enemy paint was completed without the side's own mopper or splasher in view of the ruin after the first enemy tile:
  - 0% of 252 ours and 0% of 56 theirs in the losses;
  - 0% of 208 ours in the wins.
- **Cleaner presence.** 48% of our blocked attempts never had a cleaner in view (study 8's set: 33%); 9% of theirs. Even with one in view, we completed 29% (splasher) and 34% (mopper); they completed 59% and 58%.
- **Who cleans.** Their moppers clear half their ruin tiles (13145 of 26440 enemy tiles removed inside free ruins). Our splashers clear most of ours: 10542 of 15089 in the losses, 23988 of 32129 in the wins. They have 4.3 times our mopper-turns.
- **The cost.** Blocked attempts we then gave up lasted a median 29 rounds and spent a median 255 paint per game after the first enemy tile.
- **At r100** our half held 209 contested free ruins. We built 47 of them first, they 92. The 103 with 1-4 enemy tiles held a median 20 of our tiles and drew a median 0 mop actions in 50 rounds.

**Code.**
- `Soldier.pickRuin` (Soldier.java:118): one enemy tile in a visible ruin's 5x5 marks the ruin bad for 50 rounds, so no new soldier takes it up.
- `Soldier.workRuin`:
  - it counts enemy tiles (241) and keeps painting the rest of the pattern (248-252);
  - it gives up after 25 blocked turns, whether or not a cleaner is near (259-260).
- `G.remember` builds the splash grid (G.java:96-101).
  - An empty tile scores 1, an enemy tile 2 (inner 3x3 only), our own paint 0.
  - A pattern holding a median 20 of our tiles therefore scores below `Splasher.splash`'s thresholds (9 before moving, 6 after; Splasher.java:20, 31) unless it holds several enemy tiles.
- `Mopper.act` (Mopper.java:46) and `Mopper.target` (90) add 40 for enemy paint within d2 8 of a visible ruin. A mopper only sees what is in view.

**Rule.**
- (a) **Splashers.** In `G.remember`, for each visible ruin with no tower whose 5x5 holds 8+ of our tiles, add 6 to `v2` for each enemy tile in that 5x5. One enemy tile in the inner 3x3 then counts like four empty ones, enough to clear the threshold. Watch the bytecode: a few ruins times 24 tiles.
- (b) **Soldiers.** In `workRuin`, when `enemyTiles > 0` and no own mopper or splasher is in `G.allies`, give the ruin up after 5 blocked turns instead of 25 (`markBad(r, 40)`). Keep 25 while a cleaner is in view.
- (c) **Towers.** A paint tower that sees such a ruin (free, 8+ of our tiles, 1+ enemy tiles) and holds 100+ paint builds a mopper next, at most once per 20 rounds.

**Expected size.**
- Medium-large. It fires in won and lost games alike (887 blocked attempts in our wins), so the local tourney should see it.
- Lifting our completion of blocked attempts from 16% to 30% would add about 0.8 towers per lost game; at r200 we are 1 tower behind (5 / 6).
- (b) frees about 20 soldier-turns on each of a median 3 abandoned blocked attempts per lost game.

**Prior attempts.**
- t73: keep contested ruins with up to 4 enemy tiles, -32.
- t74: mopper ruin weight 40, crowned. Weights 80 and 20 lost (y167, y168).
- t90 / t94 / t98 / t100: idle moppers walk to remembered contested ruins; +32 on y195, -35 on y197.
- None of them changed the splash grid or the soldier's give-up rule.

**Candidates.** (a); (b); then (a)+(b). (c) after the spawn-mix candidates in the pool (y238-y245) settle. Maps: DefaultHuge, DonkeyKong, Bunny, Portal (the losses with 10-17 abandoned blocked attempts each).

### 2.2 No paint tower: rebuild paint, not money (medium-high; study 8 2.5a, untested, now larger)

**Evidence** (`t106`, `t67`, `t114`, `t51`).
- **Last paint tower.** Ours died for good in 43 of 89 losses (median r173) and in 0 of 96 wins (study 8's set: 16 of 41 and 0 of 51). All 20 eliminations lost it first.
- **Spells.** 48 losses had a spell with no paint tower (study 8: 18 of 41), from a median r138.5, and we never had one again (median). Their 10 spells ended after a median 69 rounds.
- **What we built.** During our spells we completed 91 towers, all money: 69 on old money ruins, 21 on new ruins, 1 on an old paint ruin.
- **The old ruin.** When our last paint tower was killed, its ruin held a median 9.5 of its 24 pattern tiles. 31 of the 58 were never built on again, and 13 went to them.
- **Rebuilds overall.** They rebuilt 86% of their killed towers, we 44%.
- **Paint, not chips.** Every tower of ours holds under 200 paint in 55% of the rounds of the losses (theirs 30%), while we hold a median 2310 chips in those rounds.

**Code.**
- `Unit.rebuild` (Unit.java:74-84), run by every robot every turn, completes only a money tower.
- `Tower.churn` (Tower.java:23-41) rebuilds money.
- `Soldier.readMarks` (Soldier.java:165-185, used at 219) keeps an old money mark, and `workRuin` paints it.
- `Soldier.wantType` (135-151) returns PAINT with no paint tower only when every tower is known (`pt + mt >= n`, 141).
- Dead towers stay in `G.towerLoc` until a robot runs refill or churn at them; `G.forgetTower` is called only from Unit.java:32 and Tower.java:38.

**Rule** (study 8 2.5a, plus forgetting on sight).
- Forget a remembered tower when its tile is in view and holds no tower (`G.remember`).
- While every tower is known and none paints:
  - `Unit.rebuild` doesn't complete money;
  - `Tower.churn` doesn't fire;
  - `workRuin` treats a money mark as unmarked and marks paint (16 of the 24 tiles differ).
- Prefer the ruin of the last paint tower, which still holds a median 9.5 of its pattern tiles.

**Expected size.** Medium on the replica. It fires in about half the losses, from a median r138, and would turn up to 70 of the 91 money builds into paint towers. Locally it fires only after we lose our paint towers, so check how often that happens there first.

**Prior attempts.**
- t86 (-2) and t87 (-26) changed only `wantType`, which reaches the 21 new-ruin builds.
- t96 (-69) repainted standing money towers while chips were idle. This rule touches only dead towers, and only with no paint tower at all.

**Candidates.** Narrow: the rebuild path (`Unit.rebuild` + `workRuin`). Broad: also no churn while no paint tower stands. Maps: Jail, CastleDefense, Bread, TargetPractice, DefaultSmall, Brat (our last paint tower died for good by r66).

### 2.3 Down to one tower: build, don't paint (medium-low; new)

**Evidence** (`t110`, `t106`, m3790g2).
- **Episodes.** 46 of 89 losses had an episode on one tower or none (study 8's set: 20 of 41). They had 5 in those games, and all 5 recovered within a median 6 rounds.
- **The 13 eliminations.** Our first episodes that ended in elimination began at a median r170, with 1720 chips and 3 soldiers holding 74 paint. 2 clean free ruins were known, the nearest at d2 26.
  - We built nothing in the 80 rounds that followed.
  - 75% of the soldier-turns had no action, and 15.5% were at 0 paint.
- **m3790g2.** We had 2640 chips, 245 paint and 11 clean ruins on the map, built nothing, and were eliminated at r142.
- **No robots.** 22 losses had rounds with towers but no robot (study 8's set: 10 of 41); they had none.

**Code.**
- `Soldier.turn` (Soldier.java:25-36):
  - `pickRuin` (111-129) only looks at ruins in sight (`G.ruins`, 115);
  - `paintNear` (34, 36) spends the paint a pattern needs;
  - `deny` (29) and `siege` (30) run first.
- `workRuin` (214-218): below 10 paint it calls `Unit.refill(10000)` and returns true. With no tower to refill from, `refill` returns false (Unit.java:28) and the soldier stands still.

**Rule.** While `rc.getNumberTowers() <= 1` and chips ≥ 1000:
- no `paintNear`, `deny` or `siege`;
- a soldier with no ruin in sight walks to the nearest ruin in `G.ruinList` whose remembered 5x5 holds no enemy paint (`G.paintAt`), and builds PAINT when no paint tower stands, else MONEY;
- a soldier below 10 paint with nothing to refill from goes on to the ruin and paints what it can, instead of standing still.

**Expected size.** Small. It fires in about half the losses, but late (median r170), and locally only when we are nearly dead, so expect it to look flat there. It costs nothing in other games.

**Prior attempts.** t89 (-88) walked every idle soldier to remembered free ruins. This one fires only on one tower or none.

**Candidates.** One candidate. Maps: defensetower, Brat, Snowman, Filter, DefaultSmall, Paintball, BunnyGame (our eliminations).

### 2.4 Refill: dry flags (low; bug-level, cheap)

**Evidence** (`t117`, `t113`, m3450g1).
- **Stuck robots.** 8.4% / 9.7% of our robot-turns in r101-200 / r201-400 were stuck at low paint; theirs 3.8% / 5.2% (study 8's set: 7.7% / 7.8% against 3.9% / 3.5%).
  - Most of that is famine (2.2).
  - The part a fix can reach: stuck with a paint-holding (50+) own tower within d2 100, 2.5% / 3.5% against 1.3% / 1.5%.
- **m3450g1.** Soldiers at 3-7 paint stood still for 30+ rounds at d2 17-34 from our paint tower, which held 100-250 paint.
- **Drained L2+ money towers.** These can never churn. Our robots spent 6521 turns beside them in the losses, 5261 of them with 2000+ chips, and 35 of 89 losses had 50+ such turns. Theirs are as high (9699), so this is a bug of ours, not a gap.

**Code.** `Unit.refill` (Unit.java:14-57):
- 23: a flagged tower is skipped for 40 rounds before it is sensed (30), so a flagged tower in sight is never re-checked. An L2 paint tower makes 400 paint in 40 rounds.
- 23: the churn bypass `G.towerKind[i] == 2 && churnable()` covers every money tower.
  - Only an L1 money tower can churn (Tower.java:25), and lines 42 and 52 do check the level.
  - The starting money tower is L2 from round 1 (RULES.md:301).
  - `G.kind` (G.java:124-130) uses `getBaseType`, so the level isn't stored.
- 47 and 52 flag a tower below 20 / 40 paint.
- With every tower flagged, `refill` returns false (28), and `workRuin` (Soldier.java:214-218) leaves the soldier standing.

**Rule.**
- In the loop at 21-27, when a flagged tower is in sight, sense it and ignore the flag if it holds 50+ paint.
- A paint tower's flag expires after 10 rounds; money towers keep 40.
- Apply the churn bypass only to L1 money towers: store the level in `noteTower`, or check `t.type` when the tower is in sight.

**Expected size.** Small: 1-2% of robot-turns in the losses, more on maps with one paint tower. It fires in every game and is a few lines.

**Prior attempts.** t110 (+14 on y221), then t113 (-21 on t111): honour a money tower's flag for 20 rounds after a failed churn wait. This rule goes the other way: shorter flags that are re-checked.

**Candidates.** Re-sense plus the 10-round paint flag; then the L1-only bypass. Maps: DefaultHuge, yearofthesnake, PlumberGame, Oasis (the losses with the most stuck turns in sight of a tower, `t117`).

### 2.5 Lower priority
- **(a) Raids deep in our half** (`t118`, `t94`, `t89`, `t104`).
  - This is the largest raw gap. Deep in our half our paint towers die 67% of the time, theirs 10%.
  - 69% of their splasher damage on our towers comes from d2 10-16.
  - Every defense rule so far has lost locally: t103 -72, t109 -38, t77 -51, t51 -131, sw31 -135.
  - Wait for t111's replica games before trying another, since the stand-off changes this exchange.
- **(b) Mopper drain** (`t47`, `t41`, `t91`).
  - Their moppers drain 420 / 750 paint per game from our robots in r101-200 / r201-300; ours drain 130 / 255.
  - 74% of our soldiers that ran dry had been drained in the 10 rounds before (29% of theirs).
  - It comes from their mopper count, so it is a spawn-mix question, and y238-y245 are already testing that.
- **(c) Money towers stall after 2 units** (`t54`), at the splasher slot with 200 paint left (100 for the L2 starting tower). Theirs spawn up to 5, mostly moppers. y240 (S M X M S S) is testing a fix.
- **(d) First mopper at r89.5 against r41** (`t44`, `t43`). y238, y239, y241 and y242 are testing the soldier-only window.
- **(e) SRPs** (`t95`, `t97`).
  - The enemy breaks 52% of our home SRPs, against 7% of theirs.
  - 185 of our 532 SRP breaks were our own soldiers painting a tower pattern.
  - That is study 8 2.3 (t104 -62); no new rule.
- **(f) Our splashes flip our own pattern tiles** (`t112`): 440 tiles in free-ruin 5x5s over the losses, a median 1 per game. Too small for a rule; 2.1a will add a few.
- **(g) Idle soldiers** (`t116`). Soldier-turns with no action are 57-75% for both sides, so that is not a difference. Sitting at 0 paint is (5.3% / 6.5% against 1.5% / 2.5%).

## 3. What changed since study 8

"study 8's set" is study 8's 41 losses, measured with this study's scripts (`*_prev.txt`).

| item | study 8 (us / them) | now (us / them) | status |
|---|---|---|---|
| median loss round | r412 | r400 (r307 on maps up to 900 tiles, r446 larger) | about the same |
| eliminations among the losses | 9 of 41 | 20 of 89 | same share (22%) |
| losses behind on towers at r100 | 21 of 41 | 32 of 89 | better: the opening is no longer where most are lost |
| small maps lost | 7 of 9 | 23 of 32 | same |
| new-ruin towers in r101-250, losses reaching r250 | 64 / 142 (34 games) | 134 / 223 (71 games) | narrower per game (1.9 / 3.1, was 1.9 / 4.2) |
| rounds in r101-400 with 3000+ chips, median loss | 21% / 7% | 35% / 2% | worse |
| paint towers at r300 / r400, losses | 2 / 3, 2.5 / 3.5 | 1 / 3, 2 / 3 | worse |
| paint income per round at r300, losses | 25.4 / 50.0 | 15.8 / 35.3 | lower on both sides |
| losses with a spell without a paint tower | 18 of 41, first at r95 | 48 of 89, first at r138.5 | more often (2.2) |
| last paint tower dead for good, losses / wins | 16 of 41 / 0 of 51 | 43 of 89 / 0 of 96 | worse (2.2) |
| towers built during those spells | 66, all money | 91, all money (69 on old money ruins) | open (2.2) |
| losses with an episode on one tower or none | 20 of 41 (them 1) | 46 of 89 (them 5) | same share (2.3) |
| tower-turns paint-blocked r101-200 / r201-300 / r301-400 | 60.2/19.6, 69.7/44.2, 67.9/60.8 | 67.4/31.9, 83.5/44.3, 84.6/52.3 | worse |
| robot-turns stuck at low paint, r101-200 / r201-400 | 7.7/3.9, 7.8/3.5 | 8.4/3.8, 9.7/5.2 | a little worse (2.4) |
| tower attempts completed, losses | 48% / 66% | 42% / 66% | worse (2.1) |
| blocked attempts completed; share with no cleaner in view | 20% / 48%; 33% / 9% | 16% / 52%; 48% / 9% | worse (2.1) |
| first mopper | r92 / r44 | r89.5 / r41 | open (y238-y242) |
| deaths per 100 turns: soldiers / moppers / splashers | 0.71/0.45, 0.95/0.48, 0.71/0.36 | 0.83/0.47, 0.93/0.67, 0.91/0.44 | our soldiers and splashers die more |
| soldier deaths drained in their last 10 rounds | 50% / 28% | 58% / 27% | worse |
| SRPs standing at r300, losses | 1 / 3 | 0 / 2 | same |
| defense towers in our losses | 53 | 45 (immutable 13, scienceqiu 13) | same |
| splasher damage on towers from beyond d2 9, losses | 47% / 67% | 46% / 76% | open; t111 has no games yet |

By version on this set:
- y211 won 66% (42-22), y221 55% (30-25; 21-22 against the six top teams);
- y195 33%, y197 48%;
- t91's 4 late matches, all against top teams, 2-10 (it won 65% in study 8's set).

Study 8's rules in the local tournament:
- **2.1, defense towers on hot ruins:** -72 (t103, narrow). Not proposed again.
- **2.2, the first tower:**
  - (a) and (a)+(b) were tested as t102 and t105; y221 = t105 + explore timeout 90, crowned (submission 73).
  - y225 (pre-paint up to 5 towers, +23) and y224 (explore 75, +12) were retired at t111's crowning. On t111, y229 was flat (+3) and y230 -31.
- **2.3, SRPs:** (b)+(c) -62 (t104); (a) (t106) was retired at y221's crowning.
- **2.4, splasher stand-off:** crowned as t111 (submission 74).
  - Stand-off from 30 paint -26 (t112), from 70 flat (t114, +2), from 90 flat (t115, -1).
  - Grid and timing tunings (y231-y236) were flat or behind.
- **2.5a, no paint tower:** untested; it is 2.2 here.
- **2.5b, mopper on damage:** -38 (t109).
- **2.5c, dry flag after a failed churn wait:** +14 on y221 (t110), -21 on t111 (t113).

## 4. Broken in our bot (t111)
1. **A soldier out of paint mid-pattern can stand still for up to 40 rounds.**
   - `workRuin` (Soldier.java:214-218) calls `Unit.refill(10000)` and returns true.
   - When every known tower is flagged dry, `refill` returns false (Unit.java:28) and the soldier does nothing until a flag expires (40 rounds, Unit.java:23). See 2.3 and 2.4.
2. **Dry flags are never re-checked in sight.**
   - A flagged tower is skipped (Unit.java:23) before the only sense (30).
   - So a paint tower that has refilled stays ignored for 40 rounds, even next to the robot. m3450g1 shows it (2.4).
3. **The churn bypass ignores the level.**
   - Unit.java:23 lets any money tower through while chips ≥ 2000, but only L1 can churn (Tower.java:25).
   - The starting money tower is L2 (RULES.md:301), and so is every upgraded one. `G.kind` (G.java:124-130) uses `getBaseType`, so the level is not stored.
   - Our robots spent 6521 turns beside drained L2+ money towers in the losses (`t113`).
4. **`G.forgetTower` loses dry flags** (G.java:137-141). It moves the last slot into the freed one without its `Unit.towerDry` flag (Unit.java:10). Still open from study 8.
5. **Dead towers stay in memory** until a robot runs refill or churn at them (`G.forgetTower` is called only from Unit.java:32 and Tower.java:38). So `wantType`'s "every tower known" test (Soldier.java:141) misreads. Still open.
6. **`Unit.rebuild` completes only money** (Unit.java:74-84). Still open (2.2).
7. **`pickRuin` only sees ruins in sight** (Soldier.java:115).
   - `G.ruinList` (G.java:35) is used only by SRPs (Soldier.java:345).
   - Splashers never add to it: G.java:113 is in the non-splasher branch (2.3).
8. **Comments that don't match the code.**
   - `pickRuin` says "two soldiers per ruin at most" (Soldier.java:119); the rule is at 122-124.
   - `Tower.choose` says "S X X M" (Tower.java:66); the cycle is S X X M S X.
   - `enemyNear` (Tower.java:60-61) is computed and never used.
9. **Still open from studies 6-8:**
   - money towers stall after 2 units, because the X slot needs 300 paint and 200 is left (Tower.java:69-76); y240 is testing a fix;
   - robots and towers exchange no messages;
   - no mopper before r80 (Tower.java:63).

## 5. Suggested test order
1. **2.4:** the re-sense and the 10-round paint flag, then the L1-only bypass. It is a few lines, fires in every game and changes no strategy. 2.2 and 2.3 send robots to refill, so they lean on it.
2. **2.1:** (a), the splasher ruin bonus; then (b), giving up sooner without a cleaner; then (a)+(b). (c) after the spawn-mix candidates settle.
3. **2.2:** narrow, then broad.
4. **2.3:** expect it flat locally.

Build on t111. Suggested candidates:
- Dry flags: re-sense flagged towers in sight; paint-tower flags expire after 10 rounds (2.4).
- Splashers add 6 per enemy tile in the 5x5 of a free ruin holding 8+ of our tiles (2.1a).
- A blocked soldier with no own mopper or splasher in view gives the ruin up after 5 turns (2.1b).
- With every tower known and none painting: `Unit.rebuild` skips money, churn stops, and `workRuin` re-marks money ruins as paint (2.2).
- On one tower or none: no ground painting, `deny` or `siege`; walk to the nearest remembered clean ruin and build (2.3).

Maps to test each rule on, if the local set has them:
- 2.1: DefaultHuge, DonkeyKong, Bunny, Portal.
- 2.2: Jail, CastleDefense, Bread, TargetPractice, DefaultSmall, Brat.
- 2.3: defensetower, Snowman, Filter, Paintball, BunnyGame.
- 2.4: DefaultHuge, yearofthesnake, PlumberGame, Oasis.

Once t111 has replica games, rerun `t111`, `t104`, `t89` and `t117` with `S9VER=t111` first.

## Summary: the top three
1. **Blocked patterns (2.1).**
   - Half our tower attempts in the losses meet enemy paint. We complete 16% of those, they complete 52%.
   - No attempt by either side completes without its own mopper or splasher in view after the first enemy tile. 48% of ours never get one (study 8's set: 33%), against 9% of theirs.
   - Rule: splashers weight enemy tiles inside a free ruin we are building, and a blocked soldier with no cleaner in view gives up after 5 turns instead of 25 (`G.remember` G.java:96-101, `Soldier.workRuin` 259-260).
2. **No paint tower (2.2).**
   - Our last paint tower died for good in 43 of 89 losses and in none of 96 wins.
   - In the 48 spells without one we built 91 towers, all money, 69 of them on old money ruins. Meanwhile we held a median 2310 chips, with every tower under 200 paint.
   - Rule: with every tower known and none painting, `Unit.rebuild` and churn stop rebuilding money, and `workRuin` re-marks money ruins as paint (Unit.java:74-84, Tower.java:23-41, Soldier.java:219).
3. **Down to one tower (2.3).**
   - In 13 eliminations we sat for 80 rounds on 1720 chips and 3 soldiers holding 74 paint, knowing 2 clean free ruins, and built nothing. Their 5 such episodes recovered in a median 6 rounds.
   - Rule: on one tower or none, stop ground painting, walk to the nearest remembered clean ruin and build, and never stand still at low paint (`Soldier.turn` 25-36, `workRuin` 214-218).

The cheapest first test is 2.4, the dry-flag fix in `Unit.refill` (Unit.java:23).
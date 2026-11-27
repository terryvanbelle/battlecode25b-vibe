# Field study 10 (2026-11-27): t111 and t118 on the replica since submission 74

This study used replays only. I read no competitor code and no write-ups, made no `contest.py` call, ran no games, and edited no bots.

**t122 (submission 76, now the champion and `src/vibe`) has no games here.** The newest match is 4602, played by t118, so nothing below measures t122's dry-flag change. The rules are written against `bots/t122` and use its line numbers.

The data is the 60 matches after study 9's last (3951), ids 3999-4602 (\* = unranked):
- 42 matches by **t111** (submission 74: the splasher stand-off);
- 18 matches by **t118** (submission 75: the blocked-pattern give-up).

Matches 4569, 4579, 4594 and 4602 were fetched while the study ran and are included.

| match | ver | opponent | W-L | | match | ver | opponent | W-L |
|---|---|---|---|---|---|---|---|---|
| 3999 | t111 | gone-whalin | 1-2 | | 4287 | t111 | lobster-roll | 2-1\* |
| 4001 | t111 | gone-whalin | 2-1 | | 4288 | t111 | scienceqiu | 2-0 (g2 dup) |
| 4002 | t111 | scienceqiu | 2-1\* | | 4289 | t111 | varunvejalla | 2-1\* |
| 4003 | t111 | immutable | 1-2 | | 4309 | t111 | spaark | 1-1 (g0 dup) |
| 4004 | t111 | varunvejalla | 1-2\* | | 4325 | t111 | varunvejalla | 1-0 (g0, g1 dup) |
| 4005 | t111 | lobster-roll | 1-2 | | 4331 | t111 | scienceqiu | 3-0 |
| 4006 | t111 | angtn | 2-1\* | | 4366 | t111 | immutable | 2-1 |
| 4055 | t111 | scienceqiu | 1-2 | | 4367 | t111 | gone-whalin | 2-1\* |
| 4056 | t111 | slifland | 1-2\* | | 4368 | t111 | subscribe-to-caterpillow | 2-1 |
| 4057 | t111 | subscribe-to-caterpillow | 2-1 | | 4369 | t111 | spaark | 1-2\* |
| 4058 | t111 | placeholder-name-2 | 3-0\* | | 4370 | t111 | om-nom | 1-2 |
| 4099 | t111 | lobster-roll | 2-1 | | 4371 | t111 | scienceqiu | 1-2\* |
| 4127 | t111 | gone-whalin | 0-3 | | 4393 | t111 | spaark | 2-1 |
| 4150 | t111 | lobster-roll | 1-2 | | 4440 | t118 | immutable | 3-0 |
| 4151 | t111 | placeholder-name-2 | 2-1\* | | 4441 | t118 | gone-whalin | 1-2\* |
| 4152 | t111 | gone-whalin | 1-1 (g0 dup) | | 4442 | t118 | subscribe-to-caterpillow | 3-0 |
| 4153 | t111 | slifland | 3-0\* | | 4443 | t118 | spaark | 1-2\* |
| 4154 | t111 | scienceqiu | 1-2 | | 4448 | t118 | spaark | 2-1 |
| 4155 | t111 | podemice | 3-0\* | | 4471 | t118 | spaark | 1-2 |
| 4160 | t111 | varunvejalla | 2-1 | | 4515 | t118 | om-nom | 1-2 |
| 4222 | t111 | spaark | 1-2 | | 4516 | t118 | subscribe-to-caterpillow | 2-1\* |
| 4223 | t111 | placeholder-name-2 | 2-1\* | | 4517 | t118 | just-woke-up | 1-2 |
| 4224 | t111 | lobster-roll | 2-1 | | 4518 | t118 | gone-whalin | 2-1\* |
| 4225 | t111 | varunvejalla | 2-1\* | | 4519 | t118 | confused | 1-2 |
| 4226 | t111 | scienceqiu | 2-1 | | 4520 | t118 | spaark | 2-1\* |
| 4227 | t111 | podemice | 2-1\* | | 4523 | t118 | subscribe-to-caterpillow | 2-1 |
| 4250 | t111 | spaark | 2-1 | | 4542 | t118 | spaark | 1-2 |
| 4251 | t111 | lobster-roll | 2-1\* | | 4569 | t118 | subscribe-to-caterpillow | 2-1 |
| 4286 | t111 | spaark | 1-2 | | 4579 | t118 | confused | 0-3 |
| | | | | | 4594 | t118 | om-nom | 2-1 |
| | | | | | 4602 | t118 | immutable | 3-0 |

Five games exactly repeat an earlier one and are left out (`S10DUP`, `t119`):
- m4152g0 = m4001g1;
- m4288g2 = m4055g2;
- m4309g0 = m3773g1. That game was played by y221 in study 9's set, so the stand-off never changed it.
- m4325g0 = m4225g0;
- m4325g1 = m4004g1.

That leaves **175 games: 100 won and 75 lost**.
- **t111:** 70-51 (58%): 34-32 against the top teams and 36-19 against the rest.
- **t118:** 30-24 (56%), all against the top teams. y221 went 21-22 against them in study 9.
- **Against the eight top teams:** 64-56 (53%). Against study 9's six of them: 62-49, up from 40-48.
- **Ranked:** 59-50. **Unranked:** 41-25.
- Two games went to r2000 on maze; we won both.

| opponent | W-L now | study 9 | | opponent | W-L now | study 9 |
|---|---|---|---|---|---|---|
| spaark | 15-17 | 1-2 | | om-nom | 4-5 | 0-3 |
| subscribe-to-caterpillow | 13-5 | 4-10 | | confused | 1-5 | - |
| gone-whalin | 9-11 | 21-14 | | just-woke-up | 1-2 | - |
| immutable | 9-3 | 11-10 | | lobster-roll | 10-8 | |
| scienceqiu | 12-8 | 3-9 | | varunvejalla | 8-5 | |
| placeholder-name-2 | 7-2 | | | podemice / slifland / angtn | 5-1 / 4-2 / 2-1 | |

**How to run.**
- `lib.py` is study 9's loader with the new dumps. It reads these environment variables:
  - `S10VER` and `S10TEAMS` (versions and opponents; `S10TEAMS=top` = the eight teams above);
  - `S10RANKED=1` (ranked matches only);
  - `S10SET=main|prev|all` (`prev` = study 9's set, 3211-3951);
  - `S10DUP=1` (keep the repeats).
  - The `S9*` names are still accepted.
- t0-t118 are study 9's scripts, rerun on this set; those without a `.txt` were not rerun. t119-t125 are new.
- `S10VER=t111 ./run.sh t111_denied.py t111_t111.txt` (and the same for `t118`) splits the blocked-attempt numbers by version.
- **Dumps:** `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study10/dump/mM` (60 matches, `covMismatch` 0, dump version 3). Caches are in `.../study10/cache`; study 9's set is in `.../study9/`.
- The scratchpad can be cleared. Rebuild with `~/opt/jdk21/bin/java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`, one java process at a time.

## 1. How the games were lost

### Overview
- **By map size** (`t40`, paintable tiles, W-L; study 9 in brackets):

  | paintable tiles | now | study 9 |
  |---|---|---|
  | up to 500 | 3-7 | 6-16 |
  | 501-900 | 21-20 | 12-23 |
  | 901-1600 | 30-22 | 23-25 |
  | 1601-2500 | 32-12 | 25-17 |
  | over 2500 | 14-14 | 30-8 (worse now) |

  - By short side: 25 or less 8-15; 26-35 40-31; over 35 52-29.
  - Median loss round: r316 on maps up to 900 tiles, r417 on larger maps.
- **Towers at r100** (ours minus theirs):

  | at r100 | won | lost |
  |---|---|---|
  | behind | 8 | 32 |
  | level | 10 | 13 |
  | ahead | 82 | 30 |

  So 32 of the 75 losses were already behind at r100 (study 9: 32 of 89).
- **Eliminations:** 18 of the 75 losses. All 18 had lost their last paint tower first.
- **Last paint tower dead for good** (`t106`):
  - us in 33 of 75 losses (median r192, 5 robots alive), them in 4;
  - against the top teams, 28 of 56;
  - in our wins, 0 of 100.
- **Paint-blocked:** in 56% of the rounds of a loss, every tower of ours holds under 200 paint (theirs 28%). We hold a median 2250 chips in those rounds.

### Median timeline of the 75 losses (`t0`, us / them; median end r392)

| round | coverage % | towers | paint towers | chips | robots (S / X / M) |
|---|---|---|---|---|---|
| r100 | 21.0 / 20.6 | 5 / 5 | 1 / 1 | 1120 / 940 | 9 / 11 |
| r200 | 31.1 / 33.0 | 6 / 7.5 | 1 / 2 | 2455 / 1096 | 11 / 18 (6/9, 1/2, 3/8) |
| r300 | 31.4 / 44.5 | 6 / 10 | 1 / 3 | 2780 / 1440 | 12 / 32 |
| r400 | 28.1 / 52.4 | 6 / 11 | - | 2878 / 1370 | 10 / 40.5 |

SRPs standing at r300: 0 / 2. This is study 9's picture again: level at r100, then they turn paint into units and towers while our chips sit idle.

### Where the lead comes from (`t107`, `t122`, `t86`, `t30`, `t120`)
- **The tower lead.** Their tower lead becomes permanent at a median r197 (p25 r100, p75 r295): by r100 in 19 games, in r101-200 in 20, later in 36.
  - In the 50 rounds before it, they built 157 towers (96 on new ruins, 50 rebuilt on their own, 11 taken from us) and lost 65.
  - We built 99 (60 new, 36 rebuilt, 3 taken) and lost 87.
- **The opening, in the 32 losses behind at r100.**
  - Their 2nd and 3rd towers came at r35 and r53, ours at r41 and r63.
  - We lost 53 towers by r100, they lost 34.
  - They spawned 111 moppers by r100, we spawned 18.
- **Economy in r101-300** (`t30`):

  | | us | them |
  |---|---|---|
  | paint-blocked tower-turns, r101-200 | 61% | 32% |
  | paint-blocked tower-turns, r201-300 | 84% | 41% |
  | paint income, r201-300 | 1566 | 3329 |
  | paint towers built per 100 rounds | 0 | 1 |

  Their paint towers spawn 8 units per loss in r101-200 against our 3, and 26.5 against 7.5 in r201-400 (`t120`).
- **Army size.** In r201+ they have 3.6 times our splasher-turns (237775 against 65468) and 2.8 times our robot-turns (`t121`, `t117`).

### What goes wrong
1. **The starting towers have no pattern, die early and change hands** (`t125`, new).
   - Our starting paint tower died in 52 of 75 losses: 21 by r100, 30 by r200, median r132. Theirs died in 13.
   - In our wins, ours died in 19 of 100 and theirs in 53.
   - The killers: about 2.3 soldiers in its last 40 rounds, doing 95% of the damage.
   - Defenders: own mopper-rounds within d2 20 of it in those 40 rounds were a median **0 for us (zero in 35 of 52)** and **27 for them (zero in 0 of 13)**.
   - The 5x5 holds no pattern from r0:
     - at r80 our starting paint tower's 24 tiles are 2.7 in its pattern, 1.5 wrong colour, 18.4 empty and 1.4 enemy;
     - at death, 6.8 / 3.4 / 10.4 / 3.3.
     - 83% of the empty tiles in our killed paint towers' 5x5 had never been painted since r0 (`t124`).
   - What happened to the ruin next: we rebuilt 4 of the 52 within 50 rounds, **they took 23**, and 19 were never rebuilt.
   - Yet 27 of the 52 had no enemy tile in the 5x5 when the tower died.
   - Our starting money tower died in 47 losses (median r197). We rebuilt 1, they took 19, and 19 of the 47 had no enemy tile at death.
   - Compare paint towers built later (so with a painted pattern): at death they held 15.9 pattern tiles in the losses (theirs 20.1) and 20.1 in the wins.
2. **Ruins change hands one way** (`t114`, `t124`).
   - In the losses they rebuilt 76 of the 100 paint towers we killed as paint (60 within 50 rounds), and about 82% of the 277 money towers. We took 11 of those 377 ruins (3%).
   - They took 50 of our 155 killed paint-tower ruins and about 165 of our 550 money-tower ruins (30%).
   - In our wins it reverses: they never rebuilt 93 of 212 paint towers, and we took 27 paint and 88 money ruins.
   - At death, their killed towers held only 1.1-1.2 of our tiles in the 5x5 (in the losses).
3. **Moppers** (`t44`, `t54`, `t47`, `t123`).
   - In the losses they had 4.6 times our mopper-turns (373799 against 80891). Their first mopper came at r39, ours at r95.5.
   - Mopper share of spawns by paint towers that lived 100+ rounds: **ours 11-16%, theirs 36-48%**, in losses and wins alike.
   - Paint our robots lose to their moppers, per game, against what theirs lose to ours:

     | | r1-100 | r101-200 | r201-300 |
     |---|---|---|---|
     | losses | 110 / 0 | 325 / 135 | 860 / 250 |
     | wins | 90 / 0 | 310 / 140 | 620 / 285 |

   - **Starvation**, in r101+ of the losses, per 100 unit-turns:
     - our soldiers starve 0.75 times, theirs 0.30;
     - our splashers 0.86, theirs 0.18 (92% of our splasher deaths are starvation, and only 8% of all their r201+ deaths are by towers);
     - 72% of our starved soldiers and 65% of our starved splashers had been drained by enemy moppers in their last 15 rounds; for theirs it was 34% and 26%.
     - In the wins our death rates are the lower ones (splashers 0.24 against 0.44), so the death gap follows map control, while the mopper and drain gap does not.
   - **Refills:** our splashers leave a tower with a median 227 paint in the losses (theirs 298), because our towers are dry.
4. **Blocked patterns after t118** (`t111`, `t111_t111`, `t111_t118`).
   - Overall in the losses:
     - we completed 41% of 991 tower attempts, they 69% of 1346;
     - 50% of ours met enemy paint, and we completed 13% of those, they 53%;
     - no attempt by either side completed without its own mopper or splasher in view after the first enemy tile (0% of our 227, 0% of their 47);
     - 46% of our blocked attempts never had a cleaner in view; 8% of theirs.
   - **By version:**
     - blocked attempts completed: t111 11% of 332, t118 16% of 164;
     - completed with a splasher in view: 16% → 30%; with a mopper in view: 23% → 35%;
     - paint spent after the first enemy tile on blocked attempts we then abandoned: 387 → 281 per loss;
     - but the share with no cleaner in view is unchanged (45% → 48%).
   - **Who clears enemy tiles inside free ruins:** our moppers 4727 and splashers 6127; their moppers 13293 and splashers 9072.
5. **The stand-off works per splasher, not in total** (`t121`, `t104`). Losses, r201+ (study 9's set in brackets):
   - our splasher damage on towers rose to 50.4 per 100 splasher-turns [19.1], theirs 39.1;
   - 64% of ours now comes from d2 10-16 [27%], and only 5% from d2 9 or less [54%];
   - splashers killed 24 towers [14 in 89 games].
   - But they killed 470 of our towers and we killed 198, the same per-game exchange as before, because they field 3.6 times our splasher-turns. Our splashers still die at 0.99 per 100 turns [0.94].
6. **Small maps** (`t122`), short side 25 or less or 600 or fewer paintable tiles: 15 losses.
   - Towers: 2.5 / 3 at r100, 2 / 5 at r200.
   - Robots: 3.5 / 9 at r100, 1 / 14 at r200.
   - Our last paint tower died for good in 11 of the 15 (median r63), and we held 5227 chips at r200.
   - 13 losses lost the last paint tower for good by r130. 7 of them were on small maps: Filter r27, FourCorners r34 and r97, CastleDefense r33, Jail r47 and r63, Racetrack r51.
7. **Paint famine is still there** (`t106`, `t117`, `t76`).
   - 32 losses had a spell with no paint tower.
   - We held 3000+ chips in a median 28% of the rounds of a loss; they held that much in 4%.
   - Robot-turns stuck at low paint, us / them:
     - 7.0% / 4.2% in r101-200, 9.8% / 4.7% in r201-400;
     - with a paint-holding own tower within d2 100: 2.5% / 1.3% and 3.2% / 1.5%, unchanged from study 9. t122's fix has no games here.

### How the top teams beat us (`t108`, losses)
- **spaark** (17 losses, median end r401, 3 eliminations).
  - First tower kill on us at r75; ours on them at r93.
  - At r200: towers 6 / 9, moppers 3 / 7, chips 2538 / 986.
  - At r300: soldiers 5 / 16, splashers 3 / 7, moppers 5 / 14.
  - In the 15 wins we led 7 / 4 towers at r200.
- **gone-whalin** (11 losses). First kill on us at r38. Moppers 0 / 5 at r100; at r300, soldiers 2.5 / 6 and moppers 3 / 10. We held 3505 chips at r300.
- **scienceqiu** (8 losses, 3 eliminations). Moppers at r300: 7 / 33.
- **subscribe-to-caterpillow** (5 losses, 2 eliminations). At r300: splashers 2 / 12.5, moppers 6 / 19, paint towers 1 / 4.5.
- **om-nom** (5 losses, 4 eliminations, median end r259). At r200: towers 2 / 8, splashers 1 / 6, moppers 1 / 12.
- **confused** (5 losses, 2 eliminations). First kill on us at r60; towers 3 / 11 at r300.
- **immutable** (3 losses). At r200: splashers 2 / 13; at r300: paint towers 1 / 8.
- **just-woke-up** (2 losses). Coverage 27% / 52% at r200.

The common signature: the early tower kill, mopper-heavy armies from r100, and 2-3 times our units by r300. Their paint towers spawn 20.5 units each (32 for the starting one) against our 7 (17) (`t54`).

## 2. Differences, as codeable rules
Ranked by expected size, weighed by how often the rule fires in local games, since the local tourney is the judge.

### 2.1 Starting towers: paint their patterns, and rebuild paint (high; new)

**Evidence** (`t125`, `t124`, `t114`).
- Our starting paint tower died in 52 of 75 losses and 19 of 100 wins. Our starting money tower died in 47 and 23.
- The starting towers come with no pattern (RULES 4: spawned at r0, 5x5 unpainted).
  - At r80, 18.4 of our starting paint tower's 24 pattern tiles are still empty.
  - At its death, 6.8 are right, 10.4 empty, 3.4 wrong colour and 3.3 enemy.
- What happened to the ruins:
  - starting paint towers: we rebuilt 4 of 52 within 50 rounds; the enemy took 23;
  - starting money towers: we rebuilt 1 of 47; the enemy took 19.
- 27 of the 52 paint towers and 19 of the 47 money towers had no enemy tile in the 5x5 at death. A full pattern of our paint would have been rebuildable at once.
  - Their killers are soldiers, and a soldier can't paint over our paint.
  - In the wins, 14 of 19 and 10 of 23 had no enemy tile.
- How often an intact pattern gets rebuilt:
  - killed money towers of ours with an intact pattern were rebuilt by us within 50 rounds in 141 of 173 cases (81%, losses);
  - killed paint towers of ours, all of them: 38 of 155.
- Wrong colours in our killed paint towers' 5x5:
  - 62% were last written by our own soldiers, which paint empty tiles primary (`paintNear` / `paintHere`);
  - 29% by our own splashes.

**Code.**
- `Unit.rebuild` (Unit.java:81-91, called by every robot every turn from RobotPlayer.java:19) completes only `LEVEL_ONE_MONEY_TOWER` (85-86).
- `Soldier.paintHere` / `paintNear` (Soldier.java:467-487) always paint primary (`rc.attack(l, false)`).
- `Unit.repairPattern` (Unit.java:97-110) already repaints a standing tower's pattern, but money only (100), and only during a churn wait (Unit.java:51).
- `Soldier.turn` (Soldier.java:15-37): after `deny` (29) and `siege` (30), an idle soldier goes to `srpTurn` (31), refill (32) or explore (34-36).

**Rule.**
- (a) **Rebuild paint.** In `Unit.rebuild`, also complete `LEVEL_ONE_PAINT_TOWER` when its pattern is intact, then call `G.noteTower(r, 1)`.
- (b) **Colour by pattern.** In `paintHere` / `paintNear`, when the tile is within Chebyshev 2 of a known own tower (`G.towerLoc` / `G.towerKind`), paint it in that tower's pattern colour: `Soldier.bit(patternOf(type), dx, dy)`. It costs nothing extra.
- (c) **Fill the starting patterns.** A soldier with no ruin, 60+ paint and its action ready paints one tile per turn of the pattern of a visible starting tower, in that tower's pattern colour.
  - A starting tower is an ally tower with `getID() < 10000`; per RULES their ids come from the map, 0-16.
  - Only tiles in attack range, with no walking. EMPTY tiles first; in a second version also our own wrong-colour tiles.
  - Call it in `Soldier.turn` between `siege` (30) and `srpTurn` (31), from about r30.
  - Each starting tower needs about 20 tiles, 100 paint, once per game.
- A paint pattern on a money tower's ruin can't happen. The starting money tower is L2 and can't churn, so (c) doesn't touch `Tower.churn`.

**Expected size.** Small to medium; on the replica it fires in 69% of losses and about 20% of wins.
- Up to about 27 paint-tower and 19 money-tower rebuilds per 75 losses at the 81% rate, near r132 and r197, each one bringing back 500 paint.
- It also makes the 42 captures cost the enemy 24 mops instead of about 10.
- Locally it fires whenever our own bots kill a starting tower, and their soldier sieges do.
- Risk: SRP workers and (c) fighting over the same tiles. The first version fills only EMPTY tiles. Watch `pickSrp`, which prefers centres 3-4 tiles from a tower.

**Prior attempts.**
- t72, rebuild any tower type with an intact pattern: -4 against t70 after 355 games (flat).
- t79 (t74 + t72): -44.
- No rule ever painted the starting towers' patterns. t102 / y221 and y225 / y230 pre-painted new ruins.

**Candidates.** (a)+(b)+(c) with EMPTY tiles only; then the same with wrong colours repainted too. Maps: Filter, BunnyGame, FourCorners, Jail, CastleDefense, Racetrack, DefaultLarge, starburst, lighthouse, Brat (our last paint tower dead by r130).

### 2.2 Paint towers: a mopper every third spawn (medium; spawn mix, untested in this form)

**Evidence** (`t54`, `t44`, `t47`, `t123`, `t111`, `t125`).
- Moppers are 11% (starting tower) and 16% (built towers) of our paint towers' spawns, in losses and wins alike. Theirs: 38% / 36% in the losses, 41% / 48% in our wins.
- In the losses they have 4.6 times our mopper-turns; their first mopper comes at r39, ours at r95.5.
- Their moppers drain 2-3 times the paint ours do, in our wins too: our robots lose 620 per game to drain in r201-300 of a win, theirs 285. Drain precedes 65-72% of our starvation deaths.
- Their cleaners are in view of 92% of their blocked attempts, ours of 54%. Their moppers clear 13293 enemy tiles inside free ruins in the losses, ours 4727.
- Their killed starting paint towers always had moppers near (a median 27 mopper-rounds in the last 40); ours had none in 35 of 52.

**Code.** `Tower.choose` (Tower.java:58-77).
- 63: soldiers only before r80.
- 66: paint towers cycle `k % 4` over `k = built % 6`, which gives S X X M S X (1 mopper in 6). The comment says "S X X M".
- Money towers spawn S M X M S M (69-76) but stall after S M (`t54`: 0 of 420 money towers of ours spawned 3+).

**Rule.** From r80, paint towers cycle S X M: `k % 3 == 2 ? MOPPER : (k % 3 == 0 ? SOLDIER : SPLASHER)`. `k = built % 6` still works, since 6 % 3 == 0. Moppers rise from 1 in 6 to 1 in 3 of paint-tower spawns, and splashers drop from 1 in 2 to 1 in 3.

**Expected size.** Medium on the replica. Locally unknown: it fires in every game, and our won games run on a splasher-heavy mix.

**Prior attempts.**
- t64, paint towers S X M M from r300 (study 5 2.6): retired unscored at t61's crowning.
- y240, money towers one mopper fewer: flat.
- Opening length: y238 -5, y239 -7, y241 -17.
- Mopper fallbacks: t71 -317, t76 -295, t83 -54.
- None of them changed the paint towers' mid-game share.

**Candidates.** S X M from r80; S X M from r150; S M X M from r150. Maps: DefaultHuge, quack, SMILE, TargetPractice, Snowglobe (spaark); Restart, giver, Oasis (scienceqiu, immutable).

### 2.3 Small maps: a guard mopper for the paint tower (medium-low; a narrowed t108 / t109)

**Evidence** (`t122`, `t40`, `t125`, `t46`).
- Short side 25 or less: 8-15 (35% won).
- In the 15 small-map losses our last paint tower died for good in 11, at a median r63. Robots were 3.5 / 9 at r100 and 1 / 14 at r200.
- 7 of the 13 losses that lost their last paint tower by r130 were on small maps.
- Our towers fall to a median 2 soldiers after 12-13 rounds of siege, with 0 defending moppers (theirs 1).
- The first kill on us came at a median r39 on small maps.

**Code.**
- `Tower.choose`: Tower.java:63 returns SOLDIER before r80 whatever is near; `enemyNear` (60-61) is computed and unused.
- `Tower.build`: the mopper emergency (Tower.java:88) only lowers the chip reserve.
- `Mopper.target` (Mopper.java:77-94) already puts enemies within `DEFEND_R2` 25 of our towers first (8, 83).

**Rule.** On a map with `min(W, H) <= 25`, a paint tower whose turn sees an enemy soldier within d2 20, and no own mopper within d2 20, spawns a mopper. This applies before r80 too, at most once per 20 rounds, with 100+ paint.

**Expected size.** Small locally (it fires only on small maps under attack). Medium on the replica's small maps, where most of our eliminations are.

**Prior attempts.**
- t108 / t109, any tower hit spawns a mopper, on every map: -38 on y221.
- t11 -59, sw31 -135, t51 -131 (global early or defensive moppers).
- The map-size and paint-tower restriction is new.

**Candidates.** One. Maps: Filter, FourCorners, Jail, CastleDefense, Racetrack, DefaultSmall.

### 2.4 Salt the ruins of towers we kill (medium-low; new)

**Evidence** (`t114`, `t124`).
- In the losses they rebuild 76% of the paint towers we kill (60 of 100 within 50 rounds) and about 82% of the money towers; we take 3% of their ruins.
- Their killed towers keep 18.5-19.8 of 24 pattern tiles, with only 1.1-1.2 of ours in the 5x5.
- In our wins their killed paint towers keep 15.0 and stay dead in 93 of 212 cases.

**Code.**
- `Soldier.deny` (Soldier.java:63-88) paints only EMPTY tiles (soldiers can't paint over enemy paint), and stops at 2 of our tiles (74). Their dead ruins have about 1.9 empty tiles.
- The splash grid (G.java:78-102) scores enemy tiles 2 in the inner 3x3 and gives towerless ruins nothing.

**Rule.** In `G.remember`'s splasher branch, for a visible ruin with no robot on it whose 5x5 holds 12+ enemy tiles, add 4 to `v2` for each enemy tile of that 5x5.
- One splash then overwrites up to 8 of their pattern tiles, and the rebuild needs 8 mops.
- Bytecode: a few ruins times 24 tiles, only on turns when the splasher can act.

**Expected size.** Small to medium. Each denied rebuild keeps them a tower down for tens of rounds; it fires whenever we kill a tower, locally too.

**Prior attempts.**
- t117 / t120 (study 9 2.1a): +6 for enemy tiles inside a ruin *we* were building, -12.
- Denial tunings t80 (-39), y187, y188, y196 and y206 changed soldiers only.

### 2.5 `G.forgetTower` loses dry flags (low; bug)

`G.forgetTower` (G.java:137-141) moves the last slot into the freed one, but `Unit.towerDry` (Unit.java:10) is not moved:
- the moved tower takes the forgotten tower's flag;
- the next `noteTower` (G.java:132-135) inherits a stale flag.

Since t122 a flagged tower is re-sensed in sight (Unit.java:23-30), which limits the harm, but money flags still last 40 rounds.

**Fix:** `Unit.towerDry[i] = Unit.towerDry[nTowers]; Unit.towerDry[nTowers] = 0;` inside the loop. Two lines; on its own it will be flat. Ride it with 2.1, or test it alone.

### 2.6 Lower priority
- **(a) Splasher starvation** (`t123`). 0.86 against 0.18 per 100 splasher-turns in the losses, and 65% drained in the last 15 rounds.
  - Splashers last held 50+ paint a median 16 rounds before dying, at d2 109 from the nearest own tower holding paint.
  - Every refill and avoidance tuning has lost: y234 refill 80 (-37), y50 refill 150 (-28), t77 soldiers step away from moppers (-51).
  - 2.2 attacks the cause, their drain.
- **(b) SRPs** (`t84`). In the losses we complete a median 3 per game, they 9. 52% of ours end by enemy paint (theirs 5%); 8% of ours are intact at the end (theirs 61%).
  - Priors: t104 -62, y213 flat, y214 -85.
- **(c) Money upgrades while paint-bound** (`t78`, `t30`).
  - We made 102 money-tower upgrades in the losses: 69 to L2 in 31 games from r285, 33 to L3. In the wins, 45.
  - That happens while 84% of tower-turns are paint-blocked.
  - Tower.java:109 lets a money tower upgrade at 6200 chips, the same as a paint tower's L2→L3 (108).
  - Prior: t54 (never upgrade money, study 5) and the y183 / y218 spare tunings.
- **(d) Pattern marks** (`t47`). We spend a median 150 paint per loss on marks in r1-100; they spend 0, so they never mark.
- **(e) Money towers stall after 2 spawns** (Tower.java:69-76, `t54`). Every fix lost: t71 -317, t76 -295, t83 -54, y240 flat. No new rule.

## 3. What changed since study 9
"study 9" means study 9's 89 losses with its scripts.

| item | study 9 (us / them) | now (us / them) | status |
|---|---|---|---|
| record vs study 9's six top teams | 40-48 | 62-49 (eight teams: 64-56) | better |
| median loss round | r400 | r392 | same |
| eliminations among the losses | 20 of 89 | 18 of 75 | same share |
| losses behind on towers at r100 | 32 of 89 | 32 of 75 | worse share (43%) |
| maps up to 500 tiles / over 2500 tiles | 6-16 / 30-8 | 3-7 / 14-14 | big maps worse |
| last paint tower dead for good, losses / wins | 43 of 89 / 0 of 96 | 33 of 75 / 0 of 100 | a little better |
| losses with a spell without a paint tower | 48 of 89 | 32 of 75 | better |
| paint towers at r300, losses | 1 / 3 | 1 / 3 | same |
| SRPs at r300, losses | 0 / 2 | 0 / 2 | same |
| tower attempts completed, losses | 42% / 66% | 41% / 69% | same |
| blocked attempts completed (t111 games / t118 games) | 16% / 52% | 11% / 16%, theirs 53% | t118 helped a little |
| blocked attempts with no cleaner in view | 48% / 9% | 46% / 8% | same (open) |
| paint after the first enemy tile on abandoned blocked attempts, per loss | 351 | 387 (t111) / 281 (t118) | t118 cut 27% |
| splasher damage on towers per 100 splasher-turns, r201+ losses | 19.1 | 50.4 (theirs 39.1) | better (stand-off) |
| share of it from d2 10-16 | 27% | 64% | better |
| tower kills r201+ per loss, us / them | 2.0 / 5.3 | 2.6 / 6.3 | same exchange |
| splasher deaths per 100 turns, r201+ losses | 0.94 / 0.45 | 0.99 / 0.27 | same for us |
| stuck at low paint, r101-200 / r201-400 | 8.4/3.8, 9.7/5.2 | 7.0/4.2, 9.8/4.7 | same (t122 untested) |
| first mopper | r89.5 / r41 | r95.5 / r39 | open (2.2) |
| our starting paint tower killed, losses / wins | not measured | 52 of 75 / 19 of 100 | new (2.1) |

By version:
- t111 won 58% (52% against the top teams);
- t118 won 56%, all against the top teams.

Study 9's rules in the local tournament:
- 2.1b: crowned as t118.
- 2.4: crowned as t122 (the L1-only bypass t126 -38).
- 2.1a: -12 (t120).
- 2.1c: -26 (t125).
- 2.2: -28 (t124).
- 2.3: flat (t123; t127 in the pool).
- The give-up tunings y250-y260: flat.

## 4. Broken in our bot (t122)
1. **`G.forgetTower` loses dry flags** (G.java:137-141). See 2.5.
2. **`Unit.rebuild` completes only money** (Unit.java:81-91). A killed paint tower with an intact pattern waits for a soldier's `pickRuin`, which may re-mark it money through `wantType` (Soldier.java:135-151).
3. **The starting towers never get a pattern.** Nothing paints them, and `paintNear` paints their 5x5 primary from r80 (Soldier.java:34, 36, 475-487). See 2.1.
4. **Dead towers stay in memory.** `G.forgetTower` is called only from Unit.java:39 and Tower.java:38, so `wantType`'s every-tower-known test (Soldier.java:141) misreads.
5. **`workRuin` returns true when refill fails** (Soldier.java:214-218), so the soldier stands still. Paint flags now expire in 10 rounds, money flags still in 40 (Unit.java:23).
6. **`pickRuin` only sees ruins in sight** (Soldier.java:115), and splashers never add to `G.ruinList` (G.java:113 is in the non-splasher branch).
7. **Money towers stall at the X slot** (Tower.java:69-76). None of our 420 money towers that lived 100+ rounds spawned more than 2 units (`t54`).
8. **Comments and dead code.**
   - Tower.java:66 says "S X X M"; the cycle is S X X M S X.
   - `enemyNear` (Tower.java:60-61) is never used.
   - Soldier.java:119 says two soldiers per ruin; the rule is at 120-124.

## 5. Suggested test order
1. **2.1:** (a)+(b)+(c) with EMPTY tiles only. It is cheap, fires in every game where a starting tower dies (our bots' sieges do that locally), and changes no spawn mix. Then the version that also repaints wrong colours.
2. **2.5:** alone, or bundled into 2.1's second candidate.
3. **2.2:** S X M on paint towers from r80, then from r150.
4. **2.3:** expect it flat locally; keep it only if it isn't behind.
5. **2.4:** after 2.2 settles, since more moppers change who cleans ruins.

Build on t122. Once t122 has replica games, rerun `t125`, `t111`, `t117` and `t123` with `S10VER=t122`.

## Summary: the top three
1. **Starting towers (2.1).**
   - Our starting paint tower dies in 52 of 75 losses (21 by r100) with no mopper near it (35 of 52); theirs had moppers near in every kill.
   - It has no pattern: 18.4 of 24 tiles are empty at r80. We rebuilt 4 of 52; the enemy took 23. Yet 27 had no enemy tile at death, and intact patterns are rebuilt 81% of the time.
   - Rule: `Unit.rebuild` also completes paint (Unit.java:81-91); `paintNear` / `paintHere` paint in the pattern colour near own towers (Soldier.java:467-487); idle soldiers fill the starting towers' patterns (new step in `Soldier.turn`, between 30 and 31).
2. **More moppers from paint towers (2.2).**
   - Moppers are 11-16% of our paint-tower spawns and 36-48% of theirs, in wins and losses alike. They have 4.6 times our mopper-turns in the losses.
   - Their moppers drain 2-3 times what ours do, and drain precedes 65-72% of our starvation deaths. Their cleaners are in view of 92% of their blocked attempts, ours of 54%.
   - Rule: paint towers cycle S X M from r80 (Tower.java:66).
3. **Small-map guard mopper (2.3).**
   - We are 8-15 on maps with a short side of 25 or less. Our last paint tower died for good in 11 of 15 small-map losses (median r63), and robots were 1 / 14 at r200.
   - Rule: on `min(W, H) <= 25`, a paint tower that sees an enemy soldier within d2 20 and no own mopper spawns a mopper, before r80 too (Tower.java:63).

Also broken: `G.forgetTower` drops `Unit.towerDry` (G.java:137-141, a two-line fix), and `Unit.rebuild` is money-only (Unit.java:85-86).

Files are in `/home/terryvanbelle/projects/vibe/2025b/research/field/study10/`. The new scripts are `t119_dups.py` and `t120_paintflow.py` through `t125_startpt.py`; the outputs are the `tNN.txt` files plus `t111_t111.txt` and `t111_t118.txt`. The dumps are in `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study10/dump/`.

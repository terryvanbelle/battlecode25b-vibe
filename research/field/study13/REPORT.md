# Field study 13 (2026-11-28): t140 and t158 on the replica since submission 78

This study used replays only. I read no competitor code and no write-ups, made no `contest.py` or replica call, ran no games, and edited no bots, tools or tests.

**Versions.** The 82 matches after study 12's last (5557), 5572-6493, were played by two of our submissions; `pkgs.py` read every replay header (`pkgs.txt`):
- **t140** (submission 78, crowned 2026-11-27 08:28; r140 is t140 refactored with identical behaviour), 65 matches, 5572-6332;
- **t158** (submission 79, crowned 16:27: r140 + study 12 2.2, moppers hit and run in `Mopper.retreat`), 17 matches, 6370-6493 (6370, 6383-6388, 6411-6415, 6442, 6447, 6478, 6483, 6493).

**All code references are to `bots/t158`.** t160 (submission 80) and y316 (submission 81) have been crowned since, but no replay of them is in this window. Unit, Churn, Soldier, Tower, Towers, Pattern and RobotPlayer are identical in y316, so every line number in those files holds there too. In y316's Mopper.java the lines after 40 move down by 3.

Unless a line says otherwise, the numbers are **t140 + t158 together: 220 games, 118 won and 102 lost** (t140 91 / 78, t158 27 / 24). t158 changed only the mopper's movement, so the two share everything else. t158 alone (51 games) is too few to split most measures; section 3 splits the mopper measures by version.

| match | ver | opponent | W-L | | match | ver | opponent | W-L |
|---|---|---|---|---|---|---|---|---|
| 5572 | t140 | immutable | 2-1 | | 6101 | t140 | scienceqiu | 3-0 |
| 5573 | t140 | spaark | 2-1\* | | 6106 | t140 | spaark | 1-1 (dup g1) |
| 5602 | t140 | subscribe-to-caterpillow | 0-3 | | 6119 | t140 | om-nom | 2-1 |
| 5620 | t140 | gone-whalin | 1-2 | | 6120 | t140 | spaark | 0-2\* (dup g0) |
| 5638 | t140 | gone-whalin | 3-0 | | 6124 | t140 | immutable | 0-1 (dup g0,g1) |
| 5681 | t140 | spaark | 2-1 | | 6150 | t140 | om-nom | 2-1 |
| 5683 | t140 | gone-whalin | 2-1 | | 6151 | t140 | spaark | 2-1\* |
| 5700 | t140 | immutable | 1-2 | | 6152 | t140 | confused | 1-2 |
| 5701 | t140 | subscribe-to-caterpillow | 2-1\* | | 6153 | t140 | subscribe-to-caterpillow | 1-2\* |
| 5702 | t140 | confused | 1-2 | | 6154 | t140 | just-woke-up | 1-2 |
| 5703 | t140 | spaark | 2-1\* | | 6155 | t140 | scienceqiu | 2-1\* |
| 5704 | t140 | om-nom | 0-3 | | 6186 | t140 | subscribe-to-caterpillow | 1-0 (dup g0,g2) |
| 5705 | t140 | scienceqiu | 2-1\* | | 6196 | t140 | subscribe-to-caterpillow | 2-1 |
| 5718 | t140 | lobster-roll | 2-1 | | 6208 | t140 | spaark | 1-1 (dup g1) |
| 5742 | t140 | spaark | 2-1 | | 6283 | t140 | spaark | 1-1 (dup g2) |
| 5751 | t140 | scienceqiu | 1-1 (dup g2) | | 6306 | t140 | om-nom | 1-2 |
| 5787 | t140 | immutable | 1-1 (dup g1) | | 6307 | t140 | spaark | 1-1\* (dup g2) |
| 5788 | t140 | gone-whalin | 3-0\* | | 6308 | t140 | confused | 1-1 (dup g0) |
| 5789 | t140 | confused | 2-1 | | 6309 | t140 | subscribe-to-caterpillow | 1-2\* |
| 5790 | t140 | spaark | 2-1\* | | 6310 | t140 | just-woke-up | 0-3 |
| 5812 | t140 | immutable | 2-0 (dup g0) | | 6311 | t140 | scienceqiu | 0-3\* |
| 5822 | t140 | gone-whalin | 0-2 (dup g2) | | 6328 | t140 | spaark | 2-1 |
| 5861 | t140 | immutable | 2-1 | | 6331 | t140 | om-nom | 0-2 (dup g2) |
| 5880 | t140 | subscribe-to-caterpillow | 1-2 | | 6332 | t140 | subscribe-to-caterpillow | 2-0\* (dup g0) |
| 5889 | t140 | confused | 1-2 | | 6370 | t158 | subscribe-to-caterpillow | 2-1 |
| 5890 | t140 | immutable | 2-1\* | | 6383 | t158 | om-nom | 2-1 |
| 5897 | t140 | immutable | 1-0 (dup g0,g1) | | 6384 | t158 | spaark | 1-2\* |
| 5903 | t140 | subscribe-to-caterpillow | 3-0 | | 6385 | t158 | confused | 1-2 |
| 5921 | t140 | subscribe-to-caterpillow | 1-1 (dup g2) | | 6386 | t158 | subscribe-to-caterpillow | 3-0\* |
| 5930 | t140 | immutable | 2-1 | | 6387 | t158 | just-woke-up | 1-2 |
| 5934 | t140 | scienceqiu | 2-1 | | 6388 | t158 | immutable | 3-0\* |
| 5948 | t140 | spaark | 1-1 (dup g1) | | 6411 | t158 | spaark | 0-3\* |
| 5977 | t140 | immutable | 3-0 | | 6412 | t158 | confused | 1-2 |
| 6055 | t140 | om-nom | 2-1 | | 6413 | t158 | subscribe-to-caterpillow | 2-1\* |
| 6056 | t140 | spaark | 2-0\* (dup g1) | | 6414 | t158 | just-woke-up | 1-2 |
| 6057 | t140 | confused | 1-1 (dup g0) | | 6415 | t158 | immutable | 2-1\* (g1 = m5572g1, kept) |
| 6058 | t140 | subscribe-to-caterpillow | 1-2\* | | 6442 | t158 | old-but-gold | 1-2 |
| 6059 | t140 | old-but-gold | 0-3 | | 6447 | t158 | om-nom | 1-2 (g0 = m6331g0, kept) |
| 6060 | t140 | scienceqiu | 2-1\* | | 6478 | t158 | confused | 1-2 |
| 6067 | t140 | subscribe-to-caterpillow | 0-0 (all dup) | | 6483 | t158 | spaark | 3-0 |
| 6088 | t140 | spaark | 1-1 (dup g1) | | 6493 | t158 | immutable | 2-1 |

\* = unranked. "dup" = the game repeats an earlier one and is left out.

**Repeats** (`t147`). The engine is deterministic, and the replica replays pairings. **26 t140 games exactly repeat an earlier t140 game** (same map, opponent, end round, coverage and spawn counts) and are left out (`lib.DUP`). 22 of them repeat a game inside this set. Four repeat study 12's t140 set: m5787g1 = m5492g0, m5897g0 = m5492g1, m6106g1 = m5497g2 and m6124g1 = m5492g2. Two t158 games are identical to t140 games: **m6415g1 = m5572g1** (immutable, Snowman, MAJ150) and **m6447g0 = m6331g0** (om-nom, Brat, ALL355). The hit and run did not change these games at all, and they are kept as t158's results.

**Record** (`t147`, repeats left out; t158's two kept repeats are both losses):

| | t140 | t158 | all |
|---|---|---|---|
| top 7 (om-nom, spaark, subscribe-to-caterpillow, immutable, scienceqiu, lobster-roll, gone-whalin) | 83-61 (58%) | 21-10 (68%); 21-12 with the kept two | 104-71 |
| the rest (confused, just-woke-up, old-but-gold) | 8-17 (32%) | 6-12 (33%) | 14-29 |
| all | 91-78 (54%) | 27-22 (55%); 27-24 with the kept two | 118-100 |

Per opponent, t140 / t158: confused 7-9 / 3-6, gone-whalin 9-5 / -, immutable 16-8 / 7-1, just-woke-up 1-5 / 2-4, lobster-roll 2-1 / -, old-but-gold 0-3 / 1-2, om-nom 7-10 / 3-2, scienceqiu 12-8 / -, spaark 22-15 / 4-5, subscribe-to-caterpillow 15-14 / 7-2. just-woke-up and old-but-gold are new since study 12; confused played one match there (1-2). We have losing records against all three.

Ends of the 102 losses: 77 on majority paint, 24 eliminations, and one area decision at r2000 (m6385g0, Paintball, confused). t140's 78 losses end at a median r426.5 (21 eliminations). t158's 22 (repeats left out) end at r371.5 (2 eliminations); counting the kept two, it is 24 losses and 3 eliminations.

**Did t158 change the replica results? It cannot be told** (`t151`). t158 and t140 share 14 (opponent, map) pairings: t158 went 4-10 and t140 5-10. There are two flips each way: t158 lost where t140 won on om-nom/Filter and spaark/Castle, and won where t140 lost on immutable/memstore and subscribe-to-caterpillow/Restart. Locally t158 measured +40 ±24 over r140 in 217 games. On the replica its moppers do move differently (section 3), but the record shows nothing either way.

**How to run.**
- `lib.py` is study 12's loader with the study 13 dumps; versions come from `pkgs.txt`. Environment: `S13VER=t140,t158` (versions), `S13TEAMS=a,b|top`, `S13RANKED=1`, `S13SET=main|prev|old|all` (`prev` = study 12's set), `S13DUP=1` keeps repeats, and `S13WHICH=won` (t0 only). The `S12*` .. `S8*` names still work.
- `./run.sh tNN_x.py [out]` writes `tNN.txt`. Every script ran on t140 + t158 unless noted.
  - Rerun from study 12: `t106_famine`, `t108_teams`. `t140_drain`, `t141_nav` and `t143_actions` ran once per version (`tNN_t140.txt`, `tNN_t158.txt`).
  - New: `t0_medians` (`t0.txt` losses, `t0_won.txt`, `t0_t140.txt`, `t0_t158.txt`, `t0_t158won.txt`), `t147_dups`, `t148_income`, `t149_towerfall`, `t150_rebuild`, `t151_paired`, `t152_srp`, `t153_vacant`, `t154_conflict`, `t155_colour`, `t156_stuck` and `t157_srppick`.
  - `t145_ground` and `t146_walkpaint` were copied but not run.
  - `t152` checks its SRP replay against the engine: the replayed active-SRP count equals `rounds.tsv`'s `srp` column in 179894 of 179894 side-rounds.
- Dumps: `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study13/dump/mM` (82 matches, 246 games, dump version 3, 355M). Pickles are in `.../study13/cache` (232M). Rebuild with `~/opt/jdk21/bin/java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`, one java process at a time. The scratchpad can be cleared at any time.

## 1. How the games were lost

### Overview (102 losses, 118 wins)
- **Level at r100-150, then outgrown.** At r100 the median loss has 19.8 / 21.3% coverage and 5 / 5 towers; at r150, 25.2 / 26.6% and 6 / 6. By r200 it is 5 / 7 towers and 1349 / 2627 paint, while we bank 2120 / 1380 chips. At r400 (53 games) it is 5 / 11 towers and 28.9 / 50.1%.
- **The tower gap is towers killed and not rebuilt** (`t149`, `t150`).
  - Our towers are killed 1.44 / 2.01 / 6.54 times a loss (r1-100 / r101-200 / r201+), theirs 1.14 / 1.22 / 2.55.
  - We rebuild 60 / 50 / 34% of the ruins, they rebuild 91 / 92 / 80%. Their killers take 19 / 27 / 21% of ours.
  - Our wins are the mirror: we rebuild 85 / 93 / 82%, they rebuild 74 / 65 / 27%. The rebuild rate follows whoever holds the ground (2.5).
- **Paint-bound, chip-rich** (`t106`). In 52.4% of the rounds of a loss every tower of ours holds under 200 paint (theirs 29.6%; study 12 50.9%). In those rounds we hold a median 2148 chips. **Our last paint tower died for good in 52 of 102 losses, at a median r211** (theirs 5). In study 12 it was 14 of 44, at r384.5. The worst opponents are om-nom (11 of 13 losses), scienceqiu (6 of 8) and confused (9 of 15).
- **New this study: our robots run dry beside our own towers** (`t156`, 2.1). 47.0 of our robots hit 0 paint in a loss. 24% of them (11.1 a loss) hit 0 beside one of our towers, and 71% of those were beside a drained money tower while we held 2000+ chips. Theirs: 4% (3.1 a loss, out of 84.0 robots that hit 0, with 2.2x our robot-turns).

### Median timeline of the 102 losses (`t0`, us / them)

| round | coverage % | towers | paint towers | chips | paint (units + towers) | robots (S / X / M) |
|---|---|---|---|---|---|---|
| r50 | 13.9 / 14.9 | 4 / 4 | 1 / 1 | 830 / 860 | 1474 / 1562 | 8 / 7 (8/6, 0/0, 0/1) |
| r75 | 15.4 / 18.4 | 5 / 4 | 1 / 1 | 785 / 855 | 1853 / 1798 | 7 / 9 (7/6, 0/0, 0/2) |
| r100 | 19.8 / 21.3 | 5 / 5 | 1 / 1 | 1080 / 918 | 1639 / 2005 | 8 / 11 (7/6, 0/0, 0/3) |
| r150 | 25.2 / 26.6 | 6 / 6 | 1 / 1 | 1240 / 1070 | 1451 / 2259 | 10 / 14 (7/7, 1/1, 2/5) |
| r200 (93) | 29.6 / 33.0 | 5 / 7 | 1 / 2 | 2120 / 1380 | 1349 / 2627 | 10 / 18 (5/8, 2/2, 3/6) |
| r300 (72) | 33.5 / 42.5 | 5 / 9 | 1 / 3 | 1680 / 1661 | 1605 / 3915 | 11.5 / 27 (6/10, 3/5, 3/11) |
| r400 (53) | 28.9 / 50.1 | 5 / 11 | 1 / 4 | 2300 / 1878 | 1544 / 5327 | 11 / 35 (4/12, 4/10, 3/14) |

This is the shape of studies 11 and 12. The opening gap of study 12 is still there (15.4 / 18.4% at r75). After r150 their paint turns into units and towers, while ours sits at 1350-1600 with the chips in the bank. Wins (`t0_won`) are the mirror: at r200 41.0 / 25.8% coverage and 8 / 6 towers, at r300 51.2 / 25.4% and 11 / 6.

### The paint economy (`t148`, losses, medians per game and phase [means])
- **Paint in** (base + SRP + new towers x 500): 3000 / 3000 in r1-100, 3000 / 3689 in r101-200, 3736 / 5522 in r201-300, 4222 / 8161 in r301-400.
- **Paint towers** (mean alive): 1.0 / 1.0, 1.3 / 1.8, 2.4 / 2.8, 2.8 / 3.6.
- **SRP paint income** is the late gap: 231 / 1118 [2771 / 4626] in r201-300 and 549 / 2892 [6003 / 11448] in r301-400. Active SRPs (mean) are 2.1 / 3.4 and 3.5 / 6.6.
- **SRPs completed** are close until r300: 3.2 / 3.3 in r101-200 and 5.2 / 5.6 in r201-300. What differs is how long they last (`t152`). Our r101-200 SRPs break 88% of the time (theirs 35%) and 70% reach lifetime 50 (theirs 89%). Of the breaks, 54% are enemy splasher paint, 30% our own soldiers' paint and 14% enemy mops. In our wins it reverses: ours break 36%, theirs 77%. **SRP survival follows the ground, like rebuilding.** The exception is our own paint (2.2).

### Towers that fall (`t149`, `t150`, `t153`)
- **Killed by soldiers:** the killing blow is a soldier's in 75-100% of cases (splashers 25% after r200 in losses). There are 2.2-2.9 distinct attackers in the last 30 rounds and a 13-17-round final assault.
- **Ours die alone:** in 56 / 32 / 19% of our losses' tower deaths no robot of ours is within r2 20 (theirs 33 / 24 / 12%). Within r2 20 at death we have 0.03 / 0.46 / 0.96 moppers, they have 0.95 / 1.01 / 1.85. Their towers kill 0.35-0.36 attackers in the assault, ours 0.18-0.32.
- **The ruin stays contested.** After the death, enemy paint is in our ruin's 5x5 in 64 / 72 / 86% of the rounds, against 25 / 38 / 46% for their fallen ruins. Enemy robots in r2 20 per contested round: 1.38 / 2.33 / 4.28 (theirs 0.45 / 1.05 / 1.26). The enemy paints 5.9 / 12.1 / 29.8 rows into the 5x5 per death (theirs 1.3 / 2.5 / 8.0).
- **Neither side rebuilds a contested ruin:** the median rebuild comes after 0 contested rounds, for both sides. Their own moppers come to their fallen ruins (0.49 / 0.79 / 1.64 per contested round); ours do not (0.06 / 0.44 / 0.51).
- **They switch type:** they rebuild a different type 21-29% of the time, we 1-3% (`t153`).

### What the robots do (`t141`, `t143`, `t140_drain`, `t156`)
- **Moppers:** see section 3. t158's moppers move and reverse more than t140's, but they still stand still on 38-43% of turns (theirs 9-22%).
- **Robots that run out of paint** (`t156`, losses, us / them):
  - At 0 paint a robot can neither act nor move, so it can never withdraw again (RULES 3). It loses 20 HP a turn, and every ally beside it pays 1-2 paint a turn for it (RULES 5.3).
  - Our robots spend 331 turns a loss at 0 paint (4.9% of our robot-turns; theirs 357.8, 2.4%).
  - Starved to death per loss: our soldiers 18.4, splashers 15.3, moppers 10.0. Theirs: 14.1, 16.2, 29.8, plus 15.5 disintegrated (2.4).
- **Splashers and soldiers:** nothing new beyond study 12. In this window our soldiers' paint on open ground (`t155`) is 0-16% secondary, theirs 24-31%. Neither side's matches the SRP lattice (best alignment 71-82%, both sides), so there is no rule in it.

## 2. Differences, as codeable rules
Line numbers are for `bots/t158` (the same in y316 for every file but Mopper.java). The "already tried" list of the brief is not proposed again: opening cover, explore painting, early SRPs, more moppers, full refills, mopper gives below 60%, and the Nav paint weight and ally term.

### 2.1 Do not wait beside a drained money tower with little paint (high; new)
**Evidence** (`t156`, `t154`; us / them):
- **Where our robots run dry.** In a loss 47.0 of our robots hit 0 paint: 20.2 soldiers, 16.8 splashers and 10.0 moppers. **24% (11.1 a loss) hit 0 beside one of our own towers, theirs 4% (3.1).** In wins it is 18% (5.6 a game) against 4% (1.7). The tower held 50+ paint in 4% of these cases.
- **Beside which tower** (losses): a money tower while we held 2000+ chips 71%, a money tower under 2000 chips 12%, a paint tower 18%. Wins: 65%, 27% and 8%. 2000 chips is `Tune.CHURN_CHIPS`, the gate of the churn wait in `Unit.refill`. Theirs are spread over every tower type and chip level.
- **How it happens.** Our robots arrive with a median 10.5 paint (wins 8; theirs 6). They hit 0 after a median 3 rounds beside the tower, which is `CHURN_WAIT_ROUNDS` = 3. Waiting beside a tower costs at least 1 paint a turn, because the tower counts as an adjacent ally (RULES 5.3), plus 1 for each other robot beside us.
- **The waits are long and mostly in vain.**
  - Our robots spend 353 turns a loss beside a drained (< 10 paint) money tower of ours, and 368 a win. Theirs: 233 and 47.
  - The tower can churn only with its money pattern intact. That was true in 17% of the drained turns with 2000+ chips in losses and 19% in wins; theirs 39% and 44% (`t154`).
  - Of our losses' drained turns, 60% had our own paint in the other colour outside any SRP, 27% a tile held by one of our SRPs, 26% enemy paint and 22% an empty tile; a turn can have several.
- **A robot that hits 0 beside the tower is lost even if the tower churns:** a 0-paint robot cannot withdraw from the fresh 500 (RULES 3). It can still complete the pattern, because that needs no paint, and then it starves.

**Code (t158):**
- Unit.java:22: a money tower's dry flag is ignored while `Churn.churnable()` (2000+ chips). Unit.java:58 does not flag it from afar either. So every robot below its refill threshold (soldiers and splashers 100, moppers 40) heads for the nearest drained money tower; paint towers count only 30% closer.
- Unit.java:47-52, the churn wait: beside a drained L1 money tower, every robot waits 3 rounds. A soldier that repaints a tile restarts the wait (line 50, `Churn.repairPattern`).
- Unit.java:54: `if (!rc.isActionReady()) return true;` also keeps a robot beside a dry tower.
- Churn.java:61 (`repairPattern`) uses `rc.canAttack(l)`, which accepts an enemy-painted tile. A soldier cannot paint over enemy paint (RULES 2, pitfall 9), so the shot spends 5 paint and does nothing. The same tile comes first in the scan every turn, and each shot restarts the wait.
- Churn.towerTurn (Churn.java:17-33) needs only **one** ally beside the tower.

**Rule:** a robot waits beside a drained money tower only when it can survive the wait and is needed.
- Join the wait only with paint ≥ 3 x (1 + own robots already beside the tower) + 5, and only when no other robot of ours is already waiting there.
- Otherwise flag the tower dry (`Towers.markDry`) and fall through to the next tower. Or stand off at r2 4-8 on our own paint, which costs nothing with no ally adjacent, and step in once it holds paint.
- The repair skips tiles it cannot paint (`rc.canPaint`). When the pattern has an enemy tile, no soldier can fix it, so the tower is flagged dry.

**Expected size:** medium. Up to 11 units a loss and 5.6 a win starve here, mostly soldiers and splashers costing 200-300 paint and 250-400 chips each. Saving half is about 5 units a loss, 1000-1500 paint of units; an L1 paint tower makes 500 paint in 100 rounds. A churn needs one adjacent ally, so a few churns may be lost when fewer robots wait.

**Prior attempts:**
- t110 and t113 (study 8 2.5c): after a failed churn wait, honour that tower's dry flag for 20 rounds. t110 went 130-126 against y221, t113 72-57 against t111 but 234-257 overall; neither was crowned.
- y279 / y285 (no repair shots at enemy paint, bundled with a 30-paint floor for free hits): 141-153 against t135 and 67-74 against t140.
- The churn chip gate was dialled flat (y181 / y186 1500, y189 / y193 / y198 2500).
- None of these limited who waits, or kept the waiters off the tower's side.

**Candidates:**
- `w1`: in the churn-wait branch (Unit.java:47-52), wait only when `G.paint >= 15` and no other robot of ours is within r2 2 of the tower (count `rc.senseNearbyRobots(best, 2, G.me)`, leaving out the tower and ourselves). Otherwise `Towers.markDry(best)` and return false. A soldier that is repairing keeps waiting, as now.
- `w2`: `w1`, plus `Churn.repairPattern` skips tiles where `!rc.canPaint(l)`, and returns false (no wait restart) when only such tiles are wrong.
- `w3`: `w2`, plus the line 22 exemption applies to soldiers only, so moppers and splashers honour a money tower's dry flag; a soldier is the one that can repair it.

### 2.2 SRPs beside our money towers disagree with their patterns (medium-low; bug)
**Evidence** (`t154`, `t157`):
- **Our SRPs disagree with our own money towers, and our own paint breaks them.**
  - 4.29 of our 11.28 SRPs a loss (7.44 of 21.58 a win) are completed with a money tower of ours at Chebyshev 3-4 whose pattern disagrees on the shared tiles.
  - Our own paint breaks 53% of them in losses and 41% in wins. For SRPs with no tower of ours at 3-4 it is 11% and 8%.
- **The pick check works; the work loop lacks it** (`t157`, all games).
  - There are 1775 cases of an SRP of ours completed with a money tower of ours at Chebyshev 3-4 (an SRP beside two counts twice). 1452 of them disagree: 81% for t140, 85% for t158.
  - In 1446 of the 1452, the completing soldier had not been within sight of the tower by the round it picked the centre.
  - When it had seen the tower, and the tower stood at the pick, 162 of 168 agree. When it had not, 122 of 1445 agree (8%).
- **They block churns.** In 10% of our drained-money-tower turns with 2000+ chips (11% in wins), a registered SRP of ours holds a tile of the tower's pattern in the other colour, and nothing else is wrong. `Churn.repairPattern` (Churn.java:50-64) only knows the money pattern, so repairing that tile breaks the SRP.
- **The top teams also complete disagreeing SRPs** (7.75 a loss), but their own paint breaks only 35% of them. Why was not split. This is a bug in our code, not a difference in play.

**Code (t158):**
- Soldier.java:328 (`pickSrp`) skips a centre within Chebyshev 4 of a money tower it knows (`Towers.kind == MONEY`) whose pattern disagrees (`Pattern.agreesWithMoney`, Pattern.java:61-67), for `SRP_SKIP_MONEY` = 300 rounds.
- Soldier.java:409-416 (`workSrp`) re-checks the ruins around the centre every turn, but only asks that a ruin within Chebyshev 4 hold one of our towers (415). A money tower first seen after the pick is painted over.

**Rule:** `workSrp` applies `pickSrp`'s money check to every tower of ours it senses at Chebyshev 3-4.

**Expected size:** small. It removes about 2.3 own-paint breaks a loss (4.29 x 53%) and the churn blocks, but it also removes those SRP sites; the soldier picks another centre.

**Prior attempts:** t104 (study 8 2.3 b+c) checked agreement with the money pattern at every tower of any type, in both `pickSrp` and `workSrp`, and made the repair skip enemy paint. It went 198-279 overall (46-70 against y211). That is a broader rule: it also ruled out SRPs beside paint towers. The narrow `kind == MONEY` check in `pickSrp` has been in every champion since (t100 has it); the work-loop check never was.

**Candidates:**
- `s1`: after Soldier.java:415, `if (Towers.kindOf(t.type) == Towers.MONEY && !Pattern.agreesWithMoney(c.x, c.y, r)) { srpSkipFor(c, Tune.SRP_SKIP_MONEY); srp = null; return false; }`.
- `s2`: `s1`, plus `Churn.repairPattern` leaves a tile alone when it is right for a registered SRP of ours (`rc.senseMapInfo(cc).isResourcePatternCenter()` for the centres within Chebyshev 2). This keeps SRPs that were already built.

### 2.3 Moppers: keep moving while the action cools down (low-medium; follows t158)
**Evidence** (section 3, `t141` / `t140_drain` / `t143` per version, losses r1-100 / r101-200 / r201+):
- t158's hit and run changed the moppers. Stand-still went from 54.2 / 47.7 / 39.0% to 42.6 / 39.9 / 37.7%, and free A-B-A reversals from 1.7 / 2.0 / 2.8 to 7.4 / 8.2 / 8.1 per 100 moves. Passive paint loss after r200 fell from 145 to 90 per 100 mopper-turns.
- The gap to theirs is still large. Their moppers stand still on 22.5 / 15.3 / 9.4% of turns, and idle with a free move on 16.7 / 11.6 / 7.1% (ours 27.4 / 28.3 / 27.6%). They move on 76-79 turns in 100, ours on 55-57.
- A mopper acts at most every third turn (cooldown 30). Ours retreat only on the turn they acted. On the two cooling turns they walk to the target, and within r2 2 of it they stand.

**Code (t158):** Mopper.java:22 `if (acted && rc.isMovementReady() && retreat()) return;`; Mopper.java:24 `if (goal != null && G.here.distanceSquaredTo(goal) <= 2) goal = G.here;`.

**Rule:** on a turn when the action is not ready, retreat as after acting when a threat is in reach. With no threat, stay within reach of the goal but on our own paint. Step in on the turn the action is ready.

**Expected size:** small. t158 alone moved the replica record by nothing measurable. This is the rest of the same gap.

**Prior attempts:** t158 itself (crowned, +40 ±24). t153 (an enemy robot in mop reach scores 55, above ruin paint) went 86-75 against r140 and was not crowned. t160's single-robot swing (crowned) changed the attack, not the movement.

**Candidates:**
- `m1`: Mopper.java:22 `if ((acted || !rc.isActionReady()) && rc.isMovementReady() && retreat()) return;`.
- `m2`: `m1`, plus line 24: with the action not ready, `goal = G.here` only if we stand on our own paint, else step to an adjacent own-paint tile within r2 2 of the goal.

### 2.4 Disintegrate a robot stuck at 0 paint (low; new)
**Evidence** (`t156`):
- **Three teams do it.** confused, spaark and subscribe-to-caterpillow disintegrate robots, and nearly always at 0 paint. Per loss: confused 38.5, spaark 43.8, subscribe-to-caterpillow 7.4. confused's moppers go at HP 10, the turn before the 0-paint damage would kill them.
- **We never do.**
  - Our robots spend 331 turns a loss at 0 paint, with 0.92 robots of ours beside each one. Each of those pays 1 paint a turn for it, or 2 on enemy paint (RULES 5.3).
  - 11.1 a loss sit beside one of our towers, where they also block a tile that another robot needs to refill or rebuild (2.1).
  - A 0-paint robot cannot act or move, and our moppers give paint to robots 0.1-1.9 times per 100 mopper-turns, so it is rarely saved.

**Code (t158):** none; RobotPlayer.java's turn dispatch would call it. `rc.disintegrate()` works at 0 paint (RULES 3).

**Rule:** at 0 paint, with no mopper of ours in sight and an ally (robot or tower) within r2 2, disintegrate. Keep the robot when it stands beside a ruin whose pattern it can complete: completing needs no paint.

**Expected size:** small. At most about 300 paint a loss (331 x 0.92) comes back to its neighbours, plus the freed tiles beside towers. 2.1 removes much of the need.

**Prior attempts:** none. Study 12 2.5 noted their disintegrations as "too small to chase" (about 2.5 a game then).

**Candidate:** `d1`.

### 2.5 Lower priority (measured, but weak, tried before, or not codeable yet)
- **Fallen towers are not rebuilt** (1, "Towers that fall"; `t150`, `t153`). This is the biggest measured gap in tower count: we rebuild 34-60% of our killed towers in losses, they rebuild 80-92%. But it is symmetric with the result (in our wins they rebuild 27-74%), and neither side rebuilds a contested ruin. The levers have been tried:
  - mopper ruin weights (t74, crowned; y167 -38, y168 -24);
  - idle moppers walking to remembered contested ruins (t90, t94, t98, t100; not crowned);
  - giving up blocked ruins without a cleaner (t118, crowned);
  - splashers clearing blocked patterns (t117 / t120; not crowned);
  - more moppers (t161 -72, t162 -59).

  The part that is not covered is their moppers standing by their towers before the fall (0.95-1.85 within r2 20 at death, ours 0.03-0.96). Not a rule without a cheap way to station them.
- **They switch type at a rebuild** (21-29% of their rebuilds; ours 1-3%), and confused disintegrates defence towers and L3 money towers into paint or money towers. Not decoded; possibly churn by type.
- **SRP survival** (1, the paint economy): 88% of our r101-200 SRPs break in losses, 54% of them to enemy splashers. After a break, 44% of ours are completed again in r101-200 of losses, against 83% of theirs. `srpComplete` bars the completer from its own centre for good (Soldier.java:393). It follows the ground, and our wins invert it.
- **Paint-tower wipeouts** (1.1): 52 of 102 losses. wantType already asks for paint with 1500+ chips from 3 towers (Soldier.java:149). The gap is getting a ruin finished, which is 2.1 (units alive) and the rebuild problem above.
- **Open-ground colour** (`t155`): they paint 24-31% of open ground secondary, we 0-16%. There is no lattice in it (best SRP-lattice alignment 71-82% for both), and their SRPs need as many repaints as ours (4.5-8.8 per SRP). No rule.

## 3. What changed since study 12
- **The versions.** t158 = r140 + study 12 2.2's hit and run (+40 ±24 over r140 in 217 local games). r140 = t140 refactored, identical in 43 of 43 twin games. Study 12's other rules were tested since: 2.1 opening cover (t149, t150, y299, not crowned), 2.3 early SRPs (t154, -22), and 2.4 the Nav ally term (in t160, crowned after this window).
- **Replica record.** t140 went 91-78 in this window (top 7: 83-61), t158 27-24 (21-12). The paired comparison (`t151`) finds nothing either way (above).
- **Did the hit and run change the moppers on the replica? Yes, measurably** (losses r1-100 / r101-200 / r201+; t140 = the 78 t140 losses of this window, t158 = its 24; "theirs" = the opponents in the t158 games):

  | per mopper | t140 | t158 | theirs |
  |---|---|---|---|
  | moves per 100 turns (`t141`) | 45.6 / 47.7 / 51.2 | 56.7 / 57.0 / 54.7 | 76.4 / 79.0 / 79.1 |
  | stood still, % of turns | 54.2 / 47.7 / 39.0 | 42.6 / 39.9 / 37.7 | 22.5 / 15.3 / 9.4 |
  | idle with a free move, % | 34.2 / 30.1 / 25.1 | 27.4 / 28.3 / 27.6 | 16.7 / 11.6 / 7.1 |
  | free A-B-A reversals per 100 moves | 1.7 / 2.0 / 2.8 | 7.4 / 8.2 / 8.1 | 17.2 / 13.2 / 10.4 |
  | passive paint loss per 100 turns (`t140_drain`), r101-200 / r201+ | 106.8 / 145.1 | 89.8 / 90.0 | 103.5 / 90.0 |
  | of it crowding (beside a tower), r201+ | 99.3 (31.9) | 50.4 (16.2) | 45.9 (5.5) |
  | turns on enemy paint, r101-200 / r201+ | 4.9 / 7.4% | 1.4 / 3.6% | 3.7 / 3.1% |
  | tiles mopped per 100 turns (`t143`), r101-200 / r201+ | 18.4 / 11.9 | 19.8 / 16.7 | 17.8 / 11.5 |
  | robot drains per 100 turns, r101-200 / r201+ | 6.98 / 6.65 | 7.41 / 7.45 | 4.80 / 3.33 |

  Part of the drain drop is the game mix: in the t140 games the opponents' moppers lost 99.7 / 122.3, in the t158 games 103.5 / 90.0. Against the opponents in the same games, our r201+ drain went from 1.19x theirs to 1.00x. Wins show the same (r201+ drain 115.3 to 91.3). The hit and run works as designed; what remains is the cooling turns (2.3).
- **Losses are shorter and harsher:** median end r404.5 (study 12 r436.5); 24 eliminations of 102 (6 of 44). Our last paint tower died for good in 52 of 102 losses, against 14 of 44 in study 12. The three teams outside the top 7 (confused, just-woke-up, old-but-gold; the last two new since study 12) beat us 14-29.
- **Repeats:** a quarter of t140's games (26) repeat an earlier game exactly, because the replica replays pairings. t158's two repeats of t140 games (m6415g1, m6447g0) show the hit and run left some games untouched.

## 4. Broken in our bot (t158)
1. **The churn wait starves robots** (Unit.java:22, 47-54; 2.1). With 2000+ chips, every low robot heads for the nearest drained money tower and waits beside it at 1+ paint a turn. That is 71% of the 11.1 robots a loss that hit 0 beside our towers. This is a design flaw with a measured cost.
2. **`Churn.repairPattern` shoots at enemy paint** (Churn.java:61): `if (rc.canAttack(l)) { rc.attack(l, s); ... return true; }`. `canAttack` accepts an enemy-painted tile; the shot does nothing (RULES pitfall 9: check with `canPaint`). The function then returns true, so the caller restarts the churn wait (Unit.java:50). The same tile comes first in the scan every turn. Our silent soldier attacks run at most 0.23 per 100 soldier-turns (`t140_t158`), so it is not frequent. But each shot is 5 of the roughly 10 paint the waiter arrived with.
3. **`workSrp` lacks the money-pattern check that `pickSrp` has** (Soldier.java:409-416 against 328; 2.2).
4. **`srpComplete` bars the completer from its own centre for good** (Soldier.java:393, `srpSkipFor(c, Integer.MAX_VALUE)`). After the SRP breaks, only other soldiers can redo it. Minor.
5. **`Towers.forget` leaves the dry flags behind** (Towers.java:31-37, marked "Known bug, kept"): the moved tower inherits the removed tower's flag.
6. **`Nav.last1` / `last2` are still dead state** (Nav.java:13, 100).

## 5. Suggested test order
1. `w1` (2.1): a few lines in `Unit.refill`, behind the biggest new gap (11.1 units a loss starving beside our towers, 3.6x theirs). If it leads or is flat, try `w2` (the repair fix) and `w3`.
2. `s1` (2.2): one line, a bug fix; `s2` if `s1` is flat.
3. `m1` (2.3): one condition.
4. `d1` (2.4).

Unit, Churn, Soldier and RobotPlayer are identical in y316, and Mopper.java's lines 22 and 24 are unchanged there, so all four build on the current champion as written.

**Not measured:**
- How many of the robots saved by `w1` would find paint elsewhere. Many starve far from any tower anyway (54% of our 0-paint events have no tower in sight).
- Why confused, spaark and subscribe-to-caterpillow disintegrate: whether it is for the adjacency drain or to free tiles was not split.
- The type switches at rebuilds (2.5) were not decoded.

## Summary: the top three
1. **The churn wait starves our robots (2.1).** 24% of our robots that run dry (11.1 a loss) do it beside one of our own towers, against 4% (3.1) of theirs. 71% of those are beside a drained money tower while we hold 2000+ chips. That is `Unit.refill`'s churn wait (Unit.java:22, 47-52): every low robot comes, arrives with about 10 paint, and waits 3 rounds at 1+ paint a turn. The tower's pattern is intact in only 17% of such turns. Rule: wait only with 15+ paint and as the only waiter, else flag it dry (`w1`). Then fix `repairPattern`'s shots at enemy paint (`w2`).
2. **SRPs vs our money towers (2.2).** 4.3 of our 11.3 SRPs a loss disagree with a money tower of ours beside them, and our own paint breaks 53% of those (11% elsewhere). `pickSrp` checks this (Soldier.java:328), but `workSrp` does not (409-416), so a money tower first seen after the pick is painted over (1446 of 1452 disagreeing cases). Rule: the same check in `workSrp` (`s1`).
3. **Moppers still stand on cooling turns (2.3).** t158's hit and run measurably changed the moppers on the replica (stand-still 54-39% to 43-38%, A-B-A 2-3 to 7-8 per 100 moves, r201+ drain 145 to 90) but not the record. They still stand on 38-43% of turns against 9-22%. Rule: retreat on cooling turns too (`m1`, Mopper.java:22).

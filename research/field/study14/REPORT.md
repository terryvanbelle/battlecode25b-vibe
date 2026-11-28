# Field study 14 (2026-11-28): t158, t160, y316 and y323 on the replica since submission 79

This study used replays only. I read no competitor code and no write-ups, made no `contest.py` or replica call, ran no games, and edited no bots, tools or tests.

**Versions.** The 29 matches after study 13's last (6493), 6515-6860, were played by four of our submissions. `pkgs.py` read every replay header (`pkgs.txt`):
- **t158** (submission 79), 1 match: 6515;
- **t160** (submission 80: `Nav.tileCost` counts adjacent allies; moppers swing at a single robot), 7 matches: 6592-6598;
- **y316** (submission 81: `NAV_PAINT_WEIGHT` 8), 19 matches: 6635-6796;
- **y323** (submission 82: `CHURN_WAIT_ROUNDS` 2), 2 matches: 6816 and 6860.

There is **no replay of y328** (submission 83, `DRY_ROUNDS` 60) yet.

**All code references are to `bots/y328`.** From t160 to y328 only three `Tune` constants change, so every measure here except the t158 games is y328's code with older constants.

The numbers are **all 82 games, 51 won and 31 lost** (87 played, 5 exact repeats left out), unless a line says otherwise.

| match | ver | opponent | W-L | | match | ver | opponent | W-L |
|---|---|---|---|---|---|---|---|---|
| 6515 | t158 | subscribe-to-caterpillow | 2-1 | | 6678 | y316 | scienceqiu | 2-1 |
| 6592 | t160 | om-nom | 2-1 | | 6706 | y316 | om-nom | 2-1 |
| 6593 | t160 | subscribe-to-caterpillow | 3-0\* | | 6707 | y316 | spaark | 0-3\* |
| 6594 | t160 | confused | 2-1 | | 6708 | y316 | confused | 1-1 (dup g0) |
| 6595 | t160 | spaark | 2-1\* | | 6709 | y316 | immutable | 2-1\* |
| 6596 | t160 | just-woke-up | 0-3 | | 6710 | y316 | just-woke-up | 0-3 |
| 6597 | t160 | immutable | 3-0\* | | 6711 | y316 | subscribe-to-caterpillow | 2-1\* |
| 6598 | t160 | spaark | 1-2 | | 6748 | y316 | spaark | 2-1 |
| 6635 | y316 | immutable | 1-2 | | 6774 | y316 | spaark | 2-0 (dup g2) |
| 6662 | y316 | om-nom | 3-0 | | 6776 | y316 | immutable | 1-1 (dup g2) |
| 6663 | y316 | spaark | 3-0\* | | 6777 | y316 | scienceqiu | 3-0 |
| 6664 | y316 | confused | 3-0 | | 6796 | y316 | immutable | 1-1 (dup g0) |
| 6665 | y316 | immutable | 1-2\* | | 6816 | y323 | subscribe-to-caterpillow | 2-1 |
| 6666 | y316 | just-woke-up | 2-1 | | 6860 | y323 | subscribe-to-caterpillow | 1-1 (dup g0) |
| 6667 | y316 | subscribe-to-caterpillow | 2-1\* | | | | | |

\* = unranked. "dup" = the game repeats an earlier one and is left out.

**Repeats** (`t147_dups`). Five games exactly repeat an earlier game of the same version: m6708g0 = m6664g0, m6774g2 = m6748g2, m6776g2 = m6665g2, m6796g0 = m6635g0 and m6860g0 = m6816g1. None repeats a study 13 game, because t160's Nav change touches every game.

**Record** (repeats left out): **51-31 (62%)**.
- By version: t158 2-1, t160 13-8, y316 33-20, y323 3-2.
- The top teams (om-nom, spaark, subscribe-to-caterpillow, immutable, scienceqiu) 43-22 (66%); the rest (confused, just-woke-up) 8-9. Ranked 33-22, unranked 18-9.
- Per opponent: confused 6-2, immutable 9-7, just-woke-up 2-7, om-nom 7-2, scienceqiu 5-1, spaark 10-7, subscribe-to-caterpillow 12-5.

Ends of the 31 losses: 26 on majority paint, 5 eliminations (m6515g1 lighthouse r189, m6667g0 Barcode r343, m6678g0 DefaultSmall r108, m6708g1 Terminal r360, m6748g0 AlarmClock r375). Median end r403.

**Did the new versions change the replica results? Not measurably** (`t151_paired`). y316 and t140 share 20 (opponent, map) pairings: y316 went 14-7 and t140 17-9. t160 and t140 share 8: 5-3 and 4-5. So the record being up on study 13 (54%) comes from which pairings were played, not from a measured change.

**How to run.**
- `lib.py` is study 13's loader, with the study 14 dumps (kept outside the repo) and versions from `pkgs.txt`.
  - Environment: `S14VER=t160,y316` (versions), `S14TEAMS=a,b|top`, `S14RANKED=1`, `S14DUP=1` (keeps repeats) and `S14WHICH=won` (t0 only). The `S13*` to `S8*` names still work.
  - `S14SET=main|prev|prev2|old|all`: `prev` is study 13's t140 + t158 set, and reads study 13's dumps. `t151_paired` and `t158_churnrate` use it.
- `./run.sh tNN_x.py` writes `tNN.txt`.
  - Rerun from study 13: `t0_medians` (`t0.txt`, `t0_won.txt`), `t106_famine`, `t108_teams`, `t147_dups`, `t148_income`, `t149_towerfall`, `t150_rebuild`, `t151_paired` (adapted to the new versions), `t152_srp`, `t153_vacant`, `t154_conflict`, `t156_stuck` (also `t156_<ver>.txt` and `t156_prev_<ver>.txt`) and `t157_srppick`.
  - New: `t158_churnrate`, `t159_ready`, `t160_breakage`, `t161_wear`, `t162_assault`, `t163_attackers`, `t164_kite`, `t165_company` and `t166_pergame`.
  - Copied but not run: `t140_drain`, `t141_nav`, `t143_actions` and `t155_colour`.
- The topic numbers continue study 13's (t158 and up). They clash with bot names, so this report names each script in full.

## 1. How the games were lost

### Overview (31 losses, 51 wins)
- **Behind in the opening, then outgrown.**
  - At r75 the median loss has 15.9 / 25.0% coverage (study 13: 15.4 / 18.4%) with 5 / 4 towers. At r100 it has 6 / 5 towers.
  - By r200 the towers are 5 / 7, and by r300 they are 5 / 9 at 33.7 / 48.0% coverage, while we bank 3045 / 1351 chips.
  - Wins are the mirror. At r200 a win has 40.0 / 26.6% coverage and 8 / 6 towers; at r400, 58.4 / 24.4% and 10 / 5.5.
- **The tower gap is towers killed, not rebuilt, and taken** (`t149_towerfall`).
  - Our towers are killed 0.90 / 1.81 / 5.87 times a loss (r1-100 / r101-200 / r201+), theirs 1.13 / 1.74 / 2.32.
  - We rebuild 61 / 52 / 35% of those ruins, they rebuild 91 / 91 / 83%. Their killers take 21 / 25 / 30% of ours; we take 0 / 2 / 8% of theirs.
- **Paint-bound and chip-rich** (`t106_famine`).
  - In 52.8% of a loss's rounds every tower of ours holds under 200 paint (theirs 31.0%). In those rounds we hold a median 2687.5 chips.
  - Our last paint tower died for good in 11 of the 31 losses, at a median r202; theirs never did. All 5 eliminations lost the last paint tower first (median r146).
- **New this study: our soldiers die to tower fire at twice their rate, in wins as well as losses** (`t163_attackers`, `t164_kite`, `t165_company`; 2.1-2.3).
  - Tower fire kills 12.8 of our robots a loss (10.0 of them soldiers) and 6.4 of theirs. In wins it is 15.1 against 7.7.
  - Of our soldiers whose attack run on a tower fails (the tower stands), 63% die (52% to that tower). Of theirs, 42% die (29%).

### Median timeline of the 31 losses (`t0_medians`, us / them)

| round | coverage % | towers | paint towers | chips | paint (units + towers) | robots (S / X / M) |
|---|---|---|---|---|---|---|
| r25 | 10.5 / 11.0 | 3 / 3 | 1 / 1 | 770 / 1060 | 1257 / 1149 | 7 / 5 (7/5, 0/0, 0/0) |
| r50 | 14.4 / 20.5 | 4 / 4 | 1 / 1 | 850 / 930 | 1559 / 1544 | 8 / 7 (8/6, 0/0, 0/1) |
| r75 | 15.9 / 25.0 | 5 / 4 | 1 / 1 | 940 / 860 | 1989 / 1834 | 8 / 9 (8/6, 0/0, 0/2) |
| r100 | 22.6 / 28.4 | 6 / 5 | 1 / 1 | 1150 / 970 | 1582 / 1856 | 8 / 10 (7/6, 0/1, 1/3) |
| r150 (30) | 29.0 / 32.9 | 5 / 6 | 1 / 1.5 | 1955 / 1044 | 1467.5 / 2516 | 11 / 14 (7.5/7, 1/2, 2/5) |
| r200 (28) | 36.1 / 40.8 | 5 / 7 | 1 / 2 | 1903 / 1024.5 | 1508.5 / 2707.5 | 11 / 15.5 (6/7.5, 2/2, 4/6) |
| r300 (24) | 33.7 / 48.0 | 5 / 9 | 1 / 3 | 3045 / 1351 | 1254 / 3250 | 10 / 23 (4/9.5, 3/5.5, 5/7.5) |
| r400 (16) | 30.3 / 53.8 | 6.5 / 9.5 | 1.5 / 4 | 3168.5 / 2011.5 | 1501 / 4739 | 13.5 / 31 (5/10, 5/10, 4/13) |

- The opening gap is wider than in study 13: 9 points at r75 against 3 (`t166_pergame`).
  - It comes mostly from immutable. Their median r75 lead is 12.8 points over the 7 immutable losses, against about 2 elsewhere. They reach 25-43% coverage by r75 on BatSignal, Bread, TargetPractice, windmill and Racetrack, while we stand at 12-30%.
  - We still win some of those games: on CastleDefense they had 45.0% at r75 to our 23.2%.
  - In all 16 immutable games we have at least as many towers at r100.
- Active SRPs (median) are 0 / 1 at r200 and r300, and 0 / 4.5 at r400.

### The paint economy (`t148_income`, losses, medians per game and phase [means])
- **Paint in** (base + SRP + new towers x 500): 3080 / 3000 in r1-100, 3290 / 3442 in r101-200, 2929 / 4550 in r201-300, and 4236 / 6948 in r301-400.
- **SRP paint** is the late gap: 0 / 64 in r101-200, 6 / 620 in r201-300 and 57 / 3024 in r301-400.
  - Active SRPs (mean): 0.2 / 0.6, 1.1 / 2.0 and 1.0 / 4.2.
  - In wins we hold 2.6 / 2.1 in r201-300 and 4.7 / 4.3 in r301-400.
- **SRP survival follows the ground** (`t152_srp`). In r201+ of a loss we complete 2.71 SRPs a game, they complete 11.06.
  - 93% of ours break (theirs 50%), 64% before lifetime 50.
  - What breaks ours: enemy splasher paint 44%, our own soldiers 33%, enemy mops 18%.
  - In wins we complete 10.55 to their 5.16.
- **Paint towers** (mean alive): 1.0 / 1.1, 1.4 / 1.7, 1.9 / 2.5 and 2.5 / 3.2.

### Towers that fall (`t149_towerfall`, `t150_rebuild`, `t159_ready`, `t160_breakage`, `t161_wear`, `t162_assault`)
- **Our towers face assaults alone and dry** (`t162_assault`). An assault is the run of damage rows on a tower with gaps under 15 rounds.
  - We lose 42% of the assaults on our towers, they lose 29% (r201+: 41 / 23%). In wins it is 37 / 47%.
  - Tower paint before the first hit (median): 40 / 90. In r1-100 it is 110 / 244, in r201+ 11 / 28.
  - Robots spawned per assault: 0.18 / 0.44. Moppers: 0.06 / 0.25, and in r1-100 0.03 / 0.40.
  - Own robots within r2 20 per round: 1.99 / 3.09 (moppers 0.71 / 1.34).
  - No own robot at any round end of the assault: 15 / 5%; in r1-100, 23 / 6%.
  - Mop hits by own moppers near the tower per assault: 2.62 / 4.09.
  - Attackers the tower killed per assault: 0.24 / 0.55 (wins 0.30 / 0.57).
- **At the death** (`t149_towerfall`, `t150_rebuild`). No own robot within r2 20 in 57 / 23% (r1-100), 32 / 17% and 15 / 7% of deaths.
  - Pattern tiles right (median): 24 / 24, 21.5 / 24 and 14 / 19.
  - Enemy tiles in the 5x5 (median): 0 / 0, 0 / 0 and 3 / 0.
- **Why the ruins are not rebuilt: the pattern is gone before anyone comes** (`t159_ready`, `t160_breakage`).
  - Our dead tower's pattern is already broken at the death in 76% of our losses' tower deaths; theirs in 58% (r201+: 88 / 79%).
  - An own robot stands beside the ruin within a median 1 round after the death (79% of deaths), and within r2 8 at once in 94%. So our robots come, but to a broken pattern.
  - A ruin counts as rebuild-ready at a round end when its pattern is intact, an own robot is adjacent and we hold 1000+ chips. Only 3% of our deaths ever reach that state; 20% of theirs do. 13% of ours have a robot adjacent before the pattern breaks; 27% of theirs do.
  - Our ruins keep their marks: 88% of the 5x5s say the same type at the death. So the type is not the problem.
- **What breaks a standing tower's pattern** (`t161_wear`, losses, per 100 tower-rounds, towers completed in the game).
  - Our money towers: 5.75 breaks, 4.02 of them enemy splashes. Theirs: 2.38, 0.74 enemy splashes.
  - Our paint towers: 8.96 breaks, 7.02 enemy splashes. Theirs: 3.96, 1.38.
  - Our money patterns are intact 45% of tower-rounds (theirs 48%), our paint patterns 19% (theirs 40%).
  - In wins the enemy splashes ours 1.42 / 2.53 times per 100 tower-rounds, and we splash theirs 1.75 / 3.60. Again it follows the ground.
- **Drained money towers rarely churnable** (`t154_conflict`). In our drained-money-tower turns with 2000+ chips, the money pattern is intact 17% of the time; theirs 41%.
  - What blocks ours: our own paint in the other colour outside any SRP 59% (theirs 24%), enemy paint 26% (8%), an empty tile 18% (8%), and an SRP tile 18% (34%).
  - Churns per loss: 4.00 / 1.84.

### What the robots do (`t156_stuck`, `t158_churnrate`, `t163_attackers`, `t164_kite`, `t165_company`)
- **Tower fire** (`t163_attackers`). Our soldiers make 18.1 attack runs a loss on towers that stand, theirs 14.8.
  - Of our soldiers' runs, 63% end in death, 52% to that tower. Of theirs, 42% (29%). In wins: 64% (55%) against 55% (36%).
  - By hit points at the hit (losses), our soldiers die to that tower within 5 rounds:
    - at 0-49 HP: 85%, theirs 53%;
    - at 50-99: 56%, theirs 27%;
    - at 100-149: 17%, theirs 5%.
  - They hit at low HP nearly as often as we do (12.0 hits a loss at 0-49 HP against our 16.7). They live through it more often.
  - Turns ending inside an enemy tower's range: ours 124 a loss (1.9% of our robot-turns), theirs 137 (1.0%). The exposure is the same; the deaths are not.
- **Where our hitters stand** (`t164_kite`, hits on paint and money towers that stood).
  - 14% of our hits are made from inside range by a soldier that also ends the turn inside range ("in->in"); theirs 4% (wins 13 / 6%).
  - 8% of our hits are followed by a step that stays inside range; theirs 1%.
  - 11% of our hits end at r2 1-4 from the tower, 4% of theirs.
- **Defense towers** (`t164_kite`). 23% of our soldier hits in losses land on a side with a defense tower standing (16% in wins), and 8% hit a defense tower itself.
  - After a buffed hit, 42% of our hitters die to that tower; after an unbuffed one, 14% (theirs 8%). We build no defense towers, so their hits are never buffed.
  - immutable builds 2.9 defense towers per loss (1.0 per win), spaark 2.7 (0.8). These two teams account for 14 of our 31 losses.
  - Tower fire kills 14.6 of our robots a game in the immutable losses and 20.1 in the spaark losses.
- **Lone sieges** (`t165_company`). A run with no other robot of ours hitting the same tower within 3 rounds topples the tower 14% of the time in losses, and the soldier dies in 47%. Theirs: 24% and 24%.
  - With one companion: 33 / 34% against 48 / 13%. With two or more: 61 / 16% against 69 / 10%.
  - Lone runs against a defense-buffed side: 4.2 a loss, 8% topple the tower and 73% die.
- **Running dry** (`t156_stuck`, `t158_churnrate`). 30.9 of our robots hit 0 paint a loss (study 13: 47.0). 22% of those (6.9 a loss) are beside an own tower, and 86% of those are beside a drained money tower while we hold 2000+ chips.
  - Both sides starve robots: ours 28.6 a loss, theirs 40.5 (they field 2.2x our robot-turns).
  - The study 13 2.1 case (hit 0 beside a drained money tower with 2000+ chips), per 1000 of our robot-turns, all games:

    | version | games | rate |
    |---|---|---|
    | t140 | 169 | 0.67 |
    | t158 (study 13) | 51 | 0.59 |
    | t160 | 21 | 0.33 |
    | y316 | 53 | 0.73 |
    | y323 | 5 | 0.31 |

  - Against subscribe-to-caterpillow, the only opponent y323 met, y316 had 1.27 over 6 games.
  - y323's drop is in the right direction but rests on 5 games. y328 is unmeasured.

## 2. Differences, as codeable rules

Every rule here is new, or comes with new evidence. They share one target: our soldiers die to towers at twice the enemy's rate (2.1-2.3). Each soldier costs 250 chips and 200 paint. That paint is what a loss lacks: in r201+ all our towers are under 200 paint in more than half the rounds.

### 2.1 Siege: stand at the edge of range and really step out (high; new)
**Evidence** (`t163_attackers`, `t164_kite`).
- 14% of our tower hits are in->in, against their 4%. 8% are followed by a step that stays in range, against their 1%. 11% end at r2 <= 4, against 4%.
- After a hit that ends at r2 4 or 5, 17-19% of our hitters die within 5 rounds; at r2 1-2, 41%. Their hitters die 8-12% after hits ending at r2 4-5.
- Below 150 HP our hitters die 1.6-3.4x as often as theirs.

**Code.** `Soldier.siege` (Soldier.java:54-70).
- The approach is `Nav.moveTo(t)` (line 59), which can stop anywhere inside r2 9, often at r2 4-5.
- The step-out (63-67) tries `away`, `rotateLeft` and `rotateRight` and takes the first move that `canMove` allows. It never checks that the new tile is outside range: from (2,0) the move "away" lands on (3,0), r2 9, still in range.
- The free shot (Soldier.java:23-28) fires from inside range. The rest of the turn (workRuin, deny, refill) can then leave the soldier there.

**Rule.**
- (a) **Approach.** When r2 > 9 and the action is ready, move to the neighbour that is passable, has r2 <= 9 to t, and has the largest r2 (9, 8, then 5; own paint breaks ties); then hit. When no neighbour reaches r2 9, keep `Nav.moveTo(t)`.
- (b) **Step out.** After a hit, if movement is ready and the soldier is within the tower's range (9; 16 for a defense tower), try all 8 directions. Take a `canMove` tile beyond that range, preferring own paint and then the largest r2. If none leaves range, take the largest r2.
- (c) After the free shot, if the soldier is still within range, its movement is ready and it holds no ruin within r2 8, run the same step-out before the rest of the turn.

**Expected size.** Medium, and it fires in nearly every game, locally too.
- Cutting in->in from 14% to their 4% removes about 16 tower shots a loss on our soldiers (165.5 hits a loss). At 30 HP a shot that is about two soldiers a game, before counting fewer ends at r2 <= 4.

**Prior attempts.** Study 11 2.2's HP exit (t141 -53, t142 -92) changed whether to hit at low HP. This keeps every hit and changes only where the soldier stands. y209 and y219 tuned `SOL_SIEGE_R2` and `SOL_SIEGE_PAINT`.

**Candidates.** k1 = (a) + (b); k2 = k1 + (c).

### 2.2 No lone siege on a healthy tower (medium; new)
**Evidence** (`t165_company`, losses / wins).
- Our lone runs: 12.9 / 14.1 a game. They topple the tower 14 / 23% of the time and the soldier dies in 47 / 42%. Theirs: 24 / 19% and 24 / 30%.
- With two or more companions: 61% topple and 16 / 24% die.
- 6.1 of our soldiers a loss die on lone runs.

**Code.** The entry test of `Soldier.siege` (Soldier.java:57).

**Rule.** Siege t only if another of our soldiers or splashers is within r2 16 of t (sense around t), or t's health is at most c. The free shot stays, since it costs no move.

**Expected size.** Medium if it holds: halving the lone deaths saves about 3 soldiers a loss.
- The risk is the one that sank the HP exit: lone hits soften towers that fall later (study 11 measured killed episodes starting at a median 800 / 400 / 500 HP).

**Prior attempts.** None on company. The HP exits (t141, t142) lost locally by hitting less, which is the same risk.

**Candidates.** c1: c = 200 (four hits); c2: c = 350. Test them on top of the winner of 2.1.

### 2.3 Count the defense buff before a siege (medium on the replica; replica-only)
**Evidence** (`t164_kite`, `t165_company`).
- 23% of our soldier hits in losses land on a buffed side (each defense tower adds +5 to every tower's single shot, uncapped; RULES 5). Our hitters die 42% after those hits, 14% after unbuffed ones.
- Lone runs against a buffed side die 73% of the time and topple 8% (3.1 soldiers a loss).
- 8% of our hits are on defense towers themselves (2000 HP, r2 16 reach, 40 + 20 a turn, and 20 chips per attack that hits).
- immutable and spaark build 2.9 and 2.7 defense towers per loss, against 1.0 and 0.8 per win.

**Code.**
- `Unit.scanEnemyTowers` (Unit.java:103-117) remembers only the nearest enemy tower, not its type.
- `Soldier.siege` (54-70) and the free shot (23-28) make the decision.

**Rule.**
- Remember the round an enemy defense tower was last seen.
- While one was seen in the last 100 rounds, a siege needs two companions (2.2's count) or a target at 150 HP or less.
- A defense tower target needs two companions or 250 HP or less (study 11 2.2's rule 5, never tested on its own). The 2.1 (b) step-out uses r2 16 for it.

**Expected size.** About 3 soldiers per loss against immutable and spaark. Nothing elsewhere.

**Prior attempts.** None on its own. Building defense towers ourselves lost (t103 -72), so do not copy their towers; this rule only stops feeding them.

**It cannot be judged locally**, because no pool bot builds defense towers, so d1 never fires there. It can be measured on the replica only, or locally against a sparring bot that builds them (t103's rule).

**Candidate.** d1 = the winner of 2.1/2.2 + this rule.

### 2.4 `Churn.rebuild` for paint towers (low-medium; bug, only tested in bundles)
**Evidence** (`t159_ready`, losses).
- 10% of our killed built paint towers (about 5 cases) were rebuild-ready at some round (intact pattern, robot adjacent, 1000+ chips). None was rebuilt within a round, and 3.2 ready rounds passed on average. In wins: 9%, 33% at once, 2.33 missed.
- At the first ready round, the robot adjacent to our paint ruins was a splasher in 60% and a mopper in 60% (a round can have both). Neither can complete through `workRuin`.

**Code.** `Churn.rebuild` (Churn.java:35-46) tries only `LEVEL_ONE_MONEY_TOWER`.

**Rule.** Try `LEVEL_ONE_PAINT_TOWER` too, then note it with `Towers.note(r, Towers.PAINT)`. The two patterns differ, so at most one can match.

**Expected size.** Small, a handful of saves per 31 losses. Each one saves a paint tower, and our last paint tower died for good in 11 of the 31 losses.

**Prior attempts.** t128 -13 and t133 -22 bundled it with pattern-colour painting (t128 also with an idle fill). It was never tested alone.

**Candidate.** r1.

### 2.5 Lower priority (measured, but tried before or not codeable yet)
- **Fallen ruins under enemy paint.**
  - 76% of our dead patterns are broken at the death. The killers take 28% of our ruins (we take 4% of theirs).
  - The inner ring of both the paint and the money pattern is primary on the four orthogonal tiles and secondary on the four diagonals (`lib.secondary`). So one splash of ours on the ruin clears enemy paint from all eight, leaves the orthogonals right, and leaves four diagonal repaints for a soldier.
  - Splashers clearing blocked patterns (t117, t120) and moppers walking to contested ruins (t90-t100) were tried, so this is listed only as a fact for a future variant.
- **Towers under attack spawn little** (`t162_assault`): 0.18 robots per assault against 0.44, with tower paint 40 against 90. Tried: t108 and t109 (-38, spawn a mopper when hit), t47. Not proposed.
- **Our own wrong-colour paint on money patterns** (`t154_conflict`: 59% against 24% of the drained turns). `paintHere` and `paintNear` (Soldier.java:437-457) always paint primary, and 16 of the money pattern's 24 tiles are secondary. Pattern-colour painting was tried inside t128 and t133. Not proposed alone without a cleaner test.
- **The opening against immutable** (r75 coverage 12.2-29.5% against 25.0-43.2%). Our record against them fell from 23-9 to 9-7. Opening cover painting was tried; there is no new rule.
- **Their attackers die less even unbuffed and out of range**: 6-9% against our 12-14% after hits that end out of range (`t164_kite`). Two possible causes, neither measured:
  - Their moppers escorting the attack. `Tower.attack` (Tower.java:23-36) scores a full-HP mopper at 50, below any soldier over 110 HP (HP - `TWR_SHOT_NONMOPPER` 60), so our single shot goes to the escort.
  - They stop re-entering at low HP.

## 3. What changed since study 13
- **Record**: 62% (51-31), up from 54%, but not a measured change (`t151_paired`: on shared pairings y316 went 14-7 and t140 17-9). just-woke-up is still our worst opponent (2-7; study 13 3-9). immutable fell from 23-9 to 9-7.
- **Tower deaths and rebuilds** are about the same.
  - Ours killed 0.90 / 1.81 / 5.87 a loss (study 13: 1.44 / 2.01 / 6.54).
  - Rebuilt 61 / 52 / 35% (60 / 50 / 34%). Taken 21 / 25 / 30% (19 / 27 / 21%).
  - Towers dying alone: 57 / 32 / 15% (56 / 32 / 19%).
- **Paint famine**: unchanged at 52.8% of rounds (52.4%), with more chips banked (2687.5 against 2148). The last paint tower died for good in 35% of losses (study 13: 51%).
- **Running dry**: fewer robots hit 0 paint (30.9 a loss against 47.0), and fewer robot-turns are spent at 0 (3.2% against 4.9%). The share beside a drained money tower is 86% (71%).
  - The churn-wait rate per 1000 robot-turns rose under y316 (0.73) and fell under y323 (0.31, 5 games).
- **Tower fire**: their towers kill 0.31 / 0.44 / 0.64 attackers per final assault, ours 0.25 / 0.25 / 0.27 (study 13: 0.35-0.36 against 0.18-0.32). Now traced to where our soldiers stand (2.1), lone sieges (2.2) and defense buffs (2.3).

## 4. Broken in our bot (y328)
1. **`Soldier.siege`'s step-out does not check that it leaves range** (Soldier.java:63-67). It tries three directions and takes the first legal one, and from r2 4-5 the step "away" often stays inside r2 9. The approach (line 59) walks toward the tower's tile rather than to the edge of range. 8% of our hits are followed by a step that stays in range; 1% of theirs are (`t164_kite`).
2. **The free shot can leave the soldier inside range for the rest of its turn** (Soldier.java:23-28). It fires at 5+ paint (`SOL_SHOT_PAINT`) and nothing steps out afterwards. Replica replays carry no indicator strings, so its share of the in->in hits cannot be split out.
3. **`Churn.rebuild` completes money towers only** (Churn.java:35-46).
4. **`Churn.repairPattern` still shoots with `rc.canAttack`** (Churn.java:61), which is true on enemy paint, where a soldier's attack paints nothing (RULES 4.1). The fixes were mixed: t171 +13 on y316, t175 -16 on y323.
5. **`Towers.forget` leaves dry flags behind** (Towers.java:31-37, "known bug, kept"). With `DRY_ROUNDS` 60 a stale flag now lasts 60 rounds instead of 40.
6. Study 13's other items stand: `workSrp` has no money check, and `srpComplete` bars the completer for good (Soldier.java:387-399). Both were tried as fixes (t168 -26, t177 -5).

## 5. Suggested test order
1. **k1** (2.1 a+b) against y328. It fires in nearly every game.
2. **k2** (k1 + the free-shot exit) if k1 is level or better.
3. **c1**, then **c2** (2.2), on the winner.
4. **r1** (2.4) alone. It is cheap, and it has never been tested apart from the colour rule.
5. **d1** (2.3). It cannot show up locally. The choice is to bundle it with a crowned k or c bot as a replica-only change, or to measure it against a sparring bot that builds defense towers.

**Not measured:**
- y328 (no replays yet);
- why their attackers survive more even unbuffed (escorts or re-entry; 2.5);
- whether our moppers near a tower under attack mop the attackers or the paint;
- the churn wait under y323/y328 beyond the 5 games.

## Summary: the top three
1. **2.1 Siege geometry.** 14% of our tower hits are in->in, against their 4%; 8% are followed by a step that stays in range, against 1%. Tower fire kills 12.8 of our robots a loss and 6.4 of theirs (15.1 / 7.7 in wins). Fix the approach and the step-out in `Soldier.siege` (Soldier.java:54-70).
2. **2.2 No lone siege on a healthy tower.** Lone runs topple 14% and die 47%; theirs topple 24% and die 24%; with two or more companions ours topple 61% and die 16%. Gate the `Soldier.siege` entry (line 57) on a companion within r2 16 of the target, or target HP <= 200.
3. **2.3 Count the defense buff** (replica-only). 23% of our hits in losses land on a buffed side, and 42% of those hitters die, against 14% unbuffed. immutable and spaark build 2.7-2.9 defense towers per loss. Remember defense towers in `Unit.scanEnemyTowers` (Unit.java:103-117) and gate `siege` on them.

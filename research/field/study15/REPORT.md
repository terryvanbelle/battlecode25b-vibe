# Field study 15 (2026-11-28): y328, t186 and t188 on the replica since submission 83

This study used replays only. I read no competitor code and no write-ups, made no `contest.py` or replica call, ran no games, and edited no bots, tools or tests.

**Versions.** The 34 matches after study 14's last (6860), 6901-7209, were played by three of our submissions. `pkgs.py` read every replay header (`pkgs.txt`):
- **y328** (submission 83: `DRY_ROUNDS` 60), 25 matches: 6901-7143;
- **t186** (submission 84: y328 + `Soldier.stepOut`, the siege leaves tower range after a hit), 2 matches: 7157 and 7181;
- **t188** (submission 85: t186 + `Soldier.colourAt`, soldiers paint empty tiles inside a known paint/money tower's 5x5 in its pattern colour), 7 matches: 7191 and 7204-7209.

**All code references are to `bots/t188`** (the champion; `src/vibe` is identical). y328 to t186 changes only `Soldier.siege`'s step-out; t186 to t188 changes only `paintHere`/`paintNear`.

The numbers are **all 100 games, 56 won and 44 lost** (102 played, 2 exact repeats left out), unless a line says otherwise. "new" means t186 + t188 together (27 games).

| match | ver | opponent | W-L | | match | ver | opponent | W-L |
|---|---|---|---|---|---|---|---|---|
| 6901 | y328 | confused | 2-1 | | 7017 | y328 | spaark | 3-0 |
| 6902 | y328 | immutable | 2-1\* | | 7050 | y328 | spaark | 1-2 |
| 6903 | y328 | om-nom | 1-2 | | 7059 | y328 | immutable | 3-0 |
| 6904 | y328 | subscribe-to-caterpillow | 3-0\* | | 7060 | y328 | subscribe-to-caterpillow | 0-2 (dup g0) |
| 6937 | y328 | confused | 1-2 | | 7140 | y328 | spaark | 1-2 |
| 6938 | y328 | immutable | 1-2\* | | 7143 | y328 | subscribe-to-caterpillow | 3-0 |
| 6939 | y328 | om-nom | 1-2 | | 7157 | t186 | spaark | 3-0 |
| 6940 | y328 | subscribe-to-caterpillow | 0-3\* | | 7181 | t186 | immutable | 2-1 |
| 6941 | y328 | just-woke-up | 0-3 | | 7191 | t188 | scienceqiu | 3-0 |
| 6942 | y328 | spaark | 1-2\* | | 7204 | t188 | just-woke-up | 2-1 |
| 6965 | y328 | subscribe-to-caterpillow | 2-1 | | 7205 | t188 | immutable | 2-1\* |
| 6979 | y328 | om-nom | 2-1 | | 7206 | t188 | om-nom | 2-1 |
| 6980 | y328 | immutable | 1-2\* | | 7207 | t188 | spaark | 2-1\* |
| 6981 | y328 | confused | 1-2 | | 7208 | t188 | confused | 2-1 |
| 6982 | y328 | subscribe-to-caterpillow | 2-1\* | | 7209 | t188 | gone-whalin | 2-1\* |
| 6983 | y328 | just-woke-up | 0-2 (dup g0) | | | | | |
| 6984 | y328 | spaark | 1-2\* | | | | | |
| 6999 | y328 | immutable | 3-0 | | | | | |
| 7016 | y328 | immutable | 1-2 | | | | | |

\* = unranked. "dup" = the game repeats an earlier one and is left out.

**Repeats** (`t147_dups`). m6983g0 = m6941g2 (just-woke-up, PlumberGame) and m7060g0 = m6982g2 (subscribe-to-caterpillow, Oasis), both y328 repeating y328.

**Record** (repeats left out): **56-44 (56%)**.
- By version: y328 36-37 (49%), t186 5-1, t188 15-6 (71%).
- The top five (just-woke-up, spaark, subscribe-to-caterpillow, immutable, om-nom) 45-37; the rest (confused, gone-whalin, scienceqiu) 11-7. Ranked 39-28, unranked 17-16.
- Per opponent: confused 6-6, gone-whalin 2-1, immutable 15-9, just-woke-up 2-6 (y328 0-5), om-nom 6-6, scienceqiu 3-0, spaark 12-9, subscribe-to-caterpillow 10-7.
- The 7 losses of t186/t188: m7181g0 immutable Mirage (paint, r295), m7204g0 just-woke-up TheBest (paint, r357), m7205g0 immutable AlarmClock (paint, r397), m7206g1 om-nom BunnyGame (eliminated, r194), m7207g1 spaark Piglets2 (eliminated, r343), m7208g2 confused walalilongla (paint, r377), m7209g0 gone-whalin Bread (paint, r492).

Ends of the 44 losses: 32 on majority paint, 12 eliminations. Median end r364.

**Did the new versions change the replica results? Not measurably** (`t151_paired`).
- On the 5 (opponent, map) pairings that both new and y328 played, new went 2-3 and y328 3-2.
- On the pairings new shares with y316 it went 4-1 (y316 3-1), and with t140 8-2 (t140 9-3).
- y328 and y316 share 10 pairings: 5-5 against 6-4.
- So y328's 49% comes from the pairings it drew (0-5 against just-woke-up), and t188's 71% rests on 21 games.

**How to run.**
- `lib.py` is study 14's loader with the study 15 dumps (kept outside the repo) and versions from `pkgs.txt`.
  - Environment: `S15VER=t186,t188`, `S15TEAMS=a,b|top|top5`, `S15RANKED=1`, `S15DUP=1` (keeps repeats) and `S15WHICH=won` (t0 only). The `S14*` to `S8*` names still work.
  - `S15SET=main|prev|prev2|prev3|old|all|all2`: `prev` is study 14's t158/t160/y316/y323 set (study 14's dumps), `prev2` study 13's, `prev3` study 12's, `old` study 11's.
- `./run.sh tNN_x.py` writes `tNN.txt`.
  - Rerun from study 14: `t0_medians` (`t0.txt`, `t0_won.txt`), `t106_famine`, `t108_teams`, `t147_dups` and `t151_paired` (both adapted to the new versions), `t148_income`, `t149_towerfall`, `t150_rebuild`, `t152_srp`, `t153_vacant`, `t154_conflict`, `t156_stuck`, `t157_srppick`, `t158_churnrate` (adapted), `t159_ready`, `t160_breakage`, `t161_wear`, `t162_assault`, `t163_attackers`, `t164_kite`, `t165_company` and `t166_pergame`.
  - New: `t167_siege`, `t168_owncolour`, `t169_towerfire`, `t170_lowhp`, `t171_lethal`, `t172_starve`, `t173_paintkite`, `t174_lethal_next`, `t175_srpbreak`, `t176_defense` and `t177_traces`.
  - Copied but not run: `t140_drain`, `t141_nav`, `t143_actions` and `t155_colour`.

## 1. How the games were lost

### Overview (44 losses, 56 wins)
- **Level opening, then outgrown in r100-300.**
  - At r75 the median loss has 15.1 / 16.6% coverage (study 14: 15.9 / 25.0%) with 5 / 5 towers. At r100 it is 20.2 / 20.1%.
  - By r200 it is 30.8 / 35.8% with 6 / 8 towers and 13 / 19 units; by r300 32.0 / 50.9% with 5 / 10 towers and 10 / 31.5 units, while we bank 2313 / 1215 chips.
  - Wins are the mirror: at r200 38.5 / 25.9% with 8 / 5 towers, at r300 48.3 / 26.0% with 10 / 5.
- **Paint-bound and chip-rich** (`t106_famine`).
  - In 51.4% of a loss's rounds every tower of ours holds under 200 paint (theirs 27.1%), while we hold a median 2156 chips.
  - Our last paint tower died for good in 20 of the 44 losses (median r181), theirs in 1. All 12 eliminations lost it first.
- **Our soldiers die to tower fire at two to three times their rate.** Tower fire kills 9.9 of our robots a loss (8.1 soldiers) and 4.6 of theirs (3.2) (`t163_attackers`). The step-out fixed where our soldiers stand (section 3) but not this. What remains is what a soldier does once it is one tower turn from death (2.1), and defense towers (2.2).

### Median timeline of the 44 losses (`t0_medians`, us / them)
| round | n | coverage % | towers | paint towers | money towers | chips | paint | active SRPs | units | soldiers | splashers | moppers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r50 | 44 | 13.2 / 13.0 | 4 / 4 | 1 / 1 | 3 / 3 | 880 / 570 | 1527 / 1664 | 0 / 0 | 8 / 7 | 8 / 5.5 | 0 / 0 | 0 / 1 |
| r75 | 44 | 15.1 / 16.6 | 5 / 5 | 1 / 1 | 4 / 4 | 775 / 735 | 2057 / 2159 | 0 / 0 | 8 / 8.5 | 8 / 6 | 0 / 0 | 0 / 2 |
| r100 | 44 | 20.2 / 20.1 | 5 / 6 | 1 / 1 | 4 / 4 | 1150 / 803 | 1584 / 2574 | 0 / 0 | 9 / 10 | 8 / 7 | 0 / 0.5 | 1 / 3 |
| r150 | 42 | 25.1 / 28.2 | 6 / 7 | 1 / 2 | 5 / 5 | 1200 / 1071 | 1654 / 2690 | 0 / 0 | 11 / 17 | 9 / 8 | 1 / 1 | 2 / 5 |
| r200 | 39 | 30.8 / 35.8 | 6 / 8 | 1 / 2 | 5 / 6 | 2567 / 1150 | 1428 / 2699 | 0 / 1 | 13 / 19 | 7 / 9 | 2 / 3 | 3 / 8 |
| r300 | 34 | 32.0 / 50.9 | 5 / 10 | 2 / 3 | 3.5 / 6.5 | 2313 / 1216 | 1299 / 5333 | 1 / 4 | 10 / 31.5 | 4 / 12 | 3 / 11 | 4 / 10.5 |
| r400 | 15 | 26.4 / 56.7 | 3 / 10 | 1 / 3 | 2 / 6 | 4204 / 1560 | 763 / 4503 | 1 / 4 | 7 / 30 | 2 / 11 | 3 / 8 | 3 / 10 |

Against immutable the gap is splashers and moppers (r200: 2 / 6 and 3 / 7). Against spaark it is soldiers and towers (r200: 4 / 8 soldiers, 5.5 / 8 towers; `t108_teams`).

### The paint economy (`t148_income`, losses, medians per game [means])
| | r101-200 us / them | r201-300 us / them |
|---|---|---|
| paint towers (mean) | 1.7 / 1.9 | 2.4 / 3.3 |
| paint in (base + SRP + new towers) | 3410 / 4005 [3884 / 4723] | 3502 / 7380 [6517 / 13229] |
| of it SRP paint | 0 / 252 [128 / 721] | 399 / 1896 [3164 / 8121] |
| new towers x 500 | 2500 / 2500 | 1500 / 2500 |
| spawn paint | 1900 / 3100 | 1900 / 4900 |
| active SRPs (mean) | 0.2 / 0.9 | 2.7 / 5.0 |
| SRPs completed / broke | 5.2 / 5.3, 0.2 / 0.3 | 5.4 / 8.5, 1.8 / 0.6 |

They complete 0.93 SRPs a loss by r100 (median r76); we complete none (`SRP_ROUND` 100).

### Towers that fall (`t149_towerfall`, `t160_breakage`, `t162_assault`, `t153_vacant`)
- Our towers are killed 1.05 / 2.02 / 5.36 times a loss (r1-100 / r101-200 / r201+), theirs 1.36 / 1.30 / 2.25.
- We rebuild 57 / 49 / 20% of those ruins, they rebuild 85 / 95 / 79%. Their killers take 26 / 37 / 25% of ours; we take 0 / 0 / 3% of theirs. In r201+ their splashers deliver the killing blow on 27% of our towers.
- Fallen ruins: in 76 / 84 / 88% of their vacant rounds ours have enemy paint in the 5x5, theirs 25 / 44 / 49%.
- r201+ assaults: 451 on our towers (47% fall), 376 on theirs (23% fall).
  - Our tower holds a median 14 paint at the first hit, theirs 72.
  - During the assault ours spawn 0.31 units (0.07 moppers), theirs 0.49 (0.26).
  - Ours have 2.69 own robots within r2 20, theirs 4.57.

### SRPs (`t175_srpbreak`, losses)
| | r101-200 us / them | r201+ us / them |
|---|---|---|
| completed a game | 4.61 / 4.75 | 6.02 / 16.25 |
| reached lifetime 50 | 66% / 81% | 37% / 38% |
| broke before the end | 88% / 31% | 78% / 42% |
| completed again after a break | 40% / 78% | 31% / 89% |
| breaker: enemy splash / enemy mop | 54% / 12%, 18% / 11% | 54% / 7%, 13% / 1% |
| breaker: own soldier inside a ruin's 5x5 | 22% / 53% | 29% / 51% |

Every own-soldier break, on both sides, is tower-pattern work inside a ruin's 5x5; none comes from an overlapping SRP or ground painting.

### What the robots do: the siege (`t163`-`t165`, `t169`-`t174`, `t177`)
- **Same kite, same exposure.** Both sides kite at two hits per tower turn in range (`t177_traces`). Per hit the tower shoots ours 0.51 times and theirs 0.52 at 100+ paint (`t173_paintkite`, new). A run is 7.4 hits on both sides (`t169_towerfire`).
- **Different ends.** 27% of our runs end in our soldier's death and 33% in the tower's; theirs end 12% and 50% (losses). The gap stays at equal company: alone, ours die 42% and theirs 19%; with two or more companions, 19% and 8% (`t165_company`).
- **The gap is at low HP** (`t171_lethal`, losses). After a hit, our soldiers die within 5 rounds at these rates, theirs in brackets:
  - at 31-60 HP: 84% (43%);
  - at 61-90 HP: 59% (23%);
  - above 90 HP: 4% (2%).
- **Ours walk back in at lethal HP** (`t174_lethal_next`): see 2.1.
- **The leavers starve** (`t170_lowhp`). Our soldiers that leave a siege alive leave at a median 140 HP with 34 paint, and 71-75% starve within 40 rounds. Theirs leave at 70 HP with 55 paint, and 46% starve.
- **Starvation overall** (`t156_stuck`, `t172_starve`).
  - 13.4 of our soldiers starve a loss, 8.8 of theirs.
  - 55% of ours had hit a tower in the 30 rounds before (theirs 56%).
  - 60% of ours hit 0 paint with no own tower in sight.

## 2. Differences, as codeable rules

The first two rules share study 14's target: our soldiers still die to towers at twice the enemy's rate. Every soldier costs 250 chips and 200 paint, which is exactly what a loss lacks.

### 2.1 Lethal-HP guard: never step back into range one tower turn from death (high; new)
**Evidence** (`t174_lethal_next`, `t171_lethal`, `t164_kite`, `t177_traces`).
- A paint or money tower deals at most 30 a turn to one robot (single 20 plus the defense buff, AoE 10; RULES 9). So at HP <= L = 30 + 5 per enemy L1 defense tower, one more turn in its range kills.
- **After a tower's shot leaves a sieging soldier at HP <= L:**
  - ours (losses) end a turn back in the tower's reach within their next 5 turns 84% of the time, and die to that tower 75%. Only 5% live 20 more rounds;
  - theirs go back 44% and die 37%, and 38% live 20 more rounds;
  - under t186/t188: ours 89% back, 78% dead; theirs 52%, 44%;
  - both sides get there equally often (6.1 / 6.3 times a loss). The difference is the next step, not how often.
- 24-30% of ours could not move on that next turn: the low-paint multiplier left a movement cooldown of 20+. The other three quarters walked back in.
- At 31-60 HP both sides go back (85 / 83%). But ours then die 55% and theirs 24%, because theirs stop at the next shot and ours do not.
- **Hits at HP <= L** are 97% step-ins and 98% end in death: 2.7 a loss for us, 1.4 for them (`t171_lethal`).
- **Under 100 HP** our soldiers step in 9.9 times a loss and 80% die; theirs step in more (12.3) and 35% die (`t164_kite`).
- **Traces** (`t177_traces`):
  - our soldier 10333 (m7191g0) kites a paint tower from 240 HP down to 30, steps in at 30 HP and dies;
  - spaark's 12567 (m7157g0) does the same kite down to 40 HP, stands off two turns, re-enters once (down to 10 HP), then leaves and lives;
  - just-woke-up's 12407 (m7204g0) leaves at 40 HP.
- **Ruled out:**
  - exposure rate: shots per hit match (above);
  - fire from a second tower: only 10% of our soldiers killed by towers took damage from two towers in their last 10 rounds, theirs 18% (`t171_lethal`);
  - defense towers alone: against opponents with no defense towers, ours still die after 7% of their hits at 100+ paint, theirs 1% (`t173_paintkite`).

**Code.** `Soldier.siege` (Soldier.java:54-67).
- The entry (line 57) checks only the paint and the distance.
- The step-in (59: `Nav.moveTo(t)` when r2 > 9) runs at any HP whenever the action is ready.
- The other branches can walk back in too: workRuin (33), deny (35), refill (44) and explore (48). `Nav.moveTo` (Nav.java:27) does not avoid tower range.

**Rule.**
- (a) In `siege()`, when `rc.getHealth() <= L` and r2 > 9: do not step in. Remember t as this soldier's no-go tower until it has refilled, and return false so the turn goes on to SRP, refill or explore. L = 30 + 5 x the enemy defense towers known (2.2); 30 if none are known.
- (b) While HP <= L, `Nav.moveTo` skips moves that end within r2 9 of the no-go tower (16 for a defense tower).
- Keep every step-in above L (theirs re-enter at 31-60 HP too) and the free shot (it fires from inside range).

**Expected size.** Medium, and it fires in nearly every game, locally too.
- Matching their 44% death rate after a lethal shot saves about 2.4 soldiers a game (7.0 x (0.78 - 0.44)), for about 4.4 fewer hits (220 tower damage).
- The soldiers saved have about 48 paint, as theirs do.

**Prior attempts.** Study 11 2.2's HP exit: t141 (70 HP, -53) and t142 (100 HP, -92), both on t135 before the step-out.
- It barred the free hit and every step-in at 31-70 HP, which theirs make and survive.
- It then stepped one tile with the old three-direction step.
- y289 (siege exit at 50 paint) lost 20.

**Candidates.** h1 = (a); h2 = (a) + (b); h3 = h2 with L = 40 (a margin for a second tower's AoE).

### 2.2 Defense towers: do not kite them, count their buff (medium-high on the replica; needs a sparring bot locally)
**Evidence** (`t176_defense`, `t172_starve`, `t171_lethal`, `t164_kite`).
- **Who builds them.** immutable and spaark build 1.58 and 1.57 defense towers a game (spaark's first at a median r156, immutable's at r305). subscribe-to-caterpillow builds 0.59, just-woke-up 0.12, the rest none, and we build none. immutable and spaark are 45 of the 100 games and 18 of the 44 losses.
- **What they cost us** (immutable / spaark):
  - their defense towers kill 7.1 / 9.3 of our robots a game (soldiers 4.6 / 5.4, splashers 2.0 / 2.7, moppers 0.5 / 1.1);
  - they deal 1793 / 1990 damage to our robots a game, against 3056 / 3652 from their paint and money towers;
  - tower fire kills 10.1 / 14.9 of our soldiers a game, against 4.1-8.4 for the other opponents. 46% / 36% of those soldiers took damage from a defense tower in their last 10 rounds.
- **What we get back.** Our soldiers hit their defense towers (2000 HP each) 26.3 / 20.3 times a game and destroy 0.46 / 0.33 a game.
- In losses, 18% of our hits land on a defense-buffed side, and 40% of those hitters die, against 13% unbuffed (`t164_kite`).

**Code.**
- `Unit.scanEnemyTowers` (Unit.java:103-116) remembers only the nearest enemy tower's location, not its type, and `Soldier.siege` (54-67) kites whatever it is.
- A defense tower outranges the kite: r2 16 against the soldier's 9, and 40 + 20 a turn. Each L1 defense tower also adds 5 to every tower's single shot (RULES 9).
- `stepOut` uses the r2 16 reach only when the tower is in sensing range that turn (Soldier.java:76-79).
- The splasher already skips defense towers as targets and stands off r2 16 (Splasher.java:130, 143). The soldier has no such check.

**Rule.**
- (a) `scanEnemyTowers` keeps the type. `siege` skips defense towers, and paint or money towers within r2 16 of a known defense tower unless the target has 200 HP or less.
- (b) The known enemy defense towers count into L (2.1) and into `stepOut`'s reach.
- (c) `Nav` keeps soldiers and splashers out of r2 16 of known defense towers.

**How to test locally.** No pool bot builds defense towers, so the local tourney cannot see this rule.
- Build a sparring bot s1: t188 whose `wantType` returns `LEVEL_ONE_DEFENSE_TOWER` for every fourth tower from r150, when it knows an enemy tower within r2 100 of the ruin. That is about spaark's 1.6 a game.
- Play d1 and t188 against s1 on the same maps and seeds, in a matrix run on the box rather than the pool.
- Then send a d1 that gains against s1 through the normal pool, to check it costs nothing elsewhere.

**Expected size.** Medium on the replica (45% of the games), and nothing locally without s1.

**Prior attempts.** None. Study 14 2.3 proposed it, and it was not built for lack of a local test.

**Candidates.** d1 = (a); d2 = d1 + (b) + (c); s1 = the sparring bot.

### 2.3 Leave a siege with the paint to get home (low-medium; a tuning with new evidence)
**Evidence** (`t170_lowhp`, `t173_paintkite`, `t172_starve`).
- **The leavers.** 8.3 of our sieges a loss end with the soldier alive and the tower standing.
  - Ours leave at 34 paint (`SOL_SIEGE_PAINT` 30); 71-75% starve within 40 rounds, alive 10-14 of those rounds, painting 0.7 tiles.
  - Theirs leave with 55-59 paint; 46% starve, alive 20-24 rounds, painting 2-3 tiles.
- **Below 50 paint our kite breaks** (new). Shots per hit are 0.87 at 30-49 paint and 1.63 under 30, against 0.51 at 100+. In->in is 16% and 67% of those hits (theirs 20% and 37%).
- **Starved soldiers.** 13.4 of ours a loss, 8.8 of theirs. Both sides' starved soldiers had last hit a tower at about 30 paint (ours 30, theirs 27). So this is a difference of degree.

**Code.** `Tune.SOL_SIEGE_PAINT` at the siege entry (Soldier.java:57).

**Rule.** p1: `SOL_SIEGE_PAINT` 50. p2: exit when paint is below 2 x the Chebyshev distance to the nearest known own paint tower + 10 (a robot loses 2 paint a turn on enemy paint; RULES 5.3).

**Expected size.** Small. The cost it targets is the starved soldiers.

**Prior attempts.**
- y219 (50, before the step-out) and y289 (exit at 50 on t140, -20 after 280 games).
- y350 (20 on t188, -46).
- The higher direction has not been tried since t186's step-out.

**Candidates.** p1 on t188 (one constant); p2.

### 2.4 Lower priority (measured, but tried before or not a difference)
- **Towers drained before the assault** (`t162_assault`).
  - In r201+ our towers hold 14 paint at the first hit, theirs 72. Ours spawn 0.07 moppers during the assault, theirs 0.26, and 47% of ours fall against 23%.
  - Tried: t108 and t109 (spawn a mopper when hit, -38) and t47.
  - A paint floor in money towers works against the churn, which needs a drained money tower. Not proposed alone.
- **SRPs broken by their splashers** (`t175_srpbreak`).
  - Enemy splashes cause 54% of our SRP breaks in losses. 88% of our r101-200 SRPs break (theirs 31%), and we redo 31-40% (theirs 78-89%).
  - Tried: the redo after 150 rounds (t177, t180), SRP distance to enemy towers (y343, y345, y351) and SRPs from r60 (t154).
  - y356 (SRPs from r80; they complete 0.93 by r100, median r76) is already queued.
- **Own soldiers breaking our SRPs** happens only through tower-pattern work inside a ruin's 5x5: 22-29% of our breaks in losses and 41-51% in wins. Theirs do the same (51-53%). Not a difference.
- **Fallen ruins under enemy paint** (`t153_vacant`, `t160_breakage`). See section 1. Moppers and splashers clearing them were tried (t90-t100, t117, t120).
- **Paint-tower patterns stay broken** (`t168_owncolour`, `t161_wear`).
  - They are intact in 14% of tower-rounds under t188 (12% under y328).
  - Our own soldiers break 69% of them first, at a median 8 rounds after completion.
  - This matters only for a rebuild.

## 3. What changed since study 14
- **Record.** 56% (56-44), down from 62%, but not a measured change (`t151_paired`; see the header). just-woke-up is still our worst opponent (2-6; study 14 2-7).
- **The opening gap closed.** At r75 coverage is 15.1 / 16.6% (study 14: 15.9 / 25.0%) with 5 / 5 towers. The gap now opens in r100-300.
- **Tower deaths and rebuilds** are about the same. Ours are killed 1.05 / 2.02 / 5.36 a loss (0.90 / 1.81 / 5.87) and rebuilt 57 / 49 / 20% (61 / 52 / 35%).
- **Paint famine** is unchanged: 51.4% of rounds (52.8%), with 2156 chips banked (2687.5). The last paint tower died for good in 20 of 44 losses (11 of 31).

**Question 2a: did the step-out keep soldiers out of range?** Yes (`t167_siege`).
- In->in hits fell from 14% (y328) to 5% (t186 3%, t188 6%); theirs are 4-7%.
- A step that stays in range ("in->in moved") fell from 7.8% to 1.3%.
- What is left is mostly stuck soldiers: 3.0% of hits have a movement cooldown of 10+ and 1.2% are free; 85% of these are under 100 paint.
- On the 5 pairings shared with y328, in->in is 6% against 14%. On the 4 shared with study 14's versions, 5% against 12%.

**Question 2b: did it cut soldier deaths to tower fire?** No.
- Deaths within 5 rounds per hit: new 14.1%, y328 13.9%. Our soldiers killed by towers: 9.5 a game against 9.0.
- Hits per soldier killed by a tower: 17.9 against 18.8 (theirs about 37).
- On the shared pairings: 8.0 against 9.6 a game with y328, and 20.2 against 16.0 with study 14's versions. The latter are mostly spaark and immutable pairings.
- By paint band the death rate per hit did not move (`t173_paintkite`): at 100+ paint 7% to 9%, at 70-99 17% to 17%.
- The geometry was one cause, but the death rate is set by re-entry at lethal HP (2.1) and by defense towers (2.2).

**Question 2c: how often do our own wrong-colour tiles block our patterns, after colourAt?** Less on money towers, the same on paint towers, and no more churns (`t168_owncolour`, `t158_churnrate`).
- Where the wanted colour is secondary and the tile is empty, our soldiers now paint it right 93% of the time (t188), against 20-24% under y316, y328 and t186. That is colourAt working.
- **Money towers.** Own wrong-colour tiles per tower-round fell from 2.68 (y328) to 1.63, and intact tower-rounds rose from 40% to 50%.
- **Paint towers.** Intact tower-rounds stayed at 14% (y328 12%), with 3.33 own wrong tiles per tower-round (4.32).
- **Drained money towers with 2000+ chips.** Intact rose from 17% to 25%, but our own other colour still blocks 68% (75%). Theirs are intact 39-57%.
- **Churns.** 14.6 per 1000 of our robot-turns under t188, 14.5 under y328: the same.
- What still blocks:
  - repaints of tiles that are already ours: where secondary is wanted over our primary, we get it right only 36% of the time;
  - SRPs that disagree with the tower (section 4, item 5).

## 4. Broken in our bot (t188)
1. **`Soldier.siege` steps in at any HP** (Soldier.java:58-59), down to certain death. See 2.1.
2. **Soldiers do not know defense towers** (Unit.java:103-116; Soldier.java:54-93).
   - The nearest enemy tower is remembered without its type, and `siege` kites a defense tower (2000 HP, r2 16) like any other.
   - `stepOut`'s reach is 16 only when the tower is sensed that turn.
   - The splasher has the check (Splasher.java:130, 143). See 2.2.
3. **`colourAt` only colours empty tiles** (Soldier.java:460-492).
   - `paintHere` and `paintNear` paint `EMPTY` tiles only, so a tile already in our wrong colour stays wrong (2c).
   - It also reads `Towers.loc` entries that may be stale (a dead tower's pattern), and it takes the first 5x5 containing the tile.
4. **The siege paint gate also gates the step-out** (Soldier.java:57, 64).
   - After the free shot (24-28, which fires from 5 paint), a soldier under 30 paint gets no step-out from `siege()`. Under 30 paint, 67% of our hits are in->in (theirs 37%; `t173_paintkite`).
   - t192 (step out after the free shot) covers this and was flat.
5. **`pickSrp` checks agreement with money towers only** (Soldier.java:351), never with paint towers.
   - 73% of t188's SRPs beside one of our money towers disagree with it (`t157_srppick`).
   - Over all versions, 506 of the 538 disagreeing SRPs were picked before the soldier had seen the tower, which already stood.
   - A `workSrp` re-check was tried (t168, -26).
6. **Still standing from study 14:**
   - `Churn.rebuild` completes money towers only (Churn.java:36-46);
   - `Churn.repairPattern` shoots with `rc.canAttack` (Churn.java:61), which is true on enemy paint;
   - `Towers.forget` leaves dry flags behind (Towers.java:33-37; t185, t189 and t191 were flat to -56).

## 5. Suggested test order
1. **h1** (2.1 a) against t188. It is small and fires in every game. Then **h2** if h1 is level or better.
2. **p1** (2.3, one constant) on t188, or on the h winner.
3. **s1**, then **d1** and **d2** against s1 in a matrix run (2.2). Only after that, send d1 through the pool, alone or bundled with a crowned h bot.
4. y356 (queued, SRPs from r80) as planned.

**Not measured:**
- what our soldiers do between leaving a siege and starving: they paint 0.7 tiles in 40 rounds, but where they walk was not traced;
- the t186/t188 losses alone: only 7 games;
- whether spaark's and immutable's defense towers sit where our sieges arrive, or just where their ruins happened to be.

**Dump directories to delete afterwards** (all in the session scratchpad, about 1.5 GB):
- `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study15/dump` (139M) and `.../study15/cache` (89M);
- `.../scratchpad/study14/dump` (115M) and `.../study14/cache` (73M);
- `.../scratchpad/study13/dump` (355M) and `.../study13/cache` (232M);
- `.../scratchpad/study12/dump` (6.1M) and `.../study12/cache` (161M);
- `.../scratchpad/study11/dump` (200M) and `.../study11/cache` (126M).

Study 15's `S15SET=prev|prev2` comparisons and its `t147`, `t151` and `t158` reruns read the study 14 and 13 dumps and caches, and the study 12 and 11 summaries. Delete those only when no rerun is planned.

## Summary: the top three
1. **2.1 Lethal-HP guard.**
   - After a tower's shot leaves our sieging soldier one turn from death, it walks back into range 84-89% of the time and dies 75-78%. Theirs go back 44-52% and die 37-44%. Both sides get there about 6-7 times a game.
   - Gate the step-in in `Soldier.siege` (Soldier.java:59) on HP > 30 + 5 x known defense towers, and keep `Nav` out of that tower's range while under it.
   - This is narrower than t141: no ban at 31-70 HP, and the free shot is kept.
2. **2.2 Defense towers** (replica-first; test against a sparring bot).
   - immutable and spaark build about 1.6 a game. These kill 7.1-9.3 of our robots a game and are involved in 36-46% of our soldiers' tower deaths against them.
   - We hit them 20-26 times a game and destroy 0.33-0.46.
   - Keep the type in `Unit.scanEnemyTowers` (Unit.java:103-116), skip them in `siege`, and count their buff.
3. **2.3 Leave with paint to get home.**
   - Our siege leavers exit at 34 paint and 71-75% starve within 40 rounds; theirs exit with 55 paint and 46% starve.
   - Below 50 paint our kite takes 0.87-1.63 shots per hit, against 0.51.
   - Retest `SOL_SIEGE_PAINT` 50 on t188 (y289's -20 predates the step-out).

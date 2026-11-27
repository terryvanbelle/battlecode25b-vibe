# Field study 11 (2026-11-27): t122 on the replica since submission 76

This study used replays only. I read no competitor code and no write-ups, made no `contest.py` call, ran no games, and edited no bots.

All games here are **t122** (submission 76); the rules use `bots/t122` line numbers. Since then **t135** (t122 + study 10 2.6d, the lone-soldier mark skip) was crowned at 06:10 (`champions.csv`: +9 ±22 in 262 fresh games, +14 overall) and is now `src/vibe`. It differs from t122 only at Soldier.java:226 (one line became five), so every t122 line number holds for t135 up to 226 and is 4 higher after it. `pkgs.py` checked every replay header: our package is t122 in all 37 matches, and every opponent package is one study 10 already saw (`pkgs.txt`), so same-opponent comparisons with study 10 are like for like.

The data is 37 matches (\* = unranked):
- the **32 listed matches, 4692-5012**;
- **5 earlier t122 matches that study 10 did not have: 4661, 4662, 4663, 4664 and 4682.** They are included in every number below; `S11SET=listed` drops them.

| match | opponent | W-L | | match | opponent | W-L |
|---|---|---|---|---|---|---|
| 4661 | subscribe-to-caterpillow | 1-2 | | 4841 | scienceqiu | 2-1 |
| 4662 | immutable | 3-0\* | | 4842 | gone-whalin | 1-1\* (g2 dup) |
| 4663 | om-nom | 0-3 | | 4878 | immutable | 1-2 |
| 4664 | spaark | 2-1\* | | 4879 | scienceqiu | 1-2\* |
| 4682 | gone-whalin | 2-1 | | 4880 | spaark | 2-1 |
| 4692 | spaark | 0-3 | | 4881 | gone-whalin | 1-2\* |
| 4699 | immutable | 0-3 | | 4916 | spaark | 1-2 |
| 4716 | lobster-roll | 0-3 | | 4917 | scienceqiu | 2-1\* |
| 4725 | lobster-roll | 2-1 | | 4918 | immutable | 1-2 |
| 4726 | gone-whalin | 0-3\* | | 4919 | gone-whalin | 3-0\* |
| 4765 | gone-whalin | 3-0 | | 4920 | subscribe-to-caterpillow | 2-1 |
| 4766 | scienceqiu | 2-1\* | | 4921 | lobster-roll | 0-3\* |
| 4787 | scienceqiu | 0-3 | | 4954 | spaark | 1-2 |
| 4800 | varunvejalla | 3-0 | | 4955 | scienceqiu | 1-1\* (g0 dup) |
| 4805 | spaark | 0-3 | | 4956 | immutable | 1-2 |
| 4806 | immutable | 2-1\* | | 4957 | gone-whalin | 1-2\* |
| | | | | 4981 | gone-whalin | 2-1 |
| | | | | 4992 | scienceqiu | 3-0 |
| | | | | 4993 | lobster-roll | 2-1\* |
| | | | | 5010 | gone-whalin | 1-2 |
| | | | | 5012 | gone-whalin | 1-1 (g1 dup) |

Three games exactly repeat an earlier one and are left out (`S11DUP`, `t126`): m4842g2 = m4682g2, m4955g0 = m4841g0, m5012g1 = m4726g1 (Jail, lost at r78).

That leaves **108 games: 50 won and 58 lost (46%)**. Study 10 had 100-75 (57%).
- **Against the eight top teams:** 43-50 (46%); study 10 64-56 (53%). Against lobster-roll and varunvejalla: 7-8.
- **Ranked:** 29-39. **Unranked:** 21-19. The 32 listed matches alone: 42-51.
- Win types: 46 of the losses by majority paint, 12 eliminations; one win went to r2000 (Leaf).

| opponent | t122 | study 10 (t111 + t118) | | opponent | t122 | study 10 |
|---|---|---|---|---|---|---|
| gone-whalin | 15-13 | 9-11 | | spaark | 6-12 | 15-17 |
| scienceqiu | 11-9 | 12-8 | | lobster-roll | 4-8 | 10-8 |
| immutable | 8-10 | 9-3 | | om-nom | 0-3 | 4-5 |
| subscribe-to-caterpillow | 3-3 | 13-5 | | varunvejalla | 3-0 | 8-5 |

**Is t122 worse than t111 / t118? Not measurably** (`t127`). Games are deterministic (the three repeats are identical), so a pairing (opponent package, map) played by two of our versions isolates the version.
- On the 34 pairings t122 shares with t111 or t118, t122 went 16-20 (44%), t111 11-13 (46%), t118 7-4.
- t122 lost 6 pairings that every older game won and won 4 that every older game lost.
- Most of the drop from 57% is the schedule: in study 10, t111 went 18-6 against four weak teams (placeholder-name-2, podemice, slifland, angtn) that t122 never met, and t122 met spaark 18 times.

**How to run.**
- `lib.py` is study 10's loader with the t122 dumps. Environment variables:
  - `S11VER`, `S11TEAMS` (`top` = the eight teams), `S11RANKED=1`;
  - `S11SET=main|listed|prev|all` (`main` = the 37 t122 matches, `listed` = the 32, `prev` = study 10's set 3999-4602);
  - `S11DUP=1` keeps the repeats. The `S10*` / `S9*` / `S8*` names still work.
- `./run.sh tNN_x.py` writes `tNN.txt`. t0-t125 are earlier scripts rerun on this set (those without a `.txt` were not rerun); **t126-t136 are new** (`t126_dups`, `t127_paired`, `t128_chipuse`, `t129_opening`, `t130_drytest`, `t131_ledger`, `t132_markwait`, `t133_shot`, `t134_siege`, `t135_siege2`, `t136_topup`).
- Dumps: `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study11/dump/mM` (37 matches, `covMismatch` 0, dump version 3); caches in `.../study11/cache`; study 10's set is read from `.../study10/`. The scratchpad can be cleared. Rebuild with `~/opt/jdk21/bin/java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`, one java process at a time.

## 1. How the games were lost

### Overview
- **By map size** (`t40`, paintable tiles, W-L; study 10 in brackets):

  | paintable tiles | now | study 10 |
  |---|---|---|
  | up to 500 | 4-4 | 3-7 |
  | 501-900 | 7-17 | 21-20 (much worse now) |
  | 901-1600 | 18-16 | 30-22 |
  | 1601-2500 | 15-15 | 32-12 (worse) |
  | over 2500 | 6-6 | 14-14 |

  - By short side: 25 or less 6-12 (8-15); 26-35 18-26 (40-31); over 35 26-20 (52-29).
  - Median loss round: r372 on maps up to 900 tiles, r421 on larger maps (study 10: r316 / r417).
- **Towers at r100** (ours minus theirs):

  | at r100 | won | lost |
  |---|---|---|
  | behind | 2 | 16 |
  | level | 7 | 13 |
  | ahead | 41 | 29 |

  Half the losses (29 of 58) were ahead at r100, and only 16 were behind (study 10: 30 and 32 of 75). **t122 loses later, from a lead.**
- **Eliminations:** 12 of 58 (study 10: 18 of 75). All 12 lost their last paint tower for good first (median r186, 3.5 robots alive then).
- **Last paint tower dead for good** (`t106`): 21 of 58 losses (median r198; study 10 33 of 75), 19 of the 50 losses to the top teams, 0 of 50 wins (theirs: 12 of our wins).
- **Paint-bound, chip-rich** (`t106`, `t49`):
  - every tower of ours holds under 200 paint in 58.8% of the rounds of a loss (theirs 22.0%; study 10 56% / 28%), while we hold a median 2452 chips;
  - from r40, 67% of our tower-turns are paint-blocked (paint under 200 with 1250+ chips) against their 37%. Theirs are more often short of both (31% / 18%) or of chips (14% / 7%): they spend what they have.

### Median timeline of the 58 losses (`t0`, us / them; median end r410.5, study 10 r392)

| round | coverage % | towers | paint towers | chips | paint (units + towers) | robots (S / X / M) |
|---|---|---|---|---|---|---|
| r50 | 13.8 / 17.1 | 4 / 4 | 1 / 1 | 895 / 700 | 1405 / 1661 | 8 / 7 (8/6, 0/0, 0/1) |
| r100 | 22.2 / 25.0 | 6 / 5 | 1 / 1 | 1100 / 950 | 1758 / 2066 | 9 / 10 (7/7, 0/0, 1/3) |
| r150 | 31.7 / 30.0 | 6 / 7 | 1 / 1 | 1620 / 1390 | 1510 / 2576 | 11 / 14 (7/7, 1/1, 3/6) |
| r200 | 31.9 / 34.5 | 6.5 / 7.5 | 1 / 2 | 1994 / 1292 | 1376 / 2805 | 12 / 20 (6/8, 1/2, 4/8) |
| r300 | 28.6 / 46.8 | 5 / 10 | 1 / 2.5 | 2965 / 1428 | 1089 / 4203 | 9 / 26.5 (3/9, 2/5, 3/12) |
| r400 | 27.1 / 53.1 | 4 / 13 | 1 / 3.5 | 3540 / 1957 | 1047 / 6306 | 7.5 / 44.5 (3/12.5, 3/8.5, 1.5/18) |

Active SRPs: 0 / 1 at r200, 0 / 1.5 at r300, 0 / 3.5 at r400; theirs peak at 36-41 on DefaultHuge and Oasis, ours at 19 at most. The picture is study 9's and study 10's again: level or ahead at r100, then from r150 they turn paint into units and towers while our chips pile up.

### Where the lead comes from (`t107`, `t68`, `t61`, `t62`, `t72`, `t74`)
- **The tower lead becomes permanent at a median r162.5** (p25 r106, p75 r261; study 10 r197): by r100 in 13 games, in r101-200 in 22, later in 23.
  - In the 50 rounds before it they built 113 towers (70 on new ruins, 34 rebuilt, 9 taken from us) and lost 56.
  - We built 53 (30 new, 22 rebuilt, 1 taken) and lost 63.
- **Tower flow r101-250** (`t68`, the 53 losses that reach r250; sums, us / them):

  | | us | them |
  |---|---|---|
  | standing at r100 | 309 | 277 |
  | built on new ruins | 93 | 198 |
  | rebuilt after a kill | 65 | 103 |
  | taken from the other side | 4 | 20 |
  | churn rebuilds | 183 | 78 |
  | killed by the other side | 142 | 92 |
  | standing at r250 | 325 | 500 |

  So the r101-250 swing of about 4 towers per game is mostly **new ruins (-105)**, then kills (-50) and rebuilds (-38).
- **We stop at five new ruins** (`t61`). We reach our 5th new-ruin tower in 34 of 58 losses (median r79, theirs r120), the 6th in 28 (r101), the 7th in 19 and the 8th in 14. They reach the 6th in 53, the 7th in 51 and the 8th in 49 (r160 / r181 / r238). In our wins we reach the 8th in 38 of 50.
- **Two paint towers at once:** we get there in 22 of 58 losses (median r126.5) and in 44 of 50 wins. They get there in 44 of 58 of our losses. Three paint towers: 14 of 58 losses, 40 of 50 wins.
- **Where their r101-250 new towers are** (`t74`): of 198, 125 are in their half, 52 in ours and 21 in the middle. 86 of the 198 had our paint in the 5x5 in the 50 rounds before (they cleaned it); 28 of our 93 did.
- **The free ruins in our half** (`t62`, `t72`, losses):
  - At r100, 287 free ruins sit in our half: 139 with no enemy tile, 77 with 1-4, 71 with 5+.
  - Clean ones: we marked 26 of 139 within 50 rounds and built 25; our soldiers spent a median 2 turns within Chebyshev 4 of each in those 50 rounds. Their next owner: us 70, them 45, never 24. In the wins: 157 clean, 53 built within 50 rounds, a median 12 soldier-turns near each.
  - Enemy-painted ones (148): we built 4 within 50 rounds; they built 86 of them eventually, we 27.
  - 108 of the free ruins in our half were never within sight of our robots by r100 (`t72`), nearly all on maps of 45x45 and up (giver 9, maze 8 and 7, DonkeyKong 11, DefaultHuge 5 and 7, Oasis 6, memstore 6 and 4). We built 41 of them later and they built 43.

### The opening, r1-150 (`t129`, `t98`, `t102`, `t65`, `t90`, `t133`, `t46`)
In the losses, us / them:
- **Spawns.** The first five come by r10 for both. Ours #6-#8 come at r18.5 / r30 / r35.5, theirs at r26 / r38 / r56.5. By r50 we have spawned 8, they 7. Their first mopper comes at r43, ours at r91.5 (3 / 1 moppers spawned by r100).
- **Towers.** New-ruin builds #1-#5: r17 / r20, r36 / r35.5, r52 / r53, r64 / r78.5, r79 / r120.5, on ruins of the same rank (2nd-3rd nearest) and front position. Painters per build 1.5 / 2, paint per build 120 / 120, parallel attempts 1.9 / 2.0. Our opening builds are as fast as theirs, faster from #4.
  - The exception is the 16 losses behind at r100: our 2nd tower came at r65 on the 9th-nearest ruin (d2 324; theirs r52, rank 4.5, d2 123), the 3rd at r183 (theirs r85).
  - Tower #3 in the level/ahead losses: pattern ready to built 17 rounds for us, 7 for them (`t98`), with 720 / 810 chips at the ready round.
- **Marks.** By r150 we place 7 pattern marks per loss (425 in all, 25 paint each). They place **none**, but 11.5 single marks and 3 unmarks per loss (1488 and 225 in all). Their first towers carry no mark at all in 48 of 105 cases (`t102`).
- **SRPs.** Their first comes at r76.5, ours at r133; completed by r150: 121 / 67 in all.
- **Defense towers.** Their first comes at a median r155, in 29 of the 58 losses. We never build one.
- **Fights.** Towers killed: r1-100 58 of ours / 76 of theirs, r101-200 90 / 60 (`t46`). Robots killed by towers by r150: 183 of ours, 95 of theirs.
- **Exploration is not the gap in the median game** (`t65`): by r100 we have seen 100% of the ruins in our half (median), they 92%. The unseen ones are the big-map cases above.
- Neither starting paint tower is dead by r150 in 42 of the 58 losses (`t90`).

### Chips (`t128`, `t76`, `t78`, `t42`)
Losses, per game medians (sums over the 58 games in brackets), us / them:

| | r101-200 | r201-300 | r301-400 |
|---|---|---|---|
| income | 10500 / 11827 | 10282 / 14841 | 11088 / 21525 |
| new-ruin towers | 1000 / 2000 [73k / 148k] | 0 / 1000 [33k / 102k] | 0 / 1000 [9k / 50k] |
| rebuilt / taken towers | [48k / 67k], [3k / 9k] | [39k / 68k], [1k / 26k] | [37k / 47k], [0 / 26k] |
| churn rebuilds | 2000 / 0 [123k / 40k] | 1000 / 0 [96k / 82k] | 500 / 0 [36k / 86k] |
| units | 3500 / 4600 | 3250 / 5425 | 2775 / 7300 |
| upgrades | [42.5k / 95k] | [165k / 252.5k] | [137.5k / 300k] |
| SRPs | [32k / 29.8k] | [30.8k / 40.8k] | [11.6k / 35.6k] |
| mean chips held | 1827 / 1309 | 2469 / 1698 | 3061 / 2012 |
| share of rounds ending at 2500+ | 14.5% / 2.5% | 46.5% / 22% | 60% / 29% |
| spent per round when starting it with 2000+ | 142 / 205 | 122 / 244 | 114 / 318 |

- In r1-100 they put 11400 chips into SRPs (we 0) and both sides spend 4000 on new towers.
- **Idle chips** (`t76`): we end a median 41% of the rounds r101-400 of a loss at 3000+ chips (study 10 28%), they 6%. In our wins it is 6% / 2%.
- **In our wins we are the fast spender**: 236-290 chips per rich round against their 161-197. The conversion speed follows paint, not a different spending rule.
- **Upgrades** (`t78`; the starting towers begin at L2). They upgrade paint towers to L2 118 times in 29 of the 58 losses (first at a median r242) and to L3 59 times in 15; money towers to L2 132 times in 27 losses. We upgrade built paint towers to L2 30 times in 16 losses, paint towers to L3 37 times in 29 losses (r246; mostly the starting tower: 5000 chips for +5 paint a round), and money towers to L2 76 times in 25 losses (r292).
- **Churn** (`t42`): we churn 349 money towers in the losses (rebuilt 343) and they 415 (132 of them in one maze game). Our churn blockers, in tower-rounds of a drained L1 money tower: enemy in view 5763, no ally adjacent 5088, other 2757.

How the top teams use a surplus: they rarely have one. They hold 1300-2000 chips and turn them into units (spawn paint 1400 / 700 per loss in r101-200 from paint towers), new and taken towers, and upgrades. That needs paint income, which they have and we don't (paint-tower income r201-300: 1539 / 2569 per loss, us / them, `t47`).

### What goes wrong
1. **Paint towers spend 43% of their paint on refills, and t122's dry flags raised it** (`t120`, `t130`, `t136`).
   - r101-200 of the losses, per game: robots withdrew 520 paint from our paint towers (study 10 270) and our paint towers spent 700 on spawns. Theirs: 254 withdrawn, 1400 spawned. Our paint towers spawned 3 units, theirs 8.
   - r201-400: withdrawn 870 / 1825, spawned 2050 / 5150; spawns 8.5 / 24.
   - So 43% of our paint-tower outflow in r101-200 goes to refills, 15% of theirs. Both sides draw most refills from money towers (972 / 610 per loss), but ours also take 520 from paint towers, theirs 254.
   - Dry flags (Unit.java:23-30) are measured below (section 3). They brought robots back sooner and made them take more, without raising spawns.
2. **We lose our soldiers in sieges and to drain** (`t131`, `t133`, `t134`, `t135`, `t123`).
   - Robots lost, sums over the losses, us / them:

     | | r1-100 | r101-200 | r201-300 |
     |---|---|---|---|
     | spawned | 654 / 709 | 640 / 858 | 648 / 1372 |
     | shot by towers | 101 / 57 | 161 / 81 | 166 / 140 |
     | starved | 71 / 52 | 292 / 221 | 460 / 406 |
     | of those drained by moppers first | 50 / 8 | 193 / 74 | 284 / 142 |
     | net change | +482 / +600 | +187 / +554 | +22 / +812 |

   - **Tower fire hits our robots while they hit towers**: 99% of the tower damage our robots take in r1-100 and 89% in r101-200 comes in a round they attacked a tower (`t133`). Of our robots that died within 3 rounds of a tower hit, 93 of 98 (r1-100) and 128 of 178 (r101-200) were sieging; theirs 46 of 57 and 51 of 89.
   - **Lone sieges kill our soldiers** (`t134`, `t135`). A siege episode is one soldier's run of hits on one enemy tower. Our lone episodes end with the soldier dead and the tower standing 56% / 44% / 47% of the time (r1-100 / r101-200 / r201-400); theirs 35% / 27% / 26%. Counting soldiers that die within 3 rounds of their last hit, we lose 1.68 / 2.22 / 2.29 soldiers per tower our soldiers kill, they 1.03 / 0.73 / 0.64. See 2.2.
   - Drain then starvation: 193 / 74 in r101-200, and 155 / 68 in our wins too. Our starving soldiers sit at 0 paint for their last 10 turns (median paint 10 turns before death 0, 20 turns before 61); theirs had 10.5 and 38. A 0-paint robot can neither move nor withdraw (RULES 3).
3. **Moppers: the same per mopper, a quarter of the count** (`t44`, `t54`, `t45`).
   - Per 100 mopper-turns, ours and theirs are alike: mop attacks on robots 4.4 / 4.7, tiles mopped 15.6 / 11.0, swings 3.0 / 5.5.
   - But they have 4.3 times our mopper-turns (295150 / 69328 in the losses), 2 alive against 0.2 in r51-100, 5.5 / 2.7 in r101-200, 10.2 / 3.6 in r201-300.
   - Moppers are 16% of our built paint towers' spawns (123 of 770) and 12% of the starting tower's; theirs 35% and 36%. Our money towers spawn at most 2 units each (0 of 306 that lived 100+ rounds spawned a 3rd); theirs up to 5.
4. **Blocked ruins** (`t111`, losses).
   - We completed 42% of 686 attempts, they 67% of 1089. By phase: r101-250 42% / 71%, r251+ 28% / 69%; the other side took 19% / 1% and 21% / 1%.
   - 324 of ours met an enemy tile (12% completed). With an own splasher in view after the first enemy tile 15% of 108 completed, with a mopper 23% of 165, with neither 0% of 136. Theirs: 501, 51% completed; 60%, 58%, and 0% of 53.
   - Enemy tiles cleared inside free ruins: our moppers 3624 and splashers 6455; their moppers 11132 and splashers 7802.
5. **Paint towers die and stay dead** (`t125`, `t114`, `t124`).
   - Our starting paint tower died in 31 of 58 losses (10 by r100, median r263; study 10 52 of 75) and 8 of 50 wins. Own mopper-rounds near it in its last 40 rounds: a median 0 (zero in 22 of 31); theirs 20 (zero in none).
   - Killed paint towers never rebuilt: ours 51 of 104 (49%; study 10 40%), theirs 5 of 78 (6%). Killed money towers: 103 of 357 / 11 of 187. They rebuild their killed money ruins as paint or defense towers.
6. **Small maps** (`t122`; short side 25 or less, or 600 or fewer paintable tiles): 12 losses. Towers 3 / 3 at r100 and 5 / 5.5 at r200, robots 5 / 10 and 9.5 / 15; our last paint tower died for good in 7 (median r129) while we held 3039 chips at r200. Jail is lost at r78 and r120, Filter at r129, CastleDefense at r177.
7. **Marks cost paint they don't spend** (`t47`, `t132`). Pattern marks cost us 175 paint per loss in r1-100 (study 10 150) and 217 per loss over the game (342 per win), in all 58 losses (6.5 marks per game in r1-100, 1 in r101-200). Waiting at an unmarked ruin with 10-24 paint is rare (43 turns in all), so the cost is the paint itself. See 2.1.

### How the top teams beat us (`t108`, losses)
- **gone-whalin** (13 losses, median end r372, 3 eliminations). First tower kill on us at r34, the earliest. At r100 moppers 0.5 / 5, chips 1185 / 1640; at r200 moppers 2 / 11. Two of the losses are Jail eliminations by r120.
- **spaark** (12 losses, median end r449, 3 eliminations). Level at r100 (7 / 7 towers); at r200 7 / 10 towers, chips 2420 / 1411; at r300 paint towers 1 / 5 and towers 6 / 13.
- **immutable** (10 losses, no eliminations). We lead at r100 (7.5 / 5.5 towers) and are level at r200 (8 / 8); at r300 splashers 3 / 13 and paint towers 1.5 / 3.5.
- **scienceqiu** (9 losses, 4 eliminations). Behind from r100 (2 / 5 towers); at r300 paint towers 0 / 4. First tower kill on us at r61.
- **lobster-roll** (8 losses). Ahead at r100 (6 / 4); at r200 moppers 3 / 11.5 and chips 2068 / 768; at r300 chips 3866 / 1097.
- **subscribe-to-caterpillow** and **om-nom** (3 losses each). At r300 splashers 3 / 17 and 1 / 11; om-nom's paint towers 0 / 4.

The common signature has moved later: no early collapse in most losses, then by r200-300 two to four paint towers and two to three times our units, with mopper-heavy armies.

## 2. Differences, as codeable rules
Ranked by expected size, weighed by how often the rule fires in local games, since the local tourney is the judge. None of them repeats a study 10 rule already tested (2.1-2.4, 2.6c, 2.6d, 4.5, the dry-flag dials).

### 2.1 Free marks: signal the tower type with `rc.mark`, not `markTowerPattern` (high; new)

**Evidence** (`t47`, `t129`, `t132`, `t102`).
- `markTowerPattern` costs 25 paint (RULES 4.6); `rc.mark` costs nothing, has no cooldown and no limit, reaches r²=2, and marks are invisible to the enemy (RULES 4.5).
- We pay for a pattern mark on every new ruin: 6.5 per loss in r1-100 (in all 58 losses), 1 in r101-200. That is 175 paint per loss in r1-100 (study 10 150, study 9 150) and 217 per loss over the game; 342 per win.
- A pattern costs 120 paint to paint (`t129`, both sides), so the mark adds 21% to each of our towers, at the time paint binds hardest (soldiers only, before the first refills).
- They place no pattern marks at all: 0 against our 425 by r150 in the losses. They place single marks instead, 11.5 per loss by r150 (1488 in all), and remove 3 (225), in 44-45 of the 58 losses. 48 of their 105 first towers had no mark at all (`t102`).
- Local evidence on both halves of the mark:
  - The paint matters: t135 (a lone soldier skips the mark) is now the champion (+14 overall in `champions.csv`; the brief gave +72 early, -6 in 257 fresh games, +33 overall). y276, which skips the mark only before r150, went -38 against t135, so the saving matters late as well as early.
  - The signal matters: never marking (y269) went -84; marking only with 2+ soldiers in view (y272) went -48. Helpers read the type from the marks (`readMarks`), so without marks two soldiers can paint different patterns.
  - Free marks keep the signal for every ruin and save the 25 paint for every ruin, lone or not.

**Code.**
- `Soldier.workRuin` mark block (Soldier.java:221-229). The soldier walks to d2 ≤ 2 and calls `markTowerPattern(wantType(), r)` (226), which needs 25 paint. With 10-24 paint it can't mark, and the turn ends at 228.
- `readMarks` (Soldier.java:165-185) already decodes partial marks. It counts mismatches of the visible marked tiles against the paint, money and defense patterns, and ties go paint, then money, then defense. The paint and money patterns differ on all 16 outer-ring tiles (|dx| = 2 or |dy| = 2) and agree on the inner ring, so **one outer-ring mark decodes the type**.
- `readMarks` runs at 219 at the start of every `workRuin` turn while the type is unknown, before the soldier moves. A soldier that sees no mark there walks to d2 ≤ 2 and marks its own `wantType()` at 226 in the same turn, without looking again. From d2 ≤ 2, every tile of the 5x5 is within its vision (r²=20).
- Nothing else reads marks (`getMark` appears only at Soldier.java:173), and SRPs don't use marks.

**Rule.**
1. In the block at 224-227, after reaching d2 ≤ 2: `ruinType = readMarks(r)` again (the whole 5x5 is in sight now). If that is still null, set `ruinType = wantType()` and mark it.
2. Marking: for each outer-ring offset (dx, dy) of the 5x5 whose tile `l` is within r²=2 of the soldier, `if (rc.canMark(l) && rc.senseMapInfo(l).getMark() == PaintType.EMPTY) rc.mark(l, bit(patternOf(ruinType), dx, dy))`. That is 3 tiles from a side-adjacent spot and 5 from a diagonal one. Keep `markTowerPattern`'s other test, that the 5x5 fits on the map (`rc.onTheMap(r.translate(-2, -2)) && rc.onTheMap(r.translate(2, 2))`), and set `ruinType` only then.
3. Every later `workRuin` turn, top up the outer-ring tiles in reach the same way (at most 5 `senseMapInfo` calls), so a helper arriving from any side finds a mark within sight.
4. `readMarks` needs no change.

**Expected size.** Small to medium, and it fires in every game, on every new ruin: about 9 marks per loss and 14 per win (`t132`).
- It saves 25 paint per tower: 175-200 paint per game in r1-150 (1.5 patterns, or one soldier's tank) and 50-150 later.
- A soldier with 10-24 paint now starts the pattern instead of waiting.
- t135 gained from saving the paint on lone soldiers only, and paid for the lost signal on their ruins. This keeps the signal and saves the paint for paired soldiers too, so it should do at least as well. The risk is a helper that sees no mark from where it stands; rule 1's re-read covers that once it is adjacent.

**Prior attempts.** t135 (champion), y269 never marking (-84), y271 marking less (flat, -4 vs t135), y272 marking only with 2+ other soldiers in view (-48), y276 skipping only before r150 (-38 vs t135). No candidate has used `rc.mark`.

**Candidates.** (a) rules 1-4 on t135, replacing its lines 226-230. That is the same code as rules 1-4 on t122, because the lone-soldier test has nothing left to decide once marks are free. (b) (a) without rule 3 (one set of marks on arrival only), to check that the top-up marks matter.

### 2.2 Siege HP discipline: stop hitting a tower two tower turns before death (medium-high; new)

**Evidence** (`t134`, `t135`, `t133`).
- A siege episode is one soldier's run of hits on one enemy tower, with gaps of 5 rounds or less. It ends **killed** (the tower dies), **died** (the soldier dies within 3 rounds of its last hit and the tower stands) or **left**. It is **lone** if no other soldier of the side hits that tower within 3 rounds of its hits. Losses, us / them:

  | | r1-100 | r101-200 | r201-400 |
  |---|---|---|---|
  | episodes | 366 / 263 | 356 / 321 | 537 / 698 |
  | lone share | 47% / 40% | 62% / 53% | 57% / 43% |
  | lone: died | **56% / 35%** | **44% / 27%** | **47% / 26%** |
  | lone: killed | 12% / 17% | 13% / 22% | 15% / 32% |
  | lone: left | 32% / 48% | 43% / 51% | 38% / 42% |
  | with company: died | 16% / 15% | 24% / 11% | 29% / 13% |
  | with company: killed | 66% / 63% | 43% / 67% | 42% / 58% |
  | soldier HP at the last hit: left | 110 / **60** | 130 / **70** | 140 / 130 |
  | soldier HP at the last hit: died | 10 / 10 | 40 / 30 | 40 / 30 |
  | soldiers dead per tower killed by soldiers | **1.68 / 1.03** | **2.22 / 0.73** | **2.29 / 0.64** |

  In our wins, lone episodes die 57% / 31% / 39% (theirs 36% / 30% / 30%), and we lose 1.55 / 1.10 / 1.31 soldiers per kill.
- **Their soldiers walk away at 60-70 HP in r1-200; ours keep hitting until they die.** Ours leave at 110-140 HP, when the code moves them on (paint under 30, a ruin, another tower). Both sides' dying soldiers make their last hit at 10-40 HP.
- **It is tower fire, not paint.**
  - Of our died episodes, 121 / 120 / 190 end with the soldier shot dead by a tower and 7 / 9 / 21 with it starved.
  - Our dying soldiers still hold 59 / 56 / 65 paint at their last hit (theirs 36 / 35 / 29). Only 5 / 20 / 27 of our episodes end at 5 paint or less.
  - 99% (r1-100) and 89% (r101-200) of the tower damage our robots take comes in a round they hit a tower (`t133`).
- **Their towers are guarded, ours are not.** An enemy mopper drains our soldier during 49% / 58% / 72% of our episodes; ours drain theirs in 3% / 27% / 30%. Below half paint a soldier's cooldowns grow (RULES 3), which breaks the step-in / step-out rhythm.
- **Lone sieges soften towers, so they still matter.** Killed episodes start on a tower at a median 800 / 400 / 500 HP (both sides alike), against 1000 for the others. A full L1 tower takes 20 soldier hits (RULES 1).
- **Defense towers.** 12% (r101-200) and 20% (r201-400) of our episodes hit one; none of theirs do, since we build none. A defense tower has 2000 HP, reaches r² 16 and deals 40 + 20 a turn (RULES 1). Siege's one-tile step-out (to r² > 9) leaves the soldier inside that range.

**Code.**
- t122 never reads a health value: there is no `getHealth` call and no `.health` test outside `Tower.attack`.
- The free hit (Soldier.java:18-22) fires for any soldier within r² 9 of an enemy tower with 5+ paint. Its comment says "when healthy enough to trade", but nothing tests health.
- `siege()` (Soldier.java:41-58) runs whenever the soldier has 30+ paint (`SIEGE_PAINT`) and a known enemy tower within r² 144 (`SIEGE_R2`). It steps into r² 9, hits, and steps one tile away (51-55). Nothing in it looks at HP. It stops only when paint falls under 30, the tower is gone or beyond r² 144, a ruin turns up (`workRuin` runs first) or `deny()` fires.

**Rule.**
1. Add `static final int SIEGE_HP = 70;` beside `SIEGE_PAINT` (Soldier.java:41). 70 HP is two L1 tower turns of 20 + 10.
2. Add a helper: `towerHp(t)` = `rc.senseRobotAtLocation(t).health` when `t` is in sight, else `Integer.MAX_VALUE` (an unseen tower counts as healthy, so a low-HP soldier does not walk toward it).
3. Free hit (18-22): also require `rc.getHealth() > SIEGE_HP || towerHp(Unit.enemyTower) <= 50` (the hit kills).
4. `siege()`: after the existing entry test, if `rc.getHealth() <= SIEGE_HP && towerHp(t) > 100` (not two hits from dead), do not step in. If the soldier is inside the tower's range (r² ≤ 9, or ≤ 16 for a defense tower) and can move, step away with the loop at 51-55. Then `return false`, so the turn goes on to `srpTurn` / `refill` / explore. A robot's HP never comes back (RULES lists no healing, only tower fire and the 0-paint drain, 2.1 and 4.1), so from then on the soldier builds and paints.
5. (b) Defense towers: `siege()` and the free hit skip a `DEFENSE_TOWER` target unless `towerHp ≤ 250` or another of our soldiers is within r² 16 of it. This is replica-only: no local bot builds defense towers, so it cannot show up in the local tourney.
6. (c) A soldier at `SIEGE_HP` or less adds a high cost in `Nav.tileCost` (Nav.java:18) to tiles within r² 9 of `Unit.enemyTower`, so it stops walking through tower range on its way to ruins.

**Expected size.** Medium, and it fires in most games: 6.3 siege episodes per loss in r1-100 and 6.1 in r101-200.
- If our lone episodes died at their rate, we would keep 36 + 37 + 64 = 137 soldiers over the 58 losses: about 1.3 per game by r200 and 2.4 by r400. Each is 250 chips, 200 paint (the binding resource) and the 56-65 paint it carries when it dies. By r200 we have a median 6 soldiers alive.
- **It costs little damage.** Killed episodes end at a median 140-190 HP, so the exit rarely stops a kill, and the two-hit exception covers the rest. A soldier that leaves at 70 HP has already dealt about three quarters of the hits it would have dealt before dying.
- **A 70-HP soldier is still a full worker.** Only towers do HP damage (RULES 4.1), so it paints and builds like a fresh one.

**Prior attempts.**
- No candidate has used HP.
- Every siege entry rule lost:
  - only with a partner: sw23 -83, t10 -41, t31 -76;
  - from 100 paint: y53 -34, t34 -34;
  - range: y96 -43, y99 -36, y209 -23;
  - from 15 paint at r² 225: y39 -10;
  - y219 (50 paint) was retired unplayed.
- This rule keeps every siege start, lone ones included, and ends only the last two tower turns of each soldier's siege life. The softening that lone sieges do stays.

**Candidates.** (a) rules 1-4 with `SIEGE_HP` 70; (b) `SIEGE_HP` 100; (c) (a) + 5 + 6.

### 2.3 `G.forgetTower` drops the dry flags (low; bug, study 10 2.5, never tested alone)

**Evidence.** Code reading only.
- Every game churns or loses towers: our towers killed in r101-250 average 2.7 per loss (`t68`), and churns 2 per loss in r101-200 (`t128`). Each such tower is forgotten by the robots that find it gone.
- Robots queue at a paint tower that ended its turn under 50 paint 0.87 times per 100 robot-turns in r101-200 of the losses, against their 0.22 (`t130`). How much of that the bug causes cannot be told from a replay.

**Code.**
- `G.forgetTower` (G.java:137-141) moves the last tower into slot i (`towerLoc`, `towerKind`) but not `Unit.towerDry[i]`. The moved tower inherits the forgotten tower's dry flag and loses its own.
- `G.noteTower` (G.java:132-135) appends a new tower without clearing `towerDry[nTowers]`, so the new tower can inherit a stale flag from that slot.
- Callers: `Unit.refill` (Unit.java:39) and `Tower.churn` (Tower.java:38, the tower's own memory).

**Rule.**
- In `forgetTower`, after the swap: `Unit.towerDry[i] = Unit.towerDry[nTowers]; Unit.towerDry[nTowers] = 0;`.
- In `noteTower`, set `Unit.towerDry[nTowers] = 0` before appending.

**Expected size.** Small. A wrong flag hides a full tower, or sends robots to a dry one, for 10 rounds (paint) or 40 (money). It is a bug fix and a free rider, not a lever.

**Prior attempts.** Only inside t132 (-140 early), whose loss the pool note puts on the wrong-colour repaint (`research/tourney/pool.txt`).

**Candidates.** Add it to whichever of 2.1 / 2.2 wins. Alone it is too small to measure in a few hundred games.

### 2.4 Lower priority (measured, but weak, or tried before)
- **Paint-tower outflow** (`t130`, `t136`, `t120`).
  - Robots take 4.9 paint per paint-tower turn in r101-200 of the losses (t111 4.5, t118 4.0, them 2.7), and our paint towers spawn 6.7 a turn (them 11.1).
  - Top-ups are not the cause. Robots already half full take 17.5% of that paint (them 17.3%).
  - Our splashers take 26% of it in r101-200 and 51% in r201-400 (theirs 11% / 33%).
  - Our wins show the same ratio (5.4 against their 2.7), so this is our style more than the cause of losing.
  - Paint reserves lost before: sw04 -21, sw07 -93, sw08 -34. The dry-flag dials were flat.
- **Drained soldiers starve** (`t123`, r101+ of the losses).
  - 910 of our soldiers starved (0.69 per 100 soldier-turns; theirs 694, 0.28). 70% had been drained by enemy moppers in their last 15 rounds (theirs 33%). An own mopper was within d² 8 in their last 5 turns for 17% (theirs 46%).
  - A soldier under 100 paint with an enemy mopper within r² 8 could head for its refill tower.
  - No prior. The risk is handing contested ruins to their moppers. Our wins show the same 69% drained share.
- **Ground cover** (`t109`).
  - Our soldiers spend 15.6% of their turns in r101-200 on cover paint (theirs 5.9%): about 530 paint per loss against 210.
  - Our wins show the same (15.2% / 6.7%). Coverage is how 46 of the 58 losses ended, so cutting cover is not a rule by itself.
  - No test since study 3 tactic 2 (no cover before r80).
- **Clean free ruins in our half** (`t64`, `t62`, `t72`).
  - At r100 of the losses there are 139. Only 44 had been within d² 20 of one of our robots. Our first soldier comes within d² 20 a median 48 rounds later (theirs 36, on their side). We build 70 of them and they build 45; in our wins we build 135 of 157.
  - Priors: remembered clean ruins (t121 / t123; t127 flat, -3), explore targets (y215 -122, t101 -20, y217 -16).
- **Churn** (`t42`).
  - Drained L1 money towers wait 13608 tower-rounds in the losses: 5763 blocked by an enemy in view and 5088 by no ally adjacent.
  - Priors: t75 (churn ignores enemy moppers) -21; chip dials y57 +8, y61 -26, y103 -45, y104 -54, y186 -10, sw30 +2, sw32 -19.
- **Mopper mix and guards.** They have 4.3x our mopper-turns, and their moppers drain most of our sieges (2.2). Priors: t129 -41, t130 flat, t71 -317, t76 -295, t83 -54, y240 flat.
- **SRPs.** Their first comes at r76.5 against our r133, with 11400 chips in r1-100 against our 0 (`t129`, `t128`). Priors: y213 -3, y214 -85, t104 -62, sw09 -103.
- **Defense towers.** Their first comes at r155, in 29 of 58 losses. Prior: t103 -72.
- **A second paint tower.** We have two paint towers standing at once in 22 of 58 losses and 44 of 50 wins (`t61`), the strongest win/loss split in the study.
  - Type rules were tried: t124 -28, t128 -13, t133 -22.
  - Upgrade dials too: y218 -22, t136 +2; t138 and y277 are in the pool now.

## 3. What changed since study 10

| measure | study 10 (t111 + t118) | now (t122) |
|---|---|---|
| record | 100-75 (57%) | 50-58 (46%); level with t111 / t118 on shared pairings (`t127`) |
| against the eight top teams | 64-56 | 43-50 |
| W-L on maps of 501-900 paintable tiles | 21-20 | 7-17 |
| losses behind / ahead at r100 | 32 / 30 of 75 | 16 / 29 of 58 |
| eliminations | 18 of 75 | 12 of 58 |
| last paint tower dead for good | 33 of 75 (r192) | 21 of 58 (r198) |
| our starting paint tower died | 52 of 75 losses | 31 of 58 |
| killed paint towers never rebuilt | 40% | 49% |
| loss rounds with every tower under 200 paint, us / them | 56% / 28% | 59% / 22% |
| tower lead becomes permanent | r197 | r162.5 |
| median end of a loss | r392 | r410.5 |
| chips at r200, us / them | 2455 / 1096 | 1994 / 1292 |
| towers at r300 | 6 / 10 | 5 / 10 |
| robots at r300 | 12 / 32 | 9 / 26.5 |
| loss rounds r101-400 ending at 3000+ chips | 28% | 41% |
| paint withdrawn from our paint towers per loss, r101-200 | 270 | 520 |
| pattern-mark paint per loss, r1-100 | 150 | 175 |

**What the dry-flag change did** (`t130`, losses, paint towers (PT); t122, then t111 / t118, then them):

| | r101-200 | r201-400 |
|---|---|---|
| PT turns ending under 50 paint | 19.4% (12.6 / 17.8); them 11.1% | 22.4% (18.2 / 24.9); them 14.3% |
| paint withdrawn per PT turn | 4.9 (4.5 / 4.0); them 2.7 | 6.3 (6.1 / 4.7); them 4.8 |
| spawn paint per PT turn | 6.7 (6.1 / 8.2); them 11.1 | 11.5 (12.2 / 10.2); them 20.7 |
| robot-turns queued at an empty PT, per 100 | 0.87 (0.50 / 0.68); them 0.22 | 1.56 (0.90 / 0.81); them 0.45 |
| robot's paint after a PT withdrawal (share of capacity) | 86% (99 / 99); them 99.5% | 88% (99 / 98); them 99.3% |

- It did what it was built for: robots come back to paint towers sooner and draw more.
- But the towers sit empty more often, robots queue at empty towers about twice as often and leave them partly filled, and spawns did not rise. **It moved paint from spawns to refills without adding any.**
- What differs is the number of paint towers and their income (their spawn paint per PT turn doubles in r201-400), not the routing. That fits the flat results of y260, y263 and y267.

**New in this study** (not measured by studies 9-10):
- the siege-episode exchange, lone and accompanied (2.2);
- the mark gap: 0 pattern marks for them, 11.5 single marks (2.1);
- what each side spends chips on (`t128`) and the opening build clock (`t129`);
- the paired version comparison (`t127`);
- the split of paint-tower withdrawals into refills and top-ups (`t136`).

## 4. Broken in our bot (t122)
1. **The free hit ignores HP** (Soldier.java:18-22), despite its comment. Nothing in the bot reads its own health → 2.2.
2. **Siege steps out to r² > 9 only** (Soldier.java:51-55), which is still inside a defense tower's r² 16 → 2.2 (b).
3. **`G.forgetTower` / `G.noteTower` mishandle `Unit.towerDry`** (G.java:132-141) → 2.3.
4. **Money towers stall at the splasher slot** (Tower.java:69-76).
   - A money tower holds 500 paint and makes none. It spawns two units (S S before r80, S M after), then waits for good for 300 paint for the X slot. 0 of 306 money towers that lived 100+ rounds spawned a third unit (`t54`).
   - **Leave it.** The fixes lost: t71 -317, t76 -295, t83 -54, y240 flat. Its leftover paint feeds refills (972 per loss in r101-200).
5. **Tower.java:66** says "S X X M", but `built % 6` then `% 4` gives S X X M S X. `enemyNear` (Tower.java:60-61) is computed and never used.
6. **`Unit.rebuild`** (Unit.java:78-89) completes money towers only. The paint rebuilds were tried (t128 -13, t133 -22).
7. **`workRuin` stands still when the refill finds no tower** (Soldier.java:214-218): it returns true at under 10 paint. t134 (explore instead) was flat.
8. **`pickRuin` sees only visible ruins** (Soldier.java:115). Splashers never add to `G.ruinList` (G.java:113), which SRP placement reads (Soldier.java:348).
9. **`Sym` is computed but only shown in the indicator** (Tower.java:16).
10. **Possible, not checked against the maps:** if a ruin's 5x5 does not fit on the map, `canMarkTowerPattern` fails at 226 and the soldier waits up to the 150-round timeout (213). With free marks (2.1), test the fit explicitly.

## 5. Suggested test order
1. **2.1 (a), free marks, on t135.** It fires on every ruin of every game. Expect a small gain. If it is level, try (b).
2. **2.2 (a), the siege HP exit at 70.** It fires in most games. If it is level, try (b) at 100. Keep (c) for later: its defense-tower part shows only against teams that build defense towers, and no local bot does.
3. **2.1 + 2.2 together** once each is level or better on its own.
4. **2.3, the dry-flag fix,** as a free rider on the winner of 1-3.
5. The 2.4 ideas only with a new argument. Most have lost before in some form.

## Summary: the top three
1. **Free marks (2.1, high).**
   - Pattern marks cost us 175 paint per loss in r1-100 (217 per loss over the game, 342 per win); the top teams place no pattern marks at all.
   - `rc.mark` is free and team-private, and one outer-ring mark tells paint from money. It keeps the helper signal that y269 (-84) and y272 (-48) showed we need, and the paint that t135 saved.
   - Code: Soldier.java:221-229 (t135: 221-233).
2. **Siege HP exit (2.2, medium-high).**
   - Our lone siege episodes end with the soldier dead 56% / 44% / 47% of the time (theirs 35% / 27% / 26%). We lose 1.68 / 2.22 / 2.29 soldiers per tower killed (they 1.03 / 0.73 / 0.64).
   - Their soldiers walk away at 60-70 HP, ours hit until they die, and the killer is tower fire (121 / 120 / 190 shot against 7 / 9 / 21 starved).
   - Code: Soldier.java:18-22 and 41-58. No prior has used HP.
3. **Dry-flag bookkeeping (2.3, low).** `forgetTower` / `noteTower` (G.java:132-141) mishandle `Unit.towerDry`. It is a free-rider bug fix.

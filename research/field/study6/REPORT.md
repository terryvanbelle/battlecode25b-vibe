# Field study 6 (2026-11-26): t47-y155 against the strong teams since study 5

Replays only (no competitor code or write-ups). 20 matches (60 games) against the strong teams after study 5's set, ids 2323-2599: 2323 the-kragle W3-0, 2344 varunvejalla L0-3, 2364 angtn L1-2, 2365 ryanaspen W2-1 (unranked), 2366 geesegeesego L1-2, 2367 the-kragle W3-0 (unranked), 2397 ryanaspen W2-1, 2418 the-kragle W2-1, 2439 botpocalypse W2-1, 2446 angtn W3-0, 2469 geesegeesego W2-1, 2471 varunvejalla L0-3, 2472 podemice W2-1 (unranked), 2476 the-kragle W2-1, 2485 podemice W2-1, 2508 varunvejalla L0-3, 2529 ryanaspen W2-1, 2565 ryanaspen W2-1, 2567 the-kragle L1-2, 2599 podemice W2-1. That gives **26 lost games** and 34 won games (the control). 2390 (bc25-vibe-orig) and 2470 (slifland), both 3-0 wins, are dumped but not used. Our package in each game comes from the replay header: t47 (2323-2446, 30 games), t58 (2469-2529, 21), t61 (2565, 2567), y155 (2599). Only 9 games ran the t61/y155 tower rule.

`lib.py` is study 5's loader, adapted. `games('lost'|'won'|'all')` takes the env filters S6VER and S6TEAMS. Scripts t0-t37 are study 5's, rerun. Scripts t40-t54 are new. Each `tNN_*.py` writes `tNN.txt`; run them with `./run.sh tNN_x.py`. Dumps live in the session scratchpad (`study6/dump/mM`). Rebuild them with `java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`.

(The study agent wrote the scripts and outputs; its report was saved here by the main session.)

## 1. How the games were lost
- 22 of 26 games ended by MAJORITY_PAINTED and 4 by ALL_UNITS_DESTROYED (CastleDefense three times, FourCorners). The median loss came at **r370** (study 5: r480). By version: t47 r362 (11 games), t58 r454 (11), t61/y155 r309 (4).
- Map size (`t40`): with min side <= 25 we lost **11 of 13**; 26-35, 11 of 24; > 35, 4 of 23. With <= 500 paintable tiles we lost 7 of 9.
- Opponents: varunvejalla won 9 of 9; the other six teams won 17 of 51.
- Towers at r100, ours minus theirs: >= +3 gave 16 W / 2 L; +1..+2 gave 12 / 10; 0 gave 4 / 3; <= -1 gave 2 / 11.

Median timeline of the 26 losses (`t0_medians`; us / them; S / X / M = soldiers / splashers / moppers):

| round | cov % | towers | paint towers | chips | paint | units | S / X / M |
|---|---|---|---|---|---|---|---|
| r50 | 17.3 / 21.0 | 4 / 4 | 1 / 1 | 915 / 915 | 1466 / 1808 | 7 / 6 | 7/0/0 vs 5/0/1 |
| r100 | 25.6 / 31.1 | 4 / 4 | 1 / 1 | 1365 / 885 | 1446 / 1769 | 8 / 10 | 7/0/1 vs 6/0/3 |
| r150 (25) | 30.3 / 33.5 | 5 / 5 | 1 / 1 | **2390 / 940** | 1583 / 1937 | **7 / 12** | 6/0/2 vs 7/0/5 |
| r200 (23) | 34.2 / 37.8 | 5 / 6 | 1 / 1 | 1750 / 820 | 1983 / 2431 | 9 / 15 | 6/1/3 vs 8/0/7 |
| r300 (19) | 36.5 / 49.9 | 5 / 8 | 1 / 1 | 2160 / 1320 | 1736 / 3097 | **9 / 24** | 4/2/3 vs 9/4/11 |
| r400 (10) | 41.2 / 50.0 | 7 / 7.5 | 1 / 1.5 | 3584 / 1150 | 1913 / 3373 | 12.5 / 19.5 | 4/2/4.5 vs 6/2.5/11.5 |

- In our 34 wins (`t37`) we lead in towers early: 6 / 3 at r100 and 8 / 4 at r150. We also lead in units: 10 / 9, 15.5 / 12 and 20 / 13 at r100, r150 and r200.
- In the losses the gap opens in units, not coverage. From r100 they field more robots while we bank chips. Robots alive per round (`t45`, us / them):

| S / M / X alive | r51-100 | r101-200 | r201-300 |
|---|---|---|---|
| lost | 7.2/0.4/0 vs 5.7/2.0/0 | 7.0/1.7/0.7 vs 7.7/4.7/0 | 5.4/3.2/1.4 vs 8.7/8.9/2.0 |
| won | 7.5/0.3/0 vs 5.0/2.3/0 | 10.5/3.5/1.1 vs 5.1/4.6/0.9 | 13.2/7.9/3.6 vs 6.7/6.4/2.3 |

  Their mix is about the same whether they win or lose. What changes is how many soldiers we keep alive.
- Our robots die about twice as fast (`t41`). Deaths per 100 robot-turns are 0.88-0.89 for every type against their 0.42-0.54 (in our wins: 0.33-0.62). 54% of our dead soldiers had been drained by an enemy mopper in their last 10 rounds (theirs: 40%).
- Tower kills are even (`t46`). In the losses they killed 166 of our towers and we killed 185 of theirs. Both sides kill with about 2 soldiers in a 9-15 round siege; splashers hardly take part. The gap is what happens next: they rebuild and we don't (2.1).
- Small maps (`t43`): contact comes at r3-r94 (median about r24). All 4 ALL_UNITS_DESTROYED losses began with our only paint tower dying (r25-r179) and never coming back. In CastleDefense (2344/2471, the same game twice) we held 2240-4900 chips while our paint ran out.

Economy by phase (`t30`, `t47`; medians per game, us / them):

| | r1-100 | r101-200 | r201-300 |
|---|---|---|---|
| paint from paint towers | 1000 / 1000 | 1033 / 1000 | 1470 / 1512 |
| paint from new towers (500 each, incl. churn) | 1750 / 2500 | 2500 / 2500 | 1500 / 2500 |
| paint drained from robots by enemy moppers | 58 / 0 | **310 / 210** | **685 / 435** |
| paint still held by robots when they died | 140 / 20 | 177 / 56 | 155 / 47 |
| paint put into new robots | 2000 / 2000 | **1300 / 2100** | **1800 / 3100** |
| mean chips held | 1267 / 940 | **2306 / 943** | 2367 / 1380 |
| tower-turns paint-blocked\* | 39.7% / 11.9% | **78.8% / 16.2%** | **90.5% / 44.6%** |
| mopper spawns (corrected, see 3) | 1 / 3 | 2 / 6 | 3 / 8 |

\* The tower holds < 200 paint while the team holds >= 1250 chips (study 5's definition).

Both sides bring in the same paint. They turn it into robots. We lose ours to drains, to robots that die full, and to towers waiting for a splasher they can't pay for (2.3).

## 2. Differences, as codeable rules (none of them is about the tower mix or splasher exploration)

### 2.1 Take back our own ruins: rebuild killed towers, clean contested ruins (very high; partly a bug)
- After a tower is killed (`t51`, lost games), they rebuild **177 of 185 (96%)**, median 16 rounds. We rebuild **78 of 166 (47%)**; they take 33 of ours (median 78 rounds later) and 55 never come back. Our wins show the mirror image: we rebuild 65 of 82 (79%), they rebuild 100 of 216 (46%), and we take 29 of theirs.
- Paint towers: they rebuild 41 of 44 (33 as paint), median 12 rounds. We rebuild 5 of 19 (2 as paint), median 61.
- The cause shows ten rounds after the kill (`t52`). Our ruins not rebuilt within 50 rounds had a median of **4 enemy tiles** in the 5x5 (only 10 of 71 were clean). The ones we did rebuild were clean in 61 of 64 cases. At those deaths we held a median of 2130 chips, and our soldiers still passed nearby (median 14 soldier-turns within 4 tiles).
- New ruins show the same thing. Of ruins with enemy paint at our first mark, we finish 7 of 45 and they finish 38 of 54 (`t13`). Our 65 failed ruins peaked at a median of **19 of 24 correct tiles** with 3 enemy tiles and 1660 chips, and we mopped inside them a median of 0 times (`t11`). When a ruin they finished had enemy paint during the attempt, they mopped inside its 5x5 a median of 14 times (ours: 5).
- Their moppers spend 32% of their turns within 3 tiles of an open ruin; ours spend 17-19%. This holds in won and lost games alike (`t44`). Podemice and ryanaspen mop their own ruins 89-419 times per game (`t12`).
- Code, all in y155:
  - `Soldier.pickRuin` drops a ruin for 50 rounds if any visible tile in its 5x5 is enemy paint: `if (contested(r)) { markBad(r, 50); continue; }`.
  - `Soldier.workRuin` drops it after 25 blocked rounds (`markBad(r, 100)`).
  - `Mopper.target` puts enemy robots first. Enemy paint near a ruin counts only 6 d2 nearer.
  - `Unit.rebuild` tries only `LEVEL_ONE_MONEY_TOWER`. A killed paint tower with its pattern intact is never re-completed by the robot standing beside it.
- Rule:
  - (a) `Unit.rebuild` tries the type the intact pattern spells: paint, money, or defense.
  - (b) A ruin with <= 4 enemy tiles stays pickable. The soldier paints the other tiles and waits next to it.
  - (c) `Mopper.target` treats enemy tiles inside an unbuilt ruin's 5x5 like a defended enemy robot (-40). `Mopper.act` mops those tiles before open ground.
  - (d) A soldier that sees one of our towers die takes that ruin first.

### 2.2 Deny their ruins (high; new)
- Our marked ruins that they painted into (`t53`, lost games): we finished **7 of 48 (15%)**, only 1 within 50 rounds. Clean ones: 116 of 140 (83%). In our wins: 12 of 30 against 398 of 456.
- They did this to 48 of our 188 marked ruins, in 17 of 26 losses, with soldiers and splashers (`t12`):
  - the-kragle: Mirage 310 paints, FourCorners 147, CastleDefense 69, Brat 67
  - geesegeesego: Portal 195, Racetrack 90
  - varunvejalla: all 6 games, 2-124 paints
  - angtn: DefaultSmall 52

  We did it to 6 of their 159, in 3 games.
- Two styles: the-kragle, varunvejalla, geesegeesego and angtn deny. Podemice and ryanaspen clean (2.1) and open with moppers.
- They rebuild 96% of the towers we kill (`t51`). 54% of those still had an intact pattern at death and came back in a median of 11 rounds. Of the 49 that were not back within 50 rounds, 28 had none of our paint in the 5x5 (`t52`). Each rebuild gives them a tower back plus 500 paint.
- Rule:
  - A soldier with no ruin of its own paints empty tiles in the 5x5 of a ruin the enemy has marked, or of an enemy tower it just killed. 2-3 tiles are enough, at 5 paint each.
  - Soldiers can't paint over enemy paint. An intact dead pattern needs a splasher (it overwrites within d2 2 of its centre) or a mopper (mop one pattern tile, then a soldier paints it).
- Code: `Soldier.turn` (a new step between `siege()` and `srpTurn()`; `siege()` knows when its target is gone), the splasher's target grid in `Splasher.java` (next to the enemy-tower weight at line 45), and `Mopper.act`.

### 2.3 Spawn what the tower can pay for; moppers before r80 (high; a bug)
- Our money towers never spawn a third unit. Of 378 money towers that lived >= 100 rounds, none spawned more than 2 units, and none spawned a splasher (`t54`). Their built money towers spawned 3-5 units in 31 of 141 cases, mostly moppers (136 M, 125 S, 27 X).
- Cause:
  - `Tower.choose` cycles a money tower through S M X M S M by its own spawn count. Before r80 it spawns only soldiers, but the count still advances.
  - `Tower.build` returns when the tower holds less paint than the unit costs: `if (G.paint < t.paintCost) return;`.
  - A money tower gets 500 paint when built and has no paint income. After S (200) and M (100) it has at most 200 left, so the splasher (300) never comes. Our starting money tower spawns exactly 2 soldiers per game.
- From r40, our towers spawn on 1.4% of tower-turns against their 2.5%, and they are paint-blocked on 77% (theirs 44%; ours in our wins 49%) (`t49`). Of the stalled tower-turns, 80% wait for a splasher, and in 19% a mopper was affordable (`t48`).
- Our first mopper comes at r81 (`if (r < 80) return UnitType.SOLDIER;`). Theirs comes at r50 in our losses and r30 in our wins. On small maps their first mopper came at r2-r3 in 3 of 11 losses (podemice twice, ryanaspen) and at r22 in a fourth.
- Enemy moppers drain 310 / 685 paint from our robots in r101-200 / r201-300 (we drain 210 / 435). They mop 76.5 / 119 of our tiles (we mop 23.5 / 33 of theirs) (`t47`, `t31`).
- Rule:
  - When the tower's paint is below the chosen unit's cost but >= 100, and chips >= 300 + the reserve, build a mopper. If a splasher was due and the tower holds >= 200 paint, build a soldier instead.
  - Money towers cycle S M M.
  - Optional (lower confidence, since their mopper count is the same in our wins): one mopper among each tower's first 3 units before r80, from r1 on maps with min side <= 25.

### 2.4 Churn under contact (medium)
- Churns (`t42`): in the losses, 188 by us and 234 by them (varunvejalla Leaf 70, Restart 37; the-kragle Mirage 28). In the wins, 362 by us and 68 by them. They rebuild a churned tower in a median of 2 rounds; we take 1.
- In the losses, a drained L1 money tower with >= 2000 chips waited 6688 tower-rounds. 2077 of those were blocked only by a visible enemy (`if (G.enemies.length > 0) return false;` in `Tower.churn`). 2681 lacked an adjacent ally. In the wins, 1137 tower-rounds were blocked by a visible enemy.
- Rule: `Tower.churn` ignores enemy moppers and enemies beyond d2 20. The pattern is ours, so they can't complete it, and we rebuild in about 1 round. A unit that refills while chips >= 2000 picks a drained L1 money tower (`Unit.refill` already waits 3 rounds beside one).

### 2.5 Soldiers and splashers step away from enemy moppers (medium)
- Our soldiers and splashers die at 0.89 and 0.88 per 100 turns, against their 0.54 and 0.42. 54% of our soldier deaths came within 10 rounds of an enemy mopper drain (theirs 40%).
- Our robots end 13.9% of their turns on enemy paint, theirs 9.6% (`t24`; study 5 had 8.8% / 11.4%).
- No code looks at enemy moppers: `Nav` weighs only paint.
- Rule: a soldier or splasher that is not about to complete a pattern leaves d2 <= 8 of an enemy mopper before it acts.

### 2.6 Lower (weak evidence)
- Mopper swings: theirs hit 1.17 robots per swing (single targets); ours hit 2.15, because `Mopper.act` swings only at >= 2. But our moppers mop robots more often (8.3 against 2.7 per 100 turns). The gap is numbers and position, not the swing rule.
- Tower defence: their moppers guard sieged towers. They mop attackers 1.98 times per siege to our 0.21, with 2 defending moppers to our 0. Yet their towers die in 36% of sieges and ours in 31%. Our attackers die 0.64 per siege, theirs 0.49 (`t14`, `t25`).
- SRPs: median 0 / 0 up to r300 in the losses, 1 / 0.5 at r400. Not a gap. Defense towers: they rebuilt 15 churned money towers as defense towers; we never build one. Not measured further.

## 3. What changed since study 5

| study 5 item | then (us / them) | now (us / them) | status |
|---|---|---|---|
| median loss round | r480 | r370 (t47 r362, t58 r454, t61/y155 r309) | earlier, with more small maps |
| paint-blocked tower-turns, r101-200 / r201-300 | 46.1 / 21.6, 80.1 / 31.6 | 78.8 / 16.2, 90.5 / 44.6 | paint is still the limit |
| splasher idle with full paint (2.3) | 8.6% / 0.1% | t47 9.6%, t58 0.0%, t61/y155 0.0% | fixed by t58 |
| splashes per 100 splasher turns | - | 7.8 / 4.2 in the losses; t47 4.7, t58 6.2, t61/y155 8.8 | ahead |
| paint towers in the losses (2.1) | 1 / 4 at r300 | 1 / 1 at r300; y155-era losses 0.5, never a second | see below |
| money upgrades end churn (2.2) | 8 of 16 games | 12 of 26 losses, 0-4 churns after | open |
| trickle refills (2.4) | 51.6% / 6.6% | 45.4% / 30.9% | open, smaller gap |
| splasher hits on towers (2.5) | 2 / 13 per game | 1.5 / 2.5 | closed against these teams |
| mopper spawns (2.6) | 10 / 13.5, 12.5 / 18, 14 / 36 | 2 / 6, 3 / 8, 3 / 7 | study 5's numbers were wrong |
| turns ending on enemy paint | 8.8% / 11.4% | 13.9% / 9.6% | regressed |

- The y155 paint-tower rule needs 6 towers. In 11 of 26 losses we never stood more than 4 towers at once, and the median is 4-5 towers from r50 to r300. So the losses keep one paint tower, and often lose it. t70's rule (2000+ chips makes the next tower a paint tower) hits exactly this case: the losses hold a median of 2390 chips at r150.
- Counting bug in study 5: `t30` matched `a[6][:2] == 'MO'`, which also matches MONEY_TOWER, because spawn rows include tower builds. Study 5's mopper-spawn row and its rule 2.6 are invalid. Study 6's `t30`, `t10` and `t43` use exact robot names. Study 5's `t25` "mop targets tile vs robot" counted mop-swing rows, two per swing.

## 4. Broken in our bot (y155; t70 differs only in `Soldier.wantType` and the splasher tower weight)
1. Money towers stop after 2 units: the S M X cycle plus no fallback in `Tower.build` (2.3). This holds for 378 of 378 long-lived money towers.
2. `Unit.rebuild` completes only money towers. A killed paint tower's intact pattern is never re-completed (2.1).
3. `Soldier.pickRuin` / `workRuin` drop a ruin over a single enemy tile, and `Mopper.target` barely favours ruin paint. Our failed ruins sat at 19/24 correct with 3 enemy tiles and were mopped 0 times (2.1).
4. `Tower.churn` is blocked by any visible enemy, even a mopper 6 tiles away (2.4).
5. Still open from study 5: money upgrades end churn (12 of 26 losses; t54 and t55 were not promoted), and trickle refills (45%).
6. `Sym` is computed but unused. No defense towers are ever built (not shown to matter).

## 5. Suggested test order
1. 2.3 first: it is the cheapest change and a bug.
2. Then 2.1, then 2.2.
3. Then 2.4 and 2.5.

Build on t70. Suggested candidates:
- mopper fallback when the tower can't pay, and money towers cycle S M M (2.3)
- each tower's 3rd unit before r80 is a mopper (2.3, optional)
- `Unit.rebuild` for any type, soldiers keep ruins with <= 4 enemy tiles, and moppers clean ruin tiles (2.1)
- soldiers deny enemy-marked and freshly killed ruins (2.2)
- churn ignores enemy moppers and enemies beyond d2 20 (2.4)
- soldiers and splashers step away from enemy moppers (2.5)

Test on small maps too (CastleDefense, DefaultSmall, FourCorners, Justice, Filter, Barcode): we lost 11 of 13 small-map games, and the local pool may not have enough of them.

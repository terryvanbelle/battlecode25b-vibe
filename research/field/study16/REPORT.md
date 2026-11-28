# Field study 16 (2026-11-28): t188, y358 and y360 on the replica since submission 85

This study used replays only. I read no competitor code and no write-ups, made no `contest.py` or replica call, ran no games, and edited no bots, tools or tests. Dumps were made one java process at a time.

**Versions.** `pkgs.py` read every replay header (`pkgs.txt`).
- **Main set:** the 22 matches after study 15's last (7209), 7239-7459, 66 games.
  - **t188** (submission 85: t186 + `Soldier.colourAt`), 8 matches: 7239-7310;
  - **y358** (submission 86: t188 + `Tune.SOL_REFILL` 100 to 120, so soldiers refill below 120 paint), 14 matches: 7351-7459.
- **New set:** 15 matches fetched while the study ran, 7490-7636, 45 games (`S16SET=y360`).
  - **y360** (submission 87: y358 + `Tune.SOL_PAINT_NEAR` 50 to 40, so soldiers explore-paint from 40 paint), 14 matches;
  - **y374** (submission 88, the champion: y360 + `Tune.SOL_PAINT_HERE` 25 to 10), 1 match (7636).
  - I kept this set apart. It checks the rules (section 2), answers question 2 for y360 (section 3) and has its own record (1.2).

**All code references are to `bots/y360`.** `bots/y374` and `src/vibe` differ from it only at Tune.java:41, so every reference holds for them too. From t188 to y360 only Tune.java:44 and 46 change.

Numbers are for the main set's **66 games, 37 won and 29 lost** (no repeats), unless a line says "new set". Question 2 also uses study 15's 21 t188 games, so t188 has 45 games there.

**Main set:**

| match | ver | opponent | W-L | | match | ver | opponent | W-L |
|---|---|---|---|---|---|---|---|---|
| 7239 | t188 | just-woke-up | 1-2 | | 7394 | y358 | confused | 1-2 |
| 7240 | t188 | spaark | 2-1\* | | 7418 | y358 | spaark | 3-0 |
| 7241 | t188 | om-nom | 1-2 | | 7422 | y358 | just-woke-up | 1-2 |
| 7242 | t188 | immutable | 2-1\* | | 7423 | y358 | scienceqiu | 3-0\* |
| 7265 | t188 | spaark | 3-0 | | 7424 | y358 | gone-whalin | 1-2\* |
| 7268 | t188 | scienceqiu | 3-0 | | 7425 | y358 | om-nom | 3-0 |
| 7294 | t188 | gone-whalin | 1-2 | | 7426 | y358 | lobster-roll | 2-1\* |
| 7310 | t188 | spaark | 1-2 | | 7432 | y358 | om-nom | 1-2 |
| 7351 | y358 | spaark | 0-3 | | 7452 | y358 | old-but-gold | 0-3\* |
| 7358 | y358 | lobster-roll | 3-0 | | 7459 | y358 | om-nom | 2-1 |
| 7365 | y358 | om-nom | 2-1 | | | | | |
| 7373 | y358 | old-but-gold | 1-2 | | | | | |

**New set:**

| match | ver | opponent | W-L | | match | ver | opponent | W-L |
|---|---|---|---|---|---|---|---|---|
| 7490 | y360 | just-woke-up | 1-2 | | 7565 | y360 | om-nom | 0-3 |
| 7491 | y360 | confused | 1-2\* | | 7572 | y360 | immutable | 2-1 |
| 7520 | y360 | old-but-gold | 1-2\* | | 7599 | y360 | om-nom | 1-2 |
| 7527 | y360 | just-woke-up | 1-2 | | 7600 | y360 | spaark | 2-1\* |
| 7528 | y360 | confused | 2-1\* | | 7627 | y360 | lobster-roll | 2-1 |
| 7544 | y360 | om-nom | 1-2 | | 7631 | y360 | spaark | 1-2 |
| 7547 | y360 | confused | 2-1 | | 7636 | y374 | spaark | 1-2 |
| 7564 | y360 | old-but-gold | 1-2\* | | | | | |

\* = unranked.

**Repeats** (`t147_dups`, `t192_newset`): none in either set. The opponents' package names are the same as in study 15 (`pkgs.txt`).

**Main-set record: 37-29 (56%).**
- By version: t188 14-10 (58%), y358 23-19 (55%).
- The seven teams of the brief (TOP7: just-woke-up, spaark, om-nom, confused, old-but-gold, immutable, gone-whalin) 26-28 (48%). The rest (lobster-roll, scienceqiu) 11-1.
- Ranked 27-21, unranked 10-8.
- Per opponent: confused 1-2, gone-whalin 2-4, immutable 2-1, just-woke-up 2-4, lobster-roll 5-1, old-but-gold 1-5, om-nom 9-6, scienceqiu 6-0, spaark 9-6.

**New-set record: 19-26 (42%).**
- By version: y360 18-24 (43%), y374 1-2. TOP7 17-25 (40%); ranked 12-18, unranked 7-8.
- Per opponent: confused 5-4, immutable 2-1, just-woke-up 2-4, lobster-roll 2-1, old-but-gold 2-4, om-nom 2-7, spaark 4-5.
- Whole study: 56-55.

**Ends of the losses.**
- **Main set (29 losses):** 22 on majority paint and 7 eliminations (spaark 4, om-nom 2, confused 1; one at r95). Median end r420. Four ran past r690.
- **New set (26 losses):** 20 on majority paint, 1 on area at r2000 (m7491g2) and 5 eliminations (om-nom 4, at r112, r207, r569 and r583; spaark 1). Median end r418.

**Paired results** (`t151_paired`, on (opponent, map) pairings both versions played):
- y358 against t188: 5 pairings, 3-2 against 2-3 (one flip, om-nom/Portal).
- y360 against y358: 2 pairings, 1-1 each.
- y360 against y328: 5 pairings, 0-5 against 2-3.
- y360 against t140: 12 pairings, 5-7 against 6-6.
- None of these is a measurable difference.

**How to run.**
- `lib.py` is study 15's loader with the study 16 dumps (kept outside the repo) and versions from `pkgs.txt`.
  - Environment: `S16VER`, `S16TEAMS=a,b|top|top5|top7`, `S16RANKED=1`, `S16DUP=1` and `S16WHICH=won` (t0 only). The `S15*` to `S8*` names still work.
  - `S16SET=main|prev|prev2|prev3|all|all2|t188|y360|all3`. `y360` is the new set; `all3` = main + new.
- `./run.sh tNN_x.py [out]` writes `tNN.txt`. The new-set outputs are `tNN_y360.txt`, written by the scratchpad's `runnew.sh`.
- **Rerun from study 15:** t0, t106, t108, t147, t148, t149, t150, t151 (y360 added), t152, t153, t156, t157, t160, t162, t163, t172, t175 and t176.
- **New:**
  - t178_ledger, t179_refill, t180_towers, t181_freeruins, t182_visits;
  - t183_trap, t184_versions (y360 added), t185_l2money, t186_drains, t187_teams;
  - t188_cleanspells, t189_trace, t190_l2churn, t191_srpblock;
  - t192_newset, t193_elims, t194_l2intact and t195_reserve.
- **Copied but not run:** t140, t141, t143, t154, t155, t158, t159, t161, t164 to t171, t173, t174 and t177.

## 1. How the games were lost

### 1.1 Main set (29 losses, 37 wins)
- **We lead to r150, then stall.**
  - At r100 the median loss has 25.6 / 18.6% coverage (us / them) with 5 / 5 towers. At r150 it has 34.5 / 26.2% with 6 / 7.
  - From r150 to r300:

    | r150 to r300 | us | them |
    |---|---|---|
    | coverage | 34.5 to 30.4% | 26.2 to 43.0% |
    | towers | 6 to 6 | 7 to 8.5 |
    | units | 12.5 to 13 | 16 to 28 |
    | chips | 1940 to 3390 | 1312 to 1860 |

  - Wins are the mirror: at r300 55.5 / 19.7% with 13 / 6.5 towers and 6 / 1 paint towers.
- **Paint-bound and chip-rich** (`t106`).
  - In 56.1% of a loss's rounds every tower of ours holds under 200 paint (theirs 29.2%), while we hold a median 2280 chips.
  - 13 losses have rounds with no paint tower (12.5% of the rounds; theirs 4.5%).
  - Our last paint tower died for good in 11 losses (median r276); theirs in 3.
- **One paint tower** (`t180`).
  - The median loss has 1 paint tower of ours from r100 to r400. Theirs has 1 / 1 / 2 / 4 at r100 / r200 / r300 / r400.
  - We reach a second paint tower in 10 of the 29 losses; they do in 22. In wins we reach it in 34 of 37 (median r151).
- **Few new towers in r101-300** (`t180`, `t181`). In r101-200 we build 1.47 new towers a loss and they 2.64; in wins we build 3.57. See 2.4.
- **Starvation, not tower fire, thins our soldiers** (`t184`, `t163`).
  - In y358's TOP7 losses, 4.3 / 3.8 of our soldiers starve a game (r101-200 / r201-300), against 1.6 / 1.1 other deaths.
  - Tower fire kills 7.6 of our robots a loss (6.3 soldiers) and 11.9 of theirs (6.5).
- **Their moppers drain our soldiers** (`t178`, `t186`).
  - At r200 they field 9 moppers to our 4.
  - In r101-300 our soldiers lose 59-67 paint per 100 soldier-rounds to them; theirs lose 20-23.
- **Our robots get stuck at drained money towers** (`t182`, `t183`, `t189`, `t191`). See 2.1 and 2.2.

**Median timeline of the 29 losses** (`t0`, us / them):

| round | n | coverage % | towers | paint towers | money towers | chips | paint | active SRPs | units | soldiers | splashers | moppers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r50 | 29 | 14.9 / 15.4 | 4 / 4 | 1 / 1 | 3 / 3 | 860 / 700 | 1541 / 1791 | 0 / 0 | 8 / 6 | 8 / 5 | 0 / 0 | 0 / 1 |
| r100 | 28 | 25.6 / 18.6 | 5 / 5 | 1 / 1 | 5 / 4 | 1035 / 1000 | 1883 / 2401 | 0 / 0 | 10 / 11.5 | 8.5 / 6 | 0 / 0 | 1 / 4.5 |
| r150 | 28 | 34.5 / 26.2 | 6 / 7 | 1 / 1 | 5 / 5 | 1940 / 1312 | 1802 / 2717 | 0 / 0 | 12.5 / 16 | 7 / 8 | 1 / 1 | 3 / 7 |
| r200 | 28 | 32.2 / 33.1 | 6.5 / 7.5 | 1 / 1 | 5 / 5 | 2170 / 1483 | 1703 / 2806 | 0 / 1 | 12.5 / 19.5 | 6.5 / 8.5 | 2 / 3 | 4 / 9 |
| r300 | 24 | 30.4 / 43.0 | 6 / 8.5 | 1 / 2 | 4.5 / 7 | 3390 / 1860 | 1271 / 4072 | 0 / 1.5 | 13 / 28 | 5 / 9 | 2 / 5.5 | 5 / 11.5 |
| r400 | 16 | 23.9 / 55.2 | 5.5 / 11.5 | 1 / 4 | 4 / 8.5 | 3682 / 1210 | 884 / 6476 | 0 / 3 | 12.5 / 39.5 | 4 / 15 | 3 / 9.5 | 4 / 15 |

**Per opponent** (`t187`; medians, us / them):
- **spaark** (6 losses, 4 eliminations): towers 4.5 / 9.5 at r200; at r300 towers 3 / 13 and paint towers 1 / 5.
- **om-nom** (6 losses, 2 eliminations): paint 1707 / 3314 at r200; at r300 towers 7 / 13 and moppers 5 / 13.
- **old-but-gold** (5 losses): we lead to r300, but they keep 10-11 moppers from r100 on and win late.
- **just-woke-up** (4 losses): at r200 soldiers 2.5 / 9, moppers 4 / 10.
- **gone-whalin** (4 losses): at r300 they lead 49.5 / 37.5% while we hold 4920 chips.

**The paint economy** (`t148`; losses, medians per game [means]):

| | r101-200 us / them | r201-300 us / them |
|---|---|---|
| base paint income | 1000 / 1052 [959 / 1241] | 1068 / 1710 [1493 / 1876] |
| SRP paint income | 0 / 16 [66 / 411] | 4 / 582 [722 / 1340] |
| new towers x 500 | 2250 / 2000 | 2000 / 3000 |
| paint in (base + SRP + new - capped) | 3299 / 3580 | 3595 / 5786 |
| spawn paint | 1950 / 2400 | 1900 / 3300 |
| active SRPs (mean) | 0.2 / 0.7 | 1.0 / 1.8 |
| SRP chip income | 0 / 34 [323 / 1337] | 94 / 1426 [1933 / 3923] |

- **Our "new tower" paint is mostly churns** (`t180`). We churn 2.21 / 2.14 money towers a loss (they 0.71 / 2.68). We build 1.47 / 0.50 genuinely new towers; they build 2.64 / 1.42, plus 0.54 taken from us in r201-300.
- **The soldier ledger** (`t178`, per 100 soldier-rounds, r101-200 / r201-300). The flows match except for the drain:

  | | us | them |
  |---|---|---|
  | withdrawn | 157 / 116 | 132 / 125 |
  | spent | 180 / 124 | 169 / 133 |
  | drained by enemy moppers | 59 / 67 | 20 / 23 |

- **Towers that fall** (`t149`, `t162`, `t153`).
  - Ours are killed 1.03 / 1.62 / 7.52 times a loss (r1-100 / r101-200 / r201+), theirs 1.10 / 1.21 / 3.00.
  - We rebuild 73 / 51 / 42%; they rebuild 94 / 91 / 99%. Their killers take 13 / 45 / 24% of our ruins.
  - At the first hit our tower holds a median 40 paint in r101-200 (theirs 146).
- **SRPs** (`t175`, losses).
  - Completed: 2.69 / 10.66 a game (r101-200 / r201+); theirs 2.48 / 20.76.
  - Broke before the end: 87 / 99%; theirs 60 / 69%.
  - Our own soldiers' tower-pattern work causes 46 / 56% of our SRP breaks.
- **Refill trips** (`t179`, `t182`; soldiers in losses, r101-200 / r201-300).
  - We walk Chebyshev 7 / 6 to refill; they walk 3 / 3.
  - 42 / 59% of our arrivals under 100 paint are dry (theirs 25 / 32%).
  - 38 / 56% of them are at a money tower with 2000+ chips and a broken pattern (theirs 7 / 9%), and 83 / 87% of those are dry.
  - After a dry visit we withdraw elsewhere within 10 rounds 9 / 12% of the time (theirs 36 / 34%).
- **Starving beside our own towers** (`t156`).
  - 16% of the times our robots hit 0 paint they are beside one of our towers, 11.1 times a loss (theirs 3.0). 67% of those are at money towers while we hold 2000+ chips.
  - 510 robot-turns a loss end beside our drained money towers (4.5%; theirs 1.8%).

### 1.2 New set (y360 and y374; 26 losses, 19 wins)
**The same shape, a little less extreme** (`t0_y360`, us / them):

| round | n | coverage % | towers | paint towers | chips | paint | units | soldiers | moppers |
|---|---|---|---|---|---|---|---|---|---|
| r100 | 26 | 18.1 / 20.0 | 6 / 5 | 1 / 1 | 1045 / 1060 | 2328 / 2267 | 10 / 11 | 9 / 6.5 | 0.5 / 3.5 |
| r150 | 25 | 28.1 / 25.7 | 7 / 7 | 1 / 1 | 1990 / 1159 | 1921 / 2392 | 13 / 16 | 10 / 8 | 3 / 6 |
| r200 | 25 | 31.1 / 28.2 | 7 / 8 | 1 / 2 | 1971 / 1874 | 1805 / 2871 | 16 / 21 | 8 / 9 | 4 / 7 |
| r300 | 22 | 29.8 / 39.0 | 6 / 11 | 2 / 3 | 2039 / 1216 | 2166 / 4853 | 18.5 / 29.5 | 8 / 13 | 6 / 12 |
| r400 | 15 | 28.1 / 48.5 | 5 / 12 | 2 / 4 | 1780 / 1127 | 2189 / 6805 | 20 / 43 | 6 / 18 | 6 / 14 |

- Wins at r200: 43.0 / 26.8% coverage, 2 / 1 paint towers, 1328 chips.
- **Famine** (`t106_y360`): 46.4% of loss rounds have every tower under 200 paint (theirs 34.0%), at a median 1942 chips. Our last paint tower died for good in 10 losses (median r341.5); theirs in none.
- **Second paint tower** (`t180_y360`): in 18 of 26 losses (12 by r200); theirs in 25.
- **New towers** (`t180_y360`): we build 1.42 / 1.44 (r101-200 / r201-300); they build 2.31 / 2.40, plus 0.60 taken from us.
- **Refill visits** (`t182_y360`): 51 / 60% of our arrivals are dry (theirs 19 / 26%). 51 / 41% are at money towers with 2000+ chips and a broken pattern (theirs 10 / 10%), 83 / 84% of them dry.
- **Drains** (`t186_y360`): our soldiers lose 50 / 59 paint per 100 soldier-rounds to enemy moppers (theirs 21 / 22). Their mopper-rounds per loss are 630 / 934; ours 277 / 456.
- **Tower fire** (`t163_y360`): kills 10.0 of our robots a loss (7.7 soldiers) and 8.3 of theirs (5.8). Siege rules have been tried repeatedly; no new rule.
- **Per opponent** (`t187_y360`): om-nom (7 losses, 4 eliminations) leads 11 / 4 towers at r300 with 14 / 4 soldiers. confused leads 15.5 / 8.5 towers at r300.

**Eliminations** (`t193`; 12 over both sets).
- How our towers die:
  - 95 of our towers were killed, mostly by soldiers (2.0-2.6 per kill, 0.2-0.4 splashers), in assaults lasting a median 13-22 rounds;
  - before the final assault the tower held a median 100 / 34 / 25 / 0 paint (r1-100 / r101-200 / r201-300 / r301+);
  - it spawned 0.23 / 0.29 / 0.42 / 0.00 robots during the assault, with a median 1 robot of ours within d2 20.
- 35 of the 36 robots alive when our last tower fell then starved.
- The two early eliminations are om-nom rushes on small maps:
  - **m7565g1 (Jail):** 3 soldiers kill our paint tower at r35 and our money tower at r49.
  - **m7565g0 (Brat):** money towers fall at r53 and r62. Then our paint tower never spawns again (see bug 4.5).

## 2. Differences, as codeable rules

The first two rules are one failure seen from two sides. With 2000+ chips, our robots keep returning to drained money towers that will not churn, and they starve there. It happens in r100-300, in the paint economy, and in every game that reaches 2000 chips.

### 2.1 r1: let the churn-wait repair reach the wrong tile (high-medium; new)
**Evidence** (`t191_srpblock`, `t183_trap`). The visits counted are our soldiers' dry visits at L1 money towers while we hold 2000+ chips and the 5x5 holds no enemy paint. Numbers are for losses, r101-200 / r201-300.

| | main set (29 losses) | new set (26 losses) |
|---|---|---|
| visits (theirs) | 96 / 144 (12 / 24) | 74 / 107 (7 / 25) |
| pattern broken | 76 / 90% | 86 / 89% |
| wrong tiles per broken pattern (median) | 1 / 1 | 2 / 3 |
| wrong tiles: own paint, wrong colour | 62 / 80% | 82 / 92% |
| wrong tiles: empty | 38 / 20% | 18 / 8% |
| soldier visits at 1-3 wrong tiles | 38 / 61 | 39 / 28 |
| ... a wrong tile in reach at some turn | 32 / 28% | 28 / 21% |

- **A soldier can fix these tiles.** `Churn.repairPattern` repaints both kinds (own wrong colour and empty).
- **But it rarely reaches them.** Wins show the same low reach: 27 / 46% (main), 41 / 30% (new).
  - The stay lasts a median 2 rounds, which is `CHURN_WAIT_ROUNDS`.
  - The tiles left wrong are the ones earlier waiters could not reach.
- **One or two steps fix it.** From a tower-adjacent tile on a side, 4 of the 24 pattern tiles lie outside the soldier's attack reach (r2 9); from a corner, 7. One step along the ring of adjacent tiles (two from a corner) brings any of them into reach, and the soldier stays adjacent, as `Churn.towerTurn` and `Churn.rebuild` require.
- **This is the "pattern wrong" part of the trap** (main 30 / 36% of our soldiers' dry money visits; new 29 / 20%). One unreachable tile blocks the churn. The robot flags the tower, then ignores the flag because we hold 2000+ chips (Unit.java:22), and comes back. A new wait at the same tower needs `CHURN_WAIT_RESET` (50 rounds).

**Code.**
- `Churn.repairPattern` (Churn.java:50-64) repaints the first wrong tile it can attack, and never moves.
- The churn wait (Unit.java:47-52) goes on while it paints; otherwise it lasts `CHURN_WAIT_ROUNDS` (2; Tune.java:131) and restarts only after `CHURN_WAIT_RESET` (50; Tune.java:132).

**Rule (r1).** In `repairPattern`, when no wrong tile is in attack range:
- step to the free tower-adjacent tile nearest the nearest wrong tile without enemy paint;
- repaint it if it is now in range;
- count the turn as repairing (`churnAt = G.round`);
- leave enemy-painted tiles alone.

**Expected size.** Medium, in r100-300 and in paint.
- About 70 (main) and 50 (new) soldier visits in r101-300 of the losses had no wrong tile in reach. That is roughly 0.6 to 1 more churn a loss, each 500 paint for 1000 of the 2000-3400 chips we leave idle.
- It also shortens trap episodes, half of which end with the robot dead.

**Interaction with SRPs.** 40% of the wrong tiles in the new set (11 / 33% in the main set) carry the colour of one of our completed SRPs. Repairing them breaks that SRP, and our SRP work completes 56-77% of broken SRPs again (`t175`). So the two can fight; v1 (2.3) removes the clash at its source.

**Prior attempts.** The repair has never been made to move:
- skip enemy paint: t171 +13, t175 -16, y285 +2;
- leave SRP tiles alone: t178 -35;
- repaint our own wrong colour outside the wait: t132 -140, t196 -102.

**Candidates.** r1; r1d1; r1v1.

### 2.2 d1: honour the dry flag at level-2+ money towers (medium; a bug, tried before only in a bundle)
**The mechanism.**
- `Unit.refill` skips any tower flagged dry, except a money tower while we hold 2000+ chips, betting that the tower will churn.
- Only an L1 money tower churns (Tower.java:18). The starting money tower is L2, and money towers never regain paint. So a drained L2+ money tower is empty for good.
- Yet it stays the nearest refill target. The robot arrives, takes nothing, flags the tower, steps away, and the next turn ignores the flag again.

**Evidence** (`t183`, `t185`, `t189`; losses, our soldiers, r101-200 / r201-300).
- **Main set:**
  - Dry money-tower visits: 0.6 / 1.0 per 100 soldier-rounds (theirs 0.2 / 0.2).
  - What blocked the churn:

    | blocked by | us | them |
    |---|---|---|
    | an L2+ tower | 42 / 41% | 6 / 11% |
    | wrong pattern | 30 / 36% | |

  - Episodes, from the visit to the next withdrawal of 30+ paint (theirs in brackets): 7.3 / 8.5 episode rounds per 100 soldier-rounds (3.7 / 2.4), a median 25 / 23.5 rounds, and 50 / 48% end with the robot dead (20 / 15%).
  - L2+ episodes last a median 52 / 51 rounds with 5.6 / 7.8 re-entries, while another tower held 60+ paint at a median Chebyshev 8 / 9.5.
  - Splashers: 15.5 / 17.5 episode rounds per 100 splasher-rounds (theirs 3.4 / 6.0).
  - The starting money tower stands drained with 2000+ chips for 65 rounds a loss in r101-300 (in 23 of 29 losses), drawing 29 robot-rounds within Chebyshev 2.
  - **Long stays** (`t189`): 99 stays of 10+ rounds beside the drained starting tower, 40 of them ending with the robot dead. Examples:
    - m7373g1: soldier 10838 waits from r406 to its death at r573, with a 60-paint tower 3 tiles away;
    - m7310g2: soldiers 13312 and 10142 die the same way.
- **New set:**
  - Dry money-tower visits: 0.8 / 0.9 per 100 soldier-rounds (theirs 0.1 / 0.1).
  - L2+ blocks 46 / 53% of them (92% of the 36 visits in r1-100).
  - Episode rounds 7.4 / 7.3 per 100 (theirs 2.6 / 2.7), of which 2.1 / 2.6 at L2+ towers.
  - L2+ episodes last a median 128.5 / 72 rounds with 15.5 / 8.3 re-entries.
  - The starting tower stands drained for 58 rounds a loss (19 of 26 losses).
  - 41 long stays, 13 robots dead. Example: m7527g2, soldier 13277 beside the starting L2 tower from r76 to r181 with 2780 chips; the nearest tower with 60+ paint was 25 tiles away.
- **An L2 churn would rarely help** (`t190`, `t194`).
  - Main set: 0 of 153 dry L2+ visits in r101-300 found the pattern intact.
  - New set: 51 of 180 did, all at two towers (m7547g2's starting tower, m7520g0's upgraded one).

**Code.**
- Unit.java:22:
  ```java
  if (Towers.dry[i] > 0 && G.round - Towers.dry[i] < (...) && !(Towers.kind[i] == Towers.MONEY && Churn.churnable())) {
  ```
- `Towers` keeps no level (Towers.java:14-16; `note` at 26-29, called from G.java:97).
- Beside a dry tower, Unit.java:54 (`if (!rc.isActionReady()) return true;`) waits out the cooldown with nothing to take.

**Rule.**
- **d1:**
  - `Towers` keeps an L1 flag. It is set in `note` from `RobotInfo.type` (G.java:97), and is true for towers we complete ourselves (Churn.java:42, Soldier.java:268 and 287).
  - `forget` moves it along. Allocate it next to `dry` (Unit.java:79), so G's class-init bytecode stays the same.
  - The exemption at line 22 then also requires the flag.
- **d1b:** d1, and line 54 waits only when `take > 0`.

**Expected size.** Small to medium.
- About 45 soldier-rounds and 20 splasher-rounds a loss in r101-300, and about 0.3-0.5 robots.
- About 1 robot a loss after r300.
- No churn is lost, because an L2+ tower cannot churn.

**Prior attempts.**
- t126 (L1 only, and only once the tower was in sight): -38.
- y286 (this check plus four other dry-flag changes): flat, -1 after 568.
- y288 (stop walking to a dry tower): -21.
- Other dry-flag work: t110 / t113, t139, t173, t166, t191.
- The level check alone has not been tested since t126. The trap's size in both sets is the new evidence.

**Candidates.** d1; d1b.

### 2.3 v1: SRP picks must see their Chebyshev-4 ring (medium; new evidence, stronger in the new set)
**Evidence** (`t157`, `t191`).

| | main set | new set |
|---|---|---|
| our SRPs beside our money towers that disagree with the pattern | 82% (t188), 74% (y358) | 90% (y360, 255 of 282), 88% (y374) |
| of those, picked by a soldier that never saw the already-standing tower | 466 of 531 (88%) | 258 of 276 (93%) |
| broken money patterns at dry L1 visits holding an SRP-coloured tile (r101-200 / r201-300) | 14 / 36% | 59 / 49% |
| ... where the SRP colour is the only fault | 14 / 28% | 48 / 27% |

**Code.** `Soldier.pickSrp` (Soldier.java:321-370). The ruin loop (340-353) walks `G.ruinList`, which holds only ruins this soldier has seen, so the money-agreement test at line 351 never sees unseen towers.

**Rule (v1).** Reject a centre while any tile within Chebyshev 4 of it lacks G's SEEN bit. Then every ruin and tower near it is known and checked. The test costs up to 56 more memory reads per candidate, inside `SRP_PICK_BC`.

**Expected size.** Medium-low and uncertain.
- It removes most clashes (about 8 a game) and the churns they block.
- It delays SRPs at the edge of explored ground.

**Prior attempts.** All pick restrictions lost: t104 -62 (bundled), t168 -26, t178 -35, t199 -30. v1 delays picks rather than dropping them.

**Candidates.** v1; r1v1.

### 2.4 Lower priority
- **The new-tower stall in r101-300** (`t180`, `t181`, `t188`). This is the largest structural difference, but I have no new safe rule for it.
  - 66% of our free ruin-rounds are contested and `pickRuin` skips them (Soldier.java:144).
  - Of the ruins nearer to us at r101, we build 43% and they build 18% (wins 67 / 5%).
  - Tried: moppers to contested ruins (t90-t100); splasher pattern clearing (t117, t120, t131); the contested skip at 80 rounds (y369 -21).
  - Untried: **c1** = `SOL_CONTESTED_BAD` 20 (Tune.java:52). Evidence is weak: their clean spells near our towers last a median 10 rounds.
- **Mopper drains** (`t186`): 59 / 67 paint per 100 soldier-rounds for ours against 20 / 23 for theirs (new set 50 / 59 against 21 / 22). Tried: t77 -51, t144, y13 -33, t174, t179, y305.
- **Money-tower upgrades** (`t185`): 1.83 a loss in the main set, 0.58 in the new set (0.11 a win). Each turns a churnable L1 tower into a trap (2.2). Recheck `MONEY_UPGRADE_EXTRA` only after d1.
- **Splashers at broken L1 patterns** (`t183`).
  - 10-12 episode rounds per 100 splasher-rounds (theirs 0.4-2.2), and splashers cannot repair a pattern.
  - **d2** = d1 + splashers and moppers honour the flag when they see the pattern broken. Try it only after d1 and r1 (t173 lost 24).
- **Spawn reserve with no money tower** (bug 4.5): 3 of 55 losses; small.

## 3. What changed since study 15
- **Record.** Main set 56% (37-29), the same as study 15 (56-44). New set 42% (19-26).
  - om-nom: 9-6 in the main set, 2-7 in the new set (4 eliminations) with the same package (srpStack).
  - old-but-gold: 1-5 and 2-4.
- **The gap opens later and more slowly in losses.**

  | losses (study 15 in brackets) | towers | coverage |
  |---|---|---|
  | r200 | 6.5 / 7.5 (6 / 8) | 32.2 / 33.1% (30.8 / 35.8%) |
  | r300 | 6 / 8.5 (5 / 10) | 30.4 / 43.0% (32.0 / 50.9%) |

  Median end r420 (r364); eliminations 7 of 29 (12 of 44).
- **Tower fire.** Main set 7.6 of ours against 11.9 of theirs (study 15: 9.9 against 4.6); new set 10.0 against 8.3. t198, the lethal-HP guard, was retired flat (+4 after 582).
- **Paint famine** is a little worse in the main set: 56.1% of loss rounds (51.4%), new set 46.4%. Our last paint tower dies later: r276 (r181), new set r341.5.
- **Drained money towers.** 4.5% of our robot-turns end beside one (4.2%); theirs 1.8% (1.1%).

**Question 2: did y358 and y360 do what they intend?** (`t184_versions`; t188 45 games, y358 42, y360 42; per 100 soldier-rounds unless stated)

| | t188 | y358 | y360 |
|---|---|---|---|
| soldier turns under 100 paint, r101-200 | 43.6% | 36.3% | 39.7% |
| soldier turns under 50 paint, r101-200 | 18.3% | 18.3% | 20.1% |
| turns at 0 paint, r101-200 | 3.1% | 3.7% | 4.3% |
| starved soldiers per game (r1-100 / r101-200 / r201-300) | 1.04 / 3.51 / 4.00 | 1.43 / 4.12 / 4.12 | 1.12 / 4.50 / 3.45 |
| y360's window: turns at 40-49 paint with no paint action (same phases) | 3.07 / 2.49 / 1.87 | 2.56 / 2.57 / 1.79 | 1.27 / 2.10 / 2.04 |
| paint actions (same phases) | 45.0 / 42.3 / 29.8 | 42.1 / 41.4 / 29.7 | 41.9 / 38.4 / 29.4 |
| coverage at r100 / r150 / r200 (median %) | 20.5 / 31.0 / 38.3 | 19.5 / 30.2 / 35.9 | 22.0 / 31.7 / 34.7 |

- **y358: partly.** It cut low-paint soldier turns, but did not reduce starvation or raise coverage. On its 5 pairings shared with t188 it looks better (starved 5.4 to 3.6 in r101-200), but that is too few games to call.
- **y360: only in r1-100.** It halves its window in r1-100 and adds 2.5 points of coverage at r100. After r100 there is no gain: paint actions and coverage at r200 are lower, and starvation in r101-200 is higher.
  - Record: y360 18-24 against y358's 23-19 (TOP7 16-23 against 15-18). y360 drew harder opponents.
  - On shared pairings there is no measurable difference (see t151 above).
- **The trap did not grow.** Trap-episode rounds were t188 6.8 / 5.2, y358 5.1 / 4.4, and y360 7.4 / 7.3 per 100 soldier-rounds.
- **y374:** one match (1-2 against spaark). Not measurable.

## 4. Broken in our bot (y360; the same in y374)
1. **The money-tower dry-flag exemption ignores the tower's level** (Unit.java:22; Towers.java:14-29; G.java:97). research/audit/bugs-t135.md 1(a) found it before. See 2.2.
2. **The churn-wait repair never moves** (Churn.java:50-64; Unit.java:47-52). See 2.1.
3. **`Unit.refill` lingers at dry towers.** It waits out the cooldown with nothing to take (Unit.java:54), and walks on toward a tower it has just flagged dry (Unit.java:58-60; y288's fix tested -21).
4. **`pickSrp` checks only the ruins and towers the soldier has seen** (Soldier.java:340-353). See 2.3.
5. **New: the spawn reserve deadlocks when no money tower stands** (`t195`).
   - `Tower.reserve` (Tower.java:61-66) holds 1000 chips from r40. `Tower.build` (Tower.java:76) then waits for the unit cost + 1000 (Tune.java:17-20).
   - With no money tower there is no chip income, so the wait never ends.
   - It held back a soldier we could afford in 3 of 55 losses: m7351g2 (30 rounds), m7565g0 (137 rounds from r71) and m7599g1 (43 rounds). It also happened in one 2000-round win.
   - In m7565g0 a paint tower holding up to 712 paint sat beside 990 chips and never spawned; one enemy soldier killed it at r207.
   - Fix: reserve 0 when chips have not risen for a few rounds. Small impact.
6. **Still standing:**
   - `repairPattern` attacks enemy-painted tiles (Churn.java:61);
   - `Towers.forget` leaves dry flags behind (Towers.java:31-37);
   - `Churn.rebuild` completes money towers only (Churn.java:36-46);
   - `Tower.build` stalls at the first unit it cannot pay (Tower.java:46-47, 73-86);
   - the comment at Tune.java:44 cites y357 (cosmetic).

## 5. Suggested test order
1. **r1** (2.1) on y374. It fires in every game that reaches 2000 chips.
2. **d1** (2.2) on y374, as a separate candidate.
   - If r1 and d1 are both level or better, then r1d1.
   - Try d1b only after d1.
3. **v1** (2.3) on y374; then **r1v1** if r1 and v1 are both level or better.
4. **Optional:** c1; the reserve fix (4.5); d2 only after d1 and r1.

None of these overlaps the pool's current candidates (y377-y381: explore-paint timing, paint underfoot, refill threshold, siege range).

**Not measured:**
- why a third of the reachable wrong tiles still went unrepaired;
- y374 beyond 3 games;
- whether their clean-and-take of our ruins uses moppers or splashers;
- the trap in study 15's set;
- whether our own SRP breaks come from ruins the picker had not seen.

**Dump directories to delete afterwards** (session scratchpad /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad, about 1.3 GB):
- /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study16/dump (188M) and /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study16/cache (121M)
- /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study15/dump (139M) and /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study15/cache (89M)
- /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study14/dump (115M) and /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study14/cache (73M)
- /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study13/dump (355M) and /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study13/cache (232M)

`S16SET=prev|prev2|prev3|t188`, `t151` and `t184` read the older dumps, so delete them only when no rerun is planned.

## Summary: the top three
1. **r1: let the churn-wait repair reach the wrong tile** (Churn.java:50-64).
   - When a drained L1 money tower fails to churn while we hold 2000+ chips, its pattern is usually 1-3 tiles off, in our own paint or empty.
   - The waiting soldier reaches a wrong tile in only 21-32% of visits, in both sets.
   - One or two steps along the ring fix it: about 0.6 to 1 more 500-paint churn a loss, paid with chips we leave idle. New.
2. **d1: honour the dry flag at L2+ money towers** (Unit.java:22, with an L1 flag in `Towers`).
   - 41-53% of our soldiers' dry money-tower visits are at L2+ towers that can never churn or refill.
   - Those episodes last a median 51-128 rounds with up to 15 re-entries, and 140 long stays in 55 losses ended with 53 robots dead.
   - A small bug fix; earlier forms were t126 (-38) and the y286 bundle (flat).
3. **v1: SRP picks must see their Chebyshev-4 ring** (Soldier.java:340-353).
   - 74-90% of our SRPs beside our money towers disagree with them, nearly always because the picker never saw the tower.
   - In the new set, SRP colours are the only fault in 27-48% of the broken patterns that block churns.
   - Test v1, and r1v1 together.

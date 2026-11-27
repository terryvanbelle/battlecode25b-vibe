# Local tournament Elo

Bradley-Terry ratings of our own bots in the local tournament (`tools/tourney.py`), all 133930 games in one fit as of 2026-11-27 04:08 PDT, so every point is on the same scale; earlier champions are shown at their current rating, and "Gain" is the rating over the champion it replaced. `tools/tourney.py rank` rewrites this table; `tools/tourney.py chart` also redraws the chart.

![local elo](local-elo.png)

| Champion from (PDT) | Bot | Change on base | Submission | Rating +- SE | Gain | Games |
|---|---|---|---:|---:|---:|---:|
| 2026-11-25 08:28 | v01 | foundation bot |  | 212 +- 18 |  | 435 |
| 2026-11-25 08:39 | v02 | nav wall-follow fix + bytecode guards on v01 | #6 | 277 +- 13 | +65 | 801 |
| 2026-11-25 09:01 | y02 | paint-heavy tower mix + paint towers upgraded first on v02 | #7 | 336 +- 11 | +59 | 1080 |
| 2026-11-25 09:49 | y06 | 3 opening soldiers instead of 2 on y02 | #35 | 357 +- 13 | +21 | 700 |
| 2026-11-25 10:09 | sw06 | no moppers before r80; a third of spawns moppers after (field study 1) on y02 | #36 | 415 +- 12 | +79 | 863 |
| 2026-11-25 11:04 | y11 | mid-game mix 3 moppers per 6 (soldier mopper splasher mopper soldier mopper) on sw06 | #37 | 448 +- 14 | +33 | 655 |
| 2026-11-25 11:24 | sw11 | at most 1 helper soldier per ruin (more ruins claimed in parallel) on y11 | #38 | 506 +- 11 | +58 | 1159 |
| 2026-11-25 12:24 | y17 | sw11 + moppers prefer enemies within r2 25 of our towers (sw12) on sw11 | #39 | 524 +- 12 | +18 | 871 |
| 2026-11-25 12:44 | y19 | sw11 with soldiers joining an occupied ruin only when adjacent (r2<=2) on y17 | #40 | 559 +- 14 | +35 | 678 |
| 2026-11-25 13:04 | y24 | y17 with mopper defence widened (DEFEND_R2 36 / bonus 80) on y19 | #41 | 593 +- 13 | +35 | 679 |
| 2026-11-25 13:24 | y25 | y19 (adjacent-only ruin helping) + y17 tower-defending moppers on y24 | #42 | 603 +- 12 | +9 | 898 |
| 2026-11-25 13:44 | sw16 | y25 + soldier siege: with no ruin and paint>=80 kite a known enemy tower within r2 64 on y25 | #43 | 627 +- 11 | +24 | 976 |
| 2026-11-25 14:04 | sw17 | y28 (siege from 50 paint r2 100) + splasher siege (towers weigh 40; walk to known tower within r2 100 at paint>=100) on sw16 | #44 | 660 +- 10 | +33 | 1110 |
| 2026-11-25 14:44 | y30 | y28 with soldier siege from 30 paint within r2 144 (no splasher siege) on sw17 | #45 | 677 +- 7 | +17 | 2377 |
| 2026-11-25 16:30 | y44 | study 3 tactic 3 (enemy refill policy): return at 50% paint (soldier 100/splasher 100/mopper 40) + end-of-turn top-up from any adjacent ally tower on y30 | #46 | 808 +- 8 | +131 | 2250 |
| 2026-11-25 17:30 | y56 | study 3 tactic 4 (tower churn): a drained L1 money tower with intact pattern and an ally adjacent disintegrates at >=2000 chips; adjacent robots re-complete it for a fresh 500 paint on y44 | #47 | 885 +- 10 | +77 | 1320 |
| 2026-11-25 18:50 | y58 | study 3 tactic 2 (early soldiers paint patterns not coverage): exploring soldiers paint no coverage before r50 on y56 | #48 | 926 +- 11 | +42 | 997 |
| 2026-11-25 19:30 | t04 | t02 (no coverage painting before r80) + t03 (units wait beside drained money towers and repair their pattern so churn fires; study 3 tactics 2 and 4) on y58 | #49 | 959 +- 11 | +33 | 1065 |
| 2026-11-25 20:30 | t08 | study 4 2.2 (contested ruins): soldiers skip a ruin with enemy paint in its visible 5x5 (bad for 50 rounds) on t04 | #50 | 1039 +- 13 | +80 | 775 |
| 2026-11-25 20:50 | t16 | t12 (t08 + study 4 2.1 spawn freeze 8 rounds in 20 below 1000+cost) + study 4 2.4 money-first: builds money until 8 towers then paint while paint towers < n/5; paint first only if none (all towers known) on t08 | #51 | 1314 +- 12 | +274 | 1213 |
| 2026-11-25 21:50 | t20 | study 4 2.3: splashers weight enemy towers 30 (was 12) in the splash score on t16 | #52 | 1355 +- 15 | +41 | 587 |
| 2026-11-25 22:10 | y74 | unit audit (owner prompt #15): splash-grid bug fix (enemy tiles never scored) + moppers stop once enemy paint is in mop reach; built on t16 on t20 | #53 | 1500 +- 10 | +145 | 1255 |
| 2026-11-25 23:10 | t25 | unit audit + top teams' unit mix (616 S / 662 X / 701 M): after r80 paint towers cycle soldier-splasher-mopper; money towers keep S M X M S M on y74 | #54 | 1536 +- 13 | +36 | 680 |
| 2026-11-25 23:30 | t27 | top teams' splasher-heavy late mix pushed further: paint towers cycle soldier-splasher-splasher-mopper after r80 on t25 | #55 | 1558 +- 9 | +23 | 1554 |
| 2026-11-26 00:30 | y95 | upgrade spare 1200 (was 800): chips stay for new towers longer on t27 | #56 | 1594 +- 9 | +35 | 1822 |
| 2026-11-26 02:01 | t36 | late SRPs (study 4 2.6 / study 3 tactic 7): soldiers without a ruin build SRPs on the x%4==2 y%4==2 lattice from r100 with chips>=1000; splashers avoid repainting SRP secondary tiles on y95 | #57 | 1631 +- 11 | +37 | 977 |
| 2026-11-26 02:50 | y110 | money towers upgrade only with 2500 chips beyond the cost+spare (was 1000): chips go to new towers and SRPs on t36 | #58 | 1662 +- 10 | +31 | 1260 |
| 2026-11-26 03:30 | t42 | study 4 3.1 recovery: with every tower known and no money tower left the next ruin is a money tower on y110 | #59 | 1677 +- 10 | +15 | 1332 |
| 2026-11-26 04:10 | t45 | study 3 tactic 1: after r40 towers spawn only with 1000 chips beyond the unit's cost (no 600-chip window) on t42 | #60 | 1724 +- 10 | +47 | 1226 |
| 2026-11-26 04:50 | t47 | study 3 tactic 5: a mopper due in the cycle spawns even below the 1000 reserve when an enemy robot is within d2 20 of the tower on t45 | #61 | 1753 +- 7 | +30 | 2398 |
| 2026-11-26 06:30 | t58 | study 5 2.3: a splasher that has not splashed for 8 rounds (while able to) explores instead of chasing the nearest non-ally tile on t47 | #62 | 1819 +- 11 | +66 | 1087 |
| 2026-11-26 07:10 | t61 | study 5 2.1 (softened): money towers for builds 1-5; then one more paint tower per 4 towers on t58 | #63 | 1856 +- 11 | +37 | 938 |
| 2026-11-26 07:30 | y155 | study 5 2.1 tuned: money towers for builds 1-6; then one more paint tower per 4 towers on t61 | #64 | 1888 +- 9 | +32 | 1615 |
| 2026-11-26 08:27 | t70 | y155 + splashers weight enemy towers 30 (t68) + 2000+ chips makes the next tower a paint tower (y159) on y155 | #65 | 1916 +- 7 | +28 | 2530 |
| 2026-11-26 09:47 | t74 | moppers weight enemy paint near ruins 40 (study 6 2.1c) on t70 | #66 | 1935 +- 8 | +19 | 2200 |
| 2026-11-26 10:47 | y170 | soldiers make the next tower a paint tower at 1500+ chips (t63 tuning; was 2000) on t74 | #67 | 1931 +- 7 | -4 | 2823 |
| 2026-11-26 11:27 | t85 | study 6 2.2 ruin denial from where the soldier stands: a soldier with no ruin paints empty tiles of a ruin the enemy is building; without walking to it on y170 | #68 | 1989 +- 7 | +58 | 2556 |
| 2026-11-26 12:47 | t91 | study 7 2.5: moppers ignore ruins under enemy towers when weighting ruin paint on t85 | #69 | 2002 +- 5 | +13 | 4664 |
| 2026-11-26 13:27 | y195 | study 7 2.1a: explore unseen tiles first; up to 16 random draws on t91 | #70 | 2015 +- 9 | +13 | 1349 |
| 2026-11-26 14:12 | y197 | ruin denial stops at 2 of our tiles (tuning of study 6 2.2) on y195 | #71 | 2031 +- 7 | +16 | 2235 |
| 2026-11-26 15:27 | y211 | study 7 2.1a tuned: up to 128 random draws for an unseen explore target (was 16) on y197 | #72 | 2034 +- 6 | +3 | 4141 |
| 2026-11-26 17:47 | y221 | study 8 2.2 (paint the first tower's pattern on the way in; a second soldier on the first ruin) + explore timeout 90; first champion through the confirmation stage (owner #46) on y211 | #73 | 2067 +- 5 | +33 | 5536 |
| 2026-11-26 19:34 | t111 | splashers attack enemy paint/money towers from a stand-off tile outside their range (study 8 2.4) on y221 | #74 | 2085 +- 5 | +18 | 7332 |
| 2026-11-26 23:27 | t118 | study 9 2.1b: a soldier on a blocked pattern with no own mopper or splasher in view gives up after 5 turns (was 25); confirmed +71 +-29 in 153 fresh games on t111 | #75 | 2123 +- 6 | +38 | 4833 |
| 2026-11-27 01:07 | t122 | study 9 2.4: paint-tower dry flags expire after 10 rounds (was 40) and a flagged tower in sight is re-sensed; confirmed +6 +-19 in 378 fresh games; +16 overall on t118 | #76 | 2138 +- 5 | +15 | 5800 |

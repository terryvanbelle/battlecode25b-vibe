# Local tournament Elo

Bradley-Terry ratings of our own bots in the local tournament (`tools/tourney.py`), all 53904 games in one fit as of 2026-11-26 03:32 PDT, so every point is on the same scale; earlier champions are shown at their current rating, and "Gain" is the rating over the champion it replaced. `tools/tourney.py rank` rewrites this table; `tools/tourney.py chart` also redraws the chart.

![local elo](local-elo.png)

| Champion from (PDT) | Bot | Change on base | Submission | Rating +- SE | Gain | Games |
|---|---|---|---:|---:|---:|---:|
| 2026-11-25 08:28 | v01 | foundation bot |  | 1098 +- 18 |  | 435 |
| 2026-11-25 08:39 | v02 | nav wall-follow fix + bytecode guards on v01 | #6 | 1161 +- 13 | +64 | 801 |
| 2026-11-25 09:01 | y02 | paint-heavy tower mix + paint towers upgraded first on v02 | #7 | 1216 +- 11 | +55 | 1080 |
| 2026-11-25 09:49 | y06 | 3 opening soldiers instead of 2 on y02 | #35 | 1232 +- 13 | +16 | 700 |
| 2026-11-25 10:09 | sw06 | no moppers before r80; a third of spawns moppers after (field study 1) on y02 | #36 | 1280 +- 12 | +64 | 863 |
| 2026-11-25 11:04 | y11 | mid-game mix 3 moppers per 6 (soldier mopper splasher mopper soldier mopper) on sw06 | #37 | 1299 +- 14 | +19 | 655 |
| 2026-11-25 11:24 | sw11 | at most 1 helper soldier per ruin (more ruins claimed in parallel) on y11 | #38 | 1330 +- 11 | +31 | 1159 |
| 2026-11-25 12:24 | y17 | sw11 + moppers prefer enemies within r2 25 of our towers (sw12) on sw11 | #39 | 1342 +- 12 | +12 | 871 |
| 2026-11-25 12:44 | y19 | sw11 with soldiers joining an occupied ruin only when adjacent (r2<=2) on y17 | #40 | 1348 +- 14 | +6 | 678 |
| 2026-11-25 13:04 | y24 | y17 with mopper defence widened (DEFEND_R2 36 / bonus 80) on y19 | #41 | 1372 +- 13 | +24 | 679 |
| 2026-11-25 13:24 | y25 | y19 (adjacent-only ruin helping) + y17 tower-defending moppers on y24 | #42 | 1361 +- 12 | -11 | 898 |
| 2026-11-25 13:44 | sw16 | y25 + soldier siege: with no ruin and paint>=80 kite a known enemy tower within r2 64 on y25 | #43 | 1384 +- 11 | +23 | 976 |
| 2026-11-25 14:04 | sw17 | y28 (siege from 50 paint r2 100) + splasher siege (towers weigh 40; walk to known tower within r2 100 at paint>=100) on sw16 | #44 | 1394 +- 10 | +10 | 1110 |
| 2026-11-25 14:44 | y30 | y28 with soldier siege from 30 paint within r2 144 (no splasher siege) on sw17 | #45 | 1399 +- 7 | +5 | 2377 |
| 2026-11-25 16:30 | y44 | study 3 tactic 3 (enemy refill policy): return at 50% paint (soldier 100/splasher 100/mopper 40) + end-of-turn top-up from any adjacent ally tower on y30 | #46 | 1458 +- 8 | +59 | 2250 |
| 2026-11-25 17:30 | y56 | study 3 tactic 4 (tower churn): a drained L1 money tower with intact pattern and an ally adjacent disintegrates at >=2000 chips; adjacent robots re-complete it for a fresh 500 paint on y44 | #47 | 1524 +- 10 | +65 | 1320 |
| 2026-11-25 18:50 | y58 | study 3 tactic 2 (early soldiers paint patterns not coverage): exploring soldiers paint no coverage before r50 on y56 | #48 | 1544 +- 11 | +20 | 997 |
| 2026-11-25 19:30 | t04 | t02 (no coverage painting before r80) + t03 (units wait beside drained money towers and repair their pattern so churn fires; study 3 tactics 2 and 4) on y58 | #49 | 1507 +- 11 | -37 | 1065 |
| 2026-11-25 20:30 | t08 | study 4 2.2 (contested ruins): soldiers skip a ruin with enemy paint in its visible 5x5 (bad for 50 rounds) on t04 | #50 | 1530 +- 13 | +23 | 738 |
| 2026-11-25 20:50 | t16 | t12 (t08 + study 4 2.1 spawn freeze 8 rounds in 20 below 1000+cost) + study 4 2.4 money-first: builds money until 8 towers then paint while paint towers < n/5; paint first only if none (all towers known) on t08 | #51 | 1707 +- 11 | +177 | 1169 |
| 2026-11-25 21:50 | t20 | study 4 2.3: splashers weight enemy towers 30 (was 12) in the splash score on t16 | #52 | 1706 +- 15 | -2 | 587 |
| 2026-11-25 22:10 | y74 | unit audit (owner prompt #15): splash-grid bug fix (enemy tiles never scored) + moppers stop once enemy paint is in mop reach; built on t16 on t20 | #53 | 1785 +- 10 | +79 | 1255 |
| 2026-11-25 23:10 | t25 | unit audit + top teams' unit mix (616 S / 662 X / 701 M): after r80 paint towers cycle soldier-splasher-mopper; money towers keep S M X M S M on y74 | #54 | 1790 +- 13 | +6 | 680 |
| 2026-11-25 23:30 | t27 | top teams' splasher-heavy late mix pushed further: paint towers cycle soldier-splasher-splasher-mopper after r80 on t25 | #55 | 1771 +- 9 | -19 | 1554 |
| 2026-11-26 00:30 | y95 | upgrade spare 1200 (was 800): chips stay for new towers longer on t27 | #56 | 1769 +- 9 | -2 | 1822 |
| 2026-11-26 02:01 | t36 | late SRPs (study 4 2.6 / study 3 tactic 7): soldiers without a ruin build SRPs on the x%4==2 y%4==2 lattice from r100 with chips>=1000; splashers avoid repainting SRP secondary tiles on y95 | #57 | 1775 +- 11 | +7 | 977 |
| 2026-11-26 02:50 | y110 | money towers upgrade only with 2500 chips beyond the cost+spare (was 1000): chips go to new towers and SRPs on t36 | #58 | 1790 +- 10 | +15 | 1194 |
| 2026-11-26 03:30 | t42 | study 4 3.1 recovery: with every tower known and no money tower left the next ruin is a money tower on y110 | #59 | 1814 +- 16 | +24 | 462 |

# Local tournament Elo

Bradley-Terry ratings of our own bots in the local tournament (`tools/tourney.py`), all 40209 games in one fit as of 2026-11-25 23:12 PDT, so every point is on the same scale; earlier champions are shown at their current rating, and "Gain" is the rating over the champion it replaced. `tools/tourney.py rank` rewrites this table; `tools/tourney.py chart` also redraws the chart.

![local elo](local-elo.png)

| Champion from (PDT) | Bot | Change on base | Submission | Rating +- SE | Gain | Games |
|---|---|---|---:|---:|---:|---:|
| 2026-11-25 08:28 | v01 | foundation bot |  | 1117 +- 18 |  | 435 |
| 2026-11-25 08:39 | v02 | nav wall-follow fix + bytecode guards on v01 | #6 | 1181 +- 13 | +64 | 801 |
| 2026-11-25 09:01 | y02 | paint-heavy tower mix + paint towers upgraded first on v02 | #7 | 1236 +- 11 | +55 | 1080 |
| 2026-11-25 09:49 | y06 | 3 opening soldiers instead of 2 on y02 | #35 | 1251 +- 13 | +16 | 700 |
| 2026-11-25 10:09 | sw06 | no moppers before r80; a third of spawns moppers after (field study 1) on y02 | #36 | 1301 +- 12 | +65 | 863 |
| 2026-11-25 11:04 | y11 | mid-game mix 3 moppers per 6 (soldier mopper splasher mopper soldier mopper) on sw06 | #37 | 1321 +- 14 | +20 | 655 |
| 2026-11-25 11:24 | sw11 | at most 1 helper soldier per ruin (more ruins claimed in parallel) on y11 | #38 | 1354 +- 11 | +33 | 1159 |
| 2026-11-25 12:24 | y17 | sw11 + moppers prefer enemies within r2 25 of our towers (sw12) on sw11 | #39 | 1367 +- 12 | +12 | 871 |
| 2026-11-25 12:44 | y19 | sw11 with soldiers joining an occupied ruin only when adjacent (r2<=2) on y17 | #40 | 1376 +- 14 | +10 | 678 |
| 2026-11-25 13:04 | y24 | y17 with mopper defence widened (DEFEND_R2 36 / bonus 80) on y19 | #41 | 1401 +- 13 | +25 | 679 |
| 2026-11-25 13:24 | y25 | y19 (adjacent-only ruin helping) + y17 tower-defending moppers on y24 | #42 | 1393 +- 12 | -8 | 898 |
| 2026-11-25 13:44 | sw16 | y25 + soldier siege: with no ruin and paint>=80 kite a known enemy tower within r2 64 on y25 | #43 | 1416 +- 11 | +23 | 976 |
| 2026-11-25 14:04 | sw17 | y28 (siege from 50 paint r2 100) + splasher siege (towers weigh 40; walk to known tower within r2 100 at paint>=100) on sw16 | #44 | 1430 +- 10 | +13 | 1110 |
| 2026-11-25 14:44 | y30 | y28 with soldier siege from 30 paint within r2 144 (no splasher siege) on sw17 | #45 | 1437 +- 7 | +7 | 2377 |
| 2026-11-25 16:30 | y44 | study 3 tactic 3 (enemy refill policy): return at 50% paint (soldier 100/splasher 100/mopper 40) + end-of-turn top-up from any adjacent ally tower on y30 | #46 | 1511 +- 8 | +74 | 2250 |
| 2026-11-25 17:30 | y56 | study 3 tactic 4 (tower churn): a drained L1 money tower with intact pattern and an ally adjacent disintegrates at >=2000 chips; adjacent robots re-complete it for a fresh 500 paint on y44 | #47 | 1578 +- 10 | +67 | 1320 |
| 2026-11-25 18:50 | y58 | study 3 tactic 2 (early soldiers paint patterns not coverage): exploring soldiers paint no coverage before r50 on y56 | #48 | 1605 +- 11 | +27 | 997 |
| 2026-11-25 19:30 | t04 | t02 (no coverage painting before r80) + t03 (units wait beside drained money towers and repair their pattern so churn fires; study 3 tactics 2 and 4) on y58 | #49 | 1593 +- 11 | -13 | 1065 |
| 2026-11-25 20:30 | t08 | study 4 2.2 (contested ruins): soldiers skip a ruin with enemy paint in its visible 5x5 (bad for 50 rounds) on t04 | #50 | 1638 +- 13 | +45 | 738 |
| 2026-11-25 20:50 | t16 | t12 (t08 + study 4 2.1 spawn freeze 8 rounds in 20 below 1000+cost) + study 4 2.4 money-first: builds money until 8 towers then paint while paint towers < n/5; paint first only if none (all towers known) on t08 | #51 | 1859 +- 11 | +221 | 1169 |
| 2026-11-25 21:50 | t20 | study 4 2.3: splashers weight enemy towers 30 (was 12) in the splash score on t16 | #52 | 1879 +- 15 | +20 | 587 |
| 2026-11-25 22:10 | y74 | unit audit (owner prompt #15): splash-grid bug fix (enemy tiles never scored) + moppers stop once enemy paint is in mop reach; built on t16 on t20 | #53 | 2000 +- 10 | +121 | 1159 |
| 2026-11-25 23:10 | t25 | unit audit + top teams' unit mix (616 S / 662 X / 701 M): after r80 paint towers cycle soldier-splasher-mopper; money towers keep S M X M S M on y74 | #54 | 2036 +- 19 | +36 | 332 |

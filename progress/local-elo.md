# Local tournament Elo

Bradley-Terry ratings of our own bots in the local tournament (`tools/tourney.py`), all 25640 games in one fit as of 2026-11-25 17:51 PDT, so every point is on the same scale; earlier champions are shown at their current rating, and "Gain" is the rating over the champion it replaced. `tools/tourney.py rank` rewrites this table; `tools/tourney.py chart` also redraws the chart.

![local elo](local-elo.png)

| Champion from (PDT) | Bot | Change on base | Submission | Rating +- SE | Gain | Games |
|---|---|---|---:|---:|---:|---:|
| 2026-11-25 08:28 | v01 | foundation bot |  | 1227 +- 18 |  | 435 |
| 2026-11-25 08:39 | v02 | nav wall-follow fix + bytecode guards on v01 | #6 | 1291 +- 13 | +64 | 801 |
| 2026-11-25 09:01 | y02 | paint-heavy tower mix + paint towers upgraded first on v02 | #7 | 1347 +- 11 | +56 | 1080 |
| 2026-11-25 09:49 | y06 | 3 opening soldiers instead of 2 on y02 | #35 | 1364 +- 13 | +17 | 700 |
| 2026-11-25 10:09 | sw06 | no moppers before r80; a third of spawns moppers after (field study 1) on y02 | #36 | 1415 +- 12 | +69 | 863 |
| 2026-11-25 11:04 | y11 | mid-game mix 3 moppers per 6 (soldier mopper splasher mopper soldier mopper) on sw06 | #37 | 1439 +- 14 | +23 | 655 |
| 2026-11-25 11:24 | sw11 | at most 1 helper soldier per ruin (more ruins claimed in parallel) on y11 | #38 | 1480 +- 11 | +41 | 1159 |
| 2026-11-25 12:24 | y17 | sw11 + moppers prefer enemies within r2 25 of our towers (sw12) on sw11 | #39 | 1494 +- 12 | +14 | 871 |
| 2026-11-25 12:44 | y19 | sw11 with soldiers joining an occupied ruin only when adjacent (r2<=2) on y17 | #40 | 1513 +- 14 | +19 | 678 |
| 2026-11-25 13:04 | y24 | y17 with mopper defence widened (DEFEND_R2 36 / bonus 80) on y19 | #41 | 1541 +- 13 | +28 | 679 |
| 2026-11-25 13:24 | y25 | y19 (adjacent-only ruin helping) + y17 tower-defending moppers on y24 | #42 | 1540 +- 12 | -1 | 898 |
| 2026-11-25 13:44 | sw16 | y25 + soldier siege: with no ruin and paint>=80 kite a known enemy tower within r2 64 on y25 | #43 | 1564 +- 11 | +24 | 976 |
| 2026-11-25 14:04 | sw17 | y28 (siege from 50 paint r2 100) + splasher siege (towers weigh 40; walk to known tower within r2 100 at paint>=100) on sw16 | #44 | 1586 +- 10 | +22 | 1110 |
| 2026-11-25 14:44 | y30 | y28 with soldier siege from 30 paint within r2 144 (no splasher siege) on sw17 | #45 | 1599 +- 7 | +13 | 2377 |
| 2026-11-25 16:30 | y44 | study 3 tactic 3 (enemy refill policy): return at 50% paint (soldier 100/splasher 100/mopper 40) + end-of-turn top-up from any adjacent ally tower on y30 | #46 | 1715 +- 10 | +116 | 1451 |
| 2026-11-25 17:30 | y56 | study 3 tactic 4 (tower churn): a drained L1 money tower with intact pattern and an ally adjacent disintegrates at >=2000 chips; adjacent robots re-complete it for a fresh 500 paint on y44 | #47 | 1805 +- 17 | +90 | 428 |

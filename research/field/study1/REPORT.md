# Field study 1 (2026-11-25): y02 vs the top field, 21 lost games

The study covers matches 8, 9, 10, 11, 13, 27 and 28, with 12 won games as contrast (matches 6, 7, 12, 14). It used
replays only; no competitor code was read. The scripts and the full output (`rep.txt`) are in this folder.

**Losses:** 16 by MAJORITY_PAINTED, 5 by ALL_UNITS_DESTROYED. The median game lasted 354 rounds.

**When the losses happen:**
- We lead at round 100 (281 painted tiles vs 246).
- Then our coverage stays flat while theirs climbs: 286 vs 554 at r200, and 271 vs 886 at r300.

Medians across the 21 lost games:

| metric | us | them |
|---|---|---|
| paint stored in towers at r50 | 100 | 906 |
| paint withdrawals per game | 6 | 113 |
| robot deaths per game | 22 (20 at 0 paint) | 13 |
| spawns, r100-199 | 6 | 17 |
| spawns, r200-299 | 4 | 26 |
| towers by r100 / r200 | 2 / 3 | 4 / 8 |
| SRPs completed per game | 0 | 10 (first at a median r87) |
| SRPs active at r200 | 0 | 2 |
| our towers lost per game | 3 | 0 (they lost 1 tower in 21 games) |
| enemy units near our starting towers by r100 | 4 (first at r24) | 1 |
| soldier attacks | 21 | 91 |
| mop swings | 6 | 140 |
| paint moppers drained from enemy robots | 130 | 915 |
| moppers alive at r200 | 1 | 9 |
| tower upgrades | 1 | 3 |

**Ranked hypotheses, each turned into a build:**
1. Paint starvation: towers run dry and units die at 0 paint. Build: **sw04**.
2. Slow tower claiming, while far ruins go to them. Build: open with more soldiers (**y06** is a partial test).
3. Their early tower rushes, with nothing similar from us. Build: **sw05**.
4. Too few moppers. Build: **sw06**.
5. No SRPs and few paint-tower upgrades. Build: SRP v3, which waits on fix 1.

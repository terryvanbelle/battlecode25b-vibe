# Field study 2 (2026-11-25): the siege bot vs the top field, 12 lost games

**The bot studied:**
- Soldiers and splashers siege enemy towers.
- 3 of every 6 spawns are moppers.
- Moppers defend our towers (sw17 / y25 lineage).

**Games:**
- Lost: matches 608 (old-but-gold), 609 (just-woke-up), 610 (confused) and 611 (om-nom). That is 12 games, all lost.
- Contrast: matches 642, 593, 546 and 521. Of these 12 games we won 10.
- Replays only; no competitor code was read.

**Scripts:**
- `an.py`..`an5.py` and `rep.py` are the study 1 scripts with the match ids changed.
- `an6.py` covers spawns by type, sieges, death causes and tower counts.
- `an7.py` covers why marked ruins fail.
- `an8.py` covers how sieges go.

**Outputs:** `rep.txt`, `rep2.txt`, `an6.txt`, `an7.txt` and `an8.txt`. `*_study1.txt` are the new scripts run on study 1's replays.

**Rebuilding the dumps (not kept):**
1. `java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv ~/projects/vibe/bc25b-galaxy-replays/M/replay.bc25 DIR/mM`
2. `DUMP=DIR python3 -I an.py` (the same for an2-an5), then `python3 -I an6.py DIR`.

**Losses:**
- 7 by MAJORITY_PAINTED (median r253).
- 5 by ALL_UNITS_DESTROYED (median r205): all 3 games against confused, plus 608 g2 and 611 g2.
- The median loss lasts 252 rounds (study 1: 354).

**Coverage, painted tiles (median, us vs them):**

| round | us | them | note |
|---|---|---|---|
| r50 | 288 | 202 | we lead |
| r100 | 308 | 321 | about even |
| r150 | 279 | 438 | |
| r200 | 256 | 717 | |
| r300 | 264 | 1295 | |

Our coverage peaks around r104; theirs keeps rising.

## Medians across the 12 lost games (study 1, 21 lost games, for comparison)

| metric | us | them | study 1: us vs them |
|---|---|---|---|
| games where we never built a tower | **4 of 12** | 0 | 0 of 21 |
| towers built by r100 / r200 | 3 / 4.5 | 4.5 / 9 | 2 / 3 vs 4 / 8 |
| towers alive at r100 / r200 | 3 / 2 | 6 / 9 | 3 / 3 vs 6 / 10 |
| our towers lost per game | 4 (first at r74) | 0 (they lost 8 in 12 games) | 3 (first at r115) vs 0 |
| tower upgrades | 0 | 1 | 1 vs 3 |
| SRPs completed | 0 (0 in all 24 games) | 13 (first at r97) | 0 vs 10 |
| paint in towers at r50 / r100 / r200 | 436 / 276 / 129 | 930 / 813 / 396 | 100 / 255 / 256 vs 906 / 722 / 504 |
| chips banked at r150 / r300 | 1870 / 3175 | 2106 / 2471 | 1560 / 3125 |
| withdrawals from towers | 8 | 69 | 6 vs 113 |
| soldier turns below 20 paint (to r200) | 26% | 3% | 27% vs 5% |
| robot deaths (at 0 paint) | 15.5 (15) | 6.5 (5) | 22 (20) vs 13 (8) |
| spawns r0-99 / r100-199 / r200-299 | 12.5 / 5 / **0** | 13.5 / 17 / 39 | 13 / 6 / 4 vs 14 / 17 / 26 |
| spawned soldier / splasher / mopper | 13.5 / 1 / 3.5 | 23 / 12 / 18.5 | 15 / 5 / 6 vs 28 / 17 / 26 |
| moppers alive at r100 / r200 | 1 / 1 | 2.5 / 9 | 1 / 1 vs 3 / 9 |
| our moppers within r²20 of a falling tower | 0.1 | - | 0.1 |
| soldier attacks on enemy towers | 26.5 | 92.5 | 21 vs 91 |
| sieges / that killed a tower (all 12 games) | 47 / 7 (15%) | 131 / 55 (42%) | 158 / 1 vs 225 / 79 |
| our sieges with a single attacker | 68% | 61% | 83% |
| sieges with 3+ attackers that killed | 2 of 3 | 91% | |

## What changed since study 1

**Better:**
- Tower paint at r50 is 436, up from 100.
- Towers built by r100 / r200 rose from 2 / 3 to 3 / 4.5.
- 15% of our sieges now kill a tower (study 1: 1%).
- The first enemy unit reaches our towers at r44 (study 1: r24).

**Unchanged:**
- Starvation: 15 of our 15.5 deaths happen at 0 paint, and we withdraw 8 times to their 69.
- No SRPs.
- Few moppers, and they are not at the towers that fall.

**Worse:**
- In 4 of 12 games we never built a tower: 608 g2, 609 g1, 610 g2 and 611 g2.
- Spawning stops after r100 while 2000-5000 chips sit unused.
- We lose 4 towers per game, and sooner.
- Splashers nearly vanished: 1 per game, none before r100.
- 0 upgrades per game.

## How a loss happens

1. We open with 5-9 soldiers.
2. The spawning towers drop to 100-200 paint, so soldiers can't refill there.
3. Marked ruins stall at about 15 of 24 tiles with no enemy paint on them; the builders run dry.
4. With no new tower, we spawn one soldier every 40 rounds from 5 paint per turn, while chips pile up.
5. Their sieges of 2+ soldiers take our towers.
6. We are left with 1 paint tower and no SRPs, and spawning reaches 0 by r200.

## Ranked hypotheses, each with a code change

1. **Opening paint bankruptcy: no first tower in 4 of 12 games.**
   - (a) Cap the opening at 4 soldiers until the first new tower stands, and keep a tower paint reserve of at least 150.
   - (b) A soldier with a ruin target stops painting coverage once its paint is below the pattern's remaining need + 30.
   - (c) If a marked ruin gains no tile for 15 rounds, the soldier retargets.
2. **Spawning is limited by paint, not chips (0 spawns in r200-299, 1 paint tower, 0 upgrades).**
   - (a) Build a PAINT tower when chips are over 1500 and tower paint is under 300.
   - (b) Upgrade a paint tower to L2 once chips reach 2500.
   - (c) Build SRPs once 2+ towers stand.
3. **Towers are lost early (4 per game, first at r74), and the mopper defence misses them.**
   - (a) A damaged tower upgrades itself when chips are 2500 or more (+500 HP; in 25% of our tower deaths we held 2500+ chips).
   - (b) Keep the ring around each tower in our paint.
   - (c) Leash defending moppers to the tower nearest the enemy.
4. **Starvation (15 of 15.5 deaths at 0 paint).** A 0-paint soldier is a median 8.2 tiles from one of our towers.
   - Refill when paint is below 2 × (distance to the nearest tower) + 40.
   - This depends on fixes 1 and 2: in the won games we withdraw 80 times per game.
5. **Single-soldier sieges fail (68% have one attacker, 15% kill).**
   - (a) Attack only with 3+ attackers within r²20, or when the tower is nearly dead.
   - (b) Otherwise hold outside range and paint.
   - (c) Use splashers in sieges.
6. **No SRPs.** They multiply fix 2, and wait on fixes 1 and 2.

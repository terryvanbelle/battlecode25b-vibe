# Field study 3 (2026-11-25): the top teams' tactics, as rules we can code

**Data:**
- 33 lost games, seen from the top team's side: matches 8, 9, 10, 11, 13, 27, 28, 608, 609, 610 and 611.
- Games per team:

  | team | games |
  |---|---|
  | just-woke-up | 6 |
  | confused | 6 |
  | om-nom | 6 |
  | lobster-roll | 6 |
  | spaark | 3 |
  | podemice | 3 |
  | old-but-gold | 3 |

- Replays only; no competitor code was read.

**Scripts and outputs:**
- `lib.py` is the shared loader. Each topic has a script (`t1_spawn.py` .. `t9_explore.py`, `churn.py`) and an output (`*.txt`).
- The study 1 and 2 dumps were reused; study 2's REPORT.md says how to rebuild them.

**Caveats:**
- They were playing our weak bot, so they rarely had to defend.
- "Chips before X" means the team's money at the end of the previous round.

**Engine facts:**
- Every new tower starts with 500 paint, money towers included.
- Money towers make no paint.
- An L1 paint tower makes 5 paint per turn.
- Costs:

  | item | paint | chips |
  |---|---|---|
  | soldier | 200 | 250 |
  | splasher | 300 | 400 |
  | mopper | 100 | 300 |
  | tower | – | 1000 |
  | upgrade to L2 / L3 | – | 2500 / 5000 |

## Tactics to adopt, ranked

1. **A money-first economy with a 1000-chip reserve for the next tower.** Importance: very high.
   - Rule:
     - The first 2 new towers are MONEY, and builds 3-5 mostly money.
     - Keep a single paint tower until about 5-6 towers stand. At r200 the ratio is about 1 paint to 3-5 money.
     - Spawn only while chips are at least 1000 + the unit's cost; the exception is defensive moppers (tactic 5).
     - Keep no paint reserve in towers.
   - Evidence:
     - 33 of 33 games open with 2 money towers.
     - Spawn rate per tower-turn (when the tower has 200+ paint): 1-2% below 900 chips, 18-42% at 1100-1500 chips.
     - Paint left after a spawn: median 18-71.
     - Chips before a tower build: median about 980.
     - Median rounds of builds 1-8: 19, 37, 50, 72, 90, 116, 141, 165.
     - Each tower also brings 500 paint.
2. **Disciplined ruin building.** Importance: very high.
   - Rule:
     - Mark the pattern first.
     - Put a median of 2 builders on a ruin (p90 3-5).
     - Within 3 tiles of the ruin, paint only its pattern tiles, in the right colour.
     - Complete the tower as soon as chips reach 1000.
     - Early soldiers paint patterns, not coverage.
   - Evidence:
     - 21-24 paints per 24-tile pattern, about 100% of them the right colour and on pattern tiles.
     - First mark to completion: median 17-33 rounds.
     - Ruins that are never built are almost all single marks late in a game.
3. **Refill to full at every tower contact, and go back at about 40-50% paint.** Importance: high.
   - Rule:
     - Top up whenever adjacent to an ally tower that has paint, even small amounts (median 2-5 paint).
     - Make real return trips at 40-56% paint (soldiers).
     - Leave the tower at 100%.
   - Evidence:
     - Soldiers turn back 2-7 tiles from the tower.
     - Towers hand out everything: money towers are near 0 paint by r150.
4. **Churn towers for paint in the late game.** Importance: high once chips are banked.
   - Rule: with chips at about 3000 or more and a money tower at 0 paint with an intact pattern, disintegrate it, rebuild on the same ruin in the same round, and withdraw its fresh 500 paint.
   - Evidence: confused did this 133 times in 6 games, om-nom 66 times.
5. **Spawn cycle S → M → X per tower, with defensive moppers.** Importance: medium-high.
   - Rule:
     - With an enemy robot within d² 20 of the tower, spawn a mopper even below the reserve.
     - Splashers start once 5-7 towers stand (r74-162).
   - Mix by phase:

     | rounds | soldier | mopper | splasher |
     |---|---|---|---|
     | r1-50 | 80% | 18% | 2% |
     | r51-100 | 52% | 37% | 11% |
     | r101-200 | 37% | 41% | 22% |
     | r201+ | 29% | 32% | 39% |

6. **Kite when attacking a tower.** Importance: medium-high.
   - Rule:
     - Alternate turns ending inside and outside the tower's range.
     - Arrive with at least 100 paint.
     - 2-3 attackers that trickle in is enough; don't wait to gather.
   - Evidence:
     - About 45% of their attack turns end out of range.
     - Episodes that kill a tower: 2-3 attackers, lasting 12-18 rounds.
7. **SRPs on the x%4==2, y%4==2 lattice next to our own towers.** Importance: medium-high.
   - Rule:
     - From about r35-100, with 3-7 towers standing, put SRP centres 3-4 tiles from our towers.
     - Overlapping a standing tower's pattern is fine; never overlap an unbuilt ruin.
     - Complete even below the chip reserve.
   - Evidence:
     - 3-16 SRPs per game, 2-3.5 active at r200.
     - 99% are completed by soldiers.
     - 80% overlap a standing tower of their own; 4% overlap an unbuilt ruin.
8. **Upgrade a paint tower first.** Importance: medium.
   - Rule: at 2500+ chips with no ruin waiting.
   - Evidence: the first upgrade was a paint tower in 25 of 26 games.
9. **Splash for 5+ tiles gained; moppers as a garrison.** Importance: medium-low.
   - Splashers:
     - Splash only for at least 5 tiles gained (median 6-9).
     - Refill at 50-100 paint.
   - Moppers:
     - Stay 4.5-6 tiles from our towers.
     - Mop ruin-pattern paint first.
     - Give about 30 paint to allies below 25%.
     - They are idle on 73-93% of turns.
10. **Opening.** Importance: low.
    - Rule:
      - Both starting towers spawn a soldier on r1 and r2.
      - The paint tower spawns a 5th soldier at r10-12, once its paint is back to 200.
      - Then wait for chips.
    - Evidence: 33 of 33 games.

The topic sections with every number are in the `.txt` outputs. The study's full text was returned to the parent session and is condensed here.

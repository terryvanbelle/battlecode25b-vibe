# Battlecode 2025 (engine 3.1.0) — engine-cited rules digest

Sources: `build/src/battlecode/**` (extracted engine), `docs/specs.txt`, and
`MethodCosts.txt` / `AllowedPackages.txt` from `engine/battlecode25-java-3.1.0.jar`.
Citations are `File.java:line`. Paths are relative to `build/src/battlecode/`
(`world/`, `common/`, `server/`, `instrumenter/`, `schema/`).
Where the engine and the spec disagree, **the engine wins** (see §12).

Coordinates: (0,0) is bottom-left, +x is East, +y is North. Direction.NORTH is +y.
Squared distances are used throughout. Tiles are indexed `idx = x + y*width`
(`world/LiveMap.java:346-348`).

---

## 1. Unit stats (`common/UnitType.java:4-18`)

Constructor order is `(paintCost, moneyCost, attackCost, health, level, paintCapacity, actionCooldown, actionRadiusSquared, attackStrength, aoeAttackStrength, paintPerTurn, moneyPerTurn, attackMoneyBonus)` (`UnitType.java:96`).

| Type | paint cost | money | atk paint | HP | cap | action CD | act r² | single | AoE | paint/t | money/t | $/hit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOLDIER | 200 | 250 | 5 | 250 | 200 | 10 | 9 | 50 (towers only) | – | | | |
| SPLASHER | 300 | 400 | 50 | 150 | 300 | 50 | 4 | – | 100 (towers only) | | | |
| MOPPER | 100 | 300 | 0 | 50 | 100 | 30 | 2 | – | – | | | |
| PAINT L1/L2/L3 | 0 | 1000/2500/5000 | 0 | 1000/1500/2000 | 1000 | 10 | 9 | 20 | 10 | 5/10/15 | 0 | 0 |
| MONEY L1/L2/L3 | 0 | 1000/2500/5000 | 0 | 1000/1500/2000 | 1000 | 10 | 9 | 20 | 10 | 0 | 20/30/40 | 0 |
| DEFENSE L1/L2/L3 | 0 | 1000/2500/5000 | 0 | 2000/2500/3000 | 1000 | 10 | 16 | 40/50/60 | 20/25/30 | 0 | 0 | 20/30/40 |

* The tower "moneyCost" for L2/L3 is the **upgrade** price (`RobotControllerImpl.java:646-651`). Building a tower always costs the L1 price of 1000 (`RobotControllerImpl.java:719,736,786`).
* Vision is r²=20 for every unit, towers included (`GameConstants.java:159`, `InternalRobot.java:204-215`). There is no line-of-sight: walls do not block sensing.
* Bytecode limits: robots 17,500, towers 20,000 (`GameConstants.java:59,62`, `InternalRobot.java:78,612`).
* Starting money is 2500 per team (`GameConstants.java:83`, `GameWorld.java:99-100`).
* Hard caps: 25 towers per team (`GameConstants.java:89`), 2000 rounds (`GameConstants.java:56`), maps from 20x20 to 60x60 (`GameConstants.java:19-28`).

## 2. Round and turn order

### 2.1 Round skeleton (`world/GameWorld.java:155-187`)
1. `processBeginningOfRound()` (`GameWorld.java:820-830`):
   1. `currentRound++`. The first round is 1.
   2. `updateResourcePatterns()` (`:199-216`): re-checks every registered SRP. If the pattern is intact, its lifetime goes up by 1. If it is broken, it is deregistered and its lifetime resets to 0.
   3. For every unit (hash-map order, which does not matter here), `InternalRobot.processBeginningOfRound()` (`InternalRobot.java:591-605`):
      * Expires messages with `round <= current-5` (`:575-580`).
      * Clears the indicator string.
      * **Income.** A tower with `paintPerTurn != 0` gains `paintPerTurn + 3*activeSRPs` paint, capped at 1000. A tower with `moneyPerTurn != 0` adds `moneyPerTurn + 3*activeSRPs` to the team's money (`:595-598`). The SRP bonus is therefore paid **per paint tower and per money tower**, not once per team. Defense towers get no income and no SRP bonus.
2. `updateDynamicBodies()` runs units in **creation (spawn) order** (`ObjectInfo.java:94-110`, `dynamicBodyExecOrder.add` at `:160`).
   * The order array is snapshotted before the loop (`ObjectInfo.java:96`). A unit spawned during round R gets its first turn in round R+1. It is appended to the end, so it always runs after every older unit.
   * Units that die mid-round are skipped (`ObjectInfo.java:100`).
   * The initial towers run in the order of the map file's `initialBodies` (`GameWorld.java:132-135`). Team A does **not** necessarily go first; on many built-in maps a Team B tower is listed first (§9.3).
   * For each unit, `updateRobot` runs (`GameWorld.java:351-367`):
     1. `processBeginningOfTurn()` (`InternalRobot.java:607-614`) resets the sent-message count and the tower single/AoE attack flags, then sets **both cooldowns to `max(0, cd-10)`**. The decrement happens at the start of the unit's own turn, not "after every turn" as the spec says.
     2. Player code runs until `Clock.yield()` or until bytecode runs out.
     3. `processEndOfTurn()` (`InternalRobot.java:616-648`) applies the paint penalty (§5.3), then **−20 HP if paint == 0** (robots only, `:642-644`). After that it records the replay `Turn`.
     4. If the player thread has terminated (returned from `run`, threw an uncaught exception, or called `disintegrate`), the unit is destroyed now (`GameWorld.java:360-364`).
3. `processEndOfRound()` (`GameWorld.java:975-988`) records team money, coverage and SRP count in the replay. Then `checkEndOfMatch()` applies the tiebreakers if `round >= 2000` (`:957-973`). The game stops once a winner is set.

### 2.2 New-unit cooldowns
A new unit starts with `actionCooldown = type.actionCooldown` and `movementCooldown = 10` (`InternalRobot.java:82-83`). The first decrement happens before its first turn, so:
* Soldier: can move and act on turn 1.
* Mopper: action cooldown is 20, 10, 0, so the first action is on turn **3**.
* Splasher: action cooldown is 40, 30, 20, 10, 0, so the first attack is on turn **5**. Moving is allowed from turn 1.
* A newly built tower: 10 becomes 0, so it can build on its first turn.

### 2.3 Win conditions
* **70% paint:** `TeamInfo.addPaintedSquares` (`world/TeamInfo.java:74-80`) runs on **every `setPaint`**. It sets the winner as soon as `painted / areaWithoutWalls * 100 >= 70`.
  * `areaWithoutWalls = W*H − #walls` (`GameWorld.java:83-88`). **Ruin tiles, tower tiles included, count in the denominator but can never be painted**, so the real threshold is a little above 70% of the paintable tiles.
  * Both of a team's colours count toward its total.
  * The comparison is `>=`, not "more than" as the spec says.
  * Example: 20x20 with 28 walls gives an area of 372, so 261 tiles are needed (260 is 69.9%).
* The win check fires mid-turn, but the round still finishes (`running=false` only at end of round, `GameWorld.java:986-987`). `setWinner` overwrites, so **the last event in the round wins**. For example, if A crosses 70% and B crosses 70% later in the same round, B wins. A team losing its last unit later in that round also overrides. Painting back below 70% does not unset the winner.
* **Destroy all units:** `currentNumberUnits` counts robots plus towers. It is decremented in `destroyRobot`; at 0, the opponent wins with `DESTROY_ALL_UNITS` (`GameWorld.java:1067-1070`).
* **Tiebreak after round 2000** (`GameWorld.java:964-973`), in this order:
  1. Raw count of painted tiles (`:840-856`).
  2. Number of towers alive (`:881-899`).
  3. Money (`:861-876`).
  4. Total paint stored in all robots and towers (`:928-947`).
  5. Number of robots alive (`:905-923`).
  6. `Math.random()` (`:953-955`). This is **unseeded**, so the coin flip is nondeterministic.
* **Resign:** destroys all of your units, then sets the opponent as winner with `RESIGNATION` (`RobotControllerImpl.java:1147-1157`).
* **Execution-time limit:** `MAX_TEAM_EXECUTION_TIME = 1.2e12 ns` (1200 s, i.e. 20 min) per team per match (`GameConstants.java:95`).
  * It is accumulated as wall-clock `System.nanoTime()` around each `player.step()`.
  * Once over the limit, the team auto-resigns in the middle of the round (`world/control/PlayerControlProvider.java:185-200`).
  * The timer resets each match (`:133`). `Clock.getTimeLeft()` and `Clock.getTimeElapsed()` expose it.

## 3. Cooldowns and low-paint multiplier

* An action needs `actionCooldown < 10`; a move needs `movementCooldown < 10` (`InternalRobot.java:190-199`, `GameConstants.java:218`).
* **A robot with 0 paint can neither act nor move** (`RobotControllerImpl.java:380-411`). This includes `transferPaint`, so **a 0-paint robot cannot withdraw from a tower**. Only a mopper can save it.
  * Things that need no action-readiness still work at 0 paint: mark, complete patterns, upgrade, messages, disintegrate.
  * Towers are never blocked by paint.
* Multiplier for robots only (`InternalRobot.java:264-286`):
  ```
  pct = (int) Math.round(paint*100.0 / capacity)
  if pct < 50:  cd += (int) Math.round(cd * (100 - 2*pct) / 100.0)
  ```
  * The paint value used is the robot's paint **at the moment of the call**:
    * `attack`: before the paint cost is deducted (`RobotControllerImpl.java:937-939`).
    * `transferPaint`: after the transfer (`:1135-1138`).
    * `move`: before moving (`:463-464`).
  * Example: a soldier at 40/200 paint (20%) moves with cooldown 10+6=16. Its cooldowns then go 16, 6 (can move again), 22, 12, 2, and so on, which works out to 2 moves per 3 turns.
* Base cooldowns:

  | Action | Cooldown | Source |
  |---|---|---|
  | move | 10 | `GameConstants.java:226` |
  | buildRobot | 10 | `:231` |
  | mopSwing | 20 | `:234` |
  | transferPaint | 10 | `:237` |
  | soldier attack | 10 | `RobotControllerImpl.java:937-938`, `UnitType.actionCooldown` |
  | splasher attack | 50 | same |
  | mopper attack | 30 | same |

* Towers' `attack` adds **no cooldown** and ignores `isActionReady` (`RobotControllerImpl.java:889-900,937`). A tower can build one robot **and** do one single attack **and** one AoE attack in the same turn.
* Cooldown debt carries over: there is no cap, and it only drops by 10 per turn.

## 4. RobotController API (preconditions and gotchas)

"Act radius" means `dist² <= r²` from the caller plus the location being on the map (`RobotControllerImpl.java:191-199`). Every `canX` is the matching `assertCanX` wrapped in try/catch.

### 4.1 attack(loc[, useSecondaryColor]) — `RobotControllerImpl.java:902-945`, `InternalRobot.java:327-464`
* **Soldier** (r²=9, 5 paint, cd 10, `:861-869`)
  * Rejects walls only. It **can target a ruin, enemy paint, or an occupied tile**, and the 5 paint and cooldown are still spent.
  * If an **enemy tower** stands on the tile, the tower takes 50 damage and no painting happens. An allied tower on the tile means nothing happens (`InternalRobot.java:336-342`).
  * Otherwise the tile is painted only if it is paintable and is **empty or already our paint**. Repainting our own primary to secondary (or back) is allowed (`:345-349`). **A soldier cannot paint over enemy paint**; such an attack silently does nothing.
  * `canPaint(loc)` checks this (`RobotControllerImpl.java:849-853`). `canAttack` does not.
* **Splasher** (centre within r²=4, 50 paint, cd 50, `:871-877`)
  * There is no passability check, so the centre may be a wall.
  * Every tile within **r²=4 of the centre** (13 tiles) is processed (`InternalRobot.java:366-388`):
    * An enemy tower on the tile takes 100 damage.
    * A paintable tile that is empty or ours is painted.
    * A tile with **enemy paint is overwritten only within r²=2 of the centre** (the inner 3x3, `GameConstants.java:211`).
  * Robots on the tiles take no damage.
* **Mopper** (r²=2, 0 paint, cd 30, `:879-887`)
  * The target must be passable, so a mopper cannot target a wall, a ruin, or a tower tile.
  * An **enemy robot** on the tile loses 10 paint and the mopper gains 5 (`InternalRobot.java:404-412`). The robot takes no HP damage.
  * Any non-ally paint on the tile is cleared to empty (`:415-418`).
  * `useSecondaryColor` is irrelevant for moppers.
* **Tower** (r² = its `actionRadiusSquared`)
  * **The player must call these; nothing happens automatically.**
  * `attack(loc)` is the single-target attack: once per turn, it hits any non-allied unit on `loc` for `attackStrength + defenseBuff` (`InternalRobot.java:448-460`). The flag is consumed even if the tile is empty.
  * `attack(null)` is the AoE: once per turn, it hits every enemy unit within the tower's action radius for `aoeAttackStrength + round(buff*0/100)`. Because `DEFENSE_ATTACK_BUFF_AOE_EFFECTIVENESS = 0` (`GameConstants.java:141`, `InternalRobot.java:430-447`), **the buff never applies to AoE**.
  * Neither attack costs paint or adds cooldown.
  * `attackMoneyBonus` (defense towers only: 20/30/40) is added **once per attack call that hits at least one robot** (`:461-463`). Using both attacks can earn it twice per turn.
* Robots deal HP damage **only to towers**. Only towers deal HP damage to robots, apart from the 0-paint drain.

### 4.2 mopSwing(dir) — `RobotControllerImpl.java:947-976`, `InternalRobot.java:477-511`
* Mopper only. The direction must be one of the 4 cardinals. The adjacent tile in that direction must be on the map. Needs action readiness. Cooldown 20, no paint cost.
* It affects the 3 tiles one step in the direction (centre and both diagonals) and the 3 tiles two steps out. For example, NORTH hits dx∈{-1,0,1} at dy=+1 and dy=+2.
* Each **enemy robot** there loses 5 paint. The mopper gains nothing. **Tiles are not mopped.**

### 4.3 transferPaint(loc, amount) — `RobotControllerImpl.java:1091-1140`
* The caller must be a robot (towers cannot transfer). The target must be within r²=2, allied, and not the caller. Needs action readiness, so it **fails at 0 paint**. `amount != 0`.
* `amount > 0` gives paint. **Only moppers** can give, and they can give to robots or towers.
* `amount < 0` withdraws. **Any robot** can withdraw, but only from a **tower** of any kind; money and defense towers also hold paint. The amount must not exceed the tower's paint.
* Cooldown 10, with the multiplier applied using paint *after* the transfer.
* **Gotcha:** the receiving side is clamped to its capacity (`InternalRobot.java:130-139`) while the giver loses the full amount. Over-withdrawing or over-giving **destroys the excess paint**.

### 4.4 buildRobot(type, loc) — `RobotControllerImpl.java:483-527`
* Caller must be a tower; type must be a robot type. Target within r²=4 (`GameConstants.java:168`), on the map, unoccupied, passable. Needs action readiness.
* The tower needs paint ≥ `paintCost` and the team needs money ≥ `moneyCost`. Cooldown is +10, so a tower builds at most **one robot per turn**.
* The new robot starts with **full paint** (`GameWorld.java:1017`) and first acts next round.
* New IDs come from a shuffled block of 10001..14096 seeded by the **map seed** (`world/IDGenerator.java:19-56`), so ID sequences are deterministic per map.

### 4.5 Marks — `RobotControllerImpl.java:529-575`, `GameWorld.java:455-468`
* `mark(loc, secondary)` and `removeMark(loc)`: robot only, r²=2 (`GameConstants.java:162`), target must be paintable (no wall or ruin).
* **No paint cost, no cooldown, no per-turn limit.** The spec's "1 paint" is not implemented.
* `removeMark` requires an existing mark of our team.
* Marks are stored per team (`markersA` and `markersB`), so the enemy never sees them. `MapInfo.getMark()` returns ALLY_PRIMARY, ALLY_SECONDARY or EMPTY (`RobotControllerImpl.java:78-88`).
* Marks have no effect on game rules. They do appear in the replay.

### 4.6 markTowerPattern(type, loc) / markResourcePattern(loc) — `RobotControllerImpl.java:577-621, 679-716`
* Robot only. Costs **25 paint** and needs paint ≥ 25 (`GameConstants.java:123`). No cooldown.
* Tower: `loc` must be a ruin within **r²=2** and the 5x5 must fit on the map. The ruin may already hold a tower, in which case the 25 paint is wasted.
* SRP: `loc` within **r²=8**, the 5x5 fits, and it contains **no walls or ruins** (`GameWorld.java:594-612`).
* Writes marks (1 = primary, 2 = secondary) on every paintable tile of the 5x5 and overwrites existing marks (`GameWorld.java:470-519`).
* The rotation and reflection parameters exist only on the `RobotControllerImpl` overload, not on the interface. They are ignored because all patterns are D4-symmetric.

### 4.7 completeTowerPattern(type, loc) — `RobotControllerImpl.java:718-789`
* `type` is reduced to its base (L1) type. Robot only. The ruin must be within **r²=2** of the robot, i.e. **the robot must be adjacent** (8-neighbourhood).
* The ruin must have no tower. The team needs ≥ 1000 money. The 5x5 must fit, the centre must be unoccupied, and the pattern must match (§6). The team must have < 25 towers.
* **No paint, no action cooldown, and no paint > 0 required.**
* Effect:
  * Spawns an L1 tower with **500 paint** (`GameWorld.java:1012-1015`). Completing any tower gives you a fresh 500-paint stockpile.
  * Costs 1000 money.
  * A new L1 defense tower adds +5 to the team buff (`GameWorld.java:1018-1019`).
  * The new tower acts next round.

### 4.8 completeResourcePattern(loc) — `RobotControllerImpl.java:791-834`
* Robot only. The centre must be within **r²=8**, so it does not need to be adjacent: any tile of the 5x5 works.
* Needs 200 money (`GameConstants.java:126`). The centre must not already be registered for our team. The 5x5 must be valid (no walls or ruins) and the pattern must match.
* No paint and no cooldown. Registers the centre with lifetime 0 (`GameWorld.java:340-349`).

### 4.9 upgradeTower(loc) — `RobotControllerImpl.java:623-677`, `InternalRobot.java:255-259`
* The target must be an allied tower at level < 3 within **r²=2 of the caller**. The team needs the next level's `moneyCost` (2500 for L2, 5000 for L3).
* **The caller can be a robot or a tower, and a tower can upgrade itself** (distance 0 ≤ 2). There is no robot-type check, no cooldown and no paint requirement, and nothing stops two upgrades in one turn (L1 straight to L3).
* Damage taken is preserved: `newHP = newMax − (oldMax − oldHP)`. Paint is unchanged.
* Upgrading a defense tower adds +2 to the team buff (`GameWorld.java:567-570`).

### 4.10 Messages — `RobotControllerImpl.java:982-1085`, `InternalRobot.java:544-580`
* `sendMessage(loc, int)` is allowed only between a robot and a tower, in either direction. Robot↔robot and tower↔tower are rejected.
  * Same team, target within **r²=20** of the sender.
  * Limits: robots send 1 message per turn, towers 20 per turn (`GameConstants.java:199-202`).
  * The two units must be **connected by paint** (`GameWorld.java:744-763`):
    * The robot's own tile must carry the robot team's paint, primary or secondary.
    * A BFS over 4-connected (no diagonals) tiles with our paint must reach the tower tile. The tower tile itself is unpainted; it is accepted as soon as it is dequeued.
    * The BFS is **unbounded** (it can walk the whole map) but is charged a flat 50 bytecodes.
* The message arrives **instantly** in the recipient's queue. A recipient that runs later in the same round can read it that round.
* `broadcastMessage(int)`: tower only. Reaches every allied tower within **r²=80**, with no paint connection needed. It counts as 1 toward the tower's 20 messages.
* `readMessages(round)`: `-1` returns all queued messages. A message from round r is readable in rounds r..r+4 and is purged at the start of round r+5. A `Message` carries the int, the sender ID and the round.

### 4.11 Sensing — `RobotControllerImpl.java:173-374`
* `canSenseLocation(loc)`: on the map and `dist² <= 20` from the caller.
* `senseNearbyRobots(r)`, `senseNearbyMapInfos(r)`, `senseNearbyRuins(r)`, `getAllLocationsWithinRadiusSquared(c, r)`:
  * `r = -1` means 20; otherwise `min(r, 20)`. `r < -1` throws.
  * The `center` overloads still filter by the caller's own vision.
  * `senseNearbyRobots` excludes the caller.
* `senseNearbyRuins` returns **all ruins, including those under towers**. `MapInfo.hasRuin()` is also true under a tower (`GameWorld.java:138`).
* `MapInfo.isResourcePatternCenter()` means "registered by **our** team". It is true from the moment `completeResourcePattern` succeeds, **before** the 50 rounds have passed. It becomes false after the start-of-round check finds the pattern broken.
* `getNumberTowers()` is the team's live tower count (`RobotControllerImpl.java:164-167`, `TeamInfo.java:65`).

### 4.12 Misc
* `disintegrate()` throws `RobotDeathException`. The unit is destroyed **after** its end-of-turn processing, and the replay records it in `diedIds` (`RobotControllerImpl.java:1142-1145`, `GameWorld.java:360-364`).
* `resign()`: see §2.3.
* `setIndicatorString`: truncated to 256 characters (`GameConstants.java:68`). The last value of the turn is kept. A null argument throws NPE.
* `setIndicatorDot` and `setIndicatorLine` throw if a location is off the map.
* `setTimelineMarker(label, r, g, b)`: truncated to 64 characters, stored per team and round in the MatchFooter (`RobotControllerImpl.java:1190-1196`). Indicators are dropped when `showIndicators` is off.
* `getResourcePattern()` and `getTowerPattern(t)` return `boolean[5][5]` indexed **[dx+2][dy+2]** (x first), with `true` meaning secondary (`GameWorld.java:237-245`).
* **Uncaught exception or returning from `run()`:** the player thread terminates and **the unit is destroyed** at the end of that turn (`instrumenter/SandboxedRobotPlayer.java:177-226`, `GameWorld.java:360-364`). This applies to towers too.
* `Math.random` and `new Random()` are seeded with the robot's **ID** (`PlayerControlProvider.java:144-152`, `SandboxedRobotPlayer.java:112-119,180`), so runs are deterministic.

## 5. Paint rules

### 5.1 Paint encoding (`GameWorld.java:35,634-664`)
| Value | Meaning |
|---|---|
| 0 | empty |
| 1 | Team A primary |
| 2 | Team A secondary |
| 3 | Team B primary |
| 4 | Team B secondary |

* Walls and ruins are never paintable; `setPaint` ignores them (`:433-442,614-620`).
* Paint is **not** removed from tiles when units die.

### 5.2 What paints and what removes paint
| Source | Can paint | Removes enemy paint |
|---|---|---|
| Soldier | 1 tile: empty or own | no |
| Splasher | up to 13 tiles in r²=4: empty or own | yes, overwrites with own colour within r²=2 of the centre |
| Mopper attack | – | yes, sets the tile to empty (1 tile) |
| mopSwing | – | no |

### 5.3 End-of-turn paint penalty (robots only, `InternalRobot.java:622-640`)
```
owning   = team of paint under the robot
mult     = (MOPPER ? 2 : 1)
allies   = # allied UNITS (robots AND towers) within r²=2, excluding self
neutral : paint -= 1*mult + allies
enemy   : paint -= 2*mult + 2*allies
own     : paint -= allies
then if paint == 0 : HP -= 20
```
* **Allied towers count as adjacent allies**, so waiting next to your own tower to refill costs 1 paint per turn.
* The mopper multiplier applies only to the base term, not to the adjacency term.
* A robot with 1 paint ending its turn on neutral ground drops to 0 and takes 20 damage on that same turn.

## 6. Patterns

### 6.1 Encoding and matching
* Bit index = `5*(dx+2) + (dy+2)`, where dx is the x offset (`GameWorld.java:230-235`). Bit 1 means **secondary**, bit 0 means **primary**.
* `checkPattern` (`GameWorld.java:255-332`) needs **every** tile of the 5x5 to carry exactly our primary or secondary as specified. Empty, enemy or wrong-colour paint fails. The centre is skipped for tower patterns (it is the ruin).
* Marks are irrelevant to the check.
* There is no rotation or reflection search (that code is commented out), and none is needed: all four patterns are invariant under 90° rotation and both reflections, which I verified.
* The pattern ints stored in a map file are ignored; the engine always uses the hard-coded constants (`GameWorld.java:43,113-114`).

### 6.2 Grids (`GameConstants.java:37-46`)
`S` = secondary, `P` = primary, `.` = ruin (ignored). Rows run from dy=+2 (north, top) to dy=−2; columns run from dx=−2 to +2.
```
RESOURCE_PATTERN 28873275   PAINT_TOWER 18157905   MONEY_TOWER 15583086   DEFENSE_TOWER 4685252
  S S P S S                   S P P P S              P S S S P              P P S P P
  S P P P S                   P S P S P              S S P S S              P S S S P
  P P S P P                   P P . P P              S P . P S              S S . S S
  S P P P S                   P S P S P              S S P S S              P S S S P
  S S P S S                   S P P P S              P S S S P              P P S P P
```
(The SRP centre is S. The centre bits of the tower patterns are S, P and S, but they are ignored.)

### 6.3 SRP lifecycle
* `completeResourcePattern` in round R sets lifetime 0. Each round start where the pattern is intact adds 1. The SRP is **active when lifetime ≥ 50** (`GameWorld.java:549-561`, `GameConstants.java:132`).
* Activity is evaluated before income in the same `processBeginningOfRound`, so **the first bonus is paid at the start of round R+50**.
* **"Disturbed"** means any of the 25 tiles is not the exact required colour at a round-start check: enemy paint, mopped to empty, our other colour, or a tile the enemy splashed. On failure the SRP is **deregistered entirely**. You must repaint it, call `complete...` again, pay another 200, and wait another 50 rounds.
* The check runs **only at round start**. A disturbance that is repaired later in the same round goes unnoticed. That requires your fixer to act after the enemy in exec order.
* Bonus: +3 per active SRP to **each** paint tower's paint and **each** money tower's money every round (§2.1). Example: with 4 money towers, one SRP is worth +12 money per round.
* Overlap: nothing forbids SRPs sharing tiles, or sharing tiles with tower 5x5s, as long as the colours agree. Each SRP needs its own 5x5 free of walls and ruins.
* The enemy cannot see your SRP registrations. They can register their own centre at the same location once the tiles hold their colours.

## 7. Towers

* **Destroying a tower** (`GameWorld.java:1040-1071`): the tower is removed and the team's tower count goes down. The **ruin remains** because `allRuinsByLoc` is never cleared, and the surrounding paint stays.
  * Either team can rebuild on that ruin by painting the pattern in its own colours and completing it.
  * Defense buff is removed: −5 for L1, −7 for L2, −9 for L3.
* **Defense buff** (`GameWorld.java:563-570,1018-1019`): the team-wide sum is +5 per L1 defense tower, +2 more for each upgrade level. It is added to the **single-target** attack of **every** allied tower and **stacks with no cap**. For example, three L1 defense towers give every tower +15 single-target damage.
* **Initial towers:** each team gets one paint tower and one money tower, spawned at L1 with 500 paint and then **upgraded to L2** at construction (`GameWorld.java:141-146`).
  * In practice that is L2 HP 1500, 10 paint/turn and 30 money/turn.
  * Round-1 income is paid before any turn, so the first turn sees 2530 money and 510 tower paint.
  * Their IDs come from the map file and are **small numbers (0–16)**, not ≥ 10000 as the spec claims.
* **Tower limit:** 25 live towers (`RobotControllerImpl.java:763-767`).
* Every tower can hold 1000 paint. Money and defense towers start with 500 paint and never regenerate it, but robots can still withdraw it.

## 8. Bytecode accounting

* **Limits:** 17,500 for robots, 20,000 for towers.
* **Overrun:** if code exceeds the limit, the thread pauses mid-code and resumes next turn. The overrun is **debt**: `bytecodesLeft += limit` on resume when it is negative (`instrumenter/inject/RobotMonitor.java:148-175,319-330`). Unused bytecodes do not carry over. `Clock.yield()` costs 0.
* **Exceptions:** +500 bytecodes each time control enters a `catch` handler in player code (`instrumenter/bytecode/InstrumentingMethodVisitor.java:641-645`, `GameConstants.java:74`).
  * The engine's own `canX` try/catch is not instrumented, so `canX` costs only its listed price.
* **Arrays:** `NEWARRAY` and `ANEWARRAY` add `max(1, length)` (`InstrumentingMethodVisitor.java:647-676`). `MULTIANEWARRAY` adds the product of the dimensions (each at least 1) (`:603-639`, `RobotMonitor.java:230-237`).
* **Library code:** `java.util`, `java.math` and scala are instrumented as if they were your code. Other listed methods have the fixed cost in `MethodCosts.txt`; unlisted methods are free (spec §"More information").
* **Allowed packages:** java.io, java.lang(.invoke), java.math, java.util(.function, .regex, .stream), java.text, battlecode.common, scala.*. Direct calls into `java/lang/invoke` are rejected (`InstrumentingMethodVisitor.java:597-600`).
* `debug_*` void methods are free and are stripped when debug methods are disabled (`InstrumentingMethodVisitor.java:29,164,505`).

Fixed RobotController costs (`MethodCosts.txt`):
| Cost | Methods |
|---|---|
| 0 | attack, mopSwing, move, upgradeTower, disintegrate, resign, setIndicator*, setTimelineMarker, Clock.* |
| 1 | getID/Team/Location/Health/Paint/Money/Chips/Type/RoundNum/MapWidth/MapHeight, isActionReady, isMovementReady, get*CooldownTurns, adjacentLocation |
| 2 | getResourcePattern, getTowerPattern, canUpgradeTower |
| 5 | canSenseLocation, canSenseRobot, canSenseRobotAtLocation, isLocationOccupied, onTheMap, sensePassability, **senseMapInfo**, getNumberTowers, canMark, mark, canRemoveMark, removeMark, canTransferPaint, transferPaint, canBroadcastMessage |
| 10 | canMove, canAttack, canPaint, canMopSwing, canBuildRobot, readMessages |
| 15 | senseRobotAtLocation |
| 20 | buildRobot |
| 25 | senseRobot |
| 50 | canSendMessage, sendMessage, broadcastMessage, can/markTowerPattern, can/markResourcePattern, can/completeTowerPattern, can/completeResourcePattern |
| 100 | senseNearbyRobots, senseNearbyMapInfos, senseNearbyRuins, getAllLocationsWithinRadiusSquared |

* MapLocation methods cost 2 each, except `valueOf` at 25.
* Direction methods cost 1. MapInfo getters cost 1–2 (`toString` 15).
* RobotInfo getters cost 1–2; `equals`, `hashCode` and `toString` cost 15.
* UnitType predicates cost 3.
* Message getters cost 3.
* A stale `readSharedArray` entry (cost 2) is still listed but the method does not exist.
* Tip: `senseMapInfo(loc)` costs 5 per tile versus 100 for the whole r²=20 disc (69 tiles), so the disc is cheaper only when you need about 20 or more tiles.

## 9. Maps

### 9.1 Guarantees (`world/LiveMap.java:360-441`; enforced only when map guarantees are checked, `server/Server.java:264`)
* Size between 20 and 60 in each dimension.
* Walls must be **under 20%** (`numWalls*100 >= W*H*20` is rejected, `:422`).
* No wall on a ruin.
* Ruins pairwise `dist² >= 25` (`:426-432`).
* **No wall within dist² ≤ 8 of any ruin**, so every ruin's 5x5 is wall-free (`:434-441`).
* Exactly 2 initial towers per team: 1 paint and 1 money, with equal type counts per team (`:377-409`).
* Initial towers sit on ruins (`GameWorld.java:138`).
* Symmetry is declared in the file but not validated.

### 9.2 Symmetry (`world/MapSymmetry.java`)
The ordinal is stored in `GameMap.symmetry`. I checked the meanings against the wall and ruin data of all built-in maps:

| Ordinal | Name | Mapping |
|---|---|---|
| 0 | ROTATIONAL | (x,y) → (W−1−x, H−1−y) |
| 1 | HORIZONTAL | (x,y) → (x, H−1−y), i.e. flip y |
| 2 | VERTICAL | (x,y) → (W−1−x, y), i.e. flip x |

* All 75 built-in maps match their declared symmetry for walls and ruins.
* Initial paint is mirrored with team swap (1↔3, 2↔4) on every map except **Parking_lot**: the counts are equal but the placement is not mirrored.

### 9.3 `.map25` format (`world/GameMapIO.java:187-345`)
The file is a raw, **uncompressed** FlatBuffer whose root table is `schema.GameMap`. The table has 9 fields:

| Slot | Field | Type / notes |
|---|---|---|
| 0 | name | string; must equal the file name |
| 1 | size | struct Vec{int x, int y} |
| 2 | symmetry | int |
| 3 | initialBodies | InitialBodyTable{spawnActions: [struct SpawnAction]} |
| 4 | randomSeed | int; seeds the ID generator |
| 5 | walls | [bool], W*H, idx = x + y*W |
| 6 | paint | [byte], W*H, values 0–4 |
| 7 | ruins | VecTable{xs:[int], ys:[int]}; includes the initial tower tiles |
| 8 | paintPatterns | [int]; ignored by the engine and empty in the shipped maps |

* `SpawnAction` is an 8-byte struct: `u16 id, u16 x, u16 y, i8 team (1=A, 2=B), i8 robotType`. Robot types are 1=PAINT_TOWER, 2=MONEY_TOWER, 3=DEFENSE_TOWER, 4=SOLDIER, 5=SPLASHER, 6=MOPPER (`schema/RobotType.java`).
* The **order of `initialBodies` is the turn order** of the initial towers.
* In the second game of an alternating pair, teams are swapped (`teamsReversed`, `server/Server.java:178-183`). Paint is swapped 1↔3 and 2↔4 and body teams are flipped (`GameMapIO.java:351-380`), but the body order is unchanged.
* Tower turn order differs between maps: some list Team A's towers first and others list Team B's first. Examples are AlarmClock, DefaultSmall and DefaultHuge.

### 9.4 Built-in maps in the 3.1.0 jar (75, not 50)
Format: name, size, symmetry (R/H/V), wall %, ruin count.
```
AlarmClock 35x35 H 10.9% 16     Barcode 50x21 V 8.0% 18       BatSignal 40x25 V 11.0% 10
box 31x31 H 13.7% 8             boxofchocolates 55x55 R 19.5% 15  Brat 29x29 H 15.0% 11
Bread 35x29 V 10.0% 12          Bunny 44x30 V 7.0% 16         BunnyGame 30x50 V 14.3% 12
Castle 27x27 V 12.8% 10         CastleDefense 20x20 R 15.0% 6 catface 30x30 V 3.6% 6
Circuit 60x21 H 13.0% 14        Crab 40x30 V 12.8% 14         DefaultHuge 59x59 H 1.7% 49
DefaultLarge 50x30 V 1.6% 20    DefaultMedium 35x35 V 2.6% 19 DefaultSmall 20x20 R 7.0% 8
defensetower 40x59 H 7.9% 18    Dominoes 44x30 V 7.0% 20      DonkeyKong 60x60 H 10.2% 46
Filter 21x21 H 5.0% 5           fix 40x50 H 7.2% 24           Flower 45x41 V 12.0% 12
Fossil 30x30 H 3.6% 14          FourCorners 25x25 H 13.3% 10  galaxy 45x45 R 9.4% 24
gardenworld 60x60 R 11.7% 22    Gears 55x55 H 4.6% 14         giver 50x50 R 6.2% 26
gridworld 31x31 R 20.0%* 21     headphones 60x60 V 11.5% 32   HungerGames 50x50 R 9.7% 26
Jail 20x30 V 10.0% 8            Justice 21x20 V 7.4% 8        Leaf 60x60 V 4.4% 52
leavemealone 50x30 V 9.1% 14    lighthouse 31x31 V 11.2% 11   maze 60x60 V 19.8% 28
memstore 59x39 V 9.6% 26        Mirage 40x40 V 7.5% 18        mit 60x60 V 16.3% 24
Money 35x35 R 6.9% 20           MoneyTower 35x50 V 14.2% 10   Oasis 59x59 R 4.1% 24
Paintball 20x20 R 11.5% 8       Parking_lot 45x45 H 11.4% 23  Piglets2 60x40 V 15.3% 20
PlumberGame 60x30 V 6.2% 18     Portal 35x35 R 7.8% 22        quack 30x35 H 11.2% 12
Racetrack 25x25 R 10.1% 10      rain 30x30 R 5.6% 12          Restart 55x55 R 12.2% 28
roads 30x30 H 14.4% 8           Rose 40x40 R 5.5% 26          SaltyPepper 40x40 V 7.2% 20
SandyBeach 30x30 V 8.7% 16      sayhi 40x50 R 13.3% 22        shell 40x40 V 11.4% 20
sierpinski 39x50 H 16.9% 16     SMILE 60x60 V 3.3% 38         Snowglobe 40x40 V 7.6% 20
Snowman 25x25 V 11.5% 6         starburst 30x30 R 6.2% 8      sunrise 45x55 V 10.8% 17
TargetPractice 30x30 V 9.3% 12  Terminal 40x30 R 14.8% 12     TheBest 60x60 H 8.6% 44
Thirds 55x40 H 12.2% 22         UglySweater 50x50 R 6.4% 28   UnderTheSea 45x45 H 8.8% 23
walalilongla 45x45 R 10.6% 18   windmill 30x30 R 13.3% 8      yearofthesnake 45x45 R 18.4% 16
```
(*gridworld is 19.98%, just under the limit.)

* The minimum ruin spacing across all maps is exactly 25.
* Most maps start with some paint: 0 to 1450 tiles. Gears has 725 tiles per team.

## 10. Replay `.bc25` format (`server/GameMaker.java`)

* **Envelope:** a **gzip-compressed** FlatBuffer (`GameMaker.java:163-191`).
* **Root `GameWrapper`:**
  * `events: [EventWrapper]`
  * `matchHeaders: [int]` and `matchFooters: [int]`, which are indices into `events`
* **`EventWrapper`:** `{e_type: u8, e: union}`. Union tags: 1=GameHeader, 2=MatchHeader, 3=Round, 4=MatchFooter, 5=GameFooter (`schema/Event.java`).
* **Event tables** (field slot order shown):
  * `GameHeader{specVersion:"1", teams:[TeamData{name, packageName, teamId}], robotTypeMetadata:[RobotTypeMetadata{type, actionCooldown, actionRadiusSquared, baseHealth, basePaint, bytecodeLimit, maxPaint, messageRadiusSquared, movementCooldown, visionRadiusSquared}], constants:{}}`
  * `MatchHeader{map: GameMap (as in §9.3, after team reversal), maxRounds}`
  * `Round{teamIds:[int], teamResourceAmounts:[int] (money), teamCoverageAmounts:[int], teamResourcePatternAmounts:[int] (active SRPs), turns:[Turn], diedIds:[int], roundId:int}`
    * `teamCoverageAmounts` is per-mille: `round(painted*1000/areaWithoutWalls)` (`GameWorld.java:976-979`).
  * `Turn{robotId, health, paint, moveCooldown, actionCooldown, bytecodesUsed, x:u8, y:u8, actions_type:[u8], actions:[union]}`
    * One Turn is written per unit per round, in execution order, **after** end-of-turn processing (`GameMaker.java:487-501`).
    * The state is end-of-turn state: paint is after the penalty and HP after any 0-paint damage.
    * The actions in a Turn are the ones that happened while that unit ran. The actor is the Turn's `robotId`.
    * Actions emitted between turns are attached to the **next** Turn. An example is the round-1 `UpgradeAction` of the initial towers, emitted in `processBeginningOfRound` (`InternalRobot.java:601-604`; `GameMaker.java:728-749`).
  * `MatchFooter{winner:u8 (1=A, 2=B), winType:u8, totalRounds, timelineMarkers:[{team:u8 (0=A, 1=B; ordinal, not TeamMapping), round, colorHex, label}], profilerFiles}`
    * WinType values: 0=RESIGNATION, 1=MAJORITY_PAINTED (70%), 2=ALL_UNITS_DESTROYED, 3=AREA_PAINTED, 4=MORE_TOWERS, 5=MORE_MONEY, 6=MORE_STORED_PAINT, 7=MORE_ROBOTS, 8=COIN_FLIP (`util/FlatHelpers.java:77-100`).
  * `GameFooter{winner}`
* **Action union** (`schema/Action.java`). Structs unless noted. `loc` is u16 = `x + W*y`; ids are u16.

| Tag | Action | Layout | Meaning |
|---|---|---|---|
| 1 | DamageAction | {id, damage:u16} | HP damage to a tower or robot. **Also** used for paint removed by a mopper (10 or 5) (`GameMaker.java:512-526`) |
| 2 | PaintAction | {loc, isSecondary:u8} | tile painted |
| 3 | UnpaintAction | {loc} | mopper cleared the tile |
| 4 | MarkAction | {loc, isSecondary} | |
| 5 | UnmarkAction | {loc} | |
| 6 | AttackAction | {id} | target id |
| 7 | SplashAction | {loc} | splash centre |
| 8 | MopAction | {id0, id1, id2} | two per swing (6 ids, 0-padded) |
| 9 | BuildAction | {id} | tower completed; preceded by a SpawnAction |
| 10 | TransferAction | {id, amount:i32} | `amount` is as passed: positive = give, negative = withdraw. **Overloaded:** `amount == 0` means `completeResourcePattern` and `id` is then the **loc** of the SRP centre (`GameMaker.java:596-603`) |
| 11 | MessageAction | {id, data:i32} | never emitted; the call is commented out at `RobotControllerImpl.java:1041` |
| 12 | SpawnAction | {id, x, y, team, robotType} | robot built or tower completed |
| 13 | DieAction | {id, dieType:u8} | 0=UNKNOWN (killed by damage), 1=EXCEPTION (sandbox or instrumentation failure) |
| 14 | UpgradeAction | {id, newHealth, newMaxHealth, newPaint, newMaxPaint} | |
| 15 | IndicatorStringAction | table {value: string} | |
| 16 | IndicatorDotAction | {loc, colorHex} | |
| 17 | IndicatorLineAction | {startLoc, endLoc, colorHex} | |

* Deaths that are not from damage (disintegrate, uncaught exception or return from `run`, resign) are recorded in `Round.diedIds`, not as DieAction (`GameWorld.java:1063-1066`).
* Neither tower AoE vs. single attacks nor soldier attacks on enemy paint (which do nothing) leave a distinguishing record. A soldier attack that does nothing leaves no action at all.
* To track paint in a parser, apply PaintAction and UnpaintAction in Turn order, starting from `MatchHeader.map.paint`. The team of a PaintAction is the team of the Turn's robot.

## 11. Surprises, edge cases and exploitable quirks

1. **Towers attack only when your code calls `rc.attack(loc)` (single) or `rc.attack(null)` (AoE).** They have no cooldown, and a tower can attack and build in the same turn.
2. **A 0-paint robot cannot withdraw paint** (`assertIsActionReady` inside `transferPaint`) and loses 20 HP per turn. It needs a mopper.
3. **The SRP bonus multiplies by tower count** (+3 per SRP to each paint tower and each money tower), and defense buffs stack without a cap across all defense towers.
4. **Any unit, including a tower on itself, can call `upgradeTower`** with no cooldown. Multiple upgrades per turn are allowed.
5. **Completing a tower or SRP needs no cooldown and no paint.** A tower pattern needs an adjacent robot (r²=2); an SRP only needs the robot within r²=8 of its centre.
6. **Each new tower comes with 500 paint**, and robots can drain money and defense towers' paint too.
7. **Marking is free and unlimited** (the spec says 1 paint), and its range is r²=2 rather than only your own tile.
8. **Over-transfer is destroyed** by capacity clamping. Never withdraw more than `capacity − paint`.
9. **Soldier attacks on enemy paint or empty ruins waste 5 paint plus cooldown.** Check with `canPaint`, not `canAttack`.
10. **The 70% test runs on every paint operation**, but the round finishes and the last winner set wins. Ruins count in the denominator.
11. **Exec order is spawn order**, and initial tower order comes from the map file. On many maps Team B's tower acts first in round 1, and older units always act before newer ones.
12. **SRP integrity is only sampled at round start.** Damage repaired before the next round start does not count.
13. **The adjacency paint penalty counts allied towers**, and moppers do not double that part.
14. **The paint connection for messages is a 4-connected BFS from the robot's tile** with no length limit. The robot itself must stand on its own team's paint, and diagonal-only links do not connect.
15. **Uncaught exceptions kill the unit**, towers included, at end of turn. Each caught exception costs 500 bytecodes.
16. **The coin-flip tiebreak uses unseeded `Math.random()`**, so it is nondeterministic.
17. **Splasher centres can be walls or ruins**: there is no passability check, only on-map and r²≤4.
18. **Tower single-target `attack(loc)` on an empty tile still uses up** that turn's single attack.
19. **A tower cannot attack an enemy tower in practice**: ruin spacing gives dist² ≥ 25, which is more than the maximum tower range r²=16.
20. Initial towers have map-file IDs (0–16). Spawned IDs are 10001–14096 in a map-seed-shuffled order, so IDs (and per-robot RNG seeds) repeat exactly across games on the same map.

## 12. Spec vs. engine discrepancies (the engine is authoritative)

| Topic | Spec says | Engine does |
|---|---|---|
| Mark cost | 1 paint | 0 (`RobotControllerImpl.java:546-550`) |
| L3 defense AoE | 35 | 30 (`UnitType.java:18`) |
| Cooldown decrement | after each turn | at the start of the unit's own turn (`InternalRobot.java:610-611`) |
| Win threshold | more than 70% of paintable tiles | ≥ 70% of (W·H − walls), ruins included (`TeamInfo.java:77`) |
| Adjacency penalty | adjacent bots | adjacent units, towers included (`InternalRobot.java:626`) |
| Robot IDs | ≥ 10000 | initial towers use map IDs (0–16) |
| Uncaught exception | "may paralyze" | the unit is destroyed (`GameWorld.java:360-364`) |
| Number of maps | – | 75 shipped in 3.1.0 |

## Maintainability audit of bots/t135 (= src/vibe)

**Verdict.** At 1324 lines the bot is not too big. A one-threshold tweak through `variant.py` is still cheap, and the y-series tunings show that works. What is expensive is any change that touches several places at once, for four reasons:
- **Hidden conditions.** Each step of a unit's turn keeps its own paint/round/bytecode condition inside the method, so the priority order cannot be read in one place.
- **Protocols spread across files.** Churning a money tower involves 4 files; the tower memory is split across 2 classes.
- **Rules that never run.** At least two tuning experiments (y240, y190/y194) probably changed code that cannot execute.
- **Wrong comments**, worst in the spawn-mix code the owner tunes most.

There is no messaging between robots at all (no `sendMessage`/`readMessages`). The symmetry module is computed but only feeds a debug string.

Everything below is from reading the code. I compiled twice (one javac at a time), only in the scratchpad.

---

### 1. Per-turn decision order (as it actually runs)

Before every unit's logic, `G.startTurn` → `G.remember` (G.java:75) does several jobs: it updates the map memory, runs `Sym.observe` on newly seen tiles, records ally towers, and, only for splashers, fills `Splasher.V1/V2`.

After every robot's logic, `RobotPlayer` (RobotPlayer.java:19) runs `Unit.rebuild()` and `Unit.topUp()`. Neither is visible from any `turn()`.

**Soldier.turn** (Soldier.java:15-37)
1. `scanEnemyTowers` updates the remembered nearest enemy tower (it persists out of sight).
2. Free shot at that tower if d2≤9, paint≥5 and action ready (:19). This uses the action before ruin painting can.
3. `pickRuin` if there is no ruin, unless mid-SRP with ≥6 towers (:25).
   - Skips contested ruins (marked bad for 50 rounds).
   - Helper limits: with 2 towers, at most one other soldier, within d2 20; otherwise none unless we are adjacent.
4. `workRuin` (:209-282) is itself a 9-stage chain:
   - drop if a tower stands there; give up after 150 rounds (bad for 150);
   - paint<10 → `refill(10000)` and return;
   - read marks; walk up; prePaint if towers≤3; mark, unless no other soldier is in view;
   - paint the nearest wrong tile; complete;
   - blocked >5 turns (>25 with a cleaner in view) → bad 40/100;
   - move; complete again.
5. `deny` (paint≥40, :65): paint one empty tile of a visible contested ruin, from where we stand.
6. `siege` (known enemy tower within d2 144, paint≥30): returns true even when it did not attack.
7. `srpTurn`: starts only at r≥100, chips≥1000, paint≥60 and ≥6000 bytecodes left (:323). It has its own refill below 15 paint and gives up after 60 rounds.
8. `refill(100)` (stops at 3/4 capacity; may churn-wait and repair a money tower's pattern) → `paintHere` (paint≥25).
9. Explore: `paintNear` (r≥80, paint≥50) → move to the explore target → `paintNear`.

**Splasher.turn** (Splasher.java:13-33)
1. `scanEnemyTowers`; `towersIntoGrid` (+30 per enemy tower).
2. If paint≥50 and action ready: splash with minimum score 9.
3. `refill(100)` → return.
4. `lastSplash` clamp (:25): rounds when it could not splash do not count.
5. Pick a goal, in order:
   - `standOff` (paint≥50, >6000 bytecodes);
   - else `frontier` (>5000 bytecodes and a splash within the last 8 rounds);
   - else the explore target.
6. Move there; if it has not splashed yet: splash with minimum score 6 (needs >2500 bytecodes).

**Mopper.turn** (Mopper.java:9-19)
1. `act`:
   - swing if it hits ≥2 enemy robots;
   - else mop the best tile within d2 2 (enemy paint 10, enemy robot +15, +40 near a ruin with no enemy tower);
   - else, with paint>60, give paint to an adjacent soldier/splasher below 40%, keeping 40.
2. `paint<40 && refill(40)` → return.
3. Target the nearest enemy robot (−40 if within d2 25 of a known tower of ours) or enemy tile (+2, −40 near a ruin). Stop once within d2 2.
4. Move; `act` again.

**Tower.turn** (Tower.java:10-17)
1. `attack`: single target (lowest health, −60 unless a mopper), then the area attack.
2. `build` (if action ready). `choose`:
   - r<80 → soldier;
   - paint towers: `built%6%4` gives S X X M S X;
   - other towers: S M X M S M.
   - Reserve: 0 before r40, else 1000 while under 25 towers, 0 for a due mopper with an enemy within d2 20.
   - Returns without advancing `built` if it cannot pay chips or paint.
3. `upgrade`: paint towers at cost+1200; money towers at cost+3700; defense towers never.
4. `churn`: an L1 money tower with paint<10, chips≥2000, no enemy in view, a robot adjacent and its pattern intact disintegrates.

**Soldier.wantType** (tower type for a new ruin, :135-151)
1. Every known tower, none paint → PAINT.
2. No money tower → MONEY.
3. n≥3 and chips≥1500 → PAINT.
4. n<6 → MONEY.
5. pt < 1+(n−6)/4 → PAINT.
6. n<8 → MONEY.
7. chips≥3000 → PAINT. **Unreachable**: step 3 already returned.
8. pt*5<n → PAINT, else MONEY.

**Readability.** The top-level Soldier chain reads well. Below it, it gets harder:
- The deciding conditions are inside each method, so knowing what a soldier with 45 paint does next to a contested ruin and an enemy tower means reading 5 methods.
- The booleans mean different things ("acted" for `deny`, "busy" for `siege`).
- There are free actions both before the chain (the free shot) and after it (`rebuild`, `topUp`).
- `refill` secretly contains the churn wait and `repairPattern`, which spends the action.

---

### 2. Tunable constants (file:line)

**Soldier** (paint capacity 200)
- Minimum paint 5: :19, :192, :252, :412, and Unit.java:99.
- Attack d2 9: :20, :47, :51, :199, :249, :405.
- Paint ladder: ruin refill 10 (:214), SRP refill 15 (:453), `paintHere` 25 (:473), `SIEGE_PAINT` 30 (:41), deny 40 (:65), `paintNear` 50 (:481), SRP start 60 (:323), refill 100 (:32).
- Other siege/deny: `SIEGE_R2` 144 (:41); deny stops at 2 own tiles (:74).
- Rounds: no ground paint before r80 (:34, :36).
- `pickRuin`: d2 8, towers==2, d2 20, d2 2 (:121-124); contested → bad 50 (:118).
- `workRuin`: 150/150 (:213); prePaint while towers≤3 (:223); give up after 5/25, bad 40/100 (:267).
- `wantType`: 3, 1500 (:145); 6 (:146-147); 4 (:147); 8 (:148); `IDLE_CHIPS` 3000 (:134, dead); 5 (:150).
- SRP:
  - Start conditions: `SRP_ROUND` 100, `SRP_CHIPS` 1000, `SRP_TOWERS` 6, `SRP_GIVE_UP` 60 (:290).
  - Bytecode guards 6000/3000/2500/4000 (:323, :343, :454, :461); search radius 7 and d2 50 (:337-346).
  - Chebyshev 2/4/6 (:355-362); skip timers 100/300/60/80/150/100 (:359, :362, :372, :400, :440, :449).
  - Enemy tower d2 25 (:452); score 3·right, tower bonus 40/15 (:376).

**Splasher** (capacity 300)
- 50 appears 4 times (:20, :25, :26, :29). At :20/:25/:29 it is the splash cost; at :26 it is the stand-off gate, a separate knob (t112/t114/t115 tried 30/70/90).
- Minimum scores 9 (:20) and 6 (:31); refill 100 (:21); window 8 and clamp −4 (:25, :27).
- Bytecode guards 6000/5000/2500 (:26, :27, :29); tower grid value 30 (:46).
- Grid values 1/2/−50 live in G.java:98 and :101, not in Splasher.
- Stand-off ring (:73-74); tower ranges 9/16 (:95); frontier d2 5 and −3 (:114-115).

**Mopper** (capacity 100)
- 40 appears 6 times with 4 meanings: refill (:12, twice), ruin bonus (:46, :90), `DEFEND_BONUS` (:8), ally 40% (:57), keep 40 (:60).
- Give-paint gate 60 (:51); mop scores 10/15 (:43, :45); ruin d2 8 (:67); `DEFEND_R2` 25 (:8).

**Unit**
- Refill stops at 3/4 capacity (:18, :45); dry flags last 10/40 rounds (:23); a flag drops at 50 paint (:28); paint towers count 7/10 of the distance (:32).
- Churn wait: 10 paint, 50, 3 (:49-52); dry thresholds 20 (:54) and 40 (:59).
- `rebuild` at 1000 chips (:83); explore: reached at d2 8, timeout 90 (:121), 128 draws (:126).
- `towerDry[32]` (:10) must match `G.towerLoc[32]` and `towerKind[32]` (G.java:30-31).

**Tower**
- Opening r80 (:63); reserve: r40, 1000, 25 (:86); 1000 again (:89, redundant); mopper defense d2 20 (:88).
- Attack bias 60/10000 (:51); `UPGRADE_SPARE` 1200 (:8); money upgrades +2500 (:109).
- `CHURN_CHIPS` 2000 (:19, also read by `Unit.churnable`); churn paint 10 (:25).
- Cycles (:66, :69-76); placement ×4 + rand(4) (:96).

**Nav**: target reset d2 8 (:29), tile-cost weight 6 (:51), robot-block wait 3 (:59), follow cap 2(W+H) (:40).

**Tower kind codes 1/2/3** are bare literals in G.java:31 and :126-128, Unit.java:23, :32, :87, Soldier.java:140, :307, :357-362, Splasher.java:82, :95, and Tower.java:79, :108-109.

**Constants that interact:**
- **Soldier paint ladder vs `refill(100)`.** Refill comes after deny/siege/SRP in the chain, so soldiers with 40-99 paint deny or siege first. `paintNear`'s 50 only matters when no non-dry tower is known, because `refill(100)` fires first.
- **Round 80** is in two files (Tower.java:63 and Soldier.java:34/36). It was tuned only in Tower (y238-y246).
- **Chips.** Reserve 1000, rebuild 1000, SRP 1000, paint tower 1500, churn 2000, upgrade 1200/+2500 and the dead 3000 are spread over Tower, Soldier and Unit. No single place shows which spender gets chips first.
- **Churn** needs agreement across 3 files: Tower.java:25 (paint<10, 2000 chips) and Unit.java:49 (paint<10, `churnable()`), with `rebuild` at 1000.

**Would a constants table help? Yes.** Proposed `Tune.java`: one `static final int` per line, grouped by unit and by economy, each with where it is used, what it means and the values already tried (taken from notes.tsv):
```java
static final int OPENING_SOLDIERS_UNTIL = 80;   // Tower.choose (y238 60, y239 100, y241 120, y246 150: none crowned)
static final int SOLDIER_SAVE_PAINT_UNTIL = 80; // Soldier.turn paintNear (study 3 tactic 2) - same value, separate knob
static final int SOL_DENY_PAINT = 40;           // Soldier.deny (y206 25)
static final int SOL_SIEGE_PAINT = 30;          // Soldier.siege (y219 50)
static final int SPAWN_RESERVE = 1000;          // Tower.build (y243 800)
static final int PAINT_TOWER_CHIPS = 1500;      // wantType from 3 towers (y178 1250, y180 1750)
static final int PAINT = 1, MONEY = 2, DEFENSE = 3;   // G.towerKind codes
```
This is provably free. javac inlines compile-time constants. I tested it: moving three Splasher literals into a `Tune` class gave bytecode identical to t135 for every class, ignoring constant-pool numbering. Two further benefits:
- A variant becomes `variant.py NEW BASE Tune.java "SOL_DENY_PAINT = 40" "SOL_DENY_PAINT = 25"`, which is unique by construction. Today the variant author has to pick surrounding code to make the search string unique.
- Literals that share a value but not a meaning (80/80, the four 40s) must get separate names, so they stay identical.

Keep engine-derived values as literals for the identical step (e.g. 9 = `SOLDIER.actionRadiusSquared`): a field read changes bytecode. `GameConstants.*` values are themselves inlined, so they are safe to use.

---

### 3. Shared mutable state: who writes what

- **`G.here`.** Written by `startTurn`, `Nav.step` (Nav.java:101), Soldier.java:48/:54/:460 and Splasher.java:30. The writes at :48, :460 and Splasher:30 are redundant after `Nav.moveTo`. Any move made outside `Nav.step` must remember to update it by hand (:54 does).
- **`G.paint`.** Manually refreshed at about 14 action sites. Forgetting one feeds a stale value into every later threshold in the turn.
- **`G.chips`.** Only `startTurn` and `srpComplete` update it.
  - `Tower.build` spends chips without refreshing it, so `upgrade()` (:107-109) and `churn()` (:25) see the pre-build value.
  - `Unit.churnable`/`rebuild` and `wantType` call `rc.getChips()` instead, so the code mixes the two.
- **Tower memory.**
  - `G.towerLoc/towerKind/nTowers` are written by `G.remember`, `Soldier.workRuin`, `Unit.rebuild`, `Unit.refill` (forget) and `Tower.churn` (forget).
  - They are read by `Unit.refill`, `wantType`, `allyTowerKind` and `Mopper.target`.
  - `Unit.towerDry` is a parallel array in another class, indexed the same way. `G.forgetTower` (G.java:137-141) swap-removes `towerLoc`/`towerKind` but not `towerDry`, so a dry flag moves to a different tower (bug; t132's "2.5" fixes it but was not crowned).
- **`Splasher.V1/V2`** are filled in `G.remember` (G depends on Splasher internals). `Splasher.towersIntoGrid` must run before any move, because it sets `gx0/gy0` to match the turn-start position.
- **`G.ruinList/nRuins`** are filled only on the non-splasher branch (G.java:113). They are always empty for splashers: a trap for any future splasher rule.
- **`Unit.enemyTower`** is set only by soldiers and splashers (`scanEnemyTowers`). It is always null for moppers (another trap), and it persists out of sight, which is what drives `siege`.
- **`Unit.refillAt`/`churnLoc`/`churnAt`/`explore`** carry state across turns and across callers. Mopper.java:12 adds an outer `paint<40` check on top of `refill`'s stop-at-3/4 rule.
- **`Nav.*`.** One bug-follow state per robot. `workRuin` can call `moveTo` twice with different targets in one turn (:222, :271), and a target jump of more than d2 8 resets the follow state.
- **`Soldier.ruin` vs `Soldier.srp`** are two concurrent jobs. A ruin can preempt a running SRP (with <6 towers) while `srpSince` keeps counting.
- **`Tower.built`** advances only on a successful build (see the stall in "Possible bugs").
- **`Tower.CHURN_CHIPS`** is read by `Unit.churnable`. `Soldier.patternOf/bit` are used by Unit and Tower. `G.SRP_MASK` decoding is written twice (G.java:101, Soldier.java:297).

---

### 4. Dead code, overridden rules, stale comments

**Never called or never read**
- `Sym.killIf/mirror/count/best` (Sym.java:35-48).
- `G.paintAt` (:145), `G.onMap` (:151), `G.dist` (:153).
- `Nav.stepRandom` (Nav.java:106-115) and so `G.DIRS` (:21).
- `G.spawnLoc` (:14, :49); `Nav.last1/last2` (written at :100, read only by tests); the empty `if` at Nav.java:91-92.
- `Sym.live` is used only for the tower debug string (Tower.java:16). Even so, `Sym.observe` runs on every newly seen tile (G.java:92, :112).

**Runs but has no effect**
- `enemyNear` loop in `Tower.choose` (:60-61).
- Tower.java:89 `&& !(G.chips >= 1000 + t.moneyCost)` is redundant: the reserve is either 0 or 1000.
- `wantType`:149 (`IDLE_CHIPS`) is unreachable since t70/y170. So y190 and y194 tuned a dead rule.
- Soldier.java:20 `d2<=9` repeats what `canAttack` already checks.

**A rule overridden by a later one**
- The money-tower cycle (Tower.java:69-76) only ever reaches slot 1-2. A money tower never gains paint: it starts with 500 and produces none, and robots withdraw from it. `build()` returns without advancing `built` when paint < cost (:90). So after S+M or S+S (300-400 paint), it waits forever for a 300-paint splasher.
  - y240 changed slot 5 and finished flat (−1 after 599 games), consistent with a no-op.
  - The defensive-mopper exception (:88) only fires when a mopper is due, so a stalled money tower never defends.
- `wantType`:145 (1500 chips) runs before :146 "money for towers 1-5/6".
- Mopper.java:12's outer check adds nothing to `refill(40)`'s own check.
- `lastSplash` is not the last splash round (the clamp at :25), so any future rule that uses it would be misled.

**Comments that no longer match the code**
- Splasher.java:37 says towers add 12; the code adds 30 (:46).
- Splasher.java:16 says "one splash evaluation a turn"; it can be two (:20, :31).
- Tower.java:64-66 says the paint-tower cycle is "S X X M / a mopper every third"; it is S X X M S X (2:3:1).
- Tower.java:67-68 says "a third moppers"; S M X M S M is half moppers (and only slots 0-1 run).
- Tower.java:85 says "freeze spawns 8 rounds in 20"; there is no freeze.
- Soldier.java:131-133 (wantType doc) and :144 ("1-5") predate y155/y170.
- Unit.java:124 says "up to 8 tiles"; it is 128.
- Nav.java:105 says `stepRandom` is "used to get off enemy paint"; it has no caller.

---

### 5. How hard is a new behaviour today, and what would make it cheaper

- **Coordinated attack.** There are no comms, so there is no shared target. `Unit.enemyTower` is just "the nearest tower I saw". `siege` is a single-unit kite. An attack mode must decide what it preempts among `workRuin`, `deny`, SRP and `refill`, and each of those decides inside itself.
  - Sym already knows the symmetry, and `mirror()`, which would give the enemy's starting towers, is written but unused.
  - Estimate: about 200 lines over 5-6 files plus reasoning through the hidden conditions.
- **A unit role** (raider, SRP builder, guard). Unit type is the only role. There is no per-unit role field, and a tower cannot tell a new robot anything without messages. Every role becomes an `if` near the top of `turn()`.
- **A tower-spawn policy.** `choose` is two modulo cycles plus a round cutoff; `build` has ad-hoc reserve exceptions and the silent stall. The record of past attempts shows the cost: t71 −317, t76 −295, t83 −54, t125 −26, t129 −41, t130 −8, y240 −1. Each was another special case.

**Three refactors, in this order.**

**Step 0: verification harness.**
- (a) `bytecode-diff.sh`, already written (path at the end). It compares `javap -c` of two compiled trees, ignoring constant-pool numbering.
- (b) Twin games: the same opponent, maps and seeds with `arena.py game --keep`, then `ReplayDump tsv`, then diff `actions.tsv` and `turns.tsv` without the bc/ind columns. `turns.tsv` has a per-turn `bc` column, so any divergence can be traced to a bytecode check near its threshold.
- Why the harness is needed: game behaviour depends on `Clock.getBytecodesLeft()` (Soldier.java:323/343/454/461, Splasher.java:26/27/29). Any change in executed bytecode can flip a branch on rare turns.

**R1: `Tune.java` plus tower-kind names, comment fixes, and deleting code that never runs.**
- Size: about 90 constants, about 200 edited lines, 2-3 hours. Risk ≈ 0.
- Proof of identity: `bytecode-diff` shows 0 differences in every surviving method. No games are needed.
- Removals that do run (the `enemyNear` loop, the :89 clause, :149, `Nav.last1/2`, `G.DIRS` in the static initializer) are not part of R1.

**R2: give state an owner (move code, do not rewrite it).**
- `Towers.java`: `G.towerLoc/towerKind/nTowers/noteTower/forgetTower/kind` plus `Unit.towerDry/markDry`. Keep the current forget behaviour for now.
- `Churn.java`: `Tower.churn`, `Unit.churnable/repairPattern/rebuild`, `CHURN_CHIPS`.
- `Pattern.java`: `patternOf/bit/readMarks/contested/agreesWithMoney/srpSec`.
- Move the splasher grid fill out of `G.remember` into a single `Splasher.sense()` call.
- Size: about 200 lines moved, about 30 written, 2 hours. Risk: very low.
- Moving a static method keeps its instruction sequence identical. What changes: the one added call, and static initializers running at a different point in a unit's first turn. Twin games settle it.

**R3: explicit decision lists.**
- Each `turn()` becomes an ordered list `if (gate && behaviour()) return;` with the gates at the call site. The free actions (free shot, `rebuild`, `topUp`) are listed explicitly, and each step adds one label to the debug string.
- `Tower.choose` becomes cycle arrays per tower kind and phase, plus an ordered override list, with the "can't pay → wait" rule written out. Keep it exactly as it is for now.
- Remove the dead code that does run.
- Size: about 150-200 lines rewritten in Soldier/Splasher/Mopper/Tower, half a day. Risk: low-medium, mainly from carrying each method's internal condition over correctly.
- Proof: twin games identical, apart from bytecode-check flips that `turns.tsv` explains. Tower.java reads no `Clock` at all, so tower-only edits are identical unless a tower overruns (`G.overruns`).

After R1-R3, a coordinated attack becomes: a new Comms module (towers relay a target within message radius 20 / broadcast 80), one Attack behaviour, one line in each chain, and entries in Tune. A spawn policy becomes a table edit.

Things to avoid: interfaces or behaviour objects (virtual calls and allocations cost bytecode). Keep it static.

**Process questions for the owner.**
- A refactor that behaves identically cannot win the local tournament; it can only tie. It needs the owner's OK to become the variant base as a verified re-snapshot rather than a crowning.
- The best time is right after a crowning. t138 and y277 (both based on t135) keep running as snapshots. Only `variant.py port` onto the new base would fail; re-expressed as `Tune` edits, most become one-liners.

---

### Possible bugs (for the bug hunter)

1. `G.forgetTower` does not move `Unit.towerDry`, so a dry flag ends up on the wrong tower (G.java:137-141, Unit.java:10).
2. Tower: `G.chips` is stale after `buildRobot`, so the upgrade spare is short by the unit's cost (Tower.java:89-109), and `churn` also reads it.
3. A money tower's spawning stalls for good at the first unit it cannot pay for; this also suppresses the defensive mopper (Tower.java:88-90).
4. In `workRuin` (Soldier.java:214-217), a soldier with paint<10 and no usable tower idles until the 150-round timeout (t134 tests a fix).
5. `Sym` spends bytecode on every newly seen tile for a debug string. Removing it, or using it, is a behaviour change: it frees bytecode on the expensive first turn on big maps.

Debug strings are built every turn even with `DEBUG=false`, because `G.endTurn` (G.java:148) sets them whenever `G.ind` is non-empty. That is a minor cost.

---

Files are in /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/audit-structure/:
- bytecode-diff.sh
- a/ and b/: t135 and the 3-literal `Tune` sample
- ca/ and cb/: their compiled classes

Nothing under bots/ or src/ was edited, nothing was committed, and no games were run.

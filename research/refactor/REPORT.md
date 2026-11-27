# Refactor r135 / r140 (owner #57, R1-R3)

Written by the refactor agent on 2026-11-27; the final-verification section and the variant guide come from its hand-back. The scratch tools it used are in `tools/` (their paths point at the session scratch dir; adjust before reuse). `r140_twins.txt` is the per-game table of the final r140 twin games.

```
REFACTOR r135 / r140 - report

Deliverables: bots/r135 (t135 refactored, R1+R2+R3), bots/r140 (r135 + t140's study-11 free-marks change).
Neither is registered in research/tourney/pool.txt. Nothing outside bots/r135, bots/r140 and the scratch dir was
edited; no commits. Scratch: /tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/refactor/

== R1 (Tune, names, comments, dead code) ==
- Tune.java (new): 107 `static final int`, one per tunable, each with: where used, meaning, values tried
  (notes.tsv; "crowned" marks a champion). Same-value-different-meaning literals have separate names. Engine values
  (d2 9, 5 paint/attack, 50 paint/splash, adjacency 2, 5x5 geometry) stay literal. Every `NAME = VALUE` is unique.
  Former in-class constants moved in: Mopper.DEFEND_R2, Soldier.IDLE_CHIPS/SIEGE_PAINT/SRP_ROUND,
  Tower.CHURN_CHIPS/UPGRADE_SPARE.
- Tower-kind codes named (PAINT=1, MONEY=2, DEFENSE=3; in Towers after R2).
- Never-called code deleted: G.dist, G.onMap, G.paintAt, Nav.stepRandom, Sym.best/count/killIf/mirror.
- Stale comments fixed throughout (file headers, step comments, study refs).
- Proof: tools/bytecode-diff.sh cls/t135 cls/r1 -> diff lines per class: G$1 0, G 45, Mopper 4, Nav 37,
  RobotPlayer$1 0, RobotPlayer 0, Soldier$1 0, Soldier 14, Splasher 0, Sym 101, Tower 4, Unit 0; every non-zero
  line is a deleted method or a removed/added constant field (inlined, so no code change). Member diff of all
  surviving methods: "CHANGED members: 0".

== R2 (one owner per piece of shared state; code moved, not rewritten) ==
- Towers.java (new): tower memory loc[]/kind[]/dry[] (was G.towerLoc/towerKind + Unit.towerDry), kind codes,
  kindOf (was G.kind), note/forget (was G.noteTower/forgetTower; forget keeps the dry[] drift bug, documented),
  markDry (was Unit.markDry), kindAt (was Soldier.allyTowerKind). Count stays G.nTowers (BotTest resets it there);
  loc/kind are allocated in G's static block and dry in Unit's, exactly where t135 allocated them (see below).
- Churn.java (new): churnable, towerTurn (was Tower.churn), rebuild, repairPattern (were in Unit); class doc
  explains the whole tactic (tower side, robot side, wait state Unit.churnLoc/churnAt).
- Pattern.java (new): SRP_MASK, of (was Soldier.patternOf), bit, srpSec, readMarks, contested, agreesWithMoney.
- Splasher.sense() (new): the splash-grid fill that sat inside G.remember, moved verbatim; G.remember calls it
  once for splashers, as Splasher.sense(W) (W passed in to keep the bytecode count exact, see the flip below).
- G, Unit, Soldier, Tower, Mopper, RobotPlayer: callers repointed (invokestatic -> invokestatic, same cost).
  Soldier.bit kept as a one-line forwarder to Pattern.bit because test/vibe/BotTest calls Soldier.bit.
- Proof (scratch movecheck.py: javap of t135 vs r2, members mapped old->new, offsets/branch targets/local slots/
  ldc-vs-ldc_w normalised): all 82 moved or untouched methods identical; differences only where planned:
  G.remember (splasher branch -> Splasher.sense call), G.static{} (+tower arrays), Unit.static{} (-towerDry),
  new Splasher.sense, new Soldier.bit forwarder.

== R3 (explicit decision lists) ==
- Tower.java rewritten: turn() = 1 attack, 2 build (gate: action ready), 3 upgrade (gate: canUpgradeTower),
  4 churn (gate at the call site: L1 money tower, paint < CHURN_PAINT, chips >= CHURN_CHIPS, no enemy, then
  Churn.towerTurn checks helper + pattern). choose() = cycle table by phase/kind (OPENING {S,S,S,S,S,S} before
  OPENING_SOLDIERS_UNTIL; PAINT_CYCLE {S,X,X,M,S,X}; OTHER_CYCLE {S,M,X,M,S,M}) indexed built % 6, with a documented
  override slot (none today). reserve(t) = ordered rules (before SPAWN_RESERVE_FROM: 0; >= SPAWN_RESERVE_TOWERS
  towers: 0; mopper due + enemy robot within DEFEND_MOPPER_R2: 0; else SPAWN_RESERVE). build(): explicit
  "can't pay -> wait" rule `chips < cost + min(reserve, SPAWN_ANYWAY_CHIPS) || paint < paintCost -> return`
  (equivalent to t135's two clauses for every value; `built` not advanced, so the money-tower stall is kept and
  documented). upgrade(): gate at call site, still reads the stale turn-start G.chips (bug kept). A no-effect
  enemy-scan loop in the old choose was removed.
- Churn.towerTurn: its first two gate lines moved to the Tower.turn call site.
- Mopper.java: turn() as numbered steps (1 act, 2 refill when paint < MOP_REFILL, 3 target/move, 4 act again);
  act() stays one method with its stages numbered (1 swing, 2 mop, 3 give when paint > MOP_GIVE_ABOVE); see below.
  Audit claim checked and kept: the outer paint check at the refill call is not redundant (it ends a refill walk
  at 40 paint).
- Soldier.turn / Splasher.turn / RobotPlayer: the step list is written out at the call sites (numbered comments
  with each step's "in:" gate), but the gates were NOT moved out of the step methods. Reason: soldiers and
  splashers read Clock.getBytecodesLeft() (Soldier srpTurn < 6000, pickSrp < 3000 per candidate, workSrp
  < 2500 / > 4000; Splasher standOff > 6000, frontier > 5000, after-move splash > 2500), and hoisting a gate changes
  the instruction count before those reads (measured: siege fail -8, deny -4, splasher refill -5, SRP start -1),
  which can flip a branch; the free actions (Churn.rebuild, Unit.topUp) run near the 17500 limit (splasher first
  turns reach 17435-17505 on DefaultHuge), so moving their gates shifts which turns overrun. Only code change in
  Soldier.turn: `if (ruin != null) { if (workRuin()) return; }` -> `if (ruin != null && workRuin()) return;`
  (identical bytecode). Towers read no Clock and stay far below their limit (max seen 15982 / 20000), so only
  Tower was restructured in code.
- Running-but-no-effect code kept (each sits on a Clock-sensitive path or in the first-turn class init, so
  removing it would change bc): Soldier free-shot `d2 <= 9` re-check, wantType's IDLE_CHIPS rule, G.DIRS, an
  empty if in Nav; Nav.last1/last2 are kept because BotTest reads them.

== Clock/overrun flip found and removed ==
First r140 twin run: t118_B_DefaultHuge_s0 diverged at round 485. Cause: every splasher turn cost 1 bytecode less
than in t140. The engine's instrumenter charges nothing for a call to our own method (only API methods carry a
MethodCosts cost), while the callee's `return` costs 1. So R2's `Splasher.sense()` (call 0 + return 1) replaced
t135's `int w = W` (2), giving -1 per turn. Splasher 12016 then used 17499 bytecodes at round 484 where t140 used
exactly 17500 (the limit), so the t140 splasher was suspended through round 485 and the r140 one moved.
Fix: `Splasher.sense(W)`, with w used per tile. Pushing W (1) + return (1) = the old local (2); the per-turn cost
is 8 = 8 under the engine's cost model, and the loop body is 164 = 164 instructions (scratch pyjavap.py). All 7
r140 games from that run were discarded and rerun; the 8 t140 baselines were kept.
(Earlier in the work I had assumed invokestatic costs 1; that only changes the numbers in my "why the gates stay
inside" estimates, not the decision.)

== Two more exactness fixes after the first r140 run (no game diverged from them; done to rule out overrun shifts) ==
- Mopper.act split (swing/mop/give methods) changed mopper bc by -6..+22 per turn, and moppers do reach the limit
  (17502/17508 seen on DefaultHuge first turns). Restored the single-method act() (bytecode-identical to t135) with
  the stage list in its doc. So the R3 mopper list is turn() steps 1-4 + act's documented stages.
- R2 had moved the towerDry allocation (35 bytecodes) from Unit's class init to G's. Totals were equal, but on an
  overrunning first turn the cut-off point moves 35 instructions; for moppers (first Unit access late in the turn)
  that could move an action a round. Now Towers.dry is allocated in Unit's static block, loc/kind in G's, exactly
  where t135 allocated them; G/Unit/Splasher/Soldier/Sym/Nav class inits identical; switch-map classes
  G$1->Towers$1 and Soldier$1->Pattern$1 have identical 19-instruction inits.
- Final movecheck (both t140->r140 and t135->r135): robot-side differences only G.remember + Splasher.sense
  (cost-equal); the rest is tower-only (Tower.*, Churn.towerTurn, Tower.static{}).
```

## Final verification of r140 (hand-back)

- Twin games: 43 r140 games against the 43 t140 baselines (same opponents t118, y221, t91, t140; same maps
  DefaultSmall, DefaultMedium, DefaultHuge, Snowman, Fossil, Mirage, galaxy, Leaf; same seeds; both seats).
  Compared on actions.tsv + turns.tsv: 43/43 IDENTICAL, 0 diverged; winner and round count equal in all 43.
  Checked again from the main session with `cmp_all.py` (games/p140/base vs games/f140): DIVERGED games: 0.
- Per-turn bytecode, r140 - t140: soldier [0,0] (43 games), splasher [0,0] (37), mopper [0,0] (41);
  paint tower [-173,+81], money tower [-132,+81]. Towers read no Clock and peak at 15982 of 20000; robots do reach
  the 17500 limit (soldier 17589, splasher 17601, mopper 17508) and are identical on every turn.
- The study-11 change carried over exactly: Soldier.freeMarks and Soldier.workRuin are bytecode-identical between
  t140 and r140, and they are the only methods that differ from t135->t140 and from r135->r140.
- Unit tests: BotTest 96/96 on r140 and r135.
- r135 twin games were stopped at 26 of 43 (no divergence flagged): t135 is retired, so r135 is not used.

## Writing variants on r140

- A knob: `python3 tools/variant.py NEW r140 Tune.java 'NAME = 40;' 'NAME = 25;'` (every `NAME = VALUE` in Tune is
  unique; each constant's comment gives where it is used, what it means and the values tried).
- Decision lists: Soldier.turn, Splasher.turn, Mopper.turn and Mopper.act, Tower.turn (choose, reserve, build);
  free actions after every robot turn in RobotPlayer (Churn.rebuild, Unit.topUp). Shared state: Towers, Churn,
  Pattern.
- Cost model: a call to our own method is free and its return costs 1. Moving a gate, splitting a method or adding
  a local in robot code shifts the bytecode count before Soldier's and Splasher's Clock reads and changes which
  turns hit 17500, so a structural edit meant to be behaviour-neutral needs its own twin check. A Tune value change
  does not.
- BotTest resets G.nTowers and calls Soldier.bit (a forwarder to Pattern.bit): keep both unless BotTest changes.

package y344;

/** Every tunable constant, one per line: where it is used, what it means, and the values tried before
 *  (research/tourney/notes.tsv; "crowned" = that bot became champion with it). javac inlines compile-time constants,
 *  so the bytecode is the same as with bare literals and this class is never loaded. A variant is one edit:
 *      python3 tools/variant.py NEW r140 Tune.java 'NAME = 40;' 'NAME = 25;'
 *  (each `NAME = VALUE` occurs once in this file, so the edit is unique).
 *  Two literals with the same value but a different meaning have separate names here (e.g. the three 80s and the
 *  mopper's four 40s), so changing one never changes the other.
 *  Engine values are NOT here and stay literal at their call sites: attack and action radius d2 9, a soldier's
 *  5 paint per attack, a splash's 50 paint, adjacency d2 2, and the 5x5 pattern geometry (Chebyshev 2 = d2 8;
 *  two 5x5s overlap within Chebyshev 4). */
public strictfp class Tune {
    // ================================ economy: who spends chips ================================
    // In code order a turn checks: Churn.rebuild (robots, after their turn), Tower.build (spawns), Tower.upgrade,
    // the churn (Tower.turn / Churn.towerTurn); soldiers read chips in wantType (tower type) and srpTurn (SRP start).
    static final int SPAWN_RESERVE = 1000;           // Tower.reserve: spawn only with unit cost + this (t45 crowned; y243 800)
    static final int SPAWN_RESERVE_FROM = 40;        // Tower.reserve: no reserve before this round (y245/y247 60)
    static final int SPAWN_RESERVE_TOWERS = 25;      // Tower.reserve: no reserve from this many towers on
    static final int SPAWN_ANYWAY_CHIPS = 1000;      // Tower.build: spawn anyway with cost + this (the wait rule uses min(reserve, this)); no effect while >= SPAWN_RESERVE
    static final int UPGRADE_SPARE = 1200;           // Tower.upgrade: paint towers upgrade at next cost + this (y95 crowned, was 800; y173/y176/y183 800; y218 1600)
    static final int MONEY_UPGRADE_EXTRA = 2500;     // Tower.upgrade: money towers need this beyond cost + UPGRADE_SPARE (y110 crowned; y275 3500; t136/t138 5000; y274/y277 7500; t54/t60 never)
    static final int CHURN_CHIPS = 2000;             // Tower.turn churn gate, Churn.churnable: a drained L1 money tower churns at this many chips (y181/y186 1500; y189/y193/y198 2500)
    static final int CHURN_PAINT = 10;               // Tower.turn churn gate, Unit.refill: a money tower below this paint is drained (churns / is waited on)
    static final int REBUILD_CHIPS = 1000;           // Churn.rebuild: re-complete an adjacent churned money tower (= its cost)
    static final int SRP_CHIPS = 1000;               // Soldier.srpTurn: start an SRP only with this many chips (t36)
    static final int WANT_PAINT_CHIPS = 1500;        // Soldier.wantType: from WANT_PAINT_CHIPS_TOWERS towers, this many chips make the next tower paint (t63 2000; y164/y170 crowned 1500; y171 1000; y178 1250; y180/y185 1750; y165 3000)
    static final int IDLE_CHIPS = 3000;              // Soldier.wantType: UNREACHABLE (WANT_PAINT_CHIPS fires first); y190/y194 tuned it to 2000 in vain

    // ================================ tower spawning: Tower.choose / build ================================
    static final int OPENING_SOLDIERS_UNTIL = 80;    // Tower.choose: only soldiers before this round (y238 60; y239 100; y241 120; y246 150: none crowned)
    static final int DEFEND_MOPPER_R2 = 20;          // Tower.reserve: a due mopper ignores the reserve with an enemy robot within this d2 (t47 crowned; y244 36)
    static final int TWR_SHOT_NONMOPPER = 60;        // Tower.attack: a soldier/splasher counts this much weaker than a mopper
    static final int TWR_SHOT_TOWER = 10000;         // Tower.attack: a tower counts this much stronger (shot last)

    // ================================ soldier (paint capacity 200) ================================
    // the paint ladder, low to high; the turn order is in Soldier.turn
    static final int SOL_SHOT_PAINT = 5;             // Soldier.turn: free shot at the remembered enemy tower from this paint (5 = the attack's cost)
    static final int SOL_RUIN_REFILL = 10;           // Soldier.workRuin: below this, refill mid-pattern
    static final int SRP_REFILL = 15;                // Soldier.workSrp: below this, refill mid-SRP
    static final int SOL_PAINT_HERE = 25;            // Soldier.paintHere (on the refill path)
    static final int SOL_SIEGE_PAINT = 30;           // Soldier.siege (y219 50)
    static final int SOL_DENY_PAINT = 40;            // Soldier.deny (y206 25)
    static final int SOL_PAINT_NEAR = 50;            // Soldier.paintNear (explore painting)
    static final int SRP_PAINT = 60;                 // Soldier.srpTurn: start an SRP only with this much paint
    static final int SOL_REFILL = 100;               // Soldier.turn: refill below this
    static final int SOL_SAVE_PAINT_UNTIL = 80;      // Soldier.turn: no explore painting before this round (study 3 tactic 2: t04 crowned 80, y58 50); not OPENING_SOLDIERS_UNTIL
    // siege and denial
    static final int SOL_SIEGE_R2 = 144;             // Soldier.siege: kite a remembered enemy tower within this d2 (y209 100)
    static final int SOL_DENY_OURS = 2;              // Soldier.deny: skip a contested ruin already showing this many of our tiles (t85 3; y188/y192/y197 crowned 2; y187 5; y196/y199 1)
    // ruins
    static final int SOL_CONTESTED_BAD = 50;         // Soldier.pickRuin: a contested ruin is skipped this many rounds (t08)
    static final int SOL_HELPER_R2 = 8;              // Soldier.pickRuin: an ally soldier within this d2 of a ruin is working it
    static final int SOL_PAIR_TOWERS = 2;            // Soldier.pickRuin: with exactly this many towers a second soldier may join a ruin...
    static final int SOL_PAIR_JOIN_R2 = 20;          // ...from within this d2 (t105/y221 crowned; y226 32); otherwise only when adjacent
    static final int SOL_RUIN_GIVE_UP = 150;         // Soldier.workRuin: drop a ruin after this many rounds...
    static final int SOL_RUIN_GIVE_UP_BAD = 150;     // ...and skip it this many rounds
    static final int SOL_PREPAINT_TOWERS = 3;        // Soldier.workRuin: pre-paint on the way in while we have at most this many towers (t102; y225/y228/y230/y231 5)
    static final int SOL_BLOCKED_ALONE = 5;          // Soldier.workRuin: blocked turns before giving up, no own mopper/splasher in view (t118 crowned, was 25; y248/y251 3; y258 8)
    static final int SOL_BLOCKED_ALONE_BAD = 40;     // ...then skip the ruin this many rounds (y250/y252 20; y253/y257 10)
    static final int SOL_BLOCKED_CLEANER = 25;       // ...with a cleaner in view (y249 15; y259/y261 35; y262 45)
    static final int SOL_BLOCKED_CLEANER_BAD = 100;  // ...then skip the ruin this many rounds
    // tower type for a new ruin (Soldier.wantType; its rules in order)
    static final int WANT_PAINT_CHIPS_TOWERS = 3;    // from this many towers WANT_PAINT_CHIPS applies (y179 2)
    static final int WANT_MONEY_UNTIL = 6;           // money below this many towers; then a paint tower per WANT_PAINT_PER (t61 5; y155 crowned 6; y154 4; y158 7)
    static final int WANT_PAINT_PER = 4;             // (t61/y155 4; y153/y157/y161/y163 3)
    static final int WANT_MONEY_UNTIL_LATE = 8;      // then money below this many towers
    static final int WANT_PAINT_SHARE = 5;           // then paint while paint towers * this < towers (t16)
    // special resource patterns (SRPs)
    static final int SRP_ROUND = 100;                // Soldier.srpTurn: no SRP before this round (t36)
    static final int SRP_TOWERS = 6;                 // Soldier.turn: with this many towers a soldier mid-SRP takes no new ruin (y208/y210/y213 5; y212/y214 4)
    static final int SRP_GIVE_UP = 60;               // Soldier.workSrp: drop an SRP after this many rounds...
    static final int SRP_SKIP_GIVE_UP = 150;         // ...and skip its centre this many rounds
    static final int SRP_START_BC = 6000;            // Soldier.srpTurn: search for a centre only with this many bytecodes left
    static final int SRP_PICK_BC = 3000;             // Soldier.pickSrp: stop scanning centres below this many bytecodes left
    static final int SRP_WORK_BC = 2500;             // Soldier.workSrp: below this many bytecodes left, hold this turn
    static final int SRP_REPAINT_BC = 4000;          // Soldier.workSrp: rescan and paint after the move only above this
    static final int SRP_SEARCH = 7;                 // Soldier.pickSrp: centres within this many tiles in x and in y...
    static final int SRP_PICK_R2 = 50;               // ...and within this d2
    static final int SRP_RIGHT_WEIGHT = 3;           // Soldier.pickSrp score: d2 - this * (tiles already right) - tower bonus
    static final int SRP_TOWER_FAR = 6;              // Soldier.pickSrp: one of our towers within this Chebyshev distance earns SRP_BONUS_FAR
    static final int SRP_BONUS_NEAR = 40;            // ...within Chebyshev 4 (its 5x5 overlaps the SRP's)
    static final int SRP_BONUS_FAR = 15;
    static final int SRP_SKIP_RUIN = 100;            // Soldier.pickSrp/workSrp: skip a centre this long when an unbuilt ruin's 5x5 overlaps it
    static final int SRP_SKIP_MONEY = 300;           // Soldier.pickSrp: ...when it disagrees with an overlapping money tower's pattern (t104)
    static final int SRP_SKIP_ENEMY_MEM = 60;        // Soldier.pickSrp: ...when the map memory shows enemy paint in it
    static final int SRP_SKIP_ENEMY = 80;            // Soldier.srpScan: ...when enemy paint is seen in it
    static final int SRP_ENEMY_TOWER_R2 = 25;        // Soldier.workSrp: drop an SRP whose centre is within this d2 of the remembered enemy tower...
    static final int SRP_SKIP_ENEMY_TOWER = 100;     // ...and skip it this long

    // ================================ splasher (paint capacity 300) ================================
    static final int SPL_REFILL = 100;               // Splasher.turn: refill below this (y148/y152/y156/y162 75; y149 60; y234 80)
    static final int SPL_SCORE_FIRST = 9;            // Splasher.turn: splash before moving only at this score (y233 7)
    static final int SPL_SCORE_AFTER = 6;            // Splasher.turn: splash after the move at this score
    static final int SPL_STANDOFF_PAINT = 50;        // Splasher.turn: stand-off only with this much paint (t111 crowned; t112 30; t114/y237/y242 70; t115 90); the other 50s are the splash cost
    static final int SPL_STANDOFF_BC = 6000;         // Splasher.turn: stand-off search only above this many bytecodes left (y236 4000)
    static final int SPL_FRONTIER_BC = 5000;         // Splasher.turn: frontier search only above this
    static final int SPL_FRONTIER_ROUNDS = 8;        // Splasher.turn: chase the frontier only within this many rounds of lastSplash, else explore (t58 crowned; y146 5; y147/y235 12)
    static final int SPL_IDLE_CLAMP = 4;             // Splasher.turn: a turn that cannot splash raises lastSplash to at least round - this
    static final int SPL_AFTER_BC = 2500;            // Splasher.turn: the after-move splash only above this many bytecodes left
    static final int SPL_TOWER_VALUE = 50; // y344 (was 30)           // Splasher.towersIntoGrid: an enemy tower's grid value (t20/t50 crowned, was 12; y166/y169 50; y232 45; y174/y177/y184 15)
    static final int SPL_EMPTY_VALUE = 1;            // Splasher.sense splash grid: an empty tile, inner 3x3 and outer ring
    static final int SPL_ENEMY_VALUE = 2;            // Splasher.sense splash grid: an enemy tile, inner 3x3 only
    static final int SPL_SRP_GUARD = -50;            // Splasher.sense splash grid: our secondary paint where the SRP lattice wants it (rules the splash out)
    static final int SPL_FRONTIER_MIN_R2 = 5;        // Splasher.frontier: only tiles at least this far
    static final int SPL_FRONTIER_ENEMY = 3;         // Splasher.frontier: an enemy tile counts this much nearer

    // ================================ mopper (paint capacity 100) ================================
    static final int MOP_REFILL = 40;                // Mopper.turn: refill below this (gate at the call and refill's threshold)
    static final int MOP_ENEMY_PAINT = 10;           // Mopper.act mop score: an enemy-painted tile
    static final int MOP_ENEMY_ROBOT = 15;           // Mopper.act mop score: an enemy robot on the tile
    static final int MOP_RUIN_MOP_BONUS = 40;        // Mopper.act mop score: beside a ruin with no enemy tower (t74 crowned, was 10; y167 80 and y168 20, both with MOP_RUIN_CHASE_BONUS)
    static final int MOP_GIVE_ABOVE = 60;            // Mopper.act (gate of the give stage): give paint only above this much
    static final int MOP_GIVE_BELOW_PCT = 40;        // Mopper.act give: ...to an adjacent soldier/splasher below this % of its capacity...
    static final int MOP_GIVE_KEEP = 40;             // Mopper.act give: ...keeping this much
    static final int MOP_DEFEND_R2 = 25;             // Mopper.target: an enemy robot within this d2 of a known tower of ours... (y207 36)
    static final int MOP_DEFEND_BONUS = 40;          // ...counts this much nearer (y220 60)
    static final int MOP_TILE_EXTRA = 2;             // Mopper.target: an enemy tile counts this much farther than a robot
    static final int MOP_RUIN_CHASE_BONUS = 40;      // Mopper.target: enemy paint beside a ruin counts this much nearer (t74 crowned, was 6; y167 80; y168 20)

    // ================================ every robot: Unit (refill, dry flags, churn wait, explore) ================================
    static final int REFILL_STOP_NUM = 3;            // Unit.refill: a refill ends at NUM/DEN of capacity
    static final int REFILL_STOP_DEN = 4;
    static final int REFILL_PAINT_NUM = 7;           // Unit.refill: a paint tower's d2 counts NUM/DEN (paint towers preferred)
    static final int REFILL_PAINT_DEN = 10;
    static final int DRY_PAINT_ROUNDS = 10;          // Unit.refill: a dry flag on a paint tower lasts this many rounds (t116/t122 crowned, was 40; y254 5; y264 20)
    static final int DRY_ROUNDS = 60; // y328 (was 40)                // Unit.refill: a dry flag on another tower lasts this many rounds
    static final int DRY_CLEAR_PAINT = 50;           // Unit.refill: a flagged tower in sight holding this much is unflagged (y260/y266/y270 25; y263 10; y267 35)
    static final int DRY_ADJ_PAINT = 20;             // Unit.refill: an adjacent tower holding less than this is flagged dry
    static final int DRY_FAR_PAINT = 40;             // Unit.refill: a tower in sight holding less than min(this, our room) is flagged dry (t57 50)
    static final int CHURN_WAIT_ROUNDS = 2; // y323 (study 13 2.1: waiters hit 0 paint after a median 3 rounds)          // Unit.refill: wait this many rounds beside a drained money tower for its churn
    static final int CHURN_WAIT_RESET = 50;          // Unit.refill: a wait older than this starts over
    static final int EXPLORE_REACHED_R2 = 8;         // Unit.exploreTarget: the target is reached within this d2
    static final int EXPLORE_TIMEOUT = 90;           // Unit.exploreTarget: renewed after this many rounds (y201 40; y211 crowned 60; y216/y221 crowned 90; y224/y229 75; y223 120)
    static final int EXPLORE_DRAWS = 128;            // Unit.exploreTarget: random draws for a never-seen tile (t88 8; y195 crowned 16; y200/y204 32; y203/y205 64; y211 crowned 128; y217 192)

    // ================================ movement: Nav ================================
    static final int NAV_RETARGET_R2 = 8;            // Nav.moveTo: a new target within this d2 of the old keeps the wall-follow state
    static final int NAV_PAINT_WEIGHT = 8; // y316 (y312 4)           // Nav.moveTo: greedy step score = d2 + this * paint cost of the tile
    static final int NAV_ROBOT_WAIT = 3;             // Nav.moveTo: turns to wait on a robot before wall following
}

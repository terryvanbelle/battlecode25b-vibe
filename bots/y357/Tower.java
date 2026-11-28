package y357;

import battlecode.common.*;

/** Towers: attack (single + area, both free each turn), spawn units, upgrade, churn. Tower code reads no Clock, so
 *  its bytecode count does not steer any decision (the tower limit, 20000, is far above what a turn uses). */
public strictfp class Tower {
    static int built;   // units this tower has built, the opening's too; indexes the spawn cycles

    /** A tower's turn, in order; each step runs when its gate holds. */
    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        attack();                                                   // 1. shoot: single target, then the area attack
        if (rc.isActionReady()) build();                            // 2. spawn (choose, reserve, can't pay -> wait)
        if (rc.canUpgradeTower(G.here)) upgrade();                  // 3. upgrade out of a surplus
        // 4. churn (Churn.towerTurn checks the adjacent helper and the pattern): an L1 money tower below
        //    CHURN_PAINT paint, CHURN_CHIPS chips, no enemy in view
        if (rc.getType() == UnitType.LEVEL_ONE_MONEY_TOWER && rc.getPaint() < Tune.CHURN_PAINT && G.chips >= Tune.CHURN_CHIPS
                && G.enemies.length == 0 && Churn.towerTurn()) return;
        G.ind = "b" + built + " sym" + Sym.live;
    }

    static void attack() throws GameActionException {
        RobotController rc = G.rc;
        RobotInfo[] en = G.enemies;
        if (en.length == 0) return;
        RobotInfo best = null; int bestScore = Integer.MAX_VALUE;
        for (RobotInfo e : en) {
            if (!rc.canAttack(e.location)) continue;
            // finish the weakest first; soldiers and splashers threaten towers more than moppers
            int s = e.health - (e.type == UnitType.MOPPER ? 0 : Tune.TWR_SHOT_NONMOPPER) - (e.type.isTowerType() ? -Tune.TWR_SHOT_TOWER : 0);
            if (s < bestScore) { bestScore = s; best = e; }
        }
        if (best != null) rc.attack(best.location);
        if (rc.canAttack(null)) rc.attack(null);
    }

    // ---- spawn policy: choose() picks the unit (overrides, then the cycle), reserve() the chips kept back for
    // towers, build() pays or waits.
    static final UnitType S = UnitType.SOLDIER, X = UnitType.SPLASHER, M = UnitType.MOPPER;
    /** Spawn cycles per tower kind and phase, indexed by built % 6. */
    static final UnitType[] OPENING = {S, S, S, S, S, S};       // round < OPENING_SOLDIERS_UNTIL, every tower
    // paint towers, the only ones with paint for splashers: 2 soldiers, 3 splashers, 1 mopper per six (t27; the
    // unit audit: the top teams field about one splasher per soldier)
    static final UnitType[] PAINT_CYCLE = {S, X, X, M, S, X};
    // money and defense towers: half moppers. A money tower never gains paint and build() waits without advancing
    // `built`, so in practice it stalls for good at the first unit it cannot pay (slot 1 or 2).
    static final UnitType[] OTHER_CYCLE = {S, M, X, M, S, M};

    static boolean rc_isPaintTower() { return Towers.kindOf(G.rc.getType()) == Towers.PAINT; }

    /** The unit to build next: the first override that fires, else the cycle entry. Overrides (first match wins):
     *  none today; add them here as `if (condition) return TYPE;` above the cycle lookup. */
    static UnitType choose() {
        UnitType[] cycle = G.round < Tune.OPENING_SOLDIERS_UNTIL ? OPENING : rc_isPaintTower() ? PAINT_CYCLE : OTHER_CYCLE;
        return cycle[built % 6];
    }

    /** Chips kept back so soldiers at ruins can complete towers (study 3 tactic 1); the first rule that fires wins:
     *  1. before round SPAWN_RESERVE_FROM: none;  2. at SPAWN_RESERVE_TOWERS towers or more: none;
     *  3. a mopper is due and an enemy robot is within d2 DEFEND_MOPPER_R2 (study 3 tactic 5): none;
     *  4. else SPAWN_RESERVE. */
    static int reserve(UnitType t) {
        if (G.round < Tune.SPAWN_RESERVE_FROM) return 0;
        if (G.rc.getNumberTowers() >= Tune.SPAWN_RESERVE_TOWERS) return 0;
        if (t == UnitType.MOPPER) for (RobotInfo e : G.enemies) if (!e.type.isTowerType() && G.here.distanceSquaredTo(e.location) <= Tune.DEFEND_MOPPER_R2) return 0;
        return Tune.SPAWN_RESERVE;
    }

    /** Build choose()'s unit on the buildable tile nearest the map centre (G.rand breaks ties). Can't pay -> wait:
     *  with chips below its cost + min(reserve, SPAWN_ANYWAY_CHIPS), or paint below its paint cost, return without
     *  building and without advancing `built`, so the same unit is due next turn (the money-tower stall above). */
    static void build() throws GameActionException {
        RobotController rc = G.rc;
        UnitType t = choose();
        if (G.chips < t.moneyCost + Math.min(reserve(t), Tune.SPAWN_ANYWAY_CHIPS) || G.paint < t.paintCost) return;   // can't pay -> wait
        MapLocation here = G.here;
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        MapLocation goal = G.center;
        for (MapLocation l : rc.getAllLocationsWithinRadiusSquared(here, GameConstants.BUILD_ROBOT_RADIUS_SQUARED)) {
            if (!rc.canBuildRobot(t, l)) continue;
            int d = l.distanceSquaredTo(goal) * 4 + G.rand(4);
            if (d < bestD) { bestD = d; best = l; }
        }
        if (best != null) { rc.buildRobot(t, best); built++; }
    }

    /** Upgrade out of a surplus: paint towers at next cost + UPGRADE_SPARE, money towers at next cost + UPGRADE_SPARE
     *  + MONEY_UPGRADE_EXTRA, defense towers never (paint binds once the economy runs). Gate at the call site:
     *  rc.canUpgradeTower. G.chips is as at turn start (build() does not refresh it). */
    static void upgrade() throws GameActionException {
        RobotController rc = G.rc;
        int need = rc.getType().getNextLevel().moneyCost + Tune.UPGRADE_SPARE;
        int k = Towers.kindOf(rc.getType());
        if (k == Towers.PAINT && G.chips >= need) rc.upgradeTower(G.here);
        else if (k == Towers.MONEY && G.chips >= need + Tune.MONEY_UPGRADE_EXTRA) rc.upgradeTower(G.here);
    }
}

package y216;

import battlecode.common.*;

/** Towers: attack (single + area, both free each turn), build units, upgrade. */
public strictfp class Tower {
    static int built;
    static final int UPGRADE_SPARE = 1200;

    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        attack();
        if (rc.isActionReady()) build();
        upgrade();
        if (churn()) return;
        G.ind = "b" + built + " sym" + Sym.live;
    }

    static final int CHURN_CHIPS = 2000;

    /** study 3 tactic 4: a drained L1 money tower with its pattern intact and an ally robot adjacent (who can rebuild it
     *  at once: completing needs no cooldown or paint) disintegrates, so the rebuilt tower brings a fresh 500 paint. */
    static boolean churn() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.getType() != UnitType.LEVEL_ONE_MONEY_TOWER || rc.getPaint() >= 10 || G.chips < CHURN_CHIPS) return false;
        if (G.enemies.length > 0) return false;
        boolean helper = false;
        for (RobotInfo a : rc.senseNearbyRobots(2, G.me)) if (a.type.isRobotType()) { helper = true; break; }
        if (!helper) return false;
        int pat = Soldier.patternOf(UnitType.LEVEL_ONE_MONEY_TOWER);
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = G.here.translate(dx, dy);
            if (!rc.canSenseLocation(l)) return false;
            PaintType p = rc.senseMapInfo(l).getPaint();
            if (!p.isAlly() || p.isSecondary() != Soldier.bit(pat, dx, dy)) return false;
        }
        G.forgetTower(G.here);
        rc.disintegrate();
        return true;
    }

    static void attack() throws GameActionException {
        RobotController rc = G.rc;
        RobotInfo[] en = G.enemies;
        if (en.length == 0) return;
        RobotInfo best = null; int bestScore = Integer.MAX_VALUE;
        for (RobotInfo e : en) {
            if (!rc.canAttack(e.location)) continue;
            // finish the weakest first; soldiers and splashers threaten towers more than moppers
            int s = e.health - (e.type == UnitType.MOPPER ? 0 : 60) - (e.type.isTowerType() ? -10000 : 0);
            if (s < bestScore) { bestScore = s; best = e; }
        }
        if (best != null) rc.attack(best.location);
        if (rc.canAttack(null)) rc.attack(null);
    }

    static UnitType choose() {
        int r = G.round;
        int enemyNear = G.enemies.length;
        for (RobotInfo e : G.enemies) if (e.type == UnitType.MOPPER) enemyNear--;
        int k = built % 6;
        if (r < 80) return UnitType.SOLDIER;
        // unit audit: the top teams field about one splasher per soldier; paint towers (the only ones with paint for
        // splashers) alternate soldier and splasher with a mopper every third
        if (rc_isPaintTower()) return k % 4 == 3 ? UnitType.MOPPER : (k % 4 == 0 ? UnitType.SOLDIER : UnitType.SPLASHER);   // S X X M
        // mid game: splashers do the bulk of the painting; soldiers keep building towers; moppers clean
        // a third moppers: they drain enemy robots, clean ruins and feed allies
        switch (k) {
            case 0: return UnitType.SOLDIER;
            case 1: return UnitType.MOPPER;
            case 2: return UnitType.SPLASHER;
            case 3: return UnitType.MOPPER;
            case 4: return UnitType.SOLDIER;
            default: return UnitType.MOPPER;
        }
    }

    static boolean rc_isPaintTower() { return G.kind(G.rc.getType()) == 1; }

    static void build() throws GameActionException {
        RobotController rc = G.rc;
        UnitType t = choose();
        // keep a reserve for towers once the opening is done, so soldiers at ruins can complete them
        // study 4 2.1: freeze spawns 8 rounds in 20 below 1000 + cost, so chips reach 1000 for finished patterns
        int reserve = G.round < 40 ? 0 : (rc.getNumberTowers() < 25 ? 1000 /* study 3 tactic 1: spawn only at 1000 + cost */ : 0);
        // study 3 tactic 5: with an enemy robot within d2 20, a mopper spawns even below the reserve
        if (t == UnitType.MOPPER) for (RobotInfo e : G.enemies) if (!e.type.isTowerType() && G.here.distanceSquaredTo(e.location) <= 20) { reserve = 0; break; }
        if (G.chips < t.moneyCost + reserve && !(G.chips >= 1000 + t.moneyCost)) return;
        if (G.paint < t.paintCost) return;
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

    static void upgrade() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.canUpgradeTower(G.here)) return;
        UnitType next = rc.getType().getNextLevel();
        // upgrade out of a surplus: paint towers first (paint binds once the economy runs), money towers later
        int need = next.moneyCost + UPGRADE_SPARE;
        if (G.kind(rc.getType()) == 1 && G.chips >= need) rc.upgradeTower(G.here);
        else if (G.kind(rc.getType()) == 2 && G.chips >= need + 2500) rc.upgradeTower(G.here);
    }
}

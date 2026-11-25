package sw07;

import battlecode.common.*;

/** Towers: attack (single + area, both free each turn), build units, upgrade. */
public strictfp class Tower {
    static int built;
    static final int PAINT_KEEP = 200;
    static final int UPGRADE_SPARE = 800;

    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        attack();
        if (rc.isActionReady()) build();
        upgrade();
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
            int s = e.health - (e.type == UnitType.MOPPER ? 0 : 60) - (e.type.isTowerType() ? -10000 : 0);
            if (s < bestScore) { bestScore = s; best = e; }
        }
        if (best != null) rc.attack(best.location);
        if (rc.canAttack(null)) rc.attack(null);
    }

    static UnitType choose() {
        int r = G.round;
        if (built < 3) return UnitType.SOLDIER;
        int enemyNear = G.enemies.length;
        for (RobotInfo e : G.enemies) if (e.type == UnitType.MOPPER) enemyNear--;
        int k = built % 6;
        if (r < 80) return k == 2 ? UnitType.MOPPER : UnitType.SOLDIER;
        // mid game: splashers do the bulk of the painting; soldiers keep building towers; moppers clean
        switch (k) {
            case 0: return UnitType.SOLDIER;
            case 1: return UnitType.SPLASHER;
            case 2: return UnitType.MOPPER;
            case 3: return UnitType.SPLASHER;
            case 4: return UnitType.SOLDIER;
            default: return UnitType.SPLASHER;
        }
    }

    static void build() throws GameActionException {
        RobotController rc = G.rc;
        UnitType t = choose();
        // keep a reserve for towers once the opening is done, so soldiers at ruins can complete them
        int reserve = G.round < 40 ? 0 : (rc.getNumberTowers() < 25 ? 600 : 0);
        if (G.chips < t.moneyCost + reserve && !(G.chips >= 1000 + t.moneyCost)) return;
        // keep paint in the tower for refills: units already paid for are cheaper to keep alive than new ones
        if (G.paint < t.paintCost + (G.round < 30 ? 0 : PAINT_KEEP)) return;
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
        else if (G.kind(rc.getType()) == 2 && G.chips >= need + 1000) rc.upgradeTower(G.here);
    }
}

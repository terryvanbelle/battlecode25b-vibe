package t151;

import battlecode.common.*;

/** Moppers: swing at enemy robots, mop enemy paint (ruin pattern areas and ground under enemies first), give paint
 *  to low allies, and hunt enemy paint near our territory. */
public strictfp class Mopper {
    /** A mopper's turn, in order; each step runs when its gate holds. Mopper code reads no Clock. After it,
     *  RobotPlayer runs the free actions Churn.rebuild and Unit.topUp. */
    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.isActionReady()) act();                                            // 1. act (swing / mop / give)
        // 2. refill below MOP_REFILL paint. This gate is the whole gate for moppers (refill's own threshold test
        //    never fires below it); it also ends a refill walk once paint is back to MOP_REFILL.
        if (G.paint < Tune.MOP_REFILL && Unit.refill(Tune.MOP_REFILL)) return;
        // 3. move toward the target (else explore). Unit audit (owner prompt #15): moppers chasing enemy paint ended
        //    44% of those turns on it (double drain for moppers); mop reaches r2 2, so stop once in reach
        MapLocation goal = target();
        if (goal != null && G.here.distanceSquaredTo(goal) <= 2) goal = G.here;
        Nav.moveTo(goal != null ? goal : Unit.exploreTarget());
        if (rc.isActionReady()) act();                                            // 4. act again
    }

    /** The mopper's action, an ordered list where the first stage that acts ends it:
     *  1. swing toward the side holding the most enemy robots, if that is two or more;
     *  2. mop the best tile in reach (d2 2): an enemy robot standing on enemy paint first, then enemy paint, pattern
     *     areas weighing more (MOP_ENEMY_PAINT, MOP_ENEMY_ROBOT, MOP_RUIN_MOP_BONUS);
     *  3. with more than MOP_GIVE_ABOVE paint, give to the neediest adjacent soldier/splasher below MOP_GIVE_BELOW_PCT
     *     of its capacity, keeping MOP_GIVE_KEEP.
     *  Kept as one method on purpose: splitting the stages into methods changes a mopper's bytecode count by -6..+22
     *  per turn (a call to our own method is free, each return costs 1), and moppers do reach the 17500 limit
     *  (17502 seen on DefaultHuge), so the turns that overrun could change. */
    static void act() throws GameActionException {
        RobotController rc = G.rc;
        // 1. swing
        Direction bestDir = null; int bestN = 1;
        for (Direction d : new Direction[]{Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST}) {
            if (!rc.canMopSwing(d)) continue;
            int n = 0;
            // the engine's swing: the 3x2 block 1..2 tiles ahead, one tile either side (InternalRobot.mopSwing)
            for (RobotInfo e : G.enemies) {
                if (!e.type.isRobotType()) continue;
                int lx = e.location.x - G.here.x, ly = e.location.y - G.here.y;
                int f = lx * d.dx + ly * d.dy, lat = lx * d.dy - ly * d.dx;
                if (f >= 1 && f <= 2 && lat >= -1 && lat <= 1) n++;
            }
            if (n > bestN) { bestN = n; bestDir = d; }
        }
        if (bestDir != null) { rc.mopSwing(bestDir); return; }
        // 2. mop
        MapLocation best = null; int bestS = 0;
        for (MapInfo mi : rc.senseNearbyMapInfos(G.here, 2)) {
            MapLocation l = mi.getMapLocation();
            int s = 0;
            if (mi.getPaint().isEnemy()) s += Tune.MOP_ENEMY_PAINT;
            RobotInfo r = rc.canSenseRobotAtLocation(l) ? rc.senseRobotAtLocation(l) : null;
            if (r != null && r.team == G.them && r.type.isRobotType()) s += Tune.MOP_ENEMY_ROBOT;
            if (s > 0 && nearRuin(l)) s += Tune.MOP_RUIN_MOP_BONUS;   // study 6 2.1: their moppers clean ruins 14x to our 0 (was 10)
            if (s > bestS && rc.canAttack(l)) { bestS = s; best = l; }
        }
        if (best != null) { rc.attack(best); G.paint = rc.getPaint(); return; }
        // 3. give (gate: paint > MOP_GIVE_ABOVE)
        if (G.paint > Tune.MOP_GIVE_ABOVE) {
            RobotInfo need = null; int needP = Integer.MAX_VALUE;
            for (RobotInfo a : G.allies) {
                if (a.type == UnitType.MOPPER || !a.type.isRobotType()) continue;
                if (a.location.distanceSquaredTo(G.here) > 2) continue;
                int frac = a.paintAmount * 100 / a.type.paintCapacity;
                if (frac < Tune.MOP_GIVE_BELOW_PCT && frac < needP) { needP = frac; need = a; }
            }
            if (need != null) {
                int amt = Math.min(G.paint - Tune.MOP_GIVE_KEEP, need.type.paintCapacity - need.paintAmount);
                if (amt > 0 && rc.canTransferPaint(need.location, amt)) { rc.transferPaint(need.location, amt); G.paint = rc.getPaint(); }
            }
        }
    }

    static boolean nearRuin(MapLocation l) {
        for (MapLocation r : G.ruins) if (r.distanceSquaredTo(l) <= 8) {   // the ruin's 5x5
            // study 7 2.5: skip ruins under an enemy tower (mopping beside enemy towers rose 2.2% -> 3.9% with t74)
            boolean enemyTower = false;
            for (RobotInfo e : G.enemies) if (e.location.equals(r)) { enemyTower = true; break; }
            if (!enemyTower) return true;
        }
        return false;
    }

    /** Nearest enemy robot (not tower) or enemy-painted tile, enemy paint near ruins counting as nearer. */
    static MapLocation target() {
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (RobotInfo e : G.enemies) {
            if (!e.type.isRobotType()) continue;
            int d = G.here.distanceSquaredTo(e.location);
            // defend: enemy robots within reach of one of our towers come first
            for (int i = G.nTowers; --i >= 0; ) if (Towers.loc[i].distanceSquaredTo(e.location) <= Tune.MOP_DEFEND_R2) { d -= Tune.MOP_DEFEND_BONUS; break; }
            if (d < bestD) { bestD = d; best = e.location; }
        }
        for (MapInfo mi : G.infos) {
            if (!mi.getPaint().isEnemy()) continue;
            MapLocation l = mi.getMapLocation();
            int d = G.here.distanceSquaredTo(l) + Tune.MOP_TILE_EXTRA;
            if (nearRuin(l)) d -= Tune.MOP_RUIN_CHASE_BONUS;   // study 6 2.1 (was 6)
            if (d < bestD) { bestD = d; best = l; }
        }
        return best;
    }
}

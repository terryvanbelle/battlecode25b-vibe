package t97;

import battlecode.common.*;

/** Moppers: swing at enemy robots, mop enemy paint (ruin pattern areas and ground under enemies first), give paint
 *  to low allies, and hunt enemy paint near our territory. */
public strictfp class Mopper {
    static final int DEFEND_R2 = 25, DEFEND_BONUS = 40;
    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.isActionReady()) act();
        if (G.paint < 40 && Unit.refill(40)) return;
        MapLocation goal = target();
        // unit audit (owner prompt #15): moppers chasing enemy paint ended 44% of those turns on it (double drain for
        // moppers); mop reaches r2 2, so stop once in reach
        if (goal != null && G.here.distanceSquaredTo(goal) <= 2) goal = G.here;
        if (goal == null) goal = memRuin();   // study 7 2.3
        Nav.moveTo(goal != null ? goal : Unit.exploreTarget());
        if (rc.isActionReady()) act();
    }

    static void act() throws GameActionException {
        RobotController rc = G.rc;
        // 1. swing at two or more enemy robots
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
        // 2. mop: enemy robot standing on enemy paint first, then enemy paint (pattern areas weigh more)
        MapLocation best = null; int bestS = 0;
        for (MapInfo mi : rc.senseNearbyMapInfos(G.here, 2)) {
            MapLocation l = mi.getMapLocation();
            int s = 0;
            if (mi.getPaint().isEnemy()) s += 10;
            RobotInfo r = rc.canSenseRobotAtLocation(l) ? rc.senseRobotAtLocation(l) : null;
            if (r != null && r.team == G.them && r.type.isRobotType()) s += 15;
            if (s > 0 && nearRuin(l)) s += 40;   // study 6 2.1: their moppers clean ruins 14x to our 0 (was 10)
            if (s > bestS && rc.canAttack(l)) { bestS = s; best = l; }
        }
        if (best != null) { rc.attack(best); G.paint = rc.getPaint(); return; }
        // 3. give paint to the neediest adjacent soldier/splasher when we have spare
        if (G.paint > 60) {
            RobotInfo need = null; int needP = Integer.MAX_VALUE;
            for (RobotInfo a : G.allies) {
                if (a.type == UnitType.MOPPER || !a.type.isRobotType()) continue;
                if (a.location.distanceSquaredTo(G.here) > 2) continue;
                int frac = a.paintAmount * 100 / a.type.paintCapacity;
                if (frac < 40 && frac < needP) { needP = frac; need = a; }
            }
            if (need != null) {
                int amt = Math.min(G.paint - 40, need.type.paintCapacity - need.paintAmount);
                if (amt > 0 && rc.canTransferPaint(need.location, amt)) { rc.transferPaint(need.location, amt); G.paint = rc.getPaint(); }
            }
        }
    }

    // study 7 2.3: at r100, 22 free ruins in our half held 1-4 enemy tiles against a median 19.5 of ours; they never
    // came clean and our moppers mopped there 0 times in the next 50 rounds. A mopper with nothing in view walks to
    // the nearest remembered ruin out of view with no tower, 1-8 enemy tiles in its 5x5 and at least as many of ours.
    static MapLocation memGoal;
    static int memAt = -100;
    static MapLocation memRuin() {
        if (G.round - memAt < 5 && memGoal != null && G.here.distanceSquaredTo(memGoal) > 20) return memGoal;
        memAt = G.round; memGoal = null;
        int w = G.W, h = G.H;
        int[] m = G.mem;
        int bestD = Integer.MAX_VALUE;
        for (int i = G.nRuins; --i >= 0; ) {
            MapLocation r = G.ruinList[i];
            int d = G.here.distanceSquaredTo(r);
            if (d >= bestD || d <= 20 || (m[r.x + r.y * w] & 8) != 0) continue;
            int ours = 0, theirs = 0;
            for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
                int x = r.x + dx, y = r.y + dy;
                if (x < 0 || y < 0 || x >= w || y >= h) continue;
                int p = m[x + y * w] >> 4;
                if (p >= 3) theirs++; else if (p >= 1) ours++;
            }
            if (theirs >= 1 && theirs <= 8 && ours >= theirs) { memGoal = r; bestD = d; }
        }
        return memGoal;
    }

    static boolean nearRuin(MapLocation l) {
        for (MapLocation r : G.ruins) if (r.distanceSquaredTo(l) <= 8) {
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
            for (int i = G.nTowers; --i >= 0; ) if (G.towerLoc[i].distanceSquaredTo(e.location) <= DEFEND_R2) { d -= DEFEND_BONUS; break; }
            if (d < bestD) { bestD = d; best = e.location; }
        }
        for (MapInfo mi : G.infos) {
            if (!mi.getPaint().isEnemy()) continue;
            MapLocation l = mi.getMapLocation();
            int d = G.here.distanceSquaredTo(l) + 2;
            if (nearRuin(l)) d -= 40;   // study 6 2.1 (was 6)
            if (d < bestD) { bestD = d; best = l; }
        }
        return best;
    }
}

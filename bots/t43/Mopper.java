package t43;

import battlecode.common.*;

/** Moppers: swing at enemy robots, mop enemy paint (ruin pattern areas and ground under enemies first), give paint
 *  to low allies, and hunt enemy paint near our territory. */
public strictfp class Mopper {
    static final int DEFEND_R2 = 25, DEFEND_BONUS = 40;
    // ---- study 4 2.2: a mopper called to a contested ruin (G.MSG_GO from the tower that spawned it) unpaints the
    // enemy tiles of its 5x5 first
    static MapLocation goRuin, goTile;
    static int goSince;
    static final int GO_MAX = 80;

    static void readGo() throws GameActionException {
        Message[] ms = G.rc.readMessages(-1);
        for (int i = ms.length; --i >= 0; ) {
            int m = ms[i].getBytes();
            if (G.msgKind(m) == G.MSG_GO) { goRuin = G.msgLoc(m); goSince = G.round; return; }
        }
    }

    /** Update the ruin job: the nearest enemy tile of its 5x5 (goTile), or the ruin while it is out of sight. */
    static void ruinJob() throws GameActionException {
        RobotController rc = G.rc;
        goTile = null;
        MapLocation r = goRuin;
        if (G.round - goSince > GO_MAX) { goRuin = null; return; }
        if (!rc.canSenseLocation(r)) { goTile = r; return; }
        if (rc.senseRobotAtLocation(r) != null) { goRuin = null; return; }
        int bestD = Integer.MAX_VALUE, unseen = 0;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            MapLocation l = r.translate(dx, dy);
            if (!rc.canSenseLocation(l)) { unseen++; continue; }
            if (!rc.senseMapInfo(l).getPaint().isEnemy()) continue;
            int d = G.here.distanceSquaredTo(l);
            if (d < bestD) { bestD = d; goTile = l; }
        }
        if (goTile == null) {
            if (unseen > 0) { goTile = r; return; }
            // clean: finish the tower if the pattern is complete (any robot adjacent can), then the job is done
            if (G.here.distanceSquaredTo(r) <= 2) {
                UnitType t = Soldier.readMarks(r);
                if (t != null && rc.canCompleteTowerPattern(t, r)) { rc.completeTowerPattern(t, r); G.noteTower(r, G.kind(t)); }
            }
            goRuin = null;
        }
    }

    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        if (goRuin == null && G.round - G.born <= 4) readGo();
        if (goRuin != null) ruinJob();
        if (rc.isActionReady()) act();
        if (goRuin != null) { ruinJob(); if (goRuin != null) G.ind += " go" + goRuin; }
        if (G.paint < 40 && Unit.refill(40)) return;
        MapLocation goal = goTile != null ? goTile : target();
        // unit audit (owner prompt #15): moppers chasing enemy paint ended 44% of those turns on it (double drain for
        // moppers); mop reaches r2 2, so stop once in reach
        if (goal != null && G.here.distanceSquaredTo(goal) <= 2) goal = G.here;
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
            if (s > 0 && nearRuin(l)) s += 10;
            if (s > 0 && goRuin != null && Math.abs(l.x - goRuin.x) <= 2 && Math.abs(l.y - goRuin.y) <= 2) s += 20;
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

    static boolean nearRuin(MapLocation l) {
        for (MapLocation r : G.ruins) if (r.distanceSquaredTo(l) <= 8) return true;
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
            if (nearRuin(l)) d -= 6;
            if (d < bestD) { bestD = d; best = l; }
        }
        return best;
    }
}

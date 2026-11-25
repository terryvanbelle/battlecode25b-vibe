package y48;

import battlecode.common.*;

/** Helpers shared by soldiers, splashers and moppers. */
public strictfp class Unit {
    static MapLocation explore;
    static int exploreSince;
    static MapLocation refillAt;            // the tower being walked to for paint
    static int[] towerDry = new int[32];    // round a known tower was seen without paint (index as G.towerLoc)
    static MapLocation enemyTower;          // the nearest enemy tower seen (cleared when seen gone)

    /** Refill from an ally tower when paint < threshold. True while busy with it (moving or withdrawing). */
    static boolean refill(int threshold) throws GameActionException {
        RobotController rc = G.rc;
        if (G.paint >= threshold && refillAt == null) return false;
        int cap = G.type.paintCapacity;
        if (refillAt != null && G.paint >= cap * 3 / 4) { refillAt = null; return false; }
        // choose the nearest known tower that is not known dry; paint towers count as 30% closer
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (int i = G.nTowers; --i >= 0; ) {
            MapLocation l = G.towerLoc[i];
            if (towerDry[i] > 0 && G.round - towerDry[i] < 40) continue;
            int d = G.here.distanceSquaredTo(l);
            if (G.towerKind[i] == 1) d = d * 7 / 10;
            if (d < bestD) { bestD = d; best = l; }
        }
        if (best == null) { refillAt = null; return false; }
        refillAt = best;
        if (rc.canSenseLocation(best)) {
            RobotInfo t = rc.senseRobotAtLocation(best);
            if (t == null || t.team != G.me || !t.type.isTowerType()) { G.forgetTower(best); refillAt = null; return false; }
            int take = Math.min(cap - G.paint, t.paintAmount);
            if (G.here.distanceSquaredTo(best) <= 2) {
                if (take > 0 && rc.canTransferPaint(best, -take)) {
                    rc.transferPaint(best, -take);
                    G.paint = rc.getPaint();
                    if (G.paint >= cap * 3 / 4) refillAt = null;
                    return true;
                }
                if (t.paintAmount < 20) markDry(best);
                if (!rc.isActionReady()) return true;   // wait for the cooldown next to the tower
                refillAt = null;
                return false;
            }
            if (t.paintAmount < Math.min(40, cap - G.paint)) { markDry(best); }
        }
        Nav.moveTo(best);
        G.ind += " refill" + best;
        return true;
    }

    /** study 3 tactic 3: with the action still unused, top up to full from any adjacent ally tower holding paint. */
    static void topUp() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady()) return;
        int cap = G.type.paintCapacity, p = rc.getPaint();
        if (p >= cap) return;
        MapLocation me = rc.getLocation();
        for (RobotInfo a : rc.senseNearbyRobots(2, G.me)) {
            if (!a.type.isTowerType() || a.paintAmount <= 0) continue;
            int take = Math.min(cap - p, a.paintAmount);
            if (rc.canTransferPaint(a.location, -take)) { rc.transferPaint(a.location, -take); G.paint = rc.getPaint(); return; }
        }
    }

    static void markDry(MapLocation l) {
        for (int i = G.nTowers; --i >= 0; ) if (G.towerLoc[i].equals(l)) towerDry[i] = G.round;
    }

    /** A wandering target: a random tile, renewed when reached, after a timeout, or when it is known terrain. */
    static MapLocation exploreTarget() {
        if (explore == null || G.here.distanceSquaredTo(explore) <= 8 || G.round - exploreSince > 60
                || G.isWall(explore)) {
            explore = new MapLocation(G.rand(G.W), G.rand(G.H));
            exploreSince = G.round;
        }
        return explore;
    }

    /** Remember the nearest visible enemy tower; forget a remembered one that is visibly gone. */
    static void scanEnemyTowers() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (RobotInfo e : G.enemies) {
            if (!e.type.isTowerType()) continue;
            int d = G.here.distanceSquaredTo(e.location);
            if (d < bestD) { bestD = d; best = e.location; }
        }
        if (best != null) enemyTower = best;
        else if (enemyTower != null && rc.canSenseLocation(enemyTower)) {
            RobotInfo r = rc.senseRobotAtLocation(enemyTower);
            if (r == null || r.team == G.me) enemyTower = null;
        }
    }
}

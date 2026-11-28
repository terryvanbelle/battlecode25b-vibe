package y340;

import battlecode.common.*;

/** Helpers shared by soldiers, splashers and moppers. */
public strictfp class Unit {
    static MapLocation explore;
    static int exploreSince;
    static MapLocation refillAt;            // the tower being walked to for paint
    static MapLocation enemyTower;          // the nearest enemy tower seen (cleared when seen gone); soldiers and splashers only

    /** Refill from an ally tower when paint < threshold. True while busy with it (moving or withdrawing). */
    static boolean refill(int threshold) throws GameActionException {
        RobotController rc = G.rc;
        if (G.paint >= threshold && refillAt == null) return false;
        int cap = G.type.paintCapacity;
        if (refillAt != null && G.paint >= cap * Tune.REFILL_STOP_NUM / Tune.REFILL_STOP_DEN) { refillAt = null; return false; }
        // choose the nearest known tower that is not known dry; paint towers count as 30% closer
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (int i = G.nTowers; --i >= 0; ) {
            MapLocation l = Towers.loc[i];
            if (Towers.dry[i] > 0 && G.round - Towers.dry[i] < (Towers.kind[i] == Towers.PAINT ? Tune.DRY_PAINT_ROUNDS : Tune.DRY_ROUNDS) && !(Towers.kind[i] == Towers.MONEY && Churn.churnable())) {
                // study 9 2.4: paint-tower flags expire after 10 rounds (was 40); a flagged tower in sight is re-sensed
                // and its flag dropped if it holds 50+ paint again
                if (!rc.canSenseLocation(l)) continue;
                RobotInfo ft = rc.senseRobotAtLocation(l);
                if (ft == null || ft.team != G.me || ft.paintAmount < Tune.DRY_CLEAR_PAINT) continue;
                Towers.dry[i] = 0;
            }
            int d = G.here.distanceSquaredTo(l);
            if (Towers.kind[i] == Towers.PAINT) d = d * Tune.REFILL_PAINT_NUM / Tune.REFILL_PAINT_DEN;
            if (d < bestD) { bestD = d; best = l; }
        }
        if (best == null) { refillAt = null; return false; }
        refillAt = best;
        if (rc.canSenseLocation(best)) {
            RobotInfo t = rc.senseRobotAtLocation(best);
            if (t == null || t.team != G.me || !t.type.isTowerType()) { Towers.forget(best); refillAt = null; return false; }
            int take = Math.min(cap - G.paint, t.paintAmount);
            if (G.here.distanceSquaredTo(best) <= 2) {
                if (take > 0 && rc.canTransferPaint(best, -take)) {
                    rc.transferPaint(best, -take);
                    G.paint = rc.getPaint();
                    if (G.paint >= cap * Tune.REFILL_STOP_NUM / Tune.REFILL_STOP_DEN) refillAt = null;
                    return true;
                }
                // a drained money tower may churn (Churn.towerTurn): wait beside it up to 3 rounds to rebuild it
                if (t.paintAmount < Tune.CHURN_PAINT && t.type == UnitType.LEVEL_ONE_MONEY_TOWER && Churn.churnable()) {
                    if (!best.equals(churnLoc) || G.round - churnAt > Tune.CHURN_WAIT_RESET) { churnLoc = best; churnAt = G.round; }
                    if (G.type == UnitType.SOLDIER && Churn.repairPattern(best)) churnAt = G.round;   // keep waiting while repairing
                    if (G.round - churnAt < Tune.CHURN_WAIT_ROUNDS) { G.ind += " churnwait"; return true; }
                }
                if (t.paintAmount < Tune.DRY_ADJ_PAINT) Towers.markDry(best);
                if (!rc.isActionReady()) return true;   // wait for the cooldown next to the tower
                refillAt = null;
                return false;
            }
            if (t.paintAmount < Math.min(Tune.DRY_FAR_PAINT, cap - G.paint) && !(t.type == UnitType.LEVEL_ONE_MONEY_TOWER && Churn.churnable())) { Towers.markDry(best); }
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

    static { Towers.dry = new int[32]; }   // allocated here, as t135 allocated Unit.towerDry (see G.nTowers)

    // the churn wait inside refill (see Churn): the drained money tower being waited at, and since when
    static MapLocation churnLoc;
    static int churnAt = -100;

    /** A wandering target: a random tile, renewed when reached, after a timeout, or when it is known terrain. */
    static MapLocation exploreTarget() {
        if (explore == null || G.here.distanceSquaredTo(explore) <= Tune.EXPLORE_REACHED_R2 || G.round - exploreSince > Tune.EXPLORE_TIMEOUT
                || G.isWall(explore)) {
            // study 7 2.1 (a): 43 free ruins in our half were never seen by r100 (walled pockets, far corners of big
            // maps); draw up to EXPLORE_DRAWS (128) tiles and take the first we have never seen (else the last draw)
            MapLocation t = null;
            for (int i = Tune.EXPLORE_DRAWS; --i >= 0; ) {
                t = new MapLocation(G.rand(G.W), G.rand(G.H));
                if ((G.mem[t.x + t.y * G.W] & G.SEEN) == 0) break;
            }
            explore = t;
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

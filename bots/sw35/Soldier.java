package sw35;

import battlecode.common.*;

/** Soldiers: build towers on ruins (mark, paint the 24 pattern tiles, complete), otherwise paint and explore;
 *  attack enemy towers in range. */
public strictfp class Soldier {
    static MapLocation ruin;
    static UnitType ruinType;
    static int ruinSince, ruinBlocked;
    static MapLocation[] badRuin = new MapLocation[16];
    static int[] badUntil = new int[16];
    static int nBad;

    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        Unit.scanEnemyTowers();
        // a visible enemy tower in range: hit it (50 damage) when healthy enough to trade
        if (Unit.enemyTower != null && rc.isActionReady() && G.paint >= 5 && rc.canAttack(Unit.enemyTower)
                && G.here.distanceSquaredTo(Unit.enemyTower) <= 9) {
            rc.attack(Unit.enemyTower);
            G.paint = rc.getPaint();
        }
        if (ruin == null) pickRuin();
        if (ruin != null) {
            if (workRuin()) return;
        }
        if (siege()) return;
        if (Unit.refill(100)) { paintHere(); return; }
        // explore, painting as we go
        paintNear();
        Nav.moveTo(Unit.exploreTarget());
        paintNear();
    }

    // ---- siege: a soldier with no ruin to build and paint to spare kites a known enemy tower nearby: step into
    // range (r2 <= 9), hit it, step back out
    static final int SIEGE_PAINT = 30, SIEGE_R2 = 144;
    static boolean siege() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation t = Unit.enemyTower;
        if (t == null || G.paint < SIEGE_PAINT || G.here.distanceSquaredTo(t) > SIEGE_R2) return false;
        if (rc.isActionReady()) {
            if (G.here.distanceSquaredTo(t) > 9) Nav.moveTo(t);
            G.here = rc.getLocation();
            if (rc.canAttack(t)) { rc.attack(t); G.paint = rc.getPaint(); }
        }
        if (!rc.isActionReady() && rc.isMovementReady() && G.here.distanceSquaredTo(t) <= 9) {
            Direction away = t.directionTo(G.here);
            for (Direction d : new Direction[]{away, away.rotateLeft(), away.rotateRight()})
                if (rc.canMove(d)) { rc.move(d); G.here = rc.getLocation(); break; }
        }
        G.ind += " siege" + t;
        return true;
    }

    static boolean isBad(MapLocation r) {
        for (int i = nBad; --i >= 0; ) if (badRuin[i].equals(r) && G.round < badUntil[i]) return true;
        return false;
    }

    static void markBad(MapLocation r, int rounds) {
        for (int i = nBad; --i >= 0; ) if (badRuin[i].equals(r)) { badUntil[i] = G.round + rounds; return; }
        if (nBad < badRuin.length) { badRuin[nBad] = r; badUntil[nBad++] = G.round + rounds; }
        else { badRuin[G.rand(badRuin.length)] = r; }
    }

    static void pickRuin() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.getNumberTowers() >= GameConstants.MAX_NUMBER_OF_TOWERS) return;
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapLocation r : G.ruins) {
            if (rc.senseRobotAtLocation(r) != null) continue;       // a tower stands there
            if (isBad(r)) continue;
            // two soldiers per ruin at most
            int helpers = 0;
            for (RobotInfo a : G.allies) if (a.type == UnitType.SOLDIER && a.location.distanceSquaredTo(r) <= 8) helpers++;
            if (helpers >= 1 && G.here.distanceSquaredTo(r) > 2) continue;
            int d = G.here.distanceSquaredTo(r);
            if (d < bestD) { bestD = d; best = r; }
        }
        if (best != null) { ruin = best; ruinType = null; ruinSince = G.round; ruinBlocked = 0; }
    }

    /** Tower type for a new ruin. Paint binds: a paint tower yields 5 paint a round against a money tower's 20
     *  chips, and units plus their refills spend far more paint than chips. Third tower money, then two paint per
     *  money; always paint while chips sit idle. */
    static final int IDLE_CHIPS = 3000;
    static UnitType wantType() {
        int n = G.rc.getNumberTowers();
        if (G.rc.getChips() >= IDLE_CHIPS) return UnitType.LEVEL_ONE_PAINT_TOWER;
        if (n <= 2) return UnitType.LEVEL_ONE_MONEY_TOWER;
        return n % 3 == 2 ? UnitType.LEVEL_ONE_MONEY_TOWER : UnitType.LEVEL_ONE_PAINT_TOWER;
    }

    static int patternOf(UnitType t) {
        switch (t) {
            case LEVEL_ONE_PAINT_TOWER: return GameConstants.PAINT_TOWER_PATTERN;
            case LEVEL_ONE_MONEY_TOWER: return GameConstants.MONEY_TOWER_PATTERN;
            default: return GameConstants.DEFENSE_TOWER_PATTERN;
        }
    }

    /** true = secondary color at offset (dx, dy) from the pattern center. */
    static boolean bit(int pattern, int dx, int dy) { return ((pattern >> (5 * (dx + 2) + dy + 2)) & 1) != 0; }

    /** The tower type a ruin's marks spell (null when nothing visible is marked). */
    static UnitType readMarks(MapLocation r) throws GameActionException {
        RobotController rc = G.rc;
        int pp = GameConstants.PAINT_TOWER_PATTERN, mp = GameConstants.MONEY_TOWER_PATTERN, dp = GameConstants.DEFENSE_TOWER_PATTERN;
        int ep = 0, em = 0, ed = 0, marked = 0;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = r.translate(dx, dy);
            if (!rc.canSenseLocation(l)) continue;
            PaintType m = rc.senseMapInfo(l).getMark();
            if (m == PaintType.EMPTY) continue;
            marked++;
            boolean s = m.isSecondary();
            if (bit(pp, dx, dy) != s) ep++;
            if (bit(mp, dx, dy) != s) em++;
            if (bit(dp, dx, dy) != s) ed++;
        }
        if (marked == 0) return null;
        if (ep <= em && ep <= ed) return UnitType.LEVEL_ONE_PAINT_TOWER;
        if (em <= ed) return UnitType.LEVEL_ONE_MONEY_TOWER;
        return UnitType.LEVEL_ONE_DEFENSE_TOWER;
    }

    /** Work the current ruin; false when it was dropped (the turn continues with other work). */
    static boolean workRuin() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation r = ruin;
        if (rc.canSenseLocation(r) && rc.senseRobotAtLocation(r) != null) { ruin = null; return false; }
        if (G.round - ruinSince > 150) { markBad(r, 150); ruin = null; return false; }
        if (G.paint < 10 && !rc.canCompleteTowerPattern(ruinType == null ? wantType() : ruinType, r)) {
            // out of paint mid-pattern: refill and come back
            Unit.refill(10000);
            return true;
        }
        if (ruinType == null) ruinType = readMarks(r);
        int d = G.here.distanceSquaredTo(r);
        if (ruinType == null) {
            if (d > 2) { Nav.moveTo(r); d = G.here.distanceSquaredTo(r); }
            if (d <= 2) {
                UnitType t = wantType();
                if (rc.canMarkTowerPattern(t, r)) { rc.markTowerPattern(t, r); ruinType = t; G.paint = rc.getPaint(); }
            }
            if (ruinType == null) return true;
        }
        int pat = patternOf(ruinType);
        // paint the nearest wrong tile in range; find the nearest wrong tile overall to walk toward
        MapLocation paintL = null; boolean paintS = false; int paintD = Integer.MAX_VALUE;
        MapLocation walkL = null; int walkD = Integer.MAX_VALUE;
        int enemyTiles = 0, wrong = 0;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = r.translate(dx, dy);
            if (!rc.canSenseLocation(l)) { wrong++; continue; }
            PaintType p = rc.senseMapInfo(l).getPaint();
            boolean s = bit(pat, dx, dy);
            if (p.isEnemy()) { enemyTiles++; continue; }
            if (p != PaintType.EMPTY && p.isSecondary() == s) continue;
            wrong++;
            int dd = G.here.distanceSquaredTo(l);
            if (dd <= 9 && dd < paintD) { paintD = dd; paintL = l; paintS = s; }
            if (dd < walkD) { walkD = dd; walkL = l; }
        }
        if (paintL != null && rc.isActionReady() && rc.canPaint(paintL) && G.paint >= 5) {
            rc.attack(paintL, paintS);
            G.paint = rc.getPaint();
            wrong--;
        }
        if (rc.canCompleteTowerPattern(ruinType, r)) {
            rc.completeTowerPattern(ruinType, r);
            G.noteTower(r, G.kind(ruinType));
            ruin = null;
            return true;
        }
        if (enemyTiles > 0) {
            if (++ruinBlocked > 25) { markBad(r, 100); ruin = null; return false; }
        }
        // move: toward the nearest wrong tile, else stay adjacent to complete when the chips arrive
        if (wrong > 0 && walkL != null) {
            if (G.here.distanceSquaredTo(walkL) > 2) Nav.moveTo(walkL);
            else if (paintL == null) Nav.moveTo(r);
        } else if (d > 2) Nav.moveTo(r);
        else if (rc.isActionReady()) paintNear();
        G.ind += " ruin" + r + " " + ruinType + " w" + wrong + " e" + enemyTiles;
        if (rc.canCompleteTowerPattern(ruinType, r)) {
            rc.completeTowerPattern(ruinType, r);
            G.noteTower(r, G.kind(ruinType));
            ruin = null;
        }
        return true;
    }

    static void paintHere() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || G.paint < 25) return;
        MapInfo mi = rc.senseMapInfo(G.here);
        if (mi.getPaint() == PaintType.EMPTY && rc.canPaint(G.here)) { rc.attack(G.here, false); G.paint = rc.getPaint(); }
    }

    /** Paint one unpainted tile in range (the one under us first, then the nearest), keeping a reserve for ruins. */
    static void paintNear() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || G.paint < 50) return;
        MapInfo under = rc.senseMapInfo(G.here);
        if (under.getPaint() == PaintType.EMPTY && rc.canPaint(G.here)) { rc.attack(G.here, false); G.paint = rc.getPaint(); return; }
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapInfo mi : rc.senseNearbyMapInfos(G.here, 9)) {
            if (mi.getPaint() != PaintType.EMPTY || !mi.isPassable()) continue;
            int d = G.here.distanceSquaredTo(mi.getMapLocation());
            if (d < bestD) { bestD = d; best = mi.getMapLocation(); }
        }
        if (best != null && rc.canPaint(best)) { rc.attack(best, false); G.paint = rc.getPaint(); }
    }
}

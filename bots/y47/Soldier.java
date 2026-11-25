package y47;

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
        completeSrp();
        if (Unit.refill(100)) { paintHere(); return; }
        if (srp == null && G.paint >= 100 && G.round >= SRP_FROM && G.rc.getNumberTowers() >= SRP_MIN_TOWERS && nearOwnTower()) pickSrp();
        if (srp != null && workSrp()) return;
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

    // ---- special resource patterns (SRPs). The SRP grid repeats with period 4 in both axes (its first and last
    // rows and columns agree), so one fixed colouring of the whole map makes every lattice centre (x = y = 2 mod 4)
    // a complete SRP wherever its 5x5 is ours and free of walls and ruins. Exploring soldiers paint that colouring
    // (tiles near ruins keep the tower patterns), repaint our own tiles of the wrong colour, and complete any
    // lattice centre in reach.
    static final int SRP_MIN_TOWERS = 3, SRP_MIN_CHIPS = 200, SRP_FROM = 40, SRP_HOME_R2 = 25;

    /** Within SRP_HOME_R2 of a known ally tower: secure ground for an SRP. */
    static boolean nearOwnTower() {
        for (int i = G.nTowers; --i >= 0; ) if (G.towerLoc[i].distanceSquaredTo(G.here) <= SRP_HOME_R2) return true;
        return false;
    }

    /** true = the SRP colouring wants secondary at (x, y). */
    static boolean srpSec(int x, int y) {
        int i = (x - 2) & 3, j = (y - 2) & 3;
        return ((GameConstants.RESOURCE_PATTERN >> (5 * ((i == 3 ? -1 : i) + 2) + (j == 3 ? -1 : j) + 2)) & 1) != 0;
    }

    /** Within a tower pattern's 5x5 of a visible ruin. */
    static boolean nearRuin(MapLocation l) {
        MapLocation[] rs = G.ruins;
        for (int i = rs.length; --i >= 0; ) {
            MapLocation r = rs[i];
            int dx = r.x - l.x, dy = r.y - l.y;
            if (dx <= 2 && dx >= -2 && dy <= 2 && dy >= -2) return true;
        }
        return false;
    }

    /** A ruin's tower 5x5 overlaps the SRP 5x5 centred at c (the tower pattern would repaint it). */
    static boolean ruinOverlaps(MapLocation c) throws GameActionException {
        MapLocation[] rs = G.ruins;
        for (int i = rs.length; --i >= 0; ) {
            MapLocation r = rs[i];
            int dx = r.x - c.x, dy = r.y - c.y;
            if (G.knownTower(r)) continue;   // study 3 tactic 7: overlapping a standing tower's pattern is fine
            if (dx <= 4 && dx >= -4 && dy <= 4 && dy >= -4) return true;
        }
        return false;
    }

    /** The colour to paint at l: the SRP colouring, primary inside ruin patterns. */
    static boolean colorAt(MapLocation l) { return !nearRuin(l) && srpSec(l.x, l.y); }

    static void completeSrp() throws GameActionException {
        RobotController rc = G.rc;
        if (G.chips < SRP_MIN_CHIPS || rc.getNumberTowers() < SRP_MIN_TOWERS) return;
        int x0 = G.here.x - ((G.here.x - 2) & 3), y0 = G.here.y - ((G.here.y - 2) & 3);
        for (int cx = x0; cx <= x0 + 4; cx += 4) for (int cy = y0; cy <= y0 + 4; cy += 4) {
            if (cx < 2 || cy < 2 || cx > G.W - 3 || cy > G.H - 3) continue;
            MapLocation c = new MapLocation(cx, cy);
            if (G.here.distanceSquaredTo(c) <= 8 && !ruinOverlaps(c) && rc.canCompleteResourcePattern(c)) {
                rc.completeResourcePattern(c);
                G.chips = rc.getChips();
                srps++;
                return;
            }
        }
    }
    static int srps;

    /** The SRP this soldier is building, picked among the lattice centres in sight. */
    static MapLocation srp;
    static int srpSince;
    static final int SRP_GIVE_UP = 40;

    static void pickSrp() throws GameActionException {
        RobotController rc = G.rc;
        int x0 = G.here.x - ((G.here.x - 2) & 3), y0 = G.here.y - ((G.here.y - 2) & 3);
        MapLocation best = null; int bestS = Integer.MAX_VALUE;
        for (int cx = x0 - 4; cx <= x0 + 4; cx += 4) for (int cy = y0 - 4; cy <= y0 + 4; cy += 4) {
            if (cx < 2 || cy < 2 || cx > G.W - 3 || cy > G.H - 3) continue;
            MapLocation c = new MapLocation(cx, cy);
            int d = G.here.distanceSquaredTo(c);
            if (d > 20 || isBad(c)) continue;
            if (ruinOverlaps(c)) { markBad(c, 1000); continue; }
            if (rc.senseMapInfo(c).isResourcePatternCenter()) continue;
            // known walls, ruins or enemy paint in the 5x5 rule it out; count our right tiles
            int right = 0; boolean ok = true;
            int[] m = G.mem;
            for (int dx = -2; dx <= 2 && ok; dx++) for (int dy = -2; dy <= 2; dy++) {
                int v = m[cx + dx + (cy + dy) * G.W];
                if ((v & 6) != 0 || (v >> 4) >= 3) { ok = false; break; }
                int p = v >> 4;
                if (p != 0 && (p == 2) == srpSec(cx + dx, cy + dy)) right++;
            }
            if (!ok) { markBad(c, 300); continue; }
            int sc = d - 3 * right;
            if (sc < bestS) { bestS = sc; best = c; }
        }
        if (best != null) { srp = best; srpSince = G.round; }
    }

    /** Paint the SRP's wrong tiles and complete it; false when dropped. */
    static boolean workSrp() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation c = srp;
        if (G.round - srpSince > SRP_GIVE_UP) { markBad(c, 200); srp = null; return false; }
        if (G.paint < 10) { srp = null; return false; }
        if (rc.canSenseLocation(c) && rc.senseMapInfo(c).isResourcePatternCenter()) { srp = null; return false; }
        MapLocation paintL = null; boolean paintS = false; int paintD = Integer.MAX_VALUE;
        MapLocation walkL = null; int walkD = Integer.MAX_VALUE;
        int wrong = 0;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            MapLocation l = c.translate(dx, dy);
            if (!rc.canSenseLocation(l)) { wrong++; continue; }
            MapInfo mi = rc.senseMapInfo(l);
            PaintType p = mi.getPaint();
            if (!mi.isPassable() || p.isEnemy()) { markBad(c, 300); srp = null; return false; }
            boolean sec = bit(GameConstants.RESOURCE_PATTERN, dx, dy);
            if (p != PaintType.EMPTY && p.isSecondary() == sec) continue;
            wrong++;
            int dd = G.here.distanceSquaredTo(l);
            if (dd <= 9 && dd < paintD) { paintD = dd; paintL = l; paintS = sec; }
            if (dd < walkD) { walkD = dd; walkL = l; }
        }
        if (paintL != null && rc.isActionReady() && rc.canPaint(paintL) && G.paint >= 5) {
            rc.attack(paintL, paintS);
            G.paint = rc.getPaint();
            wrong--;
        }
        if (wrong == 0) {
            if (G.here.distanceSquaredTo(c) > 8) Nav.moveTo(c);
            if (rc.canCompleteResourcePattern(c)) {
                rc.completeResourcePattern(c);
                G.chips = rc.getChips();
                srps++;
                srp = null;
                return true;
            }
            if (G.chips < 200) { srp = null; return false; }   // painted; whoever passes with chips completes it
            return true;
        }
        if (walkL != null && G.here.distanceSquaredTo(walkL) > 9) Nav.moveTo(walkL);
        else if (G.here.distanceSquaredTo(c) > 2) Nav.moveTo(c);
        G.ind += " srp" + c + " w" + wrong;
        return true;
    }

    static void paintHere() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || G.paint < 25) return;
        MapInfo mi = rc.senseMapInfo(G.here);
        if (mi.getPaint() == PaintType.EMPTY && rc.canPaint(G.here)) { rc.attack(G.here, colorAt(G.here)); G.paint = rc.getPaint(); }
    }

    /** Paint one tile in range, keeping a reserve for ruins: the empty tile under us first, then the nearest empty
     *  tile, then (once SRPs pay) the nearest own tile of the wrong SRP colour. */
    static void paintNear() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || G.paint < 50) return;
        MapInfo under = rc.senseMapInfo(G.here);
        if (under.getPaint() == PaintType.EMPTY && rc.canPaint(G.here)) { rc.attack(G.here, colorAt(G.here)); G.paint = rc.getPaint(); return; }
        boolean fix = G.round >= SRP_FROM && rc.getNumberTowers() >= SRP_MIN_TOWERS;
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapInfo mi : rc.senseNearbyMapInfos(G.here, 9)) {
            if (!mi.isPassable()) continue;
            PaintType p = mi.getPaint();
            int d;
            if (p == PaintType.EMPTY) d = G.here.distanceSquaredTo(mi.getMapLocation());
            else if (fix && p.isAlly()) {
                MapLocation l = mi.getMapLocation();
                if (p.isSecondary() == colorAt(l)) continue;
                d = 100 + G.here.distanceSquaredTo(l);
            } else continue;
            if (d < bestD) { bestD = d; best = mi.getMapLocation(); }
        }
        if (best != null && rc.canPaint(best)) { rc.attack(best, colorAt(best)); G.paint = rc.getPaint(); }
    }
}

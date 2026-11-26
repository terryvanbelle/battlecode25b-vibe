package y118;

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
        // t36: with >= 6 towers a soldier mid-SRP finishes it before taking up a new ruin
        if (ruin == null && !(srp != null && rc.getNumberTowers() >= SRP_TOWERS)) pickRuin();
        if (ruin != null) {
            if (workRuin()) return;
        }
        if (siege()) return;
        if (srpTurn()) return;
        if (Unit.refill(100)) { paintHere(); return; }
        // explore, painting as we go; study 3 tactic 2: before r80 save paint for tower patterns (no coverage)
        if (G.round >= 80) paintNear();
        Nav.moveTo(Unit.exploreTarget());
        if (G.round >= 80) paintNear();
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

    /** Enemy paint on a visible tile of the ruin's 5x5. */
    static boolean contested(MapLocation r) throws GameActionException {
        RobotController rc = G.rc;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            MapLocation l = r.translate(dx, dy);
            if (rc.canSenseLocation(l) && rc.senseMapInfo(l).getPaint().isEnemy()) return true;
        }
        return false;
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
            if (contested(r)) { markBad(r, 50); continue; }   // study 4 2.2: we finish 2 of 58 contested ruins
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
        // study 4 2.4: money first (their builds 1-8 are nearly all money, one paint tower past r100), now that
        // patterns no longer wait for chips (2.1) and contested ruins are skipped (2.2)
        int n = G.rc.getNumberTowers();
        int pt = 0, mt = 0;
        for (int i = G.nTowers; --i >= 0; ) { if (G.towerKind[i] == 1) pt++; else if (G.towerKind[i] == 2) mt++; }
        if (pt + mt >= n && pt == 0) return UnitType.LEVEL_ONE_PAINT_TOWER;   // every tower known and none paints
        if (n < 8) return UnitType.LEVEL_ONE_MONEY_TOWER;
        if (G.rc.getChips() >= IDLE_CHIPS) return UnitType.LEVEL_ONE_PAINT_TOWER;
        return pt * 5 < n ? UnitType.LEVEL_ONE_PAINT_TOWER : UnitType.LEVEL_ONE_MONEY_TOWER;
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

    // ---- t36: late special resource patterns (study 4 2.6, study 3 tactic 7). Centres on the lattice x = y = 2
    // (mod 4); RESOURCE_PATTERN repeats with period 4 (its outer rows and columns agree), so neighbouring lattice SRPs
    // share their edge tiles consistently. Started only from r100 with 1000+ chips by a soldier with no ruin to work
    // (or, with 6+ towers, kept over a new ruin). The 5x5 must hold no walls, no enemy paint, and no ruin; and must
    // not overlap an unbuilt ruin's 5x5 (a ruin within Chebyshev 4 must carry our tower). Centres 3-4 tiles from one
    // of our towers are preferred.
    static final int SRP_ROUND = 100, SRP_CHIPS = 1500, SRP_TOWERS = 6, SRP_GIVE_UP = 60;
    static MapLocation srp;
    static int srpSince, srps;
    static int[] srpSkip;          // per lattice centre: skip it until this round (Integer.MAX_VALUE = done or never)
    static int srpLW;

    /** true = the SRP lattice colouring wants secondary at (x, y). */
    static boolean srpSec(int x, int y) { return ((G.SRP_MASK >> (((x - 2) & 3) | (((y - 2) & 3) << 2))) & 1) != 0; }

    static int srpIdx(MapLocation c) { return (c.x >> 2) + (c.y >> 2) * srpLW; }

    static void srpSkipFor(MapLocation c, int rounds) {
        srpSkip[srpIdx(c)] = rounds == Integer.MAX_VALUE ? rounds : G.round + rounds;
    }

    /** Kind of our known tower at l (1 paint, 2 money, 3 defense), 0 when none. */
    static int allyTowerKind(MapLocation l) {
        for (int i = G.nTowers; --i >= 0; ) if (G.towerLoc[i].equals(l)) return G.towerKind[i];
        return 0;
    }

    /** The SRP at c and the money-tower pattern around t agree on every shared tile (so churn repairs and the
     *  SRP never repaint each other). */
    static boolean agreesWithMoney(int cx, int cy, MapLocation t) {
        int mp = GameConstants.MONEY_TOWER_PATTERN, rp = GameConstants.RESOURCE_PATTERN;
        for (int x = Math.max(cx, t.x) - 2; x <= Math.min(cx, t.x) + 2; x++)
            for (int y = Math.max(cy, t.y) - 2; y <= Math.min(cy, t.y) + 2; y++)
                if (bit(mp, x - t.x, y - t.y) != bit(rp, x - cx, y - cy)) return false;
        return true;
    }

    static boolean srpTurn() throws GameActionException {
        if (srp == null) {
            if (G.round < SRP_ROUND || G.chips < SRP_CHIPS || G.paint < 60 || Clock.getBytecodesLeft() < 6000) return false;
            pickSrp();
            if (srp == null) return false;
        }
        return workSrp();
    }

    /** Choose the best lattice centre within d2 50: valid by the map memory, scored by distance, our tower 3-4
     *  tiles away, and tiles already right. */
    static void pickSrp() throws GameActionException {
        RobotController rc = G.rc;
        if (srpSkip == null) { srpLW = G.W / 4 + 1; srpSkip = new int[srpLW * (G.H / 4 + 1)]; }
        int W = G.W, H = G.H, hx = G.here.x, hy = G.here.y;
        int[] m = G.mem;
        int x0 = hx - 7 + ((2 - (hx - 7)) & 3), y0 = hy - 7 + ((2 - (hy - 7)) & 3);
        MapLocation best = null; int bestS = Integer.MAX_VALUE;
        for (int cx = x0; cx <= hx + 7; cx += 4) {
            if (cx < 2 || cx > W - 3) continue;
            for (int cy = y0; cy <= hy + 7; cy += 4) {
                if (cy < 2 || cy > H - 3) continue;
                if (Clock.getBytecodesLeft() < 3000) break;
                MapLocation c = new MapLocation(cx, cy);
                int d = G.here.distanceSquaredTo(c);
                if (d > 50) continue;
                int k = srpIdx(c);
                if (srpSkip[k] > G.round) continue;
                // ruins: none in the 5x5, and any within Chebyshev 4 must be our tower
                int towerCheb = 99; boolean ok = true;
                for (int i = G.nRuins; --i >= 0; ) {
                    MapLocation r = G.ruinList[i];
                    int ax = Math.abs(r.x - cx), ay = Math.abs(r.y - cy);
                    int ch = ax > ay ? ax : ay;
                    if (ch <= 2) { ok = false; srpSkip[k] = Integer.MAX_VALUE; break; }
                    if (ch > 6) continue;
                    int kind = allyTowerKind(r);
                    if (kind == 0) {
                        if (ch <= 4) { ok = false; srpSkip[k] = G.round + 100; break; }
                        continue;
                    }
                    if (ch <= 4 && kind == 2 && !agreesWithMoney(cx, cy, r)) { ok = false; srpSkip[k] = G.round + 300; break; }
                    if (ch < towerCheb) towerCheb = ch;
                }
                if (!ok) continue;
                if (rc.canSenseLocation(c) && rc.senseMapInfo(c).isResourcePatternCenter()) { srpSkip[k] = Integer.MAX_VALUE; continue; }
                int right = 0;
                for (int dx = -2; dx <= 2 && ok; dx++) for (int dy = -2; dy <= 2; dy++) {
                    int v = m[cx + dx + (cy + dy) * W];
                    if ((v & 6) != 0) { ok = false; srpSkip[k] = Integer.MAX_VALUE; break; }
                    int p = v >> 4;
                    if (p >= 3) { ok = false; srpSkip[k] = G.round + 60; break; }
                    if (p != 0 && (p == 2) == srpSec(cx + dx, cy + dy)) right++;
                }
                if (!ok) continue;
                int sc = d - 3 * right - (towerCheb <= 4 ? 40 : towerCheb <= 6 ? 15 : 0);
                if (sc < bestS) { bestS = sc; best = c; }
            }
        }
        if (best != null) { srp = best; srpSince = G.round; }
    }

    static MapLocation srpPaintL;
    static boolean srpPaintS;
    static int srpWrong;

    /** Scan the SRP's 25 tiles: count the wrong ones and pick the nearest wrong one we can paint now.
     *  False when the centre turned invalid (wall, ruin, enemy paint) and was dropped. */
    static boolean srpScan(MapLocation c) throws GameActionException {
        RobotController rc = G.rc;
        srpPaintL = null; srpWrong = 0;
        int paintD = Integer.MAX_VALUE;
        int pat = GameConstants.RESOURCE_PATTERN;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            MapLocation l = c.translate(dx, dy);
            if (!rc.canSenseLocation(l)) { srpWrong++; continue; }
            MapInfo mi = rc.senseMapInfo(l);
            if (!mi.isPassable()) { srpSkipFor(c, Integer.MAX_VALUE); srp = null; return false; }
            PaintType p = mi.getPaint();
            if (p.isEnemy()) { srpSkipFor(c, 80); srp = null; return false; }
            boolean sec = bit(pat, dx, dy);
            if (p != PaintType.EMPTY && p.isSecondary() == sec) continue;
            srpWrong++;
            int dd = G.here.distanceSquaredTo(l);
            if (dd <= 9 && dd < paintD) { paintD = dd; srpPaintL = l; srpPaintS = sec; }
        }
        return true;
    }

    static boolean srpPaint() throws GameActionException {
        RobotController rc = G.rc;
        if (srpPaintL != null && rc.isActionReady() && G.paint >= 5 && rc.canPaint(srpPaintL)) {
            rc.attack(srpPaintL, srpPaintS);
            G.paint = rc.getPaint();
            srpWrong--;
            return true;
        }
        return false;
    }

    static boolean srpComplete(MapLocation c) throws GameActionException {
        RobotController rc = G.rc;
        if (rc.canCompleteResourcePattern(c)) {
            rc.completeResourcePattern(c);
            G.chips = rc.getChips();
            srps++;
            srpSkipFor(c, Integer.MAX_VALUE);
            srp = null;
            G.ind += " SRPDONE" + c + "#" + srps;
            return true;
        }
        return false;
    }

    /** Stand on the centre (every tile of the 5x5 is then in paint range), paint wrong tiles, complete. False when
     *  the SRP was dropped (the turn goes on with other work). */
    static boolean workSrp() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation c = srp;
        if (G.round - srpSince > SRP_GIVE_UP) { srpSkipFor(c, 150); srp = null; return false; }
        if (rc.canSenseLocation(c) && rc.senseMapInfo(c).isResourcePatternCenter()) { srpSkipFor(c, Integer.MAX_VALUE); srp = null; return false; }
        // a newly seen ruin in or near the 5x5 (unbuilt, or an enemy tower) rules the centre out
        for (MapLocation r : G.ruins) {
            int ax = Math.abs(r.x - c.x), ay = Math.abs(r.y - c.y);
            int ch = ax > ay ? ax : ay;
            if (ch <= 2) { srpSkipFor(c, Integer.MAX_VALUE); srp = null; return false; }
            if (ch <= 4) {
                RobotInfo t = rc.senseRobotAtLocation(r);
                if (t == null || t.team != G.me) { srpSkipFor(c, 100); srp = null; return false; }
            }
        }
        if (Unit.enemyTower != null && Unit.enemyTower.distanceSquaredTo(c) <= 25) { srpSkipFor(c, 100); srp = null; return false; }
        if (G.paint < 15 && Unit.refill(10000)) { G.ind += " srp-refill"; return true; }
        if (Clock.getBytecodesLeft() < 2500) return true;
        if (!srpScan(c)) return false;
        srpPaint();
        if (srpWrong == 0 && srpComplete(c)) return true;
        if (!G.here.equals(c)) {
            Nav.moveTo(c);
            G.here = rc.getLocation();
            if (rc.isActionReady() && Clock.getBytecodesLeft() > 4000) {
                if (!srpScan(c)) return false;
                srpPaint();
            }
        }
        if (srpWrong == 0 && srpComplete(c)) return true;
        G.ind += " srp" + c + " w" + srpWrong;
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

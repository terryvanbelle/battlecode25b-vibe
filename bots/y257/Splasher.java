package y257;

import battlecode.common.*;

/** Splashers: splash where the most tiles turn ours (empty tiles in radius^2 4 of the center, enemy tiles only in
 *  radius^2 2), and hit enemy towers; move toward unpainted or enemy ground. */
public strictfp class Splasher {
    static final int[] CX = {0, 1, -1, 0, 0, 1, 1, -1, -1, 2, -2, 0, 0};
    static final int[] CY = {0, 0, 0, 1, -1, 1, -1, 1, -1, 0, 0, 2, -2};

    static int lastSplash;

    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        Unit.scanEnemyTowers();
        // one splash evaluation a turn (13 centers x 13 tiles is the bulk of a splasher's bytecode): before moving
        // when a target in reach is already good, else after the move
        towersIntoGrid();
        boolean done = false;
        if (G.paint >= 50 && rc.isActionReady()) done = splash(9);
        if (Unit.refill(100)) return;
        // guards: a unit's first turn on a big map spends most of its budget on the map memory
        // study 5 2.3: 8.6% of our splasher turns sat by a lone empty tile with full paint; after 8 rounds without a
        // splash (while able to splash), explore instead of chasing the nearest non-ally tile
        if (lastSplash == 0 || G.paint < 50 || !rc.isActionReady()) lastSplash = Math.max(lastSplash, G.round - 4);
        MapLocation goal = G.paint >= 50 && Clock.getBytecodesLeft() > 6000 ? standOff() : null;   // study 8 2.4
        if (goal == null) goal = Clock.getBytecodesLeft() > 5000 && G.round - lastSplash <= 8 ? frontier() : null;
        Nav.moveTo(goal != null ? goal : Unit.exploreTarget());
        if (!done && G.paint >= 50 && rc.isActionReady() && Clock.getBytecodesLeft() > 2500) {
            G.here = rc.getLocation();
            splash(6);
        }
    }

    /** Splash value grid, 11x11 centered on the turn's start position (G.remember fills it from the visible tiles):
     *  V1 = a tile's value in the outer ring of a splash (+1 empty), V2 = in the inner 3x3 (+1 empty, +2 enemy).
     *  Enemy towers add 12 to both. Tiles out of sight count 0. */
    static final int[] V1 = new int[121], V2 = new int[121], ZERO = new int[121];
    static int gx0, gy0;      // the grid's center (the turn's start position)

    static void towersIntoGrid() {
        gx0 = G.here.x; gy0 = G.here.y;
        for (RobotInfo e : G.enemies) {
            if (!e.type.isTowerType()) continue;
            int gx = e.location.x - gx0 + 5, gy = e.location.y - gy0 + 5;
            if (gx >= 0 && gx < 11 && gy >= 0 && gy < 11) { V1[gy * 11 + gx] += 30; V2[gy * 11 + gx] += 30; }   // study 5 2.5 (as t50)
        }
    }

    /** Splash at the best center in reach of our current position if it scores at least min; true when it did. */
    static boolean splash(int min) throws GameActionException {
        RobotController rc = G.rc;
        int hx = G.here.x, hy = G.here.y, W = G.W, H = G.H;
        int[] v1 = V1, v2 = V2;
        int sx = hx - gx0, sy = hy - gy0;        // our offset from the grid center (0 or one step)
        int best = -1, bestS = min - 1;
        for (int i = 0; i < 13; i++) {
            int cx = hx + CX[i], cy = hy + CY[i];
            if (cx < 0 || cy < 0 || cx >= W || cy >= H) continue;
            int c = (sy + CY[i] + 5) * 11 + sx + CX[i] + 5;
            int s = v2[c] + v2[c - 1] + v2[c + 1] + v2[c - 11] + v2[c + 11] + v2[c - 12] + v2[c - 10] + v2[c + 10]
                    + v2[c + 12] + v1[c - 2] + v1[c + 2] + v1[c - 22] + v1[c + 22];
            if (s > bestS) { bestS = s; best = i; }
        }
        if (best < 0) return false;
        MapLocation t = G.here.translate(CX[best], CY[best]);
        if (!rc.canAttack(t)) return false;
        rc.attack(t); lastSplash = G.round;
        G.paint = rc.getPaint();
        return true;
    }

    static final int[] SX = {4, -4, 0, 0, 3, 3, -3, -3, 1, 1, -1, -1};
    static final int[] SY = {0, 0, 4, -4, 1, -1, 1, -1, 3, -3, 3, -3};

    /** study 8 2.4: a firing tile at d2 10-16 from the nearest enemy paint or money tower in view (a splash reaches
     *  the tower from there; those towers shoot only to d2 9), clear of the other towers' reach; null when none. */
    static MapLocation standOff() throws GameActionException {
        RobotController rc = G.rc;
        RobotInfo tw = null; int td = Integer.MAX_VALUE;
        for (RobotInfo e : G.enemies) {
            if (!e.type.isTowerType() || G.kind(e.type) == 3) continue;
            int d = G.here.distanceSquaredTo(e.location);
            if (d < td) { td = d; tw = e; }
        }
        if (tw == null) return null;
        MapLocation best = null; int bd = Integer.MAX_VALUE;
        for (int i = 0; i < 12; i++) {
            MapLocation l = tw.location.translate(SX[i], SY[i]);
            if (!rc.onTheMap(l) || !rc.canSenseLocation(l)) continue;
            if (!l.equals(G.here) && (!rc.senseMapInfo(l).isPassable() || rc.senseRobotAtLocation(l) != null)) continue;
            boolean bad = false;
            for (RobotInfo e : G.enemies) {
                if (!e.type.isTowerType() || e.location.equals(tw.location)) continue;
                if (l.distanceSquaredTo(e.location) <= (G.kind(e.type) == 3 ? 16 : 9)) { bad = true; break; }
            }
            if (bad) continue;
            int d = G.here.distanceSquaredTo(l);
            if (d < bd) { bd = d; best = l; }
        }
        return best;
    }

    /** The visible tile with the most non-ally paintable ground around it, roughly: the nearest non-ally tile at
     *  distance^2 >= 5 (so the splash center lands on new ground), else null. */
    static MapLocation frontier() {
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapInfo mi : G.infos) {
            if (!mi.isPassable()) continue;
            PaintType p = mi.getPaint();
            if (p.isAlly()) continue;
            MapLocation l = mi.getMapLocation();
            int d = G.here.distanceSquaredTo(l);
            if (d < 5) continue;
            d += p.isEnemy() ? -3 : 0;
            if (d < bestD) { bestD = d; best = l; }
        }
        return best;
    }
}

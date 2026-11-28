package y360;

import battlecode.common.*;

/** Splashers: splash where the most tiles turn ours (empty tiles in radius^2 4 of the center, enemy tiles only in
 *  radius^2 2), and hit enemy towers; move toward unpainted or enemy ground. */
public strictfp class Splasher {
    static final int[] CX = {0, 1, -1, 0, 0, 1, 1, -1, -1, 2, -2, 0, 0};
    static final int[] CY = {0, 0, 0, 1, -1, 1, -1, 1, -1, 0, 0, 2, -2};

    static int lastSplash;

    /** A splasher's turn: the steps below in order, each gate written next to it. A gate marked "in:" is the first
     *  test inside the step's method and stays there: moving it here would change the bytecode count before the
     *  Clock reads of steps 4 and 5. Up to two splash evaluations a turn (13 centers x 13 tiles is the bulk of a
     *  splasher's bytecode): before moving when a target in reach is already good, else after the move. Before the
     *  turn, G.remember has called sense() (map memory + splash grid); after it, RobotPlayer runs the free actions
     *  Churn.rebuild and Unit.topUp. */
    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        Unit.scanEnemyTowers();                                  // free: remember the nearest enemy tower
        towersIntoGrid();                                        // free: enemy towers add SPL_TOWER_VALUE to the grid
        // 1. splash now if a center in reach scores SPL_SCORE_FIRST+; 50 = the splash's paint
        boolean done = false;
        if (G.paint >= 50 && rc.isActionReady()) done = splash(Tune.SPL_SCORE_FIRST);
        // 2. refill, ending the turn; in: paint < SPL_REFILL or a refill walk under way
        if (Unit.refill(Tune.SPL_REFILL)) return;
        // 3. lastSplash clamp (study 5 2.3: 8.6% of our splasher turns sat by a lone empty tile with full paint;
        //    after SPL_FRONTIER_ROUNDS rounds without a splash while able to splash, step 4 explores instead of
        //    chasing the nearest non-ally tile). A turn that cannot splash raises lastSplash to round -
        //    SPL_IDLE_CLAMP, so lastSplash is not the last splash round.
        if (lastSplash == 0 || G.paint < 50 || !rc.isActionReady()) lastSplash = Math.max(lastSplash, G.round - Tune.SPL_IDLE_CLAMP);
        // 4. goal, the first that applies: standOff (paint >= SPL_STANDOFF_PAINT, SPL_STANDOFF_BC bytecodes left;
        //    study 8 2.4); frontier (SPL_FRONTIER_BC left, a splash within SPL_FRONTIER_ROUNDS); explore. Then move.
        //    The bytecode guards exist because a unit's first turn on a big map spends most of its budget on the
        //    map memory.
        MapLocation goal = G.paint >= Tune.SPL_STANDOFF_PAINT && Clock.getBytecodesLeft() > Tune.SPL_STANDOFF_BC ? standOff() : null;
        if (goal == null) goal = Clock.getBytecodesLeft() > Tune.SPL_FRONTIER_BC && G.round - lastSplash <= Tune.SPL_FRONTIER_ROUNDS ? frontier() : null;
        Nav.moveTo(goal != null ? goal : Unit.exploreTarget());
        // 5. not splashed yet: splash from the new position if a center scores SPL_SCORE_AFTER+ (SPL_AFTER_BC left)
        if (!done && G.paint >= 50 && rc.isActionReady() && Clock.getBytecodesLeft() > Tune.SPL_AFTER_BC) {
            G.here = rc.getLocation();
            splash(Tune.SPL_SCORE_AFTER);
        }
    }

    /** Splash value grid, 11x11 centered on the turn's start position (sense() fills it from the visible tiles):
     *  V1 = a tile's value in the outer ring of a splash (+1 empty), V2 = in the inner 3x3 (+1 empty, +2 enemy);
     *  our secondary paint on an SRP lattice tile is -50 in both. Enemy towers add 30 to both (towersIntoGrid).
     *  Tiles out of sight count 0. */
    static final int[] V1 = new int[121], V2 = new int[121], ZERO = new int[121];
    static int gx0, gy0;      // the grid's center (the turn's start position)

    /** The splasher's half of G.remember (called from it each turn, before turn()): one pass over the visible tiles
     *  records the map memory exactly as G.remember does for other units (except the ruin list) and fills the splash
     *  value grid V1/V2 (zeroed by copying). Only a splasher that can splash this turn needs the SRP guard.
     *  w is G.W, passed in for bytecode parity with t135, which held it in a local: the engine charges nothing for
     *  a call to our own method and 1 for its return, so pushing W (1) + return (1) replaces t135's `int w = W` (2).
     *  Reading G.W per tile instead, or dropping the parameter, makes every splasher turn 1 bytecode cheaper, enough
     *  to change which turns hit the 17500 limit (seen in a twin game, t118 DefaultHuge round 484). */
    static void sense(int w) {
        int[] m = G.mem;
        int[] v1 = V1, v2 = V2;
        System.arraycopy(ZERO, 0, v1, 0, 121);
        System.arraycopy(ZERO, 0, v2, 0, 121);
        int ox = G.here.x - 5, oy = G.here.y - 5;
        int srpMask = G.rc.isActionReady() ? Pattern.SRP_MASK : 0;
        for (int i = G.infos.length; --i >= 0; ) {
            MapInfo mi = G.infos[i];
            MapLocation l = mi.getMapLocation();
            int k = l.x + l.y * w;
            int old = m[k];
            if (old == 0) {
                old = G.SEEN | (mi.isWall() ? G.WALL : 0) | (mi.hasRuin() ? G.RUIN : 0);
                Sym.observe(l.x, l.y, old);
            }
            int p = mi.getPaint().ordinal();
            m[k] = (old & 0xF) | (p << 4);
            if ((old & 0xF) == G.SEEN) {     // passable (not wall or ruin); the remembered paint bits are stale (was old == 1: enemy tiles never scored)
                int g = (l.y - oy) * 11 + l.x - ox;
                if (p == 0) { v1[g] = Tune.SPL_EMPTY_VALUE; v2[g] = Tune.SPL_EMPTY_VALUE; } else if (p >= 3) v2[g] = Tune.SPL_ENEMY_VALUE;
                // t36: our secondary paint where the SRP lattice wants secondary: a splash would repaint it
                // primary and break the SRP, so splashes covering it are ruled out
                else if (p == 2 && ((srpMask >> (((l.x - 2) & 3) | (((l.y - 2) & 3) << 2))) & 1) != 0) { v1[g] = Tune.SPL_SRP_GUARD; v2[g] = Tune.SPL_SRP_GUARD; }
            }
        }
    }

    static void towersIntoGrid() {
        gx0 = G.here.x; gy0 = G.here.y;
        for (RobotInfo e : G.enemies) {
            if (!e.type.isTowerType()) continue;
            int gx = e.location.x - gx0 + 5, gy = e.location.y - gy0 + 5;
            if (gx >= 0 && gx < 11 && gy >= 0 && gy < 11) { V1[gy * 11 + gx] += Tune.SPL_TOWER_VALUE; V2[gy * 11 + gx] += Tune.SPL_TOWER_VALUE; }   // study 5 2.5 (as t50)
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
            if (!e.type.isTowerType() || Towers.kindOf(e.type) == Towers.DEFENSE) continue;
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
                if (l.distanceSquaredTo(e.location) <= (Towers.kindOf(e.type) == Towers.DEFENSE ? 16 : 9)) { bad = true; break; }   // the towers' attack ranges
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
            if (d < Tune.SPL_FRONTIER_MIN_R2) continue;
            d += p.isEnemy() ? -Tune.SPL_FRONTIER_ENEMY : 0;
            if (d < bestD) { bestD = d; best = l; }
        }
        return best;
    }
}

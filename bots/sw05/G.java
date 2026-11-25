package sw05;

import battlecode.common.*;

/** Globals shared by every unit: the controller, map geometry, per-turn sensing and the map memory. Static fields are
 *  per robot (each robot has its own class loader). */
public strictfp class G {
    static final boolean DEBUG = false;
    static RobotController rc;
    static UnitType type;
    static Team me, them;
    static int W, H, id;
    static int round, overruns, exceptions;
    static MapLocation here, spawnLoc, center;
    static RobotInfo[] allies, enemies;
    static MapInfo[] infos;
    static MapLocation[] ruins;
    static int paint, chips;
    static String ind = "";

    static final Direction[] DIRS = {Direction.NORTH, Direction.NORTHEAST, Direction.EAST, Direction.SOUTHEAST,
            Direction.SOUTH, Direction.SOUTHWEST, Direction.WEST, Direction.NORTHWEST};

    // ---- map memory: one int per tile. bit 0 seen, bit 1 wall, bit 2 ruin; bits 4-6 paint (PaintType ordinal,
    // from this robot's view, i.e. 1/2 ally, 3/4 enemy) as last seen.
    static int[] mem;
    static final int SEEN = 1, WALL = 2, RUIN = 4;

    // ---- known ally towers (location index -> type code) for refills; a short list
    static MapLocation[] towerLoc = new MapLocation[32];
    static int[] towerKind = new int[32];       // 1 paint, 2 money, 3 defense
    static int nTowers;

    static long rng;

    static void init(RobotController r) {
        rc = r;
        type = rc.getType();
        me = rc.getTeam(); them = me.opponent();
        W = rc.getMapWidth(); H = rc.getMapHeight();
        id = rc.getID();
        here = rc.getLocation(); spawnLoc = here;
        center = new MapLocation(W / 2, H / 2);
        mem = new int[W * H];
        rng = 0x9E3779B97F4A7C15L ^ (id * 0xBF58476D1CE4E5B9L);
        Sym.init();
    }

    static int rand(int n) {
        rng ^= rng << 13; rng ^= rng >>> 7; rng ^= rng << 17;
        return (int) ((rng >>> 33) % n);
    }

    static void startTurn() throws GameActionException {
        round = rc.getRoundNum();
        here = rc.getLocation();
        paint = rc.getPaint();
        chips = rc.getChips();
        allies = rc.senseNearbyRobots(-1, me);
        enemies = rc.senseNearbyRobots(-1, them);
        infos = rc.senseNearbyMapInfos();
        ruins = rc.senseNearbyRuins(-1);
        ind = "";
        remember();
    }

    /** Record walls/ruins/paint of the visible tiles and feed symmetry elimination with tiles seen for the first time. */
    static void remember() {
        int[] m = mem;
        int w = W;
        if (type == UnitType.SPLASHER) {
            // also the splash value grid (Splasher.V1/V2, 11x11 around us; zeroed by copying)
            int[] v1 = Splasher.V1, v2 = Splasher.V2;
            System.arraycopy(Splasher.ZERO, 0, v1, 0, 121);
            System.arraycopy(Splasher.ZERO, 0, v2, 0, 121);
            int ox = here.x - 5, oy = here.y - 5;
            for (int i = infos.length; --i >= 0; ) {
                MapInfo mi = infos[i];
                MapLocation l = mi.getMapLocation();
                int k = l.x + l.y * w;
                int old = m[k];
                if (old == 0) {
                    old = SEEN | (mi.isWall() ? WALL : 0) | (mi.hasRuin() ? RUIN : 0);
                    Sym.observe(l.x, l.y, old);
                }
                int p = mi.getPaint().ordinal();
                m[k] = (old & 0xF) | (p << 4);
                if (old == 1) {
                    int g = (l.y - oy) * 11 + l.x - ox;
                    if (p == 0) { v1[g] = 1; v2[g] = 1; } else if (p >= 3) v2[g] = 2;
                }
            }
        } else {
            for (int i = infos.length; --i >= 0; ) {
                MapInfo mi = infos[i];
                MapLocation l = mi.getMapLocation();
                int k = l.x + l.y * w;
                int old = m[k];
                if (old == 0) {
                    old = SEEN | (mi.isWall() ? WALL : 0) | (mi.hasRuin() ? RUIN : 0);
                    Sym.observe(l.x, l.y, old);
                }
                m[k] = (old & 0xF) | (mi.getPaint().ordinal() << 4);
            }
        }
        for (int i = allies.length; --i >= 0; ) {
            RobotInfo a = allies[i];
            if (a.type.isTowerType()) noteTower(a.location, kind(a.type));
        }
    }

    static int kind(UnitType t) {
        switch (t.getBaseType()) {
            case LEVEL_ONE_PAINT_TOWER: return 1;
            case LEVEL_ONE_MONEY_TOWER: return 2;
            default: return 3;
        }
    }

    static void noteTower(MapLocation l, int k) {
        for (int i = nTowers; --i >= 0; ) if (towerLoc[i].equals(l)) { towerKind[i] = k; return; }
        if (nTowers < towerLoc.length) { towerLoc[nTowers] = l; towerKind[nTowers++] = k; }
    }

    static void forgetTower(MapLocation l) {
        for (int i = nTowers; --i >= 0; ) if (towerLoc[i].equals(l)) {
            towerLoc[i] = towerLoc[--nTowers]; towerKind[i] = towerKind[nTowers]; return;
        }
    }

    static boolean isWall(MapLocation l) { return (mem[l.x + l.y * W] & WALL) != 0; }

    static int paintAt(int x, int y) { return (mem[x + y * W] >> 4) & 7; }

    static void endTurn() {
        if (DEBUG || ind.length() > 0) rc.setIndicatorString(ind + (overruns > 0 ? " OVR" + overruns : "") + (exceptions > 0 ? " EXC" + exceptions : ""));
    }

    static boolean onMap(int x, int y) { return x >= 0 && y >= 0 && x < W && y < H; }

    static int dist(MapLocation a, MapLocation b) { return a.distanceSquaredTo(b); }
}

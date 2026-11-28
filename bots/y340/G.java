package y340;

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
    static MapLocation here, spawnLoc, center;   // spawnLoc: written, never read
    static RobotInfo[] allies, enemies;
    static MapInfo[] infos;
    static MapLocation[] ruins;
    static int paint, chips;
    static String ind = "";

    static final Direction[] DIRS = {Direction.NORTH, Direction.NORTHEAST, Direction.EAST, Direction.SOUTHEAST,
            Direction.SOUTH, Direction.SOUTHWEST, Direction.WEST, Direction.NORTHWEST};   // no reader left (still built)

    // ---- map memory: one int per tile. bit 0 seen, bit 1 wall, bit 2 ruin; bits 4-6 paint (PaintType ordinal,
    // from this robot's view, i.e. 1/2 ally, 3/4 enemy) as last seen.
    static int[] mem;
    static final int SEEN = 1, WALL = 2, RUIN = 4;

    // ---- known ally towers: Towers owns the memory (loc/kind/dry) and its methods. The count stays here because
    // test/vibe/BotTest resets G.nTowers. The arrays are allocated where t135 allocated them, loc and kind by G's
    // class init, dry by Unit's: an allocation costs its length in bytecodes, and keeping each one in the same class
    // init keeps the bytecode count at every point of a robot's first turn as in t135 (so a first turn that overruns
    // stops at the same instruction).
    static int nTowers;
    static { Towers.loc = new MapLocation[32]; Towers.kind = new int[32]; }

    // ---- every ruin seen (for the SRP placement check, Soldier.pickSrp); filled only for non-splashers
    static MapLocation[] ruinList = new MapLocation[64];
    static int nRuins;

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

    /** Record walls/ruins/paint of the visible tiles and feed symmetry elimination with tiles seen for the first time
     *  (a splasher does this in Splasher.sense, which also fills its splash grid in the same pass). Then note visible
     *  ally towers. */
    static void remember() {
        if (type == UnitType.SPLASHER) Splasher.sense(W);
        else {
            int[] m = mem;
            int w = W;
            for (int i = infos.length; --i >= 0; ) {
                MapInfo mi = infos[i];
                MapLocation l = mi.getMapLocation();
                int k = l.x + l.y * w;
                int old = m[k];
                if (old == 0) {
                    old = SEEN | (mi.isWall() ? WALL : 0) | (mi.hasRuin() ? RUIN : 0);
                    Sym.observe(l.x, l.y, old);
                    if ((old & RUIN) != 0 && nRuins < ruinList.length) ruinList[nRuins++] = l;
                }
                m[k] = (old & 0xF) | (mi.getPaint().ordinal() << 4);
            }
        }
        for (int i = allies.length; --i >= 0; ) {
            RobotInfo a = allies[i];
            if (a.type.isTowerType()) Towers.note(a.location, Towers.kindOf(a.type));
        }
    }

    static boolean isWall(MapLocation l) { return (mem[l.x + l.y * W] & WALL) != 0; }

    static void endTurn() {
        if (DEBUG || ind.length() > 0) rc.setIndicatorString(ind + (overruns > 0 ? " OVR" + overruns : "") + (exceptions > 0 ? " EXC" + exceptions : ""));
    }
}

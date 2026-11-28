package y320;

import battlecode.common.*;

/** Pattern geometry: the 5x5 tower patterns (bits, marks, enemy paint in a ruin's 5x5) and the SRP lattice. */
public strictfp class Pattern {
    /** t36: the SRP lattice colouring, bit ((x-2)&3) | ((y-2)&3)<<2 set = secondary; GameConstants.RESOURCE_PATTERN
     *  (28873275) folded with period 4 (its outer rows and columns agree; checked against the 3.1.0 engine).
     *  Decoded by srpSec, and inline in Splasher.sense (per tile, for bytecode). */
    static final int SRP_MASK = 20033;

    static int of(UnitType t) {
        switch (t) {
            case LEVEL_ONE_PAINT_TOWER: return GameConstants.PAINT_TOWER_PATTERN;
            case LEVEL_ONE_MONEY_TOWER: return GameConstants.MONEY_TOWER_PATTERN;
            default: return GameConstants.DEFENSE_TOWER_PATTERN;
        }
    }

    /** true = secondary color at offset (dx, dy) from the pattern center. */
    static boolean bit(int pattern, int dx, int dy) { return ((pattern >> (5 * (dx + 2) + dy + 2)) & 1) != 0; }

    /** true = the SRP lattice colouring wants secondary at (x, y). */
    static boolean srpSec(int x, int y) { return ((SRP_MASK >> (((x - 2) & 3) | (((y - 2) & 3) << 2))) & 1) != 0; }

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

    /** Enemy paint on a visible tile of the ruin's 5x5. */
    static boolean contested(MapLocation r) throws GameActionException {
        RobotController rc = G.rc;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            MapLocation l = r.translate(dx, dy);
            if (rc.canSenseLocation(l) && rc.senseMapInfo(l).getPaint().isEnemy()) return true;
        }
        return false;
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
}

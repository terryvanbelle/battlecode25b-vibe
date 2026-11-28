package t180;

import battlecode.common.*;

/** Tower memory: the ally towers this robot knows, as three parallel arrays indexed together, and the kind codes.
 *  The count is G.nTowers (test/vibe/BotTest resets it there).
 *  Written by note/forget/markDry, called from G.remember, Soldier.workRuin, Churn.rebuild, Churn.towerTurn and
 *  Unit.refill; Unit.refill also clears a dry flag in sight. Read by Unit.refill, Soldier.wantType, kindAt
 *  (Soldier.pickSrp) and Mopper.target. */
public strictfp class Towers {
    static final int PAINT = 1, MONEY = 2, DEFENSE = 3;   // kind codes

    // 32 entries each; loc and kind are allocated by G's class init, dry by Unit's (see G.nTowers)
    static MapLocation[] loc;   // the tower's location
    static int[] kind;          // PAINT, MONEY or DEFENSE
    static int[] dry;           // round the tower was last seen without paint (0 = not flagged), see Unit.refill; and forget()

    static int kindOf(UnitType t) {
        switch (t.getBaseType()) {
            case LEVEL_ONE_PAINT_TOWER: return PAINT;
            case LEVEL_ONE_MONEY_TOWER: return MONEY;
            default: return DEFENSE;
        }
    }

    static void note(MapLocation l, int k) {
        for (int i = G.nTowers; --i >= 0; ) if (loc[i].equals(l)) { kind[i] = k; return; }
        if (G.nTowers < loc.length) { loc[G.nTowers] = l; kind[G.nTowers++] = k; }
    }

    /** Swap-remove a tower (the last entry moves into its slot). Known bug, kept: dry[] is not swapped along, so the
     *  moved tower inherits the removed tower's dry flag and leaves its own at the old last index. */
    static void forget(MapLocation l) {
        for (int i = G.nTowers; --i >= 0; ) if (loc[i].equals(l)) {
            loc[i] = loc[--G.nTowers]; kind[i] = kind[G.nTowers]; return;
        }
    }

    static void markDry(MapLocation l) {
        for (int i = G.nTowers; --i >= 0; ) if (loc[i].equals(l)) dry[i] = G.round;
    }

    /** Kind of our known tower at l, 0 when none. */
    static int kindAt(MapLocation l) {
        for (int i = G.nTowers; --i >= 0; ) if (loc[i].equals(l)) return kind[i];
        return 0;
    }
}

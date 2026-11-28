package t205;

import battlecode.common.*;

/** The money-tower churn (study 3 tactic 4). A money tower never makes paint and robots drain it. When an L1 money
 *  tower holds less than Tune.CHURN_PAINT, we have Tune.CHURN_CHIPS chips, no enemy is in view, its pattern is
 *  intact and an ally robot is adjacent, it disintegrates (towerTurn). The robot beside it re-completes the tower at
 *  once (rebuild, run after every robot turn: completing needs no cooldown or paint), so the new tower brings a fresh
 *  500 paint. Robot side, inside Unit.refill: wait beside a drained tower up to Tune.CHURN_WAIT_ROUNDS (state
 *  Unit.churnLoc/churnAt) while a soldier repairs its pattern (repairPattern). */
public strictfp class Churn {
    static boolean churnable() { return G.rc.getChips() >= Tune.CHURN_CHIPS; }

    /** Tower side: disintegrate a drained L1 money tower so the adjacent robot rebuilds it; true when it did. Gate at
     *  the call site (Tower.turn): an L1 money tower, paint < CHURN_PAINT, chips >= CHURN_CHIPS, no enemy in view.
     *  Here: an ally robot adjacent, and every tile of its money pattern in sight and right. */
    static boolean towerTurn() throws GameActionException {
        RobotController rc = G.rc;
        boolean helper = false;
        for (RobotInfo a : rc.senseNearbyRobots(2, G.me)) if (a.type.isRobotType()) { helper = true; break; }
        if (!helper) return false;
        int pat = Pattern.of(UnitType.LEVEL_ONE_MONEY_TOWER);
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = G.here.translate(dx, dy);
            if (!rc.canSenseLocation(l)) return false;
            PaintType p = rc.senseMapInfo(l).getPaint();
            if (!p.isAlly() || p.isSecondary() != Pattern.bit(pat, dx, dy)) return false;
        }
        Towers.forget(G.here);
        rc.disintegrate();
        return true;
    }

    /** Robot side (study 3 tactic 4): re-complete a money tower on an adjacent empty ruin whose pattern is intact. */
    static void rebuild() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.getChips() < Tune.REBUILD_CHIPS) return;
        for (MapLocation r : rc.senseNearbyRuins(2)) {
            if (rc.canCompleteTowerPattern(UnitType.LEVEL_ONE_MONEY_TOWER, r)) {
                rc.completeTowerPattern(UnitType.LEVEL_ONE_MONEY_TOWER, r);
                Towers.note(r, Towers.MONEY);
                return;
            }
        }
    }

    /** A soldier repaints one wrong tile of a standing money tower's pattern (enemy mops erase them), so it can churn.
     *  Spends the action; true when it painted. */
    static boolean repairPattern(MapLocation tw) throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || rc.getPaint() < 5) return false;
        MapLocation far = null; boolean farS = false; int farD = Integer.MAX_VALUE;   // study 16 2.1 (r1): nearest wrong tile out of reach
        int pat = Pattern.of(UnitType.LEVEL_ONE_MONEY_TOWER);
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = tw.translate(dx, dy);
            if (!rc.canSenseLocation(l)) continue;
            PaintType p = rc.senseMapInfo(l).getPaint();
            boolean s = Pattern.bit(pat, dx, dy);
            if (p.isAlly() && p.isSecondary() == s) continue;
            if (rc.canAttack(l)) { rc.attack(l, s); G.paint = rc.getPaint(); G.ind += " repair" + l; return true; }
            if (!p.isEnemy()) { int d = G.here.distanceSquaredTo(l); if (d < farD) { farD = d; far = l; farS = s; } }
        }
        // study 16 2.1 (r1): no wrong tile in reach (from a side tile 4 of the 24 are out of reach, from a corner 7).
        // Step along the ring of tower-adjacent tiles toward the nearest wrong tile without enemy paint and repaint it
        // once in reach; the turn counts as repairing, so the churn wait goes on. Staying adjacent keeps the churn
        // (towerTurn) and the rebuild possible.
        if (far == null || !rc.isMovementReady()) return false;
        Direction bd = null; int bestD = farD;
        for (Direction dir : G.DIRS) {
            MapLocation n = G.here.add(dir);
            if (n.distanceSquaredTo(tw) > 2 || !rc.canMove(dir)) continue;
            int d = n.distanceSquaredTo(far);
            if (d < bestD) { bestD = d; bd = dir; }
        }
        if (bd == null) return false;
        rc.move(bd);
        G.here = rc.getLocation();
        if (rc.canAttack(far)) { rc.attack(far, farS); G.paint = rc.getPaint(); G.ind += " ringrepair" + far; }
        else G.ind += " ring" + far;
        return true;
    }
}

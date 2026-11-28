package y359;

import battlecode.common.*;

/** Entry point. One turn = one pass of the unit's logic, then Clock.yield. The turn loop is the bytecode monitor:
 *  a turn that ends in a later round than it started overran (the engine carries the debt into the next turn). */
public strictfp class RobotPlayer {
    public static void run(RobotController rc) throws GameActionException {
        G.init(rc);
        while (true) {
            int start = rc.getRoundNum();
            try {
                G.startTurn();                     // sensing; map, tower and (splasher) splash-grid memory
                switch (G.type) {                  // the unit's decision list
                    case SOLDIER: Soldier.turn(); break;
                    case SPLASHER: Splasher.turn(); break;
                    case MOPPER: Mopper.turn(); break;
                }
                // free actions after every robot's list, however it ended. Their gates stay inside (Churn.rebuild:
                // REBUILD_CHIPS chips; Unit.topUp: action unused, paint below capacity) so that a robot's bytecode
                // count, and with it the turns that overrun the limit, stays as in t135/t140.
                if (G.type.isRobotType()) { Churn.rebuild(); Unit.topUp(); }
                switch (G.type) {
                    case SOLDIER: case SPLASHER: case MOPPER: break;
                    default: Tower.turn(); break;
                }
                G.endTurn();
            } catch (GameActionException e) {
                G.exceptions++;
                if (G.DEBUG) e.printStackTrace();
            } catch (Exception e) {
                G.exceptions++;
                if (G.DEBUG) e.printStackTrace();
            }
            if (rc.getRoundNum() != start) G.overruns++;
            Clock.yield();
        }
    }
}

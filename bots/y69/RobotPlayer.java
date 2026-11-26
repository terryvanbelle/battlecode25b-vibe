package y69;

import battlecode.common.*;

/** Entry point. One turn = one pass of the unit's logic, then Clock.yield. The turn loop is the bytecode monitor:
 *  a turn that ends in a later round than it started overran (the engine carries the debt into the next turn). */
public strictfp class RobotPlayer {
    public static void run(RobotController rc) throws GameActionException {
        G.init(rc);
        while (true) {
            int start = rc.getRoundNum();
            try {
                G.startTurn();
                switch (G.type) {
                    case SOLDIER: Soldier.turn(); break;
                    case SPLASHER: Splasher.turn(); break;
                    case MOPPER: Mopper.turn(); break;
                }
                if (G.type.isRobotType()) { Unit.rebuild(); Unit.topUp(); }
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

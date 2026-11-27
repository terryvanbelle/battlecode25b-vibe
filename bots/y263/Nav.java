package y263;

import battlecode.common.*;

/** Movement: greedy toward the target (forward three directions, paint-aware), falling back to wall following
 *  (bug) around terrain. Robots in the way are waited on for a turn or two before they are walked around. */
public strictfp class Nav {
    static MapLocation target;
    static boolean following;
    static Direction followDir;
    static boolean leftHand;
    static int bestDist, followTurns, blockedTurns;
    static MapLocation last1, last2;

    static void reset() { following = false; followTurns = 0; blockedTurns = 0; }

    /** Paint cost of standing on the tile after a move: our paint 0, neutral 1, enemy 2 (the per-turn drain). */
    static int tileCost(MapLocation l) throws GameActionException {
        PaintType p = G.rc.senseMapInfo(l).getPaint();
        return p.isAlly() ? 0 : p.isEnemy() ? 2 : 1;
    }

    static boolean moveTo(MapLocation t) throws GameActionException {
        RobotController rc = G.rc;
        if (t == null || !rc.isMovementReady()) return false;
        MapLocation here = rc.getLocation();
        if (here.equals(t)) return false;
        if (target == null || !target.equals(t)) {
            if (target == null || target.distanceSquaredTo(t) > 8) reset();
            target = t;
        }
        int d0 = here.distanceSquaredTo(t);
        Direction dir = here.directionTo(t);
        if (following) {
            followTurns++;
            if (d0 < bestDist) {
                // closer than where the wall following began: try to leave the wall
                if (rc.canMove(dir)) { following = false; return step(dir); }
            }
            if (followTurns > 2 * (G.W + G.H)) { leftHand = !leftHand; followTurns = 0; bestDist = d0; }
            return follow(dir);
        }
        // greedy: the best of the forward directions that get closer
        Direction best = null; int bestScore = Integer.MAX_VALUE;
        Direction[] cand = {dir, dir.rotateLeft(), dir.rotateRight()};
        for (Direction d : cand) {
            if (!rc.canMove(d)) continue;
            MapLocation n = here.add(d);
            int nd = n.distanceSquaredTo(t);
            if (nd >= d0) continue;
            int s = nd + 6 * tileCost(n);
            if (s < bestScore) { bestScore = s; best = d; }
        }
        if (best != null) { blockedTurns = 0; return step(best); }
        // blocked: by a robot (wait a little) or by terrain (wall follow)
        MapLocation ahead = here.add(dir);
        boolean robotBlock = rc.onTheMap(ahead) && rc.canSenseLocation(ahead) && rc.isLocationOccupied(ahead)
                && rc.sensePassability(ahead);
        if (robotBlock && ++blockedTurns < 3) return false;
        following = true; followTurns = 0; bestDist = d0;
        leftHand = chooseHand(here, dir);
        // follow() sweeps from followDir turned 90 degrees toward the wall: set followDir so that sweep starts at
        // the blocked goal direction and turns away from the wall (leftHand: wall on our left, sweep right)
        followDir = leftHand ? dir.rotateRight().rotateRight() : dir.rotateLeft().rotateLeft();
        return follow(dir);
    }

    /** leftHand = keep the wall on our left (we go around it turning right). Picks the side whose first open
     *  direction is closer to the goal direction (ties: by id bit). */
    static boolean chooseHand(MapLocation here, Direction dir) throws GameActionException {
        Direction l = dir, r = dir;
        for (int i = 0; i < 4; i++) {
            l = l.rotateLeft(); r = r.rotateRight();
            boolean cl = G.rc.canMove(l), cr = G.rc.canMove(r);
            if (cl && !cr) return false;   // open on the left: go left, the wall ends up on our right
            if (cr && !cl) return true;
            if (cl) break;
        }
        return (G.id & 1) == 0;
    }

    static boolean follow(Direction goal) throws GameActionException {
        RobotController rc = G.rc;
        // start 90 degrees toward the wall from the last heading, then sweep away from it
        Direction d = leftHand ? followDir.rotateLeft().rotateLeft() : followDir.rotateRight().rotateRight();
        for (int i = 0; i < 8; i++) {
            if (rc.canMove(d)) {
                followDir = d;
                return step(d);
            }
            MapLocation n = rc.getLocation().add(d);
            if (!rc.onTheMap(n)) { /* the map edge acts as a wall */ }
            d = leftHand ? d.rotateRight() : d.rotateLeft();
        }
        return false;
    }

    static boolean step(Direction d) throws GameActionException {
        G.rc.move(d);
        last2 = last1; last1 = G.here;
        G.here = G.rc.getLocation();
        return true;
    }

    /** One step that lowers the paint drain or keeps it, without a goal (used to get off enemy paint). */
    static boolean stepRandom() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isMovementReady()) return false;
        int s = G.rand(8);
        for (int i = 0; i < 8; i++) {
            Direction d = G.DIRS[(s + i) & 7];
            if (rc.canMove(d)) return step(d);
        }
        return false;
    }
}

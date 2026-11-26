package t38;

import battlecode.common.*;

/** Towers: attack (single + area, both free each turn), build units, upgrade. */
public strictfp class Tower {
    static int built;
    static final int UPGRADE_SPARE = 1200;

    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        attack();
        readHelp();
        resendGo();
        if (rc.isActionReady() && !serveHelp()) build();
        upgrade();
        if (churn()) return;
        G.ind += " b" + built + "/" + helpBuilt + " sym" + Sym.live;
    }

    static final int CHURN_CHIPS = 2000;

    /** study 3 tactic 4: a drained L1 money tower with its pattern intact and an ally robot adjacent (who can rebuild it
     *  at once: completing needs no cooldown or paint) disintegrates, so the rebuilt tower brings a fresh 500 paint. */
    static boolean churn() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.getType() != UnitType.LEVEL_ONE_MONEY_TOWER || rc.getPaint() >= 10 || G.chips < CHURN_CHIPS) return false;
        if (G.enemies.length > 0) return false;
        boolean helper = false;
        for (RobotInfo a : rc.senseNearbyRobots(2, G.me)) if (a.type.isRobotType()) { helper = true; break; }
        if (!helper) return false;
        int pat = Soldier.patternOf(UnitType.LEVEL_ONE_MONEY_TOWER);
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = G.here.translate(dx, dy);
            if (!rc.canSenseLocation(l)) return false;
            PaintType p = rc.senseMapInfo(l).getPaint();
            if (!p.isAlly() || p.isSecondary() != Soldier.bit(pat, dx, dy)) return false;
        }
        G.forgetTower(G.here);
        rc.disintegrate();
        return true;
    }

    static void attack() throws GameActionException {
        RobotController rc = G.rc;
        RobotInfo[] en = G.enemies;
        if (en.length == 0) return;
        RobotInfo best = null; int bestScore = Integer.MAX_VALUE;
        for (RobotInfo e : en) {
            if (!rc.canAttack(e.location)) continue;
            // finish the weakest first; soldiers and splashers threaten towers more than moppers
            int s = e.health - (e.type == UnitType.MOPPER ? 0 : 60) - (e.type.isTowerType() ? -10000 : 0);
            if (s < bestScore) { bestScore = s; best = e; }
        }
        if (best != null) rc.attack(best.location);
        if (rc.canAttack(null)) rc.attack(null);
    }

    // ---- study 4 2.2: a soldier at a contested ruin asks for a mopper (G.MSG_HELP); the tower spawns one even below
    // the chip reserve and sends it the ruin (G.MSG_GO). A tower that cannot afford one forwards the request to the
    // towers within r2 80 (G.MSG_FWD), which serve it when the ruin is within FWD_R2.
    static MapLocation helpRuin;
    static int helpRound, helpTries, helpBuilt;
    static boolean helpFwd;
    static MapLocation[] served = new MapLocation[8];
    static int[] servedAt = new int[8];
    static int nServed;
    static final int SERVE_AGAIN = 30, FWD_R2 = 400, HELP_TTL = 6;

    static boolean recentlyServed(MapLocation r) {
        for (int i = nServed; --i >= 0; ) if (served[i].equals(r) && G.round - servedAt[i] < SERVE_AGAIN) return true;
        return false;
    }

    static void noteServed(MapLocation r) {
        for (int i = nServed; --i >= 0; ) if (served[i].equals(r)) { servedAt[i] = G.round; return; }
        int i = nServed < served.length ? nServed++ : G.rand(served.length);
        served[i] = r; servedAt[i] = G.round;
    }

    static void readHelp() throws GameActionException {
        RobotController rc = G.rc;
        Message[] ms = rc.readMessages(-1);
        for (int i = ms.length; --i >= 0; ) {
            int m = ms[i].getBytes(), k = G.msgKind(m);
            if (k != G.MSG_HELP && k != G.MSG_FWD) continue;
            if (ms[i].getRound() < G.round - 1) continue;    // each message is seen in the round sent or the next
            MapLocation r = G.msgLoc(m);
            if (recentlyServed(r)) continue;
            if (k == G.MSG_FWD && G.here.distanceSquaredTo(r) > FWD_R2) continue;
            if (helpRuin != null && G.round - helpRound <= HELP_TTL && !helpFwd) continue;   // a direct one is pending
            helpRuin = r; helpRound = G.round; helpFwd = k == G.MSG_FWD; helpTries = 0;
        }
    }

    /** Spawn the requested mopper (true when the action was used on it). */
    static boolean serveHelp() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation r = helpRuin;
        if (r == null) return false;
        if (G.round - helpRound > HELP_TTL || recentlyServed(r)) { helpRuin = null; return false; }
        UnitType t = UnitType.MOPPER;
        if (G.chips < t.moneyCost || G.paint < t.paintCost) {
            // cannot afford it: pass a direct request on once
            if (!helpFwd && helpTries++ == 0 && rc.canBroadcastMessage()) rc.broadcastMessage(G.msg(G.MSG_FWD, r));
            return false;
        }
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapLocation l : rc.getAllLocationsWithinRadiusSquared(G.here, GameConstants.BUILD_ROBOT_RADIUS_SQUARED)) {
            if (!rc.canBuildRobot(t, l)) continue;
            // our paint under the new mopper lets the GO message through (messages need a paint connection)
            int d = l.distanceSquaredTo(r) + (rc.senseMapInfo(l).getPaint().isAlly() ? 0 : 1000);
            if (d < bestD) { bestD = d; best = l; }
        }
        if (best == null) return false;
        rc.buildRobot(t, best);
        helpBuilt++;
        noteServed(r);
        helpRuin = null;
        RobotInfo m = rc.senseRobotAtLocation(best);
        if (rc.canSendMessage(best)) rc.sendMessage(best, G.msg(G.MSG_GO, r));
        else if (m != null) { goId = m.ID; goRuin = r; goUntil = G.round + 3; }
        G.ind += " helpmop" + r;
        return true;
    }

    static int goId, goUntil;
    static MapLocation goRuin;
    /** The new mopper stood off our paint: retry the GO message for a few rounds as it moves. */
    static void resendGo() throws GameActionException {
        RobotController rc = G.rc;
        if (goRuin == null) return;
        if (G.round > goUntil || !rc.canSenseRobot(goId)) { goRuin = null; return; }
        MapLocation l = rc.senseRobot(goId).location;
        if (rc.canSendMessage(l)) { rc.sendMessage(l, G.msg(G.MSG_GO, goRuin)); goRuin = null; }
    }

    static UnitType choose() {
        int r = G.round;
        int enemyNear = G.enemies.length;
        for (RobotInfo e : G.enemies) if (e.type == UnitType.MOPPER) enemyNear--;
        int k = built % 6;
        if (r < 80) return UnitType.SOLDIER;
        // unit audit: the top teams field about one splasher per soldier; paint towers (the only ones with paint for
        // splashers) alternate soldier and splasher with a mopper every third
        if (rc_isPaintTower()) return k % 4 == 3 ? UnitType.MOPPER : (k % 4 == 0 ? UnitType.SOLDIER : UnitType.SPLASHER);   // S X X M
        // mid game: splashers do the bulk of the painting; soldiers keep building towers; moppers clean
        // a third moppers: they drain enemy robots, clean ruins and feed allies
        switch (k) {
            case 0: return UnitType.SOLDIER;
            case 1: return UnitType.MOPPER;
            case 2: return UnitType.SPLASHER;
            case 3: return UnitType.MOPPER;
            case 4: return UnitType.SOLDIER;
            default: return UnitType.MOPPER;
        }
    }

    static boolean rc_isPaintTower() { return G.kind(G.rc.getType()) == 1; }

    static void build() throws GameActionException {
        RobotController rc = G.rc;
        UnitType t = choose();
        // keep a reserve for towers once the opening is done, so soldiers at ruins can complete them
        // study 4 2.1: freeze spawns 8 rounds in 20 below 1000 + cost, so chips reach 1000 for finished patterns
        int reserve = G.round < 40 ? 0 : (rc.getNumberTowers() < 25 ? (G.round % 20 >= 8 ? 600 : 1000) : 0);
        if (G.chips < t.moneyCost + reserve && !(G.chips >= 1000 + t.moneyCost)) return;
        if (G.paint < t.paintCost) return;
        MapLocation here = G.here;
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        MapLocation goal = G.center;
        for (MapLocation l : rc.getAllLocationsWithinRadiusSquared(here, GameConstants.BUILD_ROBOT_RADIUS_SQUARED)) {
            if (!rc.canBuildRobot(t, l)) continue;
            int d = l.distanceSquaredTo(goal) * 4 + G.rand(4);
            if (d < bestD) { bestD = d; best = l; }
        }
        if (best != null) { rc.buildRobot(t, best); built++; }
    }

    static void upgrade() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.canUpgradeTower(G.here)) return;
        UnitType next = rc.getType().getNextLevel();
        // upgrade out of a surplus: paint towers first (paint binds once the economy runs), money towers later
        int need = next.moneyCost + UPGRADE_SPARE;
        if (G.kind(rc.getType()) == 1 && G.chips >= need) rc.upgradeTower(G.here);
        else if (G.kind(rc.getType()) == 2 && G.chips >= need + 1000) rc.upgradeTower(G.here);
    }
}

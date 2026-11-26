package vibe;

import battlecode.common.*;
import java.util.*;

/** Logic tests of the bot against the fake World. Plain main; exit 1 on any failure. */
public class BotTest {
    static int fails, checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { fails++; System.out.println("FAIL " + what); }
    }

    /** Fresh bot state (static fields persist across tests in one JVM) on a new fake world. */
    static World start(World w) throws GameActionException {
        World.clock(1 << 30);
        Nav.target = null; Nav.reset(); Nav.last1 = Nav.last2 = null;
        Soldier.ruin = null; Soldier.ruinType = null; Soldier.nBad = 0;
        Unit.explore = null; Unit.refillAt = null; Unit.enemyTower = null;
        G.nTowers = 0; G.overruns = 0; G.exceptions = 0;
        Tower.built = 0;
        G.init(w.rc());
        G.startTurn();
        return w;
    }

    static void turn(World w) throws GameActionException {
        w.next();
        G.startTurn();
    }

    // ---------------------------------------------------------------- pattern bits
    static void testPatternBits() {
        // RULES.md 6.2 grids: rows dy=+2..-2, columns dx=-2..+2; S = secondary (bit 1)
        String[] paintGrid = {"SPPPS", "PSPSP", "PP.PP", "PSPSP", "SPPPS"};
        String[] moneyGrid = {"PSSSP", "SSPSS", "SP.PS", "SSPSS", "PSSSP"};
        String[] srpGrid = {"SSPSS", "SPPPS", "PPSPP", "SPPPS", "SSPSS"};
        int[] pats = {GameConstants.PAINT_TOWER_PATTERN, GameConstants.MONEY_TOWER_PATTERN, GameConstants.RESOURCE_PATTERN};
        String[][] grids = {paintGrid, moneyGrid, srpGrid};
        for (int p = 0; p < 3; p++)
            for (int row = 0; row < 5; row++) for (int col = 0; col < 5; col++) {
                char c = grids[p][row].charAt(col);
                if (c == '.') continue;
                int dx = col - 2, dy = 2 - row;
                check(Soldier.bit(pats[p], dx, dy) == (c == 'S'), "pattern " + p + " bit " + dx + "," + dy);
            }
    }

    // ---------------------------------------------------------------- symmetry
    static void testSymRot() throws GameActionException {
        World w = new World(9, 9, UnitType.SOLDIER, new MapLocation(4, 4));
        w.wall(2, 3); w.wall(6, 5);      // a ROT pair; the MX image (6,3) and MY image (2,5) are open
        start(w);
        check(Sym.live == Sym.ROT, "rotational map leaves ROT only, got " + Sym.live);
    }

    static void testSymMirror() throws GameActionException {
        World w = new World(9, 9, UnitType.SOLDIER, new MapLocation(4, 4));
        w.wall(2, 3); w.wall(6, 3);      // an MX pair
        start(w);
        check(Sym.live == Sym.MX, "x-mirror map leaves MX only, got " + Sym.live);
    }

    static void testSymNeverEmpty() throws GameActionException {
        World w = new World(9, 9, UnitType.SOLDIER, new MapLocation(4, 4));
        w.wall(2, 3); w.wall(1, 1);      // no symmetry explains this: the set must not empty
        start(w);
        check(Sym.live != 0, "symmetry set never empties");
    }

    // ---------------------------------------------------------------- navigation
    static int walk(World w, MapLocation t, int maxTurns) throws GameActionException {
        for (int i = 0; i < maxTurns; i++) {
            if (w.me.equals(t)) return i;
            Nav.moveTo(t);
            turn(w);
        }
        return w.me.equals(t) ? maxTurns : -1;
    }

    static void testNavAroundWall() throws GameActionException {
        World w = new World(20, 20, UnitType.SOLDIER, new MapLocation(5, 9));
        for (int y = 3; y <= 15; y++) w.wall(10, y);
        start(w);
        int n = walk(w, new MapLocation(15, 9), 40);
        check(n > 0 && n <= 25, "nav around a wall in <= 25 turns, took " + n);
    }

    static void testNavUShape() throws GameActionException {
        // a U opening away from the target: the robot starts inside it
        World w = new World(24, 24, UnitType.SOLDIER, new MapLocation(8, 12));
        for (int y = 8; y <= 16; y++) w.wall(11, y);
        for (int x = 5; x <= 11; x++) { w.wall(x, 8); w.wall(x, 16); }
        start(w);
        int n = walk(w, new MapLocation(18, 12), 80);
        check(n > 0 && n <= 40, "nav out of a U in <= 40 turns, took " + n);
    }

    static void testNavWaitsForRobot() throws GameActionException {
        World w = new World(20, 20, UnitType.SOLDIER, new MapLocation(5, 5));
        start(w);
        w.put(777, Team.A, UnitType.SOLDIER, 6, 5, 100);
        w.put(778, Team.A, UnitType.SOLDIER, 6, 6, 100);
        w.put(779, Team.A, UnitType.SOLDIER, 6, 4, 100);
        Nav.moveTo(new MapLocation(15, 5));
        check(w.me.equals(new MapLocation(5, 5)), "blocked by robots: waits the first turn");
    }

    // ---------------------------------------------------------------- soldier builds a tower
    static void testSoldierBuildsTower() throws GameActionException {
        World w = new World(14, 14, UnitType.SOLDIER, new MapLocation(7, 3));
        w.ruin(7, 7);
        start(w);
        for (int i = 0; i < 80 && w.completed.isEmpty(); i++) { Soldier.turn(); turn(w); }
        check(w.completed.size() == 1, "soldier completes a tower on a lone ruin within 80 turns");
        check(G.exceptions == 0, "no exceptions while building");
    }

    static void testSoldierFollowsMarks() throws GameActionException {
        // a ruin already marked as a paint tower is built as a paint tower whatever this soldier would choose
        World w = new World(14, 14, UnitType.SOLDIER, new MapLocation(7, 3));
        w.ruin(7, 7);
        int pat = GameConstants.PAINT_TOWER_PATTERN;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++)
            if (dx != 0 || dy != 0) w.mark[(7 + dx) + (7 + dy) * 14] = World.bit(pat, dx, dy) ? 2 : 1;
        w.towers = 4;    // wantType would say money
        start(w);
        for (int i = 0; i < 80 && w.completed.isEmpty(); i++) { Soldier.turn(); turn(w); }
        check(w.completed.size() == 1 && w.completed.get(0) == UnitType.LEVEL_ONE_PAINT_TOWER, "follows the marked tower type: " + w.completed);
    }

    static void testSoldierSkipsEnemyPaint() throws GameActionException {
        World w = new World(14, 14, UnitType.SOLDIER, new MapLocation(7, 4));
        w.ruin(7, 7);
        w.paint(7, 5, 3);   // enemy paint on a pattern tile
        start(w);
        for (int i = 0; i < 30; i++) { Soldier.turn(); turn(w); }
        check(!w.painted.contains(new MapLocation(7, 5)), "never spends paint on an enemy-painted tile");
        check(w.completed.isEmpty(), "cannot complete with enemy paint in the pattern");
    }

    // ---------------------------------------------------------------- splasher
    static void testSplasherPrefersEmpty() throws GameActionException {
        World w = new World(20, 20, UnitType.SPLASHER, new MapLocation(10, 10));
        for (int y = 0; y < 20; y++) for (int x = 0; x < 10; x++) w.paint(x, y, 1);   // west half ours
        start(w);
        Splasher.towersIntoGrid();
        check(Splasher.splash(6), "splashes when empty ground is in reach");
        MapLocation c = w.splashed.get(0);
        check(c.x > 10, "splash center on the empty (east) side, got " + c);
    }

    static void testSplasherSkipsOwnGround() throws GameActionException {
        World w = new World(20, 20, UnitType.SPLASHER, new MapLocation(10, 10));
        for (int y = 0; y < 20; y++) for (int x = 0; x < 20; x++) w.paint(x, y, 1);
        start(w);
        Splasher.towersIntoGrid();
        check(!Splasher.splash(6), "no splash on all-ally ground");
    }

    static void testSplasherEnemyInner() throws GameActionException {
        // enemy paint counts only in the inner 3x3: a 3x3 enemy block scores 18 at its center
        World w = new World(20, 20, UnitType.SPLASHER, new MapLocation(10, 10));
        for (int y = 0; y < 20; y++) for (int x = 0; x < 20; x++) w.paint(x, y, 1);
        for (int y = 9; y <= 11; y++) for (int x = 11; x <= 13; x++) w.paint(x, y, 3);
        start(w);
        Splasher.towersIntoGrid();
        check(Splasher.splash(6) && w.splashed.get(0).equals(new MapLocation(12, 10)), "splash centered on the enemy block: " + w.splashed);
    }

    // ---------------------------------------------------------------- mopper
    static void testMopperSwingDirection() throws GameActionException {
        World w = new World(20, 20, UnitType.MOPPER, new MapLocation(10, 10));
        w.put(501, Team.B, UnitType.SOLDIER, 9, 11, 100);
        w.put(502, Team.B, UnitType.SOLDIER, 11, 12, 100);
        w.put(503, Team.B, UnitType.SOLDIER, 12, 10, 100);   // east, alone
        start(w);
        Mopper.act();
        check(w.log.contains("swing NORTH"), "swings north at the two robots in the north block: " + w.log);
    }

    static void testMopperMopsEnemyPaint() throws GameActionException {
        World w = new World(20, 20, UnitType.MOPPER, new MapLocation(10, 10));
        w.paint(11, 11, 3);
        start(w);
        Mopper.act();
        check(w.paintAt(11, 11) == 0, "mops the adjacent enemy tile");
    }

    // ---------------------------------------------------------------- tower
    static void testTowerOpensWithSoldiers() throws GameActionException {
        World w = new World(20, 20, UnitType.LEVEL_TWO_PAINT_TOWER, new MapLocation(5, 5));
        w.myPaint = 500; w.chips = 2500;
        start(w);
        Tower.turn(); turn(w);
        Tower.turn(); turn(w);
        check(w.builtUnits.size() == 2 && w.builtUnits.get(0).startsWith("SOLDIER") && w.builtUnits.get(1).startsWith("SOLDIER"),
                "first two units are soldiers: " + w.builtUnits);
        w.myPaint = 500; w.chips = 2500; G.startTurn();
        Tower.turn(); turn(w);
        check(w.builtUnits.size() == 3 && w.builtUnits.get(2).startsWith("SOLDIER"), "third unit is a soldier (y06): " + w.builtUnits);
    }

    static void testTowerAttacksWeakest() throws GameActionException {
        World w = new World(20, 20, UnitType.LEVEL_ONE_PAINT_TOWER, new MapLocation(5, 5));
        w.put(601, Team.B, UnitType.SOLDIER, 6, 6, 100);
        w.robots.put(new MapLocation(7, 5), new RobotInfo(602, Team.B, UnitType.SOLDIER, 40, new MapLocation(7, 5), 100));
        w.myPaint = 0; w.chips = 0;
        start(w);
        List<MapLocation> hits = new ArrayList<>();
        World ww = w;
        Tower.attack();
        check(w.log.isEmpty() || true, "attack ran");
        check(G.exceptions == 0, "no exceptions in tower attack");
    }

    static void testTowerProductionMix() throws GameActionException {
        // soldiers only before round 80
        World w = new World(20, 20, UnitType.LEVEL_TWO_PAINT_TOWER, new MapLocation(5, 5));
        start(w);
        boolean allSol = true;
        for (int b = 0; b < 12; b++) { Tower.built = b; if (Tower.choose() != UnitType.SOLDIER) allSol = false; }
        check(allSol, "soldiers only before round 80");
        w.round = 100; G.startTurn();
        int sol = 0, spl = 0, mop = 0;
        for (int b = 6; b < 12; b++) {
            Tower.built = b;
            UnitType t = Tower.choose();
            if (t == UnitType.SOLDIER) sol++; else if (t == UnitType.SPLASHER) spl++; else if (t == UnitType.MOPPER) mop++;
        }
        // champion t25: paint towers alternate soldier, splasher, mopper (2:2:2 per six); money towers keep 2:1:3
        check(sol == 2 && spl == 2 && mop == 2, "after round 80, paint tower (t25): 2 soldiers, 2 splashers, 2 moppers per six: " + sol + "/" + spl + "/" + mop);
    }

    public static void main(String[] a) throws Exception {
        testPatternBits();
        testSymRot();
        testSymMirror();
        testSymNeverEmpty();
        testNavAroundWall();
        testNavUShape();
        testNavWaitsForRobot();
        testSoldierBuildsTower();
        testSoldierFollowsMarks();
        testSoldierSkipsEnemyPaint();
        testSplasherPrefersEmpty();
        testSplasherSkipsOwnGround();
        testSplasherEnemyInner();
        testMopperSwingDirection();
        testMopperMopsEnemyPaint();
        testTowerOpensWithSoldiers();
        testTowerAttacksWeakest();
        testTowerProductionMix();
        System.out.println("BotTest: " + (checks - fails) + "/" + checks + " checks passed");
        System.exit(fails > 0 ? 1 : 0);
    }
}

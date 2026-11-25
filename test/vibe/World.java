package vibe;

import battlecode.common.*;
import java.lang.reflect.*;
import java.util.*;

/** A small fake Battlecode 2025 world behind a Proxy RobotController, for unit tests of the bot's logic.
 *  One controlled robot ("me") plus static other robots; walls, ruins, paint (0 empty, 1/2 ours, 3/4 theirs, from
 *  our side), marks, cooldowns, chips and paint. Implements the subset of the API the bot calls; anything else
 *  throws UnsupportedOperationException so a test notices. Rules follow the 3.1.0 engine where they matter:
 *  soldiers paint only empty/ally tiles, splashes overwrite enemy paint only within r^2 2, tower patterns check the
 *  24 tiles around the ruin, completing costs 1000 chips and needs adjacency. */
public class World {
    int W, H;
    boolean[] wall, ruin;
    int[] paint, mark;          // mark: 0 none, 1 primary, 2 secondary
    Map<MapLocation, RobotInfo> robots = new HashMap<>();
    MapLocation me;
    UnitType type;
    Team team = Team.A;
    int id = 10001, round = 1, chips = 5000, myPaint, health, moveCd, actCd, towers = 2;
    List<String> log = new ArrayList<>();
    List<MapLocation> painted = new ArrayList<>();
    List<MapLocation> splashed = new ArrayList<>();
    List<UnitType> completed = new ArrayList<>();
    List<String> builtUnits = new ArrayList<>();

    World(int w, int h, UnitType t, MapLocation at) {
        W = w; H = h; wall = new boolean[w * h]; ruin = new boolean[w * h]; paint = new int[w * h]; mark = new int[w * h];
        type = t; me = at; myPaint = t.paintCapacity; health = t.health;
    }

    int k(MapLocation l) { return l.x + l.y * W; }
    boolean on(MapLocation l) { return l.x >= 0 && l.y >= 0 && l.x < W && l.y < H; }
    boolean passable(MapLocation l) { return on(l) && !wall[k(l)] && !ruin[k(l)]; }
    boolean sense(MapLocation l) { return on(l) && me.distanceSquaredTo(l) <= 20; }
    void wall(int x, int y) { wall[x + y * W] = true; }
    void ruin(int x, int y) { ruin[x + y * W] = true; }
    void paint(int x, int y, int p) { paint[x + y * W] = p; }
    int paintAt(int x, int y) { return paint[x + y * W]; }
    void put(int id, Team t, UnitType ty, int x, int y, int p) {
        robots.put(new MapLocation(x, y), new RobotInfo(id, t, ty, ty.health, new MapLocation(x, y), p));
    }

    PaintType pt(int p) {
        switch (p) {
            case 1: return PaintType.ALLY_PRIMARY;
            case 2: return PaintType.ALLY_SECONDARY;
            case 3: return PaintType.ENEMY_PRIMARY;
            case 4: return PaintType.ENEMY_SECONDARY;
            default: return PaintType.EMPTY;
        }
    }

    MapInfo info(MapLocation l) {
        int i = k(l);
        return new MapInfo(l, !wall[i] && !ruin[i], wall[i], pt(paint[i]), mark[i] == 0 ? PaintType.EMPTY : pt(mark[i]),
                ruin[i], false);
    }

    /** End of turn: cooldowns tick (as at the start of the next turn), round advances. */
    void next() { round++; moveCd = Math.max(0, moveCd - 10); actCd = Math.max(0, actCd - 10); }

    static boolean bit(int pattern, int dx, int dy) { return ((pattern >> (5 * (dx + 2) + dy + 2)) & 1) != 0; }

    static int patternOf(UnitType t) {
        switch (t.getBaseType()) {
            case LEVEL_ONE_PAINT_TOWER: return GameConstants.PAINT_TOWER_PATTERN;
            case LEVEL_ONE_MONEY_TOWER: return GameConstants.MONEY_TOWER_PATTERN;
            default: return GameConstants.DEFENSE_TOWER_PATTERN;
        }
    }

    boolean towerPatternOk(UnitType t, MapLocation c) {
        int pat = patternOf(t);
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = c.translate(dx, dy);
            if (!on(l)) return false;
            if (paint[k(l)] != (bit(pat, dx, dy) ? 2 : 1)) return false;
        }
        return true;
    }

    MapInfo[] infos(MapLocation c, int r2) {
        List<MapInfo> out = new ArrayList<>();
        for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) {
            MapLocation l = new MapLocation(x, y);
            if (c.distanceSquaredTo(l) <= r2 && sense(l)) out.add(info(l));
        }
        return out.toArray(new MapInfo[0]);
    }

    RobotController rc() {
        return (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
                new Class<?>[]{RobotController.class}, (proxy, m, a) -> call(m.getName(), a));
    }

    Object call(String n, Object[] a) throws GameActionException {
        switch (n) {
            case "getRoundNum": return round;
            case "getMapWidth": return W;
            case "getMapHeight": return H;
            case "getID": return id;
            case "getTeam": return team;
            case "getType": return type;
            case "getLocation": return me;
            case "getHealth": return health;
            case "getPaint": return myPaint;
            case "getChips": case "getMoney": return chips;
            case "getNumberTowers": return towers;
            case "onTheMap": return on((MapLocation) a[0]);
            case "canSenseLocation": return sense((MapLocation) a[0]);
            case "isLocationOccupied": return robots.containsKey(a[0]) || me.equals(a[0]);
            case "canSenseRobotAtLocation": return sense((MapLocation) a[0]) && robots.containsKey(a[0]);
            case "senseRobotAtLocation": return robots.get(a[0]);
            case "sensePassability": return passable((MapLocation) a[0]);
            case "senseMapInfo": return info((MapLocation) a[0]);
            case "senseNearbyMapInfos":
                if (a == null || a.length == 0) return infos(me, 20);
                if (a.length == 1 && a[0] instanceof Integer) return infos(me, (Integer) a[0] < 0 ? 20 : (Integer) a[0]);
                if (a.length == 1) return infos((MapLocation) a[0], 20);
                return infos((MapLocation) a[0], (Integer) a[1] < 0 ? 20 : (Integer) a[1]);
            case "senseNearbyRuins": {
                int r2 = (Integer) a[0] < 0 ? 20 : (Integer) a[0];
                List<MapLocation> out = new ArrayList<>();
                for (int i = 0; i < W * H; i++) if (ruin[i]) {
                    MapLocation l = new MapLocation(i % W, i / W);
                    if (me.distanceSquaredTo(l) <= r2) out.add(l);
                }
                return out.toArray(new MapLocation[0]);
            }
            case "senseNearbyRobots": {
                int r2 = 20; Team t = null; MapLocation c = me;
                if (a != null && a.length == 1) r2 = (Integer) a[0];
                if (a != null && a.length == 2) { r2 = (Integer) a[0]; t = (Team) a[1]; }
                if (a != null && a.length == 3) { c = (MapLocation) a[0]; r2 = (Integer) a[1]; t = (Team) a[2]; }
                if (r2 < 0) r2 = 20;
                List<RobotInfo> out = new ArrayList<>();
                for (RobotInfo r : robots.values())
                    if (c.distanceSquaredTo(r.location) <= r2 && (t == null || r.team == t)) out.add(r);
                out.sort(Comparator.comparingInt(r -> r.ID));
                return out.toArray(new RobotInfo[0]);
            }
            case "getAllLocationsWithinRadiusSquared": {
                MapLocation c = (MapLocation) a[0]; int r2 = (Integer) a[1];
                List<MapLocation> out = new ArrayList<>();
                for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) {
                    MapLocation l = new MapLocation(x, y);
                    if (c.distanceSquaredTo(l) <= r2) out.add(l);
                }
                return out.toArray(new MapLocation[0]);
            }
            case "adjacentLocation": return me.add((Direction) a[0]);
            case "isActionReady": return actCd < 10;
            case "isMovementReady": return moveCd < 10;
            case "getActionCooldownTurns": return actCd;
            case "getMovementCooldownTurns": return moveCd;
            case "canMove": {
                Direction d = (Direction) a[0];
                MapLocation t = me.add(d);
                return moveCd < 10 && passable(t) && !robots.containsKey(t);
            }
            case "move": {
                Direction d = (Direction) a[0];
                MapLocation t = me.add(d);
                if (!(moveCd < 10 && passable(t) && !robots.containsKey(t))) throw new GameActionException(GameActionExceptionType.CANT_MOVE_THERE, "fake: cannot move " + d);
                me = t; moveCd += 10; log.add("move " + d);
                return null;
            }
            case "canPaint": {
                MapLocation l = (MapLocation) a[0];
                return on(l) && passable(l) && paint[k(l)] < 3;
            }
            case "canAttack": {
                MapLocation l = (MapLocation) a[0];
                if (actCd >= 10 || l == null || !on(l)) return false;
                return me.distanceSquaredTo(l) <= type.actionRadiusSquared && myPaint >= Math.max(1, type.attackCost);
            }
            case "attack": {
                MapLocation l = (MapLocation) a[0];
                boolean sec = a.length > 1 && (Boolean) a[1];
                if (actCd >= 10 || me.distanceSquaredTo(l) > type.actionRadiusSquared) throw new GameActionException(GameActionExceptionType.CANT_DO_THAT, "fake: attack");
                actCd += type.actionCooldown; myPaint -= type.attackCost;
                int p = sec ? 2 : 1;
                if (type == UnitType.SOLDIER) {
                    if (passable(l) && paint[k(l)] < 3) { paint[k(l)] = p; painted.add(l); }
                } else if (type == UnitType.SPLASHER) {
                    splashed.add(l);
                    for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
                        MapLocation t = l.translate(dx, dy);
                        if (!on(t) || l.distanceSquaredTo(t) > 4 || !passable(t)) continue;
                        if (paint[k(t)] < 3 || l.distanceSquaredTo(t) <= 2) paint[k(t)] = p;
                    }
                } else if (type == UnitType.MOPPER) {
                    if (paint[k(l)] >= 3) paint[k(l)] = 0;
                    log.add("mop " + l);
                }
                return null;
            }
            case "canMopSwing": return type == UnitType.MOPPER && actCd < 10;
            case "mopSwing": actCd += 20; log.add("swing " + a[0]); return null;
            case "canMarkTowerPattern": {
                MapLocation c = (MapLocation) a[1];
                return me.distanceSquaredTo(c) <= 2 && ruin[k(c)] && myPaint >= 25 && c.x >= 2 && c.y >= 2 && c.x < W - 2 && c.y < H - 2;
            }
            case "markTowerPattern": {
                UnitType t = (UnitType) a[0]; MapLocation c = (MapLocation) a[1];
                int pat = patternOf(t);
                for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
                    if (dx == 0 && dy == 0) continue;
                    mark[k(c.translate(dx, dy))] = bit(pat, dx, dy) ? 2 : 1;
                }
                myPaint -= 25; log.add("markTower " + t + " " + c);
                return null;
            }
            case "canCompleteTowerPattern": {
                UnitType t = (UnitType) a[0]; MapLocation c = (MapLocation) a[1];
                return me.distanceSquaredTo(c) <= 2 && ruin[k(c)] && !robots.containsKey(c) && chips >= 1000 && towerPatternOk(t, c);
            }
            case "completeTowerPattern": {
                UnitType t = (UnitType) a[0]; MapLocation c = (MapLocation) a[1];
                chips -= 1000; towers++; completed.add(t.getBaseType());
                put(90000 + completed.size(), team, t.getBaseType(), c.x, c.y, 500);
                return null;
            }
            case "canTransferPaint": {
                MapLocation l = (MapLocation) a[0]; int amt = (Integer) a[1];
                RobotInfo r = robots.get(l);
                return actCd < 10 && r != null && r.team == team && me.distanceSquaredTo(l) <= 2 && amt != 0
                        && (amt > 0 ? type == UnitType.MOPPER && amt <= myPaint : r.type.isTowerType() && -amt <= r.paintAmount);
            }
            case "transferPaint": {
                MapLocation l = (MapLocation) a[0]; int amt = (Integer) a[1];
                RobotInfo r = robots.get(l);
                myPaint -= amt; actCd += 10;
                robots.put(l, new RobotInfo(r.ID, r.team, r.type, r.health, r.location, r.paintAmount + amt));
                log.add("transfer " + amt);
                return null;
            }
            case "canBuildRobot": {
                UnitType t = (UnitType) a[0]; MapLocation l = (MapLocation) a[1];
                return actCd < 10 && me.distanceSquaredTo(l) <= 4 && passable(l) && !robots.containsKey(l) && !l.equals(me)
                        && chips >= t.moneyCost && myPaint >= t.paintCost;
            }
            case "buildRobot": {
                UnitType t = (UnitType) a[0]; MapLocation l = (MapLocation) a[1];
                chips -= t.moneyCost; myPaint -= t.paintCost; actCd += 10;
                put(20000 + builtUnits.size(), team, t, l.x, l.y, t.paintCapacity);
                builtUnits.add(t + "@" + l);
                return null;
            }
            case "canUpgradeTower": return false;
            case "canSendMessage": case "canBroadcastMessage": return false;
            case "readMessages": return new Message[0];
            case "setIndicatorString": case "setIndicatorDot": case "setIndicatorLine": case "setTimelineMarker": return null;
            case "canMark": return false;
            case "getResourcePattern": case "getTowerPattern":
            default: throw new UnsupportedOperationException("fake RobotController: " + n);
        }
    }

    /** The fake bytecode clock: Clock.getBytecodesLeft() reads RobotMonitor's private static bytecodesLeft (0
     *  outside the engine), so tests set it. Nothing spends it. */
    static void clock(int left) {
        try {
            Class<?> c = Class.forName("battlecode.instrumenter.inject.RobotMonitor");
            java.lang.reflect.Field f = c.getDeclaredField("bytecodesLeft"); f.setAccessible(true); f.setInt(null, left);
            f = c.getDeclaredField("bytecodeLimit"); f.setAccessible(true); f.setInt(null, 1 << 30);
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }
}

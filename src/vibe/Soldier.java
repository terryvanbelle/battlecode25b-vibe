package vibe;

import battlecode.common.*;

/** Soldiers: build towers on ruins (signal the type with free marks, paint the 24 pattern tiles, complete), otherwise paint and explore;
 *  attack enemy towers in range. */
public strictfp class Soldier {
    static MapLocation ruin;
    static UnitType ruinType;
    static int ruinSince, ruinBlocked;
    static MapLocation[] badRuin = new MapLocation[16];
    static int[] badUntil = new int[16];
    static int nBad;

    /** A soldier's turn: the steps below in order; a step that returns true ends the turn. Each step's gate is
     *  written next to it. A gate marked "in:" is the first test inside the step's method and stays there: moving it
     *  here would change the bytecode count before the SRP's Clock reads (srpTurn, pickSrp, workSrp), and with it
     *  what those reads decide on some turns. Free actions, which never end the turn: scanEnemyTowers and the free
     *  shot here; Churn.rebuild and Unit.topUp in RobotPlayer after the list. */
    static void turn() throws GameActionException {
        RobotController rc = G.rc;
        Unit.scanEnemyTowers();                                  // free: remember the nearest enemy tower
        // free shot: the remembered enemy tower in attack range (r2 <= 9), before ruin painting can use the action
        if (Unit.enemyTower != null && rc.isActionReady() && G.paint >= Tune.SOL_SHOT_PAINT && rc.canAttack(Unit.enemyTower)
                && G.here.distanceSquaredTo(Unit.enemyTower) <= 9) {
            rc.attack(Unit.enemyTower);
            G.paint = rc.getPaint();
        }
        // 1. take a ruin: none held, and not mid-SRP with SRP_TOWERS+ towers (t36: finish the SRP first);
        //    in: fewer than 25 towers. Skips contested and bad ruins, at most 2 soldiers per ruin.
        if (ruin == null && !(srp != null && rc.getNumberTowers() >= Tune.SRP_TOWERS)) pickRuin();
        // 2. work it (free marks, paint, complete); false = dropped, go on
        if (ruin != null && workRuin()) return;
        // 3. deny (study 6 2.2); in: paint >= SOL_DENY_PAINT. True only when it painted.
        if (deny()) return;
        // 4. siege; in: a remembered enemy tower within d2 SOL_SIEGE_R2 and paint >= SOL_SIEGE_PAINT. True whenever
        //    it applies, even on a turn it could not attack.
        if (siege()) return;
        // 5. SRP; in: one in progress, else start one (round >= SRP_ROUND, chips >= SRP_CHIPS, paint >= SRP_PAINT,
        //    SRP_START_BC bytecodes left)
        if (srpTurn()) return;
        // 6. refill; in: paint < SOL_REFILL or a refill walk under way. Then paint the tile underfoot (in: action
        //    ready, paint >= SOL_PAINT_HERE).
        if (Unit.refill(Tune.SOL_REFILL)) { paintHere(); return; }
        // 7. explore, painting as we go (in: action ready, paint >= SOL_PAINT_NEAR); study 3 tactic 2: before round
        //    SOL_SAVE_PAINT_UNTIL save paint for tower patterns (no coverage)
        if (G.round >= Tune.SOL_SAVE_PAINT_UNTIL) paintNear();
        Nav.moveTo(Unit.exploreTarget());
        if (G.round >= Tune.SOL_SAVE_PAINT_UNTIL) paintNear();
    }

    // ---- siege: a soldier with no ruin to build and paint to spare kites a known enemy tower nearby: step into
    // range (r2 <= 9), hit it, step back out. True whenever it applies, even on a turn it could not attack.
    static boolean siege() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation t = Unit.enemyTower;
        if (t == null || G.paint < Tune.SOL_SIEGE_PAINT || G.here.distanceSquaredTo(t) > Tune.SOL_SIEGE_R2) return false;
        if (rc.isActionReady()) {
            if (G.here.distanceSquaredTo(t) > 9) Nav.moveTo(t);
            G.here = rc.getLocation();
            if (rc.canAttack(t)) { rc.attack(t); G.paint = rc.getPaint(); }
        }
        // study 14 2.1b: step out for real (the old three-direction step from r2 4-5 often stayed in range)
        if (!rc.isActionReady() && rc.isMovementReady()) stepOut(t);
        G.ind += " siege" + t;
        return true;
    }


    // study 14 2.1b: 8% of our hits were followed by a step that stayed in range (theirs 1%). Leave the tower's reach
    // (r2 9; 16 for a defense tower): of the 8 moves, one that ends beyond it, own paint first and then the largest
    // r2; if none does, the move with the largest r2, when that gains distance.
    static void stepOut(MapLocation t) throws GameActionException {
        RobotController rc = G.rc;
        int reach = 9;
        if (rc.canSenseLocation(t)) {
            RobotInfo r = rc.senseRobotAtLocation(t);
            if (r != null && r.team != G.me && r.type.isTowerType()) reach = r.type.actionRadiusSquared;
        }
        int cur = G.here.distanceSquaredTo(t);
        if (cur > reach) return;
        Direction best = null; int bestS = cur;
        for (Direction d : G.DIRS) {
            if (!rc.canMove(d)) continue;
            MapLocation n = G.here.add(d);
            int r2 = n.distanceSquaredTo(t);
            int s = r2 > reach ? 1000 + (rc.senseMapInfo(n).getPaint().isAlly() ? 100 : 0) + r2 : r2;
            if (s > bestS) { bestS = s; best = d; }
        }
        if (best == null) return;
        rc.move(best);
        G.here = rc.getLocation();
    }

    // study 6 2.2: they paint into 48 of our 188 ruins (we finish 15% of those) and we did it to 6 of their 159.
    // A soldier with no ruin to work and 40+ paint paints one empty tile a turn of the nearest visible ruin the
    // enemy is building (enemy paint in its 5x5, no tower yet) that shows fewer than 2 of our tiles; their pattern
    // can't complete until they mop it.
    static boolean deny() throws GameActionException {
        RobotController rc = G.rc;
        if (G.paint < Tune.SOL_DENY_PAINT) return false;
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapLocation r : G.ruins) {
            if (rc.senseRobotAtLocation(r) != null || !Pattern.contested(r)) continue;
            int ours = 0;
            for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
                MapLocation l = r.translate(dx, dy);
                if (rc.canSenseLocation(l) && rc.senseMapInfo(l).getPaint().isAlly()) ours++;
            }
            if (ours >= Tune.SOL_DENY_OURS) continue;
            int d = G.here.distanceSquaredTo(r);
            if (d < bestD) { bestD = d; best = r; }
        }
        if (best == null) return false;
        if (rc.isActionReady()) {
            for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
                MapLocation l = best.translate(dx, dy);
                if ((dx != 0 || dy != 0) && rc.canSenseLocation(l) && rc.canAttack(l) && rc.senseMapInfo(l).getPaint() == PaintType.EMPTY) {
                    rc.attack(l); G.paint = rc.getPaint(); G.ind += " deny" + best; return true;
                }
            }
        }
        return false;   // t84: deny only from where we stand (t80 also walked to the ruin and lost 39)
    }

    static boolean isBad(MapLocation r) {
        for (int i = nBad; --i >= 0; ) if (badRuin[i].equals(r) && G.round < badUntil[i]) return true;
        return false;
    }

    static void markBad(MapLocation r, int rounds) {
        for (int i = nBad; --i >= 0; ) if (badRuin[i].equals(r)) { badUntil[i] = G.round + rounds; return; }
        if (nBad < badRuin.length) { badRuin[nBad] = r; badUntil[nBad++] = G.round + rounds; }
        else { badRuin[G.rand(badRuin.length)] = r; }
    }

    static void pickRuin() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.getNumberTowers() >= GameConstants.MAX_NUMBER_OF_TOWERS) return;
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapLocation r : G.ruins) {
            if (rc.senseRobotAtLocation(r) != null) continue;       // a tower stands there
            if (isBad(r)) continue;
            if (Pattern.contested(r)) { markBad(r, Tune.SOL_CONTESTED_BAD); continue; }   // study 4 2.2: we finish 2 of 58 contested ruins
            // two soldiers per ruin at most
            int helpers = 0;
            for (RobotInfo a : G.allies) if (a.type == UnitType.SOLDIER && a.location.distanceSquaredTo(r) <= Tune.SOL_HELPER_R2) helpers++;
            if (rc.getNumberTowers() == Tune.SOL_PAIR_TOWERS) {   // study 8 2.2 (b): no second painter on our first tower in 35 of 89 games
                if (helpers >= 2 || (helpers == 1 && G.here.distanceSquaredTo(r) > Tune.SOL_PAIR_JOIN_R2)) continue;
            } else if (helpers >= 1 && G.here.distanceSquaredTo(r) > 2) continue;
            int d = G.here.distanceSquaredTo(r);
            if (d < bestD) { bestD = d; best = r; }
        }
        if (best != null) { ruin = best; ruinType = null; ruinSince = G.round; ruinBlocked = 0; }
    }

    /** Tower type for a new ruin; the first rule that fires wins:
     *  1. every tower known and none paints: paint;  2. every tower known and none money: money;
     *  3. from 3 towers with 1500+ chips: paint (t63, y170);  4. below 6 towers: money (y155);
     *  5. one paint tower per 4 towers beyond 6: paint;  6. below 8 towers: money;
     *  7. 3000+ idle chips: paint - unreachable, rule 3 already fired;  8. paint while paint towers < 1/5 of towers. */
    static UnitType wantType() {
        // study 4 2.4: money first (their builds 1-8 are nearly all money, one paint tower past r100), now that
        // patterns no longer wait for chips (2.1) and contested ruins are skipped (2.2)
        int n = G.rc.getNumberTowers();
        int pt = 0, mt = 0;
        for (int i = G.nTowers; --i >= 0; ) { if (Towers.kind[i] == Towers.PAINT) pt++; else if (Towers.kind[i] == Towers.MONEY) mt++; }
        if (pt + mt >= n && pt == 0) return UnitType.LEVEL_ONE_PAINT_TOWER;   // every tower known and none paints
        // study 4 3.1: with 0 money towers we sat at 10 chips for 158 rounds; rebuild money first
        if (pt + mt >= n && mt == 0 && n > 0) return UnitType.LEVEL_ONE_MONEY_TOWER;
        // study 5 2.1 (y155: money for towers 1-6), but from 3 towers 1500+ chips make it paint first (t63, y170)
        if (n >= Tune.WANT_PAINT_CHIPS_TOWERS && G.rc.getChips() >= Tune.WANT_PAINT_CHIPS) return UnitType.LEVEL_ONE_PAINT_TOWER;
        if (n < Tune.WANT_MONEY_UNTIL) return UnitType.LEVEL_ONE_MONEY_TOWER;
        if (pt < 1 + (n - Tune.WANT_MONEY_UNTIL) / Tune.WANT_PAINT_PER) return UnitType.LEVEL_ONE_PAINT_TOWER;
        if (n < Tune.WANT_MONEY_UNTIL_LATE) return UnitType.LEVEL_ONE_MONEY_TOWER;
        if (G.rc.getChips() >= Tune.IDLE_CHIPS) return UnitType.LEVEL_ONE_PAINT_TOWER;   // unreachable (rule 3)
        return pt * Tune.WANT_PAINT_SHARE < n ? UnitType.LEVEL_ONE_PAINT_TOWER : UnitType.LEVEL_ONE_MONEY_TOWER;
    }

    /** Pattern.bit, kept for test/vibe/BotTest (testPatternBits); the bot itself calls Pattern.bit. */
    static boolean bit(int pattern, int dx, int dy) { return Pattern.bit(pattern, dx, dy); }

    // study 11 2.1: the paint and money patterns differ on all 16 outer-ring tiles of the 5x5, so one ring mark spells
    // the type (Pattern.readMarks decodes partial marks); rc.mark is free, has no cooldown and reaches r2 2
    static void freeMarks(MapLocation r, UnitType t) throws GameActionException {
        RobotController rc = G.rc;
        int pat = Pattern.of(t);
        MapLocation me = rc.getLocation();
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx != -2 && dx != 2 && dy != -2 && dy != 2) continue;
            MapLocation l = r.translate(dx, dy);
            if (me.distanceSquaredTo(l) > 2 || !rc.canMark(l)) continue;
            if (rc.senseMapInfo(l).getMark() == PaintType.EMPTY) rc.mark(l, Pattern.bit(pat, dx, dy));
        }
    }

    // study 8 2.2 (a): our first tower is built at a median r25 against their r19; we start painting 3 rounds after
    // first sight (they 1) because we walked up and marked first (before study 11's free marks). On the way in, paint
    // the nearest wrong tile of the pattern we are about to take (wantType).
    static void prePaint(MapLocation r) throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || G.paint < 5) return;
        int pat = Pattern.of(wantType());
        MapLocation best = null; boolean bs = false; int bd = Integer.MAX_VALUE;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = r.translate(dx, dy);
            int dd = G.here.distanceSquaredTo(l);
            if (dd > 9 || dd >= bd || !rc.canSenseLocation(l)) continue;
            PaintType p = rc.senseMapInfo(l).getPaint();
            boolean s = Pattern.bit(pat, dx, dy);
            if (p.isEnemy() || (p != PaintType.EMPTY && p.isSecondary() == s)) continue;
            bd = dd; best = l; bs = s;
        }
        if (best != null && rc.canPaint(best)) { rc.attack(best, bs); G.paint = rc.getPaint(); G.ind += " prepaint"; }
    }

    /** Work the current ruin; false when it was dropped (the turn continues with other work). */
    static boolean workRuin() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation r = ruin;
        if (rc.canSenseLocation(r) && rc.senseRobotAtLocation(r) != null) { ruin = null; return false; }
        if (G.round - ruinSince > Tune.SOL_RUIN_GIVE_UP) { markBad(r, Tune.SOL_RUIN_GIVE_UP_BAD); ruin = null; return false; }
        if (G.paint < Tune.SOL_RUIN_REFILL && !rc.canCompleteTowerPattern(ruinType == null ? wantType() : ruinType, r)) {
            // out of paint mid-pattern: refill and come back
            Unit.refill(10000);
            return true;
        }
        if (ruinType == null) ruinType = Pattern.readMarks(r);
        int d = G.here.distanceSquaredTo(r);
        if (ruinType == null) {
            if (d > 2) { Nav.moveTo(r); d = G.here.distanceSquaredTo(r); }
            if (d > 2 && rc.getNumberTowers() <= Tune.SOL_PREPAINT_TOWERS) prePaint(r);   // study 8 2.2 (a)
            if (d <= 2) {
                // study 11 2.1: from beside the ruin the whole 5x5 is in sight: read the marks again, else take our own
                // type and signal it with free single marks (rc.mark costs no paint; markTowerPattern cost 25)
                ruinType = Pattern.readMarks(r);
                if (ruinType == null && rc.onTheMap(r.translate(-2, -2)) && rc.onTheMap(r.translate(2, 2))) ruinType = wantType();
            }
            if (ruinType == null) return true;
        }
        freeMarks(r, ruinType);   // study 11 2.1: every turn, mark the outer-ring tiles in reach so helpers read the type
        int pat = Pattern.of(ruinType);
        // paint the nearest wrong tile in range; find the nearest wrong tile overall to walk toward
        MapLocation paintL = null; boolean paintS = false; int paintD = Integer.MAX_VALUE;
        MapLocation walkL = null; int walkD = Integer.MAX_VALUE;
        int enemyTiles = 0, wrong = 0;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            if (dx == 0 && dy == 0) continue;
            MapLocation l = r.translate(dx, dy);
            if (!rc.canSenseLocation(l)) { wrong++; continue; }
            PaintType p = rc.senseMapInfo(l).getPaint();
            boolean s = Pattern.bit(pat, dx, dy);
            if (p.isEnemy()) { enemyTiles++; continue; }
            if (p != PaintType.EMPTY && p.isSecondary() == s) continue;
            wrong++;
            int dd = G.here.distanceSquaredTo(l);
            if (dd <= 9 && dd < paintD) { paintD = dd; paintL = l; paintS = s; }
            if (dd < walkD) { walkD = dd; walkL = l; }
        }
        if (paintL != null && rc.isActionReady() && rc.canPaint(paintL) && G.paint >= 5) {
            rc.attack(paintL, paintS);
            G.paint = rc.getPaint();
            wrong--;
        }
        if (rc.canCompleteTowerPattern(ruinType, r)) {
            rc.completeTowerPattern(ruinType, r);
            Towers.note(r, Towers.kindOf(ruinType));
            ruin = null;
            return true;
        }
        if (enemyTiles > 0) {
            // study 9 2.1b: no blocked attempt completes without an own mopper or splasher in view: alone, give up after 5
            boolean cleaner = false;
            for (RobotInfo a : G.allies) if (a.type == UnitType.MOPPER || a.type == UnitType.SPLASHER) { cleaner = true; break; }
            if (++ruinBlocked > (cleaner ? Tune.SOL_BLOCKED_CLEANER : Tune.SOL_BLOCKED_ALONE)) { markBad(r, cleaner ? Tune.SOL_BLOCKED_CLEANER_BAD : Tune.SOL_BLOCKED_ALONE_BAD); ruin = null; return false; }
        }
        // move: toward the nearest wrong tile, else stay adjacent to complete when the chips arrive
        if (wrong > 0 && walkL != null) {
            if (G.here.distanceSquaredTo(walkL) > 2) Nav.moveTo(walkL);
            else if (paintL == null) Nav.moveTo(r);
        } else if (d > 2) Nav.moveTo(r);
        else if (rc.isActionReady()) paintNear();
        G.ind += " ruin" + r + " " + ruinType + " w" + wrong + " e" + enemyTiles;
        if (rc.canCompleteTowerPattern(ruinType, r)) {
            rc.completeTowerPattern(ruinType, r);
            Towers.note(r, Towers.kindOf(ruinType));
            ruin = null;
        }
        return true;
    }

    // ---- t36: late special resource patterns (study 4 2.6, study 3 tactic 7). Centres on the lattice x = y = 2
    // (mod 4); RESOURCE_PATTERN repeats with period 4 (its outer rows and columns agree), so neighbouring lattice SRPs
    // share their edge tiles consistently. Started only from r100 with 1000+ chips, 60+ paint and 6000+ bytecodes
    // left by a soldier with no ruin to work (or, with 6+ towers, kept over a new ruin). The 5x5 must hold no walls,
    // no enemy paint, and no ruin; and must not overlap an unbuilt ruin's 5x5 (a ruin within Chebyshev 4 must carry
    // our tower). Centres 3-4 tiles from one of our towers are preferred.
    static MapLocation srp;
    static int srpSince, srps;
    static int[] srpSkip;          // per lattice centre: skip it until this round (Integer.MAX_VALUE = done or never)
    static int srpLW;

    static int srpIdx(MapLocation c) { return (c.x >> 2) + (c.y >> 2) * srpLW; }

    static void srpSkipFor(MapLocation c, int rounds) {
        srpSkip[srpIdx(c)] = rounds == Integer.MAX_VALUE ? rounds : G.round + rounds;
    }

    static boolean srpTurn() throws GameActionException {
        if (srp == null) {
            if (G.round < Tune.SRP_ROUND || G.chips < Tune.SRP_CHIPS || G.paint < Tune.SRP_PAINT || Clock.getBytecodesLeft() < Tune.SRP_START_BC) return false;
            pickSrp();
            if (srp == null) return false;
        }
        return workSrp();
    }

    /** Choose the best lattice centre within d2 50: valid by the map memory, scored by distance, our tower 3-4
     *  tiles away, and tiles already right. */
    static void pickSrp() throws GameActionException {
        RobotController rc = G.rc;
        if (srpSkip == null) { srpLW = G.W / 4 + 1; srpSkip = new int[srpLW * (G.H / 4 + 1)]; }
        int W = G.W, H = G.H, hx = G.here.x, hy = G.here.y;
        int[] m = G.mem;
        int x0 = hx - Tune.SRP_SEARCH + ((2 - (hx - Tune.SRP_SEARCH)) & 3), y0 = hy - Tune.SRP_SEARCH + ((2 - (hy - Tune.SRP_SEARCH)) & 3);
        MapLocation best = null; int bestS = Integer.MAX_VALUE;
        for (int cx = x0; cx <= hx + Tune.SRP_SEARCH; cx += 4) {
            if (cx < 2 || cx > W - 3) continue;
            for (int cy = y0; cy <= hy + Tune.SRP_SEARCH; cy += 4) {
                if (cy < 2 || cy > H - 3) continue;
                if (Clock.getBytecodesLeft() < Tune.SRP_PICK_BC) break;
                MapLocation c = new MapLocation(cx, cy);
                int d = G.here.distanceSquaredTo(c);
                if (d > Tune.SRP_PICK_R2) continue;
                int k = srpIdx(c);
                if (srpSkip[k] > G.round) continue;
                // ruins: none in the 5x5, and any within Chebyshev 4 must be our tower
                int towerCheb = 99; boolean ok = true;
                for (int i = G.nRuins; --i >= 0; ) {
                    MapLocation r = G.ruinList[i];
                    int ax = Math.abs(r.x - cx), ay = Math.abs(r.y - cy);
                    int ch = ax > ay ? ax : ay;
                    if (ch <= 2) { ok = false; srpSkip[k] = Integer.MAX_VALUE; break; }
                    if (ch > Tune.SRP_TOWER_FAR) continue;
                    int kind = Towers.kindAt(r);
                    if (kind == 0) {
                        if (ch <= 4) { ok = false; srpSkip[k] = G.round + Tune.SRP_SKIP_RUIN; break; }
                        continue;
                    }
                    if (ch <= 4 && kind == Towers.MONEY && !Pattern.agreesWithMoney(cx, cy, r)) { ok = false; srpSkip[k] = G.round + Tune.SRP_SKIP_MONEY; break; }
                    if (ch < towerCheb) towerCheb = ch;
                }
                if (!ok) continue;
                if (rc.canSenseLocation(c) && rc.senseMapInfo(c).isResourcePatternCenter()) { srpSkip[k] = Integer.MAX_VALUE; continue; }
                int right = 0;
                for (int dx = -2; dx <= 2 && ok; dx++) for (int dy = -2; dy <= 2; dy++) {
                    int v = m[cx + dx + (cy + dy) * W];
                    if ((v & (G.WALL | G.RUIN)) != 0) { ok = false; srpSkip[k] = Integer.MAX_VALUE; break; }
                    int p = v >> 4;
                    if (p >= 3) { ok = false; srpSkip[k] = G.round + Tune.SRP_SKIP_ENEMY_MEM; break; }
                    if (p != 0 && (p == 2) == Pattern.srpSec(cx + dx, cy + dy)) right++;
                }
                if (!ok) continue;
                int sc = d - Tune.SRP_RIGHT_WEIGHT * right - (towerCheb <= 4 ? Tune.SRP_BONUS_NEAR : towerCheb <= Tune.SRP_TOWER_FAR ? Tune.SRP_BONUS_FAR : 0);
                if (sc < bestS) { bestS = sc; best = c; }
            }
        }
        if (best != null) { srp = best; srpSince = G.round; }
    }

    static MapLocation srpPaintL;
    static boolean srpPaintS;
    static int srpWrong;

    /** Scan the SRP's 25 tiles: count the wrong ones and pick the nearest wrong one we can paint now.
     *  False when the centre turned invalid (wall, ruin, enemy paint) and was dropped. */
    static boolean srpScan(MapLocation c) throws GameActionException {
        RobotController rc = G.rc;
        srpPaintL = null; srpWrong = 0;
        int paintD = Integer.MAX_VALUE;
        int pat = GameConstants.RESOURCE_PATTERN;
        for (int dx = -2; dx <= 2; dx++) for (int dy = -2; dy <= 2; dy++) {
            MapLocation l = c.translate(dx, dy);
            if (!rc.canSenseLocation(l)) { srpWrong++; continue; }
            MapInfo mi = rc.senseMapInfo(l);
            if (!mi.isPassable()) { srpSkipFor(c, Integer.MAX_VALUE); srp = null; return false; }
            PaintType p = mi.getPaint();
            if (p.isEnemy()) { srpSkipFor(c, Tune.SRP_SKIP_ENEMY); srp = null; return false; }
            boolean sec = Pattern.bit(pat, dx, dy);
            if (p != PaintType.EMPTY && p.isSecondary() == sec) continue;
            srpWrong++;
            int dd = G.here.distanceSquaredTo(l);
            if (dd <= 9 && dd < paintD) { paintD = dd; srpPaintL = l; srpPaintS = sec; }
        }
        return true;
    }

    static boolean srpPaint() throws GameActionException {
        RobotController rc = G.rc;
        if (srpPaintL != null && rc.isActionReady() && G.paint >= 5 && rc.canPaint(srpPaintL)) {
            rc.attack(srpPaintL, srpPaintS);
            G.paint = rc.getPaint();
            srpWrong--;
            return true;
        }
        return false;
    }

    static boolean srpComplete(MapLocation c) throws GameActionException {
        RobotController rc = G.rc;
        if (rc.canCompleteResourcePattern(c)) {
            rc.completeResourcePattern(c);
            G.chips = rc.getChips();
            srps++;
            srpSkipFor(c, Integer.MAX_VALUE);
            srp = null;
            G.ind += " SRPDONE" + c + "#" + srps;
            return true;
        }
        return false;
    }

    /** Stand on the centre (every tile of the 5x5 is then in paint range), paint wrong tiles, complete. False when
     *  the SRP was dropped (the turn goes on with other work). */
    static boolean workSrp() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation c = srp;
        if (G.round - srpSince > Tune.SRP_GIVE_UP) { srpSkipFor(c, Tune.SRP_SKIP_GIVE_UP); srp = null; return false; }
        if (rc.canSenseLocation(c) && rc.senseMapInfo(c).isResourcePatternCenter()) { srpSkipFor(c, Integer.MAX_VALUE); srp = null; return false; }
        // a newly seen ruin in or near the 5x5 (unbuilt, or an enemy tower) rules the centre out
        for (MapLocation r : G.ruins) {
            int ax = Math.abs(r.x - c.x), ay = Math.abs(r.y - c.y);
            int ch = ax > ay ? ax : ay;
            if (ch <= 2) { srpSkipFor(c, Integer.MAX_VALUE); srp = null; return false; }
            if (ch <= 4) {
                RobotInfo t = rc.senseRobotAtLocation(r);
                if (t == null || t.team != G.me) { srpSkipFor(c, Tune.SRP_SKIP_RUIN); srp = null; return false; }
            }
        }
        if (Unit.enemyTower != null && Unit.enemyTower.distanceSquaredTo(c) <= Tune.SRP_ENEMY_TOWER_R2) { srpSkipFor(c, Tune.SRP_SKIP_ENEMY_TOWER); srp = null; return false; }
        if (G.paint < Tune.SRP_REFILL && Unit.refill(10000)) { G.ind += " srp-refill"; return true; }
        if (Clock.getBytecodesLeft() < Tune.SRP_WORK_BC) return true;
        if (!srpScan(c)) return false;
        srpPaint();
        if (srpWrong == 0 && srpComplete(c)) return true;
        if (!G.here.equals(c)) {
            Nav.moveTo(c);
            G.here = rc.getLocation();
            if (rc.isActionReady() && Clock.getBytecodesLeft() > Tune.SRP_REPAINT_BC) {
                if (!srpScan(c)) return false;
                srpPaint();
            }
        }
        if (srpWrong == 0 && srpComplete(c)) return true;
        G.ind += " srp" + c + " w" + srpWrong;
        return true;
    }

    static void paintHere() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || G.paint < Tune.SOL_PAINT_HERE) return;
        MapInfo mi = rc.senseMapInfo(G.here);
        if (mi.getPaint() == PaintType.EMPTY && rc.canPaint(G.here)) { rc.attack(G.here, colourAt(G.here)); G.paint = rc.getPaint(); }
    }

    /** Paint one unpainted tile in range (the one under us first, then the nearest), keeping a reserve for ruins. */
    static void paintNear() throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isActionReady() || G.paint < Tune.SOL_PAINT_NEAR) return;
        MapInfo under = rc.senseMapInfo(G.here);
        if (under.getPaint() == PaintType.EMPTY && rc.canPaint(G.here)) { rc.attack(G.here, colourAt(G.here)); G.paint = rc.getPaint(); return; }
        MapLocation best = null; int bestD = Integer.MAX_VALUE;
        for (MapInfo mi : rc.senseNearbyMapInfos(G.here, 9)) {
            if (mi.getPaint() != PaintType.EMPTY || !mi.isPassable()) continue;
            int d = G.here.distanceSquaredTo(mi.getMapLocation());
            if (d < bestD) { bestD = d; best = mi.getMapLocation(); }
        }
        if (best != null && rc.canPaint(best)) { rc.attack(best, colourAt(best)); G.paint = rc.getPaint(); }
    }

    // study 14 2.5: our own primary paint blocks 59% of our drained money towers' patterns (theirs 24%), and 16 of the
    // money pattern's 24 tiles are secondary. A tile inside a known paint or money tower's 5x5 gets that pattern's colour.
    static boolean colourAt(MapLocation l) {
        for (int i = G.nTowers; --i >= 0; ) {
            MapLocation t = Towers.loc[i];
            int dx = l.x - t.x, dy = l.y - t.y;
            if (dx < -2 || dx > 2 || dy < -2 || dy > 2 || Towers.kind[i] == Towers.DEFENSE) continue;
            return Pattern.bit(Pattern.of(Towers.kind[i] == Towers.MONEY ? UnitType.LEVEL_ONE_MONEY_TOWER : UnitType.LEVEL_ONE_PAINT_TOWER), dx, dy);
        }
        return false;
    }
}

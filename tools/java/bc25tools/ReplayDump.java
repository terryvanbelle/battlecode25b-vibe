package bc25tools;

import battlecode.schema.*;
import com.google.flatbuffers.Table;
import com.google.flatbuffers.UnionStructs;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.*;
import java.util.*;
import java.util.zip.GZIPInputStream;

/**
 * Battlecode 2025 replay reader. A .bc25 file is a gzipped flatbuffer GameWrapper holding one or more games
 * ("matches" in the schema). Facts from engine 3.1.0 (build/src, battlecode/server/GameMaker.java):
 *  - Each Round event holds Turn records, one per robot turn, written at the robot's end of turn with its state
 *    (hp, paint, cooldowns, bytecodesUsed, x, y). Actions are buffered and attach to the NEXT Turn written, which is
 *    the actor's own record for everything a robot does in its turn.
 *  - Round aggregates per team (after all turns): money (chips), paint coverage (tiles), resource patterns (SRPs).
 *  - Messages are NOT recorded (addMessageAction is commented out in RobotControllerImpl). Markers are recorded as
 *    MarkAction/UnmarkAction. completeResourcePattern is recorded as TransferAction(id = packed loc, amount = 0).
 *  - Indicator strings only when the engine ran with show-indicators (local games; never on the replica).
 *  - Teams: 1 = A, 2 = B. Locations packed x + y*width.
 *
 * Usage: java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump MODE ...
 *   summary FILE...        one JSON line per game (exit 1 if a file does not parse; that file gets {"file","error"})
 *   tsv FILE OUTDIR        g<i>.meta.json, g<i>.rounds.tsv, g<i>.turns.tsv, g<i>.actions.tsv, g<i>.summary.json,
 *                          plus the summary lines on stdout
 *   board FILE GAME ROUND  ASCII board at the end of ROUND (paint a/A b/B, '#' wall, towers by letter, robots)
 *
 * Coverage: the engine wins a team at painted >= 70% of (area - walls); ruins/tower tiles are in the denominator but
 *   can never be painted. covA/covB are exact tile counts from the tracked paint grid; covMismatch counts rounds where
 *   they disagree with the replay's per-mille aggregate (must be 0).
 * rounds.tsv columns: round, covA, covB (painted tiles), moneyA, moneyB, srpA, srpB, solA, splA, mopA, ptA, mtA,
 *   dtA (alive soldiers/splashers/moppers/paint/money/defense towers of A), same for B, paintA, paintB (paint held
 *   by A's/B's robots+towers, from each unit's latest record), died.
 * turns.tsv: round, id, team, type, x, y, hp, paint, mcd, acd, bc, ind.
 * actions.tsv: round, id, team, type (the record's robot), action, a, b, c (see ACTION docs in the code).
 * Summary JSON keys: file, game, map, width, height, paintable, teamA, teamB, winner, winType, rounds, covA, covB,
 *   covPctA, covPctB, moneyA, moneyB, srpA, srpB, towersA, towersB, unitsA, unitsB, spawnedA/B {type: n},
 *   diedA/B {type: n}, towersBuiltA/B, towersLostA/B, exceptionsA/B, maxBcRobotA/B, maxBcTowerA/B,
 *   atLimitA/B (turns whose bytecodesUsed >= the type's limit: overrun candidates), r50A/B and r70A/B (first round
 *   coverage reached 50%/70% of paintable, or -1), dumpVersion.
 */
public class ReplayDump {
    static final int DUMP_VERSION = 2;
    static final String[] TYPE = {"NONE", "PAINT_TOWER", "MONEY_TOWER", "DEFENSE_TOWER", "SOLDIER", "SPLASHER", "MOPPER"};
    static final String[] WIN = {"RESIGNATION", "MAJORITY_PAINTED", "ALL_UNITS_DESTROYED", "AREA_PAINTED",
            "MORE_TOWERS", "MORE_MONEY", "MORE_STORED_PAINT", "MORE_ROBOTS", "COIN_FLIP"};
    static final int ROBOT_LIMIT = 17500, TOWER_LIMIT = 20000;

    public static void main(String[] a) throws Exception {
        if (a.length == 0) { System.err.println("usage: summary FILE... | tsv FILE OUTDIR | board FILE GAME ROUND"); System.exit(2); }
        switch (a[0]) {
            case "summary": {
                int bad = 0;
                for (int i = 1; i < a.length; i++) {
                    try { for (String s : new ReplayDump(a[i], null).run()) System.out.println(s); }
                    catch (Exception e) { bad++; System.out.println("{\"file\":" + q(a[i]) + ",\"error\":" + q(String.valueOf(e)) + "}"); }
                }
                System.exit(bad > 0 ? 1 : 0);
            }
            case "tsv": {
                Files.createDirectories(Paths.get(a[2]));
                for (String s : new ReplayDump(a[1], a[2]).run()) System.out.println(s);
                break;
            }
            case "board": {
                ReplayDump d = new ReplayDump(a[1], null);
                d.boardGame = Integer.parseInt(a[2]); d.boardRound = Integer.parseInt(a[3]);
                d.run();
                break;
            }
            default: System.err.println("unknown mode " + a[0]); System.exit(2);
        }
    }

    static ByteBuffer read(String file) throws IOException {
        try (InputStream in = new GZIPInputStream(new FileInputStream(file))) {
            ByteBuffer bb = ByteBuffer.wrap(in.readAllBytes());
            bb.order(ByteOrder.LITTLE_ENDIAN);
            return bb;
        }
    }

    final String file, outDir;
    int boardGame = -1, boardRound = -1;
    ReplayDump(String file, String outDir) { this.file = file; this.outDir = outDir; }

    // ---- per-game state ----
    static final class Bot {
        int id, team, type, x, y, hp, paint, level = 1; boolean alive = true;
        Bot(int id, int team, int type, int x, int y) { this.id = id; this.team = team; this.type = type; this.x = x; this.y = y; }
    }
    int game, w, h, paintable;          // area minus walls: the engine's coverage denominator (ruins count)
    int[] tiles = new int[3];           // painted tiles per team, from the tracked grid (exact: every paint change is logged)
    int[] perMille = new int[3];        // the replay's own coverage aggregate (painted*1000/paintable, rounded)
    int covMismatch;                    // rounds where the grid disagrees with the aggregate (a dumper bug if > 0)
    String mapName, teamA = "A", teamB = "B", pkgA = "", pkgB = "";
    boolean[] wall, ruin;
    byte[] paint;                       // 0 empty, 1/2 A primary/secondary, 3/4 B
    Map<Integer, Bot> bots;
    int[][] spawned, died, towersBuilt, towersLost;
    int[] exceptions, maxBcRobot, maxBcTower, atLimit, r50, r70, lastCov, lastMoney, lastSrp;
    PrintWriter rounds, turns, actions;
    List<String> out = new ArrayList<>();

    List<String> run() throws IOException {
        ByteBuffer bb = read(file);
        GameWrapper gw = GameWrapper.getRootAsGameWrapper(bb);
        game = -1;
        for (int e = 0; e < gw.eventsLength(); e++) {
            EventWrapper ew = gw.events(e);
            switch (ew.eType()) {
                case Event.GameHeader: {
                    GameHeader gh = (GameHeader) ew.e(new GameHeader());
                    for (int t = 0; t < gh.teamsLength(); t++) {
                        TeamData td = gh.teams(t);
                        if (td.teamId() == 1) { teamA = td.name(); pkgA = td.packageName(); }
                        else if (td.teamId() == 2) { teamB = td.name(); pkgB = td.packageName(); }
                    }
                    break;
                }
                case Event.MatchHeader: startGame((MatchHeader) ew.e(new MatchHeader())); break;
                case Event.Round: round((Round) ew.e(new Round())); break;
                case Event.MatchFooter: endGame((MatchFooter) ew.e(new MatchFooter())); break;
                default: break;
            }
        }
        return out;
    }

    void startGame(MatchHeader mh) throws IOException {
        game++;
        GameMap m = mh.map();
        mapName = m.name(); w = m.size().x(); h = m.size().y();
        wall = new boolean[w * h]; ruin = new boolean[w * h]; paint = new byte[w * h];
        for (int i = 0; i < m.wallsLength(); i++) wall[i] = m.walls(i);
        for (int i = 0; i < m.paintLength(); i++) paint[i] = m.paint(i);
        tiles = new int[3]; perMille = new int[3]; covMismatch = 0;
        for (int i = 0; i < w * h; i++) if (paint[i] > 0) tiles[paint[i] <= 2 ? 1 : 2]++;
        VecTable rv = m.ruins();
        List<int[]> ruins = new ArrayList<>();
        for (int i = 0; i < rv.xsLength(); i++) { ruin[rv.xs(i) + rv.ys(i) * w] = true; ruins.add(new int[]{rv.xs(i), rv.ys(i)}); }
        paintable = 0;
        for (int i = 0; i < w * h; i++) if (!wall[i]) paintable++;
        bots = new HashMap<>();
        spawned = new int[3][7]; died = new int[3][7]; towersBuilt = new int[3][4]; towersLost = new int[3][4];
        exceptions = new int[3]; maxBcRobot = new int[3]; maxBcTower = new int[3]; atLimit = new int[3];
        r50 = new int[]{-1, -1, -1}; r70 = new int[]{-1, -1, -1};
        lastCov = new int[3]; lastMoney = new int[3]; lastSrp = new int[3];
        StringBuilder bodies = new StringBuilder("[");
        InitialBodyTable ib = m.initialBodies();
        SpawnAction sa = new SpawnAction();
        for (int i = 0; i < ib.spawnActionsLength(); i++) {
            ib.spawnActions(sa, i);
            Bot b = new Bot(sa.id(), sa.team(), sa.robotType(), sa.x(), sa.y());
            b.level = 2;    // starting towers are level 2 (spec v3.0.0)
            bots.put(b.id, b);
            if (i > 0) bodies.append(',');
            bodies.append(String.format("{\"id\":%d,\"team\":%d,\"type\":\"%s\",\"x\":%d,\"y\":%d}", b.id, b.team, TYPE[b.type], b.x, b.y));
        }
        bodies.append(']');
        if (outDir != null) {
            String p = outDir + "/g" + game;
            StringBuilder sb = new StringBuilder();
            sb.append("{\"file\":").append(q(new File(file).getAbsolutePath())).append(",\"game\":").append(game)
              .append(",\"map\":").append(q(mapName)).append(",\"width\":").append(w).append(",\"height\":").append(h)
              .append(",\"symmetry\":").append(m.symmetry()).append(",\"seed\":").append(m.randomSeed())
              .append(",\"teamA\":").append(q(teamA)).append(",\"teamB\":").append(q(teamB))
              .append(",\"paintable\":").append(paintable).append(",\"maxRounds\":").append(mh.maxRounds())
              .append(",\"walls\":\"");
            for (int i = 0; i < w * h; i++) sb.append(wall[i] ? '1' : '0');
            sb.append("\",\"paint\":\"");
            for (int i = 0; i < w * h; i++) sb.append((char) ('0' + paint[i]));
            sb.append("\",\"ruins\":[");
            for (int i = 0; i < ruins.size(); i++) sb.append(i > 0 ? "," : "").append("[").append(ruins.get(i)[0]).append(",").append(ruins.get(i)[1]).append("]");
            sb.append("],\"patterns\":[");
            for (int i = 0; i < m.paintPatternsLength(); i++) sb.append(i > 0 ? "," : "").append(m.paintPatterns(i));
            sb.append("],\"bodies\":").append(bodies).append(",\"dumpVersion\":").append(DUMP_VERSION).append("}");
            Files.writeString(Paths.get(p + ".meta.json"), sb + "\n");
            rounds = new PrintWriter(new BufferedWriter(new FileWriter(p + ".rounds.tsv")));
            turns = new PrintWriter(new BufferedWriter(new FileWriter(p + ".turns.tsv")));
            actions = new PrintWriter(new BufferedWriter(new FileWriter(p + ".actions.tsv")));
            rounds.println("round\tcovA\tcovB\tmoneyA\tmoneyB\tsrpA\tsrpB\tsolA\tsplA\tmopA\tptA\tmtA\tdtA\tsolB\tsplB\tmopB\tptB\tmtB\tdtB\tpaintA\tpaintB\tdied");
            turns.println("round\tid\tteam\ttype\tx\ty\thp\tpaint\tmcd\tacd\tbc\tind");
            actions.println("round\tid\tteam\ttype\taction\ta\tb\tc");
        }
    }

    static boolean isTower(int type) { return type >= 1 && type <= 3; }

    String loc(int packed) { return (packed % w) + "," + (packed / w); }

    void act(int round, Bot b, String kind, Object x, Object y, Object z) {
        if (actions != null)
            actions.println(round + "\t" + b.id + "\t" + b.team + "\t" + TYPE[b.type] + "\t" + kind + "\t" + x + "\t" + y + "\t" + z);
    }

    void round(Round r) {
        int rn = r.roundId();
        Turn t = new Turn();
        for (int i = 0; i < r.turnsLength(); i++) {
            r.turns(t, i);
            Bot b = bots.get(t.robotId());
            if (b == null) { b = new Bot(t.robotId(), 0, 0, t.x(), t.y()); bots.put(b.id, b); }
            b.x = t.x(); b.y = t.y(); b.hp = t.health(); b.paint = t.paint();
            int bc = t.bytecodesUsed();
            if (b.team > 0) {
                if (isTower(b.type)) { maxBcTower[b.team] = Math.max(maxBcTower[b.team], bc); if (bc >= TOWER_LIMIT) atLimit[b.team]++; }
                else { maxBcRobot[b.team] = Math.max(maxBcRobot[b.team], bc); if (bc >= ROBOT_LIMIT) atLimit[b.team]++; }
            }
            String ind = "";
            int n = t.actionsLength();
            ByteBuffer bb = n > 0 ? UnionStructs.bb(t) : null;
            for (int j = 0; j < n; j++) {
                byte at = t.actionsType(j);
                int pos = UnionStructs.pos(t, 22, j);
                switch (at) {
                    case Action.DamageAction: { DamageAction d = new DamageAction(); d.__assign(pos, bb);
                        act(rn, b, "damage", d.id(), d.damage(), ""); break; }
                    case Action.PaintAction: { PaintAction d = new PaintAction(); d.__assign(pos, bb);
                        int pv = b.team == 1 ? (d.isSecondary() != 0 ? 2 : 1) : (d.isSecondary() != 0 ? 4 : 3);
                        setPaint(d.loc(), pv);
                        act(rn, b, "paint", loc(d.loc()), d.isSecondary(), ""); break; }
                    case Action.UnpaintAction: { UnpaintAction d = new UnpaintAction(); d.__assign(pos, bb);
                        setPaint(d.loc(), 0);
                        act(rn, b, "unpaint", loc(d.loc()), "", ""); break; }
                    case Action.MarkAction: { MarkAction d = new MarkAction(); d.__assign(pos, bb);
                        act(rn, b, "mark", loc(d.loc()), d.isSecondary(), ""); break; }
                    case Action.UnmarkAction: { UnmarkAction d = new UnmarkAction(); d.__assign(pos, bb);
                        act(rn, b, "unmark", loc(d.loc()), "", ""); break; }
                    case Action.AttackAction: { AttackAction d = new AttackAction(); d.__assign(pos, bb);
                        act(rn, b, "attack", d.id(), "", ""); break; }
                    case Action.SplashAction: { SplashAction d = new SplashAction(); d.__assign(pos, bb);
                        act(rn, b, "splash", loc(d.loc()), "", ""); break; }
                    case Action.MopAction: { MopAction d = new MopAction(); d.__assign(pos, bb);
                        act(rn, b, "mop", d.id0(), d.id1(), d.id2()); break; }
                    case Action.BuildAction: { BuildAction d = new BuildAction(); d.__assign(pos, bb);
                        Bot tw = bots.get(d.id());
                        if (tw != null && tw.team > 0 && isTower(tw.type)) towersBuilt[tw.team][tw.type]++;
                        act(rn, b, "build", d.id(), tw == null ? "" : TYPE[tw.type], ""); break; }
                    case Action.TransferAction: { TransferAction d = new TransferAction(); d.__assign(pos, bb);
                        if (d.amount() == 0) act(rn, b, "srp", loc(d.id()), "", "");
                        else act(rn, b, "transfer", d.id(), d.amount(), ""); break; }
                    case Action.MessageAction: { MessageAction d = new MessageAction(); d.__assign(pos, bb);
                        act(rn, b, "message", d.id(), d.data(), ""); break; }
                    case Action.SpawnAction: { SpawnAction d = new SpawnAction(); d.__assign(pos, bb);
                        Bot nb = new Bot(d.id(), d.team(), d.robotType(), d.x(), d.y());
                        Bot old = bots.get(d.id());
                        if (old != null && old.team == 0) { old.team = nb.team; old.type = nb.type; }
                        else bots.put(nb.id, nb);
                        if (nb.team > 0) spawned[nb.team][nb.type]++;
                        act(rn, b, "spawn", d.id(), TYPE[d.robotType()], d.x() + "," + d.y()); break; }
                    case Action.DieAction: { DieAction d = new DieAction(); d.__assign(pos, bb);
                        Bot v = bots.get(d.id());
                        if (v != null && v.alive) {
                            v.alive = false;
                            if (v.team > 0) { died[v.team][v.type]++; if (isTower(v.type)) towersLost[v.team][v.type]++;
                                if (d.dieType() == DieType.EXCEPTION) exceptions[v.team]++; }
                        }
                        act(rn, b, "die", d.id(), d.dieType() == DieType.EXCEPTION ? "EXCEPTION" : "", v == null ? "" : TYPE[v.type]); break; }
                    case Action.UpgradeAction: { UpgradeAction d = new UpgradeAction(); d.__assign(pos, bb);
                        Bot tw = bots.get(d.id()); if (tw != null) tw.level++;
                        act(rn, b, "upgrade", d.id(), tw == null ? "" : tw.level, d.newMaxHealth()); break; }
                    case Action.IndicatorStringAction: {
                        IndicatorStringAction d = new IndicatorStringAction(); d.__assign(pos, bb);
                        ind = d.value() == null ? "" : d.value().replaceAll("[\\t\\n\\r]", " "); break; }
                    case Action.IndicatorDotAction: break;
                    case Action.IndicatorLineAction: break;
                    default: act(rn, b, "unknown" + at, "", "", "");
                }
            }
            if (turns != null)
                turns.println(rn + "\t" + b.id + "\t" + b.team + "\t" + TYPE[b.type] + "\t" + b.x + "\t" + b.y + "\t" + b.hp
                        + "\t" + b.paint + "\t" + t.moveCooldown() + "\t" + t.actionCooldown() + "\t" + bc + "\t" + ind);
        }
        for (int i = 0; i < r.diedIdsLength(); i++) {
            Bot v = bots.get(r.diedIds(i));
            if (v != null && v.alive) {
                v.alive = false;
                if (v.team > 0) { died[v.team][v.type]++; if (isTower(v.type)) towersLost[v.team][v.type]++; }
            }
        }
        for (int i = 0; i < r.teamIdsLength(); i++) {
            int tm = r.teamIds(i);
            if (tm < 1 || tm > 2) continue;
            perMille[tm] = r.teamCoverageAmounts(i); lastMoney[tm] = r.teamResourceAmounts(i); lastSrp[tm] = r.teamResourcePatternAmounts(i);
            lastCov[tm] = tiles[tm];
            if ((int) Math.round(tiles[tm] * 1000.0 / paintable) != perMille[tm]) covMismatch++;
            if (r50[tm] < 0 && tiles[tm] * 2 >= paintable) r50[tm] = rn;
            if (r70[tm] < 0 && tiles[tm] * 10 >= paintable * 7) r70[tm] = rn;
        }
        if (rounds != null) {
            int[][] cnt = new int[3][7]; int[] pt = new int[3];
            for (Bot b : bots.values()) if (b.alive && b.team > 0) { cnt[b.team][b.type]++; pt[b.team] += b.paint; }
            rounds.println(rn + "\t" + lastCov[1] + "\t" + lastCov[2] + "\t" + lastMoney[1] + "\t" + lastMoney[2] + "\t" + lastSrp[1]
                    + "\t" + lastSrp[2] + "\t" + cnt[1][4] + "\t" + cnt[1][5] + "\t" + cnt[1][6] + "\t" + cnt[1][1] + "\t" + cnt[1][2]
                    + "\t" + cnt[1][3] + "\t" + cnt[2][4] + "\t" + cnt[2][5] + "\t" + cnt[2][6] + "\t" + cnt[2][1] + "\t" + cnt[2][2]
                    + "\t" + cnt[2][3] + "\t" + pt[1] + "\t" + pt[2] + "\t" + r.diedIdsLength());
        }
        if (game == boardGame && rn == boardRound) printBoard(rn);
    }

    void printBoard(int rn) {
        char[][] g = new char[h][w];
        for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) {
            int i = x + y * w;
            g[y][x] = wall[i] ? '#' : ruin[i] ? 'R' : " aAbB".charAt(paint[i]);
            if (g[y][x] == ' ') g[y][x] = '.';
        }
        String low = "?pmdsxo", up = "?PMDSXO";
        for (Bot b : bots.values()) if (b.alive && b.team > 0) g[b.y][b.x] = (b.team == 1 ? up : low).charAt(b.type);
        System.out.println("round " + rn + " " + mapName + " (A upper, B lower: P/M/D towers, S soldier, X splasher, O mopper; paint a/b primary, A/B secondary)");
        for (int y = h - 1; y >= 0; y--) System.out.println(new String(g[y]));
    }

    void endGame(MatchFooter mf) throws IOException {
        int[] towers = new int[3], units = new int[3];
        for (Bot b : bots.values()) if (b.alive && b.team > 0) { if (isTower(b.type)) towers[b.team]++; else units[b.team]++; }
        String winner = mf.winner() == 1 ? "A" : mf.winner() == 2 ? "B" : "?";
        StringBuilder s = new StringBuilder("{");
        s.append("\"file\":").append(q(file)).append(",\"game\":").append(game).append(",\"map\":").append(q(mapName))
         .append(",\"width\":").append(w).append(",\"height\":").append(h).append(",\"paintable\":").append(paintable)
         .append(",\"teamA\":").append(q(teamA)).append(",\"teamB\":").append(q(teamB))
         .append(",\"winner\":").append(q(winner)).append(",\"winType\":").append(q(mf.winType() >= 0 && mf.winType() < WIN.length ? WIN[mf.winType()] : "?" + mf.winType()))
         .append(",\"rounds\":").append(mf.totalRounds());
        for (int tm = 1; tm <= 2; tm++) {
            String T = tm == 1 ? "A" : "B";
            s.append(",\"cov").append(T).append("\":").append(lastCov[tm])
             .append(",\"covPct").append(T).append("\":").append(String.format("%.2f", paintable == 0 ? 0 : 100.0 * lastCov[tm] / paintable))
             .append(",\"money").append(T).append("\":").append(lastMoney[tm])
             .append(",\"srp").append(T).append("\":").append(lastSrp[tm])
             .append(",\"towers").append(T).append("\":").append(towers[tm])
             .append(",\"units").append(T).append("\":").append(units[tm])
             .append(",\"spawned").append(T).append("\":").append(typeMap(spawned[tm]))
             .append(",\"died").append(T).append("\":").append(typeMap(died[tm]))
             .append(",\"towersBuilt").append(T).append("\":").append(towersBuilt[tm][1] + towersBuilt[tm][2] + towersBuilt[tm][3])
             .append(",\"towersLost").append(T).append("\":").append(towersLost[tm][1] + towersLost[tm][2] + towersLost[tm][3])
             .append(",\"exceptions").append(T).append("\":").append(exceptions[tm])
             .append(",\"maxBcRobot").append(T).append("\":").append(maxBcRobot[tm])
             .append(",\"maxBcTower").append(T).append("\":").append(maxBcTower[tm])
             .append(",\"atLimit").append(T).append("\":").append(atLimit[tm])
             .append(",\"r50").append(T).append("\":").append(r50[tm])
             .append(",\"r70").append(T).append("\":").append(r70[tm]);
        }
        s.append(",\"covMismatch\":").append(covMismatch);
        s.append(",\"dumpVersion\":").append(DUMP_VERSION).append("}");
        out.add(s.toString());
        if (outDir != null) {
            Files.writeString(Paths.get(outDir + "/g" + game + ".summary.json"), s + "\n");
            rounds.close(); turns.close(); actions.close();
            rounds = null; turns = null; actions = null;
        }
    }

    void setPaint(int loc, int v) {
        if (loc < 0 || loc >= paint.length) return;
        int old = paint[loc];
        if (old > 0) tiles[old <= 2 ? 1 : 2]--;
        paint[loc] = (byte) v;
        if (v > 0) tiles[v <= 2 ? 1 : 2]++;
    }

    static String typeMap(int[] c) {
        StringBuilder s = new StringBuilder("{");
        boolean first = true;
        for (int i = 1; i < c.length; i++) if (c[i] > 0) { s.append(first ? "" : ",").append(q(TYPE[i])).append(":").append(c[i]); first = false; }
        return s.append("}").toString();
    }

    static String q(String s) {
        if (s == null) return "null";
        StringBuilder b = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            if (c == '"' || c == '\\') b.append('\\').append(c);
            else if (c < 32) b.append(String.format("\\u%04x", (int) c));
            else b.append(c);
        }
        return b.append('"').toString();
    }
}

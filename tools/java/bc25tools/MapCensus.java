package bc25tools;

import battlecode.common.*;
import battlecode.world.*;
import java.io.File;
import java.util.*;

/** One TSV row per map: name, width, height, area, wallPct, ruins, symmetry (engine's), symOK (which of ROT/HREF/VREF
 *  hold for walls+ruins), towersA, towerDist (Chebyshev and Euclid^2 between nearest A and B starting towers),
 *  paintable, seed. With --ascii NAME prints the map (# wall, R ruin, P/M/D A towers, p/m/d B towers, ./a/b paint).
 *  Usage: MapCensus MAPDIR [--ascii NAME] */
public class MapCensus {
    public static void main(String[] a) throws Exception {
        File dir = new File(a[0]);
        if (a.length > 2 && a[1].equals("--ascii")) { ascii(GameMapIO.loadMap(a[2], dir, false)); return; }
        System.out.println("map\twidth\theight\tarea\twallPct\truins\tsymmetry\tsymOK\ttowersA\tcheb\tdist2\tpaintable\tseed");
        String[] names = dir.list((d, n) -> n.endsWith(".map25"));
        Arrays.sort(names);
        for (String n : names) {
            String name = n.substring(0, n.length() - 6);
            LiveMap m = GameMapIO.loadMap(name, dir, false);
            int w = m.getWidth(), h = m.getHeight();
            boolean[] wall = m.getWallArray(), ruin = m.getRuinArray();
            int walls = 0, ruins = 0;
            for (int i = 0; i < w * h; i++) { if (wall[i]) walls++; if (ruin[i]) ruins++; }
            StringBuilder ok = new StringBuilder();
            String[] sn = {"ROT", "HREF", "VREF"};
            for (int s = 0; s < 3; s++) {
                boolean good = true;
                for (int y = 0; y < h && good; y++) for (int x = 0; x < w && good; x++) {
                    int mx = s == 1 ? x : w - 1 - x, my = s == 2 ? y : h - 1 - y;
                    int i = x + y * w, j = mx + my * w;
                    if (wall[i] != wall[j] || ruin[i] != ruin[j]) good = false;
                }
                if (good) ok.append(ok.length() > 0 ? "," : "").append(sn[s]);
            }
            List<MapLocation> ta = new ArrayList<>(), tb = new ArrayList<>();
            for (RobotInfo r : m.getInitialBodies()) (r.getTeam() == Team.A ? ta : tb).add(r.getLocation());
            int cheb = 999, d2 = 99999;
            for (MapLocation p : ta) for (MapLocation q : tb) {
                cheb = Math.min(cheb, Math.max(Math.abs(p.x - q.x), Math.abs(p.y - q.y)));
                d2 = Math.min(d2, p.distanceSquaredTo(q));
            }
            int paintable = w * h - walls - ruins;
            System.out.printf("%s\t%d\t%d\t%d\t%.1f\t%d\t%s\t%s\t%d\t%d\t%d\t%d\t%d%n", name, w, h, w * h,
                    100.0 * walls / (w * h), ruins, m.getSymmetry(), ok, ta.size(), cheb, d2, paintable, m.getSeed());
        }
    }

    static void ascii(LiveMap m) {
        int w = m.getWidth(), h = m.getHeight();
        char[][] g = new char[h][w];
        boolean[] wall = m.getWallArray(), ruin = m.getRuinArray();
        byte[] paint = m.getPaintArray();
        for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) {
            int i = x + y * w;
            g[y][x] = wall[i] ? '#' : ruin[i] ? 'R' : paint[i] == 0 ? '.' : paint[i] <= 2 ? 'a' : 'b';
        }
        for (RobotInfo r : m.getInitialBodies()) {
            char c = r.getType().getBaseType() == UnitType.LEVEL_ONE_PAINT_TOWER ? 'P'
                    : r.getType().getBaseType() == UnitType.LEVEL_ONE_MONEY_TOWER ? 'M' : 'D';
            g[r.getLocation().y][r.getLocation().x] = r.getTeam() == Team.A ? c : Character.toLowerCase(c);
        }
        System.out.println(m.getMapName() + " " + w + "x" + h + " " + m.getSymmetry() + " (row y=" + (h - 1) + " first)");
        for (int y = h - 1; y >= 0; y--) System.out.println(new String(g[y]));
    }
}

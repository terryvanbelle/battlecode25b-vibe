package t114;

import battlecode.common.*;

/** Map symmetry by elimination. Candidates: ROT (x,y)->(W-1-x,H-1-y), MX (x,y)->(W-1-x,y), MY (x,y)->(x,H-1-y).
 *  A tile seen for the first time is compared with its image under each live candidate (if that image was seen);
 *  a wall/ruin mismatch kills the candidate. The set never empties (a contradiction keeps the last survivors). */
public strictfp class Sym {
    static final int ROT = 1, MX = 2, MY = 4;
    static int live = 7;

    static void init() { live = 7; }

    static void observe(int x, int y, int v) {
        int W = G.W, H = G.H;
        int[] mem = G.mem;
        int l = live;
        if ((l & ROT) != 0) {
            int m = mem[(W - 1 - x) + (H - 1 - y) * W];
            if ((m & 1) != 0 && (m & 7) != v) l &= ~ROT;
        }
        if ((l & MX) != 0) {
            int m = mem[(W - 1 - x) + y * W];
            if ((m & 1) != 0 && (m & 7) != v) l &= ~MX;
        }
        if ((l & MY) != 0) {
            int m = mem[x + (H - 1 - y) * W];
            if ((m & 1) != 0 && (m & 7) != v) l &= ~MY;
        }
        if (l != 0) live = l;
    }

    /** Eliminate candidates that predict an enemy tower at a location seen holding none (only for a starting tower,
     *  before round 30, when it cannot yet have been destroyed). */
    static void killIf(int c) { if ((live & ~c) != 0) live &= ~c; }

    static MapLocation mirror(MapLocation p, int c) {
        switch (c) {
            case ROT: return new MapLocation(G.W - 1 - p.x, G.H - 1 - p.y);
            case MX: return new MapLocation(G.W - 1 - p.x, p.y);
            default: return new MapLocation(p.x, G.H - 1 - p.y);
        }
    }

    static int count() { return (live & 1) + ((live >> 1) & 1) + ((live >> 2) & 1); }

    /** The candidate to act on: the only one, or ROT, MX, MY in that order of preference among the live ones. */
    static int best() { return (live & ROT) != 0 ? ROT : (live & MX) != 0 ? MX : MY; }
}

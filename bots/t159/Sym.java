package t159;

import battlecode.common.*;

/** Map symmetry by elimination. Candidates: ROT (x,y)->(W-1-x,H-1-y), MX (x,y)->(W-1-x,y), MY (x,y)->(x,H-1-y).
 *  A tile seen for the first time is compared with its image under each live candidate (if that image was seen);
 *  a wall/ruin mismatch kills the candidate. The set never empties (a contradiction keeps the last survivors).
 *  Only the tower debug string reads the result (Tower.turn). */
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
}

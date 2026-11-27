## t135 bug audit

**Scope:** I read all 9 files in `bots/t135`. API claims were checked against the extracted engine 3.1.0 source (`.../audit-bugs/engine-src`). Frequencies come from the 9 ReplayDump replays I had, restricted to the 7 team-games whose code matches t135 everywhere except one Soldier rule:
- The bots are t122, t130, y251, y257 and y265. Their G, Unit, Splasher, Mopper, Tower and Nav files match t135, apart from y265's splasher "salt" block and t130's guard mopper.
- **No t135 replay exists**, so its one new rule (the lone soldier skipping the mark, Soldier.java:226-230) has no data.
- The sample is 416 robots, against mixed local opponents rather than replica ones. Treat the counts as rough.
- I ran no games, edited nothing under `bots/` or `src/`, and committed nothing.

**Headline:**
- **Running out of paint is the leading cause of death.** 158 of 416 robots (38%) died from the no-paint damage: 52 of 100 moppers, 84 of 224 soldiers and 22 of 92 splashers. Enemy towers killed about 70.
- **175 robots reached 0 paint.** Their refill target in the 15 turns before:

  | Refill target | Robots |
  |---|---|
  | One of our own drained money towers | 75 (45 of them with chips ≥ 2000) |
  | A tower that was dead or enemy | 40 |
  | A drained paint tower | 8 |
  | A tower that actually had paint | 37 |
  | No refill target | 15 |

- **About 37% of all refill-walk turns head to the wrong tower:** 27% to drained money towers and 10% to dead towers.

---

### CONFIRMED, ranked by expected win-rate impact

**1. Refill target selection: robots walk to towers that are drained or gone.** This fires every game; the numbers are in the headline. It has five parts.

- **(a) Unit.java:23, the churn exception.**
  - *What it does:* when chips ≥ 2000, the `!(towerKind==2 && churnable())` clause ignores the empty-tower ("dry") flag on every money tower. That includes level 2/3 towers, which Tower.churn (Tower.java:25) never rebuilds, and level 1 towers whose rebuild just failed (pattern broken, or an enemy in view).
  - *Scenario:*
    1. Chips are 2400 and a robot is beside a drained money tower.
    2. It waits 3 rounds (L49-53), flags the tower (L54) and returns false (L57).
    3. Next turn it picks the same tower again, because L23 ignores the flag.
    4. It oscillates beside the tower until churnAt expires 50 rounds later, or until it reaches 0 paint and cannot move.
  - *Frequency:* every game. Refill trips to drained money towers that did not rebuild cost about 2000 robot-turns: about 290 per team-game, or 5% of all robot turns. 87 of those episodes were at level 2+ towers.
  - *Fix:* add `static boolean[] towerL1 = new boolean[32]` to G, set it from `a.type == LEVEL_ONE_MONEY_TOWER` in `remember`, then:
    ```java
    boolean churnTry = G.towerL1[i] && churnable() && !(l.equals(churnLoc) && G.round - churnAt < 50);
    if (towerDry[i] > 0 && G.round - towerDry[i] < (G.towerKind[i] == 1 ? 10 : 150) && !churnTry) {
    ```
- **(b) Unit.java:23, the 40-round expiry.** A money tower's flag expires after 40 rounds, but money towers never regain paint (0 paint per turn). Only a rebuild refills them, and a rebuilt tower is re-sensed anyway (L26-29). The fix is the 150 above.
- **(c) Only the robot that goes to refill ever sets the flag (L54, L59), and the flag is per robot.** Every robot has to walk within sight of each drained tower to learn it is empty. The traces show this, e.g. a soldier at 39 paint walking to drained (10,11), then drained (2,10). *Fix:* in G.remember, L118-121, the ally-tower loop already runs. Have `noteTower` return the index, then:
  ```java
  if (a.paintAmount < 20) Unit.towerDry[j] = round; else if (a.paintAmount >= 50) Unit.towerDry[j] = 0;
  ```
- **(d) G.java:137-141, flags drift on forget.** `forgetTower` moves the last entry into slot i but leaves `Unit.towerDry` in place. Another tower inherits the wrong flag, and the next tower added at L134 inherits a stale one. This fires on every forget, and dead-tower forgets are common (see e). *Fix:* in forgetTower add `Unit.towerDry[i]=Unit.towerDry[nTowers]; towerL1[i]=towerL1[nTowers]; Unit.towerDry[nTowers]=0;`, and in noteTower's add branch add `Unit.towerDry[nTowers]=0;`.
- **(e) Dead towers are forgotten only when they are the refill target and in sight (Unit.java:39).** 40 robots reached 0 paint walking to a dead or enemy tower. wantType (Soldier.java:140-143) also counts dead towers. *Fix:* at the end of `remember` (it has to declare `throws GameActionException`; its caller already does), add the loop below. It costs about 300-500 bytecode per turn; run it every few rounds if that is too much.
  ```java
  for (int i = nTowers; --i >= 0; ) { MapLocation l = towerLoc[i];
    if (here.distanceSquaredTo(l) <= 20 && rc.canSenseLocation(l)) { RobotInfo t = rc.senseRobotAtLocation(l);
      if (t == null || t.team != me) forgetTower(l); } }
  ```

**History:** the level-1-only exception (t126) was retired as "built on t118", and the forgetTower fix (t132) went in with the −140 repaint change. Neither has been tested alone on this lineage. I'd make (a)-(e) one candidate.

**2. Soldier.java:19-23: soldiers attack towers with no paint floor.**
- *What it does:* any soldier with at least 5 paint and an enemy tower within range 9 attacks it, before any other logic. That bypasses the SIEGE_PAINT=30 floor.
- *Scenario:* a soldier walking to refill passes an enemy tower and spends its last paint inside the tower's range.
- *Frequency:* 42 soldiers, about 6 per team-game, attacked outside siege mode and were left with under 25 paint. 41 of them were refilling at the time. 40 died within 25 rounds and 32 reached 0 paint. In 6 attacks the soldier hit exactly 0 paint and could no longer move.
- *Caveat:* refilling soldiers below 25 paint that did not attack reached 0 at 68% (vs 76% for those that did). So only part of this is recoverable.
- *Fix:* `G.paint >= SIEGE_PAINT` instead of `G.paint >= 5`.

**3. G.java:96-101: splashers repaint our own patterns.** The −50 guard only covers SRP-lattice positions, and a splash repaints ally tiles with primary.
- *Measured:* 64 of our secondary tiles were turned primary: 31 in the 5x5 of unbuilt ruins, 25 around our money towers and 8 around paint towers. The money-tower damage blocks rebuilds, since Tower.java:31-37 needs the exact pattern.
- *Fix:* inside the splasher branch, after the loop:
  ```java
  if (srpMask != 0) for (MapLocation r : ruins) for (int x = r.x-2; x <= r.x+2; x++) for (int y = r.y-2; y <= r.y+2; y++) {
    int gx = x-ox, gy = y-oy; if (gx<0||gy<0||gx>10||gy>10||x<0||y<0||x>=w||y>=H) continue;
    if ((m[x+y*w] >> 4) == 2) { v1[gy*11+gx] = -50; v2[gy*11+gx] = -50; } }
  ```

**4. Unit.java:107-108: repairPattern attacks enemy-painted tiles.** `canAttack` is true on enemy paint, but a soldier's attack does not repaint it. So it spends 5 paint and changes nothing.
- L51 then refreshes churnAt, so the soldier keeps waiting beside the tower and spends 5 paint a turn.
- *Measured:* 23 of 95 repair actions hit enemy tiles, and 3 soldiers did it 3 or more times. This matches the 5 soldiers that were waiting for a rebuild when they reached 0 paint.
- *Fix:* after L107, add `if (p.isEnemy()) return false;` (the tower cannot be rebuilt until a mopper cleans it).

**5. Soldier.java:214-218: a soldier mid-pattern idles when the refill fails.** `Unit.refill(10000); return true;` runs even when refill returns false, and it only triggers below 10 paint.
- *Trace:* in sayhi, soldier 11885 stood at (26,17) with 8 paint for 141 turns. Its only known tower (25,16) had been destroyed and forgotten.
- *Frequency:* rare, 1 robot in 7 team-games. 10 soldiers reached 0 paint with "ruin" as their last activity, because they leave for refill with only 9 paint.
- *Fix:* `if (Unit.refill(10000)) return true; markBad(r, 50); ruin = null; return false;`. t134 tried this and was flat, which fits how rare it is.

**6. Tower.java:90 (with 66 and 69-76): money towers never spawn splashers.**
- *What happens:* a money tower makes no paint. With 500 starting paint it spawns slot 0 (soldier, 200) and slot 1 (mopper, 100), then stalls at slot 2 (splasher, 300) with 200 left. Before round 80 it spawns 2 soldiers and stalls with 100 left.
- *Measured:* money towers spawned 117 soldiers, 71 moppers and **0 splashers**. Slots 3-5 are unreachable, so **y240 (a slot-5 change) was a no-op**.
- *Paint-tower comment:* it says "S X X M" (soldier, two splashers, mopper), but `built%6` then `%4` gives the 6-cycle S X X M S X. Measured paint-tower spawns were 108 soldiers, 93 splashers and 29 moppers.
- *Impact:* uncertain, because the leftover 200 paint feeds refills. You choose the intended mix. If the comment is the intent, the fix is `if (G.paint < t.paintCost) { if (!rc_isPaintTower()) built++; return; }`.

**7. Bytecode (low impact; overruns measured at 0-2 per game).**
- Unit.java:126: exploreTarget makes up to 128 random draws with no bytecode guard, and the comment says 8. Fix: `if (Clock.getBytecodesLeft() < 2000) break;` after each draw.
- Soldier.java:343: pickSrp's 3000-bytecode margin plus the explore draws produce the 17.5k peaks on full-paint turns.

**8. Minor and comment-only items.**
- **Tower.java:102-110 and 25:** upgrade and churn use G.chips read before build() spent chips, so an upgrade can leave 250-400 below UPGRADE_SPARE. Fix: `G.chips = rc.getChips();` at the top of each.
- **Unit.java:59-61:** after markDry the robot still steps toward the drained tower that turn. Fix: `{ markDry(best); refillAt = null; return false; }`.
- **Tower.java:89:** the second clause is redundant (the condition reduces to `chips < cost + reserve`). The L85 comment "freeze spawns 8 rounds in 20" is not implemented.
- **Tower.java:60-61:** `enemyNear` is never used.
- **Comment mismatches:**
  - Soldier.java:119 "two soldiers per ruin at most" vs the rule at L122-124.
  - Unit.java:123-124 "up to 8 tiles" vs 128.
  - Splasher.java:148 "add 12" vs +30 at L157.
- **Dead code:** Sym's mirror, best, killIf and count are never called; `Sym.live` only reaches the tower's indicator string, while `Sym.observe` still costs bytecode. `Nav.last1`/`last2` are written but never read.
- **Completed SRPs** are skipped forever (srpSkip=MAX at L366/L427/L441), even if they are later broken.

---

### SUSPECTED

- **S1. Soldier.java:226-230, ruin type conflict.** A lone soldier commits to `wantType()` without marking. A second soldier arriving later finds no marks and calls `wantType()` itself. That value depends on chips (L145: n≥3 and chips≥1500, L149) and on each robot's own tower memory (L140-150), so the two can disagree. They then overwrite each other's paint until the 150-round timeout and `markBad(150)`. The pre-t135 bots always marked and showed 0 conflicts in 71 ruins; t135 has no replays to check. *Fix:* when there are no marks, infer the type from existing ally paint (readMarks using `getPaint()`, adopting a type if 3 or more ally tiles match). Worth a look, since this rule is t135's only difference from t122.
- **S2. Soldier.java:41, siege exit at 30 paint is probably too low (tuning).** 67 of the 95 soldiers that reached 0 paint were last in siege mode. Siege soldiers reached 0 paint at 74 of 150, against 21 of 74 for the others. But siege also dealt all 82,600 tower damage and made 47 kills. Test SIEGE_PAINT around 50-60, or base the exit on the distance home.
- **S3. Mopper.java:12:** `G.paint < 40 &&` cancels a refill trip already under way as soon as paint gets back to 40, so moppers don't reach the 75 target unless they arrive at the tower. Fix: `(G.paint < 40 || Unit.refillAt != null)`. Probably minor.
- **S4. Soldier.java:224-232:** a soldier with 10-24 paint, another soldier in view and no marks cannot mark, and returns true without doing anything. Only 2 turns were observed, so it is rare.
- **S5. Soldier.java:193 vs 225:** prePaint and the later decision can pick different types when chips cross 1500 at n==3. Rare.

### Checked and not a problem
- Mopper and splasher avoidance of tower range: only 4 moppers and 2 splashers were killed by towers.
- Nav's wall-following and hand choice, the SRP mask (20033) and the pattern bit order are correct.
- canUpgradeTower already guards level 3.
- Mopper swing geometry matches the engine.

### Suggested order to test
1. A candidate with fix 1 (a-e) only.
2. Then fixes 2 and 4, which are one line each.
3. Then fix 3.
4. Test fix 6 and S1 separately.

Scripts and dumps are in `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/audit-bugs/`. The scripts are under `scripts/` (main ones `starve3.py`, `checks.py`, `checks2.py`, `episodes.py`; each takes the dump directories as arguments), and the dumps are under `dump/`.

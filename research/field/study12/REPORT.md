# Field study 12 (2026-11-27): t135 and t140 on the replica since submission 77

This study used replays only. I read no competitor code and no write-ups, made no `contest.py` or replica call, ran no games, and edited no bots, tools or tests.

**Versions.** The 48 matches after study 11's last (5012) were played by three of our submissions; `pkgs.py` read every replay header (`pkgs.txt`):
- **t122** (submission 76), 14 matches, 5067-5165, played before t135 reached the replica;
- **t135** (submission 77, crowned 06:10), 21 matches, 5202-5393;
- **t140** (submission 78, crowned 08:28: t135 + study 11 2.1, free marks), 13 matches, 5450-5557.

Every opponent package is one studies 10 and 11 already saw, so same-opponent comparisons are like for like. **All code references are to `bots/t140`.** t140 differs from t135 only in Soldier.java (t135's lone-soldier mark skip at 225-230 became t140's 239-242, `freeMarks` is new at 187-200 and is called at 246); every other file is identical, so a t140 line number outside Soldier.java holds for t135 too. Unless a line says otherwise, the numbers below are **t135 + t140 together (99 games: 55 won, 44 lost)**: the two share everything except the mark code, and t140 alone (37 games) is too few to split most measures.

| match | ver | opponent | W-L | | match | ver | opponent | W-L |
|---|---|---|---|---|---|---|---|---|
| 5067 | t122 | gone-whalin | 0-1 (g0,2 dup) | 5282 | t135 | scienceqiu | 2-1 |
| 5068 | t122 | lobster-roll | 3-0\* | 5283 | t135 | placeholder-name-2 | 2-1\* |
| 5069 | t122 | spaark | 1-2 | 5284 | t135 | gone-whalin | 2-1 |
| 5070 | t122 | scienceqiu | 0-2\* (g2 dup) | 5287 | t135 | slifland | 3-0 |
| 5089 | t122 | placeholder-name-2 | 1-2 | 5316 | t135 | scienceqiu | 3-0 |
| 5124 | t122 | lobster-roll | 2-1 | 5356 | t135 | immutable | 2-1 |
| 5125 | t122 | placeholder-name-2 | 2-1\* | 5366 | t135 | immutable | 1-2 |
| 5126 | t122 | scienceqiu | 2-1 | 5368 | t135 | subscribe-to-caterpillow | 3-0 |
| 5127 | t122 | angtn | 2-1\* | 5369 | t135 | immutable | 0-2\* (g2 dup) |
| 5128 | t122 | spaark | 1-2 | 5375 | t135 | immutable | 0-3 |
| 5129 | t122 | slifland | 3-0\* | 5393 | t135 | subscribe-to-caterpillow | 0-3 |
| 5156 | t122 | lobster-roll | 2-0 (g2 dup) | 5450 | t140 | gone-whalin | 3-0 |
| 5164 | t122 | immutable | 1-1 (g2 dup) | 5458 | t140 | scienceqiu | 2-1 |
| 5165 | t122 | scienceqiu | 2-1\* | 5467 | t140 | gone-whalin | 3-0 |
| 5202 | t135 | scienceqiu | 1-2 | 5492 | t140 | immutable | 1-2 |
| 5203 | t135 | lobster-roll | 2-1\* | 5493 | t140 | subscribe-to-caterpillow | 1-2\* |
| 5204 | t135 | gone-whalin | 2-1 | 5494 | t140 | confused | 1-2 |
| 5205 | t135 | placeholder-name-2 | 0-3\* | 5495 | t140 | gone-whalin | 1-1\* (g0 dup) |
| 5216 | t135 | placeholder-name-2 | 2-1 | 5496 | t140 | om-nom | 0-3 |
| 5259 | t135 | gone-whalin | 1-2 | 5497 | t140 | spaark | 1-2\* |
| 5277 | t135 | spaark | 1-2 | 5530 | t140 | spaark | 1-2 |
| 5278 | t135 | gone-whalin | 2-1\* | 5537 | t140 | subscribe-to-caterpillow | 1-2 |
| 5279 | t135 | immutable | 3-0 | 5553 | t140 | om-nom | 2-0 (g1 dup) |
| 5281 | t135 | slifland | 3-0\* | 5557 | t140 | placeholder-name-2 | 3-0 |

\* = unranked.

**Repeats** (`t137`). Nine games exactly repeat an earlier one (same map, opponent, end round, coverage and spawn counts; the engine is deterministic). Eight are left out (`lib.DUP`): five t122 games equal to study 11 t122 games (m5067 g0 and g2, m5070g2, m5156g2, m5164g2), m5369g2 = m5356g2 (t135), m5495g0 = m5450g0 and m5553g1 = m5496g1 (t140). The ninth is kept: **m5278g0 (t135) = m4957g0 (t122)**, a Justice loss at r372 that t135's change did not touch at all; it is t135's result.

That leaves **136 games: 77 won, 59 lost (57%)**; study 11 had 50-58 (46%).

| | t122 | t135 | t140 | t135 + t140 |
|---|---|---|---|---|
| all | 22-15 | 35-27 | 20-17 | 55-44 (56%) |
| the seven top teams | 14-11 | 25-22 | 16-15 | 41-37 |
| the rest | 8-4 | 10-5 | 4-2 | 14-7 |
| ranked / unranked | 10-10 / 12-5 | 26-19 / 9-8 | 17-12 / 3-5 | 43-31 / 12-13 |
| losses: median end, eliminations | r391, 6 | r411, 3 | r452, 3 | |

| opponent | t122 | t135 | t140 | | opponent | t122 | t135 | t140 |
|---|---|---|---|---|---|---|---|---|
| gone-whalin | 0-1 | 7-5 | 7-1 | | spaark | 2-4 | 1-2 | 2-4 |
| immutable | 1-1 | 6-8 | 1-2 | | subscribe-to-caterpillow | - | 3-3 | 2-4 |
| scienceqiu | 4-4 | 6-3 | 2-1 | | om-nom | - | - | 2-3 |
| lobster-roll | 7-1 | 2-1 | - | | confused | - | - | 1-2 |
| placeholder-name-2 | 3-3 | 4-5 | 3-0 | | slifland, angtn | 5-1 | 6-0 | - |

Win types: 46 losses on majority paint, 12 eliminations and one area decision at r2000 (Filter, spaark, 5497g0: 24.3% / 45.8%); 4 wins by elimination.

**Did t135 or t140 change the replica results? It cannot be told** (`t138`). A pairing (opponent package, map) played by two versions isolates the version, but there are few: t140 and t135 share 4 pairings (2-2 each), t140 and t122 8 (t140 5-3, t122 4-5), t135 and t122 12 (7-5 against 8-5). The only flips are spaark/Money (t140 won, t122 lost) and placeholder-name-2/defensetower (t135 lost, t122 won). The local tourney measured t140 at +40 ±23 over t135 in 251 fresh games; the replica set is too small to confirm or refute that.

**How to run.**
- `lib.py` is study 11's loader with the study 12 dumps; versions come from `pkgs.txt`. Environment: `S12VER=t135,t140` (versions), `S12TEAMS=a,b|top`, `S12RANKED=1`, `S12SET=main|prev|old|all` (`prev` = study 11's t122 set, `old` = study 10's), `S12DUP=1` keeps repeats; the `S11*` / `S10*` names still work. New: `lib.extra(G)` returns each turn's movement cooldown, action cooldown and bytecodes from `turns.tsv`, and `lib.games` now filters on `summary.json` before it loads a game.
- `./run.sh tNN_x.py [out]` writes `tNN.txt`. New in this study: `t137_dups`, `t138_paired`, `t139_marks` (all versions), `t140_drain`, `t141_nav`, `t143_actions`, `t144_upheal`, `t145_ground`, `t146_walkpaint`, all with `S12VER=t135,t140` unless noted. `t142_bytecode` is written but was not run. The study 11 scripts rerun here (`t0`, `t106`, `t108`) used `S12VER=t135,t140`; `t0_t140.txt` is t140 alone.
- Dumps: `/tmp/claude-1000/-home-terryvanbelle/8f9283b7-c207-4cad-877b-a8886208db0a/scratchpad/study12/dump/mM` (48 matches, 144 games, dump version 3, `covMismatch` 0). After the study their `turns.tsv` and `actions.tsv` were deleted (245M); the summaries and the pickles in `.../study12/cache` (161M) remain, so every script reruns except `t141` and `t142`, which read `turns.tsv` through `lib.extra`. Rebuild with `~/opt/jdk21/bin/java -cp build/tools:engine/battlecode25-java-3.1.0.jar bc25tools.ReplayDump tsv REPLAY DIR/mM`, one java process at a time. The scratchpad can be cleared at any time.

## 1. How the games were lost

### Overview (t135 + t140: 44 losses, 55 wins)
- **Ends:** 37 losses on majority paint, 6 eliminations, 1 area decision at r2000. Median end r436.5 (study 11 r410.5).
- **Level at r100, then outgrown.** At r100 the median loss has 6 / 6 towers and 19.6 / 20.4% coverage. By r200 it is 6 / 8 towers and 1498 / 3380 paint. Towers destroyed (`t144`): ours 11.7 a loss, theirs 6.1.
- **Paint-bound, chip-rich** (`t106`): every tower of ours holds under 200 paint in 50.9% of the rounds of a loss (theirs 28.9%; study 11 58.8 / 22.0). In those rounds we hold a median 2180 chips. Our last paint tower died for good in 14 of 44 losses (median r384.5).
- **New this study: the opening.** At r75 the median loss has 14.4 / 18.2% coverage (222 / 279 tiles) while we hold more paint, 2180 / 1882. We bank paint in soldiers that walk on unpainted ground (2.1). In 7 of the 8 teams' losses we trail on coverage at r100 (`t108`): immutable 22.5 / 29.4, subscribe-to-caterpillow 15.0 / 20.2, scienceqiu 12.4 / 16.3, spaark 23.0 / 25.2, placeholder-name-2 17.3 / 19.3, lobster-roll 21.8 / 24.6, om-nom 12.1 / 12.4. The exception is gone-whalin (28.6 / 19.9), which beats us on tower kills: first kill on us at a median r40, every loss had a kill by r100, and they have 6.5 moppers to our 1.5 at r100.

### Median timeline of the 44 losses (`t0`, us / them)

| round | coverage % | towers | paint towers | chips | paint (units + towers) | robots (S / X / M) |
|---|---|---|---|---|---|---|
| r50 | 12.6 / 13.7 | 4 / 4 | 1 / 1 | 880 / 790 | 1462 / 1666 | 8 / 7 (8/6.5, 0/0, 0/0.5) |
| r75 | 14.4 / 18.2 | 5 / 5 | 1 / 1 | 660 / 860 | 2180 / 1882 | 7 / 9 (7/7, 0/0, 0/2) |
| r100 | 19.6 / 20.4 | 6 / 6 | 1 / 1 | 1140 / 1066 | 2122 / 1943 | 8 / 10 (8/7, 0/0, 1/3) |
| r150 | 29.7 / 25.0 | 7 / 6 | 1 / 2 | 1540 / 1096 | 1694 / 2693 | 13 / 15 (9/8, 1/2, 3/5) |
| r200 | 30.6 / 30.6 | 6 / 8 | 2 / 2 | 2294 / 1250 | 1498 / 3380 | 14 / 22 (8/9, 2/3, 3/9) |
| r300 | 32.8 / 42.7 | 6 / 10 | 2 / 3 | 1602 / 1132 | 1865 / 5653 | 11 / 35 (5/11, 4/10, 3/14) |
| r400 (28) | 27.7 / 50.0 | 6 / 12.5 | 2 / 4 | 1439 / 1130 | 1512 / 8496 | 10 / 48.5 (4/15, 4/15, 2/15.5) |

The shape is study 11's again: level or ahead at r100-150, then from r150 their paint economy turns into units and towers while ours stalls with chips in the bank. The new rows are r50-r75: they paint more of the map earlier while we hold the paint.

### Where our paint goes (`t140`, an exact replay of the end-of-turn penalty; ledger check 97-100%)
- **Opening soldiers pay 61% more:** in r1-100 our soldiers lose 70.0 paint per 100 turns to the ground rule, theirs 43.4 (wins: 74.3 / 55.0). Tile cost is 47.1 / 30.0 and crowding the rest. Our soldiers end 31.1% of their turns on neutral ground, theirs 15.0%.
- **Per game,** all our robots pay 478 paint in r1-100 against their 361 (wins 521 / 432). That is 100-120 paint a game, about one tower pattern.
- **Beside towers** in r101-200 we pay 150 a loss to crowding, they pay 78 (wins 140 / 52). It is mostly splashers waiting at towers (2.5).
- **After r200** crowding scales with army size and is theirs to pay.

### What the robots do (`t141` movement and cooldowns, `t143` actions, `t145` turn classes, `t146` walking paint)
- **Soldiers, r1-100** (losses): ours move on 65.6 turns in 100, theirs on 78.3. Ours stand still on 31.0% of turns, theirs on 12.5%. Ours are below 50% paint (cooldown tax) on 28.3% of turns, theirs on 37.9%. **They spend their paint and keep moving; we hold ours.**
- **Where it goes** (`t145`): 32% of soldier-turns in r1-100 are walking for both sides, but **our walking turns end on neutral ground 56% of the time, theirs 18%**. We pay 86.8 paint per 100 walking turns, they pay 30.2. Turns at ruins cost both sides the same, 48 / 43.
- **Why** (`t146`): before r80 their walking soldiers paint the tile they stand on in 11-27% of walking turns and another tile in 11-19%. Ours do 0.8-3.3% and 0.6-3.0%, because Soldier.java:34-36 paints nothing before r80. In r101-200, when ours paint as they walk, our walking turns end on our own paint as often as theirs (83% / 86%, `t145`).
- **Moppers** (`t141`, `t143`): ours stand still on 38-46% of turns, theirs on 10-13%. Ours attack robots a third as often in r1-100 and never swing at a single robot (2.2).
- **Splashers** (`t143`, `t145`): ours spend 7-17% of their turns beside our own towers, theirs 3-4%, and withdraw paint seven times as often (2.5).

## 2. Differences, as codeable rules
Line numbers are for `bots/t140`. Study 11's 2.2 (siege HP exit; t141 -53, t142 -92) is not proposed again.

### 2.1 Opening cover: before r80 a walking soldier paints the tile it stands on (high; an old rule never retested)
**Evidence:**
- **What they do** (`t146`): walking soldier-turns away from free ruins, losses, r1-50 / r51-80, us / them.

  | ends on | us | them |
  |---|---|---|
  | own paint already | 22.5 / 24.8% | 48.0 / 56.0% |
  | a tile it painted this turn | 0.8 / 2.7% | 26.9 / 14.1% |
  | neutral | 67.5 / 59.7% | 21.2 / 23.3% |
  | painted another tile | 0.6 / 3.0% | 15.7 / 19.0% |

  Wins are the same (painted under 1.7 / 3.3% against 22.1 / 11.2%, neutral 65.3 / 56.8% against 25.2 / 26.3%). **They paint as they walk; we don't before r80.**
- **We have the paint** (`t146`, `t141`): our walking soldiers carry a mean 173.5 / 154.3 paint in r1-50 / r51-80, theirs 150.6 / 115.6. Ours are below 50% (the cooldown tax) on 28.3% of r1-100 turns, theirs on 37.9%.
- **Not painting costs us** (`t145`, `t140`): our walking turns in r1-100 pay 86.8 paint per 100 to the ground rule, theirs 30.2. Our r1-100 soldiers pay 70.0 per 100 turns, theirs 43.4. Across all robots that is 100-120 paint a game.
- **Coverage** (`t0`, `t108`): 14.4 / 18.2% at r75 of the losses (222 / 279 tiles), and we trail at r100 in the losses to 7 of 8 teams.
- **t140 alone** (`t0_t140`, 17 losses): 15.9 / 20.2% coverage at r100 while holding 2349 / 1957 paint. The 200 paint a game that free marks saved (3) went into the bank, not onto the map.
- **When ours start at r80** they catch up in a burst: 62.8% of r81-100 walking turns paint, theirs 28.2%. In r101-200 our walking turns end on own paint 83% of the time, theirs 86% (`t145`).

**Code (t140):** Soldier.java:33-36, the comment "study 3 tactic 2: before r80 save paint for tower patterns (no coverage)" and `if (G.round >= 80) paintNear();` before (34) and after (36) `Nav.moveTo(Unit.exploreTarget())`. Two helpers exist:
- `paintHere` (484-489): the tile under us only, empty only, 25-paint floor;
- `paintNear` (492-505): the tile under us first, else the nearest empty tile in r2 9, 50-paint floor.

**Rule:** before r80, after the explore move (line 36), paint the empty tile under the soldier when it holds F or more paint: `else if (G.paint >= F) paintHere();`.
- F = 150 keeps a whole pattern's 120 paint (24 tiles at 5), so a fresh soldier paints at most 10 tiles before r80.
- F = 100 matches their walking mean paint in r51-80 (116) and keeps the soldier above the cooldown tax.

**Expected size:** medium.
- Our losses have about 119 neutral walking turns a game before r80 (4316 x 67.5% + 3885 x 59.7% over 44 games).
- At F = 150 perhaps half get painted: about 60 tiles of cover by r80 (their lead at r75 is 56 tiles) for about 300 paint, of which about 60 comes back as drain not paid.
- Later walkers then cross painted ground.

**Prior attempts:**
- The rule this reverses is study 3 tactic 2. It was crowned twice on the 2026-11-25 base: y58 (no cover before r50) and t04 (t02: before r80). It has not been tested since (study 11 2.4).
- The base has changed since. It gained pre-painting at ruins (Soldier.java:237), free marks, the r40 reserve and the 1000-chip spawn gate. The paint tactic 2 protected now sits unused.

**Candidates:**
- `c1`: F = 150, the tile under only (line 36);
- `c2`: F = 100;
- `c3`: tactic 2 off at line 36 only, `paintNear()` from r1 (the tile under first, else the nearest; 50 floor). This is closest to their "another tile" 16-19%.

### 2.2 Moppers: swing at a lone robot out of mop reach, drain robots before ruin paint (medium-low; new)
**Evidence** (`t143`, `t141`; per 100 mopper-turns, losses, r1-100 / r101-200 / r201+, us / them):
- **Attacks on robots:** ours 4.7 / 6.2 / 7.5, theirs 14.7 / 8.6 / 5.5 (single drains plus swings). In wins: ours 6.3 / 6.4 / 6.5, theirs 13.2 / 9.7 / 9.8.
- **Swings:** ours 0.34 / 1.06 / 2.24, theirs 5.70 / 3.38 / 2.08. Wins: ours 0.47 / 1.09 / 1.47, theirs 3.64 / 2.87 / 3.55.
- **Victims per swing:** ours 2.0-2.1 in every phase, theirs 1.16-1.33. They swing at a single robot; we never do (`bestN = 1` means 2+ victims).
- **Tiles mopped:** ours 19.3 / 18.9 / 13.6, theirs 16.7 / 15.9 / 8.4. Our moppers clean paint; theirs fight.
- **Movement:** our moppers stand still 38-46% of turns, theirs 10-13%. Ours are idle with a free move (no move and no action, movement ready) 22-27% of turns, theirs 7-10%. They also step back and forth (A-B-A, away from towers and sieges) 8.7-20.7 times per 100 moves, ours 1.2-2.9. That is hit-and-run around enemy robots; ours walk up and stand (Mopper.java:16).
- **Passive loss** (`t140`): our moppers lose 137 / 122 / 132 paint per 100 turns, theirs 95 / 94 / 119. In wins ours are lower after r200.
- **They field more moppers:** per 100 tower-turns they spawn 0.81 / 1.20 / 2.01 moppers, we spawn 0.29 / 0.53 / 0.48. By r100 that is about 3.2 moppers a game against our 1.1, in wins and in losses alike, so the count does not separate the outcomes.

**Code (t140):**
- `Mopper.act` (Mopper.java:21-64): the swing needs 2+ victims (24 `int bestN = 1`, 35 `n > bestN`).
- The mop score (40-47): enemy paint 10, enemy robot +15, near a ruin +40. An enemy robot on our paint scores 15, below a tile of ruin paint at 50, so we clean ruin paint before we drain the soldier standing next to it.
- `Mopper.turn` 16: stop once the goal is in r2 2.

**Rule:**
- (a) With no enemy robot in mop reach (r2 2), swing at a direction that hits one robot (`bestN = 0` in that case). A single drain (10 from them, +5 to us) stays first when one is available.
- (b) Score an enemy robot in reach above ruin paint: robot +55, so a soldier on a ruin's pattern always outranks a tile.

(a) is one line. (b) changes study 6 2.1's ordering.

**Expected size:** small. Their r1-100 swings come to about 6 a game at 1.2 victims, about 38 paint drained. The point is denial at contested ruins, where one drained soldier is a tower that is not built.

**Prior attempts:** none on the swing threshold or the score order. The near-ruin weight (40) was tried at 80 (y167 -38) and 20 (y168 -24). The defend radius (y207 -24) and reactive or early moppers (t109 -38, t130 -8) are a different lever. No tested change has made moppers more aggressive against robots.

**Candidates:**
- `m1`: (a) alone;
- `m2`: (a) + (b).

### 2.3 Early SRPs: they complete them before r100, we never do (low-medium; new, unmeasured mechanism)
**Evidence** (`t143`): their soldiers complete 0.25 SRPs per 100 soldier-turns in r1-100 of our losses, about **1.45 SRPs a game before r100**. In our wins it is 0.11, about 0.61 a game. Ours: 0 in every game, because `srpTurn` cannot start before r100 (Soldier.java:303 `SRP_ROUND = 100`, 336). From r101 the rates match (ours 0.57 / 0.40, theirs 0.53 / 0.37 per 100 soldier-turns in losses). The difference is the start round, not the habit.

**Mechanism not measured:** which teams do it, on which maps, and what their soldiers give up for it. Splitting `srp` rows by team and round over the cache answers that (not run).

**Code (t140):** Soldier.java:303 (`SRP_ROUND`), 336 (the gate: round, 1000 chips, 60 paint).

**Rule:** `SRP_ROUND` 100 -> 60, keeping the chip gate. The gate is what stops early SRPs from starving towers: an SRP starts only with 1000 chips banked, and the opening rarely has that.

**Expected size:** small. Each SRP is 25 coverage tiles plus chip income.

**Prior attempts:** none on the start round. y214 (SRPs from 4 towers, -85 vs y211) and y213 (5 towers, -3) changed the tower threshold that makes a soldier finish an SRP before a new ruin. That threshold is a different gate, but it warns that SRPs competing with ruins cost a lot.

**Candidate:** `s1`: `SRP_ROUND = 60`.

### 2.4 `Nav.tileCost` leaves out the ally term (low; bug)
**Evidence:**
- **The engine's end-of-turn rule** (replayed exactly in `t140`). Allies are own robots and towers within r2 2; m = 2 for moppers.
  - Own paint costs `allies`.
  - Neutral costs `1·m + allies`.
  - Enemy costs `2·m + 2·allies`.
- `Nav.tileCost` returns 0 / 1 / 2 and its comment calls that "the per-turn drain". It ignores the allies entirely, and for a mopper it scores enemy paint 2 where the engine takes 4.
- **Crowding:**
  - In r101-200 we pay 150 paint a loss to crowding beside our towers, they pay 78 (`t140`).
  - Walking soldier-turns with an ally adjacent: 18% ours, 14% theirs in r101-200 of losses (`t145`).
  - Most of the tower crowding is deliberate waiting (Unit.java:49-55), which Nav does not decide.

**Code (t140):** Nav.java:17-21 (`tileCost`), used at 51 (`nd + 6 * tileCost(n)`).

**Rule:** `tileCost(n)` = base (own 0, neutral 1, enemy 2) x (mopper ? 2 : 1) + (allies adjacent to n other than us) x (enemy ? 2 : 1). Count the allies from `G.allies`; there are at most 3 candidates.

**Expected size:** small; flat is the likely result.

**Prior attempts:** none.

**Candidate:** `n1`.

### 2.5 Lower priority (measured, but weak, or tried before)
- **Splashers refill seven times as often** (`t143`, losses; ours / theirs per 100 splasher-turns).
  - Withdrawals: 4.79 / 0.57 in r101-200 and 3.51 / 0.61 in r201+, at 42-57 paint each (theirs 98-108). Wins: 5.50 / 0.69 and 3.02 / 0.56.
  - Spending matches: our splashers splash 7.2 / 2.6 per 100 turns in r201+ of losses, at the same 10 tiles and 5.7-5.9 enemy tiles per splash.
  - They win on numbers instead: 3.4x our splasher-turns after r200 in losses.
  - Part of our count is `Unit.topUp` (Unit.java:67-78, RobotPlayer.java:19): it takes any amount from any adjacent tower whenever the action is unused. `t143` does not split top-ups from refill trips. The refill threshold is an exhausted dial (y50 150 -28, y162 75 -2, y234 80 -37) and so is the target choice (t148 -25, y291-y294 flat to -23). **Not a rule** without a split that shows the top-ups cost something.
- **Upgrade as a heal** (`t144`): rejected.
  - The top teams almost never upgrade under fire (15 of 251 upgrades).
  - Our towers die 11.7 a loss against their 6.1.
  - An upgrade was affordable in 24% of our final sieges, and +500 HP buys about 10 rounds.
  - sw22 (-30) tried it.
- **Silent soldier attacks** (`t140`): their soldiers spend 5 paint on enemy-paint or wall tiles without a paint row on 1.3-2.8% of turns, ours on at most 0.2%. Not decoded; too small to chase.
- **Disintegration** (`t143`): they disintegrate about 2 splashers and 0.5-1.3 moppers a game, presumably dry ones far from towers. We disintegrate only towers (the churn). Too small to chase.

## 3. What changed since study 11
- **The versions.**
  - t135 = t122 + study 10 2.6d: a soldier with no other soldier in view skips the 25-paint pattern mark. Local +9 ±22 in 262 fresh games.
  - t140 = t135 + study 11 2.1: free single marks on the 5x5 outer ring replace the pattern mark, and the marks are re-read beside the ruin. Local +40 ±23 in 251 fresh games.
- **Replica record.** t135 + t140 went 55-44 (56%), against study 11's t122 at 50-58. But t122 itself went 22-15 in this window, so the window's opponents were easier.
  - Against the seven top teams: t122 14-11, t135 25-22, t140 16-15.
  - The paired comparison (`t138`) finds nothing either way.
- **Free marks work as designed** (`t139`):

  | per game | t122 | t135 | t140 |
  |---|---|---|---|
  | pattern marks (25 paint) | 13.3 (332 paint) | 8.1 (203 paint) | 0 |
  | single marks / ruins with ring marks | 0 / 0 | 0 / 0 | 176.8 / 15.4 (never both types) |
  | re-colour rows on unbuilt ruins' 5x5 | 79.0 (395 paint) | 93.3 (466 paint) | 53.1 (266 paint) |
  | tiles re-coloured twice or more | 10.5 | 13.4 | 6.4 |
  | rounds from first paint to completion (median) | 117.5 | 105 | 118 |

  t140 spends about 400 paint a game less than t135 on marks and re-colouring. Its towers do not complete faster, and the saved paint is banked (2.1).
- **Losses end later:** median r436.5 (t140 alone r452; study 11 r410.5). Eliminations: 6 of 44 (study 11: 12 of 58). Famine is a little lower: 50.9% of loss rounds with every tower under 200 paint (58.8%).
- **The opponents' marks** (`t139` part C). Not a rule; this is the "they don't mark" story of study 10 seen per team.
  - subscribe-to-caterpillow and scienceqiu mark beside a ruin and unmark it at the build (100% and 99%).
  - gone-whalin never marks.
  - lobster-roll marks 555 times a game, mostly 3+ tiles from any ruin.

## 4. Broken in our bot (t140)
1. **`Nav.tileCost` leaves out the ally term** (Nav.java:17-21), and under-scores enemy paint for moppers (2.4).
2. **`Nav.last1` / `last2` are dead state:** declared at Nav.java:13, written at 100, never read. This is harmless as it stands: our A-B-A reversal rates are below theirs (`t141`: soldiers 1.1-2.5 per 100 moves, theirs 2.9-4.9).
3. **The paint weight in the greedy step (Nav.java:51) only works near the goal.** `nd + 6 * tileCost(n)` compares squared distances. For a goal on a diagonal, the side step loses 2d-1 in d², so beyond 3 tiles a fixed 6 can never pick a painted side tile; on an axis it loses only 1. That is why our explorers walk straight across neutral ground. Not a bug, but 2.1 is the cheaper fix.
4. **`Unit.topUp` takes any amount** (Unit.java:67-78, called every turn from RobotPlayer.java:19): a splasher at 290 of 300 takes 10.
   - Our soldiers' withdrawals under 10 paint run 1.05-1.85 per 100 turns, theirs 0.17-1.37 (`t143`).
   - Our splasher withdrawals average 42-57 paint, theirs 98-108.
   - Not shown to cost anything, and the refill dials are exhausted (2.5).
5. **The mopper's swing threshold and score order** (Mopper.java:24, 40-47) are design choices rather than bugs (2.2).

## 5. Suggested test order
1. `c1` (2.1, F = 150): one line, behind the biggest measured gap. If it leads or is flat, dial F with `c2` (100) and try `c3` (`paintNear` from r1).
2. `m1` (2.2 a): one line.
3. `s1` (2.3): one constant.
4. `n1` (2.4) and `m2` (2.2 a + b).

None of these touch the siege code; study 11's 2.2 stays closed.

**Not measured:**
- `t142_bytecode` is written but was not run.
- 2.3's per-team split was not run.
- Whether `topUp` trickles cost anything was not measured.

## Summary: the top three
1. **Opening cover (2.1).** Before r80 our walking soldiers end on unpainted ground 57-68% of the time, theirs 21-26%. They paint the tile underfoot on 11-27% of walking turns, we do on 1-3%. We pay 86.8 against 30.2 paint per 100 walking turns, trail 14.4 / 18.2% coverage at r75, and hold 180-440 more paint at r75-r100. Rule: `else if (G.paint >= 150) paintHere();` after the explore move before r80, Soldier.java:34-36 (`c1`). This reverses study 3 tactic 2, crowned on 2026-11-25 and never retested.
2. **Moppers that fight (2.2).** Theirs attack robots 14.7 times per 100 mopper-turns in r1-100, ours 4.7, and theirs swing at a single robot (1.2 victims a swing) while ours need two (Mopper.java:24). Rule: swing at one robot when none is in mop reach (`m1`), then score robots above ruin paint (`m2`, Mopper.java:40-47).
3. **Early SRPs (2.3).** They complete about 1.45 SRPs a game before r100 in our losses (0.61 in our wins); we cannot start one before r100 (Soldier.java:303, 336). Rule: `SRP_ROUND = 60` with the 1000-chip gate kept (`s1`). Mechanism unmeasured; y214 (-85) warns that SRPs competing with ruins are costly.

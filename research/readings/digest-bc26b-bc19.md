# Digest: what bc26b (2026 redo) and bc19 (2019) learned, for reuse in 2025b

Written 2026-11-25. Sources read: documentation only from the filtered reading room
`~/projects/vibe/reference/readroom-no2025/{bc26b,bc19}/` (LEARNINGS, TRAINING_ALGORITHM, HANDOFF, README, RULES,
PROMPTS, ACCESS, BENCHMARK, ECONOMICS, CLAUDE.md, docs/bc26a0-lessons.md, research/{prior,tourney,audit,audits,field,
champ-corr,diag26}, progress/{local-elo,local-to-replica,champ-corr}.md, tools/galaxy*/README.md, and bc19's
TRAINING_LOG sampled at start/middle/end plus greps). Source code (.py/.sh/.java/.js) read from
`~/projects/vibe/2026b` and `~/projects/vibe/2019`. No 2025 material was opened.

Note: bc26b's TRAINING_LOG.md is **not** in the filtered reading room (only bc19's is), so bc26b's day-by-day history
comes from HANDOFF.md's dated state blocks, PROMPTS.md, research/tourney/pool.txt comments and progress/*.md.

Final outcomes, for calibration:
- **bc19**: 13 champions (v0-v12) in ~7 days; 103 REJECTED entries in the log. Method = paired local screen (reject
  only) + replica panel (accept). Shut down 2026-10-27.
- **bc26b**: ~1,080 attempts 10-27..11-12 under a replica-panel gate, then from 11-21 a continuous local
  Bradley-Terry tournament: 31 champions in 4 days, 95,502 local games, replica rank #16 of 54 at shutdown
  (11-25). Local Elo rose ~400 points (xk6 1398 -> sw96 1795).

---------------------------------------------------------------------------------------------------------------------

## 1. Process lessons

### 1.1 The arc of method (the single most important lesson)

1. **bc19 method (paired gates).** Each candidate = incumbent + one config switch. Delivery check (does it fire?) ->
   local paired screen vs incumbent (rejects only, t <= -1.5) -> replica panel block against 6-8 field bots near our
   rating, 3 maps each, both sides, scored by the *paired fresh-cell rule* (below). Produced steady gains early
   (v3..v8 in 3 days) and then a slow plateau.
2. **bc26b phase 1 (same method).** ~1,080 attempts over 16 days, 15 accepts. Three late accepts (z3x, zdb, zj3)
   each passed at the bar's minimum (D=4, +4-0, t=2.00) with 90-92 of 96 cells alike; their BT ratings were
   indistinguishable (1615/1629/1621 +-40-80). Power analysis (bc26a0-lessons): a change flipping 5% of cells and
   winning 3/4 of them needs ~320 cells for E[t]=2, ~650 for 80% power; a 2-block panel is ~96 cells. Unless >28% of
   candidates are real gains, a D=4 accept is more likely noise. **The panel no longer resolved the changes it
   accepted**, and it cost hours of scarce ladder capacity per candidate.
3. **Local-vs-panel predictiveness was tested and failed** at the per-candidate level: "on twelve builds, no local
   metric did better than chance"; hand-built archetype opponents saturated (93-97% wins). Self-play wins that exploit
   the incumbent's own habits did not transfer (bc19 LEARNINGS 32: three candidates beat incumbent locally, lost on
   the replica).
4. **bc26b phase 2 (owner 11-21): continuous local tournament decides, ladder is only scoreboard + idea source.**
   12 champions in the first 22 h; 31 in 4 days; local Elo +400; replica rating rose (with dips), rank roughly held
   then improved to #16. Later study: across 10 champions, tournament rating vs replica win rate r = +0.65
   (p 0.036), i.e. *aggregate* local strength does transfer even though single-switch verdicts did not. Fit: one
   local Elo point ~= 0.5 replica point (SE 0.25-0.80).
5. **Why it worked**: abundant local compute (Windows box, 20 threads) vs scarce ladder; risky ideas cost a few hundred
   games; Bradley-Terry over *all* games pools evidence across opponents; no gate overhead; valleys accepted.

**Takeaway for 2025b:** build the foundation, then go straight to the continuous local BT tournament with ~50%
big swings. Use the replica for ideas, field-study statistics and a progress chart, never as a gate.

### 1.2 The bc26b local tournament: exact setup to replicate

Files (repo-relative):
- `tools/tourney.py` (308 lines, stdlib + `tools/elolib.py`; matplotlib only for `chart`).
- `research/tourney/pool.txt`: one active bot per line, trailing `# comment` allowed. Retired bots are lines
  starting `# NAME  (reason...)`; the parser takes the **second word of every `#` line** as a retired name, so no
  other comment lines may live there. Retired bots are not scheduled or listed but **their games still count** in the
  fit (anchors).
- `research/tourney/champion.txt`: current champion name. `research/tourney/champions.csv`:
  `when_pdt,bot,base,change,submission` history (chart appends a row stamped with champion.txt's mtime if missing).
- `research/tourney/README.md`: naming rules and the swing table (swing, strategy, base, fate).
- `research/tourney/prod-prompt.txt`: the text of the periodic "prod" that drives each cycle (see 1.2.6).
- `runs/trNNN/cells.tsv` (plan output), `runs/trNNN/results.jsonl` (arena output), `runs/trNNN/DONE`.
- `tools/galaxy26/maps-early21.txt`: the map list the tournament samples from (owner restricted to the 21 maps
  available early in the season, mimicking a contest where few maps are public before sprints).

#### 1.2.1 Commands
```
python3 tools/tourney.py rank [--runs-root DIR]   # ladder: rating +- SE, games, W-L, lead vs champion, lead needed,
                                                  # games still needed; prints "NEW CHAMPION X (was Y)" when due
python3 tools/tourney.py plan trNNN --games 120   # writes runs/trNNN/cells.tsv (a<TAB>b<TAB>map<TAB>seed)
python3 tools/tourney.py add BOT                  # append BOT to pool.txt
python3 tools/tourney.py chart                    # progress/local-elo.png + local-elo.md (wall-clock axis)
bash tools/box.sh queue trNNN                     # ship cells + the bots they name to the box, append to its queue
bash tools/box.sh start [JOBS]                    # start the box's screen queue worker (default 6 games at once)
bash tools/box.sh status | pull trNNN | sh CMD | send PATH...
bash tools/prod.sh                                # idle check: box queue, running, finished-unpulled, VM disk; VERDICT IDLE/BUSY
python3 tools/snapvar.py NAME 'OLD=>NEW' ...      # new candidate = champion's Cfg.java with exact text edits, frozen
bash tools/unit-tests.sh [BOT]                    # bot unit tests (fake RobotController) + tool tests
bash tools/charts-refresh.sh                      # redraw local-elo / rating-history / ladder-position, commit+push
```

#### 1.2.2 Which games count (`games()`)
Every `runs/*/results.jsonl` row (not only `tr*` runs: earlier screens seed the ladder) where both bots are in the
pool or retired, a != b, the map is in the tournament map set, and winner is A or B. Any seat, any seed. Result is
a plain win/loss tuple.

#### 1.2.3 Rating (`tools/elolib.py`, stdlib only, 141 lines; reusable as is)
- Bradley-Terry by Hunter (2004) MM iteration, P(i beats j) = r_i/(r_i+r_j).
- Weak prior: every player gets 1 virtual win + 1 virtual loss vs an anchor of strength 1 (keeps 0-N players finite).
- **Per-pair cap PAIR_CAP = 200 games** (scaled keeping the win share) so one heavily repeated pairing can't dominate.
- Ratings = 400*log10(r), shifted to mean 1500. SE from the diagonal of the information matrix (slightly optimistic).
- Optional handicap key per game (Hunter home-advantage model, e.g. per map) via `fit_h`. Unplayed pool bots get
  1500 +- 400.
- Only compare ratings within one fit; the whole history is refit each time (earlier champions shown at current
  rating).

#### 1.2.4 Champion rule (`cmd_rank`)
- Eligible = bots with >= MIN_GAMES = 200 games. The top eligible bot becomes champion when its rating exceeds the
  champion's by more than one **combined SE** sqrt(SE1^2 + SE2^2) (hysteresis against title-trading on noise).
- Observed: a freshly crowned champion's rating settles downward (winner's curse): sw83 1784 +- 23 at 233 games ->
  1743 +- 16 at 479 games; sw58 crowned +26 over sw54, later below it. bc26b waited "~400 games after crowning"
  before retiring bots against a new champion, and **reinstated** bots retired against an inflated champion.
  Early ratings swing hard (forward hold +70 at 25 games, -43 at 63, +17 at 284; king finisher -190 at 12 games,
  +22 at 177): never judge before ~50 games.

#### 1.2.5 Scheduling (`cmd_plan`)
Constants: `MIN_GAMES, NEW_MIN, TOP, SEEDS = 200, 40, 20, 10`.
- `have[b]` = games played + games already planned in unfinished `runs/tr*/cells.tsv` (fractional by progress), so
  consecutive plans don't each give a newcomer its full NEW_MIN (bug seen: one bot got 60 games in each of 5 plans).
- `top` = pool bots with have >= NEW_MIN, best first, up to TOP. (TOP was 6 -> 10 -> 20: with a ~10-11 bot pool, the
  lowest-rated rated bot fell out of the top and got **no games ever**, so it could never reach MIN_GAMES.)
- Newcomers (have < NEW_MIN) get half the run (5/6 if fewer than 3 rated bots), sampled weighted by
  max(NEW_MIN - have, NEW_MIN/4); each game is vs the champion with prob 0.5, else a random top bot.
- The rest: pairs among `top`, weight = (se_a + se_b + 10) * exp(-|r_a - r_b| / 100), where se is capped at
  350/sqrt(have) so an unplayed bot's 400 prior SE doesn't hog several consecutive plans.
- Each game: seats randomized, random map from the set, random map seed in 0..SEEDS-1. Run size 120 games.
- Re-plan queued runs whenever the pool changes; take a run off the queue before replacing it.

#### 1.2.6 The game machine: `tools/box.sh` + `tools/screenq.sh` + `tools/arena.py`
- Box = owner's Windows PC, WSL2 Ubuntu, i7-13700HX 20 threads, WSL memory capped at 8 GB (20 GB thrashed), reached
  via Tailscale ssh (`ssh -i ~/.ssh/wsl_box terry@100.93.26.126`, only from the laptop). Checkout at
  `~/projects/vibe/b26b` with engine jar + `~/opt/jdk21`. ~2.7x faster per game than the e2-standard-8 VM. Game JVMs
  1.0-1.4 GB RSS at -Xmx1200m, so 5-6 concurrent games.
- `box.sh queue RUN`: tar-pipes `runs/RUN` and every `bots/X` the cells name over ssh, then appends RUN to the box's
  `runs/screenq.txt`. `pull RUN` tars `runs/RUN` back (results.jsonl, log, DONE). `start` removes
  `build/screenq.stop` and launches `tools/screenq.sh JOBS` with `setsid nohup` (BC_SLOTS, BC_JDK set).
- `screenq.sh JOBS`: loop until `build/screenq.stop` exists; under `flock runs/screenq.lock` pop the first line of
  `runs/screenq.txt`; skip if no cells or already DONE; run
  `nice python3 -I tools/arena.py matrix runs/R/cells.tsv --run runs/R --jobs JOBS`; touch DONE; log start/end to
  `runs/screenq.log` (UTC). `runs/R/KEEP` keeps replays. Multiple workers can share the queue safely.
- `arena.py matrix`: compiles each bot source dir into an immutable content-hashed class tree
  `build/bots/<pkg>-<hash12>/` (atomic rename; never recompiled while in use), skips cells already in results.jsonl
  (keyed by `a_hash|b_hash|map|seed`: resumable), runs each game as its own JVM under `unshare -rn` (no network),
  `timeout` wall cap (BC_GAME_TIMEOUT 1800 s), -Xmx (BC_XMX 1g), SerialGC, holding a **machine-wide flock slot**
  (`$BC_SLOTS_DIR/slot<i>`, i < BC_SLOTS) shared by every tool that starts games. Parses winner/round/reason from the
  engine's stdout, summarizes the replay with the Java `ReplayDump` tool into one JSON row (winType, per-side
  counters, bytecode overruns, exceptions...), deletes the replay unless KEEP.
- Throughput achieved: ~95k games in ~4 days (~24k/day) at 6 slots on the box.

#### 1.2.7 Pool management and naming
- ~10 bots: champion + ~9 newcomers, **half incremental, half big swings** (owner 11-22).
- Names: `yNN`/`ylNN` = incremental (one constant/branch on the champion, usually via snapvar); `swNN` = swing (a
  coherent strategy: bundle of constants or new mechanism). Earlier eras used other letter prefixes (x*, z*, s*...).
  Keep a swing table (strategy, base, fate).
- Every newcomer is built **on the current champion** (one cause per rating difference).
- Retire: far below champion after 200+ games; or > ~2 combined SE below with 50+ games (later practice:
  "> 2 combined SE below the champion after 200+ games", logged with the numbers in the pool comment). A failing
  swing gets a v2 that fixes its first visible failure before the strategy is dropped; try the opposite of a twice-
  failed all-in style.
- Combine swings that each hold level with the champion; do not bundle neutral tunings (combinations read negative).
- Owner rule: no quality pre-gate on newcomers; an 8-game smoke vs champion is allowed only to catch crashes and
  bytecode overruns.
- "Imitation"/sparring bots (copy a tactic the field beats us with) were first exempt from retirement, then treated as
  normal swings: if the imitation wins the tournament (sw53 did), every later bot inherits the tactic. Caveat from
  research/field/sparring-gap: imitations built as "our code with 1-4 knobs changed" copy a number, not a behaviour;
  check in replays that the imitation actually behaves like the field team.

#### 1.2.8 Crowning and the new-champion audit (same cycle)
On NEW CHAMPION X: submit X to the ladder (`contest.py submit bots/X`), write champion.txt, append champions.csv,
copy X to the dev bot (package renamed), log + mark accepted in attempts, refresh progress charts, commit + push.
Then audit **only X's diff from the previous champion** (owner: full re-read each crowning was overkill): logic
slips, mirror/symmetry slips, latent special values (0, negative, out-of-range constants), dead/misleading code.
Move `test/X/*.java` into `test/ratbot/`; whole suite must pass; add a test per new mechanism/constant (tests look
up constants by name at run time so older pool bots skip them). **Fixes enter as newcomers, never patched into the
champion** (a long-lived bug can be load-bearing). First big audit: 9 bugs + 6 mirror slips + 19 latent values; the
fix bundle rated **118 below** the champion it fixed, and no split part won head to head. Report in
`research/audit/DATE-X.md`.

#### 1.2.9 The prod cycle (~every 20 min, driven by a cron/loop prompt)
1. `bash tools/prod.sh` (idle verdict). 2. Pull finished/partial runs, `tourney.py rank`. 3. Crown if due.
4. Keep >= 3-5 runs queued past the next cycle. 5. Audit a new champion. 6. Retire / add to keep ~10 bots.
7. Check the champion's new ladder matches for ideas. 8. Log, commit, push. 9. `charts-refresh.sh`; check replica disk.
10. Report: tournament size (games, games since last cycle, active/retired/entered), **one** table of the whole pool
sorted by rating (kind, base, change, rating +- SE, games, lead vs champion, lead needed, games still needed),
retirements/additions with reasons, audit outcome, ladder rank/rating/time, disk and machine state. All times PDT.
The owner rejected terse prods and idle periods ("You just wasted two hours"; "not acceptable to sit idle 7 hours").

### 1.3 Statistics lessons (both years)

- **Determinism**: engines are deterministic per (pair, map, seed, seats); our bots too. A switch that never fires
  replays its parent's games byte-for-byte, locally and on the replica. Use this: identical end rounds = the change
  never fired (bc26b L19); a single flipped cell after a change may be chaos (early divergence re-rolls everything).
- **Paired cell is the unit of evidence** (opponent, map, side, seed): only discordant pairs inform;
  t = net / sqrt(D) (or sum d / sqrt(sum d^2) for graded d). Size reads by D, not by games.
- **Repeated cells are not new evidence** (bc19 L50): lopsided cells give one result every block, so pooled z over
  repeated blocks grows like sqrt(blocks); simulated false-accept 17-30% vs the 7% assumed. Each block on fresh cells.
- **Winner's curse**: blocks that accept overstate the candidate; a new champion plays its own control block before
  candidates are scored against it (bc19 L33). Same phenomenon in the tournament (1.2.4).
- **Simulate every gate** before trusting it (bc19 `tools/gatesim.js`, `tools/galaxy19/panelsim.py`): the old
  20-cell gate had 10-22% power for a real 65% effect; the paired fresh-cell rule: false accept 5-6%, power 13-65%
  depending on share of cells changed.
- **Map-conditional switches** need a targeted panel (bc19 L39): diluted otherwise.
- **Never read a running block; never move a bar after seeing a number; agents get finished matches only.**
- **Ladder ratings** (siarnaq's) are zero-sum with mean pinned; above-median teams drift up as the season spreads,
  so judge progress by rank or by the gap to reference places (#5, #10, #15, #20), not raw rating. siarnaq rating is
  on a different scale than BT (bc19 L46: 0.12 replica point per BT point after few dozen matches).
- **Graded objective** carries more information than win/loss (round-margin score raised paired t ~14%:
  score = 0.5 + 0.5((1-a)o + a*o*m), m = 1 - 0.5*rounds/maxRounds for early decisions).
- **Self-play peace blindness** (bc26b L12): when neither side of a self-play game goes to war, any war-only switch
  plays identical games (80/80). Need instruments that reach the regime (rush archetypes, imitations, replica).
- **Two-sided optima** for sizes/thresholds (rush size 8 and 16 both lost to 12; bank threshold 500 and 1500 both
  lost to 1000): a constant that should probably be a function of state (map size, bank).
- **Diagnose losses a candidate can flip**: in-band opponents (25-75% win rate). The owner explicitly flagged wasted
  effort on a bot far above us (bc26b L16, PROMPTS 19-20, and again later).
- **RL/ES tuning of a hand bot found nothing** (bc26a0: PPO 39 iters ~5k games flat; ES on 168 decision biases
  0.41-0.46 vs start; split-half gradient cosines 0.03-0.10). A tuned bot is a sharp local peak; gains come from new
  behaviour or bundles of audited fixes (16 fixes each ~0.8 pt, together +12.5 pts, 40/64).
- **Action-level cloning** of another bot fails (1/32 vs its source); decision-point imitation works only with
  internal access. Hand-built archetypes from replay evidence are the right form.

### 1.4 Using the ladder replica like a contestant

- Only the champion plays ranked; field bots play **only** on the replica, within its hourly request limits
  (20 ranked + 40 unranked/h), for realism (owner rules PROMPTS 8, 35). Local games = our builds, archetypes and
  the stock example player only.
- Request queue: `contest.py scrim ... --queue research/panel/queue.tsv` stores requests the 429 limit refuses,
  tagged with the active build; `drain-loop.sh` runs `contest.py drain` every 5 min, sending only rows of the active
  build, and bumps our matches ahead of field-vs-field autoscrim traffic (`spool_bump.py --team`).
- A galaxy match plays the submission active **at match creation**: submit candidate, create its matches, resubmit
  champion (`tools/interleave.sh` automated this between two builds).
- Panel calibration: pick opponents we beat 25-75% (`tools/panel_pick.py`); recalibrate when it saturates. Owner
  later preferred "the three bots immediately above us", ~40 matches per build.
- Replica games proved deterministic too (one seed per map), so a panel cell repeats unless the build diverges
  (`tools/divergence.py` predicts which panel matches would repeat from local divergence, so they can be skipped).
- Field studies: delegate statistics over 100+ replays comparing behaviour rates in our wins vs losses (e.g.
  sparring-gap: the teams beating us held our half from r200 with 25-28% forward rat-turns vs our 6-8%, 2-3x our
  trap rate, and bit our king 5-23x per window). These designed the successful swings (sw53 raiders + forward traps).
- **Learn the opponent's winning tactic yourself first** (owner): adopt it (it should win locally), then the whole
  lineage inherits it and you can build defences against your own copy.

### 1.5 Instruments and diagnosis lessons

- **Replay dumper first, thorough, and verified against the engine** (owner BEST_PRACTICES #1; bc26b L11: RatNap
  counted both grab and landing, hiding a 3x grab deficit). Fixture tests pin it.
- **Bytecode tag smuggling**: replays drop indicator strings but keep per-turn bytecode counts, so pad each turn so
  bytecodeNum mod 128 = 7-bit decision code (5 bits why-code, 1 bit role, 1 parity bit). `smuggle.py` decodes and
  detects tagged teams by parity pass-rate; TAG_K calibrated (0 misses in 14,954 turns). Also used in 2023.
- **Bytecode ledger** (`tools/ledger.py`): new code that costs even a few bytecodes a turn shifts budget-dependent
  decisions and re-rolls the game. Track debt so budget reads see the base's counts; then a never-acting candidate
  replays the base exactly (proof the change is inert until it acts). Static fields of new code must have no
  initializers. Lesson: "unledgered per-turn code re-rolls the fragile cells."
- **Behaviour-exact refactors**: `tools/bcsame.py` (javap -c per method, normalised) proves a cleanup compiles to the
  same bytecode; bc26a0 removed 43% dead code (10.4k -> 5.9k lines) with 60/60 identical games.
- **Prove delivery before value** (bc19 L19, L41, L52, L55): one game + `diff` vs base replay on the same cell; count
  where the trigger fires and check those are the situations the idea names; if it never fires, build a partner bot
  that creates the case. Read switch values back from the built artifact; tools must refuse unknown arguments (L28).
- **Price a waste before fixing it** (bc19 L48): a counted waste that doesn't decide games is not worth a candidate.
- **Replays show positions, not intent**: log the bot's state to name a cause (bc19 L24).
- **grep the log/attempts for a cell or switch before re-diagnosing** (bc19 L53; `attempts.py find TERM`).
- Win-probability model on replay aggregates (per 10-round bin, folds by game) to locate where losses turn; never as
  an acceptance score.

### 1.6 Infrastructure mistakes to avoid (all actually happened)

- `pgrep -f`/`pkill -f` match their own shell/ssh command line: waiters loop forever, kills kill themselves. Bracket a
  character (`[u]nit-tests.sh`), wait on PIDs or files, or send scripts on stdin.
- Never edit a running script. Never SIGSTOP a background job (wrapper exited early, half a census read as complete).
- Several agents share one git index: `git commit -m ... -- <paths>`; stage explicit paths only.
- Time stamps from `date` (PDT; owner is in British Columbia), never estimated: log headings drifted up to 4 h.
- Driver (2 GB e2-small) can't host a full game; OOM reaps every background shell. One heavy job at a time. Never time
  anything on a shared/burstable machine.
- Never oversubscribe the game machine: keep concurrent games <= cores; load causes init/timeouts that turn games into
  noise (bc19: 1085 init failures in 14 games at 8-way).
- **Disk**: a full VM disk silently took the replica down (HTTP 500s, Postgres stopped) twice per project. Check
  `df` every cycle, keep >= 2 GB, hourly cron pruning replays older than a day when < 4 GB free.
- **/dev/shm is volatile**: logind RemoveIPC=yes wiped 12 GB of uid's /dev/shm when the last process exited. Keep
  anything valuable under ~ and in the repo.
- A replica deploy ships every tool change since the last; test one game under the unit's own systemd sandbox
  properties before restarting saturn (bc19 L21: netlink forbidden -> 218 nacks in 10 s).
- Bulk DB `.update()` skips siarnaq's rating triggers -> stalled rating chains, frozen graphs for a day. Use the app's
  methods or run `rating_unstick.py` after.
- Behind a basic-auth gate, never let a 401 reach the browser (Chrome drops the cached gate login).
- Hand-edited CSV ledgers break (unquoted commas); edit through the tool (`attempts.py set`).
- Waiting inside a turn for a job is idle time; never stop to ask permission to try an idea (owner, repeatedly).

### 1.7 Records and owner conventions (keep in 2025b)
- PROMPTS.md: every owner prompt verbatim, timestamped PDT from the clock; `/loop` prompts not recorded.
- TRAINING_LOG.md append-only; LEARNINGS.md each lesson with its measurement; HANDOFF.md current state + how to run;
  attempts table (`progress/attempts.csv` -> ATTEMPTS.md via `attempts.py`); champion history; pool + swing table;
  audit reports; milestones (`tools/milestones.py add LABEL`) drawn on every time-axis chart.
- Charts on wall-clock axes: local-elo.png (champions + candidates), rating-history.png (our replica rating and the
  #5/#10/#15/#20 references, plus a panel of our rating minus theirs), ladder-position.png.
- Push after every commit. Clean-room readroom filtering of prior-year docs (`tools/readroom/build_readroom.py` +
  `filterYYYY.py`; exclude whole files whose year-span ends in the forbidden year).

---------------------------------------------------------------------------------------------------------------------

## 2. Strategy and tactics lessons that transfer across years

### 2.1 Foundation / basics (both years agree)
- **Rules digest from engine source, every fact cited to file:line**, with a section of spec-vs-engine
  disagreements, the in-round execution order, cost charging order, free/leaked information, and a table of how
  starter-vs-starter games end. Execution-order facts decided real bugs both years (bc26b L1: kings act before the
  units they spawn this round, so read last round's messages too; bc19 L23: a newborn acts after everyone already in
  the round, so its builder can die before it hears anything).
- **Mirror the engine's bookkeeping** (bc19 L6, L45): charge every action's cost in the local world model at call
  time; otherwise later affordability checks throw.
- **Map corpus** with census (size, symmetry, spawn geometry, resources, distances); invariants are constants.
- **Basics battery** with absolute bars: no idle producer, no stuck unit, no unforced death, 0 overruns, 0 exceptions,
  mirror self-play even from both sides.
- Bot architecture: turn loop, globals, **one constants file where every behaviour is a named switch defaulting to
  the incumbent** (`Cfg.java`), comms schema, map memory, nav, one handler per role, compute monitor (overrun count,
  stage marks, hottest stage, max bytecodes, exception type@stage) in the indicator string from commit 1.
- Lazy state built in locals and committed in one assignment; setup re-runs until a "done" flag set last (a killed
  turn keeps half-written state: bc19 L10).

### 2.2 Symmetry
- Build side symmetry in, don't test it in (bc19 L5): canonical frame (each robot sees its own side "on top"),
  tie-breaks from own geometry, never compass order / ID / team / sensed-list order; per-robot RNG seeded from
  mirror-invariant facts (birth round), not shared streams. Tools: bc19 `symcheck.js` (simultaneous stepper),
  bc26b `mirror_check.py` (compare side-swapped games through the map's symmetry).
- Keep a symmetry candidate bitmask (ROT/H/V), never empty; eliminate from walls/resources/initial features and engine
  give-aways; act on all live candidates; "guessing what can be known is a bug". Owner rule: assume maps are fully
  symmetric in every aspect (resources too) — exploit mirrored resource locations.
- Engine give-aways exist: bc26b found the sensing-list order depended on a per-team "chirality", revealing symmetry
  at round 1 for one side (rejected because it made play side-dependent; owner later allowed breaking symmetry for
  advantage: PROMPTS 21). Look for such leaks in each year's engine.
- Resources on the symmetry axis are equidistant: strict `<` comparisons drop them from both sides (MINE_TIES).

### 2.3 Economy
- **Repairs and cap removals transfer to the field; reallocations and constant tuning mostly don't** (every season).
- Spend idle resources: banks that float are wasted (bc19: bank 335 vs field's 92 at r100; bc26b: points losses ended
  with thousands banked). bc26b's champion line gained by "spending the bank on bodies" (sw54) and by a low spawn
  floor when the army is small (LOW_FLOOR 200 -> 50 -> 20 each gained).
- **A reserve must not gate the units that are the income or the defence**: reserve gates produced death spirals
  (4 babies on a 1300 bank for 360 rounds then starvation). Prefer a live unit-count target (replace losses
  immediately) over bank gates; reserve only for upkeep.
- Price swings before building: bigger armies starved in 45/83 losses of one blitz.
- Land/claim speed beats per-worker productivity (bc19 ECONOMICS: productivity at par, quantity and first-expansion
  timing were the gap). Compare the opening event stream (first spawn, first mine, first delivery, first expansion)
  with the top opponents'.
- Delivery geometry details matter (bc26b L18: carriers waiting one tile out of transfer reach across a wall).
- Raid/strip the enemy's economy (raiders holding enemy-half resources at war were a crowned swing in bc26b).
- Endgame scripting against the tiebreak (bc19 health-at-round-limit preacher dump; bc26b third king before a late
  round cut, cat-damage endgame) — count losses decided on tiebreaks first.

### 2.4 Navigation and exploration
- Greedy + bug with measured stuck condition, per-robot handedness from own geometry; **stall counter must survive
  retargeting** (biggest one-line gain of 2020 per bc26b's prior digest); never target the unreachable; dig/clear
  obstacles when the detour is long.
- Facing/turning costs (if the year has them) make facing part of navigation; units that always face their step
  expose their back (bc26b L11).
- A step capped below unit speed needs a field counted in such steps (bc19 L12: 24 tiles took 36 turns).
- Out-of-sight tiles are unknown, not free (bc19 L15); remember tiles seen taken.
- A unit parked by "best free tile" refills the tile its predecessor died on — park by a rule the enemy can't reach
  (bc19 L51: 49 of 56 deaths on one tile).
- Sticky targets beat nearest-recomputed; random far exploration target re-picked on arrival is a strong default.

### 2.5 Combat
- **Strong bots rush early and target the HQ/king**; combat and HQ defence come before economy refinements (bc26b L7:
  0-80 vs the top 5 before that). Find out how the strongest opponent actually wins before tuning anything (bc19 L22:
  StoneT2000's same-round church chains to our castles).
- Traps/area denial were the main rat-death gap (bc26b L8, L15); marking enemy front tiles cut trap hits 41-46 -> 19.
- Flee/avoid rules must check moves, not positions (bc19 L16: a unit that steps into range dies before fleeing).
- Holding a ring doesn't fight: fighters spent 359/420 engaged turns idle (bc26b L10). Measure idle-in-contact.
- Many small combat micro wins in bc26b's last day: hunt the weakest weaker enemy, bite-before-bail when bytecode runs
  out, standoff only vs healthier enemies, wounded units no longer walk home (RETREAT_HP 0).
- Spawn placement: newborns placed where visible attackers can't kill them before their first turn (bc19 DEF_SAFE).

### 2.6 Communication
- One writer and one purpose per slot, round stamps, staleness rule, unit-tested pack/unpack. Stamps modulo N alias
  after N rounds (bc26b audit S1: round & 1023 resurrected dead kings after 1024 rounds).
- Two periodic senders on one channel can silence one forever (bc19 L36). Check schedules against each other.
- Extra-bit channels: signal radius/metadata can authenticate a message for free (bc19 L4).
- A full fixed-size list must not make "report unlisted item" fire every turn (bc26b audit S5).

### 2.7 Bytecode / compute
- Compute monitor from commit 1; any overrun is a real defect; worst turn <= 90% of limit. First-turn allocation
  spikes are common; `java.util` is metered; allocate big arrays lazily and only when enough budget remains.
- Overruns judged against the field's rate in the same games, not wall-clock (bc19 L31).
- Telemetry must not change behaviour (bc26b audit S4: indicator/tag cost placed before a budget-gated allocation
  changed play).
- Budget-dependent code (spend-what's-left loops) makes every bytecode change a behaviour change -> ledger (1.5).

---------------------------------------------------------------------------------------------------------------------

## 3. Reusable code/tools catalogue

Year-specificity: **G** = generic, copy as is; **L** = light edits (paths, jar name, map extension, names);
**H** = heavy (game-specific content). Paths under `~/projects/vibe/2026b` unless noted.

| path | what it does | spec. | port effort |
|---|---|---|---|
| `tools/elolib.py` | Bradley-Terry MM fit, weak prior, pair cap, SE, optional per-key handicap, expected score | G | none |
| `tools/tourney.py` | local tournament: pool, rank + champion rule, planner, add, wall-clock chart + table | L | maps file path, PDT zone, `tr*` prefix; ~10 min |
| `tools/box.sh` | ship runs+bots to remote worker over ssh, queue, pull, start, status | L | host/key/checkout path |
| `tools/screenq.sh` | flock-based FIFO run queue worker with stop file, KEEP, log | G | none |
| `tools/prod.sh` | idle check: box queue/running/unpulled, drain backlog, VM disk; IDLE/BUSY verdict | L | hosts |
| `tools/arena.py` | headless Java runner: content-hashed compile, no-net, wall cap, global flock slots, resumable matrix, one JSON row per game via ReplayDump | L-H | engine jar name, engine `-Dbc.*` properties, stdout regex, map extension/reseed, summary keys; MapReseed was 2026-specific (maps carried a seed) |
| `tools/cells.py` | generate cells.tsv for a pair over maps/seeds/both seats | G | map ext |
| `tools/snapshot.sh` | freeze bots/ratbot as bots/NAME (package rename, SNAPSHOT with hash/commit/time, compile check) | L | jar name, pkg |
| `tools/snapvar.py` | candidate = champion Cfg.java + exact-once `'old=>new'` edits (+ presets), frozen via snapshot | G | Cfg path |
| `tools/bundle.sh` | merge several candidates' diffs onto a base | L | |
| `tools/unit-tests.sh` | compile bot (+renamed pool bot) with test/ratbot/*.java + test/BOT overrides; run *Test mains; then tool tests | L | jar, pkg |
| `test/ratbot/BotTest.java` | fake RobotController via `java.lang.reflect.Proxy` over a tiny world model (walls, units, cooldowns, shared array, messages); `check()`/exit code | H (pattern G) | rewrite the switch-case for the year's API; pattern is ~150 lines |
| `tools/test_tools.py`, `tools/tests/test_*.py` | synthetic-input tests for tools | L | |
| `bots/ratbot/Debug.java` | indicator telemetry, stage marks (overrun stage, hottest stage), exception type@stage, **bytecode-count tag** (`tag()` pad via fall-through switch, TAG_K calibration) | L | swap why-alphabets; recalibrate TAG_K per engine |
| `tools/smuggle.py` | decode the bytecode tag from replays; detect tagged teams | L-H | depends on replay dump format |
| `tools/ledger.py` | bytecode debt ledger so new inert code replays base exactly | H (idea G) | rewrite per bot |
| `tools/bcsame.py` | prove refactor compiles to identical per-method bytecode (javap) | G | none |
| `tools/divergence.py` | per-map share of cells where a candidate's outcome fingerprint differs from the champion's | G | field names |
| `tools/mirror_check.py` | side-swap symmetry check of two games through the map symmetry | H | needs dump format |
| `tools/java/bc26tools/ReplayDump.java` (1071 lines) | flatbuffer replay -> summary JSON / per-round, per-turn, per-action TSVs | H | rewrite for the year's schema; keep interface (summary mode exits 1 on parse failure) |
| `tools/java/bc26tools/MapCensus.java` | map features table, ASCII render | H | |
| `tools/build-tools.sh` | atomic, lock-protected, stamp-based rebuild of Java tools into build/tools symlink | G | jar name |
| `tools/game_report.py`, `battle_report.py`, `econ_report.py`, `king_report.py`, `stuck_report.py` | replay analyses (basics, combat, economy, HQ, stuck units) | H | rewrite on new dump; keep the report set |
| `tools/rows.py` | compact table of results.jsonl rows | L | |
| `tools/score.py` | cell score (win/loss when HQ decides, else points share) | H | |
| `tools/gauntlet.py`, `screen_t.py`, `score_screen.sh`, `abort_watch.py` | paired screens: t on per-cell d, sign test, early abort when gate unreachable | L | |
| `tools/elo.py`, `games.py`, `plot_progress.py`, `progress-refresh.sh`, `charts-refresh.sh` | all-games CSV, BT over local+replica, bc23-style progress.png, refresh+commit | L | paths, team names |
| `tools/replica_report.py` | ladder.md/png, rating-history.png with #5/#10/#15/#20 references, ladder-position.png, via galaxy public API | L | episode name |
| `tools/attempts.py` | attempts ledger: init/set/render/find (refuses malformed CSV) | G | |
| `tools/milestones.py` | milestone CSV -> chart lines and replica /milestones.json | G | |
| `tools/panel_pick.py`, `e21pair.py`, `interleave.sh`, `cellrate.py`, `pred/*` | panel selection, interleaved champion/challenger panels, local->panel predictor studies | L | |
| `tools/vm.sh` | gcloud VM ensure/start, gssh, atomic rsync sync per dir, games in flight | L | VM/zone/project |
| `tools/get-engine.sh` | checksum-pinned engine download (only contact with battlecode.org) | L | URL/version |
| `tools/readroom/build_readroom.py`, `filter2026.py` | build filtered reading room excluding a year | L | year |
| `research/diag26/*` | replica-loss census scripts (loss cause, starvation, flips) | H | ideas only |
| `tools/galaxy26/*` | full private ladder replica (section 4) | L-H | section 4 |
| bc19 `tools/gatesim.js`, `tools/galaxy19/panelsim.py` | Monte Carlo of gate/panel false-accept and power | G | none (JS/Py) |
| bc19 `tools/symcheck.js` | simultaneous-stepper exact mirror check | H (idea G) | |
| bc19 `tools/replay.js diverge [--board]` | first differing action between two replays of a cell | H (idea G) | |
| bc19 `tools/jobq.sh`, `move_stale.sh` | sequential VM job queue with superseded dir | G | |
| bc19 `tools/bench/*` (discover.py, fetch.sh, classify.py, roster.py, scan.py, compile_field.py, smoke.sh, report.py) | field-bot discovery on GitHub/GitLab (code search for year-only API names, date windows, forks), sparse fetch, dedupe by sha256, risky-pattern security scan, compile, smoke, roster | L | swap the year-only API names and file patterns; bc26b's equivalent lived outside the repo (`~/projects/vibe/bc26b-benchmarks`, `research/field/FIELD.tsv`) |
| bc19 `tools/progress/*` | earlier version of elo/games/attempts/ladder/rating_history | G | superseded by bc26b's |

Must-port first (day 1): elolib, tourney, screenq, box.sh, arena (adapted), cells, snapshot, snapvar, unit-tests +
fake-RC pattern, build-tools, Debug (monitor + tag), attempts, milestones, vm.sh, get-engine. Then ReplayDump +
reports, smuggle, mirror_check, progress/charts. Then the replica.

---------------------------------------------------------------------------------------------------------------------

## 4. The galaxy replica (tools/galaxy26; lineage galaxy23 -> galaxy19 -> galaxy26)

### 4.1 What it is
A private copy of the official judging site on the VM `battlecode-dev` (us-west1-b, e2-standard-8, 8 vCPU / 31 GB /
20 GB disk): galaxy's **siarnaq** backend (Django, run unmodified) + galaxy's React frontend (patched), plus our own
**saturn.py** stand-in for the game runner. Pinned galaxy commit `f343088f4d471b0664b2ff41129f0435a8dca1c2`
(MIT), the same commit used by the 2023, 2019 and 2026 replicas — it is episode-agnostic; the episode is created by
`bootstrap.py`. Viewer = the official web client of that year, built from a pinned commit.

### 4.2 Components (tools/galaxy26, ~6.6k lines)
- `saturn.py` (749): leases compile/execute messages from local Pub/Sub spool dirs; compile = unzip (zip-slip check,
  64 MiB) -> `javac --release 21 -proc:none` against engine jar -> engine's `battlecode.instrumenter.Verifier` -> upload
  class tree; execute = run engine per map with official properties (indicators off, validate-maps on), parse winner
  with saturn's regex, score = games won; reports via relay's unix socket. User-code failures report OK with
  accepted=false; infra failures retry.
  - **Deviation: one engine run per map**, finished games kept in `saturn/resume/<key>` until ack (a crash/restart
    resumes from the first unfinished game). Alternate-order games play a pre-reversed copy of the map
    (`java/Bc26Tool reverse-maps` using the engine's own `GameMapIO.loadMap(..., teamsReversed=true)`); verified
    game-for-game equal to native multi-map runs. `replay_merge.py` merges per-game replays into one match file.
  - Limits: `GALAXY_EXECUTE_SLOTS` (default 4, cap 8), `GALAXY_GAME_TIMEOUT` 3600 s, `GALAXY_GAME_HEAP_MB` 2048;
    unit MemoryMax 22G, CPUQuota 800%. Size heap for the field's biggest games, not ours (bc19 L26).
- `sandbox.sh`: `unshare --user --net --mount`, read-only everything but the work dir, fails closed.
- `relay.py`: saturn -> siarnaq relay; Cloud Tasks/Scheduler stand-in (`fire-jobs` each minute when the scheduler
  timer is on); autoscrim throttle `GALAXY_SCHED_MAX_WAITING` 30, `GALAXY_SCHED_MIN_HOURS`.
- `replica_settings.py`, `replica_gcp/` (config, cron, fsutil, mail, spool, storage, tokens), `standins/google`,
  `py310compat.py`: local replacements for Pub/Sub, Cloud Tasks, Scheduler, Secret Manager, GCS (files under
  `/srv/.../storage/<bucket>`), OIDC (HMAC tokens); email/OAuth/Sentry off; settings refuse to start if `google.*`
  resolves anywhere but the stand-ins; venv from hash-locked requirements with `--require-hashes --no-deps`.
- `bootstrap.py` + `maps.txt`: creates the episode (name, language, maps, ranked on, 20 ranked / 40 unranked per
  hour, autoscrim cron), service user, superuser `owner`; `status`, `audit`, `purge-teams PREFIX`.
- `client.py` (API client + CLI as a contestant; accounts in `~/.bc26-galaxy/accounts.json` 600), `contest.py` (our
  team: register, submit, ladder, scrim [--vs NAME@+/-] [--panel] [--queue], drain, matches, fetch, results,
  compare, pool, paired [--graded]), `field.py` (register/submit field teams from `field-teams.tsv`, status, queue,
  activity = spare-cycle ranked challenges near rating, boost, rate).
- `deploy/deploy.sh` (driver side: rsync stage = tools/galaxy26 + engine + maps + `git archive` of galaxy and of the
  client commit + milestones.json, then `sudo galaxy-setup.sh STEP`), `deploy/galaxy-setup.sh` (815 lines, root,
  idempotent steps: user egress postgres src venv app runtime dirs secrets password env units cli migrate bootstrap
  static viewer frontend hostname caddy site start stop status teardown [--purge-data] scheduler/activity on|off,
  milestones), `deploy/replay-prune.sh` (hourly cron: if / < 4 GB free, delete replays older than 1 day).
- `frontend/` (`install-node.sh` sha-pinned node, `build.sh`, `replica.patch`: same-origin backend, site URL, viewer
  link, self-hosted fonts, CSP meta, email verification off, milestones on rating charts), `viewer/build.sh`,
  `frontend_check.py` (bundle audit: no foreign fetch without click), `browser_check.py` (headless Chromium e2e),
  `verify.sh` (isolation + health), `rating_unstick.py`, `spool_bump.py` (reorder queue: our matches first; drop a
  team), `drain-loop.sh`.

### 4.3 Isolation (non-negotiable owner rule: zero effect on official infrastructure)
- Dedicated service user (bc26replica); nftables table limiting that uid to loopback:8026; GCE metadata dropped;
  host-wide table rejecting battlecode.org addresses for every user; all units in a slice with `IPAddressDeny=any`;
  saturn `PrivateNetwork=yes`. Postgres on a unix socket (port 5426, db siarnaq26, host lines reject). Own Caddy
  (Let's Encrypt on `galaxy26.<ip-dashes>.sslip.io`, basic-auth gate user `owner`, strict CSP). Secrets only on the
  VM and driver home (`~/.bc26b-replica-password`, `~/.bc26b-galaxy-team`), never in git (repo is public).
- Hostname unit re-reads the external IP at boot and re-renders the Caddyfile (IP changes on stop/start).
- Only contact with battlecode.org: the checksum-pinned engine download.

### 4.4 Pitfalls hit
- Disk full -> replica down silently (both years; also "episode not found" incident). Prune cron + df every prod.
- Rating chain stalls when an update task is lost or a bulk update skips triggers: ratings froze ~2 days
  (owner noticed "exactly 1561 for days"). `rating_unstick.py` run in every progress refresh.
- Ports 80/443 shared with another year's replica Caddy: whichever starts first after reboot wins.
- Deploy restarts re-run in-flight matches; keep resume store; test under the unit's sandbox first.
- Field bots with clock/init failures inflate our wins on a loaded VM (bc19 L17): keep the replica's game count
  below vCPUs, nice local jobs, raise init limits only as a documented deviation.
- Autoscrim rounds (60+ ranked matches every 8 h) block panel blocks: bump our matches ahead.
- Our own panel requests while autoscrim could pair the active candidate (GAP noted).
- Map restriction: siarnaq filters on `Map.is_public`; hide maps with a Django shell update; `bootstrap episode`
  republishes only the maps in the file passed.
- Replica site login expiry + basic-auth gate: rewrite 401 -> 403 on the JWT path.

### 4.5 What changes for another year (e.g. 2025b)
1. Engine: pin the year's engine jar(s) + sha256 (`ENGINE_JAR`, `ENGINE_SHA256` in galaxy-setup.sh; arena.py,
   snapshot.sh, unit-tests.sh, build-tools.sh all name the jar). JDK version per the year's scaffold.
2. saturn compile/execute recipe: read the year's `saturn/pkg/run/*.go` at the pinned galaxy commit and the
   scaffold's gradle tasks for the exact engine properties, verifier class and the winner regex. If the year accepts
   a second language (e.g. Python), add that recipe; bc26 built Java only.
3. Map format/extension, `maps.txt`, the reversed-map tool (`Bc26Tool.java`: uses engine classes `GameMapIO`,
   `LiveMap`), `replay_merge.py` (replay flatbuffer schema: GameHeader/GameFooter layout), replay file extension.
4. Episode bootstrap: episode name/code (`bc25`-style), language string, maps, request limits, autoscrim cron.
5. Viewer: build the official client of that year from its repo at a pinned commit; patch fonts/CSP/deps.
6. Frontend patch: episode-specific links (Replay! viewer link uses the replay extension).
7. Names: users/units/paths/ports/nft tables per year (bc19 used 8019, bc26 8026) to coexist with nothing else;
   check no other year's Caddy holds 80/443.
8. Field: discover/scan/compile public bots of that year (bc19 bench pipeline), register as teams (`field.py seed`).
9. Galaxy itself (siarnaq at f343088) should need no change.
Redeploy from scratch: `tools/galaxyNN/deploy/deploy.sh` (full `galaxy-setup.sh all`), then `contest.py register`,
`field.py seed`, `deploy.sh scheduler on`, `deploy.sh activity on` (field accounts copied to the VM), `verify.sh`,
`browser_check.py`. Note: bc26's deploy after teardown is untested.

---------------------------------------------------------------------------------------------------------------------

## 5. Suggested bootstrap order for 2025b (derived)

1. Day 0: engine download script, rules digest from engine source, map census, runner (port arena.py), ReplayDump for
   the year's replay schema + basic reports, bot skeleton with Cfg switches + compute monitor + bytecode tag from
   commit 1, snapshot/snapvar, fake-RC unit tests, mirror check.
2. Field bots discovered and scanned (never read); replica deployed with them; our first champion submitted.
3. Start the continuous local BT tournament immediately (tourney.py, box or VM via screenq), ~10 bots, half swings,
   20-minute prod cycle with the full report; crown -> submit -> audit diff -> fixes as newcomers.
4. Replica: champion ranked continuously; delegated field studies (100+ replays, wins vs losses behaviour rates)
   against in-band opponents feed swings; imitate tactics that beat us.
5. Charts on wall-clock axes with milestones; push every commit; never idle; plateau escalation: more/bigger swings,
   correctness audit by lens with adversarial verification, ablation, API sweep, cross-year re-read, rewrite.

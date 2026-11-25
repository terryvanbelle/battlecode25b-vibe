# Digest: what the bc23 and bc24 practice projects learned

Written 2026-11-25 for the clean-room 2025b project. Sources read:
- bc23 docs, filtered copies only: `~/projects/vibe/reference/readroom-no2025/bc23/` (README, LEARNINGS,
  TRAINING_ALGORITHM, HANDOFF, BENCHMARK, CLAUDE, docs/{galaxy,replica,LADDER_STRATEGY,TELEMETRY,ARCHETYPES},
  research/prior/{SYNTHESIS,GALAXY}, selected diagnoses, progress/{ATTEMPTS,ELO}; TRAINING_LOG grepped and partly read).
- bc24 docs, filtered copies only: `~/projects/vibe/reference/readroom-no2025/bc24/` (README, LEARNINGS, HANDOFF,
  TACTICS, AUDIT_PROMPT, AUDIT_PLAYBOOK, research/ADVICE-crossyear sections 3 and 7-14; TRAINING_LOG grepped).
- Code: `~/projects/vibe/2023/{tools,src}` and `~/projects/vibe/reference/battlecode24-vibe/{tools,src,test}`.
- Not read: anything about the 2025 game. That covers the bc23 files `research/prior/bc25-*.md`, which were skipped
  on purpose.

Chronology: bc24 (2024 game, one week, 2026-09-30..10-07) came first. bc23 (2023 game, two weeks, 2026-10-07..10-21)
came second, inherited bc24's method and tools, and refined them. **Where the two disagree, bc23 is the newer word.**

Outcomes, for scale:
- bc24: g_iter0 1257 rose to g_iter7 2113, rank 6 of 88, field score 88.6%. About 80 builds in a row failed until a
  correctness audit ended the plateau. Six promotions then came in four days.
- bc23: 217 attempts and 19 accepts, against 27 panel rejects, 13 screen rejects and 43 drops. The final build,
  c_gd1, rated BT 2046 +- 43: rank 11 of 140 players, 5th against the 87 field bots, field score 92%. The four bots
  above it were never beaten.

---

## 1. Process lessons

### 1.1 The loop that worked (bc23 TRAINING_ALGORITHM, year-agnostic; adopt it nearly verbatim)

- **Objective**: absolute strength against the external field. Beating our own old builds is only a means.
- **Phase 0, before any strategy.** All of these must exist and pass a known-answer check:
  - a rules digest with engine file:line for every fact;
  - a headless parallel runner keyed by (code hash, opponent, map, side, seed), with a determinism check and an
    identity control;
  - a replay reader;
  - bot iteration 0 with a monitor for overruns, near misses and exceptions, decision counters, a per-robot RNG and
    geometry-relative tie-breaks;
  - the external field, compiled blind;
  - a ladder replica with a batch BT rating;
  - a basics battery.
- **Foundation bar**: beat the starter bot on every map from both sides, pass the basics battery, get placed on the
  ladder. Then run a correctness audit before the first tuning arm.
- **Loop**: pick a target → trace before theorising → pre-register (mechanism, counter, reachability, firing rate,
  price, instrument, gate, falsifier, dose ladder with a zero arm) → one change behind a switch (defaults play
  exactly as the incumbent) → **show delivery before judging value** → gate on seeded paired cells → accept (frozen
  snapshot, ladder, post-block refresh, commit+push) or reject (restore byte for byte, ledger entry with a re-open
  condition).
- **Target sources, rotated**:
  - own degeneracies: the highest yield, and they need no opponent;
  - the field (two-group contrast);
  - capability gaps (unused API or mechanics);
  - free actions;
  - action patterns rather than counts;
  - a structural swing at least 1 time in 4.
  After 3 rejects in one area, move to another area.
- **Plateau protocol, in order**:
  1. a correctness audit of the bot **and** the instruments;
  2. ablate what we carry;
  3. an API/mechanics sweep;
  4. re-read the field's games and copy the offence that beats us;
  5. re-read the cross-year principles;
  6. stack positive near-misses with independent mechanisms;
  7. a structural attempt or rewrite, with a kill criterion.

### 1.2 Statistics and gating

- **The unit of evidence is the paired cell** (opponent, map, side, seed). Only discordant pairs inform.
  - An identity control (a byte-identical copy) must read 0 discordant on *every* tool path that produces verdicts.
  - bc24's scrim tool drew random seeds for 2.5 days: identical code flipped 15-29% of cells, so the verdicts were
    noise.
  - bc23: the first "identity" run had silently compiled a changed `src/bot`. Since then every run records
    `provenance.txt` with the code hash.
- **Seeding does not make behaviour-changing arms agree.** They still differ from the control on 14-38% of pairs, so
  size blocks from the measured discordance. On bc24's 234 band pairs, 1 SE was about 6.5 net games (about 20 Elo).
- **Map seeds make games deterministic replays (bc23).**
  - Engine IDs and RNG come from the map file, and our code keys roles, wall-following hand and RNG on the ID. So
    near-identical builds replay the same games: same-side wins in 75.8% of map-seed cells against 52.6% with random
    seeds.
  - Use explicit random seeds, the same for both sides, e.g. `random.Random('r1-'+map)`.
  - Pinned seeds can favour one seat: an identity copy scored 4/20, so 10/20 was not neutral on those cells.
  - Always pair against an identity run on the same cells, never against "50%".
- **Coin-flip tiebreaks** (an unseeded final tiebreak) must be excluded from paired counts. Parse the end reason and
  key it in the results.
- **Use the most informative per-pair statistic.**
  - bc24: wins carried 2.2-5.6x less information than the capture difference.
  - The old shipping rule had 17% power at +30 Elo, which meant 45 hours with no promotion until the owner asked.
  - The new rule reached 63-65% power at 2% false promotion: t_all >= 2.3 (or t_up >= 2.6) with wins net >= 0, looks
    at 240/480/720 pairs, ship at t >= 3.0 on the first look.
  - **Simulate a gate's power at the effect sizes you actually produce before relying on it.**
- **Three-way verdicts**: PASS at 1 SE beyond the bar, FAIL at 2 SE short, otherwise EXTEND (24→48→96→192 cells).
  Never close a line on INCONCLUSIVE. bc24 found that 16 of 28 FAILs and 7 of 15 PASSes sat within 1 SE of their bar.
- **First looks regress toward zero.** Examples: +31 over 400 pairs, then +12 over 1,880; t 2.03, then 0.32 pooled.
- **Panel rule (bc23, final)**: two 100-cell blocks with sides swapped; t = net/sqrt(D).
  - Accept at t >= 1.5 and net >= +3, after block 1 or cumulatively after block 2.
  - Reject at block-1 net <= 0.
  - Simulated P(accept): 0.11 at a null, 0.46 at a true +3 per block.
  - The old habit of accepting at net +1..+3 on one panel accepted about 44% of null candidates.
  - Basics exception: a fix of crashes, overruns or stuck units with delivery shown may accept at net >= 0.
- **One reference panel is one draw.** Bytecode-timing-dependent outcomes re-draw borderline cells, so judge against
  two reference draws (the base and the previous build).
- **A fixed panel saturates and flatters builds tuned on it.**
  - Version it. Refresh it when an opponent sits at 9-10/10 or 0-1/10, the whole panel is above 80%, or the maps are
    narrow.
  - Play a control on each new version first.
  - Never report standing from a panel-only rating: it ran about 34 points high.
- **Batch Bradley-Terry beats running Elo.**
  - Held-out log-loss was 0.572 against 0.628. One unchanged build drifted 191 points on the ladder's Elo.
  - Cap each pair at 200 games: 1,500 filler games against one 30% matchup had pulled g_iter7 below a bot it beats.
  - Iterate to tolerance: a capped fit read 30-46 points low.
  - Calibrate bots rated on few games (2274 ± 348 on 26 games became 1920).
- **Rules for reading numbers**:
  - never read a running batch;
  - never move a bar after seeing a number;
  - compare only with controls from the same period;
  - state the unit of every margin;
  - act on the earliest round at which a metric predicts the result;
  - stratify within map and opponent;
  - use capped or median statistics, because means of trip times are dominated by outliers.

### 1.3 What predicted the ladder, and what did not

- **Self-play edges do not predict field wins (bc23).**
  - c_ms1 went +22 net (t 3.18) against an identity copy in self-play, then +4 (t 0.82) on the panel, and was rejected.
  - A fix aimed at the incumbent's own blind spot exploits only the incumbent. A self-play edge earns a panel trial,
    never an accept.
- **Self-play parameter tournaments select against the field.** The Swiss winner over 16 variants (`swiss.py`) lost
  net -8 on the panel. Successive-halving races on micro knobs found nothing: those knobs were at a local optimum.
- **Local proxies measure soundness, not matchups.**
  - The h2h score and the roster net correlate about 0.45 with the panel's paired net.
  - No archetype's net tracked the panel against the team it was modelled on (-0.31 to +0.26).
  - Use local runs as regression checks. Let only field games judge matchups.
- **Screen stage (b)** (20-game h2h on the panel maps) did predict the panel:
  - b >= 12: mean net +1.7;
  - b 10-11: -0.3;
  - b <= 9: -2.6.
  A borderline screen is a reject.
- **A local screen cannot judge a narrow arm** (late-game-only or one-map). Read the cells it can change, or go to the
  panel.
- **bc24: measure against the opponents that define the gap.** A mirror cannot price a defence against rushes.
  Target-only gains did not climb the ladder. Ship on the band and use targets as diagnostics.

### 1.4 Delivery and mechanism

- **Show delivery before judging value, and make tools refuse otherwise.** bc24: 10 of 11 adoption arms were judged
  on wins without ever reproducing the behaviour. `delivery-gate.sh` refuses a band test until delivery passes.
- **A firing counter is not delivery.** Condition delivery on the trigger, and measure it on the mechanism's own
  object.
- **A mechanism can deliver its proxy and still lose.** Re-grabs +9.1 SE went 11-26; more digs meant fewer stuns.
  Pair each signature bar with an outcome guard. Estimate the proxy→outcome link first.
- **Measure the mechanism, not only the score.** One accept rested on healed HP x2.2 at net +3. One "gain" hid 11-21
  carriers fed into a death trap.
- **Measure how often a code path runs before tuning it.** bc24 dam and float traps never fired (the bank stayed under
  the threshold on 64 of 75 maps), so their ablations were void.
- **Don't price a fix from a correlational split** ("we lose more when the defect fires"): defects cluster on hard
  maps. Price it on identical cells.
- **Statistics shaped by the outcome are consequences, not levers.** Examples: kill location, "third flag lost 0% in
  wins". Drop contrasts that restate the win condition.
- **Mine your own coin-flip tie-breaks as randomized experiments** (bc24 R7). They measured the causal 3-round effect
  of ending a turn in reach, by HP bin.
- **Ablate what you carry** (bc23):
  - Switching off one early-accepted rule (launcher cohesion, added for a field study days earlier) gave +20 on the
    panel maps (z 3.2) and became an accept. A rule accepted under old code can become the largest drag.
  - Protocol: one switch off per build, panel maps x both sides x 4 fixed seeds, paired with an identity build.
  - Cost: a 15-switch sweep is about 1,200 games.

### 1.5 Stacking

- **Never stack on non-inferiority** (bc24 P3). Three "not worse" layers ended 30 games below the incumbent.
- **Do stack positive near-misses with independent mechanisms**, and judge the stack as a new arm. Two arms at t 1.0
  and t 1.3 stacked to t 3.25 and shipped as g_iter5.

### 1.6 Audits: the single biggest lever

- **bc24 R1.** About 80 tactic builds failed. Then a read-only audit ran:
  - 5 lenses: dead code; rules/API; shared state; replay behaviour; the measurement pipeline;
  - 2 adversarial verifiers;
  - 41 of 42 findings confirmed.
  Results: the audit fixes gave +169, its follow-ups +77 more, and +185 of the season's +461 came from plain bug fixes.
- **The bugs it found**:
  - an alert that was "fresh" in 1,057-1,686 of 1,800 rounds, which switched off every defender;
  - robots frozen on an unreachable enemy behind a wall;
  - a registry stale for 1,393 rounds;
  - symmetry guessed wrong on 32.4% of map-sides, because `Sym.observe` had no callers;
  - unseeded pairs.
- **"One broken basic is a sample of a class: audit at once."** Read a plateau first as broken basics, not an
  architecture ceiling. bc24's 8-agent rewrite design was never consumed, and 528 of its ~900 dead lines belonged to
  it.
- **The procedure is reusable**: `readroom-no2025/bc24/AUDIT_PROMPT.md` and `AUDIT_PLAYBOOK.md`.
  - Fix instrument defects first and prove them with an identity control.
  - Mark verdicts that rested on broken tools VOID.
  - Put each bot fix behind its own switch, build one combined arm, and confirm on fresh seeds.
  - Install permanent guards: `deadcode.py`, an arm-intent check, census columns.
- **Run it on the first working bot and at every plateau.**

### 1.7 Ladder replica usage (bc23 LADDER_STRATEGY; applies directly to a real contest too)

- **Unranked games are for experiments.** You choose opponent, maps and order, so they replay deterministically for
  paired comparisons.
- **Ranked games only bank rating, and only while a validated build is active.**
- **The trap**: a match plays whatever submission is active *when the match is created*. A candidate on trial is
  exposed to autoscrims and to incoming ranked challenges.
  - Keep trials short and start them right after an autoscrim.
  - Auto-reject incoming ranked challenges during a trial.
- **Parked trials**: once all of a panel's matches exist (about a minute after the requests), resubmit the validated
  build and let the panel play on. This turned one trial per 8-hour window into several overlapping trials.
- **Choose ranked opponents by expected gain**, `K*(P_BT - E_ladder)`. The ladder's rating is compressed, so most
  teams above offer a negative gain.
- **Pace**: BURST (one request every 5 minutes) while there are fewer than 30 rated matches or the build is under 24
  hours old, else MAINTAIN (one every 30 minutes). Galaxy's displayed rating is `mean - 1500*0.85^n`, so the first
  ~20 matches matter.
- **Pre-trial screen** (`screen.py`), enforced by `ladder_policy.py trial-start`:
  - (a) basics: 8/8 against the starter bot, with 0 overruns, exceptions, self-deaths and wrong symmetry;
  - (b) 20 h2h games on the panel maps against the incumbent;
  - (c) the archetype roster, paired with the incumbent's cached games (it may block a candidate, never accept one);
  - (d) the basics bars over every game.

### 1.8 Operational mistakes (with their fixes)

- **The machine idles between runs, not during them.** bc24's VM was idle 29% of its uptime. Keep a standing VM queue
  (`vm-queue.sh`) with at least 3 jobs and an idle filler, and collect filler results automatically: 17 filler blocks
  (about 2,000 games) once went unrecorded.
- **Budget filler by information.** Filler became 80% of bc24's games and distorted the fit.
- **Key every result by the full cell.** Seedless replay names dropped 1.6-11.5% of games and overwrote others.
- **Replay retention keyed to its consumers, plus a disk check before every block.** Both disks filled in bc24. A
  queue runner then logged "exit 0" on failures (`$?` held a date substitution's status) and spun for 18 minutes with
  no back-off.
- **Liveness alarms.** In bc23 the replica and the VM queue runner died silently, and screens sat pending for 40
  hours. `watch_events.py` now exits (waking the agent) on a dead replica, runner or ranked loop, a stuck match, or a
  50-minute heartbeat. Test liveness by the component's own lock or API, not by process name.
- **`pkill -f` / `pgrep -f` match the caller's own shell** (5 times in bc24, again in bc23). Kill by PID or use a
  `[b]racket` pattern.
- **Concurrency**:
  - per-process temp files;
  - a state check and the action it authorizes share one lock;
  - one semaphore for every game-starting path;
  - private class trees per run;
  - cap diagnostic games at 8 on an 8-vCPU VM (24 starved sshd);
  - put a lock on `unit-tests.sh`.
- **Network**: retry DNS and connection-refused errors and any GET. Never blindly resend a POST: a duplicate scrimmage
  request is a real cost. Wildcard DNS (sslip.io) failed intermittently.
- **A refresh step killed by its timeout must fail loudly.** A chart silently went stale because its cost grew
  quadratically.
- **Token budget (bc23 usage audit)**:
  - Waiting inside a turn rewrites the context cache on resume (18% of usage).
  - Large main contexts (20%) and fixed 30-minute check loops are costly.
  - One-off setup (reading prior years, building the replica) took 56% of week 1.
  - Fix: workflow agents queue long jobs and stop; an event watcher wakes the session; keep checks under the
    one-hour cache TTL; compact early.
- **Every rule that can be forgotten becomes a tool that refuses** (bc24 P2). Rules kept only in prose were followed
  in letter, not spirit.
- **Records**: an append-only TRAINING_LOG (grep-only), PROMPTS verbatim, a closed-directions ledger, LEARNINGS
  updated the day a lesson is confirmed, and HANDOFF as a closure map. The owner sees the project through
  README/HANDOFF/progress, so update them in the same commit as a promotion.
- **Owner's short basic questions were the cheapest audits** (bc24 O1). Answer them from data. Bring the owner a
  blocking rule's measured cost with a recommendation instead of silently keeping a stricter reading: one self-imposed
  ban cost 4 days.

### 1.9 Field discovery (BENCHMARK, both years)

- Discover public bots by GitHub repo search plus scaffold forks plus a web sweep. Classify repos by *counting* files
  that use that year's API names.
- Clone sparsely (sources and build metadata only) outside the repo. Run a security scan by pattern count. Compile
  blind (`javac -proc:none`, diagnostics to files).
- Pick each repo's final bot by name rules and by last-commit date. Dedupe by class-file hash. Smoke-test against the
  starter bot. **Never read their source.**
- Scale: bc23 had 864 candidates → 148 repos → 968 packages → 87 entrants. bc24 had 55 field bots.

---

## 2. Strategy and tactics lessons that transfer

### 2.1 Meta-principles (owner, bc23 PROMPTS 49-50, 139)

1. **Free actions always get a job.** An unused cooldown is lost for good: audit every per-turn action for idle turns.
   - Example: blind fire at cloud tiles that may hide an enemy.
   - Caveat: measured, that one was worth only about 1% of damage. The principle stands; the value varies.
2. **Compare action patterns, not counts.** Classify field actions by context (visibility, aim, terrain, timing,
   target) and contrast three groups: bots that beat us, bots we beat, and us.
3. **Play symmetry: every decision is mirror-symmetric.**
   - Tie-breaks go by the robot's own geometry or score, never by a fixed compass order, row-major "first found",
     a team constant, or an ID correlated with team or spawn order.
   - Check with a mirror match on every map from both sides; a persistent lopsided map is a bug.
   - Evidence: bc22 identical code won 71% as A and 44% as B. bc23 self-play split 2-67 and 75-4 by side on two maps.
   - Caution: random tie-breaks lost twice, and a fair fix can cost strength. It still faces the gates.
4. **In a live contest, read the Discord.** Old discussions are off limits in practice years.

### 2.2 Economy

- **The early game decides.** bc23: half the losses already trail by r150. Mn@100 under half the opponent's went 2-8.
  - The strong bots out-built us 3-4x in carriers by r500.
  - Early trips dying before they collected, and carriers dying at home wells, were the largest measured loss cause.
- **The whole-game gap is often decided before round ~50.** Compare the first 50 rounds' event streams side by side
  with the strongest opponents.
- **Repairs and cap removals transfer; reallocations between unit types mostly do not.** bc24: 8 economy arms, none
  shipped; the one that paid took free resources without costing fight actions.
- **Before tuning spending, census what units actually do.**
  - bc23 carriers walked empty on 36% of turns against jmerle's 10%.
  - A carrier froze 4 tiles from a well for 400 rounds.
  - Units were spawned into sealed 2-tile pockets.
  - Fixes that worked: well packing (take the nearest free collect square or step onto the well tile) and a
    spawn-pocket filter.
- **Commit to targets with explicit release conditions.** Absolute stickiness loses; per-tick re-optimisation
  ping-pongs.
- **"Hot" resource sites**: carriers flag a site where they fled an enemy, and the flag decays over time. bc23's
  version paid for itself; disabling it cost -1,429 island-rounds on one map.
- **Contested sites**: the strongest bot held contested mid-map resources from r0. Mapping where our deaths occur
  (76 of 105 early carrier deaths within d² 64 of our HQ) reframed "economy" as "we lose the home fight".
- **Reserves need a release valve, not removal.** "A reserve nobody spends is bodies nobody has." Keep stockpiles in
  units of what they buy. Never float resources.
- **Census the production chain for silent shut-offs**: stale censuses, over-broad danger gates, caps that bind while
  stock piles up.
- **Find the binding resource**: a resource never at cap is being spent; one always at cap is not the constraint.

### 2.3 Navigation and pathfinding

- **Proven set**: a greedy step scored at the *destination after any environmental push*, then bug wall-following
  when a wall blocks.
  - Handedness comes from the robot ID.
  - Leave bug mode when strictly closer than the start point.
  - Flip handedness after STALL_LIMIT (about 20-24) moves without a new best distance.
  - Robots are soft obstacles: sidestep or wait, never start wall-following on a robot.
- **Nav bugs that cost the most** (they recur every year):
  - The stall or bug state reset on every target change, so moving targets never accumulated a stall. Fix (A7): a
    target move of d² <= 8 keeps the state. bc20's version of this bug was "the most expensive nav bug".
  - A not-ready cooldown must never advance bug state or stall counters.
  - An unreachable visible enemy took the whole turn: 16-36% of enemy-in-view turns idle on walled maps. Add a
    reachability filter.
  - Map-edge flip (A9), plus an A-B-A oscillation guard.
  - Cohesion or target switches reset wall-following state, so a launcher that had escaped walked back in.
  - Followers trailed a stuck leader.
- **bc23 distance fields (`src/c_gd1/Field.java`)**, built for dead-end corridors where launchers stood 50-317 rounds:
  - A per-robot BFS toward one target over 64-bit wall-row bitmasks: sensed walls plus their symmetry images; unknown
    tiles count as open.
  - Built one wave at a time in the bytecodes left at the end of the turn (about 30 bytecodes per row per wave).
  - Descended only after greedy hits a wall toward that target (sticky per target).
  - Rebuilt only when a "downhill" tile proves to be a wall.
  - Accepted at +8 net (+2.3 SE). Launcher mean bytecodes rose from 2,500 to 7,200, which later forced a bytecode
    basics fix.
- **Don't write a heavy pathfinder first.** bc21 reverted a Dijkstra before running it. Measure navstats per map class
  (moved share, still streaks, ABA) and build heavier tools only on evidence.
- **Clear rings**: no unit parks on tiles adjacent to a producer. Spawn tiles are infrastructure; check spawn
  reachability.

### 2.4 Exploration and symmetry

- **Never guess symmetry by fixed order** (bc24: wrong on 32.4% of map-sides).
- **Observed symmetry (both years)**:
  - Keep the candidate bitmask (ROT / FLIP_X / FLIP_Y), never emptied; count conflicts instead.
  - Per-robot terrain memory: an immutable tile seen now must match its remembered image.
  - Geometric elimination from own spawns, then "predicted enemy base seen empty".
  - Collapse candidates that predict the same enemy bases.
  - OR-merge eliminations (or AND-merge survivors) through the shared array.
  - Budgeted updates (`BC_START`/`BC_STOP`, end-of-turn fill).
  - Scout toward the most discriminating tile; the map centre resolves fastest.
- **Offline test** (`SymTest`): run on every real map plus 300 random symmetric maps from both sides; the true
  symmetry is never eliminated. The decision-round distribution sets the "decided by round X" bar. symWrong = 0 is an
  absolute basics bar.
- **Watch transformed features**: directional tiles (currents) must mirror geometrically; `opposite()` was wrong on 41
  of 54 reflection maps. Resource types can break a symmetry that positions satisfy.
- **Name the consumer of every fact before building the sensor.** bc24's symmetry sensor existed and was never called.
- **Exploration**:
  - Commit each explorer to a heading and reassign only when it is confirmed stuck (bc26: +28).
  - Use a frontier search for workers with no known target (bc23 c_expl1: helped two maps, rejected overall).
  - "Move away from home" exploration walks into the enemy.
  - Locating objectives earlier did not convert into holding them (bc23 c_scout1: first anchor 24 rounds earlier,
    net -2).
- **Slice every target's games by map symmetry and side on day one.** bc24's open lead was a vertical-symmetry
  penalty against one bot: 0.19 against 0.38 on rotational maps.

### 2.5 Combat micro

- **9-tile evaluation is the micro every strong team copies.** Score each candidate square lexicographically, with no
  smooth weighted scoring (that lost 1-25 and 1-26 in bc24). Criteria:
  - enemies that can hit me there;
  - can I attack after the move;
  - distance;
  - allies adjacent;
  - HP.
- **Kite when move and action cooldowns are separate**: hit, then step out; when ready, step in and hit. Verify the
  premise first (the target must be killable, and survival must convert).
- **Hold the action for the strike** (bc24 heal hold, +144 Elo, the largest single step, found by a two-group
  contrast). Near enemies, keep the action ready instead of spending it on low-value actions, so whoever steps into
  reach is hit first.
- **Recharge tempo** (bc24 T19): after striking, leave reach; while recharging, close to one-step range so the next
  strike lands the turn it is ready. The upper tier did this 0.46 of the time, we did it 0.02.
- **Step-in discipline**: a wounded unit should not step into reach of a group that can kill it.
- **Targeting order**:
  - win-condition carriers first;
  - then what can shoot back;
  - lowest HP (kill soonest), with ties broken by a consistent key so a group focuses fire;
  - kills per action over damage.
- **Concentrate; never trickle** (Lanchester's square law). bc23 lost the first launcher war *at parity*: our dying
  launchers died 2.5 against 2 and were outnumbered 0.32 of the time, theirs 4 against 1. "Wait when outnumbered" was
  better than a focus-fire simulation (c_sim1 5/20).
- **Avoid lethal static hazards** (bc23 aura-safe movement): units killed by enemy-base auras fell from 1,227 to 35
  per 100 games. Treat hazard zones as walls for movement and allow only outward steps.
- **Heal or retreat to a safe healing zone when wounded** (bc23 c_mend2): launcher deaths -7.5 (t -2.4).
- **"Survival by inactivity" loses.** Leashes and saving-only arms cut deaths and did not raise the score (bc24 S8).
- **Presence at enemy objectives is an outcome of winning fights, not a lever** (bc24 S6). Re-grabs, relays, escorts,
  dives and late all-ins all failed. If an opponent's mechanism cannot be stopped, slowing it may be enough (the waffle
  crack: +55).
- **Combat stats are mostly symptoms**: attack/heal mix and guard counts follow fight state. Check unit- and
  producer-count parity in the exact window before blaming trade efficiency.

### 2.6 Comms

- **Schema first**:
  - fixed slots per purpose and one writer per slot;
  - a header comment with the full slot map (bc23 `Comms.java` is a good model);
  - pure packers with unit tests, plus a slot-layout test derived from constants.
- **Stamp claims with the round of observation; the newer claim wins.** Every flag needs an expiry and a clearing
  rule that has been seen firing in a long real game. "Any enemy seen" alerts and "carried" states that never expire
  switched whole roles off in bc24.
- **Write-range rules**: re-check write legality at write time. A robot that moved since turn start wrote out of
  range and threw 1-7 exceptions a game.
- **Newborns act next round.** Re-post anything a newborn needs on a schedule. Roles are assigned by the spawner, not
  chosen by the newborn.
- **Census** by an epoch accumulator: each unit adds 1 per epoch and the base zeroes the next slot. Never use an
  "ever built" counter.
- **Comms pays for knowledge, rarely for reaction.** Broadcasting targets caused stampedes.

### 2.7 Bytecode

- **Monitor from commit 1** (bc23 `RobotPlayer.java` pattern):
  - an overrun means the round changed during the turn;
  - a near miss is more than 90% of the limit, measured *before* any deliberate fill;
  - count caught exceptions;
  - a catch around the whole turn.
- **Zero overruns is a basic.** An overrun voids an arm.
  - Big blobs ran within a few hundred bytecodes of the limit, so every arm that added work overran.
  - A decision-preserving cut was the prerequisite (c_bc1: median calm-march turn 6,856 → 3,664, verified on 217k
    differential cases).
- **Bound work against crowds.** A fight scorer that took 6,500 bytecodes over 48 visible enemies overran. Fix:
  score all fighters, at most 10 non-fighters, and keep a guard.
- **Spare-bytecode fills hide real near misses** (bc24 M10). Stop the fill below the near-miss line, at 88%.
- **The first turn is the most expensive**: static initialisers and lazy W·H allocations happened there. bc23's first
  bot overran every unit's first turn.
- **Cheap patterns**:
  - static fields;
  - arrays, no `java.util` in hot paths (`HashMap.put` ≈ 143 bytecodes);
  - bit-packed long rows;
  - unrolled loops and switches;
  - no allocation in inner loops;
  - amortise scans over turns;
  - a caught exception costs about 500 bytecodes.
- **A loop guard is not a return reserve.** Measure the maximum admitted work plus the epilogue.

### 2.8 Telemetry through official-format replays (bc23, clever and portable in concept)

- Contest replays drop indicator strings and dots, but keep per-robot per-turn `bytecodesUsed`.
- **BCC channel**: at the end of the turn the bot pads its bytecode use, with a fall-through switch costing exactly n,
  so that `bytecodesUsed ≡ code (mod 64)`. That carries a 6-bit state code per robot-turn for about 48 bytecodes.
  - Sync rounds pad to a fixed code so the decoder can self-calibrate its offset.
  - Calibrate PADK on the same JDK that compiles for the contest.
- **Locally**, use the indicator string `"<state><code>…|ov=,ex=,nm=,sm=,sd=,…"` (64-character cap; the replay keeps
  only the last string of the turn) plus data dots (which cost 0 bytecodes beyond the argument pushes).

---

## 3. Reusable code and tools catalogue

Port difficulty:
- **L**: game-agnostic; change paths or names only.
- **M**: needs new column names or a new engine CLI.
- **H**: tied to that year's replay schema or API.

Paths: bc23 = `~/projects/vibe/2023/`, bc24 = `~/projects/vibe/reference/battlecode24-vibe/`.

### 3.1 Bot code (designs to re-implement; read the code directly)

| path | purpose | port |
|---|---|---|
| bc23 `src/c_gd1/RobotPlayer.java` | turn loop: overrun, near-miss and exception counters; end-of-turn budgeted fill (map memory, distance field) with an 88% stop; indicator guard; BCC pad last | L-M |
| bc23 `src/c_gd1/Nav.java` (278) | greedy after-push scoring + bug with ID handedness, stall flips, A7 small-target-move keeps state, edge flips, hazard-aura avoidance, `moveAway` | M |
| bc23 `src/c_gd1/Field.java` (173) | incremental per-robot BFS distance field on 64-bit wall rows (W <= 64), resumable across turns, stale-on-wall-contradiction | M (good candidate to port as-is) |
| bc23 `src/c_gd1/MapMem.java` (342) | per-tile char memory (known, wall, cloud, current, resource, objective bits); symmetry bitmask from contradictions; island memory; budgeted `process()` | M |
| bc23 `src/c_gd1/Comms.java` (323) | documented 64x16-bit slot schema, `enc = x*64+y+1`, write-legality re-check, stamped sightings, epoch census, per-HQ flag nibbles | M (pattern) |
| bc23 `src/c_gd1/Launcher.java` (1031) | 9-tile fight scoring, focus fire (lowest HP, then lowest ID), pinned-enemy threat, kite, mend-on-island, siege rotation, raid targets from symmetry images | H (ideas) |
| bc23 `src/c_gd1/Carrier.java` (1169) | well commit/release, packing, hot wells, flee, frontier explore | H (ideas) |
| bc23 `src/c_gd1/Telemetry.java` (419) | BCC pad, indicator v2, data-dot records | M |
| bc23 `src/c_gd1/C.java` (495) | constants with provenance comments; switch per arm (the `param.py` target) | L (pattern) |
| bc24 `src/g_iter7/Nav.java` (115) | compact greedy+bug with `resetNeeded` (A7) and stall exit | L-M |
| bc24 `src/g_iter7/Micro.java` (451) | kite/strike micro, heal hold, `bestTarget`, threat by d² reach, wary step | H (ideas) |
| bc24 `src/g_iter7/Sym.java` (258) | observed symmetry: geometric, spawn image, terrain memory, `collapseEquivalent`, `scoutTarget`, budgeted update | M |
| bc24 `test/bot/{SymTest,BotTest,ContactTest,AuditTest}.java` | no-JUnit tests; fake `RobotController` via Proxy; symmetry property test over random maps | M |
| bc23 `src/arch_*` | archetype sparring partners (copies of field styles built from replays only) | H |

### 3.2 Game running, queueing and infrastructure

| path | purpose | port |
|---|---|---|
| bc23 `tools/lib.sh` | JDK and engine classpath, one-game runner (bare java, no Gradle, `-Dbc.server.websocket=false`), result and reason parsing | M |
| bc23 `tools/gauntlet.sh` | parallel games, private class tree, results.csv keyed by full cell, provenance | M |
| bc23 `tools/get-engine.sh`; bc24 `tools/build-engine.sh` | stage a pinned engine jar, plus a seed patch (`-Dbc.game.seed`; bc24 built from source when maven artefacts were missing) | M |
| bc23 `tools/build.sh`, `snapshot.sh`, `bot-hash.sh` | compile all packages; freeze `src/bot` as `g_iterN` (package rewrite); content hash invariant to package name | L |
| bc23 `tools/param.py` | build a package with `C.java` constants overridden (`make BASE NEW K=V`), a parameter space with constraints | L-M |
| bc23 `tools/run-dev.sh`, `throughput.sh` | one diagnostic game with robot stdout; concurrency knee | L |
| bc23 `tools/vm.sh`, `vm-run.sh`, `vm-enqueue.sh`, `vm-queue.sh`, `vm-stop.sh`, `vm-tail.sh`, `vmjobs.py` | standing VM job queue (pending/running/cancelled), detached jobs by process group | L |
| bc24 `tools/vm-sync.sh`, `vm-collect.sh`, `vm-prune.sh`, `collect-fillers.sh`, `filler-pair.sh` | tar-over-ssh sync, pull results without replays, disk-threshold prune, idle filler | L |
| bc23 `tools/watch_events.py` | event watcher that exits to wake the agent: panel or screen done, stuck match, dead replica, runner or loop, heartbeat | M |
| bc23 `tools/unit-tests.sh`, `test_tools.py` (2,795 lines), `test_elo.py` | one command after every change | L (pattern) |
| bc23 `tools/web-worker/` | GitHub-Actions-runner control of the driver from a web session | M |
| bc23 `tools/build_readroom.py`, `filter_year.py` | build the filtered reading room (year-tagged blocks stripped) | L |

### 3.3 Statistics, rating, gating

| path | purpose | port |
|---|---|---|
| bc23 `tools/paired.py` | paired cells: gained, lost, D, net, t = net/sqrt(D), sign test, margin t; refuses mismatched cells files or <90% matched; excludes coin flips | L |
| bc23 `tools/elolib.py` (+ `test_elo.py`, 813 lines of tests) | batch Bradley-Terry, Newton/Cholesky fit to tolerance, prior, pair cap 200, dedupe of repeated cells, reason codes, field score | L |
| bc23 `tools/elo.py` | `progress/ELO.md` table, `elo.png` | L |
| bc23 `tools/sprt.py`, `statlib.py` | SPRT on discordant pairs (p0 0.50, p1 0.58); shared stats | L |
| bc23 `tools/compare.py`, `summarize.py`, `compose_run.py` | run-vs-run diff; summary per opponent and side; compose a control from already-played cells | L |
| bc23 `tools/screen.py` (1,212) | pre-trial screen: basics + h2h + roster paired with a cached incumbent; PASS/FAIL/INCOMPLETE records keyed by code hash | M |
| bc23 `tools/basics.py`; bc24 `tools/basics.py` | basics battery: absolute bars plus paired relative bars at 2 SE | M |
| bc23 `tools/delivery.py`; bc24 `tools/delivery-gate.sh` + `delivery-check.py` | delivery check: mechanism fires and its signature moves on identical cells; refuses the band test otherwise | M |
| bc24 `tools/eval-paired.py`, `band-test.sh`, `paired.sh`, `mirror.sh` | sequential looks at 240/480/720, split by tier; mirror SPRT | M |
| bc23 `tools/deadcode.py` | methods defined but never called (caught `Sym.observe`) | L |
| bc24 `tools/arm-intent.txt` + check | asserts every arm's switch flip is really present | L |
| bc23 `tools/swiss.py`, `race.py` | Swiss tournament / successive halving over C.java params. **Lesson: winners overfit self-play; use only with field-like opponents** | L |
| bc23 `tools/causal_dag.py` | cause-effect graph of panel losses from paired cells | M |
| bc23 `tools/attempts.py` | attempts ledger and funnel table (`progress/ATTEMPTS.md`) | L |

### 3.4 Replay parsing and analysis

| path | purpose | port |
|---|---|---|
| bc23 `tools/replaydump/ReplayDump.java` (2,661) + `replay-dump.sh` | gzipped flatbuffer → state rebuilt from events. Modes: summary, census CSV, per-round metrics, robot life, map-at-round, logs, bytecode, navstats, events, states, overruns, shots with visibility, extract (engagements, deaths, timelines, trips), fingerprint, checks (model identities), `--sa` state-action rows | **H** (schema per year), but the mode list and the model-identity checks are the design to copy |
| bc24 `tools/replaydump/` + `replay-dump.sh` | .bc24 version (compiled on demand, cached by source hash) | H |
| bc23 `tools/match_report.py` (1,242), `telemetry_query.py` | per-match report (≤ 8 KB markdown) + `telemetry.jsonl`; aggregate queries | M |
| bc23 `tools/sa_extract.py` | behavioural-cloning rows of one opponent (built a jmerle mimic sparring partner) | M |
| bc23 `tools/profile.py` | per-team tactical profile, side by side | M |
| bc24 `tools/capability-census.sh`, `capability-summary.py`, `arm-deltas.py`, `tactics-survey.py` | two-group contrast census (the method behind +144) and a tactic survey table regenerated into TACTICS.md | M |
| bc24 `tools/correlate.py`, `onset.py`, `polarity.py`, `derived.py`, `scrim-study.*` | which metrics separate wins from losses, and from which round | M |
| bc24 `tools/premise.py`, `recall-d0.py`, `contact-d0.py` | premise checks from replay truth before building an arm | H (pattern) |

### 3.5 Progress graphs and ladder views

| path | purpose | port |
|---|---|---|
| bc23 `tools/field_score.py` (from bc24 `field-score.py`) | rating, field score, score vs bots above, rank per submission, fit R0 + a·ln(1+t/1d) projected with a 95% band to weeks 1-4 → `field-score-{1w,4w}.png` | L |
| bc24 `tools/progress-chart.py` | accepted builds in order → `progress.png` | L |
| bc23 `tools/rating_history.py` (859) | replica "Rating History" redrawn with submissions marked and a BT right axis tied by least squares; panel-version changes marked | M |
| bc23 `tools/progress-refresh.sh`; bc24 `tools/post-block.sh` | one command after every accept or block: results → games.csv → ELO → charts → handoff; names failed steps | L |
| bc23 `tools/galaxy/snapshot.py` | `progress/ladder.{md,png}` from the Rankings API | M |
| bc23 `tools/scrim-cells.py`, `scrim-record.py`, `games_coverage.py` | contest-like random cells; idempotent recording into games.csv; coverage check | L |

### 3.6 Ladder client and policy

| path | purpose | port |
|---|---|---|
| bc23 `tools/contest.py` (675) | contestant client over the siarnaq API: submit `--wait`, request, matches, fetch, `block <cells>` (download into a run dir for `paired.py`), token cache | M (endpoint episode name) |
| bc23 `tools/ladder_policy.py` (771) + `test_ranked_policy.py` | ranked loop by expected gain, BURST/MAINTAIN, `trial-start/park/decide/end`, state lock, screen enforcement | M |
| bc23 `tools/bench-*.{py,sh}`, `benchcompile/` | blind field discovery, fetch, scan, compile, hash, select, roster | M (API-name list per year) |

---

## 4. The galaxy replica (bc23)

**Why.** It gave a private ladder that behaves exactly like play.battlecode.org: submissions, scrimmages, ranked
penalized Elo, autoscrims, replays. It was the only way to play the field "as a contestant". It never touched
battlecode.org.

**Timeline and cost.**
- Day 1 (10-07): a design study of galaxy's source (`research/prior/GALAXY.md`) recommended **galaxy-lite**, a
  stdlib-Python re-implementation of siarnaq's rating, matchmaking and ordering plus a saturn-protocol worker. It was
  live within hours (`tools/replica/`, `docs/replica/`).
- Same evening: retired in favour of **the real galaxy**, siarnaq and frontend unmodified at pinned commit `f343088`.
  It was verified end to end by 10-08.
- The replica plus reading prior years took about 56% of week 1's token usage. Budget for it, or reuse this build.

**Architecture** (`docs/galaxy/README.md`; code `tools/galaxy/`):
- **siarnaq unmodified** (Django, gunicorn on 127.0.0.1:8024, PostgreSQL 15 over a unix socket). Postgres rather than
  SQLite, because of `DISTINCT ON` and concurrent writers.
- **Python 3.11 venv**, hash-locked (`tools/galaxy/requirements.txt`, 44 pins, no `google-*`). One shim,
  `py310compat.py`, restores `random.sample` of a dict view; without it every ranked request was a 500.
- **The Google stand-ins** (`tools/galaxy/standins/google/`, back end `replica_gcp/`) shadow the whole `google`
  package. Each implements only what siarnaq calls and raises NotImplementedError otherwise:
  - GCS → a directory per bucket, with atomic writes and same-origin `/storage/` URLs;
  - Pub/Sub → JSON spool files;
  - Cloud Tasks → a spool plus a relay with Cloud Tasks backoff;
  - Cloud Scheduler → a recorded job fired by a systemd timer each minute;
  - Secret Manager → raises;
  - OIDC → HS256 tokens with a local key;
  - Titan → auto "Verified";
  - e-mail → dropped.
  Settings refuse to start unless every `google.*` import comes from the stand-ins, and a unit test forbids network
  imports in them.
- **saturn re-implemented** (`tools/galaxy/saturn.py`, 549 lines). It speaks saturn's message lease/ack/nack and
  report protocol:
  - Compile: zip-slip check, `javac -source 8 -target 8 -proc:none`, then the engine's `instrumenter.Verifier`.
  - Execute: one engine run with all maps (`tools/replica/worker.py match_command`: indicators off, alternate order,
    `-Dbc.server.websocket=false`), with scores from saturn's winner regex.
  - It runs in `PrivateNetwork=yes` (loopback only); its only way out is the relay's unix socket.
  - Slots: 7 execute plus 1 compile on an 8-vCPU / 31 GB VM, about 1 GB each.
  - Replica-only safeguards: a 7,200 s per-game timeout (1,800 s timed out legitimate 540-robot games), and scores
    that don't add up are reported as TRY.
- **The relay** (`relay.py`) is the only caller of siarnaq. It adds ID tokens and Cloud Tasks headers, with 3
  concurrent dispatches per queue.
- **The frontend** is galaxy's own React app, rebuilt for this origin (`tools/galaxy/frontend/`: `replica.patch`,
  `build.sh`, `check_bundle.py`), with local fonts. The viewer is the official client, pinned by hash.
- **Caddy**:
  - basic auth on everything except Bearer `/api/*` calls;
  - a 401 from siarnaq is rewritten to 403 so Chromium keeps its cached Basic credentials;
  - strict CSP (`self` only), so a mis-built bundle cannot reach another host.
- **Egress lockdown**: nftables lets the service user reach only loopback 8023/8024. Hardened systemd units. Host name
  via sslip.io, which occasionally fails DNS.
- **Verification**:
  - `verify.sh`: 116 PASS checks, covering isolation, auth matrix, forged tokens and no external hosts;
  - `e2e.py`: register, team, upload, request, accept, match, replay;
  - `browser_check.py`: headless Chromium walk-through;
  - 46 unit tests (`test/galaxy/test_galaxy.py`) plus 19 field-tool tests.

**Populating it.**
- `tools/galaxy/field.py seed` created 87 field teams, one per public bot, each as its own user, entirely through the
  public API (sign-up, team, zip upload), all with auto-accept.
- `field.py activity` runs field-vs-field ranked challenges in idle capacity, keeping 2 or fewer queued and weighted
  toward under-played teams, so displayed ratings converge.
- Autoscrims use galaxy's own path, every 8 hours. Every 4 hours didn't fit: one round is 176 matches of 3 games,
  about 3-5 hours on 7 engines.
- Hourly limits were raised to 40 unranked and 20 ranked. A request *and* its match both count.

**Operator tools.**
- `results.py`: every finished match → `progress/games.csv` (`galaxy-<id>`, our builds as `us:<pkg>`; idempotent).
- `snapshot.py`: ladder page and chart.
- `prune_replays.py`: deletes field-vs-field replays after 6 hours.
- `cancel-match.sh`: cancels stuck matches.
- `bootstrap.py`: holds episode settings (re-applied on deploy).
- `deploy/{deploy,galaxy-setup,config}.sh`: deployment.

**Gotchas found.**
- **siarnaq rates a team's matches in creation order.** One stuck RUN match froze every later rating for that team
  (21 hours once). Watch for the *oldest* unfinished match by state, not the newest N.
- Journald grew to 2 GB on a 20 GB disk; capped at 300 MB.
- Password reset can't work (no e-mail). Tournaments (Challonge) are unusable. Swagger UI is blank under the CSP.
- The galaxy autoscrim schedule is staff-only; a contestant infers it from when matches appear.
- Replays have no end reason; `reason` is blank in games.csv. Contest replays have no indicators, hence the BCC
  channel (§2.8).

**Reuse for 2025b.** The infrastructure is year-agnostic except:
- the episode name and dates (`bootstrap.py`);
- the engine jar, version and `match_command` flags;
- the viewer pins;
- the replay extension;
- galaxy's pinned commit (check that siarnaq's API and saturn's protocol are unchanged).

The stand-ins, relay, saturn skeleton, Caddy and egress setup, `contest.py`, `ladder_policy.py`, `results.py`,
`field.py` and the verify/e2e scripts should port with path renames. Galaxy-lite (`tools/replica/`) is a lighter
fallback if a full siarnaq deploy is too costly.

---

## 5. Top recommendations for 2025b (synthesis)

1. **Build the measurement first.** On day 1 you need:
   - a seeded paired runner with code-hash provenance;
   - an identity control on the verdict path;
   - `paired.py` and a BT `elolib` with a pair cap;
   - three-way verdicts and a simulated-power gate;
   - a replay reader with census, navstats and bytecode modes.
2. **Run the AUDIT_PROMPT on the first working bot and at every plateau.** It produced the largest gains of both
   years.
3. **Basics battery as absolute bars**: 0 overruns, 0 exceptions (counted in the bot), symmetry never wrong, play
   symmetry (a mirror match is not lopsided), no stuck or sealed spawns, no floating resources.
4. **Reuse the bot skeleton**:
   - the bc23 turn loop and monitor;
   - Nav (greedy+bug, with A7, stall and edge fixes);
   - the BFS distance field for dead ends;
   - observed symmetry with an offline SymTest;
   - a documented comms schema with stamps and expiry;
   - BCC telemetry.
5. **Ladder discipline**:
   - unranked panels for experiments, ranked only with a validated build, parked trials;
   - a two-block t-rule (t >= 1.5, net >= +3);
   - version and refresh the panel;
   - never trust self-play or Swiss winners without field games.
6. **Sources of gains that worked**:
   - basics and bug repairs;
   - cap removals;
   - two-group behaviour-rate contrasts against the bots above us (strike tempo, hold action);
   - ablating stale carried rules;
   - stacking independent near-misses;
   - hazard avoidance;
   - early-economy fixes.

   Sources that failed:
   - reallocations;
   - "more presence" offence;
   - saving units alone;
   - target-specific cracks;
   - elaborate rewrites;
   - self-play parameter searches.

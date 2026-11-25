# TRAINING_ALGORITHM.md

How this project turns compute into playing strength. Written for any season: no unit, resource, map or tool of a
particular year appears here. `HANDOFF.md` maps each step onto this year's tools and paths. Distilled from eight
earlier seasons' records (digests in `research/readings/`); where a rule carries a number it is a measured default
(§9).

**The method in one paragraph.** Build the instruments first, then a bot that clears a basics battery. From then on a
continuous local tournament of our own builds, rated by Bradley-Terry, decides which build is champion. Every new
build is one change on the champion. About half are small tunings, half are big strategy swings, and some copy field
tactics that beat us. A build that clearly out-rates the champion replaces it and goes to the ladder at once. It is
then audited, and its fixes compete as newcomers. Field bots play only on a private ladder replica. They supply ideas
and the progress measure, never a verdict on a build.

## 0. Objective and instruments

**Objective: strength against an unseen field, as the contest ladder measures it.** Beating our own past builds does
not by itself mean beating anyone else. One season gained +311 Elo against its own lineage but only +12 on the
ladder. So the field study steers what we build, the tournament judges builds, and the ladder keeps score.

| instrument | answers | blind to |
|---|---|---|
| rules digest (engine source, each fact cited to file:line) | what is possible, what each action costs, execution order | what wins |
| map census | geometry, symmetry and distances of every map | the opponent |
| replay reader + bot decision counters | how one game unfolded; whether a mechanism fired | frequency, value |
| **local tournament** (our builds, Bradley-Terry over every game) | which build is strongest against our lineage | what the field punishes that we never do |
| ladder replica (field bots under contest rules; the only place they play) | strength against the field; what the field does that we don't | why |
| field replay study (statistics over many replays, delegated) | behaviours that separate our wins from our losses | cause, until a build tests it |

## 1. Foundation first

No strategy work starts until each item below exists and has passed a test with a known answer. Every past
instrument was wrong on its first use, and strategy tried on a broken base measures only the defect.

1. **Rules digest from engine source, not the spec.** For each action: its legality checks, what it costs and when.
   Also: execution order within a round, the win and tiebreak conditions exactly as coded, and every point where the
   spec disagrees with the engine. Most hidden limits and free actions are found here.
2. **Map census**: size, symmetry, spawn geometry, resources and key distances for every map. Something that holds on
   every map is a constant, never something to sense.
3. **Runner**: headless and parallel, with a wall-clock cap, no network for bots, and machine-wide concurrency slots.
   It writes one row per game: builds by content hash, map, seats, seed, winner, how it ended, rounds, exceptions,
   overruns and per-side counters. Results are resumable and keyed by (build A, build B, map, seed).
4. **Determinism**: the map seed controls the engine's randomness, so every game gets an explicit seed. Identical
   builds give identical games. That is a test of the pipeline, not a statistical result.
5. **Replay reader**: per-round team aggregates, per-turn unit state, every action, and an ASCII board at any round.
   It is checked against the engine's own aggregates on every round of a real game (the mismatch counter must read
   0).
6. **Bot architecture**: a turn loop, globals, map memory, symmetry, navigation and a handler per role. Every tunable
   is a named constant, so a variant is a short edit.
   - The turn loop is the **compute monitor** from the first commit. It counts overruns (the turn ended in a later
     round than it started) and exceptions.
   - **Symmetric decisions**: no fixed compass order, no first-of-a-scan, no hard-coded team constants, and no shared
     fixed-seed RNG as a tie-break. All of these have hidden side biases of 45 points for whole seasons.
   - **Symmetry by elimination**: keep the set of candidate symmetries and remove a candidate only when a tile seen
     contradicts it. Never let the set empty, and never assume one.
   - **Navigation**: greedy toward the goal, with wall-following around terrain and a stall exit. Wait a turn or two
     for robots in the way before walking around them.
   - Static fields are per robot; a new robot first acts in the round after it is built; sensing scans run row by
     row, not by distance.
7. **Bytecode tag**: contest replays drop debug strings. The bot can still pad its compute so that the recorded
   bytecode count encodes a small decision code (count mod 64 or 128). The replay reader decodes it.
8. **Snapshot tool**: freezes a build under its own name and package, permanently. A variant tool makes the champion
   plus a list of constant edits.
9. **Unit tests**: a fake game controller (a proxy over the controller interface backed by a tiny world) tests the
   bot's logic; fixtures test the tools. **Run them after every change.** They have caught looping navigation and
   inverted geometry before a single game was played.
10. **Field bots**: found, downloaded, security-scanned (never read) and compiled by script.
11. **Private ladder replica**, isolated from the official contest, played as a contestant through its API.
12. **Basics battery** (absolute bars, run on the champion): no idle producer, no stuck unit, no unforced death, zero
    overruns and exceptions, and each unit's worst turn at most 90% of the limit. While a row fails, candidates come
    from it first.

**Foundation bar**: the build beats the starter from both seats on every map, clears the battery and is on the
replica. That build is the first champion.

## 2. The loop: a continuous local tournament

### 2.1 Pool and names
- About **10 bots**: the champion plus newcomers, half incremental and half swings. Refill whichever kind is short.
- The pool file lists active bots. Retired bots stay as comments, unscheduled, but their games keep anchoring the fit.
- Name prefixes tell the kinds apart (e.g. `yNN` tunings, `swNN` swings, `fxNN` audit fixes, `cpNN` copied field
  tactics). A swing table records each strategy and its fate.

### 2.2 Ratings and the champion
- **One Bradley-Terry fit over every local game** between pool or retired bots: any seat, any seed, the contest's map
  set. Each pair is capped at 200 games, and a weak prior keeps unplayed bots finite.
- **A bot becomes champion when it has at least MIN_GAMES games and leads the champion by more than one combined SE**,
  √(SE₁² + SE₂²). The margin is hysteresis, so near-equal bots do not trade the title on noise.
- **Early ratings mean little**: swings of ±70 before about 50 games, and new champions usually settle downward. Never
  retire a bot or celebrate one before about 50 games.

### 2.3 Building candidates
- **Every build is made on the current champion**, so a rating difference has one cause: one change, or one coherent
  strategy for a swing.
- **Show the mechanism fires before rating it.** Check one logged game, or the decision counters, before the build
  enters the pool. A change that compiled but never ran was the commonest failure in every season (162 of 162 games
  identical once).
- For a numeric change, try several sizes, zero included: optima are two-sided.
- Log each build in the attempts table with its base, change and motivation.

### 2.4 Scheduling
- A run is a fixed number of games, each on a random map from the contest set with a random seed and random seats.
- Newcomers under NEW_MIN games get half of each run, weighted by the games they lack. Half of those are against the
  champion.
- The rest goes to pairs among the top bots, weighted toward close ratings and large SEs.
- Count planned-but-unplayed games so consecutive plans don't over-feed one newcomer. Take a queued run off the queue
  before re-planning it.

### 2.5 Crowning
In one cycle: submit the champion to the ladder; record it (time, bot, base, change, submission); make the working bot
a copy of it; log it; refresh progress; commit. Expect ladder dips: the tournament, not the ladder, judges builds.

### 2.6 Retiring
Retire a bot far below the champion after about 200 games, or more than 2 SE below after about 50. A losing swing
first gets a second version that fixes its first visible failure.

### 2.7 Auditing a new champion
Once the queue is full, audit the diff from the previous champion only:
- logic slips;
- mirror slips (choices that differ between seats on a symmetric map);
- latent special values;
- dead or misleading code.

Bring the shared unit suite to passing, and add a test for every new mechanism and constant. **Fixes enter as
newcomers and are never patched into the champion**: long-lived bugs can be load-bearing. One season's first fix
bundle rated 118 below the champion it fixed. Behaviour-neutral cleanups ride along with the next newcomer.

## 3. Where candidates come from

1. **Basics battery failures**: these come first while any row fails.
2. **Field study**: behaviours that separate the champion's ladder wins from its losses. Study opponents we beat 25-75%
   of the time; studying only losses misleads. Delegate studies of 100+ replays and compare behaviour *rates*.
3. **Copy what beats us.** When a field bot's tactic wins against us, reproduce the behaviour, confirm in a replay
   that it is reproduced, then rate it. In one season, 10 of 11 copied builds were judged without the behaviour ever
   appearing.
4. **Trace one replay for stalls**: a resource stuck in a narrow band, a unit oscillating, production stopping, a
   counter that never fires.
5. **Ablation**: switch off each carried feature in turn. One stale rule has more than once been the biggest drag.
6. **Re-tests on a new base**: a change that lost on an old champion can win on a new one. Label repeats as such.
7. **Big swings**: a strategy, not a dose. Examples: a different economy, opening, army doctrine, target priority or
   style. Price the economy first: bigger armies starve. Try opposites (greed after a failed blitz), and combine
   swings that each hold level with the champion.

**What has paid off across seasons**: fixing our own bugs and basics, removing binding caps, cost-free defences,
spending idle resources, opening deployment, and mirror-safe tie-breaks. **What mostly hasn't**: reallocating
resources between unit types, "more presence" offence, keeping units alive by making them do less, plans needing
multi-unit coordination, self-play parameter searches, and fixes aimed at one opponent. The cheap tournament can still
try them, but expect less.

**Balance**: keep at least one swing in the pool at all times. After three straight losers in one area (economy,
production, movement, combat, defence, scouting), build in another area.

## 4. Statistics
- Bradley-Terry with a weak prior and a per-pair cap. Compare ratings only within one fit.
- Use the lead over the champion with a combined SE, never the rank. A lead under one SE is a tie, and a tie keeps the
  champion.
- Games are deterministic per (pair, map, seed, seats). Re-running a borderline result adds nothing; new seeds do.
- One game filters an idea; it never decides one.
- Self-play blind spots are accepted risk, corrected by the field study and by the next champions.
- Ladder ratings drift upward over a season. Judge progress by rank and by the gap to reference places (#5, #10, #20).

## 5. The ladder replica
- **Only the champion plays ranked matches**; field bots play only there, within contestant request limits. Locally,
  only our own builds play.
- Challenge bots slightly above and slightly below us; spare capacity goes to field-vs-field matches.
- Check the champion's new matches every cycle, and look hardest at losses to the teams just above.
- Keep it healthy:
  - disk above the floor, with automatic pruning;
  - liveness alarms (a dead queue once went unnoticed for 40 hours);
  - a stuck match freezes ratings, which are applied in creation order;
  - a match plays whichever submission is active when the match is created.
- Nothing we run may touch the official contest infrastructure.

## 6. When the champion stops changing
Enter at the plateau trigger (§9). Stopping is never an outcome. Escalate:
1. more and bigger swings, designed from a fresh field study;
2. a correctness audit of bot and instruments, one lens at a time: code never reached; rules and API; stale shared
   state; what replays show units doing; the tournament pipeline (a renamed copy of the champion must rate level);
3. ablate everything carried, and sweep the engine and API for capabilities never used;
4. revisit other years' principles through permitted sources only;
5. a rewrite that keeps the proven infrastructure, when the architecture is the ceiling.

A failed build condemns one implementation, not the idea.

## 7. Operations
**Prod cycle (about 20 minutes)**:
1. Check the game machine.
2. Pull and rank.
3. Crown if a bot qualifies.
4. Keep at least 5 runs queued.
5. Audit a new champion.
6. Add and retire bots to hold about 10.
7. Check the champion's ladder matches.
8. Log, commit and push.
9. Refresh the charts.
10. Report:
    - tournament size and the pool table (rating ± SE, games, lead over the champion and the lead it needs);
    - changes since the last cycle;
    - audit outcome;
    - ladder rank;
    - machine and replica health.

**Hygiene**:
- Rules live in tools that refuse; prose is forgotten.
- Kill by pid, never by pattern.
- Never edit a running script.
- Commit explicit paths and push after every commit.
- Take times from the system clock, in the owner's zone.
- Delegate reading, not deciding.
- Never wait inside a turn for a job, an idea or an approval.

**Owner**:
- Record every prompt verbatim in `PROMPTS.md`.
- Turn standing instructions into this document and into memory.
- Answer questions from data.
- Make procedure decisions without asking, and log the reason.

## 8. Records
- **Training log** (append-only): numbers each cycle, newcomers, retirements, directives.
- **Attempts table**: one row per build with base, change, motivation and fate.
- **Champion history**, pool file, swing table, audit reports and field-study write-ups.
- **Progress charts on wall-clock axes**: local champion rating, ladder rank and rating, with milestones marked.

Records hold measurements, not stories, and nothing stale stays.

## 9. Defaults

| parameter | default |
|---|---|
| pool | about 10 bots: champion + newcomers, half incremental, half swings |
| champion rule | ≥ MIN_GAMES = 200 games and a lead > √(SE₁² + SE₂²) over the champion |
| newcomer share | bots under NEW_MIN = 40 games get half of each run, half of that vs the champion |
| run | 120-200 games, random contest map, random seed in 0-9, random seats |
| fit | Bradley-Terry, weak prior, ≤ 200 games per pair, retired bots' games kept |
| retire | far below after ~200 games, or > 2 SE below after ~50; swings get a second version first |
| queue | ≥ 5 runs queued past the next cycle |
| cycle | about every 20 minutes |
| plateau | champion unchanged for 12 hours, or 10 straight newcomers below it |
| compute | 0 overruns and 0 exceptions in the champion; worst turn ≤ 90% of the limit |
| replica disk | ≥ 2 GB free; prune old replays below 4 GB |

# tools/galaxy25: the private Battlecode 2025 contest site

The bc25 replica is a private copy of the official judging site, galaxy (siarnaq backend and React frontend), plus a
local stand-in for saturn, the game runner. It runs on the VM `battlecode-dev` and plays only the pinned Battlecode
2025 Java engine (`engine/battlecode25-java-3.1.0.jar`, sha256 in `engine/SHA256SUMS`) on the 75 maps built into
that jar. It is a port of the bc26 replica (`~/projects/vibe/2026b/tools/galaxy26`, torn down 2026-11-25), itself
ported from the 2023 and 2019 replicas. It shares no files, units, users, database or nftables table with them.
`ACCESS.md` at the repository root explains how the owner opens it.

- Site: **https://galaxy25.136-86-167-127.sslip.io/** (the host name follows the VM's external IP; see "Host name").
- Galaxy source: commit `f343088` of github.com/battlecode/galaxy (MIT; the commit every earlier replica used).
  `deploy.sh` makes a `git archive` of it from `~/projects/vibe/reference/galaxy`, and `galaxy-setup.sh src` refuses
  any archive that is not of that commit. siarnaq runs unmodified.
- Episode `bc25` ("Battlecode 2025", language `java21`, release versions 3.1.0, game release 2025-01-07 00:00 UTC as
  the official `bc25java`): all 75 built-in maps public (`maps.txt`); ranked scrimmages are on; the hourly limits
  are 20 ranked and 40 unranked requests; autoscrim is scheduled `0 */8 * * *` UTC but fires only while the
  scheduler timer is on (installed disabled). The superuser is `owner`.

## Deviations from the official site

- Episode id `bc25`, not `bc25java`; there is no `bc25python` episode, and Python/Scala submissions are not built.
  galaxy's frontend at `f343088` defaults to `bc26`: `replica.patch` makes `bc25` the default and shows the official
  `bc25java` content pages (quick start, resources, ...) for it, with their internal links pointed at `/bc25/`.
- Engine 3.1.0 (the pinned jar, = `release_version_public`). The official saturn ran 3.1.2 (`release_version_saturn`
  of the public episode record); a 3.1.2 jar is not used here.
- Maps: the 75 maps in the 3.1.0 jar (`battlecode/world/resources/*.map25`) are all public. The official site's
  public map list changed over the season (sprint / qualifier maps); it is not reproduced.
- saturn plays one engine run per map (below) and merges the replays; results equal the official multi-map run.
- No e-mail, no OAuth, no Sentry, no tournaments, no resume/eligibility uploads beyond what siarnaq does locally.
- A site-wide basic-auth gate (user `owner`) in front of everything.
- Replays open in our own build of the official 3.1.0 web client at `/viewer/` instead of releases.battlecode.org.

## Isolation

- **No Google Cloud and no battlecode.org.** `standins/google` shadows the `google.*` packages siarnaq imports.
  `replica_gcp` provides local Pub/Sub, Cloud Tasks, Cloud Scheduler, Secret Manager, GCS and OIDC: spool
  directories, files under `/srv/bc25-galaxy/storage/<bucket>`, and HMAC tokens. Email, OAuth and Sentry are off.
  `replica_settings.py` refuses to start if a `google` module comes from anywhere but the stand-ins. The venv is
  built from the hash-locked `requirements.txt` with `--require-hashes --no-deps`, and setup fails if any google
  package lands in it.
- **Egress.** The nftables table `inet bc25_replica_egress` limits uid `bc25replica`, which runs every service, to
  loopback port 8025 (siarnaq). It cannot reach the internet, the DNS stub or Caddy, and the GCE metadata server is
  dropped. All units sit in `bc25-replica.slice` (`IPAddressDeny=any`, `IPAddressAllow=localhost`). saturn also has
  `PrivateNetwork=yes`. Host-wide, the table `inet bc25_official_block` rejects the addresses of battlecode.org,
  www/api/play/releases.battlecode.org (resolved at setup, plus the ones recorded on 2026-10-21) for every user.
  Loaded at boot by `bc25-replica-egress.service`.
- **Frontend.** galaxy's own frontend is built on the VM (`frontend/build.sh`) from the pinned commit with
  `replica.patch` applied: same-origin backend (`VITE_BACKEND_URL` empty instead of api.battlecode.org); the site
  URL; a bc25 Replay! link to `/viewer/index.html?gameSource=...`; self-hosted fonts; a CSP meta tag; email
  verification off; default episode `bc25`; and the optional project milestones (`/milestones.json`, from
  `progress/milestones.csv` when that exists) drawn as dashed lines on the rating charts (no file = no lines). It
  installs with `npm ci --ignore-scripts`. `frontend_check.py` audits each build and each install: no URL of
  another host is fetched without a click, battlecode.org appears only as hyperlinks, and the CSP is present.
- **Viewer.** The official Battlecode 2025 web client (battlecode25 repo `client/` + `schema/`, commit `35574f3`,
  tags `client.3.1.0` = `engine.3.1.0`, GPL-3.0) is built on the VM by `viewer/build.sh` from a `git archive` of that
  commit (`~/projects/vibe/reference/battlecode25`). The build removes the Google Fonts link and the desktop-only git
  dependency `where-is-it`, and adds the CSP meta tag. It runs `npm ci --ignore-scripts` (Electron and Tauri binaries
  are not fetched) and the same bundle audit.
- **Caddy.** This replica runs its own Caddy 2.11.7 (`/usr/local/lib/bc25-galaxy/caddy`, the pinned GitHub release,
  sha256-checked by `galaxy-setup.sh caddybin`; `bc25-replica-caddy.service`, user `bc25caddy`,
  `/etc/bc25-galaxy/Caddyfile`, data in `/var/lib/bc25-caddy`) with Let's Encrypt, a basic-auth gate (user `owner`),
  and a strict Content-Security-Policy (`connect-src 'self'` etc.). It holds ports 80/443 (free since the bc26 and
  bc23 replicas were removed; `bc23-replica-caddy` is still only ever queried, never touched).
- **Bot code.** Every compile and every game runs under `sandbox.sh` (`unshare --user --net --mount`): no network
  at all, and a read-only view of everything but its own work directory. The sandbox fails closed if any reachable
  writable mount is left. Each game is its own JVM with a heap cap and a wall limit.

## saturn.py (the game runner)

It keeps saturn's message and report protocol: Pub/Sub spool → slot leases → task recipe with step logs → reports
through the relay's unix socket → siarnaq. Galaxy itself has no changes.

- **Compile** (as `saturn/pkg/run/java.go`): unzip the submission (zip-slip check, 64 MiB limit); `javac --release 21
  -proc:none` against the engine jar; the engine's `battlecode.instrumenter.Verifier <package> <classes>`; upload
  the class tree as the binary. The user's own failures are reported `OK!` with accepted=false and the log tail;
  infrastructure failures are retried. Java only.
- **Execute.** The same engine properties as the 2025 scaffold's `gradlew run` with saturn's settings: indicators
  off, robot output not on stdout, `validate-maps=true`, profiler and debug methods off, team names = siarnaq team
  names, each team with its own package and class directory. Winner and score use saturn's regex
  `(?m)^\[server\]\s*.*\(([AB])\) wins \(round N\)$`; checked against the 3.1.0 engine (`Server.getWinnerString`
  prints `<package> (A) wins (round N)` then `Reason: ...` through `say`, i.e. with the `[server]` prefix). The score
  is games won.
- **Deviation: one engine run per map.** The official saturn runs all of a match's maps in one engine run. Here each
  map is its own run, so a finished game survives a saturn restart or a failed attempt: it is kept in
  `$GALAXY_HOME/saturn/resume/<key>` until the message is acked, at most 3 days. For an alternate-order match,
  games 2, 4, ... play a copy of the map with teams reversed (`runtime/maps-reversed`, written by
  `java/Bc25Tool reverse-maps` with the 2025 engine's own `GameMapIO.loadMap(name, dir, teamsReversed=true)` +
  `writeMap`), exactly what the engine's multi-map run does (`Server.run`: `teamsReversed` flips after each game when
  `bc.server.alternate-order`). Checked on 2026-11-25 with examplefuncsplayer vs a reseeded copy on Bread,
  DefaultSmall, Flower: the per-map games equal the native 3-map alternate-order run game for game (winner, win type,
  rounds), and the reversed map changes the outcome where it should (Bread: B wins, reversed: A wins).
  `Bc25Tool check-maps`: all 75 maps load both ways and pass `LiveMap.assertIsValid`.
- **One replay per match.** `replay_merge.py` merges the per-game replays into one `.bc25` file (one GameHeader, every
  game in order, the GameFooter of a game the overall winner won), uploaded where siarnaq expects the replay. The
  2025 schema (`schema/battlecode.fbs` at `35574f3`) has the same GameWrapper / EventWrapper / MatchHeader /
  MatchFooter layout as 2026; only the WinType enum differs (`RESIGNATION, MAJORITY_PAINTED, ALL_UNITS_DESTROYED,
  AREA_PAINTED, MORE_TOWERS, MORE_MONEY, MORE_STORED_PAINT, MORE_ROBOTS, COIN_FLIP`). A merged 3-game match parses
  with the engine's own flatbuffer classes (`Bc25Tool replay-info`) and opens in the viewer.
- **Limits** (`/etc/bc25-galaxy/galaxy.env`; override in `/etc/bc25-galaxy/local.env`, then restart saturn):

  | variable | default | meaning |
  |---|---|---|
  | `GALAXY_EXECUTE_SLOTS` | 4 | concurrent matches (cap 8) |
  | `GALAXY_GAME_TIMEOUT` | 3600 | wall seconds per game |
  | `GALAXY_GAME_HEAP_MB` | 2048 | `-Xmx` per game JVM |

  The unit also has `MemoryMax=22G` and `CPUQuota=800%`. The engine meters bytecodes, not wall time, so
  contention slows games but changes none.

## Parts

| file | role |
|---|---|
| `saturn.py`, `sandbox.sh`, `replay_merge.py`, `java/Bc25Tool.java` | game runner (above). `Bc25Tool`: `reverse-maps`, `check-maps`, `replay-info`. |
| `relay.py` | relay saturn → siarnaq, and the Cloud Tasks / Scheduler stand-in (`fire-jobs`, run each minute by `bc25-galaxy-scheduler.timer` when enabled). |
| `replica_settings.py`, `replica_gcp/`, `standins/`, `py310compat.py` | siarnaq's settings (`Replica` configuration) and the Google Cloud stand-ins. |
| `bootstrap.py`, `maps.txt` | episode `bc25` + 75 maps, service user, superuser `owner`; `status`, `audit`, `purge-teams PREFIX`. |
| `client.py` | API client + CLI as a contestant: register, submit, request, matches, fetch. Accounts in `~/.bc25-galaxy/accounts.json` (600). |
| `contest.py` | our team `vibe25b` (below). |
| `field.py`, `field-teams.tsv` | field teams: `plan`, `scan`, `seed`, `status`, `queue`, `activity`, `boost`, `rate`. |
| `browser_check.py` | headless-Chromium end-to-end walk through the site, through the replay in the viewer (on the VM). |
| `verify.sh` | the isolation and health checks (egress, no Google code, bundles, services, gate). |
| `frontend/`, `viewer/`, `frontend_check.py` | frontend and viewer builds + bundle audit. |
| `deploy/deploy.sh`, `deploy/galaxy-setup.sh`, `vm.sh` | deployment from the driver (idempotent, per step). |
| `deploy/replay-prune.sh` | disk guard carried over from bc26 (prunes replays older than a day when / has < 4 GB free); not installed. |
| `rating_unstick.py`, `spool_bump.py`, `drain-loop.sh` | operator repairs and the panel drain loop carried over from the earlier replicas (their headers). |

## Operating it

```
tools/galaxy25/deploy/deploy.sh            # full (re)deploy; or deploy.sh STEP: status | app | runtime | env | units |
                                           # start | stop | viewer | frontend | milestones | site | caddybin |
                                           # scheduler on|off | activity on|off
bash tools/galaxy25/verify.sh              # isolation + health checks (runs on the VM over ssh)

# rebuild the frontend / viewer on the VM (as the operator), then install them
gssh 'bash ~/bc25-galaxy-stage/tools/galaxy25/frontend/install-node.sh'      # once (node v24.21.0, sha256-pinned)
gssh 'bash ~/bc25-galaxy-stage/tools/galaxy25/frontend/build.sh'
gssh 'bash ~/bc25-galaxy-stage/tools/galaxy25/viewer/build.sh'
tools/galaxy25/deploy/deploy.sh frontend; tools/galaxy25/deploy/deploy.sh viewer

# our team (credentials ~/.bc25b-galaxy-team, 600)
python3 tools/galaxy25/contest.py register
python3 tools/galaxy25/contest.py submit [PKG_DIR] [-m TEXT]     # default: the scaffold's examplefuncsplayer ($GALAXY25_BOT)
python3 tools/galaxy25/contest.py ladder
python3 tools/galaxy25/contest.py scrim --n 4                    # ranked above, unranked below
python3 tools/galaxy25/contest.py scrim --vs bc25-example,bc25-example-copy@+   # @+ / @-: fixed side, unranked
python3 tools/galaxy25/contest.py matches [--all]
python3 tools/galaxy25/contest.py fetch --new        # ~/projects/vibe/bc25b-galaxy-replays/<id>/{replay.bc25,match.json}
python3 tools/galaxy25/contest.py results

# field
python3 tools/galaxy25/field.py scan                   # rows for ~/projects/vibe/bc25b-benchmarks/<team>/ (zip or package)
python3 tools/galaxy25/field.py plan                   # what seed would upload (no network)
python3 tools/galaxy25/field.py seed                   # teams of field-teams.tsv (examplefuncsplayer x2 now)
python3 tools/galaxy25/field.py status | queue
python3 tools/galaxy25/client.py request vibe25b bc25-example --maps DefaultSmall,Bread,Flower
python3 tools/galaxy25/client.py request vibe25b bc25-example --ranked

# end-to-end in a real browser (on the VM; Debian's chromium is installed there), then clean up
gssh 'python3 -I ~/bc25-galaxy-stage/tools/galaxy25/browser_check.py --out ~/bc25-galaxy-build/browser'
gssh 'sudo bc25-galaxy-manage bootstrap purge-teams e2e-'
```

`match.json` (written by `contest.py fetch`) has one record per game, read from the replay: map, team A/B,
`reversed` (game i of an alternate-order match, i even counting from 1), winner, rounds, win type (2025 WinType
names). In panel comparisons, a "side" is the start position (A or B of the map) our team played from.
`contest.py ... --graded` needs `tools/field_report.py`, which this repository does not have yet.

### Field teams from downloaded bots

`field-teams.tsv` rows are `team<TAB>location<TAB>about`. A location is a Java package directory, a submission zip
(`<package>/RobotPlayer.java ...`, the package is read from the zip), or a directory holding exactly one such zip,
which is the layout of `~/projects/vibe/bc25b-benchmarks/<team>/`. `field.py scan` prints a row (or a `#` note
saying why not) for every directory there; append the wanted rows to the table and run `field.py seed`. Re-seeding
skips teams whose uploaded content is unchanged.

## Timers (installed DISABLED)

- **Autoscrim** (galaxy's ranked round over every team, `0 */8 * * *` UTC): `tools/galaxy25/deploy/deploy.sh
  scheduler on` enables `bc25-galaxy-scheduler.timer`. Each minute it runs `relay.py fire-jobs`, which posts the due
  autoscrim job to siarnaq. The replica-only throttle `GALAXY_SCHED_MAX_WAITING` (30) holds a due autoscrim while
  30 or more matches wait. `deploy.sh scheduler off` disables it.
- **Field activity** (field teams challenge teams near their rating while fewer than 2 matches wait): the unit runs
  `field.py activity` as the operator on the VM. It reads accounts from `~/.bc25-galaxy-field/accounts.json` there.
  To enable it:

  ```
  gssh 'mkdir -m 700 -p ~/.bc25-galaxy-field'
  python3 -c "import json,os; a=json.load(open(os.path.expanduser('~/.bc25-galaxy/accounts.json'))); \
    print(json.dumps({k:v for k,v in a.items() if k != 'vibe25b'}))" | gssh 'umask 077; cat > ~/.bc25-galaxy-field/accounts.json'
  tools/galaxy25/deploy/deploy.sh activity on          # off: deploy.sh activity off
  ```

## Deploying a change to saturn or the runtime

`deploy.sh app` (code) and `deploy.sh runtime` (JDK, engine, maps from the jar, reversed maps) swap files under the
running services. saturn picks them up only on `sudo systemctl restart bc25-galaxy-saturn`. Matches in flight go
back to the queue and resume from their first unfinished game. Afterwards, watch `journalctl -u bc25-galaxy-saturn`.

## Host name and reboots

`bc25-replica-hostname.service` reads the external IP from the metadata server at boot and writes
`/etc/bc25-galaxy/hostname`. It re-renders the Caddyfile and restarts siarnaq if the IP changed. `deploy.sh` also
stores the URL in `~/.bc25-galaxy/site` on the driver. After a reboot, check `tools/galaxy25/deploy/deploy.sh status`.

## Units and paths on battlecode-dev

Units: `bc25-galaxy-web` (gunicorn 127.0.0.1:8025), `bc25-galaxy-relay`, `bc25-galaxy-saturn`,
`bc25-replica-egress`, `postgresql@15-bc25` (unix socket only, port 5425, database `siarnaq25`; `pg_hba` host lines
set to reject), `bc25-replica-caddy`, `bc25-replica-hostname`, plus `bc25-galaxy-scheduler.timer` and
`bc25-galaxy-activity` (both disabled).

Paths:
- `/opt/bc25-galaxy`: `src/` (galaxy), `venv/`, `galaxy25/` (this directory), `runtime/` (JDK 21, engine, maps,
  maps-reversed, tool).
- `/srv/bc25-galaxy`: frontend, viewer, static, storage (replays under
  `storage/bc25-replica-secure/episode/bc25/replays/`).
- `/home/bc25replica/galaxy`: secrets, spool, saturn work and resume.
- `/etc/bc25-galaxy`: env, local.env, Caddyfile, egress.nft, owner password (root 600), owner.bcrypt, hostname,
  audit outputs.
- `/usr/local/lib/bc25-galaxy`: `galaxy-setup.sh` (for the boot-time host name refresh) and `caddy`.
- CLI: `sudo bc25-galaxy-manage <manage.py command> | bootstrap ... | relay status | saturn status`.
- Teardown: `sudo /usr/local/lib/bc25-galaxy/galaxy-setup.sh teardown [--purge-data]`.

Secrets live only on the VM and in the driver's home: `~/.bc25b-replica-password` (gate + `owner`),
`~/.bc25b-galaxy-team` (our team), `~/.bc25-galaxy/accounts.json` (all team accounts). None is in git.

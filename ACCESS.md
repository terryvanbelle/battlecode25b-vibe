# ACCESS.md: how to look at the bc25 scrimmage ladder

Our practice contest runs on a private copy of the Battlecode website on our VM `battlecode-dev`: galaxy's own
frontend and backend, the same pages as play.battlecode.org, with the Battlecode 2025 engine 3.1.0. Nothing there
touches the real play.battlecode.org. How it is built and run: `tools/galaxy25/README.md`.

## Open the site

1. Go to **https://galaxy25.136-86-167-127.sslip.io/**
2. The browser first asks for the site password. This gate sits in front of everything. User: **`owner`**.
   Password: run `! cat ~/.bc25b-replica-password` in this Claude Code session. The password is not in this
   repository.
3. Then log in on galaxy's own login page (Log in, top right) as **`owner`** with the same password. `owner` is the
   site's superuser. It sees every team, match and replay, and `/admin/` (Django admin; read there, change nothing).

## To watch our games (replays)

Galaxy shows Replay buttons only on a team's own pages, so watch as our team, not as `owner`:

1. If you are logged in to galaxy as `owner`, log out (top right). Then log in as **`vibe25b`**. Password: run
   `! sed -n 2p ~/.bc25b-galaxy-team`.
2. In the left sidebar, open **Scrimmaging**, then **Scrim History**. It lists our matches, newest first. Press
   **Replay!** on a match to open the Battlecode 2025 client (`/viewer/`) on it. One file holds every game of the
   match; the client's game picker switches between them.
3. Replay files are also on disk:
   - `python3 tools/galaxy25/contest.py fetch --new` downloads our finished matches to
     `~/projects/vibe/bc25b-galaxy-replays/<match id>/replay.bc25`, with a `match.json` per-game summary. Open
     `replay.bc25` in any Battlecode 2025 client.
   - On the VM, they are under `/srv/bc25-galaxy/storage/bc25-replica-secure/episode/bc25/replays/`.

**Queue** (sidebar) lists every match on the ladder, with teams, scores and rating changes. As on
play.battlecode.org, it has no replays, because galaxy hides other teams' scrimmage replays from contestants.

## What is there (episode bc25, galaxy's own pages)

- **Rankings** (`/bc25/rankings`): every team and its rating (galaxy's displayed rating, a penalized Elo: every team
  starts at 0 and climbs over its first ranked matches).
  - Our team is **vibe25b**.
  - The test/field teams are **bc25-example** and **bc25-example-copy**, both the official examplefuncsplayer.
- **Queue** (`/bc25/queue`): every match, newest first, with status, score and rating change.
- **Team pages** (click a team name): profile, members, rating history.
- **Scrimmaging**, **Submissions**, **My Team**: the logged-in team's own pages.
  - Submissions take a zip of the Java package folder, `<package>/RobotPlayer.java ...`, which is what the
    scaffold's `zipForSubmit` makes. The package name goes in the form.
  - The site compiles it with JDK 21 against engine 3.1.0 and checks it with the engine's Verifier.
- All 75 maps built into the engine are public. A match is played on 3 maps (ranked: galaxy picks them at random);
  the score is games won.

Automatic play is **off** for now:
- galaxy's 8-hourly ranked round (autoscrim);
- the field teams' spare-time challenges.

Matches happen when a team requests them. Turning those on is described in the README, under "Timers".

## If the address stops working

The host name is built from the VM's external IP, which changes if the VM is stopped and started. A boot script
picks up the new IP and the certificate is renewed. `~/.bc25-galaxy/site` on the driver holds the current URL after
`tools/galaxy25/deploy/deploy.sh status`. If the site is unreachable, ask me.

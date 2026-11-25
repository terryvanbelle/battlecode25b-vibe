#!/usr/bin/env bash
# Deploy (or redeploy) the bc25 galaxy replica on battlecode-dev from the driver. Idempotent. Doc: tools/galaxy25/README.md.
#   tools/galaxy25/deploy/deploy.sh              push the stage, then galaxy-setup.sh all
#   tools/galaxy25/deploy/deploy.sh STEP [ARG]   push the stage, then one galaxy-setup.sh step (status, app, runtime,
#                                                units, start, viewer, frontend, milestones, site, scheduler on|off,
#                                                activity on|off ...)
# The stage on the VM (~/bc25-galaxy-stage) holds tools/galaxy25, engine/ (the pinned 3.1.0 jar; its 75 built-in
# .map25 maps are the episode's maps), galaxy.tar (git archive of the pinned galaxy commit, from the reference clone),
# viewer-src.tar (git archive of client/ and schema/ of the pinned battlecode25 commit, for viewer/build.sh),
# example/src/examplefuncsplayer (battlecode25-scaffold, for browser_check.py) and, when progress/milestones.csv
# exists, milestones.json (drawn on the site's rating charts). Nothing is downloaded from battlecode.org.
# Afterwards the driver has the site gate password (~/.bc25b-replica-password, 600) and the site URL (~/.bc25-galaxy/site).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$HERE/../../.." && pwd)"
# shellcheck source=../vm.sh
source "$REPO/tools/galaxy25/vm.sh"; ensure_vm
[ "$(hostname -s)" != battlecode-dev ] || { echo "deploy: run this on the driver" >&2; exit 1; }
STAGE=bc25-galaxy-stage
GALAXY_REF="${GALAXY_REF:-$HOME/projects/vibe/reference/galaxy}"
GALAXY_COMMIT=f343088f4d471b0664b2ff41129f0435a8dca1c2
BC25_REF="${BC25_REF:-$HOME/projects/vibe/reference/battlecode25}"
CLIENT_COMMIT=35574f3eb03c38318623709687fd09346a4de8ca     # tags client.3.1.0 = engine.3.1.0
SCAFFOLD_REF="${SCAFFOLD_REF:-$HOME/projects/vibe/reference/battlecode25-scaffold}"
RS=(rsync -a --delete --exclude __pycache__ -e "ssh ${SSHO[*]}")
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

echo "== stage ~/$STAGE on $VM"
gssh "mkdir -p ~/$STAGE/tools"
"${RS[@]}" "$REPO/tools/galaxy25/" "$USER_NAME@$IP:$STAGE/tools/galaxy25/"
"${RS[@]}" --include 'battlecode25-java-3.1.0.jar' --include SHA256SUMS --exclude '*' "$REPO/engine/" "$USER_NAME@$IP:$STAGE/engine/"
gssh "mkdir -p ~/$STAGE/example/src"
"${RS[@]}" "$SCAFFOLD_REF/java/src/examplefuncsplayer/" "$USER_NAME@$IP:$STAGE/example/src/examplefuncsplayer/"
git -C "$GALAXY_REF" archive --format=tar -o "$TMP/galaxy.tar" "$GALAXY_COMMIT"
git -C "$BC25_REF" archive --format=tar -o "$TMP/viewer-src.tar" "$CLIENT_COMMIT" client schema
extra=()
if [ -f "$REPO/progress/milestones.csv" ] && [ -f "$REPO/tools/milestones.py" ]; then
  python3 -I "$REPO/tools/milestones.py" json "$TMP/milestones.json"   # progress/milestones.csv -> the rating charts
  extra=("$TMP/milestones.json")
fi
rsync -a --checksum -e "ssh ${SSHO[*]}" "$TMP/galaxy.tar" "$TMP/viewer-src.tar" "${extra[@]}" "$USER_NAME@$IP:$STAGE/"

SETUP="sudo bash ~/$STAGE/tools/galaxy25/deploy/galaxy-setup.sh"
if [ $# -gt 0 ]; then
  case "$1" in
    stage) exit 0 ;;
    all|app|runtime|src|venv|milestones) gssh "$SETUP $1 ~/$STAGE" ;;
    *) gssh "$SETUP $*" ;;
  esac
else
  gssh "$SETUP all ~/$STAGE"
fi

echo "== driver: gate password and site URL"
umask 077
gssh 'cat ~/.bc25b-replica-password 2>/dev/null' > "$HOME/.bc25b-replica-password.new" || true
if [ -s "$HOME/.bc25b-replica-password.new" ]; then mv -f "$HOME/.bc25b-replica-password.new" "$HOME/.bc25b-replica-password"
else rm -f "$HOME/.bc25b-replica-password.new"; fi
chmod 600 "$HOME/.bc25b-replica-password" 2>/dev/null || true
host=$(gssh 'cat /etc/bc25-galaxy/hostname 2>/dev/null' || true)
if [ -n "$host" ]; then
  mkdir -p "$HOME/.bc25-galaxy"; chmod 700 "$HOME/.bc25-galaxy"
  echo "https://galaxy25.$host" > "$HOME/.bc25-galaxy/site"
  echo "site: https://galaxy25.$host/"
fi

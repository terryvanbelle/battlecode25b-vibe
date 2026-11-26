#!/usr/bin/env bash
# The mechanical steps of a prod (TRAINING_ALGORITHM.md §7.1); the judgment steps (crown, retire, build) stay manual.
#   tools/prod.sh pull            box status, pull every local run without DONE, rank
#   tools/prod.sh queue [N]       keep >= N (default 5) runs queued: plan and queue new run numbers, dedupe, md5 check
#   tools/prod.sh replica         replica sample + chart, local chart, parity top-up, fetch --new, recent matches
#   tools/prod.sh disk            df on the driver, the box and the replica VM
#   tools/prod.sh commit MSG PATH...   git add PATH... plus the tourney/progress files, commit with trailers, push
# Commit trailers: Co-Authored-By always; Claude-Session from $BC_SESSION when set.
set -u
cd "$(dirname "$0")/.." || exit 1
PY=python3
VPY=$HOME/.venv-bc25b/bin/python
BOXQ='~/projects/vibe/b25b/runs'

case "${1:-}" in
  pull)
    tools/box.sh status | head -4
    for d in runs/tr*; do
      [ -d "$d" ] && [ ! -e "$d/DONE" ] && tools/box.sh pull "$(basename "$d")" 2>&1 | grep -v "No such\|file changed"
    done
    $PY tools/tourney.py rank ;;
  queue)
    want=${2:-5}
    have=$(timeout 120 tools/box.sh sh "cat $BOXQ/screenq.txt 2>/dev/null | wc -l")
    last=$(ls -d runs/tr* 2>/dev/null | sed 's/.*tr//' | sort -n | tail -1)
    first=""
    while [ "${have:-0}" -lt "$want" ]; do
      last=$((last + 1)); r=tr$last; first=${first:-$r}
      $PY tools/tourney.py plan $r --games 400 | tail -1
      timeout 300 tools/box.sh queue $r >/dev/null || echo "queue $r failed"
      have=$((have + 1))
    done
    tools/box.sh sh "cd $BOXQ && awk '!s[\$0]++' screenq.txt > q.tmp && mv q.tmp screenq.txt; echo queue: \$(tr '\n' ' ' < screenq.txt); tail -1 screenq.log"
    if [ -n "$first" ]; then
      a=$(tools/box.sh sh "md5sum $BOXQ/$first/cells.tsv" | cut -d' ' -f1); b=$(md5sum runs/$first/cells.tsv | cut -d' ' -f1)
      [ "$a" = "$b" ] && echo "sync ok ($first)" || echo "SYNC MISMATCH on $first: box $a driver $b"
    fi ;;
  replica)
    $PY tools/tourney.py rank >/dev/null
    $PY tools/replica_elo.py sample
    $VPY tools/replica_elo.py chart
    $VPY tools/tourney.py chart | tail -1
    $PY tools/parity.py --topup
    timeout 240 $PY tools/galaxy25/contest.py fetch --new >/dev/null 2>&1; echo "fetch exit $?"
    timeout 120 $PY tools/galaxy25/contest.py matches 2>/dev/null | grep "OK!" | head -6 ;;
  disk)
    echo "driver: $(df -h ~ | tail -1)"
    echo "box:    $(tools/box.sh sh 'df -h ~ | tail -1')"
    echo "box:    $(tools/box.sh sh uptime)"
    # shellcheck disable=SC1091
    source tools/galaxy25/vm.sh; ensure_vm >/dev/null; echo "vm:     $(gssh 'df -h / | tail -1')" ;;
  commit)
    msg=${2:?commit message}; shift 2
    git add research/tourney progress/local-elo.md progress/local-elo.png progress/replica-elo.csv progress/replica-elo.png "$@" || exit 1
    trailer="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    [ -n "${BC_SESSION:-}" ] && trailer="$trailer
Claude-Session: $BC_SESSION"
    git commit -qm "$msg

$trailer" && git push -q && echo "committed and pushed" ;;
  *) sed -n 2,9p "$0"; exit 2 ;;
esac

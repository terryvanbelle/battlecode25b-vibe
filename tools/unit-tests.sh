#!/usr/bin/env bash
# Every unit test: the bot's logic tests (fake RobotController, test/vibe/*Test.java) and the tool tests.
#   bash tools/unit-tests.sh          src/vibe (the development bot) with test/vibe, then the tool tests
#   bash tools/unit-tests.sh BOT      bots/BOT compiled under package vibe with test/vibe (tool tests skipped)
# Exit status 1 when any test failed.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JDK="${BC_JDK:-$HOME/opt/jdk21}"; ENGINE="$REPO/engine/battlecode25-java-3.1.0.jar"
OUT="$REPO/build/tests"; rm -rf "$OUT"; mkdir -p "$OUT/classes"
SRC="$REPO/src/vibe"
if [ -n "${1:-}" ]; then
    [ -d "$REPO/bots/$1" ] || { echo "unit-tests: no bots/$1" >&2; exit 2; }
    mkdir -p "$OUT/src"
    for f in "$REPO/bots/$1"/*.java; do sed "s/^package $1;/package vibe;/" "$f" > "$OUT/src/$(basename "$f")"; done
    SRC="$OUT/src"
fi
"$JDK/bin/javac" -nowarn --release 21 -proc:none -d "$OUT/classes" -cp "$ENGINE" "$SRC"/*.java "$REPO"/test/vibe/*.java
FAILED=()
for t in "$REPO"/test/vibe/*Test.java; do
    "$JDK/bin/java" -cp "$OUT/classes:$ENGINE" "vibe.$(basename "$t" .java)" || FAILED+=("$(basename "$t" .java)")
done
if [ ${#FAILED[@]} -gt 0 ]; then echo "unit-tests: FAILED ${FAILED[*]}" >&2; exit 1; fi
[ -n "${1:-}" ] && exit 0
"$REPO/tools/build-tools.sh"
for t in "$REPO"/tools/tests/test_*.py; do [ -e "$t" ] && python3 -I "$t"; done
echo "unit-tests: all passed"

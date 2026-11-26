#!/usr/bin/env bash
# Crown a new local champion (TRAINING_ALGORITHM.md §2.5). Only the local champion is ever submitted (owner prompt #8).
#   tools/crown.sh NEW OLD "description for champions.csv"
# Writes champion.txt first (the guard hook only lets the champion be submitted), submits bots/NEW to the replica,
# appends champions.csv with the submission number, copies NEW into src/vibe, retires OLD in pool.txt, redraws the
# local chart, and prints the diff against OLD (package names normalised) for the audit.
set -eu
cd "$(dirname "$0")/.."
new=${1:?NEW}; old=${2:?OLD}; desc=${3:?description}
[ -d "bots/$new" ] || { echo "crown: no bots/$new"; exit 1; }
echo "$new" > research/tourney/champion.txt
out=$(python3 tools/galaxy25/contest.py submit "bots/$new" -m "$new: $desc (local champion)" 2>&1 | tail -1)
echo "$out"
sub=$(echo "$out" | sed -n 's/^submission \([0-9]*\):.*/\1/p')
[ -n "$sub" ] || { echo "crown: submit failed; champion.txt says $new but nothing was submitted"; exit 1; }
echo "$(TZ=America/Vancouver date '+%Y-%m-%d %H:%M'),$new,$old,${desc//,/;},$sub" >> research/tourney/champions.csv
for f in bots/$new/*.java; do sed "s/^package $new;/package vibe;/;s/\b$new\./vibe./g" "$f" > "src/vibe/$(basename "$f")"; done
sed -i "s/^$old\$/# $old (retired at $new's crowning)/" research/tourney/pool.txt
~/.venv-bc25b/bin/python tools/tourney.py chart | tail -1
echo "--- audit: $new against $old"
for f in bots/$new/*.java; do
  diff <(sed -E "s/^package $old;/package P;/;s/\b$old\./P./g" "bots/$old/$(basename "$f")") \
       <(sed -E "s/^package $new;/package P;/;s/\b$new\./P./g" "$f") || true
done
bash tools/unit-tests.sh 2>&1 | tail -1

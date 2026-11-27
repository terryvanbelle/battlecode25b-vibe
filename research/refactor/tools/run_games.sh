#!/usr/bin/env bash
# run_games.sh LIST OUTROOT : LIST lines "label<TAB>A_spec<TAB>B_spec<TAB>map<TAB>seed"; one game at a time,
# tsv dump kept under OUTROOT/label/; result rows appended to OUTROOT/rows.jsonl. Skips labels already done.
REPO=$HOME/projects/vibe/2025b
LIST=$1; mkdir -p "$2"; OUT=$(cd "$2" && pwd)
while IFS=$'\t' read -r label a b map seed; do
  [ -z "$label" ] && continue; [[ "$label" == \#* ]] && continue
  [ -f "$OUT/$label/DONE" ] && continue
  rm -rf "$OUT/$label"; mkdir -p "$OUT/$label"
  row=$(cd $REPO && python3 tools/arena.py game "$a" "$b" "$map" --seed "$seed" --out "$OUT/$label" --tsv 2>"$OUT/$label/stderr")
  echo "{\"label\":\"$label\",\"row\":$row}" >> "$OUT/rows.jsonl"
  rm -f "$OUT/$label"/*.bc25
  touch "$OUT/$label/DONE"
done < "$LIST"
echo ALLDONE

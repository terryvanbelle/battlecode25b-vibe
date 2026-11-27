#!/usr/bin/env bash
# watch_pairs.sh LABELS BASE NEW TAG : print a line per finished game that is not IDENTICAL or has nonzero SOLDIER/SPLASHER bc
# delta, and a progress line every 8 games; exits when the chain is done.
cd "$(dirname "$0")"; L=$1; B=$2; N=$3; T=$4; touch .seen.$T; seen="$(cat .seen.$T | tr '\n' ' ')"; n=$(wc -l < .seen.$T)
while :; do
  while read -r lab; do
    [ -z "$lab" ] && continue; [[ " $seen " == *" $lab "* ]] && continue
    [ -f "$N/$lab/DONE" ] && [ -f "$B/$lab/DONE" ] || continue
    seen="$seen $lab"; n=$((n+1)); echo "$lab" >> .seen.$T
    out=$(echo "$lab" > .w1.$T; python3 cmp_all.py .w1.$T "$B" "$N" 2>&1 | head -1)
    if ! echo "$out" | grep -q IDENTICAL || echo "$out" | grep -qP '(SOLDIER|SPLASHER) \[(?!0,0\])'; then echo "$T FLAG $out"; fi
    [ $((n % 8)) -eq 0 ] && echo "$T progress $n/43"
  done < "$L"
  [ $n -ge 43 ] && { echo "$T all 43 compared"; exit 0; }
  grep -q CHAIN_DONE games/r3.log 2>/dev/null && { echo "$T chain done, compared $n"; exit 0; }
  sleep 20
done

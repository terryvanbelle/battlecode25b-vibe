#!/usr/bin/env bash
# bytecode-diff.sh CLASSDIR_A CLASSDIR_B : compare method bytecode of two compiled bot trees, ignoring
# constant-pool indices and whitespace. Prints per-class differing line counts; exit 1 when any differ.
J=${BC_JDK:-$HOME/opt/jdk21}/bin; rc=0
for f in "$1"/*/*.class; do
  c=$(basename "$f"); g=$(ls "$2"/*/"$c" 2>/dev/null) || { echo "$c: missing in B"; rc=1; continue; }
  n=$(diff <($J/javap -c -p "$f" | sed -E 's/#[0-9]+(, *[0-9]+)?//g; s/^(Compiled|class|public|final).*//' | tr -s ' ') \
           <($J/javap -c -p "$g" | sed -E 's/#[0-9]+(, *[0-9]+)?//g; s/^(Compiled|class|public|final).*//' | tr -s ' ') | grep -c '^[<>]')
  echo "$c: $n"; [ "$n" -gt 0 ] && rc=1
done; exit $rc

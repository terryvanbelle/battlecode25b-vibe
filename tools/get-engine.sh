#!/usr/bin/env bash
# Fetch the public Battlecode 2025 engine 3.1.0 (read-only download from the public release host) and verify it.
set -euo pipefail
cd "$(dirname "$0")/../engine"
B=https://releases.battlecode.org/maven/org/battlecode/battlecode25-java/3.1.0
for f in battlecode25-java-3.1.0.jar battlecode25-java-3.1.0-sources.jar battlecode25-java-3.1.0-javadoc.jar battlecode25-java-3.1.0.pom; do
  [ -f "$f" ] || curl -sfL -o "$f" "$B/$f"
done
sha256sum -c SHA256SUMS

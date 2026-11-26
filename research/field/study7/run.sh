#!/bin/sh
# run.sh tNN_name.py [out]: runs a topic script isolated (python -I) with this directory on sys.path; output to tNN.txt
D=$(cd "$(dirname "$0")" && pwd)
S="$1"; O="${2:-$(echo "$S" | sed 's/_.*//; s/\.py$//').txt}"
python3 -I -c "import sys, runpy; sys.path.insert(0, '$D'); sys.argv = ['$S']; runpy.run_path('$D/$S', run_name='__main__')" > "$D/$O"

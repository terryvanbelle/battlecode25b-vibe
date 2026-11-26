#!/bin/sh
# Run a study-3 topic script against the study-4 dumps: sh run3.sh t2_towers.py > t2.txt
D=$(cd "$(dirname "$0")" && pwd)
python3 -c "import sys; sys.path.insert(0,'$D'); sys.argv=['$1']; exec(open('$D/../study3/$1').read())"

#!/usr/bin/env python3
"""cmp_all.py LIST BASE_ROOT NEW_ROOT : cmp.py on every label of LIST (our side: A or B from the label); one line each."""
import sys, subprocess, os, re, json
here = os.path.dirname(os.path.abspath(__file__))
lst, base, new = sys.argv[1:4]; bad = 0
for line in open(lst):
    lab = line.rstrip('\n').split('\t')[0]
    if not lab or not os.path.exists(os.path.join(new, lab, 'DONE')): continue
    side = 'A' if '_A_' in lab else 'B'
    p = subprocess.run([sys.executable, os.path.join(here, 'cmp.py'), os.path.join(base, lab), os.path.join(new, lab), '--team', side],
                       capture_output=True, text=True)
    out = p.stdout.splitlines()
    rows = ' '.join(re.findall(r'\((\d+) rows\)', p.stdout))
    bc = next((l.split(': ', 1)[1] for l in out if 'bc delta' in l), '')
    win = ''
    try:
        r = [json.loads(l) for l in open(os.path.join(new, 'rows.jsonl')) if json.loads(l).get('label') == lab]
    except Exception: r = []
    print(f'{lab:28s} {out[0] if out else p.stderr[-200:]:10s} rows {rows:12s} {bc}')
    if not out or out[0] != 'IDENTICAL':
        bad += 1; print('\n'.join('    ' + l for l in out[1:12]))
print('DIVERGED games:', bad); sys.exit(1 if bad else 0)

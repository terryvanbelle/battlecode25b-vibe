#!/usr/bin/env python3
"""variant_sim.py NEW OLD REP : run tools/variant.py's own edit() on bots/r135/Tune.java with finish() replaced by
what snapshot.sh does (package rename r135 -> NEW, then javac), all inside the scratch dir: nothing under bots/.
Also checks that every `NAME = VALUE` in Tune.java occurs exactly once (so any knob can be a variant.py edit)."""
import sys, os, re, subprocess, tempfile, glob
SCR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.expanduser('~/projects/vibe/2025b')
tempfile.tempdir = SCR
BASE = os.environ.get('BASE', 'r135')
sys.path.insert(0, os.path.join(REPO, 'tools'))
import variant
tune = open(os.path.join(REPO, f'bots/{BASE}/Tune.java')).read()
decl = re.findall(r'static final int (\w+) = (-?\d+);', tune)
bad = [(n, v, tune.count(f'{n} = {v}')) for n, v in decl if tune.count(f'{n} = {v}') != 1]
print(f'Tune.java: {len(decl)} constants; NAME = VALUE not unique: {bad}')
print(f'"{BASE}." in sources:', [f for f in glob.glob(os.path.join(REPO, f'bots/{BASE}/*.java')) if re.search(rf'\b{BASE}\.', open(f).read())])
def finish(new, base, src, add):
    out = os.path.join(SCR, 'variant_out', new); os.makedirs(out + '/src', exist_ok=True); os.makedirs(out + '/cls', exist_ok=True)
    for f in glob.glob(os.path.join(src, '*.java')):
        t = re.sub(rf'^package {base};', f'package {new};', open(f).read(), flags=re.M)
        t = re.sub(rf'\b{base}\.', f'{new}.', t)
        open(os.path.join(out, 'src', os.path.basename(f)), 'w').write(t)
    r = subprocess.run([os.path.expanduser('~/opt/jdk21/bin/javac'), '-nowarn', '--release', '21', '-proc:none', '-d', out + '/cls',
                        '-cp', os.path.join(REPO, 'engine/battlecode25-java-3.1.0.jar')] + glob.glob(out + '/src/*.java'), capture_output=True, text=True)
    print('javac', 'ok' if r.returncode == 0 else 'FAILED\n' + r.stderr)
    d = subprocess.run(['diff', os.path.join(REPO, f'bots/{BASE}/Tune.java'), os.path.join(out, 'src/Tune.java')], capture_output=True, text=True).stdout
    print('Tune.java diff:\n' + d)
variant.finish = finish
variant.edit(sys.argv[1:4] if len(sys.argv) > 4 else [sys.argv[1], BASE, 'Tune.java', sys.argv[2], sys.argv[3]], False)

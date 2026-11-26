#!/usr/bin/env python3
"""Build a candidate bot from a base bot, snapshot it and enter it in the tournament.

  python3 tools/variant.py NEW BASE  FILE OLD NEW  [FILE OLD NEW ...]
      copy bots/BASE, replace OLD with NEW in FILE (each OLD must occur exactly once), snapshot as bots/NEW,
      `tourney.py add NEW`. FILE is a bare name such as Tower.java. Nothing is snapshotted if an edit fails.
  python3 tools/variant.py port NEW BASE VAR VARBASE
      apply VAR's change against VARBASE onto BASE (package names normalised; comments untouched), as bots/NEW.
  Add --no-add to skip `tourney.py add`.

The source directory handed to tools/snapshot.sh must be named after the base package, so the copy lives in
TMP/BASE. Run `bash tools/unit-tests.sh` afterwards.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOTS = os.path.join(REPO, 'bots')


def copy_base(base):
    if not os.path.isdir(os.path.join(BOTS, base)):
        sys.exit(f'variant: no bots/{base}')
    tmp = tempfile.mkdtemp(prefix='variant-')
    src = os.path.join(tmp, base)
    shutil.copytree(os.path.join(BOTS, base), src)
    snap = os.path.join(src, 'SNAPSHOT')
    if os.path.exists(snap):
        os.remove(snap)
    return tmp, src


def normalise(text, pkg):
    text = re.sub(rf'^package {re.escape(pkg)};', 'package PKGX;', text, flags=re.M)
    return re.sub(rf'\b{re.escape(pkg)}\.', 'PKGX.', text)


def finish(new, base, src, add):
    if os.path.exists(os.path.join(BOTS, new)):
        sys.exit(f'variant: bots/{new} already exists')
    subprocess.run(['tools/snapshot.sh', new, src], cwd=REPO, check=True)
    if add:
        subprocess.run([sys.executable, 'tools/tourney.py', 'add', new], cwd=REPO, check=True)


def edit(args, add):
    new, base, rest = args[0], args[1], args[2:]
    if not rest or len(rest) % 3:
        sys.exit('variant: edits come in FILE OLD NEW triples')
    tmp, src = copy_base(base)
    try:
        for i in range(0, len(rest), 3):
            f, old, rep = rest[i:i + 3]
            p = os.path.join(src, f)
            s = open(p).read()
            n = s.count(old)
            if n != 1:
                sys.exit(f'variant: {f}: expected 1 occurrence, found {n}:\n{old}')
            open(p, 'w').write(s.replace(old, rep))
        finish(new, base, src, add)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def port(args, add):
    new, base, var, vbase = args
    tmp, src = copy_base(base)
    try:
        work = os.path.join(tmp, 'w')
        for name, d in (('a', vbase), ('b', var), ('c', base)):
            os.makedirs(os.path.join(work, name))
            for f in os.listdir(os.path.join(BOTS, d)):
                if f.endswith('.java'):
                    t = normalise(open(os.path.join(BOTS, d, f)).read(), d)
                    open(os.path.join(work, name, f), 'w').write(t)
        diff = subprocess.run(['diff', '-ruN', 'a', 'b'], cwd=work, capture_output=True, text=True).stdout
        if not diff:
            sys.exit(f'variant: {var} has no change against {vbase}')
        r = subprocess.run(['patch', '-p1', '--batch', '--forward'], cwd=os.path.join(work, 'c'), input=diff,
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit('variant: patch failed:\n' + r.stdout + r.stderr)
        for f in os.listdir(os.path.join(work, 'c')):
            if f.endswith('.java'):
                t = open(os.path.join(work, 'c', f)).read()
                t = t.replace('package PKGX;', f'package {base};').replace('PKGX.', f'{base}.')
                open(os.path.join(src, f), 'w').write(t)
        finish(new, base, src, add)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--no-add']
    add = '--no-add' not in sys.argv
    if a[:1] == ['port'] and len(a) == 5:
        port(a[1:], add)
    elif len(a) >= 5:
        edit(a, add)
    else:
        print(__doc__)
        sys.exit(2)

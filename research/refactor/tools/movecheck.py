#!/usr/bin/env python3
"""movecheck.py CLS_ORIG CLS_NEW : compare every method of the new tree with its origin in the original tree after
renaming references through the R2 move map. Instructions are compared as opcode + operand with byte offsets, branch
targets and local-variable slot numbers dropped (they shift when a method moves; the executed instruction count does
not). Prints per method: same / DIFF (with instruction counts) / new / gone."""
import sys, os, re, subprocess, glob
J = os.path.expanduser('~/opt/jdk21/bin/javap')
P = 't135/'
MOVE = {  # old owner.member -> new owner.member
    'G.towerLoc': 'Towers.loc', 'G.towerKind': 'Towers.kind', 'Unit.towerDry': 'Towers.dry',
    'G.noteTower': 'Towers.note', 'G.forgetTower': 'Towers.forget', 'G.kind': 'Towers.kindOf',
    'Unit.markDry': 'Towers.markDry', 'Soldier.allyTowerKind': 'Towers.kindAt',
    'Soldier.patternOf': 'Pattern.of', 'Soldier.bit': 'Pattern.bit', 'Soldier.readMarks': 'Pattern.readMarks',
    'Soldier.contested': 'Pattern.contested', 'Soldier.agreesWithMoney': 'Pattern.agreesWithMoney',
    'Soldier.srpSec': 'Pattern.srpSec', 'Tower.churn': 'Churn.towerTurn', 'Unit.churnable': 'Churn.churnable',
    'Unit.repairPattern': 'Churn.repairPattern', 'Unit.rebuild': 'Churn.rebuild',
}
CLASSMOVE = {'G$1': 'Towers$1', 'Soldier$1': 'Pattern$1'}
BRANCH = re.compile(r'^(if\w*|goto|goto_w|jsr)\s+\d+$')
def methods(path, owner):
    out = subprocess.run([J, '-c', '-p', path], capture_output=True, text=True).stdout
    mem, cur = {}, None
    for raw in out.splitlines():
        if re.match(r'^ {2}\S', raw) and raw.strip() not in ('Code:', '}'):
            m = re.search(r'(\w+|static \{\})\s*\(', raw.strip())
            name = 'static{}' if 'static {}' in raw else (re.search(r'([\w$<>]+)\(', raw).group(1) if '(' in raw else None)
            cur = name if name else None
            if cur: mem[cur] = []
            continue
        if cur is None: continue
        s = raw.strip()
        mm = re.match(r'^\d+: (.*)$', s)
        if not mm: continue
        ins = mm.group(1)
        if re.fullmatch(r'-?\d+', ins.strip()): continue          # tableswitch/lookupswitch entry (a byte offset)
        ins = re.sub(r'^ldc_w\b', 'ldc', ins)                       # constant-pool index width only
        # qualify same-class references, then drop the constant-pool index
        ins = re.sub(r'//\s*(Field|Method|InterfaceMethod)\s+(?![\w/$]+\.)', lambda x: f'// {x.group(1)} {P}{owner}.', ins)
        ins = re.sub(r'#\d+(, *\d+)?', '', ins)
        ins = re.sub(r'\s+', ' ', ins).strip()
        for old, new in MOVE.items():
            ins = re.sub(re.escape(P + old) + r'(?=[:.])', P + new, ins)
        for old, new in CLASSMOVE.items():
            ins = ins.replace(P + old + '.', P + new + '.')
        op = ins.split(' ')[0]
        ins = re.sub(r'^([ailfd]load|[ailfd]store)(_\d| \d+)', r'\1', ins)     # local slots
        ins = re.sub(r'^iinc \d+,', 'iinc', ins)
        if BRANCH.match(ins): ins = op
        if op in ('tableswitch', 'lookupswitch'): ins = op
        mem[cur].append(ins)
    return mem
O, N = sys.argv[1], sys.argv[2]
orig = {}
for f in glob.glob(os.path.join(O, '*', '*.class')):
    c = os.path.basename(f)[:-6]
    for m, ins in methods(f, c).items():
        key = MOVE.get(f'{c}.{m}', f'{CLASSMOVE.get(c, c)}.{m}')
        orig[key] = ins
seen = set(); same = 0; rows = []
for f in sorted(glob.glob(os.path.join(N, '*', '*.class'))):
    c = os.path.basename(f)[:-6]
    for m, ins in methods(f, c).items():
        k = f'{c}.{m}'; seen.add(k)
        if k not in orig: rows.append(f'new   {k} ({len(ins)} instr)'); continue
        if orig[k] == ins: same += 1
        else: rows.append(f'DIFF  {k}: {len(orig[k])} -> {len(ins)} instr')
for k in sorted(orig):
    if k not in seen: rows.append(f'gone  {k} ({len(orig[k])} instr)')
print('\n'.join(rows)); print(f'same: {same} methods')
if os.environ.get('SHOW'):
    for k in os.environ['SHOW'].split(','):
        c = k.split('.')[0]; f = glob.glob(os.path.join(N, '*', c + '.class'))[0]
        new = methods(f, c)[k.split('.')[1]]
        import difflib
        print(k); print('\n'.join(l for l in difflib.unified_diff(orig[k], new, lineterm='', n=0)))

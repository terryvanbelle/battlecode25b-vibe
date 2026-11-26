"""Our package per game, read from the replay headers (TeamData name + packageName, flatbuffer strings).
Prints: match game package-of-vibe25b opponent opponent-package.  Usage: python3 -I pkgs.py [min_match]"""
import gzip, os, re, struct, sys, json
R = os.path.expanduser('~/projects/vibe/bc25b-galaxy-replays')
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 2599
for m in sorted(int(x) for x in os.listdir(R) if x.isdigit()):
    if m < lo: continue
    d = gzip.decompress(open(f'{R}/{m}/replay.bc25', 'rb').read())
    j = json.load(open(f'{R}/{m}/match.json'))
    opp = [t for t in j['teams'] if t != 'vibe25b'][0]
    out = []
    for name in (b'vibe25b', opp.encode()):
        pk = []
        for mm in re.finditer(re.escape(struct.pack('<I', len(name)) + name + b'\x00'), d):
            i = mm.start()
            # the package string ends (NUL + padding) just before; scan back for a plausible length prefix
            for L in range(1, 40):
                for pad in range(0, 4):
                    s = i - pad - 1 - L
                    if s < 4: continue
                    if struct.unpack('<I', d[s - 4:s])[0] == L and d[s + L] == 0 and all(32 < c < 127 for c in d[s:s + L]):
                        pk.append(d[s:s + L].decode()); break
                else: continue
                break
        out.append(pk)
    print(m, 'R' if j['is_ranked'] else 'u', opp, 'us=' + ','.join(out[0]), 'them=' + ','.join(out[1]))

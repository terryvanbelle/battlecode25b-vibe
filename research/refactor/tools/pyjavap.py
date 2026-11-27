#!/usr/bin/env python3
"""pyjavap.py CLASSFILE [METHOD] : minimal disassembler (no JVM): prints 'pc mnemonic operand' per instruction."""
import sys, struct
OPS = {}
names = ("nop aconst_null iconst_m1 iconst_0 iconst_1 iconst_2 iconst_3 iconst_4 iconst_5 lconst_0 lconst_1 fconst_0 "
 "fconst_1 fconst_2 dconst_0 dconst_1 bipush sipush ldc ldc_w ldc2_w iload lload fload dload aload iload_0 iload_1 "
 "iload_2 iload_3 lload_0 lload_1 lload_2 lload_3 fload_0 fload_1 fload_2 fload_3 dload_0 dload_1 dload_2 dload_3 "
 "aload_0 aload_1 aload_2 aload_3 iaload laload faload daload aaload baload caload saload istore lstore fstore dstore "
 "astore istore_0 istore_1 istore_2 istore_3 lstore_0 lstore_1 lstore_2 lstore_3 fstore_0 fstore_1 fstore_2 fstore_3 "
 "dstore_0 dstore_1 dstore_2 dstore_3 astore_0 astore_1 astore_2 astore_3 iastore lastore fastore dastore aastore "
 "bastore castore sastore pop pop2 dup dup_x1 dup_x2 dup2 dup2_x1 dup2_x2 swap iadd ladd fadd dadd isub lsub fsub dsub "
 "imul lmul fmul dmul idiv ldiv fdiv ddiv irem lrem frem drem ineg lneg fneg dneg ishl lshl ishr lshr iushr lushr iand "
 "land ior lor ixor lxor iinc i2l i2f i2d l2i l2f l2d f2i f2l f2d d2i d2l d2f i2b i2c i2s lcmp fcmpl fcmpg dcmpl dcmpg "
 "ifeq ifne iflt ifge ifgt ifle if_icmpeq if_icmpne if_icmplt if_icmpge if_icmpgt if_icmple if_acmpeq if_acmpne goto "
 "jsr ret tableswitch lookupswitch ireturn lreturn freturn dreturn areturn return getstatic putstatic getfield putfield "
 "invokevirtual invokespecial invokestatic invokeinterface invokedynamic new newarray anewarray arraylength athrow "
 "checkcast instanceof monitorenter monitorexit wide multianewarray ifnull ifnonnull goto_w jsr_w").split()
for i, n in enumerate(names): OPS[i] = n
L1 = {'bipush', 'ldc', 'iload', 'lload', 'fload', 'dload', 'aload', 'istore', 'lstore', 'fstore', 'dstore', 'astore', 'ret', 'newarray'}
L2 = {'sipush', 'ldc_w', 'ldc2_w', 'iinc', 'getstatic', 'putstatic', 'getfield', 'putfield', 'invokevirtual', 'invokespecial',
      'invokestatic', 'new', 'anewarray', 'checkcast', 'instanceof', 'ifnull', 'ifnonnull', 'goto', 'jsr'} | {n for n in names if n.startswith('if')}
def parse(path):
    b = open(path, 'rb').read(); p = 8
    n = struct.unpack('>H', b[p:p+2])[0]; p += 2; cp = [None] * n; i = 1
    while i < n:
        t = b[p]; p += 1
        if t == 1: l = struct.unpack('>H', b[p:p+2])[0]; cp[i] = ('utf', b[p+2:p+2+l].decode('utf8', 'replace')); p += 2 + l
        elif t in (3, 4): cp[i] = ('int', struct.unpack('>i', b[p:p+4])[0]); p += 4
        elif t in (5, 6): cp[i] = ('long', b[p:p+8]); p += 8; i += 1
        elif t in (7, 8, 16, 19, 20): cp[i] = (t, struct.unpack('>H', b[p:p+2])[0]); p += 2
        elif t == 15: p += 3
        else: cp[i] = (t,) + struct.unpack('>HH', b[p:p+4]); p += 4
        i += 1
    def s(k):
        e = cp[k]
        if e[0] == 'utf': return e[1]
        if e[0] == 'int': return str(e[1])
        if e[0] in (7, 8): return s(e[1])
        if e[0] == 12: return s(e[1])
        if e[0] in (9, 10, 11): return s(e[1]).split('/')[-1] + '.' + s(e[2])
        return '?'
    p += 6; ni = struct.unpack('>H', b[p:p+2])[0]; p += 2 + 2 * ni
    out = {}
    for kind in ('f', 'm'):
        c = struct.unpack('>H', b[p:p+2])[0]; p += 2
        for _ in range(c):
            nm = s(struct.unpack('>H', b[p+2:p+4])[0]); ac = struct.unpack('>H', b[p+6:p+8])[0]; p += 8
            for _ in range(ac):
                an = s(struct.unpack('>H', b[p:p+2])[0]); al = struct.unpack('>I', b[p+2:p+6])[0]
                if kind == 'm' and an == 'Code':
                    cl = struct.unpack('>I', b[p+10:p+14])[0]; out[nm] = (b[p+14:p+14+cl], s)
                p += 6 + al
    return out
def dis(code, s):
    pc = 0; res = []
    while pc < len(code):
        op = OPS[code[pc]]; start = pc; arg = ''
        if op in ('tableswitch', 'lookupswitch'):
            q = (pc + 4) & ~3
            if op == 'tableswitch':
                lo, hi = struct.unpack('>ii', code[q+4:q+12]); pc = q + 12 + 4 * (hi - lo + 1)
            else:
                np_ = struct.unpack('>i', code[q+4:q+8])[0]; pc = q + 8 + 8 * np_
        elif op == 'wide': pc += 6 if OPS[code[pc+1]] == 'iinc' else 4
        elif op in ('invokeinterface', 'invokedynamic'): arg = s(struct.unpack('>H', code[pc+1:pc+3])[0]); pc += 5
        elif op == 'multianewarray': pc += 4
        elif op in ('goto_w', 'jsr_w'): pc += 5
        elif op in L1:
            arg = s(code[pc+1]) if op == 'ldc' else str(code[pc+1] if op != 'bipush' else struct.unpack('b', code[pc+1:pc+2])[0]); pc += 2
        elif op in L2:
            v = struct.unpack('>H', code[pc+1:pc+3])[0]
            if op in ('getstatic', 'putstatic', 'getfield', 'putfield', 'invokevirtual', 'invokespecial', 'invokestatic', 'new', 'anewarray', 'checkcast', 'instanceof', 'ldc_w'): arg = s(v)
            elif op == 'sipush': arg = str(struct.unpack('>h', code[pc+1:pc+3])[0])
            elif op == 'iinc': arg = f'{code[pc+1]},{struct.unpack("b", code[pc+2:pc+3])[0]}'
            else: arg = '->' + str(start + struct.unpack('>h', code[pc+1:pc+3])[0])
            pc += 3
        else: pc += 1
        res.append((start, op, arg))
    return res
if __name__ == '__main__':
    ms = parse(sys.argv[1])
    for nm, (code, s) in ms.items():
        if len(sys.argv) > 2 and nm != sys.argv[2]: continue
        ins = dis(code, s); print(f'== {nm} ({len(ins)} instr)')
        for pc, op, arg in ins: print(f'{pc:5d} {op} {arg}')

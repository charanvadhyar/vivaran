"""Vector timing: convoys, chimes, startup (VMIPS, H&P startup latencies)."""
START = {'ls': 12, 'mul': 7, 'add': 6, 'div': 20}


def unit(op):
    if op in ('LV', 'SV', 'LVWS', 'SVWS', 'LVI', 'SVI'):
        return 'ls'
    if op.startswith('MUL'):
        return 'mul'
    if op.startswith('DIV'):
        return 'div'
    return 'add'


def convoys(prog, chaining=False):
    """prog: list of (op, dest, srcs). Greedy in-order packing."""
    out, cur, used, written = [], [], set(), set()
    for ins in prog:
        op, d, srcs = ins
        u = unit(op)
        clash = u in used or (not chaining and any(s in written for s in srcs))
        if cur and clash:
            out.append(cur); cur, used, written = [], set(), set()
        cur.append(ins); used.add(u)
        if d:
            written.add(d)
    if cur:
        out.append(cur)
    return out


def time(prog, n, chaining=False, lanes=1):
    cs = convoys(prog, chaining)
    n = -(-n // lanes)
    if chaining:
        # chained convoy: startups of the chained units add up, then n cycles
        return sum(sum(START[unit(i[0])] for i in c) + n for c in cs), cs
    return sum(max(START[unit(i[0])] for i in c) + n for c in cs), cs

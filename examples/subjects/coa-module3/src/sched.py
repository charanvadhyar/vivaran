"""In-order single-issue timing with the textbook's latencies (stall cycles between producer and consumer)."""
STALL = {("load", "fp"): 1, ("load", "store"): 0, ("fp", "fp"): 3, ("fp", "store"): 2,
         ("int", "branch"): 1, ("int", "load"): 0, ("int", "store"): 0, ("int", "int"): 0, ("load", "load"): 0}
def run(prog):
    """prog: list of (text, kind, dest, [srcs]). Returns issue cycle of each instruction (1-based)."""
    t, last, out = 0, {}, []
    for text, kind, dest, srcs in prog:
        c = t + 1
        for r in srcs:
            if r in last:
                pc, pk = last[r]
                c = max(c, pc + 1 + STALL.get((pk, kind), 0))
        out.append(c); t = c
        if dest: last[dest] = (c, kind)
    return out

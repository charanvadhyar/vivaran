"""Scoreboard (CDC 6600 style, Hennessy & Patterson rules).
units: dict name->count; lat: op->exec cycles. prog: (text, op, dest, [srcs]).
Rules: issue in order, one per cycle, needs a free unit and no active instruction with the same dest (WAW);
issue at cycle >= (unit freed write cycle)+1. Read operands when no earlier active instruction will write a source
(read cycle >= producer write + 1), and >= issue + 1. Exec complete = read + lat. Write >= complete + 1, and
delayed while an earlier instruction that reads dest has not read its operands yet (write >= its read + 1)."""
UNIT = {'L.D': 'Integer', 'S.D': 'Integer', 'ADD.D': 'Add', 'SUB.D': 'Add', 'MUL.D': 'Mult', 'DIV.D': 'Divide'}
def run(prog, lat, units):
    n = len(prog); iss = [None]*n; rd = [None]*n; ex = [None]*n; wr = [None]*n; fu = [None]*n
    busy = {u: [0]*k for u, k in units.items()}  # cycle when each copy frees (write cycle)
    for i, (t, op, d, srcs) in enumerate(prog):
        u = UNIT[op]
        c = (iss[i-1] + 1) if i else 1
        # structural: earliest copy free
        # WAW: earlier with same dest must have written
        while True:
            free = [k for k, f in enumerate(busy[u]) if f is not None and f < c]
            waw = [j for j in range(i) if prog[j][2] == d and d and wr[j] >= c]
            if free and not waw: break
            c += 1
        k = free[0]; busy[u][k] = None; fu[i] = (u, k); iss[i] = c
        # read operands
        r = c + 1
        for s in srcs:
            prods = [j for j in range(i) if prog[j][2] == s]
            if prods: r = max(r, wr[prods[-1]] + 1)
        rd[i] = r; ex[i] = r + lat[op]
        w = ex[i] + 1
        for j in range(i):
            if d in prog[j][3] and rd[j] >= w: w = rd[j] + 1
        wr[i] = w; busy[u][k] = w
        # later instructions reading earlier... (WAR against LATER-issued but earlier-in-order handled since in-order issue)
    return list(zip(iss, rd, ex, wr))

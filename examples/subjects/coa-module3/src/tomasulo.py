"""Tomasulo timing (single issue, one CDB). prog: (text, op, dest, [srcs]). Loads: srcs are integer regs (always ready).
Station types: Load (3), Store (3), Add (3), Mult (2: MUL and DIV). Exec latencies from lat.
issue: in order, one per cycle, needs a free station of its type (a station frees the cycle after its write).
exec start: issue+1, and for each FP source whose latest earlier writer had not written before issue, that write + 1.
complete = start + lat - 1. write = first cycle > complete with the CDB free (older instruction wins ties).
Stores write nothing on the CDB: they finish (complete) once the value is there."""
KIND = {'L.D': 'Load', 'S.D': 'Store', 'ADD.D': 'Add', 'SUB.D': 'Add', 'MUL.D': 'Mult', 'DIV.D': 'Mult'}
def run(prog, lat, nst={'Load': 3, 'Store': 3, 'Add': 3, 'Mult': 2}):
    n = len(prog); iss = [0]*n; sta = [0]*n; cmp_ = [0]*n; wr = [None]*n; names = [None]*n
    free = {k: [0]*v for k, v in nst.items()}   # cycle from which each station is free
    cdb = set()
    for i, (t, op, d, srcs) in enumerate(prog):
        k = KIND[op]; c = iss[i-1] + 1 if i else 1
        j = min(range(len(free[k])), key=lambda x: free[k][x])
        c = max(c, free[k][j]); iss[i] = c; names[i] = f"{k}{j+1}"
        s = c + 1
        for r in srcs:
            if not r.startswith('F'): continue
            prods = [p for p in range(i) if prog[p][2] == r]
            if prods and wr[prods[-1]] is not None and wr[prods[-1]] >= c:
                s = max(s, wr[prods[-1]] + 1)
        sta[i] = s; cmp_[i] = s + lat[op] - 1
        if op == 'S.D':
            free[k][j] = cmp_[i] + 1; continue
        w = cmp_[i] + 1
        while w in cdb: w += 1
        cdb.add(w); wr[i] = w; free[k][j] = w + 1
    return names, list(zip(iss, sta, cmp_, wr))

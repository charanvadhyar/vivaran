"""Issue-slot filling for a W-wide core with threads; ready[t][c] = instructions thread t could issue in cycle c."""
def superscalar(ready, W=4):
    return [[('A', min(W, ready['A'][c]))] if ready['A'][c] else [] for c in range(len(ready['A']))]
def fine(ready, W=4, order='ABC'):
    n = len(ready['A']); out = []; k = 0
    for c in range(n):
        got = []
        for j in range(len(order)):
            t = order[(k + j) % len(order)]
            if ready[t][c]:
                got = [(t, min(W, ready[t][c]))]; k = (k + j + 1) % len(order); break
        else:
            k = (k + 1) % len(order)
        out.append(got)
    return out
def coarse(ready, W=4, order='ABC', long=2):
    """run one thread; on a stall that lasts >= long cycles, switch to the next thread; switching wastes 1 cycle."""
    n = len(ready['A']); out = []; cur = 0; c = 0
    while c < n:
        t = order[cur]
        if ready[t][c]:
            out.append([(t, min(W, ready[t][c]))]); c += 1; continue
        stall = 0
        while c + stall < n and ready[t][c + stall] == 0: stall += 1
        if stall >= long:
            cur = (cur + 1) % len(order); out.append([]); c += 1   # switch penalty cycle
        else:
            out.append([]); c += 1
    return out
def smt(ready, W=4, order='ABC'):
    out = []
    for c in range(len(ready['A'])):
        left, got = W, []
        for t in order:
            k = min(left, ready[t][c])
            if k: got.append((t, k)); left -= k
        out.append(got)
    return out
used = lambda sched: sum(k for cyc in sched for _, k in cyc)
def grid(sched, W=4):
    rows = []
    for cyc in sched:
        cells = [t for t, k in cyc for _ in range(k)]
        rows.append(cells + [''] * (W - len(cells)))
    return rows

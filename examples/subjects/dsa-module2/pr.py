"""Generic push-relabel (CLRS), FIFO discharge, with an operation log."""
from collections import deque
def push_relabel(V, cap, s, t):
    n = len(V); f = {}; h = {v: 0 for v in V}; e = {v: 0 for v in V}; h[s] = n; log = []
    def cf(u, v): return cap.get((u, v), 0) - f.get((u, v), 0) + f.get((v, u), 0)
    def add(u, v, d):
        back = min(d, f.get((v, u), 0))
        if back: f[(v, u)] -= back
        if d - back: f[(u, v)] = f.get((u, v), 0) + d - back
    nbr = {v: [w for w in V if (v, w) in cap or (w, v) in cap] for v in V}
    q = deque()
    for v in nbr[s]:
        c = cap.get((s, v), 0)
        if c: add(s, v, c); e[v] += c; e[s] -= c; q.append(v) if v != t else None
    log.append(("init", dict(h), dict(e), dict(f)))
    while q:
        u = q.popleft()
        while e[u] > 0:
            pushed = False
            for v in nbr[u]:
                if e[u] and cf(u, v) > 0 and h[u] == h[v] + 1:
                    d = min(e[u], cf(u, v)); add(u, v, d); e[u] -= d; e[v] += d
                    log.append(("push", u, v, d, dict(h), dict(e), dict(f)))
                    if v not in (s, t) and v not in q: q.append(v)
                    pushed = True
            if e[u] > 0:
                nh = 1 + min(h[v] for v in nbr[u] if cf(u, v) > 0)
                h[u] = nh; log.append(("relabel", u, nh, dict(h), dict(e), dict(f)))
    return e[t], {k: x for k, x in f.items()}, log, h

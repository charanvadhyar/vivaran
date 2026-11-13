"""Edmonds-Karp (BFS Ford-Fulkerson) with augmentation log; min cut."""
from collections import deque
def edmonds_karp(V, cap, s, t, order=None):
    """cap: dict (u,v)->c. Returns flow value, flow dict, list of (path, bottleneck), min-cut S."""
    f = {e: 0 for e in cap}; log = []
    def res(u, v):
        return cap.get((u, v), 0) - f.get((u, v), 0) + f.get((v, u), 0)
    nbr = {v: [] for v in V}
    for (u, v) in cap: nbr[u].append(v); nbr[v].append(u)
    for v in V: nbr[v] = sorted(set(nbr[v]), key=(order or V).index)
    while True:
        par = {s: None}; q = deque([s])
        while q and t not in par:
            u = q.popleft()
            for v in nbr[u]:
                if v not in par and res(u, v) > 0: par[v] = u; q.append(v)
        if t not in par: break
        path = [t]
        while path[-1] != s: path.append(par[path[-1]])
        path = path[::-1]; b = min(res(path[i], path[i + 1]) for i in range(len(path) - 1))
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            back = min(b, f.get((v, u), 0))
            if back: f[(v, u)] -= back
            if b - back: f[(u, v)] += b - back
        log.append((path, b))
    S = set(par)
    val = sum(f[e] for e in cap if e[0] == s) - sum(f[e] for e in cap if e[1] == s)
    return val, f, log, S

"""Bellman-Ford with per-pass snapshots."""
INF = float("inf")
def bellman_ford(V, E, s):
    d = {v: INF for v in V}; p = {v: None for v in V}; d[s] = 0; passes = []
    for _ in range(len(V) - 1):
        changed = False
        for u, v, w in E:
            if d[u] + w < d[v]: d[v] = d[u] + w; p[v] = u; changed = True
        passes.append((dict(d), dict(p)))
        if not changed: break
    neg = any(d[u] + w < d[v] for u, v, w in E)
    return d, p, passes, neg

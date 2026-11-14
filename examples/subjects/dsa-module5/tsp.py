import math, itertools
def d(P, a, b): return abs(P[a][0] - P[b][0]) + abs(P[a][1] - P[b][1])
def mst_prim(P, r):
    V = list(P); key = {v: math.inf for v in V}; par = {v: None for v in V}; key[r] = 0; Q = list(V); order = []
    while Q:
        u = min(Q, key=lambda v: (key[v], V.index(v))); Q.remove(u); order.append(u)
        for v in Q:
            w = d(P, u, v)
            if w < key[v]: key[v] = w; par[v] = u
    return par, order
def preorder(par, r, V):
    kids = {v: [c for c in V if par[c] == v] for v in V}; out = []
    def go(u):
        out.append(u)
        for c in kids[u]: go(c)
    go(r); return out
def length(P, tour): return sum(d(P, tour[i], tour[(i + 1) % len(tour)]) for i in range(len(tour)))
def opt(P):
    V = list(P); best = None
    for p in itertools.permutations(V[1:]):
        t = [V[0]] + list(p); L = length(P, t)
        if best is None or L < best[0] - 1e-9: best = (L, t)
    return best

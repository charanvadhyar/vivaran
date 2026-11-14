def job_seq(jobs):
    """jobs: list of (name, deadline, profit). Greedy, latest free slot. returns slots, log."""
    order = sorted(jobs, key=lambda j: -j[2]); D = max(j[1] for j in jobs); slot = [None] * (D + 1); log = []
    for name, d, p in order:
        t = min(d, D)
        while t >= 1 and slot[t] is not None: t -= 1
        if t >= 1: slot[t] = name; log.append((name, d, p, t))
        else: log.append((name, d, p, None))
    return slot[1:], log
def brute(jobs):
    from itertools import permutations, combinations
    best = 0
    for r in range(len(jobs) + 1):
        for c in combinations(jobs, r):
            s = sorted(c, key=lambda j: j[1])
            if all(s[i][1] >= i + 1 for i in range(len(s))): best = max(best, sum(j[2] for j in c))
    return best
INF = float("inf")
def prim(V, E, r):
    """CLRS MST-PRIM with array scan; ties broken by V order. log: (u, key, parent, updates[(v,newkey)])"""
    adj = {v: [] for v in V}
    for a, b, w in E: adj[a].append((b, w)); adj[b].append((a, w))
    key = {v: INF for v in V}; par = {v: None for v in V}; key[r] = 0; Q = list(V); log = []
    while Q:
        u = min(Q, key=lambda v: (key[v], V.index(v))); Q.remove(u); up = []
        for v, w in sorted(adj[u], key=lambda x: V.index(x[0])):
            if v in Q and w < key[v]: key[v] = w; par[v] = u; up.append((v, w))
        log.append((u, key[u], par[u], up))
    return par, log
def kruskal(V, E):
    p = {v: v for v in V}
    def f(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    log = []
    for a, b, w in sorted(E, key=lambda e: e[2]):
        ra, rb = f(a), f(b)
        if ra != rb: p[ra] = rb; log.append((a, b, w, True))
        else: log.append((a, b, w, False))
    return log
def huffman(freq):
    """freq: list of (sym, f). Ties: smaller f first, then earlier creation. returns codes, merges log, cost."""
    import heapq, itertools
    cnt = itertools.count(); h = [(f, next(cnt), s) for s, f in freq]; heapq.heapify(h); log = []; kids = {}
    while len(h) > 1:
        f1, _, x = heapq.heappop(h); f2, _, y = heapq.heappop(h); z = f"({x},{y})"; kids[z] = (x, y)
        log.append((x, f1, y, f2, f1 + f2)); heapq.heappush(h, (f1 + f2, next(cnt), z))
    root = h[0][2]; codes = {}
    def walk(n, c):
        if n in kids: walk(kids[n][0], c + "0"); walk(kids[n][1], c + "1")
        else: codes[n] = c or "0"
    walk(root, ""); fd = dict(freq)
    return codes, log, sum(fd[s] * len(codes[s]) for s in fd), kids, root

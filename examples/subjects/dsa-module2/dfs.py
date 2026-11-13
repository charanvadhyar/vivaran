"""CLRS DFS with times and edge classification."""
def dfs(V, adj):
    col = {v: "W" for v in V}; d, f, par, kinds, order = {}, {}, {}, {}, []
    t = [0]
    def visit(u):
        t[0] += 1; d[u] = t[0]; col[u] = "G"; order.append(u)
        for v in adj.get(u, []):
            if col[v] == "W": kinds[(u, v)] = "tree"; par[v] = u; visit(v)
            elif col[v] == "G": kinds[(u, v)] = "back"
            elif d[u] < d[v]: kinds[(u, v)] = "forward"
            else: kinds[(u, v)] = "cross"
        col[u] = "B"; t[0] += 1; f[u] = t[0]
    for v in V:
        if col[v] == "W": par[v] = None; visit(v)
    return d, f, par, kinds, order

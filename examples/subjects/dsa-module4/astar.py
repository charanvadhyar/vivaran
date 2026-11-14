import heapq
INF = float("inf")
def astar(G, start, goal, diag=True, hmul=1):
    R, C = len(G), len(G[0])
    def h(p): return hmul * max(abs(p[0] - goal[0]), abs(p[1] - goal[1])) if diag else hmul * (abs(p[0] - goal[0]) + abs(p[1] - goal[1]))
    g = {start: 0}; par = {start: None}; openh = [(h(start), 0, start)]; closed = set(); log = []; cnt = 0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] if diag else [(-1, 0), (0, -1), (0, 1), (1, 0)]
    while openh:
        f, _, u = heapq.heappop(openh)
        if u in closed: continue
        closed.add(u); log.append((u, g[u], h(u), f))
        if u == goal: break
        for dr, dc in moves:
            v = (u[0] + dr, u[1] + dc)
            if not (0 <= v[0] < R and 0 <= v[1] < C) or G[v[0]][v[1]] is None or v in closed: continue
            ng = g[u] + G[v[0]][v[1]]
            if ng < g.get(v, INF):
                g[v] = ng; par[v] = u; cnt += 1; heapq.heappush(openh, (ng + h(v), cnt, v))
    path = []; p = goal
    while p is not None: path.append(p); p = par.get(p)
    return path[::-1], g.get(goal), log
def dijkstra_count(G, start, goal, diag=True):
    return astar(G, start, goal, diag, hmul=0)

def nqueens_trace(n, stop_first=True):
    """events: ('place', r, c) ('reject', r, c, reason) ('dead', r) ('remove', r, c) ('solution', cols)"""
    cols = []; ev = []; sols = []
    def ok(r, c):
        for rr, cc in enumerate(cols):
            if cc == c: return "same column"
            if abs(cc - c) == abs(rr - r): return "same diagonal"
        return None
    def go(r):
        if r == n:
            sols.append(list(cols)); ev.append(("solution", list(cols))); return stop_first
        for c in range(n):
            why = ok(r, c)
            if why: ev.append(("reject", r, c, why)); continue
            cols.append(c); ev.append(("place", r, c))
            if go(r + 1): return True
            cols.pop(); ev.append(("remove", r, c))
        ev.append(("dead", r)); return False
    go(0); return ev, sols
def count_solutions(n):
    return len(nqueens_trace(n, stop_first=False)[1])
def sum_of_sub(w, m):
    """Horowitz SUMOFSUB, w sorted ascending. log of nodes: (k, s, r, decision, outcome)."""
    n = len(w); x = [0] * n; sols = []; log = []
    def rec(s, k, r):
        x[k] = 1
        if s + w[k] == m:
            sols.append([w[i] for i in range(k + 1) if x[i]]); log.append(("found", k, s, r, [w[i] for i in range(k + 1) if x[i]]))
        elif k + 1 < n and s + w[k] + w[k + 1] <= m:
            log.append(("include", k, s, r)); rec(s + w[k], k + 1, r - w[k])
        else: log.append(("include-pruned", k, s, r))
        if k + 1 < n and s + r - w[k] >= m and s + w[k + 1] <= m:
            x[k] = 0; log.append(("exclude", k, s, r)); rec(s, k + 1, r - w[k])
        else: log.append(("exclude-pruned", k, s, r))
        x[k] = 0
    rec(0, 0, sum(w)); return sols, log
def mcolor(V, E, m, all_solutions=False):
    adj = {v: set() for v in V}
    for a, b in E: adj[a].add(b); adj[b].add(a)
    col = {}; ev = []; sols = []
    def go(k):
        if k == len(V):
            sols.append(dict(col)); ev.append(("solution", dict(col))); return not all_solutions
        v = V[k]
        for c in range(1, m + 1):
            bad = [u for u in adj[v] if col.get(u) == c]
            if bad: ev.append(("reject", v, c, sorted(bad))); continue
            col[v] = c; ev.append(("color", v, c))
            if go(k + 1): return True
            del col[v]; ev.append(("uncolor", v, c))
        ev.append(("dead", v)); return False
    go(0); return ev, sols
def bb_subset(w, m, mode="fifo"):
    """Branch and bound on subset sum. node = (name, k, s, r). Children of node at level k decide w[k].
    Bound: keep child if s' == m (answer) or (s' + r' >= m and (k+1 == n or s' + w[k+1] <= m))."""
    from collections import deque
    n = len(w); live = deque([("1", 0, 0, sum(w), ())]); order = []; gen = 1; found = None; cnt = 1
    while live:
        node = live.popleft() if mode == "fifo" else live.pop()
        name, k, s, r, path = node; order.append((name, k, s, path))
        if k == n: continue
        kids = []
        for take in (1, 0):
            s2 = s + w[k] * take; r2 = r - w[k]; p2 = path + ((w[k],) if take else ())
            cnt += 1; nm = str(cnt)
            if s2 == m and take:
                found = (nm, p2); order.append((nm, k + 1, s2, p2)); return order, found, cnt
            ok = s2 + r2 >= m and (k + 1 == n or s2 + w[k + 1] <= m) and s2 < m
            if ok: kids.append((nm, k + 1, s2, r2, p2))
        if mode == "fifo": live.extend(kids)
        else: live.extend(reversed(kids))   # take-child explored first
    return order, found, cnt
def bb_subset_detail(w, m, mode="fifo"):
    from collections import deque
    n = len(w); live = deque([("1", 0, 0, sum(w), ())]); cnt = 1; steps = []
    def lab(p): return "{" + ", ".join(map(str, p)) + "}"
    while live:
        name, k, s, r, path = live.popleft() if mode == "fifo" else live.pop()
        kids = []; notes = []
        for take in (1, 0):
            s2 = s + w[k] * take; r2 = r - w[k]; p2 = path + ((w[k],) if take else ()); cnt += 1; nm = str(cnt)
            if take and s2 == m:
                notes.append(f"{nm} {lab(p2)} = {m}: answer"); steps.append((name, lab(path), notes, [x[0] for x in live])); return steps, (nm, p2), cnt
            if not (s2 + r2 >= m): notes.append(f"{nm} {lab(p2)}: killed, {s2} + {r2} < {m}")
            elif k + 1 < n and s2 + w[k + 1] > m: notes.append(f"{nm} {lab(p2)}: killed, {s2} + {w[k+1]} > {m}")
            elif k + 1 == n: notes.append(f"{nm} {lab(p2)}: killed, no weights left")
            else: kids.append((nm, k + 1, s2, r2, p2)); notes.append(f"{nm} {lab(p2)}: live")
        if mode == "fifo": live.extend(kids)
        else: live.extend(reversed(kids))
        steps.append((name, lab(path), notes, [x[0] for x in live]))
    return steps, None, cnt

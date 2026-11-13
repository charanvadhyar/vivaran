"""CLRS red-black insert with case log; snapshots for grid diagrams."""
class RB:
    def __init__(s): s.root = None; s.col = {}; s.L = {}; s.R = {}; s.P = {}; s.log = []
    def insert(s, k):
        y, x = None, s.root
        while x is not None:
            y = x; x = s.L.get(x) if k < x else s.R.get(x)
        s.P[k] = y; s.col[k] = "R"
        if y is None: s.root = k
        elif k < y: s.L[y] = k
        else: s.R[y] = k
        s._fix(k)
    def _rot_l(s, x):
        y = s.R[x]; b = s.L.get(y)
        if b is not None: s.R[x] = b; s.P[b] = x
        else: s.R.pop(x, None)
        s._swap_parent(x, y); s.L[y] = x; s.P[x] = y
    def _rot_r(s, x):
        y = s.L[x]; b = s.R.get(y)
        if b is not None: s.L[x] = b; s.P[b] = x
        else: s.L.pop(x, None)
        s._swap_parent(x, y); s.R[y] = x; s.P[x] = y
    def _swap_parent(s, x, y):
        p = s.P[x]; s.P[y] = p
        if p is None: s.root = y
        elif s.L.get(p) == x: s.L[p] = y
        else: s.R[p] = y
    def _fix(s, z):
        while s.P[z] is not None and s.col[s.P[z]] == "R":
            p = s.P[z]; g = s.P[p]
            if s.L.get(g) == p:
                u = s.R.get(g)
                if u is not None and s.col[u] == "R":
                    s.log.append((z, "case 1: uncle red, recolour")); s.col[p] = s.col[u] = "B"; s.col[g] = "R"; z = g
                else:
                    if s.R.get(p) == z:
                        s.log.append((z, "case 2: uncle black, triangle: rotate parent")); z = p; s._rot_l(z); p = s.P[z]
                    s.log.append((z, "case 3: uncle black, line: rotate grandparent, recolour")); s.col[p] = "B"; s.col[g] = "R"; s._rot_r(g)
            else:
                u = s.L.get(g)
                if u is not None and s.col[u] == "R":
                    s.log.append((z, "case 1: uncle red, recolour")); s.col[p] = s.col[u] = "B"; s.col[g] = "R"; z = g
                else:
                    if s.L.get(p) == z:
                        s.log.append((z, "case 2: uncle black, triangle: rotate parent")); z = p; s._rot_r(z); p = s.P[z]
                    s.log.append((z, "case 3: uncle black, line: rotate grandparent, recolour")); s.col[p] = "B"; s.col[g] = "R"; s._rot_l(g)
        s.col[s.root] = "B"
    def snap(s): return (s.root, dict(s.L), dict(s.R), dict(s.col))
    def check(s):
        """returns black-height; asserts the RB properties"""
        assert s.col[s.root] == "B"
        def go(x):
            if x is None: return 1
            for c in (s.L.get(x), s.R.get(x)):
                if c is not None and s.col[x] == "R": assert s.col[c] == "B", (x, c)
            a, b = go(s.L.get(x)), go(s.R.get(x)); assert a == b
            return a + (s.col[x] == "B")
        return go(s.root)

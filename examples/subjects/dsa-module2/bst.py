"""Plain BST for checking scripts."""
class BST:
    def __init__(s): s.l, s.r, s.root = {}, {}, None
    def insert(s, k):
        path = []
        if s.root is None: s.root = k; return path
        x = s.root
        while True:
            path.append(x)
            side = s.l if k < x else s.r
            if x in side: x = side[x]
            else: side[x] = k; return path
    def search(s, k):
        x, path = s.root, []
        while x is not None:
            path.append(x)
            if k == x: return path
            x = s.l.get(x) if k < x else s.r.get(x)
        return path
    def inorder(s, x="root"):
        x = s.root if x == "root" else x
        if x is None: return []
        return s.inorder(s.l.get(x)) + [x] + s.inorder(s.r.get(x))
    def depth(s):
        d = {}
        def go(x, k):
            if x is None: return
            d[x] = k; go(s.l.get(x), k + 1); go(s.r.get(x), k + 1)
        go(s.root, 0); return d
    def height(s): return max(s.depth().values())
    def parent(s, k):
        for p, c in list(s.l.items()) + list(s.r.items()):
            if c == k: return p
    def minimum(s, x):
        while x in s.l: x = s.l[x]
        return x
    def delete(s, k):
        """CLRS-style: two children -> successor's key moves up"""
        kids = [c for c in (s.l.get(k), s.r.get(k)) if c is not None]
        if len(kids) == 2:
            y = s.minimum(s.r[k]); s.delete(y)
            s._replace(k, y)
            return y
        child = kids[0] if kids else None
        p = s.parent(k)
        for side in (s.l, s.r):
            if p is not None and side.get(p) == k:
                if child is None: del side[p]
                else: side[p] = child
        if p is None: s.root = child
        s.l.pop(k, None); s.r.pop(k, None)
        return None
    def _replace(s, old, new):
        for side in (s.l, s.r):
            if old in side: side[new] = side.pop(old)
            for p, c in list(side.items()):
                if c == old: side[p] = new
        if s.root == old: s.root = new
def build(keys):
    t = BST()
    for k in keys: t.insert(k)
    return t

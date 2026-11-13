"""AVL insert with a log of rotations; snapshots as (root, left, right) dicts."""
class N:
    def __init__(s, k): s.k, s.l, s.r, s.h = k, None, None, 0
H = lambda n: n.h if n else -1
def upd(n): n.h = 1 + max(H(n.l), H(n.r))
def bf(n): return H(n.l) - H(n.r)
def rot_r(y):
    x = y.l; y.l = x.r; x.r = y; upd(y); upd(x); return x
def rot_l(x):
    y = x.r; x.r = y.l; y.l = x; upd(x); upd(y); return y
def snap(n):
    L, R = {}, {}
    def go(x):
        if not x: return
        if x.l: L[x.k] = x.l.k; go(x.l)
        if x.r: R[x.k] = x.r.k; go(x.r)
    go(n); return (n.k if n else None, L, R)
class AVL:
    def __init__(s): s.root = None; s.log = []
    def insert(s, k):
        s._pending = None
        s.root = s._ins(s.root, k)
        return s._pending
    def _ins(s, n, k):
        if not n: return N(k)
        if k < n.k: n.l = s._ins(n.l, k)
        else: n.r = s._ins(n.r, k)
        upd(n); b = bf(n)
        kind = None
        if b > 1 and k < n.l.k: kind = "LL"
        elif b < -1 and k > n.r.k: kind = "RR"
        elif b > 1: kind = "LR"
        elif b < -1: kind = "RL"
        if kind:
            s._pending = (kind, n.k)
            if kind == "LL": return rot_r(n)
            if kind == "RR": return rot_l(n)
            if kind == "LR": n.l = rot_l(n.l); return rot_r(n)
            n.r = rot_r(n.r); return rot_l(n)
        return n
def depths(sn):
    root, L, R = sn; d = {}
    def go(x, k):
        if x is None: return
        d[x] = k; go(L.get(x), k + 1); go(R.get(x), k + 1)
    go(root, 0); return d

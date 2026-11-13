"""CLRS red-black tree with insert and delete; logs fix-up cases."""
class Node:
    def __init__(s, k, c, nil=None): s.k, s.c, s.l, s.r, s.p = k, c, nil, nil, nil
class RBT:
    def __init__(s):
        s.nil = Node(None, "B"); s.nil.l = s.nil.r = s.nil.p = s.nil; s.root = s.nil; s.log = []
    def find(s, k):
        x = s.root
        while x is not s.nil and x.k != k: x = x.l if k < x.k else x.r
        return x
    def rot_l(s, x):
        y = x.r; x.r = y.l
        if y.l is not s.nil: y.l.p = x
        y.p = x.p
        if x.p is s.nil: s.root = y
        elif x is x.p.l: x.p.l = y
        else: x.p.r = y
        y.l = x; x.p = y
    def rot_r(s, x):
        y = x.l; x.l = y.r
        if y.r is not s.nil: y.r.p = x
        y.p = x.p
        if x.p is s.nil: s.root = y
        elif x is x.p.r: x.p.r = y
        else: x.p.l = y
        y.r = x; x.p = y
    def insert(s, k):
        z = Node(k, "R", s.nil); y, x = s.nil, s.root
        while x is not s.nil: y = x; x = x.l if k < x.k else x.r
        z.p = y
        if y is s.nil: s.root = z
        elif k < y.k: y.l = z
        else: y.r = z
        while z.p.c == "R":
            if z.p is z.p.p.l:
                u = z.p.p.r
                if u.c == "R": z.p.c = u.c = "B"; z.p.p.c = "R"; z = z.p.p
                else:
                    if z is z.p.r: z = z.p; s.rot_l(z)
                    z.p.c = "B"; z.p.p.c = "R"; s.rot_r(z.p.p)
            else:
                u = z.p.p.l
                if u.c == "R": z.p.c = u.c = "B"; z.p.p.c = "R"; z = z.p.p
                else:
                    if z is z.p.l: z = z.p; s.rot_r(z)
                    z.p.c = "B"; z.p.p.c = "R"; s.rot_l(z.p.p)
        s.root.c = "B"
    def transplant(s, u, v):
        if u.p is s.nil: s.root = v
        elif u is u.p.l: u.p.l = v
        else: u.p.r = v
        v.p = u.p
    def minimum(s, x):
        while x.l is not s.nil: x = x.l
        return x
    def delete(s, k):
        z = s.find(k); y = z; yc = y.c; ev = []
        if z.l is s.nil: x = z.r; s.transplant(z, z.r)
        elif z.r is s.nil: x = z.l; s.transplant(z, z.l)
        else:
            y = s.minimum(z.r); yc = y.c; x = y.r; ev.append(f"successor {y.k} replaces {k}")
            if y.p is z: x.p = y
            else: s.transplant(y, y.r); y.r = z.r; y.r.p = y
            s.transplant(z, y); y.l = z.l; y.l.p = y; y.c = z.c
        if yc == "B": ev += s.fix(x)
        else: ev.append("removed a red node: nothing to fix")
        s.log.append((k, ev)); return ev
    def fix(s, x):
        ev = []; s.frames = getattr(s, "frames", [])
        while x is not s.root and x.c == "B":
            left = x is x.p.l; w = x.p.r if left else x.p.l
            near, far = (w.l, w.r) if left else (w.r, w.l)
            if w.c == "R":
                ev.append("case 1"); w.c = "B"; x.p.c = "R"; (s.rot_l if left else s.rot_r)(x.p); w = x.p.r if left else x.p.l; s.frames.append(("case 1", s.snap()))
                near, far = (w.l, w.r) if left else (w.r, w.l)
            if near.c == "B" and far.c == "B":
                ev.append("case 2"); w.c = "R"; x = x.p; s.frames.append(("case 2", s.snap()))
            else:
                if far.c == "B":
                    ev.append("case 3"); near.c = "B"; w.c = "R"; (s.rot_r if left else s.rot_l)(w); w = x.p.r if left else x.p.l; s.frames.append(("case 3", s.snap()))
                    near, far = (w.l, w.r) if left else (w.r, w.l)
                ev.append("case 4"); w.c = x.p.c; x.p.c = "B"; far.c = "B"; (s.rot_l if left else s.rot_r)(x.p); x = s.root; s.frames.append(("case 4", s.snap()))
        if x.c == "R" and x is not s.nil: ev.append("x is red: colour it black")
        x.c = "B"
        if not ev: ev.append("x is the root")
        return ev
    def snap(s):
        L, R, C = {}, {}, {}
        def go(x):
            if x is s.nil: return
            C[x.k] = x.c
            if x.l is not s.nil: L[x.k] = x.l.k; go(x.l)
            if x.r is not s.nil: R[x.k] = x.r.k; go(x.r)
        go(s.root); return (s.root.k if s.root is not s.nil else None, L, R, C)
    def check(s):
        assert s.root is s.nil or s.root.c == "B"
        def go(x):
            if x is s.nil: return 1
            if x.c == "R": assert x.l.c == "B" and x.r.c == "B"
            a, b = go(x.l), go(x.r); assert a == b; return a + (x.c == "B")
        return go(s.root)

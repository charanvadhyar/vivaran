"""Binary tree helpers: build from children dict, traversals, rebuild from pre+in."""
from collections import deque
def pre(t, r):  return [] if r is None else [r] + pre(t, t.get(r, (None, None))[0]) + pre(t, t.get(r, (None, None))[1])
def ino(t, r):  return [] if r is None else ino(t, t.get(r, (None, None))[0]) + [r] + ino(t, t.get(r, (None, None))[1])
def post(t, r): return [] if r is None else post(t, t.get(r, (None, None))[0]) + post(t, t.get(r, (None, None))[1]) + [r]
def level(t, r):
    out, q = [], deque([r])
    while q:
        x = q.popleft(); out.append(x)
        for c in t.get(x, (None, None)):
            if c is not None: q.append(c)
    return out
def rebuild(pr, io):
    """children dict from preorder and inorder"""
    t = {}
    def go(pr, io):
        if not pr: return None
        r = pr[0]; k = io.index(r)
        l = go(pr[1:k + 1], io[:k]); rt = go(pr[k + 1:], io[k + 1:])
        if l is not None or rt is not None: t[r] = (l, rt)
        return r
    root = go(pr, io)
    return t, root

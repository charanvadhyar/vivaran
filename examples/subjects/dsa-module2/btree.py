"""CLRS B-tree insert (proactive split), minimum degree t."""
class BN:
    def __init__(s, leaf=True): s.keys, s.ch, s.leaf = [], [], leaf
class BTree:
    def __init__(s, t): s.t = t; s.root = BN(); s.splits = []
    def split(s, x, i):
        t = s.t; y = x.ch[i]; z = BN(y.leaf)
        mid = y.keys[t - 1]
        z.keys = y.keys[t:]; y.keys = y.keys[:t - 1]
        if not y.leaf: z.ch = y.ch[t:]; y.ch = y.ch[:t]
        x.ch.insert(i + 1, z); x.keys.insert(i, mid); s.splits.append(mid)
    def insert(s, k):
        r = s.root
        if len(r.keys) == 2 * s.t - 1:
            nr = BN(False); nr.ch = [r]; s.root = nr; s.split(nr, 0); s._nonfull(nr, k)
        else: s._nonfull(r, k)
    def _nonfull(s, x, k):
        if x.leaf:
            i = 0
            while i < len(x.keys) and x.keys[i] < k: i += 1
            x.keys.insert(i, k); return
        i = 0
        while i < len(x.keys) and x.keys[i] < k: i += 1
        if len(x.ch[i].keys) == 2 * s.t - 1:
            s.split(x, i)
            if k > x.keys[i]: i += 1
        s._nonfull(x.ch[i], k)
    def search(s, k):
        x, reads = s.root, 0
        while True:
            reads += 1; i = 0
            while i < len(x.keys) and x.keys[i] < k: i += 1
            if i < len(x.keys) and x.keys[i] == k: return reads
            if x.leaf: return -reads
            x = x.ch[i]
    def levels(s):
        out, lvl = [], [s.root]
        while lvl:
            out.append([n.keys[:] for n in lvl]); lvl = [c for n in lvl for c in n.ch]
        return out
    def snap(s):
        """list of (node id, keys, depth, parent id)"""
        res = []; cnt = [0]
        def go(x, d, p):
            i = cnt[0]; cnt[0] += 1; res.append((i, x.keys[:], d, p))
            for c in x.ch: go(c, d + 1, i)
        go(s.root, 0, None); return res

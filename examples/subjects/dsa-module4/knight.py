import sys
sys.setrecursionlimit(10000)
MV = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
def tour(n, start=(0, 0), closed=True, warnsdorff=True, limit=10**7):
    B = [[0] * n for _ in range(n)]; cnt = [0]
    def nb(r, c): return [(r + a, c + b) for a, b in MV if 0 <= r + a < n and 0 <= c + b < n and B[r + a][c + b] == 0]
    def go(r, c, k):
        cnt[0] += 1
        if cnt[0] > limit: raise RuntimeError("limit")
        if k == n * n:
            return (not closed) or any((r + a, c + b) == start for a, b in MV)
        opts = nb(r, c)
        if warnsdorff: opts.sort(key=lambda p: (len(nb(*p)), MV.index((p[0] - r, p[1] - c))))
        for p in opts:
            B[p[0]][p[1]] = k + 1
            if go(p[0], p[1], k + 1): return True
            B[p[0]][p[1]] = 0
        return False
    B[start[0]][start[1]] = 1
    ok = go(start[0], start[1], 1)
    return ok, B, cnt[0]

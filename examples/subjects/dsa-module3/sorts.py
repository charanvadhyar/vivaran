"""Merge sort and quicksort with logs (CLRS)."""
INF = float("inf")
def merge_log(L, R):
    """CLRS MERGE with sentinels; returns merged list and log of (i, j, took, value)."""
    L2, R2 = L + [INF], R + [INF]; i = j = 0; out = []; log = []
    for _ in range(len(L) + len(R)):
        if L2[i] <= R2[j]: out.append(L2[i]); log.append((i, j, "L", L2[i])); i += 1
        else: out.append(R2[j]); log.append((i, j, "R", R2[j])); j += 1
    return out, log
def comparisons_no_sentinel(L, R):
    i = j = c = 0
    while i < len(L) and j < len(R):
        c += 1
        if L[i] <= R[j]: i += 1
        else: j += 1
    return c
def merge_sort_tree(A):
    """returns list of (depth, segment-before, segment-after) in preorder and total comparisons (no sentinel)."""
    nodes = []; total = [0]
    def rec(a, d):
        idx = len(nodes); nodes.append([d, list(a), None])
        if len(a) > 1:
            q = (len(a) + 1) // 2  # CLRS q = floor((p+r)/2): left half gets the extra
            l = rec(a[:q], d + 1); r = rec(a[q:], d + 1)
            total[0] += comparisons_no_sentinel(l, r)
            res = merge_log(l, r)[0]
        else: res = list(a)
        nodes[idx][2] = res; return res
    rec(list(A), 0); return nodes, total[0]
def partition_log(A, p, r):
    """CLRS Lomuto PARTITION on A (0-based p..r); returns q and log of (j, swapped_i or None, A snapshot)."""
    x = A[r]; i = p - 1; log = []
    for j in range(p, r):
        if A[j] <= x:
            i += 1; A[i], A[j] = A[j], A[i]; log.append((j, i, list(A)))
        else: log.append((j, None, list(A)))
    A[i + 1], A[r] = A[r], A[i + 1]; log.append(("final", i + 1, list(A)))
    return i + 1, log

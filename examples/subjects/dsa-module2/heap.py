"""1-based max-heap helpers that log swaps."""
def heapify(A, i, n, log):
    while True:
        l, r, m = 2 * i, 2 * i + 1, i
        if l <= n and A[l] > A[m]: m = l
        if r <= n and A[r] > A[m]: m = r
        if m == i: return
        A[i], A[m] = A[m], A[i]; log.append((i, m)); i = m
def build(vals):
    A = [None] + list(vals); n = len(vals); log = []
    for i in range(n // 2, 0, -1):
        log.append(("at", i)); heapify(A, i, n, log)
    return A, log
def insert(A, x):
    A.append(x); i = len(A) - 1; log = []
    while i > 1 and A[i // 2] < A[i]:
        A[i], A[i // 2] = A[i // 2], A[i]; log.append((i, i // 2)); i //= 2
    return log
def extract(A):
    n = len(A) - 1; top = A[1]; A[1] = A[n]; A.pop(); log = []
    heapify(A, 1, n - 1, log); return top, log

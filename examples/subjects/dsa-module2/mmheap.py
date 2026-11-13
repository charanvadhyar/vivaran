"""Min-max heap (1-based) with logged moves."""
import math
def level(i): return int(math.floor(math.log2(i)))
def is_min(i): return level(i) % 2 == 0
def check(A):
    n = len(A) - 1
    for i in range(1, n + 1):
        # all descendants
        st = [2 * i, 2 * i + 1]
        while st:
            j = st.pop()
            if j > n: continue
            if is_min(i): assert A[i] <= A[j], (i, j)
            else: assert A[i] >= A[j], (i, j)
            st += [2 * j, 2 * j + 1]
    return True
def insert(A, x):
    A.append(x); i = len(A) - 1; log = []
    if i == 1: return log
    p = i // 2
    if is_min(i):
        if A[i] > A[p]:
            A[i], A[p] = A[p], A[i]; log.append((i, p)); i = p; _up(A, i, max, log)
        else: _up(A, i, min, log)
    else:
        if A[i] < A[p]:
            A[i], A[p] = A[p], A[i]; log.append((i, p)); i = p; _up(A, i, min, log)
        else: _up(A, i, max, log)
    return log
def _up(A, i, f, log):
    while i // 4 >= 1:
        g = i // 4
        if (f is min and A[i] < A[g]) or (f is max and A[i] > A[g]):
            A[i], A[g] = A[g], A[i]; log.append((i, g)); i = g
        else: break
def _down(A, i, log):
    n = len(A) - 1; mn = is_min(i)
    while 2 * i <= n:
        cand = [c for c in (2 * i, 2 * i + 1, 4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3) if c <= n]
        m = min(cand, key=lambda c: A[c]) if mn else max(cand, key=lambda c: A[c])
        if m >= 4 * i:  # grandchild
            if (mn and A[m] < A[i]) or (not mn and A[m] > A[i]):
                A[m], A[i] = A[i], A[m]; log.append((m, i))
                p = m // 2
                if (mn and A[m] > A[p]) or (not mn and A[m] < A[p]):
                    A[m], A[p] = A[p], A[m]; log.append((m, p))
                i = m
            else: break
        else:
            if (mn and A[m] < A[i]) or (not mn and A[m] > A[i]):
                A[m], A[i] = A[i], A[m]; log.append((m, i))
            break
def delete_min(A):
    n = len(A) - 1; x = A[1]; A[1] = A[n]; A.pop(); log = []
    if len(A) > 1: _down(A, 1, log)
    return x, log
def delete_max(A):
    n = len(A) - 1
    if n == 1: return A.pop(), []
    m = 2 if n == 2 or A[2] >= A[3] else 3
    x = A[m]; A[m] = A[n]; A.pop(); log = []
    if m < len(A): _down(A, m, log)
    return x, log

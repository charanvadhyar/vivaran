"""Fake (lighter) coin: halving and thirds, with weighing logs. coins numbered 1..n."""
import math
def halves(n, fake):
    lo, hi = 1, n; log = []
    while lo < hi:
        m = hi - lo + 1; h = m // 2
        L = list(range(lo, lo + h)); R = list(range(lo + h, lo + 2 * h)); aside = list(range(lo + 2 * h, hi + 1))
        if fake in L: res = "left lighter"; lo, hi = L[0], L[-1]
        elif fake in R: res = "right lighter"; lo, hi = R[0], R[-1]
        else: res = "balance"; lo, hi = aside[0], aside[-1]
        log.append((L, R, aside, res, (lo, hi)))
    return lo, log
def thirds(n, fake):
    lo, hi = 1, n; log = []
    while lo < hi:
        m = hi - lo + 1; g = math.ceil(m / 3)
        if 2 * g > m: g = m // 2
        L = list(range(lo, lo + g)); R = list(range(lo + g, lo + 2 * g)); rest = list(range(lo + 2 * g, hi + 1))
        if fake in L: res = "left lighter"; lo, hi = L[0], L[-1]
        elif fake in R: res = "right lighter"; lo, hi = R[0], R[-1]
        else: res = "balance"; lo, hi = rest[0], rest[-1]
        log.append((L, R, rest, res, (lo, hi)))
    return lo, log
def worst(f, n): return max(len(f(n, k)[1]) for k in range(1, n + 1))

"""Memory banks: one access may start per cycle; a bank stays busy for `busy` cycles."""
from math import gcd


def load_time(n, stride, banks, busy, latency):
    free = [0] * banks
    t = -1
    for i in range(n):
        b = (i * stride) % banks
        t = max(t + 1, free[b])
        free[b] = t + busy
    return t + latency + 1


def visited(stride, banks):
    return banks // gcd(stride, banks)

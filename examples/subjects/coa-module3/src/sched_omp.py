"""OpenMP loop schedules on a loop whose iteration i costs cost[i]."""
import math


def chunks_static(n, p, c=None):
    if c is None:
        q, r = divmod(n, p); out, s = [], 0
        for t in range(p):
            k = q + (t < r); out.append((t, list(range(s, s + k)))); s += k
        return out
    out = []
    for j, s in enumerate(range(0, n, c)):
        out.append((j % p, list(range(s, min(n, s + c)))))
    return out


def guided_sizes(n, p, c=1):
    sizes, rem = [], n
    while rem > 0:
        k = max(c, math.ceil(rem / p)); k = min(k, rem); sizes.append(k); rem -= k
    return sizes


def run_static(cost, p, c=None):
    load = [0] * p; its = [[] for _ in range(p)]
    for t, ch in chunks_static(len(cost), p, c):
        load[t] += sum(cost[i] for i in ch); its[t] += ch
    return load, its


def run_greedy(cost, p, sizes):
    """dynamic / guided: an idle thread (lowest id on ties) takes the next chunk."""
    free = [0] * p; its = [[] for _ in range(p)]; load = [0] * p; s = 0
    for k in sizes:
        t = min(range(p), key=lambda x: (free[x], x))
        ch = list(range(s, s + k)); s += k
        w = sum(cost[i] for i in ch); free[t] += w; load[t] += w; its[t] += ch
    return load, its, max(free)

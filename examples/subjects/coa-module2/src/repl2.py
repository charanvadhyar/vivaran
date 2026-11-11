def run(seq, n, pol):
    fr, out, last, order = [], [], {}, []
    for t, x in enumerate(seq):
        hit = x in fr
        victim = None
        if not hit:
            if len(fr) < n:
                fr.append(x)
            else:
                if pol == "FIFO":
                    victim = order.pop(0); i = fr.index(victim)
                elif pol == "LRU":
                    victim = min(fr, key=lambda y: last[y]); i = fr.index(victim)
                else:
                    fut = seq[t + 1:]
                    victim = max(fr, key=lambda y: (fut.index(y) if y in fut else 10**9, -fr.index(y)))
                    i = fr.index(victim)
                fr[i] = x
                if pol == "FIFO": pass
            if pol == "FIFO": order.append(x)
        last[x] = t
        out.append((x, list(fr), hit, victim))
    return out

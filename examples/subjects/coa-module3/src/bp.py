def one_bit(seq, init='N'):
    p, out = init, []
    for o in seq:
        out.append((p, p == o)); p = o
    return out
def two_bit(seq, init=0):
    """states 0 strongly NT, 1 weakly NT, 2 weakly T, 3 strongly T"""
    s, out = init, []
    for o in seq:
        pred = 'T' if s >= 2 else 'N'
        out.append((s, pred, pred == o))
        s = min(3, s + 1) if o == 'T' else max(0, s - 1)
    return out, s
def corr11(seq, hist='N'):
    """seq: list of (branch, outcome). (1,1): per branch two 1-bit predictors chosen by the last outcome of any branch."""
    tab, out = {}, []
    for b, o in seq:
        p = tab.get((b, hist), 'N')
        out.append((hist, p, p == o)); tab[(b, hist)] = o; hist = o
    return out, tab
def onebit_per(seq):
    tab, out = {}, []
    for b, o in seq:
        p = tab.get(b, 'N'); out.append((p, p == o)); tab[b] = o
    return out

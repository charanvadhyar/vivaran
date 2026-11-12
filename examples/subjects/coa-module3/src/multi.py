"""2-issue dynamically scheduled machine. prog: list of (text, kind, dest, [srcs]).
kinds: load (exec 2), alu (1), store (1, needs value), branch (1).
issue: up to W per cycle, in order. exec start >= issue+1 and >= producer write + 1 (results written the cycle after exec ends;
up to W results per cycle). spec=False: nothing after a branch may start executing before the cycle after that branch executes.
commit (spec): up to W per cycle, in order, cycle after write (stores/branches: cycle after exec)."""
LAT = {'load': 2, 'alu': 1, 'store': 1, 'branch': 1}
def run(prog, W=2, spec=True):
    n = len(prog); iss=[0]*n; st=[0]*n; en=[0]*n; wr=[None]*n; cm=[0]*n
    cdb = {}
    for i,(t,k,d,srcs) in enumerate(prog):
        iss[i] = (i // W) + 1
        s = iss[i] + 1
        for r in srcs:
            pr = [j for j in range(i) if prog[j][2] == r]
            if pr: s = max(s, wr[pr[-1]] + 1)
        if not spec:
            br = [j for j in range(i) if prog[j][1] == 'branch']
            if br: s = max(s, en[br[-1]] + 1)
        st[i] = s; en[i] = s + LAT[k] - 1
        if d:
            w = en[i] + 1
            while cdb.get(w, 0) >= W: w += 1
            cdb[w] = cdb.get(w, 0) + 1; wr[i] = w
    last, cnt = 0, {}
    for i,(t,k,d,srcs) in enumerate(prog):
        ready = (wr[i] if wr[i] else en[i]) + 1
        c = max(ready, last)
        while cnt.get(c, 0) >= W: c += 1
        cnt[c] = cnt.get(c, 0) + 1; cm[i] = c; last = c
    return list(zip(iss, st, en, wr, cm))

"""Warp scheduling: each warp runs LD, ADD (needs the LD, latency L), LD, ADD, ...
One instruction issues per cycle, from the lowest-numbered ready warp."""


def schedule(nwarps, cycles, L=4):
    ready = [1] * nwarps           # cycle at which the warp's next instruction may issue
    nxt = ['LD'] * nwarps
    out = []
    for c in range(1, cycles + 1):
        w = next((w for w in range(nwarps) if ready[w] <= c), None)
        if w is None:
            out.append('–'); continue
        op = nxt[w]
        out.append(f"W{w} {op}")
        if op == 'LD':
            ready[w] = c + L; nxt[w] = 'ADD'
        else:
            ready[w] = c + 1; nxt[w] = 'LD'
    return out


def occupancy(tpb, regs, smem_kb, max_threads=2048, max_regs=65536, max_blocks=32, smem_total=96):
    lim = {'threads': max_threads // tpb, 'registers': max_regs // (tpb * regs),
           'shared memory': int(smem_total // smem_kb) if smem_kb else 10**9, 'blocks': max_blocks}
    b = min(lim.values())
    return lim, b, b * tpb // 32, b * tpb // 32 / (max_threads // 32)

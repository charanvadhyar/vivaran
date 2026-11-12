"""MSI / MESI snooping on one block. ops: list of (core, 'R'|'W'). Returns per step: states after, bus action, data source."""
def run(ops, cores=('P1', 'P2', 'P3'), mesi=False):
    st = {c: 'I' for c in cores}; out = []
    for c, op in ops:
        s = st[c]; others = [o for o in cores if o != c and st[o] != 'I']; bus = '–'; src = ''
        if op == 'R':
            if s == 'I':
                bus = 'BusRd'
                owner = [o for o in others if st[o] in 'ME']
                if owner and st[owner[0]] == 'M':
                    src = f'{owner[0]} (writes back)'
                elif owner and mesi and st[owner[0]] == 'E':
                    src = 'memory'
                else:
                    src = 'memory'
                for o in others: st[o] = 'S'
                st[c] = 'S' if others or not mesi else 'E'
            else:
                bus = '– (hit)'
        else:
            if s == 'M':
                bus = '– (hit)'
            elif s == 'E':
                bus = '– (E → M, silent)'; st[c] = 'M'
            elif s == 'S':
                bus = 'BusUpgr'
                for o in others: st[o] = 'I'
                st[c] = 'M'
            else:
                bus = 'BusRdX'
                owner = [o for o in others if st[o] == 'M']
                src = f'{owner[0]} (writes back)' if owner else 'memory'
                for o in others: st[o] = 'I'
                st[c] = 'M'
        out.append((c, op, dict(st), bus, src))
    return out
def bus_count(res):
    return sum(1 for *_, b, _ in res if not b.startswith('–'))

"""Directory-based coherence (H&P simplified protocol, no acks counted).
State per block: U (uncached), S (shared, sharer set), M (modified, owner).
Messages counted: request to home, data reply, invalidates, fetch, write-back."""


def run(ops):
    state, sh = 'U', set()
    out = []
    for p, o in ops:
        msgs = []
        if o == 'R':
            if (state == 'S' and p in sh) or (state == 'M' and p in sh):
                pass  # hit
            elif state in 'US':
                msgs = [f"{p}→H read miss", f"H→{p} data reply"]
                state = 'S'; sh = sh | {p}
            else:
                (own,) = sh
                msgs = [f"{p}→H read miss", f"H→{own} fetch", f"{own}→H write-back", f"H→{p} data reply"]
                state = 'S'; sh = {own, p}
        else:
            if state == 'M' and p in sh:
                pass
            elif state == 'U':
                msgs = [f"{p}→H write miss", f"H→{p} data reply"]
            elif state == 'S':
                msgs = [f"{p}→H write miss"] + [f"H→{q} invalidate" for q in sorted(sh - {p})] + [f"H→{p} data reply"]
            else:
                (own,) = sh
                msgs = [f"{p}→H write miss", f"H→{own} fetch/invalidate", f"{own}→H write-back", f"H→{p} data reply"]
            state = 'M'; sh = {p}
        out.append((p, o, state, sorted(sh), msgs))
    return out

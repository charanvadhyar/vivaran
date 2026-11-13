"""Shared action helpers for DSA scripts."""
def _d(d): return {"delay": d} if d else {}
hl = lambda t, d=0: {"action": "highlight", "target": t, **_d(d)}
mk = lambda t, d=0: {"action": "mark", "target": t, **_d(d)}
dim = lambda t, d=0: {"action": "dim", "target": t, **_d(d)}
rs = lambda t, d=0: {"action": "reset", "target": t, **_d(d)}
rv = lambda t, d=0: {"action": "reveal", "target": t, **_d(d)}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **_d(d)}
pt = lambda p, to, d=0: {"action": "point", "target": p, "to": to, **_d(d)}
sw = lambda a, b, d=0: {"action": "swap", "a": a, "b": b, **_d(d)}
cmp = lambda a, b, d=0: {"action": "compare", "a": a, "b": b, **_d(d)}
ins = lambda t, i, v, d=0: {"action": "insert", "target": t, "index": i, "value": v, **_d(d)}
rm = lambda t, d=0: {"action": "remove", "target": t, **_d(d)}
addn = lambda t, i, label=None, d=0: {"action": "add_node", "target": t, "id": i, **({"label": label} if label else {}), **_d(d)}
adde = lambda t, a, b, label=None, d=0: {"action": "add_edge", "target": t, "from": a, "to": b, **({"label": label} if label else {}), **_d(d)}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

def setrow(arr_id, old, new, d0=0.0, step=0.08):
    """set only the cells that change, staggered"""
    out, k = [], 0
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b:
            out.append(st(f"{arr_id}[{i}]", b, round(min(0.9, d0 + k * step), 2))); k += 1
    return out

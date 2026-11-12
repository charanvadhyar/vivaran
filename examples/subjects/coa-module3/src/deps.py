"""Find true/anti/output dependences in a straight-line fragment. Each instr: (name, dest or None, [sources])."""
def deps(prog):
    out = []
    for j in range(len(prog)):
        for i in range(j):
            ni, di, si = prog[i]; nj, dj, sj = prog[j]
            for r in sj:
                if di == r and not any(prog[k][1] == r for k in range(i + 1, j)):
                    out.append(("true", i + 1, j + 1, r))
            if dj is not None and dj in si and not any(prog[k][1] == dj for k in range(i + 1, j)):
                out.append(("anti", i + 1, j + 1, dj))
            if dj is not None and di == dj and not any(prog[k][1] == dj for k in range(i + 1, j)):
                out.append(("output", i + 1, j + 1, dj))
    return sorted(out, key=lambda x: (["true", "anti", "output"].index(x[0]), x[1], x[2]))

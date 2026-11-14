INF = float("inf")
def mcm(p):
    n = len(p) - 1; m = [[0] * (n + 1) for _ in range(n + 1)]; s = [[0] * (n + 1) for _ in range(n + 1)]; detail = {}
    for l in range(2, n + 1):
        for i in range(1, n - l + 2):
            j = i + l - 1; m[i][j] = INF; opts = []
            for k in range(i, j):
                q = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]; opts.append((k, q))
                if q < m[i][j]: m[i][j] = q; s[i][j] = k
            detail[(i, j)] = opts
    return m, s, detail
def paren(s, i, j):
    return f"A{i}" if i == j else "(" + paren(s, i, s[i][j]) + paren(s, s[i][j] + 1, j) + ")"
def lcs(X, Y):
    m, n = len(X), len(Y); c = [[0] * (n + 1) for _ in range(m + 1)]; b = [[""] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]: c[i][j] = c[i - 1][j - 1] + 1; b[i][j] = "↖"
            elif c[i - 1][j] >= c[i][j - 1]: c[i][j] = c[i - 1][j]; b[i][j] = "↑"
            else: c[i][j] = c[i][j - 1]; b[i][j] = "←"
    out = []; i, j = m, n
    while i and j:
        if b[i][j] == "↖": out.append(X[i - 1]); i -= 1; j -= 1
        elif b[i][j] == "↑": i -= 1
        else: j -= 1
    return c, b, "".join(reversed(out))

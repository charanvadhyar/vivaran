"""DSA Module 4, video 2: longest common subsequence."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa4")
from common import Script
from h import *
from dp import lcs

X, Y = "ABCBDAB", "BDCABA"
C, B, LS = lcs(X, Y); assert LS == "BCBA" and C[7][6] == 4
EX, EY = "AGGTAB", "GXTXAYB"; EC, EB, ES = lcs(EX, EY); assert ES == "GTAB" and EC[6][7] == 4
assert 2 ** 7 == 128 and 2 ** 50 > 10 ** 15
path = []; i, j = 7, 6
while i and j:
    path.append((i, j, B[i][j]))
    if B[i][j] == "↖": i -= 1; j -= 1
    elif B[i][j] == "↑": i -= 1
    else: j -= 1
diag = [(i, j) for i, j, b in path if b == "↖"]
assert [X[i - 1] for i, j in reversed(diag)] == list("BCBA")

cols = ["", "0"] + [f"{j + 1} {Y[j]}" for j in range(len(Y))]
s = Script("Dynamic programming: longest common subsequence")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Subsequences, and why we compare them"],
    [2, "Optimal substructure: three cases"],
    [3, "The recurrence"],
    [4, "Filling Cormen's table"],
    [5, "Tracing back the subsequence"],
    [6, "The algorithm and its cost"],
    [7, "Exam question"]]})
s.obj({"id": "sq", "type": "table", "region": "center", "columns": ["subsequences", ""], "rows": [
    ["subsequence", "delete some characters, keep the order: B C D B is a subsequence of A B C B D A B"],
    ["common subsequence", "a subsequence of both strings"],
    ["LCS", "a longest common subsequence"],
    ["uses", "diff between file versions, DNA alignment, spell checking, plagiarism checks"],
    ["brute force", "a string of length m has 2ᵐ subsequences: 2⁵⁰ is over 10¹⁵"]]})
s.obj({"id": "sub", "type": "table", "region": "center", "columns": ["compare the last characters xₘ and yₙ", "then"], "rows": [
    ["xₘ = yₙ", "that character ends some LCS: LCS of the shorter prefixes, plus it"],
    ["xₘ ≠ yₙ", "an LCS drops xₘ or drops yₙ: take the longer of the two answers"],
    ["either string empty", "the LCS is empty"]]})
s.obj({"id": "rec", "type": "math", "region": "center", "lines": [
    "c[i, j] = \"length of an LCS of \" X_i = x_1 dots x_i \" and \" Y_j = y_1 dots y_j",
    "c[i, j] = cases(0 & \"if \" i = 0 \" or \" j = 0, c[i-1, j-1] + 1 & \"if \" x_i = y_j, max(c[i-1, j], c[i, j-1]) & \"if \" x_i != y_j)",
    "\"arrows: \" arrow.tl \" match, \" arrow.t \" from above, \" arrow.l \" from the left\""]})
s.obj({"id": "tb", "type": "table", "region": "center", "columns": cols,
       "rows": [["0", "0"] + ["0"] * 6] + [[f"{i} {X[i - 1]}", "0"] + [""] * 6 for i in range(1, 8)]})
s.obj({"id": "lc", "type": "code", "region": "center", "language": "text", "lines": [
    "LCS-LENGTH(X, Y, m, n)",
    "    for i = 0 to m:  c[i, 0] = 0;     for j = 0 to n:  c[0, j] = 0",
    "    for i = 1 to m",
    "        for j = 1 to n",
    "            if x[i] == y[j]:                 c[i, j] = c[i−1, j−1] + 1;  b[i, j] = ↖",
    "            elseif c[i−1, j] ≥ c[i, j−1]:   c[i, j] = c[i−1, j];      b[i, j] = ↑",
    "            else                             c[i, j] = c[i, j−1];      b[i, j] = ←",
    "",
    "PRINT-LCS(b, X, i, j):  follow the arrows from (m, n); print x[i] at every ↖, in reverse",
    "",
    "time Θ(m n), space Θ(m n);  length only: two rows, Θ(min(m, n)) space"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["X = A G G T A B,   Y = G X T X A Y B"],
    ["a) the length of an LCS, from the table"],
    ["b) an LCS, by tracing back"],
    ["c) how many table entries are computed?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["row of the table", "c[i, 1..7]", "note"], "rows": [
    ["i = 1, A", "0 0 0 0 1 1 1", "A matches y₅"],
    ["i = 2, G", "1 1 1 1 1 1 1", "G matches y₁"],
    ["i = 4, T", "1 1 2 2 2 2 2", "T matches y₃: G T"],
    ["i = 5, A", "1 1 2 2 3 3 3", "A matches y₅: G T A"],
    ["i = 6, B", "1 1 2 2 3 3 4", "B matches y₇: length 4, LCS = G T A B"],
    ["c)", "6 × 7", "42 entries, each Θ(1)"]]})

s.scene("intro")
s.step("When you compare two versions of a file, the tool finds the longest run of lines they share, in order, and shows you the rest as changes. Biologists do the same with DNA. The core problem is the longest common subsequence, and dynamic programming solves it with one table.", [s.head("Dynamic programming: longest common subsequence")])
s.step("Here are the seven stages.", show("stages"))
s.step("Subsequences, the three cases, the recurrence, and filling Cormen's table.", [hl("stages[0..=3]")])
s.step("Then tracing back the answer, the algorithm and its cost, and an exam question.", [hl("stages[4..=6]")])

s.scene("sq")
s.step("Stage 1: a subsequence keeps some of the characters, in their original order, but not necessarily next to each other. B, C, D, B is a subsequence of A, B, C, B, D, A, B.", [s.head("Stage 1 of 7: subsequences")] + hide("stages") + show("sq") + [hl("sq[0]")])
s.step("A common subsequence appears in both strings. We want a longest one: an LCS.", [hl("sq[1..=2]")])
s.step("A small example: A, B, C and A, C, B. Both A, B and A, C are common subsequences, of length 2. A, B, C is not common. So the LCS has length 2, and there are two of them: the LCS need not be unique.", [hl("sq[2]")])
s.step("It powers file comparison tools, DNA alignment, and plagiarism checks.", [hl("sq[3]")])
s.step("Checking every subsequence is hopeless: a string of length 50 has over a thousand million million of them.", [hl("sq[4]"), s.take("subsequence: same order, gaps allowed")])

s.scene("sub")
s.step("Stage 2: look at the last characters, x m and y n.", [s.head("Stage 2 of 7: three cases"), s.untake()] + hide("sq") + show("sub"))
s.step("If they are equal, that character can end an LCS. The rest is an LCS of the two strings without their last characters.", [hl("sub[0]")])
s.step("If they differ, an LCS cannot use both. It is an LCS of X without its last character and Y, or of X and Y without its last character: whichever is longer.", [hl("sub[1]")])
s.step("And if either string is empty, the LCS is empty. Each case shrinks the problem to prefixes: optimal substructure.", [hl("sub[2]"), s.take("match: diagonal +1 · no match: best of up or left")])

s.scene("rec")
s.step("Stage 3: let c of i, j be the length of an LCS of the first i characters of X and the first j of Y.", [s.head("Stage 3 of 7: the recurrence"), s.untake()] + hide("sub") + show("rec") + [hl("rec[0]")])
s.step("c is 0 when i or j is 0. If x i equals y j, c of i, j is c of i minus 1, j minus 1, plus 1. Otherwise it is the larger of c of i minus 1, j, and c of i, j minus 1.", [rv("rec[1]"), hl("rec[1]")])
s.step("We also record where each value came from: a diagonal arrow for a match, an up arrow or a left arrow otherwise. The arrows let us rebuild the subsequence.", [rv("rec[2]"), hl("rec[2]"), s.take("c[i,j] depends on up, left and up-left")])
s.step("Computing this recursively would repeat work: c of i minus 1, j and c of i, j minus 1 both need c of i minus 1, j minus 1, and so on down, exponentially. But there are only m times n different subproblems, so a table of that size holds them all.", [hl("rec[1]")])

s.scene("fill")
s.step("Stage 4: Cormen's example. X is A, B, C, B, D, A, B down the side; Y is B, D, C, A, B, A across the top. Row 0 and column 0 are all 0.", [s.head("Stage 4 of 7: filling the table"), s.untake()] + hide("rec") + show("tb") + [hl("tb[0]")])
rsay = ["Row 1, A: no match until A in column 4, which gives 0 plus 1: 1. Then 1 carries to the right.",
        "Row 2, B: B matches column 1: 1. Then 1s, until B in column 5: diagonal 1 plus 1, 2.",
        "Row 3, C: C matches column 3, diagonal 1 plus 1: 2. The rest carry 2.",
        "Row 4, B: B in column 1 gives 1; B in column 5 builds on row 3's 2: 3.",
        "Row 5, D: D in column 2, diagonal 1 plus 1: 2. The 3 above carries down.",
        "Row 6, A: A in column 4 gives 3; A in column 6, diagonal 3 plus 1: 4.",
        "Row 7, B: B in column 5 gives 4. The corner holds 4: an LCS has length 4."]
for i in range(1, 8):
    if i == 4:
        s.step("Look closely at one cell: row 3, column 3. x 3 is C and y 3 is C: a match. So take the diagonal neighbour, row 2, column 2, which is 1, and add 1: 2, with a diagonal arrow.", [hl("tb[3][4]"), hl("tb[2][3]", 0.5)])
        s.step("And row 3, column 4: C against A, no match. Above is 1, to the left is 2. Take the larger, 2, with a left arrow.", [hl("tb[3][5]")])
    acts = [hl(f"tb[{i}]")] + [st(f"tb[{i}][{j + 1}]", f"{C[i][j]}{B[i][j]}", round(0.08 * j, 2)) for j in range(1, 7)]
    if i == 7: acts += [mk("tb[7][7]", 0.7), s.take("c[7, 6] = 4")]
    s.step(rsay[i - 1], acts)

s.scene("back")
s.step("Stage 5: to find the subsequence itself, start at the corner and follow the arrows back.", [s.head("Stage 5 of 7: tracing back"), s.untake(), hl("tb[7][7]")])
s.step("An up or left arrow just moves. Every diagonal arrow is a match: write down its character.", [mk(f"tb[{i}][{j + 1}]", round(0.06 * k, 2)) for k, (i, j, b) in enumerate(path)])
s.step("Reading the matches from the corner gives A, B, C, B; reversed, the LCS is B, C, B, A. Check: it appears in order in both strings.", [x for k, (i, j) in enumerate(diag) for x in (st(f"tb[{i}][{j + 1}]", f"{C[i][j]}↖ {X[i - 1]}", round(0.2 * k, 2)), mk(f"tb[{i}][{j + 1}]", round(0.2 * k + 0.05, 2)))] + [s.take("LCS = B C B A")])
s.step("When the up and left values tie, Cormen's rule prefers up. Preferring left can give a different LCS of the same length, B, D, A, B for example. Any one is a correct answer.", [hl("tb[5]")])

s.scene("algo")
s.step("Stage 6: LCS-LENGTH starts with row 0 and column 0 at zero.", [s.head("Stage 6 of 7: the algorithm"), s.untake()] + hide("tb") + show("lc") + [ml("lc", 1, 2)])
s.step("Then it fills row by row, left to right, applying the three cases and storing an arrow in b.", [ml("lc", 3, 7)])
s.step("PRINT-LCS follows the arrows from the corner, printing the character at each diagonal, in reverse order by recursion.", [ml("lc", 9, 9)])
s.step("m times n entries, each in constant time: Theta of m n time and space. If only the length is needed, two rows are enough.", [ml("lc", 11, 11), s.take("Θ(m·n) time and space")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("lc") + show("q") + [hl("q[0]")])
s.step("Fill the table, give the length, trace back an LCS, and count the entries. Pause and work it out.", [hl("q[1..=3]")])
s.step("Row 1, A: A first matches Y's fifth character, so the row is 0, 0, 0, 0, 1, 1, 1.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Row 2, G: G matches the first character of Y, so it is 1 all the way. Row 3, the second G, is the same.", [hl("qa[1]")])
s.step("Row 4, T: T matches column 3, building on G: 2. Row 5, A: A in column 5, building on G, T: 3.", [hl("qa[2..=3]")])
s.step("Row 6, B: B in column 7, building on G, T, A: 4. Tracing back gives G, T, A, B.", [hl("qa[4]"), mk("qa[4][2]", 0.5)])
s.step("c: 6 rows by 7 columns: 42 entries, not counting row and column 0.", [hl("qa[5]")])
s.step("The usual slip: confusing a subsequence with a substring. G, T, A, B is not contiguous in either string, and it does not need to be.", [s.take("subsequence ≠ substring")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Compare last characters: on a match, extend the diagonal by one; otherwise take the better of up and left.", [hl("stages[0..=3]")])
s.step("Following the arrows back from the corner spells out an LCS, and the whole table costs Theta of m n.", [hl("stages[4..=5]")])
s.step("Next video: a different design technique for search problems. Backtracking, starting with the N-Queens problem.", [mk("stages[0..=6]"), s.take("Next: backtracking, N-Queens")])

s.save("/home/claude/playlist/dsa4/d4v2.json")

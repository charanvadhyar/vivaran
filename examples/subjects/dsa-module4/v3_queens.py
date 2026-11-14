"""DSA Module 4, video 3: backtracking, the N-Queens problem."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa4")
from common import Script
from h import *
from bt import nqueens_trace, count_solutions

EV, SOL = nqueens_trace(4); assert SOL == [[1, 3, 0, 2]] and sum(1 for e in EV if e[0] == "place") == 8
E5, S5 = nqueens_trace(5); assert S5 == [[0, 2, 4, 1, 3]] and not any(e[0] == "dead" for e in E5)
assert [count_solutions(n) for n in (4, 5, 6, 8)] == [2, 10, 4, 92]
assert nqueens_trace(4, False)[1] == [[1, 3, 0, 2], [2, 0, 3, 1]]
assert math.comb(16, 4) == 1820 and 4 ** 4 == 256 and math.factorial(4) == 24 and math.comb(64, 8) == 4426165368 and math.factorial(8) == 40320

s = Script("Backtracking: the N-Queens problem")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Backtracking: search with pruning"],
    [2, "The N-Queens problem"],
    [3, "Checking a square; the algorithm"],
    [4, "Four queens, traced"],
    [5, "How much the pruning saves"],
    [6, "The general backtracking template"],
    [7, "Exam question"]]})
s.obj({"id": "bk", "type": "table", "region": "center", "columns": ["backtracking", ""], "rows": [
    ["solution", "a vector (x₁, x₂, …, xₙ), chosen one component at a time"],
    ["state-space tree", "each level fixes one more component"],
    ["search", "depth first through that tree"],
    ["bounding function", "the moment a partial vector cannot be completed, stop exploring below it"],
    ["backtrack", "undo the last choice, and try the next value"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["N-Queens", ""], "rows": [
    ["place n queens on an n × n board", "no two attack: no shared row, column or diagonal"],
    ["any 4 squares on a 4 × 4 board", "C(16, 4) = 1820 ways"],
    ["one queen per row", "xᵢ = the column of the queen in row i: 4⁴ = 256"],
    ["also one per column", "a permutation: 4! = 24"],
    ["8 queens", "C(64, 8) ≈ 4.4 billion placements; 8! = 40,320 permutations; 92 solutions"]]})
s.obj({"id": "pc", "type": "code", "region": "center", "language": "text", "lines": [
    "PLACE(k, i)          // can queen k go in column i, given x[1 .. k−1]?",
    "    for j = 1 to k − 1",
    "        if x[j] == i                      return false   // same column",
    "        if |x[j] − i| == |j − k|          return false   // same diagonal",
    "    return true",
    "",
    "NQUEENS(k, n)        // place queens k .. n",
    "    for i = 1 to n",
    "        if PLACE(k, i)",
    "            x[k] = i",
    "            if k == n:  print x[1 .. n]",
    "            else NQUEENS(k + 1, n)"]})
s.obj({"id": "bd", "type": "table", "region": "left", "columns": ["", "c1", "c2", "c3", "c4"],
       "rows": [[f"r{r}", "", "", "", ""] for r in range(1, 5)]})
s.obj({"id": "lg", "type": "table", "region": "right", "columns": ["x = (x₁, x₂, x₃, x₄)", "event"], "rows": [["", ""] for _ in range(8)]})
s.obj({"id": "sv", "type": "table", "region": "center", "columns": ["how much is searched", "4 queens", "8 queens"], "rows": [
    ["any squares", "1820", "4,426,165,368"],
    ["one per row and column (permutations)", "24", "40,320"],
    ["backtracking, first solution", "8 queens placed", "113 placements"],
    ["backtracking, all solutions", "16 queens placed, 2 solutions", "2,056 placements, 92 solutions"]]})
s.obj({"id": "tp", "type": "code", "region": "center", "language": "text", "lines": [
    "BACKTRACK(k)",
    "    for each candidate value v for x[k]",
    "        if (x[1], …, x[k−1], v) passes the bounding function",
    "            x[k] = v",
    "            if x[1 .. k] is a complete solution:  report it",
    "            else BACKTRACK(k + 1)",
    "",
    "same skeleton: subset sum, graph colouring, the knight's tour (lab 7)",
    "worst case still exponential: pruning is what makes it practical"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) the first solution NQUEENS finds for n = 5 (columns tried from 1 upward)"],
    ["b) does it ever backtrack on the way?"],
    ["c) the two solutions for n = 4, and how they are related"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "r1: c1 · r2: c1 column, c2 diagonal → c3 · r3: c1–c4 attacked → c5", ""],
    ["a)", "r4: c1 column → c2 · r5: c1, c2, c3 columns → c4", "x = (1, 3, 5, 2, 4)"],
    ["b)", "every row found a safe column at once", "no backtracking"],
    ["c)", "(2, 4, 1, 3) and (3, 1, 4, 2)", "mirror images of each other"]]})

s.scene("intro")
s.step("Can eight queens sit on a chessboard without any two attacking each other? There are over four billion ways to place them. Backtracking finds an answer after trying about a hundred, by giving up on a partial placement the moment it goes wrong.", [s.head("Backtracking: the N-Queens problem")])
s.step("Here are the seven stages.", show("stages"))
s.step("Backtracking, the N-Queens problem, the algorithm, and a full trace with four queens.", [hl("stages[0..=3]")])
s.step("Then how much the pruning saves, the general template, and an exam question.", [hl("stages[4..=6]")])

s.scene("bk")
s.step("Stage 1: backtracking builds a solution as a vector, one component at a time.", [s.head("Stage 1 of 7: backtracking")] + hide("stages") + show("bk") + [hl("bk[0]")])
s.step("The choices form a state-space tree: the root is the empty vector, and each level fixes one more component.", [hl("bk[1]")])
s.step("The search goes depth first through that tree.", [hl("bk[2]")])
s.step("The key ingredient is the bounding function: as soon as a partial vector cannot possibly be completed, the whole subtree below it is skipped.", [hl("bk[3]")])
s.step("Then the algorithm backtracks: it undoes the last choice and tries the next value.", [hl("bk[4]"), s.take("depth-first + prune dead partial solutions")])

s.scene("pb")
s.step("Stage 2: place n queens on an n by n board so that no two share a row, a column or a diagonal.", [s.head("Stage 2 of 7: N-Queens"), s.untake()] + hide("bk") + show("pb") + [hl("pb[0]")])
s.step("Choosing any four squares on a 4 by 4 board: 1820 ways.", [hl("pb[1]")])
s.step("Since each row needs exactly one queen, write x i for the column of the queen in row i. Now there are 4 to the 4, 256 vectors.", [hl("pb[2]")])
s.step("And the columns must all differ, so x is a permutation: 24.", [hl("pb[3]")])
s.step("For eight queens: over 4 billion placements, 40 thousand permutations, and only 92 solutions.", [hl("pb[4]"), s.take("x[i] = column of the queen in row i")])

s.scene("algo")
s.step("Stage 3: can queen k go in column i? Compare it with each earlier queen j.", [s.head("Stage 3 of 7: the algorithm"), s.untake()] + hide("pb") + show("pc") + [ml("pc", 1, 2)])
s.step("Same column if x j equals i.", [ml("pc", 3, 3)])
s.step("Same diagonal if the column difference equals the row difference: the absolute value of x j minus i, equals the absolute value of j minus k.", [ml("pc", 4, 5)])
s.step("For example, a queen at row 1, column 1 and one at row 3, column 3: two rows apart and two columns apart, so they share a diagonal. Row 1, column 3 and row 2, column 2: one and one: the other diagonal.", [ml("pc", 4, 4)])
s.step("NQUEENS tries every column for queen k. If it is safe, place it, then either print the full solution, or recurse to the next row.", [ml("pc", 7, 12)])
s.step("When the loop runs out of columns, the call simply returns: that is the backtrack. The caller then tries its own next column.", [ml("pc", 8, 8), s.take("same diagonal: |x[j] − i| = |j − k|")])

s.scene("trace")
groups = [
    ("Stage 4: four queens. Row 1: column 1 is safe. Place it.", [(0, 0, "Q")], [], "(1)", "place"),
    ("Row 2: column 1 shares a column, column 2 a diagonal. Column 3 is safe.", [(1, 2, "Q")], [(1, 0), (1, 1)], "(1, 3)", "place"),
    ("Row 3: column 1 is attacked by the first queen; columns 2 and 4 by the second, diagonally; column 3 shares the second queen's column. A dead end. Backtrack: remove the queen in row 2.", [(1, 2, "")], [(2, 0), (2, 1), (2, 2), (2, 3)], "(1, –)", "dead end"),
    ("Try row 2, column 4. Safe. Row 3: column 1 is attacked; column 2 is safe.", [(1, 3, "Q"), (2, 1, "Q")], [(2, 0)], "(1, 4, 2)", "place"),
    ("Row 4: every column is attacked. Backtrack to row 3: columns 3 and 4 are attacked too. Back to row 2: no columns left. Back to row 1.", [(2, 1, ""), (1, 3, ""), (0, 0, "")], [(3, 0), (3, 1), (3, 2), (3, 3)], "(–)", "dead ends"),
    ("Row 1, column 2. Row 2: columns 1 and 3 are diagonal, column 2 is the same column. Column 4 is safe.", [(0, 1, "Q"), (1, 3, "Q")], [(1, 0), (1, 1), (1, 2)], "(2, 4)", "place"),
    ("Row 3, column 1: safe.", [(2, 0, "Q")], [], "(2, 4, 1)", "place"),
    ("Row 4: columns 1 and 2 share columns. Column 3 is safe. All four queens placed: the solution 2, 4, 1, 3.", [(3, 2, "Q")], [(3, 0), (3, 1)], "(2, 4, 1, 3)", "solution")]
prevx = []
for k, (say, sets, rej, xv, evn) in enumerate(groups):
    acts = [s.head("Stage 4 of 7: four queens"), s.untake()] + hide("pc") + show("bd", "lg") if k == 0 else []
    acts += [st(f"bd[{r}][{c + 1}]", "", 0) for r, c in prevx]
    acts += [st(f"bd[{r}][{c + 1}]", "×", round(0.08 * i, 2)) for i, (r, c) in enumerate(rej)]
    acts += [st(f"bd[{r}][{c + 1}]", v, round(0.5 + 0.08 * i, 2)) for i, (r, c, v) in enumerate(sets)]
    acts += [st(f"lg[{k}][0]", xv, 0.6), st(f"lg[{k}][1]", evn, 0.65), hl(f"lg[{k}]")]
    if evn == "solution": acts += [mk(f"bd[{r}]", 0.8) for r in range(4)] + [s.take("x = (2, 4, 1, 3)")]
    s.step(say, acts); prevx = rej
s.step("To find every solution, the algorithm does not stop here: it prints this one, then carries on as if it had failed. Continuing, it finds exactly one more: 3, 1, 4, 2.", [hl("lg[7]")])
s.step("In all, 8 queens were placed and 4 removed along the way, instead of checking 256 vectors.", [st(f"bd[{r}][{c + 1}]", "") for r, c in prevx] + [hl("lg")])

s.scene("save")
s.step("Stage 5: how much does the pruning save? For 4 queens: 1820 square choices, 24 permutations, but backtracking places only 8 queens to find the first solution.", [s.head("Stage 5 of 7: what pruning saves"), s.untake()] + hide("bd", "lg") + show("sv") + [hl("sv[0..=2]")])
s.step("For 8 queens, the first solution comes after 113 placements, and all 92 solutions after about two thousand. Compare 4.4 billion.", [hl("sv[2..=3]")])
s.step("Each dead end cuts off an entire subtree: every completion of a bad partial placement is skipped at once.", [s.take("prune early, prune whole subtrees")])

s.scene("tp")
s.step("Stage 6: the same skeleton solves many problems. For each candidate value of the next component:", [s.head("Stage 6 of 7: the template"), s.untake()] + hide("sv") + show("tp") + [ml("tp", 1, 2)])
s.step("If the partial solution still passes the bounding function, fix the value, and either report a complete solution or recurse.", [ml("tp", 3, 6)])
s.step("Subset sum, graph colouring, and the lab's knight's tour all fit this template; the next videos cover them.", [ml("tp", 8, 8)])
s.step("Backtracking is still exponential in the worst case. What makes it practical is how early the bounding function can say no.", [ml("tp", 9, 9), s.take("candidate → check → recurse → undo")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("tp") + show("q") + [hl("q[0]")])
s.step("Find the first 5-queens solution, say whether it backtracks, and find both 4-queens solutions. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: row 1, column 1. Row 2: column 1 shares a column, column 2 a diagonal: column 3. Row 3: columns 1 to 4 are all attacked: column 5.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Row 4: column 1 is a shared column, column 2 is safe. Row 5: columns 1, 2 and 3 are taken: column 4. The solution is 1, 3, 5, 2, 4.", [hl("qa[1]"), mk("qa[1][2]", 0.6)])
s.step("b: every row found a safe column immediately, so there was no backtracking at all. Five is an easier case than four.", [hl("qa[2]")])
s.step("c: 4 queens has exactly two solutions: 2, 4, 1, 3 and 3, 1, 4, 2. Each is the other reflected left to right.", [hl("qa[3]")])
s.step("The usual slip: forgetting the diagonal running the other way. The absolute value covers both diagonals at once.", [s.take("|Δcolumn| = |Δrow|: both diagonals")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Backtracking builds a solution component by component, depth first, and abandons a branch the moment it cannot succeed. For N-Queens, x i is the column in row i.", [hl("stages[0..=3]")])
s.step("The checks for column and diagonal prune so much that eight queens takes about a hundred placements instead of billions.", [hl("stages[4..=5]")])
s.step("Next video: backtracking for a numbers problem. Subset sum.", [mk("stages[0..=6]"), s.take("Next: subset sum")])

s.save("/home/claude/playlist/dsa4/d4v3.json")

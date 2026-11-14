"""DSA Module 4, video 1: dynamic programming, matrix chain multiplication."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa4")
from common import Script
from h import *
from dp import mcm, paren

P = [5, 4, 6, 2, 7]
M, S, D = mcm(P); assert M[1][4] == 158 and paren(S, 1, 4) == "((A1(A2A3))A4)"
assert D[(1, 3)] == [(1, 88), (2, 180)] and D[(2, 4)] == [(2, 252), (3, 104)] and D[(1, 4)] == [(1, 244), (2, 414), (3, 158)]
assert 120 + 5 * 6 * 2 + 5 * 2 * 7 == 250
assert 10 * 100 * 5 + 10 * 5 * 50 == 7500 and 100 * 5 * 50 + 10 * 100 * 50 == 75000
cat = lambda n: math.comb(2 * n, n) // (n + 1)
assert [cat(n - 1) for n in (3, 4, 5, 10)] == [2, 5, 14, 4862]
PE = [3, 5, 2, 4, 6]; ME, SE, DE = mcm(PE)
assert ME[1][4] == 114 and paren(SE, 1, 4) == "((A1A2)(A3A4))" and DE[(1, 4)] == [(1, 198), (2, 114), (3, 126)]
assert (ME[1][2], ME[2][3], ME[3][4], ME[1][3], ME[2][4]) == (30, 40, 48, 54, 108)
M6, S6, _ = mcm([30, 35, 15, 5, 10, 20, 25]); assert M6[1][6] == 15125

s = Script("Dynamic programming: matrix chain multiplication")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The order of multiplication matters"],
    [2, "Too many orders to try"],
    [3, "The dynamic-programming recurrence"],
    [4, "Filling the table: four matrices"],
    [5, "Reading off the answer; the algorithm"],
    [6, "What makes a problem dynamic programming"],
    [7, "Exam question"]]})
s.obj({"id": "ord", "type": "table", "region": "center", "columns": ["A1 10×100, A2 100×5, A3 5×50", "scalar multiplications"], "rows": [
    ["a p×q times q×r product", "p · q · r"],
    ["((A1 A2) A3)", "10·100·5 + 10·5·50 = 5000 + 2500 = 7,500"],
    ["(A1 (A2 A3))", "100·5·50 + 10·100·50 = 25000 + 50000 = 75,000"],
    ["same answer, ten times the work", "the problem: choose the parenthesization of least cost"]]})
s.obj({"id": "cnt", "type": "table", "region": "center", "columns": ["matrices n", "ways to parenthesize"], "rows": [
    ["3", "2"], ["4", "5"], ["5", "14"], ["10", "4,862"], ["n", "Catalan number: grows like 4ⁿ / n^1.5"]]})
s.obj({"id": "rec", "type": "math", "region": "center", "lines": [
    "A_i \" is \" p_(i-1) times p_i; quad m[i, j] = \"least cost of computing \" A_i A_(i+1) dots A_j",
    "\"the last multiplication splits at some \" k: quad (A_i dots A_k)(A_(k+1) dots A_j)",
    "m[i, j] = min_(i <= k < j) { m[i, k] + m[k+1, j] + p_(i-1) p_k p_j }, quad m[i, i] = 0",
    "s[i, j] = \"the best \" k"]})
s.obj({"id": "dims", "type": "table", "region": "center", "columns": ["matrix", "A1", "A2", "A3", "A4"], "rows": [["size", "5 × 4", "4 × 6", "6 × 2", "2 × 7"], ["p", "p0 = 5, p1 = 4", "p2 = 6", "p3 = 2", "p4 = 7"]]})
s.obj({"id": "mt", "type": "table", "region": "left", "columns": ["m", "j = 1", "j = 2", "j = 3", "j = 4"],
       "rows": [[f"i = {i}"] + ["0" if i == j else ("" if j > i else "·") for j in range(1, 5)] for i in range(1, 5)]})
s.obj({"id": "stt", "type": "table", "region": "right", "columns": ["s", "j = 2", "j = 3", "j = 4"],
       "rows": [[f"i = {i}"] + ["" if j > i else "·" for j in range(2, 5)] for i in range(1, 4)]})
s.obj({"id": "mc", "type": "code", "region": "center", "language": "text", "lines": [
    "MATRIX-CHAIN-ORDER(p, n)",
    "    for i = 1 to n:  m[i, i] = 0",
    "    for l = 2 to n                         // chain length",
    "        for i = 1 to n − l + 1",
    "            j = i + l − 1;   m[i, j] = ∞",
    "            for k = i to j − 1",
    "                q = m[i, k] + m[k+1, j] + p[i−1] · p[k] · p[j]",
    "                if q < m[i, j]:  m[i, j] = q;  s[i, j] = k",
    "    return m and s",
    "",
    "three nested loops: Θ(n³) time,  Θ(n²) space"]})
s.obj({"id": "dpw", "type": "table", "region": "center", "columns": ["dynamic programming", ""], "rows": [
    ["optimal substructure", "an optimal solution contains optimal solutions to subproblems"],
    ["overlapping subproblems", "plain recursion solves m[2, 3] again and again: exponential time"],
    ["DP", "solve each subproblem once, store it in a table, reuse it"],
    ["bottom-up", "fill the table from small chains to long ones (as here)"],
    ["top-down (memoised)", "recursion that checks the table first: same Θ(n³)"],
    ["the lab's AM-chain", "the + signs split it into separate product chains: optimise each, then add"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["dimensions p = ⟨3, 5, 2, 4, 6⟩: A1 3×5, A2 5×2, A3 2×4, A4 4×6"],
    ["a) the tables m and s"],
    ["b) the least number of scalar multiplications"],
    ["c) the optimal parenthesization"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["entry", "working", "value"], "rows": [
    ["m[1,2], m[2,3], m[3,4]", "3·5·2,  5·2·4,  2·4·6", "30, 40, 48"],
    ["m[1,3]", "k=1: 40 + 3·5·4 = 100;  k=2: 30 + 3·2·4 = 54", "54, s = 2"],
    ["m[2,4]", "k=2: 48 + 5·2·6 = 108;  k=3: 40 + 5·4·6 = 160", "108, s = 2"],
    ["m[1,4]", "k=1: 108 + 90 = 198;  k=2: 30 + 48 + 36 = 114;  k=3: 54 + 72 = 126", "114, s = 2"],
    ["c)", "split after A2: (A1 A2)(A3 A4)", "((A1 A2)(A3 A4))"]]})

s.scene("intro")
s.step("Multiplying a chain of matrices gives the same answer whichever pair you multiply first. But the work can differ by a factor of ten, or a thousand. Choosing the best order is the classic first example of dynamic programming, the main technique of this module.", [s.head("Dynamic programming: matrix chain multiplication")])
s.step("Here are the seven stages.", show("stages"))
s.step("Why the order matters, why we cannot try every order, the recurrence, and filling the table.", [hl("stages[0..=3]")])
s.step("Then reading off the answer, what makes a problem dynamic programming, and an exam question.", [hl("stages[4..=6]")])

s.scene("ord")
s.step("Stage 1: multiplying a p by q matrix by a q by r matrix takes p times q times r scalar multiplications.", [s.head("Stage 1 of 7: order matters")] + hide("stages") + show("ord") + [hl("ord[0]")])
s.step("Cormen's example: A1 is 10 by 100, A2 is 100 by 5, A3 is 5 by 50. First A1 times A2, then times A3: 5000 plus 2500, 7500.", [hl("ord[1]")])
s.step("First A2 times A3, then A1 times the result: 25 thousand plus 50 thousand, 75 thousand.", [hl("ord[2]")])
s.step("The same product, ten times the work. Our problem: given the dimensions, find the parenthesization with the fewest scalar multiplications.", [hl("ord[3]"), s.take("cost of p×q times q×r = p·q·r")])

s.scene("cnt")
s.step("Stage 2: why not try every order? Three matrices have 2 parenthesizations; four have 5; five have 14.", [s.head("Stage 2 of 7: too many orders"), s.untake()] + hide("ord") + show("cnt") + [hl("cnt[0..=2]")])
s.step("Ten matrices have 4862. The counts are the Catalan numbers, which grow exponentially, roughly 4 to the n.", [hl("cnt[3..=4]"), s.take("brute force is exponential")])

s.scene("rec")
s.step("Stage 3: let matrix A i be p i minus 1 by p i. Let m of i, j be the least cost of multiplying A i through A j.", [s.head("Stage 3 of 7: the recurrence"), s.untake()] + hide("cnt") + show("rec") + [hl("rec[0]")])
s.step("Whatever the best order, its very last multiplication splits the chain at some k: the product of A i to A k, times the product of A k plus 1 to A j.", [rv("rec[1]"), hl("rec[1]")])
s.step("And each half must itself be computed optimally, or we could improve the whole. So m of i, j is the minimum over k of: the cost of the left part, plus the right part, plus p i minus 1 times p k times p j to multiply the two results. A single matrix costs 0.", [rv("rec[2]"), hl("rec[2]")])
s.step("We also record s of i, j, the k that won, so we can rebuild the order later.", [rv("rec[3]"), hl("rec[3]"), s.take("m[i,j] = min over k of left + right + p(i−1)·p(k)·p(j)")])

s.scene("tab")
s.step("Stage 4: four matrices, 5 by 4, 4 by 6, 6 by 2 and 2 by 7. So p is 5, 4, 6, 2, 7.", [s.head("Stage 4 of 7: filling the table"), s.untake()] + hide("rec") + show("dims"))
s.step("The diagonal, single matrices, costs 0. We fill the table by chain length: first all pairs, then triples, then the whole chain.", hide("dims") + show("mt", "stt") + [hl("mt[0][1]"), hl("mt[1][2]", 0.2), hl("mt[2][3]", 0.4), hl("mt[3][4]", 0.6)])
s.step("Pairs have only one way: m 1 2 is 5 times 4 times 6, 120. m 2 3 is 4 times 6 times 2, 48. m 3 4 is 6 times 2 times 7, 84.",
       [st("mt[0][2]", "120"), st("stt[0][1]", "1", 0.1), st("mt[1][3]", "48", 0.35), st("stt[1][2]", "2", 0.45), st("mt[2][4]", "84", 0.7), st("stt[2][3]", "3", 0.8)])
s.step("m 1 3: split after A1: 0 plus 48 plus 5 times 4 times 2, 40: 88. Split after A2: 120 plus 0 plus 5 times 6 times 2, 60: 180. The minimum is 88, with k equal to 1.", [hl("mt[0][3]"), st("mt[0][3]", "88", 0.6), st("stt[0][2]", "1", 0.7)])
s.step("m 2 4: split after A2: 0 plus 84 plus 4 times 6 times 7, 168: 252. Split after A3: 48 plus 0 plus 4 times 2 times 7, 56: 104. So 104, with k equal to 3.", [hl("mt[1][4]"), st("mt[1][4]", "104", 0.6), st("stt[1][3]", "3", 0.7)])
s.step("The whole chain, m 1 4, has three choices. k equal to 1: 0 plus 104 plus 5 times 4 times 7, 140: 244.", [hl("mt[0][4]")])
s.step("k equal to 2: 120 plus 84 plus 5 times 6 times 7, 210: 414. k equal to 3: 88 plus 0 plus 5 times 2 times 7, 70: 158.", [hl("mt[0][4]")])
s.step("The minimum is 158, splitting after A3. Every entry used only entries already in the table, for shorter chains.", [st("mt[0][4]", "158"), st("stt[0][3]", "3", 0.2), mk("mt[0][4]", 0.5), s.take("least cost: 158")])

s.scene("read")
s.step("Stage 5: now read the order from s. s 1 4 is 3: the last product is A1 to A3, times A4.", [s.head("Stage 5 of 7: reading the answer"), s.untake(), hl("stt[0][3]")])
s.step("s 1 3 is 1: A1 times the product A2 A3. So the order is: A2 times A3 first, then A1 times that, then times A4.", [hl("stt[0][2]"), s.take("((A1 (A2 A3)) A4): 158")])
s.step("Check: A2 A3 costs 48 and gives a 4 by 2. A1 times it: 5 times 4 times 2, 40, giving 5 by 2. Times A4: 5 times 2 times 7, 70. Total 158. Plain left to right would cost 250.", [hl("mt[0][4]")])
s.step("Cormen's MATRIX-CHAIN-ORDER fills the table by chain length l, then by starting point i, then tries every split k.", hide("mt", "stt") + show("mc") + [ml("mc", 1, 8)])
s.step("Three nested loops, each up to n: Theta of n cubed time, and Theta of n squared space for the tables. For Cormen's six-matrix example, the answer is 15125, found instantly, among 42 possible orders.", [ml("mc", 11, 11), s.take("Θ(n³) time, Θ(n²) space")])

s.scene("dp")
s.step("Stage 6: two properties made this work. Optimal substructure: the best solution is built from best solutions to subproblems.", [s.head("Stage 6 of 7: what makes it DP"), s.untake()] + hide("mc") + show("dpw") + [hl("dpw[0]")])
s.step("Overlapping subproblems: a plain recursive solution would compute m 2 3 many times over, and take exponential time.", [hl("dpw[1]")])
s.step("Dynamic programming computes each subproblem once and stores it. Divide and conquer, by contrast, splits into independent subproblems that never repeat.", [hl("dpw[2]")])
s.step("We filled the table bottom up. The alternative, top-down memoisation, is a recursion that checks the table before computing. Same Theta of n cubed.", [hl("dpw[3..=4]")])
s.step("The lab's add-multiply chain fits the same idea: the plus signs cut it into separate product chains. Optimise each chain with this table, then add the results.", [hl("dpw[5]"), s.take("DP: optimal substructure + overlapping subproblems")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("dpw") + show("q") + [hl("q[0]")])
s.step("Fill m and s, give the least cost, and the parenthesization. Pause and work it out.", [hl("q[1..=3]")])
s.step("Pairs: m 1 2 is 3 times 5 times 2, 30. m 2 3 is 5 times 2 times 4, 40. m 3 4 is 2 times 4 times 6, 48.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("m 1 3: k equal to 1 gives 40 plus 60, 100; k equal to 2 gives 30 plus 24, 54. So 54.", [hl("qa[1]")])
s.step("m 2 4: k equal to 2 gives 48 plus 60, 108; k equal to 3 gives 40 plus 120, 160. So 108.", [hl("qa[2]")])
s.step("m 1 4: k equal to 1: 108 plus 90, 198. k equal to 2: 30 plus 48 plus 36, 114. k equal to 3: 54 plus 72, 126. The minimum is 114.", [hl("qa[3]"), mk("qa[3][2]", 0.5)])
s.step("s 1 4 is 2: split after A2. So A1 A2, times A3 A4, for 114 multiplications.", [hl("qa[4]")])
s.step("The usual slip: using the wrong dimensions in the last term. It is p i minus 1, p k, p j: the rows of the first matrix, the split, and the columns of the last.", [s.take("last term: p(i−1) · p(k) · p(j)")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("The order of a matrix chain changes the cost hugely, and there are exponentially many orders. m of i, j is the minimum over the last split k.", [hl("stages[0..=3]")])
s.step("Filling the table by chain length takes Theta of n cubed, and s rebuilds the order. Optimal substructure plus overlapping subproblems means dynamic programming.", [hl("stages[4..=5]")])
s.step("Next video: dynamic programming on strings. The longest common subsequence.", [mk("stages[0..=6]"), s.take("Next: longest common subsequence")])

s.save("/home/claude/playlist/dsa4/d4v1.json")

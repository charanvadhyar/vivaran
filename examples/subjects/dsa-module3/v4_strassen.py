"""DSA Module 3, video 4: Strassen's matrix multiplication."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *

def strassen(A, B):
    (a11, a12), (a21, a22) = A; (b11, b12), (b21, b22) = B
    P = (a11 + a22) * (b11 + b22); Q = (a21 + a22) * b11; R = a11 * (b12 - b22); S = a22 * (b21 - b11)
    T = (a11 + a12) * b22; U = (a21 - a11) * (b11 + b12); V = (a12 - a22) * (b21 + b22)
    return dict(P=P, Q=Q, R=R, S=S, T=T, U=U, V=V), [[P + S - T + V, R + T], [Q + S, P + R - Q + U]]
def mul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
A, B = [[1, 3], [7, 5]], [[6, 8], [4, 2]]
X, C = strassen(A, B); assert C == mul(A, B) == [[18, 14], [62, 66]]
assert X == dict(P=48, Q=72, R=6, S=-10, T=8, U=84, V=-12)
EA, EB = [[1, 2], [3, 4]], [[5, 6], [7, 8]]
EX, EC = strassen(EA, EB); assert EC == mul(EA, EB) == [[19, 22], [43, 50]]
assert EX == dict(P=65, Q=35, R=-2, S=8, T=24, U=22, V=-30)
assert 7 ** 10 == 282475249 and 1024 ** 3 == 1073741824 and abs(math.log2(7) - 2.807) < 0.001
assert 7 ** 3 == 343 and 8 ** 3 == 512

s = Script("Strassen's matrix multiplication")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The ordinary method: n³ multiplications"],
    [2, "Divide into blocks: 8 products"],
    [3, "Strassen's seven products"],
    [4, "A 2 × 2 example, worked"],
    [5, "The running time: n^2.81"],
    [6, "In practice"],
    [7, "Exam question"]]})
s.obj({"id": "ord", "type": "code", "region": "center", "language": "text", "lines": [
    "SQUARE-MATRIX-MULTIPLY(A, B, n)",
    "    for i = 1 to n",
    "        for j = 1 to n",
    "            C[i, j] = 0",
    "            for k = 1 to n",
    "                C[i, j] = C[i, j] + A[i, k] · B[k, j]",
    "    return C                  // n · n · n = n³ multiplications"]})
s.obj({"id": "blk", "type": "math", "region": "center", "lines": [
    "mat(C_11, C_12; C_21, C_22) = mat(A_11, A_12; A_21, A_22) mat(B_11, B_12; B_21, B_22) quad \"each block \" n/2 times n/2",
    "C_11 = A_11 B_11 + A_12 B_21 quad C_12 = A_11 B_12 + A_12 B_22",
    "C_21 = A_21 B_11 + A_22 B_21 quad C_22 = A_21 B_12 + A_22 B_22",
    "\"8 block products, 4 block additions: \" T(n) = 8 T(n slash 2) + Theta(n^2) = Theta(n^3)"]})
s.obj({"id": "sv", "type": "math", "region": "left", "lines": [
    "P = (A_11 + A_22)(B_11 + B_22)",
    "Q = (A_21 + A_22) B_11",
    "R = A_11 (B_12 - B_22)",
    "S = A_22 (B_21 - B_11)",
    "T = (A_11 + A_12) B_22",
    "U = (A_21 - A_11)(B_11 + B_12)",
    "V = (A_12 - A_22)(B_21 + B_22)"], "shown": 7})
s.obj({"id": "sc", "type": "math", "region": "right", "lines": [
    "C_11 = P + S - T + V",
    "C_12 = R + T",
    "C_21 = Q + S",
    "C_22 = P + R - Q + U"], "shown": 4})
s.obj({"id": "chk", "type": "math", "region": "center", "lines": [
    "\"check \" C_12: quad R + T = A_11 B_12 - A_11 B_22 + A_11 B_22 + A_12 B_22",
    "= A_11 B_12 + A_12 B_22 quad checkmark",
    "\"check \" C_21: quad Q + S = A_21 B_11 + A_22 B_11 + A_22 B_21 - A_22 B_11 = A_21 B_11 + A_22 B_21 quad checkmark",
    "\"7 multiplications and 18 additions or subtractions of \" n/2 times n/2 \" blocks\""]})
s.obj({"id": "ex", "type": "table", "region": "center", "columns": ["A = [1 3; 7 5],  B = [6 8; 4 2]", "working", "value"], "rows": [
    ["P", "(1 + 5)(6 + 2)", ""], ["Q", "(7 + 5) · 6", ""], ["R", "1 · (8 − 2)", ""], ["S", "5 · (4 − 6)", ""],
    ["T", "(1 + 3) · 2", ""], ["U", "(7 − 1)(6 + 8)", ""], ["V", "(3 − 5)(4 + 2)", ""]]})
s.obj({"id": "res", "type": "table", "region": "center", "columns": ["block of C", "formula", "value", "check: row · column"], "rows": [
    ["C11", "P + S − T + V = 48 − 10 − 8 − 12", "18", "1·6 + 3·4 = 18"],
    ["C12", "R + T = 6 + 8", "14", "1·8 + 3·2 = 14"],
    ["C21", "Q + S = 72 − 10", "62", "7·6 + 5·4 = 62"],
    ["C22", "P + R − Q + U = 48 + 6 − 72 + 84", "66", "7·8 + 5·2 = 66"]]})
s.obj({"id": "rt", "type": "math", "region": "center", "lines": [
    "T(n) = 7 T(n slash 2) + Theta(n^2)",
    "\"master method: \" n^(log_2 7) approx n^2.81 \" grows faster than \" n^2 \": case 1\"",
    "T(n) = Theta(n^(log_2 7)) = Theta(n^2.81)",
    "n = 1024: quad 7^10 = 282475249 \" against \" 1024^3 = 1073741824 \" scalar products\""]})
s.obj({"id": "lvl", "type": "table", "region": "center", "columns": ["level", "block size", "block products: ordinary", "Strassen"], "rows": [
    ["0", "n", "1", "1"], ["1", "n/2", "8", "7"], ["2", "n/4", "64", "49"], ["k", "n/2ᵏ", "8ᵏ", "7ᵏ"], ["log₂ n", "1 × 1", "8^log₂n = n³", "7^log₂n = n^log₂7"]]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["in practice", ""], "rows": [
    ["small matrices", "the 18 additions and the overhead make it slower: switch to the ordinary method below a cutoff"],
    ["n not a power of 2", "pad with zero rows and columns"],
    ["numerical accuracy", "the subtractions lose a little more precision with floating point"],
    ["extra memory", "temporary blocks for the sums"],
    ["the record today", "about n^2.37, but only for astronomically large n"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["multiply A = [1 2; 3 4] by B = [5 6; 7 8] with Strassen's method"],
    ["a) the seven products P to V"],
    ["b) the four entries of C, checked the ordinary way"],
    ["c) for n = 8, scalar multiplications: Strassen down to 1 × 1, against the ordinary method?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "P = 5·13, Q = 7·5, R = 1·(−2), S = 4·2", "P 65, Q 35, R −2, S 8"],
    ["a)", "T = 3·8, U = 2·11, V = (−2)·15", "T 24, U 22, V −30"],
    ["b)", "C11 = 65 + 8 − 24 − 30;  C12 = −2 + 24", "19, 22"],
    ["b)", "C21 = 35 + 8;  C22 = 65 − 2 − 35 + 22", "43, 50"],
    ["c)", "8 = 2³: three levels of 7 against n³", "7³ = 343 against 8³ = 512"]]})

s.scene("intro")
s.step("Multiplying matrices is at the heart of graphics, scientific computing and neural networks. For centuries it took n cubed multiplications. In 1969 Volker Strassen showed that a 2 by 2 block product needs only 7 multiplications, not 8, and so beat n cubed.", [s.head("Strassen's matrix multiplication")])
s.step("Here are the seven stages.", show("stages"))
s.step("The ordinary method, dividing into blocks, Strassen's seven products, and a worked example.", [hl("stages[0..=3]")])
s.step("Then the running time, how it is used in practice, and an exam question.", [hl("stages[4..=6]")])

s.scene("ord")
s.step("Stage 1: the ordinary method. Each entry C i j is row i of A times column j of B: n multiplications.", [s.head("Stage 1 of 7: the ordinary method")] + hide("stages") + show("ord") + [ml("ord", 4, 6)])
s.step("There are n squared entries, each needing n multiplications: n cubed in all. Three nested loops.", [ml("ord", 1, 7), s.take("ordinary: n³ multiplications")])

s.scene("blk")
s.step("Stage 2: divide. Cut each matrix into four blocks of size n over 2. Block matrices multiply just like 2 by 2 matrices of numbers.", [s.head("Stage 2 of 7: blocks"), s.untake()] + hide("ord") + show("blk") + [hl("blk[0]")])
s.step("C 1 1 is A 1 1 times B 1 1, plus A 1 2 times B 2 1. C 1 2 is similar.", [rv("blk[1]"), hl("blk[1]")])
s.step("And the bottom row the same way.", [rv("blk[2]"), hl("blk[2]")])
s.step("That is 8 products of half-size blocks, plus additions costing n squared. 8 T of n over 2, plus n squared, solves to n cubed. Dividing alone gains nothing, as with Karatsuba's first try.", [rv("blk[3]"), hl("blk[3]"), s.take("8 block products: still Θ(n³)")])

s.scene("sv")
s.step("Stage 3: Strassen's seven products, as given in Horowitz and Sahni. P multiplies the two diagonal sums.", [s.head("Stage 3 of 7: seven products"), s.untake()] + hide("blk") + show("sv", "sc") + [hl("sv[0]")])
s.step("Q, R, S and T each multiply one block by a sum or difference of two.", [hl("sv[1..=4]")])
s.step("U and V multiply two differences and sums.", [hl("sv[5..=6]")])
s.step("Then C is built from them with additions only. C 1 2 is R plus T, and C 2 1 is Q plus S.", [hl("sc[1..=2]")])
s.step("C 1 1 is P plus S minus T plus V, and C 2 2 is P plus R minus Q plus U. The products are arranged so that the unwanted terms cancel.", [hl("sc[0]"), hl("sc[3]", 0.5)])
s.step("Check one: R plus T is A 1 1 B 1 2, minus A 1 1 B 2 2, plus A 1 1 B 2 2, plus A 1 2 B 2 2. The middle terms cancel.", hide("sv", "sc") + show("chk") + [hl("chk[0]")])
s.step("What remains, A 1 1 B 1 2 plus A 1 2 B 2 2, is exactly C 1 2.", [rv("chk[1]"), hl("chk[1]")])
s.step("So 7 multiplications and 18 additions or subtractions of half-size blocks. One fewer multiplication, many more additions: but additions are only n squared.", [rv("chk[2]"), hl("chk[2]")])
s.step("Another: Q plus S. The A 2 2 B 1 1 terms cancel, leaving A 2 1 B 1 1 plus A 2 2 B 2 1: exactly C 2 1. C 1 1 and C 2 2 can be checked the same way, with more cancelling.", [rv("chk[3]"), hl("chk[3]"), s.take("7 products, 18 additions")])

s.scene("ex")
s.step("Stage 4: an example. A is 1, 3 over 7, 5; B is 6, 8 over 4, 2. Each block is a single number.", [s.head("Stage 4 of 7: a worked example"), s.untake()] + hide("chk") + show("ex"))
names = list("PQRSTUV")
say = ["P: 1 plus 5 is 6, times 6 plus 2, which is 8: 48.", "Q: 7 plus 5 is 12, times 6: 72.", "R: 1 times 8 minus 2: 6.",
       "S: 5 times 4 minus 6, that is 5 times minus 2: minus 10.", "T: 1 plus 3 is 4, times 2: 8.", "U: 7 minus 1 is 6, times 6 plus 8, 14: 84.",
       "V: 3 minus 5 is minus 2, times 4 plus 2, 6: minus 12."]
for k, nm in enumerate(names):
    s.step(say[k], [hl(f"ex[{k}]"), st(f"ex[{k}][2]", str(X[nm]), 0.5)])
s.step("Now combine. C 1 1: 48 minus 10 minus 8 minus 12, 18. C 1 2: 6 plus 8, 14.", hide("ex") + show("res") + [hl("res[0..=1]")])
s.step("C 2 1: 72 minus 10, 62. C 2 2: 48 plus 6 minus 72 plus 84, 66.", [hl("res[2..=3]")])
s.step("The ordinary way agrees: row 1 of A times column 1 of B is 6 plus 12, 18, and so on. Seven multiplications instead of eight.", [mk(f"res[{k}][2]", round(0.1 * k, 2)) for k in range(4)] + [s.take("C = [18 14; 62 66]")])

s.scene("rt")
s.step("Stage 5: apply the method recursively: each block product is itself done by Strassen. Level 1 has 7 block products instead of 8; level 2 has 49 instead of 64.", [s.head("Stage 5 of 7: the running time"), s.untake()] + hide("res") + show("lvl") + [hl("lvl[0..=2]")])
s.step("At level k, 7 to the k instead of 8 to the k. At the bottom, after log n levels, the blocks are single numbers: n cubed products the ordinary way, n to the log 2 of 7 with Strassen.", [hl("lvl[3..=4]")])
s.step("As a recurrence: 7 half-size products plus n squared additions. T of n equals 7 T of n over 2, plus n squared.", hide("lvl") + show("rt") + [hl("rt[0]")])
s.step("Master method: n to the log base 2 of 7 is about n to the 2.81, faster-growing than n squared. Case 1.", [rv("rt[1]"), hl("rt[1]")])
s.step("So T of n is Theta of n to the log 2 of 7, about n to the 2.81.", [rv("rt[2]"), hl("rt[2]")])
s.step("For n equal to 1024: 7 to the 10, about 282 million scalar multiplications, against over a billion. Saving one product in eight, at every level, compounds.", [rv("rt[3]"), hl("rt[3]"), s.take("Θ(n^log₂7) ≈ Θ(n^2.81)")])

s.scene("pr")
s.step("Stage 6: in practice, the 18 additions and the recursion overhead make Strassen slower on small matrices, so implementations switch to the ordinary method below a cutoff.", [s.head("Stage 6 of 7: in practice"), s.untake()] + hide("rt") + show("pr") + [hl("pr[0]")])
s.step("If n is not a power of 2, pad the matrices with zeros.", [hl("pr[1]")])
s.step("With floating point, the subtractions lose slightly more accuracy, and the temporary sums need extra memory.", [hl("pr[2..=3]")])
s.step("Later algorithms push the exponent down to about 2.37, but only pay off for impossibly large matrices. Strassen's is the one actually used.", [hl("pr[4]"), s.take("worth it for large n, with a cutoff")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("pr") + show("q") + [hl("q[0]")])
s.step("Compute the seven products, the four entries, and compare the counts for 8 by 8. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: P is 1 plus 4, times 5 plus 8: 65. Q is 3 plus 4, times 5: 35. R is 1 times 6 minus 8: minus 2. S is 4 times 7 minus 5: 8.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("T is 1 plus 2, times 8: 24. U is 3 minus 1, times 5 plus 6: 22. V is 2 minus 4, times 7 plus 8: minus 30.", [hl("qa[1]")])
s.step("b: C 1 1 is 65 plus 8 minus 24 minus 30, 19. C 1 2 is minus 2 plus 24, 22.", [hl("qa[2]")])
s.step("C 2 1 is 35 plus 8, 43. C 2 2 is 65 minus 2 minus 35 plus 22, 50. The ordinary way: 1 times 5 plus 2 times 7 is 19. It agrees.", [hl("qa[3]")])
s.step("c: 8 is 2 cubed, so three levels of 7 products: 343 scalar multiplications, against 8 cubed, 512.", [hl("qa[4]"), mk("qa[4][2]", 0.5)])
s.step("The usual slip: a sign. In C 2 2, Q is subtracted; in C 1 1, T is. Write the four formulas down before you start.", [s.take("C11 = P+S−T+V   C22 = P+R−Q+U")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("The ordinary method costs n cubed, and splitting into blocks alone gives 8 products, still n cubed. Strassen's seven products P to V do it with 7.", [hl("stages[0..=3]")])
s.step("7 T of n over 2 plus n squared is Theta of n to the 2.81, useful for large matrices with a cutoff for small ones.", [hl("stages[4..=5]")])
s.step("Next video: divide and conquer for a puzzle from the lab. Finding the one fake coin with the fewest weighings.", [mk("stages[0..=6]"), s.take("Next: the fake coin problem")])

s.save("/home/claude/playlist/dsa3/d3v4.json")

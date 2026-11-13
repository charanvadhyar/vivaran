"""Module 4, video 17: the GCD test and eliminating dependences."""
import sys, random
from math import gcd, log2
sys.path.insert(0, "/home/claude/playlist")
from common import Script

def deps(a, b, c, d, lo, hi):
    """pairs (j writes, k reads) with a j + b == c k + d, j, k in [lo, hi)"""
    return [(j, k) for j in range(lo, hi) for k in range(lo, hi) if a * j + b == c * k + d]

gtest = lambda a, b, c, d: (d - b) % gcd(a, c) == 0
assert not gtest(2, 3, 2, 0) and deps(2, 3, 2, 0, 0, 100) == []
assert gtest(4, 2, 2, 4) and (2, 3) in deps(4, 2, 2, 4, 0, 100) and (1, 1) in deps(4, 2, 2, 4, 0, 100)
assert gtest(1, 100, 1, 0) and deps(1, 100, 1, 0, 0, 100) == []
# exam a: A[6i+2] = A[4i+5]
assert not gtest(6, 2, 4, 5) and deps(6, 2, 4, 5, 0, 100) == []
# exam b: A[3i+1] = A[6i+4]: write at j, read at k; every pair has j > k (read first: antidependence)
P = deps(3, 1, 6, 4, 0, 100)
assert gtest(3, 1, 6, 4) and P[0] == (1, 0) and all(j > k for j, k in P) and (3, 1) in P
# renaming the textbook loop gives the same results
random.seed(7); c = 3
X = [random.randint(1, 50) for _ in range(100)]
Y, Z = [0] * 100, [0] * 100
x1 = X[:]
for i in range(100):
    Y[i] = x1[i] / c; x1[i] = x1[i] + c; Z[i] = Y[i] + c; Y[i] = c - Y[i]
T, X1, Z2, Y2 = [0] * 100, [0] * 100, [0] * 100, [0] * 100
for i in range(100):
    T[i] = X[i] / c; X1[i] = X[i] + c; Z2[i] = T[i] + c; Y2[i] = c - T[i]
assert X1 == x1 and Z2 == Z and Y2 == Y
# reductions
assert 4096 // 64 == 64 and log2(64) == 6 and 64 + 6 == 70
assert 10000 // 10 == 1000 and log2(8) == 3

s = Script("The GCD test")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The question a compiler asks"],
    [2, "The GCD test"],
    [3, "The textbook example"],
    [4, "When the test says maybe"],
    [5, "Finding every dependence in a loop"],
    [6, "Renaming removes name dependences"],
    [7, "Reductions"],
    [8, "Exam question"]]})
s.obj({"id": "qq", "type": "math", "region": "center", "lines": [
    "\"store\" X[a times i + b] quad \"load\" X[c times i + d]",
    "\"dependence\" <=> a j + b = c k + d \"for some iterations\" j, k \"in the loop\"",
    "\"affine indices: a constant times i, plus a constant\""]})
s.obj({"id": "gt", "type": "math", "region": "center", "lines": [
    "\"if a dependence exists, then\" gcd(a, c) \"divides\" d - b",
    "\"so: if\" gcd(a, c) \"does not divide\" d - b, \"there is no dependence\"",
    "\"why:\" a j - c k \"is always a multiple of\" gcd(a, c)"]})
s.obj({"id": "ex", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 100; i++)",
    "    X[2*i + 3] = X[2*i] * 5.0;"]})
s.obj({"id": "exm", "type": "math", "region": "center", "lines": [
    "a = 2, b = 3, quad c = 2, d = 0",
    "gcd(2, 2) = 2, quad d - b = -3",
    "2 \"does not divide\" -3: quad \"no dependence\"",
    "\"stores go to odd elements, loads come from even ones\""]})
s.obj({"id": "mb", "type": "table", "region": "center", "columns": ["loop", "GCD test", "the truth"], "rows": [
    ["X[4i+2] = X[2i+4] …", "gcd 2 divides 2: maybe", "real: X[10] written at i = 2, read at i = 3"],
    ["X[i+100] = X[i] …, i < 100", "gcd 1 divides 100: maybe", "none: writes 100–199, reads 0–99"],
    ["the test", "ignores the loop bounds", "passing it proves nothing"],
    ["failing it", "", "proves there is no dependence"]]})
s.obj({"id": "rn", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 100; i++) {",
    "    Y[i] = X[i] / c;     /* S1 */",
    "    X[i] = X[i] + c;     /* S2 */",
    "    Z[i] = Y[i] + c;     /* S3 */",
    "    Y[i] = c - Y[i];     /* S4 */",
    "}"]})
s.obj({"id": "rnd", "type": "table", "region": "center", "columns": ["dependence", "through", "kind"], "rows": [
    ["S1 → S3, S1 → S4", "Y[i]", "true"],
    ["S1 → S2", "X[i]: read, then written", "anti"],
    ["S3 → S4", "Y[i]: read, then written", "anti"],
    ["S1 → S4", "Y[i]: written twice", "output"]]})
s.obj({"id": "rn2", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 100; i++) {",
    "    T[i]  = X[i] / c;    /* Y renamed T: output and anti gone */",
    "    X1[i] = X[i] + c;    /* X renamed X1: anti gone */",
    "    Z[i]  = T[i] + c;",
    "    Y[i]  = c - T[i];",
    "}",
    "// later code that reads X must now read X1"]})
s.obj({"id": "rd", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 9999; i >= 0; i--) sum = sum + x[i] * y[i];   // carried: sum",
    "",
    "for (i = 9999; i >= 0; i--) p[i] = x[i] * y[i];        // fully parallel",
    "for (i = 9999; i >= 0; i--) sum = sum + p[i];          // still a reduction",
    "",
    "// 10 processors: each sums 1000 of the p[i]",
    "// then combine the 10 partial sums in a tree"]})
s.obj({"id": "rdm", "type": "math", "region": "center", "lines": [
    "\"vector length 64, n = 4096:\" quad 4096 / 64 = 64 \"vector adds\"",
    "\"then 64 partial sums\" -> 32 -> 16 -> 8 -> 4 -> 2 -> 1: quad log_2 64 = 6 \"steps\"",
    "\"floating point: a new order of additions may round differently\""]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "c", "lines": [
    "// a) for (i = 0; i < 100; i++) A[6*i + 2] = A[4*i + 5] + 1;",
    "// b) for (i = 0; i < 100; i++) A[3*i + 1] = A[6*i + 4] + 1;",
    "// c) sum of 4096 values with vector length 64: how many steps?",
    "// For a and b: apply the GCD test. If it says maybe,",
    "//   find the first pair of iterations and the kind of dependence."]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "gcd(6, 4) = 2; d − b = 5 − 2 = 3", "2 does not divide 3: no dependence"],
    ["b", "gcd(3, 6) = 3; d − b = 4 − 1 = 3", "3 divides 3: maybe"],
    ["b", "i = 0 reads A[4]; i = 1 writes A[4]", "read first: antidependence"],
    ["b", "3j + 1 = 6k + 4 gives j = 2k + 1 > k", "every pair: only anti, renaming removes it"],
    ["c", "4096 / 64 = 64 vector adds, then log₂ 64 = 6", "70 steps, against 4096"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Before a compiler can vectorise a loop, it must prove the iterations are independent. This video shows the simplest test it uses, the GCD test, and two ways to remove dependences that look fatal but are not.", [s.head("The GCD test and removing dependences")])
s.step("Here are the eight stages.", show("stages"))
s.step("The question, the GCD test, the textbook's example, and what the test cannot tell you.", [hl("stages[0..=3]")])
s.step("Then finding every dependence in a loop, renaming, reductions, and an exam question.", [hl("stages[4..=7]")])

s.scene("qq")
s.step("Stage 1: suppose a loop stores to X of a i plus b, and loads from X of c i plus d.", [s.head("Stage 1 of 8: the question")] + hide("stages") + show("qq") + [hl("qq[0]")])
s.step("A dependence exists if some iteration j stores to the same element that some iteration k loads: a j plus b equals c k plus d, with j and k inside the loop's range.", [rv("qq[1]"), hl("qq[1]")])
s.step("Indices like these, a constant times i plus a constant, are called affine. Most array loops have them, and they can be analysed exactly.", [rv("qq[2]"), hl("qq[2]"), s.take("dependence: a j + b = c k + d")])

s.scene("gt")
s.step("Stage 2: the GCD test. If a dependence exists, then the greatest common divisor of a and c divides d minus b.", [s.head("Stage 2 of 8: the GCD test"), s.untake()] + hide("qq") + show("gt") + [hl("gt[0]")])
s.step("So turn it round: if the gcd does not divide d minus b, there can be no dependence.", [rv("gt[1]"), hl("gt[1]")])
s.step("Why? a j minus c k is always a multiple of the gcd of a and c. It must equal d minus b, so d minus b must be a multiple too.", [rv("gt[2]"), hl("gt[2]"), s.take("gcd does not divide d − b ⇒ no dependence")])

s.scene("ex")
s.step("Stage 3: the textbook's example. X of 2i plus 3 is assigned X of 2i times 5.", [s.head("Stage 3 of 8: the textbook example"), s.untake()] + hide("gt") + show("ex") + [ml("ex", 1, 2)])
s.step("The store has a equal to 2 and b equal to 3. The load has c equal to 2 and d equal to 0.", hide("ex") + show("exm") + [hl("exm[0]")])
s.step("The gcd of 2 and 2 is 2. d minus b is minus 3.", [rv("exm[1]"), hl("exm[1]")])
s.step("2 does not divide minus 3, so there is no dependence. The loop can be vectorised.", [rv("exm[2]"), mk("exm[2]")])
s.step("You can see why directly: the stores all go to odd elements, and the loads all come from even ones. They never meet.", [rv("exm[3]"), hl("exm[3]"), s.take("odd stores, even loads: independent")])

s.scene("maybe")
s.step("Stage 4: when the gcd does divide, the test says only maybe. Here, X of 4i plus 2 and X of 2i plus 4: the gcd 2 divides 2.", [s.head("Stage 4 of 8: when the test says maybe"), s.untake()] + hide("exm") + show("mb") + [hl("mb[0][0]"), hl("mb[0][1]", 0.2)])
s.step("And there is a dependence: iteration 2 writes X of 10, and iteration 3 reads it.", [hl("mb[0][2]")])
s.step("But here, X of i plus 100 and X of i, with i below 100, the gcd 1 divides 100. Yet the writes go to 100 through 199 and the reads come from 0 through 99. No dependence.", [hl("mb[1]")])
s.step("The test ignores the loop bounds, so passing it proves nothing.", [hl("mb[2]")])
s.step("Only failing it is a proof. Real compilers use stronger tests when the GCD test says maybe.", [hl("mb[3]"), s.take("GCD test: fail = independent, pass = maybe")])

s.scene("find")
s.step("Stage 5: the textbook's second exercise: find every dependence in this loop.", [s.head("Stage 5 of 8: finding every dependence"), s.untake()] + hide("mb") + show("rn") + [ml("rn", 1, 6)])
s.step("True dependences: S1 writes Y of i, and S3 and S4 read it.", hide("rn") + show("rnd") + [hl("rnd[0]")])
s.step("Antidependence: S1 reads X of i, then S2 overwrites it.", [hl("rnd[1]")])
s.step("Another antidependence: S3 reads Y of i, then S4 overwrites it.", [hl("rnd[2]")])
s.step("Output dependence: S1 and S4 both write Y of i, and the final value must be S4's.", [hl("rnd[3]")])
s.step("All of these are within one iteration; none is carried. But the anti and output ones force an order on the statements, and get in the way of scheduling.", [s.take("3 kinds: true, anti, output")])

s.scene("rename")
s.step("Stage 6: anti and output dependences are only name clashes. Give the values new names and they disappear.", [s.head("Stage 6 of 8: renaming"), s.untake()] + hide("rnd") + show("rn2") + [ml("rn2", 1, 6)])
s.step("S1 now writes T instead of Y. The output dependence with S4 is gone, and so is the antidependence from S3.", [ml("rn2", 2, 2)])
s.step("S2 writes X1 instead of X: the antidependence from S1 is gone.", [ml("rn2", 3, 3)])
s.step("S3 and S4 read T. Only the true dependences remain.", [ml("rn2", 4, 5)])
s.step("Any later code that reads X must now read X1. Renaming costs memory, but frees the schedule. Hardware does the same with registers: register renaming, from Module 3.", [ml("rn2", 7, 7), s.take("rename: only true dependences remain")])

s.scene("red")
s.step("Stage 7: some true carried dependences can still be broken. A dot product adds into sum every iteration: a carried dependence on sum.", [s.head("Stage 7 of 8: reductions"), s.untake()] + hide("rn2") + show("rd") + [ml("rd", 1, 1)])
s.step("Split it. The products p of i have no dependence at all: that loop is fully parallel.", [ml("rd", 3, 3)])
s.step("What is left is a reduction: summing an array. Because addition is associative, the order can change.", [ml("rd", 4, 4)])
s.step("With 10 processors, each sums 1000 of the values, and the 10 partial sums are combined in a tree.", [ml("rd", 6, 7)])
s.step("On a vector machine with length 64, 4096 values take 64 vector adds into 64 partial sums.", hide("rd") + show("rdm") + [hl("rdm[0]")])
s.step("Then the 64 sums are halved six times: log base 2 of 64. 70 steps instead of 4096.", [rv("rdm[1]"), hl("rdm[1]")])
s.step("One caution: with floating point, a new order of additions can round differently. Compilers reorder only when allowed to.", [rv("rdm[2]"), hl("rdm[2]"), s.take("reduction: partial sums, then a tree")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("rdm") + show("q") + [ml("q", 1, 3)])
s.step("Apply the GCD test to loops a and b. If it says maybe, find the first pair of iterations and the kind of dependence. For c, count the steps. Pause and work it out.", [ml("q", 4, 5)])
s.step("a: a is 6, c is 4, their gcd is 2. d minus b is 5 minus 2, 3. 2 does not divide 3: no dependence.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: gcd of 3 and 6 is 3, and d minus b is 4 minus 1, 3. 3 divides 3: maybe.", [hl("qa[1]")])
s.step("Try values. Iteration 0 reads A of 4. Iteration 1 writes A of 3 plus 1, also A of 4. The read comes first: an antidependence, carried.", [hl("qa[2]")])
s.step("In general, 3 j plus 1 equals 6 k plus 4 gives j equals 2 k plus 1, always later than k. So every pair is read-then-write: only antidependences, and renaming A removes them.", [hl("qa[3]")])
s.step("c: 4096 over 64 is 64 vector adds, then 6 tree steps: 70.", [hl("qa[4]"), mk("qa[4][2]", 0.4)])
s.step("The usual slip: treating a passed GCD test as proof of a dependence. It only says maybe.", [s.take("the GCD test proves only independence")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("For affine indices, a dependence needs a j plus b to equal c k plus d. If the gcd of a and c does not divide d minus b, there is none; otherwise, maybe.", [hl("stages[0..=3]")])
s.step("True, anti and output dependences can be listed per statement. Renaming removes anti and output ones, and reductions become partial sums and a tree.", [hl("stages[4..=6]")])
s.step("Next video: writing these parallel loops in CUDA. Launching kernels, indexing, and memory.", [mk("stages[0..=7]"), s.take("Next: CUDA programming, part 1")])

s.save("/home/claude/playlist/m4/m4v17.json")

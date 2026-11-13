"""DSA Module 1, video 5: recursion and recurrences."""
import sys, math
from functools import lru_cache
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

fact = lambda n: 1 if n <= 1 else n * fact(n - 1)
assert [fact(k) for k in (1, 2, 3, 4)] == [1, 2, 6, 24]
calls = lambda n: 1 if n <= 1 else 1 + calls(n - 1) + calls(n - 2)
F = lambda n: n if n < 2 else F(n - 1) + F(n - 2)
assert calls(5) == 15 == 2 * F(6) - 1 and calls(6) == 25 == 2 * F(7) - 1 and F(5) == 5 and calls(30) == 2 * F(31) - 1 == 2692537
H = lambda n: 0 if n == 0 else 2 * H(n - 1) + 1
assert H(3) == 7 and H(10) == 1023 and H(64) == 2**64 - 1 and round((2**64 - 1) / 3.156e7 / 1e9) == 584
T1 = lambda n: 1 if n == 1 else T1(n - 1) + n
assert T1(10) == 55
T2 = lambda n: 1 if n == 1 else 2 * T2(n // 2) + n
assert T2(8) == 32 == 8 * 3 + 8 and T2(1024) == 1024 * 10 + 1024
B = lambda n: 1 if n == 1 else B(n // 2) + 1
assert B(1024) == 11
# master method exam: ratios settle
def T(a, b, f, n): return 1 if n <= 1 else a * T(a, b, f, n // b) + f(n)
n = 2**16
assert abs(T(4, 2, lambda m: m, n) / n**2 - 2) < 0.01            # Θ(n²)
assert abs(T(4, 2, lambda m: m * m, n) / (n * n * 16) - 1) < 0.1   # Θ(n² log n)
assert abs(T(4, 2, lambda m: m**3, n) / n**3 - 2) < 0.01           # Θ(n³)
assert math.log(9, 3) == 2 and math.isclose(math.log(4, 2), 2)

s = Script("Recursion and recurrences")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Recursion: a base and a step"],
    [2, "The call stack"],
    [3, "Fibonacci: when recursion explodes"],
    [4, "Towers of Hanoi"],
    [5, "Solving by unrolling"],
    [6, "The recursion-tree method"],
    [7, "The master method"],
    [8, "Exam question"]]})
s.obj({"id": "fc", "type": "code", "region": "center", "language": "text", "lines": [
    "FACT(n)",
    "    if n <= 1            // base case",
    "        return 1",
    "    return n * FACT(n - 1)   // recursive case"]})
s.obj({"id": "rl", "type": "table", "region": "center", "columns": ["every recursion needs"], "rows": [
    ["a base case that needs no recursion"],
    ["a recursive case on a smaller input"],
    ["progress: every call gets closer to the base"]]})
s.obj({"id": "stk", "type": "array", "region": "center", "values": ["FACT(4)"]})
s.obj({"id": "fib", "type": "diagram", "region": "center", "layout": "tree", "shape": "circle", "directed": True,
       "nodes": [{"id": i, "label": l} for i, l in [("a", "5"), ("b", "4"), ("c", "3"), ("d", "3"), ("e", "2"), ("f", "2"), ("g", "1"),
                                                     ("h", "2"), ("i", "1"), ("j", "1"), ("k", "0"), ("l", "1"), ("m", "0"), ("n", "1"), ("o", "0")]],
       "edges": [{"from": a, "to": b} for a, b in [("a", "b"), ("a", "c"), ("b", "d"), ("b", "e"), ("c", "f"), ("c", "g"), ("d", "h"), ("d", "i"),
                                                   ("e", "j"), ("e", "k"), ("f", "l"), ("f", "m"), ("h", "n"), ("h", "o")]]})
s.obj({"id": "fibm", "type": "math", "region": "center", "lines": [
    "\"FIB(n) = FIB(n − 1) + FIB(n − 2): calls(5) = 15\"",
    "\"calls\"(n) = 2 F(n + 1) - 1 quad \"FIB(30): 2,692,537 calls\"",
    "\"grows like\" 1.618^n: quad \"exponential, because the same values are recomputed\"",
    "\"remember each answer (memoisation): n + 1 calls, Θ(n)\""]})
s.obj({"id": "hn", "type": "math", "region": "center", "lines": [
    "\"move n disks: move n−1 aside, move the largest, move n−1 back on top\"",
    "T(n) = 2 T(n - 1) + 1, quad T(0) = 0",
    "T(1) = 1, quad T(2) = 3, quad T(3) = 7, quad T(n) = 2^n - 1",
    "n = 64: quad 2^64 - 1 approx 1.8 times 10^19 \"moves: about 585 billion years at one per second\""]})
s.obj({"id": "un", "type": "math", "region": "center", "lines": [
    "T(n) = T(n - 1) + n, quad T(1) = 1",
    "= T(n - 2) + (n - 1) + n",
    "= T(n - 3) + (n - 2) + (n - 1) + n = dots.c",
    "= 1 + 2 + dots.c + n = (n(n+1))/2 = Theta(n^2)",
    "\"binary search:\" T(n) = T(n/2) + 1 = log_2 n + 1 = Theta(log n)"]})
s.obj({"id": "rtree", "type": "diagram", "region": "left", "layout": "tree", "nodes": [
    {"id": "r", "label": "n"}, {"id": "a1", "label": "n/2"}, {"id": "a2", "label": "n/2"},
    {"id": "b1", "label": "n/4"}, {"id": "b2", "label": "n/4"}, {"id": "b3", "label": "n/4"}, {"id": "b4", "label": "n/4"}],
    "edges": [{"from": "r", "to": "a1"}, {"from": "r", "to": "a2"}, {"from": "a1", "to": "b1"}, {"from": "a1", "to": "b2"},
              {"from": "a2", "to": "b3"}, {"from": "a2", "to": "b4"}]})
s.obj({"id": "rt", "type": "table", "region": "right", "columns": ["level", "nodes", "cost"], "rows": [
    ["0", "1", "n"], ["1", "2", "2 · n/2 = n"], ["2", "4", "4 · n/4 = n"], ["…", "…", "n per level"], ["log₂ n levels", "", "n log₂ n + n"]]})
s.obj({"id": "ms", "type": "table", "region": "center", "columns": ["T(n) = a T(n/b) + f(n): compare f(n) with n^(log_b a)", "result"], "rows": [
    ["1: f is polynomially smaller", "Θ(n^(log_b a)): the leaves win"],
    ["2: f is Θ(n^(log_b a))", "Θ(n^(log_b a) · log n): every level equal"],
    ["3: f is polynomially larger (and a f(n/b) ≤ c f(n), c < 1)", "Θ(f(n)): the root wins"],
    ["2T(n/2) + n:  n^(log₂ 2) = n", "case 2: Θ(n log n)"],
    ["9T(n/3) + n:  n^(log₃ 9) = n²", "case 1: Θ(n²)"],
    ["T(2n/3) + 1:  n^0 = 1", "case 2: Θ(log n)"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) T(n) = 4T(n/2) + n      b) T(n) = 4T(n/2) + n²      c) T(n) = 4T(n/2) + n³"],
    ["d) how many moves does Towers of Hanoi need for 10 disks?"],
    ["e) how many calls does the naive FIB(6) make?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "n^(log₂ 4) = n²; f = n is smaller", "case 1: Θ(n²)"],
    ["b", "f = n² equals n²", "case 2: Θ(n² log n)"],
    ["c", "f = n³ is larger; 4(n/2)³ = n³/2 ≤ ½ n³", "case 3: Θ(n³)"],
    ["d", "2¹⁰ − 1", "1023 moves"],
    ["e", "2 F(7) − 1 = 2 · 13 − 1", "25 calls"]]})

s.scene("intro")
s.step("A recursive algorithm solves a problem by solving smaller copies of itself. It gives short, elegant code, and costs that are written as equations. This video covers both: how recursion runs, and how to solve its equations.", [s.head("Recursion and recurrences")])
s.step("Here are the eight stages.", show("stages"))
s.step("Recursion, the call stack, Fibonacci where recursion explodes, and the Towers of Hanoi.", [hl("stages[0..=3]")])
s.step("Then three ways to solve recurrences: unrolling, the recursion tree, and the master method, and an exam question.", [hl("stages[4..=7]")])

s.scene("base")
s.step("Stage 1: factorial. n factorial is n times n minus 1 factorial, and 1 factorial is 1.", [s.head("Stage 1 of 8: a base and a step")] + hide("stages") + show("fc", "rl") + [ml("fc", 1, 4)])
s.step("Every recursion needs a base case, solved directly. Here, n at most 1.", [ml("fc", 2, 3), hl("rl[0]", 0.3)])
s.step("A recursive case that calls itself on a smaller input. Here, n minus 1.", [ml("fc", 4, 4), hl("rl[1]", 0.3)])
s.step("And progress: every call must move closer to the base. Call FACT of minus 1 with a test of n equal to 1 instead, and it never stops.", [hl("rl[2]"), s.take("base case + smaller recursive case")])

s.scene("stack")
s.step("Stage 2: what happens when FACT of 4 runs? It cannot finish until FACT of 3 returns, so the machine keeps its frame on a stack.", [s.head("Stage 2 of 8: the call stack"), s.untake()] + hide("fc", "rl") + show("stk") + [hl("stk[0]")])
s.step("FACT of 4 calls FACT of 3, and waits.", [ins("stk", 1, "FACT(3)")])
s.step("FACT of 3 calls FACT of 2, and waits.", [ins("stk", 2, "FACT(2)")])
s.step("FACT of 2 calls FACT of 1. Four frames are now on the stack, each waiting for the one above it.", [ins("stk", 3, "FACT(1)")])
s.step("FACT of 1 is the base case: it returns 1, and its frame is popped.", [st("stk[3]", "→ 1"), rm("stk[3]", 0.6)])
s.step("FACT of 2 returns 2 times 1, 2, and is popped.", [st("stk[2]", "→ 2"), rm("stk[2]", 0.6)])
s.step("FACT of 3 returns 3 times 2, 6, and is popped.", [st("stk[1]", "→ 6"), rm("stk[1]", 0.6)])
s.step("And FACT of 4 returns 4 times 6, 24. The stack held n frames at its deepest: the space cost from video 2.", [st("stk[0]", "→ 24"), mk("stk[0]", 0.5), s.take("deepest stack = space used")])

s.scene("fib")
s.step("Stage 3: Fibonacci. FIB of n is FIB of n minus 1 plus FIB of n minus 2. Written directly, FIB of 5 makes this tree of calls.", [s.head("Stage 3 of 8: when recursion explodes"), s.untake()] + hide("stk") + show("fib"))
s.step("Look at the repeats. FIB of 3 is computed twice. FIB of 2, three times.", [mk("fib.c"), mk("fib.d", 0.2), mk("fib.e", 0.5), mk("fib.f", 0.6), mk("fib.h", 0.7)])
s.step("15 calls to compute 5. In general the calls are 2 times F of n plus 1, minus 1.", hide("fib") + show("fibm") + [hl("fibm[0]"), rv("fibm[1]", 0.5)])
s.step("FIB of 30 makes 2.7 million calls. The count grows like 1.618 to the n: exponential, only because the same values are recomputed.", [hl("fibm[1]"), rv("fibm[2]", 0.5)])
s.step("The fix is to remember each answer the first time: memoisation. Then each FIB of k is computed once: n plus 1 calls, linear. That idea is dynamic programming, Module 4.", [rv("fibm[3]"), hl("fibm[3]"), s.take("overlapping calls: remember answers")])

s.scene("hanoi")
s.step("Stage 4: the Towers of Hanoi. Move n disks from one peg to another, one at a time, never a larger disk on a smaller one.", [s.head("Stage 4 of 8: Towers of Hanoi"), s.untake()] + hide("fibm") + show("hn") + [hl("hn[0]")])
s.step("Recursively: move the top n minus 1 aside, move the largest disk, then move the n minus 1 back on top. So T of n is 2 T of n minus 1, plus 1.", [rv("hn[1]"), hl("hn[1]")])
s.step("T of 1 is 1, T of 2 is 3, T of 3 is 7. The pattern: 2 to the n, minus 1.", [rv("hn[2]"), hl("hn[2]")])
s.step("For the legendary 64 disks: 1.8 times 10 to the 19 moves. At one per second, about 585 billion years. Exponential, and this time no trick helps: every one of those moves is needed.", [rv("hn[3]"), hl("hn[3]"), s.take("Hanoi: 2ⁿ − 1 moves")])

s.scene("unroll")
s.step("Stage 5: solving a recurrence by unrolling. T of n is T of n minus 1 plus n.", [s.head("Stage 5 of 8: unrolling"), s.untake()] + hide("hn") + show("un") + [hl("un[0]")])
s.step("Replace T of n minus 1 by its own definition: T of n minus 2, plus n minus 1, plus n.", [rv("un[1]"), hl("un[1]")])
s.step("Keep going until you reach the base case, and look for the pattern.", [rv("un[2]"), hl("un[2]")])
s.step("It is 1 plus 2 up to n: n times n plus 1 over 2. Theta of n squared. This is insertion sort's worst case, written as a recurrence.", [rv("un[3]"), hl("un[3]")])
s.step("Binary search halves the range and does one comparison: T of n is T of n over 2 plus 1. Unrolled, the halving happens log 2 n times: Theta of log n.", [rv("un[4]"), hl("un[4]"), s.take("unroll, spot the pattern, sum it")])

s.scene("tree")
s.step("Stage 6: the recursion-tree method, for T of n equal to 2 T of n over 2 plus n, the shape of merge sort. The root costs n, and has two children of size n over 2.", [s.head("Stage 6 of 8: the recursion tree"), s.untake()] + hide("un") + show("rtree", "rt") + [hl("rtree.r"), hl("rt[0]", 0.3)])
s.step("Level 1: two nodes, each costing n over 2. Together, n.", [hl("rtree.a1"), hl("rtree.a2", 0.1), hl("rt[1]", 0.3)])
s.step("Level 2: four nodes of n over 4. Again n. Every level costs n.", [hl("rtree.b1"), hl("rtree.b2", 0.1), hl("rtree.b3", 0.2), hl("rtree.b4", 0.3), hl("rt[2..=3]", 0.4)])
s.step("Sizes halve until they reach 1, so there are log 2 n levels, plus n leaves. Total: n log n plus n, Theta of n log n. For n equal to 8: 8 times 3 plus 8, 32.", [hl("rt[4]"), mk("rt[4][2]", 0.5), s.take("cost per level × number of levels")])

s.scene("master")
s.step("Stage 7: the master method solves T of n equal to a T of n over b plus f of n in one step. Compare f of n with n to the log base b of a, the number of leaves.", [s.head("Stage 7 of 8: the master method"), s.untake()] + hide("rtree", "rt") + show("ms"))
s.step("Case 1: f is polynomially smaller. The leaves dominate: Theta of n to the log b a.", [hl("ms[0]")])
s.step("Case 2: f matches it. Every level costs the same: multiply by log n.", [hl("ms[1]")])
s.step("Case 3: f is polynomially larger, and shrinks geometrically down the tree. The root dominates: Theta of f.", [hl("ms[2]")])
s.step("Examples: 2 T of n over 2 plus n has n to the log 2 of 2, which is n, equal to f: case 2, n log n, as the tree showed.", [hl("ms[3]")])
s.step("9 T of n over 3 plus n: log 3 of 9 is 2, and n is smaller than n squared: case 1, Theta of n squared. T of 2n over 3 plus 1: n to the 0 is 1, equal to f: case 2, Theta of log n.", [hl("ms[4..=5]"), s.take("compare f(n) with n^(log_b a)")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("ms") + show("q") + [hl("q[0]")])
s.step("Solve three recurrences with the master method, count Hanoi moves for 10 disks, and count the calls of FIB of 6. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: a is 4, b is 2, so n to the log 2 of 4 is n squared. f is n, smaller: case 1, Theta of n squared.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: f is n squared, equal: case 2, Theta of n squared log n.", [hl("qa[1]")])
s.step("c: f is n cubed, larger. Check the condition: 4 times n over 2 cubed is n cubed over 2, at most a half times f. Case 3: Theta of n cubed.", [hl("qa[2]")])
s.step("d: 2 to the 10 minus 1: 1023 moves. e: 2 times F of 7 minus 1. F of 7 is 13, so 25 calls.", [hl("qa[3..=4]"), mk("qa[4][2]", 0.5)])
s.step("The usual slip: comparing f with n to the a, or n to the b, instead of n to the log base b of a.", [s.take("the critical exponent is log_b a")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A recursion needs a base case and a smaller recursive case. Each active call holds a stack frame. Recomputing the same calls makes Fibonacci exponential; Hanoi is exponential by nature.", [hl("stages[0..=3]")])
s.step("Recurrences are solved by unrolling, by summing a recursion tree level by level, or by the master method, comparing f with n to the log b a.", [hl("stages[4..=6]")])
s.step("Next video: the simplest data structure of all, the array, and how it sits in memory.", [mk("stages[0..=7]"), s.take("Next: arrays")])

s.save("/home/claude/playlist/dsa1/d1v5.json")

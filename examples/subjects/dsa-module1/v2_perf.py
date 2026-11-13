"""DSA Module 1, video 2: performance analysis: step counts, time and space."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

def isort_steps(a):
    """unit cost per executed line of CLRS INSERTION-SORT (8 counted lines)"""
    a = a[:]; n = len(a); c = 0
    j = 1
    while True:
        c += 1                       # for test
        if j >= n: break
        key = a[j]; c += 1; i = j - 1; c += 1
        while True:
            c += 1                   # while test
            if not (i >= 0 and a[i] > key): break
            a[i + 1] = a[i]; c += 1; i -= 1; c += 1
        a[i + 1] = key; c += 1; j += 1
    return c

best = lambda n: 5 * n - 4
worst = lambda n: 1.5 * n * n + 3.5 * n - 4
for n in range(2, 12):
    assert isort_steps(list(range(n))) == best(n)
    assert isort_steps(list(range(n, 0, -1))) == worst(n)
assert best(6) == 26 and worst(6) == 71 and worst(1000) == 1_503_496 and best(1000) == 4996
def sum_steps(n): return 1 + (n + 1) + n + 1
assert sum_steps(10) == 23 == 2 * 10 + 3
def madd(m, n): return (m + 1) + m * (n + 1) + m * n
assert madd(3, 4) == 2 * 3 * 4 + 2 * 3 + 1 == 31
def rsum(n): return 2 if n == 0 else 2 + rsum(n - 1)
assert rsum(10) == 22 == 2 * 10 + 2
def tri(n):
    c = 0
    for i in range(1, n + 2):
        c += 1
        if i > n: break
        for j in range(i, n + 2):
            c += 1
            if j > n: break
            c += 1
    return c
assert tri(10) == 131 == 10 * 10 + 3 * 10 + 1 and 10 * 11 // 2 == 55

s = Script("Performance analysis")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "What we measure, and how"],
    [2, "Space complexity"],
    [3, "The step-count method"],
    [4, "Two nested loops"],
    [5, "Insertion sort: best case"],
    [6, "Insertion sort: worst case"],
    [7, "Recursive step counts"],
    [8, "Exam question"]]})
s.obj({"id": "wh", "type": "table", "region": "center", "columns": ["", "a priori: analysis", "a posteriori: measurement"], "rows": [
    ["when", "before running", "after running"],
    ["gives", "a formula in n", "seconds on one machine"],
    ["depends on", "only the algorithm", "machine, compiler, load"],
    ["we count", "steps and memory words", "time and bytes"]]})
s.obj({"id": "sp", "type": "table", "region": "center", "columns": ["S(P) = c + S_P(instance)", "Sum(a, n)", "RSum(a, n), recursive"], "rows": [
    ["fixed part c", "code, s, i, n: 3 words", "code"],
    ["variable part S_P", "the array a: n words", "one stack frame per call"],
    ["frames", "", "n + 1 calls, 3 words each"],
    ["total", "n + 3", "3(n + 1)"]]})
s.obj({"id": "sc", "type": "table", "region": "center", "columns": ["line", "Sum(a, n)", "steps per run", "times run", "total"], "rows": [
    ["1", "s = 0", "1", "1", "1"],
    ["2", "for i = 1 to n", "1", "", ""],
    ["3", "    s = s + a[i]", "1", "", ""],
    ["4", "return s", "1", "1", "1"],
    ["", "", "", "total", ""]]})
s.obj({"id": "ma", "type": "table", "region": "center", "columns": ["line", "Add(a, b, c, m, n)", "times run"], "rows": [
    ["1", "for i = 1 to m", "m + 1"],
    ["2", "    for j = 1 to n", "m (n + 1)"],
    ["3", "        c[i][j] = a[i][j] + b[i][j]", "m n"],
    ["", "total", "2mn + 2m + 1"],
    ["", "m = 3, n = 4", "31 steps"]]})
s.obj({"id": "isb", "type": "table", "region": "center", "columns": ["line of INSERTION-SORT", "times run", "sorted input"], "rows": [
    ["for j = 2 to n", "n", "n"],
    ["key = A[j];  i = j − 1", "2 (n − 1)", "2 (n − 1)"],
    ["while test", "Σ tⱼ", "n − 1   (tⱼ = 1)"],
    ["shift;  i = i − 1", "2 Σ (tⱼ − 1)", "0"],
    ["A[i + 1] = key", "n − 1", "n − 1"],
    ["total", "", "5n − 4"]]})
s.obj({"id": "isw", "type": "math", "region": "center", "lines": [
    "\"reverse-sorted:\" quad t_j = j quad \"(the while test runs j times)\"",
    "sum_(j=2)^n j = (n(n+1))/2 - 1 quad quad sum_(j=2)^n (j - 1) = (n(n-1))/2",
    "T(n) = n + 3(n - 1) + ((n(n+1))/2 - 1) + n(n - 1) = 1.5 n^2 + 3.5 n - 4",
    "n = 6: quad \"best\" 26, \"worst\" 71 quad quad n = 1000: quad \"best\" 4996, \"worst\" 1503496"]})
s.obj({"id": "rc", "type": "code", "region": "center", "language": "text", "lines": [
    "RSUM(a, n)",
    "    if n == 0               // 1 step",
    "        return 0            // 1 step",
    "    return RSUM(a, n-1) + a[n]   // 1 step + the call"]})
s.obj({"id": "rcm", "type": "math", "region": "center", "lines": [
    "T(0) = 2",
    "T(n) = 2 + T(n - 1)",
    "= 2 + 2 + T(n - 2) = dots.c",
    "= 2n + T(0) = 2n + 2"]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "text", "lines": [
    "1  for i = 1 to n",
    "2      for j = i to n",
    "3          x = x + 1",
    "",
    "a) how many times does each line run?   b) the total for n = 10",
    "c) best and worst step counts of insertion sort for n = 10"]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"line 1:\" n + 1 quad \"line 3:\" sum_(i=1)^n (n - i + 1) = (n(n+1))/2",
    "\"line 2:\" sum_(i=1)^n (n - i + 2) = (n(n+1))/2 + n",
    "\"total\" = n^2 + 3n + 1 quad n = 10: quad 11 + 65 + 55 = 131",
    "\"c)\" quad 5 times 10 - 4 = 46 quad 1.5 times 100 + 35 - 4 = 181"]})

assert best(10) == 46 and worst(10) == 181 and isort_steps(list(range(10, 0, -1))) == 181

s.scene("intro")
s.step("How fast is an algorithm, and how much memory does it need? Not in seconds on one laptop, but as a formula in the size of the input. This video shows how to count, line by line.", [s.head("Performance analysis")])
s.step("Here are the eight stages.", show("stages"))
s.step("What we measure, space complexity, the step-count method, and two nested loops.", [hl("stages[0..=3]")])
s.step("Then insertion sort's best and worst cases, counting steps in recursion, and an exam question.", [hl("stages[4..=7]")])

s.scene("what")
s.step("Stage 1: there are two ways to judge performance. A priori analysis happens before running, and gives a formula in n, the size of the input.", [s.head("Stage 1 of 8: what we measure")] + hide("stages") + show("wh") + [hl("wh[0..=1]")])
s.step("A posteriori measurement runs the program and times it, which depends on the machine, the compiler, and whatever else is running.", [hl("wh[2]")])
s.step("What is a step? Any line whose cost does not depend on n: an assignment, a comparison, an addition. Whether it takes one machine cycle or five, it counts as one step, and that is why the answers hold on every machine.", [hl("wh[3]")])
s.step("Analysis counts steps and words of memory, so its answer holds on any machine. That is what this course does.", [hl("wh[3]"), s.take("count steps and words, as a function of n")])

s.scene("space")
s.step("Stage 2: the space a program needs is a fixed part c, for code and simple variables, plus a variable part that depends on the instance.", [s.head("Stage 2 of 8: space complexity"), s.untake()] + hide("wh") + show("sp") + [hl("sp[0]")])
s.step("An iterative Sum of an array needs s, i and n: 3 words, fixed.", [hl("sp[0][1]")])
s.step("Plus the array itself, n words. Total, n plus 3.", [hl("sp[1][1]"), hl("sp[3][1]", 0.4)])
s.step("A recursive sum has no loop variables, but every call pushes a stack frame: here a return address, a and n, 3 words.", [hl("sp[1][2]")])
s.step("RSum of n calls RSum of n minus 1, down to 0: n plus 1 frames at once. 3 times n plus 1 words of stack. Recursion trades loop variables for stack.", [hl("sp[2..=3]"), s.take("recursion costs stack: one frame per active call")])

s.scene("count")
s.step("Stage 3: the step-count method. For each line, write the steps it costs each time, and how many times it runs. Multiply, and add up.", [s.head("Stage 3 of 8: step counts"), s.untake()] + hide("sp") + show("sc") + [hl("sc[0]")])
s.step("s equals 0 runs once: 1 step.", [hl("sc[0]")])
s.step("The for line is tested once for each i from 1 to n, and once more when i reaches n plus 1 and the loop exits: n plus 1 times.", [hl("sc[1]"), st("sc[1][3]", "n + 1", 0.3), st("sc[1][4]", "n + 1", 0.5)])
s.step("The body runs n times.", [hl("sc[2]"), st("sc[2][3]", "n", 0.2), st("sc[2][4]", "n", 0.4)])
s.step("Return runs once. Total: 1 plus n plus 1 plus n plus 1: 2n plus 3. For n equal to 10, 23 steps.", [hl("sc[3]"), st("sc[4][4]", "2n + 3", 0.4), mk("sc[4][4]", 0.6), s.take("loop header: one more test than the body")])

s.scene("nest")
s.step("Stage 4: adding two m by n matrices. The outer loop header runs m plus 1 times.", [s.head("Stage 4 of 8: nested loops"), s.untake()] + hide("sc") + show("ma") + [hl("ma[0]")])
s.step("The inner header runs n plus 1 times for each of the m outer passes: m times n plus 1.", [hl("ma[1]")])
s.step("The body runs m times n times.", [hl("ma[2]")])
s.step("Total: 2mn plus 2m plus 1. For a 3 by 4 matrix: 24 plus 6 plus 1, 31 steps.", [hl("ma[3..=4]")])
s.step("For square n by n matrices this is 2 n squared plus 2n plus 1. The innermost body dominates: when loops nest, their counts multiply, and the deepest line decides how the total grows.", [s.take("nested loops multiply")])

s.scene("best")
s.step("Stage 5: insertion sort. Let t j be the number of times the while test runs for a given j. It depends on the data, not just on n.", [s.head("Stage 5 of 8: insertion sort, best case"), s.untake()] + hide("ma") + show("isb") + [hl("isb[2]")])
s.step("The for test runs n times, since j goes from 2 to n plus 1. Setting key and i runs n minus 1 times each.", [hl("isb[0..=1]")])
s.step("The while test runs sum of t j times; the shift and the decrement each run one fewer per pass: sum of t j minus 1.", [hl("isb[2..=3]")])
s.step("And dropping key in runs n minus 1 times.", [hl("isb[4]")])
s.step("If the input is already sorted, every while test fails at once: t j is 1, and nothing shifts. The total is 5n minus 4: linear in n.", [hl("isb[5]"), mk("isb[5][2]", 0.5), s.take("best case: already sorted, 5n − 4")])

s.scene("worst")
s.step("Stage 6: the worst case is reverse-sorted input. Key must travel all the way to the front, so the while test runs j times.", [s.head("Stage 6 of 8: insertion sort, worst case"), s.untake()] + hide("isb") + show("isw") + [hl("isw[0]")])
s.step("Now the two sums. Adding j for j from 2 to n gives n times n plus 1 over 2, minus 1. Adding j minus 1 gives n times n minus 1 over 2.", [rv("isw[1]"), hl("isw[1]")])
s.step("Put them in: T of n is 1.5 n squared plus 3.5 n minus 4. Quadratic.", [rv("isw[2]"), hl("isw[2]")])
s.step("For 6 elements: 26 steps at best, 71 at worst. For 1000: under five thousand against one and a half million. The same algorithm, the same n: the input decides.", [rv("isw[3]"), hl("isw[3]")])
s.step("On average, key travels about halfway, so t j is about j over 2: still quadratic. We usually quote the worst case, because it is a guarantee.", [s.take("worst case: reverse-sorted, about 1.5 n²")])

s.scene("rec")
s.step("Stage 7: counting steps in a recursive algorithm. RSum costs 2 steps when n is 0: the test and the return.", [s.head("Stage 7 of 8: recursive step counts"), s.untake()] + hide("isw") + show("rc") + [ml("rc", 2, 3)])
s.step("Otherwise, the test, plus the return with its addition, plus whatever the smaller call costs. T of n is 2 plus T of n minus 1.", [ml("rc", 4, 4)])
s.step("As equations: T of 0 is 2, and T of n is 2 plus T of n minus 1.", hide("rc") + show("rcm") + [hl("rcm[0]"), rv("rcm[1]", 0.4), hl("rcm[1]", 0.5)])
s.step("Unroll it: 2 plus 2 plus T of n minus 2, and so on, n times, down to T of 0.", [rv("rcm[2]"), hl("rcm[2]")])
s.step("2n plus 2. The same order as the loop, but with n plus 1 stack frames as well. This kind of equation is a recurrence; video 5 solves harder ones.", [rv("rcm[3]"), hl("rcm[3]"), s.take("recursion: write T(n) in terms of T(smaller)")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("rcm") + show("q") + [ml("q", 1, 3)])
s.step("Count how many times each line runs, the total for n equal to 10, and insertion sort's best and worst counts for n equal to 10. Pause and work it out.", [ml("q", 5, 6)])
s.step("Line 1 runs n plus 1 times. Line 3 runs n minus i plus 1 times for each i: n, then n minus 1, down to 1. That is n times n plus 1 over 2.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Line 2 runs one more time than its body for each i: n times n plus 1 over 2, plus n.", [rv("qa[1]"), hl("qa[1]")])
s.step("Total: n squared plus 3n plus 1. For n equal to 10: 11 plus 65 plus 55, 131.", [rv("qa[2]"), hl("qa[2]")])
s.step("c: best, 5 times 10 minus 4, 46. Worst, 150 plus 35 minus 4, 181.", [rv("qa[3]"), hl("qa[3]")])
s.step("The usual slip: forgetting the final failing test of each loop header, which adds n plus 1 extra steps here.", [s.take("headers run once more than bodies")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("We count steps and memory words as functions of n. Space is a fixed part plus a variable part, and recursion adds a stack frame per active call. Step counts multiply the cost of each line by how often it runs.", [hl("stages[0..=3]")])
s.step("Insertion sort costs 5n minus 4 on sorted input and about 1.5 n squared on reverse-sorted input. Recursive algorithms give recurrences.", [hl("stages[4..=6]")])
s.step("Exact counts are tedious, and the constants depend on what we call a step. Next video: keeping only what matters. Big O, Omega and Theta.", [mk("stages[0..=7]"), s.take("Next: asymptotic notation")])

s.save("/home/claude/playlist/dsa1/d1v2.json")

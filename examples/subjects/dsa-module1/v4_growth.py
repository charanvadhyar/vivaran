"""DSA Module 1, video 4: growth rates compared."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

L = math.log2
assert round(L(1e6)) == 20 and 1e6 * L(1e6) / 1e9 < 0.02 and 1e12 / 1e9 == 1000 and round(1e18 / 1e9 / 3.156e7) == 32
assert round(2**60 / 1e9 / 3.156e7, 1) == 36.5 and 2**30 / 1e9 > 1
assert 1e4**2 * 10e-9 == 1.0 and 1e5**2 * 0.1e-9 == 1.0
assert 2**26 * 1e-8 < 1 < 2**27 * 1e-8 and 2**33 * 1e-10 < 1 < 2**34 * 1e-10
assert round(100 ** (1 / 3), 2) == 4.64 and round(L(100), 2) == 6.64
assert len(str(math.factorial(100))) == 158 and f"{2**100:.3g}" == "1.27e+30"
# n^10 vs 2^n: crossover
assert min(n for n in range(2, 200) if 2**n > n**10) == 59 and all(2**n < n*n for n in [3]) and 2**4 == 16 and 2**2 == 4
# log(n!) = Theta(n log n): ratio approaches 1
assert abs(math.lgamma(10**6 + 1) / math.log(2) / (1e6 * L(1e6)) - 1) < 0.08
order = ["log n", "√n", "100n", "n log n", "n²", "n³", "1.5ⁿ", "2ⁿ", "n!"]
lv = lambda n: [math.log(L(n)), 0.5*math.log(n), math.log(100*n), math.log(n*L(n)), 2*math.log(n), 3*math.log(n), n*math.log(1.5), n*math.log(2), math.lgamma(n+1)]
v = lv(1e40); assert all(v[i] < v[i+1] for i in range(8))

s = Script("Growth rates")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The usual suspects"],
    [2, "Their values"],
    [3, "What they mean in seconds"],
    [4, "A picture of small n"],
    [5, "A faster computer"],
    [6, "Comparing with limits"],
    [7, "Surprising comparisons"],
    [8, "Exam question"]]})
s.obj({"id": "cls", "type": "table", "region": "center", "columns": ["order", "name", "example"], "rows": [
    ["1", "constant", "array access A[i]"],
    ["log n", "logarithmic", "binary search"],
    ["n", "linear", "finding the maximum"],
    ["n log n", "linearithmic", "merge sort"],
    ["n², n³", "quadratic, cubic", "insertion sort, matrix multiplication"],
    ["2ⁿ", "exponential", "trying every subset"],
    ["n!", "factorial", "trying every ordering"]]})
s.obj({"id": "val", "type": "table", "region": "center", "columns": ["n", "log₂ n", "n log₂ n", "n²", "n³", "2ⁿ", "n!"], "rows": [
    ["10", "3.3", "33", "100", "1000", "1024", "3.6 million"],
    ["100", "6.6", "664", "10⁴", "10⁶", "1.27 × 10³⁰", "158 digits"],
    ["1000", "10.0", "9966", "10⁶", "10⁹", "302 digits", "2568 digits"]]})
s.obj({"id": "sec", "type": "table", "region": "center", "columns": ["n = 1,000,000 at 10⁹ steps per second", "time"], "rows": [
    ["log n", "20 nanoseconds"],
    ["n", "1 millisecond"],
    ["n log n", "20 milliseconds"],
    ["n²", "1000 seconds: about 17 minutes"],
    ["n³", "10⁹ seconds: about 32 years"],
    ["2ⁿ, even at n = 60", "about 36.5 years"]]})
s.obj({"id": "pl", "type": "plot", "region": "center", "x": {"label": "n", "min": 1, "max": 10}, "y": {"label": "steps", "min": 0, "max": 100},
       "curves": [{"id": "lg", "fn": "log2(x)", "label": "log n", "visible": False},
                  {"id": "ln", "fn": "x", "label": "n", "visible": False},
                  {"id": "nl", "fn": "x * log2(x)", "label": "n log n", "visible": False},
                  {"id": "sq", "fn": "x^2", "label": "n²", "visible": False},
                  {"id": "ex", "fn": "2^x", "label": "2ⁿ", "visible": False}]})
s.obj({"id": "fast", "type": "table", "region": "center", "columns": ["cost", "largest n in a fixed time", "on a computer 100 times faster"], "rows": [
    ["n", "N", "100 N"],
    ["n²", "N", "10 N"],
    ["n³", "N", "4.64 N"],
    ["2ⁿ", "N", "N + 6.64"]]})
s.obj({"id": "lim", "type": "math", "region": "center", "lines": [
    "lim_(n -> infinity) f(n) / g(n) = 0 quad => quad f = o(g): quad f = O(g) \"but not\" Omega(g)",
    "lim_(n -> infinity) f(n) / g(n) = c, quad 0 < c < infinity quad => quad f = Theta(g)",
    "lim_(n -> infinity) f(n) / g(n) = infinity quad => quad f = omega(g): quad f = Omega(g) \"but not\" O(g)",
    "\"example:\" (n log n) / n^2 = (log n) / n -> 0: quad n log n = o(n^2)"]})
s.obj({"id": "sur", "type": "table", "region": "center", "columns": ["comparison", "winner (grows faster)", "why"], "rows": [
    ["n¹⁰ vs 2ⁿ", "2ⁿ", "from n = 59 on, 2ⁿ is larger"],
    ["(log n)¹⁰⁰ vs √n", "√n", "any power of n beats any power of log n"],
    ["log(n!) vs n log n", "neither: Θ(n log n)", "Stirling: log n! ≈ n log n − 1.44 n"],
    ["2^(log₂ n) vs n", "equal", "2^(log₂ n) = n"],
    ["4^(log₂ n) vs n²", "equal", "4^(log₂ n) = n²"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) order by growth: n², 2ⁿ, n log n, √n, log n, n!, 100n, n³, 1.5ⁿ"],
    ["b) at 10 ns per step, how large an n can an n² algorithm and a 2ⁿ algorithm handle in 1 second?"],
    ["c) the same on a machine 100 times faster"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "answer"], "rows": [
    ["a", "log n < √n < 100n < n log n < n² < n³ < 1.5ⁿ < 2ⁿ < n!"],
    ["b) n²", "n² × 10⁻⁸ s ≤ 1 s → n² ≤ 10⁸ → n = 10,000"],
    ["b) 2ⁿ", "2ⁿ ≤ 10⁸ → n = 26   (2²⁷ steps take 1.34 s)"],
    ["c) n²", "n² ≤ 10¹⁰ → n = 100,000: 10 times larger"],
    ["c) 2ⁿ", "2ⁿ ≤ 10¹⁰ → n = 33: just 7 more"]]})

tr = lambda c, d=0: {"action": "trace", "target": c, **({"delay": d} if d else {})}

s.scene("intro")
s.step("Big O lets us say an algorithm is order n squared. But how much worse is n squared than n log n, really? This video puts the common growth rates side by side, in numbers and in seconds.", [s.head("Growth rates")])
s.step("Here are the eight stages.", show("stages"))
s.step("The common orders, their values, what they mean in seconds, and a picture.", [hl("stages[0..=3]")])
s.step("Then what a faster computer buys you, comparing functions with limits, some surprising comparisons, and an exam question.", [hl("stages[4..=7]")])

s.scene("cls")
s.step("Stage 1: the orders you will meet again and again. Constant: the cost does not depend on n, like reading A of i.", [s.head("Stage 1 of 8: the usual suspects")] + hide("stages") + show("cls") + [hl("cls[0]")])
s.step("Logarithmic: binary search, halving the problem each step. Linear: one look at each element, like finding the maximum.", [hl("cls[1..=2]")])
s.step("n log n: merge sort, the best possible for sorting by comparisons. Quadratic and cubic: two or three nested loops.", [hl("cls[3..=4]")])
s.step("Exponential: trying every subset of n items. Factorial: trying every ordering. These two are where problems become intractable, the subject of Module 5.", [hl("cls[5..=6]"), s.take("1 < log n < n < n log n < n² < n³ < 2ⁿ < n!")])

s.scene("val")
s.step("Stage 2: their values. At n equal to 10, they all look manageable. Even n factorial is 3.6 million.", [s.head("Stage 2 of 8: their values"), s.untake()] + hide("cls") + show("val") + [hl("val[0]")])
s.step("At 100, log n is 6.6 and n log n is 664. But 2 to the n is 1.27 times 10 to the 30, and n factorial has 158 digits.", [hl("val[1]")])
s.step("At 1000, n log n is under ten thousand, n cubed is a billion, and 2 to the n has 302 digits.", [hl("val[2]")])
s.step("The gaps are not factors of 2 or 10. They grow without limit as n grows.", [hl("val[2]"), s.take("the gap between orders grows with n")])

s.scene("sec")
s.step("Stage 3: in seconds. Take a million elements, on a machine doing a billion steps per second. log n: 20 nanoseconds.", [s.head("Stage 3 of 8: in seconds"), s.untake()] + hide("val") + show("sec") + [hl("sec[0]")])
s.step("Linear: 1 millisecond. n log n: 20 milliseconds. Both instant.", [hl("sec[1..=2]")])
s.step("n squared: 10 to the 12 steps, a thousand seconds, about 17 minutes.", [hl("sec[3]")])
s.step("n cubed: 10 to the 18 steps, about 32 years.", [hl("sec[4]")])
s.step("And 2 to the n is hopeless long before a million. Even at n equal to 60, it takes 36 and a half years.", [hl("sec[5]"), s.take("n log n: instant · n²: minutes · 2ⁿ: never")])

s.scene("pic")
s.step("Stage 4: for small n, the picture is misleading. Here is log n, almost flat.", [s.head("Stage 4 of 8: a picture"), s.untake()] + hide("sec") + show("pl") + [tr("pl.lg")])
s.step("n, a straight line. n log n, bending slowly upward.", [tr("pl.ln"), tr("pl.nl", 0.4)])
s.step("n squared, and 2 to the n.", [tr("pl.sq"), tr("pl.ex", 0.4)])
s.step("Between n equal to 2 and 4, 2 to the n is actually below n squared. Yet by n equal to 7 it has left the picture. Small inputs hide the true order, which is why we judge algorithms by large n.", [hl("pl.ex"), s.take("judge by large n")])

s.scene("fast")
s.step("Stage 5: does a faster computer rescue a slow algorithm? Suppose in a fixed time you can handle size N, and you buy a machine 100 times faster.", [s.head("Stage 5 of 8: a faster computer"), s.untake()] + hide("pl") + show("fast"))
s.step("A linear algorithm now handles 100 N.", [hl("fast[0]")])
s.step("Quadratic: 100 times the steps allows only 10 times the size, the square root. Cubic: the cube root of 100, 4.64 times.", [hl("fast[1..=2]")])
s.step("Exponential: each extra element doubles the work, so 100 times the speed adds only log 2 of 100, about 6.64 elements. Better hardware cannot fix a bad order; a better algorithm can.", [hl("fast[3]"), s.take("hardware adds to n; algorithms multiply it")])

s.scene("lim")
s.step("Stage 6: to compare two functions quickly, look at the limit of f over g as n grows. If it is 0, f is little o of g: f is O of g, but not Omega.", [s.head("Stage 6 of 8: comparing with limits"), s.untake()] + hide("fast") + show("lim") + [hl("lim[0]")])
s.step("If the limit is a positive constant, they grow alike: Theta.", [rv("lim[1]"), hl("lim[1]")])
s.step("If it is infinity, f is little omega of g: Omega, but not Big O.", [rv("lim[2]"), hl("lim[2]")])
s.step("Example: n log n over n squared is log n over n, which goes to 0. So n log n is little o of n squared.", [rv("lim[3]"), hl("lim[3]"), s.take("lim f/g: 0 → o · c → Θ · ∞ → ω")])

s.scene("sur")
s.step("Stage 7: some comparisons surprise people. n to the 10 against 2 to the n: the polynomial leads for a long time, but from n equal to 59 on, 2 to the n is larger, and the gap only grows.", [s.head("Stage 7 of 8: surprising comparisons"), s.untake()] + hide("lim") + show("sur") + [hl("sur[0]")])
s.step("log n to the hundredth power against root n: root n wins eventually. Any positive power of n beats any power of log n.", [hl("sur[1]")])
s.step("log of n factorial against n log n: by Stirling's formula they are Theta of each other. This fact returns when we prove that sorting needs n log n comparisons.", [hl("sur[2]")])
s.step("And exponents of logarithms simplify: 2 to the log 2 of n is just n, and 4 to the log 2 of n is n squared.", [hl("sur[3..=4]"), s.take("exponential beats polynomial beats logarithmic")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("sur") + show("q") + [hl("q[0]")])
s.step("Order nine functions by growth, and find how large an input a quadratic and an exponential algorithm can handle in one second, on two machines. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: log n, root n, 100n, n log n, n squared, n cubed, 1.5 to the n, 2 to the n, n factorial. The constant 100 keeps 100n above n log n only while log n is below 100, that is up to n equal to 2 to the 100. Growth order is about large n.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: at 10 nanoseconds a step, one second allows 10 to the 8 steps. n squared at most 10 to the 8 gives n equal to 10,000.", [hl("qa[1]")])
s.step("2 to the n at most 10 to the 8: 2 to the 26 is 67 million, 2 to the 27 is 134 million, too many. n equal to 26.", [hl("qa[2]")])
s.step("c: 100 times faster allows 10 to the 10 steps. Quadratic: n equal to 100,000, ten times larger. Exponential: 2 to the 33 is 8.6 billion, so n equal to 33: just 7 more.", [hl("qa[3..=4]"), mk("qa[4][1]", 0.5)])
s.step("The usual slip: thinking a big constant, like 100n, makes a linear algorithm worse than n log n. For large n, the order always wins.", [s.take("order beats constants, eventually")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Constant, logarithmic, linear, n log n, polynomial, exponential, factorial: the gaps between them grow without limit, from milliseconds to centuries. Small n hides the order.", [hl("stages[0..=3]")])
s.step("A faster computer multiplies a linear algorithm's reach but adds only a few elements to an exponential one. Limits of f over g settle any comparison.", [hl("stages[4..=6]")])
s.step("Next video: recursion, and how to solve the recurrences it produces.", [mk("stages[0..=7]"), s.take("Next: recursion and recurrences")])

s.save("/home/claude/playlist/dsa1/d1v4.json")

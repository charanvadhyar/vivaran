"""DSA Module 1, video 3: Big-O, Omega and Theta."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

f = lambda n: 3 * n * n + 2 * n + 5
assert all(f(n) <= 10 * n * n for n in range(1, 10000))
assert all(f(n) <= 4 * n * n for n in range(4, 10000)) and f(3) > 4 * 9 and round(1 + math.sqrt(6), 2) == 3.45
assert all(f(n) >= 3 * n * n for n in range(1, 10000))
g = lambda n: 5 * n**3 - 2 * n * n + 7
assert all(3 * n**3 <= g(n) <= 12 * n**3 for n in range(1, 10000))
assert all(2 ** (n + 1) <= 2 * 2 ** n for n in range(1, 200)) and 4 ** 30 // 2 ** 30 == 2 ** 30
assert f(1000) == 3_002_005 and round(f(1000) / (3 * 1000**2), 4) == 1.0007

s = Script("Big-O, Omega and Theta")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why drop the details"],
    [2, "Big-O: an upper bound"],
    [3, "Proving a Big-O bound"],
    [4, "The picture: c and n₀"],
    [5, "Omega: a lower bound"],
    [6, "Theta: a tight bound"],
    [7, "Disproving a bound"],
    [8, "Rules that save work"],
    [9, "Saying it correctly"],
    [10, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["n", "3n² + 2n + 5", "3n² alone", "share of 3n²"], "rows": [
    ["10", "325", "300", "92%"],
    ["100", "30,205", "30,000", "99.3%"],
    ["1000", "3,002,005", "3,000,000", "99.93%"],
    ["so", "lower terms vanish", "constants depend on the machine", "keep only n²"]]})
s.obj({"id": "bo", "type": "math", "region": "center", "lines": [
    "f(n) = O(g(n)) quad \"if there are constants\" c > 0 \"and\" n_0",
    "\"such that\" quad 0 <= f(n) <= c dot g(n) quad \"for all\" n >= n_0",
    "\"f grows no faster than g: an upper bound\""]})
s.obj({"id": "pf", "type": "math", "region": "center", "lines": [
    "\"claim:\" quad 3n^2 + 2n + 5 = O(n^2)",
    "\"for\" n >= 1: quad 2n <= 2n^2 quad \"and\" quad 5 <= 5n^2",
    "3n^2 + 2n + 5 <= 3n^2 + 2n^2 + 5n^2 = 10 n^2",
    "c = 10, quad n_0 = 1 quad checkmark",
    "\"or\" c = 4: quad 3n^2 + 2n + 5 <= 4n^2 <=> n^2 - 2n - 5 >= 0 <=> n >= 1 + sqrt(6) approx 3.45: quad n_0 = 4"]})
s.obj({"id": "pl", "type": "plot", "region": "center",
       "x": {"label": "n", "min": 0, "max": 6}, "y": {"label": "steps", "min": 0, "max": 140},
       "curves": [{"id": "f", "fn": "3x^2 + 2x + 5", "label": "f(n)", "visible": False},
                  {"id": "c4", "fn": "4x^2", "label": "4n²", "visible": False},
                  {"id": "c3", "fn": "3x^2", "label": "3n²", "visible": False}],
       "points": [{"id": "n0", "at": [3.45, 47.6], "label": "n₀ ≈ 3.45"}]})
s.obj({"id": "om", "type": "math", "region": "center", "lines": [
    "f(n) = Omega(g(n)) quad \"if\" quad 0 <= c dot g(n) <= f(n) quad \"for all\" n >= n_0",
    "3n^2 + 2n + 5 >= 3n^2 quad \"for\" n >= 1: quad c = 3, n_0 = 1",
    "\"f grows at least as fast as g: a lower bound\""]})
s.obj({"id": "th", "type": "math", "region": "center", "lines": [
    "f(n) = Theta(g(n)) quad \"if\" quad c_1 g(n) <= f(n) <= c_2 g(n) quad \"for all\" n >= n_0",
    "3n^2 <= 3n^2 + 2n + 5 <= 10n^2 quad \"for\" n >= 1",
    "c_1 = 3, c_2 = 10, n_0 = 1: quad 3n^2 + 2n + 5 = Theta(n^2)",
    "Theta <=> O \"and\" Omega \"together\""]})
s.obj({"id": "dp", "type": "math", "region": "center", "lines": [
    "\"is\" n^2 = O(n)? quad \"suppose\" n^2 <= c n \"for all\" n >= n_0",
    "\"divide by\" n: quad n <= c \"for all\" n >= n_0 quad \"— false for\" n > c",
    "\"no constant works: \" n^2 != O(n)",
    "2^(n+1) = 2 dot 2^n = O(2^n) quad \"but\" quad 2^(2n) = 4^n: quad 4^n / 2^n = 2^n -> infinity"]})
s.obj({"id": "ru", "type": "table", "region": "center", "columns": ["rule", "example"], "rows": [
    ["a polynomial of degree d is Θ(nᵈ)", "7n⁴ − n² + 9 = Θ(n⁴)"],
    ["sum: O(f) + O(g) = O(max(f, g))", "a loop of n, then a nested loop: O(n + n²) = O(n²)"],
    ["product: O(f) · O(g) = O(f · g)", "a loop of n, each calling an O(log n) search: O(n log n)"],
    ["log base does not matter", "log₂ n = log₁₀ n / log₁₀ 2: a constant factor"],
    ["transitive", "f = O(g) and g = O(h) ⇒ f = O(h)"]]})
s.obj({"id": "say", "type": "table", "region": "center", "columns": ["statement about insertion sort", "true?"], "rows": [
    ["its running time is O(n²)", "yes: on every input"],
    ["its running time is Ω(n)", "yes: on every input"],
    ["its running time is Θ(n²)", "no: sorted input takes Θ(n)"],
    ["its worst-case running time is Θ(n²)", "yes"],
    ["its best-case running time is Θ(n)", "yes"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) prove 5n³ − 2n² + 7 = Θ(n³): give c₁, c₂ and n₀"],
    ["b) is 2ⁿ⁺¹ = O(2ⁿ)?  is 2²ⁿ = O(2ⁿ)?"],
    ["c) is n log n = O(n²)?  is it Ω(n²)?"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"upper, n\" >= 1: quad 5n^3 - 2n^2 + 7 <= 5n^3 + 7n^3 = 12 n^3",
    "\"lower, n\" >= 1: quad 5n^3 - 2n^2 + 7 - 3n^3 = 2n^3 - 2n^2 + 7 > 0",
    "c_1 = 3, quad c_2 = 12, quad n_0 = 1",
    "\"b)\" 2^(n+1) <= 2 dot 2^n: \"yes\" quad 2^(2n) / 2^n = 2^n \"is unbounded: no\"",
    "\"c)\" n log n <= n^2 \"for\" n >= 1: \"yes\" quad (n log n) / n^2 = (log n) / n -> 0: \"not\" Omega(n^2)"]})

s.scene("intro")
s.step("Last video, insertion sort took 1.5 n squared plus 3.5 n minus 4 steps. Nobody quotes a number like that. We say it is order n squared. This video makes order precise: Big O, Omega and Theta.", [s.head("Asymptotic notation")])
s.step("Here are the ten stages.", show("stages"))
s.step("Why we drop details, Big O, a proof, and a picture of the constants.", [hl("stages[0..=3]")])
s.step("Then Omega, Theta, how to disprove a bound, rules that save work, how to state bounds correctly, and an exam question.", [hl("stages[4..=9]")])

s.scene("why")
s.step("Stage 1: take 3 n squared plus 2n plus 5. At n equal to 10, the 3 n squared term is already 92 percent of the total.", [s.head("Stage 1 of 10: why drop the details")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("At 100, 99.3 percent. At 1000, 99.93 percent. For large inputs, the lower terms vanish.", [hl("why[1..=2]")])
s.step("And the constant 3 depends on what we called a step and on the machine. What does not depend on anything is that the cost grows like n squared.", [hl("why[3]"), s.take("keep the fastest-growing term, drop its constant")])

s.scene("bigo")
s.step("Stage 2: Big O. f of n is O of g of n if there are positive constants c and n zero,", [s.head("Stage 2 of 10: Big-O"), s.untake()] + hide("why") + show("bo") + [hl("bo[0]")])
s.step("such that f of n is at most c times g of n, for every n from n zero onward.", [rv("bo[1]"), hl("bo[1]")])
s.step("In words: beyond some point, f never grows faster than a constant multiple of g. Big O is an upper bound.", [rv("bo[2]"), hl("bo[2]"), s.take("O: f ≤ c·g from n₀ on")])

s.scene("proof")
s.step("Stage 3: prove 3 n squared plus 2n plus 5 is O of n squared. We must find c and n zero.", [s.head("Stage 3 of 10: proving a bound"), s.untake()] + hide("bo") + show("pf") + [hl("pf[0]")])
s.step("The trick: for n at least 1, every lower term is at most the same coefficient times n squared. 2n is at most 2 n squared, and 5 is at most 5 n squared.", [rv("pf[1]"), hl("pf[1]")])
s.step("So the whole thing is at most 3 plus 2 plus 5, 10 n squared.", [rv("pf[2]"), hl("pf[2]")])
s.step("c equal to 10 and n zero equal to 1 work. Proof done.", [rv("pf[3]"), mk("pf[3]")])
s.step("The constants are not unique. A smaller c needs a larger n zero. With c equal to 4, the inequality becomes n squared minus 2n minus 5 at least 0, which holds from 1 plus root 6, about 3.45. So n zero is 4.", [rv("pf[4]"), hl("pf[4]"), s.take("any one pair (c, n₀) is a proof")])

s.scene("pic")
s.step("Stage 4: the picture. Here is f of n, 3 n squared plus 2n plus 5.", [s.head("Stage 4 of 10: c and n₀"), s.untake()] + hide("pf") + show("pl") + [{"action": "trace", "target": "pl.f"}])
s.step("And 4 n squared. Near zero, f is above it, because of the plus 5.", [{"action": "trace", "target": "pl.c4"}])
s.step("They cross at about 3.45. From there on, f stays below 4 n squared for ever. That crossing is n zero.", show() + [hl("pl.n0"), hl("pl.c4", 0.3)])
s.step("And 3 n squared stays below f everywhere: that will be a lower bound. f is squeezed between two multiples of n squared.", [{"action": "trace", "target": "pl.c3"}, s.take("beyond n₀, f stays under c·g")])

s.scene("omega")
s.step("Stage 5: Omega is the mirror image. f of n is Omega of g of n if c times g of n is at most f of n, for every n from n zero on.", [s.head("Stage 5 of 10: Omega"), s.untake()] + hide("pl") + show("om") + [hl("om[0]")])
s.step("Our f is at least 3 n squared for every n at least 1, since 2n plus 5 is positive. c equal to 3, n zero equal to 1.", [rv("om[1]"), hl("om[1]")])
s.step("Omega says f grows at least as fast as g: a lower bound.", [rv("om[2]"), hl("om[2]"), s.take("Ω: f ≥ c·g from n₀ on")])

s.scene("theta")
s.step("Stage 6: Theta means both at once. f is sandwiched: c 1 times g below, c 2 times g above, from n zero on.", [s.head("Stage 6 of 10: Theta"), s.untake()] + hide("om") + show("th") + [hl("th[0]")])
s.step("We already have both halves: 3 n squared below, 10 n squared above, for n at least 1.", [rv("th[1]"), hl("th[1]")])
s.step("So c 1 is 3, c 2 is 10, n zero is 1, and f is Theta of n squared.", [rv("th[2]"), mk("th[2]")])
s.step("Theta holds exactly when both Big O and Omega hold. It is the tight answer: f grows like g, no faster and no slower.", [rv("th[3]"), hl("th[3]"), s.take("Θ = O and Ω: a tight bound")])

s.scene("disprove")
s.step("Stage 7: how to show a bound is false. Is n squared O of n? Suppose it were: n squared at most c n for all large n.", [s.head("Stage 7 of 10: disproving a bound"), s.untake()] + hide("th") + show("dp") + [hl("dp[0]")])
s.step("Divide by n: n at most c, for every large n. But n keeps growing and c is fixed. Any n bigger than c breaks it.", [rv("dp[1]"), hl("dp[1]")])
s.step("No constant can work, so n squared is not O of n. To disprove, show that f over g grows without bound.", [rv("dp[2]"), hl("dp[2]")])
s.step("A classic trap: 2 to the n plus 1 is just 2 times 2 to the n, so it is O of 2 to the n. But 2 to the 2n is 4 to the n, and 4 to the n over 2 to the n is 2 to the n, unbounded. Constants in an exponent matter.", [rv("dp[3]"), hl("dp[3]"), s.take("disprove: f / g → ∞")])

s.scene("rules")
s.step("Stage 8: a few rules save writing a proof every time. A polynomial of degree d is Theta of n to the d: the leading term wins.", [s.head("Stage 8 of 10: rules that save work"), s.untake()] + hide("dp") + show("ru") + [hl("ru[0]")])
s.step("Sum rule: code that runs one part after another costs the larger of the two. A single loop followed by a nested loop is O of n squared.", [hl("ru[1]")])
s.step("Product rule: code nested inside a loop multiplies. n iterations, each doing a binary search, is O of n log n.", [hl("ru[2]")])
s.step("The base of a logarithm does not matter: changing base multiplies by a constant, which Big O ignores. So we just write log n.", [hl("ru[3]")])
s.step("And the bounds chain: if f is O of g and g is O of h, then f is O of h.", [hl("ru[4]"), s.take("sequence adds, nesting multiplies")])

s.scene("say")
s.step("Stage 9: saying it correctly. Insertion sort's running time is O of n squared: true, on every input, since even the worst case is quadratic.", [s.head("Stage 9 of 10: saying it correctly"), s.untake()] + hide("ru") + show("say") + [hl("say[0]")])
s.step("It is also Omega of n: every input takes at least linear time.", [hl("say[1]")])
s.step("But its running time is Theta of n squared is false: on sorted input it is linear.", [hl("say[2]")])
s.step("Name the case, and Theta is fine: its worst-case running time is Theta of n squared, and its best case is Theta of n.", [hl("say[3..=4]"), s.take("Θ of a running time needs a named case")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("say") + show("q") + [hl("q[0]")])
s.step("Prove 5 n cubed minus 2 n squared plus 7 is Theta of n cubed, and decide three more bounds. Pause and work it out.", [hl("q[1..=2]")])
s.step("Upper: drop the minus 2 n squared, which only helps, and bound 7 by 7 n cubed. At most 12 n cubed for n at least 1.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Lower: subtract 3 n cubed. 2 n cubed minus 2 n squared plus 7 is positive, because n cubed is at least n squared when n is at least 1.", [rv("qa[1]"), hl("qa[1]")])
s.step("So c 1 equal to 3, c 2 equal to 12, n zero equal to 1.", [rv("qa[2]"), mk("qa[2]")])
s.step("b: 2 to the n plus 1 is 2 times 2 to the n: yes, with c equal to 2. 2 to the 2n over 2 to the n is 2 to the n, unbounded: no.", [rv("qa[3]"), hl("qa[3]")])
s.step("c: n log n is at most n squared, since log n is at most n: yes. But n log n over n squared is log n over n, which goes to 0: it is not Omega of n squared.", [rv("qa[4]"), hl("qa[4]")])
s.step("The usual slip: dropping the negative term in the lower bound. For the lower bound you must handle it, not ignore it.", [s.take("negative terms: free for upper, careful for lower")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("We keep the fastest-growing term. Big O means at most c times g from some n zero on, and a proof is any one pair of constants.", [hl("stages[0..=3]")])
s.step("Omega is the lower bound, Theta is both. To disprove, show the ratio is unbounded. Sequence adds, nesting multiplies. And a Theta for running time needs a named case.", [hl("stages[4..=8]")])
s.step("Next video: comparing growth rates, from log n to n factorial, and what they mean in seconds.", [mk("stages[0..=9]"), s.take("Next: growth rates")])

s.save("/home/claude/playlist/dsa1/d1v3.json")

"""DSA Module 3, video 3: Karatsuba multiplication."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *

def kara(x, y, log, depth=0):
    if x < 10 or y < 10: return x * y
    m = max(len(str(x)), len(str(y))) // 2
    a, b = divmod(x, 10 ** m); c, d = divmod(y, 10 ** m)
    ac = kara(a, c, log, depth + 1); bd = kara(b, d, log, depth + 1); s = kara(a + b, c + d, log, depth + 1)
    log.append((depth, x, y, a, b, c, d, ac, bd, s, s - ac - bd))
    return ac * 10 ** (2 * m) + (s - ac - bd) * 10 ** m + bd
L = []; assert kara(1234, 5678, L) == 1234 * 5678 == 7006652
top = L[-1]; assert top[3:] == (12, 34, 56, 78, 672, 2652, 6164, 2840)
assert 46 * 134 == 6164 and 12 * 78 + 34 * 56 == 2840 and 6720000 + 284000 + 2652 == 7006652
E = []; assert kara(3141, 5926, E) == 18613566
assert E[-1][3:] == (31, 41, 59, 26, 1829, 1066, 6120, 3225) and 72 * 85 == 6120 and 31 * 26 + 41 * 59 == 3225
assert 18290000 + 322500 + 1066 == 18613566
assert 3 ** 10 == 59049 and 1024 ** 2 == 1048576 and 3 ** 6 == 729 and 4 ** 6 == 4096
assert abs(math.log2(3) - 1.585) < 0.001

s = Script("Karatsuba multiplication")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "School multiplication: n² digit products"],
    [2, "Divide and conquer, first try"],
    [3, "Karatsuba's trick: three products, not four"],
    [4, "1234 × 5678, worked"],
    [5, "The algorithm"],
    [6, "The running time: n^1.585"],
    [7, "Exam question"]]})
s.obj({"id": "sch", "type": "table", "region": "center", "columns": ["school method", ""], "rows": [
    ["1234 × 5678", "every digit of one times every digit of the other"],
    ["two n-digit numbers", "n × n = n² digit products, then additions"],
    ["n = 4", "16 products"],
    ["n = 1024 digits (cryptography)", "1,048,576 products"],
    ["question (Kolmogorov, 1960)", "is Θ(n²) the best possible? Karatsuba, aged 23: no"]]})
s.obj({"id": "sp", "type": "math", "region": "center", "lines": [
    "x = a dot 10^m + b, quad y = c dot 10^m + d quad (m = n slash 2)",
    "1234 = 12 dot 10^2 + 34, quad 5678 = 56 dot 10^2 + 78",
    "x y = a c dot 10^(2m) + (a d + b c) dot 10^m + b d",
    "\"four half-size products: \" T(n) = 4 T(n slash 2) + Theta(n) = Theta(n^2) quad \"no gain\""]})
s.obj({"id": "kt", "type": "math", "region": "center", "lines": [
    "(a + b)(c + d) = a c + a d + b c + b d",
    "a d + b c = (a + b)(c + d) - a c - b d",
    "\"products needed: \" a c, quad b d, quad (a + b)(c + d) quad \"three, not four\"",
    "\"the price: a few extra additions and subtractions, \" Theta(n)"]})
s.obj({"id": "ex", "type": "table", "region": "center", "columns": ["1234 × 5678", "working", "value"], "rows": [
    ["split", "a = 12, b = 34;   c = 56, d = 78", ""],
    ["ac", "12 × 56", ""],
    ["bd", "34 × 78", ""],
    ["(a + b)(c + d)", "46 × 134", ""],
    ["ad + bc", "6164 − 672 − 2652", ""],
    ["result", "672·10⁴ + 2840·10² + 2652", ""]]})
s.obj({"id": "kc", "type": "code", "region": "center", "language": "text", "lines": [
    "KARATSUBA(x, y)",
    "    if x < 10 or y < 10:  return x · y                   // one digit: multiply directly",
    "    m = ⌊max(digits(x), digits(y)) / 2⌋",
    "    a, b = x div 10^m, x mod 10^m;    c, d = y div 10^m, y mod 10^m",
    "    p1 = KARATSUBA(a, c)",
    "    p2 = KARATSUBA(b, d)",
    "    p3 = KARATSUBA(a + b, c + d)",
    "    return p1 · 10^(2m) + (p3 − p1 − p2) · 10^m + p2     // shifts and adds: Θ(n)"]})
s.obj({"id": "inr", "type": "table", "region": "center", "columns": ["12 × 56, one level down", "working", "value"], "rows": [
    ["split", "a = 1, b = 2;   c = 5, d = 6", ""],
    ["ac, bd", "1 × 5,   2 × 6", "5,  12"],
    ["(a + b)(c + d)", "3 × 11: 3 has one digit, so multiply directly", "33"],
    ["middle", "33 − 5 − 12", "16"],
    ["result", "5·100 + 16·10 + 12", "672 ✓"]]})
s.obj({"id": "lvl", "type": "table", "region": "center", "columns": ["level", "number size", "school-style: 4 per call", "Karatsuba: 3 per call"], "rows": [
    ["0", "n", "1", "1"], ["1", "n/2", "4", "3"], ["2", "n/4", "16", "9"], ["k", "n/2ᵏ", "4ᵏ", "3ᵏ"], ["log₂ n", "1 digit", "n²", "3^log₂n = n^log₂3"]]})
s.obj({"id": "rt", "type": "math", "region": "center", "lines": [
    "T(n) = 3 T(n slash 2) + Theta(n)",
    "\"master method: \" a = 3, b = 2, quad n^(log_2 3) approx n^1.585 \" grows faster than \" f(n) = n",
    "\"case 1: \" T(n) = Theta(n^(log_2 3)) = Theta(n^1.585)",
    "n = 1024 \" digits: \" 3^10 = 59049 \" products against \" 1024^2 = 1048576",
    "\"later: Toom-Cook, FFT methods, and Harvey and van der Hoeven (2019): \" O(n log n)"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["multiply 3141 × 5926 by Karatsuba's method (one level of splitting)"],
    ["a) give a, b, c, d and the three products"],
    ["b) find ad + bc and the result"],
    ["c) n = 64 digits, split down to single digits: single-digit products, Karatsuba against school?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "a = 31, b = 41, c = 59, d = 26", "ac = 1829, bd = 1066"],
    ["a)", "(a + b)(c + d) = 72 × 85", "6120"],
    ["b)", "6120 − 1829 − 1066", "ad + bc = 3225"],
    ["b)", "1829·10⁴ + 3225·10² + 1066 = 18290000 + 322500 + 1066", "18,613,566"],
    ["c)", "64 = 2⁶: six levels of splitting", "3⁶ = 729 against 4⁶ = 4096"]]})

s.scene("intro")
s.step("Multiplying two numbers seems too basic to improve. For two thousand years everyone used the school method. In 1960, a 23-year-old student, Anatoly Karatsuba, found a faster way, using divide and conquer and one clever line of algebra.", [s.head("Karatsuba multiplication")])
s.step("Here are the seven stages.", show("stages"))
s.step("The school method, a first divide-and-conquer attempt, Karatsuba's trick, and a worked example.", [hl("stages[0..=3]")])
s.step("Then the algorithm, its running time, and an exam question.", [hl("stages[4..=6]")])

s.scene("sch")
s.step("Stage 1: the school method multiplies every digit of one number by every digit of the other.", [s.head("Stage 1 of 7: the school method")] + hide("stages") + show("sch") + [hl("sch[0]")])
s.step("Two n-digit numbers need n times n, n squared, digit products, plus the additions.", [hl("sch[1]")])
s.step("For 4 digits that is 16 products. For 1024-digit numbers, the size used in cryptography, over a million.", [hl("sch[2..=3]")])
s.step("The mathematician Kolmogorov conjectured that n squared could not be beaten. Within a week of hearing this at his seminar, Karatsuba proved him wrong.", [hl("sch[4]"), s.take("school method: Θ(n²) digit products")])

s.scene("split")
s.step("Stage 2: divide. Split each n-digit number into a high half and a low half, each with m equals n over 2 digits. x is a times 10 to the m, plus b.", [s.head("Stage 2 of 7: a first try"), s.untake()] + hide("sch") + show("sp") + [hl("sp[0]")])
s.step("For example, 1234 is 12 times 100, plus 34; and 5678 is 56 times 100, plus 78.", [rv("sp[1]"), hl("sp[1]")])
s.step("Multiply out: x y is a c times 10 to the 2 m, plus a d plus b c, times 10 to the m, plus b d. Multiplying by a power of 10 is just a shift.", [rv("sp[2]"), hl("sp[2]")])
s.step("But that is four multiplications of half-size numbers. The recurrence 4 T of n over 2, plus n, solves to n squared again. Nothing gained.", [rv("sp[3]"), hl("sp[3]"), s.take("four half-size products: still Θ(n²)")])

s.scene("trick")
s.step("Stage 3: the trick. Multiply out a plus b, times c plus d: it gives all four products, a c plus a d plus b c plus b d.", [s.head("Stage 3 of 7: Karatsuba's trick"), s.untake()] + hide("sp") + show("kt") + [hl("kt[0]")])
s.step("So the middle term, a d plus b c, equals a plus b times c plus d, minus a c, minus b d.", [rv("kt[1]"), hl("kt[1]")])
s.step("And we need a c and b d anyway, for the outer terms. So three multiplications give everything: a c, b d, and a plus b times c plus d.", [rv("kt[2]"), hl("kt[2]")])
s.step("The price is a few extra additions and subtractions. Those cost Theta of n, much cheaper than a multiplication.", [rv("kt[3]"), hl("kt[3]"), s.take("ad + bc = (a+b)(c+d) − ac − bd")])

s.scene("ex")
s.step("Stage 4: multiply 1234 by 5678. Split: a is 12, b is 34; c is 56, d is 78.", [s.head("Stage 4 of 7: 1234 × 5678"), s.untake()] + hide("kt") + show("ex") + [hl("ex[0]")])
s.step("First product: a c, 12 times 56, is 672.", [hl("ex[1]"), st("ex[1][2]", "672", 0.5)])
s.step("Second: b d, 34 times 78, is 2652.", [hl("ex[2]"), st("ex[2][2]", "2652", 0.5)])
s.step("Third: a plus b is 46, c plus d is 134. 46 times 134 is 6164.", [hl("ex[3]"), st("ex[3][2]", "6164", 0.5)])
s.step("The middle term: 6164 minus 672 minus 2652, which is 2840. Check: 12 times 78, plus 34 times 56, is 936 plus 1904, 2840.", [hl("ex[4]"), st("ex[4][2]", "2840", 0.5)])
s.step("Assemble: 672 shifted 4 places, plus 2840 shifted 2 places, plus 2652: 7,006,652. Three multiplications of two-digit numbers instead of four.", [hl("ex[5]"), st("ex[5][2]", "7,006,652", 0.5), mk("ex[5][2]", 0.8), s.take("1234 × 5678 = 7,006,652")])

s.scene("algo")
s.step("Stage 5: the algorithm applies the trick recursively. A one-digit number is multiplied directly.", [s.head("Stage 5 of 7: the algorithm"), s.untake()] + hide("ex") + show("kc") + [ml("kc", 1, 2)])
s.step("Otherwise split both numbers at m, half the number of digits.", [ml("kc", 3, 4)])
s.step("Three recursive calls: a c, b d, and a plus b times c plus d. So 12 times 56 would itself be split into 1, 2 and 5, 6.", [ml("kc", 5, 7)])
s.step("Then combine with shifts, additions and subtractions, all linear in the number of digits.", [ml("kc", 8, 8), s.take("three recursive products + Θ(n) work")])
s.step("Let us check one recursive call: 12 times 56. Split into 1, 2 and 5, 6.", hide("kc") + show("inr") + [hl("inr[0]")])
s.step("a c is 1 times 5, 5. b d is 2 times 6, 12.", [hl("inr[1]")])
s.step("a plus b is 3, c plus d is 11. 3 has a single digit, so this one is multiplied directly: 33.", [hl("inr[2]")])
s.step("Middle term: 33 minus 5 minus 12, 16. Result: 500 plus 160 plus 12, 672: the same a c we used above.", [hl("inr[3..=4]"), mk("inr[4][2]", 0.5)])

s.scene("time")
s.step("Stage 6: count the calls level by level. Each call makes 3 smaller calls instead of 4: level 1 has 3 calls, level 2 has 9.", [s.head("Stage 6 of 7: the running time"), s.untake()] + hide("inr") + show("lvl") + [hl("lvl[0..=2]")])
s.step("At level k there are 3 to the k calls, on numbers of n over 2 to the k digits. The school-style split would have 4 to the k.", [hl("lvl[3]")])
s.step("At the bottom, log n levels down, single digits: n squared products the slow way, but only 3 to the log n, which equals n to the log 2 of 3, with Karatsuba.", [hl("lvl[4]")])
s.step("The same answer from the recurrence: three half-size problems plus linear work, T of n equals 3 T of n over 2, plus n.", hide("lvl") + show("rt") + [hl("rt[0]")])
s.step("Master method: a is 3, b is 2. n to the log base 2 of 3 is about n to the 1.585, which grows faster than the linear f of n.", [rv("rt[1]"), hl("rt[1]")])
s.step("So case 1: the leaves dominate, and T of n is Theta of n to the log 2 of 3, about n to the 1.585.", [rv("rt[2]"), hl("rt[2]")])
s.step("For 1024 digits: 10 levels of splitting, 3 to the 10, about 59 thousand digit products, against over a million for the school method.", [rv("rt[3]"), hl("rt[3]")])
s.step("For small numbers the school method still wins, so real libraries switch over below a threshold. And faster methods followed: Toom-Cook, the FFT, and in 2019, n log n.", [rv("rt[4]"), hl("rt[4]"), s.take("Θ(n^log₂3) ≈ Θ(n^1.585)")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("rt") + show("q") + [hl("q[0]")])
s.step("Find the split and the three products, the middle term and the result, then compare the counts for 64 digits. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: a is 31, b is 41; c is 59, d is 26. a c is 31 times 59, 1829. b d is 41 times 26, 1066.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("a plus b is 72, c plus d is 85: their product is 6120.", [hl("qa[1]")])
s.step("b: the middle term is 6120 minus 1829 minus 1066: 3225.", [hl("qa[2]")])
s.step("Assemble: 18,290,000 plus 322,500 plus 1066: 18,613,566.", [hl("qa[3]")])
s.step("c: 64 is 2 to the 6, so 6 levels of splitting. Karatsuba makes 3 to the 6, 729 single-digit products; the school method 4 to the 6, 4096.", [hl("qa[4]"), mk("qa[4][2]", 0.5)])
s.step("The usual slip: shifting the middle term by 2 m instead of m. a c moves 2 m places, the middle term m places, and b d stays put.", [s.take("ac · 10^2m  +  middle · 10^m  +  bd")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Splitting numbers in half naively needs four half-size products: no better than school. Karatsuba gets the middle term from one extra product: three in all.", [hl("stages[0..=3]")])
s.step("Recursively, T of n equals 3 T of n over 2, plus n: Theta of n to the 1.585.", [hl("stages[4..=5]")])
s.step("Next video: the same trick for matrices. Strassen's algorithm multiplies two matrices with 7 products instead of 8.", [mk("stages[0..=6]"), s.take("Next: Strassen's matrix multiplication")])

s.save("/home/claude/playlist/dsa3/d3v3.json")

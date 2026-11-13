"""DSA Module 3, video 5: the fake coin problem (lab)."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *
from coin import halves, thirds, worst

F8, H8 = halves(8, 6); assert F8 == 6 and len(H8) == 3
F9, T9 = thirds(9, 7); assert F9 == 7 and len(T9) == 2
F16, H16 = halves(16, 11); F16t, T16 = thirds(16, 11); assert F16 == F16t == 11 and len(H16) == 4 and len(T16) == 3
assert worst(halves, 7) == 2 and halves(7, 7)[1][-1][3] == "balance"
for n in (8, 9, 16, 27, 100, 1000):
    assert worst(halves, n) == math.floor(math.log2(n)) and worst(thirds, n) == math.ceil(math.log(n, 3) - 1e-9)
assert worst(halves, 100) == 6 and worst(thirds, 100) == 5 and worst(halves, 1000) == 9 and worst(thirds, 1000) == 7

rng = lambda g: f"c{g[0]}" if len(g) == 1 else (f"c{g[0]}–c{g[-1]}" if g else "none")
s = Script("The fake coin problem")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The problem"],
    [2, "Halving: weigh one half against the other"],
    [3, "Eight coins, traced"],
    [4, "The algorithm and its recurrence"],
    [5, "Thirds: three outcomes, three groups"],
    [6, "How many weighings: log₂ n against log₃ n"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["the fake coin problem", ""], "rows": [
    ["given", "n identical-looking coins; exactly one is fake, and lighter"],
    ["tool", "a balance scale: left lighter, right lighter, or balance"],
    ["goal", "find the fake with as few weighings as possible, in the worst case"],
    ["one by one", "compare pairs: up to n/2 weighings"],
    ["the lab task", "solve it by divide and conquer"]]})
s.obj({"id": "coins", "type": "array", "region": "center", "values": [f"c{i}" for i in range(1, 9)]})
s.obj({"id": "wt", "type": "table", "region": "center", "columns": ["weighing", "left pan", "right pan", "aside", "result"],
       "rows": [[str(k + 1), "", "", "", ""] for k in range(3)]})
s.obj({"id": "fc", "type": "code", "region": "center", "language": "text", "lines": [
    "FAKE-COIN(C, lo, hi)        // C[lo .. hi] holds exactly one lighter coin",
    "    if lo == hi:  return lo",
    "    h = ⌊(hi − lo + 1) / 2⌋",
    "    w = WEIGH(C[lo .. lo+h−1],  C[lo+h .. lo+2h−1])",
    "    if w = left lighter:   return FAKE-COIN(C, lo, lo+h−1)",
    "    if w = right lighter:  return FAKE-COIN(C, lo+h, lo+2h−1)",
    "    return hi               // balance: n was odd, the coin set aside is fake",
    "",
    "W(n) = W(⌊n/2⌋) + 1,  W(1) = 0   ⇒   W(n) = ⌊log₂ n⌋ weighings"]})
s.obj({"id": "c9", "type": "array", "region": "center", "values": [f"c{i}" for i in range(1, 10)]})
s.obj({"id": "w9", "type": "table", "region": "center", "columns": ["weighing", "left pan", "right pan", "aside", "result"],
       "rows": [[str(k + 1), "", "", "", ""] for k in range(2)]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["n coins", "halving: ⌊log₂ n⌋", "thirds: ⌈log₃ n⌉"], "rows": [
    ["8", "3", "2"], ["9", "3", "2"], ["27", "4", "3"], ["100", "6", "5"], ["1000", "9", "7"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["16 coins c1 to c16; c11 is the lighter fake"],
    ["a) show every weighing of the halving method"],
    ["b) show every weighing of the thirds method (groups as equal as possible)"],
    ["c) worst-case weighings for 100 coins, by each method"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "weighings", "found"], "rows": [
    ["a)", "c1–c8 | c9–c16: right lighter · c9–c12 | c13–c16: left lighter", ""],
    ["a)", "c9–c10 | c11–c12: right lighter · c11 | c12: left lighter", "c11, 4 weighings"],
    ["b)", "c1–c6 | c7–c12, aside c13–c16: right lighter · c7–c8 | c9–c10: balance", ""],
    ["b)", "c11 | c12: left lighter", "c11, 3 weighings"],
    ["c)", "⌊log₂ 100⌋ = 6;  3⁴ = 81 < 100 ≤ 243 = 3⁵", "6 against 5"]]})

s.scene("intro")
s.step("Here is a puzzle from the lab. You have a pile of coins that all look the same, but one is a fake, slightly lighter than the rest. You have a balance scale. How few weighings can you get away with? Divide and conquer gives the answer.", [s.head("The fake coin problem")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem, the halving method, a trace with eight coins, and the algorithm with its recurrence.", [hl("stages[0..=3]")])
s.step("Then a better split into thirds, the number of weighings for each, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: n coins, exactly one fake, and the fake is lighter.", [s.head("Stage 1 of 7: the problem")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("A balance scale compares two groups. It has three outcomes: the left pan is lighter, the right pan is lighter, or they balance.", [hl("pb[1]")])
s.step("We want the fewest weighings in the worst case, whichever coin turns out to be fake.", [hl("pb[2]")])
s.step("Weighing coins in pairs might need n over 2 weighings: 500 for a thousand coins. Divide and conquer does far better.", [hl("pb[3..=4]"), s.take("count weighings, worst case")])

s.scene("half")
s.step("Stage 2: the halving method. Put half the coins on each pan. The fake is on the lighter side, so the other half can be thrown away.", [s.head("Stage 2 of 7: halving"), s.untake()] + hide("pb") + show("coins") + [hl("coins[0..=3]"), hl("coins[4..=7]", 0.5)])
s.step("If n is odd, set one coin aside first. If the pans balance, the coin set aside is the fake.", [s.take("one weighing halves the suspects")])
s.step("For example, with seven coins: c1 to c3 against c4 to c6, with c7 aside. If they balance, c7 is the fake after a single weighing. If not, three suspects remain, and one more weighing of one coin against one, with one aside, settles it.", [dim("coins[7]"), hl("coins[0..=2]"), hl("coins[3..=5]", 0.3), hl("coins[6]", 0.6)])

s.scene("trace")
s.step("Stage 3: eight coins, c1 to c8. Secretly, c6 is the fake.", [s.head("Stage 3 of 7: eight coins"), s.untake(), rs("coins"), show("wt")])
def wrow(tb, k, w, d0=0.0):
    L, R, A, res, _ = w
    return [hl(f"{tb}[{k}]"), st(f"{tb}[{k}][1]", rng(L), d0), st(f"{tb}[{k}][2]", rng(R), d0 + 0.1), st(f"{tb}[{k}][3]", rng(A), d0 + 0.2), st(f"{tb}[{k}][4]", res, d0 + 0.4)]
def dims(arr, keep, n, d=0.6):
    return [dim(f"{arr}[{i - 1}]", d) for i in range(1, n + 1) if not (keep[0] <= i <= keep[1])]
s.step("Weighing 1: c1 to c4 against c5 to c8. The right pan is lighter, so the fake is among c5 to c8. Four coins are cleared.", wrow("wt", 0, H8[0]) + dims("coins", H8[0][4], 8))
s.step("Weighing 2: c5, c6 against c7, c8. Now the left is lighter: the fake is c5 or c6.", wrow("wt", 1, H8[1]) + [dim("coins[6]", 0.6), dim("coins[7]", 0.6)])
s.step("Weighing 3: c5 against c6. The right is lighter: c6 is the fake. Three weighings for 8 coins: log 2 of 8.", wrow("wt", 2, H8[2]) + [dim("coins[4]", 0.6), mk("coins[5]", 0.8), s.take("8 → 4 → 2 → 1: three weighings")])

s.scene("algo")
s.step("Stage 4: as a recursive algorithm. One coin left: it is the fake.", [s.head("Stage 4 of 7: the algorithm"), s.untake()] + hide("coins", "wt") + show("fc") + [ml("fc", 1, 2)])
s.step("Otherwise, take h, half the count rounded down, and weigh the first h coins against the next h.", [ml("fc", 3, 4)])
s.step("Recurse into whichever pan is lighter. If they balance, there must have been an odd coin set aside, and it is the fake.", [ml("fc", 5, 7)])
s.step("Each weighing at least halves the problem, so W of n equals W of n over 2 rounded down, plus 1. That gives the floor of log base 2 of n weighings. Only one subproblem is solved, so this is also called decrease and conquer.", [ml("fc", 9, 9), s.take("W(n) = ⌊log₂ n⌋")])
s.step("Unroll it: W of n is W of n over 2 plus 1, which is W of n over 4 plus 2, and after k halvings, W of n over 2 to the k, plus k. One coin remains when 2 to the k reaches n: k is log 2 of n.", [ml("fc", 9, 9)])
s.step("The running time counts weighings, but each weighing also puts coins on the scale. Adding up the pans, n over 2 plus n over 4 and so on, that is fewer than n coin placements: linear work, logarithmic weighings.", [ml("fc", 3, 4)])

s.scene("third")
s.step("Stage 5: we can do better. The scale has three outcomes, but halving only uses two of them: balance happens only for the odd coin.", [s.head("Stage 5 of 7: thirds"), s.untake()] + hide("fc") + show("c9", "w9"))
s.step("So split into three groups: two equal groups on the pans, one aside. Each outcome points to one group: left lighter, right lighter, or balance, meaning the fake is in the group aside.", [hl("c9[0..=2]"), hl("c9[3..=5]", 0.4), hl("c9[6..=8]", 0.8)])
s.step("Nine coins, c7 fake. Weighing 1: c1 to c3 against c4 to c6. They balance, so the fake is among c7, c8, c9.", wrow("w9", 0, T9[0]) + dims("c9", T9[0][4], 9))
s.step("Weighing 2: c7 against c8, with c9 aside. The left is lighter: c7 is the fake. Just two weighings for nine coins.", wrow("w9", 1, T9[1]) + [dim("c9[7]", 0.6), dim("c9[8]", 0.6), mk("c9[6]", 0.8)])
s.step("Each weighing now keeps only a third: W of n equals W of n over 3, plus 1, so about log base 3 of n weighings, rounded up.", [s.take("W(n) = ⌈log₃ n⌉")])
s.step("The algorithm changes in one line: groups of the ceiling of n over 3 on each pan, the rest aside. Recurse into the lighter pan, or into the group aside on a balance.", [s.take("W(n) = ⌈log₃ n⌉")])

s.scene("count")
s.step("Stage 6: side by side. With 8 or 9 coins, halving needs 3 weighings, thirds only 2.", [s.head("Stage 6 of 7: how many weighings"), s.untake()] + hide("c9", "w9") + show("cmp") + [hl("cmp[0..=1]")])
s.step("27 coins: 4 against 3. 100 coins: 6 against 5. A thousand: 9 against 7.", [hl("cmp[2..=4]")])
s.step("Both are logarithmic, so even a million coins need only 20 or 13 weighings. The lesson: when a test has three outcomes, divide into three.", [s.take("use every outcome of the test")])
s.step("A harder version: if you do not know whether the fake is heavier or lighter, 12 coins can still be solved in 3 weighings, but it needs a cleverer plan. That is a classic puzzle worth trying.", [hl("cmp[4]")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("cmp") + show("q") + [hl("q[0]")])
s.step("Trace both methods on 16 coins with c11 fake, then count the worst case for 100 coins. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: c1 to c8 against c9 to c16: the right is lighter. Then c9 to c12 against c13 to c16: the left is lighter.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("c9, c10 against c11, c12: the right is lighter. c11 against c12: the left is lighter. c11, in 4 weighings.", [hl("qa[1]")])
s.step("b: groups of 6, 6 and 4. c1 to c6 against c7 to c12: the right is lighter. Then c7, c8 against c9, c10, with c11, c12 aside: balance.", [hl("qa[2]")])
s.step("c11 against c12: the left is lighter. c11, in 3 weighings.", [hl("qa[3]")])
s.step("c: halving needs the floor of log 2 of 100: 6. Thirds: 3 to the 4 is 81, less than 100, so 4 is not enough; 5 weighings.", [hl("qa[4]"), mk("qa[4][2]", 0.5)])
s.step("The usual slip: with thirds, the two groups on the pans must be the same size. Otherwise a lighter pan tells you nothing.", [s.take("equal groups on the pans, always")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Weighing half against half finds the fake in floor log 2 of n weighings, keeping one half each time.", [hl("stages[0..=3]")])
s.step("Splitting into thirds uses all three outcomes of the scale: the ceiling of log 3 of n weighings.", [hl("stages[4..=5]")])
s.step("That completes divide and conquer. Next video: the greedy method, starting with job sequencing with deadlines.", [mk("stages[0..=6]"), s.take("Next: greedy job sequencing")])

s.save("/home/claude/playlist/dsa3/d3v5.json")

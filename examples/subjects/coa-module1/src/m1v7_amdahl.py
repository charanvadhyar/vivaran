"""Module 1, video 7: Amdahl's law: the formula, the limit, processors, edge cases, inverse problems."""
import sys
sys.path.insert(0, ".")
from common import Script

A = lambda *parts: 1 / (1 - sum(f for f, _ in parts) + sum(f / s for f, s in parts))
r = lambda x, n=2: round(x, n)
assert r(A((0.4, 10)), 4) == 1.5625 and r(1 / 0.6) == 1.67
assert [r(1 / (1 - f)) for f in (0.5, 0.9, 0.95, 0.99)] == [2, 10, 20, 100]
assert r(A((0.95, 8))) == 5.93 and r(A((0.95, 100)), 1) == 16.8 and r(A((0.95, 8)) / 8 * 100) == 74.07
assert r(A((0.95, 100)) / 100 * 100) == 16.81
f_orig = 5 / 5.5; assert r(f_orig, 3) == 0.909 and r(A((f_orig, 10)), 2) == 5.5
assert r(A((0.2, 10)), 2) == 1.22 and r(A((0.5, 1.6)), 2) == 1.23
assert r(A((0.3, 3), (0.2, 4)), 2) == 1.54
assert r(0.8 / (1 / 4 - 0.2), 6) == 16
assert r(A((0.4, 2)), 2) == 1.25 and r(A((0.2, 5)), 2) == 1.19 and r(A((0.4, 2), (0.2, 5)), 4) == 1.5625
assert r(A((0.9, 16)), 1) == 6.4 and r(1 / 0.1) == 10
assert r(0.05 + 0.95 * 100, 2) == 95.05

s = Script("Amdahl's law: how much one improvement can buy")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The law, from the time it saves"],
    [2, "The limit: speeding up a part forever"],
    [3, "Amdahl for N processors"],
    [4, "Edge case: the fraction must be of the old time"],
    [5, "Choosing between improvements, and combining them"],
    [6, "Working backwards: what speedup do I need?"],
    [7, "Exam question"]]})
s.obj({"id": "bar", "type": "timeline", "region": "center", "lanes": ["old run", "new run"], "end": 10, "unit": "seconds", "now": 0, "blocks": []})
s.obj({"id": "law", "type": "math", "region": "center", "lines": [
    "T_\"new\" = T_\"old\" times ((1 - f) + f / s)",
    "\"speedup\" = T_\"old\" / T_\"new\" = 1 / ((1 - f) + f / s)",
    "f = 0.4, s = 10: quad 1 / (0.6 + 0.04) = 1 / 0.64 approx 1.56"]})
s.obj({"id": "lim", "type": "table", "region": "right", "columns": ["fraction improved f", "best possible speedup 1 ÷ (1 − f)"], "rows": [
    ["0.4", "1.67"], ["0.5", "2"], ["0.9", "10"], ["0.95", "20"], ["0.99", "100"]]})
s.obj({"id": "limf", "type": "math", "region": "left", "lines": [
    "s -> infinity: quad f / s -> 0",
    "\"speedup\" -> 1 / (1 - f)",
    "f = 0.4: quad 1 / 0.6 approx 1.67"]})
s.obj({"id": "procf", "type": "math", "region": "center", "lines": [
    "\"speedup\"(N) = 1 / ((1 - p) + p / N)",
    "\"efficiency\" = \"speedup\" / N"]})
s.obj({"id": "proc", "type": "table", "region": "center", "columns": ["processors N", "speedup, p = 0.95", "efficiency"], "rows": [
    ["8", "", ""], ["100", "", ""], ["infinitely many", "", ""]]})
s.obj({"id": "gus", "type": "table", "region": "center", "columns": ["", "Amdahl", "Gustafson"], "rows": [
    ["problem size", "fixed", "grows with N"],
    ["speedup", "1 ÷ ((1 − p) + p ÷ N)", "(1 − p) + p × N"],
    ["p = 0.95, N = 100", "16.8", "95.05"]]})
s.obj({"id": "after", "type": "timeline", "region": "center", "lanes": ["new run", "old run"], "end": 6, "unit": "seconds", "now": 0, "blocks": []})
s.obj({"id": "afterm", "type": "math", "region": "center", "lines": [
    "\"old time\" = 0.5 + 0.5 times 10 = 5.5 quad => quad \"speedup\" = 5.5 / 1 = 5.5",
    "f = 5 / 5.5 approx 0.909 quad \"(not 0.5)\""]})
s.obj({"id": "pick", "type": "table", "region": "center", "columns": ["option", "f", "s", "overall speedup"], "rows": [
    ["square root unit", "0.2", "10", ""], ["whole FP unit", "0.5", "1.6", ""]]})
s.obj({"id": "multi", "type": "math", "region": "center", "lines": [
    "\"speedup\" = 1 / ((1 - f_1 - f_2) + f_1 / s_1 + f_2 / s_2)",
    "f_1 = 0.3, s_1 = 3, quad f_2 = 0.2, s_2 = 4",
    "1 / (0.5 + 0.1 + 0.05) = 1 / 0.65 approx 1.54"]})
s.obj({"id": "inv", "type": "math", "region": "center", "lines": [
    "f = 0.8, \"want overall\" 4: quad 1 / 4 = 0.2 + 0.8 / s",
    "0.8 / s = 0.05 quad => quad s = 16",
    "\"want overall\" 5: quad 1 / 5 = 0.2 + 0.8 / s quad => quad 0.8 / s = 0",
    "\"impossible: the limit is\" 1 / (1 - 0.8) = 5"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["A program spends 40% of its time on memory and 20% on floating point. Find:"], "rows": [
    ["a) speedup if memory becomes 2 times faster"],
    ["b) speedup if floating point becomes 5 times faster"],
    ["c) speedup with both"],
    ["d) 90% of it runs in parallel on 16 cores: speedup, and the limit?"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 1 / (0.6 + 0.4 / 2) = 1 / 0.8 = 1.25",
    "\"b)\" quad 1 / (0.8 + 0.2 / 5) = 1 / 0.84 approx 1.19",
    "\"c)\" quad 1 / (0.4 + 0.2 + 0.04) = 1 / 0.64 approx 1.56",
    "\"d)\" quad 1 / (0.1 + 0.9 / 16) approx 6.4, quad \"limit\" 1 / 0.1 = 10"]})


def blk(t, id, lane, a, b, label, delay=0):
    return {"action": "add_block", "target": t, "id": id, "lane": lane, "start": a, "end": b, "label": label, **({"delay": delay} if delay else {})}


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("You make one part of a program ten times faster. Does the program get ten times faster? Almost never. Amdahl's law tells you by how much.", [s.head("Amdahl's law")])
s.step("Here are the seven stages.", [{"action": "show", "target": "stages"}])
s.step("The law itself, its limit, and its version for many processors.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Then the edge case that costs the most marks: which time the fraction is measured on.", [{"action": "highlight", "target": "stages[3]"}])
s.step("Then choosing and combining improvements, working backwards, and an exam question.", [{"action": "highlight", "target": "stages[4..=6]"}])

# ---------------------------------------------------------------- law
s.scene("law")
s.step("Stage 1: a program takes 10 seconds. 40 percent of that time, 4 seconds, is spent in a part we can speed up.", [s.head("Stage 1 of 7: the law"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "bar"},
       blk("bar", "o1", "old run", 0, 6, "6 s: not improved"), blk("bar", "o2", "old run", 6, 10, "4 s: f = 0.4", 0.4)])
s.step("Make that part 10 times faster. Its 4 seconds shrink to 0.4 seconds.", [blk("bar", "n2", "new run", 6, 6.4, "0.4 s", 0.4)])
s.step("But the other 6 seconds are untouched. The new run takes 6.4 seconds.", [blk("bar", "n1", "new run", 0, 6, "6 s: unchanged")])
s.step("The part you did not improve now dominates: 6 of the 6.4 seconds.")
s.step("In general, the new time is the old time times one minus f, plus f over s. f is the fraction of the time that is improved, and s is how much faster that part gets.", [{"action": "hide", "target": "bar"}, {"action": "show", "target": "law"}])
s.step("Speedup is old time over new time, so the old time cancels: one over one minus f, plus f over s.", [{"action": "reveal", "target": "law[1]"}, {"action": "highlight", "target": "law[1]"}])
s.step("Here: one over 0.6 plus 0.04, which is 1 over 0.64, about 1.56. Ten times faster in one part bought only 1.56 overall.", [{"action": "reveal", "target": "law[2]"}, {"action": "highlight", "target": "law[2]"}])

# ---------------------------------------------------------------- limit
s.scene("limit")
s.step("Stage 2: what if we made that part infinitely fast?", [s.head("Stage 2 of 7: the limit"), {"action": "hide", "target": "law"}, {"action": "show", "target": "limf"}])
s.step("As s goes to infinity, f over s goes to zero, and the speedup approaches one over one minus f.", [{"action": "reveal", "target": "limf[1]"}, {"action": "highlight", "target": "limf[1]"}])
s.step("With f equal to 0.4, the best possible speedup is 1 over 0.6, about 1.67. However fast that part becomes, you never beat 1.67.", [{"action": "reveal", "target": "limf[2]"}, {"action": "highlight", "target": "limf[2]"}])
s.step("The table shows how harsh this is. Improve half the time, and the best you can ever get is 2.", [{"action": "show", "target": "lim"}, {"action": "highlight", "target": "lim[1]"}])
s.step("Even with 95 percent improved, the ceiling is 20. The last 5 percent decides it.", [{"action": "highlight", "target": "lim[3]"}])
s.step("So the rule is: make the common case fast. The bigger f is, the more an improvement can buy.", [s.take("limit: speedup < 1 ÷ (1 − f) · make the common case fast")])

# ---------------------------------------------------------------- processors
s.scene("proc")
s.step("Stage 3: the same law for parallel processors. Let p be the fraction of the time that can run in parallel, spread over N processors.", [s.head("Stage 3 of 7: N processors"), {"action": "hide", "target": "limf"}, {"action": "hide", "target": "lim"}, s.untake(), {"action": "show", "target": "procf"}])
s.step("Then s is just N: speedup equals one over one minus p, plus p over N. And efficiency is speedup divided by N, how well each processor is used.", [{"action": "reveal", "target": "procf[1]"}, {"action": "highlight", "target": "procf[1]"}])
s.step("Take p equal to 0.95. With 8 processors: one over 0.05 plus 0.11875, about 5.93. Efficiency 74 percent.", [{"action": "hide", "target": "procf"}, {"action": "show", "target": "proc"}, {"action": "highlight", "target": "proc[0]"},
       {"action": "set", "target": "proc[0][1]", "value": "5.93", "delay": 0.4}, {"action": "set", "target": "proc[0][2]", "value": "74%", "delay": 0.8}])
s.step("With 100 processors: one over 0.05 plus 0.0095, about 16.8. Efficiency falls to under 17 percent.", [{"action": "highlight", "target": "proc[1]"},
       {"action": "set", "target": "proc[1][1]", "value": "16.8", "delay": 0.4}, {"action": "set", "target": "proc[1][2]", "value": "17%", "delay": 0.8}])
s.step("And with infinitely many, the limit is one over 0.05: 20, no matter how many processors you buy.", [{"action": "highlight", "target": "proc[2]"},
       {"action": "set", "target": "proc[2][1]", "value": "20", "delay": 0.4}, {"action": "set", "target": "proc[2][2]", "value": "→ 0", "delay": 0.8}])
s.step("Amdahl assumes the problem size stays fixed. Gustafson's law assumes it grows with the machine, so the parallel part grows too.", [{"action": "hide", "target": "proc"}, {"action": "show", "target": "gus"}, {"action": "highlight", "target": "gus[0]"}])
s.step("His scaled speedup is one minus p, plus p times N. With p 0.95 and 100 processors, that is 95, against Amdahl's 16.8. Use Amdahl unless the question says the problem is scaled up.", [{"action": "highlight", "target": "gus[1..=2]"}, s.take("fixed size: Amdahl · scaled size: Gustafson")])

# ---------------------------------------------------------------- old time
s.scene("old")
s.step("Stage 4, the edge case. A question says: after the enhancement, the enhanced mode is used 50 percent of the time, and it is 10 times faster. What is the speedup?", [s.head("Stage 4 of 7: which time is f measured on?"), {"action": "hide", "target": "gus"}, s.untake(), {"action": "show", "target": "after"}])
s.step("The tempting answer puts f equal to 0.5 in the formula. That is wrong: f must be a fraction of the old time, before the enhancement.", [blk("after", "a1", "new run", 0, 0.5, "0.5 normal"), blk("after", "a2", "new run", 0.5, 1, "0.5 enhanced", 0.3)])
s.step("Work from the new run. Say it takes 1 unit: 0.5 normal, and 0.5 in enhanced mode.")
s.step("Without the enhancement, that enhanced half would have taken 10 times longer: 5 units. So the old run took 0.5 plus 5, which is 5.5.", [blk("after", "b1", "old run", 0, 0.5, "0.5"), blk("after", "b2", "old run", 0.5, 5.5, "0.5 × 10 = 5", 0.3)])
s.step("The speedup is 5.5 over 1, which is 5.5. In terms of the old time, f was 5 over 5.5, about 0.909, not 0.5.", [{"action": "hide", "target": "after"}, {"action": "show", "target": "afterm"}, {"action": "reveal", "target": "afterm[1]", "delay": 0.5}, {"action": "highlight", "target": "afterm[1]", "delay": 0.5}])
s.step("Check: one over 0.091 plus 0.0909 gives 5.5. Same answer, once f is measured on the old time.", [s.take("f is always a fraction of the OLD time")])

# ---------------------------------------------------------------- choose and combine
s.scene("choose")
s.step("Stage 5: you can afford one improvement. Square root takes 20 percent of the time, and a new unit makes it 10 times faster. All floating point takes 50 percent, and a new unit makes it 1.6 times faster.", [s.head("Stage 5 of 7: choose and combine"), {"action": "hide", "target": "afterm"}, s.untake(), {"action": "show", "target": "pick"}])
s.step("Square root: one over 0.8 plus 0.02, about 1.22.", [{"action": "highlight", "target": "pick[0]"}, {"action": "set", "target": "pick[0][3]", "value": "1 ÷ 0.82 ≈ 1.22", "delay": 0.4}])
s.step("All floating point: one over 0.5 plus 0.3125, about 1.23.", [{"action": "highlight", "target": "pick[1]"}, {"action": "set", "target": "pick[1][3]", "value": "1 ÷ 0.8125 ≈ 1.23", "delay": 0.4}])
s.step("The modest improvement to the common case wins, even though 1.6 sounds much smaller than 10.", [{"action": "mark", "target": "pick[1]"}])
s.step("To combine two improvements on separate parts of the program, keep the unimproved part, and divide each improved part by its own speedup.", [{"action": "hide", "target": "pick"}, {"action": "show", "target": "multi"}])
s.step("30 percent made 3 times faster, and 20 percent made 4 times faster.", [{"action": "reveal", "target": "multi[1]"}, {"action": "highlight", "target": "multi[1]"}])
s.step("One over 0.5 plus 0.1 plus 0.05, which is 1 over 0.65, about 1.54. Edge case: this only works when the two parts do not overlap. Never multiply the two separate speedups together.", [{"action": "reveal", "target": "multi[2]"}, {"action": "highlight", "target": "multi[2]"}, s.take("separate parts: one formula, never multiply the speedups")])

# ---------------------------------------------------------------- inverse
s.scene("inverse")
s.step("Stage 6: working backwards. 80 percent of the time can be improved, and we want the whole program 4 times faster. How fast must that part become?", [s.head("Stage 6 of 7: working backwards"), {"action": "hide", "target": "multi"}, s.untake(), {"action": "show", "target": "inv"}])
s.step("Set the formula equal to 4: one quarter equals 0.2 plus 0.8 over s.", [{"action": "highlight", "target": "inv[0]"}])
s.step("So 0.8 over s is 0.05, and s is 16. That part must become 16 times faster.", [{"action": "reveal", "target": "inv[1]"}, {"action": "highlight", "target": "inv[1]"}])
s.step("Now ask for 5 times overall. One fifth is 0.2, so 0.8 over s must be zero.", [{"action": "reveal", "target": "inv[2]"}, {"action": "highlight", "target": "inv[2]"}])
s.step("That needs an infinitely fast part. 5 is exactly the limit, one over 0.2, so it can never be reached. Anything above 5 is impossible too.", [{"action": "reveal", "target": "inv[3]"}, {"action": "highlight", "target": "inv[3]"}, s.take("a target ≥ 1 ÷ (1 − f) is impossible")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), {"action": "hide", "target": "inv"}, s.untake(), {"action": "show", "target": "q"}])
s.step("A program spends 40 percent of its time on memory and 20 percent on floating point. Find the speedup from a 2 times faster memory, from 5 times faster floating point, and from both.", [{"action": "highlight", "target": "q[0..=2]"}])
s.step("Then, separately: 90 percent of it runs in parallel on 16 cores. Find the speedup and its limit. Pause and work it out.", [{"action": "highlight", "target": "q[3]"}])
s.step("a: one over 0.6 plus 0.2, which is 1 over 0.8: 1.25.", [{"action": "hide", "target": "q"}, {"action": "show", "target": "qa"}, {"action": "highlight", "target": "qa[0]"}])
s.step("b: one over 0.8 plus 0.04, which is 1 over 0.84: about 1.19. The bigger part gave the bigger win, even with the smaller speedup.", [{"action": "reveal", "target": "qa[1]"}, {"action": "highlight", "target": "qa[1]"}])
s.step("c: the parts do not overlap, so one formula: one over 0.4 plus 0.2 plus 0.04, which is 1 over 0.64, about 1.56. Not 1.25 times 1.19.", [{"action": "reveal", "target": "qa[2]"}, {"action": "highlight", "target": "qa[2]"}])
s.step("d: one over 0.1 plus 0.9 over 16, about 6.4. And however many cores, the limit is one over 0.1: 10.", [{"action": "reveal", "target": "qa[3]"}, {"action": "highlight", "target": "qa[3]"}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qa"}, {"action": "show", "target": "stages"}])
s.step("Speedup is one over one minus f, plus f over s, and it can never reach one over one minus f.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Measure f on the old time, put separate improvements into one formula, and check a target against the limit before solving for it.", [{"action": "highlight", "target": "stages[3..=5]"}])
s.step("Next video: pipeline speedup for real, with unequal stage delays and latch overhead.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Next: pipeline speedup with stage delays and latches")])

s.save("./m1v7.json")

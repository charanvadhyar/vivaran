"""DSA Module 4, video 4: subset sum by backtracking."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa4")
from common import Script
from h import *
from bt import sum_of_sub

S1, L1 = sum_of_sub([3, 5, 6, 7], 15); assert S1 == [[3, 5, 7]]
assert [x[0] for x in L1] == ["include", "include", "include-pruned", "exclude", "found", "exclude-pruned", "exclude", "include-pruned", "exclude-pruned", "exclude", "include", "include-pruned", "exclude-pruned", "exclude-pruned"]
SE, LE = sum_of_sub([5, 10, 12, 13, 15, 18], 30); assert SE == [[5, 10, 15], [5, 12, 13], [12, 18]]
assert 2 ** 4 == 16 and 2 ** 6 == 64 and 2 ** 40 > 10 ** 12 and 3 + 5 + 6 + 7 == 21

s = Script("Backtracking: subset sum")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The subset sum problem"],
    [2, "The state-space tree: take it or leave it"],
    [3, "Two bounding functions"],
    [4, "Tracing {3, 5, 6, 7}, target 15"],
    [5, "The algorithm"],
    [6, "Cost, and the dynamic-programming alternative"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["subset sum", ""], "rows": [
    ["given", "positive weights w₁ … wₙ and a target m"],
    ["find", "every subset whose weights add up to exactly m"],
    ["example", "{3, 5, 6, 7}, m = 15:  3 + 5 + 7 = 15"],
    ["brute force", "2ⁿ subsets: 2⁴⁰ is over a million million"],
    ["uses", "budgets, cutting stock, loading a truck exactly"]]})
s.obj({"id": "tr", "type": "table", "region": "center", "columns": ["state-space tree", ""], "rows": [
    ["xᵢ = 1 or 0", "take weight i, or leave it"],
    ["level i", "decides xᵢ: a binary tree with 2ⁿ leaves"],
    ["s", "the sum of the weights taken so far"],
    ["r", "the sum of the weights not yet decided"],
    ["sort the weights ascending", "makes the bounding tests stronger"]]})
s.obj({"id": "bf", "type": "table", "region": "center", "columns": ["bounding functions (weights sorted ascending)", "prune when"], "rows": [
    ["even taking everything left cannot reach m", "s + r < m"],
    ["even the smallest next weight overshoots", "s + wₖ₊₁ > m"],
    ["so a node is worth exploring only if", "s + r ≥ m   and   s + wₖ₊₁ ≤ m"]]})
s.obj({"id": "tt", "type": "table", "region": "center", "columns": ["decision", "s", "check", "outcome"], "rows": [["", "", "", ""] for _ in range(9)]})
s.obj({"id": "sc", "type": "code", "region": "center", "language": "text", "lines": [
    "SUMOFSUB(s, k, r)       // w[1..n] ascending;  s = taken so far;  r = w[k] + … + w[n]",
    "    x[k] = 1",
    "    if s + w[k] == m:  print x[1 .. k]                          // found",
    "    elseif s + w[k] + w[k+1] ≤ m:  SUMOFSUB(s + w[k], k + 1, r − w[k])",
    "    if s + r − w[k] ≥ m  and  s + w[k+1] ≤ m",
    "        x[k] = 0",
    "        SUMOFSUB(s, k + 1, r − w[k])",
    "",
    "first call:  SUMOFSUB(0, 1, w[1] + … + w[n])"]})
s.obj({"id": "cost", "type": "table", "region": "center", "columns": ["cost", ""], "rows": [
    ["worst case", "still O(2ⁿ) nodes"],
    ["in practice", "the bounds cut most of the tree: our example visits a handful of 31 nodes"],
    ["dynamic programming", "a table of n × m true/false entries: O(n · m)"],
    ["which is better?", "DP when m is small; backtracking when m is huge or all subsets are wanted"],
    ["branch and bound", "the same problem, searched breadth first with bounds: two videos from now"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["w = {5, 10, 12, 13, 15, 18}, m = 30"],
    ["a) every subset that sums to 30, in the order SUMOFSUB finds them"],
    ["b) why is the branch that takes 5, 10 and 12 abandoned at once?"],
    ["c) what happens in the branch that leaves out 5, 10, 12 and 13?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "take 5, 10: 15; 12 and 13 would overshoot with the next; take 15", "{5, 10, 15}"],
    ["a)", "take 5, leave 10: 5 + 12 + 13 = 30", "{5, 12, 13}"],
    ["a)", "leave 5 and 10: 12 + 18 = 30", "{12, 18}"],
    ["b)", "s = 15 + 12 = 27, next weight 13: 40 > 30", "s + w[k+1] > m"],
    ["c)", "0 + 15 + 18 = 33 ≥ 30: explored · take 15: 15 + 18 > 30 · leave 15: 18 < 30", "both pruned: no solution"]]})

s.scene("intro")
s.step("You have a set of numbers and a target. Which of them add up to exactly the target? With 40 numbers there are over a million million subsets to try. Backtracking, with two simple tests, skips almost all of them.", [s.head("Backtracking: subset sum")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem, the take-it-or-leave-it tree, the two bounding functions, and a full trace.", [hl("stages[0..=3]")])
s.step("Then the algorithm, its cost against dynamic programming, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: we are given positive weights and a target m.", [s.head("Stage 1 of 7: subset sum")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("We want every subset of the weights that adds up to exactly m.", [hl("pb[1]")])
s.step("For the weights 3, 5, 6, 7 and target 15: 3 plus 5 plus 7.", [hl("pb[2]")])
s.step("There are 2 to the n subsets: hopeless to list for large n.", [hl("pb[3]")])
s.step("The problem appears in budgeting, cutting material without waste, and loading a container exactly.", [hl("pb[4]"), s.take("find subsets with sum exactly m")])

s.scene("tr")
s.step("Stage 2: for each weight, we decide: x i is 1 to take it, 0 to leave it.", [s.head("Stage 2 of 7: the state-space tree"), s.untake()] + hide("pb") + show("tr") + [hl("tr[0]")])
s.step("Level i of the tree decides weight i. With n weights, a full binary tree with 2 to the n leaves.", [hl("tr[1]")])
s.step("At each node we keep two numbers: s, the sum taken so far, and r, the sum of the weights still to be decided.", [hl("tr[2..=3]")])
s.step("Sorting the weights in ascending order first makes the tests on the next weight as strong as possible.", [hl("tr[4]"), s.take("x[i] = 1 take, 0 leave")])

s.scene("bf")
s.step("Stage 3: two tests prune the tree. First: if even taking every remaining weight cannot reach m, give up. s plus r less than m.", [s.head("Stage 3 of 7: bounding functions"), s.untake()] + hide("tr") + show("bf") + [hl("bf[0]")])
s.step("Second: if adding even the smallest next weight overshoots m, give up. Because the weights are sorted, every later weight would overshoot too.", [hl("bf[1]")])
s.step("A node survives only if s plus r is at least m, and s plus the next weight is at most m.", [hl("bf[2]"), s.take("s + r ≥ m  and  s + w(k+1) ≤ m")])

s.scene("trace")
rows = [("take 3", "3", "3 + 5 ≤ 15", "go on"),
        ("take 5", "8", "8 + 6 ≤ 15", "go on"),
        ("take 6?", "14", "14 + 7 = 21 > 15", "pruned"),
        ("leave 6", "8", "8 + 7 = 15 ≥ 15", "go on"),
        ("take 7", "15", "= m", "solution {3, 5, 7}"),
        ("leave 5", "3", "3 + 6 + 7 = 16 ≥ 15", "go on"),
        ("take or leave 6", "3", "9 + 7 > 15;  3 + 7 < 15", "both pruned"),
        ("leave 3", "0", "5 + 6 + 7 = 18 ≥ 15", "go on"),
        ("take 5;  leave 5", "5;  0", "11 + 7 > 15, 5 + 7 < 15;  6 + 7 < 15", "all pruned: done")]
say = ["Stage 4: weights 3, 5, 6, 7, target 15. Start with s 0 and r 21. Take 3: s is 3. Is 3 plus the next weight, 5, at most 15? Yes: go on.",
       "Take 5: s is 8. 8 plus 6 is 14: fine. Go on.",
       "Take 6? s would be 14, and the next weight, 7, would make 21: overshoot. Taking 6 cannot lead anywhere: prune.",
       "Leave 6 instead. s stays 8, and the only weight left is 7: 8 plus 7 is 15, enough to reach the target. Go on.",
       "Take 7: s is 15, exactly m. A solution: 3, 5, 7.",
       "Backtrack to the decision about 5. Leave 5: s is 3. With 6 and 7 still available, 3 plus 13 is 16: still possible.",
       "Take 6: 9, then 7 would make 16: overshoot. Leave 6: only 3 plus 7, 10: too little. Both pruned.",
       "Backtrack to the top: leave 3. s is 0, and 5, 6, 7 add up to 18: possible. Go on.",
       "Take 5: then 6 overshoots with 7, and leaving 6 leaves only 12. Leave 5: 6 plus 7 is just 13. Everything is pruned. The search ends: one solution."]
for k, row in enumerate(rows):
    acts = ([s.head("Stage 4 of 7: a trace"), s.untake()] + hide("bf") + show("tt")) if k == 0 else []
    acts += [st(f"tt[{k}][{c}]", v, round(0.1 * c, 2)) for c, v in enumerate(row)] + [hl(f"tt[{k}]")]
    if "solution" in row[3]: acts += [mk(f"tt[{k}]", 0.6), s.take("{3, 5, 7}")]
    if "pruned" in row[3]: acts.append(dim(f"tt[{k}]", 0.7))
    s.step(say[k], acts)
s.step("The full tree has 31 nodes. The search examined about a dozen, and found the only answer.", [hl("tt")])

s.scene("algo")
s.step("Stage 5: Horowitz and Sahni's SUMOFSUB. The weights are sorted; s is the sum so far, r the sum of weight k onwards.", [s.head("Stage 5 of 7: the algorithm"), s.untake()] + hide("tt") + show("sc") + [ml("sc", 1, 1)])
s.step("First try taking weight k. If that hits m exactly, print the solution.", [ml("sc", 2, 3)])
s.step("Otherwise recurse with it taken, but only if the next weight would still fit.", [ml("sc", 4, 4)])
s.step("Notice the include test checks s plus w k plus w k plus 1. If even the smallest weight after k cannot be added, taking weight k can only finish if it hits m exactly, which line 3 has already checked.", [ml("sc", 3, 4)])
s.step("Then try leaving weight k out: but only if the rest could still reach m, and the next weight fits.", [ml("sc", 5, 7)])
s.step("The first call has s 0, k 1, and r the total of all weights.", [ml("sc", 9, 9), s.take("try take, then try leave, each only if it can still work")])

s.scene("cost")
s.step("Stage 6: in the worst case, backtracking still visits exponentially many nodes.", [s.head("Stage 6 of 7: cost"), s.untake()] + hide("sc") + show("cost") + [hl("cost[0]")])
s.step("In practice the bounds cut away most of the tree, as in our trace.", [hl("cost[1]")])
s.step("Dynamic programming offers another route: a table of n by m true-or-false entries saying whether the first i weights can make sum j. That takes O of n times m.", [hl("cost[2]")])
s.step("If m is small, the table wins. If m is enormous, or you want all the subsets, backtracking is the better tool.", [hl("cost[3]")])
s.step("For our example, the table would have 4 rows and 15 columns: 60 entries, each one true if the target j can be made from the first i weights. Fast, because 15 is small.", [hl("cost[2]")])
s.step("Two videos from now, branch and bound searches the same tree breadth first, with a queue or a stack, still using bounds.", [hl("cost[4]"), s.take("O(2ⁿ) worst; DP O(n·m) when m is small")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("cost") + show("q") + [hl("q[0]")])
s.step("Find every subset, and explain two of the prunings. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: take 5 and 10: 15. Taking 12 would make 27, and the next weight, 13, overshoots. Leave 12, leave 13, take 15: 30. The first solution: 5, 10, 15.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Back up: take 5, leave 10. Take 12 and 13: 30. The second: 5, 12, 13.", [hl("qa[1]")])
s.step("Leave 5 and 10: take 12 and 18: 30. The third: 12, 18.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("b: with 5, 10 and 12 taken, s is 27, and the smallest weight left is 13: 40 is over 30. So the bound s plus the next weight fails at once.", [hl("qa[3]")])
s.step("c: nothing taken, and 15 and 18 left: together 33, at least 30, so the node is explored. Take 15: 15 plus 18 overshoots. Leave 15: 18 alone falls short. Both children are pruned: no solution there.", [hl("qa[4]")])
s.step("The usual slip: forgetting to sort first. The test on the next weight is only valid when it is the smallest remaining one.", [s.take("sort ascending before you start")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Subset sum searches a take-or-leave tree. Two bounds prune it: the rest must be able to reach m, and the next weight must not overshoot.", [hl("stages[0..=3]")])
s.step("Horowitz's SUMOFSUB applies them before every recursive call. Worst case exponential, but fast in practice; dynamic programming wins when m is small.", [hl("stages[4..=5]")])
s.step("Next video: backtracking with colours. The graph colouring problem.", [mk("stages[0..=6]"), s.take("Next: graph colouring")])

s.save("/home/claude/playlist/dsa4/d4v4.json")

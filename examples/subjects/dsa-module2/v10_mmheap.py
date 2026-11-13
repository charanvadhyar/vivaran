"""DSA Module 2, video 10: min-max heaps."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from mmheap import insert, delete_min, delete_max, check

H0 = [None, 7, 70, 40, 30, 9, 10, 15, 45, 50, 30, 20, 12]
assert check(H0)
A = H0[:]; L5 = insert(A, 5); assert A[1:] == [5, 70, 40, 30, 9, 7, 15, 45, 50, 30, 20, 12, 10] and L5 == [(13, 6), (6, 1)] and check(A)
B = H0[:]; L80 = insert(B, 80); assert B[1:] == [7, 70, 80, 30, 9, 10, 15, 45, 50, 30, 20, 12, 40] and L80 == [(13, 3)] and check(B)
C = H0[:]; x, LD = delete_min(C); assert x == 7 and C[1:] == [9, 70, 40, 30, 12, 10, 15, 45, 50, 30, 20] and check(C)
D = H0[:]; y, LM = delete_max(D); assert y == 70 and D[1:] == [7, 50, 40, 12, 9, 10, 15, 45, 30, 30, 20] and check(D)
E = [None]; elog = []
for k in [10, 20, 30, 5, 25, 40, 15]: elog.append(insert(E, k))
assert E[1:] == [5, 25, 40, 10, 20, 30, 15] and elog == [[], [], [], [(4, 1)], [(5, 2)], [(6, 3)], []]
ez, _ = delete_min(E); assert ez == 5 and E[1:] == [10, 25, 40, 15, 20, 30] and check(E)

def tree(i, vals, region="center"):
    n = len(vals)
    return {"id": i, "type": "diagram", "region": region, "layout": "tree", "shape": "circle", "directed": False,
            "nodes": [{"id": f"h{k}", "label": str(vals[k - 1])} for k in range(1, n + 1)],
            "edges": [{"from": f"h{k // 2}", "to": f"h{k}"} for k in range(2, n + 1)]}

s = Script("Min-max heaps")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "A double-ended priority queue"],
    [2, "Min levels and max levels"],
    [3, "Finding the minimum and the maximum"],
    [4, "Inserting: up through grandparents"],
    [5, "Deleting the minimum"],
    [6, "Deleting the maximum, and costs"],
    [7, "Exam question"]]})
s.obj({"id": "de", "type": "table", "region": "center", "columns": ["need", "one heap", "two heaps", "min-max heap"], "rows": [
    ["min and max, both fast", "only one end is fast", "works, but 2 copies kept in step", "one array, both ends"],
    ["example uses", "", "", "a sliding window's extremes; a bounded buffer that drops either end"],
    ["operations", "", "", "find-min, find-max, insert, delete-min, delete-max"]]})
s.obj({"id": "lv", "type": "table", "region": "center", "columns": ["min-max heap (Atkinson et al., 1986)", ""], "rows": [
    ["shape", "a complete binary tree in an array, as before"],
    ["levels 0, 2, 4, …", "min levels: a node is ≤ everything below it"],
    ["levels 1, 3, 5, …", "max levels: a node is ≥ everything below it"],
    ["so a node is compared", "with its grandparent, not just its parent"]]})
s.obj(tree("t0", H0[1:]))
s.obj(tree("t5", H0[1:] + [5]))
s.obj(tree("t80", H0[1:] + [80]))
s.obj({"id": "ir", "type": "table", "region": "center", "columns": ["INSERT x at the end, position i", ""], "rows": [
    ["i on a min level, x > parent", "swap with the parent; continue up the max levels"],
    ["i on a min level, x ≤ parent", "continue up the min levels"],
    ["i on a max level", "the mirror image"],
    ["continue up", "swap with the grandparent while out of order"],
    ["cost", "O(log n): one path, every other level"]]})
s.obj(tree("td", [12, 70, 40, 30, 9, 10, 15, 45, 50, 30, 20]))
s.obj({"id": "co", "type": "table", "region": "center", "columns": ["operation", "cost"], "rows": [
    ["find-min, find-max", "O(1): root, or the larger root child"],
    ["insert", "O(log n)"],
    ["delete-min", "O(log n): trickle down through children and grandchildren"],
    ["delete-max", "O(log n): the same, starting at the larger child of the root"],
    ["building from n keys", "O(n), bottom-up as for heaps"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) insert 10, 20, 30, 5, 25, 40, 15 into an empty min-max heap: the array after each insertion"],
    ["b) find the minimum and the maximum"],
    ["c) delete the minimum: the array afterwards"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["insert", "what happens", "array"], "rows": [
    ["10, 20, 30", "20, 30 sit on a max level", "10 20 30"],
    ["5", "min level, < parent 20; < grandparent 10: swap", "5 20 30 10"],
    ["25", "min level, > parent 20: swap; then max levels", "5 25 30 10 20"],
    ["40", "min level, > parent 30: swap", "5 25 40 10 20 30"],
    ["15", "min level, < parent 40, > grandparent 5", "5 25 40 10 20 30 15"],
    ["b, c", "min 5, max 40 · delete 5: 15 to the root, trickles to 10", "10 25 40 15 20 30"]]})

s.scene("intro")
s.step("A max-heap gives the largest key fast, but finding the smallest means searching every leaf. Some problems need both ends. The min-max heap answers both, in one array, with the same logarithmic costs. This video builds one.", [s.head("Min-max heaps")])
s.step("Here are the seven stages.", show("stages"))
s.step("Why we want both ends, the alternating levels, and finding the minimum and maximum.", [hl("stages[0..=2]")])
s.step("Then inserting, deleting from both ends, and an exam question.", [hl("stages[3..=6]")])

s.scene("why")
s.step("Stage 1: a double-ended priority queue removes either its smallest or its largest item. One ordinary heap makes only one end fast.", [s.head("Stage 1 of 7: both ends"), s.untake()] + hide("stages") + show("de") + [hl("de[0]")])
s.step("Two heaps, one min and one max, work, but every key is stored twice and deletions must be mirrored in the other heap.", [hl("de[0][2]")])
s.step("A min-max heap does it in one array. It is used for the extremes of a sliding window, or a bounded buffer that may drop its best or its worst entry.", [hl("de[1..=2]"), s.take("one structure, both extremes")])

s.scene("levels")
s.step("Stage 2: the shape is a complete binary tree in an array, as before. The order is new: the levels alternate.", [s.head("Stage 2 of 7: min and max levels"), s.untake()] + hide("de") + show("lv") + [hl("lv[0]")])
s.step("Even levels, starting with the root at level 0, are min levels: a node there is at most every key below it.", [hl("lv[1]")])
s.step("Odd levels are max levels: a node there is at least every key below it.", [hl("lv[2]")])
s.step("So the order runs between a node and its grandchildren, two levels apart, and that is how the algorithms move.", [hl("lv[3]"), s.take("even levels min, odd levels max")])

s.scene("find")
s.step("Stage 3: this min-max heap, from Horowitz and Sahni: 7 at the root, 70 and 40 below, then 30, 9, 10, 15, then 45, 50, 30, 20, 12.", [s.head("Stage 3 of 7: min and max"), s.untake()] + hide("lv") + show("t0"))
s.step("The root, on a min level, is at most everything: the minimum is 7.", [mk("t0.h1")])
s.step("The maximum lies on level 1: the larger of the root's two children. 70 against 40: the maximum is 70. Both found in constant time.", [hl("t0.h2"), hl("t0.h3", 0.3), mk("t0.h2", 0.6), s.take("min = A[1] · max = max(A[2], A[3])")])

s.scene("ins")
s.step("Stage 4: insertion. Put the key at the next free position, then compare it with its parent to decide which kind of levels it must climb.", [s.head("Stage 4 of 7: inserting"), s.untake()] + hide("t0") + show("ir") + [hl("ir[0..=2]")])
s.step("Then climb two levels at a time, swapping with the grandparent while out of order. One path, every other level: O of log n.", [hl("ir[3..=4]")])
s.step("Insert 5. It lands at position 13, below 10. Position 13 is on level 3, a max level, but 5 is smaller than its parent 10, which sits on a min level. So 5 belongs on the min levels.", hide("ir") + show("t5") + [hl("t5.h13")])
s.step("Swap it with the parent: 5 moves to position 6. Then climb the min levels: its grandparent, the root, holds 7. 5 is smaller, swap. 5 is the new minimum.", [st("t5.h13", "10"), st("t5.h6", "5", 0.1), st("t5.h6", "7", 0.5), st("t5.h1", "5", 0.6), mk("t5.h1", 0.8)])
s.step("Insert 80 instead. It lands at position 13, below 10, on a max level. 80 is larger than its parent, so it stays on the max levels and climbs by grandparents: the grandparent, 40 at position 3, is smaller, so swap. Position 3 has no grandparent. 80 is the new maximum.", hide("t5") + show("t80") + [hl("t80.h13"), st("t80.h13", "40", 0.4), st("t80.h3", "80", 0.5), mk("t80.h3", 0.8), s.take("parent decides the side, grandparents do the climbing")])

s.scene("dmin")
s.step("Stage 5: delete the minimum, 7. Move the last key, 12, to the root, and shrink the heap.", [s.head("Stage 5 of 7: deleting the minimum"), s.untake()] + hide("t80") + show("td") + [hl("td.h1")])
s.step("Now trickle down. Among the root's children and grandchildren, the smallest is 9, a grandchild.", [hl("td.h5")])
s.step("9 is smaller than 12: swap. 12 is now at position 5, on a min level. Check its parent, 70, on a max level: 12 is smaller, so no swap is needed there.", [st("td.h1", "9"), st("td.h5", "12", 0.1), mk("td.h1", 0.5)])
s.step("Position 5's children, 30 and 20, are both larger than 12: done. The heap is 9, 70, 40, 30, 12, 10, 15, 45, 50, 30, 20. Each round moves down two levels: O of log n.", [s.take("trickle down through grandchildren")])

s.scene("dmax")
s.step("Stage 6: delete the maximum works the same way, starting at the larger child of the root, 70, and trickling down with the comparisons reversed.", [s.head("Stage 6 of 7: delete-max and costs"), s.untake()] + hide("td") + show("co") + [hl("co[3]")])
s.step("So all the costs: find-min and find-max are constant.", [hl("co[0]")])
s.step("Insert, delete-min and delete-max are O of log n each.", [hl("co[1..=3]")])
s.step("And building a min-max heap from n keys bottom-up is O of n, as for an ordinary heap.", [hl("co[4]"), s.take("O(1) find, O(log n) change, at both ends")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("co") + show("q") + [hl("q[0]")])
s.step("Insert seven keys, find both extremes, and delete the minimum. Pause and work it out.", [hl("q[1..=2]")])
s.step("10 is the root. 20 and 30 go on level 1, a max level; both are larger than 10, so they stay.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("5 lands at position 4, a min level, under 20. It is smaller than 20, so it climbs min levels: smaller than the grandparent 10, swap. 5 is the root.", [hl("qa[1]")])
s.step("25 lands under 20 at position 5. It is larger than 20, so it swaps up onto the max level. 40 lands under 30, larger, and swaps up the same way.", [hl("qa[2..=3]")])
s.step("15 lands under 40: smaller, so it climbs min levels, but it is larger than the grandparent 5. It stays. 5, 25, 40, 10, 20, 30, 15.", [hl("qa[4]")])
s.step("b: minimum 5, at the root; maximum 40, the larger of 25 and 40. c: delete 5, move 15 to the root, and the smallest child or grandchild, 10, swaps with it: 10, 25, 40, 15, 20, 30.", [hl("qa[5]"), mk("qa[5][2]", 0.5)])
s.step("The usual slip: comparing a new key only with its parent, as in an ordinary heap. In a min-max heap, after the first comparison, keys move by grandparents.", [s.take("climb by grandparents")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A min-max heap alternates min levels and max levels in one complete tree. The minimum is the root; the maximum is one of its children.", [hl("stages[0..=2]")])
s.step("Insertion picks a side with the parent, then climbs by grandparents. Deletion trickles down through children and grandchildren. All O of log n.", [hl("stages[3..=5]")])
s.step("Next video: leaving trees for graphs. How to store a graph.", [mk("stages[0..=6]"), s.take("Next: graph representation")])

s.save("/home/claude/playlist/dsa2/d2v10.json")

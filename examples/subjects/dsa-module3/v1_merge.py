"""DSA Module 3, video 1: divide and conquer, merge sort."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *
from sorts import merge_log, merge_sort_tree, comparisons_no_sentinel

L0, R0 = [2, 4, 5, 7], [1, 2, 3, 6]
OUT, MLOG = merge_log(L0, R0)
assert OUT == [1, 2, 2, 3, 4, 5, 6, 7] and [x[2] for x in MLOG] == list("RLRRLLRL")
NODES, TOT = merge_sort_tree([5, 2, 4, 7, 1, 3, 2, 6]); assert TOT == 17
EN, ET = merge_sort_tree([38, 27, 43, 3, 9, 82, 10]); assert ET == 14
assert comparisons_no_sentinel([3, 27, 38, 43], [9, 10, 82]) == 6
assert 1 + 1 + 3 + 1 + 2 + 6 == 14
assert 8 * (math.log2(8) + 1) == 32 and 1024 * 10 == 10240 and 1024 * 1023 // 2 == 523776

lbl = lambda a: " ".join(map(str, a))
ids = [f"n{i}" for i in range(len(NODES))]
# tree edges from preorder depths
par = {}; stack = []
for i, (d, a, b) in enumerate(NODES):
    while stack and NODES[stack[-1]][0] >= d: stack.pop()
    if stack: par[i] = stack[-1]
    stack.append(i)

s = Script("Divide and conquer: merge sort")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Divide and conquer"],
    [2, "Merging two sorted lists"],
    [3, "MERGE-SORT"],
    [4, "The whole sort, level by level"],
    [5, "The running time: a recurrence"],
    [6, "Properties, and when to use it"],
    [7, "Exam question"]]})
s.obj({"id": "dc", "type": "table", "region": "center", "columns": ["divide and conquer", ""], "rows": [
    ["divide", "split the problem into smaller problems of the same kind"],
    ["conquer", "solve each one recursively; tiny ones directly"],
    ["combine", "build the answer from the smaller answers"],
    ["merge sort", "divide: halve the array  ·  conquer: sort each half  ·  combine: merge"],
    ["this module", "merge sort, quicksort, Karatsuba, Strassen, fake coin"]]})
s.obj({"id": "mc", "type": "code", "region": "left", "language": "text", "lines": [
    "MERGE(A, p, q, r)",
    "    n1 = q − p + 1;   n2 = r − q",
    "    copy A[p .. q] into L[1 .. n1],  A[q+1 .. r] into R[1 .. n2]",
    "    L[n1 + 1] = ∞;   R[n2 + 1] = ∞          // sentinels",
    "    i = 1;   j = 1",
    "    for k = p to r",
    "        if L[i] ≤ R[j]",
    "            A[k] = L[i];   i = i + 1",
    "        else A[k] = R[j];   j = j + 1"]})
s.obj({"id": "la", "type": "array", "region": "left", "values": L0 + ["∞"]})
s.obj({"id": "ra", "type": "array", "region": "left", "values": R0 + ["∞"]})
s.obj({"id": "aa", "type": "array", "region": "right", "values": [""] * 8})
s.obj({"id": "pi", "type": "pointer", "label": "i", "target": "la[0]"})
s.obj({"id": "pj", "type": "pointer", "label": "j", "target": "ra[0]"})
s.obj({"id": "pk", "type": "pointer", "label": "k", "target": "aa[0]"})
s.obj({"id": "ms", "type": "code", "region": "center", "language": "text", "lines": [
    "MERGE-SORT(A, p, r)",
    "    if p < r                          // more than one element",
    "        q = ⌊(p + r) / 2⌋                // divide",
    "        MERGE-SORT(A, p, q)             // conquer the left half",
    "        MERGE-SORT(A, q + 1, r)         // conquer the right half",
    "        MERGE(A, p, q, r)               // combine",
    "",
    "first call:  MERGE-SORT(A, 1, n)"]})
def pieces(d, which):
    return "  |  ".join(lbl(n[which]) for n in NODES if n[0] == d)
s.obj({"id": "lv", "type": "table", "region": "center", "columns": ["level", "after dividing", "after merging"],
       "rows": [[str(d), "", ""] for d in range(4)]})
s.obj({"id": "rec", "type": "math", "region": "center", "lines": [
    "T(n) = 2 T(n slash 2) + c n, quad T(1) = c",
    "\"level\" 0: c n quad \"level\" 1: 2 dot c n/2 = c n quad \"level\" 2: 4 dot c n/4 = c n",
    "\"levels: \" log_2 n + 1 quad \"each costs \" c n",
    "T(n) = c n (log_2 n + 1) = Theta(n log n)",
    "\"master method, case 2: \" a = 2, b = 2, n^(log_2 2) = n = f(n) arrow.r.double Theta(n log n)"]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["merge sort", ""], "rows": [
    ["time", "Θ(n log n): best, average and worst alike"],
    ["extra space", "Θ(n) for L and R: not in place"],
    ["stable", "yes: ties take L first (the ≤ in MERGE)"],
    ["n = 1024", "about 10,240 steps against insertion sort's 523,776 comparisons, worst"],
    ["good for", "linked lists, and files too big for memory (external sorting)"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["sort ⟨38, 27, 43, 3, 9, 82, 10⟩ with MERGE-SORT (q = ⌊(p + r)/2⌋)"],
    ["a) draw the tree of splits and merges"],
    ["b) how many comparisons does the final merge make, without sentinels?"],
    ["c) how many comparisons in the whole sort?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a) divide", "q = 4: ⟨38 27 43 3⟩ | ⟨9 82 10⟩, then ⟨38 27⟩ ⟨43 3⟩ ⟨9 82⟩ ⟨10⟩", ""],
    ["a) merge", "⟨27 38⟩ ⟨3 43⟩ ⟨9 82⟩ → ⟨3 27 38 43⟩ ⟨9 10 82⟩", "⟨3 9 10 27 38 43 82⟩"],
    ["b)", "3<9, 9<27, 10<27, 27<82, 38<82, 43<82: left half used up", "6"],
    ["c)", "1 + 1 + 3 for the left, 1 + 2 for the right, 6 at the top", "14"]]})

s.scene("intro")
s.step("Insertion sort needs about n squared over 4 comparisons on average: for a million items, 250 billion. Merge sort needs about 20 million. The idea behind it, divide and conquer, runs through this whole module.", [s.head("Divide and conquer: merge sort")])
s.step("Here are the seven stages.", show("stages"))
s.step("Divide and conquer, merging, the algorithm, and a full trace.", [hl("stages[0..=3]")])
s.step("Then the running time, its properties, and an exam question.", [hl("stages[4..=6]")])

s.scene("dc")
s.step("Stage 1: divide and conquer has three parts. Divide the problem into smaller problems of the same kind.", [s.head("Stage 1 of 7: divide and conquer")] + hide("stages") + show("dc") + [hl("dc[0]")])
s.step("Conquer them by solving each recursively, and the tiny ones directly.", [hl("dc[1]")])
s.step("Combine their answers into the answer to the original problem.", [hl("dc[2]")])
s.step("For merge sort: divide the array into two halves. Sort each half recursively. Combine by merging the two sorted halves into one.", [hl("dc[3]")])
s.step("This module uses the same pattern for quicksort, fast multiplication of numbers and matrices, and the fake coin puzzle from the lab.", [hl("dc[4]"), s.take("divide · conquer · combine")])

s.scene("merge")
s.step("Stage 2: the heart of merge sort is MERGE, from Cormen. It copies the two sorted halves into arrays L and R.", [s.head("Stage 2 of 7: merging"), s.untake()] + hide("dc") + show("mc") + [ml("mc", 1, 3)])
s.step("And puts infinity at the end of each, as a sentinel: a card that never wins, so neither list ever runs out.", [ml("mc", 4, 4)])
s.step("Then it fills A one place at a time: compare the front of L with the front of R, and copy the smaller. Ties take L.", [ml("mc", 5, 9), s.take("each step: copy the smaller front element")])
s.step("Cormen's example: L holds 2, 4, 5, 7, and R holds 1, 2, 3, 6. i and j point at the fronts, and k at the next free place in A.", [s.untake()] + hide("mc") + show("la", "ra", "aa", "pi", "pj", "pk"))
say = ["1 is smaller than 2: take 1 from R.", "2 against 2: a tie, so take 2 from L.", "4 against 2: take 2 from R.", "4 against 3: take 3 from R.",
       "4 against 6: take 4 from L.", "5 against 6: take 5 from L.", "7 against 6: take 6 from R. R is now down to its sentinel.",
       "7 against infinity: take 7. Eight steps for eight elements: the merge is linear, Theta of n."]
i = j = 0
for k, (ii, jj, side, v) in enumerate(MLOG):
    acts = [cmp(f"la[{ii}]", f"ra[{jj}]"), st(f"aa[{k}]", v, 0.4)]
    if side == "L": i += 1; acts.append(pt("pi", f"la[{i}]", 0.6))
    else: j += 1; acts.append(pt("pj", f"ra[{j}]", 0.6))
    if k < 7: acts.append(pt("pk", f"aa[{k + 1}]", 0.7))
    if k == 7: acts += [mk("aa"), s.take("merging n elements: Θ(n)")]
    s.step(say[k], acts)

s.scene("ms")
s.step("Stage 3: now the whole algorithm. If the range from p to r has more than one element:", [s.head("Stage 3 of 7: MERGE-SORT"), s.untake()] + hide("la", "ra", "aa", "pi", "pj", "pk") + show("ms") + [ml("ms", 1, 2)])
s.step("Divide: q is the midpoint, rounded down.", [ml("ms", 3, 3)])
s.step("Conquer: sort the left half, p to q, and the right half, q plus 1 to r, by the same procedure.", [ml("ms", 4, 5)])
s.step("Combine: merge them. A single element is already sorted, so the recursion stops there.", [ml("ms", 6, 6)])
s.step("The first call sorts the whole array, from 1 to n.", [ml("ms", 8, 8), s.take("split at the middle, sort both halves, merge")])

s.scene("tree")
s.step("Stage 4: sort 5, 2, 4, 7, 1, 3, 2, 6. Level 0 is the whole array: one call.", [s.head("Stage 4 of 7: the whole sort"), s.untake()] + hide("ms") + show("lv") + [st("lv[0][1]", pieces(0, 1)), hl("lv[0]")])
s.step("Each call splits its part in two: two pieces of 4, then four pieces of 2.", [st("lv[1][1]", pieces(1, 1)), st("lv[2][1]", pieces(2, 1), 0.4), hl("lv[1..=2]")])
s.step("Then eight single elements. Three levels of halving, from 8 to 1. A single element is already sorted.", [st("lv[3][1]", pieces(3, 1)), st("lv[3][2]", pieces(3, 2), 0.5), hl("lv[3]")])
s.step("Now the merges, from the bottom up. 5 and 2 become 2, 5. 4, 7 stays. 1, 3 stays. 2, 6 stays.", [st("lv[2][2]", pieces(2, 2)), hl("lv[2][2]")])
s.step("Next level: 2, 5 merged with 4, 7 gives 2, 4, 5, 7. And 1, 3 with 2, 6 gives 1, 2, 3, 6: exactly the L and R we merged in stage 2.", [st("lv[1][2]", pieces(1, 2)), hl("lv[1][2]")])
s.step("The top merge gives 1, 2, 2, 3, 4, 5, 6, 7. Every level does merges totalling n elements of work.", [st("lv[0][2]", pieces(0, 2)), hl("lv[0][2]"), mk("lv[0][2]", 0.4), s.take("each level merges n elements in all")])
s.step("One detail: the computer does not work level by level as drawn. The calls go depth first: the left half, 5, 2, 4, 7, is completely sorted before the right half is even split. The merges are the same; only their order differs.", [hl("lv[1]")])

s.scene("time")
s.step("Stage 5: the running time. Two half-size subproblems, plus a merge that costs c n: T of n equals 2 T of n over 2, plus c n.", [s.head("Stage 5 of 7: the recurrence"), s.untake()] + hide("lv") + show("rec") + [hl("rec[0]")])
s.step("Draw it as a recursion tree. The top costs c n. The next level has 2 problems of size n over 2: c n again. Then 4 of size n over 4: c n again.", [rv("rec[1]"), hl("rec[1]")])
s.step("Halving from n down to 1 takes log n steps, so there are log n plus 1 levels, each costing c n.", [rv("rec[2]"), hl("rec[2]")])
s.step("Total: c n times log n plus 1, which is Theta of n log n. For our 8 elements: 4 levels of 8.", [rv("rec[3]"), hl("rec[3]")])
s.step("The master method from Module 1 says the same: a and b are both 2, n to the log base 2 of 2 is n, which matches f of n. Case 2: Theta of n log n.", [rv("rec[4]"), hl("rec[4]"), s.take("T(n) = 2T(n/2) + Θ(n) = Θ(n log n)")])
s.step("What that means in practice: double n, and the time only slightly more than doubles. A million elements take 20 levels of a million steps each.", [hl("rec[3]")])

s.scene("prop")
s.step("Stage 6: merge sort takes Theta of n log n on every input: sorted, reversed or random. There is no bad case.", [s.head("Stage 6 of 7: properties"), s.untake()] + hide("rec") + show("pr") + [hl("pr[0]")])
s.step("Its cost: the extra arrays L and R, Theta of n space. It does not sort in place.", [hl("pr[1]")])
s.step("It is stable: equal keys keep their order, because a tie takes the left one first.", [hl("pr[2]")])
s.step("For 1024 elements: about 10 thousand steps, against more than half a million comparisons for insertion sort in the worst case.", [hl("pr[3]")])
s.step("It suits linked lists, which need no extra array to merge, and data too big for memory, merged in sorted runs from disk.", [hl("pr[4]"), s.take("always n log n; stable; needs Θ(n) extra")])
s.step("For small pieces, below about 20 elements, insertion sort is actually faster, because it has less overhead. Real libraries switch to it at the bottom of the recursion.", [hl("pr[3]")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("pr") + show("q") + [hl("q[0]")])
s.step("Draw the tree, count the comparisons in the final merge, and in the whole sort. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: with 7 elements, q is 4, so the left part gets 4: 38, 27, 43, 3, and the right gets 9, 82, 10. Split again into pairs, and 10 on its own.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Merging up: 27, 38 and 3, 43 give 3, 27, 38, 43. On the right, 9, 82 and 10 give 9, 10, 82. The top merge gives 3, 9, 10, 27, 38, 43, 82.", [hl("qa[1]")])
s.step("b: compare 3 with 9, then 27 with 9, 27 with 10, 27 with 82, 38 with 82, 43 with 82. The left half is used up, and 82 is copied without a comparison: 6.", [hl("qa[2]")])
s.step("c: the left side costs 1, 1 and 3; the right side 1 and 2; the top 6. 14 comparisons in all.", [hl("qa[3]"), mk("qa[3][2]", 0.5)])
s.step("The usual slip: counting a comparison for every element copied. Once one list runs out, the rest is copied for free.", [s.take("no comparisons once a list is exhausted")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Divide and conquer: split, solve recursively, combine. Merge sort halves the array and merges the sorted halves in linear time.", [hl("stages[0..=3]")])
s.step("The recurrence 2 T of n over 2 plus n gives Theta of n log n, always, at the price of Theta of n extra space.", [hl("stages[4..=5]")])
s.step("Next video: a sort that does its work before the recursion instead of after. Quicksort.", [mk("stages[0..=6]"), s.take("Next: quicksort")])

s.save("/home/claude/playlist/dsa3/d3v1.json")

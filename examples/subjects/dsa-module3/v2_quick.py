"""DSA Module 3, video 2: quicksort."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *
from sorts import partition_log

A0 = [2, 8, 7, 1, 3, 5, 6, 4]
Q, PL = partition_log(list(A0), 0, 7)
assert Q == 3 and PL[-1][2] == [2, 1, 3, 4, 7, 5, 6, 8]
assert [x[1] for x in PL[:-1]] == [0, None, None, 1, 2, None, None]
def qs(A, p, r, calls):
    if p < r:
        q, _ = partition_log(A, p, r); calls.append((p, r, q, list(A))); qs(A, p, q - 1, calls); qs(A, q + 1, r, calls)
C = []; qs(list(A0), 0, 7, C)
assert [(p + 1, r + 1, q + 1) for p, r, q, _ in C] == [(1, 8, 4), (1, 3, 3), (1, 2, 1), (5, 8, 8), (5, 7, 6)]
E0 = [10, 80, 30, 90, 40, 50, 70]; EQ, EL = partition_log(list(E0), 0, 6)
assert EQ == 4 and EL[-1][2] == [10, 30, 40, 50, 70, 90, 80] and sum(1 for x in EL[:-1] if x[1] is not None) == 4
assert sum(range(1, 7)) == 21 and 1000 * 999 // 2 == 499500

s = Script("Quicksort")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The idea: partition, then recurse"],
    [2, "PARTITION"],
    [3, "Tracing PARTITION"],
    [4, "QUICKSORT, call by call"],
    [5, "Best, worst and average"],
    [6, "Randomized quicksort, and quicksort in practice"],
    [7, "Exam question"]]})
s.obj({"id": "idea", "type": "table", "region": "center", "columns": ["quicksort", ""], "rows": [
    ["divide", "pick a pivot; partition: smaller-or-equal to its left, larger to its right"],
    ["conquer", "sort the left part and the right part recursively"],
    ["combine", "nothing to do: the pivot is already in its final place"],
    ["merge sort", "easy divide, hard combine"],
    ["quicksort", "hard divide, no combine; sorts in place"]]})
s.obj({"id": "pc", "type": "code", "region": "left", "language": "text", "lines": [
    "PARTITION(A, p, r)",
    "    x = A[r]                    // the pivot: the last element",
    "    i = p − 1                   // end of the ≤ x region",
    "    for j = p to r − 1",
    "        if A[j] ≤ x",
    "            i = i + 1",
    "            exchange A[i] with A[j]",
    "    exchange A[i + 1] with A[r]  // pivot to its place",
    "    return i + 1"]})
s.obj({"id": "inv", "type": "table", "region": "right", "columns": ["while j moves", ""], "rows": [
    ["A[p .. i]", "≤ pivot"],
    ["A[i+1 .. j−1]", "> pivot"],
    ["A[j .. r−1]", "not yet looked at"],
    ["A[r]", "the pivot"]]})
s.obj({"id": "arr", "type": "array", "region": "center", "values": A0})
s.obj({"id": "pjj", "type": "pointer", "label": "j", "target": "arr[0]"})
s.obj({"id": "pii", "type": "pointer", "label": "i", "target": "arr[0]"})
s.obj({"id": "qc", "type": "code", "region": "left", "language": "text", "lines": [
    "QUICKSORT(A, p, r)",
    "    if p < r",
    "        q = PARTITION(A, p, r)",
    "        QUICKSORT(A, p, q − 1)",
    "        QUICKSORT(A, q + 1, r)",
    "",
    "first call:  QUICKSORT(A, 1, n)"]})
s.obj({"id": "calls", "type": "table", "region": "right", "columns": ["call", "pivot", "pivot's place", "array after"], "rows": [
    [f"A[{p + 1}..{r + 1}]", "", "", ""] for p, r, q, _ in C]})
s.obj({"id": "an", "type": "math", "region": "center", "lines": [
    "\"best: pivot always the median\" quad T(n) = 2 T(n slash 2) + Theta(n) = Theta(n log n)",
    "\"worst: pivot always the largest or smallest\" quad T(n) = T(n - 1) + Theta(n)",
    "T(n) = n + (n - 1) + dots + 2 = Theta(n^2) quad \"e.g. an already sorted array\"",
    "\"even 9 to 1 splits: depth \" log_(10 slash 9) n, \" each level \" <= c n arrow.r.double Theta(n log n)",
    "\"average, all orders equally likely: \" Theta(n log n), \" about \" 1.39 n log_2 n \" comparisons\""]})
s.obj({"id": "rq", "type": "table", "region": "center", "columns": ["in practice", ""], "rows": [
    ["randomized quicksort", "swap a random element into A[r] before partitioning"],
    ["effect", "no fixed input is bad: expected Θ(n log n) on every input"],
    ["in place", "only the recursion stack: O(log n) on average"],
    ["not stable", "the long swaps can reorder equal keys"],
    ["why it is popular", "tight inner loop, cache-friendly: usually faster than merge sort"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["A = ⟨10, 80, 30, 90, 40, 50, 70⟩, PARTITION(A, 1, 7) with pivot A[7]"],
    ["a) the array after PARTITION, and the value returned"],
    ["b) how many comparisons A[j] ≤ x, and how many exchanges in the loop?"],
    ["c) QUICKSORT on the sorted ⟨1, 2, 3, 4, 5, 6, 7⟩: comparisons in all?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "10 ≤ 70: i=1 · 80 no · 30: i=2, swap 80↔30 · 90 no · 40: i=3, swap 80↔40 · 50: i=4, swap 90↔50", ""],
    ["a)", "then swap A[5] = 80 with the pivot", "⟨10 30 40 50 70 90 80⟩, returns 5"],
    ["b)", "j runs from 1 to 6: one comparison each; 4 of them succeed", "6 comparisons, 4 exchanges"],
    ["c)", "pivot is always the largest: parts of 6, 5, 4, 3, 2, 1", "6+5+4+3+2+1 = 21"]]})

s.scene("intro")
s.step("Quicksort is the sort most libraries reach for first. It is also divide and conquer, but it does all its work before the recursion, not after. And it sorts in place, with no extra array.", [s.head("Quicksort")])
s.step("Here are the seven stages.", show("stages"))
s.step("The idea, the PARTITION procedure, a trace of it, and the whole sort call by call.", [hl("stages[0..=3]")])
s.step("Then the best and worst cases, randomized quicksort, and an exam question.", [hl("stages[4..=6]")])

s.scene("idea")
s.step("Stage 1: divide by picking one element, the pivot, and rearranging so everything smaller or equal is to its left, and everything larger to its right.", [s.head("Stage 1 of 7: the idea")] + hide("stages") + show("idea") + [hl("idea[0]")])
s.step("Conquer: sort the two sides recursively.", [hl("idea[1]")])
s.step("Combine: nothing. The pivot is already exactly where it belongs, and so is everything else once both sides are sorted.", [hl("idea[2]")])
s.step("Compare merge sort: its divide is trivial and its merge does the work. Quicksort is the opposite: the partition does the work, and there is no combine.", [hl("idea[3..=4]"), s.take("partition does the work; no combine step")])

s.scene("part")
s.step("Stage 2: Cormen's PARTITION uses the last element as the pivot, x.", [s.head("Stage 2 of 7: PARTITION"), s.untake()] + hide("idea") + show("pc", "inv") + [ml("pc", 1, 2)])
s.step("i marks the end of the region of elements smaller or equal to the pivot. It starts just before p: that region is empty.", [ml("pc", 3, 3), hl("inv[0]")])
s.step("j scans from left to right. Everything between i and j is larger than the pivot; everything from j on is not yet examined.", [ml("pc", 4, 4), hl("inv[1..=2]")])
s.step("When A of j is small enough, grow the small region by one, and swap A of j into it.", [ml("pc", 5, 7), hl("inv[0]")])
s.step("At the end, swap the pivot into the first place of the large region, i plus 1, and return that position.", [ml("pc", 8, 9), hl("inv[3]"), s.take("A[p..i] ≤ x < A[i+1..j−1]")])

s.scene("trace")
s.step("Stage 3: Cormen's example: 2, 8, 7, 1, 3, 5, 6, 4. The pivot is 4. i starts before the array; j at the first element.", [s.head("Stage 3 of 7: tracing PARTITION"), s.untake()] + hide("pc", "inv") + show("arr", "pjj") + [hl("arr[7]")])
s.step("2 is at most 4: i moves to the first place, and 2 swaps with itself. The small region is just 2.", [cmp("arr[0]", "arr[7]"), *show("pii"), mk("arr[0]", 0.5), pt("pjj", "arr[1]", 0.8)])
s.step("8 is larger than 4: nothing to do, j moves on. 7 is larger too.", [cmp("arr[1]", "arr[7]"), pt("pjj", "arr[2]", 0.4), cmp("arr[2]", "arr[7]", 0.5), pt("pjj", "arr[3]", 0.8)])
s.step("1 is at most 4: i moves to the second place, and 1 swaps with the 8 there. Small region: 2, 1.", [cmp("arr[3]", "arr[7]"), pt("pii", "arr[1]", 0.3), sw("arr[1]", "arr[3]", 0.4), mk("arr[1]", 0.8), pt("pjj", "arr[4]", 0.9)])
s.step("3 is at most 4: i moves to the third place, and 3 swaps with the 7. Small region: 2, 1, 3.", [cmp("arr[4]", "arr[7]"), pt("pii", "arr[2]", 0.3), sw("arr[2]", "arr[4]", 0.4), mk("arr[2]", 0.8), pt("pjj", "arr[5]", 0.9)])
s.step("5 and 6 are both larger: j passes them.", [cmp("arr[5]", "arr[7]"), pt("pjj", "arr[6]", 0.4), cmp("arr[6]", "arr[7]", 0.5)])
s.step("Finally the pivot 4 swaps with 8, the first element of the large region. 4 is now in place, fourth, and PARTITION returns 4.", [sw("arr[3]", "arr[7]"), mk("arr[3]", 0.6), s.take("pivot 4 lands in its final place")])
s.step("Everything left of it, 2, 1, 3, is smaller; everything right, 7, 5, 6, 8, is larger. Seven comparisons for eight elements: partition is linear.", [hl("arr[0..=2]"), hl("arr[4..=7]", 0.5)])

s.scene("qs")
s.step("Stage 4: QUICKSORT partitions, then sorts the left part and the right part. Here is every call that does work.", [s.head("Stage 4 of 7: QUICKSORT"), s.untake()] + hide("arr", "pjj", "pii") + show("qc", "calls") + [ml("qc", 1, 5)])
say = ["The first call, the whole array: pivot 4, placed fourth, as we traced.",
       "Left part, 2, 1, 3: pivot 3 is the largest, so it stays third, and 2, 1 is left.",
       "Then 2, 1: pivot 1 goes first. The left part of the array is sorted.",
       "Right part, 7, 5, 6, 8: pivot 8 is the largest, so it stays last.",
       "Then 7, 5, 6: pivot 6 goes in the middle. Single elements need no call. Sorted."]
for k, (p, r, q, arr) in enumerate(C):
    acts = [hl(f"calls[{k}]"), st(f"calls[{k}][1]", str(arr[q]), 0.2), st(f"calls[{k}][2]", str(q + 1), 0.4), st(f"calls[{k}][3]", " ".join(map(str, arr)), 0.6)]
    if k == len(C) - 1: acts.append(s.take("each call places one pivot for good"))
    s.step(say[k], acts)

s.scene("an")
s.step("Stage 5: how fast? Partition costs Theta of n. In the best case the pivot is always the median, and the recurrence is merge sort's: Theta of n log n.", [s.head("Stage 5 of 7: best, worst, average"), s.untake()] + hide("qc", "calls") + show("an") + [hl("an[0]")])
s.step("In the worst case the pivot is always the largest or smallest: one side is empty, the other has n minus 1 elements.", [rv("an[1]"), hl("an[1]")])
s.step("Then the costs are n, plus n minus 1, and so on down to 2: Theta of n squared. With the last element as pivot, an already sorted array does exactly this.", [rv("an[2]"), hl("an[2]")])
s.step("For a thousand sorted elements that is 499,500 comparisons, where a good split would need about 10 thousand. A reversed array is just as bad.", [hl("an[2]")])
s.step("But the split need not be even. Even if every split were 9 to 1, the depth is only log base 10 over 9 of n, with at most c n per level: still Theta of n log n.", [rv("an[3]"), hl("an[3]")])
s.step("And averaged over all input orders, quicksort makes about 1.39 n log n comparisons: Theta of n log n.", [rv("an[4]"), hl("an[4]"), s.take("Θ(n log n) on average, Θ(n²) worst")])

s.scene("rand")
s.step("Stage 6: to avoid the bad case, randomized quicksort swaps a randomly chosen element into the last place before partitioning.", [s.head("Stage 6 of 7: in practice"), s.untake()] + hide("an") + show("rq") + [hl("rq[0]")])
s.step("Now no particular input is bad. Sorted, reversed, anything: the expected time is Theta of n log n.", [hl("rq[1]")])
s.step("It sorts in place: the only extra memory is the recursion stack, logarithmic on average.", [hl("rq[2]")])
s.step("It is not stable: the long-distance swaps can change the order of equal keys.", [hl("rq[3]")])
s.step("Its inner loop is short, and it walks memory in order, so in practice it usually beats merge sort.", [hl("rq[4]"), s.take("random pivot: expected Θ(n log n), any input")])
s.step("Two common refinements. Median of three: take the middle value of the first, middle and last elements as the pivot, which makes sorted input harmless. And Hoare's original partition, which scans from both ends and swaps fewer times.", [hl("rq[0..=1]")])
s.step("Library sorts combine these: quicksort for large parts, insertion sort for tiny ones, and a switch to heapsort if the recursion gets too deep. That hybrid is called introsort.", [hl("rq[4]")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("rq") + show("q") + [hl("q[0]")])
s.step("Partition the array, count the comparisons and exchanges, and find the cost of sorting an already sorted array. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: pivot 70. 10 is smaller: i becomes 1. 80 no. 30: i is 2, swap 80 and 30. 90 no. 40: i is 3, swap 80 and 40. 50: i is 4, swap 90 and 50.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Then swap the pivot with A of 5, which holds 80. The array is 10, 30, 40, 50, 70, 90, 80, and PARTITION returns 5.", [hl("qa[1]")])
s.step("b: j runs over the first 6 places, one comparison each: 6 comparisons. Four succeed, so 4 exchanges in the loop, counting the first, which swaps 10 with itself.", [hl("qa[2]")])
s.step("c: on a sorted array the pivot is always the largest. The parts have 6, 5, 4, 3, 2 and 1 comparisons: 21 in all, the n squared case.", [hl("qa[3]"), mk("qa[3][2]", 0.5)])
s.step("The usual slip: forgetting the final swap of the pivot, or starting i at p instead of p minus 1.", [s.take("i starts at p − 1; finish with the pivot swap")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Quicksort partitions around a pivot in linear time, places it for good, and sorts each side. No combine, no extra array.", [hl("stages[0..=3]")])
s.step("Balanced splits give n log n; always-extreme pivots give n squared. A random pivot makes n log n the expected time on any input.", [hl("stages[4..=5]")])
s.step("Next video: divide and conquer applied to arithmetic. Multiplying large numbers with Karatsuba's algorithm.", [mk("stages[0..=6]"), s.take("Next: Karatsuba multiplication")])

s.save("/home/claude/playlist/dsa3/d3v2.json")

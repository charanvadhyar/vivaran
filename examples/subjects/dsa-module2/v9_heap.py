"""DSA Module 2, video 9: binary heaps and heapsort."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from heap import heapify, build, insert, extract

B0 = [4, 1, 3, 2, 16, 9, 10, 14, 8, 7]
BA, BLOG = build(B0)
assert BA[1:] == [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]
assert BLOG == [("at", 5), ("at", 4), (4, 8), ("at", 3), (3, 7), ("at", 2), (2, 5), (5, 10), ("at", 1), (1, 2), (2, 4), (4, 9)]
H = BA[:]; IL = insert(H, 15); assert H[1:] == [16, 15, 10, 8, 14, 9, 3, 2, 4, 1, 7] and IL == [(11, 5), (5, 2)]
top, XL = extract(H); assert top == 16 and H[1:] == [15, 14, 10, 8, 7, 9, 3, 2, 4, 1] and XL == [(1, 2), (2, 5)]
EA, ELOG = build([5, 3, 17, 10, 84, 19, 6, 22, 9]); assert EA[1:] == [84, 22, 19, 10, 3, 17, 6, 5, 9]
et, EXL = extract(EA); assert et == 84 and EA[1:] == [22, 10, 19, 9, 3, 17, 6, 5]
# heapsort result
def heapsort(v):
    A, _ = build(v); n = len(v); out = []
    for k in range(n, 1, -1):
        A[1], A[k] = A[k], A[1]; heapify(A, 1, k - 1, [])
    return A[1:]
assert heapsort(B0) == sorted(B0)
_A, _ = build(B0); _A[1], _A[10] = _A[10], _A[1]; heapify(_A, 1, 9, []); assert _A[1:10] == [14, 8, 10, 4, 7, 9, 3, 2, 1]
_A[1], _A[9] = _A[9], _A[1]; heapify(_A, 1, 8, []); assert _A[1:9] == [10, 8, 9, 4, 7, 1, 3, 2]
assert sum(h * (2 ** (10 - h)) for h in range(1, 11)) < 2 * 2**10

def tree(i, n, vals, region="left"):
    return {"id": i, "type": "diagram", "region": region, "layout": "tree", "shape": "circle", "directed": False,
            "nodes": [{"id": f"h{k}", "label": str(vals[k - 1])} for k in range(1, n + 1)],
            "edges": [{"from": f"h{k // 2}", "to": f"h{k}"} for k in range(2, n + 1)]}
class Tr:
    """apply swaps to both the tree labels and the array"""
    def __init__(s, tid, aid, vals): s.t, s.a, s.v = tid, aid, [None] + list(vals)
    def swap(s, i, j, d=0.0):
        s.v[i], s.v[j] = s.v[j], s.v[i]
        return [st(f"{s.t}.h{i}", str(s.v[i]), d), st(f"{s.t}.h{j}", str(s.v[j]), d), sw(f"{s.a}[{i - 1}]", f"{s.a}[{j - 1}]", d)]

s = Script("Binary heaps")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The heap property"],
    [2, "Sifting down: MAX-HEAPIFY"],
    [3, "Building a heap"],
    [4, "Why building is linear"],
    [5, "Insert and extract-max"],
    [6, "Heapsort"],
    [7, "Exam question"]]})
s.obj({"id": "hp", "type": "table", "region": "center", "columns": ["binary max-heap", ""], "rows": [
    ["shape", "a complete binary tree, stored in an array from index 1"],
    ["parent of i, children of i", "⌊i/2⌋ · 2i and 2i + 1 (video 1)"],
    ["max-heap property", "A[parent(i)] ≥ A[i] for every i > 1"],
    ["so", "the largest key is at the root, A[1]"],
    ["but", "siblings are in no particular order: a heap is not sorted"],
    ["height", "⌊log₂ n⌋"]]})
s.obj(tree("t1", 10, [16, 4, 10, 14, 7, 9, 3, 2, 8, 1]))
s.obj({"id": "a1", "type": "array", "region": "right", "values": [16, 4, 10, 14, 7, 9, 3, 2, 8, 1]})
s.obj(tree("t2", 10, B0))
s.obj({"id": "a2", "type": "array", "region": "right", "values": B0})
s.obj({"id": "lin", "type": "math", "region": "center", "lines": [
    "\"BUILD calls HEAPIFY on nodes\" floor(n/2) \"down to\" 1",
    "\"a node at height\" h \"costs\" O(h); quad \"at most\" ceil(n / 2^(h+1)) \"nodes have height\" h",
    "sum_(h=0)^(log n) n / 2^(h+1) dot O(h) = O(n sum_h h / 2^h) = O(n dot 2) = O(n)",
    "\"most nodes are near the bottom, where sifting is cheap\""]})
s.obj(tree("t3", 11, BA[1:] + [15]))
s.obj({"id": "a3", "type": "array", "region": "right", "values": BA[1:] + [15]})
s.obj({"id": "hs", "type": "table", "region": "center", "columns": ["HEAPSORT(A)", ""], "rows": [
    ["BUILD-MAX-HEAP(A)", "O(n)"],
    ["for k = n down to 2", "swap A[1] (the maximum) with A[k]"],
    ["", "shrink the heap to k − 1, MAX-HEAPIFY(A, 1)"],
    ["total", "O(n log n), always, and in place"],
    ["but", "not stable, and its jumps around the array suit caches poorly"]]})
s.obj({"id": "pq", "type": "table", "region": "center", "columns": ["max-priority queue on a heap", "cost"], "rows": [
    ["MAXIMUM", "Θ(1): A[1]"],
    ["EXTRACT-MAX", "O(log n): move the last key to the root, sift down"],
    ["INSERT", "O(log n): add at the end, sift up"],
    ["INCREASE-KEY", "O(log n): sift up"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) build a max-heap from 5, 3, 17, 10, 84, 19, 6, 22, 9 (index 1 to 9)"],
    ["b) then extract the maximum: the array afterwards"],
    ["c) is 23, 17, 14, 6, 13, 10, 1, 5, 7, 12 a max-heap?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["step", "array"], "rows": [
    ["start", "5 3 17 10 84 19 6 22 9"],
    ["i = 4: 10 ↔ 22", "5 3 17 22 84 19 6 10 9"],
    ["i = 3: 17 ↔ 19", "5 3 19 22 84 17 6 10 9"],
    ["i = 2: 3 ↔ 84", "5 84 19 22 3 17 6 10 9"],
    ["i = 1: 5 ↔ 84, 5 ↔ 22, 5 ↔ 10", "84 22 19 10 3 17 6 5 9"],
    ["b) extract 84: 9 to the root, sift down", "22 10 19 9 3 17 6 5"],
    ["c) A[4] = 6 has child A[9] = 7", "not a heap: 6 < 7"]]})

T1 = Tr("t1", "a1", [16, 4, 10, 14, 7, 9, 3, 2, 8, 1])
T2 = Tr("t2", "a2", B0)
T3 = Tr("t3", "a3", BA[1:] + [15])

s.scene("intro")
s.step("A priority queue keeps handing out its most important item. The binary heap does that in logarithmic time, inside a plain array, with no pointers at all, and it also gives a guaranteed n log n sort. This video builds one.", [s.head("Binary heaps")])
s.step("Here are the seven stages.", show("stages"))
s.step("The heap property, sifting down, building a heap, and why building takes only linear time.", [hl("stages[0..=3]")])
s.step("Then insert and extract-max, heapsort, and an exam question.", [hl("stages[4..=6]")])

s.scene("prop")
s.step("Stage 1: a binary heap is a complete binary tree, stored in an array from index 1, with the parent and child formulas from video 1.", [s.head("Stage 1 of 7: the heap property")] + hide("stages") + show("hp") + [hl("hp[0..=1]")])
s.step("In a max-heap, every parent is at least as large as its children.", [hl("hp[2]")])
s.step("So the largest key is always at the root.", [hl("hp[3]")])
s.step("But a heap is not sorted: nothing orders two siblings, or two different subtrees. It is a much weaker, and much cheaper, arrangement than a search tree.", [hl("hp[4]")])
s.step("A min-heap is the mirror image: every parent at most its children, and the minimum at the root. Everything in this video works for it with the comparisons reversed.", [hl("hp[2]")])
s.step("Its height is the floor of log 2 of n, because it is complete.", [hl("hp[5]"), s.take("parent ≥ children · max at A[1]")])

s.scene("heapify")
s.step("Stage 2: MAX-HEAPIFY fixes one node whose subtrees are already heaps. Here, the node at index 2 holds 4, smaller than its children 14 and 7.", [s.head("Stage 2 of 7: sifting down"), s.untake()] + hide("hp") + show("t1", "a1") + [hl("t1.h2"), hl("a1[1]", 0.3)])
s.step("Swap it with the larger child, 14. Larger, so that the new parent beats both children.", T1.swap(2, 4) + [hl("t1.h4", 0.5)])
s.step("Now 4 sits at index 4, with children 2 and 8. Swap with 8.", T1.swap(4, 9) + [hl("t1.h9", 0.5)])
s.step("At index 9, 4 is a leaf: done. Each swap moves one level down, so MAX-HEAPIFY costs O of the height: O of log n.", [mk("t1.h9"), s.take("sift down: swap with the larger child")])

s.scene("build")
s.step("Stage 3: to build a heap from an unordered array, call MAX-HEAPIFY on every internal node, from the last one, at n over 2, back to the root. Leaves are already heaps.", [s.head("Stage 3 of 7: building a heap"), s.untake()] + hide("t1", "a1") + show("t2", "a2") + [hl("t2.h5")])
s.step("i equal to 5: 16 is larger than its child 7. Nothing to do. i equal to 4: 2 is smaller than 14: swap.", [hl("t2.h4")] + T2.swap(4, 8, 0.4))
s.step("i equal to 3: 3 is smaller than 10: swap. i equal to 2: 1 sinks, first below 16, then below 7.", T2.swap(3, 7) + T2.swap(2, 5, 0.4) + T2.swap(5, 10, 0.7))
s.step("i equal to 1: 4 sinks below 16, then below 14, then below 8.", T2.swap(1, 2) + T2.swap(2, 4, 0.35) + T2.swap(4, 9, 0.7))
s.step("The result: 16, 14, 10, 8, 7, 9, 3, 2, 4, 1. Every parent beats its children.", [mk("t2.h1"), s.take("heapify from n/2 back to 1")])

s.scene("linear")
s.step("Stage 4: n over 2 calls, each up to log n, suggests n log n. The true cost is lower. A call on a node of height h costs O of h.", [s.head("Stage 4 of 7: building is linear"), s.untake()] + hide("t2", "a2") + show("lin") + [hl("lin[0]")])
s.step("And at most n over 2 to the h plus 1 nodes have height h: half the nodes are leaves, a quarter have height 1, and so on.", [rv("lin[1]"), hl("lin[1]")])
s.step("The sum of h over 2 to the h converges to 2, so the total is O of n.", [rv("lin[2]"), hl("lin[2]")])
s.step("Most nodes are near the bottom, where sifting down is short. Building a heap is linear.", [rv("lin[3]"), hl("lin[3]"), s.take("BUILD-MAX-HEAP: O(n), not O(n log n)")])

s.scene("ops")
s.step("Stage 5: insert 15 into our heap. It goes into the next free position, index 11, as a child of 7.", [s.head("Stage 5 of 7: insert and extract-max"), s.untake()] + hide("lin") + show("t3", "a3") + [hl("t3.h11")])
s.step("Sift it up: 15 beats its parent 7, so swap. Then 15 beats 14, so swap again. 16 is larger: stop.", T3.swap(11, 5) + T3.swap(5, 2, 0.5))
s.step("Extract-max: take 16 from the root. Move the last key, 7, into the root, and shrink the heap.", st("t3.h1", "7") and [st("t3.h1", "7"), st("a3[0]", 7), rm("t3.h11", 0.4), rm("a3[10]", 0.4)])
s.step("Then sift 7 down: below 15, then below 14. The new root is 15. Both operations follow one path: O of log n.", [st("t3.h1", "15"), st("t3.h2", "7"), sw("a3[0]", "a3[1]"), st("t3.h2", "14", 0.5), st("t3.h5", "7", 0.5), sw("a3[1]", "a3[4]", 0.5)])
s.step("These are exactly the priority-queue operations: maximum is instant, and insert, extract-max and increase-key are all O of log n.", hide("t3", "a3") + show("pq") + [hl("pq"), s.take("insert: sift up · extract: sift down")])

s.scene("sort")
s.step("Stage 6: heapsort. Build a max-heap: O of n.", [s.head("Stage 6 of 7: heapsort"), s.untake()] + hide("pq") + show("hs") + [hl("hs[0]")])
s.step("Then repeatedly swap the maximum at A of 1 with the last element of the heap, shrink the heap by one, and sift the new root down.", [hl("hs[1..=2]")])
s.step("On our heap 16, 14, 10, 8, 7, 9, 3, 2, 4, 1: swap 16 with the last key, 1, and sift 1 down. The heap part becomes 14, 8, 10, 4, 7, 9, 3, 2, 1, with 16 parked at the end.", [hl("hs[1..=2]")])
s.step("Next, swap 14 with 1 and sift down: 10, 8, 9, 4, 7, 1, 3, 2, then 14, 16 at the end. The sorted part grows from the right, one maximum at a time.", [hl("hs[1..=2]")])
s.step("The largest keys collect at the end of the array, in order. n minus 1 sift-downs: O of n log n in every case, using no extra array.", [hl("hs[3]")])
s.step("Its weaknesses: it is not stable, and its long jumps across the array make poor use of caches, so quicksort is usually faster in practice.", [hl("hs[4]"), s.take("heapsort: O(n log n) worst case, in place")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("hs") + show("q") + [hl("q[0]")])
s.step("Build a heap, extract the maximum, and check whether an array is a heap. Pause and work it out.", [hl("q[1..=2]")])
s.step("n is 9, so start at 4: 10 against children 22 and 9. Swap with 22.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("i equal to 3: 17 against 19 and 6: swap with 19. i equal to 2: 3 against 22 and 84: swap with 84.", [hl("qa[2..=3]")])
s.step("i equal to 1: 5 sinks below 84, then below 22, then below 10. The heap: 84, 22, 19, 10, 3, 17, 6, 5, 9.", [hl("qa[4]")])
s.step("b: remove 84, move the last key 9 to the root, and sift down: below 22, then below 10. 22, 10, 19, 9, 3, 17, 6, 5.", [hl("qa[5]")])
s.step("c: check each parent. A of 4 is 6, and its child A of 9 is 7. 6 is smaller: not a max-heap.", [hl("qa[6]"), mk("qa[6][1]", 0.5)])
s.step("The usual slip: swapping with the first child that is larger, instead of the larger of the two children.", [s.take("swap with the larger child")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A max-heap is a complete tree in an array, every parent at least its children. MAX-HEAPIFY sifts a key down in O of log n, and building a heap bottom-up costs only O of n.", [hl("stages[0..=3]")])
s.step("Insert sifts up, extract-max sifts down, both O of log n, and heapsort sorts in place in O of n log n.", [hl("stages[4..=5]")])
s.step("Next video: a heap that serves both the minimum and the maximum. The min-max heap.", [mk("stages[0..=6]"), s.take("Next: min-max heaps")])

s.save("/home/claude/playlist/dsa2/d2v9.json")

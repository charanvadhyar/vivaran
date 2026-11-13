"""DSA Module 2, video 8: segment trees."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *

class Seg:
    def __init__(s, a, f=lambda x, y: x + y):
        s.n, s.f, s.t, s.iv = len(a), f, {}, {}
        s.build(1, 0, s.n - 1, a)
    def build(s, v, l, r, a):
        s.iv[v] = (l, r)
        if l == r: s.t[v] = a[l]; return
        m = (l + r) // 2; s.build(2 * v, l, m, a); s.build(2 * v + 1, m + 1, r, a); s.t[v] = s.f(s.t[2 * v], s.t[2 * v + 1])
    def query(s, ql, qr, v=1, used=None, seen=None):
        used = [] if used is None else used; seen = [] if seen is None else seen
        l, r = s.iv[v]; seen.append(v)
        if ql <= l and r <= qr: used.append(v); return s.t[v], used, seen
        m = (l + r) // 2; res = None
        if ql <= m: res, _, _ = s.query(ql, qr, 2 * v, used, seen)
        if qr > m:
            x, _, _ = s.query(ql, qr, 2 * v + 1, used, seen); res = x if res is None else s.f(res, x)
        return res, used, seen
    def update(s, i, val, v=1, path=None):
        path = [] if path is None else path; l, r = s.iv[v]; path.append(v)
        if l == r: s.t[v] = val; return path
        m = (l + r) // 2
        s.update(i, val, 2 * v if i <= m else 2 * v + 1, path); s.t[v] = s.f(s.t[2 * v], s.t[2 * v + 1]); return path

A = [2, 1, 5, 3, 4, 2, 6, 1]
S = Seg(A)
assert S.t[1] == 24 and (S.t[2], S.t[3]) == (11, 13) and [S.t[i] for i in (4, 5, 6, 7)] == [3, 8, 6, 7]
q, used, seen = S.query(2, 6)
assert q == 20 and [S.iv[v] for v in used] == [(2, 3), (4, 5), (6, 6)] and len(seen) == 7
path = S.update(3, 7)
assert [S.iv[v] for v in path] == [(0, 7), (0, 3), (2, 3), (3, 3)] and S.t[1] == 28 and S.t[2] == 15 and S.t[5] == 12
EA = [5, 8, 6, 3, 2, 7, 2, 6]
E = Seg(EA); Em = Seg(EA, min)
assert E.t[1] == 39 and (E.t[2], E.t[3]) == (22, 17) and [E.t[i] for i in (4, 5, 6, 7)] == [13, 9, 9, 8]
eq, eu, _ = E.query(1, 5); assert eq == 26 and [E.iv[v] for v in eu] == [(1, 1), (2, 3), (4, 5)]
mq, _, _ = Em.query(1, 5); assert mq == 2
E.update(4, 9); assert E.t[1] == 46 and E.t[6] == 16 and E.t[3] == 24
assert sum(A[2:7]) == 20 and sum(EA[1:6]) == 26

def seg_obj(i, st, region="center"):
    ids = sorted(st.iv)
    lab = lambda v: (f"{st.iv[v][0]}: {st.t[v]}" if st.iv[v][0] == st.iv[v][1] else f"{st.iv[v][0]}–{st.iv[v][1]}: {st.t[v]}")
    return {"id": i, "type": "diagram", "region": region, "layout": "tree",
            "nodes": [{"id": f"v{v}", "label": lab(v), "shape": "box"} for v in ids],
            "edges": [{"from": f"v{v}", "to": f"v{c}"} for v in ids for c in (2 * v, 2 * v + 1) if c in st.iv]}

s = Script("Segment trees")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The range query problem"],
    [2, "The shape of a segment tree"],
    [3, "Building it"],
    [4, "Answering a range query"],
    [5, "Updating one element"],
    [6, "Other operations"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["array of n numbers, many operations", "sum(l, r)", "A[i] = x"], "rows": [
    ["plain array: add up A[l..r]", "Θ(n)", "Θ(1)"],
    ["prefix sums P: P[r] − P[l − 1]", "Θ(1)", "Θ(n): every later prefix changes"],
    ["segment tree", "Θ(log n)", "Θ(log n)"],
    ["10⁵ elements, 10⁵ mixed operations", "≈ 10¹⁰ steps for the first two", "≈ 3.4 × 10⁶ for the tree"]]})
s.obj({"id": "sh", "type": "table", "region": "center", "columns": ["segment tree", ""], "rows": [
    ["each node", "covers an interval [l, r] and stores its sum"],
    ["the root", "covers the whole array [0, n − 1]"],
    ["a node's children", "cover the two halves: [l, m] and [m + 1, r], m = ⌊(l + r)/2⌋"],
    ["the leaves", "are single elements"],
    ["size", "2n − 1 nodes; stored in an array of 4n, children of v at 2v and 2v + 1"]]})
s.obj({"id": "arr", "type": "array", "region": "center", "values": A})
s.obj(seg_obj("t0", Seg(A)))
s.obj({"id": "qc", "type": "table", "region": "center", "columns": ["QUERY(node covering [l, r], query [ql, qr])", ""], "rows": [
    ["[l, r] inside [ql, qr]", "return the node's sum: it is used whole"],
    ["[l, r] outside [ql, qr]", "return 0: ignore it"],
    ["partly overlapping", "ask both children, add the answers"],
    ["cost", "at most 4 nodes per level: O(log n)"]]})
s.obj(seg_obj("t1", S))
s.obj({"id": "cd", "type": "code", "region": "center", "language": "text", "lines": [
    "QUERY(v, l, r, ql, qr)            // node v covers [l, r]",
    "    if qr < l or r < ql: return 0               // outside",
    "    if ql <= l and r <= qr: return T[v]         // inside",
    "    m = (l + r) / 2                              // rounded down",
    "    return QUERY(2v, l, m, ql, qr) + QUERY(2v+1, m+1, r, ql, qr)",
    "",
    "UPDATE(v, l, r, i, x)",
    "    if l == r: T[v] = x; return",
    "    m = (l + r) / 2",
    "    if i <= m: UPDATE(2v, l, m, i, x) else UPDATE(2v+1, m+1, r, i, x)",
    "    T[v] = T[2v] + T[2v+1]"]})
s.obj({"id": "ops", "type": "table", "region": "center", "columns": ["store in each node", "answers"], "rows": [
    ["sum", "range sums"],
    ["minimum or maximum", "range minimum queries (RMQ)"],
    ["gcd, count, product, …", "any associative combination"],
    ["add v to a whole range", "lazy propagation: store a pending addition, push it down only when needed"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: A = [5, 8, 6, 3, 2, 7, 2, 6], indices 0 to 7"], "rows": [
    ["a) build the sum segment tree: the root and the two levels below it"],
    ["b) sum(1, 5): which nodes are used?   c) the minimum of A[1..5]"],
    ["d) set A[4] = 9: which nodes change, and the new root"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "root 39 · [0–3] 22, [4–7] 17 · 13, 9, 9, 8", ""],
    ["b", "[1] 8 + [2–3] 9 + [4–5] 9", "26"],
    ["c", "min(8, 6, 3, 2, 7)", "2"],
    ["d", "[4] 2 → 9; [4–5] 9 → 16; [4–7] 17 → 24; root 39 → 46", "root 46"]]})

s.scene("intro")
s.step("Many problems ask the same question again and again about different parts of an array: what is the sum, or the smallest value, between positions l and r, while the array keeps changing. The segment tree answers each question, and makes each change, in logarithmic time.", [s.head("Segment trees")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem, the shape of the tree, building it, and answering a range query.", [hl("stages[0..=3]")])
s.step("Then updating an element, other operations, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: an array of n numbers, and a long mix of two operations: the sum from l to r, and setting A of i to a new value. With a plain array, a sum adds up to n elements; an update is instant.", [s.head("Stage 1 of 7: the range query problem")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("With prefix sums, a range sum is one subtraction, but an update changes every later prefix: Theta of n.", [hl("pb[1]")])
s.step("A segment tree does both in Theta of log n.", [hl("pb[2]")])
s.step("For a hundred thousand elements and a hundred thousand operations, the first two can need about 10 to the 10 steps. The segment tree needs a few million.", [hl("pb[3]"), s.take("both operations in O(log n)")])

s.scene("shape")
s.step("Stage 2: every node of a segment tree covers an interval of the array and stores the sum of that interval. The root covers everything.", [s.head("Stage 2 of 7: the shape"), s.untake()] + hide("pb") + show("sh") + [hl("sh[0..=1]")])
s.step("A node's two children cover the left and right halves of its interval.", [hl("sh[2]")])
s.step("Halving stops at single elements: those are the leaves.", [hl("sh[3]")])
s.step("There are 2n minus 1 nodes, usually stored in an array of size 4n, with the children of node v at 2v and 2v plus 1, as in a heap.", [hl("sh[4]"), s.take("node = interval + its sum")])
s.step("Why 4n, when there are fewer than 2n nodes? When n is not a power of 2, the halves are uneven, and the heap-style numbering skips some positions. 4n is always enough.", [hl("sh[4]")])

s.scene("build")
s.step("Stage 3: build it for this array: 2, 1, 5, 3, 4, 2, 6, 1.", [s.head("Stage 3 of 7: building it"), s.untake()] + hide("sh") + show("arr"))
s.step("The leaves hold the elements. Each internal node adds its two children, from the bottom up: 2 plus 1 is 3, 5 plus 3 is 8, then 6 and 7.", hide("arr") + show("t0") + [hl("t0.v4"), hl("t0.v5", 0.2), hl("t0.v6", 0.4), hl("t0.v7", 0.6)])
s.step("One level up: 3 plus 8 is 11 for positions 0 to 3, and 6 plus 7 is 13 for positions 4 to 7.", [hl("t0.v2"), hl("t0.v3", 0.3)])
s.step("The root: 24, the sum of the whole array. Building visits each node once: Theta of n.", [mk("t0.v1"), s.take("build bottom-up: Θ(n)")])

s.scene("query")
s.step("Stage 4: to answer a query, start at the root. If a node's interval lies wholly inside the query, use its sum. If it lies wholly outside, ignore it. Otherwise ask both children.", [s.head("Stage 4 of 7: a range query"), s.untake()] + hide("t0") + show("qc") + [hl("qc[0..=2]")])
s.step("In code, the three cases are three lines. The recursion starts at the root, node 1, covering 0 to n minus 1.", hide("qc") + show("cd") + [ml("cd", 1, 5)])
s.step("Sum from 2 to 6. The root, 0 to 7, overlaps partly: go to both children.", hide("cd") + show("t0") + [rs("t0"), hl("t0.v1")])
s.step("On the left, 0 to 3 overlaps partly; its child 0 to 1 is outside, and 2 to 3 is inside: use 8.", [mk("t0.v5")])
s.step("On the right, 4 to 7 overlaps partly; 4 to 5 is inside: use 6. 6 to 7 overlaps partly; its leaf 6 is inside: use 6, and leaf 7 is outside.", [mk("t0.v6"), mk("t0.v14", 0.4)])
s.step("8 plus 6 plus 6: 20. Check: 5 plus 3 plus 4 plus 2 plus 6 is 20. At most four nodes are touched per level, so a query costs O of log n.", [s.take("whole inside: use it · outside: skip · partial: split")])

s.scene("update")
s.step("Stage 5: set A of 3 to 7, an increase of 4. Only the nodes whose intervals contain position 3 change: one per level, from the leaf up to the root.", [s.head("Stage 5 of 7: an update"), s.untake()] + hide("t0") + show("t1") + [hl("t1.v11")])
s.step("The leaf becomes 7. 2 to 3 becomes 12. 0 to 3 becomes 15. The root becomes 28.", [mk("t1.v11"), mk("t1.v5", 0.25), mk("t1.v2", 0.5), mk("t1.v1", 0.75)])
s.step("The update in code: walk down to the leaf, set it, and recompute each sum on the way back up.", hide("t1") + show("cd") + [ml("cd", 7, 11)])
s.step("Four nodes, log 2 of 8 plus 1. Every other node's interval misses position 3, so its sum is still right. An update costs O of log n.", [s.take("update: the leaf and its ancestors only")])

s.scene("ops")
s.step("Stage 6: the same tree works for any operation that combines two halves associatively. Store sums for range sums.", [s.head("Stage 6 of 7: other operations"), s.untake()] + hide("cd") + show("ops") + [hl("ops[0]")])
s.step("Store the minimum or maximum, and it answers range minimum queries.", [hl("ops[1]")])
s.step("Greatest common divisors, counts and products work the same way.", [hl("ops[2]")])
s.step("And to add a value to a whole range at once, lazy propagation stores a pending addition in a node and pushes it down only when a query needs to look inside. Range updates then cost O of log n as well.", [hl("ops[3]"), s.take("any associative operation; lazy for range updates")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("ops") + show("q") + [hl("q[0]")])
s.step("Build the sum tree, find a range sum and a range minimum, and update one element. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: pairs: 5 plus 8 is 13, 6 plus 3 is 9, 2 plus 7 is 9, 2 plus 6 is 8. Then 22 and 17. Root 39.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: sum from 1 to 5 uses leaf 1, which is 8; node 2 to 3, which is 9; and node 4 to 5, which is 9. Total 26.", [hl("qa[1]")])
s.step("c: the minimum of 8, 6, 3, 2 and 7 is 2. A minimum tree would combine the same three nodes.", [hl("qa[2]")])
s.step("d: A of 4 goes from 2 to 9, plus 7. Leaf 4 becomes 9, node 4 to 5 becomes 16, node 4 to 7 becomes 24, and the root becomes 46.", [hl("qa[3]"), mk("qa[3][2]", 0.5)])
s.step("The usual slip: splitting a query at the query's own midpoint instead of the node's. Always split at the node's midpoint.", [s.take("split by the node's interval")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A segment tree stores, for each interval obtained by halving, its sum. It is built bottom-up in Theta of n.", [hl("stages[0..=2]")])
s.step("A query combines at most a few nodes per level, an update fixes one path, both O of log n, and the idea works for minimum, maximum and lazy range updates.", [hl("stages[3..=5]")])
s.step("Next video: another array-based tree, built for priority queues. The binary heap.", [mk("stages[0..=6]"), s.take("Next: binary heaps")])

s.save("/home/claude/playlist/dsa2/d2v8.json")

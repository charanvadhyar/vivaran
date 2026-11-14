"""DSA Module 3, video 8: Kruskal's algorithm."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *
from greedy import kruskal

V = list("abcdefghi")
E = [("a", "b", 4), ("a", "h", 8), ("b", "c", 8), ("b", "h", 11), ("c", "d", 7), ("c", "f", 4), ("c", "i", 2), ("d", "e", 9), ("d", "f", 14), ("e", "f", 10), ("f", "g", 2), ("g", "h", 1), ("g", "i", 6), ("h", "i", 7)]
KL = kruskal(V, E)
assert [(a + b, ok) for a, b, w, ok in KL] == [("gh", True), ("ci", True), ("fg", True), ("ab", True), ("cf", True), ("gi", False), ("cd", True), ("hi", False), ("ah", True), ("bc", False), ("de", True), ("ef", False), ("bh", False), ("df", False)]
assert sum(w for a, b, w, ok in KL if ok) == 37 and sum(1 for x in KL if x[3]) == 8
VE = list("ABCDEF"); EE = [("A", "B", 4), ("A", "C", 4), ("B", "C", 2), ("C", "D", 3), ("C", "E", 2), ("C", "F", 4), ("D", "F", 3), ("E", "F", 3)]
EK = kruskal(VE, EE); assert sum(w for a, b, w, ok in EK if ok) == 14 and [a + b for a, b, w, ok in EK if not ok] == ["EF", "AC", "CF"]

POS = {"a": [0, 1], "b": [2, 0], "c": [4, 0], "d": [7, 0], "e": [8, 1], "f": [6, 2], "g": [4, 2], "h": [2, 2], "i": [4, 1]}
s = Script("Minimum spanning trees: Kruskal's algorithm")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Kruskal's idea: cheapest edges first"],
    [2, "Detecting a cycle: disjoint sets"],
    [3, "Cormen's example, edge by edge"],
    [4, "The algorithm"],
    [5, "Union by rank and path compression"],
    [6, "Running time; Prim or Kruskal?"],
    [7, "Exam question"]]})
s.obj({"id": "idea", "type": "table", "region": "center", "columns": ["Kruskal's idea", ""], "rows": [
    ["start", "a forest: every vertex is its own tree"],
    ["sort", "all edges by weight, smallest first"],
    ["for each edge", "if its ends are in different trees, take it: the two trees merge"],
    ["otherwise", "skip it: it would close a cycle"],
    ["why safe", "the edge is light across the cut around one of the two trees (cut property)"],
    ["stop", "after n − 1 edges: one tree"]]})
s.obj({"id": "ds", "type": "table", "region": "center", "columns": ["disjoint-set operations", ""], "rows": [
    ["MAKE-SET(v)", "a new set containing only v"],
    ["FIND-SET(v)", "the representative of v's set: its tree's root"],
    ["UNION(u, v)", "merge the two sets"],
    ["cycle test", "edge (u, v) closes a cycle exactly when FIND-SET(u) = FIND-SET(v)"]]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "label": v, "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": a, "to": b, "label": str(w)} for a, b, w in E]})
EK_ = {frozenset((a, b)): f"{a}->{b}" for a, b, w in E}
s.obj({"id": "et", "type": "table", "region": "right", "columns": ["edge", "w", "result", "edge ", "w ", "result "],
       "rows": [[f"{KL[r][0]}–{KL[r][1]}", str(KL[r][2]), "", f"{KL[r + 7][0]}–{KL[r + 7][1]}", str(KL[r + 7][2]), ""] for r in range(7)]})
def cell(k, c): return f"et[{k % 7}][{c + (3 if k >= 7 else 0)}]"
s.obj({"id": "kc", "type": "code", "region": "center", "language": "text", "lines": [
    "MST-KRUSKAL(G, w)",
    "    A = ∅",
    "    for each vertex v:  MAKE-SET(v)",
    "    sort the edges into non-decreasing order of weight w",
    "    for each edge (u, v), in that order",
    "        if FIND-SET(u) ≠ FIND-SET(v)",
    "            A = A ∪ {(u, v)}",
    "            UNION(u, v)",
    "    return A"]})
s.obj({"id": "uf", "type": "table", "region": "center", "columns": ["making the sets fast", ""], "rows": [
    ["each set", "a tree of parent pointers; the root is the representative"],
    ["union by rank", "hang the shorter tree under the taller: height stays O(log n)"],
    ["path compression", "after FIND-SET, point every node on the path straight at the root"],
    ["both together", "m operations take O(m α(n)); α grows so slowly it is ≤ 4 in practice"]]})
s.obj({"id": "rt", "type": "table", "region": "center", "columns": ["", "Kruskal", "Prim"], "rows": [
    ["sort the edges", "O(E log E) = O(E log V)", "none"],
    ["main loop", "O(E α(V)) with disjoint sets", "O(E log V) with a binary heap"],
    ["total", "O(E log V)", "O(E log V), or O(V²) with an array"],
    ["grows", "a forest that merges", "one tree"],
    ["best for", "sparse graphs, edges already sorted", "dense graphs"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["edges: A–B 4, A–C 4, B–C 2, C–D 3, C–E 2, C–F 4, D–F 3, E–F 3 (ties in this order)"],
    ["a) run Kruskal: the edges taken and skipped"],
    ["b) the MST weight"],
    ["c) for each skipped edge, the cycle it would close"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["edge", "sets before", "result"], "rows": [
    ["B–C 2, C–E 2", "all separate", "take both: {B, C, E}"],
    ["C–D 3, D–F 3", "D, F separate from {B, C, E}", "take both: {B, C, D, E, F}"],
    ["E–F 3", "E and F already together", "skip: E–C–D–F–E"],
    ["A–B 4", "A alone", "take: one tree, 5 edges"],
    ["A–C 4, C–F 4", "same set", "skip: A–B–C–A, C–D–F–C"],
    ["weight", "2 + 2 + 3 + 3 + 4", "14"]]})

s.scene("intro")
s.step("Prim grows one tree outward from a start vertex. Kruskal takes the opposite view: forget the start, look at the cheapest connections anywhere in the graph, and keep every one that does not close a loop. On the same graph, it finds a minimum spanning tree of the same weight.", [s.head("Minimum spanning trees: Kruskal's algorithm")])
s.step("Here are the seven stages.", show("stages"))
s.step("Kruskal's idea, detecting cycles with disjoint sets, and Cormen's example edge by edge.", [hl("stages[0..=2]")])
s.step("Then the algorithm, making the sets fast, the running time compared with Prim, and an exam question.", [hl("stages[3..=6]")])

s.scene("idea")
s.step("Stage 1: start with a forest: every vertex is a tree on its own.", [s.head("Stage 1 of 7: cheapest edges first")] + hide("stages") + show("idea") + [hl("idea[0]")])
s.step("Sort all the edges by weight, smallest first.", [hl("idea[1]")])
s.step("Go through them in order. If an edge joins two different trees, take it: the two trees merge into one.", [hl("idea[2]")])
s.step("If both ends are already in the same tree, skip it: it would close a cycle.", [hl("idea[3]")])
s.step("Why is a taken edge safe? Draw the cut around one of the two trees it joins. No chosen edge crosses that cut, and this is the cheapest edge that does, because every cheaper edge was already considered. The cut property says it belongs to some MST.", [hl("idea[4]")])
s.step("After n minus 1 edges, the forest is a single tree.", [hl("idea[5]"), s.take("sort edges; take each that joins two trees")])

s.scene("ds")
s.step("Stage 2: how do we test whether two vertices are already in the same tree? With the disjoint-set structure. MAKE-SET starts a set holding one vertex.", [s.head("Stage 2 of 7: disjoint sets"), s.untake()] + hide("idea") + show("ds") + [hl("ds[0]")])
s.step("FIND-SET returns a representative of a vertex's set. Two vertices are in the same set exactly when their representatives match.", [hl("ds[1]")])
s.step("UNION merges two sets into one.", [hl("ds[2]")])
s.step("So edge u, v closes a cycle exactly when FIND-SET of u equals FIND-SET of v.", [hl("ds[3]"), s.take("same representative ⇒ cycle")])
s.step("Why not just search the tree for a path from u to v? That works, but costs O of V per edge. Disjoint sets make the test almost free.", [hl("ds[3]")])

s.scene("trace")
s.step("Stage 3: Cormen's graph again, the one Prim gave weight 37. Here are its 14 edges, sorted by weight.", [s.head("Stage 3 of 7: edge by edge"), s.untake()] + hide("ds") + show("g", "et"))
say = {0: "g, h, weight 1: different trees. Take it.",
       1: "c, i, weight 2: take it.",
       2: "f, g, weight 2: take it. Now f, g and h form one tree.",
       3: "a, b, weight 4: take it.",
       4: "c, f, weight 4: c's tree is c and i; f's is f, g, h. Different: take it. They merge into c, f, g, h, i.",
       5: "g, i, weight 6: g and i are now in the same tree, through f and c. Skip: it would close a cycle.",
       6: "c, d, weight 7: d is alone. Take it.",
       7: "h, i, weight 7: same tree. Skip.",
       8: "a, h, weight 8: a's tree is a, b; h's is the big one. Take it. Prim used b, c here; with the tie, either works.",
       9: "b, c, weight 8: now b and c are in the same tree. Skip.",
       10: "d, e, weight 9: e is alone. Take it. That is the eighth edge: one tree.",
       11: "The rest, e, f, b, h and d, f, would all close cycles. The algorithm can stop as soon as it has n minus 1 edges."}
for k in range(11):
    a, b, w, ok = KL[k]; e = EK_[frozenset((a, b))]
    acts = [hl(cell(k, 0)), hl(cell(k, 1))]
    acts += [mk(f"g.{e}", 0.4), mk(f"g.{a}", 0.4), mk(f"g.{b}", 0.4), st(cell(k, 2), "take", 0.5), mk(cell(k, 2), 0.6)] if ok else [hl(f"g.{e}", 0.3), st(cell(k, 2), "skip", 0.5), dim(cell(k, 2), 0.7)]
    s.step(say[k], acts)
s.step(say[11], [x for k in (11, 12, 13) for x in (st(cell(k, 2), "—", 0.1 * (k - 11)), dim(cell(k, 0), 0.3), dim(cell(k, 1), 0.3))])
s.step("Look at how the forest grew: first scattered pieces, g, h, then c, i, then a, b, which only joined the rest at the end. Kruskal never needs the edges it takes to be connected along the way.", [hl("g.a->h")])
s.step("Total: 1, 2, 2, 4, 4, 7, 8 and 9: 37, the same as Prim, though one edge differs.", [s.take("MST weight 37, as with Prim")])

s.scene("algo")
s.step("Stage 4: Cormen's MST-KRUSKAL. Start with an empty edge set A, and make every vertex its own set.", [s.head("Stage 4 of 7: the algorithm"), s.untake()] + hide("g", "et") + show("kc") + [ml("kc", 1, 3)])
s.step("Sort the edges by weight.", [ml("kc", 4, 4)])
s.step("For each edge in that order: if its ends are in different sets, add it to A and unite the sets.", [ml("kc", 5, 8)])
s.step("Return A. It is a minimum spanning tree.", [ml("kc", 9, 9), s.take("sort, then find-find-union")])

s.scene("uf")
s.step("Stage 5: the sets are stored as trees of parent pointers. The root of each tree is its representative.", [s.head("Stage 5 of 7: fast disjoint sets"), s.untake()] + hide("kc") + show("uf") + [hl("uf[0]")])
s.step("Union by rank: when merging, hang the shorter tree under the root of the taller one. Heights stay logarithmic.", [hl("uf[1]")])
s.step("Path compression: after a FIND-SET walks up to the root, point every node it passed straight at the root. The next search is immediate.", [hl("uf[2]")])
s.step("For example, if d points to c, c to b, and b to the root a, FIND-SET of d walks three steps. Afterwards d, c and b all point directly at a, so finding any of them again takes one step.", [hl("uf[2]")])
s.step("Together, any sequence of m operations takes O of m times alpha of n, where alpha is the inverse Ackermann function: at most 4 for any input that fits in the universe.", [hl("uf[3]"), s.take("union by rank + path compression: ≈ constant")])

s.scene("rt")
s.step("Stage 6: Kruskal's cost is dominated by sorting the edges: O of E log E, which is the same as O of E log V, since E is at most V squared.", [s.head("Stage 6 of 7: Prim or Kruskal?"), s.untake()] + hide("uf") + show("rt") + [hl("rt[0]")])
s.step("The loop over the edges is nearly linear with fast disjoint sets. Prim with a binary heap is also O of E log V.", [hl("rt[1..=2]")])
s.step("Prim grows one tree; Kruskal merges a forest.", [hl("rt[3]")])
s.step("Kruskal suits sparse graphs, especially if the edges come already sorted. Prim with a plain array, at O of V squared, suits dense graphs.", [hl("rt[4]"), s.take("both O(E log V); Kruskal sparse, Prim dense")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("rt") + show("q") + [hl("q[0]")])
s.step("Run Kruskal, give the weight, and name the cycle each skipped edge would close. Pause and work it out.", [hl("q[1..=3]")])
s.step("The two edges of weight 2, B, C and C, E, join separate vertices: take both. B, C and E form one tree.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Weight 3: C, D joins D; D, F joins F. Take both.", [hl("qa[1]")])
s.step("E, F, weight 3: E and F are already connected, through C and D. Skip: it would close the cycle E, C, D, F.", [hl("qa[2]")])
s.step("A, B, weight 4: A is alone. Take it. Five edges for six vertices: done.", [hl("qa[3]")])
s.step("A, C and C, F would close the cycles A, B, C and C, D, F. The MST weighs 2 plus 2 plus 3 plus 3 plus 4: 14.", [hl("qa[4..=5]"), mk("qa[5][2]", 0.5)])
s.step("The usual slip: skipping an edge just because both ends already have edges. The test is whether they are in the same tree, not whether they are touched.", [s.take("skip only if both ends share a tree")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Kruskal sorts the edges and takes each one that joins two different trees; a disjoint-set structure answers that question in near-constant time.", [hl("stages[0..=4]")])
s.step("It runs in O of E log V, like Prim, and finds a tree of the same minimum weight.", [hl("stages[5]")])
s.step("Next video: greedy for compression. Huffman coding builds the best prefix code by merging the two rarest symbols.", [mk("stages[0..=6]"), s.take("Next: Huffman coding")])

s.save("/home/claude/playlist/dsa3/d3v8.json")

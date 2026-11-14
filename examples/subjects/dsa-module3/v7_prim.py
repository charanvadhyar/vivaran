"""DSA Module 3, video 7: minimum spanning trees, Prim's algorithm."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *
from greedy import prim, kruskal, INF

V = list("abcdefghi")
E = [("a", "b", 4), ("a", "h", 8), ("b", "c", 8), ("b", "h", 11), ("c", "d", 7), ("c", "f", 4), ("c", "i", 2), ("d", "e", 9), ("d", "f", 14), ("e", "f", 10), ("f", "g", 2), ("g", "h", 1), ("g", "i", 6), ("h", "i", 7)]
PAR, LOG = prim(V, E, "a")
assert [l[0] for l in LOG] == list("abcifghde") and sum(l[1] for l in LOG) == 37
assert [l[1] for l in LOG] == [0, 4, 8, 2, 4, 2, 1, 7, 9]
VE = list("ABCDE"); EE = [("A", "B", 2), ("A", "D", 6), ("B", "C", 3), ("B", "D", 8), ("B", "E", 5), ("C", "E", 7), ("D", "E", 9)]
EP, EL = prim(VE, EE, "A"); assert [l[0] for l in EL] == list("ABCED") and sum(l[1] for l in EL) == 16
assert 4 + 8 + 2 + 4 + 2 + 1 + 7 + 9 == 37 and 9 ** 7 == 4782969

POS = {"a": [0, 1], "b": [2, 0], "c": [4, 0], "d": [7, 0], "e": [8, 1], "f": [6, 2], "g": [4, 2], "h": [2, 2], "i": [4, 1]}
ekey = {}
for a, b, w in E: ekey[frozenset((a, b))] = f"{a}->{b}"
s = Script("Minimum spanning trees: Prim's algorithm")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Spanning trees and the MST problem"],
    [2, "The cut property: why greedy works"],
    [3, "Prim's idea: grow one tree"],
    [4, "Cormen's example, step by step"],
    [5, "The algorithm with a priority queue"],
    [6, "Running time"],
    [7, "Exam question"]]})
s.obj({"id": "mst", "type": "table", "region": "center", "columns": ["minimum spanning tree", ""], "rows": [
    ["connected, undirected graph", "every edge has a weight (a cost)"],
    ["spanning tree", "connects all n vertices using n − 1 edges, no cycles"],
    ["minimum spanning tree (MST)", "the spanning tree of least total weight"],
    ["uses", "laying cable or pipes, road networks, clustering, approximating TSP (Module 5)"],
    ["brute force", "a complete graph on 9 vertices has 9⁷ = 4,782,969 spanning trees"]]})
s.obj({"id": "cut", "type": "table", "region": "center", "columns": ["the cut property", ""], "rows": [
    ["cut", "split the vertices into two groups, S and V − S"],
    ["crossing edge", "one end in each group"],
    ["light edge", "a crossing edge of least weight"],
    ["property", "if no tree edge chosen so far crosses the cut, a light edge is safe: some MST contains it"],
    ["why", "an MST without it must cross the cut elsewhere; swap that edge for the light one: no heavier"]]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "label": v, "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": a, "to": b, "label": str(w)} for a, b, w in E]})
s.obj({"id": "kt", "type": "table", "region": "right", "columns": ["vertex", "key", "π", "in tree"],
       "rows": [[v, "0" if v == "a" else "∞", "nil", ""] for v in V]})
s.obj({"id": "pc", "type": "code", "region": "center", "language": "text", "lines": [
    "MST-PRIM(G, w, r)",
    "    for each vertex u:  u.key = ∞;  u.π = nil",
    "    r.key = 0",
    "    Q = all vertices                       // a min-priority queue on key",
    "    while Q is not empty",
    "        u = EXTRACT-MIN(Q)                 // cheapest vertex to attach",
    "        for each v adjacent to u",
    "            if v is in Q and w(u, v) < v.key",
    "                v.π = u;  v.key = w(u, v)  // DECREASE-KEY",
    "",
    "the tree: the edges (v, v.π) for every v ≠ r"]})
s.obj({"id": "rt", "type": "table", "region": "center", "columns": ["Q implemented as", "EXTRACT-MIN × V", "DECREASE-KEY × E", "total"], "rows": [
    ["plain array (scan for the minimum)", "O(V) each", "O(1) each", "O(V²): best for dense graphs"],
    ["binary heap", "O(log V) each", "O(log V) each", "O(E log V)"],
    ["Fibonacci heap", "O(log V) amortised", "O(1) amortised", "O(E + V log V)"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["edges: A–B 2, A–D 6, B–C 3, B–D 8, B–E 5, C–E 7, D–E 9"],
    ["a) run Prim from A: the order vertices join, and each one's edge"],
    ["b) the weight of the MST"],
    ["c) would the MST change if the edge B–D weighed 1?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["step", "keys of the vertices not yet in the tree", "joins"], "rows": [
    ["start", "A 0", "A"],
    ["after A", "B 2, D 6, C ∞, E ∞", "B, by A–B 2"],
    ["after B", "C 3, E 5, D 6 (B–D 8 is worse)", "C, by B–C 3"],
    ["after C", "E 5 (C–E 7 is worse), D 6", "E, by B–E 5;  then D, by A–D 6"],
    ["b)", "2 + 3 + 5 + 6", "16"],
    ["c)", "B–D 1 would replace A–D 6", "yes: 2 + 3 + 5 + 1 = 11"]]})

def addv(k, d0=0.0):
    u, key, p, up = LOG[k]; i = V.index(u); out = [mk(f"g.{u}", d0), st(f"kt[{i}][3]", "✓", d0 + 0.1), mk(f"kt[{i}]", d0 + 0.1)]
    if p: out.append(mk(f"g.{ekey[frozenset((u, p))]}", d0))
    dd = d0 + 0.35
    for v, w in up:
        j = V.index(v); out += [st(f"kt[{j}][1]", str(w), round(dd, 2)), st(f"kt[{j}][2]", u, round(dd + 0.05, 2)), hl(f"g.{ekey[frozenset((u, v))]}", round(dd, 2))]; dd += 0.1
    return out

s.scene("intro")
s.step("A company wants to connect nine towns with fibre cable. Each possible link has a cost. It must reach every town, but needs no redundant loops. Which links should it lay? That is the minimum spanning tree problem, and Prim's greedy algorithm solves it.", [s.head("Minimum spanning trees: Prim's algorithm")])
s.step("Here are the seven stages.", show("stages"))
s.step("Spanning trees, the cut property that makes greedy work, Prim's idea, and a full example.", [hl("stages[0..=3]")])
s.step("Then the algorithm with a priority queue, its running time, and an exam question.", [hl("stages[4..=6]")])

s.scene("mst")
s.step("Stage 1: take a connected, undirected graph with a weight on every edge.", [s.head("Stage 1 of 7: spanning trees")] + hide("stages") + show("mst") + [hl("mst[0]")])
s.step("A spanning tree connects all n vertices with exactly n minus 1 edges, and has no cycles.", [hl("mst[1]")])
s.step("A minimum spanning tree is one whose total weight is as small as possible. There may be more than one.", [hl("mst[2]")])
s.step("It shows up in network design, in clustering data, and later in this course, inside an approximation for the travelling salesman.", [hl("mst[3]")])
s.step("Trying every spanning tree is hopeless: a complete graph on just 9 vertices has nearly 5 million of them.", [hl("mst[4]"), s.take("MST: connect all, n − 1 edges, least weight")])

s.scene("cut")
s.step("Stage 2: why can a greedy choice be safe? Split the vertices into two groups, S and the rest. That is a cut.", [s.head("Stage 2 of 7: the cut property"), s.untake()] + hide("mst") + show("cut") + [hl("cut[0]")])
s.step("An edge crosses the cut if its ends are in different groups. A crossing edge of least weight is called a light edge.", [hl("cut[1..=2]")])
s.step("The cut property: if none of the edges chosen so far crosses the cut, then a light edge across it is safe: some minimum spanning tree contains it.", [hl("cut[3]")])
s.step("The reason: any spanning tree must cross the cut somewhere. If an MST crosses with a heavier edge, swap it for the light edge: still a spanning tree, and no heavier.", [hl("cut[4]"), s.take("the lightest edge across a cut is safe")])
s.step("Both MST algorithms in this module are this one rule, applied to different cuts. Prim uses the cut around its growing tree; Kruskal, next video, uses the cut around one of its forest's pieces.", [hl("cut[3]")])

s.scene("idea")
s.step("Stage 3: Prim's idea. Grow a single tree from a starting vertex. The cut is always: the tree, against everything else.", [s.head("Stage 3 of 7: grow one tree"), s.untake()] + hide("cut") + show("g", "kt"))
s.step("At each step, add the lightest edge leaving the tree. By the cut property, that edge is safe.", [hl("g.a")])
s.step("To find that edge quickly, each vertex outside the tree keeps a key: the weight of its cheapest edge into the tree so far, and π, the tree vertex at the other end. The start, a, has key 0; the others, infinity.", [hl("kt[0]"), s.take("key = cheapest edge into the tree")])

s.scene("trace")
say = ["Stage 4: start at a, key 0. Its neighbours get keys: b 4, h 8.",
       "The smallest key outside the tree is b, 4: add b with edge a, b. b offers c a key of 8. h stays at 8: b to h is 11, worse.",
       "c and h tie at 8; take c, by edge b, c. c lowers d to 7, f to 4, and i to 2.",
       "The smallest key is i, 2: add edge c, i. i lowers g to 6 and h to 7.",
       "Next, f with key 4, by edge c, f. f lowers g to 2, and gives e a key of 10.",
       "g, key 2, by edge f, g. g lowers h to 1.",
       "h, key 1, by edge g, h. Its other neighbours are already in the tree.",
       "d, key 7, by edge c, d. d lowers e from 10 to 9.",
       "Finally e, key 9, by edge d, e. Every vertex is in the tree."]
for k in range(len(LOG)):
    acts = addv(k)
    if k == 0: acts = [s.head("Stage 4 of 7: Cormen's example"), s.untake()] + acts
    s.step(say[k], acts)
s.step("Eight edges for nine vertices. Total weight: 4, 8, 2, 4, 2, 1, 7 and 9: 37. That is the minimum.", [s.take("MST weight 37")])
s.step("At the tie between c and h, both at 8, choosing h instead would have used edge a, h in place of b, c. Same total, 37: a graph can have several minimum spanning trees, but they all weigh the same.", [hl("g.a->h"), hl("g.b->c", 0.5)])
s.step("Notice how the keys did the work: each vertex remembered its cheapest connection, and lowered it whenever the tree grew closer.", [hl("kt")])

s.scene("algo")
s.step("Stage 5: Cormen's MST-PRIM. Every key starts at infinity, except the root's, 0.", [s.head("Stage 5 of 7: the algorithm"), s.untake()] + hide("g", "kt") + show("pc") + [ml("pc", 1, 3)])
s.step("All vertices go into a min-priority queue, ordered by key.", [ml("pc", 4, 4)])
s.step("Repeatedly extract the vertex with the smallest key: it joins the tree by the edge to its π.", [ml("pc", 5, 6)])
s.step("Then update its neighbours still outside: if the new edge is cheaper than a neighbour's key, lower the key and set π. That is DECREASE-KEY.", [ml("pc", 7, 9)])
s.step("Why check that v is still in Q? A vertex already in the tree must never be re-attached: its edge is final. Without the check, a later edge could overwrite the parent of a vertex already in the tree, and the tree would fall apart.", [ml("pc", 8, 8)])
s.step("At the end, the tree is the set of edges from each vertex to its π.", [ml("pc", 11, 11), s.take("extract-min, then decrease-key the neighbours")])

s.scene("rt")
s.step("Stage 6: the cost depends on the priority queue. V extractions, and up to E key decreases.", [s.head("Stage 6 of 7: running time"), s.untake()] + hide("pc") + show("rt"))
s.step("With a plain array, finding the minimum takes a scan of V, so O of V squared in all. Simple, and the best choice for dense graphs.", [hl("rt[0]")])
s.step("With a binary heap, both operations take log V: O of E log V. Better for sparse graphs.", [hl("rt[1]")])
s.step("A Fibonacci heap brings decrease-key down to constant amortised time: O of E plus V log V.", [hl("rt[2]"), s.take("array O(V²) · heap O(E log V)")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("rt") + show("q") + [hl("q[0]")])
s.step("Run Prim from A, give the MST weight, and see what one changed weight does. Pause and work it out.", [hl("q[1..=3]")])
s.step("Start at A. Its neighbours get keys: B 2, D 6.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("B joins by A, B, weight 2. It offers C 3 and E 5; its edge to D, 8, is worse than D's key 6.", [hl("qa[2]")])
s.step("C joins by B, C, weight 3. Its edge to E, 7, is worse than 5. Then E joins by B, E, 5, and D by A, D, 6.", [hl("qa[3]")])
s.step("b: 2 plus 3 plus 5 plus 6: 16.", [hl("qa[4]"), mk("qa[4][2]", 0.4)])
s.step("c: if B, D weighed 1, D's key would drop to 1 when B joins, and that edge would replace A, D. The weight becomes 11.", [hl("qa[5]")])
s.step("The usual slip: taking the cheapest edge out of the most recent vertex only. Prim takes the cheapest edge out of the whole tree.", [s.take("cheapest edge leaving the whole tree")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A minimum spanning tree connects every vertex at least total weight. The lightest edge across any cut is safe, and Prim grows one tree by always adding the lightest edge leaving it.", [hl("stages[0..=3]")])
s.step("Keys in a priority queue make that fast: O of V squared with an array, O of E log V with a heap.", [hl("stages[4..=5]")])
s.step("Next video: the same problem from the other direction. Kruskal's algorithm sorts the edges and joins forests.", [mk("stages[0..=6]"), s.take("Next: Kruskal's algorithm")])

s.save("/home/claude/playlist/dsa3/d3v7.json")

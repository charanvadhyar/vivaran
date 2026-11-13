"""DSA Module 2, video 14: Bellman-Ford."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from bf import bellman_ford, INF

V = list("stxyz"); E = [("t", "x", 5), ("t", "y", 8), ("t", "z", -4), ("x", "t", -2), ("y", "x", -3), ("y", "z", 9), ("z", "x", 7), ("z", "s", 2), ("s", "t", 6), ("s", "y", 7)]
d, p, PS, neg = bellman_ford(V, E, "s")
fmt = lambda x: "∞" if x == INF else str(x)
rows = [[fmt(q[0][v]) for v in V] for q in PS]
assert rows == [["0", "6", "∞", "7", "∞"], ["0", "6", "4", "7", "2"], ["0", "2", "4", "7", "2"], ["0", "2", "4", "7", "-2"]] and not neg
assert p == {"s": None, "t": "x", "x": "y", "y": "s", "z": "t"}
V2 = list("ABCD"); E2 = [("A", "B", 4), ("A", "C", 5), ("B", "C", -3), ("C", "D", 2), ("B", "D", 6)]
d2, p2, ps2, n2 = bellman_ford(V2, E2, "A"); assert d2 == {"A": 0, "B": 4, "C": 1, "D": 3} and not n2 and len(ps2) == 2
d3, _, ps3, n3 = bellman_ford(V2, E2 + [("D", "B", -1)], "A"); assert n3 and -3 + 2 - 1 == -2
assert 5 * 10 == 50

POS = {"s": [0, 1], "t": [1, 0], "x": [4, 0], "y": [1, 2], "z": [3, 2]}
s = Script("Bellman-Ford")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Shortest paths with weights"],
    [2, "Relaxing an edge"],
    [3, "The algorithm"],
    [4, "Cormen's example, pass by pass"],
    [5, "Why n − 1 passes are enough"],
    [6, "Detecting a negative cycle"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["single-source shortest paths", ""], "rows": [
    ["input", "a directed graph with edge weights, and a source s"],
    ["output", "for every v, the least total weight of a path s ⇝ v"],
    ["BFS", "counts edges only: wrong once weights differ"],
    ["Dijkstra", "fast, but needs all weights ≥ 0"],
    ["negative weights happen", "refunds, gains, exchange rates, time differences"],
    ["a negative cycle reachable from s", "no shortest path at all: go round it again and again"]]})
s.obj({"id": "rx", "type": "code", "region": "center", "language": "text", "lines": [
    "RELAX(u, v, w)",
    "    if v.d > u.d + w(u, v)          // a cheaper way into v, through u?",
    "        v.d = u.d + w(u, v)",
    "        v.π = u",
    "",
    "BELLMAN-FORD(G, w, s)",
    "    every v.d = ∞, v.π = nil;  s.d = 0",
    "    repeat n − 1 times",
    "        for each edge (u, v): RELAX(u, v, w)",
    "    for each edge (u, v)",
    "        if v.d > u.d + w(u, v): return FALSE    // negative cycle",
    "    return TRUE"]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": True,
       "nodes": [{"id": v, "label": f"{v} {'0' if v == 's' else '∞'}", "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": a, "to": b, "label": str(w)} for a, b, w in E]})
s.obj({"id": "pt", "type": "table", "region": "right", "columns": ["after pass", "s", "t", "x", "y", "z"], "rows": [["0", "0", "∞", "∞", "∞", "∞"]] + [[str(i + 1), "", "", "", "", ""] for i in range(4)]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["why n − 1 passes", ""], "rows": [
    ["a shortest path (no negative cycle)", "never repeats a vertex: at most n − 1 edges"],
    ["after pass k", "every vertex whose shortest path has ≤ k edges has its final d"],
    ["the path s → y → x → t → z", "4 edges: fixed by pass 4"],
    ["cost", "n − 1 passes × m edges: O(n m)"],
    ["early stop", "a pass that changes nothing means all d are final"]]})
s.obj({"id": "nc", "type": "table", "region": "center", "columns": ["the extra pass", ""], "rows": [
    ["after n − 1 passes", "with no negative cycle, no edge can still be relaxed"],
    ["if some edge can still be relaxed", "a reachable negative cycle exists: report it"],
    ["example", "add D → B, −1, to the exam graph: cycle B → C → D → B weighs −3 + 2 − 1 = −2"],
    ["Dijkstra", "O((n + m) log n), but cannot handle negative edges at all"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: source A"], "rows": [
    ["edges in this order: A→B 4, A→C 5, B→C −3, C→D 2, B→D 6"],
    ["a) d after each pass   b) the shortest path to D and its weight"],
    ["c) add the edge D→B with weight −1: what does Bellman-Ford report?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a) pass 1", "B = 4; C = min(5, 4 − 3) = 1; D = min(1 + 2, 4 + 6) = 3", "A 0, B 4, C 1, D 3"],
    ["a) pass 2", "nothing changes: stop early", "same"],
    ["b)", "π: D ← C ← B ← A", "A → B → C → D, weight 3"],
    ["c)", "cycle B → C → D → B: −3 + 2 − 1 = −2 < 0", "a negative cycle: FALSE"]]})

def apply(k):
    prev = PS[k - 1][0] if k else {v: (0 if v == "s" else INF) for v in V}; cur = PS[k][0]; out = []; dd = 0.0
    for j, v in enumerate(V):
        out.append(st(f"pt[{k + 1}][{j + 1}]", fmt(cur[v]), round(0.05 * j, 2)))
        if cur[v] != prev[v]:
            out.append(st(f"g.{v}", f"{v} {fmt(cur[v])}", round(0.4 + dd, 2))); dd += 0.1
    return out

s.scene("intro")
s.step("BFS finds the fewest hops. But when links have costs, the cheapest route may use more of them, and some costs may even be negative. Bellman-Ford finds the cheapest routes anyway, and tells you when no cheapest route can exist. This video traces Cormen's example pass by pass.", [s.head("Bellman-Ford")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem, relaxing an edge, the algorithm, and the example.", [hl("stages[0..=3]")])
s.step("Then why n minus 1 passes suffice, negative cycles, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: given a directed graph with weights and a source s, find for every vertex the least total weight of a path from s.", [s.head("Stage 1 of 7: weighted shortest paths")] + hide("stages") + show("pb") + [hl("pb[0..=1]")])
s.step("BFS only counts edges, so it fails as soon as weights differ.", [hl("pb[2]")])
s.step("Dijkstra's algorithm is faster, but it assumes no edge is negative.", [hl("pb[3]")])
s.step("Negative weights do occur: a refund on a route, a gain in currency exchange, a time-zone change.", [hl("pb[4]")])
s.step("And if a cycle of negative total weight is reachable, there is no shortest path at all: going round it once more always lowers the cost.", [hl("pb[5]"), s.take("negative edges allowed, negative cycles detected")])

s.scene("relax")
s.step("Stage 2: every vertex keeps an estimate d, the best total weight found so far, and π, the vertex it came from.", [s.head("Stage 2 of 7: relaxing an edge"), s.untake()] + hide("pb") + show("rx") + [ml("rx", 1, 1)])
s.step("Relaxing the edge u to v asks: is going through u cheaper than v's current estimate? If so, lower v's estimate and record u as its parent.", [ml("rx", 2, 4)])
s.step("Estimates only ever go down, and never below the true distance. Shortest-path algorithms differ only in which edges they relax, and in what order.", [s.take("relax: d(v) = min(d(v), d(u) + w)")])

s.scene("algo")
s.step("Stage 3: Bellman-Ford starts with every estimate infinite, except the source at 0.", [s.head("Stage 3 of 7: the algorithm"), s.untake(), ml("rx", 6, 7)])
s.step("Then it relaxes every edge, in a fixed order, and repeats that whole pass n minus 1 times.", [ml("rx", 8, 9)])
s.step("Finally, one more check over every edge: if any can still be relaxed, there is a negative cycle.", [ml("rx", 10, 12), s.take("n − 1 passes over all edges, then one check")])

s.scene("trace")
s.step("Stage 4: Cormen's example: five vertices, ten edges, two of them negative, minus 4 and minus 3, and one more, minus 2. The source is s. Each pass relaxes the edges starting with t to x and ending with s to t, then s to y.", [s.head("Stage 4 of 7: pass by pass"), s.untake()] + hide("rx") + show("g", "pt") + [hl("pt[0]")])
s.step("Pass 1: early edges leave from vertices still at infinity, so nothing happens until the last two: s to t gives t 6, s to y gives y 7.", apply(0) + [hl("pt[1]", 0.6)])
s.step("Pass 2: t to z gives z 6 minus 4, 2. y to x gives x 7 minus 3, 4.", apply(1) + [hl("pt[2]", 0.6)])
s.step("Pass 3: x to t gives t 4 minus 2, 2: cheaper than 6, through s, y, x.", apply(2) + [hl("pt[3]", 0.6)])
s.step("Pass 4: t to z now gives z 2 minus 4, minus 2. Final: s 0, t 2, x 4, y 7, z minus 2.", apply(3) + [hl("pt[4]", 0.6), mk("pt[4]", 0.8)])
s.step("Follow the parents back from z: z came from t, t from x, x from y, y from s. The cheapest route s, y, x, t, z uses 4 edges, where the direct-looking s, t, z costs 2.", [hl("g.z"), hl("g.t", 0.25), hl("g.x", 0.5), hl("g.y", 0.75), s.take("π gives the routes; d the costs")])

s.scene("why")
s.step("Stage 5: why n minus 1 passes? Without a negative cycle, a shortest path never repeats a vertex, so it has at most n minus 1 edges.", [s.head("Stage 5 of 7: why n − 1 passes"), s.untake()] + hide("g", "pt") + show("why") + [hl("why[0]")])
s.step("Pass 1 fixes every vertex whose best path has 1 edge; pass 2, those with 2 edges, because the path's first edge was already right; and so on.", [hl("why[1]")])
s.step("z's path has 4 edges, so it settled on pass 4, the last one needed with 5 vertices.", [hl("why[2]")])
s.step("Cost: n minus 1 passes over m edges, O of n times m. And if a pass changes nothing, everything is final and the loop can stop early.", [hl("why[3..=4]"), s.take("pass k fixes paths of ≤ k edges")])

s.scene("neg")
s.step("Stage 6: after n minus 1 passes, if there is no negative cycle, no edge can be relaxed any more.", [s.head("Stage 6 of 7: negative cycles"), s.untake()] + hide("why") + show("nc") + [hl("nc[0]")])
s.step("So one extra pass is a test: if any edge still improves an estimate, a negative cycle is reachable from the source, and Bellman-Ford returns false.", [hl("nc[1]")])
s.step("For example, a cycle B, C, D, B with weights minus 3, 2 and minus 1 totals minus 2: the estimates on it would fall forever.", [hl("nc[2]")])
s.step("Dijkstra, in Module 3, is faster, O of n plus m, times log n, but cannot handle negative edges at all. Bellman-Ford is the general tool.", [hl("nc[3]"), s.take("still improving after n − 1 passes ⇒ negative cycle")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("nc") + show("q") + [hl("q[0]")])
s.step("Run Bellman-Ford from A, give the shortest path to D, and decide what happens when one more edge is added. Pause and work it out.", [hl("q[1..=2]")])
s.step("Pass 1, in the given order: B becomes 4. C becomes 5, then 4 minus 3, which is 1. D becomes 1 plus 2, 3; the edge B to D offers 10, worse.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Pass 2 changes nothing, so the algorithm can stop: A 0, B 4, C 1, D 3.", [hl("qa[1]")])
s.step("b: following parents from D: C, then B, then A. The path A, B, C, D, weight 4 minus 3 plus 2, 3.", [hl("qa[2]")])
s.step("c: with D to B at minus 1, the cycle B, C, D, B weighs minus 2. The final check finds an edge still relaxable, so Bellman-Ford returns false: a negative cycle.", [hl("qa[3]"), mk("qa[3][2]", 0.5)])
s.step("The usual slip: stopping after one pass because the edges happened to be in a lucky order. In general you need up to n minus 1 passes, or a pass with no change.", [s.take("stop only after n − 1 passes, or a quiet pass")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Weighted shortest paths need relaxation: lower v's estimate whenever u offers a cheaper way in. Bellman-Ford relaxes every edge, n minus 1 times.", [hl("stages[0..=3]")])
s.step("Pass k fixes paths of up to k edges, so n minus 1 passes suffice, in O of n m time, and one extra pass detects negative cycles.", [hl("stages[4..=5]")])
s.step("Next video: pushing as much as possible through a network. Maximum flow and the Ford-Fulkerson method.", [mk("stages[0..=6]"), s.take("Next: Ford-Fulkerson")])

s.save("/home/claude/playlist/dsa2/d2v14.json")

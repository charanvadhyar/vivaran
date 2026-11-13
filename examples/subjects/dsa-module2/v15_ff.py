"""DSA Module 2, video 15: Ford-Fulkerson (and Edmonds-Karp)."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from flow import edmonds_karp

V = list("sabcdt")
CAP = {("s", "a"): 10, ("s", "b"): 10, ("a", "b"): 2, ("a", "c"): 4, ("a", "d"): 8, ("b", "d"): 9, ("c", "t"): 10, ("d", "c"): 6, ("d", "t"): 10}
val, F, LOG, S = edmonds_karp(V, CAP, "s", "t")
assert val == 19 and S == {"s", "b"}
assert LOG == [(list("sact"), 4), (list("sadt"), 6), (list("sbdt"), 4), (list("sbdct"), 5)]
assert sum(c for (u, w), c in CAP.items() if u in S and w not in S) == 19
# the small cancelling example
CS = {("s", "a"): 2, ("s", "b"): 2, ("a", "b"): 2, ("a", "t"): 2, ("b", "t"): 2}
assert edmonds_karp(list("sabt"), CS, "s", "t")[0] == 4
# the bad case
BAD = {("s", "u"): 1000, ("s", "v"): 1000, ("u", "v"): 1, ("u", "t"): 1000, ("v", "t"): 1000}
bv, _, blog, _ = edmonds_karp(list("suvt"), BAD, "s", "t"); assert bv == 2000 and len(blog) == 2
# exam
VE = list("sABCt"); CE = {("s", "A"): 6, ("s", "B"): 8, ("A", "B"): 3, ("A", "C"): 4, ("B", "C"): 5, ("A", "t"): 3, ("C", "t"): 9}
ev, ef, elog, es = edmonds_karp(VE, CE, "s", "t")
assert ev == 11 and es == {"s", "B"} and elog == [(list("sAt"), 3), (list("sACt"), 3), (list("sBCt"), 5)]
assert CE[("s", "A")] + CE[("B", "C")] == 11

POS = {"s": [0, 1], "a": [1, 0], "b": [1, 2], "c": [3, 0], "d": [3, 2], "t": [4, 1]}
s = Script("Maximum flow: Ford-Fulkerson")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Flow networks"],
    [2, "Residual network and augmenting paths"],
    [3, "Cancelling flow: why backward edges matter"],
    [4, "The Ford-Fulkerson method"],
    [5, "A full trace, path by path"],
    [6, "Max-flow min-cut"],
    [7, "Running time, and Edmonds-Karp"],
    [8, "Exam question"]]})
s.obj({"id": "fd", "type": "table", "region": "center", "columns": ["flow network", ""], "rows": [
    ["graph", "directed; a source s and a sink t"],
    ["capacity c(u, v) ≥ 0", "the most that edge (u, v) can carry"],
    ["capacity constraint", "0 ≤ f(u, v) ≤ c(u, v)"],
    ["flow conservation", "at every vertex except s and t: flow in = flow out"],
    ["value |f|", "net flow out of s  (= net flow into t)"],
    ["maximum-flow problem", "find a flow of largest value"]]})
s.obj({"id": "rd", "type": "table", "region": "center", "columns": ["residual capacity c_f(u, v)", ""], "rows": [
    ["(u, v) is an edge", "c(u, v) − f(u, v): room left to push forward"],
    ["(v, u) is an edge", "f(v, u): flow we may cancel, by pushing back"],
    ["residual network G_f", "every pair with c_f > 0"],
    ["augmenting path", "a simple path s ⇝ t in G_f"],
    ["bottleneck c_f(p)", "the least residual capacity on the path"]]})
s.obj({"id": "fn", "type": "diagram", "region": "left", "layout": "grid", "directed": True,
       "nodes": [{"id": v, "label": v, "at": p, "shape": "circle"} for v, p in {"s": [0, 1], "a": [1, 0], "b": [1, 2], "t": [2, 1]}.items()],
       "edges": [{"from": u, "to": w, "label": f"0/{c}"} for (u, w), c in CS.items()]})
s.obj({"id": "rn", "type": "diagram", "region": "right", "layout": "grid", "directed": True,
       "nodes": [{"id": v, "label": v, "at": p, "shape": "circle"} for v, p in {"s": [0, 1], "a": [1, 0], "b": [1, 2], "t": [2, 1]}.items()],
       "edges": [{"from": u, "to": w, "label": str(c)} for (u, w), c in CS.items()]})
s.obj({"id": "ff", "type": "code", "region": "center", "language": "text", "lines": [
    "FORD-FULKERSON(G, s, t)",
    "    for each edge (u, v) in G.E:  (u, v).f = 0",
    "    while there is a path p from s to t in the residual network G_f",
    "        c_f(p) = min { c_f(u, v) : (u, v) on p }       // the bottleneck",
    "        for each edge (u, v) on p",
    "            if (u, v) is in G.E:  (u, v).f = (u, v).f + c_f(p)   // push forward",
    "            else:                 (v, u).f = (v, u).f − c_f(p)   // cancel",
    "    return f"]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": True,
       "nodes": [{"id": v, "label": v, "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": u, "to": w, "label": f"0/{c}"} for (u, w), c in CAP.items()]})
s.obj({"id": "aug", "type": "table", "region": "right", "columns": ["#", "augmenting path", "bottleneck", "|f|"],
       "rows": [[str(i + 1), "", "", ""] for i in range(4)]})
s.obj({"id": "mc", "type": "table", "region": "center", "columns": ["max-flow min-cut", ""], "rows": [
    ["cut (S, T)", "split V: s in S, t in T"],
    ["capacity of the cut", "sum of c(u, v) over edges from S to T only"],
    ["any flow", "|f| ≤ capacity of any cut: all flow must cross it"],
    ["when no augmenting path is left", "S = vertices reachable from s in G_f"],
    ["our network", "S = {s, b}: c(s, a) + c(b, d) = 10 + 9 = 19 = |f|"],
    ["theorem", "max flow value = min cut capacity"]]})
s.obj({"id": "rt", "type": "table", "region": "center", "columns": ["running time", ""], "rows": [
    ["integer capacities", "each augmentation adds ≥ 1: at most |f*| rounds"],
    ["one round", "find a path, O(E):  total O(E · |f*|)"],
    ["bad choice", "s→u, s→v, u→t, v→t of 1000 and u→v of 1"],
    ["", "paths through u→v, then back v→u: 2000 rounds of 1"],
    ["Edmonds-Karp", "choose a shortest path (BFS): 2 rounds here"],
    ["", "O(V · E²), whatever the capacities"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["s→A 6, s→B 8, A→B 3, A→C 4, B→C 5, A→t 3, C→t 9"],
    ["a) find the maximum flow, using Edmonds-Karp (shortest paths first)"],
    ["b) give a minimum cut and check its capacity"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["round", "path", "bottleneck", "|f|"], "rows": [
    ["1", "s → A → t", "min(6, 3) = 3", "3"],
    ["2", "s → A → C → t", "min(6 − 3, 4, 9) = 3", "6"],
    ["3", "s → B → C → t", "min(8, 5, 9 − 3) = 5", "11"],
    ["stop", "from s, G_f reaches only B: s→A full, B→C full", "", "11"],
    ["cut", "S = {s, B}: c(s, A) + c(B, C) = 6 + 5", "", "11 ✓"]]})

def setflow(flows, d0=0.0, step=0.12):
    out = []
    for k, ((u, w), c) in enumerate(CAP.items()):
        if flows.get((u, w)) is not None:
            out.append(st(f"g.{u}->{w}", f"{flows[(u, w)]}/{c}", round(min(0.9, d0), 2)))
    return out

cur = {e: 0 for e in CAP}
def augment(i):
    path, b = LOG[i]; out = []; changed = {}
    if i:
        pp = LOG[i - 1][0]
        out += [rs(f"g.{pp[k]}->{pp[k + 1]}") for k in range(len(pp) - 1)]
    for k in range(len(path) - 1):
        e = (path[k], path[k + 1]); cur[e] += b; changed[e] = cur[e]
        out.append(mk(f"g.{e[0]}->{e[1]}", round(0.1 + 0.15 * k, 2)))
    for k, (e, f) in enumerate(changed.items()):
        out.append(st(f"g.{e[0]}->{e[1]}", f"{f}/{CAP[e]}", round(0.6 + 0.08 * k, 2)))
    tot = sum(LOG[j][1] for j in range(i + 1))
    out += [st(f"aug[{i}][1]", " → ".join(path)), st(f"aug[{i}][2]", str(b), 0.3), st(f"aug[{i}][3]", str(tot), 0.5)]
    return out

s.scene("intro")
s.step("A water network, a road system, a data network: each link can carry only so much per second. How much can we move from one point to another in total? That is the maximum-flow problem, and Ford-Fulkerson answers it by repeatedly finding a path with room to spare.", [s.head("Maximum flow: Ford-Fulkerson")])
s.step("Here are the eight stages.", show("stages"))
s.step("Flow networks, residual networks, why we sometimes push flow backwards, and the method itself.", [hl("stages[0..=3]")])
s.step("Then a full trace, the max-flow min-cut theorem, running time with Edmonds-Karp, and an exam question.", [hl("stages[4..=7]")])

s.scene("net")
s.step("Stage 1: a flow network is a directed graph with a source s, a sink t, and a capacity on each edge.", [s.head("Stage 1 of 8: flow networks")] + hide("stages") + show("fd") + [hl("fd[0..=1]")])
s.step("A flow puts an amount on every edge. Two rules. First, never more than the capacity, and never negative.", [hl("fd[2]")])
s.step("Second, conservation: at every vertex other than s and t, what flows in must flow out. Nothing is stored or lost on the way.", [hl("fd[3]")])
s.step("The value of a flow is the net amount leaving s, which equals the net amount reaching t. We want the largest value possible.", [hl("fd[4..=5]"), s.take("respect capacities; conserve at every inner vertex")])

s.scene("res")
s.step("Stage 2: the key idea is the residual network: for every pair of vertices, how much more could we still send from u to v?", [s.head("Stage 2 of 8: residual network"), s.untake()] + hide("fd") + show("rd"))
s.step("If u to v is an edge, the answer is its unused capacity: capacity minus flow.", [hl("rd[0]")])
s.step("If v to u is an edge carrying flow, we may also send back from u to v, up to that flow: that simply cancels some of what we sent before.", [hl("rd[1]")])
s.step("The residual network keeps every pair with positive residual capacity. A simple path from s to t in it is called an augmenting path.", [hl("rd[2..=3]")])
s.step("Its bottleneck, the smallest residual capacity on it, is how much more flow that path can carry.", [hl("rd[4]"), s.take("augmenting path = s ⇝ t in G_f")])

s.scene("cancel")
s.step("Stage 3: why backward edges matter. A small network: every edge has capacity 2. Left: the flow, written flow over capacity. Right: the residual network.", [s.head("Stage 3 of 8: cancelling flow"), s.untake()] + hide("rd") + show("fn", "rn"))
s.step("Suppose we first choose the path s, a, b, t, with bottleneck 2. Push 2 along it.", [mk("fn.s->a"), mk("fn.a->b", 0.2), mk("fn.b->t", 0.4),
    st("fn.s->a", "2/2", 0.6), st("fn.a->b", "2/2", 0.7), st("fn.b->t", "2/2", 0.8)])
s.step("Those three edges are now full, so forwards they vanish from the residual network. But each can be undone: a back edge appears with capacity 2.", [rm("rn.s->a"), rm("rn.a->b", 0.15), rm("rn.b->t", 0.3),
    adde("rn", "a", "s", "2", 0.5), adde("rn", "b", "a", "2", 0.6), adde("rn", "t", "b", "2", 0.7)])
s.step("Without back edges we would be stuck at 2: in the original graph, every path from s to t now uses a full edge. In the residual network there is still a path: s, b, then back from b to a, then a, t.", [mk("rn.s->b"), mk("rn.b->a", 0.25), mk("rn.a->t", 0.5)])
s.step("Push 2 along it. The step b to a is not real flow from b to a: it cancels the 2 we had sent from a to b. That edge goes back to 0.", [rs("fn.s->a"), rs("fn.a->b"), rs("fn.b->t"), st("fn.s->b", "2/2"), st("fn.a->b", "0/2", 0.3), st("fn.a->t", "2/2", 0.5), mk("fn.s"), mk("fn.t")])
s.step("The residual network updates too: s to b and a to t are now full, so they turn around, and a to b has its room back. Look at s: nothing leaves it any more. No augmenting path, so the flow is maximum.", [rm("rn.s->b"), rm("rn.b->a", 0.1), rm("rn.a->t", 0.2),
    adde("rn", "b", "s", "2", 0.4), adde("rn", "a", "b", "2", 0.5), adde("rn", "t", "a", "2", 0.6), hl("rn.s", 0.8)])
s.step("Total 4: s sends 2 to a, a sends them straight to t; s sends 2 to b, b sends them to t. The first path was a poor choice, and the back edge let us repair it.", [s.take("back edges let a bad choice be undone")])

s.scene("algo")
s.step("Stage 4: Cormen's Ford-Fulkerson method. Start with zero flow on every edge.", [s.head("Stage 4 of 8: the method"), s.untake()] + hide("fn", "rn") + show("ff") + [ml("ff", 1, 2)])
s.step("While the residual network still has a path from s to t, find one, and take its bottleneck.", [ml("ff", 3, 4)])
s.step("For each edge of the path: if it is a real edge, add the bottleneck to its flow. If it is a back edge, subtract the bottleneck from the real edge it reverses.", [ml("ff", 5, 7)])
s.step("When no augmenting path is left, the flow is maximum. Ford-Fulkerson does not say how to find the path. Choosing it by breadth-first search, the fewest edges first, is the Edmonds-Karp algorithm, and that is what we use now.", [ml("ff", 8, 8), s.take("augment until G_f has no s ⇝ t path")])

s.scene("trace")
s.step("Stage 5: six vertices, nine edges. Every edge starts at 0 over its capacity. Each round, BFS finds a shortest augmenting path.", [s.head("Stage 5 of 8: a full trace"), s.untake()] + hide("ff") + show("g", "aug"))
s.step("Round 1: s, a, c, t. Residual capacities 10, 4 and 10: the bottleneck is a to c, 4. Flow value 4.", augment(0))
s.step("Round 2: s, a, d, t. s to a has 6 left, a to d 8, d to t 10: bottleneck 6. Now s to a is full. Value 10.", augment(1))
s.step("Round 3: s to a is full, so BFS goes through b: s, b, d, t. d to t has only 4 left: bottleneck 4, and d to t is full. Value 14.", augment(2))
s.step("Round 4: the shortest remaining path is longer: s, b, d, c, t. Residuals 6, 5, 6 and 6: bottleneck 5, from b to d. Value 19.", augment(3))
s.step("Now search again. From s, a is full; b still has 1 spare, but from b, the edge to d is full, and nothing else leaves b. No path to t. The flow, 19, is maximum.", [rs("g.s->b"), rs("g.b->d"), rs("g.d->c"), rs("g.c->t"), hl("g.s"), hl("g.b", 0.3), mk("aug[3]", 0.6), s.take("max flow = 19")])

s.scene("cut")
s.step("Stage 6: how can we be sure 19 is the best possible? Cut the vertices into two groups: S containing s, and T containing t.", [s.head("Stage 6 of 8: max-flow min-cut"), s.untake()] + hide("g", "aug") + show("mc") + [hl("mc[0]")])
s.step("The capacity of a cut adds up only the edges that go from S across to T.", [hl("mc[1]")])
s.step("Every unit of flow has to cross from S to T, so no flow can be bigger than any cut's capacity.", [hl("mc[2]")])
s.step("When Ford-Fulkerson stops, take S to be every vertex still reachable from s in the residual network. Every edge leaving S is full, so the flow equals this cut's capacity.", [hl("mc[3]")])
s.step("Here S is s and b. Edges leaving it: s to a, 10, and b to d, 9. The edge a to b goes into S, so it is not counted. 19, exactly our flow.", [hl("mc[4]")])
s.step("That is the max-flow min-cut theorem: the maximum flow value equals the minimum cut capacity. A cut is your certificate that a flow is optimal.", [hl("mc[5]"), mk("mc[5]", 0.4), s.take("max flow = min cut")])

s.scene("time")
s.step("Stage 7: with integer capacities, every augmentation adds at least 1, so there are at most f-star rounds, where f-star is the maximum flow.", [s.head("Stage 7 of 8: running time"), s.untake()] + hide("mc") + show("rt") + [hl("rt[0]")])
s.step("Each round finds a path in O of E time, so the total is O of E times f-star. That depends on the size of the capacities, not just of the graph.", [hl("rt[1]")])
s.step("The classic bad case: four edges of capacity 1000 and one middle edge of capacity 1. A careless choice of path goes through the middle edge, then back across it, each time adding just 1: 2000 rounds.", [hl("rt[2..=3]")])
s.step("Edmonds-Karp always takes a shortest path. Here that means the two outer paths, 2 rounds. In general it needs O of V times E squared time, whatever the capacities.", [hl("rt[4..=5]"), s.take("Edmonds-Karp: BFS paths, O(V E²)")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("rt") + show("q") + [hl("q[0]")])
s.step("Find the maximum flow from s to t with Edmonds-Karp, then give a minimum cut. Pause and work it out.", [hl("q[1..=2]")])
s.step("Round 1: the only path of two edges is s, A, t. Bottleneck min of 6 and 3: 3.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Round 2: s, A, C, t. s to A has 3 left: bottleneck 3. Value 6, and s to A is now full.", [hl("qa[1]")])
s.step("Round 3: s, B, C, t. C to t has 6 left; B to C allows 5. Value 11.", [hl("qa[2]")])
s.step("Search again: from s we reach B, but B to C is full, and s to A is full. Stop at 11.", [hl("qa[3]")])
s.step("The reachable set gives the cut: S is s and B. Edges leaving it: s to A, 6, and B to C, 5. Capacity 11, equal to the flow. Maximum confirmed.", [hl("qa[4]"), mk("qa[4][3]", 0.5)])
s.step("The usual slip: counting edges that go from T back into S, like A to B here. Only edges from S to T count in a cut's capacity.", [s.take("cut capacity: S → T edges only")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A flow respects capacities and conservation. The residual network shows spare room forwards and flow that can be cancelled backwards.", [hl("stages[0..=2]")])
s.step("Ford-Fulkerson augments along paths in the residual network until none is left; with BFS paths, Edmonds-Karp runs in O of V E squared.", [hl("stages[3..=6]")])
s.step("The cut of vertices still reachable from s proves the flow maximum. Next video: a different way to reach the same answer, push-relabel.", [mk("stages[0..=7]"), s.take("Next: push-relabel")])

s.save("/home/claude/playlist/dsa2/d2v15.json")

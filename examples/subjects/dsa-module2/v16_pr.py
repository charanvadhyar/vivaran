"""DSA Module 2, video 16: push-relabel."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from pr import push_relabel

V = list("sabt"); CAP = {("s", "a"): 4, ("s", "b"): 2, ("a", "b"): 3, ("a", "t"): 1, ("b", "t"): 3}
val, F, LOG, H = push_relabel(V, CAP, "s", "t")
ops = [l[:4] if l[0] == "push" else l[:3] for l in LOG[1:]]
assert val == 4 and ops == [("relabel", "a", 1), ("push", "a", "b", 3), ("push", "a", "t", 1), ("relabel", "b", 1), ("push", "b", "t", 3),
    ("relabel", "b", 2), ("push", "b", "a", 2), ("relabel", "a", 3), ("push", "a", "b", 2), ("relabel", "b", 4), ("push", "b", "a", 2),
    ("relabel", "a", 5), ("push", "a", "s", 2)]
assert F == {("s", "a"): 2, ("s", "b"): 2, ("a", "b"): 1, ("a", "t"): 1, ("b", "t"): 3}
assert CAP[("a", "t")] + CAP[("b", "t")] == 4 and max(H.values()) <= 2 * len(V) - 1
VE = list("sABt"); CE = {("s", "A"): 5, ("s", "B"): 3, ("A", "B"): 2, ("A", "t"): 2, ("B", "t"): 4}
ev, ef, elog, eh = push_relabel(VE, CE, "s", "t")
assert ev == 6 and [l[:4] if l[0] == "push" else l[:3] for l in elog[1:6]] == [("relabel", "A", 1), ("push", "A", "B", 2), ("push", "A", "t", 2), ("relabel", "A", 5), ("push", "A", "s", 1)]
assert elog[0][2] == {"s": -8, "A": 5, "B": 3, "t": 0}

s = Script("Maximum flow: push-relabel")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The idea: preflow, excess and height"],
    [2, "The two operations: push and relabel"],
    [3, "Starting: initialise the preflow"],
    [4, "A full trace"],
    [5, "Why it ends with a maximum flow"],
    [6, "Push-relabel versus Ford-Fulkerson"],
    [7, "Exam question"]]})
s.obj({"id": "idea", "type": "table", "region": "center", "columns": ["push-relabel", ""], "rows": [
    ["Ford-Fulkerson", "keeps a valid flow; improves it along whole paths s ⇝ t"],
    ["push-relabel", "works locally, one edge at a time"],
    ["preflow", "capacities hold, but a vertex may take in more than it sends out"],
    ["excess e(u)", "flow in − flow out; u overflows when e(u) > 0"],
    ["height h(u)", "flow is pushed only downhill, from height k to k − 1"],
    ["the end", "no vertex overflows: the preflow is a flow, and it is maximum"]]})
s.obj({"id": "ops", "type": "code", "region": "center", "language": "text", "lines": [
    "PUSH(u, v)      // u overflows, c_f(u, v) > 0, u.h = v.h + 1",
    "    Δ = min(u.e, c_f(u, v))",
    "    if (u, v) is in E:  (u, v).f = (u, v).f + Δ",
    "    else:               (v, u).f = (v, u).f − Δ      // cancel",
    "    u.e = u.e − Δ;  v.e = v.e + Δ",
    "",
    "RELABEL(u)      // u overflows, no residual edge (u, v) goes downhill",
    "    u.h = 1 + min { v.h : (u, v) in E_f }",
    "",
    "INITIALIZE-PREFLOW(G, s)",
    "    every h, e and f = 0;   s.h = |V|",
    "    for each edge (s, v):  (s, v).f = c(s, v);  v.e = c(s, v);  s.e = s.e − c(s, v)",
    "",
    "GENERIC-PUSH-RELABEL(G):  initialise, then while some push or relabel applies, do it"]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": True,
       "nodes": [{"id": v, "label": v, "at": p, "shape": "circle"} for v, p in {"s": [0, 1], "a": [1, 0], "b": [1, 2], "t": [2, 1]}.items()],
       "edges": [{"from": u, "to": w, "label": f"0/{c}"} for (u, w), c in CAP.items()]})
s.obj({"id": "he", "type": "table", "region": "right", "columns": ["vertex", "height h", "excess e"],
       "rows": [[v, "0", "0"] for v in V]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["why it works", ""], "rows": [
    ["s.h = |V| = 4, t.h = 0", "a residual path s ⇝ t would drop 4 levels in at most 3 edges: impossible"],
    ["so at every moment", "G_f has no augmenting path"],
    ["when nothing overflows", "the preflow is a flow with no augmenting path: maximum"],
    ["an overflowing vertex", "always has a residual path back to s, so heights stay ≤ 2|V| − 1"],
    ["bounds", "O(V²) relabels, O(V² E) pushes: generic O(V² E)"],
    ["relabel-to-front (Cormen)", "O(V³)"]]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["", "Ford-Fulkerson / Edmonds-Karp", "push-relabel"], "rows": [
    ["keeps", "a valid flow", "a preflow (excess allowed)"],
    ["one step", "a whole path s ⇝ t", "one edge, or one height"],
    ["stops when", "no augmenting path", "no overflowing vertex"],
    ["time", "O(V E²)", "O(V² E); O(V³) relabel-to-front"],
    ["in practice", "simple to code", "fastest on large dense networks"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["s→A 5, s→B 3, A→B 2, A→t 2, B→t 4"],
    ["a) give every height and excess after INITIALIZE-PREFLOW"],
    ["b) apply the operations at A until A no longer overflows"],
    ["c) what is the maximum flow value? Prove it with a cut"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "result"], "rows": [
    ["a)", "s.h = 4; edges out of s saturated", "h: s 4, A 0, B 0, t 0;  e: A 5, B 3, s −8"],
    ["b) 1", "A overflows; no neighbour at height −1", "relabel A: 1 + min(0, 0, 4) = 1"],
    ["b) 2", "A.h = 1 = B.h + 1 and t.h + 1", "push 2 to B, push 2 to t: A.e = 1"],
    ["b) 3", "A→B, A→t full; only A→s is residual", "relabel A: 1 + 4 = 5; push 1 back to s"],
    ["c)", "cut S = {s, A, B}: c(A, t) + c(B, t) = 2 + 4", "max flow = 6"]]})

def frame(k, d0=0.3):
    """table and edge labels for log entry k, against entry k − 1"""
    h, e, f = LOG[k][-3], LOG[k][-2], LOG[k][-1]
    if k: ph, pe, pf = LOG[k - 1][-3], LOG[k - 1][-2], LOG[k - 1][-1]
    else: ph, pe, pf = {v: 0 for v in V}, {v: 0 for v in V}, {}
    out = []; dd = d0
    for i, v in enumerate(V):
        if h[v] != ph[v]: out.append(st(f"he[{i}][1]", str(h[v]), round(dd, 2))); dd += 0.08
        if e[v] != pe[v]: out.append(st(f"he[{i}][2]", str(e[v]), round(dd, 2))); dd += 0.08
    for (u, w), c in CAP.items():
        if f.get((u, w), 0) != pf.get((u, w), 0): out.append(st(f"g.{u}->{w}", f"{f.get((u, w), 0)}/{c}", round(dd, 2))); dd += 0.08
    return out

def op(k):
    l = LOG[k]
    if l[0] == "push":
        u, w = l[1], l[2]; tgt = f"g.{u}->{w}" if (u, w) in CAP else f"g.{w}->{u}"
        return [hl(tgt), hl(f"he[{V.index(u)}]")] + frame(k)
    return [hl(f"g.{l[1]}"), hl(f"he[{V.index(l[1])}]")] + frame(k)

s.scene("intro")
s.step("Ford-Fulkerson pushes flow along a whole path from source to sink at a time. Push-relabel does something quite different: it floods the network from the source and lets water run downhill, one edge at a time, raising vertices when it gets stuck. It is behind the fastest practical max-flow programs.", [s.head("Maximum flow: push-relabel")])
s.step("Here are the seven stages.", show("stages"))
s.step("The idea, the two operations, how to start, and a full trace.", [hl("stages[0..=3]")])
s.step("Then why it gives a maximum flow, how it compares with Ford-Fulkerson, and an exam question.", [hl("stages[4..=6]")])

s.scene("idea")
s.step("Stage 1: Ford-Fulkerson always holds a valid flow and improves it along whole paths. Push-relabel works locally: one vertex, one edge at a time.", [s.head("Stage 1 of 7: the idea")] + hide("stages") + show("idea") + [hl("idea[0..=1]")])
s.step("It holds a preflow: every edge respects its capacity, but a vertex may take in more than it sends out, for now.", [hl("idea[2]")])
s.step("The difference, flow in minus flow out, is the vertex's excess. A vertex with positive excess is overflowing, and must get rid of it.", [hl("idea[3]")])
s.step("Each vertex also has a height. Flow is only pushed downhill, from a vertex to a neighbour exactly one level lower, like water in a reservoir.", [hl("idea[4]")])
s.step("When no vertex overflows any more, the preflow is a real flow, and as we will see, a maximum one.", [hl("idea[5]"), s.take("preflow + heights; push downhill")])

s.scene("ops")
s.step("Stage 2: Cormen's two operations. Push applies when u overflows, the residual edge u to v has room, and u is exactly one level above v.", [s.head("Stage 2 of 7: push and relabel"), s.untake()] + hide("idea") + show("ops") + [ml("ops", 1, 1)])
s.step("Push as much as possible: delta, the smaller of u's excess and the edge's residual capacity. On a real edge, flow goes up. On a back edge, flow on the original edge goes down: cancelling, as in Ford-Fulkerson.", [ml("ops", 2, 4)])
s.step("Excess moves with it: u loses delta, v gains delta.", [ml("ops", 5, 5)])
s.step("Relabel applies when u overflows but every residual edge out of u leads to a vertex no lower than u. Nothing can flow, so lift u to one more than its lowest residual neighbour.", [ml("ops", 7, 8)])
s.step("Now u stands exactly one level above that neighbour, so a push becomes possible.", [s.take("push: downhill by one level;  relabel: lift just enough")])

s.scene("init")
s.step("Stage 3: start with all heights, excesses and flows at zero. Then raise the source to the number of vertices.", [s.head("Stage 3 of 7: initialise"), s.untake(), ml("ops", 10, 11)])
s.step("And fill every edge leaving the source to capacity. Its neighbours overflow at once; the source's excess goes negative.", [ml("ops", 12, 12)])
s.step("The generic algorithm: after initialising, as long as some push or relabel applies anywhere, apply it, in any order.", [ml("ops", 14, 14), s.take("s.h = |V|; saturate every edge out of s")])

s.scene("trace")
s.step("Stage 4: a network of four vertices. Edges are labelled flow over capacity; the table holds each vertex's height and excess.", [s.head("Stage 4 of 7: a full trace"), s.untake()] + hide("ops") + show("g", "he"))
s.step("Initialise: s goes to height 4, the number of vertices. s to a carries 4, s to b carries 2. So a has excess 4, b has 2, and s has minus 6.", frame(0, 0.2))
s.step("a overflows at height 0, and nothing is lower. Relabel: its residual neighbours b and t are at 0, s at 4. a becomes 1 plus 0, height 1.", op(1))
s.step("Now push downhill: a to b takes 3, its full capacity. a's excess drops to 1, b's rises to 5.", op(2))
s.step("Push a to t: 1 more, its full capacity. a's excess is 0. The sink t has received 1.", op(3))
s.step("b overflows with 5 at height 0. Relabel to 1, one above t.", op(4))
s.step("Push b to t: only 3 fits. b still holds 2, and the sink has 4. Both edges into t are now full, so the remaining 2 can never reach t: they must go back.", op(5))
s.step("Watch how. b's only residual edges now lead back: to a, by cancelling flow, and to s. Lowest is a at 1, so b rises to 2.", op(6))
s.step("Push b to a, 2 units: this cancels 2 of the 3 we sent from a to b.", op(7))
s.step("Now a overflows at height 1. It cannot push to t, which is full, so it rises to 3, one above b. It pushes the 2 back to b.", op(8) + op(9))
s.step("The two bounce: b rises to 4 and pushes to a; a rises to 5, one above the source.", op(10) + op(11) + op(12))
s.step("Finally a pushes 2 down to s, cancelling 2 of the flow on s to a. Nothing overflows. The flow value is 4: a to t, 1, and b to t, 3.", op(13) + [mk("g.t", 0.8), s.take("excess that cannot reach t climbs back to s")])
s.step("And the cut separating t from everything else, edges a to t and b to t, has capacity 1 plus 3, 4. So 4 is maximum.", [hl("g.a->t"), hl("g.b->t", 0.4)])

s.scene("why")
s.step("Stage 5: why must the answer be maximum? The source sits at height 4, the sink at 0, and every residual edge drops at most one level.", [s.head("Stage 5 of 7: why it works"), s.untake()] + hide("g", "he") + show("why") + [hl("why[0]")])
s.step("A simple path from s to t has at most 3 edges, so it cannot fall 4 levels. So, at every moment, there is no augmenting path.", [hl("why[1]")])
s.step("When nothing overflows, we hold a true flow with no augmenting path: by max-flow min-cut, it is maximum.", [hl("why[2]")])
s.step("And it does stop: an overflowing vertex always has a residual path back to s, so no height ever exceeds 2 V minus 1. That limits the relabels to O of V squared, and the pushes to O of V squared E.", [hl("why[3..=4]")])
s.step("Cormen's relabel-to-front version picks the order carefully and runs in O of V cubed.", [hl("why[5]"), s.take("h(s) = |V| ⇒ never an augmenting path")])

s.scene("cmp")
s.step("Stage 6: side by side. Ford-Fulkerson keeps a flow and works along whole paths; push-relabel keeps a preflow and works one edge at a time.", [s.head("Stage 6 of 7: compared"), s.untake()] + hide("why") + show("cmp") + [hl("cmp[0..=1]")])
s.step("One stops when no augmenting path remains; the other when no vertex overflows.", [hl("cmp[2]")])
s.step("Edmonds-Karp takes O of V E squared; push-relabel O of V squared E, or V cubed. On large dense networks push-relabel is usually fastest.", [hl("cmp[3..=4]"), s.take("both give the same maximum value")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("cmp") + show("q") + [hl("q[0]")])
s.step("Initialise the preflow, apply the operations at A, and find the maximum flow with a cut to prove it. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: the source rises to 4, the number of vertices. s to A fills with 5, s to B with 3. So A has excess 5, B has 3, s minus 8; every other height is 0.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: A overflows, but its neighbours B and t are at the same height, 0. Relabel A to 1 plus 0, 1.", [hl("qa[1]")])
s.step("Now A is one above both. Push 2 to B and 2 to t, both edges' full capacity. A still has 1.", [hl("qa[2]")])
s.step("Both edges out of A are full; the only residual edge goes back to s, at height 4. Relabel A to 5, and push the 1 back to s. A no longer overflows.", [hl("qa[3]")])
s.step("c: the cut with only t on one side has edges A to t, 2, and B to t, 4: capacity 6. B will send its 3 plus 2 from A: 4 to t, 1 back to s. The maximum flow is 6.", [hl("qa[4]"), mk("qa[4][2]", 0.5)])
s.step("The usual slip: pushing to a neighbour that is lower but not exactly one level lower. Push only from height k to height k minus 1.", [s.take("push only when u.h = v.h + 1")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Push-relabel holds a preflow with heights. Push sends excess one level downhill; relabel lifts a stuck vertex just enough.", [hl("stages[0..=2]")])
s.step("Excess that cannot reach t climbs back to s. Since the source starts at height V, there is never an augmenting path, so the final flow is maximum.", [hl("stages[3..=5]")])
s.step("That completes Module 2. Next, Module 3: divide and conquer, starting with merge sort.", [mk("stages[0..=6]"), s.take("Next: Module 3, divide and conquer")])

s.save("/home/claude/playlist/dsa2/d2v16.json")

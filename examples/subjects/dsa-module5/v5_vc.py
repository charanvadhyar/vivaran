"""DSA Module 5, video 5: approximation, vertex cover (lab 9)."""
import sys, itertools
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa5")
from common import Script
from h import *

E = [("a", "b"), ("b", "c"), ("c", "d"), ("c", "e"), ("d", "e"), ("d", "f"), ("d", "g"), ("e", "f")]
V = sorted(set(x for e in E for x in e))
def approx(E, order):
    rem = list(E); C = []; A = []; steps = []
    for e in order:
        if e in rem:
            u, v = e; A.append(e); C += [u, v]; gone = [f for f in rem if u in f or v in f]; rem = [f for f in rem if f not in gone]; steps.append((e, gone, list(rem)))
    return C, A, rem, steps
def opt(V, E):
    for k in range(len(V) + 1):
        for S in itertools.combinations(V, k):
            if all(u in S or v in S for u, v in E): return S
C, A, REM, ST = approx(E, [("b", "c"), ("e", "f"), ("d", "g")])
C2, A2, R2, S2 = approx(E, [("d", "e"), ("a", "b")]); assert sorted(C2) == list("abde") and not R2
assert sorted(C) == list("bcdefg") and not REM and opt(V, E) == ("b", "d", "e")
assert [len(g) for e, g, r in ST] == [4, 3, 1]
P = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
PC, PA, PR, PS = approx(P, P); assert sorted(PC) == [1, 2, 3, 4, 5, 6] and len(opt(list(range(1, 7)), P)) == 3

POS = {"a": [0, 0], "b": [1, 0], "c": [2, 0], "d": [3, 0], "e": [1, 1], "f": [2, 1], "g": [3, 1]}
s = Script("Approximation: vertex cover")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The lab problem: monitoring a network"],
    [2, "Approximation algorithms and the ratio ρ"],
    [3, "APPROX-VERTEX-COVER"],
    [4, "Cormen's example, edge by edge"],
    [5, "Proof: never more than twice the best"],
    [6, "Why not pick the busiest vertex?"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["monitoring agents (lab 9)", ""], "rows": [
    ["network", "nodes (servers, routers, switches) and links"],
    ["an agent on a node", "monitors every link touching that node"],
    ["goal", "every link monitored, with as few agents as possible"],
    ["that is", "a minimum vertex cover: a set touching every edge"],
    ["but", "VERTEX-COVER is NP-complete: no fast exact algorithm is known"]]})
s.obj({"id": "ap", "type": "table", "region": "center", "columns": ["approximation algorithm", ""], "rows": [
    ["runs in", "polynomial time"],
    ["returns", "a valid solution, not necessarily the best"],
    ["ratio ρ(n)", "cost of our solution ≤ ρ × cost of the best, on every input"],
    ["2-approximation", "never more than twice the optimum"],
    ["the catch", "we must prove the bound without knowing the optimum"]]})
s.obj({"id": "ac", "type": "code", "region": "center", "language": "text", "lines": [
    "APPROX-VERTEX-COVER(G)",
    "    C = ∅;   E' = G.E",
    "    while E' is not empty",
    "        let (u, v) be any edge of E'",
    "        C = C ∪ {u, v}                     // take BOTH ends",
    "        remove from E' every edge touching u or v",
    "    return C",
    "",
    "with adjacency lists: O(V + E)"]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "label": v, "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": a, "to": b} for a, b in E]})
s.obj({"id": "tt", "type": "table", "region": "right", "columns": ["pick", "add to C", "edges removed"], "rows": [["", "", ""] for _ in ST] + [["result", "", ""]]})
s.obj({"id": "pf", "type": "math", "region": "center", "lines": [
    "A = \"the edges picked\": \" no two share an end (each pick removes its neighbours)\"",
    "\"any vertex cover \" C^* \" must touch every edge of \" A: quad |C^*| >= |A|",
    "\"our cover takes both ends of each:\" quad |C| = 2|A|",
    "|C| = 2|A| <= 2|C^*| quad \"a 2-approximation\"",
    "\"example: \" |A| = 3 => |C^*| >= 3; quad |C| = 6 <= 2 dot 3"]})
s.obj({"id": "gr", "type": "table", "region": "center", "columns": ["\"take the vertex of highest degree\"", ""], "rows": [
    ["sounds better", "it often gives smaller covers in practice"],
    ["but", "there are graphs where it is a factor of about log n worse than optimal"],
    ["no constant guarantee", "its ratio grows with n"],
    ["the dumb-looking rule", "taking both ends of any edge is guaranteed within 2"],
    ["better than 2?", "no polynomial algorithm with ratio below about 1.36 unless P = NP"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: the path 1–2–3–4–5–6"], "rows": [
    ["a) run APPROX-VERTEX-COVER, picking the first remaining edge each time"],
    ["b) find an optimal cover"],
    ["c) what ratio did the approximation achieve here?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "pick 1–2: remove 1–2, 2–3 · pick 3–4: remove 3–4, 4–5 · pick 5–6", "C = {1, 2, 3, 4, 5, 6}"],
    ["b)", "{2, 4, 5}: covers 1–2, 2–3, 3–4, 4–5, 5–6; 3 picked edges force at least 3", "size 3"],
    ["c)", "6 / 3", "exactly 2: the bound is tight"]]})

s.scene("intro")
s.step("The lab asks for something that sounds simple: place monitoring agents on network nodes so that every link is watched, using as few agents as possible. That is vertex cover, which is NP-complete. So we settle for a fast answer that is provably close to the best.", [s.head("Approximation: vertex cover")])
s.step("Here are the seven stages.", show("stages"))
s.step("The lab problem, what an approximation ratio means, the algorithm, and Cormen's example.", [hl("stages[0..=3]")])
s.step("Then the proof that it is never worse than twice optimal, why a greedier rule fails, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: the network has nodes and links. An agent on a node watches every link touching it.", [s.head("Stage 1 of 7: the problem")] + hide("stages") + show("pb") + [hl("pb[0..=1]")])
s.step("We want every link watched with the fewest agents.", [hl("pb[2]")])
s.step("In graph terms: a minimum vertex cover, a smallest set of vertices touching every edge.", [hl("pb[3]")])
s.step("Putting an agent on every node always works, but wastes agents. On a star-shaped network, one agent at the hub is enough. The question is how few will do in general.", [hl("pb[2]")])
s.step("Last video showed vertex cover is NP-complete. For a network of thousands of nodes, an exact answer is out of reach.", [hl("pb[4]"), s.take("vertex cover: touch every edge")])

s.scene("ap")
s.step("Stage 2: an approximation algorithm runs in polynomial time, and always returns a valid solution.", [s.head("Stage 2 of 7: approximation ratio"), s.untake()] + hide("pb") + show("ap") + [hl("ap[0..=1]")])
s.step("Its ratio rho bounds how far from the best it can be: our cost is at most rho times the optimal cost, on every input.", [hl("ap[2]")])
s.step("A 2-approximation never uses more than twice the optimum.", [hl("ap[3]")])
s.step("Think of a quote that says: this job will cost at most twice what the best contractor in the world would charge. Not perfect, but a promise you can plan around.", [hl("ap[2]")])
s.step("The challenge: proving that bound without ever knowing the optimum. We need a lower bound on the best possible answer.", [hl("ap[4]"), s.take("cost ≤ ρ × optimum, always")])

s.scene("ac")
s.step("Stage 3: Cormen's APPROX-VERTEX-COVER. Start with an empty cover and all the edges.", [s.head("Stage 3 of 7: the algorithm"), s.untake()] + hide("ap") + show("ac") + [ml("ac", 1, 2)])
s.step("While edges remain, pick any one, u, v.", [ml("ac", 3, 4)])
s.step("Put both its ends into the cover. One of them must be in any cover; we take both, because we do not know which.", [ml("ac", 5, 5)])
s.step("Then delete every edge touching u or v: they are all covered now.", [ml("ac", 6, 7)])
s.step("Each edge is examined a constant number of times: linear time, O of V plus E.", [ml("ac", 9, 9), s.take("take both ends of any uncovered edge")])

s.scene("trace")
s.step("Stage 4: Cormen's network of seven nodes and eight links.", [s.head("Stage 4 of 7: an example"), s.untake()] + hide("ac") + show("g", "tt"))
say = ["Pick edge b, c. Add b and c. Remove every edge touching them: a b, b c, c d and c e. Four links covered.",
       "Of the remaining four, pick e, f. Add e and f. Remove d e, d f and e f.",
       "Only d, g is left. Add d and g. Nothing remains."]
for k, (e, gone, rem) in enumerate(ST):
    u, v = e
    acts = [hl(f"g.{u}->{v}"), mk(f"g.{u}", 0.3), mk(f"g.{v}", 0.3), st(f"tt[{k}][0]", f"{u}–{v}"), st(f"tt[{k}][1]", f"{u}, {v}", 0.3), st(f"tt[{k}][2]", ", ".join(a + b for a, b in gone), 0.5), hl(f"tt[{k}]")]
    acts += [dim(f"g.{a}->{b}", round(0.6 + 0.05 * i, 2)) for i, (a, b) in enumerate(gone)]
    s.step(say[k], acts)
s.step("The cover is b, c, d, e, f and g: six agents. Every link is watched.", [st("tt[3][1]", "6 vertices"), st("tt[3][2]", "optimal: b, d, e = 3", 0.4), hl("tt[3]"), s.take("our cover 6, optimal 3")])
s.step("The edge picked each time can be any uncovered one. Picking d, e first covers six links at once; then a, b finishes: a cover of four. Different choices give different covers, but every choice stays within twice the optimum.", [hl("g.d->e"), hl("g.a->b", 0.5)])
s.step("The best cover is just b, d and e: three. Our answer is exactly twice the optimum, the worst the algorithm can ever do.", [hl("g.b"), hl("g.d", 0.3), hl("g.e", 0.6)])

s.scene("pf")
s.step("Stage 5: the proof. Let A be the set of edges the algorithm picked. Each pick removed every edge touching its ends, so no two picked edges share a vertex.", [s.head("Stage 5 of 7: the factor 2"), s.untake()] + hide("g", "tt") + show("pf") + [hl("pf[0]")])
s.step("Any vertex cover, including the optimal one, must touch every edge in A, and since those edges share no vertices, it needs a different vertex for each. So the optimum is at least the size of A.", [rv("pf[1]"), hl("pf[1]")])
s.step("Our cover takes both ends of each edge in A: exactly twice the size of A.", [rv("pf[2]"), hl("pf[2]")])
s.step("Put together: our cover is at most twice the optimum. That is the lower-bound trick: the picked edges prove the optimum cannot be small.", [rv("pf[3]"), mk("pf[3]")])
s.step("In the example: 3 picked edges, so any cover needs at least 3; we used 6.", [rv("pf[4]"), hl("pf[4]"), s.take("|C| = 2|A| ≤ 2|C*|")])

s.scene("gr")
s.step("Stage 6: wouldn't it be smarter to pick the busiest vertex, the one touching the most links?", [s.head("Stage 6 of 7: the greedy alternative"), s.untake()] + hide("pf") + show("gr") + [hl("gr[0]")])
s.step("Often it does better. But there are graphs where it uses about log n times the optimum.", [hl("gr[1]")])
s.step("So it has no constant guarantee: its worst case grows with the network.", [hl("gr[2]")])
s.step("The simple rule, taking both ends of any edge, always stays within 2. And unless P equals NP, no polynomial algorithm can guarantee better than about 1.36.", [hl("gr[3..=4]"), s.take("a guarantee beats a good guess")])

s.scene("exam")
s.step("Now an exam question on the path 1, 2, 3, 4, 5, 6.", [s.head("Exam question"), s.untake()] + hide("gr") + show("q") + [hl("q[0]")])
s.step("Run the algorithm, find an optimal cover, and compute the ratio. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: pick 1, 2, which also covers 2, 3. Pick 3, 4, which covers 4, 5. Pick 5, 6. The cover is all six vertices.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 2, 4 and 5 cover all five edges. And the three picked edges share no vertices, so no cover can be smaller than 3.", [hl("qa[1]")])
s.step("c: 6 against 3: a ratio of exactly 2. The bound is tight: some inputs really do reach it.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("The usual slip: adding only one end of the chosen edge. That can leave other edges uncovered, or break the proof; take both.", [s.take("both ends, every pick")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Placing monitoring agents is minimum vertex cover, which is NP-complete. An approximation runs fast and promises a ratio.", [hl("stages[0..=2]")])
s.step("Taking both ends of any uncovered edge gives a cover at most twice optimal, because the picked edges force the optimum to be at least half as large.", [hl("stages[3..=5]")])
s.step("Next video: covering a whole universe with as few sets as possible. Set cover, and its greedy approximation.", [mk("stages[0..=6]"), s.take("Next: set cover")])

s.save("/home/claude/playlist/dsa5/d5v5.json")

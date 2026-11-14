"""DSA Module 5, video 7: approximating the travelling salesman."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa5")
from common import Script
from h import *
from tsp import d, mst_prim, preorder, length, opt

P = {"a": (0, 0), "b": (3, 0), "c": (3, 2), "d": (0, 3), "e": (1, 5), "f": (5, 4)}
PAR, ORD = mst_prim(P, "a"); MW = sum(d(P, v, PAR[v]) for v in P if PAR[v])
T = preorder(PAR, "a", list(P)); TL = length(P, T); OL, OT = opt(P)
assert PAR == {"a": None, "b": "a", "c": "b", "d": "a", "e": "d", "f": "c"} and MW == 15
assert T == list("abcfde") and TL == 24 and OL == 20 and OT == list("abcfed")
assert [d(P, T[i], T[(i + 1) % 6]) for i in range(6)] == [3, 2, 4, 6, 3, 6]
PE = {"A": (0, 0), "B": (4, 0), "C": (1, 2), "D": (5, 3)}
EP, EO = mst_prim(PE, "A"); assert sum(d(PE, v, EP[v]) for v in PE if EP[v]) == 11 and preorder(EP, "A", list(PE)) == list("ABDC") and length(PE, list("ABDC")) == 16 and opt(PE)[0] == 16
assert length(PE, list("ABCD")) == 22 and length(PE, list("ACBD")) == 20

GPOS = {"a": [0, 5], "b": [3, 5], "c": [3, 3], "d": [0, 2], "e": [1, 0], "f": [5, 1]}  # y flipped for display
s = Script("Approximation: the travelling salesman")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "TSP, and the triangle inequality"],
    [2, "The idea: a tree is almost a tour"],
    [3, "APPROX-TSP-TOUR"],
    [4, "Six cities, traced"],
    [5, "Proof: at most twice the optimum"],
    [6, "Without the triangle inequality; better ratios"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["the travelling salesman", ""], "rows": [
    ["given", "n cities and the cost c(u, v) of travelling between each pair"],
    ["find", "the cheapest tour visiting every city once and returning home"],
    ["hard", "NP-hard (HAM-CYCLE reduces to it, video 2)"],
    ["triangle inequality", "c(u, w) ≤ c(u, v) + c(v, w): a detour never saves"],
    ["holds for", "road and straight-line distances, travel times on sensible maps; here, city-block distance"]]})
s.obj({"id": "id", "type": "table", "region": "center", "columns": ["the idea", ""], "rows": [
    ["delete one edge from the best tour", "a spanning tree (a path)"],
    ["so", "MST weight ≤ cost of the optimal tour"],
    ["walk around the MST", "every edge twice: a closed walk of cost 2 × MST"],
    ["skip cities already visited", "shortcuts never cost more (triangle inequality)"]]})
s.obj({"id": "ac", "type": "code", "region": "center", "language": "text", "lines": [
    "APPROX-TSP-TOUR(G, c)",
    "    choose a root r",
    "    T = MST-PRIM(G, c, r)                 // video 7 of Module 3",
    "    H = the vertices of T in preorder     // a depth-first walk, first visits only",
    "    return the tour H, then back to r",
    "",
    "MST: O(V²) on a complete graph;  preorder: O(V)"]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "label": f"{v}{P[v]}".replace(" ", ""), "at": GPOS[v], "shape": "pill"} for v in P],
       "edges": [{"from": v, "to": PAR[v], "label": str(d(P, v, PAR[v]))} for v in P if PAR[v]]})
s.obj({"id": "tt", "type": "table", "region": "right", "columns": ["step", "result"], "rows": [
    ["MST from a (Prim)", ""], ["its weight", ""], ["preorder", ""], ["tour costs", ""], ["tour total", ""], ["optimal (brute force)", ""]]})
s.obj({"id": "pf", "type": "math", "region": "center", "lines": [
    "\"delete an edge from the optimal tour \" H^*: \" a spanning tree, so \" c(T) <= c(H^*)",
    "\"full walk around \" T: \" each edge twice: \" c(W) = 2 c(T)",
    "\"shortcutting repeated cities never increases cost (triangle inequality):\" quad c(H) <= c(W)",
    "c(H) <= 2 c(T) <= 2 c(H^*) quad \"a 2-approximation\"",
    "\"here: \" 15 <= 20, quad 24 <= 30 <= 40"]})
s.obj({"id": "nt", "type": "table", "region": "center", "columns": ["beyond", ""], "rows": [
    ["no triangle inequality", "no constant ratio at all, unless P = NP"],
    ["why", "with costs 1 for G's edges and ρn + 1 otherwise, a ρ-approximation would decide HAM-CYCLE"],
    ["Christofides (1976)", "MST plus a minimum matching on odd-degree vertices: ratio 1.5"],
    ["Euclidean plane", "approximation schemes get within 1 + ε, for any ε > 0"],
    ["in practice", "heuristics like 2-opt improve tours to within a few percent"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: costs AB 4, AC 3, AD 8, BC 5, BD 4, CD 5"], "rows": [
    ["a) the MST, built by Prim from A"],
    ["b) the APPROX-TSP-TOUR tour (children in alphabetical order) and its cost"],
    ["c) the optimal tour, and the ratio achieved"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "A–C 3, then A–B 4, then B–D 4", "weight 11"],
    ["b)", "preorder: A, B, D, C;  4 + 4 + 5 + 3", "A B D C A: 16"],
    ["c)", "the three tours cost 16 (ABDC), 22 (ABCD), 20 (ACBD)", "optimal 16: ratio 1"],
    ["check", "16 ≤ 2 × 11 = 22", "within the bound"]]})

s.scene("intro")
s.step("A delivery van must visit every customer once and return to the depot, by the shortest route. That is the travelling salesman problem, the most famous NP-hard problem of all. When distances behave like real distances, a minimum spanning tree gives a route at most twice the best.", [s.head("Approximation: the travelling salesman")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem and the triangle inequality, the idea, the algorithm, and a trace.", [hl("stages[0..=3]")])
s.step("Then the proof of the factor 2, what goes wrong without the triangle inequality, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: given n cities and the cost of travelling between each pair, find the cheapest tour that visits every city once and comes home.", [s.head("Stage 1 of 7: the problem")] + hide("stages") + show("pb") + [hl("pb[0..=1]")])
s.step("It is NP-hard: Hamiltonian cycle reduces to it, as we saw in video 2.", [hl("pb[2]")])
s.step("We assume the triangle inequality: going from u to w directly never costs more than going via v. A detour never saves.", [hl("pb[3]")])
s.step("Real distances satisfy it. Our example uses city-block distance: blocks east-west plus blocks north-south.", [hl("pb[4]"), s.take("metric TSP: detours never help")])

s.scene("id")
s.step("Stage 2: take the optimal tour and delete one edge. What remains is a path through every city: a spanning tree.", [s.head("Stage 2 of 7: the idea"), s.untake()] + hide("pb") + show("id") + [hl("id[0]")])
s.step("So the minimum spanning tree weighs no more than the optimal tour. That is our lower bound.", [hl("id[1]")])
s.step("Walk around the spanning tree, like tracing its outline: every edge is used twice, once each way. That walk costs exactly twice the tree.", [hl("id[2]")])
s.step("The walk revisits cities. Skip each repeat, going straight to the next new city. By the triangle inequality, each shortcut costs no more.", [hl("id[3]"), s.take("tour ≤ walk = 2 × MST ≤ 2 × optimal")])

s.scene("ac")
s.step("Stage 3: Cormen's APPROX-TSP-TOUR. Choose a root, and build a minimum spanning tree with Prim's algorithm.", [s.head("Stage 3 of 7: the algorithm"), s.untake()] + hide("id") + show("ac") + [ml("ac", 1, 3)])
s.step("List the vertices in preorder: a depth-first walk, writing each vertex down the first time it is reached. That is exactly the shortcut walk.", [ml("ac", 4, 4)])
s.step("The tour visits them in that order and returns to the root.", [ml("ac", 5, 5)])
s.step("Prim on a complete graph costs O of V squared; the preorder walk is linear.", [ml("ac", 7, 7), s.take("MST, then preorder")])

s.scene("trace")
s.step("Stage 4: six cities on a street grid. Distances count blocks: the difference in x plus the difference in y. Here is the minimum spanning tree Prim builds from a.", [s.head("Stage 4 of 7: six cities"), s.untake()] + hide("ac") + show("g", "tt") + [st("tt[0][1]", "a–b 3, b–c 2, a–d 3, d–e 3, c–f 4", 0.4), hl("tt[0]")])
s.step("Its weight: 3 plus 2 plus 3 plus 3 plus 4, 15.", [st("tt[1][1]", "15"), hl("tt[1]")])
s.step("Preorder from a: a first, then its first child b, then b's child c, then c's child f. Back up to a's second child, d, then d's child e.", [st("tt[2][1]", "a, b, c, f, d, e"), hl("tt[2]"), hl("g.a"), hl("g.b", 0.15), hl("g.c", 0.3), hl("g.f", 0.45), hl("g.d", 0.6), hl("g.e", 0.75)])
s.step("The tour a, b, c, f, d, e, back to a. Its legs cost 3, 2, 4, 6, 3 and 6.", [st("tt[3][1]", "3 + 2 + 4 + 6 + 3 + 6"), hl("tt[3]")])
s.step("On the map: four legs are tree edges. The two shortcuts, f to d and e back to a, replace walking back along the tree.", [adde("g", "f", "d", "6"), adde("g", "e", "a", "6", 0.3)] + [mk(f"g.{e}", round(0.5 + 0.05 * i, 2)) for i, e in enumerate(["b->a", "c->b", "f->c", "f->d", "e->d", "e->a"])])
s.step("Total 24. Trying all 60 tours by brute force, the best is a, b, c, f, e, d, costing 20. Our tour is 1.2 times the optimum, well inside the factor 2.", [st("tt[4][1]", "24"), st("tt[5][1]", "a b c f e d: 20", 0.4), hl("tt[4..=5]"), mk("tt[4]", 0.6), s.take("approx 24 · optimal 20 · bound 2 × 15 = 30")])

s.scene("pf")
s.step("Stage 5: the proof. Delete any edge from an optimal tour: a spanning tree. So the MST costs at most the optimum.", [s.head("Stage 5 of 7: the factor 2"), s.untake()] + hide("g", "tt") + show("pf") + [hl("pf[0]")])
s.step("The full walk around the MST uses each edge twice: twice the MST.", [rv("pf[1]"), hl("pf[1]")])
s.step("Our tour is that walk with repeated cities skipped. Each skip replaces a detour by a direct hop, which by the triangle inequality is no longer.", [rv("pf[2]"), hl("pf[2]")])
s.step("Chain them: our tour is at most twice the MST, which is at most twice the optimum.", [rv("pf[3]"), mk("pf[3]")])
s.step("In the example: MST 15 is at most 20; our tour 24 is at most the walk, 30, which is at most 40.", [rv("pf[4]"), hl("pf[4]"), s.take("c(H) ≤ 2 c(MST) ≤ 2 c(H*)")])

s.scene("nt")
s.step("Stage 6: without the triangle inequality, no polynomial algorithm can guarantee any constant ratio, unless P equals NP.", [s.head("Stage 6 of 7: limits and better ratios"), s.untake()] + hide("pf") + show("nt") + [hl("nt[0]")])
s.step("The reason: give G's edges cost 1 and every other pair a huge cost. A good approximation would have to find a tour of cost n whenever one exists, which decides Hamiltonian cycle.", [hl("nt[1]")])
s.step("With the triangle inequality we can do better than 2. Christofides' algorithm adds a minimum matching on the odd-degree vertices of the MST, and achieves 1.5.", [hl("nt[2]")])
s.step("For points in the plane, approximation schemes get within any factor above 1. And in practice, local improvement like 2-opt brings tours within a few percent of optimal.", [hl("nt[3..=4]"), s.take("metric: 2 (or 1.5) · general: no constant")])

s.scene("exam")
s.step("Now an exam question on four cities.", [s.head("Exam question"), s.untake()] + hide("nt") + show("q") + [hl("q[0]")])
s.step("Build the MST, produce the approximate tour, and compare it with the optimum. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: from A, the cheapest edge is A, C, 3. Then A, B, 4. Then from the tree, B, D, 4. Weight 11.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: A's children are B and C; B's child is D. Preorder: A, B, D, C. The tour costs 4 plus 4 plus 5 plus 3: 16.", [hl("qa[1]")])
s.step("c: four cities have only three distinct tours: 16, 22 and 20. So 16 is optimal, and here the approximation found it exactly.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("And 16 is within twice the MST, 22, as the theorem promises.", [hl("qa[3]")])
s.step("The usual slip: walking the MST in level order instead of preorder. The proof needs the depth-first walk, whose shortcuts trace the doubled tree.", [s.take("preorder, not level order")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("With the triangle inequality, a minimum spanning tree costs at most the best tour, and its preorder walk, with repeats skipped, is a tour at most twice the tree.", [hl("stages[0..=4]")])
s.step("So APPROX-TSP-TOUR is a 2-approximation; Christofides reaches 1.5; without the triangle inequality, no constant ratio is possible unless P equals NP.", [hl("stages[5]")])
s.step("That completes Module 5, and the course: from arrays and lists, through trees, graphs and design techniques, to the limits of efficient computation.", [mk("stages[0..=6]"), s.take("End of the course")])

s.save("/home/claude/playlist/dsa5/d5v7.json")

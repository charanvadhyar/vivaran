"""DSA Module 5, video 2: reductions and NP-completeness."""
import sys, itertools
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa5")
from common import Script
from h import *

V = list("abcd"); E = {("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"), ("a", "c")}
inG = lambda x, y: (x, y) in E or (y, x) in E
cost = {(x, y): 0 if inG(x, y) else 1 for x, y in itertools.combinations(V, 2)}
assert sum(1 for c in cost.values() if c == 1) == 1 and cost[("b", "d")] == 1
def tours(V):
    for p in itertools.permutations(V[1:]):
        t = [V[0]] + list(p); yield t, sum(cost[tuple(sorted((t[i], t[(i + 1) % len(t)])))] for i in range(len(t)))
assert min(c for t, c in tours(V)) == 0
VE = list("pqrs"); EE = {("p", "q"), ("q", "r"), ("r", "s"), ("p", "r")}
inE = lambda x, y: (x, y) in EE or (y, x) in EE
ce = {(x, y): 0 if inE(x, y) else 1 for x, y in itertools.combinations(VE, 2)}
best = min(sum(ce[tuple(sorted((t[i], t[(i + 1) % 4])))] for i in range(4)) for t in ([VE[0]] + list(p) for p in itertools.permutations(VE[1:])))
assert best == 1 and sum(ce.values()) == 2 and len(ce) == 6

s = Script("Reductions and NP-completeness")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Reductions: solving one problem with another"],
    [2, "What a reduction tells us"],
    [3, "NP-hard and NP-complete"],
    [4, "A reduction worked: HAM-CYCLE to TSP"],
    [5, "How to prove a problem NP-complete"],
    [6, "The family tree of NP-complete problems"],
    [7, "Exam question"]]})
s.obj({"id": "rd", "type": "table", "region": "center", "columns": ["polynomial-time reduction  A ≤p B", ""], "rows": [
    ["a function f", "turns any instance x of A into an instance f(x) of B"],
    ["computable fast", "f runs in polynomial time"],
    ["preserves the answer", "x is a yes-instance of A  ⇔  f(x) is a yes-instance of B"],
    ["so", "to decide x, compute f(x) and ask B's algorithm"],
    ["everyday example", "\"is n odd?\" reduces to \"is the last digit odd?\""]]})
s.obj({"id": "wt", "type": "table", "region": "center", "columns": ["if A ≤p B", "then"], "rows": [
    ["B ∈ P", "A ∈ P: the reduction plus B's algorithm is polynomial"],
    ["A is hard", "B is at least as hard: otherwise A would be easy"],
    ["read ≤p as", "\"A is no harder than B\""],
    ["direction matters", "to show B hard, reduce a known hard problem TO B"]]})
s.obj({"id": "nc", "type": "table", "region": "center", "columns": ["definitions", ""], "rows": [
    ["NP-hard", "every problem in NP reduces to it"],
    ["NP-complete (NPC)", "NP-hard, and itself in NP"],
    ["key theorem", "if any NPC problem is in P, then P = NP"],
    ["contrapositive", "if P ≠ NP, no NPC problem has a polynomial algorithm"],
    ["NP-hard but not in NP", "e.g. the optimisation versions, or the halting problem"]]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "label": v, "at": p, "shape": "circle"} for v, p in {"a": [0, 3], "b": [3, 0], "c": [6, 3], "d": [3, 2]}.items()],
       "edges": [{"from": x, "to": y} for x, y in sorted(E)]})
s.obj({"id": "k", "type": "diagram", "region": "right", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "label": v, "at": p, "shape": "circle"} for v, p in {"a": [0, 3], "b": [3, 0], "c": [6, 3], "d": [3, 2]}.items()],
       "edges": [{"from": x, "to": y, "label": str(c)} for (x, y), c in sorted(cost.items())]})
s.obj({"id": "how", "type": "table", "region": "center", "columns": ["to prove that problem X is NP-complete", ""], "rows": [
    ["1. X ∈ NP", "give a certificate and a polynomial verifier"],
    ["2. pick a known NPC problem Y", "e.g. 3-CNF-SAT, CLIQUE, VERTEX-COVER"],
    ["3. design f", "turn every instance of Y into an instance of X"],
    ["4. prove both directions", "yes for Y ⇒ yes for X,  and  yes for X ⇒ yes for Y"],
    ["5. check f is polynomial", "then Y ≤p X, so X is NP-hard; with 1, NP-complete"]]})
s.obj({"id": "tree", "type": "diagram", "region": "center", "layout": "tree", "directed": True,
       "nodes": [{"id": i, "label": l} for i, l in [("cs", "CIRCUIT-SAT"), ("sat", "SAT"), ("cnf", "3-CNF-SAT"), ("cl", "CLIQUE"), ("ss", "SUBSET-SUM"), ("vc", "VERTEX-COVER"), ("hc", "HAM-CYCLE"), ("tsp", "TSP")]],
       "edges": [{"from": a, "to": b} for a, b in [("cs", "sat"), ("sat", "cnf"), ("cnf", "cl"), ("cnf", "ss"), ("cl", "vc"), ("vc", "hc"), ("hc", "tsp")]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) A ≤p B and B can be solved in O(n²). What follows about A?"],
    ["b) A ≤p B, A is NP-complete, and B ∈ NP. What is B?"],
    ["c) reduce HAM-CYCLE on vertices p, q, r, s with edges p–q, q–r, r–s, p–r to TSP: costs, k, and the answer"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "compute f(x) in polynomial time, then run B's algorithm on it", "A ∈ P"],
    ["b)", "every NP problem reduces to A, and A to B: B is NP-hard; and B ∈ NP", "B is NP-complete"],
    ["c)", "complete graph on 4 vertices: edges of G cost 0; p–s and q–s cost 1; k = 0", ""],
    ["c)", "s has only one edge in G, so every tour pays at least 1: cheapest tour costs 1 > 0", "TSP says no ⇒ no Hamiltonian cycle"]]})

s.scene("intro")
s.step("How can we say a problem is hard, when nobody has proved that it has no fast algorithm? By comparison: if a fast algorithm for it would also solve a problem known to be hard. That comparison is a reduction, and it is the main tool of this module.", [s.head("Reductions and NP-completeness")])
s.step("Here are the seven stages.", show("stages"))
s.step("Reductions, what they tell us, NP-hard and NP-complete, and a worked reduction.", [hl("stages[0..=3]")])
s.step("Then the recipe for NP-completeness proofs, the family tree of NP-complete problems, and an exam question.", [hl("stages[4..=6]")])

s.scene("rd")
s.step("Stage 1: a polynomial-time reduction from A to B is a function f that turns any instance of A into an instance of B.", [s.head("Stage 1 of 7: reductions")] + hide("stages") + show("rd") + [hl("rd[0]")])
s.step("f must run in polynomial time.", [hl("rd[1]")])
s.step("And it must preserve the answer: x is a yes-instance of A exactly when f of x is a yes-instance of B.", [hl("rd[2]")])
s.step("Then any algorithm for B also decides A: transform the input, and ask B.", [hl("rd[3]")])
s.step("An everyday example: is a number odd? Reduce it to: is its last digit odd? Ten easy cases answer every number.", [hl("rd[4]"), s.take("A ≤p B: transform A's input into B's")])

s.scene("wt")
s.step("Stage 2: if A reduces to B, and B is in P, then A is in P too: the transformation plus B's algorithm stays polynomial.", [s.head("Stage 2 of 7: what it tells us"), s.untake()] + hide("rd") + show("wt") + [hl("wt[0]")])
s.step("Turned round: if A is hard, B must be hard too, or A would be easy.", [hl("wt[1]")])
s.step("So read the symbol as: A is no harder than B.", [hl("wt[2]")])
s.step("The direction is the commonest mistake. To prove a new problem B hard, reduce a known hard problem to B, not B to it.", [hl("wt[3]"), s.take("reduce the known hard problem TO the new one")])

s.scene("nc")
s.step("Stage 3: a problem is NP-hard if every problem in NP reduces to it.", [s.head("Stage 3 of 7: NP-complete"), s.untake()] + hide("wt") + show("nc") + [hl("nc[0]")])
s.step("It is NP-complete if it is NP-hard and also in NP: the hardest problems inside NP.", [hl("nc[1]")])
s.step("The key theorem: if any single NP-complete problem has a polynomial algorithm, then every problem in NP does, and P equals NP.", [hl("nc[2]")])
s.step("Equivalently, if P is not NP, no NP-complete problem can be solved in polynomial time. That is why NP-complete means: stop looking for a fast exact algorithm.", [hl("nc[3]")])
s.step("Some problems are NP-hard without being in NP, such as the optimisation versions, which do not have yes-or-no answers.", [hl("nc[4]"), s.take("NPC = in NP + NP-hard")])
s.step("Thousands of practical problems are now known to be NP-complete: timetabling, routing, packing, circuit layout, protein folding models. They stand or fall together.", [hl("nc[2]")])

s.scene("ex")
s.step("Stage 4: Cormen's reduction from Hamiltonian cycle to the travelling salesman. Start with any graph G: here, four vertices and five edges.", [s.head("Stage 4 of 7: HAM-CYCLE ≤p TSP"), s.untake()] + hide("nc") + show("g") + [hl("g.a")])
s.step("Build a complete graph on the same vertices. An edge costs 0 if it is in G, and 1 if it is not. Here only b to d is missing from G, so it costs 1.", show("k") + [hl("k.b->d", 0.5)])
s.step("Ask TSP: is there a tour of cost at most k equal to 0?", [hl("k.a")])
s.step("A tour of cost 0 uses only edges of G, and visits every vertex once: exactly a Hamiltonian cycle. And a Hamiltonian cycle in G is a tour of cost 0. So the answers agree.", [mk("k.a->b"), mk("k.b->c", 0.2), mk("k.c->d", 0.4), mk("k.a->d", 0.6), mk("g.a->b"), mk("g.b->c", 0.2), mk("g.c->d", 0.4), mk("g.d->a", 0.6)])
s.step("Building the complete graph takes O of n squared time: polynomial. So Hamiltonian cycle reduces to TSP, and since Hamiltonian cycle is NP-complete, TSP is NP-hard.", [s.take("HAM-CYCLE ≤p TSP: cost 0 for edges of G")])
s.step("Notice what the reduction does not do: it never searches for a cycle. It only rewrites the question. All the hard work is left to whoever solves TSP.", [hl("k.b->d")])

s.scene("how")
s.step("Stage 5: the recipe for proving a problem X NP-complete. First, show X is in NP: give a certificate and a fast verifier.", [s.head("Stage 5 of 7: the recipe"), s.untake()] + hide("g", "k") + show("how") + [hl("how[0]")])
s.step("Second, choose a problem Y already known to be NP-complete.", [hl("how[1]")])
s.step("Third, design a transformation from instances of Y to instances of X.", [hl("how[2]")])
s.step("Fourth, prove both directions: a yes for Y gives a yes for X, and a yes for X gives a yes for Y.", [hl("how[3]")])
s.step("Fifth, check the transformation is polynomial. Then X is NP-hard, and with step 1, NP-complete.", [hl("how[4]"), s.take("in NP + known NPC ≤p X")])

s.scene("tree")
s.step("Stage 6: it all starts with circuit satisfiability. Cook and Levin showed directly that every NP problem reduces to it. It is the first NP-complete problem.", [s.head("Stage 6 of 7: the family tree"), s.untake()] + hide("how") + show("tree") + [hl("tree.cs")])
s.step("From there, Cormen chains reductions: circuit satisfiability to formula satisfiability, SAT, then to 3-CNF-SAT.", [hl("tree.sat"), hl("tree.cnf", 0.5)])
s.step("3-CNF-SAT reduces to CLIQUE, and to SUBSET-SUM.", [hl("tree.cl"), hl("tree.ss", 0.5)])
s.step("CLIQUE to VERTEX-COVER, then to HAM-CYCLE, and finally to TSP, the reduction we just saw.", [hl("tree.vc"), hl("tree.hc", 0.3), hl("tree.tsp", 0.6)])
s.step("The next three videos walk down the top of this tree: circuits and 3-CNF, then cliques, independent sets and vertex covers.", [mk("tree.cs"), mk("tree.sat", 0.1), mk("tree.cnf", 0.2), mk("tree.cl", 0.3), s.take("every arrow is a ≤p reduction")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("tree") + show("q") + [hl("q[0]")])
s.step("Draw conclusions from two reductions, and carry out one. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: transform A's input in polynomial time and run B's quadratic algorithm on it. The total is polynomial, so A is in P.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: every NP problem reduces to A, and A reduces to B, so every NP problem reduces to B: B is NP-hard. Since B is in NP, it is NP-complete.", [hl("qa[1]")])
s.step("c: build the complete graph on p, q, r, s. The four edges of G cost 0. The two missing ones, p to s and q to s, cost 1. Ask for a tour of cost at most 0.", [hl("qa[2]")])
s.step("Vertex s has only one edge in G, to r, but a tour needs two edges at every vertex. So every tour pays at least 1. TSP answers no, and correctly: G has no Hamiltonian cycle.", [hl("qa[3]"), mk("qa[3][2]", 0.5)])
s.step("The usual slip: reducing the new problem to a known hard one. That shows nothing about hardness. Reduce the known hard problem to the new one.", [s.take("known NPC ≤p new problem")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A reduction transforms instances of A into instances of B in polynomial time, preserving the answer. It shows A is no harder than B.", [hl("stages[0..=3]")])
s.step("NP-complete problems are in NP and NP-hard. To add one, reduce a known NP-complete problem to it. The tree starts at circuit satisfiability.", [hl("stages[4..=5]")])
s.step("Next video: the root of the tree. Circuit satisfiability, and 3-CNF satisfiability.", [mk("stages[0..=6]"), s.take("Next: Circuit-SAT and 3-CNF-SAT")])

s.save("/home/claude/playlist/dsa5/d5v2.json")

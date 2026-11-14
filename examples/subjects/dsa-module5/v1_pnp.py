"""DSA Module 5, video 1: the classes P and NP."""
import sys, itertools, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa5")
from common import Script
from h import *

V = [1, 2, 3, 4, 5]; E = {(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (1, 4)}
adj = lambda a, b: (a, b) in E or (b, a) in E
cert = [1, 2, 4, 5, 3]
assert all(adj(cert[i], cert[(i + 1) % 5]) for i in range(5)) and sorted(cert) == V
bad = [1, 2, 3, 4, 5]; assert not adj(3, 4)
assert math.factorial(4) // 2 == 12 and math.factorial(19) // 2 > 10 ** 16
assert 2 ** 60 > 10 ** 18 and 60 ** 3 == 216000

POS = {1: [0, 0], 2: [2, 0], 3: [1, 1], 4: [3, 1], 5: [2, 2]}
s = Script("Complexity classes: P and NP")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Tractable and intractable"],
    [2, "Decision problems"],
    [3, "The class P"],
    [4, "The class NP: checking a certificate"],
    [5, "Easy problems with hard twins"],
    [6, "P ⊆ NP, and the open question"],
    [7, "Exam question"]]})
s.obj({"id": "tr", "type": "table", "region": "center", "columns": ["n = 60", "steps", "at 10⁹ steps per second"], "rows": [
    ["n³", "216,000", "0.0002 seconds"],
    ["2ⁿ", "about 1.15 × 10¹⁸", "over 36 years"],
    ["tractable", "solvable in O(nᵏ) for some constant k", "polynomial time"],
    ["intractable", "no polynomial algorithm known (or possible)", "exponential in practice"]]})
s.obj({"id": "dp", "type": "table", "region": "center", "columns": ["optimisation problem", "decision version: answer yes or no"], "rows": [
    ["shortest path from u to v", "PATH: is there a path from u to v with at most k edges?"],
    ["travelling salesman: cheapest tour", "TSP: is there a tour of cost at most k?"],
    ["largest clique", "CLIQUE: is there a clique of size k?"],
    ["why decision versions", "if the decision version is hard, the optimisation is at least as hard"]]})
s.obj({"id": "pc", "type": "table", "region": "center", "columns": ["the class P", ""], "rows": [
    ["P", "decision problems solvable in O(nᵏ) time, for some constant k, on input size n"],
    ["examples", "sorting, shortest paths, MST, max flow, 2-colouring, LCS, matrix chains"],
    ["closed under composition", "a polynomial algorithm calling a polynomial subroutine is still polynomial"],
    ["the working definition of efficient", "n¹⁰⁰ is in P, but natural problems rarely need such exponents"]]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": f"v{v}", "label": str(v), "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": f"v{a}", "to": f"v{b}"} for a, b in sorted(E)]})
s.obj({"id": "np", "type": "table", "region": "right", "columns": ["the class NP", ""], "rows": [
    ["HAM-CYCLE", "a cycle through every vertex once?"],
    ["certificate", "an order of the vertices"],
    ["verifier", "checks it in polynomial time"],
    ["NP", "yes-answers checkable fast"],
    ["the name", "nondeterministic polynomial"]]})
s.obj({"id": "tw", "type": "table", "region": "center", "columns": ["in P", "its look-alike, NP-complete"], "rows": [
    ["shortest simple path", "longest simple path"],
    ["Euler tour: every edge once", "Hamiltonian cycle: every vertex once"],
    ["2-CNF satisfiability", "3-CNF satisfiability"],
    ["2-colouring", "3-colouring"],
    ["minimum spanning tree", "travelling salesman"]]})
s.obj({"id": "pn", "type": "table", "region": "center", "columns": ["P and NP", ""], "rows": [
    ["P ⊆ NP", "if you can solve it fast, you can check it fast: ignore the certificate and solve"],
    ["P = NP?", "unknown: the most famous open problem in computer science"],
    ["most researchers believe", "P ≠ NP: checking is easier than finding"],
    ["Clay Millennium Prize", "one million dollars for a proof either way"],
    ["NP-complete (next videos)", "the hardest problems in NP: a fast algorithm for one gives one for all"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) SUBSET-SUM: do some of the given numbers add up to t? Give a certificate and a verifier's cost"],
    ["b) is \"given a graph, is there NO Hamiltonian cycle?\" obviously in NP? why?"],
    ["c) is \"is there a path from u to v with at most k edges?\" in P? in NP?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "certificate: the chosen subset; add it up, compare with t", "O(n) additions: in NP"],
    ["b)", "what short certificate would prove that no cycle exists?", "not obviously: it is in co-NP"],
    ["c)", "BFS answers it in O(V + E)", "in P, hence also in NP"]]})

s.scene("intro")
s.step("Some problems have fast algorithms, and for others, after decades of effort, nobody has found one. Module 5 makes that difference precise. This first video defines the two classes everything else rests on: P and NP.", [s.head("Complexity classes: P and NP")])
s.step("Here are the seven stages.", show("stages"))
s.step("Tractable and intractable problems, decision problems, the class P, and the class NP.", [hl("stages[0..=3]")])
s.step("Then easy problems with hard twins, how P and NP relate, and an exam question.", [hl("stages[4..=6]")])

s.scene("tr")
s.step("Stage 1: compare n cubed and 2 to the n for an input of size 60. n cubed is 216 thousand steps: a fraction of a millisecond.", [s.head("Stage 1 of 7: tractable or not")] + hide("stages") + show("tr") + [hl("tr[0]")])
s.step("2 to the 60 is over a billion billion steps: more than 36 years at a billion steps a second.", [hl("tr[1]")])
s.step("So we call a problem tractable if some algorithm solves it in polynomial time, O of n to the k for a constant k.", [hl("tr[2]")])
s.step("Intractable problems have no known polynomial algorithm, and in practice we only know exponential ones.", [hl("tr[3]"), s.take("polynomial = tractable")])
s.step("Faster hardware does not rescue an exponential algorithm. A computer a thousand times faster lets a 2 to the n algorithm handle inputs only 10 larger, since 2 to the 10 is about a thousand. For n cubed, the input can grow ten times.", [hl("tr[1]")])

s.scene("dp")
s.step("Stage 2: complexity theory studies decision problems, whose answer is yes or no. Shortest path becomes: is there a path with at most k edges?", [s.head("Stage 2 of 7: decision problems"), s.untake()] + hide("tr") + show("dp") + [hl("dp[0]")])
s.step("The travelling salesman becomes: is there a tour of cost at most k? The largest clique becomes: is there a clique of size k?", [hl("dp[1..=2]")])
s.step("This loses nothing that matters. If the yes-or-no version is already hard, the optimisation version, which answers it, is at least as hard.", [hl("dp[3]"), s.take("decision problems: answer yes or no")])

s.scene("p")
s.step("Stage 3: P is the class of decision problems that can be solved in polynomial time.", [s.head("Stage 3 of 7: the class P"), s.untake()] + hide("dp") + show("pc") + [hl("pc[0]")])
s.step("Almost everything in this course so far is in P: sorting, shortest paths, spanning trees, maximum flow, two-colouring, the dynamic programs.", [hl("pc[1]")])
s.step("P is robust: a polynomial algorithm that calls a polynomial subroutine polynomially often is still polynomial.", [hl("pc[2]")])
s.step("n to the 100 is technically in P, but natural problems in P almost always have small exponents, so P is a good working definition of efficient.", [hl("pc[3]"), s.take("P: solvable in polynomial time")])

s.scene("np")
s.step("Stage 4: consider the Hamiltonian cycle problem: is there a cycle that visits every vertex exactly once? No polynomial algorithm is known.", [s.head("Stage 4 of 7: the class NP"), s.untake()] + hide("pc") + show("g", "np") + [hl("np[0]")])
s.step("But suppose someone hands us an answer: the order 1, 2, 4, 5, 3. That is a certificate.", [hl("np[1]"), hl("g.v1"), hl("g.v2", 0.15), hl("g.v4", 0.3), hl("g.v5", 0.45), hl("g.v3", 0.6)])
s.step("Checking it is easy. Every vertex appears once. And each consecutive pair is an edge: 1 to 2, 2 to 4, 4 to 5, 5 to 3, and 3 back to 1. Yes: a Hamiltonian cycle.", [hl("np[2]"), mk("g.v1->v2"), mk("g.v2->v4", 0.15), mk("g.v4->v5", 0.3), mk("g.v3->v5", 0.45), mk("g.v1->v3", 0.6)])
s.step("A wrong certificate, like 1, 2, 3, 4, 5, fails at once: 3 and 4 are not joined. Checking takes O of n squared time at most.", [hl("g.v3"), hl("g.v4", 0.3)])
s.step("NP is the class of decision problems whose yes-answers have certificates that can be checked in polynomial time. The name means nondeterministic polynomial: a machine that could guess the certificate would solve the problem fast.", [hl("np[3..=4]"), s.take("NP: a yes-answer can be checked fast")])

s.scene("tw")
s.step("Stage 5: hard problems often look almost exactly like easy ones. Shortest simple path is in P; longest simple path is NP-complete.", [s.head("Stage 5 of 7: hard twins"), s.untake()] + hide("g", "np") + show("tw") + [hl("tw[0]")])
s.step("An Euler tour, using every edge once, is easy to decide. A Hamiltonian cycle, using every vertex once, is hard.", [hl("tw[1]")])
s.step("Satisfiability with two literals per clause is in P; with three it is NP-complete. Two-colouring is BFS; three-colouring is hard.", [hl("tw[2..=3]")])
s.step("Trying every order of the vertices to find a Hamiltonian cycle means trying n minus 1 factorial over 2 orders: 12 for 5 vertices, but over 10 to the 16 for 20. That is why a certificate, which skips the search, is so valuable.", [hl("tw[1]")])
s.step("And the minimum spanning tree is greedy and fast, while the travelling salesman, which also connects every city cheaply, is hard. A small change in the question can cross the line.", [hl("tw[4]"), s.take("small changes, huge difference")])

s.scene("pn")
s.step("Stage 6: every problem in P is in NP. If you can solve it fast, you can check a yes-answer by just solving it.", [s.head("Stage 6 of 7: P versus NP"), s.untake()] + hide("tw") + show("pn") + [hl("pn[0]")])
s.step("Is every problem in NP also in P? Nobody knows. It is the most famous open question in computer science.", [hl("pn[1]")])
s.step("Most researchers believe P is not NP: that finding an answer is genuinely harder than checking one. A proof either way would earn a million-dollar Millennium Prize.", [hl("pn[2..=3]")])
s.step("The next videos meet the NP-complete problems: the hardest in NP. A polynomial algorithm for any one of them would give one for all of NP.", [hl("pn[4]"), s.take("P ⊆ NP; P = NP is open")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("pn") + show("q") + [hl("q[0]")])
s.step("Give a certificate and its checking cost, decide whether a negative question is obviously in NP, and classify a path problem. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: for subset sum, the certificate is the chosen subset. Add its numbers and compare with t: linear time. So subset sum is in NP.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: to prove a graph has no Hamiltonian cycle, what short certificate could we hand over? None is known. Such complements of NP problems form the class co-NP, which is not known to equal NP.", [hl("qa[1]")])
s.step("c: breadth-first search answers it in O of V plus E. So it is in P, and therefore also in NP.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("The usual slip: thinking NP means not polynomial. NP means checkable in polynomial time, and it includes all of P.", [s.take("NP ≠ “not polynomial”")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("We study yes-or-no problems. P holds those solvable in polynomial time; NP those whose yes-answers can be checked in polynomial time, given a certificate.", [hl("stages[0..=3]")])
s.step("Many problems in NP have near twins in P. P is inside NP, and whether they are equal is open.", [hl("stages[4..=5]")])
s.step("Next video: how to compare problems. Reductions, and the meaning of NP-complete.", [mk("stages[0..=6]"), s.take("Next: reductions and NP-completeness")])

s.save("/home/claude/playlist/dsa5/d5v1.json")

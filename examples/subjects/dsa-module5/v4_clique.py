"""DSA Module 5, video 4: independent set and clique."""
import sys, itertools
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa5")
from common import Script
from h import *

CL = [[1, -2, -3], [-1, 2, 3], [1, 2, 3]]
nodes = [(c, i, l) for c, cl in enumerate(CL) for i, l in enumerate(cl)]
edges = [(a, b) for a, b in itertools.combinations(nodes, 2) if a[0] != b[0] and a[2] != -b[2]]
assert len(edges) == 21
clique = [(0, 1, -2), (1, 2, 3), (2, 2, 3)]
assert all((a, b) in edges or (b, a) in edges for a, b in itertools.combinations(clique, 2))
def satf(a): return all(any((a[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in CL)
assert satf((0, 0, 1)) and satf((1, 0, 1))
# C5
C5 = {(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)}
adj = lambda a, b: (a, b) in C5 or (b, a) in C5
def maxind(n, adj):
    for k in range(n, 0, -1):
        for S in itertools.combinations(range(n), k):
            if all(not adj(a, b) for a, b in itertools.combinations(S, 2)): return k, S
assert maxind(5, adj)[0] == 2
comp = lambda a, b: a != b and not adj(a, b)
assert maxind(5, comp)[0] == 2  # max clique of C5 = max independent set of complement
assert all(sum(1 for b in range(5) if comp(a, b)) == 2 for a in range(5))

lab = lambda l: ("x" if l > 0 else "¬x") + str(abs(l))
nid = lambda n: f"c{n[0]}{n[1]}"
POS = {(0, 0): [1, 0], (0, 1): [3, 0], (0, 2): [5, 0], (1, 0): [0, 2], (1, 1): [0, 4], (1, 2): [0, 6], (2, 0): [6, 2], (2, 1): [6, 4], (2, 2): [6, 6]}
s = Script("Independent set and clique")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Cliques and independent sets"],
    [2, "Both are in NP"],
    [3, "3-CNF-SAT ≤p CLIQUE: the construction"],
    [4, "Why the reduction is correct"],
    [5, "Clique ⇔ independent set ⇔ vertex cover"],
    [6, "What this means in practice"],
    [7, "Exam question"]]})
s.obj({"id": "df", "type": "table", "region": "center", "columns": ["in an undirected graph", ""], "rows": [
    ["clique", "a set of vertices, every two joined by an edge"],
    ["independent set", "a set of vertices, no two joined by an edge"],
    ["CLIQUE", "is there a clique of size k?"],
    ["INDEPENDENT-SET", "is there an independent set of size k?"],
    ["uses", "clique: tightly knit groups in social networks · independent set: non-conflicting schedules"]]})
s.obj({"id": "np", "type": "table", "region": "center", "columns": ["in NP", ""], "rows": [
    ["certificate", "the k vertices"],
    ["check a clique", "all k(k − 1)/2 pairs are edges: O(k²) lookups"],
    ["check an independent set", "no pair is an edge: O(k²)"],
    ["brute force", "try all C(n, k) subsets: exponential when k grows with n"]]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": nid(n), "label": lab(n[2]), "at": POS[(n[0], n[1])], "shape": "circle"} for n in nodes],
       "edges": [{"from": nid(a), "to": nid(b)} for a, b in edges]})
s.obj({"id": "rc", "type": "table", "region": "right", "columns": ["clause", "literals (where)"], "rows": [
    ["C1", "x1 ∨ ¬x2 ∨ ¬x3 (top)"],
    ["C2", "¬x1 ∨ x2 ∨ x3 (left)"],
    ["C3", "x1 ∨ x2 ∨ x3 (right)"],
    ["edge", "different clauses, not x with ¬x"],
    ["ask", "a clique of size 3?"]]})
s.obj({"id": "pf", "type": "table", "region": "center", "columns": ["why it works", ""], "rows": [
    ["formula satisfiable ⇒ clique", "pick one true literal per clause; true literals never clash, and come from different clauses: all joined"],
    ["clique of size k ⇒ satisfiable", "no edges inside a clause, so one vertex per clause; no x with ¬x, so set them all true"],
    ["here", "¬x2 from C1, x3 from C2, x3 from C3: x2 = 0, x3 = 1, any x1"],
    ["size of the graph", "3m vertices, O(m²) edges: built in polynomial time"]]})
s.obj({"id": "eq", "type": "table", "region": "center", "columns": ["three views of one problem", ""], "rows": [
    ["S is a clique in G", "⇔ S is an independent set in the complement Ḡ"],
    ["S is an independent set", "⇔ V − S is a vertex cover: every edge has an end outside S"],
    ["so", "max independent set + min vertex cover = n"],
    ["reductions", "CLIQUE ≤p INDEPENDENT-SET ≤p VERTEX-COVER, each in polynomial time"],
    ["all three", "NP-complete"]]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["in practice", ""], "rows": [
    ["k fixed (say 3)", "try all C(n, 3) triples: O(n³), polynomial"],
    ["k part of the input", "NP-complete: k = n/2 has exponentially many subsets"],
    ["special graphs", "bipartite graphs: max independent set via max flow, in P"],
    ["large graphs", "branch and bound, or approximations (next videos)"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: the 5-cycle 1–2–3–4–5–1"], "rows": [
    ["a) the largest independent set"],
    ["b) the smallest vertex cover"],
    ["c) the largest clique, and the complement graph"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "three vertices of a 5-cycle always include two neighbours", "size 2, e.g. {1, 3}"],
    ["b)", "n − max independent set = 5 − 2", "size 3, e.g. {2, 4, 5}"],
    ["c)", "no triangle in a 5-cycle", "size 2: any edge"],
    ["c)", "complement joins 1–3, 3–5, 5–2, 2–4, 4–1", "another 5-cycle"]]})

s.scene("intro")
s.step("Find a group of people who all know one another. Or a group in which nobody knows anybody else. These are the clique and independent-set problems, and this video proves them NP-complete, by turning any 3-CNF formula into a graph.", [s.head("Independent set and clique")])
s.step("Here are the seven stages.", show("stages"))
s.step("The definitions, why both are in NP, and Cormen's reduction from 3-CNF-SAT to CLIQUE.", [hl("stages[0..=3]")])
s.step("Then the links between clique, independent set and vertex cover, what this means in practice, and an exam question.", [hl("stages[4..=6]")])

s.scene("df")
s.step("Stage 1: a clique is a set of vertices in which every two are joined by an edge.", [s.head("Stage 1 of 7: definitions")] + hide("stages") + show("df") + [hl("df[0]")])
s.step("An independent set is the opposite: no two of its vertices are joined.", [hl("df[1]")])
s.step("The decision problems ask: is there a clique of size k? Is there an independent set of size k?", [hl("df[2..=3]")])
s.step("Cliques find tight communities in networks; independent sets pick tasks that do not conflict.", [hl("df[4]"), s.take("clique: all joined · independent: none joined")])

s.scene("np")
s.step("Stage 2: both are in NP. The certificate is the k vertices.", [s.head("Stage 2 of 7: in NP"), s.untake()] + hide("df") + show("np") + [hl("np[0]")])
s.step("For a clique, check that all k times k minus 1 over 2 pairs are edges. For an independent set, that none are. Quadratic time.", [hl("np[1..=2]")])
s.step("Finding one by brute force means trying all subsets of size k: exponential when k grows with n.", [hl("np[3]"), s.take("certificate: the k vertices")])

s.scene("red")
s.step("Stage 3: now reduce 3-CNF-SAT to CLIQUE. Take Cormen's formula with three clauses.", [s.head("Stage 3 of 7: the construction"), s.untake()] + hide("np") + show("g", "rc") + [hl("rc[0..=2]")])
s.step("Make one vertex for each literal in each clause: 9 vertices. The top row is clause 1, the left column clause 2, the right column clause 3.", [hl("rc[0]"), hl("g.c00"), hl("rc[1]", 0.3), hl("g.c10", 0.3), hl("rc[2]", 0.6), hl("g.c20", 0.6)])
s.step("Join two literals when they are in different clauses and are not a variable and its own negation.", [hl("rc[3]")])
s.step("For example, x1 at the top and not x1 at the left are not joined: they could never both be true. But x1 at the top and x2 at the left are joined.", [hl("g.c00"), hl("g.c10", 0.3), hl("g.c00->c11", 0.6)])
s.step("So there are no edges inside a clause, and none between, say, x1 in clause 1 and not x1 in clause 2. Of the 27 cross-clause pairs, 6 are dropped: 21 edges.", [hl("rc[3]")])
s.step("Ask CLIQUE: is there a clique whose size equals the number of clauses, 3?", [hl("rc[4]"), s.take("vertex per literal; edge = compatible, different clauses")])

s.scene("pf")
s.step("Here is one: not x2 from clause 1, x3 from clause 2, x3 from clause 3. All three pairs are joined.", [s.head("Stage 4 of 7: why it works"), mk("g.c01"), mk("g.c12", 0.3), mk("g.c22", 0.6), mk("g.c01->c12", 0.4), mk("g.c01->c22", 0.5), mk("g.c12->c22", 0.6)])
s.step("Stage 4: if the formula is satisfiable, pick one true literal in each clause. They come from different clauses, and true literals can never be x and not x, so all pairs are joined: a clique of size k.", hide("g", "rc") + show("pf") + [hl("pf[0]")])
s.step("Conversely, a clique of size k has one vertex per clause, since a clause has no internal edges, and never both x and not x. Make all its literals true: every clause is satisfied.", [hl("pf[1]")])
s.step("Our clique says x2 is false and x3 is true, with x1 free. Check: clause 1 holds by not x2, clauses 2 and 3 by x3.", [hl("pf[2]")])
s.step("The graph has 3m vertices and at most m squared times 9 over 2 edges, built in polynomial time. So CLIQUE is NP-complete.", [hl("pf[3]"), s.take("3-CNF-SAT ≤p CLIQUE")])

s.scene("eq")
s.step("Stage 5: a clique in a graph is an independent set in its complement, the graph with exactly the missing edges. So CLIQUE reduces to INDEPENDENT-SET in polynomial time.", [s.head("Stage 5 of 7: three views"), s.untake()] + hide("pf") + show("eq") + [hl("eq[0]")])
s.step("And S is an independent set exactly when the remaining vertices, V minus S, form a vertex cover: since no edge lies inside S, every edge has an end outside it.", [hl("eq[1]")])
s.step("So the largest independent set plus the smallest vertex cover always add up to n.", [hl("eq[2]")])
s.step("In a social network, a vertex cover is a set of people that touches every friendship. Its complement is a set of mutual strangers: the two problems are two sides of one coin.", [hl("eq[1]")])
s.step("These easy transformations chain the three problems together: all three are NP-complete.", [hl("eq[3..=4]"), s.take("max independent set + min vertex cover = n")])

s.scene("pr")
s.step("Stage 6: for a fixed k, such as 3, try all triples: O of n cubed, polynomial. The hardness comes when k is part of the input.", [s.head("Stage 6 of 7: in practice"), s.untake()] + hide("eq") + show("pr") + [hl("pr[0..=1]")])
s.step("Special graphs can be easy: in bipartite graphs, the largest independent set comes from a maximum flow.", [hl("pr[2]")])
s.step("And when k is small and fixed, say finding groups of 4 mutual friends, trying every 4-subset of a few thousand people is perfectly feasible. NP-completeness bites when k grows with n.", [hl("pr[0]")])
s.step("For large general graphs, we use branch and bound, or settle for approximations, as the next videos do.", [hl("pr[3]"), s.take("hard in general, easy for fixed k")])

s.scene("exam")
s.step("Now an exam question on a 5-cycle.", [s.head("Exam question"), s.untake()] + hide("pr") + show("q") + [hl("q[0]")])
s.step("Find the largest independent set, the smallest vertex cover, and the largest clique. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: any three vertices of a 5-cycle include two neighbours. So the largest independent set has 2 vertices, such as 1 and 3.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: the smallest vertex cover is the rest: 5 minus 2, 3 vertices: 2, 4 and 5.", [hl("qa[1]"), mk("qa[1][2]", 0.5)])
s.step("c: a 5-cycle has no triangle, so the largest clique is a single edge: size 2.", [hl("qa[2]")])
s.step("Its complement joins each vertex to the two it was not joined to: 1 to 3, 3 to 5, 5 to 2, 2 to 4, 4 to 1. Another 5-cycle, whose largest independent set is again 2, matching the clique.", [hl("qa[3]")])
s.step("The usual slip: allowing edges inside a clause in the reduction. Without that rule, a clique could take two literals from one clause and none from another.", [s.take("no edges inside a clause")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("CLIQUE and INDEPENDENT-SET are in NP. Cormen's reduction makes a vertex per literal, joins compatible literals in different clauses, and asks for a clique the size of the clause count.", [hl("stages[0..=3]")])
s.step("Complements turn cliques into independent sets, and the leftover vertices form a vertex cover: all three are NP-complete.", [hl("stages[4..=5]")])
s.step("Next video: if we cannot find the smallest vertex cover fast, can we get close? A 2-approximation, from the lab.", [mk("stages[0..=6]"), s.take("Next: approximating vertex cover")])

s.save("/home/claude/playlist/dsa5/d5v4.json")

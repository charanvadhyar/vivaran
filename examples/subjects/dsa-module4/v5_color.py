"""DSA Module 4, video 5: graph colouring by backtracking."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa4")
from common import Script
from h import *
from bt import mcolor

V = list("ABCDEF"); E = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "E"), ("C", "E"), ("C", "F"), ("D", "E"), ("D", "F")]
EV, SOL = mcolor(V, E, 3)
assert [e for e in EV if e[0] != "reject"] == [("color", "A", 1), ("color", "B", 2), ("color", "C", 3), ("color", "D", 1), ("dead", "E"), ("uncolor", "D", 1), ("color", "D", 2), ("color", "E", 1), ("color", "F", 1), ("solution", {"A": 1, "B": 2, "C": 3, "D": 2, "E": 1, "F": 1})]
assert not mcolor(V, E, 2)[1] and len(mcolor(V, E, 3, True)[1]) == 18
VQ = list("1234"); EQ = [("1", "2"), ("2", "3"), ("3", "4"), ("4", "1"), ("1", "3")]
QE, QS = mcolor(VQ, EQ, 3); assert QS == [{"1": 1, "2": 2, "3": 3, "4": 2}] and not mcolor(VQ, EQ, 2)[1] and len(mcolor(VQ, EQ, 3, True)[1]) == 6
assert 3 ** 6 == 729

NAME = {1: "red", 2: "green", 3: "blue"}
POS = {"A": [0, 1], "B": [2, 0], "C": [2, 2], "E": [4, 0], "F": [4, 2], "D": [6, 1]}
s = Script("Backtracking: graph colouring")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The m-colouring problem"],
    [2, "The state-space tree"],
    [3, "The algorithm"],
    [4, "Six vertices, three colours, traced"],
    [5, "Chromatic number; two colours are easy"],
    [6, "Counting all colourings; cost"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["graph colouring", ""], "rows": [
    ["m-colouring", "give each vertex one of m colours, so that adjacent vertices differ"],
    ["chromatic number χ(G)", "the least m for which this is possible"],
    ["maps", "countries = vertices, shared borders = edges: four colours always suffice for a flat map"],
    ["timetables", "exams = vertices, a shared student = an edge, colours = time slots"],
    ["compilers", "variables = vertices, live at the same time = edge, colours = registers"]]})
s.obj({"id": "tr", "type": "table", "region": "center", "columns": ["state-space tree", ""], "rows": [
    ["x[i]", "the colour of vertex i, from 1 to m"],
    ["level i", "colours vertex i: m children per node"],
    ["full tree", "mⁿ leaves: 3 colours, 6 vertices: 729"],
    ["bounding function", "the colour of vertex i must differ from every coloured neighbour"]]})
s.obj({"id": "pc", "type": "code", "region": "center", "language": "text", "lines": [
    "MCOLORING(k)          // colour vertices k .. n;  x[1 .. k−1] already coloured",
    "    for c = 1 to m",
    "        if no neighbour j of k, with j < k, has x[j] == c",
    "            x[k] = c",
    "            if k == n:  print x[1 .. n]",
    "            else MCOLORING(k + 1)",
    "    x[k] = 0              // no colour worked: backtrack"]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "label": v, "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": a, "to": b} for a, b in E]})
s.obj({"id": "ct", "type": "table", "region": "right", "columns": ["vertex", "neighbours", "colour"],
       "rows": [[v, ", ".join(sorted(u for a, b in E for u, w in ((a, b), (b, a)) if w == v)), ""] for v in V]})
s.obj({"id": "chi", "type": "table", "region": "center", "columns": ["chromatic number", ""], "rows": [
    ["our graph", "A, B, C form a triangle: χ ≥ 3; we found 3 colours: χ = 3"],
    ["m = 2", "possible exactly when the graph is bipartite: no odd cycle"],
    ["test for 2", "BFS, colouring each level alternately: O(V + E)"],
    ["m = 3 and above", "NP-complete (Module 5): no polynomial algorithm is known"],
    ["finding χ", "try m = 1, 2, 3, … until MCOLORING succeeds"]]})
s.obj({"id": "ac", "type": "table", "region": "center", "columns": ["all colourings", ""], "rows": [
    ["do not stop at the first", "print, then keep looping as if it had failed"],
    ["our graph, m = 3", "18 colourings: 3! = 6 for the triangle; E is forced; D and F: 3 ways"],
    ["worst case", "O(n · mⁿ): the tree is mⁿ leaves, each check O(n)"],
    ["practical order", "colour high-degree vertices first: conflicts appear earlier"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["vertices 1, 2, 3, 4; edges 1–2, 2–3, 3–4, 4–1, 1–3"],
    ["a) is the graph 2-colourable?"],
    ["b) the first 3-colouring MCOLORING finds"],
    ["c) how many 3-colourings are there in all?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "1, 2, 3 form a triangle: an odd cycle", "no: χ ≥ 3"],
    ["b)", "1 → 1;  2 → 2 (1 is a neighbour);  3 → 3 (neighbours 1, 2)", ""],
    ["b)", "4: neighbours 1 and 3 have colours 1 and 3 → 2", "x = (1, 2, 3, 2)"],
    ["c)", "triangle 1, 2, 3: 3! = 6 ways; 4 must take the colour of 2: 1 way", "6"]]})

def colstep(v, c, d=0.0):
    i = V.index(v); return [st(f"g.{v}", f"{v} {c}", d), st(f"ct[{i}][2]", f"{c} {NAME[c]}", d + 0.1), hl(f"ct[{i}]", d)]

s.scene("intro")
s.step("Colour a map so that neighbouring countries differ. Schedule exams so that no student has two at once. Assign variables to processor registers. All three are the same problem: colouring the vertices of a graph. Backtracking solves it exactly.", [s.head("Backtracking: graph colouring")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem, the state-space tree, the algorithm, and a traced example.", [hl("stages[0..=3]")])
s.step("Then the chromatic number, counting all colourings, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: an m-colouring gives each vertex one of m colours, with every edge joining two different colours.", [s.head("Stage 1 of 7: the problem")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("The chromatic number, chi of G, is the smallest m that works.", [hl("pb[1]")])
s.step("A triangle needs 3 colours: each vertex touches the other two. A graph with no edges needs only 1. Most graphs lie in between, and finding the exact number is the hard part.", [hl("pb[1]")])
s.step("For maps, countries are vertices and shared borders are edges. Any flat map needs at most four colours: the famous four colour theorem.", [hl("pb[2]")])
s.step("For exam timetables, exams are vertices and an edge means a student takes both: colours are time slots. Compilers do the same with registers.", [hl("pb[3..=4]"), s.take("adjacent vertices, different colours")])

s.scene("tr")
s.step("Stage 2: x i is the colour of vertex i, a number from 1 to m.", [s.head("Stage 2 of 7: the tree"), s.untake()] + hide("pb") + show("tr") + [hl("tr[0]")])
s.step("Level i of the tree colours vertex i, so every node has m children.", [hl("tr[1]")])
s.step("The full tree has m to the n leaves: 729 for 6 vertices and 3 colours.", [hl("tr[2]")])
s.step("The bounding function: the colour of vertex i must differ from every neighbour already coloured. A branch dies the moment it breaks this.", [hl("tr[3]"), s.take("x[i] ≠ x[j] for every coloured neighbour j")])

s.scene("algo")
s.step("Stage 3: MCOLORING colours vertex k, assuming vertices 1 to k minus 1 are done. Try each colour in turn.", [s.head("Stage 3 of 7: the algorithm"), s.untake()] + hide("tr") + show("pc") + [ml("pc", 1, 2)])
s.step("A colour is allowed if no earlier neighbour already has it.", [ml("pc", 3, 3)])
s.step("Assign it, then either print a complete colouring or recurse to the next vertex.", [ml("pc", 4, 6)])
s.step("If every colour fails, reset x k and return: that is the backtrack, and the caller tries its next colour.", [ml("pc", 7, 7), s.take("try colours in order; undo on failure")])

s.scene("trace")
s.step("Stage 4: six vertices and three colours: 1 red, 2 green, 3 blue. A, B and C form a triangle. Colour in the order A to F.", [s.head("Stage 4 of 7: a trace"), s.untake()] + hide("pc") + show("g", "ct"))
s.step("A takes colour 1. B is adjacent to A, so 1 is out: B takes 2. C is adjacent to both: it takes 3.", colstep("A", 1) + colstep("B", 2, 0.3) + colstep("C", 3, 0.6))
s.step("D has no coloured neighbours yet: E and F are still blank. D takes 1.", colstep("D", 1))
s.step("E is adjacent to B, C and D: colours 2, 3 and 1. All three are used. A dead end.", [hl("g.E"), st("ct[4][2]", "none fits", 0.4), hl("ct[4]", 0.4)])
s.step("MCOLORING tried colour 1 for E: D has it. Colour 2: B has it. Colour 3: C has it. The loop ends with no colour assigned, so this call returns.", [hl("g.D"), hl("g.B", 0.35), hl("g.C", 0.7)])
s.step("Backtrack to D, and try its next colour: 2. Its neighbours E and F are blank, so 2 is allowed.", [st("ct[4][2]", ""), *colstep("D", 2, 0.3)])
s.step("Now E's neighbours have 2, 3 and 2: colour 1 is free. E takes 1.", colstep("E", 1))
s.step("F is adjacent to C, 3, and D, 2: it takes 1. Every vertex is coloured, and no edge joins two equal colours.", colstep("F", 1) + [mk("ct", 0.5), s.take("A1 B2 C3 D2 E1 F1")])
s.step("The early choice for D only failed two levels later. Backtracking repaired it without restarting: it went back exactly one decision.", [hl("ct[3]")])

s.scene("chi")
s.step("Stage 5: our graph contains a triangle, so it needs at least 3 colours, and we found a 3-colouring: its chromatic number is 3.", [s.head("Stage 5 of 7: the chromatic number"), s.untake()] + hide("g", "ct") + show("chi") + [hl("chi[0]")])
s.step("Two colours are possible exactly when the graph is bipartite: it has no cycle of odd length.", [hl("chi[1]")])
s.step("That is easy to test: run BFS, colour alternate levels differently, and check every edge. Linear time.", [hl("chi[2]")])
s.step("A square, four vertices in a cycle, is bipartite: colour opposite corners alike, two colours. Add one diagonal, and you create a triangle: now it needs three.", [hl("chi[1]")])
s.step("From three colours up, deciding colourability is NP-complete, a class we meet in Module 5: no fast algorithm is known.", [hl("chi[3]")])
s.step("To find the chromatic number, try m equal to 1, 2, 3 and so on, until MCOLORING succeeds.", [hl("chi[4]"), s.take("χ = 2 ⇔ bipartite; χ ≥ 3 is hard")])

s.scene("all")
s.step("Stage 6: to list every colouring, do not stop at the first: print it and keep searching.", [s.head("Stage 6 of 7: all colourings, and cost"), s.untake()] + hide("chi") + show("ac") + [hl("ac[0]")])
s.step("Our graph has 18 three-colourings. The triangle can be coloured in 6 ways. E must then match A, and D and F together have 3 options: 6 times 3.", [hl("ac[1]")])
s.step("In the worst case, the tree has m to the n leaves, and checking each node costs up to n: O of n times m to the n.", [hl("ac[2]")])
s.step("A practical trick: colour the vertices of highest degree first. Conflicts show up near the root, where pruning saves the most.", [hl("ac[3]"), s.take("O(n · mⁿ) worst case")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("ac") + show("q") + [hl("q[0]")])
s.step("Decide 2-colourability, find the first 3-colouring, and count all 3-colourings. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: vertices 1, 2 and 3 form a triangle, an odd cycle. So two colours are impossible.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 1 takes colour 1. 2 is adjacent to 1: colour 2. 3 is adjacent to 1 and 2: colour 3.", [hl("qa[1]")])
s.step("4 is adjacent to 1 and 3, coloured 1 and 3: so 4 takes 2. The first colouring is 1, 2, 3, 2.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("c: the triangle can be coloured in 3 factorial, 6 ways. Then vertex 4 must avoid the colours of 1 and 3, leaving exactly one. 6 colourings.", [hl("qa[3]")])
s.step("The usual slip: checking only the previous vertex instead of every coloured neighbour. The test covers all edges to earlier vertices.", [s.take("check every coloured neighbour")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Graph colouring assigns colours so that neighbours differ. Backtracking colours vertex by vertex and undoes a choice when a later vertex has no colour left.", [hl("stages[0..=3]")])
s.step("Two colours is a quick BFS test; three or more is NP-complete; listing all colourings costs up to n m to the n.", [hl("stages[4..=5]")])
s.step("Next video: branch and bound, which explores the tree breadth first, with FIFO and LIFO strategies, on subset sum.", [mk("stages[0..=6]"), s.take("Next: branch and bound")])

s.save("/home/claude/playlist/dsa4/d4v5.json")

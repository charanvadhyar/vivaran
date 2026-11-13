"""DSA Module 2, video 13: depth-first search."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from dfs import dfs

V = ["u", "v", "w", "x", "y", "z"]; ADJ = {"u": ["v", "x"], "v": ["y"], "w": ["y", "z"], "x": ["v"], "y": ["x"]}
D, F, P, K, O = dfs(V, ADJ)
assert D == {"u": 1, "v": 2, "y": 3, "x": 4, "w": 9, "z": 10} and F == {"x": 5, "y": 6, "v": 7, "u": 8, "z": 11, "w": 12}
assert K == {("u", "v"): "tree", ("v", "y"): "tree", ("y", "x"): "tree", ("x", "v"): "back", ("u", "x"): "forward", ("w", "y"): "cross", ("w", "z"): "tree"}
TA = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": ["E"]}; _, TF, _, _, _ = dfs(list("ABCDE"), TA)
assert TF == {"E": 5, "D": 6, "B": 7, "C": 9, "A": 10} and sorted(TF, key=lambda x: -TF[x]) == list("ACBDE")
V2 = [1, 2, 3, 4, 5]; A2 = {1: [2, 3], 2: [4], 3: [4], 4: [5], 5: [2]}; D2, F2, _, K2, O2 = dfs(V2, A2)
assert D2 == {1: 1, 2: 2, 4: 3, 5: 4, 3: 8} and F2 == {5: 5, 4: 6, 2: 7, 3: 9, 1: 10}
assert K2 == {(1, 2): "tree", (2, 4): "tree", (4, 5): "tree", (5, 2): "back", (1, 3): "tree", (3, 4): "cross"}
L = list("ABCDEFGHIJ"); LE = [("A", "B"), ("A", "C"), ("B", "D"), ("B", "E"), ("C", "E"), ("C", "F"), ("D", "G"), ("E", "H"), ("F", "I"), ("G", "J"), ("H", "J"), ("I", "J")]
LA = {v: [] for v in L}
for a, b in LE: LA[a].append(b); LA[b].append(a)
for v in L: LA[v].sort()
_, _, LP, _, LO = dfs(L, LA); assert LO == list("ABDGJHECFI")

POS = {"u": [0, 0], "v": [1, 0], "w": [2, 0], "x": [0, 1], "y": [1, 1], "z": [2, 1]}
s = Script("Depth-first search")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Go deep, then back up"],
    [2, "The algorithm, with timestamps"],
    [3, "A trace"],
    [4, "Four kinds of edge"],
    [5, "Cycles and back edges"],
    [6, "Topological sort"],
    [7, "DFS against BFS"],
    [8, "Exam question"]]})
L_POS = {"A": (2, 0), "B": (1, 1), "C": (3, 1), "D": (0, 2), "E": (2, 2), "F": (4, 2), "G": (0, 3), "H": (2, 3), "I": (4, 3), "J": (2, 4)}
s.obj({"id": "lab", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "at": list(L_POS[v]), "shape": "circle"} for v in L], "edges": [{"from": a, "to": b} for a, b in LE]})
s.obj({"id": "lo", "type": "table", "region": "right", "columns": ["DFS from A", "alphabetical"], "rows": [
    ["visit order", "A B D G J H E C F I"],
    ["backs up when", "all neighbours visited"],
    ["tree edges", "one long path here"]]})
s.obj({"id": "code", "type": "code", "region": "right", "language": "text", "lines": [
    "DFS(G)",
    "  for each u: u.color = WHITE;  time = 0",
    "  for each u: if u.color == WHITE: VISIT(u)",
    "VISIT(u)",
    "  time = time + 1;  u.d = time;  u.color = GRAY",
    "  for each v in Adj[u]",
    "      if v.color == WHITE: v.π = u;  VISIT(v)",
    "  u.color = BLACK;  time = time + 1;  u.f = time"]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": True,
       "nodes": [{"id": v, "label": v, "at": POS[v], "shape": "circle"} for v in V],
       "edges": [{"from": a, "to": b} for a in ADJ for b in ADJ[a]]})
s.obj({"id": "ek", "type": "table", "region": "right", "columns": ["kind", "v was", "here"], "rows": [
    ["tree", "white", "u→v, v→y, y→x, w→z"],
    ["back", "gray: an open ancestor", "x→v"],
    ["forward", "black descendant", "u→x"],
    ["cross", "black, elsewhere", "w→y"]]})
s.obj({"id": "cy", "type": "table", "region": "right", "columns": ["facts", ""], "rows": [
    ["parenthesis theorem", "[d, f] intervals nest or are disjoint"],
    ["directed cycle", "⇔ DFS finds a back edge"],
    ["here", "x → v closes v → y → x → v"],
    ["undirected", "a back edge (not to the parent) = a cycle"]]})
s.obj({"id": "ts", "type": "diagram", "region": "left", "layout": "layers", "directed": True,
       "nodes": [{"id": v, "label": f"{v} {TF[v]}", "shape": "circle"} for v in "ABCDE"],
       "edges": [{"from": a, "to": b} for a in TA for b in TA[a]]})
s.obj({"id": "tt", "type": "table", "region": "right", "columns": ["TOPOLOGICAL-SORT(G), G a DAG", ""], "rows": [
    ["run DFS", "record each finish time"],
    ["as each vertex finishes", "put it at the front of a list"],
    ["finish times here", "E 5, D 6, B 7, C 9, A 10"],
    ["decreasing finish", "A C B D E"],
    ["why", "every edge u → v has u.f > v.f in a DAG"]]})
s.obj({"id": "vs", "type": "table", "region": "center", "columns": ["", "BFS", "DFS"], "rows": [
    ["frontier kept in", "a queue", "a stack (or the recursion)"],
    ["order", "level by level", "one branch to its end, then back"],
    ["gives", "shortest hop counts", "d/f times, edge kinds, parenthesis structure"],
    ["used for", "shortest paths, k-hop reach, diameter", "cycles, topological order, components, mazes"],
    ["cost (lists)", "O(n + m)", "O(n + m)"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: directed graph, edges 1→2, 1→3, 2→4, 3→4, 4→5, 5→2"], "rows": [
    ["a) DFS from 1, smaller numbers first: d and f of every vertex"],
    ["b) classify every edge   c) does the graph have a cycle? can it be sorted topologically?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "answer"], "rows": [
    ["a) d / f", "1: 1/10 · 2: 2/7 · 4: 3/6 · 5: 4/5 · 3: 8/9"],
    ["b) tree", "1→2, 2→4, 4→5, 1→3"],
    ["b) back", "5→2: 2 is still gray"],
    ["b) cross", "3→4: 4 already finished, not 3's descendant"],
    ["c)", "a back edge: cycle 2 → 4 → 5 → 2; not a DAG, no topological order"]]})

lab = lambda v: f"{v} {D[v]}/{F[v]}" if v in F else v
s.scene("intro")
s.step("Breadth-first search spreads out in rings. Depth-first search does the opposite: it follows one path as far as it can, then backs up and tries the next branch, like exploring a maze with one hand on the wall.", [s.head("Depth-first search")])
s.step("The order in which it finishes vertices reveals cycles and dependency orders. This video traces it and puts it to work.")
s.step("Here are the eight stages.", show("stages"))
s.step("The idea, the algorithm with discovery and finish times, a trace, and the four kinds of edge.", [hl("stages[0..=3]")])
s.step("Then cycles, topological sorting, DFS against BFS, and an exam question.", [hl("stages[4..=7]")])

s.scene("idea")
s.step("Stage 1: on the lab's network, start at A and always take the alphabetically first unvisited neighbour. A, then B, then D, then G, then J.", [s.head("Stage 1 of 8: go deep")] + hide("stages") + show("lab", "lo") + [mk("lab.A"), mk("lab.B", 0.2), mk("lab.D", 0.4), mk("lab.G", 0.6), mk("lab.J", 0.8)])
s.step("From J, G is done, so go to H, then E. From E, B is done, so C; then F; then I.", [mk("lab.H"), mk("lab.E", 0.2), mk("lab.C", 0.4), mk("lab.F", 0.6), mk("lab.I", 0.8), hl("lo[0]", 0.5)])
s.step("At I every neighbour is visited, so DFS backs up, all the way to A, finding nothing new. A completely different order from BFS's A to J by distance.", [hl("lo[1..=2]"), s.take("follow one path to its end, then back up")])

s.scene("algo")
s.step("Stage 2: Cormen's DFS colours vertices white, undiscovered; gray, discovered but not finished; and black, finished. It also stamps two times on each vertex.", [s.head("Stage 2 of 8: the algorithm"), s.untake()] + hide("lab", "lo") + show("code") + [ml("code", 1, 3)])
s.step("On entering a vertex, the clock ticks and the discovery time d is recorded; the vertex turns gray.", [ml("code", 5, 5)])
s.step("Every white neighbour is visited recursively, with u as its parent.", [ml("code", 6, 7)])
s.step("When all neighbours are done, the clock ticks again and the finish time f is recorded; the vertex turns black. The outer loop restarts from any vertex still white, so every vertex is reached.", [ml("code", 8, 8), s.take("d on entry, f on exit")])

s.scene("trace")
s.step("Stage 3: Cormen's directed example: six vertices, u, v, w, x, y, z. Start at u.", [s.head("Stage 3 of 8: a trace"), s.untake()] + show("g") + [hl("g.u")])
s.step("u is discovered at time 1. Its first neighbour v: time 2. v's neighbour y: time 3. y's neighbour x: time 4.", [st("g.u", "u 1/"), st("g.v", "v 2/", 0.25), st("g.y", "y 3/", 0.5), st("g.x", "x 4/", 0.75)])
s.step("x's only neighbour, v, is gray: still open. Nothing to visit, so x finishes at 5. Then y finishes at 6, v at 7.", [st("g.x", "x 4/5"), st("g.y", "y 3/6", 0.3), st("g.v", "v 2/7", 0.6)])
s.step("Back at u, its other neighbour x is already black. u finishes at 8.", [st("g.u", "u 1/8"), mk("g.u", 0.3)])
s.step("w is still white, so DFS starts again there: discovered at 9. y is black; z is new, 10, and finishes at 11. w finishes at 12.", [st("g.w", "w 9/"), st("g.z", "z 10/11", 0.4), st("g.w", "w 9/12", 0.8), s.take("u 1/8 · v 2/7 · y 3/6 · x 4/5 · w 9/12 · z 10/11")])

s.scene("edges")
s.step("Stage 4: each edge u to v is classified by v's colour when it is examined. Tree edges reach a white vertex: they form the DFS forest.", [s.head("Stage 4 of 8: four kinds of edge"), s.untake()] + hide("code") + show("ek") + [hl("ek[0]"), hl("g.u->v", 0.3), hl("g.v->y", 0.4), hl("g.y->x", 0.5), hl("g.w->z", 0.6)])
s.step("A back edge reaches a gray vertex, an ancestor that is still open: x to v.", [hl("ek[1]"), hl("g.x->v", 0.3)])
s.step("A forward edge reaches a black descendant: u to x, since x was finished inside u's interval.", [hl("ek[2]"), hl("g.u->x", 0.3)])
s.step("A cross edge reaches a black vertex that is not a descendant: w to y, into the first tree.", [hl("ek[3]"), hl("g.w->y", 0.3), s.take("white: tree · gray: back · black: forward or cross")])

s.scene("cycle")
s.step("Stage 5: the times obey the parenthesis theorem: two intervals from d to f are either nested or disjoint. v's interval, 2 to 7, lies inside u's, 1 to 8, exactly because v is u's descendant.", [s.head("Stage 5 of 8: cycles"), s.untake()] + hide("ek") + show("cy") + [hl("cy[0]")])
s.step("A directed graph has a cycle exactly when DFS finds a back edge.", [hl("cy[1]")])
s.step("Here, x to v is a back edge, and it closes the cycle v, y, x, v.", [hl("cy[2]"), hl("g.x->v", 0.3)])
s.step("In an undirected graph there are only tree and back edges; any back edge other than the one to your own parent means a cycle.", [hl("cy[3]"), s.take("back edge ⇔ cycle")])

s.scene("topo")
s.step("Stage 6: a directed acyclic graph, a DAG, can describe dependencies: A must happen before B and C, both before D, and D before E. A topological sort lists the vertices so every edge points forward.", [s.head("Stage 6 of 8: topological sort"), s.untake()] + hide("g", "cy") + show("ts", "tt") + [hl("tt[0]")])
s.step("Run DFS and, as each vertex finishes, put it at the front of a list.", [hl("tt[1]")])
s.step("From A: B, then D, then E. E finishes at 5, D at 6, B at 7. Then C, at 9, and A at 10.", [hl("tt[2]")])
s.step("Decreasing finish time: A, C, B, D, E. In a DAG every edge goes from a later finish to an earlier one, so this order respects every dependency. Theta of n plus m.", [hl("tt[3..=4]"), s.take("topological order = decreasing finish time")])

s.scene("vs")
s.step("Stage 7: DFS against BFS. BFS keeps its frontier in a queue; DFS in a stack, here the recursion.", [s.head("Stage 7 of 8: DFS against BFS"), s.untake()] + hide("ts", "tt") + show("vs") + [hl("vs[0..=1]")])
s.step("BFS gives shortest hop counts; DFS gives discovery and finish times, edge kinds and nesting.", [hl("vs[2]")])
s.step("So BFS answers distance questions, and DFS answers structure questions: cycles, orderings, connected and strongly connected components, maze solving. Both cost O of n plus m with adjacency lists.", [hl("vs[3..=4]"), s.take("BFS: distances · DFS: structure")])

s.scene("exam")
s.step("Now an exam question on a directed graph of five vertices.", [s.head("Exam question"), s.untake()] + hide("vs") + show("q") + [hl("q[0]")])
s.step("Find every discovery and finish time, classify every edge, and decide whether a topological order exists. Pause and work it out.", [hl("q[1]")])
s.step("From 1 at time 1: 2 at time 2, 4 at 3, 5 at 4. 5's edge to 2 meets a gray vertex. 5 finishes at 5, 4 at 6, 2 at 7. Then 3 at 8; its edge to 4 meets a black vertex; 3 finishes at 9, and 1 at 10.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Tree edges: 1 to 2, 2 to 4, 4 to 5, and 1 to 3.", [hl("qa[1]")])
s.step("5 to 2 is a back edge, because 2 was gray. 3 to 4 is a cross edge: 4 was already finished and is not 3's descendant.", [hl("qa[2..=3]")])
s.step("c: the back edge means a cycle, 2, 4, 5, 2. So it is not a DAG, and no topological order exists.", [hl("qa[4]"), mk("qa[4][1]", 0.5)])
s.step("The usual slip: calling 3 to 4 a forward edge. Forward edges go to a descendant; check the intervals: 4's interval, 3 to 6, is not inside 3's, 8 to 9.", [s.take("forward needs nested intervals")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("DFS goes deep and backs up, stamping discovery and finish times; colours classify edges as tree, back, forward or cross.", [hl("stages[0..=3]")])
s.step("A back edge means a cycle; decreasing finish times give a topological order; and DFS answers structure questions in O of n plus m, as BFS answers distance questions.", [hl("stages[4..=6]")])
s.step("Next video: shortest paths when edges have weights, even negative ones. The Bellman-Ford algorithm.", [mk("stages[0..=7]"), s.take("Next: Bellman-Ford")])

s.save("/home/claude/playlist/dsa2/d2v13.json")

"""DSA Module 2, video 11: graphs and how to store them."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *

V = list("ABCDEFGHIJ")
E = [("A", "B"), ("A", "C"), ("B", "D"), ("B", "E"), ("C", "E"), ("C", "F"), ("D", "G"), ("E", "H"), ("F", "I"), ("G", "J"), ("H", "J"), ("I", "J")]
adj = {v: [] for v in V}
for a, b in E: adj[a].append(b); adj[b].append(a)
for v in V: adj[v].sort()
deg = {v: len(adj[v]) for v in V}
assert sum(deg.values()) == 2 * len(E) == 24 and deg["E"] == 3 and deg["J"] == 3 and deg["A"] == 2
M = [[1 if b in adj[a] else 0 for b in V] for a in V]
assert all(M[i][j] == M[j][i] for i in range(10) for j in range(10)) and sum(map(sum, M)) == 24
DE = [(1, 2), (1, 3), (2, 3), (3, 1), (3, 4), (4, 2)]
outd = {v: sum(1 for a, b in DE if a == v) for v in range(1, 5)}; ind = {v: sum(1 for a, b in DE if b == v) for v in range(1, 5)}
assert outd == {1: 2, 2: 1, 3: 2, 4: 1} and ind == {1: 1, 2: 2, 3: 2, 4: 1}
assert 1000 * 1000 == 10**6 and 1000 + 2 * 5000 == 11000

POS = {"A": (2, 0), "B": (1, 1), "C": (3, 1), "D": (0, 2), "E": (2, 2), "F": (4, 2), "G": (0, 3), "H": (2, 3), "I": (4, 3), "J": (2, 4)}
s = Script("Graph representation")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Graphs and their words"],
    [2, "The lab's network"],
    [3, "The adjacency matrix"],
    [4, "Adjacency lists"],
    [5, "Which to choose"],
    [6, "Directed and weighted graphs"],
    [7, "Exam question"]]})
s.obj({"id": "wd", "type": "table", "region": "center", "columns": ["G = (V, E)", ""], "rows": [
    ["vertices V, edges E", "n = |V|, m = |E|"],
    ["undirected · directed", "a road both ways · a one-way street"],
    ["weighted", "each edge carries a number: a distance, a cost"],
    ["degree", "edges at a vertex; directed: in-degree and out-degree"],
    ["path · cycle", "a sequence of edges · a path back to its start"],
    ["connected", "every vertex reachable from every other"]]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "at": list(POS[v]), "shape": "circle"} for v in V], "edges": [{"from": a, "to": b} for a, b in E]})
s.obj({"id": "gd", "type": "table", "region": "right", "columns": ["the lab's network", ""], "rows": [
    ["devices", "10: A to J"],
    ["links", "12, undirected, unweighted"],
    ["degrees", "A 2 · B 3 · C 3 · E 3 · J 3 · …"],
    ["sum of degrees", "24 = 2 × 12: every edge has two ends"]]})
s.obj({"id": "mx", "type": "table", "region": "right", "columns": [""] + V, "rows": [[a] + [str(x) for x in M[i]] for i, a in enumerate(V)]})
s.obj({"id": "al", "type": "table", "region": "right", "columns": ["vertex", "neighbours"], "rows": [[v, " → ".join(adj[v])] for v in V]})
s.obj({"id": "ch", "type": "table", "region": "center", "columns": ["", "adjacency matrix", "adjacency lists"], "rows": [
    ["space", "Θ(n²)", "Θ(n + m)"],
    ["is (u, v) an edge?", "Θ(1)", "Θ(degree of u)"],
    ["list u's neighbours", "Θ(n)", "Θ(degree of u)"],
    ["visit every edge (BFS, DFS)", "Θ(n²)", "Θ(n + m)"],
    ["best for", "dense graphs, m close to n²", "sparse graphs: most real ones"]]})
s.obj({"id": "dg", "type": "diagram", "region": "left", "layout": "grid", "directed": True,
       "nodes": [{"id": f"v{k}", "label": str(k), "at": at, "shape": "circle"} for k, at in [(1, [0, 0]), (2, [2, 0]), (3, [0, 2]), (4, [2, 2])]],
       "edges": [{"from": f"v{a}", "to": f"v{b}", **({"label": w} if w else {})} for (a, b), w in zip(DE, ["", "", "", "", "", ""])]})
s.obj({"id": "dw", "type": "table", "region": "right", "columns": ["directed and weighted", ""], "rows": [
    ["directed matrix", "M[u][v] = 1 for an edge u → v: not symmetric"],
    ["directed lists", "each edge appears once, in its tail's list"],
    ["weighted matrix", "M[u][v] = the weight; ∞ (or 0) for no edge"],
    ["weighted lists", "store (v, weight) pairs"],
    ["incidence matrix", "n × m: rows vertices, columns edges"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: directed graph on 1, 2, 3, 4"], "rows": [
    ["edges: 1→2, 1→3, 2→3, 3→1, 3→4, 4→2"],
    ["a) the adjacency matrix   b) the adjacency lists   c) every in-degree and out-degree"],
    ["d) a graph has 1000 vertices and 5000 undirected edges: cells in a matrix, entries in lists?"]]})
s.obj({"id": "qm", "type": "table", "region": "left", "columns": ["", "1", "2", "3", "4"], "rows": [
    ["1", "0", "1", "1", "0"], ["2", "0", "0", "1", "0"], ["3", "1", "0", "0", "1"], ["4", "0", "1", "0", "0"]]})
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["part", "answer"], "rows": [
    ["b) lists", "1: 2, 3 · 2: 3 · 3: 1, 4 · 4: 2"],
    ["c) out-degree", "1: 2 · 2: 1 · 3: 2 · 4: 1"],
    ["c) in-degree", "1: 1 · 2: 2 · 3: 2 · 4: 1"],
    ["d) matrix", "1000 × 1000 = 1,000,000 cells"],
    ["d) lists", "1000 heads + 2 × 5000 = 11,000 entries"]]})

s.scene("intro")
s.step("Trees have one path between any two nodes. Graphs allow any connections at all: road networks, social networks, the internet, the dependencies between tasks. Before any graph algorithm can run, the graph has to be stored. This video compares the two standard ways.", [s.head("Graphs and how to store them")])
s.step("Here are the seven stages.", show("stages"))
s.step("The vocabulary, the lab's network, the adjacency matrix and adjacency lists.", [hl("stages[0..=3]")])
s.step("Then how to choose between them, directed and weighted graphs, and an exam question.", [hl("stages[4..=6]")])

s.scene("words")
s.step("Stage 1: a graph G is a set of vertices V and a set of edges E. We write n for the number of vertices and m for the number of edges.", [s.head("Stage 1 of 7: the words")] + hide("stages") + show("wd") + [hl("wd[0]")])
s.step("Undirected edges work both ways, like a two-way road. Directed edges have a direction, like a one-way street.", [hl("wd[1]")])
s.step("In a weighted graph each edge carries a number: a distance, a time, a cost.", [hl("wd[2]")])
s.step("The degree of a vertex counts its edges. In a directed graph, in-degree counts edges coming in, out-degree edges going out.", [hl("wd[3]")])
s.step("A path is a sequence of edges; a cycle is a path that returns to its start; and a graph is connected if every vertex can reach every other.", [hl("wd[4..=5]"), s.take("G = (V, E): n vertices, m edges")])

s.scene("lab")
s.step("Stage 2: the lab's communication network. Ten devices, A to J, and twelve direct links.", [s.head("Stage 2 of 7: the lab's network"), s.untake()] + hide("wd") + show("g", "gd") + [hl("gd[0..=1]")])
s.step("Count the degrees. A links to B and C: degree 2. E links to B, C and H: degree 3.", [hl("g.A"), hl("g.E", 0.4), hl("gd[2]", 0.5)])
s.step("Add all ten degrees and you get 24, exactly twice the 12 edges, because every edge is counted once at each of its two ends. This is the handshake lemma: the degrees always add up to 2m.", [hl("gd[3]"), s.take("sum of degrees = 2m")])

s.scene("mat")
s.step("Stage 3: the adjacency matrix is an n by n table with a 1 in row u, column v when u and v are joined.", [s.head("Stage 3 of 7: the adjacency matrix"), s.untake()] + hide("gd") + show("mx") + [hl("mx[0]")])
s.step("Row A has 1s in columns B and C. Row J has 1s in G, H and I.", [hl("mx[0]"), hl("mx[9]", 0.5)])
s.step("For an undirected graph it is symmetric: A to B and B to A are the same edge. The 1s add up to 2m, 24.", [hl("mx[1]")])
s.step("Asking whether two vertices are joined is one lookup, Theta of 1. But the table always needs n squared cells, 100 here, however few edges there are, and listing a vertex's neighbours means scanning a whole row.", [s.take("matrix: Θ(n²) space, Θ(1) edge test")])

s.scene("list")
s.step("Stage 4: adjacency lists keep, for each vertex, a list of its neighbours.", [s.head("Stage 4 of 7: adjacency lists"), s.untake()] + hide("mx") + show("al") + [hl("al[0]")])
s.step("A's list holds B and C. E's holds B, C and H.", [hl("al[0]"), hl("al[4]", 0.5)])
s.step("Each undirected edge appears twice, once in each endpoint's list: 24 entries, plus 10 list heads.", [hl("al")])
s.step("Space is Theta of n plus m. Listing a vertex's neighbours costs exactly its degree. Checking a single edge means scanning one list.", [s.take("lists: Θ(n + m) space, neighbours in Θ(degree)")])

s.scene("choose")
s.step("Stage 5: which to choose? Space: n squared against n plus m.", [s.head("Stage 5 of 7: which to choose"), s.untake()] + hide("g", "al") + show("ch") + [hl("ch[0]")])
s.step("Edge tests favour the matrix; listing neighbours favours the lists.", [hl("ch[1..=2]")])
s.step("Breadth-first and depth-first search look at every vertex's neighbours once. With lists that is Theta of n plus m; with a matrix, Theta of n squared.", [hl("ch[3]")])
s.step("Most real graphs are sparse: a road junction meets a handful of roads, not millions. So adjacency lists are the default, and the matrix suits small or dense graphs.", [hl("ch[4]"), s.take("sparse: lists · dense: matrix")])

s.scene("dir")
s.step("Stage 6: a directed graph. Edge 1 to 2 is not edge 2 to 1: they would be two different edges.", [s.head("Stage 6 of 7: directed and weighted"), s.untake()] + hide("ch") + show("dg", "dw"))
s.step("In its matrix, row u marks the edges leaving u, so the matrix is no longer symmetric. In its lists, each edge appears once, in the list of its tail.", [hl("dw[0..=1]")])
s.step("For weights, the matrix stores the weight itself, with infinity, or sometimes 0, meaning no edge. The lists store pairs: neighbour and weight.", [hl("dw[2..=3]")])
s.step("A third form, the incidence matrix, has a row per vertex and a column per edge. It is used less in algorithms, more in network theory.", [hl("dw[4]"), s.take("directed: not symmetric · weighted: store the weight")])

s.scene("exam")
s.step("Now an exam question on a small directed graph.", [s.head("Exam question"), s.untake()] + hide("dg", "dw") + show("q") + [hl("q[0]")])
s.step("Write its matrix and lists, find every in-degree and out-degree, and compare space for a large sparse graph. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: row 1 has 1s in columns 2 and 3; row 2 in column 3; row 3 in columns 1 and 4; row 4 in column 2.", hide("q") + show("qm"))
s.step("b: the lists: 1 to 2 and 3; 2 to 3; 3 to 1 and 4; 4 to 2.", show("qa") + [hl("qa[0]")])
s.step("c: out-degrees are the row sums: 2, 1, 2, 1. In-degrees are the column sums: 1, 2, 2, 1. Both total 6, the number of edges.", [hl("qa[1..=2]")])
s.step("d: a matrix needs a million cells. Lists need 1000 heads and 10,000 entries, each edge twice: about 11,000. Ninety times smaller.", [hl("qa[3..=4]"), mk("qa[4][1]", 0.5)])
s.step("The usual slip: counting each undirected edge once in the lists. It appears in both endpoints' lists.", [s.take("undirected edge: in two lists")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qm", "qa") + show("stages"))
s.step("A graph is vertices and edges, directed or not, weighted or not; the degrees always sum to twice the edges. The matrix gives Theta of 1 edge tests in n squared space.", [hl("stages[0..=2]")])
s.step("Lists use n plus m space and give each vertex's neighbours directly, which is what traversals need; directed and weighted graphs need only small changes.", [hl("stages[3..=5]")])
s.step("Next video: exploring a graph level by level. Breadth-first search, on this same network.", [mk("stages[0..=6]"), s.take("Next: breadth-first search")])

s.save("/home/claude/playlist/dsa2/d2v11.json")

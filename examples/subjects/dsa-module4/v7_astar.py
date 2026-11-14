"""DSA Module 4, video 7: least-cost search and A* (lab 8: grid routing)."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa4")
from common import Script
from h import *
from astar import astar, dijkstra_count

X = None
G = [[1, 1, 3, 1, 1], [1, X, X, 5, 1], [2, X, 1, 1, 2], [1, 1, 1, X, 1]]
PATH, COST, LOG = astar(G, (0, 0), (3, 4))
assert PATH == [(0, 0), (1, 0), (2, 0), (3, 1), (2, 2), (2, 3), (3, 4)] and COST == 7 and len(LOG) == 10
assert [(u, g, h) for u, g, h, f in LOG] == [((0, 0), 0, 4), ((0, 1), 1, 3), ((1, 0), 1, 4), ((0, 2), 4, 3), ((2, 0), 3, 4), ((3, 1), 4, 3), ((2, 2), 5, 2), ((3, 2), 5, 2), ((2, 3), 6, 1), ((3, 4), 7, 0)]
P2, C2, L2 = dijkstra_count(G, (0, 0), (3, 4)); assert C2 == 7 and len(L2) == 14
assert 1 + 3 + 1 + 1 + 1 + 1 == 8
GE = [[1, 4, 1, 1], [1, X, X, 1], [3, 1, 2, 1]]
EP, EC, EL = astar(GE, (0, 0), (2, 3)); assert EP == [(0, 0), (1, 0), (2, 1), (2, 2), (2, 3)] and EC == 5 and len(EL) == 5
assert 4 + 1 + 1 + 1 == 7

cell = lambda r, c: "X" if G[r][c] is None else str(G[r][c])
s = Script("A* search")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The lab problem: routing on a city grid"],
    [2, "Least-cost search: f = g + h"],
    [3, "A good heuristic for the grid"],
    [4, "A* on a 4 × 5 grid, traced"],
    [5, "Why A* finds the cheapest path"],
    [6, "A* against Dijkstra; the algorithm"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["the delivery grid (lab 8)", ""], "rows": [
    ["city map", "an M × N grid; each cell has a traffic cost"],
    ["restricted zones", "cells that cannot be entered (cost ∞): marked X"],
    ["moves", "horizontal, vertical and diagonal: 8 neighbours"],
    ["cost of a path", "the sum of the costs of the cells entered"],
    ["goal", "the cheapest path from the depot to the delivery cell"]]})
s.obj({"id": "fg", "type": "table", "region": "center", "columns": ["least-cost (LC) search", ""], "rows": [
    ["g(n)", "the cost of the best path found from the start to n"],
    ["h(n)", "an estimate of the cost still needed from n to the goal"],
    ["f(n) = g(n) + h(n)", "estimated cost of the cheapest path through n"],
    ["always expand", "the live node with the smallest f: a priority queue"],
    ["h = 0", "Dijkstra's algorithm: no sense of direction"]]})
s.obj({"id": "hh", "type": "table", "region": "center", "columns": ["choosing h for the grid", ""], "rows": [
    ["admissible", "h never overestimates the true remaining cost"],
    ["with diagonal moves", "reaching the goal needs at least max(|Δrow|, |Δcol|) moves"],
    ["every cell costs at least 1", "h(n) = max(|Δrow|, |Δcol|) × 1: admissible"],
    ["Manhattan distance |Δr| + |Δc|", "would overestimate when diagonals are allowed: not admissible here"]]})
s.obj({"id": "gd", "type": "table", "region": "left", "columns": ["", "c0", "c1", "c2", "c3", "c4"],
       "rows": [[f"r{r}"] + [cell(r, c) for c in range(5)] for r in range(4)]})
s.obj({"id": "ex", "type": "table", "region": "right", "columns": ["expanded", "g", "h", "f"], "rows": [["", "", "", ""] for _ in LOG]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["why A* is optimal", ""], "rows": [
    ["claim", "with an admissible h, the first time the goal is expanded, its g is the least cost"],
    ["suppose a cheaper path exists", "some node n on it is still waiting in the queue"],
    ["then", "f(n) = g(n) + h(n) ≤ the cheaper cost < g(goal) = f(goal)"],
    ["so", "n would have been expanded before the goal: contradiction"],
    ["consistent h", "h(u) ≤ cost(u, v) + h(v): each cell is expanded at most once (ours is)"]]})
s.obj({"id": "ac", "type": "code", "region": "center", "language": "text", "lines": [
    "A-STAR(grid, s, t)",
    "    g[s] = 0;   insert s into Q with key f = h(s)",
    "    while Q is not empty",
    "        u = EXTRACT-MIN(Q)                  // least f",
    "        if u == t:  return g[t] and the path by parent links",
    "        mark u closed",
    "        for each of the 8 neighbours v of u, not X and not closed",
    "            if g[u] + cost(v) < g[v]",
    "                g[v] = g[u] + cost(v);  parent[v] = u",
    "                insert or decrease v in Q with key g[v] + h(v)",
    "    return \"no path\"",
    "",
    "binary heap: O(E log V); a better h only reduces the nodes expanded"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["grid rows: (1 4 1 1) · (1 X X 1) · (3 1 2 1); start top-left, goal bottom-right; 8 moves"],
    ["a) the order A* expands cells, with g, h and f"],
    ["b) the cheapest path and its cost"],
    ["c) the cost of the route along the top row, and why A* never expands it"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["expanded", "g", "h", "f"], "rows": [
    ["(0,0) start", "0", "3", "3"],
    ["(1,0)", "1", "3", "4"],
    ["(2,1) diagonal", "2", "2", "4"],
    ["(2,2)", "4", "1", "5"],
    ["(2,3) goal", "5", "0", "5:  path (0,0) (1,0) (2,1) (2,2) (2,3), cost 5"],
    ["c) top route", "4 + 1 + 1 + 1 = 7", "", "(0,1) has f = 4 + 2 = 6 > 5: never chosen"]]})

s.scene("intro")
s.step("A delivery vehicle crosses a city grid. Some streets are jammed, some are closed. Searching every possible route is wasteful, because most of them head the wrong way.", [s.head("A* search")])
s.step("A star searches with a sense of direction, and still guarantees the cheapest route. It is the algorithm behind the lab's routing task.")
s.step("Here are the seven stages.", show("stages"))
s.step("The lab problem, least-cost search with f equals g plus h, a heuristic for the grid, and a full trace.", [hl("stages[0..=3]")])
s.step("Then why A star is optimal, A star against Dijkstra, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: the city is a grid of cells, and each cell has a traffic cost: the delay for driving through it.", [s.head("Stage 1 of 7: the problem")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("Restricted zones and accident sites cannot be entered at all. We mark them X.", [hl("pb[1]")])
s.step("The vehicle moves to any of its 8 neighbours: across, up and down, or diagonally.", [hl("pb[2]")])
s.step("A path costs the sum of the cells it enters. We want the cheapest path from the depot to the destination.", [hl("pb[3..=4]"), s.take("cost of a path = sum of cells entered")])

s.scene("fg")
s.step("Stage 2: least-cost search keeps, for every node, g: the cost of the best path found to it so far.", [s.head("Stage 2 of 7: f = g + h"), s.untake()] + hide("pb") + show("fg") + [hl("fg[0]")])
s.step("And h: an estimate of the cost still needed to reach the goal.", [hl("fg[1]")])
s.step("Their sum, f, estimates the cost of the cheapest complete path through that node.", [hl("fg[2]")])
s.step("The live nodes sit in a priority queue, and the one with the smallest f is always expanded next. This is the least-cost branch and bound from the last video.", [hl("fg[3]")])
s.step("If h is 0 everywhere, this is just Dijkstra's algorithm: it spreads out evenly, with no idea where the goal lies.", [hl("fg[4]"), s.take("expand the smallest f = g + h")])

s.scene("hh")
s.step("Stage 3: choosing h. The rule is that h must be admissible: it may underestimate, but never overestimate, the true remaining cost.", [s.head("Stage 3 of 7: the heuristic"), s.untake()] + hide("fg") + show("hh") + [hl("hh[0]")])
s.step("With diagonal moves, getting from one cell to another takes at least the larger of the row difference and the column difference.", [hl("hh[1]")])
s.step("Every cell costs at least 1, so h equals that number of moves times 1. It can never overestimate.", [hl("hh[2]")])
s.step("The Manhattan distance, rows plus columns, would overestimate whenever a diagonal shortcut exists. With 8 moves, it is not admissible.", [hl("hh[3]"), s.take("h = max(|Δr|, |Δc|) × cheapest cell")])

s.scene("trace")
s.step("Stage 4: a 4 by 5 grid. Start at the top-left corner, row 0, column 0; the goal is the bottom-right, row 3, column 4. X marks closed cells.", [s.head("Stage 4 of 7: a trace"), s.untake()] + hide("hh") + show("gd", "ex") + [hl("gd[0][1]"), hl("gd[3][5]", 0.4)])
say = ["Expand the start: g is 0, and the goal is 4 moves away: h 4, f 4. Its neighbours enter the queue.",
       "The smallest f is row 0, column 1: g 1, h 3, f 4. Moving right is moving towards the goal.",
       "Next, row 1, column 0: g 1, but still 4 moves from the goal: f 5.",
       "Row 0, column 2 costs 3 to enter: g 4, h 3, f 7. Now several cells tie at f 7.",
       "Row 2, column 0: g 3 through the left column, f 7.",
       "Row 3, column 1, reached diagonally: g 4, h 3, f 7.",
       "Row 2, column 2: g 5, h 2, f 7.",
       "Row 3, column 2: g 5, h 2, f 7.",
       "Row 2, column 3: g 6, h 1, f 7.",
       "The goal: g 7, h 0, f 7. It is expanded with the smallest f, so its cost, 7, is final."]
for k, (u, g, h_, f) in enumerate(LOG):
    r, c = u
    acts = [st(f"ex[{k}][0]", f"({r},{c})"), st(f"ex[{k}][1]", str(g), 0.1), st(f"ex[{k}][2]", str(h_), 0.15), st(f"ex[{k}][3]", str(f), 0.2), hl(f"ex[{k}]"), hl(f"gd[{r}][{c + 1}]", 0.3)]
    s.step(say[k], acts)
s.step("Following the parent links back gives the path: down the left column, diagonally down to row 3, column 1, diagonally up to row 2, column 2, right, and diagonally into the goal. Cost 1, 2, 1, 1, 1, 1: 7.", [mk(f"gd[{r}][{c + 1}]", round(0.1 * i, 2)) for i, (r, c) in enumerate(PATH)] + [s.take("cheapest path: cost 7")])
s.step("The top route through the 3 and the 5 costs more. A star touched only two of its cells, and never went near the right side of row 1.", [hl("gd[1][4]")])

s.scene("why")
s.step("Stage 5: why is the answer guaranteed cheapest? Claim: with an admissible h, when the goal is first expanded, its g is the least possible cost.", [s.head("Stage 5 of 7: why it is optimal"), s.untake()] + hide("gd", "ex") + show("why") + [hl("why[0]")])
s.step("Suppose a cheaper path existed. Some node n on that path is still waiting in the queue.", [hl("why[1]")])
s.step("Because h never overestimates, f of n is at most the cheaper path's cost, which is less than the goal's f.", [hl("why[2]")])
s.step("So n has a smaller f and would have been expanded before the goal: a contradiction.", [hl("why[3]")])
s.step("If h is also consistent, never dropping by more than the cost of a step, each cell is expanded at most once. Ours is consistent.", [hl("why[4]"), s.take("admissible h ⇒ optimal path")])

s.scene("algo")
s.step("Stage 6: on our grid, A star expanded 10 cells. Dijkstra, with h equal to 0, expands 14 to find the same cost: it searches in every direction equally.", [s.head("Stage 6 of 7: the algorithm"), s.untake()] + hide("why") + show("ac") + [ml("ac", 1, 2)])
s.step("The algorithm: repeatedly extract the cell with least f. If it is the goal, stop and follow the parent links.", [ml("ac", 3, 6)])
s.step("Otherwise relax each open neighbour: if going through u is cheaper, update its g and parent, and its key in the queue.", [ml("ac", 7, 10)])
s.step("If the queue empties first, the goal cannot be reached: the closed zones wall it off.", [ml("ac", 11, 11)])
s.step("With a binary heap the cost is O of E log V, like Dijkstra. A better heuristic does not change that bound, but it cuts the number of cells expanded, which is what matters on a large map.", [ml("ac", 13, 13), s.take("A* = Dijkstra + a sense of direction")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("ac") + show("q") + [hl("q[0]")])
s.step("Trace the expansions, give the path and its cost, and explain why the top route is never taken. Pause and work it out.", [hl("q[1..=3]")])
s.step("Expand the start: g 0, h 3, f 3. Then row 1, column 0: g 1, h 3, f 4.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("Then row 2, column 1, diagonally: g 2, h 2, f 4.", [hl("qa[2]")])
s.step("Row 2, column 2 costs 2: g 4, h 1, f 5. Then the goal: g 5, h 0, f 5. The path costs 1, 1, 2, 1: 5.", [hl("qa[3..=4]"), mk("qa[4][3]", 0.5)])
s.step("c: the top route costs 4 plus 1 plus 1 plus 1, 7. Its first cell, row 0, column 1, already has f equal to 4 plus 2, 6, more than 5, so A star never expands it.", [hl("qa[5]")])
s.step("The usual slip: using Manhattan distance when diagonal moves are allowed. It overestimates, and A star may then miss the cheapest path.", [s.take("diagonals allowed: use max(|Δr|, |Δc|)")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A star expands the node with the smallest f, the cost so far plus an estimate of the cost to go. On a grid with diagonal moves, the estimate is the larger coordinate difference.", [hl("stages[0..=3]")])
s.step("With an admissible estimate, the first time the goal is expanded its cost is optimal, and A star expands fewer cells than Dijkstra.", [hl("stages[4..=5]")])
s.step("Next video: the lab's knight's tour, backtracking on a chessboard, with Warnsdorff's rule.", [mk("stages[0..=6]"), s.take("Next: the knight's tour")])

s.save("/home/claude/playlist/dsa4/d4v7.json")

"""DSA Module 4, video 8: the knight's tour (lab 7)."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa4")
from common import Script
from h import *
from knight import tour, MV

OK, B, CALLS = tour(8, closed=True); assert OK and CALLS == 117
POS = {B[r][c]: (r, c) for r in range(8) for c in range(8)}
assert POS[1] == (0, 0) and POS[64] == (1, 2) and POS[2] == (2, 1) and POS[3] == (0, 2) and POS[4] == (1, 0) and POS[5] == (3, 1)
assert any((POS[64][0] + a, POS[64][1] + b) == POS[1] for a, b in MV)
o5 = tour(5, closed=False); p5 = tour(5, closed=False, warnsdorff=False); assert o5[0] and o5[2] == 25 and p5[0] and p5[2] == 8840
assert tour(8, closed=False)[2] == 64

s = Script("Backtracking: the knight's tour")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The lab problem: a closed knight's tour"],
    [2, "Backtracking on the board"],
    [3, "Warnsdorff's rule: hardest square first"],
    [4, "An 8 × 8 closed tour, built"],
    [5, "Generalising to n × n"],
    [6, "Why it works so well; cost"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["the knight's tour (lab 7)", ""], "rows": [
    ["a knight moves", "two squares one way and one square the other: up to 8 moves"],
    ["tour", "visit every square exactly once"],
    ["closed tour", "the last square is one knight's move from the first"],
    ["output", "the order of the squares, starting from the given one"],
    ["generalise", "an n × n board"]]})
s.obj({"id": "bt", "type": "code", "region": "center", "language": "text", "lines": [
    "TOUR(r, c, k)            // the knight stands on (r, c) after k moves; B[r][c] = k",
    "    if k == n²",
    "        return (the start is one knight's move from (r, c))   // closed?",
    "    for each knight move (r', c') onto an unvisited square",
    "        B[r'][c'] = k + 1",
    "        if TOUR(r', c', k + 1):  return true",
    "        B[r'][c'] = 0      // undo: backtrack",
    "    return false",
    "",
    "plain order of moves: 5 × 5 open tour from a corner needs 8,840 calls"]})
s.obj({"id": "wr", "type": "table", "region": "center", "columns": ["Warnsdorff's rule (1823)", ""], "rows": [
    ["degree of a square", "how many unvisited squares a knight could jump to from it"],
    ["rule", "move to the neighbour of least degree"],
    ["why", "squares with few exits are visited before they are cut off"],
    ["ties", "break them in a fixed order of the 8 moves"],
    ["inside backtracking", "try neighbours in increasing degree; backtrack if stuck"]]})
s.obj({"id": "bd", "type": "table", "region": "left", "columns": ["", "c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7"],
       "rows": [[f"r{r}"] + ["" for _ in range(8)] for r in range(8)]})
s.obj({"id": "dg", "type": "table", "region": "right", "columns": ["from", "least degree", "go to"], "rows": [
    ["(0,0)", "(2,1) 5, (1,2) 5", "(2,1)"],
    ["(2,1)", "(0,2) 3, (4,0) 3", "(0,2)"],
    ["(0,2)", "(1,0) 2", "(1,0)"],
    ["(1,0)", "(3,1) 5", "(3,1)"]]})
s.obj({"id": "gn", "type": "table", "region": "center", "columns": ["n × n boards", ""], "rows": [
    ["any closed tour", "needs n² even: a knight always changes square colour, so a closed tour alternates colours"],
    ["n = 5 (25 squares)", "open tours exist; closed ones are impossible"],
    ["closed tours exist", "for every even n ≥ 6"],
    ["the program", "the same code with n as a parameter; Warnsdorff keeps it fast for n > 8"]]})
s.obj({"id": "cs", "type": "table", "region": "center", "columns": ["search effort", "calls to TOUR"], "rows": [
    ["5 × 5 open tour, plain move order", "8,840"],
    ["5 × 5 open tour, Warnsdorff order", "25: no backtracking at all"],
    ["8 × 8 open tour, Warnsdorff", "64"],
    ["8 × 8 closed tour, Warnsdorff + backtracking", "117"],
    ["worst case", "still exponential: up to 8 choices at each of n² levels"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) prove that a 5 × 5 board has no closed knight's tour"],
    ["b) a knight starts in a corner of a 5 × 5 board: the Warnsdorff degrees of its two possible moves"],
    ["c) how many moves does a closed tour of an n × n board make?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "each move changes colour; a closed tour of 25 squares returns after 25 moves", ""],
    ["a)", "an odd number of colour changes cannot end on the starting colour", "impossible"],
    ["b)", "(2,1) and (1,2): each has 5 unvisited neighbours", "5 and 5: a tie"],
    ["c)", "n² − 1 moves to visit every square, plus 1 back to the start", "n² moves"]]})

s.scene("intro")
s.step("A knight on an empty chessboard must land on every square exactly once, and finish one jump from where it began. People have studied this puzzle for over a thousand years. It is the lab's backtracking task, and one simple rule from 1823 makes it fast.", [s.head("Backtracking: the knight's tour")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem, plain backtracking, Warnsdorff's rule, and an 8 by 8 tour built step by step.", [hl("stages[0..=3]")])
s.step("Then the general n by n board, the cost, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: a knight moves two squares in one direction and one square at right angles: up to 8 moves from a square.", [s.head("Stage 1 of 7: the problem")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("A tour visits every square exactly once.", [hl("pb[1]")])
s.step("The lab asks for a closed tour: the last square must be a knight's move from the first, so the tour could start again.", [hl("pb[2]")])
s.step("The program prints the order of the squares, and should work for any n by n board.", [hl("pb[3..=4]"), s.take("every square once; end next to the start")])

s.scene("bt")
s.step("Stage 2: backtracking. Number the squares in the order visited. Square k holds the knight after k minus 1 moves.", [s.head("Stage 2 of 7: backtracking"), s.untake()] + hide("pb") + show("bt") + [ml("bt", 1, 1)])
s.step("When all n squared squares are numbered, check that the start is one move away.", [ml("bt", 2, 3)])
s.step("Otherwise try each move onto an unvisited square, number it, and recurse.", [ml("bt", 4, 6)])
s.step("If the recursion fails, clear the square and try the next move. That is the backtrack.", [ml("bt", 7, 8)])
s.step("The trouble with a fixed order: the knight wanders into the middle early, leaves corner squares stranded with no unvisited neighbours, and only discovers the problem dozens of moves later. Backtracking then has a huge subtree to undo.", [ml("bt", 4, 4)])
s.step("Trying the moves in a fixed order is slow: even a 5 by 5 open tour takes 8840 calls. On 8 by 8, plain backtracking can run for hours.", [ml("bt", 10, 10), s.take("number, recurse, un-number")])

s.scene("wr")
s.step("Stage 3: H. C. von Warnsdorff's rule. The degree of a square is the number of unvisited squares a knight could jump to from it.", [s.head("Stage 3 of 7: Warnsdorff's rule"), s.untake()] + hide("bt") + show("wr") + [hl("wr[0]")])
s.step("The rule: always jump to the neighbour with the smallest degree.", [hl("wr[1]")])
s.step("The intuition: a square with few exits left will soon have none. Visit it now, while you still can.", [hl("wr[2]")])
s.step("Ties are broken in a fixed order of the eight moves.", [hl("wr[3]")])
s.step("Combined with backtracking, the rule simply sets the order in which moves are tried. If it ever leads to a dead end, backtracking repairs it.", [hl("wr[4]"), s.take("go where the exits are fewest")])

s.scene("tour")
s.step("Stage 4: an 8 by 8 board, starting in the top-left corner, row 0, column 0. That is square 1.", [s.head("Stage 4 of 7: an 8 × 8 tour"), s.untake()] + hide("wr") + show("bd", "dg") + [st("bd[0][1]", "1"), hl("bd[0][1]")])
s.step("Two moves are possible, to row 2, column 1, or row 1, column 2. Both have degree 5: a tie, so take the first in move order. Square 2.", [hl("dg[0]"), st("bd[2][2]", "2", 0.5), hl("bd[2][2]", 0.5)])
s.step("From there, five candidates, with degrees 7, 7, 5, 3 and 3. The two of degree 3 are on the edge: row 0, column 2 comes first. Square 3.", [hl("dg[1]"), st("bd[0][3]", "3", 0.5)])
s.step("From row 0, column 2, the options have degrees 7, 5 and 2. Row 1, column 0 has only 2 exits: go there now. Square 4.", [hl("dg[2]"), st("bd[1][1]", "4", 0.5)])
s.step("Then row 3, column 1, degree 5, beats the other option, degree 7. Square 5. The knight hugs the edge, clearing the awkward squares first.", [hl("dg[3]"), st("bd[3][2]", "5", 0.5)])
chunks = [(6, 16), (17, 32), (33, 48), (49, 64)]
csay = ["Continuing by the same rule: squares 6 to 16 run down the left side, along the bottom edge and up the right.",
        "Squares 17 to 32 make a second lap around the outer rings of the board.",
        "Squares 33 to 48 work inwards.",
        "Squares 49 to 64 take what is left, including the far corner at 59. Along the way the search backtracked a few times: 117 calls for 64 squares."]
for (a, b), say in zip(chunks, csay):
    acts = [st(f"bd[{POS[k][0]}][{POS[k][1] + 1}]", str(k), round(0.9 * (k - a) / (b - a + 1), 2)) for k in range(a, b + 1)]
    s.step(say, acts)
s.step("Square 64 is at row 1, column 2: one knight's move from square 1 in the corner. A closed tour, found in 117 calls.", [mk("bd[1][3]"), mk("bd[0][1]", 0.3), s.take("closed tour: 64 is a knight's move from 1")])

s.scene("gn")
s.step("Stage 5: the lab asks to generalise to n by n. A knight always moves from a light square to a dark one, or back.", [s.head("Stage 5 of 7: n × n boards"), s.untake()] + hide("bd", "dg") + show("gn") + [hl("gn[0]")])
s.step("So a closed tour alternates colours all the way round, and needs an even number of squares. A 5 by 5 board, with 25, has open tours but no closed one.", [hl("gn[1]")])
s.step("For every even n from 6 up, closed tours exist.", [hl("gn[2]")])
s.step("Open tours, which need not return, exist for every n from 5 upwards. Boards of 2, 3 and 4 have no tour at all: there are not enough moves to escape the corners.", [hl("gn[1]")])
s.step("The program is the same, with n as a parameter. Warnsdorff's ordering keeps it fast for boards larger than 8.", [hl("gn[3]"), s.take("closed tour needs n² even")])

s.scene("cs")
s.step("Stage 6: the difference the rule makes. A 5 by 5 open tour: 8840 calls with plain order, 25 with Warnsdorff's: no backtracking at all.", [s.head("Stage 6 of 7: cost"), s.untake()] + hide("gn") + show("cs") + [hl("cs[0..=1]")])
s.step("An 8 by 8 open tour: 64 calls, one per square. The closed tour: 117, a little backtracking at the end.", [hl("cs[2..=3]")])
s.step("The worst case is still exponential, up to 8 choices at each of n squared levels. The heuristic changes the order, not the bound, but in practice it is what makes the search finish.", [hl("cs[4]"), s.take("same algorithm, better order")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("cs") + show("q") + [hl("q[0]")])
s.step("Prove the 5 by 5 case impossible, compute two degrees, and count the moves in a closed tour. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: every knight's move changes the square's colour. A closed tour of 25 squares makes 25 moves to return to the start.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("25 colour changes is odd, so the knight would end on the opposite colour from where it began: it cannot be back at the start. Impossible.", [hl("qa[1]"), mk("qa[1][2]", 0.5)])
s.step("b: from a corner, the knight can reach row 2, column 1 or row 1, column 2. Each has 5 unvisited neighbours: a tie.", [hl("qa[2]")])
s.step("c: visiting all n squared squares takes n squared minus 1 moves, and one more returns to the start: n squared moves in all.", [hl("qa[3]")])
s.step("The usual slip: forgetting to clear a square when backtracking. Without the undo, a failed branch leaves squares marked as visited.", [s.take("always undo the square on the way back")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A closed knight's tour is a backtracking search over moves. Warnsdorff's rule tries the square with the fewest exits first.", [hl("stages[0..=3]")])
s.step("Closed tours need an even number of squares. With the rule, an 8 by 8 closed tour takes 117 calls instead of hours.", [hl("stages[4..=5]")])
s.step("That completes Module 4. Module 5 asks which problems have no fast algorithm at all: P, NP and NP-completeness.", [mk("stages[0..=6]"), s.take("Next: Module 5, P and NP")])

s.save("/home/claude/playlist/dsa4/d4v8.json")

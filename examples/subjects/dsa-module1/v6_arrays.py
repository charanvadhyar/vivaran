"""DSA Module 1, video 6: arrays: address calculation, operations, sparse matrices."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

loc1 = lambda base, i, lb, w: base + (i - lb) * w
rowm = lambda base, i, j, lr, lc, nc, w: base + ((i - lr) * nc + (j - lc)) * w
colm = lambda base, i, j, lr, lc, nr, w: base + ((j - lc) * nr + (i - lr)) * w
assert loc1(1000, 25, 0, 4) == 1100
assert rowm(2000, 5, 7, 1, 1, 15, 4) == 2264 and colm(2000, 5, 7, 1, 1, 10, 4) == 2256
assert rowm(1000, 2, 5, -5, 2, 10, 8) == 1584 and colm(1000, 2, 5, -5, 2, 11, 8) == 1320
# order of cells in a 3 x 4 array
R = [[r * 4 + c for c in range(4)] for r in range(3)]; C = [[c * 3 + r for c in range(4)] for r in range(3)]
assert R[1][2] == 6 and C[1][2] == 7
a = [10, 20, 30, 40, 50]; a.insert(2, 25); assert a == [10, 20, 25, 30, 40, 50]
copies, cap = 0, 1
for k in range(17):
    if k == cap: copies += cap; cap *= 2
assert copies == 31 and cap == 32 and copies < 2 * 17
M = [[15, 0, 0, 22, 0, -15], [0, 11, 3, 0, 0, 0], [0, 0, 0, -6, 0, 0], [0, 0, 0, 0, 0, 0], [91, 0, 0, 0, 0, 0], [0, 0, 28, 0, 0, 0]]
trip = [(r, c, v) for r in range(6) for c in range(6) if (v := M[r][c])]
assert len(trip) == 8 and 3 * (len(trip) + 1) == 27
Q = [[0, 0, 3, 0, 4], [0, 0, 5, 7, 0], [0, 0, 0, 0, 0], [0, 2, 6, 0, 0]]
qt = [(r, c, v) for r in range(4) for c in range(5) if (v := Q[r][c])]
assert qt == [(0, 2, 3), (0, 4, 4), (1, 2, 5), (1, 3, 7), (3, 1, 2), (3, 2, 6)] and 3 * 7 == 21 > 20

s = Script("Arrays")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "What an array is"],
    [2, "The address of A[i]"],
    [3, "Two dimensions: row-major"],
    [4, "Column-major"],
    [5, "Inserting and deleting"],
    [6, "Growing an array"],
    [7, "Sparse matrices"],
    [8, "Exam question"]]})
s.obj({"id": "wh", "type": "table", "region": "center", "columns": ["an array", ""], "rows": [
    ["elements of one type", "each w bytes"],
    ["stored contiguously", "one after another in memory"],
    ["reached by index", "A[i]: any element in one step, Θ(1)"],
    ["fixed size, set when created", "the price of that speed"]]})
s.obj({"id": "arr", "type": "array", "region": "center", "values": [7, 3, 9, 4, 1, 8]})
s.obj({"id": "l1", "type": "math", "region": "center", "lines": [
    "\"LOC\"(A[i]) = \"base\" + (i - \"lb\") times w",
    "\"base\" = 1000, w = 4, \"lb\" = 0: quad \"LOC\"(A[25]) = 1000 + 25 times 4 = 1100",
    "\"one multiply and one add, whatever i is: \" Theta(1)"]})
s.obj({"id": "g", "type": "table", "region": "center", "columns": ["3 × 4 array", "col 0", "col 1", "col 2", "col 3"], "rows": [
    ["row 0", "", "", "", ""], ["row 1", "", "", "", ""], ["row 2", "", "", "", ""]]})
s.obj({"id": "rm", "type": "math", "region": "center", "lines": [
    "\"row-major:\" quad \"LOC\"(A[i][j]) = \"base\" + ((i - l_r) n_\"cols\" + (j - l_c)) times w",
    "\"column-major:\" quad \"LOC\"(A[i][j]) = \"base\" + ((j - l_c) n_\"rows\" + (i - l_r)) times w",
    "A[1..10][1..15], \"base\" 2000, w = 4, \"find\" A[5][7]",
    "\"row-major:\" quad 2000 + (4 times 15 + 6) times 4 = 2000 + 264 = 2264",
    "\"column-major:\" quad 2000 + (6 times 10 + 4) times 4 = 2000 + 256 = 2256"]})
s.obj({"id": "ins", "type": "array", "region": "center", "values": [10, 20, 30, 40, 50]})
s.obj({"id": "insx", "type": "table", "region": "center", "columns": ["operation", "cost"], "rows": [
    ["access A[i]", "Θ(1)"],
    ["search, unsorted", "Θ(n) worst"],
    ["search, sorted", "Θ(log n): binary search"],
    ["insert or delete at position k", "n − k shifts: Θ(n) worst, at the front"],
    ["insert or delete at the end", "Θ(1)"]]})
s.obj({"id": "gr", "type": "table", "region": "center", "columns": ["when the array is full", ""], "rows": [
    ["allocate twice the size", "copy everything across"],
    ["17 appends from capacity 1", "copies: 1 + 2 + 4 + 8 + 16 = 31"],
    ["in general", "copies < 2n for n appends"],
    ["so each append costs", "Θ(1) on average: amortised"],
    ["used by", "C++ vector, Java ArrayList, Python list"]]})
s.obj({"id": "sm", "type": "table", "region": "left", "rows": [[str(x) for x in r] for r in M]})
s.obj({"id": "tr", "type": "table", "region": "right", "columns": ["row", "col", "value"], "rows": [["6", "6", "8"]] + [[str(r), str(c), str(v)] for r, c, v in trip]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) A[−5..5][2..11], base 1000, 8 bytes per element: the address of A[2][5], row-major and column-major"],
    ["b) shifts to insert at the front of a full-length array of 1000 (with room for one more)"],
    ["c) the 4 × 5 matrix rows 0 0 3 0 4 · 0 0 5 7 0 · 0 0 0 0 0 · 0 2 6 0 0: its triplets, and does it save space?"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "n_\"rows\" = 5 - (-5) + 1 = 11, quad n_\"cols\" = 11 - 2 + 1 = 10",
    "\"row-major:\" quad 1000 + ((2 + 5) times 10 + (5 - 2)) times 8 = 1000 + 73 times 8 = 1584",
    "\"column-major:\" quad 1000 + ((5 - 2) times 11 + (2 + 5)) times 8 = 1000 + 40 times 8 = 1320",
    "\"b) all 1000 elements shift right: 1000 shifts\"",
    "\"c) (4,5,6) (0,2,3) (0,4,4) (1,2,5) (1,3,7) (3,1,2) (3,2,6): 21 values against 20: no saving\""]})

s.scene("intro")
s.step("The array is the simplest data structure, and the one every other structure is built on. This video shows how an array sits in memory, how the machine finds A of i in one step, and what that speed costs.", [s.head("Arrays")])
s.step("Here are the eight stages.", show("stages"))
s.step("What an array is, the address formula, and two-dimensional arrays stored by row and by column.", [hl("stages[0..=3]")])
s.step("Then inserting and deleting, growing an array, sparse matrices, and an exam question.", [hl("stages[4..=7]")])

s.scene("what")
s.step("Stage 1: an array holds elements of one type, each the same size, w bytes.", [s.head("Stage 1 of 8: what an array is")] + hide("stages") + show("wh") + [hl("wh[0]")])
s.step("They are stored contiguously: element 1 right after element 0, with no gaps.", [hl("wh[1]")])
s.step("So any element can be reached by its index in a single step.", [hl("wh[2]")])
s.step("The price: the size is fixed when the array is created, and the elements cannot be moved apart to make room.", [hl("wh[3]"), s.take("contiguous + same size = Θ(1) access")])

s.scene("addr")
s.step("Stage 2: here is an array of 6 integers.", [s.head("Stage 2 of 8: the address of A[i]"), s.untake()] + hide("wh") + show("arr") + [hl("arr")])
s.step("To find A of 3, the machine does not walk past A of 0, 1 and 2. It computes the address.", [hl("arr[3]")])
s.step("The address is the base address, plus i minus the lower bound, times the element size w.", show("l1") + [hl("l1[0]")])
s.step("With base 1000, 4-byte integers, and indices from 0: A of 25 is at 1000 plus 25 times 4, 1100.", [rv("l1[1]"), hl("l1[1]")])
s.step("C and Java always start at index 0, so the lower bound drops out and the address is just base plus i times w. Exam questions often use other lower bounds, like 1 or minus 5, so keep the subtraction.", [hl("l1[0]")])
s.step("One multiply and one add, whatever i is. That is why array access is Theta of 1.", [rv("l1[2]"), hl("l1[2]"), s.take("LOC = base + (i − lb) · w")])

s.scene("row")
s.step("Stage 3: memory is one long line, so a two-dimensional array must be laid out in one dimension. Here is a 3 by 4 array.", [s.head("Stage 3 of 8: row-major order"), s.untake()] + hide("arr", "l1") + show("g"))
s.step("Row-major order, used by C, C++ and Java, stores row 0 first, then row 1, then row 2. Here are the positions.", [st(f"g[{r}][{c + 1}]", str(R[r][c]), round(0.05 * (r * 4 + c), 2)) for r in range(3) for c in range(4)])
s.step("A of 1, 2 is at position 6: one full row of 4 before it, plus 2.", [hl("g[1][3]")])
s.step("The formula: base, plus the row offset times the number of columns, plus the column offset, all times w.", hide("g") + show("rm") + [hl("rm[0]"), s.take("row-major: skip whole rows, then columns")])

s.scene("col")
s.step("Stage 4: column-major order, used by Fortran and MATLAB, stores column 0 first. Skip whole columns, each of n rows elements, then the rows.", [s.head("Stage 4 of 8: column-major order"), s.untake(), rv("rm[1]"), hl("rm[1]")])
s.step("An example: A indexed 1 to 10 by 1 to 15, base 2000, 4 bytes each. Find A of 5, 7.", [rv("rm[2]"), hl("rm[2]")])
s.step("Row-major: 4 full rows of 15 before row 5, plus 6 before column 7: 66 elements, 264 bytes. Address 2264.", [rv("rm[3]"), hl("rm[3]")])
s.step("Column-major: 6 full columns of 10, plus 4: 64 elements, 256 bytes. Address 2256.", [rv("rm[4]"), hl("rm[4]")])
s.step("Three dimensions work the same way. In row-major order, A of i, j, k skips i whole planes of n 2 times n 3 elements, then j rows of n 3, then k elements.", [hl("rm[0]")])
s.step("The same element, two different addresses. Always check which order the question uses, and subtract the lower bounds first.", [s.take("subtract lower bounds, then count what comes before")])

s.scene("ins")
s.step("Stage 5: the price of contiguity. Insert 25 at index 2 of this array.", [s.head("Stage 5 of 8: inserting and deleting"), s.untake()] + hide("rm") + show("ins") + [hl("ins[2]")])
s.step("There is no gap, so 30, 40 and 50 must each shift one place right to make room. Three shifts, then 25 goes in.", [hl("ins[2..=4]"), ins("ins", 2, 25, 0.5)])
s.step("In general, inserting at position k shifts n minus k elements. At the front, all n: Theta of n. Deleting shifts the same way, left.", hide("ins") + show("insx") + [hl("insx[3]")])
s.step("At the end, nothing shifts: Theta of 1.", [hl("insx[4]")])
s.step("And access stays Theta of 1, with search linear, or logarithmic if the array is kept sorted.", [hl("insx[0..=2]"), s.take("fast to read, slow to insert in the middle")])

s.scene("grow")
s.step("Stage 6: what if the array is full? A dynamic array allocates a new one, twice the size, and copies everything across.", [s.head("Stage 6 of 8: growing an array"), s.untake()] + hide("insx") + show("gr") + [hl("gr[0]")])
s.step("Append 17 elements, starting with room for 1. It grows at 1, 2, 4, 8 and 16 elements: 31 copies in all.", [hl("gr[1]")])
s.step("The copies always add to less than twice the number of appends.", [hl("gr[2]")])
s.step("So the average append costs Theta of 1, even though a single one occasionally costs n. That average over a sequence is called amortised cost.", [hl("gr[3]")])
s.step("This is how C plus plus vector, Java ArrayList and Python lists grow.", [hl("gr[4]"), s.take("double when full: Θ(1) amortised append")])

s.scene("sparse")
s.step("Stage 7: a sparse matrix is mostly zeros. This 6 by 6 matrix has 36 entries, but only 8 are non-zero.", [s.head("Stage 7 of 8: sparse matrices"), s.untake()] + hide("gr") + show("sm") + [mk("sm[0][0]"), mk("sm[0][3]", 0.1), mk("sm[0][5]", 0.2), mk("sm[1][1]", 0.3), mk("sm[1][2]", 0.4), mk("sm[2][3]", 0.5), mk("sm[4][0]", 0.6), mk("sm[5][2]", 0.7)])
s.step("Store only the non-zeros, as triplets: row, column, value. The first row is a header: 6 rows, 6 columns, 8 non-zeros.", show("tr") + [hl("tr[0]")])
s.step("Then one triplet per non-zero, in row order: 0, 0, 15; 0, 3, 22; and so on.", [hl("tr[1..=8]")])
s.step("9 triplets of 3 values: 27 values instead of 36. With t non-zeros, the triplets win only when 3 times t plus 1 is less than m times n.", [s.take("triplets: (row, col, value), header first")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("sm", "tr") + show("q") + [hl("q[0]")])
s.step("Find an address in both orders, count the shifts for an insert at the front, and write a small matrix as triplets. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: the rows run from minus 5 to 5: 11 rows. The columns from 2 to 11: 10 columns.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Row-major: row offset 2 minus minus 5, 7, times 10, plus column offset 3: 73 elements, times 8, 584. Address 1584.", [rv("qa[1]"), hl("qa[1]")])
s.step("Column-major: column offset 3 times 11 rows, plus row offset 7: 40 elements, 320 bytes. Address 1320.", [rv("qa[2]"), hl("qa[2]")])
s.step("b: every one of the 1000 elements shifts right: 1000 shifts.", [rv("qa[3]"), hl("qa[3]")])
s.step("c: 6 non-zeros. The header 4, 5, 6, then 0, 2, 3; 0, 4, 4; 1, 2, 5; 1, 3, 7; 3, 1, 2; 3, 2, 6. That is 21 values, more than the 20 entries of the matrix: no saving here.", [rv("qa[4]"), hl("qa[4]")])
s.step("The usual slip: forgetting to subtract a negative lower bound. 2 minus minus 5 is 7, not minus 3.", [s.take("i − lb, even when lb is negative")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("An array is contiguous, so A of i is one multiply and one add away. Two-dimensional arrays are laid out by rows or by columns, and the formula counts what comes before.", [hl("stages[0..=3]")])
s.step("Inserting in the middle shifts elements, doubling gives amortised constant appends, and triplets store sparse matrices compactly, when they are sparse enough.", [hl("stages[4..=6]")])
s.step("Next video: a structure that only lets you touch one end. The stack.", [mk("stages[0..=7]"), s.take("Next: stacks")])

s.save("/home/claude/playlist/dsa1/d1v6.json")

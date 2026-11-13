"""DSA Module 1, video 1: algorithms, data structures, and how to specify an algorithm."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

def isort(a):
    a = a[:]; passes = []; shifts = []
    for j in range(1, len(a)):
        key = a[j]; i = j - 1; s = 0
        while i >= 0 and a[i] > key:
            a[i + 1] = a[i]; i -= 1; s += 1
        a[i + 1] = key; passes.append(a[:]); shifts.append(s)
    return passes, shifts

P, S = isort([5, 2, 4, 6, 1, 3])
assert P == [[2, 5, 4, 6, 1, 3], [2, 4, 5, 6, 1, 3], [2, 4, 5, 6, 1, 3], [1, 2, 4, 5, 6, 3], [1, 2, 3, 4, 5, 6]] and S == [1, 1, 0, 4, 3]
Q, QS = isort([31, 41, 59, 26, 41, 58])
assert Q[-1] == [26, 31, 41, 41, 58, 59] and QS == [0, 0, 3, 1, 1] and sum(QS) == 5
assert Q[2] == [26, 31, 41, 59, 41, 58] and Q[3] == [26, 31, 41, 41, 59, 58]
assert (1_000_000).bit_length() == 20

s = Script("Algorithms and their specification")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "What an algorithm is"],
    [2, "What a data structure is"],
    [3, "Five properties of an algorithm"],
    [4, "Writing an algorithm down"],
    [5, "Insertion sort, step by step"],
    [6, "Why it is correct: a loop invariant"],
    [7, "Why the data structure matters"],
    [8, "Exam question"]]})
s.obj({"id": "def", "type": "table", "region": "center", "columns": ["an algorithm", ""], "rows": [
    ["a well-defined procedure", "a finite list of exact steps"],
    ["takes an input", "a value or set of values"],
    ["produces an output", "a value or set of values"],
    ["solves a problem", "for every instance, not just one"],
    ["the sorting problem", "input: ⟨31, 41, 59, 26, 41, 58⟩ → output: ⟨26, 31, 41, 41, 58, 59⟩"]]})
s.obj({"id": "ds", "type": "table", "region": "center", "columns": ["a data structure", ""], "rows": [
    ["a way to store and organise data", "so that access and changes are cheap"],
    ["linear", "array, stack, queue, linked list: one after another"],
    ["non-linear", "trees, heaps, graphs: Module 2"],
    ["no single best one", "each makes some operations fast and others slow"]]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["property", "meaning", "fails when…"], "rows": [
    ["input", "zero or more quantities supplied", ""],
    ["output", "at least one quantity produced", "it returns nothing"],
    ["definiteness", "every step is clear and unambiguous", "\"add a few\""],
    ["finiteness", "it stops after finitely many steps", "while (true) with no exit"],
    ["effectiveness", "every step can be done exactly, in finite time", "\"divide by the largest prime\""]]})
s.obj({"id": "spec", "type": "table", "region": "center", "columns": ["way to write it", "good for", "weak at"], "rows": [
    ["natural language", "the idea", "ambiguous"],
    ["flowchart", "small control flow", "large programs"],
    ["pseudocode", "exact, yet language-free", "needs agreed conventions"],
    ["a program", "running it", "hides the idea in details"]]})
s.obj({"id": "code", "type": "code", "region": "left", "language": "text", "lines": [
    "INSERTION-SORT(A, n)",
    "  for j = 2 to n",
    "      key = A[j]",
    "      // insert A[j] into the sorted A[1 .. j-1]",
    "      i = j - 1",
    "      while i > 0 and A[i] > key",
    "          A[i + 1] = A[i]        // shift right",
    "          i = i - 1",
    "      A[i + 1] = key"]})
s.obj({"id": "arr", "type": "array", "region": "right", "values": [5, 2, 4, 6, 1, 3]})
s.obj({"id": "jp", "type": "pointer", "label": "j", "target": "arr[1]"})
s.obj({"id": "inv", "type": "table", "region": "center", "columns": ["loop invariant", "A[1 .. j−1] holds the original first j−1 elements, sorted"], "rows": [
    ["initialization", "j = 2: A[1 .. 1] is one element, so it is sorted"],
    ["maintenance", "each pass shifts the larger ones right and drops key into the gap"],
    ["termination", "the loop ends at j = n + 1: A[1 .. n] is sorted"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["find a value among n = 1,000,000", "comparisons, worst case"], "rows": [
    ["unsorted array: look at each in turn", "1,000,000"],
    ["sorted array: binary search", "20"],
    ["the same data, organised differently", "50,000 times fewer steps"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) trace INSERTION-SORT on ⟨31, 41, 59, 26, 41, 58⟩: the array after each pass"],
    ["b) how many shifts (line 6) in all?"],
    ["c) which property fails?  (i) \"repeat until x is small enough\"   (ii) i = 1; while (i > 0) i++;"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["j", "key", "array after the pass", "shifts"], "rows": [
    ["2", "41", "31 41 59 26 41 58", "0"],
    ["3", "59", "31 41 59 26 41 58", "0"],
    ["4", "26", "26 31 41 59 41 58", "3"],
    ["5", "41", "26 31 41 41 59 58", "1"],
    ["6", "58", "26 31 41 41 58 59", "1"]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"b) shifts\" = 0 + 0 + 3 + 1 + 1 = 5",
    "\"c) (i) definiteness: 'small enough' is not exact\" quad \"(ii) finiteness: it never stops\""]})

s.scene("intro")
s.step("Every program you write is an algorithm working on some data structure. This first video says exactly what those two words mean, and how to write an algorithm down so that anyone can follow it and check it.", [s.head("Algorithms and data structures")])
s.step("Here are the eight stages.", show("stages"))
s.step("What an algorithm is, what a data structure is, the five properties every algorithm must have, and ways of writing one down.", [hl("stages[0..=3]")])
s.step("Then insertion sort traced step by step, why it is correct, why the choice of data structure matters, and an exam question.", [hl("stages[4..=7]")])

s.scene("def")
s.step("Stage 1: an algorithm is a well-defined procedure: a finite list of exact steps.", [s.head("Stage 1 of 8: what an algorithm is")] + hide("stages") + show("def") + [hl("def[0]")])
s.step("It takes an input, a value or a set of values, and produces an output.", [hl("def[1..=2]")])
s.step("And it solves a problem: it must work for every instance of the problem, not just the one you tried.", [hl("def[3]")])
s.step("The sorting problem is the standard example. The input is a sequence of numbers; the output is the same numbers in increasing order. 31, 41, 59, 26, 41, 58 becomes 26, 31, 41, 41, 58, 59.", [hl("def[4]"), s.take("algorithm: input → exact steps → output")])

s.scene("ds")
s.step("Stage 2: a data structure is a way to store and organise data so that the operations we need, finding, adding, removing, are cheap.", [s.head("Stage 2 of 8: what a data structure is"), s.untake()] + hide("def") + show("ds") + [hl("ds[0]")])
s.step("Linear structures keep items one after another: arrays, stacks, queues and linked lists, the rest of this module.", [hl("ds[1]")])
s.step("Non-linear structures branch: trees, heaps and graphs, in Module 2.", [hl("ds[2]")])
s.step("There is no single best structure. Each makes some operations fast and others slow, so the choice depends on what the program does most.", [hl("ds[3]"), s.take("choose the structure for the operations you need")])

s.scene("prop")
s.step("Stage 3: the classic definition, from Knuth, lists five properties. Input: zero or more quantities are supplied.", [s.head("Stage 3 of 8: five properties"), s.untake()] + hide("ds") + show("pr") + [hl("pr[0]")])
s.step("Output: at least one quantity is produced. A procedure that returns nothing solves nothing.", [hl("pr[1]")])
s.step("Definiteness: every step is clear and unambiguous. An instruction like add a few is not.", [hl("pr[2]")])
s.step("Finiteness: it stops after a finite number of steps, for every input. A loop with no way out fails this.", [hl("pr[3]")])
s.step("Effectiveness: each step is basic enough to be carried out exactly, in finite time. Divide by the largest prime cannot be done: there is no largest prime.", [hl("pr[4]")])
s.step("A procedure that has the first four but may run forever, like an operating system, is called a computational procedure, not an algorithm.", [s.take("input · output · definite · finite · effective")])

s.scene("spec")
s.step("Stage 4: how do we write an algorithm down? In natural language: good for the idea, but ambiguous.", [s.head("Stage 4 of 8: writing it down"), s.untake()] + hide("pr") + show("spec") + [hl("spec[0]")])
s.step("As a flowchart: clear for small control flow, unreadable for large programs.", [hl("spec[1]")])
s.step("As pseudocode: exact, yet free of any one language's details. This course, like Cormen's textbook, uses pseudocode, with arrays counted from 1.", [hl("spec[2]")])
s.step("As a real program: it runs, but the idea is buried under declarations and input-output.", [hl("spec[3]"), s.take("pseudocode: exact but language-free")])

s.scene("trace")
s.step("Stage 5: insertion sort, in Cormen's pseudocode. It sorts the way you sort playing cards in your hand.", [s.head("Stage 5 of 8: insertion sort"), s.untake()] + hide("spec") + show("code", "arr") + [ml("code", 1, 9)])
s.step("The cards to the left of j are already sorted. Take the next one, key, and shift every larger card one place right, then drop key into the gap.", [ml("code", 2, 9)])
s.step("Our input: 5, 2, 4, 6, 1, 3. j starts at the second element, 2. The picture numbers cells from 0, the pseudocode from 1, so j equal to 2 is the cell marked 1.", show("jp") + [hl("arr[1]")])
s.step("j equal to 2: key is 2. 5 is larger, so it shifts right, and 2 goes first. 2, 5.", [ml("code", 6, 7)] + setrow("arr", [5, 2, 4, 6, 1, 3], P[0], 0.3) + [mk("arr[0..=1]", 0.6)])
s.step("j equal to 3: key is 4. 5 shifts right; 2 is smaller, so 4 goes after 2. 2, 4, 5.", [pt("jp", "arr[2]")] + setrow("arr", P[0], P[1], 0.3) + [mk("arr[0..=2]", 0.6)])
s.step("j equal to 4: key is 6. 5 is smaller, so nothing moves.", [pt("jp", "arr[3]"), mk("arr[0..=3]", 0.4)])
s.step("j equal to 5: key is 1, the smallest so far. 6, 5, 4 and 2 all shift right: four shifts. 1 goes first.", [pt("jp", "arr[4]")] + setrow("arr", P[2], P[3], 0.3) + [mk("arr[0..=4]", 0.7)])
s.step("j equal to 6: key is 3. 6, 5 and 4 shift right, and 3 goes after 2. The array is sorted: 1, 2, 3, 4, 5, 6.", [pt("jp", "arr[5]")] + setrow("arr", P[3], P[4], 0.3) + [mk("arr[0..=5]", 0.7), s.take("sorted part grows by one each pass")])

s.scene("inv")
s.step("Stage 6: how do we know it always works, not just on this input? With a loop invariant: at the start of each pass, A of 1 to j minus 1 holds the original first j minus 1 elements, in sorted order.", [s.head("Stage 6 of 8: a loop invariant"), s.untake()] + hide("code", "arr", "jp") + show("inv"))
s.step("Initialization: before the first pass, j is 2, and A of 1 to 1 is a single element. One element is always sorted.", [hl("inv[0]")])
s.step("Maintenance: each pass shifts the larger elements right and puts key in the gap, so A of 1 to j is sorted before j grows.", [hl("inv[1]")])
s.step("Termination: the loop stops when j reaches n plus 1. The invariant then says A of 1 to n is sorted: the whole array.", [hl("inv[2]"), s.take("invariant: true at start, kept by each pass, gives the answer at the end")])

s.scene("why")
s.step("Stage 7: why does the data structure matter? Find a value among a million. In an unsorted array, the worst case looks at every element: a million comparisons.", [s.head("Stage 7 of 8: why structure matters"), s.untake()] + hide("inv") + show("why") + [hl("why[0]")])
s.step("Keep the array sorted, and binary search halves the range each time: 20 comparisons, since 2 to the 20 is just over a million.", [hl("why[1]")])
s.step("The same data, organised differently: fifty thousand times fewer steps. Measuring that difference precisely is the next two videos.", [hl("why[2]"), s.take("organisation decides cost")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("why") + show("q") + [hl("q[0..=1]")])
s.step("Trace insertion sort on 31, 41, 59, 26, 41, 58, count the shifts, and say which property each of two procedures breaks. Pause and work it out.", [hl("q[2]")])
s.step("j equal to 2 and 3: 41 and 59 are already larger than everything before them. No shifts.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("j equal to 4: key 26 is smaller than 59, 41 and 31. Three shifts, and 26 goes first.", [hl("qa[2]")])
s.step("j equal to 5: key 41. Only 59 is larger: one shift. The equal 41 stays in front, since the test is strictly greater. That keeps equal keys in their original order.", [hl("qa[3]")])
s.step("j equal to 6: key 58. 59 shifts: one shift. Sorted.", [hl("qa[4]"), mk("qa[4][2]", 0.4)])
s.step("b: 0 plus 0 plus 3 plus 1 plus 1: 5 shifts.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("c: small enough is not exact, so the first fails definiteness. The second loop counts up from 1 forever, so it fails finiteness.", [rv("qb[1]"), hl("qb[1]")])
s.step("The usual slip: writing greater than or equal in the while test. It still sorts, but equal keys swap places, and it does extra shifts.", [s.take("A[i] > key, not ≥")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("An algorithm turns input into output by exact, finite, effective steps. A data structure organises data so the needed operations are cheap.", [hl("stages[0..=3]")])
s.step("Insertion sort grows a sorted prefix one element at a time, and a loop invariant proves it correct. Organisation can change the cost by factors of thousands.", [hl("stages[4..=6]")])
s.step("Next video: measuring cost. Performance analysis, step counts, time and space.", [mk("stages[0..=7]"), s.take("Next: performance analysis")])

s.save("/home/claude/playlist/dsa1/d1v1.json")

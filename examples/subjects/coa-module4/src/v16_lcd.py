"""Module 4, video 16: loop-carried dependences."""
import sys, random
sys.path.insert(0, "/home/claude/playlist")
from common import Script

random.seed(4)
R = lambda n: [random.randint(0, 9) for _ in range(n)]

# example 2 (Hennessy and Patterson): S1 A[i] = A[i] + B[i]; S2 B[i+1] = C[i] + D[i]
A, B, C, D = R(101), R(101), R(100), R(100)
a1, b1 = A[:], B[:]
for i in range(100):
    a1[i] = a1[i] + b1[i]; b1[i + 1] = C[i] + D[i]
a2, b2 = A[:], B[:]
a2[0] = a2[0] + b2[0]
for i in range(99):
    b2[i + 1] = C[i] + D[i]; a2[i + 1] = a2[i + 1] + b2[i + 1]
b2[100] = C[99] + D[99]
assert (a1, b1) == (a2, b2)

# exam part c: S1 A[i] = B[i] + 1; S2 B[i+1] = C[i] * 2
A, B, C = R(100), R(101), R(100)
a1, b1 = A[:], B[:]
for i in range(100):
    a1[i] = b1[i] + 1; b1[i + 1] = C[i] * 2
a2, b2 = A[:], B[:]
a2[0] = b2[0] + 1
for i in range(99):
    b2[i + 1] = C[i] * 2; a2[i + 1] = b2[i + 1] + 1
b2[100] = C[99] * 2
assert (a1, b1) == (a2, b2)

# distance 3: A[i] = A[i-3] + B[i]; chunks of 3 consecutive i are independent
A, B = R(30), R(30)
s1 = A[:]
for i in range(3, 30): s1[i] = s1[i - 3] + B[i]
s2 = A[:]
for j in range(3, 30, 3):
    old = s2[:]
    for i in range(j, min(j + 3, 30)): s2[i] = old[i - 3] + B[i]
assert s1 == s2
# a vector of 4 would be wrong
s3 = A[:]
for j in range(3, 30, 4):
    old = s3[:]
    for i in range(j, min(j + 4, 30)): s3[i] = old[i - 3] + B[i]
assert s3 != s1

s = Script("Loop-carried dependences")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Can the iterations run at once?"],
    [2, "Carried, or within one iteration"],
    [3, "Following the chain"],
    [4, "A carried dependence that is not a cycle"],
    [5, "Dependence distance"],
    [6, "True, anti and output dependences"],
    [7, "When the compiler cannot tell"],
    [8, "Exam question"]]})
s.obj({"id": "ok", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 999; i >= 0; i--)",
    "    x[i] = x[i] + s;          // iteration i touches only x[i]",
    "",
    "for (i = 1; i < 1000; i++)",
    "    x[i] = x[i - 1] + s;      // iteration i needs iteration i - 1"]})
s.obj({"id": "e1", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 100; i++) {",
    "    A[i+1] = A[i] + C[i];      /* S1 */",
    "    B[i+1] = B[i] + A[i+1];    /* S2 */",
    "}"]})
s.obj({"id": "e1d", "type": "table", "region": "center", "columns": ["dependence", "value", "kind"], "rows": [
    ["S1 → S1", "A[i] was written as A[i+1] last iteration", "loop-carried"],
    ["S2 → S2", "B[i] was written as B[i+1] last iteration", "loop-carried"],
    ["S1 → S2", "A[i+1] written earlier in the same iteration", "within the iteration"]]})
s.obj({"id": "tr", "type": "table", "region": "center", "columns": ["iteration", "S1 reads", "S1 writes", "S2 reads", "S2 writes"], "rows": [
    ["0", "A[0]", "A[1]", "B[0], A[1]", "B[1]"],
    ["1", "A[1]", "A[2]", "B[1], A[2]", "B[2]"],
    ["2", "A[2]", "A[3]", "B[2], A[3]", "B[3]"],
    ["3", "A[3]", "A[4]", "B[3], A[4]", "B[4]"]]})
s.obj({"id": "e2", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 100; i++) {",
    "    A[i] = A[i] + B[i];        /* S1: uses B[i] from S2 last time */",
    "    B[i+1] = C[i] + D[i];      /* S2: uses nothing from S1 */",
    "}",
    "",
    "A[0] = A[0] + B[0];                           // first S1 on its own",
    "for (i = 0; i < 99; i++) {",
    "    B[i+1] = C[i] + D[i];",
    "    A[i+1] = A[i+1] + B[i+1];   // now within one iteration",
    "}",
    "B[100] = C[99] + D[99];                       // last S2 on its own"]})
s.obj({"id": "ds", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 3; i < 1000; i++)",
    "    A[i] = A[i-3] + B[i];      // distance 3",
    "",
    "// A[3], A[4], A[5] need only A[0], A[1], A[2]: independent",
    "// A[6], A[7], A[8] need A[3], A[4], A[5]",
    "// so 3 at a time can run in parallel, but not 4"]})
s.obj({"id": "ty", "type": "table", "region": "center", "columns": ["kind", "pattern", "example", "real?"], "rows": [
    ["true (RAW)", "write, then read", "X[i] = …;  … = X[i];", "yes: data flows"],
    ["anti (WAR)", "read, then write", "… = X[i];  X[i] = …;", "no: a name clash"],
    ["output (WAW)", "write, then write", "X[i] = …;  X[i] = …;", "no: a name clash"]]})
s.obj({"id": "al", "type": "code", "region": "center", "language": "c", "lines": [
    "void add(float *x, float *y, int n) {",
    "    for (i = 0; i < n; i++)",
    "        x[i] = y[i] + 1;        // safe only if x and y do not overlap",
    "}",
    "add(p + 1, p, n);              // overlap: x[i] is y[i+1], a carried dependence",
    "",
    "void add(float *restrict x, float *restrict y, int n);   // promise: no overlap"]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "c", "lines": [
    "// a)",
    "for (i = 0; i < 100; i++) {",
    "    A[i] = B[i] + C[i];     /* S1 */",
    "    D[i] = A[i] * E[i];     /* S2 */",
    "    B[i+1] = D[i] + 1;      /* S3 */",
    "}",
    "// b) for (i = 0; i < 100; i++) A[i+4] = A[i] * 2;",
    "// c) for (i = 0; i < 100; i++) { A[i] = B[i] + 1; B[i+1] = C[i] * 2; }",
    "// for each: dependences, which are carried, can it run in parallel?"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["loop", "dependences", "parallel?"], "rows": [
    ["a", "S1 → S2 (A[i]), S2 → S3 (D[i]): within; S3 → S1 (B[i]): carried", "no: S3 → S1 → S2 → S3 is a cycle"],
    ["b", "A[i+4] read 4 iterations later: carried, distance 4", "4 at a time"],
    ["c", "S2 → S1 (B[i]): carried, but no cycle", "yes, after the rewrite"]]})
s.obj({"id": "qc", "type": "code", "region": "center", "language": "c", "lines": [
    "A[0] = B[0] + 1;",
    "for (i = 0; i < 99; i++) {",
    "    B[i+1] = C[i] * 2;",
    "    A[i+1] = B[i+1] + 1;      // no carried dependence: fully parallel",
    "}",
    "B[100] = C[99] * 2;"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Vector units, SIMD instructions and GPUs all need the same thing: loop iterations that can run at the same time. This video shows how to tell, by finding the dependences between iterations.", [s.head("Loop-carried dependences")])
s.step("Here are the eight stages.", show("stages"))
s.step("The basic question, dependences carried between iterations, following the chain, and a dependence that can be removed by rewriting.", [hl("stages[0..=3]")])
s.step("Then dependence distance, the three kinds of dependence, pointers that hide dependences, and an exam question.", [hl("stages[4..=7]")])

s.scene("ok")
s.step("Stage 1: in this loop, iteration i reads and writes only x of i. No iteration needs another, so all 1000 can run at once.", [s.head("Stage 1 of 8: can the iterations run at once?")] + hide("stages") + show("ok") + [ml("ok", 1, 2)])
s.step("In this one, iteration i reads x of i minus 1, written by the iteration before. Each must wait for the last: the loop is sequential.", [ml("ok", 4, 5)])
s.step("A dependence from one iteration to a later one is called loop-carried. Loop-level parallelism exists when there are no loop-carried dependences.", [s.take("parallel loop = no loop-carried dependence")])

s.scene("e1")
s.step("Stage 2: the textbook's first example. Two statements, S1 and S2.", [s.head("Stage 2 of 8: carried or within"), s.untake()] + hide("ok") + show("e1") + [ml("e1", 1, 4)])
s.step("S1 reads A of i, and S1 itself wrote that value, as A of i plus 1, in the previous iteration.", [ml("e1", 2, 2)])
s.step("S2 does the same with B: it reads B of i, written by S2 last time.", [ml("e1", 3, 3)])
s.step("And S2 reads A of i plus 1, which S1 wrote earlier in the same iteration.", hide("e1") + show("e1d") + [hl("e1d[2]")])
s.step("So two dependences are loop-carried, S1 on itself and S2 on itself. One is within a single iteration, and does not stop the iterations from running at once.", [hl("e1d[0..=1]"), s.take("S1 → S1 and S2 → S2 are carried: sequential")])

s.scene("trace")
s.step("Stage 3: to see it, list what each iteration reads and writes. Iteration 0 writes A of 1.", [s.head("Stage 3 of 8: following the chain"), s.untake()] + hide("e1d") + show("tr") + [hl("tr[0][2]")])
s.step("Iteration 1 reads A of 1. So it cannot start until iteration 0 has finished S1.", [hl("tr[1][1]")])
s.step("The same holds for every pair: A of 2, A of 3, A of 4. A chain through all 100 iterations.", [hl("tr[1][2]"), hl("tr[2][1]", 0.3), hl("tr[2][2]", 0.6), hl("tr[3][1]", 0.9)])
s.step("Compare S2 reading A of 1 in iteration 0: written by S1 in the same row. A dependence inside one row does not stop the rows from running together; each row just runs S1 before S2.", [hl("tr[0][2]"), hl("tr[0][3]", 0.3)])
s.step("And for B too. The value read in one row was written in the row above. That is a loop-carried dependence, seen in a table.", [hl("tr[0][4]"), hl("tr[1][3]", 0.3), s.take("a value written in one row, read in the next")])

s.scene("e2")
s.step("Stage 4: a second example. S1 reads B of i, which S2 wrote in the previous iteration. That is loop-carried.", [s.head("Stage 4 of 8: carried, but no cycle"), s.untake()] + hide("tr") + show("e2") + [ml("e2", 1, 4)])
s.step("But S2 uses nothing from S1, and nothing from itself. The dependence goes one way, S2 to S1, with no cycle back.", [ml("e2", 3, 3)])
s.step("Then the loop can be rewritten. Do the first S1 on its own.", [ml("e2", 6, 6)])
s.step("Inside the loop, put S2 first, then the next iteration's S1. Now S1 reads B of i plus 1, written just before, in the same iteration.", [ml("e2", 7, 10)])
s.step("Finish with the last S2 on its own. The new loop has no carried dependence, so its 99 iterations can run in parallel.", [ml("e2", 11, 11), s.take("no cycle: rewrite and parallelise")])

s.scene("dist")
s.step("Stage 5: here A of i depends on A of i minus 3. The dependence distance is 3.", [s.head("Stage 5 of 8: dependence distance"), s.untake()] + hide("e2") + show("ds") + [ml("ds", 1, 2)])
s.step("A of 3, 4 and 5 need only A of 0, 1 and 2, which already exist. Those three can be computed together.", [ml("ds", 4, 4)])
s.step("A of 6, 7 and 8 need A of 3, 4 and 5: the next group of three.", [ml("ds", 5, 5)])
s.step("So the loop runs in parallel 3 at a time, but not 4: a vector of 4 would read A of 6 before it is written. A distance of d allows vectors of length d.", [ml("ds", 6, 6)])
s.step("In practice a distance of 3 helps little: a 64-element vector register, or a warp of 32, would be mostly idle. A distance of 64 or more lets a whole vector, or a whole warp, run at once.", [s.take("distance d: d iterations at a time")])

s.scene("types")
s.step("Stage 6: dependences come in three kinds. A true dependence: write, then read. Data really flows from one to the other.", [s.head("Stage 6 of 8: three kinds"), s.untake()] + hide("ds") + show("ty") + [hl("ty[0]")])
s.step("An antidependence: read, then write. The later write must not overwrite the value before it is read.", [hl("ty[1]")])
s.step("An output dependence: two writes to the same place. The final value must come from the later one.", [hl("ty[2]")])
s.step("Only true dependences are real. Anti and output dependences come from reusing a name, and renaming removes them. That is the next video.", [hl("ty[1][3]"), hl("ty[2][3]", 0.3), s.take("only true dependences are real")])

s.scene("alias")
s.step("Stage 7: with pointers, the compiler often cannot tell. This function looks parallel.", [s.head("Stage 7 of 8: when the compiler cannot tell"), s.untake()] + hide("ty") + show("al") + [ml("al", 1, 4)])
s.step("But if it is called with x one element past y, then x of i is y of i plus 1. Each iteration writes what the next one reads: a carried dependence.", [ml("al", 5, 5)])
s.step("So the compiler must assume the worst and not vectorise, unless the programmer promises there is no overlap, with the restrict keyword.", [ml("al", 7, 7), s.take("unknown pointers: assume a dependence")])

s.scene("exam")
s.step("Now an exam question: three loops.", [s.head("Exam question"), s.untake()] + hide("al") + show("q") + [ml("q", 1, 6)])
s.step("For each, find the dependences, say which are carried, and whether the loop can run in parallel. Pause and work it out.", [ml("q", 7, 9)])
s.step("Loop a: S2 reads A of i from S1, and S3 reads D of i from S2. Both are within one iteration.", hide("q") + show("qa") + [hl("qa[0][1]")])
s.step("But S1 reads B of i, which S3 wrote last iteration. Carried. And it closes a cycle: S3, then S1, then S2, then S3 again. Loop a is sequential.", [hl("qa[0][2]")])
s.step("Loop b: A of i plus 4 is read 4 iterations later. Carried, with distance 4: it runs 4 iterations at a time.", [hl("qa[1]")])
s.step("Loop c: S1 reads B of i from S2's last iteration. Carried, but S2 depends on nothing, so there is no cycle.", [hl("qa[2]")])
s.step("Rewrite it as in stage 4: the first S1 alone, then S2 followed by the next S1, then the last S2 alone. The loop is now fully parallel.", hide("qa") + show("qc") + [ml("qc", 1, 6)])
s.step("The usual slip: calling every carried dependence fatal. Look for a cycle first.", [s.take("carried + cycle = sequential")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qc") + show("stages"))
s.step("A loop is parallel when no iteration needs a value from another. Tables of reads and writes show the carried dependences, and a carried dependence without a cycle can be rewritten away.", [hl("stages[0..=3]")])
s.step("A distance d allows d iterations at once. Only true dependences are real, and unknown pointers force the compiler to assume the worst.", [hl("stages[4..=6]")])
s.step("Next video: a test that decides whether a dependence can exist, and how to remove name dependences. The GCD test.", [mk("stages[0..=7]"), s.take("Next: the GCD test")])

s.save("/home/claude/playlist/m4/m4v16.json")

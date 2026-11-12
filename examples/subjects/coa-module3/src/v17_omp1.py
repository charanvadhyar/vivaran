"""Module 3, video 17: OpenMP part 1 - fork-join, parallel, for, sections, single, data scoping."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script


def static_chunks(n, p):
    """schedule(static) without a chunk size: contiguous blocks, as equal as possible."""
    q, r = divmod(n, p)
    out, start = [], 0
    for t in range(p):
        k = q + (1 if t < r else 0)
        out.append(list(range(start, start + k))); start += k
    return out


def fp_lp(x0, n, p):
    """firstprivate(x) lastprivate(y), body: x += i; y = x."""
    last_y = None
    for t, its in enumerate(static_chunks(n, p)):
        x = x0
        for i in its:
            x += i; y = x
            if i == n - 1:
                last_y = y
    return x0, last_y


assert static_chunks(8, 4) == [[0, 1], [2, 3], [4, 5], [6, 7]]
assert static_chunks(10, 4) == [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9]]
assert fp_lp(10, 4, 2) == (10, 15)
assert fp_lp(5, 8, 4) == (5, 18)
assert 3 + 1 + 6 == 10

s = Script("OpenMP, part 1")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The fork-join model"],
    [2, "The parallel region"],
    [3, "Sharing a loop: omp for"],
    [4, "sections and single"],
    [5, "Who owns a variable: shared and private"],
    [6, "firstprivate and lastprivate"],
    [7, "A race, and a wrong fix"],
    [8, "Exam question"]]})
s.obj({"id": "fj", "type": "diagram", "region": "center", "layout": "layers", "direction": "down", "nodes": [
    {"id": "m0", "label": "master"},
    {"id": "t0", "label": "thread 0"}, {"id": "t1", "label": "thread 1"}, {"id": "t2", "label": "thread 2"}, {"id": "t3", "label": "thread 3"},
    {"id": "j", "label": "join"},
    {"id": "m1", "label": "master"}],
    "edges": [{"from": "m0", "to": "t0"}, {"from": "m0", "to": "t1"}, {"from": "m0", "to": "t2"}, {"from": "m0", "to": "t3"},
              {"from": "t0", "to": "j"}, {"from": "t1", "to": "j"}, {"from": "t2", "to": "j"}, {"from": "t3", "to": "j"},
              {"from": "j", "to": "m1"}]})
s.obj({"id": "hello", "type": "code", "region": "center", "language": "c", "lines": [
    "#include <omp.h>",
    "int main(void) {",
    "  #pragma omp parallel num_threads(4)",
    "  {",
    "    int id = omp_get_thread_num();",
    "    printf(\"hello from %d of %d\\n\", id, omp_get_num_threads());",
    "  }",
    "  return 0;",
    "}"]})
s.obj({"id": "par", "type": "table", "region": "center", "columns": ["the parallel region", ""], "rows": [
    ["#pragma omp parallel", "every thread in the team runs the whole block"],
    ["number of threads", "num_threads clause, else OMP_NUM_THREADS, else the core count"],
    ["output order", "any order: the four lines may come out shuffled"],
    ["compile", "gcc -fopenmp hello.c"]]})
s.obj({"id": "for", "type": "code", "region": "center", "language": "c", "lines": [
    "#pragma omp parallel num_threads(4)",
    "{",
    "  #pragma omp for",
    "  for (i = 0; i < 8; i++)",
    "    c[i] = a[i] + b[i];",
    "}",
    "// short form:  #pragma omp parallel for"]})
s.obj({"id": "fort", "type": "table", "region": "center", "columns": ["thread", "iterations, schedule(static)"], "rows": [
    [str(t), ", ".join(map(str, its))] for t, its in enumerate(static_chunks(8, 4))] + [
    ["rules", "iterations must be independent; the count must be known at entry"],
    ["at the end", "an implicit barrier, unless nowait"]]})
s.obj({"id": "sec", "type": "code", "region": "center", "language": "c", "lines": [
    "#pragma omp parallel",
    "{",
    "  #pragma omp sections",
    "  {",
    "    #pragma omp section",
    "    load_images();",
    "    #pragma omp section",
    "    load_sounds();",
    "  }",
    "  #pragma omp single",
    "  printf(\"loaded\\n\");",
    "}"]})
s.obj({"id": "sect", "type": "table", "region": "center", "columns": ["construct", "who runs it", "barrier at end"], "rows": [
    ["for", "the iterations are split across the team", "yes"],
    ["sections", "each section goes to one thread: different tasks", "yes"],
    ["single", "exactly one thread, any one", "yes"],
    ["master (masked)", "thread 0 only", "no"]]})
s.obj({"id": "sc", "type": "table", "region": "center", "columns": ["default rule", "scope"], "rows": [
    ["declared before the region", "shared: one copy, all threads see it"],
    ["declared inside the region", "private: one copy per thread"],
    ["the index of an omp for loop", "private"],
    ["clauses override", "shared(a), private(t), default(none)"],
    ["default(none)", "the compiler makes you scope every variable: catches mistakes"]]})
s.obj({"id": "cl", "type": "code", "region": "left", "language": "c", "lines": [
    "int n = 8, t;",
    "#pragma omp parallel for private(t)",
    "for (i = 0; i < n; i++) {",
    "  int k = 2 * i;",
    "  t = a[i] + k;",
    "  b[i] = t;",
    "}"]})
s.obj({"id": "clt", "type": "table", "region": "right", "columns": ["variable", "scope", "why"], "rows": [
    ["n", "shared", "declared before"],
    ["a, b", "shared", "each i touches its own element"],
    ["i", "private", "omp for index"],
    ["t", "private", "the clause"],
    ["k", "private", "declared inside"]]})
s.obj({"id": "fp", "type": "code", "region": "center", "language": "c", "lines": [
    "int t = 10, last;",
    "#pragma omp parallel for num_threads(2) schedule(static) \\",
    "        firstprivate(t) lastprivate(last)",
    "for (i = 0; i < 4; i++) { t = t + i; last = t; }",
    "printf(\"%d %d\\n\", t, last);"]})
s.obj({"id": "fpt", "type": "table", "region": "center", "columns": ["", "thread 0: i = 0, 1", "thread 1: i = 2, 3"], "rows": [
    ["private t starts at", "10 (firstprivate copies it in)", "10"],
    ["after its iterations", "10, then 11", "12, then 15"],
    ["last iteration, i = 3", "", "last = 15"],
    ["after the loop", "t is still 10 · last = 15", ""]]})
s.obj({"id": "fpk", "type": "table", "region": "center", "columns": ["clause", "on entry", "on exit"], "rows": [
    ["private", "uninitialised", "discarded"],
    ["firstprivate", "copy of the original", "discarded"],
    ["lastprivate", "uninitialised", "value from the last iteration copied out"]]})
s.obj({"id": "race", "type": "code", "region": "center", "language": "c", "lines": [
    "int sum = 0;",
    "#pragma omp parallel for",
    "for (i = 0; i < 1000; i++)",
    "  sum += a[i];          // sum is shared: a race",
    "",
    "#pragma omp parallel for private(sum)",
    "for (i = 0; i < 1000; i++)",
    "  sum += a[i];          // each copy starts undefined, and is thrown away"]})
s.obj({"id": "racet", "type": "table", "region": "center", "columns": ["thread 0", "thread 1", "sum"], "rows": [
    ["load sum: 5", "", "5"],
    ["", "load sum: 5", "5"],
    ["add 3, store 8", "", "8"],
    ["", "add 4, store 9", "9: thread 0's update is lost"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "c", "lines": [
    "// a) what is printed?",
    "int x = 5, y = 0;",
    "#pragma omp parallel for num_threads(4) schedule(static) \\",
    "        firstprivate(x) lastprivate(y)",
    "for (i = 0; i < 8; i++) { x += i; y = x; }",
    "printf(\"%d %d\\n\", x, y);"]})
s.obj({"id": "q2", "type": "code", "region": "center", "language": "c", "lines": [
    "// b) how many A, B and C are printed?",
    "#pragma omp parallel num_threads(3)",
    "{",
    "  printf(\"A\");",
    "  #pragma omp single",
    "  printf(\"B\");",
    "  #pragma omp for",
    "  for (i = 0; i < 6; i++) printf(\"C\");",
    "}"]})
s.obj({"id": "f10", "type": "table", "region": "center", "columns": ["thread", "10 iterations, 4 threads, schedule(static)"], "rows": [
    [str(k), ", ".join(map(str, its))] for k, its in enumerate(static_chunks(10, 4))]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part a", "answer"], "rows": [
    ["iterations of thread 3", "6 and 7: the last ones"],
    ["thread 3's private x", "starts 5, then 11, then 18"],
    ["y, copied out from i = 7", "18"],
    ["x after the loop", "5: firstprivate never copies back"],
    ["printed", "5 18"]]})
s.obj({"id": "qb", "type": "table", "region": "center", "columns": ["part b", "count", "why"], "rows": [
    ["A", "3", "every thread runs the region"],
    ["B", "1", "single: one thread"],
    ["C", "6", "omp for splits the 6 iterations; it does not repeat them"],
    ["total", "10", ""]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("We have seen the hardware: cores, caches, coherence. Now the software that uses it. OpenMP is the standard way to parallelise C, C++ and Fortran on a shared-memory machine, with a few compiler directives.", [s.head("OpenMP, part 1")])
s.step("Here are the eight stages.", show("stages"))
s.step("The fork-join model, the parallel region, sharing a loop, and sections and single.", [hl("stages[0..=3]")])
s.step("Then the part students most often get wrong: who owns each variable. Shared, private, firstprivate, lastprivate, a race, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- fork-join
s.scene("fj")
s.step("Stage 1: an OpenMP program starts as one thread, the master, running serial code.", [s.head("Stage 1 of 8: fork-join")] + hide("stages") + show("fj") + [hl("fj.m0")])
s.step("At a parallel region it forks: a team of threads is created, and the master becomes thread 0 of the team.", [hl("fj.t0"), hl("fj.t1", 0.15), hl("fj.t2", 0.3), hl("fj.t3", 0.45)])
s.step("At the end of the region, every thread waits at an implicit barrier. That is the join.", [hl("fj.j")])
s.step("Then only the master continues. A program may fork and join many times.", [hl("fj.m1"), s.take("fork at a region · join at its end")])

# ---------------------------------------------------------------- parallel
s.scene("par")
s.step("Stage 2: the parallel region. The directive pragma omp parallel, with four threads.", [s.head("Stage 2 of 8: the parallel region"), s.untake()] + hide("fj") + show("hello") + [ml("hello", 3, 3)])
s.step("Every thread runs the whole block. omp_get_thread_num gives each its number, 0 to 3, and omp_get_num_threads gives the team size.", [ml("hello", 5, 6)])
s.step("So the message is printed four times.", hide("hello") + show("par") + [hl("par[0]")])
s.step("How many threads? The num_threads clause if present; otherwise the environment variable OMP_NUM_THREADS; otherwise usually one per core.", [hl("par[1]")])
s.step("The four lines can appear in any order: the threads run at the same time.", [hl("par[2]")])
s.step("And the code is compiled with the fopenmp flag. Without it, the pragmas are ignored and the program is simply serial.", [hl("par[3]"), s.take("parallel: every thread runs the block")])

# ---------------------------------------------------------------- for
s.scene("for")
s.step("Stage 3: running the same code on every thread is rarely what we want. Usually we want to split a loop.", [s.head("Stage 3 of 8: omp for"), s.untake()] + hide("par") + show("for"))
s.step("pragma omp for, inside a parallel region, divides the loop's iterations among the team. No iteration runs twice.", [ml("for", 3, 5)])
s.step("Parallel and for are so often used together that they combine into one directive: pragma omp parallel for.", [ml("for", 7, 7)])
s.step("With a static schedule, eight iterations and four threads, each thread gets a contiguous block of two.", hide("for") + show("fort") + [hl("fort[0..=3]")])
s.step("If the count does not divide evenly, the first threads get one extra. Ten iterations on four threads: blocks of 3, 3, 2 and 2.", hide("fort") + show("f10") + [hl("f10[0..=1]"), hl("f10[2..=3]", 0.5)])
s.step("Two rules. The iterations must be independent, and the loop count must be known when the loop starts: no break.", hide("f10") + show("fort") + [hl("fort[4]")])
s.step("And the loop ends with an implicit barrier. A nowait clause removes it, when the next work does not depend on this loop.", [hl("fort[5]"), s.take("omp for splits iterations, never repeats them")])

# ---------------------------------------------------------------- sections, single
s.scene("sec")
s.step("Stage 4: not all parallelism is a loop. Sections run different pieces of code at the same time.", [s.head("Stage 4 of 8: sections and single"), s.untake()] + hide("fort") + show("sec") + [ml("sec", 3, 9)])
s.step("Each section goes to one thread. Here one thread loads images while another loads sounds.", [ml("sec", 5, 8)])
s.step("Single: exactly one thread, whichever arrives first, runs the block. The others wait at its end.", [ml("sec", 10, 11)])
s.step("Comparing them. For splits iterations; sections hand out different tasks; single picks one thread. All three end with a barrier.", hide("sec") + show("sect") + [hl("sect[0..=2]")])
s.step("Master, renamed masked in newer versions, is like single, but always thread 0, and with no barrier at all.", [hl("sect[3]"), s.take("for: split · sections: different work · single: one thread")])

# ---------------------------------------------------------------- scoping
s.scene("scope")
s.step("Stage 5: the most important question in OpenMP. For each variable, is there one copy, or one per thread?", [s.head("Stage 5 of 8: shared and private"), s.untake()] + hide("sect") + show("sc"))
s.step("A variable declared before the region is shared by default: one copy, which every thread reads and writes.", [hl("sc[0]")])
s.step("A variable declared inside the region is private: each thread has its own.", [hl("sc[1]")])
s.step("The index of an omp for loop is made private automatically. Otherwise the threads would fight over i.", [hl("sc[2]")])
s.step("Clauses override the defaults: shared, private, and default.", [hl("sc[3]")])
s.step("default none is the safe habit. The compiler then refuses any variable whose scope you did not state.", [hl("sc[4]"), s.take("before the region: shared · inside: private")])
s.step("Try it on this loop. Classify n, a, b, i, t and k.", [s.untake()] + hide("sc") + show("cl") + [ml("cl", 1, 7)])
s.step("n, a and b were declared before the region: shared. Sharing the arrays is safe, because each iteration touches its own element.", show("clt") + [hl("clt[0..=1]")])
s.step("i is the loop index, so it is private. t is private because of the clause. Without it, t would be shared, and threads would overwrite each other's t between two lines.", [hl("clt[2..=3]")])
s.step("And k is declared inside the loop body: private automatically.", [hl("clt[4]"), s.take("shared arrays are fine · shared temporaries are not")])

# ---------------------------------------------------------------- firstprivate, lastprivate
s.scene("fp")
s.step("Stage 6: a private variable has a weakness. It starts uninitialised, and it vanishes at the end. Two clauses fix that.", [s.head("Stage 6 of 8: firstprivate and lastprivate"), s.untake()] + hide("cl", "clt") + show("fpk") + [hl("fpk[0]")])
s.step("firstprivate initialises each thread's copy from the original value.", [hl("fpk[1]")])
s.step("lastprivate copies out the value from the sequentially last iteration.", [hl("fpk[2]")])
s.step("An example: t starts at 10. Two threads, four iterations; each adds i to t and stores it in last.", hide("fpk") + show("fp") + [ml("fp", 1, 4)])
s.step("Both private copies of t start at 10, thanks to firstprivate.", hide("fp") + show("fpt") + [hl("fpt[0]")])
s.step("Thread 0 runs i equal to 0 and 1: t becomes 10, then 11. Thread 1 runs 2 and 3: 12, then 15.", [hl("fpt[1]")])
s.step("Iteration 3 is the last, so last gets thread 1's value, 15.", [hl("fpt[2]")])
s.step("And after the loop, the original t is still 10: firstprivate copies in, never out. The program prints 10 15.", [hl("fpt[3]"), s.take("firstprivate: copy in · lastprivate: copy out")])

# ---------------------------------------------------------------- race
s.scene("race")
s.step("Stage 7: the classic bug. Sum an array in parallel, with sum shared.", [s.head("Stage 7 of 8: a race, and a wrong fix"), s.untake()] + hide("fpt") + show("race") + [ml("race", 1, 4)])
s.step("sum plus equals a of i is three steps: load, add, store. Two threads can interleave them.", hide("race") + show("racet") + [hl("racet[0..=1]")])
s.step("Both load 5. One stores 8, the other stores 9. One update is lost, and the answer changes from run to run.", [hl("racet[2..=3]")])
s.step("A tempting fix: make sum private. Now each thread adds into its own copy, which starts undefined and is thrown away at the end. The shared sum stays 0.", hide("racet") + show("race") + [ml("race", 6, 8)])
s.step("The right fixes are a critical section, an atomic, or best of all a reduction. They are the subject of the next video.", [s.take("shared accumulator: a race · private: lost result")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question in two parts.", [s.head("Exam question"), s.untake()] + hide("race") + show("q"))
s.step("Part a: x starts at 5, y at 0. Four threads, static schedule, eight iterations, x firstprivate and y lastprivate. What is printed? Pause and work it out.", [ml("q", 2, 6)])
s.step("With a static schedule, thread 3 gets iterations 6 and 7, the last two.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Its private x starts at 5. Adding 6 gives 11, adding 7 gives 18.", [hl("qa[1]")])
s.step("y is lastprivate, so it takes the value from iteration 7: 18.", [hl("qa[2]")])
s.step("And x is printed from the original variable, which firstprivate never changes: 5. The output is 5 18.", [hl("qa[3]"), mk("qa[4]", 0.5)])
s.step("Part b: three threads. How many A's, B's and C's are printed? Pause and work it out.", hide("qa") + show("q2") + [ml("q2", 2, 9)])
s.step("A is printed by every thread: 3 times.", hide("q2") + show("qb") + [hl("qb[0]")])
s.step("B is inside single: once.", [hl("qb[1]")])
s.step("C is inside omp for, which splits the six iterations among the threads: 6 times, not 18. Ten characters in all.", [hl("qb[2]"), mk("qb[3]", 0.5)])
s.step("The usual slip: thinking omp for repeats the loop on every thread. That is what a plain for inside a parallel region would do.", [s.take("omp for divides · a plain for repeats")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Fork-join: a team at each parallel region. omp for splits a loop; sections run different tasks; single runs once.", [hl("stages[0..=3]")])
s.step("Variables before the region are shared, inside it private. firstprivate copies in, lastprivate copies out. And a shared accumulator is a race.", [hl("stages[4..=6]")])
s.step("Next video: OpenMP, part 2. Loop schedules, synchronization, reductions, and the runtime routines.", [mk("stages[0..=7]"), s.take("Next: OpenMP, part 2")])

s.save("/home/claude/playlist/m3/m3v17.json")

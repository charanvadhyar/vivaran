"""Module 3, video 18: OpenMP part 2 - schedules, synchronization, reduction, runtime routines."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from sched_omp import run_static, run_greedy, guided_sizes, chunks_static

COST = [16 - i for i in range(16)]       # iteration i costs 16 - i: a triangular loop
assert sum(COST) == 136 and 136 / 4 == 34
S0 = run_static(COST, 4); S1 = run_static(COST, 4, 1)
D1 = run_greedy(COST, 4, [1] * 16); GS = guided_sizes(16, 4); G = run_greedy(COST, 4, GS)
assert S0[0] == [58, 42, 26, 10] and max(S0[0]) == 58
assert S1[0] == [40, 36, 32, 28] and max(S1[0]) == 40
assert D1[2] == 34 and D1[0] == [34, 34, 34, 34]
assert GS == [4, 3, 3, 2, 1, 1, 1, 1] and G[2] == 58
EXC = chunks_static(10, 3, 2)
assert [(t, c) for t, c in EXC] == [(0, [0, 1]), (1, [2, 3]), (2, [4, 5]), (0, [6, 7]), (1, [8, 9])]
assert guided_sizes(20, 3) == [7, 5, 3, 2, 1, 1, 1]
assert 10 + sum(range(1, 9)) == 46

s = Script("OpenMP, part 2")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why the schedule matters"],
    [2, "static, with and without a chunk"],
    [3, "dynamic and guided"],
    [4, "The four schedules on one loop"],
    [5, "critical and atomic"],
    [6, "barrier and nowait"],
    [7, "reduction"],
    [8, "Runtime routines and environment variables"],
    [9, "Exam question"]]})
s.obj({"id": "tri", "type": "code", "region": "center", "language": "c", "lines": [
    "#pragma omp parallel for num_threads(4) schedule(...)",
    "for (i = 0; i < 16; i++)",
    "  for (j = i; j < 16; j++)     // iteration i does 16 - i units of work",
    "    work(i, j);",
    "// total 136 units: ideal is 136 / 4 = 34 per thread"]})
s.obj({"id": "st", "type": "table", "region": "center", "columns": ["schedule(static)", "iterations", "work"], "rows": [
    [f"thread {t}", ", ".join(map(str, S0[1][t])), str(S0[0][t])] for t in range(4)] + [
    ["finish", "", "58: thread 3 waits 48 units"]]})
s.obj({"id": "st1", "type": "table", "region": "center", "columns": ["schedule(static, 1)", "iterations", "work"], "rows": [
    [f"thread {t}", ", ".join(map(str, S1[1][t])), str(S1[0][t])] for t in range(4)] + [
    ["finish", "", "40"]]})
s.obj({"id": "dg", "type": "table", "region": "center", "columns": ["schedule", "how chunks are handed out", "cost"], "rows": [
    ["static", "fixed in advance", "none"],
    ["dynamic, c", "an idle thread grabs the next c (default 1)", "a grab per chunk"],
    ["guided, c", "chunk ≈ remaining / threads, at least c", "fewer grabs"],
    ["guided: 16, 4 threads", "4, 3, 3, 2, 1, 1, 1, 1", ""]]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["schedule", "work per thread", "finish", "chunks grabbed"], "rows": [
    ["static", "58, 42, 26, 10", "58", "0"],
    ["static, 1", "40, 36, 32, 28", "40", "0"],
    ["dynamic, 1", "34, 34, 34, 34", "34", "16"],
    ["guided", "58, " + ", ".join(map(str, G[0][1:])), "58", str(len(GS))]]})
s.obj({"id": "cr", "type": "code", "region": "center", "language": "c", "lines": [
    "#pragma omp parallel for",
    "for (i = 0; i < n; i++) {",
    "  #pragma omp critical",
    "  { if (a[i] > best) best = a[i]; }   // any block, one thread at a time",
    "}",
    "",
    "#pragma omp parallel for",
    "for (i = 0; i < n; i++) {",
    "  #pragma omp atomic",
    "  count += (a[i] > 0);               // one update of one variable",
    "}"]})
s.obj({"id": "crt", "type": "table", "region": "center", "columns": ["", "critical", "atomic"], "rows": [
    ["protects", "any block of code", "one simple update: x += e, x++, x = x op e"],
    ["how", "a lock: one thread inside at a time", "a hardware atomic instruction"],
    ["cost", "high: every thread queues", "lower: one atomic memory operation"]]})
s.obj({"id": "br", "type": "code", "region": "center", "language": "c", "lines": [
    "#pragma omp parallel",
    "{",
    "  #pragma omp for nowait",
    "  for (i = 0; i < n; i++) a[i] = f(i);",
    "  #pragma omp for nowait",
    "  for (i = 0; i < n; i++) b[i] = g(i);    // independent of a: nowait is safe",
    "  #pragma omp barrier",
    "  #pragma omp for",
    "  for (i = 0; i < n; i++) c[i] = a[i] + b[n - 1 - i];  // needs all of a and b",
    "}"]})
s.obj({"id": "rd", "type": "code", "region": "center", "language": "c", "lines": [
    "int sum = 0;",
    "#pragma omp parallel for reduction(+:sum)",
    "for (i = 0; i < 1000; i++)",
    "  sum += a[i];"]})
s.obj({"id": "rdt", "type": "table", "region": "center", "columns": ["reduction(op: var)", ""], "rows": [
    ["1. each thread", "gets a private copy, set to the identity of op"],
    ["2. inside the loop", "each thread updates only its own copy: no race, no lock"],
    ["3. at the end", "the copies are combined with op, and with the original value"],
    ["identities", "+ and |: 0 · *: 1 · &: all ones · max: smallest value · min: largest"]]})
s.obj({"id": "rt", "type": "table", "region": "center", "columns": ["runtime routine", "returns or does"], "rows": [
    ["omp_get_thread_num()", "this thread's number, 0 to team size − 1"],
    ["omp_get_num_threads()", "the team size (1 outside a parallel region)"],
    ["omp_set_num_threads(n)", "team size for later regions"],
    ["omp_get_max_threads()", "the team size the next region would get"],
    ["omp_get_num_procs()", "processors available"],
    ["omp_in_parallel()", "nonzero inside an active parallel region"],
    ["omp_get_wtime()", "wall-clock seconds: time a region with two calls"]]})
s.obj({"id": "ev", "type": "table", "region": "center", "columns": ["environment variable", "sets"], "rows": [
    ["OMP_NUM_THREADS=8", "the default team size"],
    ["OMP_SCHEDULE=\"dynamic,4\"", "the schedule for loops with schedule(runtime)"],
    ["OMP_DYNAMIC=true", "lets the runtime choose fewer threads"],
    ["OMP_PROC_BIND, OMP_PLACES", "pin threads to cores"],
    ["precedence", "clause > routine > variable > default"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "c", "lines": [
    "// a) 10 iterations, 3 threads, schedule(static, 2): which thread runs which?",
    "// b) 20 iterations, 3 threads, schedule(guided): the chunk sizes?",
    "// c) what is printed?",
    "int s = 10;",
    "#pragma omp parallel for num_threads(4) reduction(+:s)",
    "for (i = 1; i <= 8; i++) s += i;",
    "printf(\"%d\\n\", s);"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["a) chunk", "iterations", "thread"], "rows": [
    [str(k + 1), f"{c[0]}, {c[1]}", str(t)] for k, (t, c) in enumerate(EXC)] + [
    ["so", "thread 0: 0, 1, 6, 7 · thread 1: 2, 3, 8, 9 · thread 2: 4, 5", ""]]})
s.obj({"id": "qb", "type": "table", "region": "center", "columns": ["b) remaining", "chunk = ⌈remaining / 3⌉"], "rows": [
    ["20", "7"], ["13", "5"], ["8", "3"], ["5", "2"], ["3, 2, 1", "1, 1, 1"], ["sizes", "7, 5, 3, 2, 1, 1, 1: total 20"]]})
s.obj({"id": "qc", "type": "math", "region": "center", "lines": [
    "\"c) private copies start at\" 0; quad \"together they add\" 1 + 2 + dots + 8 = 36",
    "s = 10 + 36 = 46"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Part 1 split loops and scoped variables. Part 2 makes the split fair, makes shared updates safe, and controls the runtime: loop schedules, synchronization, reductions, and the runtime routines and environment variables.", [s.head("OpenMP, part 2")])
s.step("Here are the nine stages.", show("stages"))
s.step("Why the schedule matters, static, dynamic and guided, and all four compared on one loop.", [hl("stages[0..=3]")])
s.step("Then critical, atomic, barrier, reduction, the runtime routines, and an exam question.", [hl("stages[4..=8]")])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: a loop where iterations are not equal. Iteration i runs the inner loop from i to 16, so it does 16 minus i units of work.", [s.head("Stage 1 of 9: why the schedule matters")] + hide("stages") + show("tri") + [ml("tri", 2, 4)])
s.step("That is 136 units in total. With four threads, the ideal is 34 each.", [ml("tri", 5, 5)])
s.step("The loop finishes only when the slowest thread finishes. So the question is: how evenly does the schedule spread the work?", [s.take("the slowest thread sets the time")])

# ---------------------------------------------------------------- static
s.scene("static")
s.step("Stage 2: schedule static, with no chunk size. Each thread gets one contiguous block of 4.", [s.head("Stage 2 of 9: static"), s.untake()] + hide("tri") + show("st") + [hl("st[0..=3]")])
s.step("Thread 0 gets the four heaviest iterations: 58 units. Thread 3 gets the lightest: 10.", [hl("st[0]"), hl("st[3]", 0.4)])
s.step("So the loop takes 58, and thread 3 sits idle for 48 of them.", [hl("st[4]")])
s.step("Now static with a chunk of 1. Chunks are dealt round-robin, like cards: thread 0 gets 0, 4, 8, 12.", hide("st") + show("st1") + [hl("st1[0]")])
s.step("Each thread now gets a mix of heavy and light iterations. 40, 36, 32, 28. The loop takes 40.", [hl("st1[0..=3]")])
s.step("Static costs nothing at run time: every thread knows its iterations before the loop starts.", [hl("st1[4]"), s.take("static: fixed in advance · a chunk deals round-robin")])

# ---------------------------------------------------------------- dynamic, guided
s.scene("dyn")
s.step("Stage 3: when we cannot predict the work, hand it out while the loop runs.", [s.head("Stage 3 of 9: dynamic and guided"), s.untake()] + hide("st1") + show("dg") + [hl("dg[0]")])
s.step("Dynamic: a thread that finishes a chunk grabs the next one. The default chunk is 1 iteration. Each grab costs a little synchronization.", [hl("dg[1]")])
s.step("Guided: also on demand, but chunks start big and shrink. Each chunk is about the remaining iterations divided by the number of threads, never smaller than c. Fewer grabs than dynamic.", [hl("dg[2]")])
s.step("For 16 iterations on 4 threads: 4, then 3, 3, 2, and then 1 at a time.", [hl("dg[3]"), s.take("dynamic: grab as you go · guided: big chunks first")])

# ---------------------------------------------------------------- compare
s.scene("cmp")
s.step("Stage 4: all four on our triangular loop.", [s.head("Stage 4 of 9: the four schedules compared"), s.untake()] + hide("dg") + show("cmp"))
s.step("Static: 58. Static with chunk 1: 40.", [hl("cmp[0..=1]")])
s.step("Dynamic with chunk 1: a thread that drew a heavy iteration simply grabs fewer. All four end at exactly 34, the ideal. The price is 16 grabs.", [hl("cmp[2]")])
s.step("Guided does badly here: its first, biggest chunk is iterations 0 to 3, the heaviest ones. One thread gets 58 units at once.", [hl("cmp[3]")])
s.step("So guided suits loops where the work is uneven but not heaviest at the start. There is no universally best schedule; measure.", [mk("cmp[2]"), s.take("uneven work: dynamic · even work: static")])

# ---------------------------------------------------------------- critical, atomic
s.scene("crit")
s.step("Stage 5: synchronization. Critical: only one thread at a time may run the block. Here it protects a compare-and-update of best.", [s.head("Stage 5 of 9: critical and atomic"), s.untake()] + hide("cmp") + show("cr") + [ml("cr", 3, 4)])
s.step("Atomic: one simple update of one memory location, such as count plus equals something.", [ml("cr", 9, 10)])
s.step("Critical protects any block, using a lock. Atomic allows only a single update statement.", hide("cr") + show("crt") + [hl("crt[0]")])
s.step("Atomic is done with a hardware atomic instruction, so it is usually much cheaper than a lock.", [hl("crt[1]")])
s.step("But both still serialise every update. In a loop of a million iterations, that is a million turns at the lock. Use them for rare updates.", [hl("crt[2]"), s.take("critical: any block · atomic: one update")])

# ---------------------------------------------------------------- barrier
s.scene("barrier")
s.step("Stage 6: a barrier makes every thread wait until all have arrived. For, sections and single already end with one.", [s.head("Stage 6 of 9: barrier and nowait"), s.untake()] + hide("crt") + show("br"))
s.step("Here the first two loops are independent. nowait lets a thread finish its part of a and go straight on to b.", [ml("br", 3, 6)])
s.step("But the third loop reads every element of a and b, including ones other threads wrote. So an explicit barrier is needed first.", [ml("br", 7, 9)])
s.step("The rule: drop a barrier only when the next work cannot read what the previous work wrote.", [s.take("nowait only when the next work is independent")])

# ---------------------------------------------------------------- reduction
s.scene("red")
s.step("Stage 7: back to our racing sum. The right fix is one clause: reduction, plus, colon, sum.", [s.head("Stage 7 of 9: reduction"), s.untake()] + hide("br") + show("rd") + [ml("rd", 2, 2)])
s.step("Each thread gets a private copy of sum, set to the identity of the operator: zero for plus.", hide("rd") + show("rdt") + [hl("rdt[0]")])
s.step("In the loop, each thread adds only into its own copy. No race, and no lock.", [hl("rdt[1]")])
s.step("At the end, the copies are combined, once, together with the original value of sum.", [hl("rdt[2]")])
s.step("The identities: zero for plus and or; one for times; all ones for and; for max, the smallest possible value, and for min, the largest.", [hl("rdt[3]"), s.take("reduction: private partial results, combined once")])

# ---------------------------------------------------------------- runtime
s.scene("rt")
s.step("Stage 8: the runtime library. We have met the first two: this thread's number, and the team size.", [s.head("Stage 8 of 9: runtime routines"), s.untake()] + hide("rdt") + show("rt") + [hl("rt[0..=1]")])
s.step("omp_set_num_threads sets the team size for later regions, and omp_get_max_threads tells you what the next region would get.", [hl("rt[2..=3]")])
s.step("omp_get_num_procs counts the processors, and omp_in_parallel tells code whether it is running inside a region.", [hl("rt[4..=5]")])
s.step("And omp_get_wtime returns wall-clock time. Call it before and after a region, subtract, and you have measured your speedup.", [hl("rt[6]")])
s.step("Environment variables set defaults without recompiling. OMP_NUM_THREADS sets the team size.", hide("rt") + show("ev") + [hl("ev[0]")])
s.step("OMP_SCHEDULE sets the schedule of any loop written with schedule runtime. So you can try static, dynamic and guided without rebuilding.", [hl("ev[1]")])
s.step("OMP_DYNAMIC lets the runtime use fewer threads, and OMP_PROC_BIND and OMP_PLACES pin threads to cores.", [hl("ev[2..=3]")])
s.step("When they disagree: the num_threads clause wins, then omp_set_num_threads, then the environment variable, then the default.", [hl("ev[4]"), s.take("clause > routine > environment > default")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question in three parts.", [s.head("Exam question"), s.untake()] + hide("ev") + show("q"))
s.step("Part a: 10 iterations, 3 threads, static with chunk 2. Part b: 20 iterations, 3 threads, guided: the chunk sizes. Part c: what does the reduction print? Pause and work it out.", [ml("q", 1, 7)])
s.step("Part a. Chunks of 2 are dealt round-robin: 0 and 1 to thread 0, 2 and 3 to thread 1, 4 and 5 to thread 2.", hide("q") + show("qa") + [hl("qa[0..=2]")])
s.step("Then back to thread 0 for 6 and 7, and thread 1 for 8 and 9. Thread 2 gets only one chunk.", [hl("qa[3..=4]"), mk("qa[5]", 0.6)])
s.step("Part b. Each chunk is the remaining count over 3, rounded up. 20 over 3 gives 7, leaving 13. Then 5, leaving 8.", hide("qa") + show("qb") + [hl("qb[0..=1]")])
s.step("Then 3, then 2, then three chunks of 1. Sizes 7, 5, 3, 2, 1, 1, 1: twenty in all.", [hl("qb[2..=4]"), mk("qb[5]", 0.6)])
s.step("Part c. Each private copy starts at zero, and together they add 1 to 8, which is 36.", hide("qb") + show("qc") + [hl("qc[0]")])
s.step("And the original value, 10, is combined in at the end. The program prints 46, not 36.", [rv("qc[1]"), mk("qc[1]")])
s.step("The usual slip: forgetting that a reduction includes the variable's value from before the loop.", [s.take("reduction keeps the original value")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qc") + show("stages"))
s.step("Static deals iterations in advance; dynamic and guided hand them out as threads become free. On uneven work, dynamic balances best.", [hl("stages[0..=3]")])
s.step("Critical and atomic serialise updates; barriers order phases; a reduction gives each thread its own partial result.", [hl("stages[4..=6]")])
s.step("And the runtime routines and environment variables control the team without changing the code. That completes Module 3: from instruction-level parallelism inside one core, to threads across many.", [hl("stages[7..=8]"), mk("stages[0..=8]", 0.5), s.take("Module 3 complete")])

s.save("/home/claude/playlist/m3/m3v18.json")

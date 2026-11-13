"""Module 4, video 1: introduction to data-level parallelism."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

# DAXPY on 64 elements (H&P): MIPS loop body 9 instructions, 2 setup; VMIPS 6 instructions
assert 9 * 64 + 2 == 578 and round(578 / 6) == 96
# exam: Z = X + Y on 64 elements: scalar body L.D, L.D, ADD.D, S.D, 3 pointer bumps... use the given 8-instruction body
assert 8 * 64 + 2 == 514 and 4 == len(["LV", "LV", "ADDVV.D", "SV"]) and round(514 / 4, 1) == 128.5

s = Script("Data-level parallelism")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Three kinds of parallelism"],
    [2, "Data-level parallelism"],
    [3, "Which loops have it"],
    [4, "DAXPY: scalar against vector"],
    [5, "Why one instruction for many data is cheap"],
    [6, "How much it helps a whole program"],
    [7, "Three ways hardware exploits DLP"],
    [8, "Exam question"]]})
s.obj({"id": "three", "type": "table", "region": "center", "columns": ["kind", "the parallel unit", "found by", "seen in"], "rows": [
    ["ILP", "independent instructions", "hardware or compiler", "Modules 1, 3"],
    ["TLP", "independent threads", "the programmer", "Module 3"],
    ["DLP", "one operation, many data items", "compiler, from loops", "this module"]]})
s.obj({"id": "dlp", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 64; i++)",
    "    Y[i] = a * X[i] + Y[i];      // DAXPY: double a times X plus Y",
    "",
    "// 64 multiplies and 64 adds, all independent",
    "// one instruction could say: do this to all 64"]})
s.obj({"id": "vec", "type": "table", "region": "center", "columns": ["loop", "vectorizable?", "why"], "rows": [
    ["C[i] = A[i] + B[i]", "yes", "every iteration independent"],
    ["Y[i] = a * X[i] + Y[i]", "yes", "each i touches only its own elements"],
    ["A[i] = A[i-1] + B[i]", "no", "iteration i needs the result of i − 1: a loop-carried dependence"],
    ["if (A[i] > 0) B[i] = A[i]", "yes, with a mask", "only some elements are written"],
    ["sum += A[i]", "yes, as a reduction", "partial sums in parallel, then combine"]]})
s.obj({"id": "sc", "type": "code", "region": "center", "language": "asm", "lines": [
    "      L.D    F0,a",
    "      DADDIU R4,Rx,#512",
    "Loop: L.D    F2,0(Rx)",
    "      MUL.D  F2,F2,F0",
    "      L.D    F4,0(Ry)",
    "      ADD.D  F4,F4,F2",
    "      S.D    F4,0(Ry)",
    "      DADDIU Rx,Rx,#8",
    "      DADDIU Ry,Ry,#8",
    "      DSUBU  R20,R4,Rx",
    "      BNEZ   R20,Loop"]})
s.obj({"id": "vc", "type": "code", "region": "center", "language": "asm", "lines": [
    "L.D      F0,a        ; the scalar a",
    "LV       V1,Rx       ; load 64 X values",
    "MULVS.D  V2,V1,F0    ; 64 multiplies",
    "LV       V3,Ry       ; load 64 Y values",
    "ADDVV.D  V4,V2,V3    ; 64 adds",
    "SV       V4,Ry       ; store 64 results"]})
s.obj({"id": "cnt", "type": "math", "region": "center", "lines": [
    "\"scalar:\" quad 2 + 9 times 64 = 578 \"instructions\"",
    "\"vector:\" quad 6 \"instructions\" quad => quad 578 / 6 approx 96 \"times fewer\"",
    "\"stalls: scalar ADD.D waits for MUL.D 64 times · vector: once per vector\""]})
s.obj({"id": "eff", "type": "table", "region": "center", "columns": ["one instruction, 64 operations", "saves"], "rows": [
    ["fetch and decode", "once instead of 64 times: less energy, less bandwidth"],
    ["hazard checks", "elements are independent by definition: no checks between them"],
    ["memory access", "a known pattern: fetched in bulk, latency paid once"],
    ["loop overhead", "no branches or pointer bumps per element"]]})
s.obj({"id": "am", "type": "math", "region": "center", "lines": [
    "\"vectorizable fraction\" f, quad \"vector speedup\" v: quad S = 1 / ((1 - f) + f / v)",
    "f = 0.7, v = 10: quad S = 1 / (0.3 + 0.07) = 1 / 0.37 approx 2.70",
    "f = 0.9, v = 10: quad S = 1 / (0.1 + 0.09) = 1 / 0.19 approx 5.26",
    "\"the compiler's job: raise\" f \"· the hardware's job: raise\" v"]})
s.obj({"id": "hw", "type": "table", "region": "center", "columns": ["hardware", "idea", "examples"], "rows": [
    ["vector machines", "long vector registers, pipelined units", "Cray-1, NEC SX, RISC-V V"],
    ["SIMD extensions", "short fixed-width registers in a CPU", "MMX, SSE, AVX, Neon"],
    ["GPUs", "thousands of threads in lockstep groups", "NVIDIA, AMD"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "c", "lines": [
    "// a) which can be vectorized directly?",
    "(1) for (i = 0; i < n; i++) D[i] = A[i] * B[i] + C[i];",
    "(2) for (i = 1; i < n; i++) A[i] = A[i-1] * 2;",
    "(3) for (i = 0; i < n; i++) if (B[i] != 0) A[i] = A[i] / B[i];",
    "(4) for (i = 0; i < n; i++) A[i] = B[i+1] + B[i];",
    "// b) Z = X + Y, 64 elements: the scalar loop body has 8 instructions",
    "//    and 2 setup instructions. Count scalar and vector instructions.",
    "// c) 80% of the run vectorizes, 8 times faster: overall speedup?"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["loop", "vectorizable?", "why"], "rows": [
    ["(1)", "yes", "independent multiply-adds"],
    ["(2)", "no", "A[i] needs A[i-1]: loop-carried"],
    ["(3)", "yes, with a mask", "skip elements where B[i] is 0"],
    ["(4)", "yes", "reads B only, writes A only"]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"scalar:\" quad 2 + 8 times 64 = 514 \"instructions\"",
    "\"vector:\" quad \"LV, LV, ADDVV.D, SV\" = 4 \"instructions\" quad 514 / 4 approx 128 \"times fewer\"",
    "\"c)\" quad S = 1 / (0.2 + 0.8 / 8) = 1 / 0.3 approx 3.33"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Modules 1 and 3 found parallelism between instructions, and between threads. This module is about a third kind, the one that powers graphics cards and machine learning: doing the same operation on many data items at once.", [s.head("Data-level parallelism")])
s.step("Here are the eight stages.", show("stages"))
s.step("The three kinds of parallelism, what data-level parallelism is, and which loops have it.", [hl("stages[0..=2]")])
s.step("Then a scalar and a vector program side by side, why the vector one is so cheap, the effect on a whole program, the three hardware families, and an exam question.", [hl("stages[3..=7]")])

s.scene("three")
s.step("Stage 1: instruction-level parallelism finds independent instructions within one stream. The hardware finds a few at a time, as we saw with Tomasulo.", [s.head("Stage 1 of 8: three kinds")] + hide("stages") + show("three") + [hl("three[0]")])
s.step("Thread-level parallelism runs independent threads on separate cores, or on one core with multithreading. The programmer creates the threads.", [hl("three[1]")])
s.step("Data-level parallelism applies the same operation to many data items. It comes from loops over arrays: images, matrices, signals, neural network layers.", [hl("three[2]"), s.take("ILP: instructions · TLP: threads · DLP: data")])

s.scene("dlp")
s.step("Stage 2: the running example of this module, DAXPY. Y equals a times X plus Y, for 64 elements.", [s.head("Stage 2 of 8: data-level parallelism"), s.untake()] + hide("three") + show("dlp") + [ml("dlp", 1, 2)])
s.step("Every iteration does one multiply and one add, on its own elements. No iteration needs another's result.", [ml("dlp", 4, 4)])
s.step("So instead of 64 instructions that each say: multiply this one number, one instruction could say: multiply all 64. That is the whole idea.", [ml("dlp", 5, 5), s.take("one instruction, many data: SIMD")])

s.scene("which")
s.step("Stage 3: which loops have data-level parallelism? Adding two arrays: yes, every iteration is independent.", [s.head("Stage 3 of 8: which loops"), s.untake()] + hide("dlp") + show("vec") + [hl("vec[0]")])
s.step("DAXPY: yes. Each iteration reads and writes only its own elements.", [hl("vec[1]")])
s.step("A of i equals A of i minus 1 plus B of i: no. Each iteration needs the one before. That is a loop-carried dependence, and video 16 of this module is about finding them.", [hl("vec[2]")])
s.step("A loop with an if inside: yes, with a mask that switches off the elements where the condition is false.", [hl("vec[3]")])
s.step("And a sum: yes, as a reduction. Add in parallel into several partial sums, then combine them at the end.", [hl("vec[4]"), s.take("vectorizable: iterations independent, or a reduction")])

s.scene("daxpy")
s.step("Stage 4: DAXPY in scalar MIPS code. Two setup instructions, then a loop of nine.", [s.head("Stage 4 of 8: scalar against vector"), s.untake()] + hide("vec") + show("sc") + [ml("sc", 3, 11)])
s.step("Two loads, a multiply, an add, a store, two pointer bumps, a compare and a branch. Only two of the nine do arithmetic.", [ml("sc", 3, 7)])
s.step("Now the vector version, in VMIPS: the textbook's vector extension of MIPS, with 64-element vector registers. RISC-V's vector extension has the same instructions under other names, like vle, vfmul and vfadd.", hide("sc") + show("vc") + [ml("vc", 1, 6)])
s.step("Load the scalar a. Load 64 X values into vector register V1. Multiply all 64 by a.", [ml("vc", 1, 3)])
s.step("Load 64 Y values, add the two vectors, and store 64 results. Six instructions in all.", [ml("vc", 4, 6)])
s.step("Count them. The scalar loop runs nine instructions 64 times, plus two: 578. The vector code: 6. About 96 times fewer instructions.", hide("vc") + show("cnt") + [hl("cnt[0]"), rv("cnt[1]"), hl("cnt[1]", 0.4)])
s.step("And the stalls. In the scalar loop, every add must wait for its multiply: 64 waits. In the vector code the add waits for the multiply once per vector, not once per element.", [rv("cnt[2]"), hl("cnt[2]"), s.take("578 instructions → 6")])

s.scene("why")
s.step("Stage 5: why is one vector instruction so much cheaper than 64 scalar ones?", [s.head("Stage 5 of 8: why it is cheap"), s.untake()] + hide("cnt") + show("eff"))
s.step("The instruction is fetched and decoded once, not 64 times. That saves energy and instruction bandwidth.", [hl("eff[0]")])
s.step("The 64 operations are independent by definition, so the hardware needs no hazard checks between them.", [hl("eff[1]")])
s.step("Memory is accessed in a known pattern, so many elements can be fetched at once, and the latency is paid once per vector.", [hl("eff[2]")])
s.step("And the loop overhead, branches and pointer bumps, almost disappears.", [hl("eff[3]"), s.take("fewer instructions, fewer checks, bulk memory access")])

s.scene("amdahl")
s.step("Stage 6: how much faster does a whole program get? Amdahl's law again. If a fraction f of the run vectorizes, and that part runs v times faster, the speedup is one over one minus f, plus f over v.", [s.head("Stage 6 of 8: the whole program"), s.untake()] + hide("eff") + show("am") + [hl("am[0]")])
s.step("If 70 percent vectorizes and runs 10 times faster: 0.3 plus 0.07 is 0.37. The program runs only 2.7 times faster.", [rv("am[1]"), hl("am[1]")])
s.step("Raise the vectorizable part to 90 percent, with the same hardware: 0.1 plus 0.09 is 0.19. Now 5.26 times faster.", [rv("am[2]"), hl("am[2]")])
s.step("So the serial part dominates. The compiler's job is to vectorize as much of the program as it can; the hardware's job is to make the vector part fast. Both matter.", [rv("am[3]"), hl("am[3]"), s.take("the unvectorized part sets the limit")])

s.scene("hw")
s.step("Stage 7: three hardware families exploit this. Vector architectures: long vector registers feeding deeply pipelined units. Cray machines, NEC's SX line, and now RISC-V's vector extension.", [s.head("Stage 7 of 8: three families"), s.untake()] + hide("am") + show("hw") + [hl("hw[0]")])
s.step("SIMD extensions: short fixed-width registers added to ordinary processors. MMX, SSE and AVX on x86, Neon on ARM.", [hl("hw[1]")])
s.step("And GPUs: thousands of threads, run in lockstep groups. This module takes them in that order.", [hl("hw[2]"), s.take("vector · SIMD extensions · GPU")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("hw") + show("q"))
s.step("Part a: which of these four loops can be vectorized directly?", [ml("q", 1, 5)])
s.step("Part b: adding two 64-element vectors, with a scalar loop body of 8 instructions and 2 setup instructions. Count the scalar and the vector instructions. Part c: if 80 percent of a run vectorizes, 8 times faster, what is the overall speedup? Pause and work it out.", [ml("q", 6, 8)])
s.step("Loop 1: independent multiply-adds. Yes.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Loop 2: each A of i needs A of i minus 1. No.", [hl("qa[1]")])
s.step("Loop 3: yes, with a mask, skipping the elements where B is 0.", [hl("qa[2]")])
s.step("Loop 4 looks suspicious, with i plus 1. But it reads only B and writes only A, so no iteration depends on another. Yes.", [hl("qa[3]")])
s.step("Part b: scalar, 2 plus 8 times 64: 514 instructions. Vector: two loads, an add and a store: 4. About 128 times fewer.", hide("qa") + show("qb") + [hl("qb[0]"), rv("qb[1]"), hl("qb[1]", 0.4)])
s.step("Part c: 0.2 plus 0.8 over 8 is 0.3. One over 0.3: about 3.33 times faster, far from 8.", [rv("qb[2]"), hl("qb[2]")])
s.step("The usual slip: calling any loop with an i plus 1 or i minus 1 a dependence. Check what is written and what is read.", [s.take("a dependence needs one iteration to write what another reads")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Data-level parallelism is the same operation on many items, found in loops whose iterations are independent, or are reductions.", [hl("stages[0..=2]")])
s.step("One vector instruction replaces dozens of scalar ones: 578 became 6 for DAXPY. Amdahl's law limits the whole program. Vector machines, SIMD extensions and GPUs all exploit it.", [hl("stages[3..=6]")])
s.step("Next video: vector architecture. The registers, the instructions, and how VMIPS is built.", [mk("stages[0..=7]"), s.take("Next: vector architecture")])

s.save("/home/claude/playlist/m4/m4v1.json")

"""Module 1, video 9: beyond one instruction per cycle: superpipelined, superscalar, VLIW, and how they differ."""
import sys
sys.path.insert(0, ".")
from common import Script

K, N = 4, 6
ST = ["IF", "ID", "EX", "WB"]
scalar = K + N - 1
ss = K + (N - 2) / 2
sp = K + (N - 1) / 2
assert (scalar, ss, sp) == (9, 6, 6.5)
k, n = 4, 12
assert (k + n - 1, k + (n - 2) / 2, k + (n - 1) / 2, k + (n - 2) / 4) == (15, 9, 9.5, 6.5)
assert (round(15 / 9, 2), round(15 / 9.5, 2), round(15 / 6.5, 2)) == (1.67, 1.58, 2.31)
assert (5 + 19, 5 + 16 / 4, 5 + 19 / 4, 5 + 18 / 4) == (24, 9, 9.75, 9.5)
assert (round(24 / 9, 2), round(24 / 9.75, 2), round(24 / 9.5, 2)) == (2.67, 2.46, 2.53)
LANES = [f"I{i + 1}" for i in range(N)]

s = Script("Superscalar, superpipelined and VLIW processors")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The limit of a scalar pipeline: at most one instruction per cycle"],
    [2, "Superpipelined: a faster clock from more, shorter stages"],
    [3, "Superscalar: several pipelines, several instructions per cycle"],
    [4, "VLIW: the compiler packs operations into one long instruction"],
    [5, "Counting cycles for each"],
    [6, "All the differences in one table"],
    [7, "Exam question"]]})
s.obj({"id": "scal", "type": "timeline", "region": "center", "lanes": LANES, "end": 9, "unit": "base clock cycle", "now": 0, "blocks": []})
s.obj({"id": "spip", "type": "timeline", "region": "center", "lanes": LANES, "end": 9, "unit": "base clock cycle", "now": 0, "blocks": []})
s.obj({"id": "sscl", "type": "timeline", "region": "center", "lanes": LANES, "end": 9, "unit": "base clock cycle", "now": 0, "blocks": []})
s.obj({"id": "ssx", "type": "table", "region": "center", "columns": ["what a superscalar core must do every cycle"], "rows": [
    ["fetch and decode several instructions"],
    ["check them against each other for dependences, in hardware"],
    ["find a free functional unit for each"],
    ["issue the ones that are ready, maybe out of order"]]})
s.obj({"id": "vcode", "type": "code", "region": "left", "language": "c", "lines": [
    "a = b + c;", "d = e * f;", "x = load(p);", "store(q, y);", "g = a - d;", "if (g < 0) goto L;"]})
s.obj({"id": "vliw", "type": "table", "region": "center", "columns": ["word", "integer ALU", "multiply", "memory", "branch"], "rows": [
    ["1", "a = b + c", "d = e * f", "x = load(p)", "NOP"],
    ["2", "g = a − d", "NOP", "store(q, y)", "NOP"],
    ["3", "NOP", "NOP", "NOP", "if g < 0 goto L"]]})
s.obj({"id": "vx", "type": "table", "region": "center", "columns": ["VLIW", "consequence"], "rows": [
    ["the compiler schedules everything", "simple hardware: no dependence checking"],
    ["empty slots become NOPs", "larger code"],
    ["the slot layout is part of the instruction set", "a wider model needs recompiled code"],
    ["the compiler cannot know cache misses", "one stall freezes the whole word"]]})
s.obj({"id": "cnt", "type": "math", "region": "center", "lines": [
    "\"scalar\": quad k + N - 1",
    "\"superscalar, degree\" m: quad k + (N - m) / m",
    "\"superpipelined, degree\" n: quad k + (N - 1) / n",
    "\"both,\" (m, n): quad k + (N - m) / (m n)",
    "\"speedup limits as\" N -> infinity: quad m, quad n, quad m n"]})
s.obj({"id": "cntx", "type": "table", "region": "center", "columns": ["k = 4, N = 12", "base cycles", "speedup"], "rows": [
    ["scalar", "4 + 11 = 15", "1"],
    ["superscalar, m = 2", "", ""],
    ["superpipelined, n = 2", "", ""],
    ["both, m = 2, n = 2", "", ""]]})
s.obj({"id": "diff", "type": "table", "region": "center", "columns": ["", "superpipelined", "superscalar", "VLIW"], "rows": [
    ["idea", "more, shorter stages", "several parallel pipelines", "one long word, many operations"],
    ["issue", "1 per minor cycle", "m per cycle", "1 word per cycle"],
    ["clock", "faster", "same", "same"],
    ["who finds the parallelism", "nothing extra needed", "hardware, at run time", "compiler, ahead of time"],
    ["hardware", "more latches, tight timing", "complex: checks, scheduling", "simple"],
    ["weak spot", "latch overhead, long branch penalty", "power and area grow fast", "NOPs, code size, recompiling"],
    ["ideal CPI", "1 (in base cycles: 1 ÷ n)", "1 ÷ m", "1 ÷ slots"],
    ["examples", "MIPS R4000", "Intel Core, ARM Cortex-A", "Itanium, TI C6000 DSPs"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["A 5-stage pipeline runs 20 instructions. Find the cycles and speedup for:"], "rows": [
    ["a) the scalar pipeline"], ["b) a degree 4 superscalar"], ["c) a degree 4 superpipeline"], ["d) superscalar degree 2, superpipelined degree 2"],
    ["e) which one needs NOPs from the compiler, and why?"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 5 + 19 = 24",
    "\"b)\" quad 5 + (20 - 4) / 4 = 9, quad 24 / 9 approx 2.67",
    "\"c)\" quad 5 + (20 - 1) / 4 = 9.75, quad 24 / 9.75 approx 2.46",
    "\"d)\" quad 5 + (20 - 2) / 4 = 9.5, quad 24 / 9.5 approx 2.53",
    "\"e) VLIW: fixed slots the compiler cannot fill\""]})


def instr(t, i, start, w=1, delay=True):
    return [{"action": "add_block", "target": t, "id": f"{t}{i}{j}", "lane": LANES[i], "start": start + j * w, "end": start + (j + 1) * w,
             "label": st, **({"delay": round(min(0.8, j * 0.12), 2)} if delay else {})} for j, st in enumerate(ST)]


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("A pipeline overlaps instructions, but at best it still finishes one per cycle. Three designs go further: superpipelined, superscalar, and VLIW.", [s.head("Beyond one instruction per cycle")])
s.step("Here are the seven stages.", [{"action": "show", "target": "stages"}])
s.step("The scalar limit, then each of the three designs and how it works.", [{"action": "highlight", "target": "stages[0..=3]"}])
s.step("Then the cycle formulas for each, a table of every difference, and an exam question.", [{"action": "highlight", "target": "stages[4..=6]"}])

# ---------------------------------------------------------------- scalar
s.scene("scalar")
s.step("Stage 1: a scalar four-stage pipeline: IF, ID, EX and WB. Six instructions, one entering each cycle.", [s.head("Stage 1 of 7: the scalar limit"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "scal"}]
       + [b for i in range(N) for b in instr("scal", i, i, delay=False)])
s.step("They finish in k plus N minus 1, which is 4 plus 5: 9 cycles.", [{"action": "advance", "target": "scal", "to": 9}])
s.step("Once full, one instruction finishes per cycle. So the CPI can never go below 1, or the IPC above 1. This is called the Flynn bottleneck.", [s.take("scalar pipeline: CPI ≥ 1, at most one instruction per cycle")])
s.step("To beat it we can either make the cycles shorter, or start several instructions in each cycle.")

# ---------------------------------------------------------------- superpipelined
s.scene("superpipe")
s.step("Stage 2: superpipelining. Split every stage into two halves, each with its own latch. The clock can now tick twice as fast.", [s.head("Stage 2 of 7: superpipelined"), {"action": "hide", "target": "scal"}, s.untake(), {"action": "show", "target": "spip"}])
s.step("Measured in the original, base cycles, a new instruction now starts every half cycle.", [b for i in range(N) for b in instr("spip", i, i / 2, delay=False)])
s.step("Each instruction still takes 4 base cycles in total. But six of them finish in 4 plus 5 halves: 6.5 base cycles, instead of 9.", [{"action": "advance", "target": "spip", "to": 6.5}])
s.step("This is a superpipeline of degree 2. Degree n means each stage is split into n, and n instructions start per base cycle.", [s.take("superpipelined degree n: n minor cycles per base cycle")])
s.step("The cost: more latches, so latch overhead grows, as we saw last video. And with more stages, hazards cost more cycles, especially branches.")

# ---------------------------------------------------------------- superscalar
s.scene("superscalar")
s.step("Stage 3: superscalar. Keep the clock, but build two complete pipelines side by side. Two instructions are fetched and issued together.", [s.head("Stage 3 of 7: superscalar"), {"action": "hide", "target": "spip"}, s.untake(), {"action": "show", "target": "sscl"}])
s.step("I1 and I2 start in cycle 1, I3 and I4 in cycle 2, I5 and I6 in cycle 3.", [b for i in range(N) for b in instr("sscl", i, i // 2, delay=False)])
s.step("They finish in 6 cycles, against 9 for the scalar pipeline. Up to two instructions finish per cycle, so the ideal CPI is one half.", [{"action": "advance", "target": "sscl", "to": 6}])
s.step("This is superscalar of degree 2, or 2-way. The catch: hardware must decide, every cycle, which instructions can safely go together.", [{"action": "hide", "target": "sscl"}, {"action": "show", "target": "ssx"}])
s.step("It fetches and decodes several instructions, and checks them against each other for dependences.", [{"action": "highlight", "target": "ssx[0..=1]"}])
s.step("It finds a free functional unit for each, and issues the ready ones, often out of program order.", [{"action": "highlight", "target": "ssx[2..=3]"}])
s.step("If I2 needs I1's result, the pair cannot issue together, and one slot goes empty. This checking logic grows quickly with the width, so real cores stop at around 4 to 8.", [s.take("superscalar: hardware finds the parallelism at run time")])

# ---------------------------------------------------------------- VLIW
s.scene("vliw")
s.step("Stage 4: VLIW, very long instruction word. Move all that checking out of the hardware and into the compiler.", [s.head("Stage 4 of 7: VLIW"), {"action": "hide", "target": "ssx"}, s.untake(), {"action": "show", "target": "vcode"}])
s.step("Take these six statements. The add, the multiply and the load do not depend on each other. g needs a and d, and the branch needs g.", [{"action": "mark_lines", "target": "vcode", "from": 1, "to": 3}, {"action": "goto_line", "target": "vcode", "line": 5, "delay": 0.5}, {"action": "goto_line", "target": "vcode", "line": 6, "delay": 0.8}])
s.step("Each instruction word has fixed slots, one for each functional unit: here an integer ALU, a multiplier, a memory unit and a branch unit.", [{"action": "hide", "target": "vcode"}, {"action": "show", "target": "vliw"}, {"action": "highlight", "target": "vliw[0]"}])
s.step("The compiler finds that the add, the multiply and the load are independent, and packs them into word 1.", [{"action": "highlight", "target": "vliw[0]"}])
s.step("g needs a and d, so it must wait for word 2. The store can share that word.", [{"action": "highlight", "target": "vliw[1]"}])
s.step("The branch needs g, so it goes alone in word 3.", [{"action": "highlight", "target": "vliw[2]"}])
s.step("Every slot the compiler cannot fill holds a NOP: 6 of the 12 slots here are wasted.", [{"action": "mark", "target": "vliw[0][4]"}, {"action": "mark", "target": "vliw[1][2]", "delay": 0.2}, {"action": "mark", "target": "vliw[1][4]", "delay": 0.4}, {"action": "mark", "target": "vliw[2][1]", "delay": 0.6}, {"action": "mark", "target": "vliw[2][2]", "delay": 0.7}, {"action": "mark", "target": "vliw[2][3]", "delay": 0.8}])
s.step("So the hardware is simple, because it never checks for dependences. But there is a price.", [{"action": "hide", "target": "vliw"}, {"action": "show", "target": "vx"}, {"action": "highlight", "target": "vx[0]"}])
s.step("NOPs make the code larger. And because the slots are part of the instruction set, a wider model needs the program recompiled.", [{"action": "highlight", "target": "vx[1..=2]"}])
s.step("And the compiler cannot predict a cache miss, so when one operation waits, the whole word waits with it.", [{"action": "highlight", "target": "vx[3]"}, s.take("VLIW: the compiler finds the parallelism ahead of time")])

# ---------------------------------------------------------------- counting
s.scene("count")
s.step("Stage 5: cycle counts, measured in base cycles, for a k stage pipeline running N instructions.", [s.head("Stage 5 of 7: counting cycles"), {"action": "hide", "target": "vx"}, s.untake(), {"action": "show", "target": "cnt"}])
s.step("Superscalar of degree m: the first m finish after k cycles, and the other N minus m finish m per cycle. So k plus N minus m, over m.", [{"action": "reveal", "target": "cnt[1]"}, {"action": "highlight", "target": "cnt[1]"}])
s.step("Superpipelined of degree n: the first finishes after k base cycles, and the other N minus 1 finish n per base cycle. So k plus N minus 1, over n.", [{"action": "reveal", "target": "cnt[2]"}, {"action": "highlight", "target": "cnt[2]"}])
s.step("Both together: k plus N minus m, over m times n.", [{"action": "reveal", "target": "cnt[3]"}, {"action": "highlight", "target": "cnt[3]"}])
s.step("For very long programs, the speedups approach m, n, and m times n.", [{"action": "reveal", "target": "cnt[4]"}, {"action": "highlight", "target": "cnt[4]"}])
s.step("Check with k equal to 4 and N equal to 12. Scalar: 15 cycles.", [{"action": "hide", "target": "cnt"}, {"action": "show", "target": "cntx"}, {"action": "highlight", "target": "cntx[0]"}])
s.step("Superscalar, m equals 2: 4 plus 10 over 2, which is 9 cycles. Speedup 1.67.", [{"action": "highlight", "target": "cntx[1]"}, {"action": "set", "target": "cntx[1][1]", "value": "4 + 10 ÷ 2 = 9", "delay": 0.3}, {"action": "set", "target": "cntx[1][2]", "value": "1.67", "delay": 0.7}])
s.step("Superpipelined, n equals 2: 4 plus 11 over 2, which is 9.5. Speedup 1.58, slightly less, because only one instruction starts at a time.", [{"action": "highlight", "target": "cntx[2]"}, {"action": "set", "target": "cntx[2][1]", "value": "4 + 11 ÷ 2 = 9.5", "delay": 0.3}, {"action": "set", "target": "cntx[2][2]", "value": "1.58", "delay": 0.7}])
s.step("Both: 4 plus 10 over 4, which is 6.5. Speedup 2.31.", [{"action": "highlight", "target": "cntx[3]"}, {"action": "set", "target": "cntx[3][1]", "value": "4 + 10 ÷ 4 = 6.5", "delay": 0.3}, {"action": "set", "target": "cntx[3][2]", "value": "2.31", "delay": 0.7}])
s.step("Edge case: these are ideal counts. They assume no dependences and, for superscalar, that N is a multiple of m.", [s.take("ideal: no hazards · superscalar formula needs N a multiple of m")])

# ---------------------------------------------------------------- differences
s.scene("diff")
s.step("Stage 6: all the differences in one table.", [s.head("Stage 6 of 7: the differences"), {"action": "hide", "target": "cntx"}, s.untake(), {"action": "show", "target": "diff"}])
s.step("The idea: superpipelined makes stages shorter, superscalar adds pipelines, and VLIW packs many operations into one word.", [{"action": "highlight", "target": "diff[0]"}])
s.step("Issue: one instruction per minor cycle, m per cycle, or one long word per cycle. Only superpipelining changes the clock.", [{"action": "highlight", "target": "diff[1..=2]"}])
s.step("The key exam point: who finds the parallelism. Superscalar hardware finds it while the program runs. A VLIW compiler finds it before.", [{"action": "highlight", "target": "diff[3]"}, {"action": "mark", "target": "diff[3][2]", "delay": 0.4}, {"action": "mark", "target": "diff[3][3]", "delay": 0.6}])
s.step("So superscalar hardware is complex, VLIW hardware is simple, and each has its weak spot.", [{"action": "highlight", "target": "diff[4..=5]"}])
s.step("Ideal CPI: 1 over m for superscalar, 1 over the number of slots for VLIW. And the examples you can quote.", [{"action": "highlight", "target": "diff[6..=7]"}])
s.step("Note: superscalar and VLIW are both still SISD in Flynn's grid. They exploit instruction-level parallelism inside one instruction stream.", [s.take("superscalar = dynamic ILP · VLIW = static ILP · both SISD")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question. A five stage pipeline runs 20 instructions.", [s.head("Exam question"), {"action": "hide", "target": "diff"}, s.untake(), {"action": "show", "target": "q"}])
s.step("Find the cycles and the speedup for the scalar pipeline, a 4-way superscalar, a degree 4 superpipeline, and a design that is 2-way superscalar and degree 2 superpipelined. Then one question about VLIW. Pause and work it out.", [{"action": "highlight", "target": "q[0..=4]"}])
s.step("a: scalar, 5 plus 19: 24 cycles.", [{"action": "hide", "target": "q"}, {"action": "show", "target": "qa"}, {"action": "highlight", "target": "qa[0]"}])
s.step("b: 5 plus 16 over 4, which is 9 cycles. Speedup 24 over 9, about 2.67.", [{"action": "reveal", "target": "qa[1]"}, {"action": "highlight", "target": "qa[1]"}])
s.step("c: 5 plus 19 over 4, which is 9.75. Speedup about 2.46.", [{"action": "reveal", "target": "qa[2]"}, {"action": "highlight", "target": "qa[2]"}])
s.step("d: 5 plus 18 over 2 times 2, which is 9.5. Speedup about 2.53.", [{"action": "reveal", "target": "qa[3]"}, {"action": "highlight", "target": "qa[3]"}])
s.step("e: VLIW. Its words have fixed slots, and when the compiler cannot find enough independent operations, it must fill the rest with NOPs.", [{"action": "reveal", "target": "qa[4]"}, {"action": "highlight", "target": "qa[4]"}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qa"}, {"action": "show", "target": "stages"}])
s.step("A scalar pipeline finishes at most one instruction per cycle. Superpipelining shortens the cycle; superscalar issues several per cycle.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("VLIW lets the compiler pack the word. The cycle formulas and the difference table are what exams ask.", [{"action": "highlight", "target": "stages[3..=5]"}])
s.step("Next video: arithmetic pipelines, for floating point add, subtract, multiply and divide.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Next: arithmetic pipelines")])

s.save("./m1v9.json")

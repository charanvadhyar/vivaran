"""Module 4, video 6: vector mask registers."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

X = [3, 0, 5, 0, 0, 2, 7, 0]
Y = [1, 4, 2, 6, 3, 1, 1, 2]
M = [int(x != 0) for x in X]
R = [x - y if m else x for x, y, m in zip(X, Y, M)]
assert M == [1, 0, 1, 0, 0, 1, 1, 0] and R == [2, 0, 3, 0, 0, 1, 6, 0] and sum(M) == 4
A = [4, -1, 2, -3, 5, 0, -2, 1]
QM = [int(a > 0) for a in A]
QC = [a * 10 if a > 0 else a + 10 for a in A]
assert QM == [1, 0, 1, 0, 1, 0, 0, 1] and QC == [40, 9, 20, 7, 50, 10, 8, 10] and sum(QM) == 4
assert 64 * 2 == 128 and round(16 / 64 * 100) == 25

s = Script("Vector mask registers")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "An if inside a loop"],
    [2, "The vector mask register"],
    [3, "The VMIPS code"],
    [4, "Element by element"],
    [5, "What masking costs"],
    [6, "If and else: two masks"],
    [7, "When few elements are active"],
    [8, "Masks in RISC-V, AVX-512 and GPUs"],
    [9, "Exam question"]]})
s.obj({"id": "c", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 64; i++)",
    "    if (X[i] != 0)",
    "        X[i] = X[i] - Y[i];",
    "",
    "// some elements are updated, others must be left alone",
    "// a plain SUBVV.D would change all 64"]})
s.obj({"id": "vm", "type": "table", "region": "center", "columns": ["the mask register VM", "meaning"], "rows": [
    ["one bit per element", "64 bits for VMIPS"],
    ["set by a vector compare", "SNEVS.D V1,F0: bit i = 1 where V1[i] ≠ F0"],
    ["while VM is in use", "every vector instruction changes only elements whose bit is 1"],
    ["CVM", "clear the mask: all bits 1, every element active again"],
    ["POP R1,VM", "count the 1 bits"]]})
s.obj({"id": "code", "type": "code", "region": "center", "language": "asm", "lines": [
    "LV       V1,Rx        ; load X",
    "LV       V2,Ry        ; load Y",
    "L.D      F0,#0        ; the scalar 0",
    "SNEVS.D  V1,F0        ; VM[i] = 1 where X[i] != 0",
    "SUBVV.D  V1,V1,V2     ; subtract, only under the mask",
    "CVM                   ; all elements active again",
    "SV       V1,Rx        ; store X"]})
s.obj({"id": "el", "type": "table", "region": "center", "columns": ["element", "0", "1", "2", "3", "4", "5", "6", "7"], "rows": [
    ["X", *map(str, X)], ["Y", *map(str, Y)], ["mask: X ≠ 0", "", "", "", "", "", "", "", ""], ["new X", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "cost", "type": "table", "region": "center", "columns": ["masked execution", "effect"], "rows": [
    ["time", "the instruction still steps through all VL elements"],
    ["masked-off elements", "do no useful work, but take their cycles"],
    ["16 of 64 active", "25% of the subtract's cycles are useful"],
    ["but", "no branch, no misprediction, no scalar loop"],
    ["and", "no exception from a masked element: X[i] / Y[i] with Y[i] = 0 is safe"]]})
s.obj({"id": "ie", "type": "code", "region": "left", "language": "c", "lines": [
    "for (i = 0; i < 64; i++)",
    "    if (A[i] > 0)",
    "        C[i] = A[i] * s;",
    "    else",
    "        C[i] = A[i] + s;"]})
s.obj({"id": "iea", "type": "code", "region": "right", "language": "asm", "lines": [
    "LV       V1,Ra",
    "L.D      F0,#0      ; F2 holds s",
    "SGTVS.D  V1,F0      ; A > 0",
    "MULVS.D  V3,V1,F2   ; then-part",
    "SLEVS.D  V1,F0      ; A <= 0",
    "ADDVS.D  V3,V1,F2   ; else-part",
    "CVM",
    "SV       V3,Rc"]})
s.obj({"id": "few", "type": "table", "region": "center", "columns": ["4 of 64 active", "masked", "compress, then gather"], "rows": [
    ["how", "SUBVV.D under the mask", "CVI: list the 4 active indices"],
    ["then", "", "gather 4 · subtract 4 · scatter 4"],
    ["arithmetic work", "64 element steps", "4 element steps"],
    ["memory", "unit-stride loads", "indexed: slower per element"],
    ["choose", "many elements active", "very few active"]]})
s.obj({"id": "oth", "type": "table", "region": "center", "columns": ["machine", "masks"], "rows": [
    ["RISC-V V", "mask in v0 · vmfne sets it · ', v0.t' masks"],
    ["AVX-512", "mask registers k0 to k7"],
    ["GPUs", "a predicate per thread"],
    ["everywhere", "masked-off lanes sit idle"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["element", "0", "1", "2", "3", "4", "5", "6", "7"], "rows": [
    ["A", *map(str, A)], ["mask A > 0", "", "", "", "", "", "", "", ""], ["C", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["using the if-else code with s = 10, find:"], "rows": [
    ["a) the mask after SGTVS.D"], ["b) C for these 8 elements"], ["c) element operations done and useful in MULVS and ADDVS"], ["d) with 64 elements of which 16 are positive: the useful share of MULVS"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"c)\" quad \"MULVS: 8 done, 4 useful · ADDVS: 8 done, 4 useful\" quad 8 / 16 = 50%",
    "\"d)\" quad \"MULVS works on all 64; 16 are useful:\" quad 16 / 64 = 25%"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Loops in real programs are full of ifs. A vector instruction treats every element the same way, so how can it run a loop where some elements are changed and others are not? The answer is a mask.", [s.head("Vector mask registers")])
s.step("Here are the nine stages.", show("stages"))
s.step("The problem, the mask register, the VMIPS code, and a trace element by element.", [hl("stages[0..=3]")])
s.step("Then what masking costs, an if with an else, when very few elements are active, masks on other machines, and an exam question.", [hl("stages[4..=8]")])

s.scene("pb")
s.step("Stage 1: this loop subtracts Y from X, but only where X is not zero.", [s.head("Stage 1 of 9: an if inside a loop")] + hide("stages") + show("c") + [ml("c", 1, 3)])
s.step("Some elements must change, and the rest must be left exactly as they are. A plain vector subtract would change all 64.", [ml("c", 5, 6)])
s.step("Without help, the compiler could not vectorize this loop at all. Loops like it are common: in the textbook's measurements, many programs vectorize poorly for exactly this reason.", [s.take("an if makes the elements behave differently")])

s.scene("vm")
s.step("Stage 2: the vector mask register holds one bit per element: 64 bits for VMIPS.", [s.head("Stage 2 of 9: the mask register"), s.untake()] + hide("c") + show("vm") + [hl("vm[0]")])
s.step("A vector compare sets it. SNEVS.D compares each element with a scalar, and sets bit i to 1 where they are not equal.", [hl("vm[1]")])
s.step("While the mask is in use, every vector instruction changes only the elements whose bit is 1. The others keep their old values.", [hl("vm[2]")])
s.step("CVM clears the mask, making every element active again. Forgetting it is a classic bug: every later instruction stays masked.", [hl("vm[3]")])
s.step("And POP counts the 1 bits, the number of active elements.", [hl("vm[4]"), s.take("compare sets the mask · masked instructions skip 0 bits")])

s.scene("code")
s.step("Stage 3: the loop in VMIPS. Load X and Y, and put 0 in a scalar register.", [s.head("Stage 3 of 9: the VMIPS code"), s.untake()] + hide("vm") + show("code") + [ml("code", 1, 3)])
s.step("SNEVS.D sets the mask where X is not zero.", [ml("code", 4, 4)])
s.step("SUBVV.D now subtracts only where the mask is 1.", [ml("code", 5, 5)])
s.step("CVM restores the full mask, and SV stores X. Elements that were masked off are stored back unchanged.", [ml("code", 6, 7), s.take("7 instructions, no branch")])

s.scene("el")
s.step("Stage 4: watch 8 of the elements. Here are X and Y.", [s.head("Stage 4 of 9: element by element"), s.untake()] + hide("code") + show("el") + [hl("el[0..=1]")])
s.step("The compare sets the mask: 1 where X is not zero. Elements 0, 2, 5 and 6.", [st(f"el[2][{i + 1}]", str(m), round(0.08 * i, 2)) for i, m in enumerate(M)])
s.step("The subtract runs under the mask. 3 minus 1 is 2, 5 minus 2 is 3, 2 minus 1 is 1, 7 minus 1 is 6.", [st(f"el[3][{i + 1}]", str(r), round(0.08 * i, 2)) for i, r in enumerate(R)])
s.step("And the masked-off elements, the zeros, are untouched: exactly what the if asked for.", [hl("el[3]"), s.take("mask 1: computed · mask 0: unchanged")])

s.scene("cost")
s.step("Stage 5: what does it cost? The masked instruction still steps through all VL elements. On VMIPS, a masked subtract takes as long as an unmasked one.", [s.head("Stage 5 of 9: the cost"), s.untake()] + hide("el") + show("cost") + [hl("cost[0]")])
s.step("Masked-off elements do no useful work, but they still use their cycles.", [hl("cost[1]")])
s.step("If only 16 of 64 elements are active, only a quarter of the subtract's cycles do useful work.", [hl("cost[2]")])
s.step("Even so, it usually beats the alternative: no branches, no mispredictions, no scalar loop of 64 iterations.", [hl("cost[3]")])
s.step("And a masked element raises no exception. Dividing under a mask where the divisor is zero is safe, because those elements are never computed.", [hl("cost[4]"), s.take("masked elements cost time, not correctness")])

s.scene("ie")
s.step("Stage 6: an if with an else. Positive elements are multiplied by s; the others have s added.", [s.head("Stage 6 of 9: if and else"), s.untake()] + hide("cost") + show("ie", "iea") + [ml("ie", 1, 5)])
s.step("Compare greater than zero, and run the then-part under that mask.", [ml("iea", 3, 4)])
s.step("Then compare less than or equal, which sets the opposite mask, and run the else-part. Both write into V3, so each element gets the right result.", [ml("iea", 5, 6)])
s.step("Clear the mask and store. Notice the cost: both halves run over all 64 elements. An if-else costs the time of both branches.", [ml("iea", 7, 8), s.take("if-else: both halves run, each under its mask")])

s.scene("few")
s.step("Stage 7: masking wastes the most when very few elements are active. Suppose only 4 of 64 are non-zero.", [s.head("Stage 7 of 9: few elements active"), s.untake()] + hide("ie", "iea") + show("few") + [hl("few[0][1]")])
s.step("The alternative: compress. VMIPS has CVI, create vector index, which builds a short vector holding just the positions whose mask bit is 1: here 4 indices.", [hl("few[0][2]")])
s.step("Then an indexed load gathers just those 4 X and Y values, the subtract runs on 4 elements, and an indexed store scatters them back.", [hl("few[1]")])
s.step("The arithmetic drops from 64 element steps to 4. But indexed loads and stores are slower per element than unit-stride ones.", [hl("few[2..=3]")])
s.step("So the compiler chooses: masks when many elements are active, compress and gather when very few are. Gather and scatter get their own video soon.", [hl("few[4]"), s.take("many active: mask · few active: compress and gather")])

s.scene("oth")
s.step("Stage 8: every data-parallel machine has the same idea. In RISC-V V, register v0 is the mask. A compare like vmfne sets it, and adding v0 dot t to an instruction makes it masked.", [s.head("Stage 8 of 9: masks elsewhere"), s.untake()] + hide("few") + show("oth") + [hl("oth[0]")])
s.step("AVX-512 added eight mask registers, k0 to k7, usable by almost every instruction.", [hl("oth[1]")])
s.step("And GPUs mask threads: when threads in a group take different sides of a branch, the hardware runs each side with the other threads masked off. That is branch divergence, video 13.", [hl("oth[2]")])
s.step("The cost is the same everywhere: masked-off lanes sit idle.", [hl("oth[3]"), s.take("vectors, SIMD and GPUs all mask")])

s.scene("exam")
s.step("Now an exam question, using the if-else code with s equal to 10.", [s.head("Exam question"), s.untake()] + hide("oth") + show("q") + [hl("q[0]")])
s.step("Find the mask after the first compare, the values of C, the element operations done and useful, and the useful share when 16 of 64 elements are positive. Pause and work it out.", hide("q") + show("qx") + [hl("qx")])
s.step("a: the mask is 1 where A is positive: elements 0, 2, 4 and 7.", hide("qx") + show("q") + [st(f"q[1][{i + 1}]", str(m), round(0.08 * i, 2)) for i, m in enumerate(QM)])
s.step("b: positive elements times 10: 40, 20, 50, 10. The others plus 10: 9, 7, 10, 8.", [st(f"q[2][{i + 1}]", str(c), round(0.08 * i, 2)) for i, c in enumerate(QC)])
s.step("Careful with element 5: A is 0, and 0 is not greater than 0. So it takes the else-part: 0 plus 10, 10.", [hl("q[2][6]")])
s.step("c: the multiply and the add each process all 8 elements, but only 4 are useful in each. 8 useful out of 16: 50 percent.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("d: with 16 positive out of 64, the multiply does useful work on 16 of its 64 elements: 25 percent.", [rv("qa[1]"), hl("qa[1]")])
s.step("The usual slip: forgetting CVM before the store, or before the next loop. Every later instruction would stay masked.", [s.take("always CVM after masked code")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A vector compare sets one mask bit per element, and masked instructions change only the elements whose bit is 1.", [hl("stages[0..=3]")])
s.step("Masked elements still take their cycles, and an if-else runs both halves. When few are active, compressing and gathering can win. RISC-V, AVX-512 and GPUs all mask the same way.", [hl("stages[4..=7]")])
s.step("Next video: memory. How vector loads keep up, memory banks, and strided access.", [mk("stages[0..=8]"), s.take("Next: memory banks and stride")])

s.save("/home/claude/playlist/m4/m4v6.json")

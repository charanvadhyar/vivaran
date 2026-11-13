"""Module 4, video 5: strip mining and the vector length register."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script


def strips(n, mvl=64):
    out, low, vl = [], 0, n % mvl
    for _ in range(n // mvl + 1):
        if vl:
            out.append((low, low + vl - 1, vl))
        low += vl
        vl = mvl
    return out


def T(n, chimes, tstart, tloop=15, mvl=64):
    return -(-n // mvl) * (tloop + tstart) + n * chimes


assert strips(200) == [(0, 7, 8), (8, 71, 64), (72, 135, 64), (136, 199, 64)]
assert T(200, 3, 12 + 7 + 12) == 784 and 4 * 46 == 184 and round(784 / 200, 2) == 3.92
assert strips(150) == [(0, 21, 22), (22, 85, 64), (86, 149, 64)]
assert T(150, 4, 12 + 12 + 6 + 12) == 771 and 3 * 57 == 171 and round(771 / 150, 2) == 5.14
assert strips(128) == [(0, 63, 64), (64, 127, 64)] and 128 % 64 == 0
assert T(1000, 3, 31) == 16 * 46 + 3000 == 3736 and round(3736 / 1000, 2) == 3.74

s = Script("Strip mining")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "When n is not 64"],
    [2, "The vector length register"],
    [3, "Strip mining"],
    [4, "The same loop in VMIPS"],
    [5, "The strips for n = 200"],
    [6, "A time formula"],
    [7, "A worked example"],
    [8, "RISC-V makes it simple"],
    [9, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["case", "problem"], "rows": [
    ["n < 64", "only part of each register should be used"],
    ["n > 64", "the data does not fit in one register"],
    ["n unknown until run time", "for (i = 0; i < n; i++) with n read from input"],
    ["the answer", "a register that says how long a vector is, and a loop over pieces"]]})
s.obj({"id": "vl", "type": "table", "region": "center", "columns": ["VMIPS", "meaning"], "rows": [
    ["MVL", "maximum vector length: 64, the register size"],
    ["VLR", "vector length register: how many elements the next instructions use"],
    ["MTC1 VLR,R1", "set VLR from R1; VLR may be anything from 0 to MVL"],
    ["every vector instruction", "operates on elements 0 to VLR − 1 only"]]})
s.obj({"id": "c", "type": "code", "region": "center", "language": "c", "lines": [
    "low = 0;",
    "VL = n % MVL;                       // the odd-size piece first",
    "for (j = 0; j <= n / MVL; j++) {    // one pass per strip",
    "    for (i = low; i < low + VL; i++)    // runs as vector code, VLR = VL",
    "        Y[i] = a * X[i] + Y[i];",
    "    low = low + VL;                 // start of the next strip",
    "    VL = MVL;                       // every later strip is full",
    "}"]})
s.obj({"id": "vm", "type": "code", "region": "center", "language": "asm", "lines": [
    "      ANDI    R1,Rn,#63     ; VL = n mod 64",
    "      MTC1    VLR,R1",
    "Loop: LV      V1,Rx         ; the vector work: VL elements",
    "      MULVS.D V2,V1,F0",
    "      LV      V3,Ry",
    "      ADDVV.D V4,V2,V3",
    "      SV      V4,Ry",
    "      DSLL    R2,R1,#3      ; bytes done = VL × 8",
    "      DADDU   Rx,Rx,R2",
    "      DADDU   Ry,Ry,R2",
    "      DSUBU   Rn,Rn,R1      ; elements left",
    "      DADDIU  R1,R0,#64     ; later strips are full",
    "      MTC1    VLR,R1",
    "      BNEZ    Rn,Loop"]})
s.obj({"id": "st", "type": "table", "region": "center", "columns": ["strip", "elements", "VL"], "rows": [
    ["1", "", ""], ["2", "", ""], ["3", "", ""], ["4", "", ""]]})
s.obj({"id": "tf", "type": "math", "region": "center", "lines": [
    "T_n = ceil(n / \"MVL\") times (T_\"loop\" + T_\"start\") + n times T_\"chime\"",
    "T_\"loop\": \"scalar loop overhead per strip (take 15)\"",
    "T_\"start\": \"sum of the convoys' startups, paid once per strip\"",
    "T_\"chime\": \"the number of convoys: cycles per element\""]})
s.obj({"id": "ex", "type": "code", "region": "center", "language": "asm", "lines": [
    "; A = B × s, n = 200, MVL = 64, no chaining",
    "LV       V1,Rb        ; convoy 1, startup 12",
    "MULVS.D  V2,V1,F0     ; convoy 2, startup 7",
    "SV       V2,Ra        ; convoy 3, startup 12"]})
s.obj({"id": "exm", "type": "math", "region": "center", "lines": [
    "T_\"chime\" = 3, quad T_\"start\" = 12 + 7 + 12 = 31, quad T_\"loop\" = 15",
    "T_200 = ceil(200 / 64) times (15 + 31) + 200 times 3 = 4 times 46 + 600 = 784",
    "784 / 200 approx 3.92 \"cycles per element\"",
    "n = 1000: quad 16 times 46 + 3000 = 3736 quad 3.74 \"per element\""]})
s.obj({"id": "rv", "type": "code", "region": "center", "language": "asm", "lines": [
    "loop: vsetvli  t0,a0,e64      # t0 = min(a0, VLMAX): this strip's length",
    "      vle64.v  v1,(a1)        # load X",
    "      vle64.v  v2,(a2)        # load Y",
    "      vfmacc.vf v2,fa0,v1     # Y = a*X + Y",
    "      vse64.v  v2,(a2)        # store Y",
    "      sub      a0,a0,t0       # elements left",
    "      slli     t1,t0,3        # bytes done = t0 × 8",
    "      add      a1,a1,t1",
    "      add      a2,a2,t1",
    "      bnez     a0,loop"]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "asm", "lines": [
    "; A = B + C, MVL = 64, no chaining, one load-store unit",
    "LV       V1,Rb",
    "LV       V2,Rc",
    "ADDVV.D  V3,V1,V2",
    "SV       V3,Ra",
    "; a) strips for n = 150   b) T_150 with T_loop = 15   c) strips for n = 128"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["a) strip", "elements", "VL"], "rows": [
    [str(k + 1), f"{a} to {b}", str(v)] for k, (a, b, v) in enumerate(strips(150))] + [
    ["c) n = 128", "128 mod 64 = 0: the first piece is empty", "2 full strips"]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"convoys: LV · LV · ADDVV.D · SV\" quad T_\"chime\" = 4",
    "T_\"start\" = 12 + 12 + 6 + 12 = 42",
    "T_150 = 3 times (15 + 42) + 150 times 4 = 171 + 600 = 771 quad 5.14 \"per element\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("So far every vector had exactly 64 elements, the size of a register. Real arrays have 10 elements, or 10 million, often unknown until the program runs. This video shows how vector code handles any length.", [s.head("Strip mining")])
s.step("Here are the nine stages.", show("stages"))
s.step("The problem, the vector length register, the strip-mining loop in C and in VMIPS, and the strips for one example.", [hl("stages[0..=4]")])
s.step("Then a formula for the time, a worked example, how RISC-V simplifies it, and an exam question.", [hl("stages[5..=8]")])

s.scene("pb")
s.step("Stage 1: three cases break our simple code. A vector shorter than 64 should use only part of each register.", [s.head("Stage 1 of 9: when n is not 64")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("A vector longer than 64 does not fit in one register at all.", [hl("pb[1]")])
s.step("And often n is a variable, read from input, so the compiler cannot know it.", [hl("pb[2]")])
s.step("The answer has two parts: a register that tells the hardware how long the vector is, and a loop over pieces of at most 64.", [hl("pb[3]"), s.take("any n: a length register plus a loop")])

s.scene("vl")
s.step("Stage 2: MVL, the maximum vector length, is fixed by the hardware: 64 for VMIPS.", [s.head("Stage 2 of 9: the vector length register"), s.untake()] + hide("pb") + show("vl") + [hl("vl[0]")])
s.step("VLR, the vector length register, holds the length the next vector instructions should use.", [hl("vl[1]")])
s.step("MTC1 VLR, R1 copies a value from a scalar register. It may be anything from 0 up to MVL.", [hl("vl[2]")])
s.step("Every vector instruction then works only on elements 0 to VLR minus 1. The rest of the register is left alone.", [hl("vl[3]"), s.take("VLR ≤ MVL · instructions use VLR elements")])

s.scene("strip")
s.step("Stage 3: for longer vectors, the compiler generates strip mining: it cuts the loop into strips of at most MVL elements. Here is the textbook's version for DAXPY.", [s.head("Stage 3 of 9: strip mining"), s.untake()] + hide("vl") + show("c") + [ml("c", 1, 8)])
s.step("First, VL is set to n mod MVL: the odd-sized piece goes first.", [ml("c", 2, 2)])
s.step("The outer loop runs n over MVL plus 1 times, once per strip.", [ml("c", 3, 3)])
s.step("The inner loop is the part that becomes vector code. It sets VLR to VL, and runs LV, MULVS, LV, ADDVV and SV on that many elements.", [ml("c", 4, 5)])
s.step("Then it moves low past the strip just done, and sets VL to MVL: every later strip is full length.", [ml("c", 6, 7), s.take("odd piece first, then full strips of MVL")])

s.scene("vmips")
s.step("Stage 4: the same loop in VMIPS assembly. Before the loop, n mod 64 goes into VLR. ANDI with 63 keeps the low six bits: that is n mod 64.", [s.head("Stage 4 of 9: the VMIPS loop"), s.untake()] + hide("c") + show("vm") + [ml("vm", 1, 2)])
s.step("The loop body starts with the five vector instructions of DAXPY, working on VL elements.", [ml("vm", 3, 7)])
s.step("Then the scalar bookkeeping: move both pointers on by VL times 8 bytes, and subtract VL from the count.", [ml("vm", 8, 11)])
s.step("Set VLR to 64 for every later strip, and branch back while elements remain.", [ml("vm", 12, 14)])
s.step("Those seven scalar instructions run once per strip. With their stalls, that is the loop overhead the time formula will call T loop.", [ml("vm", 8, 14), s.take("5 vector + 7 scalar instructions per strip")])

s.scene("strips")
s.step("Stage 5: take n equal to 200. 200 mod 64 is 8, so the first strip has just 8 elements, 0 to 7.", [s.head("Stage 5 of 9: strips for n = 200"), s.untake()] + hide("vm") + show("st") + [st("st[0][1]", "0 to 7"), st("st[0][2]", "8", 0.3)])
s.step("Then three full strips of 64: 8 to 71, 72 to 135, and 136 to 199.", [st("st[1][1]", "8 to 71"), st("st[1][2]", "64", 0.1), st("st[2][1]", "72 to 135", 0.3), st("st[2][2]", "64", 0.4), st("st[3][1]", "136 to 199", 0.6), st("st[3][2]", "64", 0.7)])
s.step("Four strips: 8 plus 3 times 64 is 200. In general, the ceiling of n over MVL strips.", [hl("st[0..=3]"), s.take("200 = 8 + 64 + 64 + 64: 4 strips")])

s.scene("time")
s.step("Stage 6: how long does it take? The textbook's formula has three parts.", [s.head("Stage 6 of 9: a time formula"), s.untake()] + hide("st") + show("tf") + [hl("tf[0]")])
s.step("T loop: the scalar instructions that run the outer loop, about 15 cycles per strip.", [rv("tf[1]"), hl("tf[1]")])
s.step("T start: the startups of all the convoys, paid again in every strip.", [rv("tf[2]"), hl("tf[2]")])
s.step("And T chime: the number of convoys, which is the cycles per element once the pipelines are running.", [rv("tf[3]"), hl("tf[3]"), s.take("T_n = ⌈n / MVL⌉ (T_loop + T_start) + n T_chime")])

s.scene("ex")
s.step("Stage 7: A equals B times a scalar s, with 200 elements, and no chaining.", [s.head("Stage 7 of 9: a worked example"), s.untake()] + hide("tf") + show("ex") + [ml("ex", 1, 4)])
s.step("Three convoys: the load, the multiply, the store. Their startups are 12, 7 and 12.", [ml("ex", 2, 4)])
s.step("So T chime is 3, T start is 31, and T loop is 15.", hide("ex") + show("exm") + [hl("exm[0]")])
s.step("Four strips, each paying 15 plus 31, that is 46: 184 cycles. Plus 200 elements at 3 cycles each: 600. 784 cycles.", [rv("exm[1]"), hl("exm[1]")])
s.step("About 3.92 cycles per element, against the ideal of 3.", [rv("exm[2]"), hl("exm[2]")])
s.step("For 1000 elements, 16 strips: 3736 cycles, 3.74 per element. The longer the vector, the closer to the chime count, since the overhead per strip is spread over 64 elements.", [rv("exm[3]"), hl("exm[3]"), s.take("overhead per strip, work per element")])

s.scene("rv")
s.step("Stage 8: RISC-V's vector extension makes strip mining almost free to write. Each pass of the loop starts with vsetvli.", [s.head("Stage 8 of 9: RISC-V"), s.untake()] + hide("exm") + show("rv") + [ml("rv", 1, 1)])
s.step("vsetvli takes the number of elements left, and sets the vector length to that number or to the hardware maximum, whichever is smaller. It returns the length in t0.", [ml("rv", 1, 1)])
s.step("Then the loads, a fused multiply-add, and the store, on t0 elements.", [ml("rv", 2, 5)])
s.step("Subtract t0 from the count, move the pointers on by t0 times 8 bytes, and loop while elements remain.", [ml("rv", 6, 10)])
s.step("No odd piece to compute in advance, no knowledge of the hardware's maximum length. The last strip is simply the short one. The same binary runs on any vector length.", [s.take("vsetvli: the hardware picks each strip's length")])

s.scene("exam")
s.step("Now an exam question: A equals B plus C, maximum vector length 64, no chaining, one load-store unit.", [s.head("Exam question"), s.untake()] + hide("rv") + show("q") + [ml("q", 1, 5)])
s.step("Find the strips for 150 elements, the execution time with a loop overhead of 15, and the strips for 128 elements. Pause and work it out.", [ml("q", 6, 6)])
s.step("150 mod 64 is 22. So strip 1 has 22 elements, 0 to 21. Then two full strips: 22 to 85, and 86 to 149.", hide("q") + show("qa") + [hl("qa[0..=2]")])
s.step("For 128: 128 mod 64 is 0, so the first piece is empty, and the code does two full strips. The formula's ceiling, 2, counts this correctly.", [hl("qa[3]")])
s.step("The time. Four convoys: the two loads cannot share the load-store unit. T chime is 4.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("The startups: 12, 12, 6 and 12, total 42.", [rv("qb[1]"), hl("qb[1]")])
s.step("3 strips times 57, plus 150 times 4: 171 plus 600, 771 cycles, about 5.14 per element.", [rv("qb[2]"), hl("qb[2]")])
s.step("The usual slip: counting n over MVL strips, rounded down. 150 needs 3 strips, not 2. Always round up.", [s.take("strips = ⌈n / MVL⌉")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("The vector length register lets instructions work on fewer than MVL elements. Strip mining cuts a loop of any length into an odd piece and full strips.", [hl("stages[0..=4]")])
s.step("Time is the strips times the loop and startup overhead, plus n times the chimes. RISC-V's vsetvli lets the hardware choose each strip's length.", [hl("stages[5..=7]")])
s.step("Next video: what if the loop has an if inside? Vector mask registers.", [mk("stages[0..=8]"), s.take("Next: vector masks")])

s.save("/home/claude/playlist/m4/m4v5.json")

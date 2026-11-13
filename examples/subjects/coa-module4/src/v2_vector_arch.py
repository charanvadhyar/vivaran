"""Module 4, video 2: vector architecture: VMIPS and RV64V."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

assert 8 * 64 * 8 == 4096          # 8 registers x 64 elements x 8 bytes = 4 KB
assert 64 * 3 == 192               # Z = X*X + Y*Y: 64 mul + 64 mul + 64 add
assert 32 * 32 * 8 == 8192         # exam: 32 registers x 32 elements x 8 bytes = 8 KB
assert 64 * 2 == 128               # exam: add + multiply on 64 elements

s = Script("Vector architecture")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The VMIPS machine"],
    [2, "Vector registers"],
    [3, "Why registers, not memory"],
    [4, "Fully pipelined vector units"],
    [5, "The vector instruction set"],
    [6, "VMIPS and RISC-V V side by side"],
    [7, "Writing a vector program"],
    [8, "Exam question"]]})
s.obj({"id": "dg", "type": "diagram", "region": "center", "layout": "layers", "direction": "down", "nodes": [
    {"id": "mem", "label": "memory"},
    {"id": "ls", "label": "load/store"},
    {"id": "vr", "label": "vector regs"}, {"id": "sr", "label": "scalar regs"},
    {"id": "add", "label": "FP add"}, {"id": "mul", "label": "FP multiply"}, {"id": "div", "label": "FP divide"},
    {"id": "int", "label": "integer"}, {"id": "log", "label": "logical"}],
    "edges": [{"from": "mem", "to": "ls"}, {"from": "ls", "to": "vr"}, {"from": "ls", "to": "sr"},
              {"from": "vr", "to": "add"}, {"from": "vr", "to": "mul"}, {"from": "vr", "to": "div"},
              {"from": "vr", "to": "int"}, {"from": "vr", "to": "log"}]})
s.obj({"id": "vr", "type": "table", "region": "center", "columns": ["vector registers", "VMIPS"], "rows": [
    ["how many", "8: V0 to V7"],
    ["each holds", "64 elements of 64 bits"],
    ["total size", "8 × 64 × 8 bytes = 4 KB"],
    ["ports", "16 read and 8 write, through crossbars to every unit"],
    ["special registers", "VLR: vector length · VM: vector mask"]]})
s.obj({"id": "mm", "type": "table", "region": "center", "columns": ["", "memory-memory", "vector-register"], "rows": [
    ["operands", "from memory", "from registers"],
    ["example", "CDC STAR-100, 1974", "Cray-1, 1976, and since"],
    ["startup", "long", "short"],
    ["results", "back to memory", "stay in registers"]]})
s.obj({"id": "pipe", "type": "table", "region": "center", "columns": ["cycle", "1", "2", "3", "4", "5", "6", "7", "8"], "rows": [
    ["stage 1 of the adder", "e0", "e1", "e2", "e3", "e4", "e5", "e6", "e7"],
    ["stage 2", "", "e0", "e1", "e2", "e3", "e4", "e5", "e6"],
    ["stage 3", "", "", "e0", "e1", "e2", "e3", "e4", "e5"],
    ["stage 4", "", "", "", "e0", "e1", "e2", "e3", "e4"],
    ["result", "", "", "", "", "e0", "e1", "e2", "e3"]]})
s.obj({"id": "isa", "type": "table", "region": "center", "columns": ["VMIPS instruction", "operands", "meaning"], "rows": [
    ["ADDVV.D V1,V2,V3", "vector, vector", "V1[i] = V2[i] + V3[i] for every element"],
    ["ADDVS.D V1,V2,F0", "vector, scalar", "V1[i] = V2[i] + F0"],
    ["LV V1,R1 · SV V1,R1", "unit stride", "load or store consecutive elements"],
    ["LVWS V1,(R1,R2)", "strided", "load every R2-th element"],
    ["LVI V1,(R1+V2)", "indexed (gather)", "load from R1 + V2[i]"],
    ["SEQVV.D V1,V2", "compare", "set the mask bit where V1[i] = V2[i]"],
    ["MTC1 VLR,R1", "control", "set the vector length"]]})
s.obj({"id": "rv", "type": "table", "region": "center", "columns": ["operation", "VMIPS", "RISC-V V (RV64V)"], "rows": [
    ["set the vector length", "MTC1 VLR,R1", "vsetvli t0,a0,e64"],
    ["unit-stride load", "LV V1,R1", "vle64.v v1,(a1)"],
    ["strided load", "LVWS V1,(R1,R2)", "vlse64.v v1,(a1),a2"],
    ["indexed load", "LVI V1,(R1+V2)", "vluxei64.v v1,(a1),v2"],
    ["vector × scalar", "MULVS.D V2,V1,F0", "vfmul.vf v2,v1,fa0"],
    ["vector + vector", "ADDVV.D V4,V2,V3", "vfadd.vv v4,v2,v3"],
    ["store", "SV V4,R2", "vse64.v v4,(a2)"]]})
s.obj({"id": "rvx", "type": "table", "region": "center", "columns": ["RISC-V V differs", "how"], "rows": [
    ["vector length", "not fixed at 64: each chip chooses; vsetvli says how many fit"],
    ["element width", "set by vsetvli: e64, e32, e16, e8"],
    ["same binary", "runs on narrow and wide hardware alike"]]})
s.obj({"id": "pr", "type": "code", "region": "center", "language": "asm", "lines": [
    "; Z[i] = X[i]*X[i] + Y[i]*Y[i], 64 elements",
    "LV       V1,Rx       ; X",
    "MULVV.D  V2,V1,V1    ; X squared",
    "LV       V3,Ry       ; Y",
    "MULVV.D  V4,V3,V3    ; Y squared",
    "ADDVV.D  V5,V2,V4    ; sum",
    "SV       V5,Rz       ; store Z"]})
s.obj({"id": "prx", "type": "math", "region": "center", "lines": [
    "6 \"instructions\" quad 64 + 64 + 64 = 192 \"floating-point operations\"",
    "\"registers used: V1 to V5, five of the eight\""]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["question"], "rows": [
    ["a) write VMIPS code for D[i] = (A[i] + B[i]) × s, 64 elements"],
    ["b) how many instructions, and how many floating-point operations?"],
    ["c) a vector file of 32 registers, 32 elements of 64 bits each: its size?"],
    ["d) write the add in RISC-V V"]]})
s.obj({"id": "qa", "type": "code", "region": "center", "language": "asm", "lines": [
    "L.D      F0,s",
    "LV       V1,Ra",
    "LV       V2,Rb",
    "ADDVV.D  V3,V1,V2",
    "MULVS.D  V4,V3,F0",
    "SV       V4,Rd"]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"b)\" quad 6 \"instructions\" quad 64 + 64 = 128 \"FP operations\"",
    "\"c)\" quad 32 times 32 times 8 \"bytes\" = 8192 \"bytes\" = 8 \"KB\"",
    "\"d)\" quad \"vfadd.vv v3, v1, v2\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Last video showed that six vector instructions can replace 578 scalar ones. Now we open the machine that runs them: the textbook's VMIPS, and its modern relative, the RISC-V vector extension.", [s.head("Vector architecture")])
s.step("Here are the eight stages.", show("stages"))
s.step("The machine, its vector registers, why they are registers at all, and the pipelined units.", [hl("stages[0..=3]")])
s.step("Then the instruction set, VMIPS beside RISC-V, writing a small program, and an exam question.", [hl("stages[4..=7]")])

s.scene("machine")
s.step("Stage 1: VMIPS is an ordinary scalar MIPS processor with a vector unit added. Its heart is the vector register file.", [s.head("Stage 1 of 8: the VMIPS machine")] + hide("stages") + show("dg") + [hl("dg.vr")])
s.step("A vector load-store unit moves whole vectors between memory and the registers. It is pipelined too: after an initial latency it delivers one word per cycle.", [hl("dg.mem"), hl("dg.ls", 0.3)])
s.step("Five vector functional units read from and write to the vector registers: floating-point add, multiply and divide, integer, and logical.", [hl("dg.add"), hl("dg.mul", 0.15), hl("dg.div", 0.3), hl("dg.int", 0.45), hl("dg.log", 0.6)])
s.step("And the scalar registers supply single values, like the a in DAXPY, and addresses.", [hl("dg.sr"), s.take("memory ↔ load/store ↔ vector registers ↔ pipelined units")])

s.scene("regs")
s.step("Stage 2: VMIPS has eight vector registers, V0 to V7.", [s.head("Stage 2 of 8: vector registers"), s.untake()] + hide("dg") + show("vr") + [hl("vr[0]")])
s.step("Each one holds 64 elements of 64 bits: a whole vector of doubles.", [hl("vr[1]")])
s.step("Eight registers of 64 elements of 8 bytes: 4 kilobytes. Far bigger than a scalar register file of 32 registers.", [hl("vr[2]")])
s.step("Several units work at once, so the file needs many ports: 16 read and 8 write, connected to the units by crossbars.", [hl("vr[3]")])
s.step("Two special registers come up again and again: the vector length register, VLR, for vectors shorter than 64, and the vector mask register, VM, for conditionals. Each gets its own video.", [hl("vr[4]"), s.take("8 registers × 64 elements × 64 bits = 4 KB")])

s.scene("why")
s.step("Stage 3: why keep vectors in registers at all? The earliest vector machines did not. The CDC STAR-100 of 1974 read every operand from memory and wrote every result back.", [s.head("Stage 3 of 8: why registers"), s.untake()] + hide("vr") + show("mm") + [hl("mm[0..=1]")])
s.step("That made every instruction wait for memory before its first element could start: a long startup on every operation.", [hl("mm[2]")])
s.step("And a result needed by the next instruction made a round trip through memory.", [hl("mm[3]")])
s.step("The Cray-1, two years later, put vectors in registers. Loads and stores move data in bulk, and arithmetic works register to register, exactly like a RISC processor. Every vector machine since has followed it, VMIPS included.", [mk("mm[1][2]"), s.take("load once, compute in registers, store once")])

s.scene("pipe")
s.step("Stage 4: each vector unit is fully pipelined. Here is a 4-stage adder working through a vector.", [s.head("Stage 4 of 8: pipelined units"), s.untake()] + hide("mm") + show("pipe") + [hl("pipe[0]")])
s.step("Element 0 enters in cycle 1, element 1 in cycle 2, and so on. A new element starts every cycle.", [hl("pipe[0..=3]")])
s.step("The first result appears after the pipeline latency, in cycle 5. After that, one result comes out every cycle.", [hl("pipe[4]")])
s.step("The pipeline never stalls inside a vector, because the elements are independent. So vector units can be very deeply pipelined, and clocked fast. A vector of n elements takes about the latency plus n cycles.", [mk("pipe[4]"), s.take("one element per cycle, after the startup latency")])

s.scene("isa")
s.step("Stage 5: the instruction set. Arithmetic comes in two forms. Vector-vector: ADDVV.D adds two vectors element by element.", [s.head("Stage 5 of 8: the instruction set"), s.untake()] + hide("pipe") + show("isa") + [hl("isa[0]")])
s.step("Vector-scalar: ADDVS.D adds the same scalar to every element.", [hl("isa[1]")])
s.step("Three kinds of load and store. Unit stride, LV and SV, for consecutive elements.", [hl("isa[2]")])
s.step("Strided, LVWS, for every k-th element: a column of a matrix stored by rows.", [hl("isa[3]")])
s.step("And indexed, LVI, which loads from addresses given by another vector: a gather, for sparse data.", [hl("isa[4]")])
s.step("Compares set bits in the mask register, and MTC1 sets the vector length. These come later in the module.", [hl("isa[5..=6]"), s.take("VV and VS arithmetic · unit, strided and indexed memory")])

s.scene("rv")
s.step("Stage 6: the same operations in the RISC-V vector extension, which real chips now ship.", [s.head("Stage 6 of 8: VMIPS and RISC-V V"), s.untake()] + hide("isa") + show("rv"))
s.step("vsetvli sets the vector length and the element width.", [hl("rv[0]")])
s.step("Loads: vle64 for unit stride, vlse64 for strided, vluxei64 for indexed.", [hl("rv[1..=3]")])
s.step("Arithmetic: vfmul dot vf multiplies a vector by a scalar register, and vfadd dot vv adds two vectors. The same pattern as MULVS and ADDVV.", [hl("rv[4..=5]")])
s.step("And vse64 stores.", [hl("rv[6]")])
s.step("The big difference: RISC-V does not fix the vector length at 64. Each chip chooses its own, and vsetvli tells the program how many elements fit.", hide("rv") + show("rvx") + [hl("rvx[0]")])
s.step("The element width is chosen at run time too, so the same registers hold 64-bit doubles or 8-bit pixels.", [hl("rvx[1]")])
s.step("So one binary runs on a small chip with short vectors and a big chip with long ones.", [hl("rvx[2]"), s.take("same ideas · RISC-V lets the hardware pick the length")])

s.scene("prog")
s.step("Stage 7: write a program. Z equals X squared plus Y squared, for 64 elements.", [s.head("Stage 7 of 8: a vector program"), s.untake()] + hide("rvx") + show("pr") + [ml("pr", 1, 1)])
s.step("Load X, and multiply it by itself: a vector-vector multiply.", [ml("pr", 2, 3)])
s.step("Load Y, and square it.", [ml("pr", 4, 5)])
s.step("Add the two squares, and store Z.", [ml("pr", 6, 7)])
s.step("Notice the dependences between instructions: each multiply needs its load, and the add needs both multiplies. Within a vector there are none, but between vector instructions there are. How the machine overlaps them decides the running time, the subject of the next two videos.", [ml("pr", 2, 6)])
s.step("Six instructions do 192 floating-point operations, and use five of the eight vector registers. With only eight, the compiler must reuse registers carefully in bigger loops.", hide("pr") + show("prx") + [hl("prx[0]"), rv("prx[1]"), hl("prx[1]", 0.4), s.take("6 instructions, 192 operations")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("prx") + show("q"))
s.step("Write VMIPS code for D equals A plus B, times a scalar s, for 64 elements. Count instructions and operations. Find the size of a register file with 32 registers of 32 elements. And write the add in RISC-V. Pause and work it out.", [hl("q")])
s.step("Load the scalar s into F0. Load A and B.", hide("q") + show("qa") + [ml("qa", 1, 3)])
s.step("Add them with ADDVV, multiply by the scalar with MULVS, and store D.", [ml("qa", 4, 6)])
s.step("Six instructions, and 64 adds plus 64 multiplies: 128 operations.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("The register file: 32 times 32 times 8 bytes, 8 kilobytes. Twice VMIPS's, even though each register is half as long.", [rv("qb[1]"), hl("qb[1]")])
s.step("And in RISC-V, vfadd dot vv, v3, v1, v2.", [rv("qb[2]"), hl("qb[2]")])
s.step("The usual slip: using a VV instruction with a scalar operand. A scalar needs the VS form: MULVS, or vfmul dot vf.", [s.take("scalar operand → VS form")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("VMIPS adds eight 64-element vector registers, a pipelined load-store unit and five fully pipelined units to a scalar MIPS. Registers, not memory, hold the vectors, as in the Cray-1.", [hl("stages[0..=3]")])
s.step("Its instructions come in vector-vector and vector-scalar forms, with unit-stride, strided and indexed memory access. RISC-V V has the same ideas, with a hardware-chosen length.", [hl("stages[4..=6]")])
s.step("Next video: how long does vector code take? Convoys, chimes and startup time.", [mk("stages[0..=7]"), s.take("Next: vector execution time")])

s.save("/home/claude/playlist/m4/m4v2.json")

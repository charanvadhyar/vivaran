"""Module 4, video 9: SIMD instruction set extensions: MMX, SSE, AVX."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

assert [256 // w for w in (8, 16, 32, 64)] == [32, 16, 8, 4]
assert 5 + 9 * 16 == 149 and 2 + 9 * 64 == 578
sat = lambda a, b: min(255, a + b)
assert sat(250, 10) == 255 and (250 + 10) % 256 == 4 and sat(100, 50) == 150
assert 2 * 4 * 2 * 3 == 48                    # 2 FMA units x 4 doubles x 2 flops x 3 GHz
assert 1920 * 1080 == 2_073_600 and 2_073_600 // 32 == 64_800 and 2_073_600 % 32 == 0
assert 64 // 8 == 8 and 5 + 9 * 8 == 77
assert 2 * 8 * 2 * 2 == 64
assert sat(200, 100) == 255 and (200 + 100) % 256 == 44

s = Script("SIMD extensions: MMX, SSE, AVX")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why ordinary CPUs added SIMD"],
    [2, "Partitioned registers"],
    [3, "From MMX to AVX-512"],
    [4, "Saturating arithmetic"],
    [5, "DAXPY with SIMD instructions"],
    [6, "AVX from C"],
    [7, "SIMD extensions against vector machines"],
    [8, "Peak performance"],
    [9, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["observation", "consequence"], "rows": [
    ["media data is narrow", "pixels are 8 bits, audio samples 16 bits"],
    ["a 64-bit adder", "can be cut into eight 8-bit adders by breaking the carry chain"],
    ["cheap to add", "little new state, reuses the existing pipeline and caches"],
    ["the result", "one instruction does 8, 16, 32 or 64 narrow operations"]]})
s.obj({"id": "pt", "type": "table", "region": "center", "columns": ["a 256-bit AVX register holds", "lanes", "typical data"], "rows": [
    ["8-bit elements", "32", "pixels"],
    ["16-bit elements", "16", "audio samples"],
    ["32-bit elements", "8", "floats, ints"],
    ["64-bit elements", "4", "doubles"]]})
s.obj({"id": "hist", "type": "table", "region": "center", "columns": ["extension", "about", "width", "added"], "rows": [
    ["MMX", "1996", "64 bits", "integer only, in the FP registers"],
    ["SSE", "1999", "128 bits", "new XMM registers, single-precision floats"],
    ["SSE2", "2001", "128 bits", "doubles, wider integers"],
    ["AVX", "2010", "256 bits", "YMM registers, three-operand form"],
    ["AVX2", "2013", "256 bits", "integer at 256 bits, fused multiply-add, gather"],
    ["AVX-512", "2016", "512 bits", "ZMM registers, mask registers, scatter"]]})
s.obj({"id": "sat", "type": "table", "region": "center", "columns": ["8-bit pixel add", "250 + 10", "100 + 50"], "rows": [
    ["wrap-around (ordinary)", "260 mod 256 = 4: a bright pixel turns black", "150"],
    ["saturating", "clamped to 255: stays white", "150"],
    ["MMX's answer", "both, as different instructions", ""]]})
s.obj({"id": "dx", "type": "code", "region": "center", "language": "asm", "lines": [
    "      L.D     F0,a          ; the scalar a",
    "      MOV     F1,F0         ; a in 4 lanes",
    "      MOV     F2,F0",
    "      MOV     F3,F0",
    "      DADDIU  R4,Rx,#512",
    "Loop: L.4D    F4,0(Rx)      ; 4 X values",
    "      MUL.4D  F4,F4,F0",
    "      L.4D    F8,0(Ry)      ; 4 Y values",
    "      ADD.4D  F8,F8,F4",
    "      S.4D    F8,0(Ry)",
    "      DADDIU  Rx,Rx,#32     ; 32 bytes",
    "      DADDIU  Ry,Ry,#32",
    "      DSUBU   R20,R4,Rx",
    "      BNEZ    R20,Loop"]})
s.obj({"id": "dxc", "type": "table", "region": "center", "columns": ["DAXPY, 64 elements", "instructions", "how"], "rows": [
    ["MIPS (scalar)", "578", "2 + 9 × 64"],
    ["MIPS with 4-wide SIMD", "149", "5 + 9 × 16"],
    ["VMIPS (vector)", "6", "one per vector operation"]]})
s.obj({"id": "c", "type": "code", "region": "center", "language": "c", "lines": [
    "#include <immintrin.h>",
    "__m256d va = _mm256_set1_pd(a);          // a in all 4 lanes",
    "for (i = 0; i + 4 <= n; i += 4) {",
    "    __m256d x = _mm256_loadu_pd(&X[i]);",
    "    __m256d y = _mm256_loadu_pd(&Y[i]);",
    "    y = _mm256_fmadd_pd(va, x, y);        // y = a*x + y, fused",
    "    _mm256_storeu_pd(&Y[i], y);",
    "}",
    "for (; i < n; i++) Y[i] = a * X[i] + Y[i];   // leftover elements"]})
s.obj({"id": "vs", "type": "table", "region": "center", "columns": ["", "vector machine", "SIMD extension"], "rows": [
    ["vector length", "VLR, up to MVL", "fixed by the opcode"],
    ["leftovers", "a shorter last strip", "a scalar cleanup loop"],
    ["strided, indexed", "from the start", "late: AVX2, AVX-512"],
    ["masks", "from the start", "only from AVX-512"],
    ["why they won", "", "cheap, small state"]]})
s.obj({"id": "pk", "type": "math", "region": "center", "lines": [
    "\"peak\" = \"units\" times \"lanes\" times \"flops per lane\" times \"clock\"",
    "\"AVX2, 2 FMA units, 3 GHz, doubles:\" quad 2 times 4 times 2 times 3 = 48 \"GFLOP/s per core\"",
    "\"FMA counts as 2 flops: a multiply and an add\""]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["question"], "rows": [
    ["a) a 1920 × 1080 image of 8-bit pixels: how many 256-bit AVX2 adds to brighten every pixel?"],
    ["b) 200 + 100 in 8 bits, wrap-around and saturating?"],
    ["c) DAXPY on 64 doubles with 8-wide AVX-512, loop of 9, 5 setup: instructions?"],
    ["d) peak for 2 AVX-512 FMA units at 2 GHz, doubles?"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 1920 times 1080 = 2073600 \"pixels\" quad 2073600 / 32 = 64800 \"adds\"",
    "\"b)\" quad \"wrap:\" 300 \"mod\" 256 = 44 quad \"saturating:\" 255",
    "\"c)\" quad 64 / 8 = 8 \"iterations\" quad 5 + 9 times 8 = 77",
    "\"d)\" quad 2 times 8 times 2 times 2 = 64 \"GFLOP/s\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Vector supercomputers were expensive. But the idea of one instruction for many data slipped into every desktop and phone processor through a back door: multimedia. This video covers MMX, SSE and AVX.", [s.head("SIMD extensions: MMX, SSE, AVX")])
s.step("Here are the nine stages.", show("stages"))
s.step("Why ordinary processors added SIMD, partitioned registers, the history from MMX to AVX-512, and saturating arithmetic.", [hl("stages[0..=3]")])
s.step("Then DAXPY with SIMD, AVX from C, how these extensions compare with vector machines, peak performance, and an exam question.", [hl("stages[4..=8]")])

s.scene("why")
s.step("Stage 1: media data is narrow. A pixel colour is 8 bits, an audio sample 16.", [s.head("Stage 1 of 9: why SIMD in a CPU")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("A 64-bit adder can be cut into eight 8-bit adders, simply by breaking the carry chain at every 8th bit.", [hl("why[1]")])
s.step("That costs very little: little new state, and the same pipeline, caches and memory system.", [hl("why[2]")])
s.step("So one instruction does 8, 16, 32 or 64 narrow operations at once. This is SIMD, single instruction multiple data, inside an ordinary processor.", [hl("why[3]"), s.take("cut a wide register into narrow lanes")])

s.scene("lanes")
s.step("Stage 2: a 256-bit AVX register can hold 32 8-bit elements.", [s.head("Stage 2 of 9: partitioned registers"), s.untake()] + hide("why") + show("pt") + [hl("pt[0]")])
s.step("Or 16 elements of 16 bits.", [hl("pt[1]")])
s.step("Or 8 floats or 32-bit integers, or 4 doubles.", [hl("pt[2..=3]")])
s.step("The instruction says how to split it. So the number of lanes is the register width divided by the element width.", [mk("pt[3]"), s.take("lanes = register width ÷ element width")])

s.scene("hist")
s.step("Stage 3: Intel's x86 extensions grew in steps. MMX, around 1996: 64 bits, integers only, borrowing the floating-point registers.", [s.head("Stage 3 of 9: MMX to AVX-512"), s.untake()] + hide("pt") + show("hist") + [hl("hist[0]")])
s.step("SSE, 1999: new 128-bit XMM registers, and single-precision floats. SSE2 added doubles.", [hl("hist[1..=2]")])
s.step("AVX, around 2010: 256-bit YMM registers, and a three-operand form, so a result need not overwrite a source.", [hl("hist[3]")])
s.step("AVX2: 256-bit integers, fused multiply-add, and a gather instruction.", [hl("hist[4]")])
s.step("AVX-512: 512-bit ZMM registers, mask registers and scatter. Step by step, SIMD extensions acquired what vector machines had from the start. ARM followed a similar path with Neon, and then SVE.", [hl("hist[5]"), s.take("64 → 128 → 256 → 512 bits")])

s.scene("sat")
s.step("Stage 4: a detail that matters for media: overflow. Adding 10 to a pixel of 250 gives 260, which does not fit in 8 bits.", [s.head("Stage 4 of 9: saturating arithmetic"), s.untake()] + hide("hist") + show("sat") + [hl("sat[0]")])
s.step("Ordinary arithmetic wraps around: 260 mod 256 is 4. A bright white pixel suddenly turns black.", [hl("sat[0][1]")])
s.step("Saturating arithmetic clamps the result at the largest value, 255. The pixel stays white, which is what the eye expects.", [hl("sat[1]")])
s.step("MMX offered both, as different instructions. When nothing overflows, as with 100 plus 50, they agree.", [hl("sat[2]"), s.take("saturating: clamp at the maximum, never wrap")])

s.scene("daxpy")
s.step("Stage 5: DAXPY with 4-wide SIMD, written in the textbook's MIPS style. First, copy a into four registers, one per lane.", [s.head("Stage 5 of 9: DAXPY with SIMD"), s.untake()] + hide("sat") + show("dx") + [ml("dx", 1, 5)])
s.step("Each pass loads 4 X values and 4 Y values, multiplies, adds and stores 4 results.", [ml("dx", 6, 10)])
s.step("The pointers move by 32 bytes: 4 doubles. Then the usual compare and branch.", [ml("dx", 11, 14)])
s.step("Count them: 5 setup instructions, plus 9 in the loop, run 16 times. 149 instructions.", hide("dx") + show("dxc") + [hl("dxc[1]")])
s.step("Against 578 for scalar MIPS, and 6 for VMIPS. SIMD helps by the width, 4 times here, but still pays the full loop overhead every 4 elements.", [hl("dxc[0]"), hl("dxc[2]", 0.4), s.take("578 scalar · 149 SIMD · 6 vector")])

s.scene("c")
s.step("Stage 6: from C, programmers use intrinsics: functions that map to single instructions. set1 copies a into all four lanes.", [s.head("Stage 6 of 9: AVX from C"), s.untake()] + hide("dxc") + show("c") + [ml("c", 2, 2)])
s.step("The loop steps by 4: load 4 X values and 4 Y values.", [ml("c", 3, 5)])
s.step("fmadd computes a times x plus y in one fused instruction, and store writes 4 results.", [ml("c", 6, 7)])
s.step("And a scalar loop finishes the leftover elements when n is not a multiple of 4. A vector machine would just set a shorter vector length.", [ml("c", 9, 9)])
s.step("Most of the time, though, the compiler writes this for you. Auto-vectorization at optimisation level 3 turns the plain loop into exactly this code.", [s.take("intrinsics: one C call, one instruction")])

s.scene("vs")
s.step("Stage 7: SIMD extensions against true vector machines. The vector length is fixed in the opcode, so every new width needs a whole new set of instructions.", [s.head("Stage 7 of 9: against vector machines"), s.untake()] + hide("c") + show("vs") + [hl("vs[0]")])
s.step("There is no vector length register, so leftover elements need scalar cleanup code.", [hl("vs[1]")])
s.step("Strided and indexed access, and masks, came late: gather in AVX2, scatter and masks only in AVX-512.", [hl("vs[2..=3]")])
s.step("Why did they win anyway? They are cheap to add, add little state for the operating system to save, and need no special memory system. Every laptop and phone has them.", [hl("vs[4]"), s.take("less capable than vectors, but everywhere")])

s.scene("peak")
s.step("Stage 8: peak performance. Multiply the number of SIMD units, the lanes, the flops per lane, and the clock.", [s.head("Stage 8 of 9: peak performance"), s.untake()] + hide("vs") + show("pk") + [hl("pk[0]")])
s.step("A core with two AVX2 fused multiply-add units at 3 gigahertz, on doubles: 2 times 4 lanes times 2 flops times 3. 48 gigaflops per core.", [rv("pk[1]"), hl("pk[1]")])
s.step("A fused multiply-add counts as two flops, a multiply and an add. Exam questions often hinge on that factor of two. And peak is rarely reached: memory usually limits it first, the subject of the next video.", [rv("pk[2]"), hl("pk[2]"), s.take("peak = units × lanes × flops × clock")])

s.scene("exam")
s.step("Now an exam question in four parts.", [s.head("Exam question"), s.untake()] + hide("pk") + show("q"))
s.step("The number of 256-bit adds to brighten a full HD image of 8-bit pixels. 200 plus 100 in 8 bits, both ways. DAXPY instructions on 8-wide AVX-512. And the peak of two AVX-512 units at 2 gigahertz. Pause and work it out.", [hl("q")])
s.step("a: 1920 times 1080 is about 2.07 million pixels. A 256-bit register holds 32 of them: 64,800 adds.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 300 does not fit. Wrap-around gives 300 mod 256, 44. Saturating gives 255.", [rv("qa[1]"), hl("qa[1]")])
s.step("c: 64 doubles, 8 per register: 8 passes of the loop. 5 plus 9 times 8: 77 instructions.", [rv("qa[2]"), hl("qa[2]")])
s.step("d: 2 units, 8 doubles each, 2 flops per fused multiply-add, at 2 gigahertz: 64 gigaflops.", [rv("qa[3]"), hl("qa[3]")])
s.step("The usual slip: using the register width in bits as the lane count. Divide by the element width first: 256 bits is 32 bytes, 4 doubles.", [s.take("256 bits = 32 pixels = 4 doubles")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("SIMD extensions cut a wide register into narrow lanes, from MMX's 64 bits to AVX-512's 512, with saturating arithmetic for media.", [hl("stages[0..=3]")])
s.step("DAXPY drops from 578 instructions to 149 with 4-wide SIMD. Fixed widths and cleanup loops make them weaker than vector machines, but they are everywhere.", [hl("stages[4..=7]")])
s.step("Next video: a model that tells you whether a loop is limited by arithmetic or by memory. The roofline.", [mk("stages[0..=8]"), s.take("Next: the roofline model")])

s.save("/home/claude/playlist/m4/m4v9.json")

"""Module 4, video 10: the roofline performance model."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

roof = lambda peak, bw, i: min(peak, bw * i)
assert round(2 / 24, 3) == 0.083 and round(16 * 2 / 24, 2) == 1.33
P, B = 64, 16                       # the example machine: 64 GFLOP/s, 16 GB/s, ridge 4
assert P / B == 4
K = [("DAXPY", 2 / 24), ("sparse matrix-vector", 0.25), ("stencil", 0.5), ("FFT", 2), ("dense matrix multiply", 8)]
KV = [(n, round(i, 3), roof(P, B, i)) for n, i in K]
assert [round(v, 2) for _, _, v in KV] == [1.33, 4, 8, 32, 64]
# textbook machines (H&P): NEC SX-9 102.4 GFLOP/s, 162 GB/s; Core i7 920 42.66 GFLOP/s, 16.4 GB/s
assert round(102.4 / 162, 2) == 0.63 and round(42.66 / 16.4, 2) == 2.6
assert round(162 * 2 / 24, 1) == 13.5 and round(16.4 * 2 / 24, 2) == 1.37
# exam: peak 200, BW 50
assert 200 / 50 == 4 and roof(200, 50, 0.5) == 25 and roof(200, 50, 8) == 200
assert 3 / 24 == 0.125 and roof(200, 50, 0.125) == 6.25 and 200 / 0.5 == 400
assert roof(200, 50, 2) == 100

assert 5 / 16 == 0.3125 and 3 / 16 == 0.1875 and 3 / 32 == 0.09375
s = Script("The roofline model")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Two limits: arithmetic and memory"],
    [2, "Arithmetic intensity"],
    [3, "Counting intensity"],
    [4, "The roofline formula"],
    [5, "Drawing the roofline"],
    [6, "Kernels on the roofline"],
    [7, "Two real machines"],
    [8, "Ceilings, and how to climb"],
    [9, "Exam question"]]})
s.obj({"id": "lim", "type": "table", "region": "center", "columns": ["a kernel can be limited by", "measured in"], "rows": [
    ["how fast the processor computes", "peak GFLOP/s: lanes × units × clock"],
    ["how fast memory delivers data", "peak bandwidth: GB/s from DRAM"],
    ["which one?", "depends on how much arithmetic each byte supports"]]})
s.obj({"id": "ai", "type": "math", "region": "center", "lines": [
    "\"arithmetic intensity\" I = \"floating-point operations\" / \"bytes moved to or from DRAM\"",
    "\"DAXPY:\" quad Y_i = a X_i + Y_i quad 2 \"flops\" quad \"read\" X_i, Y_i, \"write\" Y_i : 3 times 8 = 24 \"bytes\"",
    "I_\"DAXPY\" = 2 / 24 approx 0.083 \"flops per byte\"",
    "\"dense matrix multiply:\" I \"grows with the matrix size: data is reused many times\""]})
s.obj({"id": "cnt", "type": "code", "region": "center", "language": "c", "lines": [
    "// (1) a polynomial: 3 multiplies, 2 adds = 5 flops",
    "y[i] = a*x[i]*x[i] + b*x[i] + c;      // DRAM: read x, write y = 16 bytes",
    "",
    "// (2) a 3-point average: 2 adds, 1 multiply = 3 flops",
    "B[i] = (A[i-1] + A[i] + A[i+1]) * third;"]})
s.obj({"id": "cntm", "type": "math", "region": "center", "lines": [
    "(1) quad I = 5 / 16 approx 0.31",
    "(2) \" with cache reuse: each A read from DRAM once:\" quad 3 / (8 + 8) approx 0.19",
    "(2) \" without reuse: 3 reads + 1 write:\" quad 3 / 32 approx 0.094"]})
s.obj({"id": "rf", "type": "math", "region": "center", "lines": [
    "\"attainable GFLOP/s\" = min(\"peak GFLOP/s\", quad \"bandwidth\" times I)",
    "\"ridge point:\" quad I_\"ridge\" = \"peak\" / \"bandwidth\"",
    "I < I_\"ridge\": \"memory-bound\" quad quad I > I_\"ridge\": \"compute-bound\""]})
s.obj({"id": "rp", "type": "plot", "region": "center",
       "x": {"label": "log₂ of intensity: −4 is 1/16, 0 is 1, 4 is 16 flops per byte", "min": -4, "max": 4},
       "y": {"label": "log₂ of GFLOP/s: 6 is 64", "min": -1, "max": 7},
       "curves": [{"id": "roof", "points": [[-4, 0], [2, 6], [4, 6]], "label": "roof", "visible": False}],
       "points": [{"id": "ridge", "at": [2, 6], "label": "ridge"},
                  {"id": "dax", "at": [-3.585, 0.415], "label": "DAXPY"},
                  {"id": "spmv", "at": [-2, 2], "label": "SpMV"},
                  {"id": "fft", "at": [1, 5], "label": "FFT"},
                  {"id": "mm", "at": [3, 6], "label": "matmul"}]})
s.obj({"id": "kt", "type": "table", "region": "center", "columns": ["kernel", "I (flops/byte)", "16 × I", "attainable", "bound by"], "rows": [
    [n, f"{i:g}", f"{B * i:.2f}".rstrip('0').rstrip('.'), f"{v:.2f}".rstrip('0').rstrip('.'), "memory" if i < 4 else "compute"] for n, i, v in KV]})
s.obj({"id": "rm", "type": "table", "region": "center", "columns": ["textbook machine", "peak", "bandwidth", "ridge", "DAXPY attains"], "rows": [
    ["NEC SX-9 (vector)", "102.4 GFLOP/s", "162 GB/s", "0.63", "162 × 0.083 = 13.5"],
    ["Intel Core i7 920", "42.66 GFLOP/s", "16.4 GB/s", "2.6", "16.4 × 0.083 = 1.37"]]})
s.obj({"id": "ce", "type": "table", "region": "center", "columns": ["ceiling", "lowers", "climb past it by"], "rows": [
    ["no SIMD", "the compute roof", "vectorizing the loop"],
    ["unbalanced multiply and add", "the compute roof", "using fused multiply-add"],
    ["no prefetching, poor locality", "the memory slope", "prefetching, unit-stride access"],
    ["low intensity itself", "where the kernel sits", "blocking and reuse: raise I"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["a machine: peak 200 GFLOP/s, bandwidth 50 GB/s"], "rows": [
    ["a) the ridge point"],
    ["b) attainable GFLOP/s for kernels with I = 0.5, 2 and 8"],
    ["c) a kernel with 3 flops per element that reads 2 doubles and writes 1: its I and GFLOP/s"],
    ["d) the bandwidth needed for the I = 0.5 kernel to reach peak"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 200 / 50 = 4 \"flops per byte\"",
    "\"b)\" quad min(200, 50 times 0.5) = 25 quad min(200, 100) = 100 quad min(200, 400) = 200",
    "\"c)\" quad I = 3 / 24 = 0.125 quad 50 times 0.125 = 6.25 \"GFLOP/s: memory-bound\"",
    "\"d)\" quad 200 / 0.5 = 400 \"GB/s\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Last video's AVX core could do 48 gigaflops. Will DAXPY get anywhere near that? Almost never. The roofline model, from Williams, Waterman and Patterson in 2009, tells you in one picture what limits a loop, and how fast it can possibly run.", [s.head("The roofline model")])
s.step("Here are the nine stages.", show("stages"))
s.step("The two limits, arithmetic intensity and how to count it, the formula, and drawing the roofline.", [hl("stages[0..=4]")])
s.step("Then where real kernels sit on it, two real machines, how to climb, and an exam question.", [hl("stages[5..=8]")])

s.scene("lim")
s.step("Stage 1: a loop can be limited by how fast the processor computes: its peak floating-point rate.", [s.head("Stage 1 of 9: two limits")] + hide("stages") + show("lim") + [hl("lim[0]")])
s.step("Or by how fast memory delivers the data: its peak bandwidth from DRAM, in gigabytes per second.", [hl("lim[1]")])
s.step("Which limit bites depends on the loop: how many operations it performs for each byte it moves.", [hl("lim[2]"), s.take("compute or memory: whichever runs out first")])

s.scene("ai")
s.step("Stage 2: arithmetic intensity is the floating-point operations divided by the bytes moved to or from main memory.", [s.head("Stage 2 of 9: arithmetic intensity"), s.untake()] + hide("lim") + show("ai") + [hl("ai[0]")])
s.step("DAXPY: each element needs a multiply and an add, 2 flops. It reads X and Y, and writes Y: 3 doubles, 24 bytes.", [rv("ai[1]"), hl("ai[1]")])
s.step("So its intensity is 2 over 24, about 0.083 flops per byte. Very low: one operation for every 12 bytes.", [rv("ai[2]"), hl("ai[2]")])
s.step("Dense matrix multiplication is the opposite. Each element is reused many times from the caches, so the intensity grows with the matrix size.", [rv("ai[3]"), hl("ai[3]"), s.take("I = flops ÷ DRAM bytes")])

s.scene("cnt")
s.step("Stage 3: count intensity for two more loops. A polynomial: three multiplies and two adds, 5 flops. It reads x and writes y: 16 bytes.", [s.head("Stage 3 of 9: counting intensity"), s.untake()] + hide("ai") + show("cnt") + [{"action": "mark_lines", "target": "cnt", "from": 1, "to": 2}])
s.step("A 3-point average: two adds and a multiply by a third, 3 flops per element.", [{"action": "mark_lines", "target": "cnt", "from": 4, "to": 5}])
s.step("The polynomial: 5 over 16, about 0.31 flops per byte.", hide("cnt") + show("cntm") + [hl("cntm[0]")])
s.step("The average reads three neighbours of A. But A of i plus 1 for this element is A of i for the next one, so with a cache each A comes from DRAM once. 3 flops over 8 bytes read and 8 written: about 0.19.", [rv("cntm[1]"), hl("cntm[1]")])
s.step("Without that reuse, every access goes to DRAM: 32 bytes, and only 0.094. The cache doubled the intensity. Count what reaches DRAM, not what the code mentions.", [rv("cntm[2]"), hl("cntm[2]"), s.take("count DRAM bytes, after cache reuse")])

s.scene("rf")
s.step("Stage 4: the formula. Attainable performance is the smaller of two numbers: the peak, and the bandwidth times the intensity.", [s.head("Stage 3 of 9: the formula"), s.untake()] + hide("cntm") + show("rf") + [hl("rf[0]")])
s.step("Bandwidth times intensity is how fast memory can feed operations: gigabytes per second, times flops per byte, gives flops per second.", [hl("rf[0]")])
s.step("The two are equal at the ridge point: the peak divided by the bandwidth.", [rv("rf[1]"), hl("rf[1]")])
s.step("A kernel to the left of the ridge is memory-bound: a faster processor would not help it. To the right, it is compute-bound: more bandwidth would not help.", [rv("rf[2]"), hl("rf[2]"), s.take("attainable = min(peak, BW × I)")])

s.scene("draw")
s.step("Stage 5: draw it for a machine with a 64 gigaflop peak and 16 gigabytes per second of bandwidth.", [s.head("Stage 4 of 9: drawing the roofline"), s.untake()] + hide("rf") + show("rp") + [{"action": "trace", "target": "rp.roof"}])
s.step("Both axes are logarithmic, the usual way to draw it, so the memory roof, 16 times I, becomes a straight slanted line. Each step right doubles the intensity; each step up doubles the performance.", [hl("rp.roof")])
s.step("The flat part is the compute roof, at 64 gigaflops, 2 to the 6.", [hl("rp.roof")])
s.step("They meet at the ridge, at 4 flops per byte. A loop needs at least 4 flops for every byte it moves to reach peak.", [hl("rp.ridge"), s.take("slope: bandwidth · flat: peak · corner: ridge")])

s.scene("kern")
s.step("Stage 6: place some kernels. DAXPY, at 0.083, attains just 16 times 0.083: 1.3 gigaflops. 2 percent of peak.", [s.head("Stage 5 of 9: kernels"), s.untake()] + [hl("rp.dax")])
s.step("Sparse matrix-vector product, about 0.25 flops per byte: 4 gigaflops. Still deep in memory-bound territory.", [hl("rp.spmv")])
s.step("An FFT, about 2: 32 gigaflops, half of peak.", [hl("rp.fft")])
s.step("And a large dense matrix multiply, intensity 8 or more: it reaches the full 64.", [hl("rp.mm")])
s.step("In a table: everything left of the ridge is limited by memory, whatever the arithmetic hardware. Most real loops live there.", hide("rp") + show("kt") + [hl("kt[0..=3]"), hl("kt[4]", 0.5), s.take("most kernels are memory-bound")])

s.scene("real")
s.step("Stage 7: the textbook compares two real machines. NEC's SX-9 vector computer: 102.4 gigaflops, but a huge 162 gigabytes per second of memory bandwidth. Its ridge is at only 0.63.", [s.head("Stage 6 of 9: two real machines"), s.untake()] + hide("kt") + show("rm") + [hl("rm[0]")])
s.step("An Intel Core i7 920: 42.66 gigaflops, with 16.4 gigabytes per second. Its ridge is at 2.6.", [hl("rm[1]")])
s.step("On DAXPY, the SX-9 attains 13.5 gigaflops, the Core i7 just 1.37. Ten times faster, though its peak is only 2.4 times higher. Vector machines were built around memory bandwidth, and on memory-bound loops that is what counts.", [hl("rm[0][4]"), s.take("a low ridge point: a balanced machine")])

s.scene("ceil")
s.step("Stage 8: a real program rarely reaches even its roofline. Lower ceilings sit beneath the roofs. Without SIMD, the compute roof drops by the number of lanes.", [s.head("Stage 7 of 9: ceilings"), s.untake()] + hide("rm") + show("ce") + [hl("ce[0]")])
s.step("Without fused multiply-adds, or with an unbalanced mix, it drops again.", [hl("ce[1]")])
s.step("Poor locality, or no prefetching, lowers the memory slope.", [hl("ce[2]")])
s.step("And the kernel's own intensity decides where it sits. Blocking a loop so that data is reused from cache raises I, and moves the kernel to the right, toward the compute roof.", [hl("ce[3]"), s.take("vectorize to raise the roof · reuse data to raise I")])

s.scene("exam")
s.step("Now an exam question: a machine with a 200 gigaflop peak and 50 gigabytes per second.", [s.head("Exam question"), s.untake()] + hide("ce") + show("q") + [hl("q[0]")])
s.step("Find the ridge, the attainable rate for intensities 0.5, 2 and 8, the intensity and rate of a kernel with 3 flops per element reading 2 doubles and writing 1, and the bandwidth the 0.5 kernel would need to reach peak. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: 200 over 50: the ridge is at 4 flops per byte.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: at 0.5, 50 times 0.5 is 25 gigaflops. At 2, 100. At 8, 400 exceeds the peak, so 200.", [rv("qa[1]"), hl("qa[1]")])
s.step("c: 3 flops for 3 doubles, 24 bytes: intensity 0.125. 50 times 0.125: 6.25 gigaflops, memory-bound.", [rv("qa[2]"), hl("qa[2]")])
s.step("d: to reach 200 at intensity 0.5 needs 200 over 0.5: 400 gigabytes per second, eight times the bandwidth.", [rv("qa[3]"), hl("qa[3]")])
s.step("The usual slip: counting bytes that come from cache. Arithmetic intensity counts only the traffic to main memory.", [s.take("I counts DRAM traffic only")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Arithmetic intensity is flops per byte of DRAM traffic. Attainable performance is the minimum of the peak and the bandwidth times the intensity.", [hl("stages[0..=4]")])
s.step("Kernels left of the ridge are memory-bound, and most are. Vectorizing raises the roof; reusing data raises the intensity.", [hl("stages[5..=7]")])
s.step("Next video: graphics processors. CUDA, and the hierarchy of threads, blocks and grids.", [mk("stages[0..=8]"), s.take("Next: GPUs and CUDA")])

s.save("/home/claude/playlist/m4/m4v10.json")

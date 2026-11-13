"""Module 4, video 19: CUDA programming, part 2."""
import sys
import numpy as np
sys.path.insert(0, "/home/claude/playlist")
from common import Script

# tree reduction trace
s8 = [3, 1, 4, 1, 5, 9, 2, 6]; tr = []
h = 4
while h:
    for t in range(h): s8[t] += s8[t + h]
    tr.append(s8[:h]); h //= 2
assert tr == [[8, 10, 6, 7], [14, 17], [31]] and sum([3, 1, 4, 1, 5, 9, 2, 6]) == 31
# tiled matmul equals A @ B
rng = np.random.default_rng(1); N, T = 8, 4
A, B = rng.integers(0, 5, (N, N)), rng.integers(0, 5, (N, N)); C = np.zeros((N, N), int)
for by in range(N // T):
    for bx in range(N // T):
        acc = np.zeros((T, T), int)
        for t in range(N // T):
            As = A[by*T:(by+1)*T, t*T:(t+1)*T]; Bs = B[t*T:(t+1)*T, bx*T:(bx+1)*T]
            acc += As @ Bs
        C[by*T:(by+1)*T, bx*T:(bx+1)*T] = acc
assert (C == A @ B).all()
# intensities and bounds (floats, 4 bytes)
assert 2 / 8 == 0.25 and 2 * 16 / 8 == 4 and 0.25 * 224 == 56 and 4 * 224 == 896
assert round(2 * 2048**3 / 40e-3 / 1e9, 1) == 429.5 and round(2 * 2048**3 / 8e-3 / 1e9) == 2147
# exam
assert 2 * 32 * 32 * 4 == 8192 and 2 * 1024 == 2048 and 2 * 1024 // 32 == 64
assert 2 * 32 / 8 == 8 and 8 * 300 == 2400 and round(2 * 1024**3 / 4e-3 / 1e9, 1) == 536.9
assert (1024 // 32) ** 2 == 1024 and 32 * 32 == 1024

s = Script("CUDA programming 2")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Threads that cooperate"],
    [2, "__syncthreads: a barrier"],
    [3, "Summing a block in shared memory"],
    [4, "Timing with CUDA events"],
    [5, "Matrix multiply, the simple way"],
    [6, "Tiles in shared memory"],
    [7, "Why two barriers"],
    [8, "How much it helps"],
    [9, "Exam question"]]})
s.obj({"id": "co", "type": "table", "region": "center", "columns": ["", "why"], "rows": [
    ["so far", "each thread worked alone on its own element"],
    ["many problems need sharing", "sums, matrix products, stencils, sorting"],
    ["threads of one block can share", "shared memory, on the same SM"],
    ["but they run at different speeds", "warps are scheduled independently"],
    ["so they need a way to wait", "until the shared data is ready"]]})
s.obj({"id": "sy", "type": "table", "region": "center", "columns": ["__syncthreads()", "meaning"], "rows": [
    ["a barrier for one block", "no thread passes until every thread of the block arrives"],
    ["after it", "every write to shared memory before it is visible"],
    ["only within a block", "blocks cannot wait for each other inside a kernel"],
    ["every thread must reach it", "never inside a branch some threads skip: the block can hang"]]})
s.obj({"id": "rd", "type": "code", "region": "center", "language": "c", "lines": [
    "__global__ void block_sum(const float *x, float *out) {",
    "    __shared__ float s[256];",
    "    int t = threadIdx.x;",
    "    s[t] = x[blockIdx.x * 256 + t];",
    "    __syncthreads();                      // all 256 loaded",
    "    for (int h = 128; h > 0; h /= 2) {",
    "        if (t < h) s[t] += s[t + h];      // fold the top half onto the bottom",
    "        __syncthreads();                  // outside the if: every thread reaches it",
    "    }",
    "    if (t == 0) out[blockIdx.x] = s[0];",
    "}"]})
s.obj({"id": "rt", "type": "table", "region": "center", "columns": ["8 values", "s[0]", "s[1]", "s[2]", "s[3]", "s[4]", "s[5]", "s[6]", "s[7]"], "rows": [
    ["loaded", "3", "1", "4", "1", "5", "9", "2", "6"],
    ["h = 4", "", "", "", "", "", "", "", ""],
    ["h = 2", "", "", "", "", "", "", "", ""],
    ["h = 1", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "ev", "type": "code", "region": "center", "language": "c", "lines": [
    "cudaEvent_t start, stop;",
    "cudaEventCreate(&start);  cudaEventCreate(&stop);",
    "cudaEventRecord(start);               // a marker in the GPU's queue",
    "mm<<<grid, block>>>(A, B, C, N);",
    "cudaEventRecord(stop);",
    "cudaEventSynchronize(stop);           // wait until the GPU reaches stop",
    "float ms;  cudaEventElapsedTime(&ms, start, stop);",
    "// GFLOP/s = 2 N^3 / (ms × 10^6):  N = 2048, 40 ms → 429.5"]})
s.obj({"id": "nv", "type": "code", "region": "center", "language": "c", "lines": [
    "__global__ void mm(const float *A, const float *B, float *C, int N) {",
    "    int row = blockIdx.y * blockDim.y + threadIdx.y;",
    "    int col = blockIdx.x * blockDim.x + threadIdx.x;",
    "    float sum = 0;",
    "    for (int k = 0; k < N; k++)",
    "        sum += A[row * N + k] * B[k * N + col];   // 2 loads, 2 FLOPs",
    "    C[row * N + col] = sum;",
    "}",
    "// 2 FLOPs per 8 bytes from global memory: 0.25 FLOP/byte"]})
s.obj({"id": "tl", "type": "code", "region": "center", "language": "c", "lines": [
    "#define T 16",
    "__shared__ float As[T][T], Bs[T][T];",
    "int tx = threadIdx.x, ty = threadIdx.y;",
    "int row = blockIdx.y * T + ty, col = blockIdx.x * T + tx;",
    "for (int t = 0; t < N / T; t++) {",
    "    As[ty][tx] = A[row * N + t * T + tx];     // each thread loads one of A",
    "    Bs[ty][tx] = B[(t * T + ty) * N + col];   // and one of B",
    "    __syncthreads();                          // the tiles are complete",
    "    for (int k = 0; k < T; k++)",
    "        sum += As[ty][k] * Bs[k][tx];         // 16 multiply-adds from shared",
    "    __syncthreads();                          // everyone is done with the tiles",
    "}"]})
s.obj({"id": "tw", "type": "table", "region": "center", "columns": ["without", "what goes wrong"], "rows": [
    ["the first barrier", "a fast warp reads As and Bs before slower warps have loaded them"],
    ["the second barrier", "a fast warp starts the next tile and overwrites As and Bs while others still read them"],
    ["both", "wrong answers that change from run to run: a race"]]})
s.obj({"id": "hm", "type": "math", "region": "center", "lines": [
    "\"simple: 2 FLOPs per 8 bytes\" = 0.25 \"FLOP/byte\"",
    "\"tiled, T = 16: per tile, 2 loads (8 bytes) feed 16 multiply-adds (32 FLOPs)\": quad 4 \"FLOP/byte\"",
    "\"at 224 GB/s:\" quad 0.25 times 224 = 56 quad \"against\" quad 4 times 224 = 896 \"GFLOP/s\"",
    "\"global traffic falls by a factor of\" T = 16"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["tiled matrix multiply, N = 1024 floats, T = 32"], "rows": [
    ["a) shared memory per block"],
    ["b) global loads per thread: simple, and tiled"],
    ["c) arithmetic intensity, and the bound at 300 GB/s"],
    ["d) CUDA events measure 4 ms: the GFLOP/s achieved"],
    ["e) the second __syncthreads is deleted: what happens?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "2 tiles × 32 × 32 × 4 bytes", "8 KB"],
    ["b", "simple: 2 × 1024 · tiled: 2 × 1024 / 32", "2048 and 64"],
    ["c", "2 loads (8 B) feed 32 multiply-adds (64 FLOPs)", "8 FLOP/byte → 2400 GFLOP/s"],
    ["d", "2 × 1024³ / 0.004 s", "536.9 GFLOP/s"],
    ["e", "a fast warp overwrites a tile still being read", "a race: wrong, varying results"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("In part 1, every thread worked alone. The fastest CUDA programs make threads work together, sharing data through on-chip memory. This video shows how, and how to measure whether it helped.", [s.head("CUDA programming, part 2")])
s.step("Here are the nine stages.", show("stages"))
s.step("Why threads cooperate, the barrier syncthreads, a block sum in shared memory, and timing with CUDA events.", [hl("stages[0..=3]")])
s.step("Then matrix multiply, the simple way and with shared-memory tiles, why it needs two barriers, how much it helps, and an exam question.", [hl("stages[4..=8]")])

s.scene("co")
s.step("Stage 1: so far, each thread worked alone on its own element.", [s.head("Stage 1 of 9: threads that cooperate")] + hide("stages") + show("co") + [hl("co[0]")])
s.step("Many problems need sharing: a sum, a matrix product, a stencil, a sort.", [hl("co[1]")])
s.step("Threads of one block live on the same SM, so they can share its shared memory.", [hl("co[2]")])
s.step("But their warps are scheduled independently, and run at different speeds.", [hl("co[3]")])
s.step("So a thread that wants another thread's value needs a way to wait until it has been written.", [hl("co[4]"), s.take("sharing needs waiting")])

s.scene("sync")
s.step("Stage 2: double-underscore syncthreads is a barrier for one block. No thread passes it until every thread of the block has arrived.", [s.head("Stage 2 of 9: a barrier"), s.untake()] + hide("co") + show("sy") + [hl("sy[0]")])
s.step("After it, every write to shared memory made before the barrier is visible to the whole block.", [hl("sy[1]")])
s.step("It works only within a block. Different blocks cannot wait for each other inside a kernel; to combine results across blocks, launch another kernel.", [hl("sy[2]")])
s.step("And every thread of the block must reach the same barrier. Put it inside an if that some threads skip, and the block can hang forever.", [hl("sy[3]"), s.take("__syncthreads: the whole block waits")])

s.scene("red")
s.step("Stage 3: summing 256 values per block. Each thread loads one value into shared memory, then a barrier: all 256 are loaded.", [s.head("Stage 3 of 9: a block sum"), s.untake()] + hide("sy") + show("rd") + [ml("rd", 1, 5)])
s.step("Then a loop that halves h each time. Threads below h add the value h places above them: the top half folds onto the bottom.", [ml("rd", 6, 7)])
s.step("A barrier after every step, placed outside the if so that all threads reach it.", [ml("rd", 8, 8)])
s.step("After 8 steps, log base 2 of 256, the block's sum is in s of 0, and thread 0 writes it out.", [ml("rd", 10, 10)])
s.step("Trace it with 8 values: 3, 1, 4, 1, 5, 9, 2, 6.", hide("rd") + show("rt") + [hl("rt[0]")])
s.step("h equal to 4: threads 0 to 3 add the value 4 places up. 3 plus 5 is 8, 1 plus 9 is 10, 4 plus 2 is 6, 1 plus 6 is 7.", [st("rt[1][1]", "8"), st("rt[1][2]", "10", 0.15), st("rt[1][3]", "6", 0.3), st("rt[1][4]", "7", 0.45), hl("rt[1]", 0.6)])
s.step("h equal to 2: 8 plus 6 is 14, 10 plus 7 is 17.", [st("rt[2][1]", "14"), st("rt[2][2]", "17", 0.2), hl("rt[2]", 0.4)])
s.step("h equal to 1: 14 plus 17 is 31, the sum of all eight. Three steps for 8 values: the tree from the reductions in video 17.", [st("rt[3][1]", "31"), mk("rt[3][1]", 0.3), s.take("a tree in shared memory, a barrier per level")])

s.scene("ev")
s.step("Stage 4: how fast is a kernel? A CPU timer around the launch measures nothing, because the launch returns at once. CUDA events are timestamps recorded by the GPU itself.", [s.head("Stage 4 of 9: timing with events"), s.untake()] + hide("rt") + show("ev") + [ml("ev", 1, 2)])
s.step("Record start, launch the kernel, record stop. Each record puts a marker in the GPU's queue.", [ml("ev", 3, 5)])
s.step("Wait until the GPU reaches the stop marker, then ask for the time between them, in milliseconds.", [ml("ev", 6, 7)])
s.step("Turn time into a rate. A matrix multiply does 2 N cubed floating-point operations. With N equal to 2048 and 40 milliseconds: 429.5 gigaflops per second. Compare it with the roofline.", [ml("ev", 8, 8), s.take("events: GPU timestamps around the kernel")])

s.scene("naive")
s.step("Stage 5: matrix multiply, the simple way. One thread per element of C, with a 2-D grid.", [s.head("Stage 5 of 9: the simple matrix multiply"), s.untake()] + hide("ev") + show("nv") + [ml("nv", 1, 4)])
s.step("Each thread walks a row of A and a column of B. Neighbouring threads share the row and read neighbouring columns of B, so the loads are coalesced.", [ml("nv", 5, 6)])
s.step("But every multiply-add needs two loads from global memory: 2 floating-point operations per 8 bytes, 0.25 per byte. Deep in the memory-bound part of the roofline.", [ml("nv", 9, 9)])
s.step("And it is wasteful: every element of A is loaded N times, once by each thread in its row of C.", [s.take("simple: 0.25 FLOP/byte, each value loaded N times")])

s.scene("tile")
s.step("Stage 6: tiling. A block of 16 by 16 threads computes a 16 by 16 tile of C, and keeps 16 by 16 tiles of A and B in shared memory.", [s.head("Stage 6 of 9: tiles in shared memory"), s.untake()] + hide("nv") + show("tl") + [ml("tl", 1, 4)])
s.step("The outer loop walks across: one tile of A and one tile of B at a time.", [ml("tl", 5, 5)])
s.step("Each thread loads one element of each tile. 256 threads, 256 elements: the tiles are loaded in one step, with coalesced reads.", [ml("tl", 6, 7)])
s.step("A barrier: the tiles must be complete before anyone uses them.", [ml("tl", 8, 8)])
s.step("Now each thread does 16 multiply-adds, reading only from shared memory.", [ml("tl", 9, 10)])
s.step("And a second barrier before the next tile is loaded.", [ml("tl", 11, 11), s.take("load a tile · sync · compute · sync")])

s.scene("two")
s.step("Stage 7: why two barriers? Without the first, a fast warp could read As and Bs before slower warps have loaded their parts.", [s.head("Stage 7 of 9: why two barriers"), s.untake()] + hide("tl") + show("tw") + [hl("tw[0]")])
s.step("Without the second, a fast warp would start the next tile and overwrite As and Bs while other warps are still reading the old values.", [hl("tw[1]")])
s.step("Either way the result is a race: wrong answers that change from run to run, which are hard to find. Every reuse of shared memory needs a barrier before and after.", [hl("tw[2]"), s.take("barrier before reading, barrier before overwriting")])

s.scene("help")
s.step("Stage 8: how much does it help? The simple version: 2 operations per 8 bytes, 0.25 per byte.", [s.head("Stage 8 of 9: how much it helps"), s.untake()] + hide("tw") + show("hm") + [hl("hm[0]")])
s.step("Tiled: per tile, each thread loads 2 values, 8 bytes, and does 16 multiply-adds, 32 operations. 4 per byte: 16 times better.", [rv("hm[1]"), hl("hm[1]")])
s.step("At 224 gigabytes per second, the roofline allows 56 gigaflops for the simple version, and 896 for the tiled one.", [rv("hm[2]"), hl("hm[2]")])
s.step("In general, tiles of size T cut global traffic by a factor of T. Bigger tiles help more, until shared memory or registers run out and occupancy falls. Measure with events to find the best.", [rv("hm[3]"), hl("hm[3]"), s.take("tiling multiplies intensity by T")])

s.scene("exam")
s.step("Now an exam question: tiled matrix multiply, N equal to 1024 floats, with tiles of 32.", [s.head("Exam question"), s.untake()] + hide("hm") + show("q") + [hl("q[0..=2]")])
s.step("Find the shared memory per block, the global loads per thread, the intensity and its bound at 300 gigabytes per second, the rate if events measure 4 milliseconds, and what happens without the second barrier. Pause and work it out.", [hl("q[3..=4]")])
s.step("a: two tiles of 32 by 32 floats, 4 bytes each: 8 kilobytes.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: the simple version loads a row and a column, 2 times 1024 values per thread. Tiled, 32 tiles, 2 loads each: 64.", [hl("qa[1]")])
s.step("c: per tile, 8 bytes feed 32 multiply-adds, 64 operations: 8 per byte. At 300 gigabytes per second, the bound is 2400 gigaflops.", [hl("qa[2]")])
s.step("d: 2 times 1024 cubed is about 2.15 billion operations, in 4 milliseconds: 536.9 gigaflops per second.", [hl("qa[3]"), mk("qa[3][2]", 0.4)])
s.step("e: a fast warp loads the next tile while others still read the current one. A race: wrong results that vary.", [hl("qa[4]")])
s.step("The usual slip: putting syncthreads inside if t less than h in the reduction. Threads that skip it never arrive, and the block can hang.", [s.take("barriers outside branches")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Threads of a block share data through shared memory, and syncthreads makes them wait for each other. A block sum is a tree with a barrier per level. CUDA events time kernels on the GPU.", [hl("stages[0..=3]")])
s.step("Tiled matrix multiply loads each tile once into shared memory and reuses it T times, with a barrier before and after. That multiplies the intensity by T.", [hl("stages[4..=7]")])
s.step("Next video, the last of the module: a real GPU. The NVIDIA Maxwell architecture.", [mk("stages[0..=8]"), s.take("Next: case study, NVIDIA Maxwell")])

s.save("/home/claude/playlist/m4/m4v19.json")

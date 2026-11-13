"""Module 4, video 11: GPUs, CUDA, and the thread hierarchy."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

cdiv = lambda a, b: -(-a // b)
assert 16 * 512 == 8192 and cdiv(8192, 512) == 16
assert 3 * 256 + 5 == 773
assert cdiv(1000, 256) == 4 and 4 * 256 - 1000 == 24
assert cdiv(5000, 128) == 40 and 40 * 128 == 5120 and 5120 - 5000 == 120
assert 7 * 128 + 100 == 996 and divmod(4321, 128) == (33, 97)
assert cdiv(1920, 16) == 120 and cdiv(1080, 16) == 68 and 120 * 68 == 8160
assert divmod(500, 16) == (31, 4) and divmod(300, 16) == (18, 12)
assert cdiv(640, 16) == 40 and cdiv(480, 16) == 30 and divmod(100, 16) == (6, 4) and divmod(50, 16) == (3, 2)

s = Script("GPUs and CUDA")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "From graphics to general computing"],
    [2, "The heterogeneous model: host and device"],
    [3, "DAXPY in CUDA"],
    [4, "Threads, blocks and grids"],
    [5, "Which thread does which element"],
    [6, "Two-dimensional grids"],
    [7, "CUDA in vector terms"],
    [8, "Exam question"]]})
s.obj({"id": "hist", "type": "table", "region": "center", "columns": ["", "meaning"], "rows": [
    ["GPUs were built for", "graphics: millions of pixels, each computed the same way"],
    ["that is", "data-level parallelism on a huge scale"],
    ["CUDA (NVIDIA, 2007)", "an extension of C to program the GPU for any computation"],
    ["also", "OpenCL, an open standard on the same model"]]})
s.obj({"id": "het", "type": "table", "region": "center", "columns": ["", "host", "device"], "rows": [
    ["is", "the CPU", "the GPU"],
    ["memory", "main memory", "its own GPU memory"],
    ["runs", "the serial program", "kernels: functions run by many threads at once"],
    ["marked", "__host__", "__global__ (called from the host, runs on the device)"]]})
s.obj({"id": "code", "type": "code", "region": "center", "language": "c", "lines": [
    "// the kernel: every thread handles one element",
    "__global__ void daxpy(int n, double a, double *x, double *y) {",
    "    int i = blockIdx.x * blockDim.x + threadIdx.x;   // which element am I?",
    "    if (i < n) y[i] = a * x[i] + y[i];",
    "}",
    "",
    "// the host launches it: 256 threads per block",
    "int nblocks = (n + 255) / 256;",
    "daxpy<<<nblocks, 256>>>(n, 2.0, x, y);"]})
s.obj({"id": "hier", "type": "table", "region": "center", "columns": ["level", "is", "example: n = 8192"], "rows": [
    ["thread", "one instance of the kernel, usually one element", "8192 threads"],
    ["thread block", "a group of threads that run on one SM and can cooperate", "512 threads per block"],
    ["grid", "all the blocks of one kernel launch", "8192 / 512 = 16 blocks"],
    ["built-in variables", "threadIdx, blockIdx, blockDim, gridDim", "known to every thread"]]})
s.obj({"id": "blk", "type": "table", "region": "center", "columns": ["blocks", "within a block", "between blocks"], "rows": [
    ["share", "fast on-chip shared memory", "only global memory"],
    ["synchronise", "__syncthreads(): a barrier for the block", "no: blocks must be independent"],
    ["run", "together, on one SM", "in any order, on any SM"],
    ["so", "cooperation", "scalability: a bigger GPU runs more blocks at once"]]})
s.obj({"id": "idx", "type": "math", "region": "center", "lines": [
    "i = \"blockIdx.x\" times \"blockDim.x\" + \"threadIdx.x\"",
    "\"block 3, thread 5, 256 per block:\" quad i = 3 times 256 + 5 = 773",
    "n = 1000: quad ceil(1000 / 256) = 4 \"blocks\" = 1024 \"threads\" quad 24 \"fail the test\" i < n",
    "\"(n + 255) / 256 is the ceiling, written in integer division\""]})
s.obj({"id": "two", "type": "code", "region": "center", "language": "c", "lines": [
    "dim3 block(16, 16);                                   // 256 threads",
    "dim3 grid((W + 15) / 16, (H + 15) / 16);",
    "brighten<<<grid, block>>>(img, W, H);",
    "",
    "__global__ void brighten(unsigned char *img, int W, int H) {",
    "    int x = blockIdx.x * blockDim.x + threadIdx.x;   // column",
    "    int y = blockIdx.y * blockDim.y + threadIdx.y;   // row",
    "    if (x < W && y < H) img[y * W + x] += 10;",
    "}"]})
s.obj({"id": "twox", "type": "math", "region": "center", "lines": [
    "640 times 480 \"image, 16 × 16 blocks:\" quad \"grid\" = 40 times 30 = 1200 \"blocks\"",
    "\"pixel\" (x, y) = (100, 50): quad \"block\" (6, 3), quad \"thread\" (4, 2)",
    "\"since\" 100 = 6 times 16 + 4 \"and\" 50 = 3 times 16 + 2"]})
s.obj({"id": "voc", "type": "table", "region": "center", "columns": ["CUDA", "vector-machine equivalent"], "rows": [
    ["CUDA thread", "the work of one element: one lane's share"],
    ["thread block", "the body of a strip-mined vector loop"],
    ["grid", "the whole vectorizable loop"],
    ["if (i < n)", "the vector length register, done by masking"],
    ["the difference", "the programmer writes one element; the hardware groups threads"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["question"], "rows": [
    ["a) DAXPY with n = 5000 and 128 threads per block: blocks launched, and idle threads"],
    ["b) the element handled by block 7, thread 100"],
    ["c) which block and thread handle element 4321?"],
    ["d) a 1920 × 1080 image with 16 × 16 blocks: the grid, and the block and thread for pixel (500, 300)"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad ceil(5000 / 128) = 40 \"blocks\" = 5120 \"threads\" quad 120 \"idle\"",
    "\"b)\" quad 7 times 128 + 100 = 996",
    "\"c)\" quad 4321 = 33 times 128 + 97 quad \"block 33, thread 97\"",
    "\"d)\" quad 120 times 68 = 8160 \"blocks\" quad 500 = 31 times 16 + 4, quad 300 = 18 times 16 + 12",
    "\"block\" (31, 18), quad \"thread\" (4, 12)"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("The third family of data-parallel machines is the one in every gaming laptop and every AI data centre: the GPU. This video introduces how it is programmed, with CUDA, and the hierarchy of threads, blocks and grids.", [s.head("GPUs and CUDA")])
s.step("Here are the eight stages.", show("stages"))
s.step("Where GPUs came from, the host and device model, DAXPY in CUDA, and threads, blocks and grids.", [hl("stages[0..=3]")])
s.step("Then how a thread finds its element, two-dimensional grids, CUDA in vector terms, and an exam question.", [hl("stages[4..=7]")])

s.scene("hist")
s.step("Stage 1: GPUs were built for graphics. A screen has millions of pixels, and each is computed in the same way.", [s.head("Stage 1 of 8: from graphics")] + hide("stages") + show("hist") + [hl("hist[0]")])
s.step("That is data-level parallelism on an enormous scale.", [hl("hist[1]")])
s.step("In 2007 NVIDIA released CUDA, an extension of C that lets programmers use the GPU for any computation, not just graphics.", [hl("hist[2]")])
s.step("OpenCL is an open standard built on the same model. We use CUDA, as the textbook does.", [hl("hist[3]"), s.take("graphics hardware, programmed in C")])

s.scene("het")
s.step("Stage 2: a GPU does not run on its own. The host is the CPU, running the ordinary program.", [s.head("Stage 2 of 8: host and device"), s.untake()] + hide("hist") + show("het") + [hl("het[0]")])
s.step("The device is the GPU, with its own memory. Data must be in GPU memory before the GPU can use it.", [hl("het[1]")])
s.step("The host calls kernels: functions that the device runs with thousands of threads at once.", [hl("het[2]")])
s.step("In the code, a kernel is marked double underscore global: called from the host, run on the device. This is heterogeneous computing: two kinds of processor, each doing what it does best.", [hl("het[3]"), s.take("host: CPU, serial · device: GPU, kernels")])

s.scene("code")
s.step("Stage 3: DAXPY in CUDA. The kernel is written for one element.", [s.head("Stage 3 of 8: DAXPY in CUDA"), s.untake()] + hide("het") + show("code") + [ml("code", 1, 2)])
s.step("Each thread first works out which element it owns, from its block number and its thread number within the block.", [ml("code", 3, 3)])
s.step("Then, if that element exists, it does one multiply-add. There is no loop at all: the loop has become the threads.", [ml("code", 4, 4)])
s.step("The host launches the kernel with triple angle brackets: the number of blocks, then the threads per block. 256 threads per block, and enough blocks to cover n.", [ml("code", 7, 9), s.take("write the code for one element")])

s.scene("hier")
s.step("Stage 4: the hierarchy. A thread is one instance of the kernel, usually handling one element. The textbook's example has 8192 elements, so 8192 threads.", [s.head("Stage 4 of 8: threads, blocks, grids"), s.untake()] + hide("code") + show("hier") + [hl("hier[0]")])
s.step("Threads are grouped into thread blocks. A block runs on one streaming multiprocessor, an SM, and its threads can cooperate. Here, 512 threads per block.", [hl("hier[1]")])
s.step("All the blocks of one launch form the grid: 8192 over 512, 16 blocks.", [hl("hier[2]")])
s.step("Every thread can read built-in variables: its threadIdx and blockIdx, and the sizes blockDim and gridDim.", [hl("hier[3]")])
s.step("Within a block, threads share fast on-chip memory, and can wait for each other at a barrier, syncthreads.", hide("hier") + show("blk") + [hl("blk[0..=1]")])
s.step("Between blocks, there is no synchronisation: blocks run in any order, on any SM.", [hl("blk[2]")])
s.step("That rule is what lets CUDA scale. A small GPU runs a few blocks at a time, a big one runs many, and the same program works on both.", [hl("blk[3]"), s.take("blocks: cooperate inside, independent outside")])

s.scene("idx")
s.step("Stage 5: which element does a thread own? i equals blockIdx times blockDim, plus threadIdx.", [s.head("Stage 5 of 8: which element"), s.untake()] + hide("blk") + show("idx") + [hl("idx[0]")])
s.step("Block 3, thread 5, with 256 threads per block: 3 times 256 plus 5, element 773.", [rv("idx[1]"), hl("idx[1]")])
s.step("If n is 1000, we need the ceiling of 1000 over 256: 4 blocks, 1024 threads. The last 24 threads find i not less than n, and do nothing. That is why the if is there.", [rv("idx[2]"), hl("idx[2]")])
s.step("n plus 255, over 256, in integer division, is exactly that ceiling.", [rv("idx[3]"), hl("idx[3]"), s.take("i = blockIdx × blockDim + threadIdx")])

s.scene("two")
s.step("Stage 6: images are two-dimensional, so blocks and grids can be too. Here, blocks of 16 by 16 threads, and a grid that covers the image.", [s.head("Stage 6 of 8: 2-D grids"), s.untake()] + hide("idx") + show("two") + [ml("two", 1, 3)])
s.step("Each thread computes a column x from the x parts of its indices, and a row y from the y parts.", [ml("two", 6, 7)])
s.step("Then, if the pixel is inside the image, it brightens it. Pixel x, y is at y times W plus x.", [ml("two", 8, 8)])
s.step("A 640 by 480 image with 16 by 16 blocks: a grid of 40 by 30, 1200 blocks.", hide("two") + show("twox") + [hl("twox[0]")])
s.step("Pixel 100, 50 belongs to block 6, 3, and is thread 4, 2 within it, because 100 is 6 times 16 plus 4, and 50 is 3 times 16 plus 2.", [rv("twox[1]"), hl("twox[1]"), rv("twox[2]"), hl("twox[2]", 0.5), s.take("x from the .x indices · y from the .y indices")])

s.scene("voc")
s.step("Stage 7: CUDA looks very different from vector code, but it is the same idea. A CUDA thread is the work of one element: one lane's share.", [s.head("Stage 7 of 8: in vector terms"), s.untake()] + hide("twox") + show("voc") + [hl("voc[0]")])
s.step("A thread block is like the body of a strip-mined vector loop: one strip of elements.", [hl("voc[1]")])
s.step("The grid is the whole loop.", [hl("voc[2]")])
s.step("And the if i less than n does the job of the vector length register: the hardware masks off the threads past the end.", [hl("voc[3]")])
s.step("The difference: the programmer writes code for one element, and the hardware groups threads into vector-like bundles. How it does that is the next video.", [hl("voc[4]"), s.take("thread ≈ element · block ≈ strip · grid ≈ loop")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("voc") + show("q"))
s.step("DAXPY with 5000 elements and 128 threads per block: how many blocks, and how many idle threads? The element of block 7, thread 100. The block and thread for element 4321. And a full HD image with 16 by 16 blocks. Pause and work it out.", [hl("q")])
s.step("a: the ceiling of 5000 over 128 is 40 blocks: 5120 threads, so 120 do nothing.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 7 times 128 plus 100: element 996.", [rv("qa[1]"), hl("qa[1]")])
s.step("c: divide 4321 by 128: 33, remainder 97. Block 33, thread 97.", [rv("qa[2]"), hl("qa[2]")])
s.step("d: 1920 over 16 is 120; 1080 over 16 is 67.5, rounded up to 68. 8160 blocks. Pixel 500, 300: 500 is 31 sixteens and 4, 300 is 18 sixteens and 12. Block 31, 18, thread 4, 12.", [rv("qa[3]"), hl("qa[3]"), rv("qa[4]"), hl("qa[4]", 0.5)])
s.step("The usual slip: rounding down the number of blocks. 1080 over 16 rounded down leaves the bottom rows of the image unprocessed.", [s.take("blocks = ⌈n / threads per block⌉")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("The host CPU launches kernels on the device GPU. A kernel is written for one element; the loop becomes thousands of threads.", [hl("stages[0..=3]")])
s.step("Threads form blocks, blocks form a grid. A thread finds its element from blockIdx, blockDim and threadIdx, in one or two dimensions. In vector terms: element, strip, loop.", [hl("stages[4..=6]")])
s.step("Next video: how the hardware actually runs those threads. Warps, SIMT, and the streaming multiprocessor.", [mk("stages[0..=7]"), s.take("Next: warps and SIMT")])

s.save("/home/claude/playlist/m4/m4v11.json")

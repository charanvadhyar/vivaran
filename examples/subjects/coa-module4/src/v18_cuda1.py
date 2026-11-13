"""Module 4, video 18: CUDA programming, part 1."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

cdiv = lambda a, b: -(-a // b)
assert cdiv(1_000_000, 256) == 3907 and 3907 * 256 - 1_000_000 == 192
G = 80 * 256
assert G == 20480 and len(range(0, 1_000_000, G)) == 49 and len(range(20479, 1_000_000, G)) == 48
mb = 3 * 1_000_000 * 4
assert mb == 12_000_000 and mb / 12e9 == 1e-3 and round(mb / 224e9 * 1e3, 3) == 0.054 and round(1e-3 / (mb / 224e9)) == 19
# exam
assert cdiv(10_000, 256) == 40 and 40 * 256 - 10_000 == 240 and 17 * 256 + 45 == 4397
assert list(range(100, 10_000, 2048)) == [100, 2148, 4196, 6244, 8292] and len(range(2000, 10_000, 2048)) == 4
assert 8 * 256 == 2048

s = Script("CUDA programming 1")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "A whole CUDA program"],
    [2, "Kernels and the launch"],
    [3, "How many blocks?"],
    [4, "The grid-stride loop"],
    [5, "Explicit memory"],
    [6, "What the copies cost"],
    [7, "Unified memory"],
    [8, "Checking for errors"],
    [9, "Exam question"]]})
s.obj({"id": "prog", "type": "code", "region": "center", "language": "c", "lines": [
    "__global__ void add(int n, const float *x, const float *y, float *z) {",
    "    int i = blockIdx.x * blockDim.x + threadIdx.x;",
    "    if (i < n) z[i] = x[i] + y[i];",
    "}",
    "",
    "int main() {",
    "    int n = 1000000;",
    "    ...                                  // allocate and fill x, y on the GPU",
    "    add<<<(n + 255) / 256, 256>>>(n, x, y, z);",
    "    cudaDeviceSynchronize();             // wait for the GPU",
    "    ...                                  // use z, free memory",
    "}"]})
s.obj({"id": "kq", "type": "table", "region": "center", "columns": ["CUDA", "meaning"], "rows": [
    ["__global__", "a kernel: runs on the GPU, called from the host"],
    ["__device__", "runs on the GPU, called only from GPU code"],
    ["__host__", "ordinary CPU code (the default)"],
    ["kernel<<<blocks, threads>>>(…)", "launch: blocks × threads copies of the kernel"],
    ["the launch returns at once", "the CPU continues; the GPU works in the background"],
    ["cudaDeviceSynchronize()", "the CPU waits until the GPU has finished"]]})
s.obj({"id": "nb", "type": "math", "region": "center", "lines": [
    "\"blocks\" = ceil(n / T) = (n + T - 1) / T \"in integer arithmetic\"",
    "n = 1000000, T = 256: quad (1000000 + 255) / 256 = 3907",
    "3907 times 256 = 1000192: quad 192 \"threads have no element\"",
    "\"so every kernel tests\" i < n",
    "T: \"a multiple of 32, at most 1024; 128 to 512 is usual\""]})
s.obj({"id": "gs", "type": "code", "region": "center", "language": "c", "lines": [
    "__global__ void add(int n, const float *x, const float *y, float *z) {",
    "    int stride = blockDim.x * gridDim.x;      // threads in the whole grid",
    "    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n; i += stride)",
    "        z[i] = x[i] + y[i];",
    "}",
    "add<<<80, 256>>>(n, x, y, z);    // 20,480 threads for 1,000,000 elements",
    "// thread 0: elements 0, 20480, 40960, …  49 of them",
    "// thread 20479: 48 of them"]})
s.obj({"id": "ex", "type": "code", "region": "center", "language": "c", "lines": [
    "float *h_x = (float *) malloc(bytes);       // host copy",
    "float *d_x;  cudaMalloc(&d_x, bytes);       // device copy",
    "cudaMemcpy(d_x, h_x, bytes, cudaMemcpyHostToDevice);    // in",
    "",
    "add<<<blocks, 256>>>(n, d_x, d_y, d_z);",
    "",
    "cudaMemcpy(h_z, d_z, bytes, cudaMemcpyDeviceToHost);    // out: waits",
    "cudaFree(d_x);  free(h_x);"]})
s.obj({"id": "cost", "type": "math", "region": "center", "lines": [
    "\"moved:\" 3 times 1000000 times 4 \"bytes\" = 12 \"MB (2 arrays in, 1 out)\"",
    "\"PCIe at about 12 GB/s:\" quad \"12 MB ÷ 12 GB/s\" = 1 \"ms\"",
    "\"the kernel, at 224 GB/s:\" quad \"12 MB ÷ 224 GB/s\" approx 0.054 \"ms\"",
    "\"the copies take about 19 times longer than the work\""]})
s.obj({"id": "um", "type": "code", "region": "center", "language": "c", "lines": [
    "float *x;",
    "cudaMallocManaged(&x, bytes);    // one pointer, valid on CPU and GPU",
    "for (i = 0; i < n; i++) x[i] = 1.0f;          // CPU writes",
    "add<<<blocks, 256>>>(n, x, y, z);             // pages move to the GPU on demand",
    "cudaDeviceSynchronize();                      // needed before the CPU reads",
    "printf(\"%f\", z[0]);                         // pages move back on demand",
    "cudaFree(x);",
    "// optional: cudaMemPrefetchAsync(x, bytes, device) avoids the page faults"]})
s.obj({"id": "umc", "type": "table", "region": "center", "columns": ["", "explicit", "unified"], "rows": [
    ["pointers", "two per array: h_x and d_x", "one"],
    ["copies", "cudaMemcpy, written by you", "pages migrate on first touch"],
    ["control", "you decide when data moves", "the driver decides"],
    ["speed", "best when tuned", "page faults, unless prefetched"],
    ["good for", "production code", "learning, prototypes, complex data"]]})
s.obj({"id": "er", "type": "code", "region": "center", "language": "c", "lines": [
    "add<<<blocks, 2048>>>(n, x, y, z);        // more than 1024 threads per block",
    "cudaError_t e = cudaGetLastError();       // the launch failed silently",
    "if (e != cudaSuccess)",
    "    printf(\"%s\\n\", cudaGetErrorString(e)); // invalid configuration argument",
    "",
    "e = cudaDeviceSynchronize();              // errors while the kernel ran"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["n = 10,000 floats, 256 threads per block"], "rows": [
    ["a) how many blocks, and how many threads are idle?"],
    ["b) which element does block 17, thread 45 handle?"],
    ["c) a grid-stride loop with 8 blocks: which elements does thread 100 handle? how many does thread 2000?"],
    ["d) add<<<5, 2048>>> prints nothing and z stays 0. Why, and how would you find out?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "answer"], "rows": [
    ["a", "⌈10,000 / 256⌉ = 40 blocks; 40 × 256 = 10,240: 240 idle"],
    ["b", "17 × 256 + 45 = 4397"],
    ["c", "stride 8 × 256 = 2048: 100, 2148, 4196, 6244, 8292"],
    ["c", "thread 2000: 2000, 4048, 6096, 8144: 4 elements"],
    ["d", "2048 > 1024 threads per block: the launch fails; cudaGetLastError"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("We have seen what a GPU is made of. Now we write programs for it. This video covers the parts of CUDA every program needs: launching a kernel, finding each thread's element, and moving data between the CPU and the GPU.", [s.head("CUDA programming, part 1")])
s.step("Here are the nine stages.", show("stages"))
s.step("A whole program, kernels and the launch, choosing the number of blocks, and the grid-stride loop.", [hl("stages[0..=3]")])
s.step("Then explicit memory and its cost, unified memory, checking for errors, and an exam question.", [hl("stages[4..=8]")])

s.scene("prog")
s.step("Stage 1: a complete program that adds two vectors of a million floats. First the kernel: the code one thread runs.", [s.head("Stage 1 of 9: a whole program")] + hide("stages") + show("prog") + [ml("prog", 1, 4)])
s.step("Each thread computes its global index, checks it is inside the array, and adds one pair of elements.", [ml("prog", 2, 3)])
s.step("The host program allocates the arrays, launches the kernel with enough blocks of 256 threads to cover a million elements, and waits for the GPU.", [ml("prog", 6, 10)])
s.step("Then it uses the result and frees the memory. Every CUDA program has this shape: prepare data, launch, wait, collect.", [ml("prog", 11, 12), s.take("prepare · launch · wait · collect")])

s.scene("kern")
s.step("Stage 2: double-underscore global marks a kernel: it runs on the GPU and is called from the host.", [s.head("Stage 2 of 9: kernels and the launch"), s.untake()] + hide("prog") + show("kq") + [hl("kq[0]")])
s.step("Device functions run on the GPU and can be called only from GPU code. Host functions are ordinary CPU code, the default.", [hl("kq[1..=2]")])
s.step("The triple angle brackets launch the kernel: blocks times threads copies of it, each with its own block and thread index.", [hl("kq[3]")])
s.step("The launch returns at once. The CPU carries on while the GPU works.", [hl("kq[4]")])
s.step("So before the CPU uses results, it must wait, with cudaDeviceSynchronize, or with a copy back, which waits by itself.", [hl("kq[5]"), s.take("launches are asynchronous")])

s.scene("blocks")
s.step("Stage 3: how many blocks? With n elements and T threads per block, we need the ceiling of n over T. In integer arithmetic, n plus T minus 1, divided by T.", [s.head("Stage 3 of 9: how many blocks?"), s.untake()] + hide("kq") + show("nb") + [hl("nb[0]")])
s.step("A million elements, 256 per block: 3907 blocks.", [rv("nb[1]"), hl("nb[1]")])
s.step("That is 1,000,192 threads: 192 have no element.", [rv("nb[2]"), hl("nb[2]")])
s.step("That is why every kernel tests i less than n. Without the test, those 192 threads write past the end of the array.", [rv("nb[3]"), hl("nb[3]")])
s.step("And T: a multiple of 32, so no warp is half empty, and at most 1024. 128 to 512 is the usual choice.", [rv("nb[4]"), hl("nb[4]"), s.take("blocks = (n + T − 1) / T, and test i < n")])

s.scene("gs")
s.step("Stage 4: another style, the grid-stride loop. Each thread handles several elements, stepping by the number of threads in the whole grid.", [s.head("Stage 4 of 9: the grid-stride loop"), s.untake()] + hide("nb") + show("gs") + [ml("gs", 1, 5)])
s.step("The stride is block size times the number of blocks.", [ml("gs", 2, 2)])
s.step("The loop starts at the thread's own index, and adds the stride until it passes n.", [ml("gs", 3, 4)])
s.step("Now the grid can be any size. 80 blocks of 256 is 20,480 threads for a million elements.", [ml("gs", 6, 6)])
s.step("Thread 0 handles elements 0, 20,480, 40,960, and so on: 49 of them. The last thread handles 48. Consecutive threads still touch consecutive elements, so every access stays coalesced.", [ml("gs", 7, 8), s.take("grid-stride: any grid size, still coalesced")])

s.scene("expl")
s.step("Stage 5: where do x and y live? The GPU has its own memory. In the explicit style there are two copies of each array: one on the host, from malloc, one on the device, from cudaMalloc.", [s.head("Stage 5 of 9: explicit memory"), s.untake()] + hide("gs") + show("ex") + [ml("ex", 1, 2)])
s.step("cudaMemcpy with host-to-device copies the input over.", [ml("ex", 3, 3)])
s.step("The kernel is given the device pointers. Passing a host pointer to a kernel is a common crash.", [ml("ex", 5, 5)])
s.step("cudaMemcpy device-to-host brings the result back. It waits for the kernel first, so no separate synchronise is needed.", [ml("ex", 7, 7)])
s.step("And both copies are freed: cudaFree on the device, free on the host.", [ml("ex", 8, 8), s.take("malloc + cudaMalloc · copy in · launch · copy out")])

s.scene("cost")
s.step("Stage 6: those copies are not free. Adding two arrays of a million floats moves 12 megabytes: two arrays in, one out.", [s.head("Stage 6 of 9: what the copies cost"), s.untake()] + hide("ex") + show("cost") + [hl("cost[0]")])
s.step("Over PCI Express at about 12 gigabytes per second, that is 1 millisecond.", [rv("cost[1]"), hl("cost[1]")])
s.step("The kernel itself reads and writes the same 12 megabytes from GPU memory at 224 gigabytes per second: about 0.054 milliseconds.", [rv("cost[2]"), hl("cost[2]")])
s.step("The copies take 19 times longer than the work. So keep data on the GPU across many kernels, and copy only at the start and the end.", [rv("cost[3]"), hl("cost[3]"), s.take("copies can cost more than the kernel")])

s.scene("um")
s.step("Stage 7: unified memory. cudaMallocManaged returns one pointer that works on both the CPU and the GPU.", [s.head("Stage 7 of 9: unified memory"), s.untake()] + hide("cost") + show("um") + [ml("um", 1, 2)])
s.step("The CPU writes the array. When the kernel touches it, the pages migrate to the GPU on demand.", [ml("um", 3, 4)])
s.step("Synchronise before the CPU reads the result. Then the pages migrate back.", [ml("um", 5, 6)])
s.step("Each first touch is a page fault, which is slow. A prefetch call moves the data ahead of time.", [ml("um", 8, 8)])
s.step("Comparing them: explicit memory needs two pointers per array and copies written by you; unified memory needs one pointer and no copies.", hide("um") + show("umc") + [hl("umc[0..=1]")])
s.step("Explicit gives you control, and is fastest when tuned. Unified is simpler, but pays for page faults unless prefetched.", [hl("umc[2..=3]")])
s.step("Unified memory is good for learning, prototypes, and data with pointers inside it. Production code often moves data explicitly.", [hl("umc[4]"), s.take("unified: simpler · explicit: more control")])

s.scene("err")
s.step("Stage 8: CUDA calls report errors through return values, and a kernel launch does not return one at all. This launch asks for 2048 threads per block, more than the limit of 1024.", [s.head("Stage 8 of 9: checking for errors"), s.untake()] + hide("umc") + show("er") + [ml("er", 1, 1)])
s.step("Nothing crashes. The kernel simply never runs. cudaGetLastError right after the launch reports it.", [ml("er", 2, 4)])
s.step("Errors during the kernel's run, like reading outside an array, appear later, from the next synchronising call.", [ml("er", 6, 6), s.take("check after the launch and after the sync")])

s.scene("exam")
s.step("Now an exam question: 10,000 floats, 256 threads per block.", [s.head("Exam question"), s.untake()] + hide("er") + show("q") + [hl("q[0..=1]")])
s.step("Find the blocks and idle threads, one thread's element, the elements of two threads in a grid-stride loop of 8 blocks, and why a launch with 2048 threads does nothing. Pause and work it out.", [hl("q[2..=3]")])
s.step("a: 10,000 over 256, rounded up, is 40 blocks. 40 times 256 is 10,240, so 240 threads are idle.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: block 17 times 256, plus 45: 4397.", [hl("qa[1]")])
s.step("c: 8 blocks of 256 gives a stride of 2048. Thread 100 handles 100, 2148, 4196, 6244 and 8292.", [hl("qa[2]")])
s.step("Thread 2000 handles 2000, 4048, 6096 and 8144; the next, 10,192, is past the end. 4 elements.", [hl("qa[3]")])
s.step("d: 2048 threads per block exceeds the limit of 1024, so the launch fails and z is never written. cudaGetLastError after the launch would say so.", [hl("qa[4]")])
s.step("The usual slip: forgetting the test i less than n, so the idle threads write past the end of the array.", [s.take("always test i < n")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A kernel is launched with blocks and threads, returns at once, and needs the ceiling of n over T blocks, with a bounds test. A grid-stride loop works for any grid size.", [hl("stages[0..=3]")])
s.step("Explicit memory copies data in and out, and those copies can cost more than the kernel. Unified memory is simpler. And launches must be checked for errors.", [hl("stages[4..=7]")])
s.step("Next video: threads that cooperate. syncthreads, shared memory, and timing with CUDA events.", [mk("stages[0..=8]"), s.take("Next: CUDA programming, part 2")])

s.save("/home/claude/playlist/m4/m4v18.json")

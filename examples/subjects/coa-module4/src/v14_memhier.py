"""Module 4, video 14: the GPU memory hierarchy."""
import sys
from math import gcd
sys.path.insert(0, "/home/claude/playlist")
from common import Script

def degree(stride, banks=32):
    """worst number of threads of one warp hitting the same bank, for s[stride * tid]"""
    hits = {}
    for t in range(32):
        hits.setdefault((stride * t) % banks, set()).add(stride * t)
    return max(len(v) for v in hits.values())

for k, d in [(1, 1), (2, 2), (3, 1), (4, 4), (8, 8), (32, 32), (33, 1)]:
    assert degree(k) == d == 32 // (32 // gcd(k, 32)) if k != 33 else degree(k) == 1
assert [(3 * t) % 32 for t in range(4)] == [0, 3, 6, 9]
assert 65536 // 2048 == 32 and 65536 // 255 == 257
assert 65536 // (256 * 48) == 5 and 5 * 8 == 40
# a 32 x 32 tile read down a column: element [r][c] is word 32 r + c; with padding 33 r + c
assert len({(32 * r) % 32 for r in range(32)}) == 1 and len({(33 * r) % 32 for r in range(32)}) == 32

s = Script("GPU memory hierarchy")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why a hierarchy"],
    [2, "The memory spaces"],
    [3, "Registers and local memory"],
    [4, "Shared memory"],
    [5, "Shared-memory banks"],
    [6, "Global memory"],
    [7, "Constant and texture memory"],
    [8, "Textbook names and CUDA names"],
    [9, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["fact", "consequence"], "rows": [
    ["a GPU runs tens of thousands of threads", "each needs operands every cycle"],
    ["DRAM is hundreds of cycles away", "warps hide latency, but not bandwidth"],
    ["bandwidth is the scarce resource", "reuse data close to the lanes"],
    ["so the programmer chooses", "where each variable lives"]]})
s.obj({"id": "sp", "type": "table", "region": "center", "columns": ["space", "where", "scope", "lifetime", "approx latency"], "rows": [
    ["registers", "on chip", "one thread", "thread", "~1 cycle"],
    ["local", "DRAM, cached", "one thread", "thread", "hundreds"],
    ["shared", "on chip", "one block", "block", "~20–30 cycles"],
    ["global", "DRAM", "all threads + host", "program", "400–800 cycles"],
    ["constant", "DRAM, cached", "all threads, read-only", "program", "~1 if cached"],
    ["texture", "DRAM, cached", "all threads, read-only", "program", "cached"]]})
s.obj({"id": "rg", "type": "table", "region": "center", "columns": ["registers and local memory", ""], "rows": [
    ["scalar variables of a thread", "registers: the fastest storage there is"],
    ["65,536 registers per SM, 2048 threads", "65,536 / 2048 = 32 per thread for full occupancy"],
    ["a thread may use up to 255", "then only 65,536 / 255 = 257 threads fit"],
    ["too many variables: spills", "the extra values go to local memory"],
    ["arrays indexed at run time", "also local memory: registers cannot be indexed"],
    ["local means private, not near", "it is DRAM, cached in L1 and L2"]]})
s.obj({"id": "sh", "type": "code", "region": "center", "language": "c", "lines": [
    "__global__ void reverse(float *d, int n) {",
    "    __shared__ float s[256];         // one copy per block, on chip",
    "    int t = threadIdx.x;",
    "    s[t] = d[blockIdx.x * 256 + t];  // each thread loads one value",
    "    __syncthreads();                 // wait until the whole block has loaded",
    "    d[blockIdx.x * 256 + t] = s[255 - t];   // read another thread's value",
    "}"]})
s.obj({"id": "bk", "type": "table", "region": "center", "columns": ["access by a warp", "banks of threads 0, 1, 2, 3", "threads per bank", "cost"], "rows": [
    ["s[t]", "0, 1, 2, 3", "1", "1 pass"],
    ["s[2t]", "0, 2, 4, 6", "", ""],
    ["s[3t]", "0, 3, 6, 9", "", ""],
    ["s[32t]", "0, 0, 0, 0", "", ""],
    ["s[0] for all", "0, 0, 0, 0", "same word", ""]]})
s.obj({"id": "bf", "type": "math", "region": "center", "lines": [
    "\"bank\" = \"word address\" mod 32 quad \"(32 banks, 4-byte words)\"",
    "s[k t]: quad \"conflict degree\" = gcd(k, 32)",
    "\"column of a 32 × 32 tile\": 32 r + c -> \"bank\" c: quad \"32-way\"",
    "\"pad to 32 × 33\": 33 r + c -> \"bank\" (r + c) mod 32: quad \"no conflict\""]})
s.obj({"id": "gl", "type": "table", "region": "center", "columns": ["global memory", ""], "rows": [
    ["the GPU's DRAM: gigabytes", "cudaMalloc allocates it; the host copies data in and out"],
    ["seen by every thread of every block", "and it outlives the kernel"],
    ["400 to 800 cycles away", "hidden by many warps, if bandwidth allows"],
    ["cached in L2, and often L1", "but the caches are small for so many threads"],
    ["each warp's accesses are combined", "into as few transactions as possible: next video"]]})
s.obj({"id": "ct", "type": "table", "region": "center", "columns": ["read-only memory", "behaviour"], "rows": [
    ["constant: __constant__, 64 KB", "cached on each SM, read-only in a kernel"],
    ["a warp reads one address", "one access, broadcast to all 32 threads"],
    ["a warp reads 32 addresses", "serialised: 32 accesses"],
    ["texture memory", "read-only cache tuned for 2-D locality"],
    ["texture extras", "interpolation, and clamp or wrap at the edges"],
    ["newer GPUs", "the same cache for any read-only data: const __restrict__"]]})
s.obj({"id": "nm", "type": "table", "region": "center", "columns": ["CUDA name", "Hennessy and Patterson's name", "what it is"], "rows": [
    ["local memory", "private memory", "per thread, in DRAM"],
    ["shared memory", "local memory", "per SM, on chip"],
    ["global memory", "GPU memory", "the whole GPU's DRAM"],
    ["CUDA thread", "SIMD lane", ""],
    ["streaming multiprocessor", "multithreaded SIMD processor", ""]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "c", "lines": [
    "__constant__ float K[64];",
    "__global__ void f(float *in, float *out) {",
    "    __shared__ float t[1024];",
    "    int i = blockIdx.x * blockDim.x + threadIdx.x;",
    "    float x = in[i];",
    "    float buf[40];   // indexed by a run-time loop variable",
    "    ...",
    "}",
    "// a) where do K, t, i, x, buf and the arrays in, out live?",
    "// b) a warp reads K[0]; then K[threadIdx.x]: accesses?",
    "// c) conflict degree of t[2*tid], t[3*tid], t[32*tid]"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["variable", "space"], "rows": [
    ["K", "constant memory"],
    ["t", "shared memory: one per block"],
    ["i, x", "registers"],
    ["buf", "local memory: indexed at run time"],
    ["the arrays in, out", "global memory"]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"b)\" K[0]: 1 \"access, broadcast\" quad K[\"tid\"]: 32 \"serialised accesses\"",
    "\"c)\" gcd(2, 32) = 2: \"2-way\" quad gcd(3, 32) = 1: \"none\" quad gcd(32, 32) = 32: \"32-way\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("A GPU has several kinds of memory, and unlike a CPU, the programmer decides which one each variable uses. Choosing well can make a kernel ten times faster. This video goes through them, from the fastest to the slowest.", [s.head("The GPU memory hierarchy")])
s.step("Here are the nine stages.", show("stages"))
s.step("Why a hierarchy, the memory spaces, registers and local memory, shared memory and its banks.", [hl("stages[0..=4]")])
s.step("Then global memory, constant and texture memory, the textbook's names for all of these, and an exam question.", [hl("stages[5..=8]")])

s.scene("why")
s.step("Stage 1: a GPU runs tens of thousands of threads, and each one wants operands every cycle.", [s.head("Stage 1 of 9: why a hierarchy")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("DRAM is hundreds of cycles away. Many warps hide that latency, as we saw, but they cannot create bandwidth.", [hl("why[1]")])
s.step("So bandwidth is the real limit, and the cure is reuse: keep data that is used again close to the lanes.", [hl("why[2]")])
s.step("On a CPU, caches do this automatically. On a GPU, the programmer also chooses where each variable lives.", [hl("why[3]"), s.take("bandwidth is scarce: reuse data on chip")])

s.scene("spaces")
s.step("Stage 2: the memory spaces. Registers: on chip, private to one thread, about one cycle.", [s.head("Stage 2 of 9: the memory spaces"), s.untake()] + hide("why") + show("sp") + [hl("sp[0]")])
s.step("Local memory: also private to one thread, but it lives in DRAM, cached.", [hl("sp[1]")])
s.step("Shared memory: on chip, shared by the threads of one block, and gone when the block finishes. About 20 to 30 cycles.", [hl("sp[2]")])
s.step("Global memory: the GPU's DRAM, seen by every thread and by the host, lasting the whole program. 400 to 800 cycles.", [hl("sp[3]")])
s.step("And two read-only spaces, constant and texture memory: in DRAM, but with their own caches. For exams, know each one's scope and where it physically is.", [hl("sp[4..=5]"), s.take("know each space's scope and location")])

s.scene("reg")
s.step("Stage 3: scalar variables of a thread go into registers, the fastest storage there is.", [s.head("Stage 3 of 9: registers and local memory"), s.untake()] + hide("sp") + show("rg") + [hl("rg[0]")])
s.step("An SM with 65,536 registers and 2048 threads gives each thread 32 registers at full occupancy.", [hl("rg[1]")])
s.step("A thread may use up to 255, but then only 257 threads fit on the SM. More registers per thread means fewer warps to hide latency.", [hl("rg[2]")])
s.step("If a thread needs more values than it has registers, the compiler spills the extra ones to local memory.", [hl("rg[3]")])
s.step("Arrays indexed by a value known only at run time go there too, because registers cannot be indexed.", [hl("rg[4]")])
s.step("The trap is the name. Local means private to the thread, not near it. It is in DRAM, as slow as global memory when it misses in the cache.", [hl("rg[5]"), s.take("local memory = private, but in DRAM")])

s.scene("shared")
s.step("Stage 4: shared memory. Declared with double-underscore shared, there is one copy per block, held on chip.", [s.head("Stage 4 of 9: shared memory"), s.untake()] + hide("rg") + show("sh") + [ml("sh", 1, 2)])
s.step("Here each thread loads one value from global memory into the shared array.", [ml("sh", 3, 4)])
s.step("syncthreads makes every thread of the block wait until all have loaded. Without it, a thread might read a slot that is not yet written.", [ml("sh", 5, 5)])
s.step("Now a thread can read a value that another thread loaded. Here each block reverses its 256 elements.", [ml("sh", 6, 6)])
s.step("Shared memory is how threads of a block cooperate, and how data loaded once from DRAM is reused many times. Video 19 uses it to speed up matrix multiply.", [s.take("shared memory: one per block, on chip, explicit")])

s.scene("banks")
s.step("Stage 5: shared memory is split into 32 banks, each 4 bytes wide. Word w is in bank w mod 32. If the 32 threads of a warp touch 32 different banks, it takes one pass.", [s.head("Stage 5 of 9: shared-memory banks"), s.untake()] + hide("sh") + show("bk") + [hl("bk[0]")])
s.step("With a stride of 2, threads 0 and 16 both hit bank 0. Two threads per bank: 2 passes, a 2-way bank conflict.", [hl("bk[1]"), st("bk[1][2]", "2"), st("bk[1][3]", "2 passes", 0.3)])
s.step("With a stride of 3, the banks are 0, 3, 6, 9, and so on. 3 and 32 share no factor, so all 32 banks are different: no conflict.", [hl("bk[2]"), st("bk[2][2]", "1"), st("bk[2][3]", "1 pass", 0.3)])
s.step("With a stride of 32, every thread hits bank 0: a 32-way conflict, 32 passes.", [hl("bk[3]"), st("bk[3][2]", "32"), st("bk[3][3]", "32 passes", 0.3)])
s.step("But if all threads read the same word, the hardware broadcasts it: one pass.", [hl("bk[4]"), st("bk[4][3]", "1 pass: broadcast")])
s.step("The rule: for an access s of k times t, the conflict degree is the gcd of k and 32. Exactly like interleaved memory banks in video 7.", hide("bk") + show("bf") + [hl("bf[0]"), rv("bf[1]"), hl("bf[1]", 0.3)])
s.step("A common case: reading down a column of a 32 by 32 tile. Element r, c is word 32 r plus c, so the whole column is in bank c: 32-way.", [rv("bf[2]"), hl("bf[2]")])
s.step("The fix is padding: declare the tile 32 by 33. Now element r, c is in bank r plus c mod 32, and a column touches all 32 banks.", [rv("bf[3]"), hl("bf[3]"), s.take("conflict degree = gcd(stride, 32); pad by 1")])

s.scene("global")
s.step("Stage 6: global memory is the GPU's DRAM, gigabytes of it. The host allocates it with cudaMalloc and copies data in and out.", [s.head("Stage 6 of 9: global memory"), s.untake()] + hide("bf") + show("gl") + [hl("gl[0]")])
s.step("Every thread of every block sees it, and it outlives the kernel, so one kernel can pass results to the next.", [hl("gl[1]")])
s.step("It is 400 to 800 cycles away. Enough warps hide the latency, but only if bandwidth is left.", [hl("gl[2]")])
s.step("There is an L2 cache, and often L1, but they are small when shared by thousands of threads.", [hl("gl[3]")])
s.step("What matters most is how a warp's 32 addresses fit together. The hardware merges them into as few memory transactions as it can: coalescing, the next video.", [hl("gl[4]"), s.take("global: big, shared by all, slow")])

s.scene("const")
s.step("Stage 7: constant memory, declared double-underscore constant, is 64 kilobytes, cached on each SM, and read-only inside a kernel.", [s.head("Stage 7 of 9: constant and texture memory"), s.untake()] + hide("gl") + show("ct") + [hl("ct[0]")])
s.step("It is built for one pattern: all threads of a warp reading the same address, such as a filter coefficient. One access, broadcast to all 32.", [hl("ct[1]")])
s.step("If the 32 threads read 32 different addresses, the accesses are serialised: 32 of them. Then constant memory is a bad choice.", [hl("ct[2]")])
s.step("Texture memory is also read-only, with a cache designed for two-dimensional locality: neighbours in an image, above and below as well as left and right.", [hl("ct[3]")])
s.step("It adds hardware interpolation between elements, and handles out-of-range coordinates by clamping or wrapping.", [hl("ct[4]")])
s.step("Newer GPUs let any read-only data use this cache, when a pointer is marked const and restrict.", [hl("ct[5]"), s.take("constant: same address for the warp")])

s.scene("names")
s.step("Stage 8: a warning for exams. Hennessy and Patterson use their own names, and two of them clash with CUDA's.", [s.head("Stage 8 of 9: two sets of names"), s.untake()] + hide("ct") + show("nm"))
s.step("What CUDA calls local memory, per thread in DRAM, the textbook calls private memory.", [hl("nm[0]")])
s.step("What CUDA calls shared memory, on chip for a block, the textbook calls local memory. So local memory means opposite things.", [hl("nm[1]")])
s.step("Global memory is the textbook's GPU memory. A CUDA thread maps to a SIMD lane, and an SM is a multithreaded SIMD processor.", [hl("nm[2..=4]"), s.take("CUDA shared = textbook local")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("nm") + show("q") + [ml("q", 1, 8)])
s.step("Say where each variable lives, how many accesses a warp makes reading K of 0 and then K of thread index, and the bank-conflict degree for three strides. Pause and work it out.", [ml("q", 9, 11)])
s.step("K is declared constant, so constant memory. t is declared shared: one copy per block.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("i and x are scalars: registers.", [hl("qa[2]")])
s.step("buf is an array indexed at run time, so it cannot be in registers: local memory, in DRAM.", [hl("qa[3]")])
s.step("The arrays that in and out point to were allocated by the host: global memory.", [hl("qa[4]")])
s.step("b: K of 0 is one address for the whole warp: 1 access, broadcast. K of thread index is 32 addresses: 32 serialised accesses.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("c: stride 2, gcd 2: 2-way. Stride 3, gcd 1: no conflict. Stride 32: 32-way.", [rv("qb[1]"), hl("qb[1]")])
s.step("The usual slip: calling local memory fast because of its name. It is private, and slow.", [s.take("local is private, not fast")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Registers are private and fastest, local memory is private but in DRAM, shared memory is on chip for a block, with 32 banks.", [hl("stages[0..=4]")])
s.step("Global memory is large, shared and slow. Constant memory broadcasts one address, texture memory caches two-dimensional neighbours, and the textbook's names differ from CUDA's.", [hl("stages[5..=7]")])
s.step("Next video: how a warp's accesses to global memory are combined. Memory coalescing.", [mk("stages[0..=8]"), s.take("Next: memory coalescing")])

s.save("/home/claude/playlist/m4/m4v14.json")

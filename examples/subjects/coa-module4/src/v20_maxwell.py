"""Module 4, video 20: case study, NVIDIA Maxwell (GM204, GeForce GTX 980).
Figures from NVIDIA's 'Maxwell: The Most Advanced CUDA GPU Ever Made' blog post and the Maxwell Tuning Guide."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m4")
from common import Script
from warp import occupancy

KEP = dict(max_blocks=16, smem_total=48)
assert occupancy(64, 32, 0)[1:] == (32, 64, 1.0) and occupancy(64, 32, 0, **KEP)[1:] == (16, 32, 0.5)
assert occupancy(256, 32, 24)[1:] == (4, 32, 0.5) and occupancy(256, 32, 24, **KEP)[1:] == (2, 16, 0.25)
QL, QB, QW, QO = occupancy(128, 64, 16)
assert QL == {'threads': 16, 'registers': 8, 'shared memory': 6, 'blocks': 32} and (QB, QW, QO) == (6, 24, 0.375)
assert 16 * 128 == 2048 and 8 * 192 == 1536 and 4 * 32 == 128 and 65536 // 4 == 16384
assert round(2048 * 2 * 1.126) == 4612 and round(2048 * 2 * 1.216) == 4981
assert round(4612 / 224.3, 1) == 20.6 and round(4612 / 165) == 28 and round(3090 / 195, 1) == 15.8 and round(28 / 15.8, 2) == 1.77
assert round(2 / 12 * 224.3, 1) == 37.4 and 16 * 2048 == 32768 and 16 * 64 == 1024

s = Script("NVIDIA Maxwell")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why Maxwell"],
    [2, "The GeForce GTX 980"],
    [3, "Inside the SMM"],
    [4, "Maxwell against Kepler"],
    [5, "Peak speed and the roofline"],
    [6, "Occupancy on Maxwell"],
    [7, "The memory system"],
    [8, "The whole module on one chip"],
    [9, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["Maxwell, 2014", ""], "rows": [
    ["the generation after Kepler", "first GM107 (GTX 750 Ti), then GM204 (GTX 980)"],
    ["the same 28 nm process as Kepler", "no help from smaller transistors"],
    ["so the goal was efficiency", "more work per watt from a better design"],
    ["NVIDIA's claim", "about twice the performance per watt of Kepler GK104"]]})
s.obj({"id": "gtx", "type": "table", "region": "center", "columns": ["GeForce GTX 980 (GM204)", "value"], "rows": [
    ["streaming multiprocessors (SMM)", "16"],
    ["CUDA cores (SIMD lanes)", "16 × 128 = 2048"],
    ["clock: base / boost", "1126 / 1216 MHz"],
    ["peak single precision", "4612 GFLOP/s"],
    ["memory", "4 GB GDDR5, 224.3 GB/s"],
    ["L2 cache", "2 MB"],
    ["power (TDP) · transistors", "165 W · 5.2 billion"]]})
s.obj({"id": "smm", "type": "diagram", "region": "center", "layout": "layers", "direction": "down", "nodes": [
    {"id": "p0", "label": "part 0"}, {"id": "p1", "label": "part 1"}, {"id": "p2", "label": "part 2"}, {"id": "p3", "label": "part 3"},
    {"id": "l1", "label": "L1 + texture"}, {"id": "sh", "label": "shared 96 KB"}],
    "edges": [{"from": "p0", "to": "l1"}, {"from": "p1", "to": "l1"}, {"from": "p2", "to": "sh"}, {"from": "p3", "to": "sh"}]})
s.obj({"id": "smx", "type": "table", "region": "center", "columns": ["one SMM", "contents"], "rows": [
    ["4 processing blocks", "each: 32 cores, 1 warp scheduler, 2 dispatch units"],
    ["32 cores = warp width", "a warp instruction issues in one cycle"],
    ["each block's own units", "no sharing between schedulers"],
    ["register file", "64K 32-bit registers (256 KB), 16K per block"],
    ["shared memory", "96 KB, dedicated; at most 48 KB per thread block"],
    ["L1 and texture cache", "combined into one unit"]]})
s.obj({"id": "vs", "type": "table", "region": "center", "columns": ["per SM", "Kepler SMX (GK104)", "Maxwell SMM (GM204)"], "rows": [
    ["CUDA cores", "192", "128"],
    ["organisation", "units shared by 4 schedulers", "4 partitions × 32, nothing shared"],
    ["registers · max warps", "64K · 64", "64K · 64"],
    ["max thread blocks", "16", "32"],
    ["shared memory", "48 KB", "96 KB"],
    ["shared-memory atomics", "lock, update, unlock", "native 32-bit"],
    ["result", "", "40% more per core"]]})
s.obj({"id": "pk", "type": "math", "region": "center", "lines": [
    "\"peak\" = 2048 \"lanes\" times 2 \"FLOPs (fused multiply-add)\" times 1.126 \"GHz\" approx 4612 \"GFLOP/s\"",
    "\"ridge point\" = 4612 / 224.3 approx 20.6 \"FLOP/byte\"",
    "\"GTX 980:\" 4612 / 165 \"W\" approx 28 \"GFLOP/s per W\" quad \"GTX 680:\" 3090 / 195 approx 15.8",
    "28 / 15.8 approx 1.77 \"times the peak per watt\""]})
s.obj({"id": "oc", "type": "table", "region": "center", "columns": ["kernel", "Kepler SMX", "Maxwell SMM"], "rows": [
    ["64 threads per block", "16 blocks × 2 warps = 32 warps: 50%", "32 blocks × 2 = 64 warps: 100%"],
    ["256 threads, 24 KB shared", "48 / 24 = 2 blocks: 16 warps, 25%", "96 / 24 = 4 blocks: 32 warps, 50%"],
    ["the same code", "", "more warps resident, no change needed"]]})
s.obj({"id": "mem", "type": "table", "region": "center", "columns": ["Maxwell memory system", ""], "rows": [
    ["L2", "2 MB, four times GK104's 512 KB: fewer trips to DRAM"],
    ["global loads", "cached in L2 only by default on GM204"],
    ["L1 + texture", "one unit, also merging a warp's accesses"],
    ["shared memory", "96 KB, separate from L1"],
    ["memory compression", "colour data compressed to save bandwidth"]]})
s.obj({"id": "all", "type": "table", "region": "center", "columns": ["module idea", "on the GTX 980"], "rows": [
    ["SIMD lanes", "2048 CUDA cores"],
    ["SIMD thread (warp)", "32 threads, one partition's 32 cores"],
    ["multithreading", "64 warps per SMM: 1024 warps, 32,768 threads"],
    ["memory hierarchy", "64K registers · 96 KB shared · 2 MB L2 · 4 GB DRAM"],
    ["roofline", "4612 GFLOP/s, 224.3 GB/s, ridge 20.6"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["GTX 980: 16 SMMs of 128 cores, 1126 MHz base, 1216 MHz boost, 224.3 GB/s"], "rows": [
    ["a) peak GFLOP/s at the boost clock"],
    ["b) SAXPY, y = a x + y in floats: intensity, and attainable GFLOP/s"],
    ["c) 128 threads per block, 64 registers per thread, 16 KB shared: blocks, warps, occupancy per SMM"],
    ["d) threads resident on the whole GPU at full occupancy"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "2048 × 2 × 1.216", "≈ 4981 GFLOP/s"],
    ["b", "2 FLOPs per 12 bytes = 0.167; × 224.3", "≈ 37.4 GFLOP/s"],
    ["c", "threads 16 · registers 8 · shared 96 / 16 = 6 · blocks 32", "6 blocks: shared memory decides"],
    ["c", "6 × 4 warps = 24 of 64", "37.5%"],
    ["d", "16 × 2048", "32,768"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("This module ends with a real GPU. NVIDIA's Maxwell architecture, in the GeForce GTX 980, puts every idea from this module on one chip: lanes, warps, multithreading, shared memory and the roofline. The figures come from NVIDIA's own Maxwell documents.", [s.head("Case study: NVIDIA Maxwell")])
s.step("Here are the nine stages.", show("stages"))
s.step("Why Maxwell was built, the GTX 980, inside its streaming multiprocessor, and how it differs from Kepler.", [hl("stages[0..=3]")])
s.step("Then its peak speed and roofline, occupancy, the memory system, the module's ideas mapped onto it, and an exam question.", [hl("stages[4..=8]")])

s.scene("why")
s.step("Stage 1: Maxwell, from 2014, followed Kepler. It appeared first in the small GM107 chip, then in the larger GM204 of the GTX 980.", [s.head("Stage 1 of 9: why Maxwell")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("It was built on the same 28 nanometre process as Kepler. No help came from smaller transistors.", [hl("why[1]")])
s.step("So the design goal was efficiency: more work per watt from a better organisation of the same transistors.", [hl("why[2]")])
s.step("NVIDIA claims about twice the performance per watt of Kepler's GK104. Let us see where it comes from.", [hl("why[3]"), s.take("same process, better design")])

s.scene("gtx")
s.step("Stage 2: the GTX 980 has 16 streaming multiprocessors, which NVIDIA calls SMMs.", [s.head("Stage 2 of 9: the GTX 980"), s.untake()] + hide("why") + show("gtx") + [hl("gtx[0]")])
s.step("Each has 128 CUDA cores, the textbook's SIMD lanes: 2048 in all.", [hl("gtx[1]")])
s.step("A base clock of 1126 megahertz, boosting to 1216, gives a peak of 4612 gigaflops per second in single precision.", [hl("gtx[2..=3]")])
s.step("4 gigabytes of GDDR5 memory at 224.3 gigabytes per second, and a 2 megabyte L2 cache.", [hl("gtx[4..=5]")])
s.step("All in 165 watts, with 5.2 billion transistors.", [hl("gtx[6]"), s.take("16 SMMs × 128 lanes, 224 GB/s, 165 W")])

s.scene("smm")
s.step("Stage 3: inside one SMM. It is split into four processing blocks, or partitions.", [s.head("Stage 3 of 9: inside the SMM"), s.untake()] + hide("gtx") + show("smm") + [hl("smm.p0"), hl("smm.p1", 0.15), hl("smm.p2", 0.3), hl("smm.p3", 0.45)])
s.step("Below them, a combined L1 and texture cache, and 96 kilobytes of shared memory.", [hl("smm.l1"), hl("smm.sh", 0.3)])
s.step("Each processing block has 32 cores, one warp scheduler, and two dispatch units.", hide("smm") + show("smx") + [hl("smx[0]")])
s.step("32 cores is exactly the warp width, so a warp instruction issues in a single cycle. With 16 lanes, as in video 12, it would take two.", [hl("smx[1]")])
s.step("And each block's units belong to its scheduler alone. No arbitration between schedulers: simpler, and less power.", [hl("smx[2]")])
s.step("The register file holds 64K 32-bit registers, 256 kilobytes, divided among the four blocks.", [hl("smx[3]")])
s.step("Shared memory is 96 kilobytes, dedicated, not shared with L1. One thread block may use at most 48.", [hl("smx[4]")])
s.step("And the L1 and texture caches are now one unit.", [hl("smx[5]"), s.take("4 × (32 lanes + 1 scheduler) per SMM")])

s.scene("vs")
s.step("Stage 4: compared with Kepler. A Kepler SMX had 192 cores; a Maxwell SMM has 128.", [s.head("Stage 4 of 9: Maxwell against Kepler"), s.untake()] + hide("smx") + show("vs") + [hl("vs[0]")])
s.step("Kepler's four schedulers shared its execution units, which needed extra control logic. Maxwell gives each scheduler its own 32 cores.", [hl("vs[1]")])
s.step("The register file and the limit of 64 warps are unchanged.", [hl("vs[2]")])
s.step("But the limit on thread blocks doubles from 16 to 32, and shared memory doubles from 48 to 96 kilobytes.", [hl("vs[3..=4]")])
s.step("Shared-memory atomics are now native instructions, instead of a lock, update and unlock sequence.", [hl("vs[5]")])
s.step("NVIDIA reports over 40 percent more delivered performance per core. Fewer, busier lanes: the efficiency comes from keeping each lane fed.", [hl("vs[6]"), s.take("fewer lanes, each kept busier")])

s.scene("peak")
s.step("Stage 5: the peak. 2048 lanes, each doing a fused multiply-add, 2 operations, every cycle, at 1.126 gigahertz: about 4612 gigaflops per second.", [s.head("Stage 5 of 9: peak speed and the roofline"), s.untake()] + hide("vs") + show("pk") + [hl("pk[0]")])
s.step("The ridge point of its roofline is 4612 over 224.3: about 20.6 operations per byte. A kernel needs that much intensity to reach the peak.", [rv("pk[1]"), hl("pk[1]")])
s.step("Per watt: the GTX 980 reaches about 28 peak gigaflops per watt; Kepler's GTX 680, about 15.8.", [rv("pk[2]"), hl("pk[2]")])
s.step("About 1.77 times, close to NVIDIA's claim of double, from the same 28 nanometre process.", [rv("pk[3]"), hl("pk[3]"), s.take("4612 GFLOP/s, ridge ≈ 20.6 FLOP/byte")])

s.scene("occ")
s.step("Stage 6: occupancy, from video 12. A kernel with blocks of 64 threads: Kepler allows 16 blocks per SM, 32 warps, 50 percent. Maxwell allows 32 blocks: 64 warps, 100 percent.", [s.head("Stage 6 of 9: occupancy on Maxwell"), s.untake()] + hide("pk") + show("oc") + [hl("oc[0]")])
s.step("A kernel with 256 threads and 24 kilobytes of shared memory per block: Kepler fits 2 blocks in 48 kilobytes, 25 percent. Maxwell fits 4 in 96: 50 percent.", [hl("oc[1]")])
s.step("The same compiled code gets more resident warps, and so hides more memory latency, with no change at all.", [hl("oc[2]"), s.take("double the blocks and shared memory: higher occupancy")])

s.scene("mem")
s.step("Stage 7: the memory system. The L2 cache grows to 2 megabytes, four times Kepler GK104's 512 kilobytes, so fewer accesses go to DRAM.", [s.head("Stage 7 of 9: the memory system"), s.untake()] + hide("oc") + show("mem") + [hl("mem[0]")])
s.step("On GM204, global loads are cached in L2 only by default; caching them in L1 is an option for the programmer.", [hl("mem[1]")])
s.step("The combined L1 and texture cache also gathers a warp's scattered accesses: coalescing, from video 15.", [hl("mem[2]")])
s.step("Shared memory is its own 96 kilobytes, no longer split with L1.", [hl("mem[3]")])
s.step("And for graphics, colour data is compressed in memory, saving bandwidth: the scarcest resource, as the roofline shows.", [hl("mem[4]"), s.take("bigger L2, more shared memory, less DRAM traffic")])

s.scene("all")
s.step("Stage 8: the whole module on one chip. The textbook's SIMD lanes are the 2048 CUDA cores.", [s.head("Stage 8 of 9: the module on one chip"), s.untake()] + hide("mem") + show("all") + [hl("all[0]")])
s.step("A SIMD thread is a warp of 32, running on one partition's 32 cores.", [hl("all[1]")])
s.step("Multithreading: 64 warps per SMM, 1024 warps on the chip, 32,768 threads, all resident at once, so latency is hidden.", [hl("all[2]")])
s.step("The memory hierarchy: registers, shared memory, L2 and DRAM. And a roofline with a peak of 4612 and a ridge at 20.6.", [hl("all[3..=4]"), s.take("lanes · warps · threads · memory · roofline")])

s.scene("exam")
s.step("Now an exam question on the GTX 980.", [s.head("Exam question"), s.untake()] + hide("all") + show("q") + [hl("q[0..=1]")])
s.step("Find the peak at the boost clock, SAXPY's intensity and attainable rate, the blocks, warps and occupancy of a kernel, and the threads resident on the whole GPU. Pause and work it out.", [hl("q[2..=3]")])
s.step("a: 2048 lanes times 2 operations times 1.216 gigahertz: about 4981 gigaflops per second.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: SAXPY reads x and y and writes y: 12 bytes, for a multiply and an add. 2 over 12 is 0.167 operations per byte, far below the ridge. 0.167 times 224.3: about 37.4 gigaflops, under 1 percent of the peak.", [hl("qa[1]")])
s.step("c: threads allow 16 blocks. Registers: 65,536 over 128 times 64 is 8. Shared memory: 96 over 16 is 6. The block limit is 32. The smallest is 6: shared memory decides.", [hl("qa[2]")])
s.step("6 blocks of 4 warps is 24 warps, out of 64: 37.5 percent occupancy.", [hl("qa[3]"), mk("qa[3][2]", 0.3)])
s.step("d: 16 SMMs times 2048 threads: 32,768.", [hl("qa[4]")])
s.step("The usual slip: using the boost clock for one part and the base clock for another. State which clock you use.", [s.take("say which clock you use")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Maxwell kept Kepler's 28 nanometre process and gained efficiency by design: 16 SMMs, each 4 partitions of 32 lanes with their own scheduler.", [hl("stages[0..=3]")])
s.step("4612 gigaflops, a ridge at 20.6, twice the blocks and shared memory per SM, and a 2 megabyte L2.", [hl("stages[4..=6]")])
s.step("That completes Module 4: vectors, SIMD, GPUs, loop-level parallelism and CUDA, all meeting in one real chip.", [mk("stages[0..=8]"), s.take("End of Module 4")])

s.save("/home/claude/playlist/m4/m4v20.json")

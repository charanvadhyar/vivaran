"""Module 4, video 12: warps, SIMT, and mapping onto the SM."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m4")
from common import Script
from warp import schedule, occupancy

S1, S4 = schedule(1, 10), schedule(4, 10)
assert sum(x != '–' for x in S1) == 4 and sum(x != '–' for x in S4) == 10
assert 8192 // 512 == 16 and 512 // 32 == 16 and 16 * 16 == 256
assert occupancy(256, 32, 0)[1:] == (8, 64, 1.0) and occupancy(256, 64, 0)[1:] == (4, 32, 0.5)
QL, QB, QW, QO = occupancy(128, 40, 12)
assert QL == {'threads': 16, 'registers': 12, 'shared memory': 8, 'blocks': 32} and (QB, QW, QO) == (8, 32, 0.5)
assert 128 // 32 == 4 and -(-100000 // 128) == 782 and 16 * 8 == 128 and -(-782 // 128) == 7
assert 1 + 600 // 30 == 21 and 1 + 400 // 20 == 21

s = Script("Warps and SIMT")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Threads travel in warps"],
    [2, "SIMT: one instruction, 32 threads"],
    [3, "Inside a streaming multiprocessor"],
    [4, "Mapping a grid onto the GPU"],
    [5, "Warp scheduling hides latency"],
    [6, "Occupancy: how many warps fit"],
    [7, "Exam question"]]})
s.obj({"id": "wp", "type": "table", "region": "center", "columns": ["a warp", "meaning"], "rows": [
    ["32 consecutive threads of a block", "threads 0–31, 32–63, 64–95, …"],
    ["the unit the hardware schedules", "the whole warp issues one instruction at a time"],
    ["textbook name", "a SIMD thread: like a vector instruction of length 32"],
    ["a block of 256 threads", "256 / 32 = 8 warps"]]})
s.obj({"id": "simt", "type": "table", "region": "center", "columns": ["SIMT", "meaning"], "rows": [
    ["single instruction, multiple threads", "one instruction, run by all 32 threads of the warp"],
    ["each thread has", "its own registers, its own index, its own data"],
    ["the lanes", "SIMD lanes, which NVIDIA calls CUDA cores"],
    ["16 lanes, 32 threads", "one warp instruction takes 2 cycles"],
    ["unlike a vector machine", "the programmer never sees the width: code is written per thread"]]})
s.obj({"id": "sm", "type": "diagram", "region": "center", "layout": "layers", "direction": "down", "nodes": [
    {"id": "ws", "label": "schedulers"},
    {"id": "rf", "label": "register file"},
    {"id": "ln", "label": "SIMD lanes"}, {"id": "ldst", "label": "load/store"}, {"id": "sfu", "label": "SFUs"},
    {"id": "sh", "label": "shared mem"}],
    "edges": [{"from": "ws", "to": "rf"}, {"from": "rf", "to": "ln"}, {"from": "rf", "to": "ldst"}, {"from": "rf", "to": "sfu"},
              {"from": "ldst", "to": "sh"}]})
s.obj({"id": "smx", "type": "table", "region": "center", "columns": ["SM part", "job"], "rows": [
    ["warp schedulers", "each cycle, pick a warp whose next instruction is ready"],
    ["register file", "tens of thousands of registers, split among all resident threads"],
    ["SIMD lanes", "integer and floating-point arithmetic"],
    ["load/store and special-function units", "memory access, and sine, square root, reciprocal"],
    ["shared memory and L1", "fast on-chip memory shared by a block"]]})
s.obj({"id": "map", "type": "table", "region": "center", "columns": ["step", "textbook example: n = 8192"], "rows": [
    ["the grid", "8192 threads in 16 blocks of 512"],
    ["the thread block scheduler", "sends each block to an SM with room for it"],
    ["inside the SM", "each block of 512 is 16 warps"],
    ["in all", "16 × 16 = 256 warps, each one SIMD instruction stream"],
    ["a block never moves", "it runs on its SM until all its warps finish"]]})
s.obj({"id": "ws", "type": "table", "region": "center", "columns": ["cycle", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], "rows": [
    ["1 warp", *S1], ["4 warps", *S4]]})
s.obj({"id": "wsx", "type": "math", "region": "center", "lines": [
    "\"warps needed\" approx 1 + \"latency\" / \"cycles of work between long waits\"",
    "\"latency\" 400, \"work\" 20: quad 1 + 400 / 20 = 21 \"warps\"",
    "\"no caches needed to hide latency: just enough warps\""]})
s.obj({"id": "oc", "type": "table", "region": "center", "columns": ["SM limit", "value", "256 threads, 32 regs", "256 threads, 64 regs"], "rows": [
    ["threads", "2048", "2048 / 256 = 8 blocks", "8 blocks"],
    ["registers", "65,536", "65,536 / (256 × 32) = 8", "65,536 / (256 × 64) = 4"],
    ["blocks", "32", "32", "32"],
    ["blocks resident", "the smallest", "8 = 64 warps: 100%", "4 = 32 warps: 50%"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["an SM: 2048 threads, 65,536 registers, 32 blocks, 96 KB shared memory"], "rows": [
    ["a kernel: 128 threads per block, 40 registers per thread, 12 KB shared memory per block"],
    ["a) warps per block   b) blocks per SM, and the limit that decides   c) occupancy"],
    ["d) n = 100,000, one thread each, 16 SMs: blocks, and how many waves"],
    ["e) warps needed to hide 600 cycles, with 30 cycles of work between loads"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["limit", "blocks"], "rows": [
    ["threads: 2048 / 128", "16"], ["registers: 65,536 / (128 × 40) = 12.8", "12"], ["shared memory: 96 / 12", "8"], ["blocks", "32"],
    ["smallest", "8 blocks = 32 warps"]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"a)\" 128 / 32 = 4 \"warps\" quad \"c)\" 32 / 64 = 50% \"occupancy\"",
    "\"d)\" ceil(100000 / 128) = 782 \"blocks\" quad 16 times 8 = 128 \"at once\" quad ceil(782 / 128) = 7 \"waves\"",
    "\"e)\" 1 + 600 / 30 = 21 \"warps: 32 resident is enough\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("A CUDA program describes thousands of independent threads. But the hardware does not run them one by one. It bundles them into groups of 32, and runs each group like a vector instruction. This video opens the streaming multiprocessor.", [s.head("Warps and SIMT")])
s.step("Here are the seven stages.", show("stages"))
s.step("Warps, the SIMT idea, and what is inside a streaming multiprocessor.", [hl("stages[0..=2]")])
s.step("Then how a grid is mapped onto the GPU, how warp scheduling hides memory latency, occupancy, and an exam question.", [hl("stages[3..=6]")])

s.scene("warp")
s.step("Stage 1: the threads of a block are split into warps of 32 consecutive threads: 0 to 31, 32 to 63, and so on.", [s.head("Stage 1 of 7: warps")] + hide("stages") + show("wp") + [hl("wp[0]")])
s.step("The warp, not the thread, is what the hardware schedules. All 32 threads issue the same instruction together.", [hl("wp[1]")])
s.step("The textbook calls a warp a SIMD thread: it behaves like one vector instruction of length 32.", [hl("wp[2]")])
s.step("A block of 256 threads is 8 warps. Block sizes are almost always multiples of 32, so no warp is left half empty.", [hl("wp[3]"), s.take("warp = 32 threads, scheduled together")])

s.scene("simt")
s.step("Stage 2: NVIDIA calls this SIMT: single instruction, multiple threads. One instruction is run by all 32 threads of the warp.", [s.head("Stage 2 of 7: SIMT"), s.untake()] + hide("wp") + show("simt") + [hl("simt[0]")])
s.step("But each thread has its own registers, its own index, and works on its own data.", [hl("simt[1]")])
s.step("The hardware that does the arithmetic is a set of SIMD lanes, which NVIDIA's marketing calls CUDA cores.", [hl("simt[2]")])
s.step("If an SM has 16 lanes per scheduler, a warp of 32 threads takes 2 cycles per instruction: half the threads, then the other half. Just like a vector machine with fewer lanes than elements.", [hl("simt[3]")])
s.step("The difference from a vector machine: the width is invisible. The programmer writes for one thread, and the hardware forms the vectors.", [hl("simt[4]"), s.take("SIMT: vector hardware, programmed per thread")])

s.scene("sm")
s.step("Stage 3: inside a streaming multiprocessor, the textbook's multithreaded SIMD processor. At the top, warp schedulers.", [s.head("Stage 3 of 7: inside an SM"), s.untake()] + hide("simt") + show("sm") + [hl("sm.ws")])
s.step("A large register file, divided among all the threads living on the SM.", [hl("sm.rf")])
s.step("The SIMD lanes, load-store units, and special-function units.", [hl("sm.ln"), hl("sm.ldst", 0.2), hl("sm.sfu", 0.4)])
s.step("And shared memory with the L1 cache.", [hl("sm.sh")])
s.step("Each part's job: a scheduler picks, every cycle, a warp whose next instruction has its operands ready.", hide("sm") + show("smx") + [hl("smx[0]")])
s.step("The register file holds every resident thread's registers at once, so switching warps costs nothing: no state is saved or restored.", [hl("smx[1]")])
s.step("Lanes do arithmetic, load-store units move data, and special-function units do sines, square roots and reciprocals.", [hl("smx[2..=3]")])
s.step("Shared memory is the fast on-chip memory that a block's threads share. A GPU is many SMs, from a handful to over a hundred.", [hl("smx[4]"), s.take("SM: schedulers, registers, lanes, shared memory")])

s.scene("map")
s.step("Stage 4: mapping the textbook's example. 8192 threads in 16 blocks of 512.", [s.head("Stage 4 of 7: mapping a grid"), s.untake()] + hide("smx") + show("map") + [hl("map[0]")])
s.step("The thread block scheduler sends each block to an SM that has room for it.", [hl("map[1]")])
s.step("Inside the SM, a block of 512 threads is 16 warps.", [hl("map[2]")])
s.step("In all, 256 warps: 256 SIMD instruction streams, each of 32 elements.", [hl("map[3]")])
s.step("A block stays on its SM until all its warps finish. That is why threads of one block can share memory and synchronise.", [hl("map[4]"), s.take("grid → blocks to SMs → warps")])

s.scene("sched")
s.step("Stage 5: why so many warps? Because memory is slow. Suppose each warp loads a value, then adds using it, and a load takes 4 cycles.", [s.head("Stage 5 of 7: hiding latency"), s.untake()] + hide("map") + show("ws") + [hl("ws[0]")])
s.step("With one warp, the add must wait for the load. 6 of these 10 cycles issue nothing.", [hl("ws[0]")])
s.step("With four warps, while warp 0 waits, warps 1, 2 and 3 issue their loads. By cycle 5, warp 0's data has arrived. Every cycle is used.", [hl("ws[1]")])
s.step("This is fine-grained multithreading, from Module 3, at a huge scale. The number of warps needed is about 1 plus the latency divided by the work between long waits.", hide("ws") + show("wsx") + [hl("wsx[0]")])
s.step("A 400-cycle memory access, with 20 cycles of work between loads: 21 warps.", [rv("wsx[1]"), hl("wsx[1]")])
s.step("So a GPU hides memory latency mainly with parallelism, not with big caches. That is where its transistors go: lanes and registers.", [rv("wsx[2]"), hl("wsx[2]"), s.take("enough warps hide any latency")])

s.scene("occ")
s.step("Stage 6: how many warps can live on one SM? It is limited by several resources. Take an SM with room for 2048 threads, 65,536 registers, and 32 blocks.", [s.head("Stage 6 of 7: occupancy"), s.untake()] + hide("wsx") + show("oc") + [hl("oc[0..=2]")])
s.step("A kernel with 256 threads per block and 32 registers per thread. Threads allow 8 blocks. Registers: 65,536 over 256 times 32, also 8.", [hl("oc[0][2]"), hl("oc[1][2]", 0.4)])
s.step("8 blocks is 64 warps: the maximum, 100 percent occupancy.", [hl("oc[3][2]")])
s.step("Now the same kernel needs 64 registers per thread. Registers allow only 4 blocks: 32 warps, 50 percent occupancy. Half the latency-hiding power is gone.", [hl("oc[1][3]"), hl("oc[3][3]", 0.4)])
s.step("Occupancy is the resident warps divided by the maximum. The smallest limit decides it, and shared memory per block is often that limit too.", [s.take("blocks per SM = the smallest of all the limits")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("oc") + show("q") + [hl("q[0..=1]")])
s.step("Find the warps per block, the blocks per SM and which limit decides, the occupancy, the number of blocks and waves for 100,000 elements on 16 SMs, and the warps needed to hide 600 cycles. Pause and work it out.", [hl("q[2..=3]")])
s.step("Threads allow 16 blocks. Registers: 128 times 40 is 5120 per block, and 65,536 over that is 12.8, so 12.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("Shared memory: 96 kilobytes over 12 is 8. The block limit is 32. The smallest is 8: shared memory decides.", [hl("qa[2..=3]"), mk("qa[4]", 0.5)])
s.step("a: 128 threads is 4 warps per block. c: 8 blocks of 4 warps is 32 warps, out of 64: 50 percent.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("d: 100,000 over 128, rounded up: 782 blocks. 16 SMs hold 8 each, 128 at once. 782 over 128 rounded up: 7 waves, the last one partly empty.", [rv("qb[1]"), hl("qb[1]")])
s.step("e: 1 plus 600 over 30: 21 warps. 32 are resident, so the latency is hidden.", [rv("qb[2]"), hl("qb[2]")])
s.step("The usual slip: checking only the thread limit. Registers and shared memory often allow fewer blocks.", [s.take("check threads, registers, shared memory and blocks")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Threads run in warps of 32. Each warp instruction runs on all 32 threads: SIMT, vector hardware programmed per thread.", [hl("stages[0..=2]")])
s.step("Blocks go to SMs and stay there. Many resident warps hide memory latency, and occupancy is set by the scarcest resource.", [hl("stages[3..=5]")])
s.step("Next video: what happens when the threads of one warp disagree at a branch. Branch divergence.", [mk("stages[0..=6]"), s.take("Next: branch divergence")])

s.save("/home/claude/playlist/m4/m4v12.json")

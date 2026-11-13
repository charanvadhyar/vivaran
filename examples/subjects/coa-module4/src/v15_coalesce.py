"""Module 4, video 15: memory coalescing."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m4")
from common import Script
from coal import eff

W = range(32)
assert eff([4 * t for t in W], 4) == (4, 1.0)
assert eff([4 * t + 4 for t in W], 4) == (5, 0.8)
assert eff([8 * t for t in W], 4) == (8, 0.5)
assert eff([16 * t for t in W], 4) == (16, 0.25)
assert eff([128 * t for t in W], 4) == (32, 0.125)
assert eff([4 * 1024 * t for t in W], 4) == (32, 0.125)
assert eff([8 * t for t in W], 8) == (8, 1.0)
assert eff([8 * t + 16 for t in W], 8)[0] == 9 and round(256 / 288 * 100, 1) == 88.9
n12, e12 = eff([12 * t for t in W], 4); assert n12 == 12 and round(e12 * 100) == 33
assert 300 * 0.125 == 37.5 and 224 * 0.25 == 56

s = Script("Memory coalescing")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "One warp, 32 addresses"],
    [2, "Sectors and transactions"],
    [3, "Five access patterns"],
    [4, "What it costs in bandwidth"],
    [5, "Arrays of structures"],
    [6, "Rows and columns"],
    [7, "Transpose with a shared tile"],
    [8, "Exam question"]]})
s.obj({"id": "w", "type": "table", "region": "center", "columns": ["a warp executes a load", ""], "rows": [
    ["x = A[i];", "32 threads, 32 addresses, in one instruction"],
    ["the memory system sees", "one request with 32 addresses"],
    ["DRAM delivers", "whole aligned blocks of bytes, not single words"],
    ["coalescing", "merging the 32 addresses into as few blocks as possible"]]})
s.obj({"id": "sc", "type": "math", "region": "center", "lines": [
    "\"sector\" = 32 \"aligned bytes\" quad \"(a 128-byte cache line holds 4)\"",
    "\"sectors for a warp\" = \"distinct\" floor(\"byte address\" / 32)",
    "\"efficiency\" = \"bytes the threads asked for\" / (\"sectors\" times 32)",
    "32 \"floats\" = 128 \"bytes\" quad -> \"at best 4 sectors\""]})
s.obj({"id": "pt", "type": "table", "region": "center", "columns": ["pattern (float A[])", "thread t reads byte", "sectors", "efficiency"], "rows": [
    ["A[t]", "4t", "", ""],
    ["A[t + 1]", "4t + 4", "", ""],
    ["A[2t]", "8t", "", ""],
    ["A[4t]", "16t", "", ""],
    ["A[32t] or worse", "128t", "", ""]]})
s.obj({"id": "bw", "type": "math", "region": "center", "lines": [
    "\"useful bandwidth\" = \"peak\" times \"efficiency\"",
    "\"peak 224 GB/s\": quad A[t] -> 224 quad A[4t] -> 224 times 0.25 = 56 \"GB/s\"",
    "\"a memory-bound kernel runs 4 times slower\"",
    "\"the roofline's bandwidth is the useful bandwidth\""]})
s.obj({"id": "aos", "type": "code", "region": "center", "language": "c", "lines": [
    "// array of structures: 16 bytes per particle",
    "struct P { float x, y, z, w; };",
    "P p[N];        p[i].x   // thread t reads byte 16t: 16 sectors, 25%",
    "",
    "// structure of arrays: each field is its own array",
    "struct Ps { float x[N], y[N], z[N], w[N]; };",
    "Ps q;          q.x[i]   // thread t reads byte 4t: 4 sectors, 100%"]})
s.obj({"id": "rc", "type": "code", "region": "center", "language": "c", "lines": [
    "// N x N matrix of floats, row-major, N = 1024",
    "int t = blockIdx.x * blockDim.x + threadIdx.x;",
    "",
    "// one thread per row: thread t walks its row",
    "for (k = 0; k < N; k++) sum += A[t * N + k];   // warp stride N: 32 sectors",
    "",
    "// one thread per column: thread t walks its column",
    "for (k = 0; k < N; k++) sum += A[k * N + t];   // warp stride 1: 4 sectors"]})
s.obj({"id": "tr", "type": "code", "region": "center", "language": "c", "lines": [
    "// naive: out[x][y] = in[y][x]",
    "out[x * N + y] = in[y * N + x];      // read coalesced, write stride N",
    "",
    "__shared__ float tile[32][33];       // 33: no bank conflicts (video 14)",
    "tile[ty][tx] = in[(by + ty) * N + bx + tx];     // coalesced read",
    "__syncthreads();",
    "out[(bx + ty) * N + by + tx] = tile[tx][ty];    // coalesced write"]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["a warp of 32 threads, 32-byte sectors; thread t = 0 … 31"], "rows": [
    ["a) double D[]: D[t], then D[t + 2]"],
    ["b) struct { float x, y, z; } S[]: S[t].x"],
    ["c) float A[1024][1024], row-major: A[t][0]"],
    ["for each: sectors and efficiency.  d) useful bandwidth for c, peak 300 GB/s"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["access", "bytes", "sectors", "efficiency"], "rows": [
    ["D[t]", "8t … 8t + 7: 0 to 255", "8", "100%"],
    ["D[t + 2]", "16 to 271", "9", "256 / 288 = 88.9%"],
    ["S[t].x", "12t: 0 to 375", "12", "128 / 384 = 33%"],
    ["A[t][0]", "4096t: one per sector", "32", "128 / 1024 = 12.5%"],
    ["d) useful bandwidth", "300 × 0.125", "", "37.5 GB/s"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Two kernels can do the same arithmetic on the same data, and one runs eight times slower. Often the only difference is the order in which threads touch memory. This video shows how a GPU combines a warp's memory accesses.", [s.head("Memory coalescing")])
s.step("Here are the eight stages.", show("stages"))
s.step("A warp's 32 addresses, how memory delivers them in sectors, five access patterns, and what they cost.", [hl("stages[0..=3]")])
s.step("Then arrays of structures, rows and columns of a matrix, a transpose using shared memory, and an exam question.", [hl("stages[4..=7]")])

s.scene("warp")
s.step("Stage 1: when a warp executes a load, its 32 threads each supply an address, all in one instruction.", [s.head("Stage 1 of 8: one warp, 32 addresses")] + hide("stages") + show("w") + [hl("w[0]")])
s.step("So the memory system receives a single request carrying 32 addresses.", [hl("w[1]")])
s.step("But DRAM does not deliver single words. It delivers whole aligned blocks of bytes.", [hl("w[2]")])
s.step("Coalescing means merging those 32 addresses into as few blocks as possible. If the addresses are close together, a few blocks serve the whole warp.", [hl("w[3]"), s.take("a warp's 32 addresses → as few blocks as possible")])

s.scene("sectors")
s.step("Stage 2: on recent NVIDIA GPUs, the block is a 32-byte sector. Four sectors make a 128-byte cache line.", [s.head("Stage 2 of 8: sectors"), s.untake()] + hide("w") + show("sc") + [hl("sc[0]")])
s.step("To count the sectors a warp needs, divide each byte address by 32, round down, and count the distinct results.", [rv("sc[1]"), hl("sc[1]")])
s.step("Efficiency is the bytes the threads asked for, divided by the bytes actually moved: sectors times 32.", [rv("sc[2]"), hl("sc[2]")])
s.step("32 floats are 128 bytes, so the best a warp can do is 4 sectors.", [rv("sc[3]"), hl("sc[3]"), s.take("efficiency = bytes used / (sectors × 32)")])

s.scene("patterns")
s.step("Stage 3: five patterns on an array of floats. A of t: thread t reads bytes 4t to 4t plus 3. Bytes 0 to 127: exactly 4 sectors. 100 percent.", [s.head("Stage 3 of 8: five access patterns"), s.untake()] + hide("sc") + show("pt") + [hl("pt[0]"), st("pt[0][2]", "4"), st("pt[0][3]", "100%", 0.3)])
s.step("A of t plus 1: bytes 4 to 131. The range is still 128 bytes, but it now crosses into a fifth sector. 128 over 160: 80 percent.", [hl("pt[1]"), st("pt[1][2]", "5"), st("pt[1][3]", "80%", 0.3)])
s.step("A of 2t: every other float, bytes 0 to 255. 8 sectors for 128 useful bytes: 50 percent.", [hl("pt[2]"), st("pt[2][2]", "8"), st("pt[2][3]", "50%", 0.3)])
s.step("A of 4t: one float in every 16 bytes. 16 sectors: 25 percent.", [hl("pt[3]"), st("pt[3][2]", "16"), st("pt[3][3]", "25%", 0.3)])
s.step("A of 32t, or any stride of 8 floats or more: every thread gets its own sector. 32 sectors, 4 useful bytes in each: 12.5 percent. Random addresses are just as bad.", [hl("pt[4]"), st("pt[4][2]", "32"), st("pt[4][3]", "12.5%", 0.3)])
s.step("The rule: consecutive threads should read consecutive addresses. Then the warp's request is one contiguous, aligned block.", [hl("pt[0]"), s.take("thread t → element t: coalesced")])

s.scene("bw")
s.step("Stage 4: what this costs. The bandwidth that does useful work is the peak times the efficiency.", [s.head("Stage 4 of 8: the cost"), s.untake()] + hide("pt") + show("bw") + [hl("bw[0]")])
s.step("A GPU with a peak of 224 gigabytes per second gets all of it with A of t, but only 56 with A of 4t.", [rv("bw[1]"), hl("bw[1]")])
s.step("A kernel limited by memory, like most simple kernels, then runs four times slower, with exactly the same instructions.", [rv("bw[2]"), hl("bw[2]")])
s.step("In the roofline model from video 10, the slanted roof should use this useful bandwidth, not the peak.", [rv("bw[3]"), hl("bw[3]"), s.take("useful bandwidth = peak × efficiency")])

s.scene("aos")
s.step("Stage 5: the most common cause in real code. An array of structures: each particle holds x, y, z and w, 16 bytes.", [s.head("Stage 5 of 8: arrays of structures"), s.untake()] + hide("bw") + show("aos") + [ml("aos", 1, 2)])
s.step("A kernel that reads only x makes thread t read byte 16t: a stride of 4 floats. 16 sectors, 25 percent.", [ml("aos", 3, 3)])
s.step("Turn it inside out: a structure of arrays, one array per field.", [ml("aos", 5, 6)])
s.step("Now the x values are contiguous. Thread t reads byte 4t: 4 sectors, 100 percent. Same data, four times the useful bandwidth.", [ml("aos", 7, 7), s.take("GPUs prefer structures of arrays")])

s.scene("rc")
s.step("Stage 6: a matrix stored row by row, 1024 by 1024 floats. Each thread sums one line of the matrix.", [s.head("Stage 6 of 8: rows and columns"), s.untake()] + hide("aos") + show("rc") + [ml("rc", 1, 2)])
s.step("If each thread walks its own row, then at each step k, thread t reads A of t times N plus k. Neighbouring threads are N floats apart: 32 sectors, 12.5 percent.", [ml("rc", 4, 5)])
s.step("If each thread walks its own column, at each step thread t reads A of k times N plus t. Neighbouring threads read neighbouring floats: 4 sectors.", [ml("rc", 7, 8)])
s.step("This is the opposite of a CPU, where one thread walking a row is the cache-friendly choice. On a GPU, what matters is what the 32 threads do at the same moment.", [s.take("look across the warp, not along a thread")])

s.scene("tr")
s.step("Stage 7: some kernels cannot be coalesced both ways. A transpose reads in of y, x and writes out of x, y.", [s.head("Stage 7 of 8: transpose with a tile"), s.untake()] + hide("rc") + show("tr") + [ml("tr", 1, 1)])
s.step("With threads running along x, the read is coalesced, but the write has stride N: 32 sectors per warp.", [ml("tr", 2, 2)])
s.step("The fix uses shared memory. A block declares a 32 by 33 tile; the 33 avoids bank conflicts, as in the last video.", [ml("tr", 4, 4)])
s.step("The block reads a 32 by 32 square of the input, row by row: coalesced.", [ml("tr", 5, 6)])
s.step("Then it writes the square out row by row, reading the tile by column. The transposing happens in fast shared memory, and both global accesses are coalesced.", [ml("tr", 7, 7), s.take("shared memory turns strided access into coalesced")])

s.scene("exam")
s.step("Now an exam question. A warp of 32 threads, and 32-byte sectors.", [s.head("Exam question"), s.untake()] + hide("tr") + show("q") + [hl("q[0..=2]")])
s.step("For each access, find the sectors and the efficiency; then the useful bandwidth for c, with a peak of 300 gigabytes per second. Pause and work it out.", [hl("q[3]")])
s.step("a: a double is 8 bytes, so 32 doubles are 256 bytes, 0 to 255: 8 sectors, 100 percent.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("D of t plus 2 starts at byte 16 and ends at 271. That reaches sector 8: 9 sectors. 256 over 288: 88.9 percent.", [hl("qa[1]")])
s.step("b: each structure is 12 bytes, so thread t reads byte 12t. The last x ends at byte 375: sectors 0 to 11, 12 of them. 128 useful bytes out of 384: one third.", [hl("qa[2]")])
s.step("c: rows are 4096 bytes apart, so each thread needs its own sector. 32 sectors, 12.5 percent.", [hl("qa[3]")])
s.step("d: 300 times 0.125: 37.5 gigabytes per second of useful bandwidth.", [hl("qa[4]"), mk("qa[4][3]", 0.4)])
s.step("The usual slip: counting addresses instead of sectors. A of t plus 1 touches 32 addresses, but costs 5 sectors, not 4.", [s.take("count distinct sectors, not threads")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A warp's 32 addresses are served in 32-byte sectors. Efficiency is useful bytes over bytes moved, and useful bandwidth is the peak times that.", [hl("stages[0..=3]")])
s.step("Use structures of arrays, have neighbouring threads touch neighbouring elements, and use a shared tile when one side must be strided.", [hl("stages[4..=6]")])
s.step("Next video: which loops can run in parallel at all. Loop-carried dependences.", [mk("stages[0..=7]"), s.take("Next: loop-carried dependences")])

s.save("/home/claude/playlist/m4/m4v15.json")

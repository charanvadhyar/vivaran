"""Module 2, video 11: ten advanced cache optimizations, part 2 (compiler, prefetching, HBM) and the summary of all ten."""
import math
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

# loop interchange: x[5000][100] doubles, 64 B blocks = 8 doubles
assert 5000 * 100 == 500000 and 500000 // 8 == 62500
# blocking: N = 512, B = 32
N, B = 512, 32
assert 2 * N**3 == 268435456 and 2 * N**3 // B + N * N == 8650752 and round(268435456 / 8650752) == 31
assert 3 * B * B * 8 == 24576 <= 32 * 1024
# hardware prefetch timeline: latency 30, iteration 30, 3 iterations
assert 3 * (30 + 30) == 180 and 30 + 3 * 30 == 120 and math.ceil(90 / 30) == 3
# compiler prefetch (Hennessy & Patterson example)
assert 3 * 100 // 2 + 101 == 251 and 7 + 4 + 4 + 4 == 19 and 100 * 2 + 2 * 100 == 400
# HBM tags
assert (1 << 30) // 64 == 1 << 24 and (1 << 24) * 6 == 96 * (1 << 20) and (1 << 30) // 4096 * 6 == 1.5 * (1 << 20)
# exam
assert 1024 * 1024 == 1048576 and 1048576 // 8 == 131072 and math.ceil(100 / 25) == 4
assert (512 << 20) // 64 * 4 == 32 << 20 and max(b for b in (8, 16, 32, 64) if 3 * b * b * 8 <= 32768) == 32

s = Script("Advanced cache optimizations, part 2")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Where part 2 fits"],
    [2, "Compiler: loop interchange"],
    [3, "Compiler: blocking"],
    [4, "Hardware prefetching"],
    [5, "Compiler-controlled prefetching"],
    [6, "HBM as an extra cache level"],
    [7, "All ten on one table"],
    [8, "Exam question"]]})
s.obj({"id": "p2", "type": "table", "region": "center", "columns": ["#", "optimization", "improves", "how"], "rows": [
    [8, "compiler optimizations", "miss rate", "reorder the program, no new hardware"],
    [9, "hardware prefetching", "miss penalty or miss rate", "fetch blocks before they are asked for"],
    [9, "compiler-controlled prefetching", "miss penalty or miss rate", "prefetch instructions in the code"],
    [10, "HBM as an extra level", "miss penalty", "a gigabyte-sized DRAM cache"]]})
s.obj({"id": "li1", "type": "code", "region": "center", "language": "c", "lines": [
    "/* before: inner loop goes down a column */",
    "for (j = 0; j < 100; j++)",
    "  for (i = 0; i < 5000; i++)",
    "    x[i][j] = 2 * x[i][j];"]})
s.obj({"id": "li2", "type": "code", "region": "center", "language": "c", "lines": [
    "/* after: inner loop goes along a row */",
    "for (i = 0; i < 5000; i++)",
    "  for (j = 0; j < 100; j++)",
    "    x[i][j] = 2 * x[i][j];"]})
s.obj({"id": "grid", "type": "table", "region": "center", "columns": ["x", "[0]", "[1]", "[2]", "[3]", "[4]", "[5]", "[6]", "[7]"], "rows": [
    ["row 0", "", "", "", "", "", "", "", ""],
    ["row 1", "", "", "", "", "", "", "", ""],
    ["row 2", "", "", "", "", "", "", "", ""],
    ["row 3", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "lim", "type": "math", "region": "center", "lines": [
    "\"column order:\" quad 5000 times 100 = 500000 \"misses\"",
    "\"row order:\" quad 500000 / 8 = 62500 \"misses\" quad \"8 times fewer\""]})
s.obj({"id": "bl1", "type": "code", "region": "center", "language": "c", "lines": [
    "/* x = y * z, all N x N */",
    "for (i = 0; i < N; i++)",
    "  for (j = 0; j < N; j++) {",
    "    r = 0;",
    "    for (k = 0; k < N; k++)",
    "      r = r + y[i][k] * z[k][j];",
    "    x[i][j] = r;",
    "  }"]})
s.obj({"id": "bl2", "type": "code", "region": "center", "language": "c", "lines": [
    "/* blocked: work on B x B tiles */",
    "for (jj = 0; jj < N; jj += B)",
    "  for (kk = 0; kk < N; kk += B)",
    "    for (i = 0; i < N; i++)",
    "      for (j = jj; j < min(jj + B, N); j++) {",
    "        r = 0;",
    "        for (k = kk; k < min(kk + B, N); k++)",
    "          r = r + y[i][k] * z[k][j];",
    "        x[i][j] = x[i][j] + r;",
    "      }"]})
s.obj({"id": "blm", "type": "math", "region": "center", "lines": [
    "\"naive, worst case:\" quad 2 N^3 + N^2 \"words from memory\"",
    "\"blocked:\" quad (2 N^3) / B + N^2 \"words\"",
    "N = 512, B = 32 : quad 268 \"million\" quad -> quad 8.65 \"million\" quad \"about 31 times fewer\"",
    "\"three tiles must fit:\" quad 3 times 32^2 times 8 \"B\" = 24 \"KB\" <= 32 \"KB L1\""]})
s.obj({"id": "co", "type": "table", "region": "center", "columns": ["other compiler tricks", "what they do"], "rows": [
    ["merging arrays", "two arrays used together become one array of pairs: one block brings both"],
    ["loop fusion", "two loops over the same data become one: reuse while it is still cached"]]})
s.obj({"id": "hp", "type": "table", "region": "center", "columns": ["hardware prefetcher", "how it guesses"], "rows": [
    ["next-line", "on a miss to block i, also fetch block i + 1"],
    ["stream buffer", "keeps the next few blocks in a small buffer beside the cache"],
    ["stride", "notices a load stepping by a fixed distance, fetches ahead along it"]]})
s.obj({"id": "pt", "type": "timeline", "region": "center", "lanes": ["no prefetch: CPU", "prefetch: CPU", "prefetch: memory"], "end": 185, "unit": "cycles", "now": 0, "blocks": []})
s.obj({"id": "ptm", "type": "math", "region": "center", "lines": [
    "\"prefetch distance\" = ceil(\"memory latency\" / \"time per iteration\")",
    "\"latency 30, iteration 30:\" quad 1 \"ahead\" quad \"latency 90:\" quad 3 \"ahead\"",
    "\"costs: memory bandwidth, and useless prefetches push out useful blocks\""]})
s.obj({"id": "cp", "type": "code", "region": "center", "language": "c", "lines": [
    "for (i = 0; i < 3; i = i + 1)",
    "  for (j = 0; j < 100; j = j + 1)",
    "    a[i][j] = b[j][0] * b[j+1][0];"]})
s.obj({"id": "cpm", "type": "math", "region": "center", "lines": [
    "\"8 KB direct-mapped, 16 B blocks, 8 B elements\"",
    "a: quad 300 / 2 = 150 \"misses\" quad quad b: quad 101 \"misses\" quad \"total\" quad 251",
    "\"prefetch 7 iterations ahead:\" quad 7 + 4 + 4 + 4 = 19 \"misses\"",
    "\"cost:\" quad 400 \"prefetch instructions\""]})
s.obj({"id": "cpx", "type": "table", "region": "center", "columns": ["kind", "meaning"], "rows": [
    ["cache prefetch", "loads the block into the cache only: the usual kind"],
    ["register prefetch", "loads the value into a register"],
    ["nonfaulting", "a bad address is simply ignored: the prefetch becomes a no-op"],
    ["needs", "a nonblocking cache, so the CPU keeps running while prefetches are in flight"]]})
s.obj({"id": "hb", "type": "table", "region": "center", "columns": ["design", "tags", "problem"], "rows": [
    ["1 GB, 64 B blocks, tags in SRAM", "2²⁴ blocks × 6 B = 96 MB", "far more SRAM than the chip has"],
    ["1 GB, 4 KB blocks, tags in SRAM", "2¹⁸ blocks × 6 B = 1.5 MB", "moves 4 KB per miss: wasted bandwidth"],
    ["64 B blocks, tags in the HBM", "no SRAM needed", "two DRAM accesses: tag, then data"],
    ["alloy cache", "tag and data side by side, direct-mapped", "one burst brings both: one access"]]})
s.obj({"id": "all", "type": "table", "region": "center", "columns": ["optimization", "hit time", "bandwidth", "miss penalty", "miss rate"], "rows": [
    ["small, simple L1", "better", "", "", "worse"],
    ["way prediction", "better", "", "", ""],
    ["pipelined access", "worse", "better", "", ""],
    ["multibanked", "", "better", "", ""],
    ["nonblocking", "", "better", "better", ""],
    ["critical word first", "", "", "better", ""],
    ["merging write buffer", "", "", "better", ""],
    ["compiler optimizations", "", "", "", "better"],
    ["prefetching", "", "", "better", "better"],
    ["HBM as a cache", "", "", "better", "better"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["double x[1024][1024], 64 B blocks, small cache", "a) misses: column order, row order"],
    ["iteration 25 cycles, memory latency 100", "b) the prefetch distance"],
    ["512 MB HBM cache, 64 B blocks, 4 B tag each", "c) the tag storage"],
    ["blocked matrix multiply, doubles, 32 KB L1", "d) the largest power-of-two tile B"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 1024 times 1024 = 1048576 \"misses\" quad \"vs\" quad 1048576 / 8 = 131072",
    "\"b)\" quad ceil(100 / 25) = 4 \"iterations ahead\"",
    "\"c)\" quad (512 \"MB\") / (64 \"B\") = 8 \"M blocks\" quad times 4 \"B\" = 32 \"MB\"",
    "\"d)\" quad 3 B^2 times 8 <= 32768 quad => quad B^2 <= 1365 quad => quad B = 32"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}


def blk(id, lane, a, b, label, d=0):
    return {"action": "add_block", "target": "pt", "id": id, "lane": lane, "start": a, "end": b, "label": label, **({"delay": d} if d else {})}


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Part 1 sped up the cache hardware. Part 2 attacks misses from two other sides: the program itself, and fetching data before it is needed.", [s.head("Ten advanced cache optimizations: part 2")])
s.step("Here are the eight stages.", show("stages"))
s.step("Two compiler techniques, two kinds of prefetching, and HBM. Then all ten on one table, and an exam question.", [hl("stages[1..=5]"), hl("stages[6..=7]", 0.6)])

# ---------------------------------------------------------------- where
s.scene("where")
s.step("Stage 1: the last three of the ten.", [s.head("Stage 1 of 8: where part 2 fits")] + hide("stages") + show("p2"))
s.step("Number 8: compiler optimizations. They lower the miss rate with no new hardware at all, just by changing the order of the work.", [hl("p2[0]")])
s.step("Number 9: prefetching, by hardware or by instructions the compiler inserts. Fetch the block before the program asks for it.", [hl("p2[1..=2]")])
s.step("Number 10: a large stacked DRAM, HBM, used as one more cache level before main memory.", [hl("p2[3]"), s.take("change the program · fetch early · add a huge cache")])

# ---------------------------------------------------------------- interchange
s.scene("interchange")
s.step("Stage 2: loop interchange. Here is a loop that doubles every element of an array x, 5000 rows by 100 columns.", [s.head("Stage 2 of 8: loop interchange"), s.untake()] + hide("p2") + show("li1") + [ml("li1", 2, 4)])
s.step("C stores arrays row by row. So x of i, j and x of i, j plus 1 sit next to each other, and a 64 byte block holds 8 doubles of one row.", [go("li1", 4)])
s.step("Look at the order. The inner loop changes i, so it walks down a column.", [go("li1", 3)] + show("grid") + hide("li1"))
s.step("x 0 0, then x 1 0, then x 2 0, then x 3 0. Every access is in a different row, so a different block.", [st("grid[0][1]", "1"), st("grid[1][1]", "2", 0.25), st("grid[2][1]", "3", 0.5), st("grid[3][1]", "4", 0.75), hl("grid[0..=3]", 0.8)])
s.step("With 5000 rows, the cache cannot hold them all. By the time the loop comes back for x 0 1, that block has long been evicted. Every access misses.", [st("grid[0][2]", "5001"), hl("grid[0][2]", 0.3)])
s.step("Now swap the two loops. The inner loop changes j, walking along a row.", [st(f"grid[{r}][{c}]", "") for r in range(4) for c in (1, 2)] + show("li2") + hide("grid") + [ml("li2", 2, 4)])
s.step("The first access to a row misses and brings in 8 elements. The next 7 accesses hit.", hide("li2") + show("grid") + [st(f"grid[0][{c}]", str(c), 0.1 * c) for c in range(1, 9)] + [mk("grid[0][1]"), hl("grid[0]", 0.9)])
s.step("The count: column order, 500 thousand misses. Row order, one in eight: 62500. Eight times fewer, and the program computes exactly the same thing.", hide("grid") + show("lim") + [hl("lim[0]")] + rv("lim", 1))
s.step("Same work, same answer, a different order. That is all a compiler optimization does.", [s.take("walk arrays in the order they are stored")])

# ---------------------------------------------------------------- blocking
s.scene("blocking")
s.step("Stage 3: blocking. Some programs cannot be fixed by swapping loops. Matrix multiply reads y along rows, but z down columns.", [s.head("Stage 3 of 8: blocking"), s.untake()] + hide("lim") + show("bl1") + [go("bl1", 6)])
s.step("For one row of x, the loop reads one row of y, and all N columns of z: the whole of z.", [ml("bl1", 2, 6)])
s.step("If z does not fit in the cache, every pass evicts it. In the worst case, 2 N cubed plus N squared words come from memory.", hide("bl1") + show("blm") + [hl("blm[0]")])
s.step("Blocking works on small B by B tiles, sized so they stay in the cache while they are reused.", hide("blm") + show("bl2") + [ml("bl2", 1, 3)])
s.step("The two outer loops pick a tile. The inner loops do all the work that tile allows, before moving on.", [ml("bl2", 4, 9)])
s.step("Now each word fetched is used B times before it leaves. Memory traffic falls to 2 N cubed over B, plus N squared.", hide("bl2") + show("blm") + rv("blm", 1))
s.step("For N of 512 and B of 32: from about 268 million words, to about 8.65 million. 31 times fewer.", rv("blm", 2))
s.step("Choose B so that three tiles fit: 3 times 32 squared times 8 bytes is 24 kilobytes. That fits a 32 kilobyte L1.", rv("blm", 3) + [s.take("blocking: reuse a tile while it is still in the cache")])
s.step("Two smaller tricks. Merging arrays: two arrays always used together become one array of pairs, so one block brings both.", hide("blm") + [s.untake()] + show("co") + [hl("co[0]")])
s.step("Loop fusion: two loops over the same data become one, so the data is reused while it is still cached.", [hl("co[1]")])

# ---------------------------------------------------------------- hardware prefetching
s.scene("hwpf")
s.step("Stage 4: hardware prefetching. The hardware guesses which blocks come next, and fetches them before they are asked for.", [s.head("Stage 4 of 8: hardware prefetching")] + hide("co") + show("hp"))
s.step("The simplest: on a miss to block i, also fetch block i plus 1. It suits code, and arrays read in order.", [hl("hp[0]")])
s.step("A stream buffer holds the next few blocks beside the cache, so wrong guesses do not evict anything.", [hl("hp[1]")])
s.step("A stride prefetcher notices a load stepping by a fixed distance, say every 256 bytes, and runs ahead along it. Modern cores, the Core i7 among them, prefetch into L1 and L2.", [hl("hp[2]")])
s.step("Why it helps, in a timeline. Each loop iteration computes for 30 cycles, and needs a new block that takes 30 cycles to fetch.", hide("hp") + show("pt"))
s.step("Without prefetching: miss, wait 30, compute 30. Again and again. Three iterations take 180 cycles.", [blk("n0", "no prefetch: CPU", 0, 30, "miss"), blk("n1", "no prefetch: CPU", 30, 60, "iter 1", 0.15), blk("n2", "no prefetch: CPU", 60, 90, "miss", 0.3), blk("n3", "no prefetch: CPU", 90, 120, "iter 2", 0.45), blk("n4", "no prefetch: CPU", 120, 150, "miss", 0.6), blk("n5", "no prefetch: CPU", 150, 180, "iter 3", 0.75)])
s.step("With prefetching one block ahead: the first miss still waits. But while iteration 1 computes, the next block is already on its way.", [blk("p0", "prefetch: CPU", 0, 30, "miss"), blk("m0", "prefetch: memory", 0, 30, "block 1", 0.1), blk("p1", "prefetch: CPU", 30, 60, "iter 1", 0.3), blk("m1", "prefetch: memory", 30, 60, "block 2", 0.4)])
s.step("Each block arrives just as it is needed. Three iterations take 120 cycles instead of 180.", [blk("p2", "prefetch: CPU", 60, 90, "iter 2"), blk("m2", "prefetch: memory", 60, 90, "block 3", 0.2), blk("p3", "prefetch: CPU", 90, 120, "iter 3", 0.4)])
s.step("How far ahead to prefetch? Memory latency over the time per iteration, rounded up.", hide("pt") + show("ptm") + [hl("ptm[0]")])
s.step("Latency 30 with 30 cycle iterations: one ahead. If latency were 90, three ahead.", rv("ptm", 1))
s.step("The costs: prefetches use memory bandwidth, and a wrong guess can push useful blocks out. So prefetchers back off when their guesses keep missing.", rv("ptm", 2) + [s.take("prefetch distance = latency ÷ iteration time, rounded up")])

# ---------------------------------------------------------------- compiler prefetching
s.scene("swpf")
s.step("Stage 5: compiler-controlled prefetching. The compiler inserts prefetch instructions, because it can see the loop's future addresses.", [s.head("Stage 5 of 8: compiler-controlled prefetching"), s.untake()] + hide("ptm") + show("cpx") + [hl("cpx[0]")])
s.step("A cache prefetch only brings the block into the cache. A register prefetch loads the value itself.", [hl("cpx[1]")])
s.step("Prefetches are nonfaulting: a bad address is ignored rather than crashing the program. And the cache must be nonblocking, so the CPU runs on while they are in flight.", [hl("cpx[2]"), hl("cpx[3]", 0.5)])
s.step("The textbook's example. a is 3 by 100, b is 101 by 3, all 8 byte doubles, in an 8 kilobyte direct-mapped cache with 16 byte blocks.", hide("cpx") + show("cp") + [ml("cp", 1, 3)])
s.step("a is written in row order, two elements per block: 300 over 2, 150 misses.", [go("cp", 3)] + show("cpm") + [hl("cpm[0]")] + rv("cpm", 1) + hide("cp"))
s.step("b is read down column 0: b of j, 0 and b of j plus 1, 0. 101 different blocks, missed only on the first pass of i. 251 misses in all.", [hl("cpm[1]")])
s.step("Now the compiler adds prefetches for a and b, 7 iterations ahead. Only the first 7 iterations of each row still miss: 7 for b, and 4 for each row of a. 19 misses.", rv("cpm", 2))
s.step("The cost: 400 extra prefetch instructions. Worth it only if the misses saved outweigh them.", rv("cpm", 3) + [s.take("251 misses → 19, for 400 prefetch instructions")])

# ---------------------------------------------------------------- HBM
s.scene("hbm")
s.step("Stage 6: HBM as an extra cache level. Put a gigabyte of stacked DRAM in the package, and use it as an L4 cache in front of main memory.", [s.head("Stage 6 of 8: HBM as an extra cache level"), s.untake()] + hide("cpm") + show("hb"))
s.step("The problem is the tags. With 64 byte blocks, 1 gigabyte is 2 to the 24 blocks. At 6 bytes of tag and state each, that is 96 megabytes of tags: far more SRAM than the chip has.", [hl("hb[0]")])
s.step("Use 4 kilobyte blocks, and the tags shrink to 1.5 megabytes. But every miss moves 4 kilobytes, most of it never used.", [hl("hb[1]")])
s.step("Or keep 64 byte blocks, and store the tags in the HBM itself. Now each access needs two DRAM reads: first the tag, then the data.", [hl("hb[2]")])
s.step("The alloy cache fixes that: direct-mapped, with each tag stored right beside its data, so one burst brings both. One access, not two.", [hl("hb[3]")])
s.step("Designs also add a predictor that guesses a miss early, and starts the main memory access at once.", [mk("hb[3]"), s.take("an HBM cache lives or dies by where its tags are kept")])

# ---------------------------------------------------------------- all ten
s.scene("all")
s.step("Stage 7: all ten advanced optimizations on one table.", [s.head("Stage 7 of 8: all ten"), s.untake()] + hide("hb") + show("all"))
s.step("Two cut the hit time.", [hl("all[0..=1]")])
s.step("Three raise bandwidth. Pipelining pays for it with more cycles per hit.", [hl("all[2..=4]")])
s.step("Two cut the miss penalty.", [hl("all[5..=6]")])
s.step("And the three from this video lower the miss rate, or hide the miss penalty.", [hl("all[7..=9]"), s.take("no optimization is free: check what it worsens")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("all") + show("q"))
s.step("An array of doubles, 1024 by 1024, stored by rows, with 64 byte blocks. How many misses for one pass in column order, and in row order?", [hl("q[0]")])
s.step("A loop iteration takes 25 cycles and memory 100: how far ahead to prefetch? A 512 megabyte HBM cache with 64 byte blocks and 4 bytes of tag each: how much tag storage? And the largest power-of-two tile for blocked matrix multiply in a 32 kilobyte L1. Pause and work it out.", [hl("q[1]"), hl("q[2]", 0.3), hl("q[3]", 0.6)])
s.step("a: column order misses on every element, 1024 times 1024, about 1.05 million. Row order misses once per 8 doubles: 131072.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 100 over 25 is 4. Prefetch 4 iterations ahead.", rv("qa", 1))
s.step("c: 512 megabytes over 64 bytes is 8 million blocks, times 4 bytes: 32 megabytes of tags.", rv("qa", 2))
s.step("d: three tiles of B squared doubles must fit in 32768 bytes, so B squared is at most 1365. The largest power of two is 32.", rv("qa", 3))
s.step("The usual slips: forgetting that C stores arrays by rows, and sizing a tile for one matrix instead of three.", [s.take("C is row-major · a tile size must fit three tiles")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Loop interchange and blocking lower the miss rate by reordering the work.", [hl("stages[1..=2]")])
s.step("Prefetching, by hardware or compiler, fetches blocks before they are needed. And HBM adds a huge cache level, if its tags are handled well.", [hl("stages[3..=5]")])
s.step("Next video: virtual memory and the TLB.", [mk("stages[0..=7]"), s.take("Next: virtual memory and the TLB")])

s.save("/home/claude/playlist/m2v11.json")

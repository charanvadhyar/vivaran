"""Module 2, video 9: memory technology: SRAM, DRAM organization and timing, refresh, DDR bandwidth, GDDR/HBM, flash."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

r = lambda x, n=2: round(x, n)
assert r(3200e6 * 8 / 1e9, 1) == 25.6 and r(4800e6 * 8 / 1e9, 1) == 38.4 and r(8 / 3200e6 * 1e9, 2) == 2.5 and 42 + 2.5 == 44.5
assert r(8192 * 50e-9 / 64e-3 * 100, 2) == 0.64 and r(64e-3 / 8192 * 1e6, 2) == 7.81
assert r(2e9 * 1024 / 8 / 1e9) == 256 and r(6.4e9 * 1024 / 8 / 1e9, 1) == 819.2
assert r(2400e6 * 8 * 2 / 1e9, 1) == 38.4 and r(64 / (2400e6 * 8) * 1e9, 2) == 3.33 and r((45 + 64 / 19.2) * 3) == 145 and r(64e-3 / 16384 * 1e6, 2) == 3.91

s = Script("Memory technology: SRAM, DRAM, DDR, HBM and flash")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Latency and bandwidth: the two numbers that matter"],
    [2, "SRAM and DRAM cells"],
    [3, "Inside a DRAM: banks, rows, the row buffer"],
    [4, "Three kinds of DRAM access, timed"],
    [5, "Refresh"],
    [6, "SDRAM and DDR: bandwidth in numbers"],
    [7, "GDDR, HBM and flash"],
    [8, "Exam question"]]})
s.obj({"id": "met", "type": "table", "region": "center", "columns": ["metric", "meaning", "decides"], "rows": [
    ["access time", "from request to the data appearing", "how long a miss waits"],
    ["cycle time", "minimum time between two requests", "how often memory can be used"],
    ["bandwidth", "bytes delivered per second", "how fast a whole block arrives"]]})
s.obj({"id": "cell", "type": "table", "region": "center", "columns": ["", "SRAM", "DRAM"], "rows": [
    ["cell", "6 transistors", "1 transistor + 1 capacitor"],
    ["keeps data", "as long as power is on", "charge leaks: must be refreshed"],
    ["reading", "non-destructive", "destructive: the row is written back"],
    ["speed", "fast: about 1 ns", "slower: tens of ns"],
    ["density, cost", "low density, costly", "about 4 to 8 times denser, cheap"],
    ["used for", "caches, registers", "main memory"]]})
s.obj({"id": "bank", "type": "table", "region": "left", "columns": ["DRAM bank", "columns 0 … 1023"], "rows": [
    ["row 0", "…"], ["row 1", "…"], ["row 2", "…"], ["row 3", "…"], ["row buffer", "(empty)"]]})
s.obj({"id": "bx", "type": "table", "region": "right", "columns": ["step", "command", "what it does"], "rows": [
    ["1", "ACTIVATE (RAS)", "row → row buffer"],
    ["2", "READ (CAS)", "bytes from the buffer"],
    ["3", "PRECHARGE", "close the row"]]})
s.obj({"id": "acc", "type": "timeline", "region": "center", "lanes": ["row hit: row already open", "row closed", "row conflict: another row open"], "end": 45, "unit": "ns", "now": 0, "blocks": []})
s.obj({"id": "ref", "type": "math", "region": "center", "lines": [
    "\"every row refreshed every\" 64 \"ms\"",
    "8192 \"rows:\" quad (64 \"ms\") / 8192 approx 7.8 \"µs between refreshes\"",
    "\"each refresh busy 50 ns:\" quad (8192 times 50 \"ns\") / (64 \"ms\") approx 0.64% \"of the time\""]})
s.obj({"id": "ddr", "type": "math", "region": "center", "lines": [
    "\"bandwidth\" = \"transfers per second\" times \"bus width in bytes\"",
    "\"DDR4-3200:\" quad 3200 times 10^6 times 8 \"B\" = 25.6 \"GB/s per channel\"",
    "\"two channels:\" quad 51.2 \"GB/s\" quad \"DDR5-4800:\" quad 38.4 \"GB/s\"",
    "\"64 B block\" = 8 \"transfers:\" quad 8 / (3200 times 10^6) = 2.5 \"ns\"",
    "\"miss penalty, row conflict:\" quad 42 + 2.5 = 44.5 \"ns\""]})
s.obj({"id": "ddrx", "type": "table", "region": "center", "columns": ["name", "means"], "rows": [
    ["SDRAM", "synchronous: commands follow a clock, bursts of data"],
    ["DDR", "double data rate: data on both clock edges"],
    ["DDR4-3200", "3200 million transfers per second, from a 1600 MHz clock"],
    ["PC4-25600", "the module's name: 25600 MB/s"]]})
s.obj({"id": "hbm", "type": "table", "region": "center", "columns": ["memory", "how it is built", "for"], "rows": [
    ["GDDR", "fast pins, many chips around the processor", "graphics cards"],
    ["HBM", "DRAM dies stacked, 1024-bit bus on a silicon interposer", "GPUs, AI accelerators"],
    ["flash (NAND)", "non-volatile; erase in large blocks; wears out", "SSDs, phones: storage, not main memory"]]})
s.obj({"id": "hbmm", "type": "math", "region": "bottom", "lines": [
    "\"HBM stack:\" quad (1024 \"bits\" times 2 \"Gb/s per pin\") / 8 = 256 \"GB/s\" quad \"(at 6.4 Gb/s: 819 GB/s)\""]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["DDR4-2400, two channels; row conflict = 3 × 15 ns; 64 B blocks; 3 GHz CPU; 16384 rows. Find:"], "rows": [
    ["a) the peak bandwidth"], ["b) the miss penalty of one block on one channel, in ns and CPU cycles"], ["c) how often a row refresh must start"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 2400 times 10^6 times 8 \"B\" times 2 = 38.4 \"GB/s\"",
    "\"b)\" quad 45 + 64 / (19.2 \"GB/s\") = 45 + 3.33 approx 48.3 \"ns\" quad times 3 \"GHz\" = 145 \"cycles\"",
    "\"c)\" quad (64 \"ms\") / 16384 approx 3.9 \"µs\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
setc = lambda t, a, b, v, d=0: {"action": "set", "target": f"{t}[{a}][{b}]", "value": v, **({"delay": d} if d else {})}
blk = lambda id, lane, a, b, label, d=0: {"action": "add_block", "target": "acc", "id": id, "lane": lane, "start": a, "end": b, "label": label, **({"delay": d} if d else {})}
H, C_, X = "row hit: row already open", "row closed", "row conflict: another row open"

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Every cache miss ends up in main memory. This video opens the memory chips themselves, and puts numbers on how long a miss really takes.", [s.head("Memory technology")])
s.step("Here are the eight stages.", show("stages"))
s.step("The two metrics, the two kinds of cell, and how a DRAM chip is organized and timed.", [hl("stages[0..=3]")])
s.step("Then refresh, DDR bandwidth, the newer memories, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- metrics
s.scene("metrics")
s.step("Stage 1: memory is measured two ways.", [s.head("Stage 1 of 8: latency and bandwidth")] + hide("stages") + show("met"))
s.step("Access time: from the request until the data appears. This is what a miss waits for.", [hl("met[0]")])
s.step("Cycle time: the minimum gap between two requests. For DRAM it is longer than the access time, because a read must be followed by restoring the row.", [hl("met[1]")])
s.step("Bandwidth: how many bytes per second flow once data starts. It decides how fast a whole block arrives.", [hl("met[2]"), s.take("miss penalty ≈ latency + block size ÷ bandwidth")])

# ---------------------------------------------------------------- cells
s.scene("cells")
s.step("Stage 2: two kinds of memory cell.", [s.head("Stage 2 of 8: SRAM and DRAM")] + hide("met") + [s.untake()] + show("cell") + [hl("cell[0]")])
s.step("SRAM stores a bit in 6 transistors, two cross-coupled inverters. DRAM stores it as charge on a capacitor, with one transistor to reach it.", [hl("cell[0][1]"), hl("cell[0][2]", 0.4)])
s.step("SRAM holds its value while powered. DRAM's charge leaks away, so every cell must be refreshed, many times a second.", [hl("cell[1]")])
s.step("Reading a DRAM cell drains it, so the value must be written back after every read. That is why its cycle time exceeds its access time.", [hl("cell[2]")])
s.step("So SRAM is fast but large and costly. DRAM is slower, but several times denser and much cheaper per bit.", [hl("cell[3..=4]")])
s.step("Hence SRAM for caches and registers, DRAM for main memory.", [hl("cell[5]"), s.take("SRAM: 6T, fast, caches · DRAM: 1T1C, dense, refresh, main memory")])

# ---------------------------------------------------------------- organization
s.scene("org")
s.step("Stage 3: inside a DRAM chip. Cells are arranged in banks, each a grid of rows and columns, with one row buffer per bank.", [s.head("Stage 3 of 8: banks, rows and the row buffer")] + hide("cell") + [s.untake()] + show("bank", "bx"))
s.step("To read, the controller first sends ACTIVATE with the row address. This is the old row address strobe, RAS.", [hl("bx[0]"), hl("bank[2]", 0.3)])
s.step("The whole row, thousands of bits, is copied into the row buffer.", [setc("bank", 4, 1, "row 2 (open)"), hl("bank[4]", 0.3)])
s.step("Then READ with the column address, the column strobe, CAS, picks the wanted bytes out of the row buffer.", [hl("bx[1]"), hl("bank[4][1]", 0.3)])
s.step("Before another row of the same bank can be opened, PRECHARGE writes the open row back and empties the buffer.", [hl("bx[2]"), setc("bank", 4, 1, "(empty)", 0.5)])
s.step("Row and column addresses share the same pins, sent one after the other. That address multiplexing halves the pin count.", [s.take("ACTIVATE (row) → READ (column) → PRECHARGE")])
s.step("And because each bank has its own row buffer, several banks can work at once: the interleaving we used in the AMAT video.", [hl("bank")])

# ---------------------------------------------------------------- access timing
s.scene("timing")
s.step("Stage 4: so the time for an access depends on the row buffer. Assume each command takes about 14 nanoseconds.", [s.head("Stage 4 of 8: three kinds of access")] + hide("bank", "bx") + [s.untake()] + show("acc"))
s.step("A row hit: the row is already open, so only the column read is needed. About 14 nanoseconds.", [blk("h1", H, 0, 14, "READ 14")])
s.step("A closed row: activate it, then read. 28 nanoseconds.", [blk("c1", C_, 0, 14, "ACTIVATE 14"), blk("c2", C_, 14, 28, "READ 14", 0.3)])
s.step("A row conflict: another row is open. Precharge it, activate ours, then read. 42 nanoseconds, three times a row hit.", [blk("x1", X, 0, 14, "PRECHARGE 14"), blk("x2", X, 14, 28, "ACTIVATE 14", 0.3), blk("x3", X, 28, 42, "READ 14", 0.6)])
s.step("That is why memory controllers reorder requests to hit open rows, and why accessing memory in order is so much faster than jumping around.", [s.take("row hit ≈ 1 step · closed ≈ 2 · conflict ≈ 3")])

# ---------------------------------------------------------------- refresh
s.scene("refresh")
s.step("Stage 5: refresh. Every DRAM row must be read and rewritten before its charge leaks, typically every 64 milliseconds.", [s.head("Stage 5 of 8: refresh")] + hide("acc") + [s.untake()] + show("ref") + [hl("ref[0]")])
s.step("With 8192 rows, a row refresh must start about every 7.8 microseconds.", rv("ref", 1))
s.step("If each refresh keeps the bank busy for 50 nanoseconds, that is 8192 times 50 nanoseconds every 64 milliseconds: about 0.64 percent of the time lost.", rv("ref", 2))
s.step("Small, but it grows with bigger chips, and an access that arrives during a refresh must wait.", [s.take("refresh interval = retention time ÷ rows")])

# ---------------------------------------------------------------- DDR
s.scene("ddr")
s.step("Stage 6: modern DRAM is synchronous, SDRAM, and double data rate, DDR.", [s.head("Stage 6 of 8: SDRAM and DDR")] + hide("ref") + [s.untake()] + show("ddrx") + [hl("ddrx[0..=1]")])
s.step("DDR moves data on both edges of the clock. So DDR4-3200 runs a 1600 megahertz clock, and makes 3200 million transfers per second.", [hl("ddrx[2]")])
s.step("The module is sold by its bandwidth: PC4-25600 means 25600 megabytes per second.", [hl("ddrx[3]")])
s.step("Where does that come from? Bandwidth is transfers per second, times the bus width in bytes.", hide("ddrx") + show("ddr") + [hl("ddr[0]")])
s.step("A channel is 64 bits, 8 bytes, wide. 3200 million times 8 is 25.6 gigabytes per second.", rv("ddr", 1))
s.step("Two channels double it, 51.2. DDR5-4800 gives 38.4 per module.", rv("ddr", 2))
s.step("A 64 byte cache block is 8 transfers, a burst of 8. At 3200 million per second, that takes 2.5 nanoseconds.", rv("ddr", 3))
s.step("So a miss that hits a row conflict costs 42 plus 2.5, about 44.5 nanoseconds. The latency, not the bandwidth, dominates a single miss.", rv("ddr", 4) + [s.take("bandwidth = MT/s × 8 B per channel · latency dominates one miss")])

# ---------------------------------------------------------------- GDDR HBM flash
s.scene("hbm")
s.step("Stage 7: other memories.", [s.head("Stage 7 of 8: GDDR, HBM and flash")] + hide("ddr") + [s.untake()] + show("hbm"))
s.step("GDDR is DRAM tuned for graphics: very fast pins, many chips placed around the GPU.", [hl("hbm[0]")])
s.step("HBM, high bandwidth memory, stacks DRAM dies on top of each other and joins them to the processor through a silicon interposer, with a 1024-bit bus.", [hl("hbm[1]")])
s.step("At 2 gigabits per second per pin, one stack gives 256 gigabytes per second. Newer stacks run at 6.4, for about 819.", show("hbmm") + [hl("hbmm[0]")])
s.step("Flash is different: it keeps data without power. It reads quickly, but must erase in large blocks, and each block survives a limited number of writes, so controllers spread writes out. It is storage, not main memory.", hide("hbmm") + [hl("hbm[2]"), s.take("GDDR, HBM: bandwidth for GPUs · flash: non-volatile storage")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question")] + hide("hbm") + [s.untake()] + show("q"))
s.step("DDR4-2400 with two channels. A row conflict costs 3 times 15 nanoseconds. Blocks are 64 bytes, the CPU runs at 3 gigahertz, and the chip has 16384 rows.", [hl("q[0]")])
s.step("Find the peak bandwidth, the miss penalty of one block on one channel, and how often a refresh must start. Pause and work it out.", [hl("q[1]"), hl("q[2]", 0.4)])
s.step("a: 2400 million transfers, times 8 bytes, times 2 channels: 38.4 gigabytes per second.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: one channel gives 19.2 gigabytes per second, so 64 bytes take 3.33 nanoseconds. Add 45 of latency: about 48.3 nanoseconds. At 3 gigahertz, that is 145 CPU cycles.", rv("qa", 1))
s.step("c: 64 milliseconds over 16384 rows: a refresh every 3.9 microseconds.", rv("qa", 2))
s.step("The usual slips: forgetting that DDR's number already counts both edges, using two channels for one block, and leaving out the latency.", [s.take("MT/s already includes both edges · one block uses one channel")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap")] + hide("qa") + [s.untake()] + show("stages"))
s.step("SRAM is fast and costly, DRAM dense and refreshed. A DRAM access opens a row, reads columns, and precharges: hits are fast, conflicts slow.", [hl("stages[0..=4]")])
s.step("DDR bandwidth is transfers per second times 8 bytes per channel; HBM stacks dies for GPUs, and flash is storage.", [hl("stages[5..=7]")])
s.step("Next video: ten advanced cache optimizations, part 1.", [{"action": "mark", "target": "stages[0..=7]"}, s.take("Next: ten advanced optimizations, part 1")])

s.save("/home/claude/playlist/m2v9.json")

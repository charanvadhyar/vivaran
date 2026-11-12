"""Module 2, video 14: case studies, the memory hierarchies of the ARM Cortex-A53 and the Intel Core i7-6700 (Skylake).
Figures: Wikipedia (A53 configuration ranges, TLBs), 7-cpu.com (measured latencies, A53 on Amlogic S905 at 1.536 GHz,
i7-6700 at 4.0 GHz), Intel ARK (DDR4-2133, two channels, 34.1 GB/s)."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

r = lambda x, n=2: round(x, n)
# VIPT checks
assert 32 // 8 == 4 and 32 // 4 == 8 and 32 // 2 == 16
# TLB reach
assert 512 * 4 == 2048 and 1536 * 4 == 6144 and 1536 * 2 == 3072 and 64 * 4 == 256
# AMAT with measured latencies, assumed miss rates
a53_mem = 15 + round(128 * 1.5)          # 15 cycles + 128 ns at 1.5 GHz
assert a53_mem == 207
assert r(3 + 0.05 * (15 + 0.3 * 200)) == 6.75 and r(6.75 / 1.5) == 4.5
i7_mem = 42 + 51 * 4                      # 42 cycles + 51 ns at 4 GHz
assert i7_mem == 246
assert r(4 + 0.05 * (12 + 0.3 * (42 + 0.2 * 246))) == 5.97 and r(5.968 / 4, 2) == 1.49
# bandwidth
assert r(2 * 2133e6 * 8 / 1e9, 1) == 34.1
# exam
assert r(3 + 0.04 * (15 + 0.25 * 200)) == 5.6

s = Script("Case studies: ARM Cortex-A53 and Intel Core i7")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Two very different processors"],
    [2, "The Cortex-A53's caches"],
    [3, "The Cortex-A53's address translation"],
    [4, "The Core i7-6700's caches"],
    [5, "The Core i7-6700's TLBs and memory"],
    [6, "Side by side, with AMAT"],
    [7, "Why they differ"],
    [8, "Exam question"]]})
s.obj({"id": "two", "type": "table", "region": "center", "columns": ["", "ARM Cortex-A53", "Intel Core i7-6700 (Skylake)"], "rows": [
    ["found in", "phones, Raspberry Pi 3, embedded boards", "desktop PCs (2015)"],
    ["pipeline", "8 stages, 2-wide, in order", "deep, 4-wide, out of order"],
    ["clock", "about 1.2 to 2 GHz", "3.4 GHz, up to 4.0 GHz"],
    ["goal", "low power, small area", "single-thread speed"]]})
s.obj({"id": "a53", "type": "table", "region": "center", "columns": ["A53 level", "size", "organization", "latency (measured)"], "rows": [
    ["L1 instruction", "8–64 KB, the chip maker's choice", "2-way, 64 B lines, VIPT", ""],
    ["L1 data", "8–64 KB", "4-way, 64 B lines, PIPT", "3 cycles"],
    ["L2, shared by the cores", "128 KB to 2 MB", "16-way, 64 B lines", "15 cycles"],
    ["main memory", "LPDDR or DDR", "", "15 cycles + 128 ns"]]})
s.obj({"id": "a53t", "type": "table", "region": "center", "columns": ["A53 translation", "entries", "role"], "rows": [
    ["micro TLB (data)", "10", "tiny and fast: checked first"],
    ["main TLB", "512, 4-way", "on a micro TLB miss, a few cycles more"],
    ["page walk cache", "64, 4-way", "keeps upper page table levels, shortening a walk"],
    ["page walk", "in hardware", "reads the page table through L2 and memory"]]})
s.obj({"id": "vp", "type": "math", "region": "center", "lines": [
    "\"VIPT needs\" quad \"size\" / \"ways\" <= 4 \"KB page\"",
    "\"A53 L1 data, 32 KB 4-way:\" quad 32 / 4 = 8 \"KB\" > 4 quad -> quad \"PIPT: translate first\"",
    "\"i7 L1 data, 32 KB 8-way:\" quad 32 / 8 = 4 \"KB\" <= 4 quad -> quad \"VIPT: in parallel\""]})
s.obj({"id": "i7", "type": "table", "region": "center", "columns": ["i7-6700 level", "size", "organization", "latency (measured)"], "rows": [
    ["L1 instruction", "32 KB per core", "8-way, 64 B lines", ""],
    ["L1 data", "32 KB per core", "8-way, 64 B lines", "4 cycles"],
    ["L2", "256 KB per core", "4-way, 64 B lines", "12 cycles"],
    ["L3, shared by 4 cores", "8 MB", "16-way, 64 B lines, inclusive", "about 42 cycles"],
    ["main memory", "DDR4-2133, 2 channels", "", "42 cycles + about 51 ns"]]})
s.obj({"id": "i7t", "type": "table", "region": "center", "columns": ["i7-6700 TLB", "entries (4 KB pages)", "notes"], "rows": [
    ["L1 instruction TLB", "128, 8-way", ""],
    ["L1 data TLB", "64, 4-way", "miss costs about 9 cycles"],
    ["L2 TLB (shared)", "1536, 12-way", "also holds 2 MB page entries"],
    ["virtual address", "48 bits", "4-level page table, walked in hardware"]]})
s.obj({"id": "bw", "type": "math", "region": "center", "lines": [
    "\"DDR4-2133, two channels:\" quad 2 times 2133 times 10^6 times 8 \"B\" approx 34.1 \"GB/s\"",
    "\"TLB reach, 4 KB pages:\" quad 64 times 4 \"KB\" = 256 \"KB\" quad 1536 times 4 \"KB\" = 6 \"MB\"",
    "\"with 2 MB pages:\" quad 1536 times 2 \"MB\" = 3 \"GB\""]})
s.obj({"id": "sbs", "type": "table", "region": "center", "columns": ["", "Cortex-A53", "Core i7-6700"], "rows": [
    ["cache levels", "2", "3"],
    ["L1 data", "8–64 KB, 4-way, PIPT, 3 cycles", "32 KB, 8-way, VIPT, 4 cycles"],
    ["last level", "L2: up to 2 MB, 15 cycles", "L3: 8 MB, about 42 cycles"],
    ["memory", "about 207 cycles at 1.5 GHz", "about 246 cycles at 4 GHz"],
    ["last-level TLB", "512 entries", "1536 entries"]]})
s.obj({"id": "am", "type": "math", "region": "center", "lines": [
    "\"assumed miss rates: L1 5%, L2 local 30%, L3 local 20%\"",
    "\"A53:\" quad 3 + 0.05 times (15 + 0.3 times 200) = 6.75 \"cycles\" = 4.5 \"ns at 1.5 GHz\"",
    "\"i7:\" quad 4 + 0.05 times (12 + 0.3 times (42 + 0.2 times 246)) approx 5.97 \"cycles\"",
    "5.97 \"cycles at 4 GHz\" approx 1.49 \"ns\""]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["choice", "A53: power and area", "i7: speed"], "rows": [
    ["L1 size", "configurable: small chips save area", "fixed 32 KB at full speed"],
    ["L1 data indexing", "PIPT, with a 10-entry micro TLB", "8 ways so that VIPT works"],
    ["levels", "two: an L3 costs power and area", "three: a big shared L3 hides memory"],
    ["out-of-order", "no: a miss stalls the pipeline", "yes: many misses in flight at once"],
    ["prefetching", "simple stream prefetch", "several aggressive prefetchers"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["4 KB pages; A53 L1D 32 KB 4-way; i7 L1D 32 KB 8-way", "a) which can be VIPT?"],
    ["A53 main TLB 512 entries; i7 L2 TLB 1536 entries", "b) TLB reach of each, 4 KB pages"],
    ["i7: DDR4-2133, two channels, 8 B each", "c) peak memory bandwidth"],
    ["A53: L1 3, L2 15, memory 200 cycles; misses 4%, 25%", "d) AMAT in cycles"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad \"A53:\" 32 / 4 = 8 \"KB\" > 4 \"KB: no\" quad \"i7:\" 32 / 8 = 4 \"KB: yes\"",
    "\"b)\" quad 512 times 4 \"KB\" = 2 \"MB\" quad 1536 times 4 \"KB\" = 6 \"MB\"",
    "\"c)\" quad 2 times 2133 times 10^6 times 8 approx 34.1 \"GB/s\"",
    "\"d)\" quad 3 + 0.04 times (15 + 0.25 times 200) = 3 + 0.04 times 65 = 5.6 \"cycles\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("After a whole module of theory, two real chips: a small ARM core found in phones, and an Intel desktop processor. Every idea from this module shows up in them.", [s.head("Case studies: Cortex-A53 and Core i7")])
s.step("Here are the eight stages.", show("stages"))
s.step("The two processors, then each one's caches and address translation.", [hl("stages[0..=4]")])
s.step("Then side by side with AMAT, why they differ, and an exam question.", [hl("stages[5..=7]")])

# ---------------------------------------------------------------- two
s.scene("two")
s.step("Stage 1: two very different processors.", [s.head("Stage 1 of 8: two processors")] + hide("stages") + show("two"))
s.step("The ARM Cortex-A53 is everywhere: phones, the Raspberry Pi 3, embedded boards. The Core i7-6700 is a 2015 desktop chip from Intel's Skylake family.", [hl("two[0]")])
s.step("The A53 has a short 8-stage pipeline, issuing 2 instructions per cycle, in order. The i7 is 4-wide and out of order, with a much deeper pipeline.", [hl("two[1]")])
s.step("The A53 runs at about 1.2 to 2 gigahertz, the i7 at 3.4, boosting to 4.", [hl("two[2]")])
s.step("And the goals are opposite. The A53 is built for low power and a small area. The i7 is built for speed on one thread.", [hl("two[3]"), s.take("same ideas, opposite goals: power versus speed")])

# ---------------------------------------------------------------- A53 caches
s.scene("a53")
s.step("Stage 2: the A53's caches. The latencies here were measured on a board running at 1.5 gigahertz.", [s.head("Stage 2 of 8: the Cortex-A53's caches"), s.untake()] + hide("two") + show("a53"))
s.step("Two L1 caches per core, instructions and data. ARM lets the chip maker pick each size, from 8 to 64 kilobytes. A small chip saves area; a phone chip may pick 32.", [hl("a53[0..=1]")])
s.step("The instruction cache is 2-way, the data cache 4-way. Both use 64 byte lines. A data hit takes 3 cycles.", [hl("a53[0][2]"), hl("a53[1][2]", 0.3), hl("a53[1][3]", 0.6)])
s.step("The L2 is shared by all the cores, 128 kilobytes to 2 megabytes, and 16-way. A hit takes about 15 cycles.", [hl("a53[2]")])
s.step("There is no L3. A miss in L2 goes to memory: 15 cycles plus about 128 nanoseconds. At 1.5 gigahertz that is about 207 cycles.", [hl("a53[3]"), s.take("A53: L1 3 cycles · L2 15 · memory ≈ 200")])
s.step("Look at the indexing. The instruction cache is virtually indexed, VIPT. The data cache is physically indexed, PIPT. Why?", [s.untake(), mk("a53[0][2]"), mk("a53[1][2]", 0.4)])
s.step("Apply the VIPT condition from earlier: size over ways must not exceed the page size.", hide("a53") + show("vp") + [hl("vp[0]")])
s.step("The A53's 32 kilobyte, 4-way data cache gives 8 kilobytes per way, more than a 4 kilobyte page. So it cannot simply index with the virtual address. It translates first.", rv("vp", 1))
s.step("The i7's 32 kilobyte cache uses 8 ways: exactly 4 kilobytes per way. So it can be VIPT. Remember that when we reach the i7.", rv("vp", 2) + [s.take("more ways can make VIPT possible")])

# ---------------------------------------------------------------- A53 translation
s.scene("a53tlb")
s.step("Stage 3: if the A53 translates before every data access, translation must be very fast.", [s.head("Stage 3 of 8: the A53's address translation"), s.untake()] + hide("vp") + show("a53t"))
s.step("So it has a micro TLB of just 10 entries. Tiny, so it answers almost instantly.", [hl("a53t[0]")])
s.step("Behind it, a main TLB of 512 entries, 4-way. A micro TLB miss that hits here costs only a couple of cycles.", [hl("a53t[1]")])
s.step("If both miss, a page walk cache of 64 entries keeps the upper levels of the page table, so most walks skip straight to the last level.", [hl("a53t[2]")])
s.step("And the walk itself is done in hardware, reading page table entries through the L2 cache. This is the TLB hierarchy we built in the virtual memory video, in miniature.", [hl("a53t[3]"), s.take("micro TLB 10 → main TLB 512 → walk cache → page walk")])

# ---------------------------------------------------------------- i7 caches
s.scene("i7")
s.step("Stage 4: the Core i7-6700. Its latencies were measured at 4 gigahertz.", [s.head("Stage 4 of 8: the Core i7-6700's caches"), s.untake()] + hide("a53t") + show("i7"))
s.step("Each of the 4 cores has 32 kilobytes of instruction cache and 32 of data, both 8-way with 64 byte lines. A data hit takes 4 cycles.", [hl("i7[0..=1]")])
s.step("Each core also has a private L2 of 256 kilobytes, 4-way, at 12 cycles.", [hl("i7[2]")])
s.step("Then an L3 of 8 megabytes, 16-way, shared by all four cores, at about 42 cycles. It is inclusive: everything in the L1s and L2s is also in L3, which makes checking other cores' data simpler.", [hl("i7[3]")])
s.step("Memory is DDR4-2133 on two channels. A miss all the way out costs about 42 cycles plus 51 nanoseconds: about 246 cycles at 4 gigahertz.", [hl("i7[4]"), s.take("i7: L1 4 · L2 12 · L3 ≈ 42 · memory ≈ 246 cycles")])

# ---------------------------------------------------------------- i7 TLB
s.scene("i7tlb")
s.step("Stage 5: the i7's translation.", [s.head("Stage 5 of 8: the i7's TLBs and memory"), s.untake()] + hide("i7") + show("i7t"))
s.step("Separate first-level TLBs: 128 entries for instructions, 8-way, and 64 entries for data, 4-way.", [hl("i7t[0..=1]")])
s.step("Behind them, a shared second-level TLB of 1536 entries, 12-way, that also holds entries for 2 megabyte pages. A data TLB miss that hits here costs about 9 cycles.", [hl("i7t[2]")])
s.step("Virtual addresses are 48 bits, with the 4-level page table we drew earlier, walked in hardware.", [hl("i7t[3]")])
s.step("Some numbers. Peak memory bandwidth: 2 channels, times 2133 million transfers, times 8 bytes. About 34.1 gigabytes per second.", hide("i7t") + show("bw") + [hl("bw[0]")])
s.step("TLB reach with 4 kilobyte pages: the 64-entry data TLB covers 256 kilobytes, the 1536-entry L2 TLB 6 megabytes.", rv("bw", 1))
s.step("With 2 megabyte pages, the L2 TLB covers 3 gigabytes. That is why databases and virtual machines ask for huge pages.", rv("bw", 2) + [s.take("TLB reach = entries × page size")])

# ---------------------------------------------------------------- side by side
s.scene("sbs")
s.step("Stage 6: side by side.", [s.head("Stage 6 of 8: side by side"), s.untake()] + hide("bw") + show("sbs"))
s.step("Two cache levels against three. The A53's L1 is configurable and physically indexed; the i7's is fixed, 8-way, and virtually indexed.", [hl("sbs[0..=1]")])
s.step("The A53's last level is a small, fast L2. The i7's is a big L3, three times slower to reach, but four times larger.", [hl("sbs[2]")])
s.step("Memory costs a similar number of cycles in both, about 200 to 250. But the i7's cycles are almost three times shorter.", [hl("sbs[3]")])
s.step("Now AMAT. The latencies are measured, with the A53's memory rounded to 200 cycles. The miss rates are assumptions, for illustration.", hide("sbs") + show("am") + [hl("am[0]")])
s.step("A53: 3, plus 0.05 times, 15 plus 0.3 times 200. 6.75 cycles. At 1.5 gigahertz, 4.5 nanoseconds.", rv("am", 1))
s.step("i7: 4, plus 0.05 times, 12 plus 0.3 times, 42 plus 0.2 times 246. About 6 cycles. At 4 gigahertz, about 1.5 nanoseconds.", rv("am", 2) + rv("am", 3))
s.step("Similar in cycles, three times apart in time. The extra L3 keeps the i7's AMAT low even though memory is farther away in cycles.", [s.take("compare AMAT in nanoseconds, not just cycles")])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 7: why did the designers choose so differently? Every row is a trade-off from this module.", [s.head("Stage 7 of 8: why they differ"), s.untake()] + hide("am") + show("why"))
s.step("L1 size: ARM lets small chips save area. Intel fixes 32 kilobytes, the largest that still hits in 4 cycles at 4 gigahertz.", [hl("why[0]")])
s.step("Indexing: the A53 pays for translation with a tiny micro TLB. The i7 uses 8 ways precisely so that VIPT works.", [hl("why[1]")])
s.step("Levels: an L3 costs power and area that a phone core cannot spare. The i7 spends them to hide memory.", [hl("why[2]")])
s.step("And out-of-order execution: when the A53 misses, its in-order pipeline waits. The i7 keeps running, with many misses in flight, the nonblocking caches of the advanced optimizations video.", [hl("why[3]")])
s.step("Prefetching follows the same pattern: simple on the A53, several aggressive prefetchers on the i7.", [hl("why[4]"), s.take("every design choice is a trade-off you can now compute")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now the exam question.", [s.head("Exam question"), s.untake()] + hide("why") + show("q"))
s.step("With 4 kilobyte pages: which L1 data cache can be VIPT? And the TLB reach of the A53's main TLB and the i7's L2 TLB.", [hl("q[0]"), hl("q[1]", 0.4)])
s.step("The i7's peak memory bandwidth. And the A53's AMAT with L1 3 cycles, L2 15, memory 200, an L1 miss rate of 4 percent and an L2 local miss rate of 25. Pause and work it out.", [hl("q[2]"), hl("q[3]", 0.4)])
s.step("a: the A53 has 32 over 4, 8 kilobytes per way, too big: no. The i7 has 32 over 8, 4 kilobytes: yes.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 512 times 4 kilobytes is 2 megabytes. 1536 times 4 kilobytes is 6 megabytes.", rv("qa", 1))
s.step("c: 2 times 2133 million times 8 bytes: about 34.1 gigabytes per second.", rv("qa", 2))
s.step("d: 15 plus 0.25 times 200 is 65. 3 plus 0.04 times 65: 5.6 cycles.", rv("qa", 3))
s.step("The usual slips: forgetting that DDR's number already counts both clock edges, and using an L2's global miss rate where the formula needs the local one.", [s.take("know which rate is local and which is global")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("The A53: small configurable caches, two levels, a physically indexed L1 data cache, and a tiny micro TLB to keep translation fast.", [hl("stages[1..=2]")])
s.step("The i7: three levels with a shared inclusive L3, an 8-way VIPT L1, large TLBs, and out-of-order execution to overlap misses.", [hl("stages[3..=4]")])
s.step("Compare them in nanoseconds, and read every choice as a trade-off. That completes Module 2, the memory hierarchy.", [hl("stages[5..=6]"), mk("stages[0..=7]", 0.5), s.take("Module 2 complete: the memory hierarchy")])

s.save("/home/claude/playlist/m2v14.json")

"""Module 2, video 5: AMAT and every common kind of AMAT problem."""
import sys
sys.path.insert(0, ".")
from common import Script

r = lambda x, n=2: round(x, n)
assert (4 + 0.1 * 20, r(0.9 * 4 + 0.1 * 20)) == (6, 5.6)
assert 1 + 0.05 * 100 == 6 and r(2e9 * 50e-9) == 100 and 6 * 0.5 == 3
assert (1 + 4 * 15 + 4 * 1, 1 + 15 + 4 * 1) == (65, 20) and r(1 + 0.05 * 65, 2) == 4.25 and 1 + 0.05 * 20 == 2
assert r(1 + 0.04 * (10 + 0.5 * 200)) == 5.4 and r(0.04 * 0.5, 3) == 0.02 and 20 / 40 == 0.5 and 20 / 1000 == 0.02
assert (r(1 / 1.3), r(0.3 / 1.3)) == (0.77, 0.23) and r(1 / 1.3 * 2 + 0.3 / 1.3 * 5) == 2.69
assert r(1 * 0.01 * 100 + 0.3 * 0.04 * 100) == 2.2 and r(1 + 2.2) == 3.2 and r(20 / 1000 * 200) == 4
assert r(0.8 * 2 + 0.2 * 0.9 * 12 + 0.2 * 0.1 * 112) == 6 and r(2 + 0.2 * (10 + 0.1 * 100)) == 6 and r(0.8 * 2 + 0.2 * 0.9 * 10 + 0.02 * 100) == 5.4
assert r(0.2 * 0.1, 3) == 0.02 and r(1.3 * 0.02 * 112 / 1.3, 2) == 2.24

assert r(1 - (4 - 2) / 50, 2) == 0.96 and r(1.2 + 0.04 * 100, 2) == 5.2 and (1 + 0.05 * 25, r(1.2 + 0.04 * 25, 2)) == (2.25, 2.2)

s = Script("AMAT: average memory access time, and every kind of problem")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The formula, and the two ways GATE counts a miss"],
    [2, "Cycles or nanoseconds"],
    [3, "Where the miss penalty comes from"],
    [4, "Two levels: L1 and L2, local and global miss rates"],
    [5, "Split instruction and data caches"],
    [6, "From AMAT to CPI and stall cycles"],
    [7, "Exam question"]]})
s.obj({"id": "f", "type": "math", "region": "center", "lines": [
    "\"AMAT\" = \"hit time\" + \"miss rate\" times \"miss penalty\"",
    "\"hit time 4 ns, miss rate\" 10%, \"memory 20 ns\": quad 4 + 0.1 times 20 = 6 \"ns\"",
    "\"parallel:\" quad 0.9 times 4 + 0.1 times 20 = 5.6 \"ns\""]})
s.obj({"id": "tl", "type": "timeline", "region": "center", "lanes": ["hit", "miss: L1 first, then memory", "miss: L1 and memory together"], "end": 25, "unit": "ns", "now": 0, "blocks": []})
s.obj({"id": "conv", "type": "table", "region": "center", "columns": ["the question says", "a miss costs", "formula"], "rows": [
    ["hierarchical / look-through / not stated", "hit time + memory time", "h·t₁ + (1 − h)(t₁ + t₂) = t₁ + (1 − h)·t₂"],
    ["simultaneous / parallel", "memory time only", "h·t₁ + (1 − h)·t₂"]]})
s.obj({"id": "cy", "type": "math", "region": "center", "lines": [
    "\"2 GHz\" => 1 \"cycle\" = 0.5 \"ns\" quad \"memory 50 ns\" = 100 \"cycles\"",
    "\"AMAT\" = 1 + 0.05 times 100 = 6 \"cycles\"",
    "6 \"cycles\" times 0.5 \"ns\" = 3 \"ns\""]})
s.obj({"id": "mp", "type": "table", "region": "center", "columns": ["memory organization", "send address", "access", "transfer", "miss penalty"], "rows": [
    ["one word wide, one bank", "1", "4 × 15", "4 × 1", ""],
    ["4 interleaved banks", "1", "15 (all banks at once)", "4 × 1", ""]]})
s.obj({"id": "mpx", "type": "math", "region": "bottom", "lines": ["\"miss rate\" 5%: quad 1 + 0.05 times 65 = 4.25 quad \"vs\" quad 1 + 0.05 times 20 = 2 \"cycles\""]})
s.obj({"id": "hier", "type": "table", "region": "center", "columns": ["level", "access time", "miss rate"], "rows": [
    ["L1", "1 cycle", "4%"], ["L2", "10 cycles", "50% of what reaches it"], ["memory", "200 cycles", "–"]]})
s.obj({"id": "more", "type": "math", "region": "center", "lines": [
    "\"target 4 ns:\" quad 2 + (1 - h) times 50 = 4 quad => quad 1 - h = 0.04 quad => quad h = 0.96",
    "\"A, direct-mapped:\" quad 1 + 0.05 times 100 = 6 \"cycles\"",
    "\"B, 2-way, slower hit:\" quad 1.2 + 0.04 times 100 = 5.2 \"cycles\"",
    "\"penalty 25 cycles:\" quad A = 1 + 0.05 times 25 = 2.25, quad B = 1.2 + 0.04 times 25 = 2.2"]})
s.obj({"id": "two", "type": "math", "region": "center", "lines": [
    "\"AMAT\" = \"HT\"_1 + \"MR\"_1 times (\"HT\"_2 + \"MR\"_2 times \"MP\"_2)",
    "= 1 + 0.04 times (10 + 0.5 times 200)",
    "= 1 + 0.04 times 110 = 5.4 \"cycles\""]})
s.obj({"id": "lg", "type": "table", "region": "center", "columns": ["", "definition", "here"], "rows": [
    ["local L2 miss rate", "L2 misses ÷ accesses that reach L2", "20 ÷ 40 = 50%"],
    ["global L2 miss rate", "L2 misses ÷ all CPU accesses", "20 ÷ 1000 = 2%"],
    ["link", "global = MR₁ × local MR₂", "0.04 × 0.5 = 0.02"]]})
s.obj({"id": "split", "type": "math", "region": "center", "lines": [
    "\"per instruction\": 1 \"fetch\" + 0.3 \"data\" = 1.3 \"accesses\"",
    "\"weights\": 1 / 1.3 approx 0.77, quad 0.3 / 1.3 approx 0.23",
    "\"I-cache\": 1 + 0.01 times 100 = 2, quad \"D-cache\": 1 + 0.04 times 100 = 5",
    "\"AMAT\" = 0.77 times 2 + 0.23 times 5 approx 2.69 \"cycles\""]})
s.obj({"id": "cpi", "type": "math", "region": "center", "lines": [
    "\"CPI\" = \"CPI\"_\"base\" + \"memory stall cycles per instruction\"",
    "\"stalls\" = sum \"accesses per instr\" times \"miss rate\" times \"penalty\"",
    "= 1 times 0.01 times 100 + 0.3 times 0.04 times 100 = 1 + 1.2 = 2.2",
    "\"CPI\" = 1 + 2.2 = 3.2 quad => quad \"a perfect cache is\" 3.2 \"times faster\"",
    "\"misses per 1000 instructions\" = 20: quad 20 / 1000 times 200 = 4 \"stall cycles\""]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["L1: 2 ns, hit ratio 0.8 · L2: 10 ns, hit ratio 0.9 · memory: 100 ns. Find:"], "rows": [
    ["a) AMAT with hierarchical (look-through) access"],
    ["b) AMAT with simultaneous access to all levels"],
    ["c) the global miss rate of L2"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 0.8 times 2 + 0.2 times 0.9 times (2 + 10) + 0.2 times 0.1 times (2 + 10 + 100)",
    "= 1.6 + 2.16 + 2.24 = 6 \"ns\" quad = 2 + 0.2 times (10 + 0.1 times 100)",
    "\"b)\" quad 0.8 times 2 + 0.2 times 0.9 times 10 + 0.2 times 0.1 times 100 = 1.6 + 1.8 + 2 = 5.4 \"ns\"",
    "\"c)\" quad 0.2 times 0.1 = 0.02 = 2%"]})


def blk(id, lane, a, b, label, d=0):
    return {"action": "add_block", "target": "tl", "id": id, "lane": lane, "start": a, "end": b, "label": label, **({"delay": d} if d else {})}


def rv(t, i):
    return [{"action": "reveal", "target": f"{t}[{i}]"}, {"action": "highlight", "target": f"{t}[{i}]"}]


hl = lambda t: {"action": "highlight", "target": t}
setc = lambda t, r_, c, v, d=0: {"action": "set", "target": f"{t}[{r_}][{c}]", "value": v, **({"delay": d} if d else {})}

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Hit rates and miss rates alone do not say how fast memory feels. AMAT, the average memory access time, does, and it is the most asked memory question in GATE.", [s.head("AMAT")])
s.step("Here are the seven stages.", [{"action": "show", "target": "stages"}])
s.step("The formula and its two conventions, units, and where the miss penalty comes from.", [hl("stages[0..=2]")])
s.step("Then two cache levels, split caches, turning AMAT into CPI, and an exam question.", [hl("stages[3..=6]")])

# ---------------------------------------------------------------- formula
s.scene("formula")
s.step("Stage 1: every access pays the hit time. Misses also pay the miss penalty.", [s.head("Stage 1 of 7: the formula"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "f"}])
s.step("So AMAT equals hit time, plus miss rate times miss penalty.", [hl("f[0]")])
s.step("Example: a 4 nanosecond cache, 10 percent misses, and 20 nanosecond memory. 4 plus 0.1 times 20 is 6 nanoseconds.", rv("f", 1))
s.step("Picture it. A hit takes 4 nanoseconds.", [{"action": "hide", "target": "f"}, {"action": "show", "target": "tl"}, blk("h", "hit", 0, 4, "L1 4")])
s.step("Usually a miss first looks in the cache, fails, then goes to memory: 4 plus 20, 24 nanoseconds. This is hierarchical, or look-through, access.", [blk("s1", "miss: L1 first, then memory", 0, 4, "L1 4"), blk("s2", "miss: L1 first, then memory", 4, 24, "memory 20", 0.4)])
s.step("Some designs start memory at the same time as the cache. Then a miss costs just the memory time, 20.", [blk("p1", "miss: L1 and memory together", 0, 20, "memory 20, L1 checked alongside")])
s.step("That is the second convention, and the formula changes: hit fraction times 4, plus miss fraction times 20, which is 5.6.", [{"action": "hide", "target": "tl"}, {"action": "show", "target": "f"}] + rv("f", 2))
s.step("GATE says which one it means. Hierarchical, look-through, or no word at all: the miss pays both. Simultaneous or parallel: the miss pays memory only.", [{"action": "hide", "target": "f"}, {"action": "show", "target": "conv"}, hl("conv[0]")])
s.step("Note the first formula simplifies: h times t1, plus 1 minus h times t1 plus t2, is just t1 plus the miss rate times t2. The same as hit time plus miss rate times penalty.", [hl("conv[0][2]")])
s.step("And the parallel one does not.", [hl("conv[1]"), s.take("look-through: t₁ + (1 − h)·t₂ · simultaneous: h·t₁ + (1 − h)·t₂")])

# ---------------------------------------------------------------- units
s.scene("units")
s.step("Stage 2: keep the units the same. Here the hit time is in cycles, but memory is given in nanoseconds.", [s.head("Stage 2 of 7: cycles or nanoseconds"), {"action": "hide", "target": "conv"}, s.untake(), {"action": "show", "target": "cy"}])
s.step("At 2 gigahertz a cycle is 0.5 nanoseconds, so 50 nanoseconds of memory is 100 cycles.", [hl("cy[0]")])
s.step("With a 1 cycle hit and 5 percent misses, AMAT is 1 plus 0.05 times 100: 6 cycles.", rv("cy", 1))
s.step("And 6 cycles is 3 nanoseconds. Convert once, at the start or the end, never in the middle.", rv("cy", 2) + [s.take("pick one unit: convert ns ↔ cycles with the clock period")])

# ---------------------------------------------------------------- miss penalty
s.scene("penalty")
s.step("Stage 3: sometimes you must build the miss penalty yourself. A block is 4 words. Sending the address takes 1 cycle, each memory access 15 cycles, and each word transfer 1 cycle.", [s.head("Stage 3 of 7: building the miss penalty"), {"action": "hide", "target": "cy"}, s.untake(), {"action": "show", "target": "mp"}])
s.step("With memory one word wide and one bank, the 4 words are read one after another: 1 plus 4 times 15 plus 4 times 1, which is 65 cycles.", [hl("mp[0]"), setc("mp", 0, 4, "1 + 60 + 4 = 65", 0.5)])
s.step("With 4 interleaved banks, all 4 words are read at once, in one 15 cycle access, then sent one per cycle: 1 plus 15 plus 4, just 20 cycles.", [hl("mp[1]"), setc("mp", 1, 4, "1 + 15 + 4 = 20", 0.5)])
s.step("With a 5 percent miss rate, AMAT falls from 4.25 to 2 cycles, with the same DRAM chips.", [{"action": "show", "target": "mpx"}, hl("mpx[0]")])
s.step("Edge case: the address is sent once, but the transfer cost is paid for every word. Count each part.", [{"action": "hide", "target": "mpx"}, s.take("penalty = address + access(es) + transfers · interleaving overlaps the accesses")])

# ---------------------------------------------------------------- two levels
s.scene("two")
s.step("Stage 4: two levels. L1 takes 1 cycle and misses 4 percent of the time. L2 takes 10 cycles and misses half of what reaches it. Memory takes 200.", [s.head("Stage 4 of 7: L1 and L2"), {"action": "hide", "target": "mp"}, s.untake(), {"action": "show", "target": "hier"}, hl("hier[0]"), {"action": "highlight", "target": "hier[1]", "delay": 0.4}])
s.step("The trick: L1's miss penalty is itself an AMAT, the AMAT of L2.", [{"action": "hide", "target": "hier"}, {"action": "show", "target": "two"}, hl("two[0]")])
s.step("So: 1 plus 0.04 times, 10 plus 0.5 times 200.", rv("two", 1))
s.step("10 plus 100 is 110. 0.04 times 110 is 4.4. AMAT is 5.4 cycles.", rv("two", 2))
s.step("Now the trap. That 50 percent is the local miss rate of L2: misses divided by the accesses that reach L2.", [{"action": "hide", "target": "two"}, {"action": "show", "target": "lg"}, hl("lg[0]")])
s.step("Out of 1000 CPU accesses, 40 miss in L1 and reach L2, and 20 of those miss again. Local: 20 over 40, 50 percent.", [hl("lg[0][2]")])
s.step("The global miss rate divides by all 1000 CPU accesses: 2 percent. It says what fraction of all accesses go to memory.", [hl("lg[1]")])
s.step("They are linked: global equals the L1 miss rate times the local L2 miss rate. Use the local rate inside the AMAT formula.", [hl("lg[2]"), s.take("AMAT uses the LOCAL L2 miss rate · global = MR₁ × local MR₂")])

# ---------------------------------------------------------------- split caches
s.scene("split")
s.step("Stage 5: most processors have separate instruction and data caches. Each instruction makes 1 fetch, and here 0.3 data accesses.", [s.head("Stage 5 of 7: split I- and D-caches"), {"action": "hide", "target": "lg"}, s.untake(), {"action": "show", "target": "split"}, hl("split[0]")])
s.step("So of every 1.3 accesses, 1 goes to the instruction cache and 0.3 to the data cache: weights of 0.77 and 0.23.", rv("split", 1))
s.step("The I-cache misses 1 percent, the D-cache 4 percent, with a 100 cycle penalty: AMATs of 2 and 5 cycles.", rv("split", 2))
s.step("The combined AMAT weights them: 0.77 times 2 plus 0.23 times 5, about 2.69 cycles.", rv("split", 3))
s.step("Edge case: do not just average 2 and 5. There are more than three instruction fetches for every data access.", [s.take("weight each cache by its share of accesses")])

# ---------------------------------------------------------------- CPI
s.scene("cpi")
s.step("Stage 6: from AMAT to CPI. Every miss stalls the processor, and those stall cycles add to the CPI.", [s.head("Stage 6 of 7: from AMAT to CPI"), {"action": "hide", "target": "split"}, s.untake(), {"action": "show", "target": "cpi"}, hl("cpi[0]")])
s.step("Stall cycles per instruction are, for each kind of access: accesses per instruction, times miss rate, times penalty.", rv("cpi", 1))
s.step("Same machine: 1 times 0.01 times 100 for fetches, plus 0.3 times 0.04 times 100 for data, gives 2.2 stall cycles per instruction.", rv("cpi", 2))
s.step("With a base CPI of 1, the real CPI is 3.2. So a perfect cache would make this machine 3.2 times faster.", rv("cpi", 3))
s.step("Some questions give misses per thousand instructions instead. 20 misses per 1000, at 200 cycles each, is 4 stall cycles per instruction.", rv("cpi", 4) + [s.take("CPI = base + Σ accesses/instr × miss rate × penalty")])

# ---------------------------------------------------------------- more problems
s.scene("more")
s.step("Two more problem types before the exam question. First, working backwards: what hit rate do we need?", [s.head("Two more problem types"), {"action": "hide", "target": "cpi"}, s.untake(), {"action": "show", "target": "more"}])
s.step("A 2 nanosecond cache, 50 nanosecond memory, look-through, and we want AMAT of 4. So 2 plus 1 minus h, times 50, equals 4. 1 minus h is 0.04, and the hit rate must be 96 percent.", [hl("more[0]")])
s.step("Second, comparing designs. Cache A is direct-mapped: 1 cycle hits, 5 percent misses, 100 cycle penalty: AMAT 6.", rv("more", 1))
s.step("Cache B is 2-way. It misses less, 4 percent, but its hit takes 1.2 cycles. AMAT: 1.2 plus 4, which is 5.2. B wins, even with the slower hit.", rv("more", 2))
s.step("Edge case: the winner depends on the penalty. With only a 25 cycle penalty, A is 2.25 and B is 2.2: almost a tie. A slower hit can lose when misses are cheap.", rv("more", 3) + [s.take("compare AMATs, never hit time or miss rate alone")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question in GATE style.", [s.head("Exam question"), {"action": "hide", "target": "more"}, s.untake(), {"action": "show", "target": "q"}])
s.step("L1 takes 2 nanoseconds with hit ratio 0.8. L2 takes 10 with hit ratio 0.9. Memory takes 100.", [hl("q[0]")])
s.step("Find the AMAT for hierarchical access, for simultaneous access, and the global L2 miss rate. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: hierarchical. 80 percent hit in L1 for 2 nanoseconds. 20 percent times 0.9 reach L2 and pay 2 plus 10. The last 2 percent pay 2 plus 10 plus 100.", [{"action": "hide", "target": "q"}, {"action": "show", "target": "qa"}, hl("qa[0]")])
s.step("That is 1.6 plus 2.16 plus 2.24, which is 6 nanoseconds. The short form gives the same: 2 plus 0.2 times, 10 plus 0.1 times 100.", rv("qa", 1))
s.step("b: simultaneous. Each access pays only the level that answers: 1.6 plus 1.8 plus 2, which is 5.4 nanoseconds.", rv("qa", 2))
s.step("c: the global miss rate of L2 is 0.2 times 0.1, 2 percent. Its local miss rate is 10 percent.", rv("qa", 3))
s.step("The usual slips: using the global rate inside AMAT, mixing cycles and nanoseconds, and picking the wrong convention for a miss.", [s.take("local rate inside AMAT · one unit · read: hierarchical or simultaneous")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qa"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("AMAT is hit time plus miss rate times miss penalty, with the miss paying both levels unless access is simultaneous. Keep one unit, and build the penalty from its parts.", [hl("stages[0..=2]")])
s.step("For two levels, nest the formula with the local miss rate. Weight split caches by their accesses, and add stall cycles to the base CPI.", [hl("stages[3..=6]")])
s.step("Next video: problems on LRU, FIFO and optimal replacement, and page faults.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Next: replacement problems and page faults")])

s.save("./m2v5.json")

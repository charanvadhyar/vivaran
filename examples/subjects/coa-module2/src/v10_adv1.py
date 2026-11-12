"""Module 2, video 10: ten advanced cache optimizations, part 1 (hit time, bandwidth, miss penalty)."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

r = lambda x, n=2: round(x, n)
# way prediction
assert r(0.85 * 1 + 0.15 * 2) == 1.15
assert (r(1 + 0.05 * 25), r(1.3 + 0.04 * 25), r(1.15 + 0.04 * 25)) == (2.25, 2.3, 2.15)
# banks
assert [b % 4 for b in (0, 1, 2, 3)] == [0, 1, 2, 3] and [b % 4 for b in (0, 4, 8)] == [0, 0, 0]
# nonblocking: A miss 20, B hit 1, C miss 20
assert (20 + 1 + 20, 20 + 20, 2 + 20) == (41, 40, 22)
# critical word: latency 40, 8 words, 1 cycle per word, want word 5
assert (40 + 8, 40 + 6, 40 + 1) == (48, 46, 41)
# exam
assert r(0.8 * 1 + 0.2 * 2) == 1.2 and (50 + 8, 50 + 1) == (58, 51)
assert (r(1.2 + 0.02 * 58), r(1.2 + 0.02 * 51)) == (2.36, 2.22) and 1027 % 8 == 3

s = Script("Advanced cache optimizations, part 1")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The map: ten advanced optimizations in five groups"],
    [2, "Small and simple first-level caches"],
    [3, "Way prediction"],
    [4, "Pipelined access and multibanked caches"],
    [5, "Nonblocking caches"],
    [6, "Critical word first and early restart"],
    [7, "Merging write buffer"],
    [8, "Exam question"]]})
s.obj({"id": "map", "type": "table", "region": "center", "columns": ["#", "optimization", "improves", "video"], "rows": [
    [1, "small and simple first-level caches", "hit time, power", "this one"],
    [2, "way prediction", "hit time, power", "this one"],
    [3, "pipelined cache access", "bandwidth", "this one"],
    [4, "multibanked caches", "bandwidth", "this one"],
    [5, "nonblocking caches", "bandwidth, miss penalty", "this one"],
    [6, "critical word first, early restart", "miss penalty", "this one"],
    [7, "merging write buffer", "miss penalty", "this one"],
    [8, "compiler optimizations", "miss rate", "part 2"],
    [9, "hardware and compiler prefetching", "miss penalty or rate", "part 2"],
    [10, "HBM as an extra cache level", "miss penalty", "part 2"]]})
s.obj({"id": "sm", "type": "table", "region": "center", "columns": ["what costs hit time", "why"], "rows": [
    ["a larger cache", "longer word lines and bit lines to drive, more rows to decode"],
    ["more ways", "more tag comparators and a wider multiplexer after them"],
    ["more ways, again", "every way's tag and data are read on each access: more energy"],
    ["direct-mapped", "the data can be used while the tag is still being checked"],
    ["index beyond the page offset", "must wait for the TLB before indexing"]]})
s.obj({"id": "smm", "type": "math", "region": "center", "lines": [
    "\"L1 must hit in 1 to 4 cycles, at full clock speed\"",
    "\"so L1 stays small (32 to 64 KB)\" quad \"and\" quad \"size\" / \"ways\" <= \"page size\"",
    "\"L2 and L3 grow instead: they can afford a slower hit\""]})
s.obj({"id": "wp", "type": "table", "region": "center", "columns": ["set 5", "tag", "access to 0x3C", "access to 0x07"], "rows": [
    ["way 0", "0x1A", "", ""], ["way 1", "0x07", "", ""], ["way 2", "0x3C", "", ""], ["way 3", "0x22", "", ""], ["hit time", "", "", ""]]})
s.obj({"id": "wpm", "type": "math", "region": "center", "lines": [
    "\"hit time\" = 0.85 times 1 + 0.15 times 2 = 1.15 \"cycles\"",
    "\"direct-mapped, hit 1, miss 5%:\" quad 1 + 0.05 times 25 = 2.25",
    "\"4-way, hit 1.3, miss 4%:\" quad 1.3 + 0.04 times 25 = 2.3",
    "\"4-way + prediction:\" quad 1.15 + 0.04 times 25 = 2.15 quad \"best\""]})
s.obj({"id": "pa", "type": "table", "region": "center", "columns": ["processor", "L1 instruction cache hit"], "rows": [
    ["Pentium (mid 1990s)", "1 cycle"],
    ["Pentium Pro to Pentium III", "2 cycles"],
    ["Pentium 4, Core i7", "4 cycles"]]})
s.obj({"id": "bk", "type": "table", "region": "center", "columns": ["", "bank 0", "bank 1", "bank 2", "bank 3"], "rows": [
    ["blocks", "0", "1", "2", "3"], ["", "4", "5", "6", "7"], ["", "8", "9", "10", "11"]]})
s.obj({"id": "bkm", "type": "math", "region": "bottom", "lines": [
    "\"bank\" = \"block address\" mod \"number of banks\""]})
s.obj({"id": "nb", "type": "timeline", "region": "center", "lanes": ["blocking", "hit under miss: A, C", "hit under miss: B", "miss under miss: A", "miss under miss: B, C"], "end": 42, "unit": "cycles", "now": 0, "blocks": []})
s.obj({"id": "nbx", "type": "table", "region": "center", "columns": ["idea", "meaning"], "rows": [
    ["MSHR", "miss status holding register: one per outstanding miss, remembers who waits for which block"],
    ["number of MSHRs", "how many misses can be in flight at once"],
    ["who needs it", "out-of-order cores: they keep running past a missing load"],
    ["what it hides", "only the part of the miss that overlaps other work"]]})
s.obj({"id": "cw", "type": "timeline", "region": "center", "lanes": ["wait for the whole block", "early restart", "critical word first"], "end": 50, "unit": "cycles", "now": 0, "blocks": []})
s.obj({"id": "cwm", "type": "math", "region": "bottom", "lines": [
    "\"latency 40, then 1 word per cycle; the CPU wants word 5 of 8:\" quad 48 quad 46 quad 41"]})
s.obj({"id": "wb", "type": "table", "region": "center", "columns": ["entry", "block address", "word 0", "word 1", "word 2", "word 3"], "rows": [
    ["1", "", "", "", "", ""], ["2", "", "", "", "", ""], ["3", "", "", "", "", ""], ["4", "", "", "", "", ""]]})
s.obj({"id": "sumt", "type": "table", "region": "center", "columns": ["optimization", "hit time", "bandwidth", "miss penalty", "cost"], "rows": [
    ["small, simple L1", "better", "", "", "higher miss rate"],
    ["way prediction", "better", "", "", "mispredictions"],
    ["pipelined access", "worse in cycles", "better", "", "longer load-use delay"],
    ["multibanked", "", "better", "", "bank conflicts"],
    ["nonblocking", "", "better", "better", "complex control"],
    ["critical word first", "", "", "better", "needs smart memory"],
    ["merging write buffer", "", "", "better", "small"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["4-way L1, given", "find"], "rows": [
    ["way prediction right 80%: 1 cycle, else 2 cycles", "a) the average hit time"],
    ["miss rate 2%, 64 B blocks", "b) the miss penalty: whole block, and critical word first"],
    ["memory: 50 cycles, then 8 B per cycle", "c) AMAT both ways"],
    ["8 banks, sequentially interleaved", "d) the bank of block address 1027"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 0.8 times 1 + 0.2 times 2 = 1.2 \"cycles\"",
    "\"b)\" quad 50 + 64 / 8 = 58 \"cycles\" quad \"critical word first:\" quad 50 + 1 = 51 \"cycles\"",
    "\"c)\" quad 1.2 + 0.02 times 58 = 2.36 quad \"vs\" quad 1.2 + 0.02 times 51 = 2.22 \"cycles\"",
    "\"d)\" quad 1027 mod 8 = 3 quad => quad \"bank 3\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]


def blk(tl, id, lane, a, b, label, d=0):
    return {"action": "add_block", "target": tl, "id": id, "lane": lane, "start": a, "end": b, "label": label, **({"delay": d} if d else {})}


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("The basic optimizations changed size, blocks and ways. The ten advanced ones change how a cache is accessed. This is part 1.", [s.head("Ten advanced cache optimizations: part 1")])
s.step("Here are the eight stages.", show("stages"))
s.step("A map of all ten, then the seven that cut the hit time, raise the bandwidth, or cut the miss penalty, each with a number. Then an exam question.", [hl("stages[0..=6]"), hl("stages[7]", 0.6)])

# ---------------------------------------------------------------- map
s.scene("map")
s.step("Stage 1: the map. The textbook lists ten advanced optimizations.", [s.head("Stage 1 of 8: the map")] + hide("stages") + show("map"))
s.step("Two reduce the hit time: small and simple first-level caches, and way prediction.", [hl("map[0..=1]")])
s.step("Three raise the cache bandwidth, the number of accesses served per cycle: pipelined access, multiple banks, and nonblocking caches.", [hl("map[2..=4]")])
s.step("Two reduce the miss penalty: critical word first, and the merging write buffer. The last three, compiler optimizations, prefetching, and HBM, are part 2.", [hl("map[5..=6]"), hl("map[7..=9]", 0.6)])
s.step("Bandwidth is the new lever: a modern core issues several loads per cycle, and the cache must keep up.", [mk("map[2..=4]"), s.take("hit time · bandwidth · miss penalty · miss rate")])

# ---------------------------------------------------------------- small and simple
s.scene("small")
s.step("Stage 2: small and simple first-level caches. Why is L1 so small, when L2 and L3 are huge?", [s.head("Stage 2 of 8: small and simple L1"), s.untake()] + hide("map") + show("sm"))
s.step("A larger cache has longer wires and more rows to decode. Signals take longer to cross it, so the hit is slower.", [hl("sm[0]")])
s.step("More ways means more tag comparators, and a wider multiplexer to pick the right way. Again slower.", [hl("sm[1]")])
s.step("And a set-associative cache reads every way on each access, then throws most away. That costs energy on every load.", [hl("sm[2]")])
s.step("A direct-mapped cache can send the data on while the tag is still checked. And an index beyond the page offset must wait for address translation.", [hl("sm[3]"), hl("sm[4]", 0.6)])
s.step("So the L1 must hit in one to four cycles at full clock speed.", hide("sm") + show("smm") + [hl("smm[0]")])
s.step("It stays small, typically 32 to 64 kilobytes, with size divided by ways no larger than a page. The growth goes into L2 and L3, which can afford a slower hit.", rv("smm", 1) + rv("smm", 2) + [s.take("L1: fast and lean · capacity goes to L2 and L3")])

# ---------------------------------------------------------------- way prediction
s.scene("waypred")
s.step("Stage 3: way prediction. Can we get the miss rate of a 4-way cache with the hit time of a direct-mapped one?", [s.head("Stage 3 of 8: way prediction"), s.untake()] + hide("smm") + show("wp"))
s.step("Each set keeps a few extra bits that predict which way the next access will hit. Only that way's tag is compared first.", [hl("wp[0..=3]")])
s.step("An access to tag hex 3 C. The predictor says way 2.", [st("wp[2][2]", "predicted", 0.3), hl("wp[2]", 0.5)])
s.step("Way 2 holds 3 C. Prediction right: the data comes out in one cycle, just like a direct-mapped cache.", [st("wp[2][2]", "predicted: hit"), mk("wp[2][1]"), st("wp[4][2]", "1 cycle", 0.4)])
s.step("Next, tag hex 0 7. The predictor again says way 2.", [st("wp[2][3]", "predicted", 0.3), hl("wp[2]", 0.5)])
s.step("Wrong. The other ways are checked in the next cycle, the hit is found in way 1, and the predictor is updated. The hit took 2 cycles.", [st("wp[2][3]", "predicted: no"), st("wp[1][3]", "next cycle: hit", 0.3), hl("wp[1]", 0.3), st("wp[4][3]", "2 cycles", 0.6)])
s.step("Predictions are right more than 90 percent of the time for 2-way caches, and about 80 percent for 4-way. With 85 percent right, the average hit time is 0.85 times 1, plus 0.15 times 2: 1.15 cycles.", hide("wp") + show("wpm") + [hl("wpm[0]")])
s.step("Compare three caches with a 25 cycle miss penalty. Direct-mapped: hit 1, miss rate 5 percent. AMAT 2.25.", rv("wpm", 1))
s.step("A plain 4-way cache misses less, 4 percent, but its hit takes 1.3 cycles. AMAT 2.3: no better.", rv("wpm", 2))
s.step("The 4-way with prediction keeps the 4 percent miss rate with a 1.15 cycle hit. AMAT 2.15, the best of the three.", rv("wpm", 3))
s.step("A variant called way selection reads only the predicted way's data too. That saves most of the energy of a set-associative read.", [s.take("way prediction: the miss rate of N ways, nearly the hit time of 1 way")])

# ---------------------------------------------------------------- pipelined and banked
s.scene("banks")
s.step("Stage 4: two ways to raise bandwidth. First, pipelined cache access.", [s.head("Stage 4 of 8: pipelined and multibanked caches"), s.untake()] + hide("wpm") + show("pa"))
s.step("Split the hit into stages, so a new access can start every cycle and the clock can be faster. On Intel, the L1 instruction cache hit took 1 cycle on the Pentium, 2 on the Pentium Pro to Pentium III, and 4 on the Pentium 4 and Core i7.", [hl("pa[0]"), hl("pa[1]", 0.3), hl("pa[2]", 0.6)])
s.step("The price: a load needs more cycles before its value can be used, and a mispredicted branch waits longer for new instructions.", [s.take("pipelining: one access per cycle, but more cycles per hit")])
s.step("Second, multiple banks. Instead of one big array, the cache is split into banks that work independently.", [s.untake()] + hide("pa") + show("bk"))
s.step("Sequential interleaving spreads blocks across banks in turn, wrapping around. So the bank is the block address mod the number of banks.", [hl("bk[0]"), hl("bk[1]", 0.3), hl("bk[2]", 0.6)] + show("bkm"))
s.step("Accesses to blocks 0, 1, 2 and 3 fall in four different banks. All four are served in the same cycle.", [mk("bk[0][1]"), mk("bk[0][2]", 0.2), mk("bk[0][3]", 0.4), mk("bk[0][4]", 0.6)])
s.step("But blocks 0, 4 and 8 all live in bank 0. That is a bank conflict: they are served one after another.", [hl("bk[0][1]"), hl("bk[1][1]", 0.3), hl("bk[2][1]", 0.6)])
s.step("The textbook's Core i7 has 4 banks in L1, so it can serve two memory accesses per clock, and 8 banks in L2.", [s.take("multibanked: bank = block mod banks · conflicts serialize")])

# ---------------------------------------------------------------- nonblocking
s.scene("nonblock")
s.step("Stage 5: nonblocking caches. A simple cache blocks: while one miss is fetched, it serves nothing else.", [s.head("Stage 5 of 8: nonblocking caches"), s.untake()] + hide("bk", "bkm") + show("nb"))
s.step("Three loads in a row. A misses, taking 20 cycles. B hits, taking 1. C misses, another 20.", [hl("nb")])
s.step("Blocking: A's miss runs from 0 to 20. B must wait for it, then hits at 21. C's miss runs to 41.", [blk("nb", "a1", "blocking", 0, 20, "A miss"), blk("nb", "b1", "blocking", 20, 21, "B", 0.3), blk("nb", "c1", "blocking", 21, 41, "C miss", 0.6)])
s.step("Hit under miss: while A is being fetched, the cache still serves hits. B is done at cycle 2.", [blk("nb", "a2", "hit under miss: A, C", 0, 20, "A miss"), blk("nb", "b2", "hit under miss: B", 1, 2, "B", 0.4)])
s.step("But C is a second miss. This cache can track only one miss, so C waits until A returns. Done at 40.", [blk("nb", "c2", "hit under miss: A, C", 20, 40, "C miss")])
s.step("Miss under miss: the cache tracks two misses at once. C starts at cycle 2, and both misses overlap. Everything is done by cycle 22.", [blk("nb", "a3", "miss under miss: A", 0, 20, "A miss"), blk("nb", "b3", "miss under miss: B, C", 1, 2, "B", 0.3), blk("nb", "c3", "miss under miss: B, C", 2, 22, "C miss", 0.6)])
s.step("41 cycles, then 40, then 22. The misses still take 20 cycles each, but they now hide behind each other.", [s.take("blocking 41 · hit under miss 40 · miss under miss 22")])
s.step("How does the cache keep track? With miss status holding registers, MSHRs.", hide("nb") + [s.untake()] + show("nbx") + [hl("nbx[0]")])
s.step("Each outstanding miss gets one: which block is coming, and which loads wait for it. Out-of-order cores need them, since they keep executing past a load that missed.", [hl("nbx[1]"), hl("nbx[2]", 0.5)])
s.step("And only the part of a miss that overlaps other work is hidden. So for these cores, the effective miss penalty is the non-overlapped part.", [hl("nbx[3]"), s.take("nonblocking: misses overlap · tracked by MSHRs")])

# ---------------------------------------------------------------- critical word
s.scene("critical")
s.step("Stage 6: critical word first and early restart. The CPU needs one word, but the cache waits for a whole block.", [s.head("Stage 6 of 8: critical word first, early restart"), s.untake()] + hide("nbx") + show("cw"))
s.step("Example: memory takes 40 cycles to start, then sends one word per cycle. A block has 8 words, and the CPU wants word 5.", [hl("cw")])
s.step("Normally the cache waits for all 8 words. 40 plus 8: the CPU restarts at cycle 48.", [blk("cw", "w1", "wait for the whole block", 0, 40, "latency 40"), blk("cw", "w2", "wait for the whole block", 40, 48, "words 0 to 7", 0.4)])
s.step("Early restart: words arrive in order, and word 5 goes to the CPU the moment it arrives. It is the sixth word, so cycle 46.", [blk("cw", "e1", "early restart", 0, 40, "latency 40"), blk("cw", "e2", "early restart", 40, 46, "words 0 to 5", 0.4)])
s.step("Critical word first: memory sends the requested word first, then wraps around to the rest. Word 5 arrives at cycle 41.", [blk("cw", "c1", "critical word first", 0, 40, "latency 40"), blk("cw", "c2", "critical word first", 40, 41, "5", 0.4), blk("cw", "c3", "critical word first", 41, 48, "6, 7, 0 … 4", 0.7)])
s.step("48, 46, 41. The gain grows with bigger blocks. But spatial locality limits it: the next access is often to the same block, and may still wait for its word.", show("cwm") + [s.take("send the wanted word first · restart the CPU at once")])

# ---------------------------------------------------------------- merging write buffer
s.scene("merge")
s.step("Stage 7: the merging write buffer. Writes to memory wait in a buffer of four entries. Each entry can hold a block of four 8-byte words.", [s.head("Stage 7 of 8: merging write buffer"), s.untake()] + hide("cw", "cwm") + show("wb"))
s.step("The program writes four words in a row, to addresses 100, 108, 116 and 124. First, without merging.", [hl("wb")])
s.step("Each write takes its own entry, and uses one word of it.", [st("wb[0][1]", "100"), st("wb[0][2]", "M[100]"), st("wb[1][1]", "108", 0.25), st("wb[1][2]", "M[108]", 0.25), st("wb[2][1]", "116", 0.5), st("wb[2][2]", "M[116]", 0.5), st("wb[3][1]", "124", 0.75), st("wb[3][2]", "M[124]", 0.75)])
s.step("The buffer is full after four writes. The fifth write stalls the CPU. And memory receives four separate one-word writes.", [mk("wb[0..=3]")])
s.step("Now with merging. The buffer checks whether a new write falls in a block already waiting there. Address 100 starts a new entry.", [st(f"wb[{i}][{c}]", "") for i in range(4) for c in (1, 2)] + [st("wb[0][1]", "100", 0.4), st("wb[0][2]", "M[100]", 0.6)])
s.step("108, 116 and 124 are the next words of the same block. They merge into the same entry.", [st("wb[0][3]", "M[108]"), st("wb[0][4]", "M[116]", 0.3), st("wb[0][5]", "M[124]", 0.6)])
s.step("One entry used, three free. And memory gets one 32-byte write, far more efficient than four small ones. Some processors call this write combining.", [hl("wb[0]"), mk("wb[1..=3]", 0.4), s.take("merge writes to the same block: fewer stalls, fewer memory writes")])

# ---------------------------------------------------------------- summary + exam
s.scene("exam")
s.step("The seven on one table, with what each improves and what it costs. Pipelining is the odd one: more bandwidth, but more cycles per hit.", [s.head("Summary"), s.untake()] + hide("wb") + show("sumt") + [hl("sumt[2]", 0.6)])
s.step("Now an exam question.", [s.head("Exam question")] + hide("sumt") + show("q"))
s.step("A 4-way L1 with way prediction: right 80 percent of the time for a 1 cycle hit, otherwise 2 cycles. The miss rate is 2 percent, and blocks are 64 bytes. Memory takes 50 cycles, then sends 8 bytes per cycle.", [hl("q[0][0]"), hl("q[1][0]", 0.3), hl("q[2][0]", 0.6)])
s.step("Find the average hit time, the miss penalty with and without critical word first, the AMAT both ways, and the bank of block 1027 with 8 banks. Pause and work it out.", [hl("q[0][1]"), hl("q[1][1]", 0.2), hl("q[2][1]", 0.4), hl("q[3]", 0.6)])
s.step("a: 0.8 times 1 plus 0.2 times 2: 1.2 cycles.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: waiting for the whole block, 50 plus 64 over 8, which is 58 cycles. With critical word first, 50 plus 1: 51 cycles.", rv("qa", 1))
s.step("c: 1.2 plus 0.02 times 58 is 2.36. With critical word first, 1.2 plus 0.02 times 51 is 2.22 cycles. d: 1027 mod 8 is 3. Bank 3.", rv("qa", 2) + rv("qa", 3))
s.step("The usual slips: forgetting that a wrong prediction still hits, just later, and counting the whole block when the CPU restarts as soon as its word arrives.", [s.take("a mispredicted way is a slow hit, not a miss")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Small, simple L1 caches and way prediction keep the hit fast. Pipelining, banks and nonblocking caches serve more accesses per cycle, and let misses overlap.", [hl("stages[1..=2]"), hl("stages[3..=4]", 0.5)])
s.step("Critical word first and the merging write buffer shorten the miss penalty.", [hl("stages[5..=6]")])
s.step("Next video: part 2. Compiler optimizations, prefetching, and HBM.", [mk("stages[0..=7]"), s.take("Next: advanced optimizations, part 2")])

s.save("/home/claude/playlist/m2v10.json")

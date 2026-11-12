"""Module 2, video 8: the six basic cache optimizations, each with its effect on AMAT and a worked number."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

r = lambda x, n=2: round(x, n)
MR = {16: 4.0, 32: 3.0, 64: 2.5, 128: 2.6, 256: 3.3}
AM = {b: r(1 + m / 100 * (40 + b / 8), 2) for b, m in MR.items()}
assert AM == {16: 2.68, 32: 2.32, 64: 2.2, 128: 2.46, 256: 3.38} and min(AM, key=AM.get) == 64
assert (r(1 + 0.04 * 50), r(1.2 + 0.03 * 50)) == (3.0, 2.7)
assert (r(1 + 0.05 * 25), r(1.36 + 0.04 * 25)) == (2.25, 2.36)
assert (r(1 + 0.04 * (10 + 0.25 * 200)), r(1 + 0.04 * 200)) == (3.4, 9.0)
assert (r(1 + 0.06 * 40), r(1.1 + 0.045 * 40), r(1.2 + 0.04 * 40)) == (3.4, 2.9, 2.8) and 32 // 4 == 8 and 32 // 8 == 4

s = Script("Six basic cache optimizations")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The three levers: hit time, miss rate, miss penalty"],
    [2, "Larger blocks"],
    [3, "Larger caches"],
    [4, "Higher associativity, and the 2:1 rule"],
    [5, "Multilevel caches"],
    [6, "Reads before writes"],
    [7, "No address translation while indexing"],
    [8, "The summary table, and an exam question"]]})
s.obj({"id": "lev", "type": "math", "region": "center", "lines": [
    "\"AMAT\" = \"hit time\" + \"miss rate\" times \"miss penalty\"",
    "\"miss rate:\" quad \"larger blocks, larger caches, more ways\"",
    "\"miss penalty:\" quad \"multilevel caches, reads before writes\"",
    "\"hit time:\" quad \"no address translation while indexing\""]})
s.obj({"id": "bs", "type": "table", "region": "center", "columns": ["block size", "miss rate", "miss penalty = 40 + size ÷ 8", "AMAT = 1 + rate × penalty"], "rows": [
    [f"{b} B", f"{m}%", f"{int(40 + b / 8)}", ""] for b, m in MR.items()]})
s.obj({"id": "bp", "type": "plot", "region": "center", "x": {"label": "block size: 16, 32, 64, 128, 256 bytes", "min": 3.5, "max": 8.5}, "y": {"label": "AMAT (cycles)", "min": 2, "max": 3.5},
       "curves": [{"id": "am", "points": [[4 + i, AM[b]] for i, b in enumerate(MR)], "label": "AMAT", "visible": False}],
       "points": [{"id": "best", "at": [6, AM[64]], "label": "64 B: 2.2"}]})
s.obj({"id": "bx", "type": "table", "region": "center", "columns": ["bigger blocks", "effect"], "rows": [
    ["more neighbours fetched on each miss", "fewer compulsory misses: spatial locality"],
    ["each miss moves more bytes", "longer miss penalty"],
    ["same cache, fewer lines", "more conflict and capacity misses, if blocks get too big"]]})
s.obj({"id": "cs", "type": "math", "region": "center", "lines": [
    "\"32 KB:\" quad 1 + 0.04 times 50 = 3.0 \"cycles\"",
    "\"64 KB, hit 1.2 cycles:\" quad 1.2 + 0.03 times 50 = 2.7 \"cycles\"",
    "\"cost: longer hit time, more area and power\""]})
s.obj({"id": "as", "type": "table", "region": "center", "columns": ["rule", "what it says"], "rows": [
    ["2:1 cache rule", "a direct-mapped cache of size N misses about as often as a 2-way cache of size N ÷ 2"],
    ["8-way ≈ fully associative", "beyond 8 ways, conflict misses almost vanish"],
    ["the price", "more comparators and a mux: a longer hit, maybe a slower clock"]]})
s.obj({"id": "asm", "type": "math", "region": "center", "lines": [
    "\"direct-mapped:\" quad 1 + 0.05 times 25 = 2.25 \"cycles\"",
    "\"2-way, clock 1.36 times longer:\" quad 1.36 + 0.04 times 25 = 2.36 \"cycles\"",
    "\"with a 100 cycle penalty:\" quad 1 + 5 = 6 quad \"vs\" quad 1.36 + 4 = 5.36"]})
s.obj({"id": "ml", "type": "math", "region": "center", "lines": [
    "\"L1 only:\" quad 1 + 0.04 times 200 = 9 \"cycles\"",
    "\"add L2 (10 cycles, local miss 25%):\" quad 1 + 0.04 times (10 + 0.25 times 200) = 3.4 \"cycles\""]})
s.obj({"id": "mlx", "type": "table", "region": "center", "columns": ["choice", "meaning"], "rows": [
    ["inclusive", "everything in L1 is also in L2: simple coherence, wasted space"],
    ["exclusive", "a block is in L1 or L2, never both: more total capacity"],
    ["L1 goal", "fast hit: small, simple"], ["L2 goal", "few misses to memory: large, more ways"]]})
s.obj({"id": "rw", "type": "table", "region": "center", "columns": ["situation", "slow way", "fast way"], "rows": [
    ["write-through, writes in buffer", "drain the buffer first", "check the buffer, then read now"],
    ["write-back, dirty victim", "write victim, then read", "buffer victim, read first"]]})
s.obj({"id": "vi", "type": "table", "region": "center", "columns": ["cache indexed and tagged with", "hit needs translation first?", "problem"], "rows": [
    ["physical address (PIPT)", "yes: TLB, then cache", "slow hit"],
    ["virtual address (VIVT)", "no", "aliases, flush on a process switch, protection"],
    ["virtual index, physical tag (VIPT)", "no: TLB and cache in parallel", "only if the index fits in the page offset"]]})
s.obj({"id": "vim", "type": "math", "region": "center", "lines": [
    "\"VIPT works when\" quad \"cache size\" / \"ways\" <= \"page size\"",
    "\"32 KB, 8-way, 4 KB pages:\" quad 32 / 8 = 4 \"KB\" <= 4 \"KB\" quad \"works\"",
    "\"32 KB, 4-way:\" quad 32 / 4 = 8 \"KB\" > 4 \"KB\" quad \"does not\""]})
s.obj({"id": "sum", "type": "table", "region": "center", "columns": ["optimization", "hit time", "miss penalty", "miss rate", "attacks"], "rows": [
    ["larger blocks", "", "worse", "better", "compulsory"],
    ["larger caches", "worse", "", "better", "capacity"],
    ["higher associativity", "worse", "", "better", "conflict"],
    ["multilevel caches", "", "better", "", "–"],
    ["reads before writes", "", "better", "", "–"],
    ["no translation in indexing", "better", "", "", "–"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["32 KB L1, miss penalty 40 cycles, 4 KB pages. Find:"], "rows": [
    ["a) the best of: A direct-mapped, hit 1, miss 6% · B 2-way, hit 1.1, miss 4.5% · C 4-way, hit 1.2, miss 4%"],
    ["b) the fewest ways that let this cache be VIPT"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"A:\" quad 1 + 0.06 times 40 = 3.4 \"cycles\"",
    "\"B:\" quad 1.1 + 0.045 times 40 = 2.9 \"cycles\"",
    "\"C:\" quad 1.2 + 0.04 times 40 = 2.8 \"cycles\" quad \"best\"",
    "\"b)\" quad (32 \"KB\") / \"ways\" <= 4 \"KB\" quad => quad \"ways\" >= 8"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Every cache optimization attacks one term of the AMAT formula. Here are the six basic ones, each with a number that shows when it helps, and when it does not.", [s.head("Six basic cache optimizations")])
s.step("Here are the eight stages.", show("stages"))
s.step("The three levers, then the three that lower the miss rate: larger blocks, larger caches, and more ways.", [hl("stages[0..=3]")])
s.step("Then two that cut the miss penalty, one that cuts the hit time, and a summary with an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- levers
s.scene("levers")
s.step("Stage 1: AMAT is hit time plus miss rate times miss penalty. So there are exactly three levers.", [s.head("Stage 1 of 8: three levers")] + hide("stages") + show("lev") + [hl("lev[0]")])
s.step("Three optimizations lower the miss rate: larger blocks, larger caches, and higher associativity.", rv("lev", 1))
s.step("Two lower the miss penalty: multilevel caches, and giving reads priority over writes.", rv("lev", 2))
s.step("And one lowers the hit time: avoiding address translation while indexing the cache.", rv("lev", 3))
s.step("The catch, which every exam question tests: improving one term usually worsens another. Only AMAT decides.", [s.take("each optimization moves one term, and usually hurts another")])

# ---------------------------------------------------------------- block size
s.scene("blocks")
s.step("Stage 2: larger blocks. A bigger block brings in more neighbouring bytes on each miss.", [s.head("Stage 2 of 8: larger blocks")] + hide("lev") + [s.untake()] + show("bx") + [hl("bx[0]")])
s.step("Thanks to spatial locality, the next few accesses find those bytes already there: fewer compulsory misses.", [hl("bx[0][1]")])
s.step("But each miss now moves more bytes, so the miss penalty grows.", [hl("bx[1]")])
s.step("And in a cache of fixed size, bigger blocks mean fewer lines. Past a point, conflict and capacity misses rise.", [hl("bx[2]")])
s.step("Numbers for one example cache. The miss penalty is 40 cycles of latency, plus 1 cycle per 8 bytes.", hide("bx") + show("bs") + [hl("bs[0][2]"), hl("bs[4][2]", 0.4)])
for i, b in enumerate(MR):
    say = {16: "16 byte blocks: 1 plus 0.04 times 42, which is 2.68 cycles.",
           32: "32 bytes: the miss rate drops to 3 percent. AMAT 2.32.",
           64: "64 bytes: 2.5 percent, penalty 48. AMAT 2.2.",
           128: "128 bytes: the miss rate starts to rise again, and the penalty is 56. AMAT 2.46.",
           256: "256 bytes: worse on both counts. AMAT 3.38."}[b]
    s.step(say, [hl(f"bs[{i}]"), {"action": "set", "target": f"bs[{i}][3]", "value": f"{AM[b]}", "delay": 0.4}])
s.step("Plot it: the AMAT curve falls, bottoms out, and rises again.", hide("bs") + show("bp") + [{"action": "trace", "target": "bp.am"}])
s.step("The best block here is 64 bytes. Not the lowest miss rate alone: the lowest AMAT.", [hl("bp.best"), s.take("block size: a U-shaped curve · pick the lowest AMAT")])

# ---------------------------------------------------------------- cache size
s.scene("size")
s.step("Stage 3: larger caches. The obvious fix for capacity misses: hold more of the program.", [s.head("Stage 3 of 8: larger caches")] + hide("bp") + [s.untake()] + show("cs") + [hl("cs[0]")])
s.step("Doubling a 32 kilobyte cache to 64 cuts the miss rate from 4 to 3 percent. But the bigger array is slower: hit time rises to 1.2 cycles.", rv("cs", 1))
s.step("Here it still wins, 2.7 against 3.0. But bigger caches also cost area and power, which is why L1 caches stay small.", rv("cs", 2) + [s.take("larger cache: fewer capacity misses · slower hit, more power")])

# ---------------------------------------------------------------- associativity
s.scene("assoc")
s.step("Stage 4: higher associativity attacks conflict misses. Two rules of thumb are worth knowing.", [s.head("Stage 4 of 8: higher associativity")] + hide("cs") + [s.untake()] + show("as"))
s.step("The 2 to 1 rule: a direct-mapped cache of size N misses about as often as a 2-way cache of half the size.", [hl("as[0]")])
s.step("And 8-way set-associative is, for practical purposes, as good as fully associative.", [hl("as[1]")])
s.step("The price: more comparators and a wider multiplexer, so the hit takes longer. Sometimes it stretches the clock itself.", [hl("as[2]")])
s.step("Example: direct-mapped, 5 percent misses, 25 cycle penalty: 2.25 cycles.", hide("as") + show("asm") + [hl("asm[0]")])
s.step("2-way cuts misses to 4 percent, but stretches the clock by 36 percent. AMAT: 2.36. Worse!", rv("asm", 1))
s.step("With a 100 cycle penalty, the same 2-way cache wins: 5.36 against 6. The more a miss costs, the more associativity is worth.", rv("asm", 2) + [s.take("more ways: fewer conflict misses · slower hit · worth it when misses are costly")])

# ---------------------------------------------------------------- multilevel
s.scene("multilevel")
s.step("Stage 5: multilevel caches attack the miss penalty. We worked the formula in the AMAT video; here is the payoff.", [s.head("Stage 5 of 8: multilevel caches")] + hide("asm") + [s.untake()] + show("ml") + [hl("ml[0]")])
s.step("L1 alone, with 4 percent misses and 200 cycle memory: 9 cycles. Add a 10 cycle L2 that catches 3 out of 4 of those misses, and AMAT drops to 3.4.", rv("ml", 1))
s.step("Design choices: an inclusive L2 also holds everything in L1, which simplifies coherence. An exclusive one never duplicates, so the two together hold more.", hide("ml") + show("mlx") + [hl("mlx[0..=1]")])
s.step("And the goals differ: L1 is kept small and simple for a fast hit; L2 is large and more associative to keep misses away from memory.", [hl("mlx[2..=3]"), s.take("L1: fast hit · L2: few memory trips")])

# ---------------------------------------------------------------- reads before writes
s.scene("rw")
s.step("Stage 6: give read misses priority over writes. The processor waits for reads; it does not wait for writes.", [s.head("Stage 6 of 8: reads before writes")] + hide("mlx") + [s.untake()] + show("rw"))
s.step("Write-through: a read miss arrives while writes sit in the write buffer. The slow way waits for the buffer to drain.", [hl("rw[0][1]")])
s.step("The fast way checks the buffer for the address. If it is not there, the read goes to memory at once, ahead of the waiting writes.", [hl("rw[0][2]")])
s.step("Write-back: a read miss must evict a dirty block. Instead of writing it back first, copy it to a buffer, read the new block, then write the victim later.", [hl("rw[1]")])
s.step("Either way, the read's miss penalty no longer includes a write.", [s.take("reads are urgent · writes can wait in a buffer")])

# ---------------------------------------------------------------- VIPT
s.scene("vipt")
s.step("Stage 7: avoid address translation during indexing. Programs use virtual addresses, but memory uses physical ones, and the TLB translates between them.", [s.head("Stage 7 of 8: no translation while indexing")] + hide("rw") + [s.untake()] + show("vi"))
s.step("A physically indexed cache must wait for the TLB first: translation, then cache. That makes every hit slower.", [hl("vi[0]")])
s.step("A fully virtual cache skips the TLB, but two virtual addresses can name the same physical block, the cache must be flushed on a process switch, and protection gets harder.", [hl("vi[1]")])
s.step("The common answer: virtually indexed, physically tagged. Index the cache with page offset bits, which translation never changes, while the TLB translates the rest in parallel. Then compare physical tags.", [hl("vi[2]")])
s.step("It works only if the index and offset bits fit inside the page offset: cache size over ways must be at most the page size.", hide("vi") + show("vim") + [hl("vim[0]")])
s.step("32 kilobytes, 8-way, 4 kilobyte pages: 4 kilobytes per way, so it fits. That is why so many L1 caches are exactly 32 kilobytes and 8-way.", rv("vim", 1))
s.step("The same cache 4-way needs 8 kilobytes per way: too big, so it cannot be VIPT.", rv("vim", 2) + [s.take("VIPT: cache size ÷ ways ≤ page size")])

# ---------------------------------------------------------------- summary
s.scene("summary")
s.step("Stage 8: all six in one table, with the term each improves and the term it can hurt.", [s.head("Stage 8 of 8: the summary")] + hide("vim") + [s.untake()] + show("sum"))
s.step("The first three cut the miss rate, and each targets one of the three C's: compulsory, capacity, conflict. But each makes something else worse.", [hl("sum[0..=2]")])
s.step("Multilevel caches and read priority cut the miss penalty. Avoiding translation cuts the hit time.", [hl("sum[3..=5]")])
s.step("Learn this table: GATE asks which optimization reduces which term, and which one it can increase.", [{"action": "mark", "target": "sum.attacks"}, s.take("miss rate: blocks, size, ways · penalty: levels, read priority · hit: VIPT")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question")] + hide("sum") + [s.untake()] + show("q"))
s.step("A 32 kilobyte L1 with a 40 cycle miss penalty. Three designs: direct-mapped, 2-way and 4-way, each with its own hit time and miss rate. Which is best?", [hl("q[0]")])
s.step("And with 4 kilobyte pages, how many ways does it need to be VIPT? Pause and work it out.", [hl("q[1]")])
s.step("A: 1 plus 0.06 times 40, 3.4 cycles.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("B: 1.1 plus 0.045 times 40, 2.9 cycles.", rv("qa", 1))
s.step("C: 1.2 plus 0.04 times 40, 2.8 cycles. C is best, despite the slowest hit.", rv("qa", 2))
s.step("b: 32 kilobytes over the number of ways must be at most 4 kilobytes, so at least 8 ways.", rv("qa", 3))
s.step("The usual slip: picking the design with the fastest hit or the lowest miss rate, instead of computing AMAT.", [s.take("always compare AMATs")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap")] + hide("qa") + [s.untake()] + show("stages"))
s.step("Larger blocks, larger caches and more ways cut the miss rate, each with a cost: a longer penalty, or a slower hit.", [hl("stages[0..=3]")])
s.step("Multilevel caches and read priority cut the penalty, and VIPT indexing cuts the hit time.", [hl("stages[4..=7]")])
s.step("Next video: memory technology, from SRAM and DRAM to DDR and HBM.", [{"action": "mark", "target": "stages[0..=7]"}, s.take("Next: memory technology")])

s.save("/home/claude/playlist/m2v8.json")

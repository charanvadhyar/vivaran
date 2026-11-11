"""Module 2, video 3: write policies in detail, animated: write-through, write buffer, write-back and dirty bits,
write-allocate and no-write-allocate, traffic counting, costs, exam question."""
import sys
sys.path.insert(0, ".")
from common import Script

LINE = {"A": 0, "B": 1, "C": 0}


def sim_wb(trace):
    cache, dirty, br, bw, log = [None, None], [0, 0], 0, 0, []
    for op, b in trace:
        l = LINE[b]
        if cache[l] == b:
            dirty[l] |= op == "W"; log.append("hit"); continue
        ev = cache[l] if cache[l] and dirty[l] else None
        bw += ev is not None; br += 1; cache[l] = b; dirty[l] = int(op == "W"); log.append(("miss", ev))
    return br, bw, log, cache, dirty


def sim_wt(trace):
    cache, br, ww, log = [None, None], 0, 0, []
    for op, b in trace:
        l = LINE[b]
        if op == "W":
            ww += 1; log.append("hit" if cache[l] == b else "miss"); continue
        if cache[l] == b:
            log.append("hit"); continue
        br += 1; cache[l] = b; log.append("miss")
    return br, ww, log, cache


T5 = [("W", "X"), ("W", "X"), ("R", "X"), ("W", "Y"), ("R", "X")]
LINE.update({"X": 0, "Y": 0})
assert sim_wb(T5)[:2] == (3, 2) and sim_wt(T5)[:2] == (1, 3)
TQ = [("W", "A"), ("W", "A"), ("R", "B"), ("W", "C"), ("R", "A"), ("W", "B")]
br, bw, log, cache, dirty = sim_wb(TQ)
assert (br, bw, cache, dirty) == (4, 2, ["A", "B"], [0, 1]) and sum(x == "hit" for x in log) == 2
br2, ww2, log2, _ = sim_wt(TQ)
assert (br2, ww2) == (2, 4) and sum(x == "hit" for x in log2) == 1
assert 1.3 * 100 == 130 and 10 ** 6 * 4 == 4_000_000 and 20_000 * 64 == 1_280_000

s = Script("Write policies, step by step")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why a write is harder than a read"],
    [2, "Write-through, animated"],
    [3, "The write buffer: why the processor need not wait"],
    [4, "Write-back and the dirty bit, animated"],
    [5, "Write misses: write-allocate or no-write-allocate"],
    [6, "One trace, two policy pairs: count the traffic"],
    [7, "What each policy costs, in cycles and bytes"],
    [8, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["", "read", "write"], "rows": [
    ["tag check", "in parallel with the data", "must finish first"],
    ["size", "whole word or block", "1 to 8 bytes"],
    ["afterwards", "cache = memory", "cache ≠ memory"]]})
# the machine
s.obj({"id": "path", "type": "diagram", "region": "left", "layout": "layers", "direction": "right", "nodes": [
    {"id": "cpu", "label": "CPU"}, {"id": "cache", "label": "cache"}, {"id": "mem", "label": "memory"}],
    "edges": [{"from": "cpu", "to": "cache"}, {"from": "cache", "to": "mem"}]})
s.obj({"id": "pathb", "type": "diagram", "region": "left", "layout": "layers", "direction": "right", "nodes": [
    {"id": "cpu", "label": "CPU"}, {"id": "cache", "label": "cache"}, {"id": "buf", "label": "buffer"}, {"id": "mem", "label": "memory"}],
    "edges": [{"from": "cpu", "to": "cache"}, {"from": "cache", "to": "buf"}, {"from": "buf", "to": "mem"}]})


def cache_tbl(id, rows):
    s.obj({"id": id, "type": "table", "region": "right", "columns": ["line", "valid", "dirty", "block", "data"], "rows": rows})


def mem_tbl(id, vals):
    s.obj({"id": id, "type": "table", "region": "bottom", "columns": ["memory block", "A", "B", "C"], "rows": [["value"] + vals]})


cache_tbl("c1", [["0", "1", "–", "A", "10"], ["1", "0", "–", "", ""]])
mem_tbl("m1", ["10", "20", "30"])
s.obj({"id": "buf", "type": "array", "region": "right", "values": ["", "", "", ""]})
s.obj({"id": "bufx", "type": "table", "region": "center", "columns": ["write buffer", "what it means"], "rows": [
    ["the CPU writes into the buffer and goes on", "a write costs about 1 cycle, not a memory access"],
    ["the buffer drains to memory in the background", "memory sees every write, just later"],
    ["the buffer is full", "the CPU stalls until a slot frees up"],
    ["a read miss to a block still in the buffer", "check the buffer first, or wait until it drains"]]})
cache_tbl("c2", [["0", "1", "0", "A", "10"], ["1", "0", "0", "", ""]])
mem_tbl("m2", ["10", "20", "30"])
cache_tbl("c3", [["0", "1", "–", "A", "10"], ["1", "0", "–", "", ""]])
mem_tbl("m3", ["10", "20", "30"])
s.obj({"id": "pairs", "type": "table", "region": "center", "columns": ["", "write-allocate", "no-write-allocate"], "rows": [
    ["on a write miss", "fetch the block, then write it in the cache", "write to memory; leave the cache alone"],
    ["usual partner", "write-back: later writes to the block hit", "write-through: every write goes to memory anyway"],
    ["good when", "the block is soon read or written again", "the data is written once and not reused"]]})
s.obj({"id": "traffic", "type": "table", "region": "center",
       "columns": ["#", "access", "write-back + write-allocate", "WB traffic", "write-through + no-write-allocate", "WT traffic"],
       "rows": [[1, "write X", "", "", "", ""], [2, "write X", "", "", "", ""], [3, "read X", "", "", "", ""],
                [4, "write Y", "", "", "", ""], [5, "read X", "", "", "", ""]]})
s.obj({"id": "tsum", "type": "table", "region": "center", "columns": ["policy pair", "block reads", "block writes", "single-word writes"], "rows": [
    ["write-back + write-allocate", "", "", ""], ["write-through + no-write-allocate", "", "", ""]]})
s.obj({"id": "cost", "type": "math", "region": "center", "lines": [
    "\"write-back miss penalty\" = (1 + f_\"dirty\") times T_\"block\"",
    "f_\"dirty\" = 0.3, quad T_\"block\" = 100: quad 1.3 times 100 = 130 \"cycles\"",
    "\"write-through traffic\" = \"writes\" times \"word size\" = 10^6 times 4 \"B\" = 4 \"MB\"",
    "\"write-back traffic\" = \"dirty evictions\" times \"block size\" = 20000 times 64 \"B\" = 1.28 \"MB\""]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["", "write-through", "write-back"], "rows": [
    ["memory up to date?", "always", "only after the block is evicted"],
    ["extra hardware", "write buffer", "dirty bit per line"],
    ["read miss cost", "fetch the block", "maybe write back a dirty block, then fetch"],
    ["traffic for repeated writes", "one memory write each time", "one block write, at eviction"],
    ["multiprocessors and I/O", "easy: memory is current", "needs coherence: memory may be stale"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["Direct-mapped, 2 lines; A and C map to line 0, B to line 1; the cache starts empty. Trace:"], "rows": [
    ["write A · write A · read B · write C · read A · write B"],
    ["a) write-back + write-allocate: hits, block reads, block writes, and which lines end dirty"],
    ["b) write-through + no-write-allocate: hits, block reads, word writes"]]})
s.obj({"id": "qt", "type": "table", "region": "center", "columns": ["access", "write-back + write-allocate", "write-through + no-write-allocate"], "rows": [
    ["write A", "", ""], ["write A", "", ""], ["read B", "", ""], ["write C", "", ""], ["read A", "", ""], ["write B", "", ""],
    ["total", "", ""]]})


def hl(*ids, d=0.0, step=0.25):
    return [{"action": "highlight", "target": t, **({"delay": round(d + k * step, 2)} if d + k * step else {})} for k, t in enumerate(ids)]


def setc(t, r, c, v, d=0.0):
    return {"action": "set", "target": f"{t}[{r}][{c}]", "value": v, **({"delay": d} if d else {})}


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("A cache must answer four questions. We have done placement, finding a block and replacement. Now the last one: what happens on a write.", [s.head("Write policies, step by step")])
s.step("Here are the eight stages.", [{"action": "show", "target": "stages"}])
s.step("Why writes are hard, then write-through with its write buffer, and write-back with its dirty bit, each animated step by step.", [{"action": "highlight", "target": "stages[0..=3]"}])
s.step("Then what happens on a write miss, a full traffic count, the costs, and an exam question.", [{"action": "highlight", "target": "stages[4..=7]"}])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: why is a write harder than a read?", [s.head("Stage 1 of 8: why writes are harder"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "why"}])
s.step("On a read, the cache reads the data and checks the tag at the same time. On a miss, it just throws the data away.", hl("why[0][1]"))
s.step("A write cannot do that. If the tag does not match, writing first would destroy another block's data. So the tag check comes first, and a write hit takes longer.", hl("why[0][2]"))
s.step("A write may also change just one byte of a block, so the cache must change exactly those bytes.", hl("why[1]"))
s.step("And after a write, the cache holds a newer value than memory. When does memory catch up? That is the policy.", hl("why[2]") + [s.take("the question: when does memory get the new value?")])

# ---------------------------------------------------------------- write-through
s.scene("wt")
s.step("Stage 2: write-through. Here is a CPU, a two line cache, and memory holding blocks A, B and C.", [s.head("Stage 2 of 8: write-through"), {"action": "hide", "target": "why"}, s.untake(),
       {"action": "show", "target": "path"}, {"action": "show", "target": "c1"}, {"action": "show", "target": "m1"}])
s.step("Line 0 holds block A, with the value 10. Memory also says 10. They agree.", hl("c1[0]", "m1[0][1]"))
s.step("The CPU writes 11 to A. It is a hit, so the cache line changes to 11.", hl("path.cpu", "path.cpu->cache", "path.cache") + [setc("c1", 0, 4, "11", 0.6)])
s.step("Write-through sends the same write on to memory at once. Memory becomes 11 too.", hl("path.cache->mem", "path.mem") + [setc("m1", 0, 1, "11", 0.5)])
s.step("Now 12, then 13. Every write goes to the cache and to memory.", [setc("c1", 0, 4, "12"), setc("m1", 0, 1, "12", 0.2), setc("c1", 0, 4, "13", 0.5), setc("m1", 0, 1, "13", 0.7)] + hl("path.cache->mem", d=0.1))
s.step("Memory always holds the latest value, so a line never needs to be written back. The dirty bit is not needed: shown as a dash.", hl("c1.dirty"))
s.step("The cost: three writes made three trips to memory. Memory takes around 100 cycles, so if the CPU waited each time, every store would cost 100 cycles.", [s.take("write-through: every write goes to memory · memory is always current")])

# ---------------------------------------------------------------- write buffer
s.scene("buffer")
s.step("Stage 3: so write-through caches add a write buffer between the cache and memory.", [s.head("Stage 3 of 8: the write buffer"), {"action": "hide", "target": "path"}, {"action": "hide", "target": "c1"}, {"action": "hide", "target": "m1"}, s.untake(),
       {"action": "show", "target": "pathb"}, {"action": "show", "target": "buf"}])
s.step("The CPU writes A equals 11 into the cache and into the buffer, and carries on with its next instruction straight away.", hl("pathb.cpu->cache", "pathb.cache->buf") + [{"action": "set", "target": "buf[0]", "value": "A=11", "delay": 0.5}])
s.step("More writes arrive: B equals 21, A equals 12, C equals 31. Each takes a slot.", [{"action": "set", "target": "buf[1]", "value": "B=21"}, {"action": "set", "target": "buf[2]", "value": "A=12", "delay": 0.3}, {"action": "set", "target": "buf[3]", "value": "C=31", "delay": 0.6}])
s.step("Meanwhile, the buffer drains to memory in the background, oldest first. A equals 11 goes out, and its slot frees up.", hl("pathb.buf->mem", "pathb.mem") + [{"action": "set", "target": "buf[0]", "value": "", "delay": 0.6}])
s.step("But if writes come faster than memory can take them, the buffer fills, and then the CPU must stall.", [{"action": "set", "target": "buf[0]", "value": "B=22"}, {"action": "mark", "target": "buf[0..=3]", "delay": 0.4}])
s.step("Here are the four rules of a write buffer.", [{"action": "hide", "target": "pathb"}, {"action": "hide", "target": "buf"}, {"action": "show", "target": "bufx"}, *hl("bufx[0..=1]")])
s.step("A full buffer stalls the CPU. And a trap: if a read misses on a block whose new value is still waiting in the buffer, memory has the old value.", hl("bufx[2]", "bufx[3]", step=0.4))
s.step("So the read must check the buffer first, or wait for it to drain. Otherwise it reads stale data.", [s.take("write buffer: the CPU does not wait · full buffer → stall · read misses check it")])

# ---------------------------------------------------------------- write-back
s.scene("wb")
s.step("Stage 4: write-back. Same machine, but now each line has a dirty bit, and memory is updated only when a line is evicted.", [s.head("Stage 4 of 8: write-back and the dirty bit"), {"action": "hide", "target": "bufx"}, s.untake(),
       {"action": "show", "target": "path"}, {"action": "show", "target": "c2"}, {"action": "show", "target": "m2"}])
s.step("Line 0 holds A equals 10, dirty bit 0, which means clean: the same as memory.", hl("c2[0]", "c2[0][2]"))
s.step("The CPU writes 11 to A. The cache changes to 11, and the dirty bit is set to 1.", hl("path.cpu->cache", "path.cache") + [setc("c2", 0, 4, "11", 0.4), setc("c2", 0, 2, "1", 0.7)])
s.step("Memory is not touched. It still says 10. The cache and memory now disagree, and the dirty bit records that.", [{"action": "mark", "target": "m2[0][1]"}, {"action": "mark", "target": "c2[0][2]", "delay": 0.3}])
s.step("Writes of 12 and 13 change only the cache. Three writes, zero trips to memory.", [setc("c2", 0, 4, "12"), setc("c2", 0, 4, "13", 0.5)] + hl("c2[0][4]"))
s.step("Now the CPU reads C. C also maps to line 0, so it is a miss, and A must be evicted.", hl("c2[0]", "m2[0][3]", step=0.4))
s.step("A is dirty, so before C can come in, the whole block A is written back. Memory finally gets 13.", hl("path.cache->mem", "path.mem") + [setc("m2", 0, 1, "13", 0.5)])
s.step("Then C is fetched into line 0, clean, with the value 30.", [setc("c2", 0, 3, "C"), setc("c2", 0, 4, "30", 0.3), setc("c2", 0, 2, "0", 0.6)] + hl("c2[0]", d=0.6))
s.step("Later, if C is evicted while still clean, it is just dropped: memory already has the same value. Only dirty blocks cost a write back.", [s.take("write-back: write the cache only · dirty bit · write the block back on eviction")])
s.step("Edge case: the dirty bit is per line, not per byte. Change one byte, and the whole block goes back to memory.", hl("c2.dirty"))

# ---------------------------------------------------------------- write miss
s.scene("wmiss")
s.step("Stage 5: so far every write was a hit. What if the block is not in the cache?", [s.head("Stage 5 of 8: write misses"), {"action": "hide", "target": "c2"}, {"action": "hide", "target": "m2"}, s.untake(),
       {"action": "show", "target": "c3"}, {"action": "show", "target": "m3"}])
s.step("Line 0 holds A. The CPU writes 31 to C, which maps to line 0: a write miss.", hl("c3[0]", "m3[0][3]", step=0.4))
s.step("Choice one, write-allocate: treat it like a read miss. Fetch C into line 0, then write 31 into the cache.", [setc("c3", 0, 3, "C"), setc("c3", 0, 4, "30", 0.3), setc("c3", 0, 4, "31", 0.7)] + hl("path.cache->mem"))
s.step("Next time the CPU touches C, it hits.", hl("c3[0]"))
s.step("Choice two, no-write-allocate: go around the cache. Put C back the way it was, with A in line 0.", [setc("c3", 0, 3, "A"), setc("c3", 0, 4, "10", 0.3)])
s.step("The write of 31 goes straight to memory, and the cache does not change. Also called write-around.", hl("path.cache->mem") + [setc("m3", 0, 3, "31", 0.5)])
s.step("Which pairs make sense?", [{"action": "hide", "target": "path"}, {"action": "hide", "target": "c3"}, {"action": "hide", "target": "m3"}, {"action": "show", "target": "pairs"}, *hl("pairs[0]")])
s.step("Write-back goes with write-allocate: bring the block in, and later writes to it hit and stay in the cache.", hl("pairs[1][1]"))
s.step("Write-through goes with no-write-allocate: every write goes to memory anyway, so fetching the block would only add traffic.", hl("pairs[1][2]"))
s.step("Write-allocate pays off when the block is used again soon. No-write-allocate pays off for data written once, like clearing a large array.", hl("pairs[2]") + [s.take("write-back + write-allocate · write-through + no-write-allocate")])

# ---------------------------------------------------------------- traffic
s.scene("traffic")
s.step("Stage 6: one trace, both pairs. X and Y map to the same line of a direct-mapped cache, which starts empty.", [s.head("Stage 6 of 8: counting the traffic"), {"action": "hide", "target": "pairs"}, s.untake(), {"action": "show", "target": "traffic"}])
rows = [
    ("Access 1, write X, misses. Write-back with allocate fetches X, writes it in the cache, and sets dirty.",
     "miss: fetch X, write, dirty", "1 block read",
     "Write-through with no allocate sends the word to memory and leaves the cache empty.",
     "miss: write word to memory", "1 word write"),
    ("Access 2, write X again. Write-back: now a hit, the cache changes, memory does not.",
     "hit: write in cache", "none",
     "Write-through: X was never brought in, so a miss again, and another word to memory.",
     "miss: write word to memory", "1 word write"),
    ("Access 3, read X. Write-back: a hit.",
     "hit", "none",
     "Write-through: a read miss, so now X is fetched into the cache.",
     "miss: fetch X", "1 block read"),
    ("Access 4, write Y, same line. Write-back: a miss; dirty X must be written back, then Y fetched.",
     "miss: write back X, fetch Y, dirty", "1 block write + 1 block read",
     "Write-through: a miss, the word goes to memory, and X stays in the cache.",
     "miss: write word to memory", "1 word write"),
    ("Access 5, read X. Write-back: X was evicted, so a miss; dirty Y goes back, then X is fetched.",
     "miss: write back Y, fetch X", "1 block write + 1 block read",
     "Write-through: X is still there, a hit.",
     "hit", "none"),
]
for i, (wb_say, wb, wbt, wt_say, wt, wtt) in enumerate(rows):
    s.step(wb_say, [{"action": "highlight", "target": f"traffic[{i}]"}, setc("traffic", i, 2, wb), setc("traffic", i, 3, wbt, 0.5)])
    s.step(wt_say, [setc("traffic", i, 4, wt), setc("traffic", i, 5, wtt, 0.5)])
s.step("Add up each column.", [{"action": "hide", "target": "traffic"}, {"action": "show", "target": "tsum"}])
s.step("Write-back: block reads at accesses 1, 4 and 5 make 3; block writes at 4 and 5 make 2; no single-word writes.", [setc("tsum", 0, 1, "3"), setc("tsum", 0, 2, "2", 0.4), setc("tsum", 0, 3, "0", 0.7)] + hl("tsum[0]"))
s.step("Write-through: one block read at access 3, and single-word writes at 1, 2 and 4: 3.", [setc("tsum", 1, 1, "1"), setc("tsum", 1, 2, "0", 0.4), setc("tsum", 1, 3, "3", 0.7)] + hl("tsum[1]"))
s.step("Neither always wins. Write-back moves whole blocks, but rarely. Write-through moves small words, but often.", [s.take("write-back: few, large transfers · write-through: many, small ones")])

# ---------------------------------------------------------------- costs
s.scene("costs")
s.step("Stage 7: putting numbers on the costs.", [s.head("Stage 7 of 8: costs in cycles and bytes"), {"action": "hide", "target": "tsum"}, s.untake(), {"action": "show", "target": "cost"}])
s.step("With write-back, a miss sometimes has to write a dirty block back first. If a fraction f of evicted blocks are dirty, the average miss penalty is 1 plus f, times the block transfer time.", hl("cost[0]"))
s.step("With 30 percent dirty and 100 cycles per block, a miss costs 130 cycles on average, not 100.", [{"action": "reveal", "target": "cost[1]"}] + hl("cost[1]"))
s.step("Traffic in bytes: a million 4 byte writes under write-through send 4 megabytes to memory.", [{"action": "reveal", "target": "cost[2]"}] + hl("cost[2]"))
s.step("Under write-back, suppose those writes cause 20 thousand dirty evictions of 64 byte blocks: 1.28 megabytes. Much less, when writes hit the same blocks again and again.", [{"action": "reveal", "target": "cost[3]"}] + hl("cost[3]"))
s.step("Here is everything side by side.", [{"action": "hide", "target": "cost"}, {"action": "show", "target": "cmp"}, *hl("cmp[0..=1]")])
s.step("Read misses cost more under write-back, because a dirty victim must go first. Repeated writes cost far less.", hl("cmp[2..=3]"))
s.step("And with several processors or DMA devices sharing memory, write-back means memory can be stale. That needs cache coherence, a later topic.", hl("cmp[4]") + [s.take("most modern caches: write-back + write-allocate, with a write buffer for the evictions")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), {"action": "hide", "target": "cmp"}, s.untake(), {"action": "show", "target": "q"}])
s.step("A direct-mapped cache with 2 lines. A and C map to line 0, and B to line 1. The trace is: write A, write A, read B, write C, read A, write B.", hl("q[0]"))
s.step("For both policy pairs, count the hits and the memory traffic, and say which lines end dirty. Pause and work it out.", hl("q[1..=2]"))
qa = [
    ("Write A: both miss. Write-back fetches A and sets it dirty. Write-through sends a word to memory, and A stays out.", "miss: read A, dirty", "miss: word write"),
    ("Write A again: a hit for write-back. Write-through misses again, another word write.", "hit", "miss: word write"),
    ("Read B: both miss and fetch B into line 1.", "miss: read B", "miss: read B"),
    ("Write C, line 0. Write-back: dirty A is written back, then C is fetched, dirty. Write-through: a word write, the cache unchanged.", "miss: write A back, read C", "miss: word write"),
    ("Read A. Write-back: dirty C is written back, then A is fetched, clean. Write-through: a miss, fetch A.", "miss: write C back, read A", "miss: read A"),
    ("Write B: a hit for both. Write-back sets B dirty. Write-through still sends the word to memory.", "hit, B dirty", "hit: word write"),
]
s.step("Here is the table.", [{"action": "hide", "target": "q"}, {"action": "show", "target": "qt"}])
for i, (say, a, b) in enumerate(qa):
    s.step(say, [{"action": "highlight", "target": f"qt[{i}]"}, setc("qt", i, 1, a, 0.3), setc("qt", i, 2, b, 0.6)])
s.step("Totals. Write-back: 2 hits, 4 block reads, 2 block writes, and line 1, holding B, ends dirty.", [setc("qt", 6, 1, "2 hits · 4 block reads · 2 block writes · B dirty")] + hl("qt[6]"))
s.step("Write-through: 1 hit, 2 block reads, 4 word writes, and nothing is ever dirty.", [setc("qt", 6, 2, "1 hit · 2 block reads · 4 word writes")] + hl("qt[6][2]"))
s.step("The usual slips: forgetting the write back of a dirty victim, and counting a no-write-allocate write as a block fetch.", [s.take("dirty victim → write back first · no-write-allocate → word to memory, no fetch")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qt"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("Writes must check the tag first, and they make the cache and memory disagree.", hl("stages[0]"))
s.step("Write-through keeps memory current, with a write buffer so the CPU need not wait. Write-back writes only the cache, and uses a dirty bit to write blocks back on eviction.", hl("stages[1..=3]"))
s.step("On a miss, allocate or write around; count the traffic and the dirty victims. Next video: the three kinds of cache misses.", [{"action": "mark", "target": "stages[0..=7]"}, s.take("Next: the three C's of cache misses")])

s.save("./m2v3.json")

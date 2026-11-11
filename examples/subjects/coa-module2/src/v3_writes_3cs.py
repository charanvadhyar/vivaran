"""Video 3: write policies (write-through / write-back, write-allocate / no-write-allocate) and the three C's."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

SEQ = [0, 4, 0, 4, 1, 1, 2, 3, 5, 0]


def classify(seq, lines=4):
    dm, fa, seen, out = [None] * lines, [], set(), []
    for b in seq:
        i = b % lines
        dmhit, fahit = dm[i] == b, b in fa
        if fahit:
            fa.remove(b)
        elif len(fa) == lines:
            fa.pop(0)
        fa.append(b)
        c = "hit" if dmhit else "compulsory" if b not in seen else "capacity" if not fahit else "conflict"
        out.append(dict(b=b, line=i, dmhit=dmhit, seen=b in seen, fahit=fahit, c=c, was=dm[i]))
        seen.add(b); dm[i] = b
    return out


C = classify(SEQ)
counts = {k: sum(o["c"] == k for o in C) for k in ("compulsory", "capacity", "conflict", "hit")}
assert counts == {"compulsory": 6, "capacity": 1, "conflict": 2, "hit": 1}

s = Script("Write policies and the three C's of cache misses")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why writes need their own rules"],
    [2, "Write hit: write-through or write-back"],
    [3, "Write miss: write-allocate or no-write-allocate"],
    [4, "One trace, two policy pairs: count the memory traffic"],
    [5, "The three C's: compulsory, capacity, conflict"],
    [6, "Classify every miss of a reference string"]]})
s.obj({"id": "hitpol", "type": "table", "region": "center", "columns": ["on a write hit", "cache", "memory", "extra hardware"], "rows": [
    ["write-through", "updated", "updated now, every write", "write buffer"],
    ["write-back", "updated", "updated only when the block is evicted", "dirty bit per line"]]})
s.obj({"id": "loop", "type": "math", "region": "bottom", "lines": [
    "\"10 writes to one block:\" quad \"write-through\" = 10 \"memory writes\" quad \"write-back\" = 1 \"block write, at eviction\""]})
s.obj({"id": "misspol", "type": "table", "region": "center", "columns": ["on a write miss", "what happens", "usual partner"], "rows": [
    ["write-allocate", "fetch the block into the cache, then write it there", "write-back"],
    ["no-write-allocate", "write straight to memory; the cache is not changed", "write-through"]]})
s.obj({"id": "traffic", "type": "table", "region": "center",
       "columns": ["#", "access", "write-back + write-allocate", "WB traffic", "write-through + no-write-allocate", "WT traffic"],
       "rows": [[1, "write X", "", "", "", ""], [2, "write X", "", "", "", ""], [3, "read X", "", "", "", ""],
                [4, "write Y", "", "", "", ""], [5, "read X", "", "", "", ""]]})
s.obj({"id": "tsum", "type": "table", "region": "center", "columns": ["policy pair", "block reads", "block writes", "single-word writes"], "rows": [
    ["write-back + write-allocate", "", "", ""], ["write-through + no-write-allocate", "", "", ""]]})
s.obj({"id": "threec", "type": "table", "region": "center", "columns": ["miss", "cause", "it would miss even in"], "rows": [
    ["compulsory", "the first reference to a block", "an infinite cache"],
    ["capacity", "the cache cannot hold every block the program is using", "a fully associative cache of the same size"],
    ["conflict", "too many blocks map to one set", "nothing: a fully associative cache would have hit"]]})
s.obj({"id": "test", "type": "diagram", "region": "right", "layout": "layers", "direction": "down", "nodes": [
    {"id": "m", "label": "a miss"},
    {"id": "q1", "label": "first use?"},
    {"id": "comp", "label": "compulsory", "shape": "pill"},
    {"id": "q2", "label": "FA LRU hit?"},
    {"id": "conf", "label": "conflict", "shape": "pill"},
    {"id": "cap", "label": "capacity", "shape": "pill"}],
    "edges": [{"from": "m", "to": "q1"}, {"from": "q1", "to": "comp", "label": "yes"}, {"from": "q1", "to": "q2", "label": "no"},
              {"from": "q2", "to": "conf", "label": "yes"}, {"from": "q2", "to": "cap", "label": "no"}]})
s.obj({"id": "cls", "type": "table", "region": "left", "columns": ["#", "block", "line", "direct-mapped", "seen?", "FA hits?", "class"],
       "rows": [[i + 1, o["b"], "", "", "", "", ""] for i, o in enumerate(C)]})
s.obj({"id": "fix", "type": "table", "region": "center", "columns": ["miss", "reduced by", "but it costs"], "rows": [
    ["compulsory", "larger blocks, prefetching", "a longer miss penalty; more conflict misses if blocks get too big"],
    ["capacity", "a larger cache", "a longer hit time, more power and area"],
    ["conflict", "higher associativity", "a longer hit time"]]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Two videos ago we placed and found blocks; last video we chose which one to evict.", [s.head("Writes, and the three C's of misses")])
s.step("This video answers question four, writes, and then sorts every miss into three kinds.", [s.take("Q4 write strategy · the three C's: compulsory, capacity, conflict")])
s.step("Here are the six stages.", [s.untake(), {"action": "show", "target": "stages"}])
s.step("Why writes are different, then what happens on a write hit, and on a write miss.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Then one trace, where we count every trip to memory under two policy pairs.", [{"action": "highlight", "target": "stages[3]"}])
s.step("Last, the three C's, with every miss of a reference string classified by hand.", [{"action": "highlight", "target": "stages[4..=5]"}])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: why do writes need their own rules?", [s.head("Stage 1 of 6: why writes are different"), {"action": "hide", "target": "stages"}])
s.step("On a read, the cache can read the data while it checks the tag, and simply ignore it on a miss.", [s.take("read: read data and check the tag at the same time")])
s.step("A write cannot do that: changing the block before the tag matches would destroy someone else's data.", [s.take("write: the tag must match before the block is changed")])
s.step("And a write makes the cache and memory disagree, unless we decide when memory is updated.", [])
s.step("So there are two decisions: what to do on a write hit, and what to do on a write miss.", [s.take("two decisions: on a write hit · on a write miss")])

# ---------------------------------------------------------------- write hit
s.scene("write-hit")
s.step("Stage 2: on a write hit, the block is in the cache. When does memory get the new value?", [s.head("Stage 2 of 6: on a write hit"), s.untake(), {"action": "show", "target": "hitpol"}])
s.step("Write-through updates the cache and memory on every write.", [{"action": "highlight", "target": "hitpol[0]"}])
s.step("Memory is always up to date, which makes the design simple.", [{"action": "highlight", "target": "hitpol[0][2]"}])
s.step("But every write now waits for slow memory, so a write buffer holds writes while the processor carries on.", [{"action": "highlight", "target": "hitpol[0][3]"}])
s.step("Write-back updates only the cache, and writes the whole block to memory when it is evicted.", [{"action": "highlight", "target": "hitpol[1]"}])
s.step("Each line gets a dirty bit, set on a write, so only changed blocks are written back.", [{"action": "highlight", "target": "hitpol[1][3]"}])
s.step("A clean block, one that was only read, is simply dropped when evicted.", [{"action": "highlight", "target": "hitpol[1][2]"}])
s.step("Example: a loop writes the same block 10 times before it is evicted.", [{"action": "show", "target": "loop"}])
s.step("Write-through makes 10 memory writes; write-back makes just 1 block write, at eviction.", [{"action": "highlight", "target": "loop[0]"}])
s.step("So write-back saves memory bandwidth when a block is written many times.", [{"action": "mark", "target": "hitpol[1]"}])

# ---------------------------------------------------------------- write miss
s.scene("write-miss")
s.step("Stage 3: on a write miss, the block is not in the cache. Do we bring it in?", [s.head("Stage 3 of 6: on a write miss"), {"action": "hide", "target": "hitpol"}, {"action": "hide", "target": "loop"}, {"action": "show", "target": "misspol"}])
s.step("Write-allocate fetches the block into the cache first, then writes it there, like a read miss followed by a write hit.", [{"action": "highlight", "target": "misspol[0]"}])
s.step("No-write-allocate writes straight to memory and leaves the cache unchanged.", [{"action": "highlight", "target": "misspol[1]"}])
s.step("Any pairing is possible, but two are usual.", [{"action": "highlight", "target": "misspol.c2"}])
s.step("Write-back goes with write-allocate, hoping later writes to the block will hit in the cache.", [{"action": "highlight", "target": "misspol[0][2]"}])
s.step("Write-through goes with no-write-allocate, since every write goes to memory anyway.", [{"action": "highlight", "target": "misspol[1][2]"}])

# ---------------------------------------------------------------- traffic
s.scene("traffic")
s.step("Stage 4: one trace, both pairs. X and Y are blocks that map to the same line of a direct-mapped cache.", [s.head("Stage 4 of 6: counting memory traffic"), {"action": "hide", "target": "misspol"}, {"action": "show", "target": "traffic"}])
s.step("The cache starts empty, and we count every block read, block write and single-word write to memory.", [{"action": "highlight", "target": "traffic.access"}])
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
    s.step(wb_say, [{"action": "highlight", "target": f"traffic[{i}]"},
                    {"action": "set", "target": f"traffic[{i}][2]", "value": wb},
                    {"action": "set", "target": f"traffic[{i}][3]", "value": wbt, "delay": 0.5}])
    s.step(wt_say, [{"action": "set", "target": f"traffic[{i}][4]", "value": wt},
                    {"action": "set", "target": f"traffic[{i}][5]", "value": wtt, "delay": 0.5}])
s.step("Now add up each column.", [{"action": "show", "target": "tsum"}])
s.step("Write-back: block reads at accesses 1, 4 and 5 make 3; block writes at 4 and 5 make 2; no single-word writes.",
       [{"action": "highlight", "target": "traffic.c3"}, {"action": "set", "target": "tsum[0][1]", "value": "3"},
        {"action": "set", "target": "tsum[0][2]", "value": "2", "delay": 0.4}, {"action": "set", "target": "tsum[0][3]", "value": "0", "delay": 0.7}])
s.step("Write-through: one block read, at access 3, and single-word writes at 1, 2 and 4, so 3.",
       [{"action": "highlight", "target": "traffic.c5"}, {"action": "set", "target": "tsum[1][1]", "value": "1"},
        {"action": "set", "target": "tsum[1][2]", "value": "0", "delay": 0.4}, {"action": "set", "target": "tsum[1][3]", "value": "3", "delay": 0.7}])
s.step("Check with hits: write-back hit at accesses 2 and 3; write-through hit only at access 5.", [{"action": "highlight", "target": "traffic.c2"}, {"action": "highlight", "target": "traffic.c4", "delay": 0.5}])
s.step("Neither always wins: write-back moves whole blocks, write-through moves many small words.", [{"action": "mark", "target": "tsum"}])
s.step("Remember this for AMAT: with no-write-allocate, a write miss costs a memory write, not a block fetch.", [])

# ---------------------------------------------------------------- 3 Cs
s.scene("three-cs")
s.step("Stage 5: every miss has a cause, and there are three kinds, the three C's.", [s.head("Stage 5 of 6: the three C's"), {"action": "hide", "target": "traffic"}, {"action": "hide", "target": "tsum"}, {"action": "show", "target": "threec"}])
s.step("Compulsory misses happen on the very first reference to a block; it has never been in the cache.", [{"action": "highlight", "target": "threec[0]"}])
s.step("Even an infinite cache would take these misses.", [{"action": "highlight", "target": "threec[0][2]"}])
s.step("Capacity misses happen when the program uses more blocks than the cache can hold.", [{"action": "highlight", "target": "threec[1]"}])
s.step("The test: even a fully associative cache of the same size would miss.", [{"action": "highlight", "target": "threec[1][2]"}])
s.step("Conflict misses happen when too many blocks map to one set, although other lines are free.", [{"action": "highlight", "target": "threec[2]"}])
s.step("A fully associative cache of the same size would have hit, so the mapping is to blame.", [{"action": "highlight", "target": "threec[2][2]"}])

# ---------------------------------------------------------------- classify
s.scene("classify")
s.step("Stage 6: classify every miss of a real trace. The procedure has two questions.", [s.head("Stage 6 of 6: classifying misses"), {"action": "hide", "target": "threec"}, {"action": "show", "target": "test"}])
s.step("First: is this the first time the block is used? If yes, it is compulsory.", [{"action": "highlight", "target": "test.q1"}, {"action": "highlight", "target": "test.comp", "delay": 0.5}])
s.step("If not: would a fully associative LRU cache of the same size have hit?", [{"action": "highlight", "target": "test.q2"}])
s.step("If it would, the miss is conflict; if it would not, the miss is capacity.", [{"action": "highlight", "target": "test.conf"}, {"action": "highlight", "target": "test.cap", "delay": 0.5}])
s.step("Our cache: direct-mapped, 4 lines, so block b goes to line b mod 4.", [{"action": "show", "target": "cls"}, s.take("direct-mapped, 4 lines · line = block mod 4 · shadow: fully associative LRU, 4 lines")])
s.step("Beside it we keep a shadow: a fully associative LRU cache, also 4 lines.", [{"action": "highlight", "target": "cls.c5"}])
s.step("The blocks referenced are 0, 4, 0, 4, 1, 1, 2, 3, 5, 0.", [{"action": "highlight", "target": "cls.block"}])

say = {
    0: "Block 0 goes to line 0; never seen before, so a compulsory miss.",
    1: "Block 4: 4 mod 4 is 0, line 0 again, and it is new: compulsory, and block 0 is thrown out.",
    2: "Block 0 again: line 0 holds 4, a miss. But we have seen 0, and the shadow still holds 0 and 4, so it would hit: conflict.",
    3: "Block 4: line 0 now holds 0, a miss; the shadow would hit again, so conflict.",
    4: "Block 1 goes to line 1, first use: compulsory.",
    5: "Block 1 again: line 1 holds 1, a hit.",
    6: "Block 2 goes to line 2, first use: compulsory.",
    7: "Block 3 goes to line 3, first use: compulsory. The shadow is now full: 4, 1, 2, 3.",
    8: "Block 5: 5 mod 4 is 1, so line 1, first use: compulsory, and block 1 is thrown out.",
    9: "Block 0: line 0 holds 4, a miss. We have seen 0, but the shadow evicted it to make room, so capacity.",
}
for i, o in enumerate(C):
    s.step(say[i], [{"action": "highlight", "target": f"cls[{i}]"},
                    {"action": "set", "target": f"cls[{i}][2]", "value": str(o["line"])},
                    {"action": "set", "target": f"cls[{i}][3]", "value": "hit" if o["dmhit"] else "miss", "delay": 0.2},
                    {"action": "set", "target": f"cls[{i}][4]", "value": "yes" if o["seen"] else "no", "delay": 0.4},
                    {"action": "set", "target": f"cls[{i}][5]", "value": ("yes" if o["fahit"] else "no") if o["seen"] and not o["dmhit"] else "–", "delay": 0.5},
                    {"action": "set", "target": f"cls[{i}][6]", "value": o["c"], "delay": 0.7}])
s.step("Count: 6 compulsory, 2 conflict, 1 capacity, and 1 hit.", [{"action": "mark", "target": "cls.class"}, s.take("6 compulsory · 2 conflict · 1 capacity · 1 hit")])
s.step("Check: 6 plus 2 plus 1 misses, plus 1 hit, gives all 10 references.", [])
s.step("Each kind of miss has its own cure, and its own cost.", [{"action": "hide", "target": "cls"}, {"action": "hide", "target": "test"}, s.untake(), {"action": "show", "target": "fix"}])
s.step("Larger blocks and prefetching cut compulsory misses, but each miss takes longer.", [{"action": "highlight", "target": "fix[0]"}])
s.step("A larger cache cuts capacity misses, but slows the hit and costs power.", [{"action": "highlight", "target": "fix[1]"}])
s.step("Higher associativity cuts conflict misses, but also slows the hit.", [{"action": "highlight", "target": "fix[2]"}])
s.step("These three ideas start the list of basic cache optimizations, two videos from now.", [{"action": "mark", "target": "fix"}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the six stages again.", [s.head("Recap"), {"action": "hide", "target": "fix"}, {"action": "show", "target": "stages"}])
s.step("A write must check the tag before it changes the block.", [{"action": "highlight", "target": "stages[0]"}])
s.step("On a hit: write-through updates memory every time; write-back waits for eviction and uses a dirty bit.", [{"action": "highlight", "target": "stages[1]"}])
s.step("On a miss: write-allocate fetches the block; no-write-allocate writes around the cache.", [{"action": "highlight", "target": "stages[2]"}])
s.step("Our trace: write-back moved 3 blocks in and 2 out; write-through, 1 block in and 3 words out.", [{"action": "highlight", "target": "stages[3]"}])
s.step("Compulsory: first use. Capacity: a fully associative cache would miss too. Conflict: it would hit.", [{"action": "highlight", "target": "stages[4..=5]"}])
s.step("Next video: putting numbers on all this, with average memory access time.", [{"action": "mark", "target": "stages[0..=5]"}, s.take("Next: AMAT and CPU time")])

s.save(sys.argv[1])

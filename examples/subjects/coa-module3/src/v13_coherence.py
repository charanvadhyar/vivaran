"""Module 3, video 13: shared-memory multiprocessors and the cache coherence problem."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

# exam bus counts
inv = ['A read miss', 'B read miss', 'A invalidates B', 'B read miss (A supplies 5)', 'C read miss']
upd = ['A read miss', 'B read miss', 'A broadcasts 5', 'C read miss']
assert (len(inv), len(upd)) == (5, 4)
assert (1 + 1, 5) == (2, 5) and round(0.8 * 100 + 0.2 * 300) == 140

s = Script("Shared memory and cache coherence")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Thread-level parallelism on shared memory"],
    [2, "Two organizations: UMA and NUMA"],
    [3, "Caching shared data"],
    [4, "The coherence problem, step by step"],
    [5, "What coherence means exactly"],
    [6, "Invalidate or update"],
    [7, "How it is enforced: snooping or directories"],
    [8, "Exam question"]]})
s.obj({"id": "tlp", "type": "table", "region": "center", "columns": ["idea", "meaning"], "rows": [
    ["thread-level parallelism", "threads with their own instruction streams, on separate cores"],
    ["shared memory", "one address space: communicate by loads and stores"],
    ["the catch", "each core caches its own copies of shared data"]]})
s.obj({"id": "uma", "type": "diagram", "region": "center", "layout": "layers", "direction": "down",
       "nodes": [{"id": "p1", "label": "core + caches"}, {"id": "p2", "label": "core + caches"}, {"id": "p3", "label": "core + caches"}, {"id": "p4", "label": "core + caches"},
                 {"id": "bus", "label": "bus"}, {"id": "mem", "label": "memory"}],
       "edges": [{"from": "p1", "to": "bus"}, {"from": "p2", "to": "bus"}, {"from": "p3", "to": "bus"}, {"from": "p4", "to": "bus"}, {"from": "bus", "to": "mem"}]})
s.obj({"id": "org", "type": "table", "region": "center", "columns": ["", "UMA: centralized shared memory (SMP)", "NUMA: distributed shared memory (DSM)"], "rows": [
    ["memory", "one memory, shared by all cores", "a slice of memory beside each node"],
    ["latency", "the same for every address", "local memory fast, remote memory slower"],
    ["scales to", "a few to a few dozen cores", "hundreds of cores"],
    ["example", "a typical single-socket multicore chip", "multi-socket servers"]]})
s.obj({"id": "numa", "type": "math", "region": "center", "lines": [
    "\"NUMA: 80% of misses local at 100 ns, 20% remote at 300 ns\"",
    "\"average\" = 0.8 times 100 + 0.2 times 300 = 140 \"ns\" quad \"so place data near the thread that uses it\""]})
s.obj({"id": "cache", "type": "table", "region": "center", "columns": ["data", "caching it"], "rows": [
    ["private: used by one thread", "no problem: exactly like a uniprocessor"],
    ["shared: used by several", "copies in several caches: faster, less traffic"],
    ["but", "if one core writes its copy, the others now hold a stale value"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["time", "event", "cache of A", "cache of B", "memory X"], "rows": [
    ["0", "start", "", "", "1"],
    ["1", "A reads X", "", "", "1"],
    ["2", "B reads X", "", "", "1"],
    ["3", "A writes 0 to X (write-through)", "", "", ""],
    ["4", "B reads X", "", "", ""]]})
s.obj({"id": "def", "type": "table", "region": "center", "columns": ["coherent if", "meaning"], "rows": [
    ["1 program order", "my read after my write returns my value"],
    ["2 writes become visible", "others eventually see my write"],
    ["3 write serialization", "everyone sees writes to X in one order"],
    ["not to confuse", "consistency: order across different addresses"]]})
s.obj({"id": "iv", "type": "table", "region": "center", "columns": ["time", "event", "cache of A", "cache of B", "memory X"], "rows": [
    ["1", "A reads X", "1", "", "1"],
    ["2", "B reads X", "1", "1", "1"],
    ["3", "A writes 0: invalidate the other copies", "0", "invalid", "0"],
    ["4", "B reads X: a miss", "0", "0", "0"]]})
s.obj({"id": "vs", "type": "table", "region": "center", "columns": ["", "write invalidate", "write update (broadcast)"], "rows": [
    ["on a write", "other copies are invalidated", "other copies get the new value"],
    ["A writes X 5 times, then B reads", "1 invalidation + 1 miss", "5 broadcasts"],
    ["writes to several words of a block", "one invalidation for the block", "one broadcast per word"],
    ["used by", "almost every modern multicore", "rarely"]]})
s.obj({"id": "how", "type": "table", "region": "center", "columns": ["scheme", "how", "scales to"], "rows": [
    ["snooping", "every cache watches a shared bus", "a few dozen cores"],
    ["directory", "a table lists each block's sharers", "hundreds of cores"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["step", "event (X = 7 at first; write-back caches)"], "rows": [
    ["1", "A reads X"], ["2", "B reads X"], ["3", "A writes 5 to X"], ["4", "B reads X"], ["5", "C reads X"]]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["find"], "rows": [
    ["a) what steps 4 and 5 return with no coherence"], ["b) what they return with write invalidate"], ["c) bus transactions: invalidate against update"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["", "no coherence", "write invalidate", "write update"], "rows": [
    ["step 4: B reads", "7 (its stale copy)", "5 (miss; A supplies it)", "5 (hit: updated)"],
    ["step 5: C reads", "7 (memory is stale)", "5", "5"],
    ["bus transactions", "–", "5: miss, miss, invalidate, miss, miss", "4: miss, miss, update, miss"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("One core finds only so much parallelism. Put several cores on one chip, let them share memory, and run a thread on each. But every core keeps its own cache, and that creates a problem every multicore must solve.", [s.head("Shared memory and cache coherence")])
s.step("Here are the eight stages.", show("stages"))
s.step("Thread-level parallelism, the two ways to organise shared memory, and caching shared data.", [hl("stages[0..=2]")])
s.step("Then the coherence problem step by step, its exact definition, the two fixes, how they are enforced, and an exam question.", [hl("stages[3..=7]")])

# ---------------------------------------------------------------- TLP
s.scene("tlp")
s.step("Stage 1: thread-level parallelism. Several threads, each with its own instruction stream, run on separate cores at the same time.", [s.head("Stage 1 of 8: shared-memory TLP")] + hide("stages") + show("tlp") + [hl("tlp[0]")])
s.step("In a shared-memory multiprocessor, every core sees one address space. Threads communicate simply by loading and storing the same addresses.", [hl("tlp[1]")])
s.step("The catch: each core has its own caches, and those caches hold their own copies of shared data.", [hl("tlp[2]"), s.take("one address space · many private caches")])

# ---------------------------------------------------------------- organizations
s.scene("org")
s.step("Stage 2: the simplest organisation. A few cores, each with its caches, share one memory through a bus or a switch.", [s.head("Stage 2 of 8: UMA and NUMA"), s.untake()] + hide("tlp") + show("uma") + [hl("uma.bus"), hl("uma.mem", 0.4)])
s.step("Every address takes the same time to reach from every core. That is uniform memory access, UMA, also called a symmetric multiprocessor, SMP.", hide("uma") + show("org") + [hl("org[0][1]"), hl("org[1][1]", 0.4)])
s.step("With many cores, one memory becomes a bottleneck. So memory is split up, with a slice beside each node. A core reaches its own slice quickly, and others' slices over a network, more slowly. Non-uniform memory access, NUMA, or distributed shared memory.", [hl("org[0][2]"), hl("org[1][2]", 0.4)])
s.step("UMA suits a few to a few dozen cores, like one multicore chip. NUMA scales to hundreds, like multi-socket servers. Either way, the programmer sees one shared memory.", [hl("org[2..=3]")])
s.step("On NUMA, where data lives matters. If 80 percent of a thread's misses go to its local memory at 100 nanoseconds, and 20 percent to a remote node at 300, the average is 140. Operating systems try to place each page near the thread that uses it.", hide("org") + show("numa") + [hl("numa[0]"), {"action": "reveal", "target": "numa[1]"}, hl("numa[1]", 0.5), s.take("UMA: one memory, equal latency · NUMA: memory per node")])

# ---------------------------------------------------------------- caching
s.scene("caching")
s.step("Stage 3: caches hold two kinds of data.", [s.head("Stage 3 of 8: caching shared data"), s.untake()] + hide("numa") + show("cache"))
s.step("Private data, used by one thread, is cached exactly as on a single core. No problem at all.", [hl("cache[0]")])
s.step("Shared data can be copied into several caches at once. That is good: each core reads its own copy quickly, without crowding the bus.", [hl("cache[1]")])
s.step("But when one core writes its copy, the other copies are suddenly out of date.", [hl("cache[2]"), s.take("replication speeds reads · and creates stale copies")])

# ---------------------------------------------------------------- the problem
s.scene("problem")
s.step("Stage 4: the problem, step by step. Two cores, A and B, with write-through caches. Memory location X holds 1.", [s.head("Stage 4 of 8: the coherence problem"), s.untake()] + hide("cache") + show("pb") + [hl("pb[0]")])
s.step("A reads X. A miss: its cache now holds 1.", [st("pb[1][2]", "1"), hl("pb[1]", 0.3)])
s.step("B reads X. Its cache also holds 1. Two copies, both correct.", [st("pb[2][2]", "1"), st("pb[2][3]", "1", 0.2), hl("pb[2]", 0.4)])
s.step("A writes 0 to X. Write-through updates A's cache and memory.", [st("pb[3][2]", "0"), st("pb[3][3]", "1", 0.2), st("pb[3][4]", "0", 0.4), hl("pb[3]", 0.5)])
s.step("But B's cache still says 1. Nothing told it.", [hl("pb[3][3]")])
s.step("B reads X again. A hit, in its own cache: it gets 1. The wrong value, even though memory and A both say 0.", [st("pb[4][2]", "0"), st("pb[4][3]", "1: stale!", 0.2), st("pb[4][4]", "0", 0.4), hl("pb[4][3]", 0.6)])
s.step("With write-back caches it is even worse: memory itself would still say 1.", [s.take("two caches, two values: the coherence problem")])

# ---------------------------------------------------------------- definition
s.scene("def")
s.step("Stage 5: what exactly must hold? A memory system is coherent if three things are true.", [s.head("Stage 5 of 8: what coherence means"), s.untake()] + hide("pb") + show("def"))
s.step("One: program order. A core that writes X, and later reads X, gets back its own value, as long as no one else wrote in between.", [hl("def[0]")])
s.step("Two: writes become visible. A write by one core is eventually seen by reads on the others, if the reads come long enough afterwards. Our example broke this rule.", [hl("def[1]")])
s.step("Three: write serialization. Two writes to the same location are seen by every core in the same order. Nobody may see 1 then 2, while someone else sees 2 then 1.", [hl("def[2]")])
s.step("Coherence is about one location. Consistency, a different question, is about when writes to different locations become visible relative to each other. That comes in a later video.", [hl("def[3]"), s.take("coherence: one address, one agreed history of writes")])

# ---------------------------------------------------------------- fixes
s.scene("fix")
s.step("Stage 6: the most common fix is write invalidate. Before a core writes, it makes sure it holds the only copy, by invalidating all the others.", [s.head("Stage 6 of 8: invalidate or update"), s.untake()] + hide("def") + show("iv") + [hl("iv[0..=1]")])
s.step("A writes 0. B's copy is invalidated.", [hl("iv[2]"), hl("iv[2][3]", 0.4)])
s.step("Now when B reads X, it misses, and fetches the current value, 0. Correct.", [hl("iv[3]")])
s.step("The alternative is write update, or broadcast: on every write, send the new value to every cache holding a copy.", hide("iv") + show("vs") + [hl("vs[0]")])
s.step("If A writes X five times before B reads it, invalidate costs one invalidation and one later miss. Update costs five broadcasts.", [hl("vs[1]")])
s.step("And writes to several words of the same block cost one invalidation, but one broadcast per word. Bus bandwidth is precious, so almost every multicore today invalidates.", [hl("vs[2..=3]"), s.take("write invalidate: only one writer holds a copy")])

# ---------------------------------------------------------------- how
s.scene("how")
s.step("Stage 7: who keeps track of the copies? Two answers.", [s.head("Stage 7 of 8: snooping or directories"), s.untake()] + hide("vs") + show("how"))
s.step("Snooping: every cache controller watches a shared bus, sees every other cache's misses and invalidations, and reacts. Simple, but every message reaches everyone, so it scales to a few dozen cores.", [hl("how[0]")])
s.step("Directories: a table records, for every block, which caches hold it. Messages go only to those caches. It scales to hundreds of cores. The next two videos cover each in detail.", [hl("how[1]"), s.take("snooping: broadcast · directory: point to point")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question. X starts at 7. The caches are write-back. A reads X, B reads X, A writes 5, then B reads X, then C reads X.", [s.head("Exam question"), s.untake()] + hide("how") + show("q"))
s.step("What do steps 4 and 5 return with no coherence, and with write invalidate? And how many bus transactions does invalidate need, against update? Pause and work it out.", hide("q") + show("qx") + [hl("qx")])
s.step("No coherence: B hits on its stale copy, 7. C misses, but memory is stale too, because A's 5 sits only in A's write-back cache. Also 7. Both wrong.", hide("qx") + show("qa") + [hl("qa[0][1]"), hl("qa[1][1]", 0.4)])
s.step("Write invalidate: A's write invalidates B's copy. B then misses, and A supplies the dirty block: 5. C misses and also gets 5.", [hl("qa[0][2]"), hl("qa[1][2]", 0.4)])
s.step("Transactions with invalidate: two read misses, one invalidation, then B's miss and C's miss. 5. With update: two misses, one broadcast of 5, which makes B's read a hit, then C's miss. 4.", [hl("qa[2]")])
s.step("So here update wins, by one. But had A written 5 times, update would send 5 broadcasts. The usual slip: forgetting that with write-back caches, memory itself goes stale.", [s.take("write-back caches: the newest value may live only in one cache")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Cores share one address space, in UMA or NUMA organisations, but cache private copies. One write can leave other copies stale.", [hl("stages[0..=3]")])
s.step("Coherence demands program order, visible writes and serialized writes. Write invalidate is the usual fix, enforced by snooping or by directories.", [hl("stages[4..=6]")])
s.step("Next video: snooping protocols, MSI and MESI, state by state.", [mk("stages[0..=7]"), s.take("Next: MSI and MESI snooping")])

s.save("/home/claude/playlist/m3/m3v13.json")

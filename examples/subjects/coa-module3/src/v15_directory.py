"""Module 3, video 15: directory-based cache coherence."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from dir import run

SEQ = [('P1', 'R'), ('P2', 'R'), ('P3', 'R'), ('P4', 'W'), ('P1', 'R'), ('P2', 'W')]
T = run(SEQ)
assert [len(x[4]) for x in T] == [2, 2, 2, 5, 4, 4] and sum(len(x[4]) for x in T) == 19
EX = [('P1', 'W'), ('P2', 'R'), ('P3', 'R'), ('P1', 'W'), ('P1', 'R'), ('P4', 'W')]
Q = run(EX)
assert [len(x[4]) for x in Q] == [2, 4, 2, 4, 0, 4] and sum(len(x[4]) for x in Q) == 16
# storage: full bit vector, 64-byte blocks = 512 data bits
assert 64 / 512 == 0.125 and 256 / 512 == 0.5 and 1024 / 512 == 2.0
assert 128 / 512 == 0.25 and 4 * 7 == 28 and round(28 / 512 * 100, 1) == 5.5
assert 2 ** 7 == 128 and 2 ** 6 == 64 and round(4 * 6 / 512 * 100, 1) == 4.7

op = lambda c, o: f"{c} {'reads' if o == 'R' else 'writes'} X"
dstate = lambda x: {'U': 'U', 'S': 'S', 'M': 'M'}[x[2]] + " {" + ",".join(x[3]) + "}"

s = Script("Directory-based coherence")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why snooping stops scaling"],
    [2, "The directory idea"],
    [3, "Where the directory lives: the home node"],
    [4, "Directory states and messages"],
    [5, "What the home node does"],
    [6, "A trace, message by message"],
    [7, "Storage overhead, and how to cut it"],
    [8, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["problem with snooping", "why"], "rows": [
    ["every miss is broadcast", "every cache must see every request"],
    ["one bus, one request at a time", "bandwidth does not grow with the core count"],
    ["every cache checks every request", "tag lookups grow with the core count too"],
    ["fine for a few cores", "8 to 16 cores, or one chip with a shared L3"],
    ["many sockets, many cores", "need point-to-point messages, sent only where needed"]]})
s.obj({"id": "idea", "type": "table", "region": "center", "columns": ["the directory", "keeps, for every memory block"], "rows": [
    ["state", "uncached, shared, or modified"],
    ["sharers", "a bit per processor: which caches hold a copy"],
    ["so on a write", "send invalidations only to the caches whose bit is set"],
    ["no broadcast", "any network will do: mesh, ring, crossbar"]]})
s.obj({"id": "dg", "type": "diagram", "region": "center", "layout": "layers", "direction": "down", "nodes": [
    {"id": "c1", "label": "P1 + cache"}, {"id": "c2", "label": "P2 + cache"}, {"id": "c3", "label": "P3 + cache"},
    {"id": "m1", "label": "mem + dir 1"}, {"id": "m2", "label": "mem + dir 2"}, {"id": "m3", "label": "mem + dir 3"},
    {"id": "net", "label": "network"}],
    "edges": [{"from": "c1", "to": "m1"}, {"from": "c2", "to": "m2"}, {"from": "c3", "to": "m3"},
              {"from": "m1", "to": "net"}, {"from": "m2", "to": "net"}, {"from": "m3", "to": "net"}]})
s.obj({"id": "nodes", "type": "table", "region": "center", "columns": ["node", "role"], "rows": [
    ["local node", "the one whose processor made the request"],
    ["home node", "the one whose memory, and directory, hold the block: fixed by the address"],
    ["remote node", "one that holds a copy: an owner or a sharer"]]})
s.obj({"id": "ds", "type": "table", "region": "center", "columns": ["directory state", "meaning"], "rows": [
    ["U: uncached", "no cache has it; memory is current"],
    ["S: shared", "one or more caches have a clean copy; memory is current"],
    ["M: modified", "exactly one cache, the owner, has written it; memory is stale"]]})
s.obj({"id": "msg", "type": "table", "region": "center", "columns": ["message", "from → to", "purpose"], "rows": [
    ["read miss, write miss", "local → home", "ask for the block"],
    ["data reply", "home → local", "send the block"],
    ["invalidate", "home → sharer", "drop your copy"],
    ["fetch", "home → owner", "send the block back; keep a shared copy"],
    ["fetch/invalidate", "home → owner", "send it back and drop it"],
    ["data write-back", "owner → home", "the dirty block returns to memory"]]})
s.obj({"id": "hp", "type": "table", "region": "center", "columns": ["state", "request", "home does", "new state", "messages"], "rows": [
    ["U", "read miss", "reply with data", "S {P}", "2"],
    ["U", "write miss", "reply with data", "M {P}", "2"],
    ["S", "read miss", "reply; add P to sharers", "S + P", "2"],
    ["S", "write miss", "invalidate each other sharer; reply", "M {P}", "2 + sharers"],
    ["M", "read miss", "fetch from owner; reply", "S {owner, P}", "4"],
    ["M", "write miss", "fetch/invalidate owner; reply", "M {P}", "4"]]})
s.obj({"id": "tt", "type": "table", "region": "center", "columns": ["step", "operation", "directory after", "messages", "count"], "rows": [
    [str(i + 1), op(c, o), "", "", ""] for i, (c, o) in enumerate(SEQ)]})
s.obj({"id": "ov", "type": "table", "region": "center", "columns": ["processors", "bits per 64-byte block", "overhead"], "rows": [
    ["64", "64", "64 / 512 = 12.5%"],
    ["256", "256", "50%"],
    ["1024", "1024", "200%: more than the data"]]})
s.obj({"id": "cut", "type": "table", "region": "center", "columns": ["way to cut it", "how"], "rows": [
    ["limited pointers", "keep i processor numbers of log₂P bits each, not P bits"],
    ["coarse vector", "one bit per group of processors; invalidate the whole group"],
    ["sparse directory", "track only blocks that are cached somewhere, like a cache of directory entries"]]})
s.obj({"id": "lp", "type": "table", "region": "center", "columns": ["64 processors, 64-byte blocks", "bits", "overhead"], "rows": [
    ["full bit vector", "64", "12.5%"],
    ["4 pointers × 6 bits", "24", "4.7%"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["step", "operation"], "rows": [
    [str(i + 1), op(c, o)] for i, (c, o) in enumerate(EX)] + [
    ["b", "128 processors, 64-byte blocks: overhead of a full bit vector, and of 4 pointers?"]]})
s.obj({"id": "qt", "type": "table", "region": "center", "columns": ["step", "operation", "directory after", "messages"], "rows": [
    [str(i + 1), op(c, o), dstate(Q[i]), str(len(Q[i][4]))] for i, (c, o) in enumerate(EX)] + [
    ["", "total", "", "16"]]})
s.obj({"id": "qb", "type": "table", "region": "center", "columns": ["128 processors, 64-byte blocks", "bits", "overhead"], "rows": [
    ["full bit vector", "128", "128 / 512 = 25%"],
    ["4 pointers × 7 bits", "28", "28 / 512 ≈ 5.5%"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]


def short(m):
    return m.replace(" read miss", " RdMiss").replace(" write miss", " WrMiss").replace(" data reply", " data") \
        .replace(" invalidate", " inv").replace(" fetch/invalidate", " fetch/inv").replace(" write-back", " WB") \
        .replace("H→", "H→").replace("/inv", "/inv")


def fill(i):
    x = T[i]
    return [st(f"tt[{i}][2]", dstate(x)), st(f"tt[{i}][3]", ", ".join(short(m) for m in x[4]) or "– hit", 0.3),
            st(f"tt[{i}][4]", str(len(x[4])), 0.6), hl(f"tt[{i}]")]


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Snooping works because every cache hears every request on one bus. That stops working once there are dozens of cores, or several sockets. This video shows the alternative used in large machines: a directory.", [s.head("Directory-based coherence")])
s.step("Here are the eight stages.", show("stages"))
s.step("Why snooping stops scaling, the directory idea, where it lives, and its states and messages.", [hl("stages[0..=3]")])
s.step("Then the protocol at the home node, a full trace counted message by message, the storage cost, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: what goes wrong with snooping? Every miss is broadcast, so every cache must see every request.", [s.head("Stage 1 of 8: why snooping stops scaling")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("A bus carries one request at a time. Add cores, and the traffic grows, but the bus does not.", [hl("why[1]")])
s.step("And every cache must look up its tags for every request, even though it almost never has the block.", [hl("why[2]")])
s.step("For a handful of cores, or one chip whose cores share an L3, that is fine.", [hl("why[3]")])
s.step("For many cores or many sockets, we want point-to-point messages, sent only to the caches that actually hold the block.", [hl("why[4]"), s.take("broadcast does not scale")])

# ---------------------------------------------------------------- idea
s.scene("idea")
s.step("Stage 2: the directory. For every block of memory it keeps two things.", [s.head("Stage 2 of 8: the directory idea"), s.untake()] + hide("why") + show("idea"))
s.step("A state: is the block uncached, shared, or modified?", [hl("idea[0]")])
s.step("And a set of sharers: one bit per processor, set if that processor's cache has a copy.", [hl("idea[1]")])
s.step("Now a write needs no broadcast. The directory knows exactly which caches to invalidate.", [hl("idea[2]")])
s.step("And because nothing is broadcast, the cores can be joined by any network: a mesh, a ring, a crossbar.", [hl("idea[3]"), s.take("the directory knows who has each block")])

# ---------------------------------------------------------------- home node
s.scene("home")
s.step("Stage 3: where does the directory live? One central directory would become the new bottleneck. So it is distributed along with memory.", [s.head("Stage 3 of 8: the home node"), s.untake()] + hide("idea") + show("dg"))
s.step("Each node has a processor and cache, a slice of main memory, and the directory entries for that slice.", [hl("dg.c1"), hl("dg.m1", 0.3)])
s.step("The nodes talk over an interconnection network, not a bus.", [hl("dg.net"), hl("dg.m1->net", 0.2), hl("dg.m2->net", 0.4), hl("dg.m3->net", 0.6)])
s.step("This gives three roles for every request.", hide("dg") + show("nodes"))
s.step("The local node: the one whose processor missed.", [hl("nodes[0]")])
s.step("The home node: the one whose memory holds the block. The address alone decides it, so everyone knows where to ask.", [hl("nodes[1]")])
s.step("And remote nodes: those whose caches hold a copy, as the owner or as sharers. Often a request touches all three.", [hl("nodes[2]"), s.take("ask the home node · it knows the sharers")])

# ---------------------------------------------------------------- states, messages
s.scene("states")
s.step("Stage 4: the directory states mirror the cache states, but describe the block across all caches.", [s.head("Stage 4 of 8: states and messages"), s.untake()] + hide("nodes") + show("ds"))
s.step("Uncached: no cache has it, and memory is current.", [hl("ds[0]")])
s.step("Shared: one or more caches have clean copies, and memory is still current.", [hl("ds[1]")])
s.step("Modified: exactly one cache, the owner, has written it. Memory is stale.", [hl("ds[2]")])
s.step("And these are the messages. The local node sends a read miss or a write miss to the home. The home answers with a data reply.", hide("ds") + show("msg") + [hl("msg[0..=1]")])
s.step("To take copies away, the home sends invalidate to a sharer.", [hl("msg[2]")])
s.step("To recover a dirty block, it sends the owner a fetch, or a fetch and invalidate. The owner answers with a data write-back.", [hl("msg[3..=5]"), s.take("request · reply · invalidate · fetch · write-back")])

# ---------------------------------------------------------------- protocol
s.scene("proto")
s.step("Stage 5: what the home node does for each request. Uncached is the easy case: read or write, it just replies with the data. Two messages.", [s.head("Stage 5 of 8: what the home does"), s.untake()] + hide("msg") + show("hp") + [hl("hp[0..=1]")])
s.step("Shared, and a read miss: reply, and add the new processor to the sharers. Still two.", [hl("hp[2]")])
s.step("Shared, and a write miss: invalidate every other sharer, reply, and the writer becomes the only owner. Two messages plus one per sharer invalidated.", [hl("hp[3]")])
s.step("Modified, and a read miss: memory is stale. Fetch the block from the owner, who writes it back, then reply. Four messages, and the block ends shared by both.", [hl("hp[4]")])
s.step("Modified, and a write miss: fetch and invalidate the owner, then reply. Four messages, and the writer is the new owner.", [hl("hp[5]")])
s.step("Real machines also send acknowledgements for invalidations, so the writer knows when it is safe. Our counts leave those out, as the textbook does.", [s.take("U: 2 · S read: 2 · S write: 2 + sharers · M: 4")])

# ---------------------------------------------------------------- trace
s.scene("trace")
s.step("Stage 6: a trace. Four processors, one block X, homed on a separate node. The directory starts uncached.", [s.head("Stage 6 of 8: a trace, message by message"), s.untake()] + hide("hp") + show("tt"))
s.step("1: P1 reads X. Uncached: a read miss, a data reply. Shared by P1. Two messages.", fill(0))
s.step("2 and 3: P2, then P3, read X. Each is a read miss and a reply, two messages, and joins the sharers.", fill(1) + [x for x in fill(2) if True])
s.step("4: P4 writes X. The block is shared by three caches. A write miss, three invalidations, a reply: five messages. P4 owns it.", fill(3))
s.step("5: P1 reads X. P4 holds it modified. Read miss, fetch to P4, write-back to home, reply to P1. Four messages. Now shared by P1 and P4.", fill(4))
s.step("6: P2 writes X. Two sharers to invalidate: write miss, two invalidations, reply. Four messages.", fill(5))
s.step("Nineteen messages in all, but every one went only where it was needed. A snooping bus would have sent every request to every cache.", [hl("tt[0..=5]"), s.take("19 messages, none broadcast")])

# ---------------------------------------------------------------- storage
s.scene("storage")
s.step("Stage 7: the cost. A full bit vector needs one bit per processor, for every memory block.", [s.head("Stage 7 of 8: storage overhead"), s.untake()] + hide("tt") + show("ov"))
s.step("With 64 processors and 64-byte blocks: 64 bits per 512 bits of data. Twelve and a half percent.", [hl("ov[0]")])
s.step("With 256 processors, fifty percent. With 1024, the directory is twice the size of memory. The full bit vector does not scale either.", [hl("ov[1]"), hl("ov[2]", 0.5)])
s.step("Three ways to cut it. Limited pointers: most blocks have only a few sharers, so store a few processor numbers instead of a bit for everyone.", hide("ov") + show("cut") + [hl("cut[0]")])
s.step("A coarse vector: one bit per group of processors. On a write, invalidate the whole group.", [hl("cut[1]")])
s.step("A sparse directory: keep entries only for blocks that are actually cached somewhere.", [hl("cut[2]")])
s.step("Limited pointers, worked out. 64 processors need 6 bits to name one. Four pointers: 24 bits, against 64. The overhead falls from 12.5 to 4.7 percent.", hide("cut") + show("lp") + [hl("lp[1]")])
s.step("If a fifth sharer arrives, the hardware must evict a sharer, or fall back to broadcast.", [s.take("overhead = P bits / block bits")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question. Four processors, one block X, homed elsewhere, starting uncached.", [s.head("Exam question"), s.untake()] + hide("lp") + show("q") + [hl("q[0..=5]")])
s.step("Give the directory state after every step and the messages each needs. Then part b: with 128 processors and 64-byte blocks, the overhead of a full bit vector, and of four pointers. Pause and work it out.", [hl("q[6]")])
s.step("1: P1 writes X. Uncached: write miss and reply, two messages. Modified, owned by P1.", hide("q") + show("qt") + [hl("qt[0]")])
s.step("2: P2 reads. P1 owns it: read miss, fetch, write-back, reply. Four. Shared by P1 and P2.", [hl("qt[1]")])
s.step("3: P3 reads: two messages, and joins the sharers.", [hl("qt[2]")])
s.step("4: P1 writes. It is a sharer, but must still ask the home, which invalidates P2 and P3. Four messages. P1 owns it again.", [hl("qt[3]")])
s.step("5: P1 reads its own modified block: a hit, no messages.", [hl("qt[4]")])
s.step("6: P4 writes. P1 owns it: write miss, fetch and invalidate, write-back, reply. Four. Total: sixteen messages.", [hl("qt[5]"), mk("qt[6]", 0.5)])
s.step("Part b. 128 processors: 128 bits per 512 bits of data, 25 percent.", hide("qt") + show("qb") + [hl("qb[0]")])
s.step("Four pointers of 7 bits each, since 2 to the 7 is 128: 28 bits, about 5.5 percent.", [hl("qb[1]")])
s.step("The usual slip: counting a hit as messages, or forgetting the write-back from the owner. A modified block always costs four.", [s.take("M block: miss, fetch, write-back, reply")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Broadcast does not scale. A directory, kept at each block's home node, records the state and the sharers, so messages go only where needed.", [hl("stages[0..=3]")])
s.step("The home replies, invalidates sharers, or fetches from the owner. A full bit vector costs P bits per block; pointers and coarse vectors cut that.", [hl("stages[4..=6]")])
s.step("Next video: memory consistency, and how to measure a multicore: speedup, efficiency, Amdahl and Gustafson.", [mk("stages[0..=7]"), s.take("Next: consistency and multicore metrics")])

s.save("/home/claude/playlist/m3/m3v15.json")

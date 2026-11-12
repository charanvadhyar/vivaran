"""Module 3, video 14: snooping coherence protocols MSI and MESI, traced; false sharing."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from msi import run, bus_count

SEQ = [('P1', 'R'), ('P1', 'W'), ('P2', 'R'), ('P3', 'W'), ('P1', 'R'), ('P1', 'W')]
MS = run(SEQ); ME = run(SEQ, mesi=True)
assert bus_count(MS) == 6 and bus_count(ME) == 5
assert [''.join(x[2][k] for k in ('P1', 'P2', 'P3')) for x in MS] == ['SII', 'MII', 'SSI', 'IIM', 'SIS', 'MII']
assert [''.join(x[2][k] for k in ('P1', 'P2', 'P3')) for x in ME] == ['EII', 'MII', 'SSI', 'IIM', 'SIS', 'MII']
EX = [('P1', 'R'), ('P1', 'W'), ('P2', 'R'), ('P2', 'W'), ('P3', 'R'), ('P1', 'W'), ('P3', 'R'), ('P3', 'W')]
QS = run(EX); QE = run(EX, mesi=True)
assert bus_count(QS) == 8 and bus_count(QE) == 7
assert 1000 * 2 == 2000

op = lambda c, o: f"{c} {'reads' if o == 'R' else 'writes'} X"
s = Script("Snooping protocols: MSI and MESI")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Snooping: every cache listens"],
    [2, "The MSI states"],
    [3, "MSI transitions"],
    [4, "An MSI trace, step by step"],
    [5, "MESI: the exclusive state"],
    [6, "The same trace with MESI"],
    [7, "False sharing"],
    [8, "Exam question"]]})
s.obj({"id": "snoop", "type": "table", "region": "center", "columns": ["snooping", "meaning"], "rows": [
    ["a shared bus", "every miss, upgrade and write-back is broadcast"],
    ["each cache controller", "watches the bus and checks its own tags for that block"],
    ["write invalidate", "before writing, a cache gets the only copy"],
    ["per block, per cache", "a small state machine: 2 bits beside the tag"]]})
s.obj({"id": "states", "type": "table", "region": "center", "columns": ["state", "means", "memory"], "rows": [
    ["M: modified", "only this cache has it, and has written it", "stale: this cache must supply it"],
    ["S: shared", "this cache, and maybe others, have a clean copy", "up to date"],
    ["I: invalid", "no valid copy here", "–"]]})
s.obj({"id": "tr", "type": "table", "region": "center", "columns": ["state", "event", "next", "bus action"], "rows": [
    ["I", "my read", "S", "BusRd: fetch the block"],
    ["I", "my write", "M", "BusRdX: fetch and invalidate the others"],
    ["S", "my write", "M", "BusUpgr: invalidate the others"],
    ["S", "another's BusRdX or BusUpgr", "I", "–"],
    ["M", "another's BusRd", "S", "write the block back, supply it"],
    ["M", "another's BusRdX", "I", "write the block back, supply it"],
    ["S, M", "my read · M: my write", "same", "– : a hit"]]})
s.obj({"id": "tt", "type": "table", "region": "center", "columns": ["step", "operation", "P1", "P2", "P3", "bus", "data from"], "rows": [
    [str(i + 1), op(c, o), "", "", "", "", ""] for i, (c, o) in enumerate(SEQ)]})
s.obj({"id": "ex", "type": "table", "region": "center", "columns": ["state", "means"], "rows": [
    ["E: exclusive", "only this cache has it, and it is clean (matches memory)"],
    ["I + my read, nobody else has it", "go to E, not S"],
    ["E + my write", "go to M silently: no bus transaction"],
    ["E + another's BusRd", "go to S"],
    ["why", "private data, read then written, never touches the bus twice"]]})
s.obj({"id": "fs", "type": "code", "region": "center", "language": "c", "lines": [
    "struct { long a; long b; } c;   // a and b share one 64-byte block",
    "// thread 1: for (i = 0; i < 1000; i++) c.a++;",
    "// thread 2: for (i = 0; i < 1000; i++) c.b++;"]})
s.obj({"id": "fsx", "type": "table", "region": "center", "columns": ["false sharing", "meaning"], "rows": [
    ["no word is shared", "thread 1 touches only a, thread 2 only b"],
    ["but the block is", "every write invalidates the other core's copy"],
    ["cost", "up to 2000 coherence misses: the block ping-pongs"],
    ["fix", "pad or align, so that a and b sit in different blocks"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["step", "operation"], "rows": [
    [str(i + 1), op(c, o)] for i, (c, o) in enumerate(EX)]})
s.obj({"id": "qt", "type": "table", "region": "center", "columns": ["step", "operation", "MSI states", "MSI bus", "MESI states", "MESI bus"], "rows": [
    [str(i + 1), op(c, o), ' '.join(QS[i][2][k] for k in ('P1', 'P2', 'P3')), QS[i][3],
     ' '.join(QE[i][2][k] for k in ('P1', 'P2', 'P3')), QE[i][3]] for i, (c, o) in enumerate(EX)]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]


def fill(res, i, d=0.0):
    c, o, stt, bus, src = res[i]
    out = [st(f"tt[{i}][{k + 2}]", stt[p], round(d + 0.1 * k, 2)) for k, p in enumerate(('P1', 'P2', 'P3'))]
    out += [st(f"tt[{i}][5]", bus, round(d + 0.4, 2)), st(f"tt[{i}][6]", src or "–", round(d + 0.5, 2))]
    return out


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Write invalidate needs every cache to know when another wants to write. On a bus, the simplest way is to listen. This video traces the two classic snooping protocols, MSI and MESI, state by state.", [s.head("Snooping protocols: MSI and MESI")])
s.step("Here are the eight stages.", show("stages"))
s.step("Snooping, the MSI states and transitions, and a trace.", [hl("stages[0..=3]")])
s.step("Then MESI's extra state, the same trace again, false sharing, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- snooping
s.scene("snoop")
s.step("Stage 1: every cache sits on a shared bus. Every miss, every upgrade, every write-back goes out on it, and every cache sees it.", [s.head("Stage 1 of 8: snooping")] + hide("stages") + show("snoop") + [hl("snoop[0]")])
s.step("Each cache controller watches, or snoops, the bus, and checks its own tags for the block being requested.", [hl("snoop[1]")])
s.step("With write invalidate, a cache must hold the only copy before it writes.", [hl("snoop[2]")])
s.step("To know what to do, each cache keeps a small state for every block it holds: two bits next to the tag.", [hl("snoop[3]"), s.take("snoop the bus · keep a state per block")])

# ---------------------------------------------------------------- states
s.scene("states")
s.step("Stage 2: MSI has three states.", [s.head("Stage 2 of 8: the MSI states"), s.untake()] + hide("snoop") + show("states"))
s.step("Modified: this cache has the only copy, and has written it. Memory is stale, so if anyone else asks, this cache must supply the block.", [hl("states[0]")])
s.step("Shared: this cache has a clean copy, and others may too. Memory is up to date.", [hl("states[1]")])
s.step("Invalid: no usable copy here. A block that was never loaded counts as invalid too.", [hl("states[2]"), s.take("M: mine, dirty · S: clean, maybe shared · I: not here")])

# ---------------------------------------------------------------- transitions
s.scene("trans")
s.step("Stage 3: the transitions. First, the ones caused by this cache's own processor.", [s.head("Stage 3 of 8: MSI transitions"), s.untake()] + hide("states") + show("tr"))
s.step("Invalid, and my processor reads: put a BusRd on the bus, fetch the block, and go to Shared.", [hl("tr[0]")])
s.step("Invalid, and my processor writes: BusRdX, read exclusive. Fetch the block and invalidate everyone else's copy. Go to Modified.", [hl("tr[1]")])
s.step("Shared, and my processor writes: I already have the data, so just BusUpgr, an invalidation. Go to Modified.", [hl("tr[2]")])
s.step("Now the ones caused by other caches, seen on the bus. Shared, and someone else wants to write: go to Invalid.", [hl("tr[3]")])
s.step("Modified, and someone else reads: I have the only good copy. Write it back and supply it, and drop to Shared.", [hl("tr[4]")])
s.step("Modified, and someone else wants to write: write back, supply, and go to Invalid.", [hl("tr[5]")])
s.step("And reads in S or M, or writes in M, are simply hits. No bus traffic.", [hl("tr[6]"), s.take("reads need a copy · writes need the only copy")])

# ---------------------------------------------------------------- MSI trace
s.scene("msi")
s.step("Stage 4: a trace. Three cores, one block X, six operations. All caches start Invalid.", [s.head("Stage 4 of 8: an MSI trace"), s.untake()] + hide("tr") + show("tt"))
s.step("1: P1 reads X. A miss: BusRd, data from memory. P1 goes to Shared.", fill(MS, 0))
s.step("2: P1 writes X. It is in Shared, so it must invalidate the others: BusUpgr, even though nobody else has a copy. P1 goes to Modified.", fill(MS, 1))
s.step("3: P2 reads X. A miss: BusRd. P1 snoops it, holds the block Modified, so it writes back and supplies it. Both end Shared.", fill(MS, 2))
s.step("4: P3 writes X. A miss: BusRdX. P1 and P2 snoop it and invalidate. P3 is Modified. Memory is up to date from step 3, so it supplies the data.", fill(MS, 3))
s.step("5: P1 reads X again. A miss: P3 writes back and supplies it. P1 and P3 are Shared.", fill(MS, 4))
s.step("6: P1 writes X: BusUpgr. P3 is invalidated, and P1 is Modified.", fill(MS, 5))
s.step("Six operations, six bus transactions. And step 2 was a waste: P1 broadcast an invalidation when it was the only holder.", [hl("tt[1]"), s.take("MSI: 6 bus transactions")])

# ---------------------------------------------------------------- MESI
s.scene("mesi")
s.step("Stage 5: MESI fixes that waste with a fourth state, Exclusive.", [s.head("Stage 5 of 8: MESI"), s.untake()] + hide("tt") + show("ex") + [hl("ex[0]")])
s.step("Exclusive means: only this cache has the block, and it is clean.", [mk("ex[0]")])
s.step("When a read miss finds that no other cache has the block, the bus tells it so, and the block goes to Exclusive instead of Shared.", [hl("ex[1]")])
s.step("A write in Exclusive then goes to Modified silently. No bus transaction at all, because there is nobody to invalidate.", [hl("ex[2]")])
s.step("If another cache reads the block, Exclusive drops to Shared.", [hl("ex[3]")])
s.step("This matters because most data is private: one thread reads it, then writes it. MESI makes that cost one bus transaction instead of two.", [hl("ex[4]"), s.take("E: mine and clean · a write is silent")])

# ---------------------------------------------------------------- MESI trace
cur_reset = [st(f"tt[{i}][{k}]", "") for i in range(6) for k in range(2, 7)]
s.scene("mesitrace")
s.step("Stage 6: the same six operations, with MESI.", [s.head("Stage 6 of 8: the same trace with MESI"), s.untake()] + hide("ex") + show("tt") + cur_reset)
s.step("1: P1 reads X, and no one else has it. Exclusive.", fill(ME, 0))
s.step("2: P1 writes X. Exclusive to Modified, silently. No bus transaction.", fill(ME, 1))
s.step("From step 3 on, the trace is the same as MSI: the block is now shared between cores, and E never appears again.", [x for i in range(2, 6) for x in fill(ME, i, 0.0)])
s.step("Five bus transactions instead of six. Real protocols go further: AMD's MOESI adds an Owned state, letting a dirty block be shared without writing it back; Intel's MESIF adds Forward, choosing one sharer to answer requests.", [hl("tt[1]"), s.take("MESI: 5 bus transactions")])

# ---------------------------------------------------------------- false sharing
s.scene("false")
s.step("Stage 7: a trap. Two threads, two separate counters. Thread 1 increments a, thread 2 increments b. No data is shared.", [s.head("Stage 7 of 8: false sharing"), s.untake()] + hide("tt") + show("fs"))
s.step("But a and b sit in the same 64-byte block, and coherence works on blocks, not words.", hide("fs") + show("fsx") + [hl("fsx[0..=1]")])
s.step("Every write by thread 1 invalidates thread 2's copy, and the other way round. The block bounces between the caches: up to 2000 coherence misses for 2000 increments.", [hl("fsx[2]")])
s.step("The fix is to pad or align the data so that a and b live in different blocks. The program does not change; it just runs many times faster.", [hl("fsx[3]"), s.take("false sharing: different words, same block")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question. Three cores, one block, eight operations. All caches start Invalid.", [s.head("Exam question"), s.untake()] + hide("fsx") + show("q"))
s.step("Give each cache's state after every step, and the bus transactions, under MSI and under MESI. Pause and work it out.", [hl("q")])
s.step("Steps 1 and 2: under MSI, P1 reads, goes Shared, then needs a BusUpgr to write. Under MESI, P1 goes Exclusive, and the write is silent.", hide("q") + show("qt") + [hl("qt[0..=1]")])
s.step("Steps 3 and 4: P2 reads; P1 writes back and both are Shared. P2 writes: BusUpgr, P1 invalid.", [hl("qt[2..=3]")])
s.step("Steps 5 and 6: P3 reads; P2 supplies the block and both are Shared. Then P1 writes: it is Invalid, so BusRdX, and both others are invalidated.", [hl("qt[4..=5]")])
s.step("Steps 7 and 8: P3 reads; P1 writes back. P3 writes: BusUpgr. In total: MSI 8 bus transactions, MESI 7.", [hl("qt[6..=7]")])
s.step("The usual slip: giving a write in Shared a BusRdX. The cache already has the data; it only needs to invalidate the others.", [s.take("S + write: BusUpgr · I + write: BusRdX")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt") + show("stages"))
s.step("Every cache snoops the bus. MSI keeps each block Modified, Shared or Invalid: reads need a copy, writes need the only copy.", [hl("stages[0..=3]")])
s.step("MESI's Exclusive state makes private read-then-write data free. And false sharing reminds us that coherence works on whole blocks.", [hl("stages[4..=6]")])
s.step("Next video: directory-based coherence, for when a bus is not enough.", [mk("stages[0..=7]"), s.take("Next: directory-based coherence")])

s.save("/home/claude/playlist/m3/m3v14.json")

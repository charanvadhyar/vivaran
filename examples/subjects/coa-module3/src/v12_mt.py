"""Module 3, video 12: multithreading: coarse-grained, fine-grained, simultaneous (SMT)."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from mt import superscalar, coarse, fine, smt, used, grid

R = {'A': [2, 1, 0, 0, 0, 0, 3, 1], 'B': [1, 3, 2, 0, 1, 2, 1, 2], 'C': [3, 0, 1, 2, 2, 0, 2, 1]}
G = {f.__name__: grid(f(R)) for f in (superscalar, coarse, fine, smt)}
U = {f.__name__: used(f(R)) for f in (superscalar, coarse, fine, smt)}
assert U == {'superscalar': 7, 'coarse': 9, 'fine': 14, 'smt': 26}
assert [round(100 * U[k] / 32) for k in ('superscalar', 'coarse', 'fine', 'smt')] == [22, 28, 44, 81]
RQ = {'A': [3, 0, 0, 0, 2, 1], 'B': [1, 2, 0, 3, 1, 2]}
UQ = {'superscalar': used(superscalar(RQ)), 'coarse': used(coarse(RQ, 4, 'AB')), 'fine': used(fine(RQ, 4, 'AB')), 'smt': used(smt(RQ, 4, 'AB'))}
assert UQ == {'superscalar': 6, 'coarse': 9, 'fine': 12, 'smt': 15}
assert round(20 / 120 * 100) == 17 and [round(min(1, n * 20 / 120) * 100) for n in (2, 4, 6)] == [33, 67, 100] and 1 + 100 // 20 == 6
assert [UQ[k] / 24 for k in ('superscalar', 'coarse', 'fine', 'smt')] == [0.25, 0.375, 0.5, 0.625]

s = Script("Multithreading")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Wasted issue slots"],
    [2, "Three threads, eight cycles"],
    [3, "One thread on a superscalar"],
    [4, "Coarse-grained multithreading"],
    [5, "Fine-grained multithreading"],
    [6, "Simultaneous multithreading"],
    [7, "How many threads hide a miss"],
    [8, "What each needs, and where it is used"],
    [9, "Exam question"]]})
s.obj({"id": "waste", "type": "table", "region": "center", "columns": ["waste", "meaning", "cause"], "rows": [
    ["vertical", "a whole cycle issues nothing", "a long stall: a cache miss"],
    ["horizontal", "a cycle issues fewer than its width", "too little ILP in this cycle"],
    ["the idea", "fill the slots from other threads", "threads are independent: no dependences between them"]]})
s.obj({"id": "rd", "type": "table", "region": "center", "columns": ["cycle", "1", "2", "3", "4", "5", "6", "7", "8"], "rows": [
    ["thread A ready", *map(str, R['A'])], ["thread B ready", *map(str, R['B'])], ["thread C ready", *map(str, R['C'])]]})
s.obj({"id": "sl", "type": "table", "region": "center", "columns": ["cycle", "slot 1", "slot 2", "slot 3", "slot 4"], "rows": [
    [str(c + 1), "", "", "", ""] for c in range(8)]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["scheme", "slots used of 32", "utilisation", "single-thread speed"], "rows": [
    ["superscalar, one thread", "7", "22%", "best"],
    ["coarse-grained", "9", "28%", "almost unchanged"],
    ["fine-grained", "14", "44%", "slower: shares every cycle"],
    ["simultaneous (SMT)", "26", "81%", "slightly slower"]]})
s.obj({"id": "hm", "type": "math", "region": "center", "lines": [
    "\"each thread: 20 cycles of work, then a 100-cycle miss\"",
    "\"one thread:\" quad 20 / (20 + 100) approx 17% \"busy\"",
    "N \"threads:\" quad \"busy\" = min(1, N times 20 / 120) quad N = 2 : 33% quad N = 4 : 67%",
    "\"fully busy when\" quad N >= 1 + 100 / 20 = 6 \"threads\""]})
s.obj({"id": "need", "type": "table", "region": "center", "columns": ["scheme", "per thread", "used in"], "rows": [
    ["coarse-grained", "PC, registers", "IBM AS/400 processors"],
    ["fine-grained", "PC, registers", "Sun Niagara: 8 cores × 4 threads · GPUs"],
    ["SMT", "PC, rename map, return stack, commit", "Intel Hyper-Threading: 2 · IBM POWER: up to 8"],
    ["shared", "units, stations, caches, predictors", "so threads also compete"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["cycle", "1", "2", "3", "4", "5", "6"], "rows": [
    ["thread A ready", *map(str, RQ['A'])], ["thread B ready", *map(str, RQ['B'])]]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["4-wide core, 6 cycles, 24 slots. Find the slots used by:"], "rows": [
    ["a) thread A alone"], ["b) coarse-grained (switch on a stall of 2+ cycles, losing 1 cycle)"], ["c) fine-grained (alternate A, B; skip a stalled thread)"], ["d) SMT (A first, then B)"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["scheme", "cycle by cycle", "slots", "utilisation"], "rows": [
    ["A alone", "AAA · – · – · – · AA · A", "6", "25%"],
    ["coarse", "AAA · switch · – · BBB · B · BB", "9", "37.5%"],
    ["fine", "AAA · BB · – · BBB · AA · BB", "12", "50%"],
    ["SMT", "AAAB · BB · – · BBB · AAB · ABB", "15", "62.5%"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
cur = [[''] * 4 for _ in range(8)]


def paint(name, cycles=range(8), d0=0.0):
    out = []
    for i, c in enumerate(cycles):
        for k in range(4):
            v = G[name][c][k]
            if v != cur[c][k]:
                out.append(st(f"sl[{c}][{k + 1}]", v, round(min(0.9, d0 + 0.1 * i), 2)))
                cur[c][k] = v
    return out


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("The limits video ended with a 4-wide core sustaining under 2 instructions per cycle. Half its issue slots go empty. Multithreading fills them with work from other threads.", [s.head("Multithreading")])
s.step("Here are the nine stages.", show("stages"))
s.step("Wasted slots, an example with three threads, and one thread alone.", [hl("stages[0..=2]")])
s.step("Then coarse-grained, fine-grained and simultaneous multithreading, how many threads it takes, what each needs, and an exam question.", [hl("stages[3..=8]")])

# ---------------------------------------------------------------- waste
s.scene("waste")
s.step("Stage 1: two kinds of waste. Vertical waste: a whole cycle where nothing issues, usually because of a long stall like a cache miss.", [s.head("Stage 1 of 9: wasted slots")] + hide("stages") + show("waste") + [hl("waste[0]")])
s.step("Horizontal waste: a cycle that issues fewer instructions than the machine's width, because this thread has too little parallelism right now.", [hl("waste[1]")])
s.step("Other threads, separate programs or separate parts of one program, are independent of this one. Their instructions can fill those slots with no dependence checks between threads.", [hl("waste[2]"), s.take("vertical waste: empty cycles · horizontal waste: empty slots")])

# ---------------------------------------------------------------- example
s.scene("example")
s.step("Stage 2: a 4-wide core, three threads, eight cycles. This table says how many instructions each thread could issue in each cycle.", [s.head("Stage 2 of 9: three threads"), s.untake()] + hide("waste") + show("rd"))
s.step("Thread A has a long stall, a cache miss, in cycles 3 to 6.", [hl("rd[0]")])
s.step("Threads B and C each have a short one-cycle stall here and there.", [hl("rd[1]"), hl("rd[2]", 0.5)])
s.step("Now we fill a grid of 8 cycles by 4 slots, 32 slots in all, under each scheme.", hide("rd") + show("sl"))

# ---------------------------------------------------------------- superscalar
s.scene("ss")
s.step("Stage 3: an ordinary superscalar runs only thread A.", [s.head("Stage 3 of 9: one thread")] + paint('superscalar'))
s.step("Cycles 1 and 2 are partly empty: horizontal waste. Cycles 3 to 6 are completely empty: the cache miss, vertical waste.", [hl("sl[0..=1]"), hl("sl[2..=5]", 0.5)])
s.step("7 slots used out of 32: 22 percent.", [s.take("one thread: 7 of 32 slots")])

# ---------------------------------------------------------------- coarse
s.scene("coarse")
s.step("Stage 4: coarse-grained multithreading. Run one thread until it hits a long stall, then switch to another.", [s.head("Stage 4 of 9: coarse-grained"), s.untake()] + paint('coarse'))
s.step("A runs cycles 1 and 2. In cycle 3 its miss is detected and the core switches to B. The switch empties the pipeline, so cycle 3 is lost.", [hl("sl[2]")])
s.step("In cycle 4, B has a one-cycle stall. Too short to switch for, so that cycle is lost too. Then B runs to the end.", [hl("sl[3]"), hl("sl[4..=7]", 0.4)])
s.step("9 of 32. It hides long stalls, and costs the running thread almost nothing. But it cannot fill short stalls or horizontal waste.", [s.take("coarse: switch on long stalls · 9 of 32")])

# ---------------------------------------------------------------- fine
s.scene("fine")
s.step("Stage 5: fine-grained multithreading. Switch threads every cycle, in turn, skipping any thread that is stalled.", [s.head("Stage 5 of 9: fine-grained"), s.untake()] + paint('fine'))
s.step("Cycle 1 goes to A, 2 to B, 3 to C. In cycle 4, A and B are stalled, so C goes again.", [hl("sl[0..=2]"), hl("sl[3]", 0.6)])
s.step("A's long miss costs nothing: the other threads simply take its turns.", [hl("sl[4..=6]")])
s.step("14 of 32. Both short and long stalls are hidden. But each cycle still holds one thread, so horizontal waste remains. And any single thread runs slower, because it gets only every third cycle.", [s.take("fine: a different thread each cycle · 14 of 32")])

# ---------------------------------------------------------------- SMT
s.scene("smt")
s.step("Stage 6: simultaneous multithreading, SMT. In every cycle, fill the slots from any threads that have instructions ready. Here A first, then B, then C.", [s.head("Stage 6 of 9: simultaneous multithreading"), s.untake()] + paint('smt'))
s.step("Cycle 1: A's two, B's one, and C fills the last slot. Cycle 2: A's one and three of B's.", [hl("sl[0]"), hl("sl[1]", 0.4)])
s.step("Even during A's miss, B and C share the slots.", [hl("sl[2..=5]")])
s.step("26 of 32, 81 percent. SMT attacks both vertical and horizontal waste. It works naturally on a dynamically scheduled core, because the renaming and stations already mix independent instructions.", [s.take("SMT: several threads in the same cycle · 26 of 32")])
s.step("Side by side: 7, 9, 14 and 26 slots. The price is shown in the last column: the more a scheme shares, the more each single thread slows down.", hide("sl") + show("cmp") + [hl("cmp[0..=3]")])

# ---------------------------------------------------------------- how many
s.scene("howmany")
s.step("Stage 7: how many threads does it take to hide a miss? Say each thread works for 20 cycles, then waits 100 cycles for memory.", [s.head("Stage 7 of 9: how many threads"), s.untake()] + hide("cmp") + show("hm") + [hl("hm[0]")])
s.step("Alone, a thread keeps the core busy 20 cycles out of every 120: about 17 percent.", [{"action": "reveal", "target": "hm[1]"}, hl("hm[1]")])
s.step("With N threads taking turns, the core is busy N times 20 out of 120 cycles, up to 100 percent. Two threads: 33 percent. Four: 67.", [{"action": "reveal", "target": "hm[2]"}, hl("hm[2]")])
s.step("It is fully busy once one thread's 100-cycle wait is covered by the others' work: 1 plus 100 over 20, 6 threads. This is why GPUs, which face long memory latencies, keep so many threads in flight.", [{"action": "reveal", "target": "hm[3]"}, hl("hm[3]"), s.take("threads needed ≈ 1 + latency ÷ work between misses")])

# ---------------------------------------------------------------- needs
s.scene("needs")
s.step("Stage 8: what each needs, and where it is used.", [s.head("Stage 8 of 9: hardware and examples"), s.untake()] + hide("hm") + show("need"))
s.step("Coarse-grained needs a separate program counter and register set per thread, and switches on a long stall. It appeared in IBM's AS/400 line.", [hl("need[0]")])
s.step("Fine-grained needs the same, but interleaves every cycle. Sun's Niagara ran 4 threads on each of 8 simple cores. GPUs push the idea to thousands of threads.", [hl("need[1]")])
s.step("SMT adds a separate rename map, return-address stack and commit per thread on top of an out-of-order core. Intel calls it Hyper-Threading, with 2 threads per core; IBM's POWER processors run up to 8.", [hl("need[2]")])
s.step("Everything else is shared: units, stations, caches, predictors. So threads also compete, and two memory-hungry threads can slow each other down.", [hl("need[3]"), s.take("SMT = an out-of-order core + per-thread state")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question. A 4-wide core, two threads, six cycles. The table shows how many instructions each could issue.", [s.head("Exam question"), s.untake()] + hide("need") + show("q"))
s.step("Count the slots used by A alone, by coarse-grained switching with a 1-cycle switch cost, by fine-grained alternation, and by SMT. Pause and work it out.", hide("q") + show("qx") + [hl("qx")])
s.step("A alone: 3, then three empty cycles, then 2 and 1. 6 of 24.", hide("qx") + show("qa") + [hl("qa[0]")])
s.step("Coarse: A runs cycle 1, stalls; the switch loses cycle 2. B is stalled in cycle 3, too briefly to switch again. Then B: 3, 1 and 2. 9 of 24.", [hl("qa[1]")])
s.step("Fine: A, then B's 2, nothing in cycle 3 when both stall, B's 3 when A is still stalled, then A's 2 and B's 2. 12.", [hl("qa[2]")])
s.step("SMT: 4, 2, 0, 3, 3, 3. 15 of 24, 62.5 percent.", [hl("qa[3]")])
s.step("The usual slip: giving fine-grained more than one thread per cycle. Only SMT mixes threads within one cycle.", [s.take("fine: one thread per cycle · SMT: several")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Coarse-grained hides long stalls; fine-grained hides every stall; SMT also fills the empty slots within a cycle.", [hl("stages[0..=5]")])
s.step("Enough threads hide even a long miss. SMT rides on the out-of-order machinery, adding a little state per thread, and the threads share everything else.", [hl("stages[6..=7]")])
s.step("Next video: shared-memory multiprocessors, and the cache coherence problem.", [mk("stages[0..=8]"), s.take("Next: shared memory and cache coherence")])

s.save("/home/claude/playlist/m3/m3v12.json")

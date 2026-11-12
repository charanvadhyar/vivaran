"""Module 3, video 16: memory consistency, and multicore metrics."""
import sys
from itertools import permutations
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script


# ---- consistency, checked by enumerating interleavings
def sc_outcomes(t1, t2):
    """t = list of ('W', var, val) or ('R', var, reg). All interleavings keeping program order."""
    res = set()
    n1, n2 = len(t1), len(t2)
    for order in set(permutations([1] * n1 + [2] * n2)):
        mem, regs, i, j = {}, {}, 0, 0
        for who in order:
            if who == 1:
                op = t1[i]; i += 1
            else:
                op = t2[j]; j += 1
            if op[0] == 'W':
                mem[op[1]] = op[2]
            else:
                regs[op[2]] = mem.get(op[1], 0)
        res.add(tuple(sorted(regs.items())))
    return res


def tso_outcomes(t1, t2):
    """Store buffers: a thread's write may become visible after its own later reads (W->R relaxed).
    Model: each thread may move a read ahead of an earlier write to a different variable."""
    def variants(t):
        out = {tuple(t)}
        for k in range(len(t) - 1):
            a, b = t[k], t[k + 1]
            if a[0] == 'W' and b[0] == 'R' and a[1] != b[1]:
                v = list(t); v[k], v[k + 1] = b, a; out.add(tuple(v))
        return out
    res = set()
    for a in variants(t1):
        for b in variants(t2):
            res |= sc_outcomes(list(a), list(b))
    return res


D1 = [('W', 'A', 1), ('R', 'B', 'r1')]
D2 = [('W', 'B', 1), ('R', 'A', 'r2')]
SC = {(dict(x)['r1'], dict(x)['r2']) for x in sc_outcomes(D1, D2)}
TSO = {(dict(x)['r1'], dict(x)['r2']) for x in tso_outcomes(D1, D2)}
assert SC == {(0, 1), (1, 0), (1, 1)} and TSO == SC | {(0, 0)}
M1 = [('W', 'data', 42), ('W', 'flag', 1)]
M2 = [('R', 'flag', 'f'), ('R', 'data', 'r')]
MSC = {(dict(x)['f'], dict(x)['r']) for x in sc_outcomes(M1, M2)}
assert (1, 0) not in MSC and (1, 42) in MSC
MTSO = {(dict(x)['f'], dict(x)['r']) for x in tso_outcomes(M1, M2)}
assert (1, 0) not in MTSO  # TSO keeps W->W and R->R order


# ---- metrics
def amdahl(f, p):
    return 1 / ((1 - f) + f / p)


def gus(f, p):
    return (1 - f) + f * p


assert 120 / 20 == 6 and 6 / 8 == 0.75
assert round(amdahl(0.9, 8), 2) == 4.71 and round(1 / 0.1) == 10
assert round(gus(0.9, 8), 1) == 7.3
ST = [(p, amdahl(0.95, p)) for p in (1, 2, 4, 8, 16)]
assert [round(x, 2) for _, x in ST] == [1.0, 1.9, 3.48, 5.93, 9.14]
assert [round(100 * x / p, 1) for p, x in ST] == [100.0, 95.2, 87.0, 74.1, 57.1]
assert round(amdahl(0.8, 16), 9) == 4.0 and round(amdahl(0.8, 16) / 16, 9) == 0.25 and round(1 / 0.2) == 5
assert round(gus(0.8, 16), 1) == 13.0
assert 200 / 40 == 5 and 5 / 16 == 0.3125
# weak scaling example: work per core fixed, 10 s on 1 core, 12.5 s on 64 cores
assert 10 / 12.5 == 0.8

s = Script("Consistency and multicore metrics")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Coherence is not consistency"],
    [2, "The test that tells them apart"],
    [3, "Sequential consistency"],
    [4, "Relaxed models and fences"],
    [5, "Speedup and efficiency"],
    [6, "Amdahl's law: strong scaling"],
    [7, "Gustafson's law: weak scaling"],
    [8, "Exam question"]]})
s.obj({"id": "cc", "type": "table", "region": "center", "columns": ["", "coherence", "consistency"], "rows": [
    ["about", "one memory location", "many locations"],
    ["question", "do all cores agree on the order of writes to X?", "in what order may a core see writes to X and to Y?"],
    ["provided by", "the cache protocol: MSI, MESI, a directory", "the memory model: hardware plus fences"]]})
s.obj({"id": "dk", "type": "code", "region": "center", "language": "c", "lines": [
    "// A = B = 0 at the start",
    "P1:  A = 1;   r1 = B;",
    "P2:  B = 1;   r2 = A;",
    "// can r1 and r2 both end up 0?"]})
s.obj({"id": "dko", "type": "table", "region": "center", "columns": ["order of events", "r1", "r2"], "rows": [
    ["P1 runs first", "0", "1"],
    ["P2 runs first", "1", "0"],
    ["both writes, then both reads", "1", "1"],
    ["with store buffers: each read overtakes its own write", "0", "0"]]})
s.obj({"id": "sc", "type": "table", "region": "center", "columns": ["sequential consistency (Lamport, 1979)", ""], "rows": [
    ["the result is as if", "all operations ran in some single order"],
    ["and in that order", "each core's operations appear in program order"],
    ["so for our test", "r1 = r2 = 0 is impossible: some write came first"],
    ["the cost", "a write must be visible everywhere before the next access: no store buffer, little overlap"]]})
s.obj({"id": "rl", "type": "table", "region": "center", "columns": ["model", "order it relaxes", "example"], "rows": [
    ["sequential consistency", "nothing", "the reference"],
    ["TSO: total store order", "a read may pass an earlier write", "x86, SPARC"],
    ["PSO: partial store order", "also write after write", "SPARC option"],
    ["weak / release consistency", "all four orders, except at synchronization", "ARM, POWER, RISC-V"]]})
s.obj({"id": "fn", "type": "table", "region": "center", "columns": ["the programmer's side", ""], "rows": [
    ["fence (barrier) instruction", "all accesses before it complete before any after it"],
    ["locks, atomics, OpenMP barriers", "contain the fences for you"],
    ["data-race-free programs", "behave as if the machine were SC"]]})
s.obj({"id": "sp", "type": "math", "region": "center", "lines": [
    "\"speedup\" quad S(p) = T_1 / T_p",
    "\"efficiency\" quad E(p) = S(p) / p",
    "T_1 = 120 \"s\", quad T_8 = 20 \"s\" quad => quad S = 6, quad E = 6 / 8 = 75%",
    "S(p) = p: \"linear\" quad quad S(p) > p: \"superlinear\" (\"more cache in total\")"]})
s.obj({"id": "am", "type": "math", "region": "center", "lines": [
    "f = \"parallel fraction,\" quad 1 - f = \"serial fraction\"",
    "S(p) = 1 / ((1 - f) + f / p)",
    "f = 0.9, p = 8: quad S = 1 / (0.1 + 0.1125) = 1 / 0.2125 approx 4.71",
    "p -> infinity: quad S -> 1 / (1 - f) = 1 / 0.1 = 10"]})
s.obj({"id": "stt", "type": "table", "region": "center", "columns": ["cores p", "speedup, f = 0.95", "efficiency"], "rows": [
    [str(p), f"{x:.2f}", f"{100 * x / p:.1f}%"] for p, x in ST]})
s.obj({"id": "gu", "type": "math", "region": "center", "lines": [
    "\"the problem grows with\" p; quad f = \"parallel share of the run on\" p \"cores\"",
    "S(p) = (1 - f) + f p",
    "f = 0.9, p = 8: quad S = 0.1 + 7.2 = 7.3",
    "\"weak-scaling efficiency\" = T_1 / T_p \"(same work per core):\" quad 10 / 12.5 = 80%"]})
s.obj({"id": "sw", "type": "table", "region": "center", "columns": ["", "strong scaling", "weak scaling"], "rows": [
    ["problem size", "fixed", "grows with p: same work per core"],
    ["law", "Amdahl", "Gustafson"],
    ["question", "how much faster is this job?", "how much bigger a job in the same time?"],
    ["ideal", "Tp = T1 / p", "Tp = T1"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "c", "lines": [
    "// a) data = flag = 0 at the start",
    "P1:  data = 42;   flag = 1;",
    "P2:  while (flag == 0) ;   r = data;",
    "// under SC, TSO and weak ordering: can r be 0?",
    "// b) 80% parallel, 16 cores: Amdahl speedup, efficiency, limit",
    "// c) the same, with Gustafson",
    "// d) T1 = 200 s, T16 = 40 s: speedup and efficiency"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["model", "can r be 0?", "why"], "rows": [
    ["SC", "no", "flag = 1 is seen only after data = 42"],
    ["TSO", "no", "writes stay in order, reads stay in order"],
    ["weak ordering", "yes", "the two writes, or the two reads, may be reordered"],
    ["fix", "a fence", "between the two writes, and between the two reads"]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"b)\" quad S = 1 / (0.2 + 0.8 / 16) = 1 / 0.25 = 4, quad E = 4 / 16 = 25%, quad \"limit\" 1 / 0.2 = 5",
    "\"c)\" quad S = 0.2 + 0.8 times 16 = 13",
    "\"d)\" quad S = 200 / 40 = 5, quad E = 5 / 16 approx 31%"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Coherence keeps every core's view of one location consistent. But programs share many locations, and the order in which writes to different locations become visible is a separate question.", [s.head("Consistency and multicore metrics")])
s.step("This video answers it, then turns to how we measure a multicore: speedup, efficiency, and the two laws that limit them.")
s.step("Here are the eight stages.", show("stages"))
s.step("First, memory consistency: how it differs from coherence, the test that tells them apart, sequential consistency, and relaxed models.", [hl("stages[0..=3]")])
s.step("Then the metrics: speedup and efficiency, Amdahl's law, Gustafson's law, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- coherence vs consistency
s.scene("cc")
s.step("Stage 1: two words that sound alike.", [s.head("Stage 1 of 8: coherence is not consistency")] + hide("stages") + show("cc"))
s.step("Coherence is about one location. Every core must agree on the order of the writes to X.", [hl("cc[0]"), hl("cc[1]", 0.4)])
s.step("Consistency is about many locations. If a core writes X and then Y, in what order may another core see them?", [hl("cc[1]")])
s.step("Coherence comes from the cache protocol. Consistency is the memory model: a contract between the hardware and the programmer.", [hl("cc[2]"), s.take("coherence: one address · consistency: the order across addresses")])

# ---------------------------------------------------------------- test
s.scene("test")
s.step("Stage 2: a two-line test. A and B start at 0. P1 sets A, then reads B. P2 sets B, then reads A.", [s.head("Stage 2 of 8: the test"), s.untake()] + hide("cc") + show("dk"))
s.step("Can both reads return 0? Think about the orders.", [{"action": "mark_lines", "target": "dk", "from": 4, "to": 4}])
s.step("If P1 runs first, r1 is 0 and r2 is 1.", hide("dk") + show("dko") + [hl("dko[0]")])
s.step("If P2 runs first, the reverse.", [hl("dko[1]")])
s.step("If both writes happen before both reads, both are 1. In every interleaving, some write comes first, so at least one read sees a 1.", [hl("dko[2]")])
s.step("But real processors put writes in a store buffer and let the next read go ahead. Each read then runs before its own core's write is visible, and both return 0. Coherence is not violated, yet the result is impossible in any interleaving.", [hl("dko[3]"), s.take("store buffers allow r1 = r2 = 0")])

# ---------------------------------------------------------------- SC
s.scene("sc")
s.step("Stage 3: the strictest model, sequential consistency, defined by Leslie Lamport in 1979.", [s.head("Stage 3 of 8: sequential consistency"), s.untake()] + hide("dko") + show("sc"))
s.step("The result must be as if all operations of all cores ran in some single order.", [hl("sc[0]")])
s.step("And in that order, each core's operations appear in its program order.", [hl("sc[1]")])
s.step("So in our test, both reads returning 0 is forbidden.", [hl("sc[2]")])
s.step("The price: a core cannot let a read pass an earlier write. Store buffers and much overlapping are lost, and performance suffers. So almost no processor implements strict sequential consistency.", [hl("sc[3]"), s.take("SC: one global order, program order kept")])

# ---------------------------------------------------------------- relaxed
s.scene("relaxed")
s.step("Stage 4: relaxed models. Each one relaxes some of the four orders: read then read, read then write, write then read, write then write.", [s.head("Stage 4 of 8: relaxed models and fences"), s.untake()] + hide("sc") + show("rl") + [hl("rl[0]")])
s.step("Total store order lets a read pass an earlier write: exactly the store buffer. This is the x86 model, and our r1 = r2 = 0 result is allowed.", [hl("rl[1]")])
s.step("Partial store order also lets writes pass each other.", [hl("rl[2]")])
s.step("Weak and release consistency relax all four orders, and restore them only at synchronization. This is ARM, POWER and RISC-V.", [hl("rl[3]")])
s.step("So how does a programmer get order back? With a fence: every access before it completes before any access after it.", hide("rl") + show("fn") + [hl("fn[0]")])
s.step("Locks, atomic operations and OpenMP barriers contain the right fences already.", [hl("fn[1]")])
s.step("And the key guarantee: if every shared access is ordered by synchronization, a data-race-free program, it behaves as if the machine were sequentially consistent.", [hl("fn[2]"), s.take("synchronize properly, and you see SC")])

# ---------------------------------------------------------------- speedup
s.scene("speedup")
s.step("Stage 5: now the metrics. Speedup on p cores is the time on one core divided by the time on p.", [s.head("Stage 5 of 8: speedup and efficiency"), s.untake()] + hide("fn") + show("sp") + [hl("sp[0]")])
s.step("Efficiency is speedup divided by p: how much of each core's time is useful.", [rv("sp[1]"), hl("sp[1]")])
s.step("A job takes 120 seconds on one core and 20 on eight. Speedup 6, efficiency 6 over 8, 75 percent.", [rv("sp[2]"), hl("sp[2]")])
s.step("Speedup equal to p is linear, the ideal. Occasionally it is superlinear, usually because eight cores bring eight times the cache, and the data suddenly fits.", [rv("sp[3]"), hl("sp[3]"), s.take("S = T1 / Tp · E = S / p")])

# ---------------------------------------------------------------- Amdahl
s.scene("amdahl")
s.step("Stage 6: Amdahl's law. Let f be the fraction of the one-core run that can be parallelised. One minus f stays serial.", [s.head("Stage 6 of 8: Amdahl's law"), s.untake()] + hide("sp") + show("am") + [hl("am[0]")])
s.step("On p cores, the serial part takes the same time, and the parallel part shrinks by p. Speedup is one over the sum.", [rv("am[1]"), hl("am[1]")])
s.step("With 90 percent parallel and 8 cores: 0.1 plus 0.9 over 8, which is 0.2125. Speedup about 4.71, not 8.", [rv("am[2]"), hl("am[2]")])
s.step("And with infinitely many cores, the parallel part vanishes, leaving one over the serial fraction. Ten percent serial caps the speedup at 10, forever.", [rv("am[3]"), hl("am[3]")])
s.step("This is strong scaling: a fixed problem on more cores. Here it is with 95 percent parallel.", hide("am") + show("stt"))
s.step("Two cores give 1.9, sixteen give only 9.14. And efficiency falls from 95 to 57 percent. Each doubling buys less.", [hl("stt[1]"), hl("stt[4]", 0.5), s.take("Amdahl: the serial part sets the ceiling")])

# ---------------------------------------------------------------- Gustafson
s.scene("gus")
s.step("Stage 7: Gustafson's objection. People do not buy more cores to run the same job faster. They run a bigger job in the same time.", [s.head("Stage 7 of 8: Gustafson's law"), s.untake()] + hide("stt") + show("gu") + [hl("gu[0]")])
s.step("So measure f on the p-core run. The serial part stays, and the parallel part would have taken p times longer on one core. Scaled speedup is one minus f, plus f times p.", [rv("gu[1]"), hl("gu[1]")])
s.step("With 90 percent and 8 cores: 0.1 plus 7.2, a speedup of 7.3. Far better than Amdahl's 4.71, because the question has changed.", [rv("gu[2]"), hl("gu[2]")])
s.step("This is weak scaling: same work per core. Ideally the time stays flat. If one core takes 10 seconds and 64 cores, with 64 times the work, take 12.5, weak-scaling efficiency is 80 percent.", [rv("gu[3]"), hl("gu[3]")])
s.step("Side by side: strong scaling fixes the problem and asks how much faster. Weak scaling grows the problem and asks how much bigger.", hide("gu") + show("sw") + [hl("sw[0..=2]")])
s.step("Ideal strong scaling divides the time by p. Ideal weak scaling keeps the time constant.", [hl("sw[3]"), s.take("strong: Amdahl, fixed size · weak: Gustafson, size grows")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question with four parts.", [s.head("Exam question"), s.untake()] + hide("sw") + show("q"))
s.step("Part a: P1 writes data, then sets a flag. P2 waits for the flag, then reads data. Under sequential consistency, TSO and weak ordering, can r be 0?", [{"action": "mark_lines", "target": "q", "from": 1, "to": 4}])
s.step("Part b: a program 80 percent parallel on 16 cores. Find the Amdahl speedup, efficiency and limit. Part c: the same with Gustafson. Part d: measured times, 200 seconds and 40. Pause and work it out.", [{"action": "mark_lines", "target": "q", "from": 5, "to": 7}])
s.step("Part a. Under SC, P2 sees flag equal to 1 only after data is 42. So r is 42.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Under TSO, writes stay in order and reads stay in order. Only a read passing a write is allowed, which does not apply here. r is still 42.", [hl("qa[1]")])
s.step("Under weak ordering, P1's writes may become visible out of order, or P2's reads may be reordered. r can be 0.", [hl("qa[2]")])
s.step("The fix: a fence between P1's two writes, and another between P2's two reads.", [hl("qa[3]")])
s.step("Part b: 0.2 plus 0.8 over 16 is 0.25. Speedup 4, efficiency 25 percent, and the limit is 1 over 0.2, which is 5.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("Part c: Gustafson gives 0.2 plus 0.8 times 16, which is 13.", [rv("qb[1]"), hl("qb[1]")])
s.step("Part d: speedup 200 over 40, which is 5, and efficiency 5 over 16, about 31 percent.", [rv("qb[2]"), hl("qb[2]")])
s.step("The usual slip: using Amdahl's f in Gustafson's formula. Amdahl's f is measured on one core, Gustafson's on p cores.", [s.take("say which f you are using")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Coherence is one address; consistency is the order across addresses. Sequential consistency is strict; real machines relax it, and fences and locks restore order.", [hl("stages[0..=3]")])
s.step("Speedup is T1 over Tp, efficiency is speedup over p. Amdahl caps a fixed problem; Gustafson describes a growing one.", [hl("stages[4..=6]")])
s.step("Next video: OpenMP, part 1. Parallel regions, work-sharing loops, and who owns each variable.", [mk("stages[0..=7]"), s.take("Next: OpenMP, part 1")])

s.save("/home/claude/playlist/m3/m3v16.json")

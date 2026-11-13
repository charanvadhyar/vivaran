"""Module 4, video 13: branch divergence."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

X = [3, 0, 5, 0, 2, 0, 0, 7]
Y = [1, 1, 1, 1, 1, 1, 1, 1]
Z = [9, 8, 7, 6, 5, 4, 3, 2]
M = [int(x != 0) for x in X]
R = [x - y if m else z for x, y, z, m in zip(X, Y, Z, M)]
assert M == [1, 0, 1, 0, 1, 0, 0, 1] and R == [2, 8, 4, 6, 1, 4, 3, 6]
eff = lambda then_n, then_len, else_n, else_len: (then_n * then_len + else_n * else_len) / ((then_len + else_len) * (then_n + else_n))
assert eff(16, 10, 16, 20) == 0.5 and (16 * 10 + 16 * 20, 30 * 32) == (480, 960)
assert sum(1 for t in range(32) if t % 4 == 0) == 8
assert (8 * 12 + 24 * 8, 20 * 32) == (288, 640) and round(288 / 640 * 100) == 45
assert [w for w in range(4) if all(t < 64 for t in range(32 * w, 32 * w + 32))] == [0, 1]
assert [w for w in range(4) if any(t < 64 for t in range(32 * w, 32 * w + 32))] == [0, 1]
TC = [3, 5, 8, 2]
assert max(TC) == 8 and sum(TC) == 18 and round(18 / 32 * 100) == 56
LT = [1, 1, 1, 1, 1, 1, 1, 40]
assert max(LT) == 40 and round(sum(LT) / (8 * 40) * 100) == 15

s = Script("Branch divergence")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "An if inside a kernel"],
    [2, "What the warp does"],
    [3, "Element by element"],
    [4, "Reconverging"],
    [5, "The cost of divergence"],
    [6, "Divergence only happens inside a warp"],
    [7, "Loops that run different lengths"],
    [8, "Exam question"]]})
s.obj({"id": "k", "type": "code", "region": "center", "language": "c", "lines": [
    "__global__ void f(double *X, double *Y, double *Z, int n) {",
    "    int i = blockIdx.x * blockDim.x + threadIdx.x;",
    "    if (X[i] != 0)",
    "        X[i] = X[i] - Y[i];     // then-part",
    "    else",
    "        X[i] = Z[i];            // else-part",
    "}"]})
s.obj({"id": "wd", "type": "table", "region": "center", "columns": ["the warp", "does"], "rows": [
    ["1. evaluate the condition", "every thread computes X[i] != 0: a predicate bit"],
    ["2. all agree", "run only that side, at full speed"],
    ["3. they disagree", "run the then-part with the false threads masked off"],
    ["4. then", "run the else-part with the true threads masked off"],
    ["5. reconverge", "after the if, all 32 threads run together again"]]})
s.obj({"id": "el", "type": "table", "region": "center", "columns": ["thread", "0", "1", "2", "3", "4", "5", "6", "7"], "rows": [
    ["X", *map(str, X)], ["predicate X ≠ 0", "", "", "", "", "", "", "", ""],
    ["then-pass: X − Y", "", "", "", "", "", "", "", ""], ["else-pass: Z", "", "", "", "", "", "", "", ""],
    ["result", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "rc", "type": "table", "region": "center", "columns": ["reconvergence", "how"], "rows": [
    ["the hardware keeps", "a stack of masks for nested branches"],
    ["at a divergent branch", "push: remember who goes which way, and where they meet"],
    ["at the meeting point", "pop: restore the full mask"],
    ["nested ifs", "each level pushes again: masks within masks"],
    ["Volta and later", "a PC per thread; paths still take turns"]]})
s.obj({"id": "co", "type": "math", "region": "center", "lines": [
    "\"then-part 10 instructions, else-part 20, half the warp each\"",
    "\"time\" = 10 + 20 = 30 \"warp instructions, whatever the split\"",
    "\"useful lane slots\" = 16 times 10 + 16 times 20 = 480 quad \"of\" 30 times 32 = 960 quad 50%",
    "\"if every thread had agreed: 10 or 20 instructions, all lanes busy\""]})
s.obj({"id": "wa", "type": "code", "region": "center", "language": "c", "lines": [
    "if (threadIdx.x < 16)  A(); else B();          // diverges: warp 0 splits 16 / 16",
    "",
    "if ((threadIdx.x / 32) % 2 == 0)  A(); else B();  // never diverges:",
    "                                              // a whole warp agrees",
    "",
    "if (data[i] > 0)  A(); else B();             // depends on the data"]})
s.obj({"id": "fx", "type": "code", "region": "center", "language": "c", "lines": [
    "// every warp diverges: even and odd threads alternate",
    "if (i % 2 == 0) even_work(i); else odd_work(i);",
    "",
    "// remap: the first half of the threads do the even elements",
    "int h = n / 2;",
    "if (i < h) even_work(2 * i);        // warps below h: all even",
    "else       odd_work(2 * (i - h) + 1);   // warps above h: all odd"]})
s.obj({"id": "lp", "type": "code", "region": "center", "language": "c", "lines": [
    "for (k = 0; k < count[i]; k++)    // each thread has its own trip count",
    "    work(i, k);",
    "",
    "// the warp keeps looping until its slowest thread is done"]})
s.obj({"id": "lpt", "type": "table", "region": "center", "columns": ["4 threads of a warp", "t0", "t1", "t2", "t3", "warp runs"], "rows": [
    ["trip count", "3", "5", "8", "2", "8 iterations"],
    ["useful iterations", "3", "5", "8", "2", "18 of 4 × 8 = 32: 56%"],
    ["8 threads: 1, 1, …, 1, 40", "", "", "", "", "40 iterations: 47 of 320, 15%"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["a warp of 32 threads; part A is 12 instructions, part B is 8"], "rows": [
    ["a) if (threadIdx.x % 4 == 0) A(); else B();   time, and lane utilisation"],
    ["b) blockDim 128: if (threadIdx.x < 64) A(); else B();   which warps diverge?"],
    ["c) a loop whose trip counts in one warp's threads are 3, 5, 8, 2: iterations run, and useful share"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a) 8 threads take A, 24 take B:\" quad 12 + 8 = 20 \"instructions\"",
    "\"useful\" = 8 times 12 + 24 times 8 = 288 quad \"of\" 20 times 32 = 640 quad 45%",
    "\"b) warps 0, 1: all threads\" < 64 \"→ A · warps 2, 3: all B · none diverges\"",
    "\"c)\" max = 8 \"iterations\" quad (3 + 5 + 8 + 2) / (4 times 8) = 18 / 32 approx 56%"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Every thread in a CUDA kernel can follow its own branches. But the 32 threads of a warp share one instruction stream. So what happens when they disagree at an if? This is branch divergence, and it is the most common reason GPU code runs slower than expected.", [s.head("Branch divergence")])
s.step("Here are the eight stages.", show("stages"))
s.step("A kernel with an if, what the warp does, a trace element by element, and how the threads come back together.", [hl("stages[0..=3]")])
s.step("Then what it costs, when it does not happen, loops of different lengths, and an exam question.", [hl("stages[4..=7]")])

s.scene("k")
s.step("Stage 1: the vector-mask example from video 6, now as a CUDA kernel, with an else added. Each thread looks at its own X.", [s.head("Stage 1 of 8: an if in a kernel")] + hide("stages") + show("k") + [ml("k", 1, 2)])
s.step("If X is not zero, subtract Y.", [ml("k", 3, 4)])
s.step("Otherwise copy Z. To the programmer, every thread simply takes its own path.", [ml("k", 5, 6), s.take("each thread takes its own path, in the source code")])

s.scene("wd")
s.step("Stage 2: in the hardware, the warp first evaluates the condition. Every thread computes one predicate bit.", [s.head("Stage 2 of 8: what the warp does"), s.untake()] + hide("k") + show("wd") + [hl("wd[0]")])
s.step("If all 32 agree, the warp runs only that side, at full speed. No cost at all.", [hl("wd[1]")])
s.step("If they disagree, the warp runs the then-part with the false threads masked off.", [hl("wd[2]")])
s.step("Then it runs the else-part, with the true threads masked off.", [hl("wd[3]")])
s.step("After the if, all 32 threads continue together again. Exactly the masked execution of a vector machine, done automatically by the hardware.", [hl("wd[4]"), s.take("disagreement: both paths, one after the other")])

s.scene("el")
s.step("Stage 3: eight threads of a warp, for clarity. Here are their X values.", [s.head("Stage 3 of 8: element by element"), s.untake()] + hide("wd") + show("el") + [hl("el[0]")])
s.step("The predicate: true for threads 0, 2, 4 and 7.", [st(f"el[1][{i + 1}]", str(m), round(0.07 * i, 2)) for i, m in enumerate(M)])
s.step("The then-pass: only the true threads compute X minus Y. With Y all 1s: 2, 4, 1, 6. The others sit idle.", [st(f"el[2][{i + 1}]", str(R[i]) if m else "idle", round(0.07 * i, 2)) for i, m in enumerate(M)])
s.step("The else-pass: now only the false threads copy Z: 8, 6, 4, 3. The true threads sit idle.", [st(f"el[3][{i + 1}]", "idle" if m else str(R[i]), round(0.07 * i, 2)) for i, m in enumerate(M)])
s.step("Every thread ends with the right answer. But each pass kept half the lanes idle.", [st(f"el[4][{i + 1}]", str(r), round(0.07 * i, 2)) for i, r in enumerate(R)] + [hl("el[4]", 0.6), s.take("correct results, half the lanes idle in each pass")])

s.scene("rc")
s.step("Stage 4: how does the warp know where to come back together? The hardware keeps a stack of masks.", [s.head("Stage 4 of 8: reconverging"), s.untake()] + hide("el") + show("rc") + [hl("rc[0]")])
s.step("At a divergent branch it pushes an entry: which threads go which way, and the point where the paths meet again.", [hl("rc[1]")])
s.step("At that meeting point it pops the entry and restores the full mask.", [hl("rc[2]")])
s.step("Nested ifs push again, so masks sit within masks, and the deeper the nesting, the fewer lanes are busy.", [hl("rc[3]")])
s.step("From Volta onward, NVIDIA GPUs track a program counter per thread, which makes some tricky code, like locks between threads of a warp, safe. But the two paths of a warp still run one after the other.", [hl("rc[4]"), s.take("a mask stack: push at the split, pop at the join")])

s.scene("cost")
s.step("Stage 5: the cost. Say the then-part is 10 instructions and the else-part 20, and half the warp goes each way.", [s.head("Stage 5 of 8: the cost"), s.untake()] + hide("rc") + show("co") + [hl("co[0]")])
s.step("The warp runs both: 30 instructions. And it is 30 whether 1 thread or 31 go one way.", [rv("co[1]"), hl("co[1]")])
s.step("Useful work: 16 threads times 10, plus 16 times 20: 480 lane slots, out of 30 times 32, 960. 50 percent.", [rv("co[2]"), hl("co[2]")])
s.step("Had every thread agreed, the warp would have run 10 or 20 instructions with every lane busy.", [rv("co[3]"), hl("co[3]"), s.take("divergent if-else costs then + else")])

s.scene("wa")
s.step("Stage 6: divergence happens only inside a warp. threadIdx less than 16 splits warp 0 in half: 16 threads each way. It diverges.", [s.head("Stage 6 of 8: only inside a warp"), s.untake()] + hide("co") + show("wa") + [ml("wa", 1, 1)])
s.step("But a condition on threadIdx over 32, the warp number, is the same for all 32 threads of each warp. Even warps take A, odd warps take B, and no warp ever diverges.", [ml("wa", 3, 4)])
s.step("A condition on the data depends on the data. If neighbouring elements tend to agree, as in an image with large smooth regions, warps rarely diverge.", [ml("wa", 6, 6)])
s.step("So a good programmer arranges the work so that each warp's threads take the same path. An example: even and odd elements need different work. Testing i mod 2 makes every warp split in half.", hide("wa") + show("fx") + [ml("fx", 1, 2)])
s.step("Instead, remap: let the first half of the threads handle all the even elements, and the second half all the odd ones. The same work, but each warp now agrees, except at most one warp at the boundary.", [ml("fx", 4, 7)])
s.step("The cost of the work stays the same; the time halves. Sorting the data by condition does the same for data-dependent branches.", [s.take("make the 32 threads of a warp agree")])

s.scene("lp")
s.step("Stage 7: loops diverge too. Here each thread runs its own number of iterations.", [s.head("Stage 7 of 8: uneven loops"), s.untake()] + hide("fx") + show("lp") + [ml("lp", 1, 2)])
s.step("The warp keeps looping until its slowest thread is done. Finished threads are masked off and wait.", [ml("lp", 4, 4)])
s.step("Four threads with trip counts 3, 5, 8 and 2: the warp runs 8 iterations. 18 useful thread-iterations out of 32: 56 percent.", hide("lp") + show("lpt") + [hl("lpt[0..=1]")])
s.step("And a single outlier is the worst case. Seven threads need 1 iteration and one needs 40: the warp runs 40, and only 15 percent of the work is useful.", [hl("lpt[2]"), s.take("a warp's loop runs as long as its slowest thread")])

s.scene("exam")
s.step("Now an exam question: a warp of 32 threads, part A 12 instructions, part B 8.", [s.head("Exam question"), s.untake()] + hide("lpt") + show("q") + [hl("q[0]")])
s.step("Part a: threadIdx mod 4 equals 0 takes A. Part b: with 128 threads, threadIdx less than 64. Part c: a loop with trip counts 3, 5, 8 and 2. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: one thread in four, 8 of 32, takes A; the other 24 take B. The warp diverges and runs both: 20 instructions.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Useful lane slots: 8 times 12 plus 24 times 8, 288, out of 20 times 32, 640. 45 percent.", [rv("qa[1]"), hl("qa[1]")])
s.step("b: threads 0 to 63 are exactly warps 0 and 1, which all take A. Warps 2 and 3 all take B. No warp diverges.", [rv("qa[2]"), hl("qa[2]")])
s.step("c: the warp runs the longest, 8 iterations. 18 useful out of 32: about 56 percent.", [rv("qa[3]"), hl("qa[3]")])
s.step("The usual slip: thinking any if costs both paths. Only a warp whose threads disagree pays. Check where the condition changes relative to the warp boundaries.", [s.take("divergence is per warp, not per kernel")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("When a warp's threads disagree, it runs each path with the others masked off, and reconverges using a stack of masks.", [hl("stages[0..=3]")])
s.step("A divergent if-else costs both paths. Divergence only happens within a warp, and a loop runs as long as its slowest thread.", [hl("stages[4..=6]")])
s.step("Next video: the GPU's memory hierarchy. Registers, shared memory, global memory, and the special constant and texture memories.", [mk("stages[0..=7]"), s.take("Next: the GPU memory hierarchy")])

s.save("/home/claude/playlist/m4/m4v13.json")

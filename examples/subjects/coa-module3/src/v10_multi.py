"""Module 3, video 10: multiple issue with dynamic scheduling and speculation (2-issue example), and the VLIW contrast."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from multi import run

body = lambda: [('LD     R2,0(R1)', 'load', 'R2', ['R1']), ('DADDIU R2,R2,#1', 'alu', 'R2', ['R2']),
                ('SD     R2,0(R1)', 'store', None, ['R2', 'R1']), ('DADDIU R1,R1,#8', 'alu', 'R1', ['R1']),
                ('BNE    R2,R3,Loop', 'branch', None, ['R2', 'R3'])]
P = body() * 3
NS = run(P, 2, False); SP = run(P, 2, True)
assert [NS[i][4] for i in (4, 9, 14)] == [9, 15, 21] and [SP[i][4] for i in (4, 9, 14)] == [9, 12, 15]
assert NS[5][1] == 8 and SP[5][1] == 5 and NS[4][2] == 7
assert (round(5 / 6, 2), round(5 / 3, 2)) == (0.83, 1.67)
cmp_ = lambda w: w * (w - 1)
assert [cmp_(w) for w in (2, 4, 8)] == [2, 12, 56]
assert round(9 / 7, 2) == 1.29 and round(23 / 9, 1) == 2.6
qb = lambda: [('LD     R2,0(R1)', 'load', 'R2', ['R1']), ('DADDIU R1,R1,#8', 'alu', 'R1', ['R1']),
              ('DADDU  R4,R4,R2', 'alu', 'R4', ['R4', 'R2']), ('BNE    R1,R3,Loop', 'branch', None, ['R1', 'R3'])]
Q = qb() * 3
QN = run(Q, 2, False); QS = run(Q, 2, True)
assert [QN[i][4] for i in (3, 7, 11)] == [7, 10, 13] and [QS[i][4] for i in (3, 7, 11)] == [7, 9, 11]


def ex(a, b):
    return str(a) if a == b else f"{a}–{b}"


def rows(T, prog, its=2):
    out = []
    for i in range(5 * its):
        iss, s, e, w, c = T[i]
        out.append([str(i // 5 + 1), prog[i][0], str(iss), ex(s, e), str(w) if w else "–", str(c)])
    return out


s = Script("Multiple issue with dynamic scheduling")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "From one instruction per cycle to several"],
    [2, "What makes wide issue hard"],
    [3, "The example: 2-issue, no speculation"],
    [4, "The same loop with speculation"],
    [5, "Comparing, and the other limits"],
    [6, "The static alternative: VLIW"],
    [7, "Exam question"]]})
s.obj({"id": "kinds", "type": "table", "region": "center", "columns": ["machine", "issue", "scheduled by", "example"], "rows": [
    ["static superscalar", "2 per cycle, in order", "hardware, in order", "early embedded cores"],
    ["VLIW", "one wide packet", "the compiler", "Itanium, DSPs"],
    ["dynamic superscalar", "4 to 8 per cycle", "hardware, out of order", "Intel Core, AMD Zen, Apple M"]]})
s.obj({"id": "hard", "type": "table", "region": "center", "columns": ["each cycle, for w instructions", "cost"], "rows": [
    ["a station and a ROB entry for each", "w allocations"],
    ["compare sources with earlier destinations in the group", "w(w − 1) comparisons"],
    ["update the register map, in order", "the last writer wins"]]})
s.obj({"id": "hm", "type": "math", "region": "bottom", "lines": [
    "w = 2 : 2 quad w = 4 : 12 quad w = 8 : 56 \"comparisons, every cycle\""]})
s.obj({"id": "lp", "type": "code", "region": "center", "language": "asm", "lines": [
    "Loop: LD     R2,0(R1)     ; R2 = array element",
    "      DADDIU R2,R2,#1     ; add 1",
    "      SD     R2,0(R1)     ; store it back",
    "      DADDIU R1,R1,#8     ; next element",
    "      BNE    R2,R3,Loop   ; stop at the last element"]})
s.obj({"id": "asm", "type": "table", "region": "center", "columns": ["assume", "value"], "rows": [
    ["issue and commit", "2 per cycle, in order"],
    ["latency", "load 2 cycles · integer ALU 1 · branch 1"],
    ["result buses", "2 per cycle"],
    ["without speculation", "nothing after a branch starts executing until the branch has executed"]]})
s.obj({"id": "tn", "type": "table", "region": "center", "columns": ["iter", "instruction", "issue", "execute", "write", "commit"], "rows": rows(NS, P)})
s.obj({"id": "ts", "type": "table", "region": "center", "columns": ["iter", "instruction", "issue", "execute", "write", "commit"], "rows": rows(SP, P)})
s.obj({"id": "cm", "type": "table", "region": "center", "columns": ["", "without speculation", "with speculation"], "rows": [
    ["iterations end (commit of BNE)", "9, 15, 21", "9, 12, 15"],
    ["cycles per iteration", "6", "3 at first, then toward 2.5"],
    ["instructions per cycle", "5 / 6 ≈ 0.83", "5 / 3 ≈ 1.67, rising toward 2"]]})
s.obj({"id": "lim", "type": "table", "region": "center", "columns": ["what else must widen", "why"], "rows": [
    ["fetch and branch prediction", "several instructions, maybe a branch, every cycle"],
    ["result buses and register ports", "several results and operands per cycle"],
    ["commit width", "otherwise finished work piles up in the ROB"],
    ["ROB and stations", "more instructions in flight to find independent ones"]]})
s.obj({"id": "vliw", "type": "table", "region": "center", "columns": ["VLIW", "meaning"], "rows": [
    ["one instruction", "a packet with slots: e.g. 2 memory, 2 FP, 1 integer or branch"],
    ["who schedules", "the compiler, using unrolling; the hardware checks nothing"],
    ["the textbook's example", "the x[i] + s loop unrolled 7 times runs in 9 cycles: 1.29 cycles per element"],
    ["costs", "empty slots waste code space; binaries are tied to one machine's latencies"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "asm", "lines": [
    "Loop: LD     R2,0(R1)",
    "      DADDIU R1,R1,#8",
    "      DADDU  R4,R4,R2",
    "      BNE    R1,R3,Loop"]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["same 2-issue machine. Find:"], "rows": [
    ["a) the cycle each of three iterations commits its BNE, without speculation"],
    ["b) the same, with speculation"],
    ["c) cycles per iteration for each, and what limits the faster one"],
    ["d) issue-stage comparisons for a 4-wide machine"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["", "without speculation", "with speculation"], "rows": [
    ["BNE commits", "7, 10, 13", "7, 9, 11"],
    ["cycles per iteration", "3", "2"],
    ["limited by", "waiting for each branch", "issue: 4 instructions ÷ 2 per cycle"],
    ["d) 4-wide", "4 × 3 = 12 comparisons", ""]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Everything so far issued one instruction per cycle, so the best CPI was 1. To beat that, issue several per cycle. Combine that with Tomasulo and speculation, and you have the core of every modern laptop and phone processor.", [s.head("Multiple issue with dynamic scheduling")])
s.step("Here are the seven stages.", show("stages"))
s.step("The kinds of multiple issue, what makes it hard, and one loop run on a 2-issue machine without speculation.", [hl("stages[0..=2]")])
s.step("Then the same loop with speculation, a comparison, the VLIW alternative, and an exam question.", [hl("stages[3..=6]")])

# ---------------------------------------------------------------- kinds
s.scene("kinds")
s.step("Stage 1: Module 1 introduced superscalar and VLIW machines. Here is where they sit now.", [s.head("Stage 1 of 7: several per cycle")] + hide("stages") + show("kinds"))
s.step("A statically scheduled superscalar issues a few instructions per cycle, in order. Simple, but one stall stops everything.", [hl("kinds[0]")])
s.step("A VLIW lets the compiler pack independent operations into one long instruction. We return to it at the end.", [hl("kinds[1]")])
s.step("A dynamically scheduled superscalar issues several per cycle into Tomasulo-style stations, with a reorder buffer and speculation. Every high-performance core today works this way.", [hl("kinds[2]"), s.take("today: wide issue + out of order + speculation")])

# ---------------------------------------------------------------- hard
s.scene("hard")
s.step("Stage 2: the hard part is issue itself. In one cycle, the issue stage must handle a whole group of instructions.", [s.head("Stage 2 of 7: what makes it hard"), s.untake()] + hide("kinds") + show("hard"))
s.step("Find a free station and a free ROB entry for each of them.", [hl("hard[0]")])
s.step("Check whether any instruction in the group needs the result of an earlier one in the same group. Each source must be compared with every earlier destination.", [hl("hard[1]")])
s.step("With w instructions of two sources each, that is w times w minus 1 comparisons. 2 for a 2-wide machine, 12 for 4-wide, 56 for 8-wide. Every cycle.", show("hm") + [hl("hm[0]")])
s.step("And the register map must be updated for the whole group in order, so the last writer in the group wins. This logic is one reason issue widths have stayed between about 4 and 8.", [hl("hard[2]")])

# ---------------------------------------------------------------- no spec
s.scene("nospec")
s.step("Stage 3: an integer loop that adds 1 to every array element.", [s.head("Stage 3 of 7: 2-issue, no speculation")] + hide("hard", "hm") + show("lp") + [ml("lp", 1, 5)])
s.step("The machine: 2 instructions issue and 2 commit per cycle. A load takes 2 cycles, an integer operation 1. Without speculation, nothing after a branch may execute until the branch itself has executed.", hide("lp") + show("asm") + [hl("asm[0..=2]"), hl("asm[3]", 0.6)])
s.step("Here are the first two iterations. The load issues in 1 and executes in 2 and 3. The add must wait for it, executing in 5.", hide("asm") + show("tn") + [hl("tn[0]"), hl("tn[1]", 0.4)])
s.step("The branch depends on the add's R2, so it executes in 7.", [hl("tn[4]")])
s.step("Now the second iteration's load. It issued back in cycle 3, and its address R1 was ready in 4. But it is behind a branch, so it may not start until cycle 8.", [hl("tn[5]"), hl("tn[4][3]", 0.4)])
s.step("Every iteration waits for the previous branch. The branches commit in 9, 15, and 21: 6 cycles per iteration, though the machine could issue an iteration every 2.5.", [hl("tn[9]"), {"action": "highlight", "target": "tn[4][5]", "delay": 0.4}, s.take("no speculation: each iteration waits for the last branch")])

# ---------------------------------------------------------------- spec
s.scene("spec")
s.step("Stage 4: the same loop, with speculation. The branch is predicted taken, and later instructions may execute before it resolves.", [s.head("Stage 4 of 7: with speculation"), s.untake()] + hide("tn") + show("ts"))
s.step("Iteration 1 is unchanged: the load, the add, the store, the branch.", [hl("ts[0..=4]")])
s.step("But iteration 2's load starts in cycle 5, as soon as R1 is ready, instead of 8. Its add, store and branch follow 3 cycles behind iteration 1.", [hl("ts[5]"), hl("ts[6..=9]", 0.4)])
s.step("Results finish out of order, but commit still marches in order, 2 per cycle. The branches commit in 9, 12 and 15.", [hl("ts[4][5]"), hl("ts[9][5]", 0.4)])
s.step("If a prediction had been wrong, the ROB would flush the work behind it, exactly as in the last video. Here every iteration but the last guesses right.", [s.take("speculation: the next iteration runs before the branch is known")])

# ---------------------------------------------------------------- compare
s.scene("cmp")
s.step("Stage 5: side by side.", [s.head("Stage 5 of 7: comparing"), s.untake()] + hide("ts") + show("cm"))
s.step("Without speculation, an iteration every 6 cycles. With it, every 3. Twice as fast, on the same hardware.", [hl("cm[0..=1]")])
s.step("In instructions per cycle: 0.83 against 1.67. Speculation is what lets a wide machine actually use its width.", [hl("cm[2]")])
s.step("Can it go faster still? Each iteration has 5 instructions, and only 2 issue per cycle, so an iteration needs at least 2.5 cycles to issue. Run ten iterations and the speculative machine settles close to that limit. The non-speculative one stays at 6.", [hl("cm[1][2]"), hl("cm[2][2]", 0.5)])
s.step("And issue is not the only thing that must widen.", hide("cm") + show("lim"))
s.step("Fetch must deliver several instructions per cycle, and predict a branch among them. There must be enough result buses and register ports for several results per cycle.", [hl("lim[0..=1]")])
s.step("Commit must keep up, or finished instructions pile up in the ROB. And the ROB and stations must be big enough to hold the instructions in flight.", [hl("lim[2..=3]"), s.take("issue, buses, commit and ROB must all widen together")])

# ---------------------------------------------------------------- VLIW
s.scene("vliw")
s.step("Stage 6: the static alternative. A VLIW instruction is a packet with fixed slots, for example 2 memory operations, 2 floating-point operations, and 1 integer or branch.", [s.head("Stage 6 of 7: VLIW"), s.untake()] + hide("lim") + show("vliw") + [hl("vliw[0]")])
s.step("The compiler fills the slots, mostly by unrolling loops. The hardware performs no dependence checks at all, so it is simple and low power.", [hl("vliw[1]")])
s.step("In the textbook's example, the add-a-scalar loop unrolled 7 times fits in 9 packets: 9 cycles for 7 elements, about 1.29 cycles each.", [hl("vliw[2]")])
s.step("The costs: unfilled slots waste code space, and the schedule is built for one machine's latencies. A cache miss stalls everything. That is why VLIW lives on in DSPs, while general-purpose cores went dynamic.", [hl("vliw[3]"), s.take("VLIW: the compiler schedules · superscalar: the hardware does")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question: a loop that sums an array into R4, on the same 2-issue machine.", [s.head("Exam question"), s.untake()] + hide("vliw") + show("q") + [ml("q", 1, 4)])
s.step("Find when each of three iterations commits its branch, without and with speculation, the cycles per iteration, what limits the faster one, and the comparisons a 4-wide issue stage needs. Pause and work it out.", hide("q") + show("qx") + [hl("qx")])
s.step("Without speculation: the branch needs the new R1, ready in cycle 3, so it executes in 4. The next iteration waits for that. The branches commit in 7, 10 and 13: 3 cycles per iteration.", hide("qx") + show("qa") + [hl("qa[0][1]"), hl("qa[1][1]", 0.5)])
s.step("With speculation: the next load starts as soon as R1 is ready. The branches commit in 7, 9 and 11: 2 cycles per iteration.", [hl("qa[0][2]"), hl("qa[1][2]", 0.5)])
s.step("Why 2? Four instructions at 2 per cycle cannot issue faster. With speculation, the limit is now the issue width itself.", [hl("qa[2]")])
s.step("d: 4 times 3, 12 comparisons each cycle. The usual slip: forgetting that commit, not execution, marks when an iteration is truly done.", [hl("qa[3]"), s.take("speculation moves the limit from branches to issue width")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Wide issue needs fast allocation and w times w minus 1 comparisons a cycle. Without speculation, our loop ran an iteration every 6 cycles; with it, every 3.", [hl("stages[0..=4]")])
s.step("VLIW moves the scheduling to the compiler, trading hardware for code size and flexibility.", [hl("stages[5]")])
s.step("Next video: the limits of ILP. How much parallelism is really there to find?", [mk("stages[0..=6]"), s.take("Next: the limits of ILP")])

s.save("/home/claude/playlist/m3/m3v10.json")

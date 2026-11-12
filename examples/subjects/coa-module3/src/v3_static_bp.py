"""Module 3, video 3 (short): static branch prediction."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

r = lambda x, n=3: round(x, n)
# nested loops: outer 10 iterations, inner 4 iterations; both loop branches at the bottom (backward)
inner_t, inner_n = 10 * 3, 10 * 1
outer_t, outer_n = 9, 1
total = inner_t + inner_n + outer_t + outer_n
assert total == 50
nt = inner_t + outer_t; tk = inner_n + outer_n; btfn = tk
assert (nt, tk, btfn) == (39, 11, 11)
assert (r(nt / total), r(tk / total)) == (0.78, 0.22)
assert (r(1 + 0.2 * 0.78 * 2), r(1 + 0.2 * 0.22 * 2)) == (1.312, 1.088)
# exam: 100 iterations; backward loop branch taken 99 times; forward if-branch taken 30 times
b_t, b_n, f_t, f_n = 99, 1, 30, 70
q_nt, q_tk, q_btfn = b_t + f_t, b_n + f_n, b_n + f_t
assert (q_nt, q_tk, q_btfn) == (129, 71, 31)
assert (q_nt / 200, q_tk / 200, q_btfn / 200) == (0.645, 0.355, 0.155)
assert (r(1 + 0.25 * 0.645 * 3, 2), r(1 + 0.25 * 0.355 * 3, 2), r(1 + 0.25 * 0.155 * 3, 2)) == (1.48, 1.27, 1.12)

s = Script("Static branch prediction")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why predict at all"],
    [2, "Four static schemes"],
    [3, "The delayed branch"],
    [4, "Counting mispredictions in nested loops"],
    [5, "Exam question"]]})
s.obj({"id": "why", "type": "math", "region": "center", "lines": [
    "\"CPI\" = 1 + \"branch frequency\" times \"misprediction rate\" times \"penalty\"",
    "\"20% branches, penalty 2, every branch wrong:\" quad 1 + 0.2 times 1 times 2 = 1.4",
    "\"static: the guess is fixed before the program runs\""]})
s.obj({"id": "sch", "type": "table", "region": "center", "columns": ["scheme", "guess", "good for"], "rows": [
    ["not taken", "fetch the next instruction; flush if taken", "simple hardware, ifs"],
    ["taken", "fetch from the target", "loops"],
    ["BTFN", "backward: taken · forward: not taken", "loops and ifs together"],
    ["profile-based", "each branch's usual direction from a test run", "branches that lean one way"]]})
s.obj({"id": "ds", "type": "table", "region": "center", "columns": ["fill the delay slot with", "condition", "when it helps"], "rows": [
    ["an instruction from before the branch", "the branch must not depend on it", "always"],
    ["an instruction from the target", "safe to run when the branch is not taken", "when taken"],
    ["an instruction from the fall-through", "safe to run when taken", "when not taken"]]})
s.obj({"id": "dsc", "type": "code", "region": "center", "language": "asm", "lines": [
    "before:  DADD R1,R2,R3",
    "         BEQZ R4,L",
    "         (empty slot)",
    "after:   BEQZ R4,L",
    "         DADD R1,R2,R3   ; in the delay slot"]})
s.obj({"id": "nl", "type": "code", "region": "left", "language": "c", "lines": [
    "for (i = 0; i < 10; i++) {",
    "  for (j = 0; j < 4; j++) {",
    "    work();",
    "  }   // inner branch",
    "}     // outer branch"]})
s.obj({"id": "nlt", "type": "table", "region": "right", "columns": ["branch", "taken", "not taken"], "rows": [
    ["inner", "", ""], ["outer", "", ""], ["total", "", ""]]})
s.obj({"id": "nlm", "type": "table", "region": "center", "columns": ["scheme", "mispredictions", "rate", "CPI (20% branches, penalty 2)"], "rows": [
    ["predict not taken", "30 + 9 = 39", "78%", "1 + 0.2 × 0.78 × 2 = 1.31"],
    ["predict taken", "10 + 1 = 11", "22%", "1 + 0.2 × 0.22 × 2 = 1.09"],
    ["BTFN", "11 (both branches are backward)", "22%", "1.09"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["loop of 100 iterations, branch at the bottom", "a) mispredictions: not taken, taken, BTFN"],
    ["a forward if-branch inside, taken 30 times", "b) misprediction rate of each"],
    ["25% branches, penalty 3 cycles", "c) CPI of each"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["scheme", "loop branch", "if-branch", "total of 200", "CPI"], "rows": [
    ["not taken", "99 wrong", "30 wrong", "129: 64.5%", "1 + 0.25 × 0.645 × 3 ≈ 1.48"],
    ["taken", "1 wrong", "70 wrong", "71: 35.5%", "≈ 1.27"],
    ["BTFN", "1 wrong", "30 wrong", "31: 15.5%", "≈ 1.12"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}

s.scene("intro")
s.step("Loop unrolling removed branches. The ones that remain still cost cycles, unless we guess their direction correctly. This short video covers the guesses made before the program runs.", [s.head("Static branch prediction")])
s.step("Five stages: why predict, four static schemes, the delayed branch, counting mispredictions in nested loops, and an exam question.", show("stages") + [hl("stages[0..=4]")])

s.scene("why")
s.step("Stage 1: every wrong guess costs a penalty of a few cycles, while the pipeline throws away wrongly fetched instructions.", [s.head("Stage 1 of 5: why predict")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("So the CPI is 1, plus the branch frequency, times the misprediction rate, times the penalty.", [mk("why[0]")])
s.step("With 20 percent branches and a 2-cycle penalty, getting every branch wrong would raise the CPI to 1.4. Every percent of accuracy matters.", rv("why", 1))
s.step("A static prediction is fixed before the program runs, by the hardware's rule or by the compiler. It never changes while running.", rv("why", 2) + [s.take("CPI = 1 + f × miss rate × penalty")])

s.scene("schemes")
s.step("Stage 2: four static schemes.", [s.head("Stage 2 of 5: four static schemes"), s.untake()] + hide("why") + show("sch"))
s.step("Predict not taken: keep fetching the next instruction, and flush it if the branch turns out taken. The simplest hardware, which is what our 5-stage pipeline did in Module 1.", [hl("sch[0]")])
s.step("Predict taken: start fetching from the target. Loops make most branches taken, but the target address must be known early.", [hl("sch[1]")])
s.step("BTFN: backward taken, forward not taken. A branch jumping backward is usually a loop, so guess taken. A forward branch is usually an if, so guess not taken.", [hl("sch[2]")])
s.step("Profile-based: run the program once on sample input, record which way each branch usually went, and let the compiler mark it with a hint bit. Misprediction rates vary a lot between programs.", [hl("sch[3]"), s.take("not taken · taken · BTFN · profile")])

s.scene("delay")
s.step("Stage 3: an older trick, the delayed branch. The instruction right after the branch, its delay slot, always runs, whatever the branch does.", [s.head("Stage 3 of 5: the delayed branch"), s.untake()] + hide("sch") + show("ds"))
s.step("The best filler comes from before the branch, if the branch does not depend on it. Then the slot always does useful work.", [hl("ds[0]")])
s.step("Here, the branch tests R4 and the add writes R1, so the add can move into the slot.", hide("ds") + show("dsc"))
s.step("Otherwise, take one from the target, which helps when the branch is taken, or from the fall-through, which helps when it is not. Either must be harmless on the other path.", hide("dsc") + show("ds") + [hl("ds[1]"), hl("ds[2]", 0.5)])
s.step("Delayed branches suited simple 5-stage pipelines. With deep pipelines and multiple issue, one slot is not enough, so modern processors predict dynamically instead.", [s.take("delay slot: always executed · fill from before if possible")])

s.scene("nested")
s.step("Stage 4: counting. Two nested loops. The outer one runs 10 times, the inner one 4 times per outer iteration. Each loop's branch sits at its bottom, jumping backward.", [s.head("Stage 4 of 5: counting mispredictions"), s.untake()] + hide("ds") + show("nl", "nlt"))
s.step("The inner branch runs 4 times per outer pass: taken 3 times, then not taken once, to exit. Over 10 passes: taken 30 times, not taken 10.", [go("nl", 4), st("nlt[0][1]", "30"), st("nlt[0][2]", "10", 0.4)])
s.step("The outer branch runs 10 times: taken 9 times, not taken once.", [go("nl", 5), st("nlt[1][1]", "9"), st("nlt[1][2]", "1", 0.4)])
s.step("In total, 50 branch executions: 39 taken, 11 not taken.", [st("nlt[2][1]", "39"), st("nlt[2][2]", "11", 0.3), hl("nlt[2]", 0.5)])
s.step("Predict not taken is wrong on every taken branch: 39 of 50, 78 percent. The CPI becomes 1.31.", hide("nl", "nlt") + show("nlm") + [hl("nlm[0]")])
s.step("Predict taken is wrong only on the 11 exits: 22 percent, a CPI of 1.09.", [hl("nlm[1]")])
s.step("And BTFN gives the same here, since both branches jump backward. It differs only when forward branches appear, as in the exam question.", [hl("nlm[2]"), s.take("loop branch: wrong once per loop exit when predicted taken")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("nlm") + show("q"))
s.step("A loop of 100 iterations with its branch at the bottom. Inside, a forward if-branch, taken 30 times. 25 percent of instructions are branches, and a misprediction costs 3 cycles. Find the mispredictions, the rates, and the CPI under not taken, taken, and BTFN. Pause and work it out.", [hl("q[0]"), hl("q[1]", 0.3), hl("q[2]", 0.6)])
s.step("Not taken: wrong on the 99 loop-backs and on the 30 taken ifs. 129 of 200 branches, 64.5 percent. CPI: 1 plus 0.25 times 0.645 times 3, about 1.48.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Taken: wrong on the one loop exit, and on the 70 untaken ifs. 71, 35.5 percent, CPI about 1.27.", [hl("qa[1]")])
s.step("BTFN: the backward loop branch is guessed taken, wrong once. The forward if is guessed not taken, wrong 30 times. 31, 15.5 percent, CPI about 1.12. The best of the three.", [hl("qa[2]")])
s.step("The usual slip: forgetting that a loop branch is not taken once, at the exit.", [s.take("BTFN wins when loops and ifs mix")])

s.scene("recap")
s.step("Static prediction fixes each guess in advance: not taken, taken, BTFN, or from a profile. Delay slots hide one cycle more. Next video: scoreboarding, the first step into dynamic scheduling.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages") + [mk("stages[0..=4]"), s.take("Next: scoreboarding")])

s.save("/home/claude/playlist/m3/m3v3.json")

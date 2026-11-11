"""Module 1, video 5: handling hazards: stalls, forwarding, the load-use stall, branch handling."""
import sys
sys.path.insert(0, ".")
from common import Script
from hz import CODE, occupancy

LANES = [f"I{i + 1}: {c[3]}" for i, c in enumerate(CODE)]
NOF, TN = occupancy(CODE, False)
FWD, TF = occupancy(CODE, True)
assert (TN, TF) == (17, 10)
Q = [("LW", "R1", ["R2"], "LW  R1, 0(R2)"), ("ADD", "R3", ["R1", "R1"], "ADD R3, R1, R1"), ("SUB", "R4", ["R3", "R5"], "SUB R4, R3, R5"), ("SW", None, ["R4", "R2"], "SW  R4, 8(R2)")]
assert occupancy(Q, False)[1] == 14 and occupancy(Q, True)[1] == 9
cpi = lambda f, t, p: round(1 + f * t * p, 2)
assert (round(1 + 0.2 * 2, 2), cpi(0.2, 0.6, 2), cpi(0.2, 0.6, 1), cpi(0.25, 0.4, 3)) == (1.4, 1.24, 1.12, 1.3)


def timeline(id, blocks, end):
    return {"id": id, "type": "timeline", "region": "center", "lanes": LANES, "end": end, "unit": "clock cycle", "now": 0, "blocks": []}


def add(tid, blocks, lane, delay=True):
    mine = [b for b in blocks if b[0] == lane]
    return [{"action": "add_block", "target": tid, "id": f"{tid}{lane}_{c}", "lane": LANES[lane], "start": c - 1, "end": c,
             "label": "—" if l == "stall" else l, **({"delay": round(min(0.8, k * 0.08), 2)} if delay else {})} for k, (_, c, l) in enumerate(mine)]


s = Script("Handling hazards: stalls, forwarding and branches")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Stalls: wait, and insert bubbles"],
    [2, "Count the cycles with stalls only"],
    [3, "Forwarding: pass results straight to the ALU"],
    [4, "The load-use case: one stall forwarding cannot remove"],
    [5, "Branches: flush, predict, decide early, or delay"],
    [6, "The branch penalty as a CPI"]]})
s.obj({"id": "code", "type": "code", "region": "left", "language": "asm", "lines": [c[3] for c in CODE]})
s.obj({"id": "depl", "type": "table", "region": "right", "columns": ["needs", "from", "register"], "rows": [
    ["I2", "I1 (ADD)", "R1"], ["I3", "I2 (SUB)", "R4"], ["I4", "I3 (LW)", "R6"], ["I5", "I4 (AND)", "R7"]]})
s.obj(timeline("nof", NOF, 17))
s.obj(timeline("fwd", FWD, 17))
s.obj({"id": "fwdx", "type": "diagram", "region": "center", "layout": "layers", "direction": "right", "nodes": [
    {"id": "ex1", "label": "ADD in EX: R1 computed"}, {"id": "reg", "label": "EX/MEM register holds R1"},
    {"id": "ex2", "label": "SUB in EX next cycle"}], "edges": [{"from": "ex1", "to": "reg"}, {"from": "reg", "to": "ex2", "label": "forward"}]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["", "stalls", "total cycles"], "rows": [
    ["ideal: 5 + 5 − 1", "0", "9"], ["stalls only", "", ""], ["with forwarding", "", ""]]})
s.obj({"id": "br", "type": "table", "region": "center", "columns": ["method", "what happens", "penalty"], "rows": [
    ["stall", "freeze fetch until the branch is decided", "2 cycles on every branch"],
    ["predict not taken", "keep fetching in order; flush if the branch is taken", "2 cycles, only when taken"],
    ["decide in ID", "add a comparator in ID, so the branch is known one stage earlier", "1 cycle"],
    ["delayed branch", "the compiler puts a useful instruction in the slot after the branch", "0 when the slot is filled"],
    ["dynamic prediction", "a branch history table guesses from past behaviour", "only on a wrong guess"]]})
s.obj({"id": "bcpi", "type": "math", "region": "center", "lines": [
    "\"CPI\" = 1 + f_\"branch\" times f_\"penalised\" times \"penalty\"",
    "\"stall\": 1 + 0.2 times 1 times 2 = 1.4",
    "\"predict not taken\": 1 + 0.2 times 0.6 times 2 = 1.24",
    "\"decide in ID, predict not taken\": 1 + 0.2 times 0.6 times 1 = 1.12"]})
s.obj({"id": "qcode", "type": "code", "region": "left", "language": "asm", "lines": [c[3] for c in Q]})
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["", "stalls", "cycles"], "rows": [
    ["ideal: 5 + 4 − 1", "0", "8"], ["stalls only", "", ""], ["forwarding", "", ""]]})
s.obj({"id": "qb", "type": "math", "region": "bottom", "lines": ["\"CPI\" = 1 + 0.25 times 0.4 times 3 = 1.3"]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Last video we found hazards. Now we handle them, and count what each fix costs in cycles.", [s.head("Handling hazards")])
s.step("Here are the six stages.", [{"action": "show", "target": "stages"}])
s.step("Stalls, and how many cycles they cost on one code sequence.", [{"action": "highlight", "target": "stages[0..=1]"}])
s.step("Then forwarding, and the one case it cannot fix: a load followed by its use.", [{"action": "highlight", "target": "stages[2..=3]"}])
s.step("Then branches: four ways to handle them, and the branch penalty turned into CPI.", [{"action": "highlight", "target": "stages[4..=5]"}])

# ---------------------------------------------------------------- code
s.scene("code")
s.step("Here is the code we will run, five instructions long.", [s.head("The code"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "code"}])
s.step("Each instruction from I2 on reads the result of the one just before it.", [{"action": "show", "target": "depl"}, {"action": "highlight", "target": "depl[0..=3]"}])
s.step("I2 needs R1 from the add, I3 needs R4 from the subtract, I4 needs R6 from the load, and I5 needs R7 from the AND.", [{"action": "mark_lines", "target": "code", "from": 1, "to": 5}])
s.step("Four RAW hazards, each only one instruction apart: the worst case.", [s.take("4 RAW hazards, each 1 apart")])

# ---------------------------------------------------------------- stalls
s.scene("stalls")
s.step("Stage 1: the simplest fix is to wait. The instruction stays in ID until its value is in the register file.", [s.head("Stage 1 and 2 of 6: stalls"), {"action": "hide", "target": "code"}, {"action": "hide", "target": "depl"}, s.untake(), {"action": "show", "target": "nof"}])
s.step("I1 runs normally and writes R1 in cycle 5.", add("nof", NOF, 0))
s.step("I2 reaches ID in cycle 3, but must wait until cycle 5 to read R1. Cycles 4 and 5 are stalls, shown as dashes.", add("nof", NOF, 1))
s.step("A stall is also called a bubble: an empty slot that moves down the pipeline doing nothing.", [])
s.step("I3 is stuck behind I2 in IF, then waits again for R4, written in cycle 8.", add("nof", NOF, 2))
s.step("I4 waits for R6 from the load, written in cycle 11.", add("nof", NOF, 3))
s.step("And I5 waits for R7, written in cycle 14. It finishes in cycle 17.", add("nof", NOF, 4) + [{"action": "advance", "target": "nof", "to": 17}])
s.step("Stage 2: count. The ideal is 5 plus 5 minus 1, which is 9 cycles. We took 17.", [s.untake(), {"action": "hide", "target": "nof"}, {"action": "show", "target": "cmp"}, {"action": "highlight", "target": "cmp[0]"}])
s.step("That is 8 stall cycles: 2 for each of the 4 hazards.", [{"action": "set", "target": "cmp[1][1]", "value": "8"}, {"action": "set", "target": "cmp[1][2]", "value": "17", "delay": 0.4}, {"action": "highlight", "target": "cmp[1]"}])
s.step("Rule: without forwarding, a RAW hazard one apart costs 2 stalls, and two apart costs 1.", [s.take("no forwarding: 1 apart → 2 stalls · 2 apart → 1 stall · 3 apart → 0")])

# ---------------------------------------------------------------- forwarding
s.scene("forwarding")
s.step("Stage 3: forwarding. Notice the add's result exists at the end of its EX stage, long before WB.", [s.head("Stage 3 of 6: forwarding"), {"action": "hide", "target": "cmp"}, s.untake(), {"action": "show", "target": "fwdx"}])
s.step("It sits in the pipeline register after EX.", [{"action": "highlight", "target": "fwdx.reg"}])
s.step("Forwarding, also called bypassing, wires that register straight back to the ALU input.", [{"action": "highlight", "target": "fwdx.reg->ex2"}])
s.step("So the next instruction can use the value in its own EX stage, the very next cycle, with no stall.", [{"action": "highlight", "target": "fwdx.ex2"}])
s.step("A second path forwards from the register after MEM, for an instruction two behind.", [s.take("forwarding paths: EX/MEM → ALU and MEM/WB → ALU")])

# ---------------------------------------------------------------- load-use
s.scene("load-use")
s.step("Stage 4: run the same code with forwarding.", [s.head("Stage 4 of 6: forwarding, and the load-use stall"), {"action": "hide", "target": "fwdx"}, s.untake(), {"action": "show", "target": "fwd"}])
s.step("I1 runs as before.", add("fwd", FWD, 0))
s.step("I2 gets R1 forwarded from I1's EX: no stall.", add("fwd", FWD, 1))
s.step("I3, the load, gets R4 forwarded from I2: no stall.", add("fwd", FWD, 2))
s.step("But I4 needs R6, and a load only has its data at the end of MEM, not EX.", [{"action": "highlight", "target": "fwd.fwd2_6"}])
s.step("I4's EX would be in cycle 6, the same cycle the load is reading memory. Too early, even with forwarding.", [])
s.step("So I4 stalls for one cycle, and gets R6 forwarded from after MEM in cycle 7.", add("fwd", FWD, 3))
s.step("I5 gets R7 forwarded from I4, and the whole sequence ends in cycle 10.", add("fwd", FWD, 4) + [{"action": "advance", "target": "fwd", "to": 10}])
s.step("Compare: 17 cycles with stalls only, 10 with forwarding, against the ideal of 9.", [s.untake(), {"action": "hide", "target": "fwd"}, {"action": "show", "target": "cmp"}, {"action": "set", "target": "cmp[2][1]", "value": "1"}, {"action": "set", "target": "cmp[2][2]", "value": "10", "delay": 0.4}, {"action": "highlight", "target": "cmp[2]"}])
s.step("This is the load-use hazard: a load followed straight away by its use always costs one stall in this pipeline.", [s.take("load-use: 1 stall even with forwarding")])
s.step("If even one independent instruction sits between the load and its use, the value is forwarded from after MEM just in time: no stall.", [])
s.step("So compilers hide the stall by moving an independent instruction into that gap. This is called instruction scheduling.", [])
s.step("Edge case: a store that only needs the loaded value as its data, not its address, can take it even later, in MEM.", [])

# ---------------------------------------------------------------- branches
s.scene("branches")
s.step("Stage 5: branches. In our pipeline, a branch is decided in EX, two cycles after it is fetched.", [s.head("Stage 5 of 6: handling branches"), {"action": "hide", "target": "cmp"}, s.untake(), {"action": "show", "target": "br"}])
s.step("Simplest: stall. Stop fetching until the branch is decided. Every branch costs 2 cycles.", [{"action": "highlight", "target": "br[0]"}])
s.step("Better: predict not taken. Keep fetching the next instructions; if the branch is not taken, nothing is lost.", [{"action": "highlight", "target": "br[1]"}])
s.step("If it is taken, flush the two wrong instructions, turning them into bubbles. The penalty is paid only on taken branches.", [{"action": "highlight", "target": "br[1][2]"}])
s.step("Decide earlier: add a comparator and an adder to ID, so the branch is known after one cycle. The penalty drops to 1.", [{"action": "highlight", "target": "br[2]"}])
s.step("Delayed branch: the instruction right after a branch always runs, and the compiler fills that slot with useful work.", [{"action": "highlight", "target": "br[3]"}])
s.step("And dynamic prediction: hardware remembers how each branch went last time, and guesses. Only wrong guesses cost cycles.", [{"action": "highlight", "target": "br[4]"}])

# ---------------------------------------------------------------- branch CPI
s.scene("branch-cpi")
s.step("Stage 6: turn the penalty into CPI, cycles per instruction.", [s.head("Stage 6 of 6: the branch penalty as CPI"), {"action": "hide", "target": "br"}, {"action": "show", "target": "bcpi"}])
s.step("Ideal CPI is 1. Add the fraction of instructions that are branches, times the fraction of those that pay, times the penalty.", [{"action": "highlight", "target": "bcpi[0]"}])
s.step("Say 20 percent of instructions are branches, and 60 percent of branches are taken.", [s.take("branches: 20% of instructions · taken: 60% of branches")])
s.step("Stalling: every branch pays 2 cycles, so 1 plus 0.2 times 1 times 2 is 1.4.", [{"action": "reveal", "target": "bcpi[1]"}, {"action": "highlight", "target": "bcpi[1]"}])
s.step("Predict not taken: only taken branches pay, so 1 plus 0.2 times 0.6 times 2 is 1.24.", [{"action": "reveal", "target": "bcpi[2]"}, {"action": "highlight", "target": "bcpi[2]"}])
s.step("Decide in ID as well: the penalty is 1, so 1 plus 0.2 times 0.6 times 1 is 1.12.", [{"action": "reveal", "target": "bcpi[3]"}, {"action": "highlight", "target": "bcpi[3]"}])
s.step("Check: each improvement must lower the CPI, and none can go below the ideal of 1.", [])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question, in two parts.", [s.head("Exam question"), {"action": "hide", "target": "bcpi"}, s.untake(), {"action": "show", "target": "qcode"}, {"action": "show", "target": "qa"}])
s.step("Part a: how many cycles does this code take with stalls only, and with forwarding? Pause and try it.", [{"action": "highlight", "target": "qa.c1"}])
s.step("The ideal is 5 plus 4 minus 1, which is 8 cycles.", [{"action": "highlight", "target": "qa[0]"}])
s.step("There are three RAW hazards, each one apart: the add needs R1, the subtract needs R3, and the store needs R4.", [{"action": "mark_lines", "target": "qcode", "from": 2, "to": 4}])
s.step("Stalls only: 2 each, so 6 stalls and 14 cycles.", [{"action": "set", "target": "qa[1][1]", "value": "6"}, {"action": "set", "target": "qa[1][2]", "value": "14", "delay": 0.4}])
s.step("With forwarding: only the load followed by its use stalls, once. So 1 stall and 9 cycles.", [{"action": "set", "target": "qa[2][1]", "value": "1"}, {"action": "set", "target": "qa[2][2]", "value": "9", "delay": 0.4}])
s.step("Part b: 25 percent of instructions are branches, 40 percent are taken, the penalty is 3, and we predict not taken.", [{"action": "show", "target": "qb"}])
s.step("CPI is 1 plus 0.25 times 0.4 times 3, which is 1.3.", [{"action": "highlight", "target": "qb[0]"}])
s.step("The usual slip in part b is multiplying by the taken fraction when the method is stalling: then every branch pays.", [])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qcode"}, {"action": "hide", "target": "qa"}, {"action": "hide", "target": "qb"}, {"action": "show", "target": "stages"}])
s.step("Stalls work but are slow: 17 cycles instead of 9.", [{"action": "highlight", "target": "stages[0..=1]"}])
s.step("Forwarding passes results straight to the ALU, leaving only the load-use stall: 10 cycles.", [{"action": "highlight", "target": "stages[2..=3]"}])
s.step("Branches are handled by stalling, predicting, deciding earlier or delaying, and their cost is 1 plus branch fraction times penalised fraction times penalty.", [{"action": "highlight", "target": "stages[4..=5]"}])
s.step("Next video: performance metrics, CPU time, CPI and MIPS, with every trap examiners use.", [{"action": "mark", "target": "stages[0..=5]"}, s.take("Next: performance metrics")])

s.save(sys.argv[1])

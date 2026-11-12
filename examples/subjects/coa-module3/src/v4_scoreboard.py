"""Module 3, video 4: dynamic scheduling with a scoreboard (textbook example, traced cycle by cycle)."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from scoreboard import run

LAT = {'L.D': 1, 'S.D': 1, 'ADD.D': 2, 'SUB.D': 2, 'MUL.D': 10, 'DIV.D': 40}
UNITS = {'Integer': 1, 'Mult': 2, 'Add': 1, 'Divide': 1}
P = [('L.D    F6,34(R2)', 'L.D', 'F6', ['R2']), ('L.D    F2,45(R3)', 'L.D', 'F2', ['R3']),
     ('MUL.D  F0,F2,F4', 'MUL.D', 'F0', ['F2', 'F4']), ('SUB.D  F8,F6,F2', 'SUB.D', 'F8', ['F6', 'F2']),
     ('DIV.D  F10,F0,F6', 'DIV.D', 'F10', ['F0', 'F6']), ('ADD.D  F6,F8,F2', 'ADD.D', 'F6', ['F8', 'F2'])]
T = run(P, LAT, UNITS)
assert T == [(1, 2, 3, 4), (5, 6, 7, 8), (6, 9, 19, 20), (7, 9, 11, 12), (8, 21, 61, 62), (13, 14, 16, 22)]
Q = [('L.D    F2,0(R1)', 'L.D', 'F2', ['R1']), ('MUL.D  F4,F2,F0', 'MUL.D', 'F4', ['F2', 'F0']),
     ('L.D    F6,8(R1)', 'L.D', 'F6', ['R1']), ('ADD.D  F8,F4,F6', 'ADD.D', 'F8', ['F4', 'F6']),
     ('SUB.D  F4,F6,F10', 'SUB.D', 'F4', ['F6', 'F10'])]
TQ = run(Q, LAT, UNITS)
assert TQ == [(1, 2, 3, 4), (2, 5, 15, 16), (5, 6, 7, 8), (6, 17, 19, 20), (21, 22, 24, 25)]
# WAW alone would let SUB.D issue right after MUL.D writes (cycle 17); the single adder holds it to 21
assert TQ[1][3] + 1 == 17 and TQ[3][3] + 1 == 21

s = Script("Scoreboarding")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why execute out of order"],
    [2, "The scoreboard's four steps"],
    [3, "Functional units and the three tables"],
    [4, "The example, cycle by cycle"],
    [5, "A snapshot of the tables"],
    [6, "The WAR stall at the end"],
    [7, "What the scoreboard cannot do"],
    [8, "Exam question"]]})
s.obj({"id": "why", "type": "code", "region": "center", "language": "asm", "lines": [
    "DIV.D F0,F2,F4     ; 40 cycles",
    "ADD.D F10,F0,F8    ; needs F0",
    "SUB.D F12,F8,F14   ; needs nothing new"]})
s.obj({"id": "whyx", "type": "table", "region": "center", "columns": ["", "in order", "out of order"], "rows": [
    ["SUB.D", "waits behind ADD.D", "starts at once"],
    ["new risk", "none", "WAR and WAW hazards"]]})
s.obj({"id": "steps", "type": "table", "region": "center", "columns": ["step", "waits until", "checks for"], "rows": [
    ["1 Issue", "its unit is free, and no active writer of its destination", "structural, WAW"],
    ["2 Read operands", "every source has been written", "RAW"],
    ["3 Execute", "the latency has passed", "–"],
    ["4 Write result", "no earlier instruction still has to read it", "WAR"]]})
s.obj({"id": "fu", "type": "table", "region": "center", "columns": ["functional unit", "how many", "execution cycles"], "rows": [
    ["integer (loads and stores)", "1", "1"],
    ["FP multiplier", "2", "10"],
    ["FP adder (add and subtract)", "1", "2"],
    ["FP divider", "1", "40"]]})
s.obj({"id": "tabs", "type": "table", "region": "center", "columns": ["table", "holds"], "rows": [
    ["instruction status", "the cycle each instruction finishes each step"],
    ["functional unit status", "per unit: busy, op, Fi, Fj, Fk, Qj, Qk, Rj, Rk"],
    ["register result status", "per register: which unit will write it next"]]})
s.obj({"id": "code", "type": "code", "region": "center", "language": "asm", "lines": [p[0] for p in P]})
s.obj({"id": "is", "type": "table", "region": "center", "columns": ["instruction", "issue", "read operands", "execution complete", "write result"], "rows": [
    [p[0], "", "", "", ""] for p in P]})
s.obj({"id": "fs", "type": "table", "region": "center", "columns": ["unit", "busy", "op", "Fi", "Fj", "Fk", "Qj", "Qk", "Rj", "Rk"], "rows": [
    ["Integer", "no", "", "", "", "", "", "", "", ""],
    ["Mult1", "yes", "MUL.D", "F0", "F2", "F4", "", "", "no", "no"],
    ["Mult2", "no", "", "", "", "", "", "", "", ""],
    ["Add", "no", "", "", "", "", "", "", "", ""],
    ["Divide", "yes", "DIV.D", "F10", "F0", "F6", "Mult1", "", "no", "yes"]]})
s.obj({"id": "rs", "type": "table", "region": "center", "columns": ["register", "F0", "F2", "F4", "F6", "F8", "F10"], "rows": [
    ["written by", "Mult1", "", "", "", "", "Divide"]]})
s.obj({"id": "lim", "type": "table", "region": "center", "columns": ["limit", "in our example"], "rows": [
    ["no forwarding", "read only the cycle after the write"],
    ["WAW stalls issue", "a second writer cannot even start"],
    ["WAR stalls write", "ADD.D done in 16, written in 22"],
    ["few units", "the second load waited to issue"],
    ["in-order issue", "one blocked issue stops all behind it"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "asm", "lines": [p[0] for p in Q]})
s.obj({"id": "qt", "type": "table", "region": "center", "columns": ["instruction", "issue", "read operands", "execution complete", "write result"], "rows": [
    [p[0], "", "", "", ""] for p in Q]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
cell = lambda tb, i, k, tt=T, d=0: st(f"{tb}[{i}][{k + 1}]", str(tt[i][k]), d)

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("So far the compiler arranged the instructions. Now the hardware does it, while the program runs, letting instructions start as soon as their operands are ready. The first such design was the scoreboard, in the CDC 6600 of 1964.", [s.head("Scoreboarding")])
s.step("Here are the eight stages.", show("stages"))
s.step("Why execute out of order, the scoreboard's four steps, and its units and tables.", [hl("stages[0..=2]")])
s.step("Then the textbook example cycle by cycle, a snapshot of the tables, the WAR stall, the limits, and an exam question.", [hl("stages[3..=7]")])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: a divide takes 40 cycles. The add needs its result, so the add must wait.", [s.head("Stage 1 of 8: why out of order")] + hide("stages") + show("why") + [go("why", 2)])
s.step("But the subtract needs nothing from either. In an in-order pipeline it is stuck behind the add anyway, for 40 cycles.", [go("why", 3)])
s.step("Compare the two ways of running it.", hide("why") + show("whyx") + [hl("whyx[0][1]")])
s.step("Dynamic scheduling lets the subtract go ahead. Instructions issue in order, but execute as soon as their operands are ready.", [hl("whyx[0][2]")])
s.step("The price: once instructions finish out of order, WAR and WAW hazards become real. If the subtract wrote F8 before the add had read it, the add would get the wrong value.", [hl("whyx[1]")])
s.step("So the hardware must track every instruction in flight. That bookkeeping is the scoreboard.", [s.take("issue in order · execute out of order · watch for RAW, WAR and WAW")])

# ---------------------------------------------------------------- steps
s.scene("steps")
s.step("Stage 2: the scoreboard splits the decode stage in two, and every instruction passes through four steps.", [s.head("Stage 2 of 8: four steps"), s.untake()] + hide("whyx") + show("steps"))
s.step("Issue: the instruction waits until its functional unit is free, and until no active instruction is going to write the same destination. That check stops structural and WAW hazards.", [hl("steps[0]")])
s.step("Read operands: it waits until every source register has been written by its producer. That is where RAW hazards are resolved, and why instructions can now start out of order.", [hl("steps[1]")])
s.step("Execute: the unit takes its latency, then tells the scoreboard it has finished.", [hl("steps[2]")])
s.step("Write result: before writing, it waits until no earlier instruction still needs to read the old value of that register. That check stops WAR hazards.", [hl("steps[3]"), s.take("issue: structural, WAW · read: RAW · write: WAR")])

# ---------------------------------------------------------------- units and tables
s.scene("units")
s.step("Stage 3: our machine has one integer unit for loads, two FP multipliers, one FP adder, and one FP divider.", [s.head("Stage 3 of 8: units and tables"), s.untake()] + hide("steps") + show("fu"))
s.step("A load takes 1 execution cycle, an add 2, a multiply 10, and a divide 40.", [hl("fu[0..=3]")])
s.step("The scoreboard keeps three tables. Instruction status records when each instruction completes each step.", hide("fu") + show("tabs") + [hl("tabs[0]")])
s.step("Functional unit status has a row per unit: whether it is busy, its operation, its destination Fi, its sources Fj and Fk, the units Qj and Qk that will produce those sources, and flags Rj and Rk saying whether they are ready.", [hl("tabs[1]")])
s.step("And register result status records, for each register, which unit will write it next. Blank means the value in the register file is current.", [hl("tabs[2]"), s.take("three tables: instructions, units, registers")])

# ---------------------------------------------------------------- trace
s.scene("trace")
s.step("Stage 4: the textbook's example. Two loads, a multiply, a subtract, a divide and an add.", [s.head("Stage 4 of 8: the example"), s.untake()] + hide("tabs") + show("code") + [ml("code", 1, 6)])
s.step("Look at the dependences: the multiply and subtract need F2 from the second load. The divide needs F0 from the multiply. And the add writes F6, which the subtract and divide read: a WAR waiting to happen.", [go("code", 3), go("code", 5), go("code", 6)])
s.step("Now the instruction status table. Cycles 1 to 4: the first load issues, reads R2, executes and writes F6.", hide("code") + show("is") + [cell("is", 0, 0), cell("is", 0, 1, d=0.2), cell("is", 0, 2, d=0.4), cell("is", 0, 3, d=0.6)])
s.step("The second load cannot issue in cycle 2: the one integer unit is busy. A structural stall. It issues in 5, after the first load frees the unit, and writes F2 in 8.", [hl("is[1]"), cell("is", 1, 0), cell("is", 1, 1, d=0.3), cell("is", 1, 2, d=0.5), cell("is", 1, 3, d=0.7)])
s.step("The multiply issues in 6, to a free multiplier. The subtract issues in 7, the divide in 8. Each has a free unit, so issue keeps flowing.", [cell("is", 2, 0), cell("is", 3, 0, d=0.3), cell("is", 4, 0, d=0.6)])
s.step("But the multiply and the subtract both need F2, written in cycle 8. So both read their operands in cycle 9.", [cell("is", 2, 1), cell("is", 3, 1, d=0.3), hl("is[1][4]", 0.5)])
s.step("The subtract takes 2 cycles: done in 11, and it writes F8 in 12.", [cell("is", 3, 2), cell("is", 3, 3, d=0.4)])
s.step("The add needs the adder, so it could not issue until the subtract freed it. It issues in 13, reads in 14, and finishes executing in 16.", [cell("is", 5, 0), cell("is", 5, 1, d=0.3), cell("is", 5, 2, d=0.6)])
s.step("Notice: the add has finished, while the multiply issued before it is still executing. Out-of-order completion.", [hl("is[5][3]"), hl("is[2]", 0.3)])
s.step("The multiply takes 10 cycles from 9: complete in 19, written in 20.", [cell("is", 2, 2), cell("is", 2, 3, d=0.4)])
s.step("The divide has been waiting for F0 since cycle 8. It reads in 21, executes for 40 cycles to 61, and writes in 62.", [cell("is", 4, 1), cell("is", 4, 2, d=0.3), cell("is", 4, 3, d=0.6)])
s.step("One cell is left: when does the add write F6? It finished in 16, so why not 17? The next stage answers that.", [hl("is[5][4]"), s.take("every instruction: issue → read → execute → write")])

# ---------------------------------------------------------------- snapshot
s.scene("snap")
s.step("Stage 5: a snapshot of the other two tables, at the end of cycle 12.", [s.head("Stage 5 of 8: a snapshot at cycle 12"), s.untake()] + hide("is") + show("fs"))
s.step("The integer unit is free: both loads are done. The adder is free too: the subtract wrote in 12.", [hl("fs[0]"), hl("fs[3]", 0.4)])
s.step("Mult1 holds the multiply: destination F0, sources F2 and F4. It has already read them, so Rj and Rk are reset to no, and it is executing.", [hl("fs[1]")])
s.step("The divider holds the divide: destination F10, sources F0 and F6. F6 is ready, Rk yes. But F0 will come from Mult1, so Qj says Mult1, and Rj is no. It waits.", [hl("fs[4]")])
s.step("And the register result status: F0 will be written by Mult1, and F10 by the divider. Every other register holds its current value.", hide("fs") + show("rs") + [hl("rs[0][1]"), hl("rs[0][6]", 0.4), s.take("Qj, Qk: who will produce my operands · Rj, Rk: are they ready")])

# ---------------------------------------------------------------- WAR
s.scene("war")
s.step("Stage 6: the add finished in 16, and wants to write F6. But the divide still has to read the old F6, and it does not read its operands until cycle 21.", [s.head("Stage 6 of 8: the WAR stall"), s.untake()] + hide("rs") + show("is") + [hl("is[4][2]"), hl("is[5][3]", 0.4)])
s.step("If the add wrote in 17, the divide would later read the add's new F6, which is wrong. So the scoreboard holds the add's write until cycle 22, the cycle after the divide reads.", [cell("is", 5, 3), mk("is[5][4]", 0.3)])
s.step("The complete table: the divide ends the sequence in 62. Out of order, but every value is correct.", [hl("is"), s.take("WAR: hold the write until earlier readers have read")])

# ---------------------------------------------------------------- limits
s.scene("limits")
s.step("Stage 7: what the scoreboard cannot do.", [s.head("Stage 7 of 8: the limits"), s.untake()] + hide("is") + show("lim"))
s.step("There is no forwarding. A result goes into the register file, and a waiting instruction reads it the next cycle.", [hl("lim[0]")])
s.step("WAW hazards stall issue, and WAR hazards stall the write: the add sat idle from 16 to 22.", [hl("lim[1]"), hl("lim[2]", 0.4)])
s.step("Structural limits: with one integer unit, the second load waited 3 cycles to issue.", [hl("lim[3]")])
s.step("And issue is in order. Once one instruction cannot issue, nothing behind it can either, however independent. All these name stalls disappear with register renaming, which is Tomasulo's idea, next video.", [hl("lim[4]"), s.take("the scoreboard detects WAR and WAW, but only by stalling")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("lim") + show("q") + [ml("q", 1, 5)])
s.step("Same units and latencies. Fill the instruction status table for these five instructions, and explain why the subtract issues so late. Pause and work it out.", [go("q", 5)])
s.step("The first load: 1, 2, 3, 4. The multiply issues in 2, but needs F2 from the load, written in 4. It reads in 5, completes in 15, writes in 16.", hide("q") + show("qt") + [cell("qt", 0, k, TQ, round(0.1 * k, 2)) for k in range(4)] + [cell("qt", 1, k, TQ, round(0.5 + 0.12 * k, 2)) for k in range(4)])
s.step("The second load waits for the integer unit: issue 5, then 6, 7, 8.", [cell("qt", 2, k, TQ, 0.15 * k) for k in range(4)])
s.step("The add issues in 6, but needs F4 from the multiply, written in 16. It reads in 17, completes in 19, writes in 20.", [cell("qt", 3, k, TQ, 0.15 * k) for k in range(4)])
s.step("The subtract writes F4, like the multiply: a WAW hazard. That alone would let it issue in 17, after the multiply writes. But it also needs the only adder, held by the add until cycle 20. So it issues in 21, reads in 22, completes in 24, and writes in 25.", [cell("qt", 4, k, TQ, round(0.2 * k, 2)) for k in range(4)] + [hl("qt[4]", 0.8)])
s.step("Its write is safe: the add, the only earlier reader of F4, read it in 17. The usual slip: checking only one reason for a stall. Here both WAW and the busy adder hold the subtract back.", [s.take("a stall can have several causes: check every one")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt") + show("stages"))
s.step("The scoreboard issues in order, reads operands when they are ready, and executes out of order.", [hl("stages[0..=3]")])
s.step("Its tables track units and registers. It handles WAR and WAW correctly, but only by stalling.", [hl("stages[4..=6]")])
s.step("Next video: Tomasulo's algorithm, which removes those stalls by renaming registers in hardware.", [mk("stages[0..=7]"), s.take("Next: Tomasulo's algorithm")])

s.save("/home/claude/playlist/m3/m3v4.json")

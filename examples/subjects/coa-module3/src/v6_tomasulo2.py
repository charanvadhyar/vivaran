"""Module 3, video 6: Tomasulo's algorithm, part 2: the full trace, a loop with two iterations in flight, memory ordering."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from tomasulo import run

LAT = {'L.D': 1, 'S.D': 1, 'ADD.D': 2, 'SUB.D': 2, 'MUL.D': 10, 'DIV.D': 40}
P = [('L.D    F6,34(R2)', 'L.D', 'F6', ['R2']), ('L.D    F2,45(R3)', 'L.D', 'F2', ['R3']),
     ('MUL.D  F0,F2,F4', 'MUL.D', 'F0', ['F2', 'F4']), ('SUB.D  F8,F6,F2', 'SUB.D', 'F8', ['F6', 'F2']),
     ('DIV.D  F10,F0,F6', 'DIV.D', 'F10', ['F0', 'F6']), ('ADD.D  F6,F8,F2', 'ADD.D', 'F6', ['F8', 'F2'])]
NM, T = run(P, LAT)
assert NM == ['Load1', 'Load2', 'Mult1', 'Add1', 'Mult2', 'Add2']
assert T == [(1, 2, 2, 3), (2, 3, 3, 4), (3, 5, 14, 15), (4, 5, 6, 7), (5, 16, 55, 56), (6, 8, 9, 10)]
Q = [('L.D    F2,0(R1)', 'L.D', 'F2', ['R1']), ('MUL.D  F4,F2,F0', 'MUL.D', 'F4', ['F2', 'F0']),
     ('L.D    F6,8(R1)', 'L.D', 'F6', ['R1']), ('ADD.D  F8,F4,F6', 'ADD.D', 'F8', ['F4', 'F6']),
     ('SUB.D  F4,F6,F10', 'SUB.D', 'F4', ['F6', 'F10'])]
NQ, TQ = run(Q, LAT)
assert NQ == ['Load1', 'Mult1', 'Load2', 'Add1', 'Add2']
assert TQ == [(1, 2, 2, 3), (2, 4, 13, 14), (3, 4, 4, 5), (4, 15, 16, 17), (5, 6, 7, 8)]
assert (62 - 56, 25 - 17) == (6, 8)

ex = lambda a, b: f"{a}" if a == b else f"{a}–{b}"
s = Script("Tomasulo's algorithm, part 2")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The timing rules"],
    [2, "The example, cycle by cycle"],
    [3, "A snapshot at cycle 6"],
    [4, "Against the scoreboard"],
    [5, "A loop: two iterations in flight"],
    [6, "Loads and stores to the same address"],
    [7, "Exam question"]]})
s.obj({"id": "rules", "type": "table", "region": "center", "columns": ["step", "timing rule"], "rows": [
    ["issue", "in order, one per cycle, if a station of the right kind is free"],
    ["execute", "starts the cycle after the last operand appears on the CDB"],
    ["write", "the cycle after execution ends; one result per cycle on the CDB"],
    ["stations", "3 load, 3 store, 3 add, 2 multiply/divide"],
    ["latencies", "load 1, add 2, multiply 10, divide 40"]]})
s.obj({"id": "code", "type": "code", "region": "center", "language": "asm", "lines": [p[0] for p in P]})
s.obj({"id": "is", "type": "table", "region": "center", "columns": ["instruction", "station", "issue", "execute", "write result"], "rows": [
    [P[i][0], NM[i], "", "", ""] for i in range(6)]})
s.obj({"id": "rs", "type": "table", "region": "center", "columns": ["station", "busy", "op", "Vj", "Vk", "Qj", "Qk"], "rows": [
    ["Load1", "no", "", "", "", "", ""],
    ["Load2", "no", "", "", "", "", ""],
    ["Add1", "yes", "SUB.D", "Mem[34+R2]", "Mem[45+R3]", "", ""],
    ["Add2", "yes", "ADD.D", "", "Mem[45+R3]", "Add1", ""],
    ["Mult1", "yes", "MUL.D", "Mem[45+R3]", "Regs[F4]", "", ""],
    ["Mult2", "yes", "DIV.D", "", "Mem[34+R2]", "Mult1", ""]]})
s.obj({"id": "rg", "type": "table", "region": "center", "columns": ["register", "F0", "F2", "F4", "F6", "F8", "F10"], "rows": [
    ["Qi", "Mult1", "", "", "Add2", "Add1", "Mult2"]]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["", "scoreboard", "Tomasulo"], "rows": [
    ["SUB.D reads operands", "cycle 9", "starts executing in 5"],
    ["ADD.D writes F6", "cycle 22: held by the WAR", "cycle 10: no WAR"],
    ["last result (DIV.D)", "cycle 62", "cycle 56"]]})
s.obj({"id": "lp", "type": "code", "region": "left", "language": "asm", "lines": [
    "Loop: L.D    F0,0(R1)",
    "      MUL.D  F4,F0,F2",
    "      S.D    F4,0(R1)",
    "      DADDUI R1,R1,#-8",
    "      BNE    R1,R2,Loop"]})
s.obj({"id": "lrs", "type": "table", "region": "right", "columns": ["station", "op", "address or operands", "waits for"], "rows": [
    ["Load1", "L.D", "R1", ""],
    ["Mult1", "MUL.D", "F2", "Load1"],
    ["Store1", "S.D", "R1", "Mult1"],
    ["Load2", "L.D", "R1 − 8", ""],
    ["Mult2", "MUL.D", "F2", "Load2"],
    ["Store2", "S.D", "R1 − 8", "Mult2"]]})
s.obj({"id": "lrg", "type": "table", "region": "bottom", "columns": ["register", "F0", "F4"], "rows": [["Qi", "Load2", "Mult2"]]})
s.obj({"id": "mem", "type": "table", "region": "center", "columns": ["case", "rule"], "rows": [
    ["load after store", "same address: the load waits (RAW)"],
    ["store after load", "same address: the store waits (WAR)"],
    ["store after store", "same address: keep the order (WAW)"],
    ["how", "addresses in program order, compared with pending ones"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "asm", "lines": [p[0] for p in Q]})
s.obj({"id": "qt", "type": "table", "region": "center", "columns": ["instruction", "station", "issue", "execute", "write result"], "rows": [
    [Q[i][0], NQ[i], "", "", ""] for i in range(5)]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}


def fill(tb, i, tt, d=0.0):
    a, b, c, w = tt[i]
    out = [st(f"{tb}[{i}][2]", str(a), d), st(f"{tb}[{i}][3]", ex(b, c), round(d + 0.25, 2))]
    if w is not None:
        out.append(st(f"{tb}[{i}][4]", str(w), round(d + 0.5, 2)))
    return out


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Last video built Tomasulo's machine. Now we run it: the same six instructions the scoreboard ran, cycle by cycle, then a loop, then memory. Watch the WAR stall vanish.", [s.head("Tomasulo's algorithm, part 2")])
s.step("Here are the seven stages.", show("stages"))
s.step("The timing rules, the trace, a snapshot of the stations, and the comparison with the scoreboard.", [hl("stages[0..=3]")])
s.step("Then a loop with two iterations in flight, loads and stores to the same address, and an exam question.", [hl("stages[4..=6]")])

# ---------------------------------------------------------------- rules
s.scene("rules")
s.step("Stage 1: the rules. Issue is in order, one instruction per cycle, as long as a station of the right kind is free.", [s.head("Stage 1 of 7: the timing rules")] + hide("stages") + show("rules") + [hl("rules[0]")])
s.step("Execution starts the cycle after the last operand appears on the common data bus. If both operands are ready at issue, it starts the very next cycle.", [hl("rules[1]")])
s.step("A result is written, on the bus, the cycle after execution ends. Only one result can use the bus each cycle.", [hl("rules[2]")])
s.step("Three load buffers, three store buffers, three add stations and two for multiply and divide. And the same latencies as the scoreboard video, so we can compare.", [hl("rules[3..=4]"), s.take("issue → execute when operands arrive → write on the CDB")])

# ---------------------------------------------------------------- trace
s.scene("trace")
s.step("Stage 2: the six instructions again.", [s.head("Stage 2 of 7: cycle by cycle"), s.untake()] + hide("rules") + show("code") + [ml("code", 1, 6)])
s.step("Now the status table. Each instruction is shown with the station it gets.", hide("code") + show("is"))
s.step("The first load: issued in 1, into Load1. It computes its address and reads memory in cycle 2, and writes F6 on the bus in 3.", fill("is", 0, T))
s.step("The second load: issued in 2. There are three load buffers, so no structural stall this time. It executes in 3, writes F2 in 4.", fill("is", 1, T))
s.step("The multiply issues in 3, into Mult1. F4 is ready and copied; F2 comes from Load2, so Qj is Load2. It hears F2 on the bus in cycle 4 and starts in 5.", [st("is[2][2]", "3"), hl("is[1][4]", 0.4), st("is[2][3]", "5–14", 0.7)])
s.step("It runs 10 cycles, 5 to 14, and writes F0 in 15.", [st("is[2][4]", "15")])
s.step("The subtract issues in 4, into Add1. F6 was written in 3, so its value is copied straight away. F2 arrives in 4. It executes in 5 and 6, and writes F8 in 7.", fill("is", 3, T))
s.step("The divide issues in 5, into Mult2. F6 is copied at issue: the old F6, from the first load. F0 must come from Mult1, so it waits for cycle 15.", [st("is[4][2]", "5"), hl("is[2][4]", 0.5)])
s.step("It starts in 16, runs 40 cycles to 55, and writes F10 in 56.", [st("is[4][3]", "16–55"), st("is[4][4]", "56", 0.5)])
s.step("The add issues in 6, into Add2. F8 comes from Add1 in cycle 7, so it starts in 8, finishes in 9, and writes F6 in 10.", fill("is", 5, T))
s.step("Cycle 10, not 22. The add overwrites F6 while the divide still has not started. That is safe, because the divide copied the old F6 at issue, five cycles earlier.", [hl("is[5][4]"), hl("is[4][3]", 0.4)])
s.step("And the whole sequence ends in cycle 56.", [mk("is[4][4]"), s.take("ADD.D writes in 10: the WAR stall is gone")])

# ---------------------------------------------------------------- snapshot
s.scene("snap")
s.step("Stage 3: the stations at the end of cycle 6, when all six have issued.", [s.head("Stage 3 of 7: a snapshot at cycle 6"), s.untake()] + hide("is") + show("rs"))
s.step("Both loads are done: their buffers are free again.", [hl("rs[0..=1]")])
s.step("Add1 holds the subtract. Both its operands are values, copied from the loads' broadcasts. It is finishing execution.", [hl("rs[2]")])
s.step("Add2 holds the add. F2's value is in Vk; F8 will come from Add1.", [hl("rs[3]")])
s.step("Mult1 is executing the multiply. Mult2 holds the divide, with the old F6 value in Vk, waiting for tag Mult1 for F0.", [hl("rs[4]"), hl("rs[5]", 0.4)])
s.step("And the register status: F0 from Mult1, F6 from Add2, F8 from Add1, F10 from Mult2. F6 points at the add, the latest writer, while the divide keeps its own copy of the old value.", hide("rs") + show("rg") + [hl("rg[0][4]"), s.take("old values live in stations · registers wait for the latest tag")])

# ---------------------------------------------------------------- compare
s.scene("cmp")
s.step("Stage 4: against the scoreboard.", [s.head("Stage 4 of 7: against the scoreboard"), s.untake()] + hide("rg") + show("cmp"))
s.step("The subtract: the scoreboard read its operands in cycle 9. Tomasulo had them off the bus and was executing in 5.", [hl("cmp[0]")])
s.step("The add's write: cycle 22 with the scoreboard, held by the WAR on F6. Cycle 10 with Tomasulo.", [hl("cmp[1]")])
s.step("And the last result: 62 against 56. Some of that is the extra load buffers, and the bus forwarding results directly; the rest is renaming.", [hl("cmp[2]"), s.take("same code, same latencies: 62 → 56 cycles")])

# ---------------------------------------------------------------- loop
s.scene("loop")
s.step("Stage 5: the real power shows in loops. This loop multiplies every element by F2.", [s.head("Stage 5 of 7: two iterations in flight"), s.untake()] + hide("cmp") + show("lp") + [ml("lp", 1, 5)])
s.step("Suppose the branch is predicted taken, and two full iterations issue before any floating-point operation finishes.", show("lrs"))
s.step("Iteration 1: the load takes Load1, the multiply Mult1, waiting for Load1, and the store Store1, waiting for Mult1.", [hl("lrs[0..=2]")])
s.step("Iteration 2 uses the very same register names, F0 and F4. But it gets different stations: Load2, Mult2 and Store2, with the address R1 minus 8.", [hl("lrs[3..=5]")])
s.step("The register status shows only the latest writers: F0 from Load2, F4 from Mult2. The two iterations never interfere.", show("lrg") + [hl("lrg[0]")])
s.step("This is loop unrolling done by the hardware, while the program runs. Renaming through stations gives each iteration its own registers, with no compiler involved.", hide("lrg") + [mk("lrs[0..=5]"), s.take("dynamic unrolling: each iteration gets its own stations")])

# ---------------------------------------------------------------- memory
s.scene("mem")
s.step("Stage 6: there is one danger left. Two iterations' loads and stores might touch the same address.", [s.head("Stage 6 of 7: memory ordering"), s.untake()] + hide("lp", "lrs") + show("mem"))
s.step("A load after an earlier store to the same address must wait for the store. That is a RAW hazard through memory.", [hl("mem[0]")])
s.step("A store after an earlier load to the same address must wait until the load has read, and stores to the same address keep their order. WAR and WAW through memory.", [hl("mem[1]"), hl("mem[2]", 0.4)])
s.step("The fix: compute effective addresses in program order, and compare each new address against all pending loads and stores before letting it go.", [hl("mem[3]"), s.take("registers are renamed · memory addresses must be compared")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question: the same five instructions as in the scoreboard exam.", [s.head("Exam question"), s.untake()] + hide("mem") + show("q") + [ml("q", 1, 5)])
s.step("Fill the Tomasulo status table, compare the finish with the scoreboard's 25, and say what value F4 ends with. Pause and work it out.", [go("q", 5)])
s.step("The first load: 1, executes in 2, writes F2 in 3. The multiply issues in 2, waits for F2, executes 4 to 13, writes F4 in 14.", hide("q") + show("qt") + fill("qt", 0, TQ) + fill("qt", 1, TQ, 0.4))
s.step("The second load: issue 3, execute 4, write F6 in 5.", fill("qt", 2, TQ))
s.step("The add issues in 4. Its F4 comes from Mult1, written in 14. It executes 15 and 16, writes in 17.", fill("qt", 3, TQ))
s.step("The subtract issues in 5. No WAW stall, and a free add station, Add2. F6 arrives in 5, so it executes 6 and 7, and writes F4 in 8.", fill("qt", 4, TQ))
s.step("Everything is done by cycle 17, against 25 for the scoreboard.", [mk("qt[3][4]")])
s.step("And F4? The subtract issued last, so F4's status points to Add2. In cycle 8 the subtract's value goes into F4. In 14, the multiply broadcasts tag Mult1: the add takes it, but F4 ignores it. F4 ends with the subtract's value, as the program requires.", [hl("qt[4]"), hl("qt[1][4]", 0.5), s.take("the latest writer wins, even when it finishes first")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt") + show("stages"))
s.step("Instructions issue in order, execute when their operands arrive on the bus, and write one per cycle. The WAR stall vanished: 62 cycles became 56.", [hl("stages[0..=3]")])
s.step("Stations give each loop iteration its own names, and memory addresses are checked to keep loads and stores safe.", [hl("stages[4..=5]")])
s.step("Next video: dynamic branch prediction, because none of this pays off if we stop at every branch.", [mk("stages[0..=6]"), s.take("Next: dynamic branch prediction")])

s.save("/home/claude/playlist/m3/m3v6.json")

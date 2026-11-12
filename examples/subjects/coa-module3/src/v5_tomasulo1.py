"""Module 3, video 5: Tomasulo's algorithm, part 1: reservation stations, renaming with tags, the common data bus."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

s = Script("Tomasulo's algorithm, part 1")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The idea: rename registers in hardware"],
    [2, "The structure"],
    [3, "Three steps: issue, execute, write result"],
    [4, "What a reservation station holds"],
    [5, "Renaming, watched entry by entry"],
    [6, "How WAR and WAW disappear"],
    [7, "Tomasulo against the scoreboard"],
    [8, "Exam question"]]})
s.obj({"id": "idea", "type": "table", "region": "center", "columns": ["idea", "what it does"], "rows": [
    ["reservation stations", "buffers in front of each unit hold waiting instructions and their operands"],
    ["copy operands at issue", "a ready value is copied in at once: later writes to the register cannot hurt it"],
    ["name results by station", "a missing operand is named by the station that will produce it: a tag"],
    ["common data bus", "every result is broadcast with its tag; everyone waiting for that tag grabs it"]]})
s.obj({"id": "dg", "type": "diagram", "region": "center", "layout": "layers", "direction": "down",
       "nodes": [
           {"id": "iq", "label": "instruction queue"},
           {"id": "lb", "label": "load buffers"}, {"id": "ars", "label": "add stations"}, {"id": "mrs", "label": "mult stations"},
           {"id": "mem", "label": "memory"}, {"id": "add", "label": "FP adder"}, {"id": "mul", "label": "FP multiplier"},
           {"id": "cdb", "label": "common data bus"},
           {"id": "reg", "label": "FP registers"}],
       "edges": [
           {"from": "iq", "to": "lb"}, {"from": "iq", "to": "ars"}, {"from": "iq", "to": "mrs"},
           {"from": "lb", "to": "mem"}, {"from": "ars", "to": "add"}, {"from": "mrs", "to": "mul"},
           {"from": "mem", "to": "cdb"}, {"from": "add", "to": "cdb"}, {"from": "mul", "to": "cdb"},
           {"from": "cdb", "to": "reg"}]})
s.obj({"id": "st3", "type": "table", "region": "center", "columns": ["step", "what happens"], "rows": [
    ["1 Issue", "needs a free station; copy each ready operand, or note its producer's tag"],
    ["", "mark the destination register with this station's tag"],
    ["2 Execute", "once both operands have arrived from the CDB, run"],
    ["3 Write result", "broadcast value and tag; everyone waiting for that tag takes it"]]})
s.obj({"id": "rsf", "type": "table", "region": "center", "columns": ["field", "meaning"], "rows": [
    ["Busy, Op", "in use, and the operation"],
    ["Vj, Vk", "operand values, once known"],
    ["Qj, Qk", "tags of the stations that will produce them (blank = value is in V)"],
    ["A", "address, for loads and stores"],
    ["register status Qi", "for each register, the station that will write it (blank = register file is current)"]]})
s.obj({"id": "rc", "type": "code", "region": "left", "language": "asm", "lines": [
    "DIV.D F0,F2,F4",
    "ADD.D F6,F0,F8",
    "S.D   F6,0(R1)",
    "SUB.D F8,F10,F14",
    "MUL.D F6,F10,F8"]})
s.obj({"id": "rt", "type": "table", "region": "right", "columns": ["station", "op", "Vj", "Vk", "Qj", "Qk"], "rows": [
    ["Mult1", "", "", "", "", ""], ["Add1", "", "", "", "", ""], ["Store1", "", "", "", "", ""],
    ["Add2", "", "", "", "", ""], ["Mult2", "", "", "", "", ""]]})
s.obj({"id": "rg", "type": "table", "region": "bottom", "columns": ["register", "F0", "F6", "F8"], "rows": [
    ["Qi", "", "", ""]]})
s.obj({"id": "hz", "type": "table", "region": "center", "columns": ["hazard", "how it is removed"], "rows": [
    ["WAR on F8", "ADD.D copied the old F8 at issue"],
    ["WAW on F6", "F6 waits only for Mult2; Add1's value goes to the store"],
    ["RAW: S.D needs F6", "S.D waits for tag Add1 on the CDB"]]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["", "scoreboard", "Tomasulo"], "rows": [
    ["RAW", "wait, then read the register file", "wait for the tag on the CDB: forwarding built in"],
    ["WAR", "stall the write", "gone: operands copied at issue"],
    ["WAW", "stall issue", "gone: only the latest writer updates the register"],
    ["hazard detection", "one central scoreboard", "spread over the stations"],
    ["limit", "functional units", "stations, and one CDB per cycle"]]})
s.obj({"id": "q", "type": "code", "region": "left", "language": "asm", "lines": [
    "L.D   F2,0(R1)",
    "MUL.D F4,F2,F6",
    "ADD.D F2,F8,F10",
    "SUB.D F6,F4,F2"]})
s.obj({"id": "qx", "type": "table", "region": "right", "columns": ["all four issue; nothing has finished. Find:"], "rows": [
    ["a) each station's V and Q fields"], ["b) the register status"], ["c) which name hazards were removed, and how"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["station", "instruction", "Vj", "Vk", "Qj", "Qk"], "rows": [
    ["Load1", "L.D F2", "", "", "", ""],
    ["Mult1", "MUL.D F4", "", "Regs[F6]", "Load1", ""],
    ["Add1", "ADD.D F2", "Regs[F8]", "Regs[F10]", "", ""],
    ["Add2", "SUB.D F6", "", "", "Mult1", "Add1"]]})
s.obj({"id": "qr", "type": "table", "region": "center", "columns": ["register", "F2", "F4", "F6"], "rows": [
    ["Qi", "Add1", "Mult1", "Add2"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}


def row(r, vals, d=0.0):
    out = []
    for k, v in enumerate(vals):
        if v:
            out.append(st(f"rt[{r}][{k + 1}]", v, round(min(0.9, d + 0.1 * k), 2)))
    return out


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("The scoreboard found WAR and WAW hazards, but could only stall for them. Robert Tomasulo, at IBM in 1967, removed them entirely, by renaming registers in hardware. His algorithm is the heart of every out-of-order processor today.", [s.head("Tomasulo's algorithm, part 1")])
s.step("Here are the eight stages.", show("stages"))
s.step("The idea, the structure, the three steps, and what a reservation station holds.", [hl("stages[0..=3]")])
s.step("Then renaming watched entry by entry, how WAR and WAW disappear, a comparison with the scoreboard, and an exam question. The full cycle-by-cycle trace is the next video.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- idea
s.scene("idea")
s.step("Stage 1: four ideas.", [s.head("Stage 1 of 8: the idea")] + hide("stages") + show("idea"))
s.step("Each functional unit gets a set of reservation stations: buffers where instructions wait, along with their operands.", [hl("idea[0]")])
s.step("When an instruction issues, any operand that is already available is copied into its station immediately. Later writes to that register cannot disturb it.", [hl("idea[1]")])
s.step("An operand not yet available is named by the station that will produce it. That name, the tag, replaces the register name. That is renaming.", [hl("idea[2]")])
s.step("And every result is broadcast on a common data bus, with its tag. Every station waiting for that tag grabs the value at once. Forwarding comes for free.", [hl("idea[3]"), s.take("stations hold operands · tags replace register names · the CDB broadcasts")])

# ---------------------------------------------------------------- structure
s.scene("struct")
s.step("Stage 2: the structure. Instructions leave an instruction queue in order.", [s.head("Stage 2 of 8: the structure"), s.untake()] + hide("idea") + show("dg") + [hl("dg.iq")])
s.step("Each goes to a station of the right kind: load buffers, add stations, or multiply stations, which also handle divides.", [hl("dg.lb"), hl("dg.ars", 0.2), hl("dg.mrs", 0.4)])
s.step("A station sends its instruction to the unit once both operands are present. So instructions execute out of order.", [hl("dg.add"), hl("dg.mul", 0.2), hl("dg.mem", 0.4)])
s.step("Results go onto the common data bus.", [hl("dg.cdb"), hl("dg.add->cdb", 0.2), hl("dg.mul->cdb", 0.4)])
s.step("From the bus they reach the registers, and also every station that is waiting for them. The bus is the only path for results.", [hl("dg.reg"), hl("dg.cdb->reg", 0.3), s.take("queue → stations → units → CDB → registers and stations")])

# ---------------------------------------------------------------- three steps
s.scene("steps")
s.step("Stage 3: every instruction goes through three steps.", [s.head("Stage 3 of 8: three steps"), s.untake()] + hide("dg") + show("st3"))
s.step("Issue: take the next instruction, in order, if a station of its kind is free. For each source: if the value is ready, copy it; if not, record the tag of the station producing it. Then mark the destination register with this station's tag.", [hl("st3[0]"), hl("st3[1]", 0.6)])
s.step("If no station is free, issue stalls: that is the only structural stall left.", [mk("st3[0..=1]")])
s.step("Execute: watch the CDB until both operands have arrived, then run. RAW hazards are resolved here, by waiting.", [hl("st3[2]")])
s.step("Write result: put the value and the tag on the CDB. Every station and register waiting for that tag takes the value, and the station is freed.", [hl("st3[3]"), s.take("issue: rename · execute: wait for RAW · write: broadcast")])

# ---------------------------------------------------------------- fields
s.scene("fields")
s.step("Stage 4: what does a station hold?", [s.head("Stage 4 of 8: station fields"), s.untake()] + hide("st3") + show("rsf"))
s.step("Busy, and the operation to perform.", [hl("rsf[0]")])
s.step("Vj and Vk: the operand values, once they are known.", [hl("rsf[1]")])
s.step("Qj and Qk: the tags of the stations that will produce the operands. For each operand, exactly one of V or Q is in use. A blank Q means the value is already in V.", [hl("rsf[2]")])
s.step("A, the address, for loads and stores.", [hl("rsf[3]")])
s.step("And for every register, a field Qi: the tag of the station that will write it next. A blank Qi means the register file holds the current value.", [hl("rsf[4]"), s.take("V: the value · Q: who will make it")])

# ---------------------------------------------------------------- renaming
s.scene("rename")
s.step("Stage 5: renaming, watched entry by entry. Our code from the dependences video, with a WAR on F8 and a WAW on F6. Suppose all five issue before anything finishes.", [s.head("Stage 5 of 8: renaming, entry by entry"), s.untake()] + hide("rsf") + show("rc", "rt", "rg") + [ml("rc", 1, 5)])
s.step("The divide goes to Mult1. F2 and F4 are ready, so their values are copied in. F0 is now marked: Mult1 will write it.", [go("rc", 1)] + row(0, ["DIV.D", "Regs[F2]", "Regs[F4]", "", ""]) + [st("rg[0][1]", "Mult1", 0.6)])
s.step("The add goes to Add1. F0 is not ready: Qj gets the tag Mult1. F8 is ready: its current value is copied into Vk. F6 is marked Add1.", [go("rc", 2)] + row(1, ["ADD.D", "", "Regs[F8]", "Mult1", ""]) + [st("rg[0][2]", "Add1", 0.6)])
s.step("The store needs F6, which Add1 will produce. So it records the tag Add1, not the register name.", [go("rc", 3)] + row(2, ["S.D", "", "", "Add1", ""]))
s.step("The subtract goes to Add2, with F10 and F14 copied in. F8 is now marked Add2.", [go("rc", 4)] + row(3, ["SUB.D", "Regs[F10]", "Regs[F14]", "", ""]) + [st("rg[0][3]", "Add2", 0.6)])
s.step("The multiply goes to Mult2. F10 is copied, and F8 comes from Add2. And F6's mark changes from Add1 to Mult2: the latest writer.", [go("rc", 5)] + row(4, ["MUL.D", "Regs[F10]", "", "", "Add2"]) + [st("rg[0][2]", "Mult2", 0.6), hl("rg[0][2]", 0.7)])
s.step("Look at the table now. No instruction refers to F6 or F8 by name any more, only to stations. The registers have been renamed into tags.", [hl("rt[0..=4]")])
s.step("The two writers of F6 now have different names, Add1 and Mult2. So do the two values of F8: the old one, copied into Add1, and the new one, Add2. There are as many names as there are stations.", [hl("rt[1]"), hl("rt[4]", 0.3), hl("rt[3]", 0.6)])

# ---------------------------------------------------------------- hazards
s.scene("hazards")
s.step("Stage 6: so what happened to the hazards?", [s.head("Stage 6 of 8: WAR and WAW disappear"), s.untake()] + hide("rc", "rt", "rg") + show("hz"))
s.step("The WAR on F8. The add copied the old F8 into its station when it issued. Whenever the subtract writes the new F8, the add is not affected. No stall.", [hl("hz[0]")])
s.step("The WAW on F6. Register F6 now points only at Mult2. When Add1 broadcasts, the store takes the value, but F6 does not, because its tag no longer matches. Only the multiply's result lands in F6. No stall.", [hl("hz[1]")])
s.step("And the real dependence, RAW: the store simply waits until tag Add1 appears on the bus.", [hl("hz[2]"), s.take("WAR: values copied early · WAW: only the latest tag updates the register")])

# ---------------------------------------------------------------- compare
s.scene("cmp")
s.step("Stage 7: Tomasulo against the scoreboard.", [s.head("Stage 7 of 8: against the scoreboard"), s.untake()] + hide("hz") + show("cmp"))
s.step("RAW: the scoreboard waits and then reads the register file a cycle later. Tomasulo takes the value straight off the bus: forwarding built in.", [hl("cmp[0]")])
s.step("WAR and WAW: the scoreboard stalls; Tomasulo removes them.", [hl("cmp[1..=2]")])
s.step("Hazard detection is spread across the stations, each watching the bus, instead of one central table.", [hl("cmp[3]")])
s.step("The new limits: the number of stations, and the single CDB, which can carry only one result per cycle.", [hl("cmp[4]"), s.take("Tomasulo: renaming + forwarding + distributed control")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("cmp") + show("q", "qx"))
s.step("All four instructions issue, and none has finished. Find each station's V and Q fields, the register status, and which name hazards were removed. Pause and work it out.", [ml("q", 1, 4), hl("qx")])
s.step("The load goes to Load1, and F2 is marked Load1.", hide("q", "qx") + show("qa") + [hl("qa[0]")])
s.step("The multiply goes to Mult1. F2 is not ready: Qj is Load1. F6 is ready: Vk is its value. F4 is marked Mult1.", [hl("qa[1]")])
s.step("The add goes to Add1, with F8 and F10 copied. F2's mark changes from Load1 to Add1.", [hl("qa[2]")])
s.step("The subtract goes to Add2. F4 comes from Mult1, F2 from Add1. F6 is marked Add2.", [hl("qa[3]")])
s.step("The register status: F2 is Add1, F4 is Mult1, F6 is Add2.", hide("qa") + show("qr") + [hl("qr[0]")])
s.step("Two name hazards were removed. The WAW on F2, between the load and the add: only Add1 will update F2, while the multiply still gets the load's value through tag Load1. And the WAR on F6: the multiply copied F6 before the subtract could overwrite it.", [mk("qr[0][1]"), mk("qr[0][3]", 0.4)])
s.step("The usual slip: writing a register name in Q. Q always holds a station tag, and V always holds a value.", [s.take("Q holds a tag, never a register name")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qr") + show("stages"))
s.step("Reservation stations hold instructions and their operands. Ready values are copied at issue; missing ones are named by tags.", [hl("stages[0..=4]")])
s.step("WAR and WAW vanish, the CDB forwards every result, and control is spread across the stations.", [hl("stages[5..=6]")])
s.step("Next video: Tomasulo's algorithm, part 2. The full example, cycle by cycle, and a loop running two iterations at once.", [mk("stages[0..=7]"), s.take("Next: Tomasulo, the full trace")])

s.save("/home/claude/playlist/m3/m3v5.json")

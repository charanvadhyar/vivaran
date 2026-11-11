"""Module 1, video 4: pipeline hazards, finding them (structural, RAW, WAR, WAW, control)."""
import sys
sys.path.insert(0, ".")
from common import Script

ST = ["IF", "ID", "EX", "MEM", "WB"]
CODE = [("LW", "R1", ["R2"], "LW  R1, 0(R2)"), ("ADD", "R3", ["R1", "R4"], "ADD R3, R1, R4"), ("SUB", "R4", ["R5", "R6"], "SUB R4, R5, R6"),
        ("MUL", "R3", ["R4", "R7"], "MUL R3, R4, R7"), ("BEQ", None, ["R3", "R0"], "BEQ R3, R0, L"), ("OR", "R8", ["R1", "R9"], "OR  R8, R1, R9")]


def deps(code):
    """RAW from the most recent earlier writer only; WAR and WAW for every pair."""
    out = []
    for j, (_, dj, sj, _) in enumerate(code):
        for r in sj:
            writers = [i for i in range(j) if code[i][1] == r]
            if writers:
                out.append((writers[-1], j, r, "RAW"))
        for i in range(j):
            if dj and dj in code[i][2]:
                out.append((i, j, dj, "WAR"))
            if dj and code[i][1] == dj:
                out.append((i, j, dj, "WAW"))
    return sorted(out, key=lambda t: (t[0], t[1]))


D = deps(CODE)
assert [(a + 1, b + 1, r, t) for a, b, r, t in D] == [
    (1, 2, "R1", "RAW"), (1, 6, "R1", "RAW"), (2, 3, "R4", "WAR"), (2, 4, "R3", "WAW"), (3, 4, "R4", "RAW"), (4, 5, "R3", "RAW")]
QCODE = [("ADD", "R1", ["R2", "R3"], "ADD R1, R2, R3"), ("SUB", "R4", ["R1", "R5"], "SUB R4, R1, R5"), ("AND", "R6", ["R1", "R7"], "AND R6, R1, R7"),
         ("OR", "R8", ["R1", "R9"], "OR  R8, R1, R9"), ("XOR", "R4", ["R10", "R11"], "XOR R4, R10, R11")]
QD = deps(QCODE)
assert [(a + 1, b + 1, r, t) for a, b, r, t in QD] == [(1, 2, "R1", "RAW"), (1, 3, "R1", "RAW"), (1, 4, "R1", "RAW"), (2, 5, "R4", "WAW")]

s = Script("Pipeline hazards: finding them")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "What a hazard is, and the three kinds"],
    [2, "Structural hazards: two instructions, one piece of hardware"],
    [3, "Data dependences: RAW, WAR and WAW"],
    [4, "Which dependences are hazards in our pipeline"],
    [5, "Control hazards: branches"],
    [6, "One code sequence, every hazard found"]]})
s.obj({"id": "three", "type": "table", "region": "center", "columns": ["hazard", "cause"], "rows": [
    ["structural", "two instructions need the same hardware in the same cycle"],
    ["data", "an instruction needs a result that is not ready yet"],
    ["control", "the next instruction to fetch depends on a branch not yet decided"]]})
s.obj({"id": "struct", "type": "timeline", "region": "center", "lanes": ["I1: LW", "I2", "I3", "I4"], "end": 8, "unit": "clock cycle", "now": 0,
       "blocks": [{"id": f"b{i}{j}", "lane": ["I1: LW", "I2", "I3", "I4"][i], "start": i + j, "end": i + j + 1, "label": ST[j]} for i in range(4) for j in range(5)]})
s.obj({"id": "kinds", "type": "table", "region": "center", "columns": ["type", "also called", "instruction j, after i, ...", "example"], "rows": [
    ["RAW: read after write", "true dependence", "reads a register that i writes", "i: ADD R1, …   j: SUB …, R1, …"],
    ["WAR: write after read", "anti-dependence", "writes a register that i reads", "i: ADD …, R4, …   j: SUB R4, …"],
    ["WAW: write after write", "output dependence", "writes a register that i also writes", "i: ADD R3, …   j: MUL R3, …"]]})
s.obj({"id": "raw", "type": "timeline", "region": "center", "lanes": ["I1: ADD R1", "I2: SUB uses R1", "I3: AND uses R1", "I4: OR uses R1"], "end": 9, "unit": "clock cycle", "now": 0,
       "blocks": [{"id": f"r{i}{j}", "lane": ["I1: ADD R1", "I2: SUB uses R1", "I3: AND uses R1", "I4: OR uses R1"][i], "start": i + j, "end": i + j + 1, "label": ST[j]} for i in range(4) for j in range(5)]})
s.obj({"id": "when", "type": "table", "region": "center", "columns": ["dependence", "a hazard in the 5-stage in-order pipeline?", "why"], "rows": [
    ["RAW, 1 or 2 instructions apart", "yes", "the value is read in ID before it is written in WB"],
    ["RAW, 3 or more apart", "no", "WB writes in the first half of a cycle, ID reads in the second"],
    ["WAR", "no", "every read in ID happens before any later instruction's WB"],
    ["WAW", "no", "writes happen in WB, in program order"]]})
s.obj({"id": "ctrl", "type": "timeline", "region": "center", "lanes": ["BEQ", "next", "next + 1"], "end": 7, "unit": "clock cycle", "now": 0,
       "blocks": [{"id": f"c{i}{j}", "lane": ["BEQ", "next", "next + 1"][i], "start": i + j, "end": i + j + 1, "label": ST[j]} for i in range(3) for j in range(5)]})
s.obj({"id": "code", "type": "code", "region": "left", "language": "asm", "lines": [c[3] for c in CODE]})
s.obj({"id": "deps", "type": "table", "region": "right", "columns": ["pair", "register", "type", "apart", "hazard?"], "rows": [
    [f"I{a + 1} → I{b + 1}", r, t, str(b - a), ""] for a, b, r, t in D]})
s.obj({"id": "qcode", "type": "code", "region": "left", "language": "asm", "lines": [c[3] for c in QCODE]})
s.obj({"id": "qdeps", "type": "table", "region": "right", "columns": ["pair", "register", "type", "hazard?"], "rows": [
    [f"I{a + 1} → I{b + 1}", r, t, ""] for a, b, r, t in QD]})

s.obj({"id": "ooo", "type": "table", "region": "center", "columns": ["order in program", "instruction", "takes", "finishes"], "rows": [
    ["1st", "DIV.D F0, F2, F4", "long: about 20 cycles in EX", "last"],
    ["2nd", "ADD.D F0, F6, F8", "short: 2 cycles in EX", "first"]]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Last video, the pipeline finished one instruction every cycle. That was the ideal.", [s.head("Pipeline hazards: finding them")])
s.step("A hazard is anything that stops the next instruction from running in its planned cycle.", [s.take("hazard: the next instruction cannot run in its planned cycle")])
s.step("This video is about finding hazards; the next one is about fixing them.", [s.untake(), {"action": "show", "target": "stages"}])
s.step("The three kinds, then structural hazards and the three data dependences.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Then which dependences really cause trouble, control hazards, and one code sequence with every hazard marked.", [{"action": "highlight", "target": "stages[3..=5]"}])

# ---------------------------------------------------------------- three
s.scene("three")
s.step("Stage 1: there are three kinds of hazard.", [s.head("Stage 1 of 6: three kinds"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "three"}])
s.step("Structural: two instructions need the same piece of hardware in the same cycle.", [{"action": "highlight", "target": "three[0]"}])
s.step("Data: an instruction needs a value that an earlier instruction has not produced yet.", [{"action": "highlight", "target": "three[1]"}])
s.step("Control: the pipeline must fetch the next instruction before it knows which way a branch goes.", [{"action": "highlight", "target": "three[2]"}])

# ---------------------------------------------------------------- structural
s.scene("structural")
s.step("Stage 2, structural hazards. Suppose instructions and data share a single memory.", [s.head("Stage 2 of 6: structural hazards"), {"action": "hide", "target": "three"}, {"action": "show", "target": "struct"}])
s.step("I1 is a load. In cycle 4 it is in MEM, reading data memory.", [{"action": "advance", "target": "struct", "to": 4}, {"action": "highlight", "target": "struct.b03"}])
s.step("In that same cycle 4, I4 is in IF, fetching its instruction from memory.", [{"action": "highlight", "target": "struct.b30"}])
s.step("One memory cannot serve both in one cycle: that is a structural hazard.", [{"action": "mark", "target": "struct.b03"}, {"action": "mark", "target": "struct.b30"}])
s.step("The standard cure is separate instruction and data caches, so IF and MEM never compete.", [s.take("structural hazard: shared hardware · cure: duplicate it, e.g. split I- and D-caches")])
s.step("The register file is shared too: ID reads it while WB writes it. Writing in the first half of the cycle and reading in the second avoids that clash.", [])

# ---------------------------------------------------------------- dependences
s.scene("dependences")
s.step("Stage 3: data hazards come from dependences between instructions. There are three kinds.", [s.head("Stage 3 of 6: RAW, WAR and WAW"), {"action": "hide", "target": "struct"}, s.untake(), {"action": "show", "target": "kinds"}])
s.step("Name them by what the later instruction, j, does after the earlier one, i.", [{"action": "highlight", "target": "kinds.c2"}])
s.step("RAW, read after write: j reads a register that i writes. j truly needs i's result, so it is called a true dependence.", [{"action": "highlight", "target": "kinds[0]"}])
s.step("WAR, write after read: j writes a register that i still has to read. No value passes between them; only the name is shared. It is an anti-dependence.", [{"action": "highlight", "target": "kinds[1]"}])
s.step("WAW, write after write: both write the same register, and the final value must be j's. It is an output dependence.", [{"action": "highlight", "target": "kinds[2]"}])
s.step("WAR and WAW are called name dependences: renaming a register removes them. RAW cannot be renamed away.", [s.take("RAW = true dependence · WAR, WAW = name dependences, removable by renaming")])

# ---------------------------------------------------------------- which are hazards
s.scene("which")
s.step("Stage 4: a dependence is not always a hazard. It depends on the pipeline. Watch R1 here.", [s.head("Stage 4 of 6: which dependences are hazards"), {"action": "hide", "target": "kinds"}, s.untake(), {"action": "show", "target": "raw"}])
s.step("I1 writes R1 in WB, in cycle 5.", [{"action": "highlight", "target": "raw.r04"}, {"action": "advance", "target": "raw", "to": 5}])
s.step("I2 reads R1 in its ID stage, in cycle 3, two cycles too early.", [{"action": "highlight", "target": "raw.r11"}, {"action": "mark", "target": "raw.r11", "delay": 0.4}])
s.step("I3 reads R1 in cycle 4, still too early.", [{"action": "highlight", "target": "raw.r21"}, {"action": "mark", "target": "raw.r21", "delay": 0.4}])
s.step("I4 reads R1 in cycle 5, the same cycle I1 writes it. Writing in the first half and reading in the second makes this safe.", [{"action": "highlight", "target": "raw.r31"}])
s.step("So in our pipeline, a RAW dependence is a hazard when the instructions are one or two apart.", [{"action": "hide", "target": "raw"}, {"action": "show", "target": "when"}, {"action": "highlight", "target": "when[0..=1]"}])
s.step("WAR is never a hazard here: every instruction reads its registers in ID, before any later instruction reaches WB.", [{"action": "highlight", "target": "when[2]"}])
s.step("WAW is not a hazard either: all writes happen in WB, in program order.", [{"action": "highlight", "target": "when[3]"}])
s.step("WAR and WAW become hazards in pipelines that run instructions out of order, issue several at once, or have stages of different lengths.", [s.take("in-order 5-stage pipeline: only RAW causes data hazards")])

# ---------------------------------------------------------------- when WAR/WAW matter
s.scene("ooo")
s.step("When do WAR and WAW become real hazards? When instructions can finish out of order.", [s.head("When WAR and WAW do matter"), {"action": "hide", "target": "when"}, s.untake(), {"action": "show", "target": "ooo"}])
s.step("A floating-point divide takes about 20 cycles in EX; an add takes 2. Both write F0.", [{"action": "highlight", "target": "ooo.c2"}])
s.step("The divide starts first, but the add finishes first and writes F0.", [{"action": "highlight", "target": "ooo[1]"}])
s.step("Then the divide finishes and overwrites F0 with the older result. The final value is wrong: a WAW hazard.", [{"action": "highlight", "target": "ooo[0]"}, {"action": "mark", "target": "ooo.finishes", "delay": 0.4}])
s.step("A WAR hazard appears the same way: if a later write is allowed to run before an earlier read of the same register, the read gets the new value.", [])
s.step("Out-of-order processors avoid both by register renaming: each write gets a fresh physical register.", [s.take("WAR and WAW: hazards only when instructions can finish out of order · cure: register renaming")])

# ---------------------------------------------------------------- control
s.scene("control")
s.step("Stage 5: control hazards.", [s.head("Stage 5 of 6: control hazards"), {"action": "hide", "target": "ooo"}, s.untake(), {"action": "show", "target": "ctrl"}])
s.step("A branch compares its registers and finds its target in EX, in cycle 3.", [{"action": "advance", "target": "ctrl", "to": 3}, {"action": "highlight", "target": "ctrl.c02"}])
s.step("But by then, the next two instructions have already been fetched.", [{"action": "highlight", "target": "ctrl.c10"}, {"action": "highlight", "target": "ctrl.c20", "delay": 0.4}])
s.step("If the branch is taken, those two were the wrong instructions, and their work must be thrown away.", [{"action": "mark", "target": "ctrl.c10"}, {"action": "mark", "target": "ctrl.c20"}])
s.step("That is a control hazard: fetching before knowing where the program goes.", [s.take("control hazard: instructions fetched before a branch is decided")])

# ---------------------------------------------------------------- worked
s.scene("worked")
s.step("Stage 6: find every hazard in this sequence of six instructions.", [s.head("Stage 6 of 6: one sequence, every hazard"), {"action": "hide", "target": "ctrl"}, s.untake(), {"action": "show", "target": "code"}])
s.step("The method: for each instruction, look at the registers it reads and writes, and compare with every earlier instruction.", [{"action": "show", "target": "deps"}])
notes = {
    (0, 1): ("I2 reads R1, which I1, a load, writes just before it. RAW, one apart: a hazard.", "yes"),
    (0, 5): ("I6 also reads R1 from I1, but five instructions later. R1 is long written: no hazard.", "no"),
    (1, 2): ("I3 writes R4, which I2 reads. WAR, one apart, but I2 reads in ID before I3 writes: no hazard here.", "no (in-order)"),
    (1, 3): ("I4 writes R3, which I2 also writes. WAW, but writes happen in order: no hazard here.", "no (in-order)"),
    (2, 3): ("I4 reads R4, written by I3 just before. RAW, one apart: a hazard.", "yes"),
    (3, 4): ("I5, the branch, reads R3. Its value comes from I4, the most recent writer, not I2. RAW, one apart: a hazard.", "yes"),
}
for k, (a, b, r, t) in enumerate(D):
    say, ans = notes[(a, b)]
    s.step(say, [{"action": "goto_line", "target": "code", "line": b + 1}, {"action": "highlight", "target": f"deps[{k}]"},
                 {"action": "set", "target": f"deps[{k}][4]", "value": ans, "delay": 0.5}])
s.step("And I5 is a branch, so I6 and the instruction after it are fetched before it is decided: a control hazard as well.", [{"action": "goto_line", "target": "code", "line": 5}])
s.step("Count: six dependences, three RAW hazards, one control hazard, and the WAR and WAW are harmless in this pipeline.", [s.take("3 RAW hazards (I1→I2, I3→I4, I4→I5) + 1 control hazard (I5)")])
s.step("Watch for the trap at I5: a register can be written twice. Always take the most recent writer.", [{"action": "highlight", "target": "deps[5]"}])

# ---------------------------------------------------------------- exam
s.scene("exam")
qnotes = [
    ("I2 reads R1, one instruction after I1 writes it: RAW, a hazard.", "yes"),
    ("I3 reads R1, two after: RAW, still a hazard.", "yes"),
    ("I4 reads R1, three after: RAW, but no hazard, because the write and read share a cycle safely.", "no"),
    ("I5 writes R4, which I2 also writes: WAW, harmless in an in-order pipeline.", "no (in-order)"),
]
s.step("Now an exam question: list every dependence in this sequence, and say which are hazards in the 5-stage pipeline.", [s.head("Exam question"), {"action": "hide", "target": "code"}, {"action": "hide", "target": "deps"}, s.untake(), {"action": "show", "target": "qcode"}])
s.step("Pause and try it, then check with me.", [{"action": "show", "target": "qdeps"}])
for k, (say, ans) in enumerate(qnotes):
    a, b, r, t = QD[k]
    s.step(say, [{"action": "goto_line", "target": "qcode", "line": b + 1}, {"action": "highlight", "target": f"qdeps[{k}]"}, {"action": "set", "target": f"qdeps[{k}][3]", "value": ans, "delay": 0.5}])
s.step("Answer: four dependences, two hazards, I1 to I2 and I1 to I3.", [s.take("hazards: I1→I2 and I1→I3 (RAW) · I1→I4 is safe · I2→I5 WAW is harmless")])
s.step("The usual slip is counting I1 to I4 as a hazard. Three apart is safe because the register file is written before it is read in the same cycle.", [{"action": "highlight", "target": "qdeps[2]"}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qcode"}, {"action": "hide", "target": "qdeps"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("Three kinds: structural, data and control.", [{"action": "highlight", "target": "stages[0..=1]"}])
s.step("RAW is a true dependence; WAR and WAW are name dependences.", [{"action": "highlight", "target": "stages[2]"}])
s.step("In the in-order 5-stage pipeline, only RAW one or two apart is a data hazard; branches cause control hazards.", [{"action": "highlight", "target": "stages[3..=5]"}])
s.step("Next video: how the pipeline deals with them, with stalls, forwarding and branch handling.", [{"action": "mark", "target": "stages[0..=5]"}, s.take("Next: handling hazards — stalls, forwarding, branches")])

s.save(sys.argv[1])

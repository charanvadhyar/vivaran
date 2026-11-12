"""Module 3, video 1: ILP, data / name / control dependences, mapping to RAW / WAR / WAW, register renaming."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from deps import deps

HP = [('DIV.D', 'F0', ['F2', 'F4']), ('ADD.D', 'F6', ['F0', 'F8']), ('S.D', None, ['F6', 'R1']),
      ('SUB.D', 'F8', ['F10', 'F14']), ('MUL.D', 'F6', ['F10', 'F8'])]
assert deps(HP) == [('true', 1, 2, 'F0'), ('true', 2, 3, 'F6'), ('true', 4, 5, 'F8'),
                    ('anti', 2, 4, 'F8'), ('anti', 3, 5, 'F6'), ('output', 2, 5, 'F6')]
REN = [('DIV.D', 'F0', ['F2', 'F4']), ('ADD.D', 'S', ['F0', 'F8']), ('S.D', None, ['S', 'R1']),
       ('SUB.D', 'T', ['F10', 'F14']), ('MUL.D', 'F6', ['F10', 'T'])]
assert [d[0] for d in deps(REN)] == ['true'] * 3
EX = [('MUL.D', 'F2', ['F4', 'F6']), ('ADD.D', 'F8', ['F2', 'F10']), ('SUB.D', 'F4', ['F12', 'F14']),
      ('S.D', None, ['F8', 'R1']), ('ADD.D', 'F8', ['F4', 'F16']), ('L.D', 'F2', ['R1'])]
assert deps(EX) == [('true', 1, 2, 'F2'), ('true', 2, 4, 'F8'), ('true', 3, 5, 'F4'),
                    ('anti', 1, 3, 'F4'), ('anti', 2, 6, 'F2'), ('anti', 4, 5, 'F8'),
                    ('output', 1, 6, 'F2'), ('output', 2, 5, 'F8')]
EXR = [('MUL.D', 'F2', ['F4', 'F6']), ('ADD.D', 'F8', ['F2', 'F10']), ('SUB.D', 'S', ['F12', 'F14']),
       ('S.D', None, ['F8', 'R1']), ('ADD.D', 'T', ['S', 'F16']), ('L.D', 'U', ['R1'])]
assert [d[0] for d in deps(EXR)] == ['true'] * 3
assert round(1 / 0.2) == 5 and round(1 / 0.15, 1) == 6.7

s = Script("Dependences and hazards")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "What ILP is, and why it is hard"],
    [2, "Data dependences"],
    [3, "Name dependences: anti and output"],
    [4, "Control dependences"],
    [5, "From dependences to RAW, WAR and WAW"],
    [6, "Register renaming by hand"],
    [7, "A full analysis"],
    [8, "Exam question"]]})
s.obj({"id": "ilp", "type": "math", "region": "center", "lines": [
    "\"pipeline CPI\" = \"ideal CPI\" + \"structural stalls\" + \"data stalls\" + \"control stalls\"",
    "\"branches: 15 to 20% of all instructions\"",
    "\"basic block\" approx 1 / 0.2 = 5 \"to\" 1 / 0.15 approx 7 \"instructions\"",
    "\"so ILP must be found across branches: in loops\""]})
s.obj({"id": "loop", "type": "code", "region": "left", "language": "asm", "lines": [
    "Loop: L.D    F0,0(R1)",
    "      ADD.D  F4,F0,F2",
    "      S.D    F4,0(R1)",
    "      DADDUI R1,R1,#-8",
    "      BNE    R1,R2,Loop"]})
s.obj({"id": "dd", "type": "table", "region": "right", "columns": ["producer", "consumer", "through"], "rows": [
    ["L.D", "ADD.D", ""], ["ADD.D", "S.D", ""], ["DADDUI", "BNE", ""]]})
s.obj({"id": "ddx", "type": "table", "region": "center", "columns": ["a data dependence", "means"], "rows": [
    ["is a property of the program", "the value must flow from producer to consumer"],
    ["may or may not cause a stall", "that depends on the pipeline: forwarding, latencies"],
    ["limits ILP", "dependent instructions cannot overlap completely"],
    ["through memory too", "does 100(R4) equal 20(R6)? hard to tell before run time"]]})
s.obj({"id": "nd", "type": "code", "region": "left", "language": "asm", "lines": [
    "I1: ADD.D F6,F0,F8",
    "I2: SUB.D F8,F10,F14",
    "I3: MUL.D F6,F10,F12"]})
s.obj({"id": "ndx", "type": "table", "region": "right", "columns": ["kind", "between", "name"], "rows": [
    ["antidependence", "I1 reads, I2 writes", "F8"],
    ["output dependence", "I1 writes, I3 writes", "F6"]]})
s.obj({"id": "cd", "type": "code", "region": "left", "language": "asm", "lines": [
    "      DADDU R2,R3,R4",
    "      BEQZ  R2,L1",
    "      LW    R1,0(R2)",
    "L1:   ..."]})
s.obj({"id": "cdx", "type": "table", "region": "center", "columns": ["rule", "why"], "rows": [
    ["not above its branch", "it would run when it should not"],
    ["not below, into the branch's shadow", "it might be skipped"],
    ["keep exceptions", "LW must not fault if R2 = 0"],
    ["keep data flow", "each read sees its true writer"]]})
s.obj({"id": "hz", "type": "table", "region": "center", "columns": ["dependence", "hazard", "the danger", "in a 5-stage in-order pipeline?"], "rows": [
    ["true (data)", "RAW: read after write", "j reads before i writes", "yes: forwarding and stalls"],
    ["anti", "WAR: write after read", "j writes before i reads", "no: reads happen early, in ID"],
    ["output", "WAW: write after write", "j writes before i: wrong final value", "no: writes happen in order, in WB"],
    ["(read after read)", "none", "nothing changes", "never a hazard"]]})
s.obj({"id": "rn", "type": "code", "region": "left", "language": "asm", "lines": [
    "1: DIV.D F0,F2,F4",
    "2: ADD.D F6,F0,F8",
    "3: S.D   F6,0(R1)",
    "4: SUB.D F8,F10,F14",
    "5: MUL.D F6,F10,F8"]})
s.obj({"id": "rnx", "type": "table", "region": "right", "columns": ["kind", "pair", "name"], "rows": [
    ["true", "1 → 2", "F0"], ["true", "2 → 3", "F6"], ["true", "4 → 5", "F8"],
    ["anti", "2 → 4", "F8"], ["anti", "3 → 5", "F6"], ["output", "2 → 5", "F6"]]})
s.obj({"id": "rn2", "type": "code", "region": "left", "language": "asm", "lines": [
    "1: DIV.D F0,F2,F4",
    "2: ADD.D S,F0,F8",
    "3: S.D   S,0(R1)",
    "4: SUB.D T,F10,F14",
    "5: MUL.D F6,F10,T"]})
s.obj({"id": "ex", "type": "code", "region": "left", "language": "asm", "lines": [
    "I1: MUL.D F2,F4,F6",
    "I2: ADD.D F8,F2,F10",
    "I3: SUB.D F4,F12,F14",
    "I4: S.D   F8,0(R1)",
    "I5: ADD.D F8,F4,F16",
    "I6: L.D   F2,8(R1)"]})
s.obj({"id": "exa", "type": "table", "region": "right", "columns": ["kind", "pairs"], "rows": [
    ["true (RAW)", "I1→I2 F2 · I2→I4 F8 · I3→I5 F4"],
    ["anti (WAR)", "I1→I3 F4 · I2→I6 F2 · I4→I5 F8"],
    ["output (WAW)", "I1→I6 F2 · I2→I5 F8"]]})
s.obj({"id": "exr", "type": "code", "region": "left", "language": "asm", "lines": [
    "I1: MUL.D F2,F4,F6",
    "I2: ADD.D F8,F2,F10",
    "I3: SUB.D S,F12,F14",
    "I4: S.D   F8,0(R1)",
    "I5: ADD.D T,S,F16",
    "I6: L.D   U,8(R1)"]})
s.obj({"id": "q", "type": "code", "region": "left", "language": "asm", "lines": [
    "I1: L.D   F2,0(R1)",
    "I2: MUL.D F4,F2,F6",
    "I3: ADD.D F2,F8,F10",
    "I4: S.D   F4,0(R1)",
    "I5: SUB.D F4,F2,F12",
    "I6: ADD.D F6,F4,F2"]})
s.obj({"id": "qx", "type": "table", "region": "right", "columns": ["find"], "rows": [
    ["a) every true dependence"], ["b) every antidependence"], ["c) every output dependence"], ["d) a renaming that leaves only true ones"]]})
Q = [('L.D', 'F2', ['R1']), ('MUL.D', 'F4', ['F2', 'F6']), ('ADD.D', 'F2', ['F8', 'F10']),
     ('S.D', None, ['F4', 'R1']), ('SUB.D', 'F4', ['F2', 'F12']), ('ADD.D', 'F6', ['F4', 'F2'])]
assert deps(Q) == [('true', 1, 2, 'F2'), ('true', 2, 4, 'F4'), ('true', 3, 5, 'F2'), ('true', 3, 6, 'F2'), ('true', 5, 6, 'F4'),
                   ('anti', 2, 3, 'F2'), ('anti', 2, 6, 'F6'), ('anti', 4, 5, 'F4'),
                   ('output', 1, 3, 'F2'), ('output', 2, 5, 'F4')], deps(Q)
QR = [('L.D', 'F2', ['R1']), ('MUL.D', 'F4', ['F2', 'F6']), ('ADD.D', 'S', ['F8', 'F10']),
      ('S.D', None, ['F4', 'R1']), ('SUB.D', 'T', ['S', 'F12']), ('ADD.D', 'U', ['T', 'S'])]
assert [d[0] for d in deps(QR)] == ['true'] * 5
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["answer", "pairs"], "rows": [
    ["a) true", "I1→I2 F2 · I2→I4 F4 · I3→I5 F2 · I3→I6 F2 · I5→I6 F4"],
    ["b) anti", "I2→I3 F2 · I2→I6 F6 · I4→I5 F4"],
    ["c) output", "I1→I3 F2 · I2→I5 F4"],
    ["d) rename", "I3 writes S · I5 writes T, reads S · I6 writes U, reads T and S"]]})
s.obj({"id": "qr", "type": "code", "region": "center", "language": "asm", "lines": [
    "I1: L.D   F2,0(R1)",
    "I2: MUL.D F4,F2,F6",
    "I3: ADD.D S,F8,F10",
    "I4: S.D   F4,0(R1)",
    "I5: SUB.D T,S,F12",
    "I6: ADD.D U,T,S"]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Module 3 is about doing more than one thing at once. First inside one thread, by overlapping instructions. Then across threads and cores. It all starts with one question: which instructions depend on which?", [s.head("Dependences and hazards")])
s.step("Here are the eight stages.", show("stages"))
s.step("What ILP is, then the three kinds of dependence: data, name, and control.", [hl("stages[0..=3]")])
s.step("How they become the hazards from Module 1, register renaming by hand, a full analysis, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- ILP
s.scene("ilp")
s.step("Stage 1: instruction-level parallelism, ILP, is overlap between the instructions of one program. A pipeline is the first way to get it.", [s.head("Stage 1 of 8: what ILP is")] + hide("stages") + show("ilp") + [hl("ilp[0]")])
s.step("The pipeline CPI is the ideal CPI plus every kind of stall. All the techniques in this module attack one of those stall terms.", [mk("ilp[0]")])
s.step("The trouble: branches are 15 to 20 percent of instructions. So a basic block, the straight-line code between two branches, is only about 5 to 7 instructions long. Not much to overlap.", rv("ilp", 1) + rv("ilp", 2))
s.step("So we must find parallelism across branches, and the richest source is loops, where every iteration does similar, often independent, work.", rv("ilp", 3) + [s.take("ILP = overlap inside one thread · limited by dependences")])

# ---------------------------------------------------------------- data
s.scene("data")
s.step("Stage 2: data dependences. Here is a loop that adds a scalar in F2 to every element of an array.", [s.head("Stage 2 of 8: data dependences"), s.untake()] + hide("ilp") + show("loop") + [ml("loop", 1, 5)])
s.step("Instruction j is data dependent on instruction i if i produces a result that j uses, or through a chain of such steps.", show("dd"))
s.step("The load writes F0, and the add reads F0. A data dependence.", [go("loop", 2), st("dd[0][2]", "F0"), hl("dd[0]", 0.3)])
s.step("The add writes F4, and the store reads F4.", [go("loop", 3), st("dd[1][2]", "F4"), hl("dd[1]", 0.3)])
s.step("And the decrement writes R1, which the branch reads.", [go("loop", 5), st("dd[2][2]", "R1"), hl("dd[2]", 0.3)])
s.step("Load, add, store is a chain: each must wait for the one before. Those three cannot fully overlap.", [mk("dd[0..=1]")])
s.step("Four facts to keep straight. A dependence is a property of the program. A hazard is a property of the pipeline.", hide("loop", "dd") + show("ddx") + [hl("ddx[0]")])
s.step("So a dependence may or may not cause a stall. With forwarding, and short latencies, often it does not.", [hl("ddx[1]")])
s.step("But it always limits ILP: the dependent instruction cannot finish before its producer.", [hl("ddx[2]")])
s.step("And dependences flow through memory too. Does 100 off R4 name the same address as 20 off R6? Often nobody can tell until the program runs.", [hl("ddx[3]"), s.take("data dependence: a value flows from producer to consumer")])

# ---------------------------------------------------------------- name
s.scene("name")
s.step("Stage 3: name dependences. Two instructions use the same register or memory location, but no value flows between them.", [s.head("Stage 3 of 8: name dependences"), s.untake()] + hide("ddx") + show("nd") + [ml("nd", 1, 3)])
s.step("I1 reads F8. Later, I2 writes F8. If I2 ran first, I1 would read the wrong value. This is an antidependence.", [go("nd", 2)] + show("ndx") + [hl("ndx[0]")])
s.step("I1 writes F6, and I3 writes F6 too. If they finished in the wrong order, F6 would end with I1's value. This is an output dependence.", [go("nd", 3), hl("ndx[1]")])
s.step("The key point: no value flows. I2 does not need anything from I1. They just happen to share a name.", [mk("ndx[0..=1]")])
s.step("So if we give I2 and I3 different registers, the conflicts vanish. That is register renaming, done by the compiler or by the hardware.", [s.take("name dependence: shared name, no value flow · remove by renaming")])

# ---------------------------------------------------------------- control
s.scene("control")
s.step("Stage 4: control dependences. Every instruction, except those in the very first block, depends on some branch deciding whether it runs.", [s.head("Stage 4 of 8: control dependences"), s.untake()] + hide("nd", "ndx") + show("cd") + [ml("cd", 1, 4)])
s.step("Here the load runs only if R2 is not zero. It is control dependent on the branch.", [go("cd", 3)])
s.step("Rule one: an instruction controlled by a branch cannot simply be moved above it. Then it would run even when the branch says no.", hide("cd") + show("cdx") + [hl("cdx[0]")])
s.step("Rule two: an instruction not controlled by the branch cannot be moved below it, into its shadow. Then it might be skipped.", [hl("cdx[1]")])
s.step("What really matters are two properties. Exception behaviour: if we hoisted this load above the branch, and R2 were 0, it could fault, and that fault should never happen.", [hl("cdx[2]")])
s.step("And data flow: every instruction must read the value from the writer it would have seen in order. Hardware speculation, later in this module, breaks these rules safely.", [hl("cdx[3]"), s.take("control dependence: keep exceptions and data flow correct")])

# ---------------------------------------------------------------- hazards
s.scene("hazards")
s.step("Stage 5: how dependences become hazards. Take an instruction i, followed by a later instruction j.", [s.head("Stage 5 of 8: RAW, WAR and WAW"), s.untake()] + hide("cdx") + show("hz"))
s.step("A true dependence risks a RAW hazard, read after write: j tries to read before i has written. In our 5-stage pipeline, forwarding and stalls handle it, as in Module 1.", [hl("hz[0]")])
s.step("An antidependence risks a WAR hazard, write after read: j writes before i has read. Impossible in the 5-stage pipeline, because every instruction reads its registers early, in decode.", [hl("hz[1]")])
s.step("An output dependence risks a WAW hazard: j writes before i, leaving the wrong final value. Also impossible in order, since every write happens in the same stage, write back.", [hl("hz[2]")])
s.step("And read after read is never a hazard: reading does not change anything.", [hl("hz[3]")])
s.step("So WAR and WAW only appear once instructions can finish out of order: long floating-point units, or dynamic scheduling. That is exactly where this module is going.", [mk("hz[1..=2]"), s.take("true → RAW · anti → WAR · output → WAW")])

# ---------------------------------------------------------------- renaming
s.scene("rename")
s.step("Stage 6: register renaming by hand, on the textbook's example.", [s.head("Stage 6 of 8: register renaming"), s.untake()] + hide("hz") + show("rn") + [ml("rn", 1, 5)])
s.step("First the true dependences. 1 writes F0, which 2 reads. 2 writes F6, which the store reads. 4 writes F8, which 5 reads.", show("rnx") + [hl("rnx[0..=2]"), go("rn", 2)])
s.step("Antidependences. 2 reads F8, then 4 writes it. The store reads F6, then 5 writes it.", [hl("rnx[3..=4]"), go("rn", 4)])
s.step("And one output dependence: 2 and 5 both write F6.", [hl("rnx[5]"), go("rn", 5)])
s.step("Now rename, using two spare registers, S and T. Instruction 2 writes S instead of F6, and the store reads S.", hide("rn") + show("rn2") + [ml("rn2", 2, 3)])
s.step("Instruction 4 writes T instead of F8, and 5 reads T.", [ml("rn2", 4, 5)])
s.step("5 still writes F6, so the final value of F6 is unchanged. Only the true dependences remain, and 4 and 5 can now run before, or alongside, 1 to 3.", [mk("rnx[0..=2]"), hl("rnx[3..=5]", 0.4), s.take("rename the later writer · keep the true dependences")])

# ---------------------------------------------------------------- full
s.scene("full")
s.step("Stage 7: a full analysis, step by step. Six instructions.", [s.head("Stage 7 of 8: a full analysis"), s.untake()] + hide("rn2", "rnx") + show("ex") + [ml("ex", 1, 6)])
s.step("The method: for each instruction, look at what it reads, and find the latest earlier writer. Each one is a true dependence.", show("exa") + [hl("exa[0]")])
s.step("I2 reads F2 from I1. I4 reads F8 from I2. I5 reads F4 from I3. Three true dependences.", [go("ex", 2), go("ex", 4), go("ex", 5)])
s.step("Then, for each write, look back for earlier reads of the same register. I3 writes F4, which I1 read. I6 writes F2, which I2 read. I5 writes F8, which the store read. Three antidependences.", [hl("exa[1]"), go("ex", 3)])
s.step("Finally, earlier writes of the same register. I6 and I1 both write F2. I5 and I2 both write F8. Two output dependences.", [hl("exa[2]"), go("ex", 6)])
s.step("Rename the later writers: I3 writes S, so I5 reads S. I5 writes T, and I6 writes U. Later code reads T for F8, and U for F2.", hide("ex") + show("exr") + [ml("exr", 3, 3), ml("exr", 5, 6)])
s.step("Only the three true dependences are left.", [mk("exa[0]"), s.take("method: last writer of each read · earlier reads and writes of each write")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("exr", "exa") + show("q", "qx"))
s.step("Six instructions. Find every true dependence, every antidependence, every output dependence, and a renaming that leaves only the true ones. Pause and work it out.", [ml("q", 1, 6), hl("qx")])
s.step("a: I2 reads F2 from I1. I4 reads F4 from I2. I5 reads F2 from I3, not from I1. I6 reads F4 from I5 and F2 from I3. Five true dependences.", hide("qx", "q") + show("qa") + [hl("qa[0]")])
s.step("b: I3 writes F2, which I2 read. I6 writes F6, which I2 read. I5 writes F4, which the store read. Three antidependences.", [hl("qa[1]")])
s.step("c: I3 rewrites F2 after I1. I5 rewrites F4 after I2. Two output dependences.", [hl("qa[2]")])
s.step("d: I3 writes S, I5 reads S and writes T, I6 reads T and S, and writes U. Now only true dependences remain.", [hl("qa[3]")])
s.step("Here is the renamed code. The usual slip: pairing a read with the first writer instead of the latest one. I5 reads F2 from I3, not I1, so it now reads S.", hide("qa") + show("qr") + [go("qr", 5), s.take("always the latest earlier writer")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qr") + show("stages"))
s.step("ILP is overlap within one thread, and basic blocks are short. Data dependences carry values; name dependences share a name; control dependences decide what runs.", [hl("stages[0..=3]")])
s.step("They become RAW, WAR and WAW hazards. Renaming removes the name dependences, leaving only the true ones.", [hl("stages[4..=6]")])
s.step("Next video: loop unrolling and instruction scheduling, exposing ILP with the compiler.", [mk("stages[0..=7]"), s.take("Next: loop unrolling and scheduling")])

s.save("/home/claude/playlist/m3/m3v1.json")

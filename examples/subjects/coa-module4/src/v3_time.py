"""Module 4, video 3: vector execution time: convoys, chimes, startup."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m4")
from common import Script
from vec import time, convoys

D = [('LV', 'V1', []), ('MULVS.D', 'V2', ['V1']), ('LV', 'V3', []), ('ADDVV.D', 'V4', ['V2', 'V3']), ('SV', None, ['V4'])]
T64, CS = time(D, 64)
assert [[i[0] for i in c] for c in CS] == [['LV'], ['MULVS.D', 'LV'], ['ADDVV.D'], ['SV']]
assert T64 == 298 and 4 * 64 == 256 and 12 + 12 + 6 + 12 == 42
assert time(D, 8)[0] == 74 and round(74 / 8, 2) == 9.25 and round(298 / 64, 2) == 4.66
E = [('LV', 'V1', []), ('LV', 'V2', []), ('DIVVV.D', 'V3', ['V1', 'V2']), ('MULVS.D', 'V4', ['V1']), ('ADDVV.D', 'V5', ['V3', 'V4']), ('SV', None, ['V5'])]
assert [[i[0] for i in c] for c in convoys(E)] == [['LV'], ['LV'], ['DIVVV.D', 'MULVS.D'], ['ADDVV.D'], ['SV']]
assert time(E, 64)[0] == 382 and 12 + 12 + 20 + 6 + 12 == 62
Q = [('LV', 'V1', []), ('LV', 'V2', []), ('MULVV.D', 'V3', ['V1', 'V2']), ('ADDVS.D', 'V4', ['V3']), ('SV', None, ['V4'])]
assert len(convoys(Q)) == 5 and time(Q, 64)[0] == 369 and time(Q, 32)[0] == 209
assert time(D, 32)[0] == 170 and time(D, 1)[0] == 46 and round(170 / 32, 2) == 5.31
assert 12 + 12 + 7 + 6 + 12 == 49 and round(369 / 64, 2) == 5.77 and round(209 / 32, 2) == 6.53

s = Script("Vector execution time")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "What decides the time"],
    [2, "Convoys"],
    [3, "Chimes"],
    [4, "DAXPY in convoys"],
    [5, "Adding startup time"],
    [6, "A convoy with two units"],
    [7, "Short vectors pay more"],
    [8, "Exam question"]]})
s.obj({"id": "fac", "type": "table", "region": "center", "columns": ["the time depends on", "because"], "rows": [
    ["the vector length n", "one element per cycle per unit"],
    ["structural hazards", "VMIPS has one unit of each kind, and one load-store unit"],
    ["data dependences", "an instruction may need the whole result of another"],
    ["startup latency", "each pipeline must fill before the first result"]]})
s.obj({"id": "cv", "type": "table", "region": "center", "columns": ["a convoy is", "a set of vector instructions that can start together"], "rows": [
    ["rule 1: no structural hazard", "no two need the same unit"],
    ["rule 2 (no chaining yet)", "none needs a result produced in the same convoy"],
    ["so", "convoys run one after another; inside one, all run at once"]]})
s.obj({"id": "ch", "type": "math", "region": "center", "lines": [
    "\"chime\" = \"the time to execute one convoy\" approx n \"cycles\"",
    "m \"convoys, length\" n: quad \"time\" approx m times n \"cycles\"",
    "\"chimes ignore startup: good for long vectors, an estimate\""]})
s.obj({"id": "dx", "type": "code", "region": "left", "language": "asm", "lines": [
    "LV       V1,Rx",
    "MULVS.D  V2,V1,F0",
    "LV       V3,Ry",
    "ADDVV.D  V4,V2,V3",
    "SV       V4,Ry"]})
s.obj({"id": "dc", "type": "table", "region": "right", "columns": ["convoy", "instructions", "why it ends"], "rows": [
    ["1", "", ""], ["2", "", ""], ["3", "", ""], ["4", "", ""]]})
s.obj({"id": "st", "type": "table", "region": "center", "columns": ["unit", "startup (cycles)"], "rows": [
    ["vector load/store", "12"], ["FP multiply", "7"], ["FP add", "6"], ["FP divide", "20"]]})
s.obj({"id": "stm", "type": "math", "region": "center", "lines": [
    "\"convoy time\" = \"largest startup in the convoy\" + n",
    "\"DAXPY, \" n = 64: quad (12 + 64) + (12 + 64) + (6 + 64) + (12 + 64) = 298 \"cycles\"",
    "\"chime estimate\" 4 times 64 = 256 quad \"startup adds\" 42",
    "298 / 64 approx 4.66 \"cycles per element\""]})
s.obj({"id": "tl", "type": "table", "region": "center", "columns": ["convoy", "instructions", "starts", "ends", "cycles"], "rows": [
    ["1", "LV", "0", "76", "12 + 64"], ["2", "MULVS.D, LV", "76", "152", "12 + 64"], ["3", "ADDVV.D", "152", "222", "6 + 64"], ["4", "SV", "222", "298", "12 + 64"]]})
s.obj({"id": "ex", "type": "code", "region": "left", "language": "asm", "lines": [
    "LV       V1,Rx",
    "LV       V2,Ry",
    "DIVVV.D  V3,V1,V2",
    "MULVS.D  V4,V1,F0",
    "ADDVV.D  V5,V3,V4",
    "SV       V5,Rz"]})
s.obj({"id": "exc", "type": "table", "region": "right", "columns": ["convoy", "instructions", "cycles"], "rows": [
    ["1", "LV V1", "12 + n"], ["2", "LV V2", "12 + n"], ["3", "DIVVV.D, MULVS.D", "max(20, 7) + n"], ["4", "ADDVV.D", "6 + n"], ["5", "SV", "12 + n"], ["total", "62 + 5n", "n = 64: 382"]]})
s.obj({"id": "sh", "type": "table", "region": "center", "columns": ["vector length n", "time = 42 + 4n", "cycles per element"], "rows": [
    ["64", "298", "4.66"], ["32", "170", "5.31"], ["8", "74", "9.25"], ["1", "46", "46"]]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "asm", "lines": [
    "LV       V1,Rx",
    "LV       V2,Ry",
    "MULVV.D  V3,V1,V2",
    "ADDVS.D  V4,V3,F0",
    "SV       V4,Rz",
    "; no chaining, one load-store unit. Find the convoys, the chimes,",
    "; and the cycles for n = 64 and n = 32, with the startup table"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["convoy", "instruction", "why a new convoy", "startup"], "rows": [
    ["1", "LV V1", "", "12"],
    ["2", "LV V2", "the load-store unit is busy", "12"],
    ["3", "MULVV.D", "needs V2 from convoy 2", "7"],
    ["4", "ADDVS.D", "needs V3", "6"],
    ["5", "SV", "needs V4", "12"]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "5 \"chimes\" quad \"startups\" 12 + 12 + 7 + 6 + 12 = 49",
    "n = 64: quad 49 + 5 times 64 = 369 \"cycles\" quad 5.77 \"per element\"",
    "n = 32: quad 49 + 5 times 32 = 209 \"cycles\" quad 6.53 \"per element\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Six instructions for DAXPY is impressive. But how many cycles do they take? Exam questions ask exactly this, and the answer needs two ideas: convoys and chimes.", [s.head("Vector execution time")])
s.step("Here are the eight stages.", show("stages"))
s.step("What decides the time, convoys, and chimes.", [hl("stages[0..=2]")])
s.step("Then DAXPY divided into convoys, startup time, a convoy with two units, why short vectors pay more, and an exam question.", [hl("stages[3..=7]")])

s.scene("fac")
s.step("Stage 1: four things decide how long vector code takes. The vector length: each unit handles one element per cycle.", [s.head("Stage 1 of 8: what decides the time")] + hide("stages") + show("fac") + [hl("fac[0]")])
s.step("Structural hazards: VMIPS has one unit of each kind, and only one load-store unit. Two loads cannot run at once.", [hl("fac[1]")])
s.step("Data dependences: an instruction may need another's result.", [hl("fac[2]")])
s.step("And startup: every pipeline takes some cycles to fill before its first result appears.", [hl("fac[3]"), s.take("length · structural hazards · dependences · startup")])

s.scene("convoy")
s.step("Stage 2: a convoy is a set of vector instructions that can start executing together.", [s.head("Stage 2 of 8: convoys"), s.untake()] + hide("fac") + show("cv"))
s.step("Rule 1: no structural hazard. No two instructions in a convoy may need the same unit.", [hl("cv[0]")])
s.step("Rule 2, for now: no instruction may need a result produced inside the same convoy. Next video, chaining relaxes this rule.", [hl("cv[1]")])
s.step("Convoys execute one after another. Within a convoy, all the instructions run side by side, each on its own unit.", [hl("cv[2]"), s.take("convoy: instructions that can run together")])

s.scene("chime")
s.step("Stage 3: a chime is the time to execute one convoy. With one element per cycle, a convoy on vectors of length n takes about n cycles.", [s.head("Stage 3 of 8: chimes"), s.untake()] + hide("cv") + show("ch") + [hl("ch[0]")])
s.step("So code that forms m convoys takes about m chimes: m times n cycles.", [rv("ch[1]"), hl("ch[1]")])
s.step("This ignores startup, so it is an estimate, accurate when vectors are long. Counting chimes is the quick first step in every timing question.", [rv("ch[2]"), hl("ch[2]"), s.take("m convoys ≈ m × n cycles")])

s.scene("daxpy")
s.step("Stage 4: divide DAXPY into convoys. Start with the first load.", [s.head("Stage 4 of 8: DAXPY in convoys"), s.untake()] + hide("ch") + show("dx", "dc") + [ml("dx", 1, 1), st("dc[0][1]", "LV V1")])
s.step("The multiply needs V1, which the load is producing. Without chaining it cannot join. Convoy 1 is just the load.", [ml("dx", 2, 2), st("dc[0][2]", "MULVS needs V1")])
s.step("Convoy 2 starts with the multiply. The second load is independent of it, and uses a different unit, so it joins.", [st("dc[1][1]", "MULVS.D, LV V3"), ml("dx", 2, 3)])
s.step("The add needs V2 and V3, both produced in convoy 2. So it starts convoy 3.", [st("dc[1][2]", "ADDVV needs V2, V3"), st("dc[2][1]", "ADDVV.D", 0.3), ml("dx", 4, 4)])
s.step("The store needs V4. Convoy 4.", [st("dc[2][2]", "SV needs V4"), st("dc[3][1]", "SV", 0.3), ml("dx", 5, 5)])
s.step("Four convoys: four chimes. For 64 elements, about 256 cycles, 4 cycles per element.", [hl("dc[0..=3]"), s.take("DAXPY without chaining: 4 chimes")])

s.scene("start")
s.step("Stage 5: now the startup. These are the textbook's latencies: 12 cycles for the load-store unit, 7 for the multiplier, 6 for the adder, 20 for the divider.", [s.head("Stage 5 of 8: adding startup"), s.untake()] + hide("dx", "dc") + show("st") + [hl("st[0..=3]")])
s.step("A convoy takes its largest startup, plus n cycles. The instructions inside it start together, so the slowest pipeline decides when the convoy is done.", hide("st") + show("stm") + [hl("stm[0]")])
s.step("DAXPY: 12 plus 64 for the load, 12 plus 64 for the multiply and load, 6 plus 64 for the add, 12 plus 64 for the store. 298 cycles.", [rv("stm[1]"), hl("stm[1]")])
s.step("The chime estimate was 256. Startup added 42.", [rv("stm[2]"), hl("stm[2]")])
s.step("About 4.66 cycles per element.", [rv("stm[3]"), hl("stm[3]")])
s.step("As a timeline: convoy 1 runs from cycle 0 to 76, convoy 2 from 76 to 152, convoy 3 to 222, and the store finishes at 298. Each convoy waits for the one before it to finish completely.", hide("stm") + show("tl") + [hl("tl[0..=3]"), s.take("time = Σ (largest startup + n)")])

s.scene("two")
s.step("Stage 6: a convoy can hold two arithmetic units with different startups. Here a divide and a multiply.", [s.head("Stage 6 of 8: a convoy with two units"), s.untake()] + hide("tl") + show("ex", "exc") + [ml("ex", 1, 6)])
s.step("The two loads need separate convoys: one load-store unit.", [ml("ex", 1, 2), hl("exc[0..=1]")])
s.step("The divide needs V2, so it starts convoy 3. The multiply needs only V1, finished long ago, and uses a different unit. It joins the divide.", [ml("ex", 3, 4), hl("exc[2]")])
s.step("That convoy takes the larger startup: the divider's 20, not the multiplier's 7.", [mk("exc[2][2]")])
s.step("The add needs both results: convoy 4. The store: convoy 5.", [ml("ex", 5, 6), hl("exc[3..=4]")])
s.step("Startups 12, 12, 20, 6 and 12 make 62. For 64 elements: 62 plus 320, 382 cycles.", [hl("exc[5]"), s.take("a shared convoy pays its slowest startup")])

s.scene("short")
s.step("Stage 7: startup is paid once per convoy, whatever the length. So it matters more and more as vectors get shorter.", [s.head("Stage 7 of 8: short vectors"), s.untake()] + hide("ex", "exc") + show("sh"))
s.step("At 64 elements: 4.66 cycles each. At 32: 5.31.", [hl("sh[0..=1]")])
s.step("At 8 elements, 74 cycles: over 9 cycles per element. And a single element takes 46 cycles, far slower than scalar code.", [hl("sh[2..=3]")])
s.step("Two remedies follow in the next videos. Chaining cuts the number of convoys, so fewer startups are paid. And strip mining handles vectors longer than a register, where startup is paid once per strip.", [hl("sh[0..=1]")])
s.step("So vector machines need long vectors to pay off. This is also why the time per convoy matters more than the count of instructions.", [mk("sh[0]"), s.take("startup is fixed · long vectors hide it")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("sh") + show("q"))
s.step("Two loads, a multiply, an add of a scalar, and a store. No chaining, one load-store unit. Find the convoys, the chimes, and the cycles for 64 and 32 elements. Pause and work it out.", [ml("q", 1, 7)])
s.step("Convoy 1: the first load. The second load cannot join: there is only one load-store unit.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("The multiply needs V2, produced in convoy 2, so it starts convoy 3. The add needs V3: convoy 4. The store needs V4: convoy 5.", [hl("qa[2..=4]")])
s.step("Five chimes. The startups add up to 49.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("For 64 elements: 49 plus 5 times 64, 369 cycles, 5.77 per element.", [rv("qb[1]"), hl("qb[1]")])
s.step("For 32 elements: 49 plus 160, 209 cycles, 6.53 per element. Shorter vectors, higher cost per element.", [rv("qb[2]"), hl("qb[2]")])
s.step("The usual slip: putting two loads in one convoy. VMIPS has a single load-store unit, so two memory instructions can never share a convoy, though one can share with arithmetic.", [s.take("one load-store unit: never two memory instructions in a convoy")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("A convoy is a group of instructions with no structural hazard and, without chaining, no dependence inside it. Each convoy takes one chime, about n cycles.", [hl("stages[0..=3]")])
s.step("Adding startup: each convoy costs its largest startup plus n. Short vectors pay much more per element.", [hl("stages[4..=6]")])
s.step("Next video: chaining, which lets dependent instructions share a convoy, and multiple lanes, which process several elements per cycle.", [mk("stages[0..=7]"), s.take("Next: chaining and lanes")])

s.save("/home/claude/playlist/m4/m4v3.json")

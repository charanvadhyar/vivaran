"""Module 4, video 4: chaining and multiple lanes."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m4")
from common import Script
from vec import time, convoys

D = [('LV', 'V1', []), ('MULVS.D', 'V2', ['V1']), ('LV', 'V3', []), ('ADDVV.D', 'V4', ['V2', 'V3']), ('SV', None, ['V4'])]
assert [[i[0] for i in c] for c in convoys(D, True)] == [['LV', 'MULVS.D'], ['LV', 'ADDVV.D'], ['SV']]
assert time(D, 64)[0] == 298 and time(D, 64, True)[0] == 241 and (12 + 7 + 64, 12 + 6 + 64, 12 + 64) == (83, 82, 76)
assert time(D, 64, True, 4)[0] == 97 and (12 + 7 + 16, 12 + 6 + 16, 12 + 16) == (35, 34, 28)
assert round(298 / 97, 2) == 3.07
LT = [(L, time(D, 64, True, L)[0]) for L in (1, 2, 4, 8, 16)]
assert [x for _, x in LT] == [241, 145, 97, 73, 61] and [round(241 / x, 2) for _, x in LT] == [1.0, 1.66, 2.48, 3.3, 3.95]
Q = [('LV', 'V1', []), ('LV', 'V2', []), ('MULVV.D', 'V3', ['V1', 'V2']), ('ADDVS.D', 'V4', ['V3']), ('SV', None, ['V4'])]
assert [[i[0] for i in c] for c in convoys(Q, True)] == [['LV'], ['LV', 'MULVV.D', 'ADDVS.D'], ['SV']]
assert time(Q, 64)[0] == 369 and time(Q, 64, True)[0] == 241 and time(Q, 64, True, 2)[0] == 145
assert (12 + 32, 12 + 7 + 6 + 32, 12 + 32) == (44, 57, 44)

s = Script("Chaining and lanes")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The idea of chaining"],
    [2, "Chaining, element by element"],
    [3, "DAXPY with chaining"],
    [4, "Startup with chaining"],
    [5, "Multiple lanes"],
    [6, "DAXPY on four lanes"],
    [7, "How far lanes go"],
    [8, "Exam question"]]})
s.obj({"id": "idea", "type": "table", "region": "center", "columns": ["chaining", "meaning"], "rows": [
    ["without it", "MULVS.D waits until LV has finished all 64 elements"],
    ["with it", "MULVS.D starts on element 0 as soon as element 0 arrives"],
    ["like", "forwarding in a pipeline, applied to every element"],
    ["convoy rule 2", "dropped: dependent instructions may share a convoy"],
    ["history", "Cray-1 (1976); modern machines chain flexibly, any unit to any unit"]]})
s.obj({"id": "ch", "type": "table", "region": "center", "columns": ["cycle", "13", "14", "15", "…", "20", "21", "22"], "rows": [
    ["LV writes element", "0", "1", "2", "…", "7", "8", "9"],
    ["MULVS.D starts element", "", "0", "1", "…", "6", "7", "8"],
    ["MULVS.D finishes element", "", "", "", "…", "", "0", "1"]]})
s.obj({"id": "dc", "type": "table", "region": "center", "columns": ["convoy", "without chaining", "with chaining"], "rows": [
    ["1", "LV", "LV → MULVS.D"],
    ["2", "MULVS.D, LV", "LV → ADDVV.D"],
    ["3", "ADDVV.D", "SV"],
    ["4", "SV", ""],
    ["chimes", "4: about 256 cycles", "3: about 192 cycles"]]})
s.obj({"id": "stm", "type": "math", "region": "center", "lines": [
    "\"in a chained convoy, startups add: each unit waits for the first element of the one before\"",
    "(12 + 7 + 64) + (12 + 6 + 64) + (12 + 64) = 83 + 82 + 76 = 241 \"cycles\"",
    "\"against 298 without chaining\" quad 241 / 64 approx 3.77 \"cycles per element\""]})
s.obj({"id": "ln", "type": "table", "region": "center", "columns": ["lane", "elements it handles", "its slice of each register"], "rows": [
    ["0", "0, 4, 8, 12, …, 60", "elements 0, 4, 8, …"],
    ["1", "1, 5, 9, 13, …, 61", "elements 1, 5, 9, …"],
    ["2", "2, 6, 10, 14, …, 62", "elements 2, 6, 10, …"],
    ["3", "3, 7, 11, 15, …, 63", "elements 3, 7, 11, …"]]})
s.obj({"id": "lnx", "type": "table", "region": "center", "columns": ["multiple lanes", "effect"], "rows": [
    ["each lane", "its own pipelined unit of each kind, and a slice of the register file"],
    ["element i", "always goes to lane i mod L: no wires between lanes"],
    ["a chime", "now n / L cycles: 64 elements on 4 lanes in 16"],
    ["the same binary", "runs on 1 lane or 16: only the speed changes"]]})
s.obj({"id": "l4", "type": "math", "region": "center", "lines": [
    "\"4 lanes:\" quad \"each convoy needs\" 64 / 4 = 16 \"cycles plus startup\"",
    "(12 + 7 + 16) + (12 + 6 + 16) + (12 + 16) = 35 + 34 + 28 = 97 \"cycles\"",
    "298 \"(plain)\" -> 241 \"(chained)\" -> 97 \"(chained, 4 lanes)\" quad 298 / 97 approx 3.07 \"times faster\""]})
s.obj({"id": "lt", "type": "table", "region": "center", "columns": ["lanes", "cycles: 49 + 3 × ⌈64 / L⌉", "speedup over 1 lane", "startup share"], "rows": [
    [str(L), str(x), f"{241 / x:.2f}", f"{round(100 * 49 / x)}%"] for L, x in LT]})
s.obj({"id": "q", "type": "code", "region": "center", "language": "asm", "lines": [
    "LV       V1,Rx",
    "LV       V2,Ry",
    "MULVV.D  V3,V1,V2",
    "ADDVS.D  V4,V3,F0",
    "SV       V4,Rz",
    "; n = 64; startups: load 12, multiply 7, add 6. One load-store unit.",
    "; a) convoys with chaining   b) cycles with chaining   c) cycles with 2 lanes"]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["convoy", "instructions", "1 lane", "2 lanes"], "rows": [
    ["1", "LV V1", "12 + 64 = 76", "12 + 32 = 44"],
    ["2", "LV V2 → MULVV.D → ADDVS.D", "12 + 7 + 6 + 64 = 89", "25 + 32 = 57"],
    ["3", "SV", "12 + 64 = 76", "12 + 32 = 44"],
    ["total", "3 chimes", "241", "145"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Last video, DAXPY took four convoys and 298 cycles, because every dependent instruction waited for a whole vector. Two ideas cut that sharply: chaining, and multiple lanes.", [s.head("Chaining and lanes")])
s.step("Here are the eight stages.", show("stages"))
s.step("What chaining is, how it works element by element, DAXPY with chaining, and its startup cost.", [hl("stages[0..=3]")])
s.step("Then multiple lanes, DAXPY on four lanes, how far lanes can go, and an exam question.", [hl("stages[4..=7]")])

s.scene("idea")
s.step("Stage 1: without chaining, the multiply waits until the load has delivered all 64 elements.", [s.head("Stage 1 of 8: the idea")] + hide("stages") + show("idea") + [hl("idea[0]")])
s.step("With chaining, the multiply starts on element 0 as soon as element 0 arrives, while the load is still bringing the rest.", [hl("idea[1]")])
s.step("It is forwarding, as in an ordinary pipeline, applied to every element of a vector.", [hl("idea[2]")])
s.step("So the second convoy rule goes away. Dependent instructions can share a convoy, as long as they use different units.", [hl("idea[3]")])
s.step("The Cray-1 introduced chaining in 1976. Modern vector machines chain flexibly, from any unit to any other.", [hl("idea[4]"), s.take("chaining: start on element 0 of a result at once")])

s.scene("elem")
s.step("Stage 2: element by element. The load's first element arrives in cycle 13, after its 12-cycle startup.", [s.head("Stage 2 of 8: element by element"), s.untake()] + hide("idea") + show("ch") + [hl("ch[0]")])
s.step("The multiply starts on element 0 in cycle 14, element 1 in cycle 15, one cycle behind the load.", [hl("ch[1]")])
s.step("After its own 7-cycle startup, the multiply's first result comes out in cycle 21, and then one per cycle.", [hl("ch[2]")])
s.step("The two units work side by side. The multiply's results lag the load by only its own startup, not by 64 cycles.", [mk("ch[1]"), s.take("a chained unit lags by its startup, not by n")])

s.scene("daxpy")
s.step("Stage 3: divide DAXPY into convoys again, now with chaining.", [s.head("Stage 3 of 8: DAXPY with chaining"), s.untake()] + hide("ch") + show("dc"))
s.step("Convoy 1: the load chains into the multiply.", [hl("dc[0]")])
s.step("Convoy 2: the second load cannot join convoy 1, because the load-store unit is busy. It starts convoy 2, and the add chains onto it, taking the multiply's result from convoy 1.", [hl("dc[1]")])
s.step("Convoy 3: the store.", [hl("dc[2]")])
s.step("Three chimes instead of four: about 192 cycles instead of 256.", [hl("dc[4]"), s.take("DAXPY: 4 chimes → 3")])

s.scene("start")
s.step("Stage 4: startup in a chained convoy. Each unit waits for the first element from the unit before it, so the startups add up.", [s.head("Stage 4 of 8: startup with chaining"), s.untake()] + hide("dc") + show("stm") + [hl("stm[0]")])
s.step("Convoy 1: 12 for the load plus 7 for the multiply, plus 64. Convoy 2: 12 plus 6 plus 64. Convoy 3: 12 plus 64. 241 cycles in all.", [rv("stm[1]"), hl("stm[1]")])
s.step("Against 298 without chaining: one startup fewer to wait through, and the 64 cycles of the multiply overlapped with the load. About 3.77 cycles per element.", [rv("stm[2]"), hl("stm[2]"), s.take("chained convoy: sum of its startups + n")])

s.scene("lanes")
s.step("Stage 5: still, each unit finishes only one element per cycle. To go faster, add lanes. With four lanes, each unit is copied four times.", [s.head("Stage 5 of 8: multiple lanes"), s.untake()] + hide("stm") + show("ln") + [hl("ln[0..=3]")])
s.step("Element i always goes to lane i mod 4. Lane 0 handles elements 0, 4, 8 and so on; lane 1 handles 1, 5, 9.", [hl("ln[0]"), hl("ln[1]", 0.4)])
s.step("The register file is split the same way: each lane holds its own elements of every register.", [hl("ln[2..=3]")])
s.step("Each lane has its own pipelined unit of each kind, and its own slice of the registers.", hide("ln") + show("lnx") + [hl("lnx[0]")])
s.step("Because element i always lives in lane i mod L, an element-wise operation never needs wires between lanes. That makes lanes cheap to add.", [hl("lnx[1]")])
s.step("A chime shrinks from n to n over L cycles: 64 elements on 4 lanes in 16.", [hl("lnx[2]")])
s.step("And the same program runs on 1 lane or 16. Only the speed changes. This is how vector machines scale with the transistor budget.", [hl("lnx[3]"), s.take("L lanes: a chime becomes n / L cycles")])

s.scene("l4")
s.step("Stage 6: DAXPY, chained, on four lanes. Each convoy now needs 16 cycles plus its startups.", [s.head("Stage 6 of 8: DAXPY on four lanes"), s.untake()] + hide("lnx") + show("l4") + [hl("l4[0]")])
s.step("35, plus 34, plus 28: 97 cycles.", [rv("l4[1]"), hl("l4[1]")])
s.step("From 298, to 241 with chaining, to 97 with four lanes: over 3 times faster. Notice that startup, 49 of the 97 cycles, is now about half the time. With more lanes, it matters even more.", [rv("l4[2]"), hl("l4[2]"), s.take("298 → 241 → 97 cycles")])

s.scene("far")
s.step("Stage 7: so why not 64 lanes? Look at chained DAXPY as lanes are added. The startups, 49 cycles, never shrink; only the 3 chimes do.", [s.head("Stage 7 of 8: how far lanes go"), s.untake()] + hide("l4") + show("lt") + [hl("lt[0]")])
s.step("Two lanes: 145 cycles, 1.66 times faster. Four: 97, nearly 2.5 times.", [hl("lt[1..=2]")])
s.step("Eight lanes: 73. Sixteen: 61, under 4 times faster for 16 times the hardware.", [hl("lt[3..=4]")])
s.step("Look at the last column. At 16 lanes, startup is 80 percent of the time. Amdahl's law again: the part that lanes cannot speed up takes over.", [hl("lt[4][3]")])
s.step("So real designs balance lanes against vector length. Longer vectors, or several vector instructions overlapping, keep wide machines busy.", [s.take("lanes shrink the chimes, never the startup")])

s.scene("exam")
s.step("Now an exam question: the sequence from last video's exam, now with chaining.", [s.head("Exam question"), s.untake()] + hide("lt") + show("q") + [ml("q", 1, 5)])
s.step("Find the convoys with chaining, the cycles for 64 elements, and the cycles with 2 lanes. Pause and work it out.", [ml("q", 6, 7)])
s.step("Convoy 1: the first load. The second load cannot join: one load-store unit.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Convoy 2: the second load, chained into the multiply, chained into the add. Three units, one convoy.", [hl("qa[1]")])
s.step("Convoy 3: the store, which needs the load-store unit again.", [hl("qa[2]")])
s.step("With one lane: 76, plus 12 plus 7 plus 6 plus 64, which is 89, plus 76. 241 cycles, against 369 without chaining.", [hl("qa[0..=3]")])
s.step("With 2 lanes, each convoy needs 32 cycles plus startups: 44, 57 and 44. 145 cycles.", [mk("qa[3]")])
s.step("The usual slip: adding startups in a convoy that is not chained, or taking only the largest in one that is. Unchained: the largest. Chained: the sum.", [s.take("unchained: largest startup · chained: sum of startups")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Chaining forwards each element as it is produced, so dependent instructions share a convoy. DAXPY drops from 4 chimes to 3, and from 298 cycles to 241.", [hl("stages[0..=3]")])
s.step("Multiple lanes run element i in lane i mod L, cutting each chime to n over L. Four lanes bring DAXPY to 97 cycles, but startup limits how far lanes help.", [hl("stages[4..=6]")])
s.step("Next video: what if the vector is longer than 64, or of unknown length? Strip mining and the vector length register.", [mk("stages[0..=7]"), s.take("Next: strip mining")])

s.save("/home/claude/playlist/m4/m4v4.json")

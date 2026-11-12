"""Module 3, video 2: loop unrolling and instruction scheduling (textbook latencies)."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from sched import run

L = lambda d, a: ('L.D', 'load', d, [a]); A = lambda d, x, y: ('ADD.D', 'fp', d, [x, y])
S = lambda v, a: ('S.D', 'store', None, [v, a]); I = lambda d: ('DADDUI', 'int', d, [d])
B = lambda *r: ('BNE', 'branch', None, list(r))
assert run([L('F0', 'R1'), A('F4', 'F0', 'F2'), S('F4', 'R1'), I('R1'), B('R1', 'R2')]) == [1, 3, 6, 7, 9]
assert run([L('F0', 'R1'), I('R1'), A('F4', 'F0', 'F2'), S('F4', 'R1x'), B('R1', 'R2')]) == [1, 2, 3, 6, 7]
un = []
for f, g in [('F0', 'F4'), ('F6', 'F8'), ('F10', 'F12'), ('F14', 'F16')]:
    un += [L(f, 'R1'), A(g, f, 'F2'), S(g, 'R1')]
assert run(un + [I('R1'), B('R1', 'R2')])[-1] == 27
us = [L('F0', 'R1'), L('F6', 'R1'), L('F10', 'R1'), L('F14', 'R1'), A('F4', 'F0', 'F2'), A('F8', 'F6', 'F2'),
      A('F12', 'F10', 'F2'), A('F16', 'F14', 'F2'), S('F4', 'R1'), S('F8', 'R1'), I('R1'), S('F12', 'R1x'),
      S('F16', 'R1x'), B('R1', 'R2')]
assert run(us) == list(range(1, 15))
assert (27 / 4, 14 / 4) == (6.75, 3.5)
ex = [L('F0', 'R1'), L('F2', 'R2'), A('F4', 'F0', 'F2'), S('F4', 'R1'), I('R1'), I('R2'), B('R1', 'R3')]
assert run(ex)[-1] == 10
exs = [L('F0', 'R1'), L('F2', 'R2'), I('R1'), A('F4', 'F0', 'F2'), I('R2'), S('F4', 'R1x'), B('R1', 'R3')]
assert run(exs) == [1, 2, 3, 4, 5, 7, 8]
exu = [L('F0', 'R1'), L('F2', 'R2'), L('F6', 'R1'), L('F8', 'R2'), A('F4', 'F0', 'F2'), A('F10', 'F6', 'F8'),
       I('R1'), I('R2'), S('F4', 'R1x'), S('F10', 'R1x'), B('R1', 'R3')]
assert run(exu) == list(range(1, 12)) and 11 / 2 == 5.5 and round(10 / 5.5, 2) == 1.82
assert 1000 % 3 == 1 and 1000 // 3 == 333

s = Script("Loop unrolling and instruction scheduling")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The latencies we must respect"],
    [2, "The loop as written: 9 cycles"],
    [3, "Scheduling it: 7 cycles"],
    [4, "Unrolling four times: 27 cycles for 4"],
    [5, "Unrolling and scheduling: 3.5 cycles each"],
    [6, "Comparing all four"],
    [7, "What the compiler must check, and the costs"],
    [8, "Exam question"]]})
s.obj({"id": "lat", "type": "table", "region": "center", "columns": ["producer", "consumer", "stall cycles between them"], "rows": [
    ["FP ALU op", "another FP ALU op", "3"],
    ["FP ALU op", "store double", "2"],
    ["load double", "FP ALU op", "1"],
    ["load double", "store double", "0"],
    ["integer ALU op", "branch", "1"]]})
s.obj({"id": "c1", "type": "code", "region": "center", "language": "asm", "lines": [
    "Loop: L.D    F0,0(R1)      ; 1",
    "      stall                ; 2",
    "      ADD.D  F4,F0,F2      ; 3",
    "      stall                ; 4",
    "      stall                ; 5",
    "      S.D    F4,0(R1)      ; 6",
    "      DADDUI R1,R1,#-8     ; 7",
    "      stall                ; 8",
    "      BNE    R1,R2,Loop    ; 9"]})
s.obj({"id": "c2", "type": "code", "region": "center", "language": "asm", "lines": [
    "Loop: L.D    F0,0(R1)      ; 1",
    "      DADDUI R1,R1,#-8     ; 2",
    "      ADD.D  F4,F0,F2      ; 3",
    "      stall                ; 4",
    "      stall                ; 5",
    "      S.D    F4,8(R1)      ; 6",
    "      BNE    R1,R2,Loop    ; 7"]})
s.obj({"id": "c3", "type": "code", "region": "center", "language": "asm", "lines": [
    "Loop: L.D    F0,0(R1)",
    "      ADD.D  F4,F0,F2",
    "      S.D    F4,0(R1)",
    "      L.D    F6,-8(R1)",
    "      ADD.D  F8,F6,F2",
    "      S.D    F8,-8(R1)",
    "      L.D    F10,-16(R1)",
    "      ADD.D  F12,F10,F2",
    "      S.D    F12,-16(R1)",
    "      L.D    F14,-24(R1)",
    "      ADD.D  F16,F14,F2",
    "      S.D    F16,-24(R1)",
    "      DADDUI R1,R1,#-32",
    "      BNE    R1,R2,Loop"]})
s.obj({"id": "c3m", "type": "math", "region": "bottom", "lines": [
    "4 times (2 + 3 + 1) + 1 + 2 = 27 \"cycles for 4 elements\" quad 27 / 4 = 6.75"]})
s.obj({"id": "c4", "type": "code", "region": "center", "language": "asm", "lines": [
    "Loop: L.D    F0,0(R1)      ; 1",
    "      L.D    F6,-8(R1)     ; 2",
    "      L.D    F10,-16(R1)   ; 3",
    "      L.D    F14,-24(R1)   ; 4",
    "      ADD.D  F4,F0,F2      ; 5",
    "      ADD.D  F8,F6,F2      ; 6",
    "      ADD.D  F12,F10,F2    ; 7",
    "      ADD.D  F16,F14,F2    ; 8",
    "      S.D    F4,0(R1)      ; 9",
    "      S.D    F8,-8(R1)     ; 10",
    "      DADDUI R1,R1,#-32    ; 11",
    "      S.D    F12,16(R1)    ; 12",
    "      S.D    F16,8(R1)     ; 13",
    "      BNE    R1,R2,Loop    ; 14"]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["version", "cycles per element", "useful work", "overhead + stalls"], "rows": [
    ["as written", "9", "3", "6"],
    ["scheduled", "7", "3", "4"],
    ["unrolled ×4", "6.75", "3", "3.75"],
    ["unrolled ×4 and scheduled", "3.5", "3", "0.5"]]})
s.obj({"id": "chk", "type": "table", "region": "center", "columns": ["the compiler must", "in our loop"], "rows": [
    ["find that iterations are independent", "each x[i] uses only x[i] and F2"],
    ["use different registers per copy", "F0/F4, F6/F8, F10/F12, F14/F16"],
    ["remove the extra tests and branches", "one DADDUI by 32, one BNE"],
    ["prove loads and stores may swap", "the addresses differ: 0, −8, −16, −24 off R1"],
    ["reschedule, keeping true dependences", "each S.D still after its ADD.D, each ADD.D after its L.D"]]})
s.obj({"id": "cost", "type": "table", "region": "center", "columns": ["cost", "why"], "rows": [
    ["more registers", "8 FP registers instead of 2: renaming needs names"],
    ["bigger code", "14 instructions instead of 5: more instruction cache misses"],
    ["shrinking returns", "the overhead is already only half a cycle per element"],
    ["unknown trip count n", "run n mod k iterations first, then n div k unrolled ones"]]})
s.obj({"id": "strip", "type": "math", "region": "bottom", "lines": [
    "n = 1000, k = 3 : quad 1000 mod 3 = 1 \"plain iteration, then\" 1000 div 3 = 333 \"unrolled ones\""]})
s.obj({"id": "q", "type": "code", "region": "left", "language": "asm", "lines": [
    "Loop: L.D    F0,0(R1)",
    "      L.D    F2,0(R2)",
    "      ADD.D  F4,F0,F2",
    "      S.D    F4,0(R1)",
    "      DADDUI R1,R1,#-8",
    "      DADDUI R2,R2,#-8",
    "      BNE    R1,R3,Loop"]})
s.obj({"id": "qx", "type": "table", "region": "right", "columns": ["find"], "rows": [
    ["a) cycles as written"], ["b) cycles scheduled"], ["c) unrolled ×2, scheduled: per element"], ["d) FP registers for c"]]})
s.obj({"id": "qa1", "type": "code", "region": "left", "language": "asm", "lines": [
    "L.D    F0,0(R1)    ; 1",
    "L.D    F2,0(R2)    ; 2",
    "DADDUI R1,R1,#-8   ; 3",
    "ADD.D  F4,F0,F2    ; 4",
    "DADDUI R2,R2,#-8   ; 5",
    "stall              ; 6",
    "S.D    F4,8(R1)    ; 7",
    "BNE    R1,R3,Loop  ; 8"]})
s.obj({"id": "qa2", "type": "code", "region": "right", "language": "asm", "lines": [
    "L.D    F0,0(R1)    ; 1",
    "L.D    F2,0(R2)    ; 2",
    "L.D    F6,-8(R1)   ; 3",
    "L.D    F8,-8(R2)   ; 4",
    "ADD.D  F4,F0,F2    ; 5",
    "ADD.D  F10,F6,F8   ; 6",
    "DADDUI R1,R1,#-16  ; 7",
    "DADDUI R2,R2,#-16  ; 8",
    "S.D    F4,16(R1)   ; 9",
    "S.D    F10,8(R1)   ; 10",
    "BNE    R1,R3,Loop  ; 11"]})
s.obj({"id": "qam", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 10 \"cycles\" quad \"b)\" quad 8 \"cycles\"",
    "\"c)\" quad 11 / 2 = 5.5 \"cycles per element\" quad \"speedup\" 10 / 5.5 approx 1.82",
    "\"d)\" quad \"F0, F2, F4, F6, F8, F10:\" quad 6 \"registers\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("A compiler can expose ILP before the program ever runs, just by reordering and repeating instructions. One loop, four versions, from 9 cycles per element down to 3.5.", [s.head("Loop unrolling and instruction scheduling")])
s.step("Here are the eight stages.", show("stages"))
s.step("The latencies, the loop as written, and the loop scheduled.", [hl("stages[0..=2]")])
s.step("Then unrolling, unrolling with scheduling, a comparison, the costs, and an exam question.", [hl("stages[3..=7]")])

# ---------------------------------------------------------------- latencies
s.scene("lat")
s.step("Stage 1: the rules. These are the textbook's latencies, given as stall cycles needed between a producer and the instruction that uses its result.", [s.head("Stage 1 of 8: the latencies")] + hide("stages") + show("lat"))
s.step("An FP add feeding another FP add needs 3 stall cycles in between. Feeding a store, 2.", [hl("lat[0..=1]")])
s.step("A load feeding an FP add needs 1. A load feeding a store, none.", [hl("lat[2..=3]")])
s.step("And an integer op feeding a branch needs 1, because the branch is resolved early, in decode. We ignore any extra branch penalty here.", [hl("lat[4]"), s.take("a consumer must wait the producer's stall cycles")])

# ---------------------------------------------------------------- as written
s.scene("plain")
s.step("Stage 2: the loop from the last video. It adds F2 to every element of an array, walking R1 downward 8 bytes at a time.", [s.head("Stage 2 of 8: the loop as written"), s.untake()] + hide("lat") + show("c1"))
s.step("The load issues in cycle 1. The add needs F0, so it waits 1 cycle, and issues in cycle 3.", [go("c1", 1), ml("c1", 2, 2), go("c1", 3)])
s.step("The store needs the add's F4: 2 stalls. It issues in cycle 6.", [ml("c1", 4, 5), go("c1", 6)])
s.step("The decrement goes in cycle 7. The branch needs its R1: 1 stall, then cycle 9.", [go("c1", 7), ml("c1", 8, 8), go("c1", 9)])
s.step("9 cycles per element. Only 3 instructions do the real work: load, add and store. The rest is overhead and stalls.", [ml("c1", 1, 9), s.take("as written: 9 cycles per element")])

# ---------------------------------------------------------------- scheduled
s.scene("sched")
s.step("Stage 3: scheduling. Reorder the instructions to fill the stall slots with useful work.", [s.head("Stage 3 of 8: scheduling"), s.untake()] + hide("c1") + show("c2"))
s.step("Move the decrement up, into the slot after the load. Now the branch's 1-cycle wait is already over when it arrives.", [go("c2", 2)])
s.step("But the store now runs after R1 has dropped by 8. So its offset changes from 0 to 8, to reach the same address. The compiler must adjust it.", [go("c2", 6)])
s.step("The add still has to wait 2 cycles before the store. Nothing is left to fill them.", [ml("c2", 4, 5)])
s.step("7 cycles per element. Only 3 do work; the other 4 are the decrement, the branch, and 2 stalls.", [ml("c2", 1, 7), s.take("scheduled: 7 cycles · offsets fixed after moving the decrement")])

# ---------------------------------------------------------------- unrolled
s.scene("unroll")
s.step("Stage 4: loop unrolling. Copy the loop body 4 times, and keep only one decrement and one branch.", [s.head("Stage 4 of 8: unrolling four times"), s.untake()] + hide("c2") + show("c3") + [ml("c3", 1, 12)])
s.step("Each copy uses its own registers: F0 and F4, F6 and F8, F10 and F12, F14 and F16. That is renaming. Without it, the copies would have name dependences and could never overlap.", [ml("c3", 4, 6), ml("c3", 7, 9)])
s.step("The offsets step by 8: 0, minus 8, minus 16, minus 24. Then one decrement by 32, and one branch.", [ml("c3", 13, 14)])
s.step("Without rescheduling, each copy still stalls. A load takes 2 cycles, an add 3, a store 1, and the branch 2. 4 times 6, plus 3: 27 cycles for 4 elements.", show("c3m") + [hl("c3m[0]")])
s.step("6.75 cycles per element. Better than 7, because three decrements and three branches are gone. But the stalls remain.", [s.take("unrolled: overhead shared by 4 elements")])

# ---------------------------------------------------------------- unrolled + scheduled
s.scene("both")
s.step("Stage 5: now schedule the unrolled loop. With four independent copies, there is plenty of work to fill the gaps.", [s.head("Stage 5 of 8: unrolled and scheduled"), s.untake()] + hide("c3", "c3m") + show("c4"))
s.step("All four loads first. By the time the first add issues, in cycle 5, its F0 is long ready.", [ml("c4", 1, 4), go("c4", 5)])
s.step("Then the four adds, back to back. They are independent of each other.", [ml("c4", 5, 8)])
s.step("The first store, in cycle 9, is 4 cycles after its add: more than the 2 it needs.", [go("c4", 9)])
s.step("The decrement slips in between the stores, so the last two stores use offsets 16 and 8 instead of minus 16 and minus 24.", [go("c4", 11), ml("c4", 12, 13)])
s.step("And the branch issues in cycle 14, with no stall at all. 14 cycles for 4 elements: 3.5 cycles each.", [go("c4", 14), s.take("unrolled and scheduled: 14 cycles, 0 stalls, 3.5 per element")])

# ---------------------------------------------------------------- comparison
s.scene("cmp")
s.step("Stage 6: all four versions side by side.", [s.head("Stage 6 of 8: comparing"), s.untake()] + hide("c4") + show("cmp"))
s.step("As written, 9 cycles per element. Scheduled, 7.", [hl("cmp[0..=1]")])
s.step("Unrolled alone, 6.75. Unrolling cuts overhead, but cannot hide stalls by itself.", [hl("cmp[2]")])
s.step("Together, 3.5. Unrolling supplies independent instructions; scheduling puts them in the gaps. The useful work stays 3 per element; the waste falls from 6 to half a cycle.", [hl("cmp[3]"), s.take("unrolling exposes the ILP · scheduling uses it")])

# ---------------------------------------------------------------- costs
s.scene("cost")
s.step("Stage 7: what must the compiler check before it may do all this? Five things.", [s.head("Stage 7 of 8: what the compiler checks"), s.untake()] + hide("cmp") + show("chk"))
s.step("First, that iterations are independent. Each element uses only itself and the constant in F2, so no iteration needs another's result.", [hl("chk[0]")])
s.step("Second, a different set of registers for every copy, to remove the name dependences.", [hl("chk[1]")])
s.step("Third, remove the extra decrements and branches, and fix the loop's exit test and the offsets.", [hl("chk[2]")])
s.step("Fourth, that the loads and stores of different copies touch different addresses, so they may be reordered. Here that is easy: the offsets differ. With pointers it can be very hard.", [hl("chk[3]")])
s.step("And fifth, keep every true dependence in order: each store after its add, each add after its load.", [hl("chk[4]"), s.take("independent iterations · new names · fewer branches · safe memory order")])
s.step("And nothing is free.", [s.head("Stage 7 of 8: the costs"), s.untake()] + hide("chk") + show("cost"))
s.step("Registers: the unrolled loop needs 8 floating-point registers instead of 2. Unroll too far and you run out, which forces spills to memory.", [hl("cost[0]")])
s.step("Code size: 14 instructions instead of 5. Big unrolled loops can cause instruction cache misses.", [hl("cost[1]")])
s.step("Shrinking returns: the overhead is already half a cycle per element. Unrolling eight times would save very little more.", [hl("cost[2]")])
s.step("And if the trip count n is unknown at compile time, the compiler emits two loops: one running n mod k plain iterations, then one running n div k unrolled iterations.", [hl("cost[3]")] + show("strip") + [hl("strip[0]")])
s.step("For 1000 elements unrolled by 3: one plain iteration, then 333 unrolled ones. This is called strip mining.", [s.take("strip mining: n mod k plain, then n div k unrolled")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("cost", "strip") + show("q", "qx"))
s.step("This loop computes x of i plus y of i. Same latencies. Find the cycles as written, after scheduling, and per element when unrolled twice and scheduled. And how many FP registers that needs. Pause and work it out.", [ml("q", 1, 7), hl("qx")])
s.step("a: loads in cycles 1 and 2. The add needs F2, loaded in 2, so it issues in 4. The store waits 2 more: 7. Decrements in 8 and 9, and the branch in 10. 10 cycles.", [go("q", 3), go("q", 4), go("q", 7)])
s.step("b: move the first decrement up to cycle 3, so the add issues in 4, then the second decrement. The store still waits for the add: cycle 7, with offset 8. Branch in 8. 8 cycles.", hide("q", "qx") + show("qa1") + [ml("qa1", 1, 8), go("qa1", 6)])
s.step("c: unrolled twice, four loads, two adds, two decrements, two stores and a branch: 11 instructions in 11 cycles, no stalls. 5.5 cycles per element.", show("qa2") + [ml("qa2", 1, 11)])
s.step("d: F0, F2, F4, F6, F8 and F10. 6 registers. And 10 over 5.5 is a speedup of about 1.82.", hide("qa1", "qa2") + show("qam") + [hl("qam[0]")] + rv("qam", 1) + rv("qam", 2))
s.step("The usual slips: forgetting to fix the store's offset after moving the decrement, and reusing a register across unrolled copies.", [s.take("moved past the decrement? fix the offset")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qam") + show("stages"))
s.step("The latencies decide the stalls. Scheduling fills them, from 9 cycles to 7.", [hl("stages[0..=2]")])
s.step("Unrolling, with renamed registers, shares the overhead and supplies independent work. With scheduling, 3.5 cycles per element, at the cost of registers and code size.", [hl("stages[3..=6]")])
s.step("Next video: static branch prediction.", [mk("stages[0..=7]"), s.take("Next: static branch prediction")])

s.save("/home/claude/playlist/m3/m3v2.json")

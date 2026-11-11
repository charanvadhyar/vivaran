"""Module 1, video 10: arithmetic pipelines: floating point add, subtract, multiply and divide, and their stages."""
import sys
sys.path.insert(0, ".")
from common import Script

r = round
assert r(0.9504 + 0.0820, 4) == 1.0324 and r(0.9504 - 0.0820, 4) == 0.8684 and r(0.5000 - 0.4990, 4) == 0.0010
assert sum([60, 70, 100, 80]) == 310 and max([60, 70, 100, 80]) + 10 == 110
assert r(310 / 110, 2) == 2.82
assert r(0.25 * 0.20, 4) == 0.05 and 130 + 129 - 127 == 132 and 132 - 127 == 5
assert r(0.80 / 0.20, 4) == 4.0 and 133 - 129 + 127 == 131
assert (4 + 99) * 110 == 11330 and 100 * 310 == 31000 and r(31000 / 11330, 2) == 2.74
assert 10 * 25 == 250 and 7 + 9 == 16
assert r(0.0300 + 0.9900, 4) == 1.02

s = Script("Arithmetic pipelines: floating point add, subtract, multiply, divide")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Floating point numbers, and why their arithmetic is pipelined"],
    [2, "Add: four stages, worked through"],
    [3, "Subtract, and the normalizing edge cases"],
    [4, "Timing the adder pipeline"],
    [5, "Multiply: exponents add, mantissas multiply"],
    [6, "Divide: why it is not fully pipelined"],
    [7, "Stages and repeat rates side by side, and an exam question"]]})
s.obj({"id": "fmt", "type": "math", "region": "center", "lines": [
    "x = plus.minus M times 10^E quad \"decimal, for working by hand\"",
    "x = (-1)^S times 1.F times 2^(e - 127) quad \"IEEE 754 single precision\"",
    "\"normalized decimal\": 0.d_1 d_2 d_3 d_4, quad d_1 != 0"]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["why pipeline floating point?"], "rows": [
    ["one operation is several dependent steps"],
    ["scientific loops do thousands of the same operation"],
    ["a pipeline finishes one per cycle once full"]]})
s.obj({"id": "add", "type": "diagram", "region": "left", "layout": "layers", "direction": "down", "nodes": [
    {"id": "s1", "label": "1 compare"}, {"id": "s2", "label": "2 align"},
    {"id": "s3", "label": "3 add"}, {"id": "s4", "label": "4 normalize"}],
    "edges": [{"from": "s1", "to": "s2"}, {"from": "s2", "to": "s3"}, {"from": "s3", "to": "s4"}]})
s.obj({"id": "addx", "type": "table", "region": "right", "columns": ["stage", "X = 0.9504 × 10³ , Y = 0.8200 × 10²"], "rows": [
    ["1", ""], ["2", ""], ["3", ""], ["4", ""]]})
s.obj({"id": "sub", "type": "table", "region": "center", "columns": ["case", "after stage 3", "stage 4 does"], "rows": [
    ["0.9504 × 10³ − 0.8200 × 10²", "0.8684 × 10³", "nothing: already normalized"],
    ["0.9504 × 10³ + 0.8200 × 10²", "1.0324 × 10³", "shift right 1, exponent + 1"],
    ["0.5000 × 10² − 0.4990 × 10²", "0.0010 × 10²", "shift left 2, exponent − 2"],
    ["X + (−Y)", "same hardware", "flip Y's sign, then add"]]})
s.obj({"id": "tm", "type": "table", "region": "center", "columns": ["", "compare", "align", "add", "normalize", "latch"], "rows": [
    ["delay (ns)", "60", "70", "100", "80", "10"]]})
s.obj({"id": "tmm", "type": "math", "region": "center", "lines": [
    "T_\"clock\" = 100 + 10 = 110 \"ns\" quad \"no pipeline\": 60 + 70 + 100 + 80 = 310 \"ns\"",
    "\"speedup limit\" = 310 / 110 approx 2.82"]})
s.obj({"id": "mul", "type": "diagram", "region": "left", "layout": "layers", "direction": "down", "nodes": [
    {"id": "m1", "label": "1 add exponents"}, {"id": "m2", "label": "2 multiply"},
    {"id": "m3", "label": "3 normalize"}, {"id": "m4", "label": "4 round"}],
    "edges": [{"from": "m1", "to": "m2"}, {"from": "m2", "to": "m3"}, {"from": "m3", "to": "m4"}]})
s.obj({"id": "mulx", "type": "math", "region": "right", "lines": [
    "(0.25 times 10^3) times (0.20 times 10^2)",
    "E = 3 + 2 = 5, quad M = 0.25 times 0.20 = 0.05",
    "0.05 times 10^5 = 0.5 times 10^4",
    "\"biased:\" quad e = 130 + 129 - 127 = 132",
    "2^3 times 2^2 = 2^5 quad (132 - 127 = 5)"]})
s.obj({"id": "div", "type": "diagram", "region": "left", "layout": "layers", "direction": "down", "nodes": [
    {"id": "d1", "label": "1 sub exponents"}, {"id": "d2", "label": "2 divide (loop)"},
    {"id": "d3", "label": "3 normalize"}, {"id": "d4", "label": "4 round"}],
    "edges": [{"from": "d1", "to": "d2"}, {"from": "d2", "to": "d3"}, {"from": "d3", "to": "d4"}]})
s.obj({"id": "divx", "type": "math", "region": "right", "lines": [
    "(0.80 times 10^5) / (0.20 times 10^2)",
    "E = 5 - 2 = 3, quad M = 0.80 / 0.20 = 4.0",
    "4.0 times 10^3 = 0.40 times 10^4",
    "\"biased:\" quad e = 133 - 129 + 127 = 131",
    "\"divide by zero\" -> infinity \"or an exception\""]})
s.obj({"id": "dalg", "type": "table", "region": "center", "columns": ["how the mantissas are divided", "how it works", "pipelined?"], "rows": [
    ["restoring / non-restoring", "subtract and shift, one quotient bit per step", "no: reuses one adder"],
    ["SRT", "a table picks 2 or more quotient bits per step", "no: still iterative"],
    ["Newton–Raphson, Goldschmidt", "repeated multiplies converge on 1 ÷ divisor", "uses the multiplier, so blocks it"]]})
s.obj({"id": "lat", "type": "table", "region": "center", "columns": ["unit", "cycles to finish one", "a new one can start every"], "rows": [
    ["integer ALU", "1", "1 cycle"],
    ["FP add / subtract", "4 stages", "1 cycle"],
    ["FP multiply", "7 stages", "1 cycle"],
    ["FP divide", "about 25", "25 cycles: not pipelined"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["Use the adder above (60, 70, 100, 80 ns, latch 10 ns) and the table of units. Find:"], "rows": [
    ["a) 0.3000 × 10² + 0.9900 × 10³, stage by stage"],
    ["b) time for 100 additions, with and without the pipeline"],
    ["c) cycles for 10 independent multiplies, and for 10 divides"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 3 - 2 = 1; quad 0.0300 times 10^3; quad 1.0200 times 10^3; quad 0.1020 times 10^4",
    "\"b)\" quad (4 + 99) times 110 = 11330 \"ns\", quad 100 times 310 = 31000 \"ns\", quad approx 2.74",
    "\"c) multiply:\" quad 7 + 9 = 16 \"cycles\"",
    "\"c) divide:\" quad 10 times 25 = 250 \"cycles\""]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Instruction pipelines overlap instructions. Arithmetic pipelines overlap the steps inside one operation, like a floating point add.", [s.head("Arithmetic pipelines")])
s.step("Here are the seven stages.", [{"action": "show", "target": "stages"}])
s.step("The number format, then the adder: its four stages, subtraction and its edge cases, and its timing.", [{"action": "highlight", "target": "stages[0..=3]"}])
s.step("Then multiply and divide, how many stages each takes, and why division is the odd one out.", [{"action": "highlight", "target": "stages[4..=6]"}])

# ---------------------------------------------------------------- format
s.scene("format")
s.step("Stage 1: a floating point number has a sign, a mantissa and an exponent.", [s.head("Stage 1 of 7: the format"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "fmt"}])
s.step("By hand, we work in decimal: a mantissa times 10 to an exponent.", [{"action": "highlight", "target": "fmt[0]"}])
s.step("The hardware does the same in binary. In IEEE single precision the stored exponent has a bias of 127, which matters for multiply and divide.", [{"action": "reveal", "target": "fmt[1]"}, {"action": "highlight", "target": "fmt[1]"}])
s.step("Normalized means the first mantissa digit is not zero. In our decimal form, 0.9504, not 0.0950.", [{"action": "reveal", "target": "fmt[2]"}, {"action": "highlight", "target": "fmt[2]"}])
s.step("Why pipeline this? Each operation is a chain of dependent steps, and scientific loops repeat the same operation thousands of times.", [{"action": "hide", "target": "fmt"}, {"action": "show", "target": "why"}, {"action": "highlight", "target": "why[0..=1]"}])
s.step("So with one stage per step, a new operation enters every cycle, and one result leaves every cycle.", [{"action": "highlight", "target": "why[2]"}])

# ---------------------------------------------------------------- add
s.scene("add")
s.step("Stage 2: the floating point adder has four stages. Add X equals 0.9504 times 10 cubed, and Y equals 0.8200 times 10 squared.", [s.head("Stage 2 of 7: the adder"), {"action": "hide", "target": "why"}, {"action": "show", "target": "add"}, {"action": "show", "target": "addx"}])
s.step("Stage 1, compare exponents: subtract them. 3 minus 2 is 1, so Y's exponent is smaller by 1.", [{"action": "highlight", "target": "add.s1"}, {"action": "set", "target": "addx[0][1]", "value": "3 − 2 = 1", "delay": 0.4}])
s.step("Stage 2, align: shift the smaller number's mantissa right by that difference. Y becomes 0.0820 times 10 cubed. Now both have the same exponent.", [{"action": "highlight", "target": "add.s2"}, {"action": "set", "target": "addx[1][1]", "value": "Y = 0.0820 × 10³", "delay": 0.4}])
s.step("Stage 3, add the mantissas: 0.9504 plus 0.0820 is 1.0324, times 10 cubed.", [{"action": "highlight", "target": "add.s3"}, {"action": "set", "target": "addx[2][1]", "value": "0.9504 + 0.0820 = 1.0324 × 10³", "delay": 0.4}])
s.step("Stage 4, normalize: 1.0324 has overflowed past the point. Shift it right once and add 1 to the exponent: 0.10324 times 10 to the 4.", [{"action": "highlight", "target": "add.s4"}, {"action": "set", "target": "addx[3][1]", "value": "0.10324 × 10⁴", "delay": 0.4}])
s.step("Edge case: always shift the smaller number, right. Shifting the larger one left would lose its leading digits.", [s.take("compare → align (shift smaller right) → add → normalize")])

# ---------------------------------------------------------------- subtract
s.scene("sub")
s.step("Stage 3: subtraction uses the same four stages. To compute X minus Y, flip Y's sign, and add.", [s.head("Stage 3 of 7: subtract and normalize"), {"action": "hide", "target": "add"}, {"action": "hide", "target": "addx"}, s.untake(), {"action": "show", "target": "sub"}, {"action": "highlight", "target": "sub[3]"}])
s.step("The same X and Y: after aligning, 0.9504 minus 0.0820 is 0.8684 times 10 cubed. It is already normalized, so stage 4 does nothing.", [{"action": "highlight", "target": "sub[0]"}])
s.step("The sum we just did overflowed instead, so stage 4 shifted right by one.", [{"action": "highlight", "target": "sub[1]"}])
s.step("The hard case: subtracting nearly equal numbers. 0.5000 minus 0.4990 is 0.0010. Two leading zeros.", [{"action": "highlight", "target": "sub[2]"}])
s.step("Stage 4 must shift left by two and subtract 2 from the exponent: 0.1000 times 10 to the 0. So the normalizer must shift both ways, and count leading zeros for the left shift.", [{"action": "mark", "target": "sub[2][2]"}])
s.step("Edge case: whether the mantissas are really added or subtracted depends on the signs as well as the operation. Adding a negative number is a subtraction.", [s.take("normalize: overflow → shift right · leading zeros → shift left")])

# ---------------------------------------------------------------- timing
s.scene("timing")
s.step("Stage 4: time the adder. Its stages take 60, 70, 100 and 80 nanoseconds, and each latch takes 10.", [s.head("Stage 4 of 7: timing the adder"), {"action": "hide", "target": "sub"}, s.untake(), {"action": "show", "target": "tm"}])
s.step("As in video 8: the clock is the slowest stage plus the latch, 100 plus 10, which is 110 nanoseconds. Without the pipeline, one add takes the sum: 310.", [{"action": "highlight", "target": "tm[0][3]"}, {"action": "hide", "target": "tm", "delay": 0.6}, {"action": "show", "target": "tmm", "delay": 0.6}])
s.step("So the speedup can approach 310 over 110, about 2.82, not 4, because the add stage is the slow one.", [{"action": "reveal", "target": "tmm[1]"}, {"action": "highlight", "target": "tmm[1]"}])

# ---------------------------------------------------------------- multiply
s.scene("mul")
s.step("Stage 5: multiplication is simpler in one way: no aligning. Exponents add and mantissas multiply.", [s.head("Stage 5 of 7: multiply"), {"action": "hide", "target": "tmm"}, {"action": "show", "target": "mul"}, {"action": "show", "target": "mulx"}])
s.step("Stage 1: add the exponents, and XOR the signs. Here 3 plus 2 is 5.", [{"action": "highlight", "target": "mul.m1"}, {"action": "reveal", "target": "mulx[1]"}])
s.step("Stage 2: multiply the mantissas: 0.25 times 0.20 is 0.05.", [{"action": "highlight", "target": "mul.m2"}, {"action": "highlight", "target": "mulx[1]"}])
s.step("Stage 3: normalize. 0.05 has a leading zero, so shift left and subtract 1: 0.5 times 10 to the 4.", [{"action": "highlight", "target": "mul.m3"}, {"action": "reveal", "target": "mulx[2]"}, {"action": "highlight", "target": "mulx[2]"}])
s.step("Stage 4: round to the available digits. Rounding can carry all the way up, so it may need one more normalizing shift.", [{"action": "highlight", "target": "mul.m4"}])
s.step("Edge case with the bias: each stored exponent already has 127 added. So add them, and subtract 127 once. 130 plus 129 minus 127 is 132, meaning 2 to the 5.", [{"action": "reveal", "target": "mulx[4]"}, {"action": "highlight", "target": "mulx[3]"}, {"action": "highlight", "target": "mulx[4]", "delay": 0.4}])
s.step("The mantissa multiply is the slow step, so it is split up itself: a tree of carry-save adders sums the partial products over several stages. Real FP multipliers have around 4 to 7 stages.", [{"action": "mark", "target": "mul.m2"}, s.take("multiply: add exponents (− bias once), multiply mantissas, normalize, round")])

# ---------------------------------------------------------------- divide
s.scene("div")
s.step("Stage 6: division. Subtract the exponents, divide the mantissas, normalize, and round.", [s.head("Stage 6 of 7: divide"), {"action": "hide", "target": "mul"}, {"action": "hide", "target": "mulx"}, s.untake(), {"action": "show", "target": "div"}, {"action": "show", "target": "divx"}])
s.step("Exponents: 5 minus 2 is 3. Mantissas: 0.80 over 0.20 is 4.0.", [{"action": "highlight", "target": "div.d1"}, {"action": "highlight", "target": "div.d2", "delay": 0.4}, {"action": "reveal", "target": "divx[1]"}, {"action": "highlight", "target": "divx[1]"}])
s.step("4.0 is too big, so normalize by shifting right: 0.40 times 10 to the 4.", [{"action": "highlight", "target": "div.d3"}, {"action": "reveal", "target": "divx[2]"}, {"action": "highlight", "target": "divx[2]"}])
s.step("With the bias, subtracting removes it, so add 127 back once: 133 minus 129 plus 127 is 131. And dividing by zero must give infinity or raise an exception.", [{"action": "reveal", "target": "divx[4]"}, {"action": "highlight", "target": "divx[3]"}, {"action": "highlight", "target": "divx[4]", "delay": 0.4}])
s.step("Now the important part: the mantissa division is iterative. It produces the quotient a few bits at a time, reusing the same hardware.", [{"action": "hide", "target": "div"}, {"action": "hide", "target": "divx"}, {"action": "show", "target": "dalg"}, {"action": "highlight", "target": "dalg[0]"}])
s.step("Restoring and non-restoring division subtract and shift, one bit per step. SRT uses a table to pick two or more bits per step, but it is still a loop.", [{"action": "highlight", "target": "dalg[0..=1]"}])
s.step("Newton–Raphson and Goldschmidt find one over the divisor by repeated multiplication, which doubles the correct bits each time. But they occupy the multiplier.", [{"action": "highlight", "target": "dalg[2]"}])
s.step("Either way, the same hardware is busy until the quotient is done. So a new divide cannot start every cycle: division is not fully pipelined.", [s.take("divide: iterative · a new divide waits for the last one")])

# ---------------------------------------------------------------- compare
s.scene("compare")
s.step("Stage 7: here are typical numbers, from the textbook MIPS floating point pipeline.", [s.head("Stage 7 of 7: side by side"), {"action": "hide", "target": "dalg"}, s.untake(), {"action": "show", "target": "lat"}])
s.step("The integer ALU takes 1 cycle. The FP adder has 4 stages, and a new add can start every cycle.", [{"action": "highlight", "target": "lat[0..=1]"}])
s.step("The multiplier has 7 stages, and is also fully pipelined: one new multiply every cycle.", [{"action": "highlight", "target": "lat[2]"}])
s.step("The divider takes about 25 cycles, and the next divide must wait all 25. Its repeat rate equals its latency.", [{"action": "highlight", "target": "lat[3]"}, {"action": "mark", "target": "lat[3][2]", "delay": 0.4}])
s.step("Keep two numbers apart: cycles to finish one operation, and how often a new one can start. Only a pipelined unit makes the second number 1.", [s.take("latency ≠ repeat rate · only pipelined units start one per cycle")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question, using that adder and that table.", [s.head("Exam question"), {"action": "hide", "target": "lat"}, s.untake(), {"action": "show", "target": "q"}])
s.step("Add 0.3000 times 10 squared and 0.9900 times 10 cubed, stage by stage. Time 100 additions with and without the pipeline. And count the cycles for 10 independent multiplies, and for 10 divides. Pause and work it out.", [{"action": "highlight", "target": "q[0..=2]"}])
s.step("a: the exponents differ by 1. Align: 0.0300 times 10 cubed. Add: 1.0200. Normalize: shift right, 0.1020 times 10 to the 4.", [{"action": "hide", "target": "q"}, {"action": "show", "target": "qa"}, {"action": "highlight", "target": "qa[0]"}])
s.step("b: with the pipeline, 4 plus 99 cycles of 110 nanoseconds, 11330. Without it, 100 times 310, 31000. A speedup of about 2.74.", [{"action": "reveal", "target": "qa[1]"}, {"action": "highlight", "target": "qa[1]"}])
s.step("c: the multiplier is pipelined, so 10 multiplies take 7 plus 9: 16 cycles.", [{"action": "reveal", "target": "qa[2]"}, {"action": "highlight", "target": "qa[2]"}])
s.step("But the divider is not, so 10 divides take 10 times 25: 250 cycles. About 15 times longer, which is why compilers replace divides with multiplies when they can.", [{"action": "reveal", "target": "qa[3]"}, {"action": "highlight", "target": "qa[3]"}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qa"}, {"action": "show", "target": "stages"}])
s.step("Add and subtract: compare exponents, align the smaller, add, normalize either way. The slowest stage plus the latch sets the clock.", [{"action": "highlight", "target": "stages[1..=3]"}])
s.step("Multiply: add exponents, subtract the bias once, multiply mantissas over several stages. Divide: iterative, and not fully pipelined.", [{"action": "highlight", "target": "stages[4..=6]"}])
s.step("That completes Module 1, the fundamentals of computer architecture. Next: Module 2, the memory hierarchy.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Module 1 complete · Next: memory hierarchy")])

s.save("./m1v10.json")

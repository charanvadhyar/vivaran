"""Module 1, video 6: performance metrics: time, the CPU time equation, CPI of a mix, MIPS, means."""
import sys
from math import sqrt
sys.path.insert(0, ".")
from common import Script

# ---- every number in the video, checked
assert round(15 / 10, 2) == 1.5 and round((15 - 10) / 15 * 100) == 33
assert round(2e9 * 1.5 / 2e9, 2) == 1.5
mix = [("ALU", 0.45, 1), ("load", 0.25, 2), ("store", 0.10, 2), ("branch", 0.20, 3)]
assert round(sum(f * c for _, f, c in mix), 2) == 1.75
assert round(2.0 / 2, 3) == 1.0 and round(3.2 / 3, 3) == 1.067
assert 10 * 2e9 * 1.2 / 6 == 4e9
cpis = {"A": 1, "B": 2, "C": 3}
def run(counts):  # counts in millions, 1 GHz
    ic = sum(counts.values()); cyc = sum(cpis[k] * v for k, v in counts.items())
    return ic, cyc, cyc, round(ic / cyc * 1000)   # IC (M), cycles (M), time (ms), MIPS
assert run({"A": 2, "B": 1, "C": 2})[:2] == (5, 10) and run({"A": 4, "B": 1, "C": 1})[:2] == (6, 9)
assert run({"A": 5, "B": 1, "C": 1}) == (7, 10, 10, 700) and run({"A": 10, "B": 1, "C": 1}) == (12, 15, 15, 800)
assert (1 + 1000, 10 + 100) == (1001, 110) and round(1001 / 110, 1) == 9.1
assert round((10 + 0.1) / 2, 2) == 5.05 and sqrt(10 * 0.1) == 1
ex = [("ALU", 0.5, 1), ("load", 0.2, 3), ("store", 0.1, 2), ("branch", 0.2, 2)]
c1 = round(sum(f * c for _, f, c in ex), 2); assert c1 == 1.7
assert round(1e9 * 1.7 / 2.5e9, 2) == 0.68 and round(2500 / 1.7) == 1471
c2 = round(c1 - 0.2 * 1, 2); assert c2 == 1.5 and round(1e9 * 1.5 / 2.5e9, 2) == 0.6
assert round(0.68 / 0.6, 2) == 1.13 and round((0.68 - 0.6) / 0.68 * 100, 1) == 11.8

s = Script("Performance metrics: CPU time, CPI, MIPS and means")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Response time, throughput, and \"n times faster\""],
    [2, "The CPU time equation"],
    [3, "CPI of an instruction mix"],
    [4, "Trap 1: a faster clock can lose"],
    [5, "Trap 2: fewer instructions can lose, and MIPS can lie"],
    [6, "Averaging over several programs"],
    [7, "Exam question"]]})
s.obj({"id": "defs", "type": "table", "region": "center", "columns": ["metric", "meaning", "includes"], "rows": [
    ["response time (elapsed)", "start to finish of one task", "CPU, memory, disk, I/O, other programs"],
    ["CPU time", "time the CPU spends on this task", "user time + system time, no waiting"],
    ["throughput", "tasks finished per unit time", "how much work per hour"]]})
s.obj({"id": "upg", "type": "table", "region": "center", "columns": ["change", "response time", "throughput"], "rows": [
    ["a faster processor", "better", "better"],
    ["more processors, one task each", "same", "better"]]})
s.obj({"id": "fast", "type": "math", "region": "center", "lines": [
    "\"performance\" = 1 / \"execution time\"",
    "X \"is\" n \"times faster than\" Y: quad n = \"time\"_Y / \"time\"_X",
    "A: 10 \"s\", quad B: 15 \"s\" quad => quad n = 15 / 10 = 1.5",
    "\"A is 50% faster,\" quad \"but takes\" (15 - 10) / 15 approx 33% \"less time\""]})
s.obj({"id": "eq", "type": "math", "region": "center", "lines": [
    "\"CPU time\" = \"IC\" times \"CPI\" times T_\"clock\" = (\"IC\" times \"CPI\") / f",
    "\"seconds\"/\"program\" = \"instructions\"/\"program\" times \"cycles\"/\"instruction\" times \"seconds\"/\"cycle\"",
    "f = 2 \"GHz\" quad => quad T_\"clock\" = 1 / (2 times 10^9) = 0.5 \"ns\"",
    "2 times 10^9 times 1.5 times 0.5 \"ns\" = 1.5 \"s\""]})
s.obj({"id": "who", "type": "table", "region": "center", "columns": ["what changes", "IC", "CPI", "clock"], "rows": [
    ["algorithm", "yes", "yes", ""],
    ["language and compiler", "yes", "yes", ""],
    ["instruction set", "yes", "yes", "yes"],
    ["hardware organization", "", "yes", "yes"],
    ["chip technology", "", "", "yes"]]})
s.obj({"id": "mix", "type": "table", "region": "center", "columns": ["class", "frequency", "CPI", "frequency × CPI"], "rows": [
    [n, f"{round(f * 100)}%", str(c), ""] for n, f, c in mix] + [["total", "100%", "", ""]]})
s.obj({"id": "clk", "type": "table", "region": "center", "columns": ["machine", "clock", "CPI", "time per instruction"], "rows": [
    ["A", "2 GHz", "2.0", ""], ["B", "3 GHz", "3.2", ""]]})
s.obj({"id": "need", "type": "math", "region": "center", "lines": [
    "\"now\": 10 \"s\" \"at\" 2 \"GHz\" quad => quad \"cycles\" = 10 times 2 times 10^9 = 20 times 10^9",
    "\"new design\": 1.2 times 20 times 10^9 = 24 times 10^9 \"cycles\"",
    "\"target\" 6 \"s\": quad f = (24 times 10^9) / 6 = 4 \"GHz\""]})
s.obj({"id": "seq", "type": "table", "region": "center", "columns": ["code", "A (CPI 1)", "B (CPI 2)", "C (CPI 3)", "instructions", "cycles", "CPI"], "rows": [
    ["sequence 1", "2", "1", "2", "", "", ""], ["sequence 2", "4", "1", "1", "", "", ""]]})
s.obj({"id": "mips", "type": "table", "region": "center", "columns": ["compiler", "A, B, C (millions)", "IC", "cycles", "time at 1 GHz", "MIPS"], "rows": [
    ["compiler 1", "5, 1, 1", "", "", "", ""], ["compiler 2", "10, 1, 1", "", "", "", ""]]})
s.obj({"id": "mipsf", "type": "math", "region": "bottom", "lines": [
    "\"MIPS\" = \"IC\" / (\"time\" times 10^6) = f / (\"CPI\" times 10^6)"]})
s.obj({"id": "mipsx", "type": "table", "region": "center", "columns": ["why MIPS misleads"], "rows": [
    ["it ignores how many instructions the program needs"],
    ["it cannot compare different instruction sets"],
    ["it changes from program to program on the same machine"]]})
s.obj({"id": "avg", "type": "table", "region": "center", "columns": ["", "time on A", "time on B", "B ÷ A", "A ÷ B"], "rows": [
    ["program 1", "1 s", "10 s", "10", "0.1"],
    ["program 2", "1000 s", "100 s", "0.1", "10"],
    ["total", "1001 s", "110 s", "", ""],
    ["arithmetic mean of ratios", "", "", "", ""],
    ["geometric mean of ratios", "", "", "", ""]]})
s.obj({"id": "q", "type": "table", "region": "left", "columns": ["class", "share", "CPI"], "rows": [
    [n, f"{round(f * 100)}%", str(c)] for n, f, c in ex]})
s.obj({"id": "qtext", "type": "table", "region": "right", "columns": ["2.5 GHz, 10⁹ instructions. Find:"], "rows": [
    ["a) CPI"], ["b) CPU time"], ["c) MIPS"], ["d) loads drop to CPI 2: speedup?"], ["e) % faster, and % less time?"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 0.5 times 1 + 0.2 times 3 + 0.1 times 2 + 0.2 times 2 = 1.7",
    "\"b)\" quad (10^9 times 1.7) / (2.5 times 10^9) = 0.68 \"s\"",
    "\"c)\" quad (2.5 times 10^9) / (1.7 times 10^6) approx 1471",
    "\"d)\" quad \"CPI\" = 1.7 - 0.2 times 1 = 1.5, quad 0.6 \"s\", quad 0.68 / 0.6 approx 1.13",
    "\"e)\" quad 13% \"faster,\" quad (0.68 - 0.6) / 0.68 approx 11.8% \"less time\""]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Which computer is faster? The answer depends on what you measure, and exams love the cases where the obvious answer is wrong.", [s.head("Performance metrics")])
s.step("Here are the seven stages.", [{"action": "show", "target": "stages"}])
s.step("What time means, the CPU time equation, and the CPI of a mix of instructions.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Then the two classic traps: a faster clock that loses, and fewer instructions or more MIPS that lose.", [{"action": "highlight", "target": "stages[3..=4]"}])
s.step("Then how to average over several programs, and one exam question that uses everything.", [{"action": "highlight", "target": "stages[5..=6]"}])

# ---------------------------------------------------------------- time
s.scene("time")
s.step("Stage 1: there are two different things people mean by time.", [s.head("Stage 1 of 7: what we measure"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "defs"}])
s.step("Response time, or elapsed time, is the wall-clock time from start to finish. It includes disk, input and output, and time spent waiting for other programs.", [{"action": "highlight", "target": "defs[0]"}])
s.step("CPU time counts only the time the processor spends on this task: user time plus system time, with no waiting.", [{"action": "highlight", "target": "defs[1]"}])
s.step("Throughput is how many tasks finish per unit time, for example jobs per hour on a server.", [{"action": "highlight", "target": "defs[2]"}])
s.step("The two can move separately. A faster processor improves both response time and throughput.", [{"action": "hide", "target": "defs"}, {"action": "show", "target": "upg"}, {"action": "highlight", "target": "upg[0]"}])
s.step("But adding processors, with one task each, leaves every task just as slow, while more tasks finish per hour: better throughput, same response time.", [{"action": "highlight", "target": "upg[1]"}])
s.step("Now, how do we say one machine is faster? Performance is one over execution time.", [{"action": "hide", "target": "upg"}, {"action": "show", "target": "fast"}, {"action": "highlight", "target": "fast[0]"}])
s.step("X is n times faster than Y when n equals Y's time divided by X's time. The slower machine's time goes on top.", [{"action": "reveal", "target": "fast[1]"}, {"action": "highlight", "target": "fast[1]"}])
s.step("If A takes 10 seconds and B takes 15, A is 15 over 10, that is 1.5 times faster.", [{"action": "reveal", "target": "fast[2]"}, {"action": "highlight", "target": "fast[2]"}])
s.step("Edge case: A is 50 percent faster, but it takes only 33 percent less time. Those are different numbers, so read which one the question asks for.", [{"action": "reveal", "target": "fast[3]"}, {"action": "highlight", "target": "fast[3]"}, s.take("n = time of slower ÷ time of faster · \"% faster\" ≠ \"% less time\"")])

# ---------------------------------------------------------------- equation
s.scene("equation")
s.step("Stage 2: the one equation behind every numerical question.", [s.head("Stage 2 of 7: the CPU time equation"), {"action": "hide", "target": "fast"}, s.untake(), {"action": "show", "target": "eq"}])
s.step("CPU time equals instruction count, times cycles per instruction, times the clock cycle time. Or, divide by the clock rate instead of multiplying by the cycle time.", [{"action": "highlight", "target": "eq[0]"}])
s.step("Check the units: instructions per program, times cycles per instruction, times seconds per cycle, gives seconds per program.", [{"action": "reveal", "target": "eq[1]"}, {"action": "highlight", "target": "eq[1]"}])
s.step("Edge case: questions give the clock rate in gigahertz. A 2 gigahertz clock has a cycle time of one over 2 times 10 to the 9, which is 0.5 nanoseconds.", [{"action": "reveal", "target": "eq[2]"}, {"action": "highlight", "target": "eq[2]"}])
s.step("So 2 billion instructions at CPI 1.5 on that clock take 1.5 seconds.", [{"action": "reveal", "target": "eq[3]"}, {"action": "highlight", "target": "eq[3]"}])
s.step("Which design choices change which factor? The algorithm and the compiler change both the instruction count and the CPI.", [{"action": "hide", "target": "eq"}, {"action": "show", "target": "who"}, {"action": "highlight", "target": "who[0..=1]"}])
s.step("The instruction set can change all three. The hardware organization changes CPI and the clock, and chip technology changes only the clock.", [{"action": "highlight", "target": "who[2..=4]"}])
s.step("No single factor tells you the speed. Only the product of all three does.", [s.take("CPU time = IC × CPI × cycle time = IC × CPI ÷ f")])

# ---------------------------------------------------------------- mix
s.scene("mix")
s.step("Stage 3: real programs mix instructions with different CPIs, so the CPI we use is a weighted average.", [s.head("Stage 3 of 7: CPI of a mix"), {"action": "hide", "target": "who"}, s.untake(), {"action": "show", "target": "mix"}])
s.step("Multiply each class's share by its CPI. ALU: 0.45 times 1 is 0.45.", [{"action": "highlight", "target": "mix[0]"}, {"action": "set", "target": "mix[0][3]", "value": "0.45", "delay": 0.4}])
s.step("Loads: 0.25 times 2 is 0.5. Stores: 0.1 times 2 is 0.2.", [{"action": "highlight", "target": "mix[1..=2]"}, {"action": "set", "target": "mix[1][3]", "value": "0.50", "delay": 0.3}, {"action": "set", "target": "mix[2][3]", "value": "0.20", "delay": 0.6}])
s.step("Branches: 0.2 times 3 is 0.6.", [{"action": "highlight", "target": "mix[3]"}, {"action": "set", "target": "mix[3][3]", "value": "0.60", "delay": 0.4}])
s.step("Add them: the average CPI is 1.75.", [{"action": "highlight", "target": "mix[4]"}, {"action": "set", "target": "mix[4][3]", "value": "CPI = 1.75", "delay": 0.4}])
s.step("Edge case: if the question gives instruction counts instead of percentages, add up the cycles and divide by the total number of instructions. Never just average the CPI column.", [{"action": "highlight", "target": "mix.CPI"}])
s.step("Edge case two: a machine that issues several instructions per cycle can have a CPI below 1. Then we often quote IPC, instructions per cycle, which is one over CPI.", [s.take("CPI = Σ (share × CPI of class) · IPC = 1 ÷ CPI")])

# ---------------------------------------------------------------- clock trap
s.scene("clock")
s.step("Stage 4, the first trap: same program, same instruction set. A runs at 2 gigahertz with CPI 2. B runs at 3 gigahertz with CPI 3.2. Which is faster?", [s.head("Stage 4 of 7: a faster clock can lose"), {"action": "hide", "target": "mix"}, s.untake(), {"action": "show", "target": "clk"}])
s.step("The instruction count is the same, so compare time per instruction: CPI times cycle time.", [{"action": "highlight", "target": "clk[0][3]"}, {"action": "highlight", "target": "clk[1][3]", "delay": 0.3}])
s.step("A: 2 cycles of 0.5 nanoseconds is 1 nanosecond per instruction.", [{"action": "highlight", "target": "clk[0]"}, {"action": "set", "target": "clk[0][3]", "value": "2 × 0.5 ns = 1.0 ns", "delay": 0.4}])
s.step("B: 3.2 cycles of a third of a nanosecond is about 1.067 nanoseconds.", [{"action": "highlight", "target": "clk[1]"}, {"action": "set", "target": "clk[1][3]", "value": "3.2 ÷ 3 ns ≈ 1.067 ns", "delay": 0.4}])
s.step("So A, with the slower clock, is about 1.067 times faster. A higher clock rate alone proves nothing.", [{"action": "mark", "target": "clk[0]"}, s.take("compare IC × CPI ÷ f, never the clock alone")])
s.step("The same equation answers design questions. A program takes 10 seconds on a 2 gigahertz machine, so it needs 20 billion cycles.", [{"action": "hide", "target": "clk"}, s.untake(), {"action": "show", "target": "need"}, {"action": "highlight", "target": "need[0]"}])
s.step("A designer wants 6 seconds, but the faster clock makes the program need 1.2 times as many cycles: 24 billion.", [{"action": "reveal", "target": "need[1]"}, {"action": "highlight", "target": "need[1]"}])
s.step("To finish 24 billion cycles in 6 seconds, the clock must be 4 gigahertz. Twice the clock, for only a 1.67 times speedup.", [{"action": "reveal", "target": "need[2]"}, {"action": "highlight", "target": "need[2]"}])

# ---------------------------------------------------------------- instruction count and MIPS trap
s.scene("count")
s.step("Stage 5, the second trap: fewer instructions does not mean faster. Classes A, B and C take 1, 2 and 3 cycles.", [s.head("Stage 5 of 7: fewer instructions, more MIPS"), {"action": "hide", "target": "need"}, {"action": "show", "target": "seq"}])
s.step("Sequence 1 uses 5 instructions: 2 times 1, plus 1 times 2, plus 2 times 3, is 10 cycles. CPI 2.", [{"action": "highlight", "target": "seq[0]"}, {"action": "set", "target": "seq[0][4]", "value": "5", "delay": 0.3}, {"action": "set", "target": "seq[0][5]", "value": "10", "delay": 0.6}, {"action": "set", "target": "seq[0][6]", "value": "2.0", "delay": 0.9}])
s.step("Sequence 2 uses 6 instructions: 4, plus 2, plus 3, is 9 cycles. CPI 1.5.", [{"action": "highlight", "target": "seq[1]"}, {"action": "set", "target": "seq[1][4]", "value": "6", "delay": 0.3}, {"action": "set", "target": "seq[1][5]", "value": "9", "delay": 0.6}, {"action": "set", "target": "seq[1][6]", "value": "1.5", "delay": 0.9}])
s.step("Sequence 2 has more instructions but fewer cycles, so it is faster. Count cycles, not instructions.", [{"action": "mark", "target": "seq[1][5]"}])
s.step("Now MIPS: millions of instructions per second. It is the instruction count over time times a million, or the clock rate over CPI times a million.", [{"action": "hide", "target": "seq"}, {"action": "show", "target": "mips"}, {"action": "show", "target": "mipsf"}])
s.step("Two compilers, a 1 gigahertz machine. Compiler 1 emits 7 million instructions taking 10 million cycles: 10 milliseconds, and 700 MIPS.", [{"action": "highlight", "target": "mips[0]"}, {"action": "set", "target": "mips[0][2]", "value": "7 M", "delay": 0.2}, {"action": "set", "target": "mips[0][3]", "value": "10 M", "delay": 0.4}, {"action": "set", "target": "mips[0][4]", "value": "10 ms", "delay": 0.6}, {"action": "set", "target": "mips[0][5]", "value": "700", "delay": 0.8}])
s.step("Compiler 2 emits 12 million instructions taking 15 million cycles: 15 milliseconds, and 800 MIPS.", [{"action": "highlight", "target": "mips[1]"}, {"action": "set", "target": "mips[1][2]", "value": "12 M", "delay": 0.2}, {"action": "set", "target": "mips[1][3]", "value": "15 M", "delay": 0.4}, {"action": "set", "target": "mips[1][4]", "value": "15 ms", "delay": 0.6}, {"action": "set", "target": "mips[1][5]", "value": "800", "delay": 0.8}])
s.step("Compiler 2 has the higher MIPS rating, yet its code is slower. It padded the program with many cheap instructions.", [{"action": "mark", "target": "mips[1][5]"}, {"action": "mark", "target": "mips[0][4]", "delay": 0.4}])
s.step("So MIPS misleads in three ways. It ignores instruction count, it cannot compare different instruction sets, and it changes from program to program.", [{"action": "hide", "target": "mips"}, {"action": "hide", "target": "mipsf"}, {"action": "show", "target": "mipsx"}, {"action": "highlight", "target": "mipsx[0..=2]"}])
s.step("The only honest measure is execution time.", [s.take("fewer instructions or higher MIPS can still be slower: compare time")])

# ---------------------------------------------------------------- averaging
s.scene("avg")
s.step("Stage 6: a benchmark suite has many programs. How do we combine their results into one number?", [s.head("Stage 6 of 7: averaging"), {"action": "hide", "target": "mipsx"}, s.untake(), {"action": "show", "target": "avg"}])
s.step("Program 1 takes 1 second on A and 10 on B. Program 2 takes 1000 seconds on A and 100 on B.", [{"action": "highlight", "target": "avg[0..=1]"}])
s.step("If you run both once, total time decides: A needs 1001 seconds, B needs 110. B is about 9.1 times faster.", [{"action": "highlight", "target": "avg[2]"}])
s.step("Now the trap. Normalize B to A, giving ratios 10 and 0.1. Their arithmetic mean is 5.05: B looks 5 times slower.", [{"action": "highlight", "target": "avg[0][3]"}, {"action": "highlight", "target": "avg[1][3]", "delay": 0.3}, {"action": "set", "target": "avg[3][3]", "value": "5.05", "delay": 0.5}])
s.step("Normalize A to B instead, and A gets the same mean of 5.05. Now A looks 5 times slower. The arithmetic mean of ratios depends on which machine you pick as the reference.", [{"action": "highlight", "target": "avg[0][4]"}, {"action": "highlight", "target": "avg[1][4]", "delay": 0.3}, {"action": "set", "target": "avg[3][4]", "value": "5.05", "delay": 0.5}])
s.step("The geometric mean, the square root of 10 times 0.1, is 1 both ways. It gives the same verdict whichever machine is the reference.", [{"action": "highlight", "target": "avg[4]"}, {"action": "set", "target": "avg[4][3]", "value": "1", "delay": 0.3}, {"action": "set", "target": "avg[4][4]", "value": "1", "delay": 0.6}])
s.step("That is why SPEC reports the geometric mean of its ratios. But it does not track total time: when the workload is known, use total time, or a weighted arithmetic mean of times.", [s.take("ratios → geometric mean (SPEC) · known workload → total or weighted time")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question that uses everything.", [s.head("Exam question"), {"action": "hide", "target": "avg"}, s.untake(), {"action": "show", "target": "q"}, {"action": "show", "target": "qtext"}])
s.step("A 2.5 gigahertz processor runs a billion instructions with this mix. Find the CPI, the CPU time, and the MIPS rating.", [{"action": "highlight", "target": "qtext[0..=2]"}])
s.step("Then the loads are improved from CPI 3 to CPI 2. Find the speedup, and say it as a percent faster and as a percent less time.", [{"action": "highlight", "target": "qtext[3..=4]"}])
s.step("Pause, work it out, then check with me.", [{"action": "highlight", "target": "q.CPI"}])
s.step("a: 0.5 times 1, plus 0.2 times 3, plus 0.1 times 2, plus 0.2 times 2, gives a CPI of 1.7.", [{"action": "hide", "target": "q"}, {"action": "hide", "target": "qtext"}, {"action": "show", "target": "qa"}, {"action": "reveal", "target": "qa[0]"}, {"action": "highlight", "target": "qa[0]"}])
s.step("b: a billion times 1.7, over 2.5 times 10 to the 9, is 0.68 seconds.", [{"action": "reveal", "target": "qa[1]"}, {"action": "highlight", "target": "qa[1]"}])
s.step("c: MIPS is the clock rate over CPI times a million: 2500 over 1.7, about 1471.", [{"action": "reveal", "target": "qa[2]"}, {"action": "highlight", "target": "qa[2]"}])
s.step("d: loads are 20 percent of instructions and each saves one cycle, so CPI drops by 0.2, to 1.5. The time becomes 0.6 seconds, a speedup of about 1.13.", [{"action": "reveal", "target": "qa[3]"}, {"action": "highlight", "target": "qa[3]"}])
s.step("e: that is 13 percent faster, but only 11.8 percent less time. Two different answers to two different questions.", [{"action": "reveal", "target": "qa[4]"}, {"action": "highlight", "target": "qa[4]"}])
s.step("The marks are usually lost on units in part b and on the percentages in part e.", [{"action": "highlight", "target": "qa[1]"}, {"action": "highlight", "target": "qa[4]", "delay": 0.4}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qa"}, {"action": "show", "target": "stages"}])
s.step("Time is the measure. n times faster is the slower time over the faster time, and CPU time is instruction count times CPI over clock rate.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Neither the clock, nor the instruction count, nor MIPS alone decides speed. And average ratios with the geometric mean.", [{"action": "highlight", "target": "stages[3..=5]"}])
s.step("Next video: Amdahl's law, which tells you how much any one improvement can ever buy.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Next: Amdahl's law")])

s.save("./m1v6.json")

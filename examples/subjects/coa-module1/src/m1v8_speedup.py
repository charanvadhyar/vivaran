"""Module 1, video 8: real pipeline speedup: unequal stage delays, latch overhead, latency, depth, stalls."""
import sys
sys.path.insert(0, ".")
from common import Script

D = [("IF", 4), ("ID", 3), ("EX", 5), ("MEM", 6), ("WB", 2)]
L = 1
T = sum(d for _, d in D); C = max(d for _, d in D) + L
assert (T, C) == (20, 7)
r = round
assert 100 * T == 2000 and (5 + 99) * C == 728 and r(2000 / 728, 2) == 2.75 and r(T / C, 2) == 2.86
assert r(1000 / C, 1) == 142.9 and 5 * C == 35
assert r(T / (4 + L), 2) == 4
assert (5 + 1 + 99) * 6 == 630 and r(2000 / 630, 2) == 3.17 and r(20 / 6, 2) == 3.33
assert r(20 / (1 + 1), 2) == 10 and 104 * 5 == 520 and r(2000 / 520, 2) == 3.85 and (20 + 99) * 2 == 238 and r(2000 / 238, 2) == 8.40
assert r(T / (1.4 * C), 2) == 2.04
assert r(2.75 / 5 * 100) == 55
E = [80, 120, 100, 60]; EL = 20
ET = sum(E); EC = max(E) + EL
assert (ET, EC) == (360, 140)
assert r(1000 / EC, 2) == 7.14 and 1000 * ET == 360000 and (4 + 999) * EC == 140420
assert r(360000 / 140420, 2) == 2.56 and r(ET / EC, 2) == 2.57 and 4 * EC == 560 and r(ET / (1.25 * EC), 2) == 2.06

s = Script("Pipeline speedup with stage delays and latches")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Without a pipeline: add up the stage delays"],
    [2, "With a pipeline: the slowest stage plus the latch sets the clock"],
    [3, "Speedup for n instructions, and its limit"],
    [4, "Latency gets worse, throughput gets better"],
    [5, "Balancing and deepening the pipeline"],
    [6, "Adding stalls"],
    [7, "Exam question"]]})
s.obj({"id": "dl", "type": "table", "region": "center", "columns": ["stage", "IF", "ID", "EX", "MEM", "WB", "total"], "rows": [
    ["delay (ns)"] + [str(d) for _, d in D] + [""]]})
s.obj({"id": "latch", "type": "diagram", "region": "center", "layout": "layers", "direction": "right", "nodes": [
    {"id": "if", "label": "IF 4"}, {"id": "l1", "label": "latch"}, {"id": "id", "label": "ID 3"}, {"id": "l2", "label": "latch"},
    {"id": "ex", "label": "EX 5"}, {"id": "l3", "label": "latch"}, {"id": "mem", "label": "MEM 6"}, {"id": "l4", "label": "latch"}, {"id": "wb", "label": "WB 2"}],
    "edges": [{"from": a, "to": b} for a, b in [("if", "l1"), ("l1", "id"), ("id", "l2"), ("l2", "ex"), ("ex", "l3"), ("l3", "mem"), ("mem", "l4"), ("l4", "wb")]]})
s.obj({"id": "clk", "type": "math", "region": "bottom", "lines": [
    "T_\"clock\" = max(\"stage delays\") + \"latch delay\" = max(4, 3, 5, 6, 2) + 1 = 7 \"ns\""]})
s.obj({"id": "sp", "type": "math", "region": "center", "lines": [
    "\"without\": n times 20 \"ns\" quad \"with\": (k + n - 1) times 7 \"ns\"",
    "n = 100: quad 100 times 20 = 2000 \"ns\" quad \"vs\" quad 104 times 7 = 728 \"ns\"",
    "\"speedup\" = 2000 / 728 approx 2.75",
    "n -> infinity: quad \"speedup\" -> 20 / 7 approx 2.86 quad \"(not\" k = 5 \")\"",
    "\"efficiency\" = 2.75 / 5 = 55%"]})
s.obj({"id": "lat", "type": "timeline", "region": "center", "lanes": ["one instruction, no pipeline", "one instruction, pipelined"], "end": 35, "unit": "ns", "now": 0, "blocks": []})
s.obj({"id": "latx", "type": "table", "region": "center", "columns": ["", "no pipeline", "pipelined"], "rows": [
    ["latency of one instruction", "20 ns", "5 × 7 = 35 ns"],
    ["throughput", "1 per 20 ns = 50 million/s", "1 per 7 ns ≈ 142.9 million/s"]]})
s.obj({"id": "deep", "type": "table", "region": "center", "columns": ["design", "stages k", "clock", "time for 100", "speedup", "limit"], "rows": [
    ["as given", "5", "6 + 1 = 7 ns", "728 ns", "2.75", "2.86"],
    ["MEM split into 3 + 3", "6", "5 + 1 = 6 ns", "", "", ""],
    ["perfectly balanced, 4 ns each", "5", "4 + 1 = 5 ns", "", "", "4"],
    ["20 stages of 1 ns", "20", "1 + 1 = 2 ns", "", "", "10, not 20"]]})
s.obj({"id": "stl", "type": "math", "region": "center", "lines": [
    "\"speedup\" = (\"time per instruction, no pipeline\") / (\"CPI\"_\"pipe\" times T_\"clock\")",
    "\"CPI\"_\"pipe\" = 1 + \"stall cycles per instruction\"",
    "0.4 \"stalls per instruction\": quad 20 / (1.4 times 7) approx 2.04",
    "\"balanced:\" quad \"speedup\" approx k / (1 + \"stalls per instruction\")"]})
s.obj({"id": "q", "type": "table", "region": "left", "columns": ["stage", "S1", "S2", "S3", "S4"], "rows": [
    ["delay (ps)"] + [str(e) for e in E]]})
s.obj({"id": "qt", "type": "table", "region": "right", "columns": ["latch 20 ps, 1000 instructions. Find:"], "rows": [
    ["a) clock period and frequency"], ["b) time with and without the pipeline, speedup"], ["c) the limit of the speedup"],
    ["d) latency of one instruction"], ["e) speedup limit with 0.25 stalls per instruction"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 120 + 20 = 140 \"ps\", quad f = 1 / (140 \"ps\") approx 7.14 \"GHz\"",
    "\"b)\" quad 1000 times 360 = 360000 \"ps\", quad (4 + 999) times 140 = 140420 \"ps\", quad approx 2.56",
    "\"c)\" quad 360 / 140 approx 2.57",
    "\"d)\" quad 4 times 140 = 560 \"ps\" quad \"(vs 360 ps without)\"",
    "\"e)\" quad 360 / (1.25 times 140) approx 2.06"]})


def blk(t, id, lane, a, b, label, delay=0):
    return {"action": "add_block", "target": t, "id": id, "lane": lane, "start": a, "end": b, "label": label, **({"delay": delay} if delay else {})}


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Video 3 assumed every stage takes exactly one equal cycle, with nothing in between. Real stages take different times, and each one ends in a latch. Now we count that properly.", [s.head("Pipeline speedup, for real")])
s.step("Here are the seven stages.", [{"action": "show", "target": "stages"}])
s.step("The time without a pipeline, the clock with one, and the speedup that follows.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Then why one instruction gets slower while the program gets faster, how splitting stages helps, and what stalls do.", [{"action": "highlight", "target": "stages[3..=5]"}])
s.step("And an exam question with every part they ask.", [{"action": "highlight", "target": "stages[6]"}])

# ---------------------------------------------------------------- unpipelined
s.scene("nopipe")
s.step("Stage 1: here are the delays of the five stages: 4, 3, 5, 6 and 2 nanoseconds.", [s.head("Stage 1 of 7: no pipeline"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "dl"}])
s.step("Without a pipeline, one instruction passes through all five pieces of logic before the next one starts. So it takes the sum: 20 nanoseconds.", [{"action": "highlight", "target": "dl[0]"}, {"action": "set", "target": "dl[0][6]", "value": "20", "delay": 0.5}])
s.step("There are no latches between the stages, so nothing is added. And n instructions take n times 20 nanoseconds.", [s.take("no pipeline: time per instruction = sum of stage delays")])

# ---------------------------------------------------------------- clock
s.scene("clock")
s.step("Stage 2: a pipeline puts a latch, a pipeline register, after each stage, to hold that stage's result for the next one.", [s.head("Stage 2 of 7: the pipeline clock"), {"action": "hide", "target": "dl"}, s.untake(), {"action": "show", "target": "latch"}])
s.step("Every stage moves forward on the same clock edge. So the clock must wait for the slowest stage: MEM, at 6 nanoseconds.", [{"action": "mark", "target": "latch.mem"}])
s.step("And the latch itself takes time to capture the value: here, 1 nanosecond.", [{"action": "highlight", "target": "latch.l1"}, {"action": "highlight", "target": "latch.l2", "delay": 0.2}, {"action": "highlight", "target": "latch.l3", "delay": 0.4}, {"action": "highlight", "target": "latch.l4", "delay": 0.6}])
s.step("So the clock period is the largest stage delay plus the latch delay: 6 plus 1, which is 7 nanoseconds.", [{"action": "show", "target": "clk"}])
s.step("Edge case: the faster stages just finish early and wait. WB is done after 2 nanoseconds and idles for 5.", [{"action": "highlight", "target": "latch.wb"}])
s.step("Edge case two: use the maximum, never the average. The average stage is 4 nanoseconds, but the clock cannot tick faster than its slowest stage.", [{"action": "mark", "target": "latch.mem"}])

# ---------------------------------------------------------------- speedup
s.scene("speedup")
s.step("Stage 3: without the pipeline, n instructions take n times 20 nanoseconds. With it, the first instruction needs k cycles, and each later one one more cycle: k plus n minus 1 cycles of 7 nanoseconds.", [s.head("Stage 3 of 7: speedup"), {"action": "hide", "target": "latch"}, {"action": "hide", "target": "clk"}, {"action": "show", "target": "sp"}])
s.step("For 100 instructions: 2000 nanoseconds without, against 104 cycles of 7, which is 728 nanoseconds.", [{"action": "reveal", "target": "sp[1]"}, {"action": "highlight", "target": "sp[1]"}])
s.step("The speedup is 2000 over 728, about 2.75.", [{"action": "reveal", "target": "sp[2]"}, {"action": "highlight", "target": "sp[2]"}])
s.step("For a very long program, the k minus 1 fill cycles stop mattering. The speedup approaches 20 over 7, about 2.86: the unpipelined time over the clock period.", [{"action": "reveal", "target": "sp[3]"}, {"action": "highlight", "target": "sp[3]"}])
s.step("Not 5, the number of stages. Two things cost us: unequal stages, and the latch overhead.", [{"action": "mark", "target": "sp[3]"}])
s.step("Efficiency is speedup over the number of stages: 2.75 over 5, which is 55 percent.", [{"action": "reveal", "target": "sp[4]"}, {"action": "highlight", "target": "sp[4]"}, s.take("limit = (sum of delays) ÷ (max delay + latch), not k")])

# ---------------------------------------------------------------- latency
s.scene("latency")
s.step("Stage 4: follow one instruction by itself. Without a pipeline it is done in 20 nanoseconds.", [s.head("Stage 4 of 7: latency and throughput"), {"action": "hide", "target": "sp"}, s.untake(), {"action": "show", "target": "lat"}] +
       [blk("lat", f"u{i}", "one instruction, no pipeline", sum(d for _, d in D[:i]), sum(d for _, d in D[:i + 1]), f"{n} {d}", round(i * 0.15, 2)) for i, (n, d) in enumerate(D)])
s.step("In the pipeline, every stage takes a full 7 nanosecond cycle, so it needs 5 times 7, which is 35 nanoseconds.", [blk("lat", f"p{i}", "one instruction, pipelined", i * 7, i * 7 + 7, n, round(i * 0.15, 2)) for i, (n, _) in enumerate(D)])
s.step("So pipelining makes each instruction slower: its latency grows from 20 to 35 nanoseconds.", [{"action": "hide", "target": "lat"}, {"action": "show", "target": "latx"}, {"action": "highlight", "target": "latx[0]"}])
s.step("But a new instruction finishes every 7 nanoseconds instead of every 20. Throughput rises from 50 to about 143 million instructions per second.", [{"action": "highlight", "target": "latx[1]"}])
s.step("Pipelining improves throughput, never the latency of one instruction.", [s.take("latency ↑ (20 → 35 ns) · throughput ↑ (1 per 20 ns → 1 per 7 ns)")])

# ---------------------------------------------------------------- balance and depth
s.scene("deep")
s.step("Stage 5: how do we get closer to the ideal? The slow MEM stage sets the clock, so split it into two stages of 3 nanoseconds.", [s.head("Stage 5 of 7: balance and depth"), {"action": "hide", "target": "latx"}, s.untake(), {"action": "show", "target": "deep"}, {"action": "highlight", "target": "deep[0]"}])
s.step("Now the slowest stage is EX at 5, so the clock is 6 nanoseconds, with 6 stages. 100 instructions take 105 cycles of 6: 630 nanoseconds. Speedup about 3.17, with a limit of 20 over 6, about 3.33.", [{"action": "highlight", "target": "deep[1]"},
       {"action": "set", "target": "deep[1][3]", "value": "105 × 6 = 630 ns", "delay": 0.3}, {"action": "set", "target": "deep[1][4]", "value": "3.17", "delay": 0.6}, {"action": "set", "target": "deep[1][5]", "value": "3.33", "delay": 0.8}])
s.step("If the same 20 nanoseconds of logic were perfectly balanced, 4 each, the clock would be 5 and the limit exactly 4. Balance matters as much as depth. 100 instructions would take 520 nanoseconds, a speedup of about 3.85.", [{"action": "highlight", "target": "deep[2]"}, {"action": "set", "target": "deep[2][3]", "value": "104 × 5 = 520 ns", "delay": 0.5}, {"action": "set", "target": "deep[2][4]", "value": "3.85", "delay": 0.7}])
s.step("Go to extremes: 20 stages of 1 nanosecond. The latch adds 1 to every stage, so the clock is 2, and the limit is 10, not 20. 100 instructions take 119 cycles of 2: 238 nanoseconds, a speedup of 8.4.", [{"action": "highlight", "target": "deep[3]"}, {"action": "set", "target": "deep[3][3]", "value": "119 × 2 = 238 ns", "delay": 0.5}, {"action": "set", "target": "deep[3][4]", "value": "8.40", "delay": 0.7}])
s.step("The deeper the pipeline, the larger the share of each cycle spent in the latch. Deeper pipelines also mean more hazards and longer branch penalties. So depth gives diminishing returns.", [{"action": "mark", "target": "deep[3][5]"}, s.take("latch overhead caps the gain from more stages")])

# ---------------------------------------------------------------- stalls
s.scene("stalls")
s.step("Stage 6: real pipelines also stall. A stall adds cycles, so the pipeline's CPI rises above 1.", [s.head("Stage 6 of 7: stalls"), {"action": "hide", "target": "deep"}, s.untake(), {"action": "show", "target": "stl"}])
s.step("The pipeline CPI is 1 plus the stall cycles per instruction.", [{"action": "reveal", "target": "stl[1]"}, {"action": "highlight", "target": "stl[1]"}])
s.step("With 0.4 stall cycles per instruction, the limit falls from 2.86 to 20 over 1.4 times 7, about 2.04.", [{"action": "reveal", "target": "stl[2]"}, {"action": "highlight", "target": "stl[2]"}])
s.step("For balanced stages with no latch overhead, this reduces to the textbook form: speedup is the pipeline depth over one plus the stalls per instruction.", [{"action": "reveal", "target": "stl[3]"}, {"action": "highlight", "target": "stl[3]"}, s.take("speedup = unpipelined time ÷ (CPI_pipe × clock)")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question. A four stage pipeline has stage delays of 80, 120, 100 and 60 picoseconds, and a 20 picosecond latch.", [s.head("Exam question"), {"action": "hide", "target": "stl"}, s.untake(), {"action": "show", "target": "q"}, {"action": "show", "target": "qt"}])
s.step("For a thousand instructions, find the clock, the times with and without the pipeline, the speedup and its limit, the latency, and the limit with 0.25 stalls per instruction. Pause and work it out.", [{"action": "highlight", "target": "qt[0..=4]"}])
s.step("a: the slowest stage plus the latch: 120 plus 20, so 140 picoseconds, about 7.14 gigahertz.", [{"action": "hide", "target": "q"}, {"action": "hide", "target": "qt"}, {"action": "show", "target": "qa"}, {"action": "highlight", "target": "qa[0]"}])
s.step("b: without the pipeline, each instruction takes the sum, 360 picoseconds, so 360 thousand in all. With it, 4 plus 999 cycles of 140: 140420 picoseconds. The speedup is about 2.56.", [{"action": "reveal", "target": "qa[1]"}, {"action": "highlight", "target": "qa[1]"}])
s.step("c: the limit is 360 over 140, about 2.57. A thousand instructions is already very close to it.", [{"action": "reveal", "target": "qa[2]"}, {"action": "highlight", "target": "qa[2]"}])
s.step("d: one instruction takes 4 cycles of 140: 560 picoseconds, longer than 360 without the pipeline.", [{"action": "reveal", "target": "qa[3]"}, {"action": "highlight", "target": "qa[3]"}])
s.step("e: with stalls, CPI is 1.25, so the limit is 360 over 1.25 times 140, about 2.06.", [{"action": "reveal", "target": "qa[4]"}, {"action": "highlight", "target": "qa[4]"}])
s.step("The usual mistakes: adding latches to the unpipelined time, using the average stage delay, and forgetting the k minus 1 fill cycles.", [s.take("max + latch · sum for no pipeline · k + n − 1 cycles")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qa"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("No pipeline: add the stage delays. Pipeline: the slowest stage plus the latch sets the clock, and n instructions take k plus n minus 1 cycles.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Latency grows while throughput rises. Balancing helps, depth hits the latch overhead, and stalls raise the CPI.", [{"action": "highlight", "target": "stages[3..=5]"}])
s.step("Next video: going beyond one instruction per cycle, with superscalar, superpipelined and VLIW processors.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Next: superscalar, superpipelined and VLIW")])

s.save("./m1v8.json")

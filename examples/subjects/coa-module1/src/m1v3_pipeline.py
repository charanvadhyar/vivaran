"""Module 1, video 3: the instruction pipeline (IF, ID, EX, MEM, WB) and the space-time diagram."""
import sys
sys.path.insert(0, ".")
from common import Script

ST = ["IF", "ID", "EX", "MEM", "WB"]
K, N = 5, 5
assert K + N - 1 == 9 and K * N == 25
assert 5 + 100 - 1 == 104 and round(500 / 104, 2) == 4.81
assert 6 + 20 - 1 == 25 and 6 * 20 == 120 and 120 / 25 == 4.8

s = Script("The instruction pipeline: IF, ID, EX, MEM, WB")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The five steps every instruction goes through"],
    [2, "What each kind of instruction does in each step"],
    [3, "Without a pipeline: one instruction at a time"],
    [4, "With a pipeline: the space-time diagram, cycle by cycle"],
    [5, "Counting cycles: k plus n minus 1"],
    [6, "Latency versus throughput"]]})
s.obj({"id": "five", "type": "table", "region": "center", "columns": ["stage", "name", "what happens"], "rows": [
    ["IF", "instruction fetch", "read the instruction at the PC from memory; PC = PC + 4"],
    ["ID", "instruction decode", "work out the operation; read the source registers"],
    ["EX", "execute", "the ALU computes: a result, an address, or a branch condition"],
    ["MEM", "memory access", "loads read memory, stores write it"],
    ["WB", "write back", "write the result into the destination register"]]})
s.obj({"id": "kinds", "type": "table", "region": "center", "columns": ["instruction", "IF", "ID", "EX", "MEM", "WB"], "rows": [
    ["LW R1, 8(R2)", "fetch", "read R2", "8 + R2", "read memory", "write R1"],
    ["ADD R3, R4, R5", "fetch", "read R4, R5", "R4 + R5", "nothing", "write R3"],
    ["SW R6, 4(R7)", "fetch", "read R6, R7", "4 + R7", "write memory", "nothing"],
    ["BEQ R1, R2, L", "fetch", "read R1, R2", "compare, target", "nothing", "nothing"]]})
s.obj({"id": "seq", "type": "timeline", "region": "center", "lanes": ["I1", "I2", "I3", "I4", "I5"], "end": 25, "unit": "clock cycle", "now": 0, "blocks": []})
s.obj({"id": "pipe", "type": "timeline", "region": "center", "lanes": ["I1", "I2", "I3", "I4", "I5"], "end": 9, "unit": "clock cycle", "now": 0, "blocks": []})
s.obj({"id": "count", "type": "math", "region": "center", "lines": [
    "\"without a pipeline\": k times n = 5 times 5 = 25 \"cycles\"",
    "\"with a pipeline\": k + (n - 1) = 5 + 4 = 9 \"cycles\"",
    "n = 100: quad 5 times 100 = 500 quad \"vs\" quad 5 + 99 = 104",
    "\"speedup\" = 500 / 104 approx 4.81 quad -> 5 = k \"as\" n -> infinity"]})
s.obj({"id": "lat", "type": "table", "region": "center", "columns": ["", "without pipeline", "with pipeline"], "rows": [
    ["latency: cycles for one instruction", "5", "5"],
    ["throughput: instructions finished per cycle", "1 every 5 cycles", "1 every cycle, once full"],
    ["cycles for 100 instructions", "500", "104"]]})
s.obj({"id": "q", "type": "math", "region": "center", "lines": [
    "k = 6 \"stages\", quad n = 20 \"instructions\"",
    "\"without\": 6 times 20 = 120 \"cycles\"",
    "\"with\": 6 + (20 - 1) = 25 \"cycles\"",
    "\"speedup\" = 120 / 25 = 4.8"]})

s.obj({"id": "rd", "type": "math", "region": "center", "lines": [
    "\"instruction\" i \"enters IF in cycle\" i",
    "\"instruction\" i \"finishes WB in cycle\" i + k - 1",
    "\"in cycle\" c, \"instruction\" i \"is in stage number\" c - i + 1",
    "\"I3 in cycle 5\": 5 - 3 + 1 = 3 quad \"(EX)\"",
    "\"I100 finishes in cycle\" 100 + 5 - 1 = 104"]})
s.obj({"id": "q2", "type": "math", "region": "center", "lines": [
    "\"I15 finishes in cycle\" 15 + 6 - 1 = 20",
    "\"in cycle 10, I7 is in stage\" 10 - 7 + 1 = 4"]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("A laundry has a washer, a dryer and a folding table. You do not wait for one load to be folded before washing the next.", [s.head("The instruction pipeline")])
s.step("A processor can do the same with instructions: start the next one before the last one has finished. That is pipelining.", [s.take("pipelining: overlap the steps of different instructions")])
s.step("Here are the six stages of this video.", [s.untake(), {"action": "show", "target": "stages"}])
s.step("The five steps, and what each kind of instruction does in them.", [{"action": "highlight", "target": "stages[0..=1]"}])
s.step("Then the same five instructions without and with a pipeline, drawn cycle by cycle.", [{"action": "highlight", "target": "stages[2..=3]"}])
s.step("And the formula for counting cycles, with the difference between latency and throughput.", [{"action": "highlight", "target": "stages[4..=5]"}])

# ---------------------------------------------------------------- five steps
s.scene("five")
s.step("Stage 1: the classic five-stage pipeline splits every instruction into five steps.", [s.head("Stage 1 of 6: the five steps"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "five"}])
s.step("IF, instruction fetch: read the instruction the program counter points to, and add 4 to the PC.", [{"action": "highlight", "target": "five[0]"}])
s.step("ID, instruction decode: work out what the instruction is, and read its source registers.", [{"action": "highlight", "target": "five[1]"}])
s.step("EX, execute: the ALU does the arithmetic, works out a memory address, or tests a branch.", [{"action": "highlight", "target": "five[2]"}])
s.step("MEM, memory access: a load reads data memory, and a store writes it.", [{"action": "highlight", "target": "five[3]"}])
s.step("WB, write back: the result goes into the destination register.", [{"action": "highlight", "target": "five[4]"}])
s.step("Each step takes one clock cycle, and each has its own hardware, so five instructions can be in five different steps at once.", [s.take("one step per cycle · each step has its own hardware")])

# ---------------------------------------------------------------- per kind
s.scene("kinds")
s.step("Stage 2: not every instruction needs every step. Here are four kinds.", [s.head("Stage 2 of 6: who uses which step"), {"action": "hide", "target": "five"}, s.untake(), {"action": "show", "target": "kinds"}])
s.step("A load uses all five: fetch, read R2, add 8 to it for the address, read memory, and write R1.", [{"action": "highlight", "target": "kinds[0]"}])
s.step("An add does its work in EX, and has nothing to do in MEM.", [{"action": "highlight", "target": "kinds[1]"}, {"action": "highlight", "target": "kinds[1][4]", "delay": 0.5}])
s.step("A store writes memory in MEM, and has no register to write back.", [{"action": "highlight", "target": "kinds[2]"}, {"action": "highlight", "target": "kinds[2][5]", "delay": 0.5}])
s.step("A branch compares its registers and works out the target address in EX.", [{"action": "highlight", "target": "kinds[3]"}, {"action": "highlight", "target": "kinds[3][3]", "delay": 0.5}])
s.step("Even so, every instruction passes through all five stages, so each one always takes five cycles. That keeps the pipeline regular.", [s.take("every instruction passes all 5 stages, even when a stage has nothing to do")])

# ---------------------------------------------------------------- sequential
s.scene("sequential")
s.step("Stage 3: five instructions, I1 to I5, without a pipeline.", [s.head("Stage 3 of 6: without a pipeline"), {"action": "hide", "target": "kinds"}, s.untake(), {"action": "show", "target": "seq"}])
for i in range(N):
    blocks = [{"action": "add_block", "target": "seq", "id": f"s{i}{j}", "lane": f"I{i + 1}", "start": i * K + j, "end": i * K + j + 1, "label": ST[j], "delay": round(j * 0.15, 2)} for j in range(K)]
    say = ("I1 goes through IF, ID, EX, MEM and WB: five cycles, and nothing else happens meanwhile." if i == 0 else
           "Only then does I2 start its fetch, in cycle 6." if i == 1 else
           f"I{i + 1} starts in cycle {i * K + 1}." if i < N - 1 else
           "And I5 finishes at the end of cycle 25.")
    s.step(say, blocks + [{"action": "advance", "target": "seq", "to": (i + 1) * K}])
s.step("Five instructions times five cycles is 25 cycles. Most of the hardware sits idle most of the time.", [s.take("5 instructions × 5 cycles = 25 cycles")])

# ---------------------------------------------------------------- pipelined
s.scene("pipelined")
s.step("Stage 4: the same five instructions, pipelined. This picture is the space-time diagram.", [s.head("Stage 4 of 6: the space-time diagram"), {"action": "hide", "target": "seq"}, s.untake(), {"action": "show", "target": "pipe"}])
s.step("Time runs left to right in clock cycles; each row is one instruction.", [])
for c in range(K + N - 1):
    acts = []
    busy = []
    for i in range(N):
        j = c - i
        if 0 <= j < K:
            acts.append({"action": "add_block", "target": "pipe", "id": f"p{i}{j}", "lane": f"I{i + 1}", "start": c, "end": c + 1, "label": ST[j]})
            busy.append(f"I{i + 1} in {ST[j]}")
    acts.append({"action": "advance", "target": "pipe", "to": c + 1})
    if c == 0:
        say = "Cycle 1: I1 is fetched."
    elif c == 1:
        say = "Cycle 2: I1 moves to decode, and I2 is fetched in the same cycle."
    elif c == 4:
        say = "Cycle 5: the pipeline is full. All five stages are busy, one instruction in each, and I1 writes back."
    elif c == 3:
        say = "Cycle 4: " + ", ".join(busy[:-1]) + ", and " + busy[-1] + "."
    elif c == 8:
        say = "Cycle 9: I5 writes back, and all five instructions are done."
    else:
        say = f"Cycle {c + 1}: " + ", ".join(busy[:-1]) + (", and " if len(busy) > 1 else "") + busy[-1] + "."
        if c == 5:
            say = "Cycle 6: I1 has left. I2 writes back, and one instruction now finishes every cycle."
        if c == 7:
            say = "Cycle 8: only I4 and I5 are left; the pipeline is draining."
    s.step(say, acts)
s.step("Read any column to see which instruction is in which stage. Read any row to see one instruction's five steps.", [])
s.step("Nine cycles instead of 25.", [s.take("pipelined: 9 cycles · not pipelined: 25 cycles")])

# ---------------------------------------------------------------- count
s.scene("count")
s.step("Stage 5: where does 9 come from? Let k be the number of stages and n the number of instructions.", [s.head("Stage 5 of 6: counting cycles"), {"action": "hide", "target": "pipe"}, s.untake(), {"action": "show", "target": "count"}])
s.step("Without a pipeline, each of the n instructions takes k cycles, so k times n: 5 times 5 is 25.", [{"action": "highlight", "target": "count[0]"}])
s.step("With a pipeline, the first instruction takes k cycles to come out.", [{"action": "reveal", "target": "count[1]"}, {"action": "highlight", "target": "count[1]"}])
s.step("After that, each of the other n minus 1 instructions finishes one cycle later. So k plus n minus 1: 5 plus 4 is 9.", [{"action": "highlight", "target": "count[1]"}])
s.step("Now take 100 instructions: 5 times 100 is 500 cycles without, and 5 plus 99 is 104 with the pipeline.", [{"action": "reveal", "target": "count[2]"}, {"action": "highlight", "target": "count[2]"}])
s.step("The speedup is 500 divided by 104, about 4.81.", [{"action": "reveal", "target": "count[3]"}, {"action": "highlight", "target": "count[3]"}])
s.step("As n grows, the k minus 1 cycles to fill the pipeline matter less, and the speedup approaches k, here 5.", [s.take("cycles = k + (n − 1) · speedup → k for large n")])
s.step("This ideal assumes every stage takes the same time and nothing ever has to wait. Real pipelines fall short; we see why in the next videos.", [])

# ---------------------------------------------------------------- latency
s.scene("latency")
s.step("Stage 6: a pipeline does not make any one instruction faster.", [s.head("Stage 6 of 6: latency and throughput"), {"action": "hide", "target": "count"}, s.untake(), {"action": "show", "target": "lat"}])
s.step("Latency, the time for one instruction from fetch to write back, is still 5 cycles.", [{"action": "highlight", "target": "lat[0]"}])
s.step("What improves is throughput: once full, the pipeline finishes one instruction every cycle instead of every five.", [{"action": "highlight", "target": "lat[1]"}])
s.step("That is why 100 instructions take 104 cycles instead of 500.", [{"action": "highlight", "target": "lat[2]"}])
s.step("Say it this way in the exam: pipelining increases throughput, not the speed of a single instruction.", [s.take("pipelining raises throughput · latency stays the same")])

# ---------------------------------------------------------------- reading the diagram
s.scene("reading")
s.step("Before the exam question, three rules for reading any space-time diagram without drawing it.", [s.head("Reading the diagram without drawing it"), {"action": "hide", "target": "lat"}, s.untake(), {"action": "show", "target": "rd"}])
s.step("Instruction i enters IF in cycle i: I1 in cycle 1, I2 in cycle 2, and so on.", [{"action": "highlight", "target": "rd[0]"}])
s.step("It spends k cycles in the pipeline, so it finishes write back in cycle i plus k minus 1.", [{"action": "reveal", "target": "rd[1]"}, {"action": "highlight", "target": "rd[1]"}])
s.step("And in cycle c, instruction i is in stage number c minus i plus 1.", [{"action": "reveal", "target": "rd[2]"}, {"action": "highlight", "target": "rd[2]"}])
s.step("Check with our diagram: I3 in cycle 5 is in stage 5 minus 3 plus 1, the third stage, EX. That matches.", [{"action": "reveal", "target": "rd[3]"}, {"action": "highlight", "target": "rd[3]"}])
s.step("And I100 finishes in cycle 100 plus 5 minus 1, which is 104, the same total we found before.", [{"action": "reveal", "target": "rd[4]"}, {"action": "highlight", "target": "rd[4]"}])
s.step("If the answer for the stage number is below 1, the instruction has not entered yet; above k, it has already left.", [s.take("stage number below 1: not entered yet · above k: already finished")])
s.step("One more note: textbooks differ on k. Some use four stages, some six or more. The rules stay the same; only k changes.", [])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), {"action": "hide", "target": "rd"}, s.untake(), {"action": "show", "target": "q"}])
s.step("A 6-stage pipeline runs 20 instructions. How many cycles with and without the pipeline, and what is the speedup? Pause and try it.", [{"action": "highlight", "target": "q[0]"}])
s.step("Without: k times n, 6 times 20, is 120 cycles.", [{"action": "reveal", "target": "q[1]"}, {"action": "highlight", "target": "q[1]"}])
s.step("With: k plus n minus 1, 6 plus 19, is 25 cycles.", [{"action": "reveal", "target": "q[2]"}, {"action": "highlight", "target": "q[2]"}])
s.step("Speedup: 120 divided by 25 is 4.8, a little below the ideal of 6.", [{"action": "reveal", "target": "q[3]"}, {"action": "highlight", "target": "q[3]"}])
s.step("Two more parts, on the same pipeline: in which cycle does I15 finish, and which stage is I7 in during cycle 10?", [{"action": "hide", "target": "q"}, {"action": "show", "target": "q2"}])
s.step("I15 finishes in cycle 15 plus 6 minus 1, which is 20.", [{"action": "highlight", "target": "q2[0]"}])
s.step("In cycle 10, I7 is in stage 10 minus 7 plus 1, which is stage 4 of the 6.", [{"action": "reveal", "target": "q2[1]"}, {"action": "highlight", "target": "q2[1]"}])
s.step("The usual slip is writing k times n for the pipelined case too, or forgetting the minus 1.", [s.take("pipelined cycles = k + n − 1, not k × n")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "q2"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("Five steps: fetch, decode, execute, memory, write back, one cycle each.", [{"action": "highlight", "target": "stages[0..=1]"}])
s.step("Without a pipeline, five instructions took 25 cycles; with one, 9.", [{"action": "highlight", "target": "stages[2..=3]"}])
s.step("Cycles are k plus n minus 1; speedup approaches k; latency stays the same, throughput goes up.", [{"action": "highlight", "target": "stages[4..=5]"}])
s.step("Next video: hazards, the reasons a pipeline sometimes has to wait.", [{"action": "mark", "target": "stages[0..=5]"}, s.take("Next: pipeline hazards — finding them")])

s.save(sys.argv[1])

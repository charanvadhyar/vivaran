"""Module 1, video 2: Flynn's taxonomy."""
import sys
sys.path.insert(0, ".")
from common import Script

s = Script("Flynn's taxonomy: SISD, SIMD, MISD, MIMD")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The idea: count instruction streams and data streams"],
    [2, "SISD: one instruction stream, one data stream"],
    [3, "SIMD: one instruction stream, many data streams"],
    [4, "MISD: many instruction streams, one data stream"],
    [5, "MIMD, and how it is programmed: SPMD"],
    [6, "The trap: superscalar is still SISD"],
    [7, "Classify real machines"]]})
s.obj({"id": "grid", "type": "table", "region": "center", "columns": ["", "single data stream", "multiple data streams"], "rows": [
    ["single instruction stream", "SISD", "SIMD"],
    ["multiple instruction streams", "MISD", "MIMD"]]})
s.obj({"id": "defs", "type": "table", "region": "bottom", "columns": ["term", "meaning"], "rows": [
    ["instruction stream", "a sequence of instructions from one program counter"],
    ["data stream", "the sequence of data those instructions work on"]]})

def flow(id, nodes, edges, direction="right"):
    return {"id": id, "type": "diagram", "region": "left", "layout": "layers", "direction": direction,
            "nodes": nodes, "edges": edges}

s.obj(flow("sisd", [{"id": "cu", "label": "control unit"}, {"id": "pe", "label": "processing unit"}, {"id": "m", "label": "memory"}],
           [{"from": "cu", "to": "pe", "label": "instructions"}, {"from": "m", "to": "pe", "label": "data"}]))
s.obj({"id": "sisdx", "type": "table", "region": "right", "columns": ["SISD"], "rows": [
    ["one program counter"], ["one instruction at a time, in program order"], ["e.g. an old single-core PC"]]})

s.obj(flow("simd", [{"id": "cu", "label": "control unit"},
                    {"id": "p0", "label": "PE 0"}, {"id": "p1", "label": "PE 1"}, {"id": "p2", "label": "PE 2"}, {"id": "p3", "label": "PE 3"},
                    {"id": "d0", "label": "data 0"}, {"id": "d1", "label": "data 1"}, {"id": "d2", "label": "data 2"}, {"id": "d3", "label": "data 3"}],
           [{"from": "cu", "to": "p0"}, {"from": "cu", "to": "p1"}, {"from": "cu", "to": "p2"}, {"from": "cu", "to": "p3"},
            {"from": "p0", "to": "d0"}, {"from": "p1", "to": "d1"}, {"from": "p2", "to": "d2"}, {"from": "p3", "to": "d3"}]))
s.obj({"id": "simdx", "type": "table", "region": "right", "columns": ["SIMD"], "rows": [
    ["one control unit broadcasts"], ["each PE: same instruction, own data"], ["all in lockstep"],
    ["e.g. vector units, GPUs, SSE, AVX"]]})
s.obj({"id": "pix", "type": "array", "region": "bottom", "values": [40, 52, 33, 61, 47, 58, 39, 44]})

s.obj(flow("misd", [{"id": "d", "label": "one data item"}, {"id": "f1", "label": "unit 1: op A"}, {"id": "f2", "label": "unit 2: op B"},
                    {"id": "f3", "label": "unit 3: op C"}],
           [{"from": "d", "to": "f1"}, {"from": "d", "to": "f2"}, {"from": "d", "to": "f3"}]))
s.obj({"id": "misdx", "type": "table", "region": "right", "columns": ["MISD: the rare one"], "rows": [
    ["different instructions, same data"],
    ["e.g. redundant flight computers that vote"],
    ["e.g. systolic arrays (often cited)"],
    ["no mainstream computer is MISD"]]})

s.obj(flow("mimd", [{"id": "c0", "label": "core 0: own PC"}, {"id": "c1", "label": "core 1: own PC"},
                    {"id": "c2", "label": "core 2: own PC"}, {"id": "c3", "label": "core 3: own PC"},
                    {"id": "mem", "label": "memory"}],
           [{"from": "c0", "to": "mem"}, {"from": "c1", "to": "mem"}, {"from": "c2", "to": "mem"}, {"from": "c3", "to": "mem"}]))
s.obj({"id": "mimdx", "type": "table", "region": "right", "columns": ["MIMD"], "rows": [
    ["own instructions, own data"], ["shared memory: multicore chips"],
    ["distributed memory: clusters"]]})

s.obj({"id": "spmd", "type": "code", "region": "left", "language": "c", "lines": [
    "id = my_core();           // 0, 1, 2 or 3",
    "lo = id * 2000;",
    "hi = lo + 2000;",
    "for (i = lo; i < hi; i++)",
    "    part += a[i];",
    "if (id == 0) total = combine();"]})
s.obj({"id": "spmdx", "type": "table", "region": "right", "columns": ["", "SIMD", "SPMD"], "rows": [
    ["PCs", "one, shared", "one per processor"],
    ["runs", "same instruction, lockstep", "same program, own pace"],
    ["branches", "all take one path", "each can differ"]]})

s.obj({"id": "trap", "type": "table", "region": "center", "columns": ["machine", "instructions per cycle", "instruction streams", "data streams", "Flynn class"], "rows": [
    ["simple single-core CPU", "1", "1", "1", "SISD"],
    ["pipelined single core", "up to 1, overlapped", "1", "1", "SISD"],
    ["4-wide superscalar core", "up to 4", "1", "1", "SISD"],
    ["4-core chip, 4 threads", "4 cores × 1 or more", "4", "4", "MIMD"]]})

s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["#", "machine", "class"], "rows": [
    ["a", "one superscalar core running one program", ""],
    ["b", "an 8-core laptop running 8 threads of a program", ""],
    ["c", "an AVX instruction adding 16 pairs of floats", ""],
    ["d", "a GPU applying one kernel to a million pixels", ""],
    ["e", "three flight computers computing on the same sensor data and voting", ""],
    ["f", "a 100-node cluster running one MPI program on different parts of the data", ""]]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("In 1966, Michael Flynn sorted computers by a simple question: how many streams of instructions, and how many streams of data?", [s.head("Flynn's taxonomy")])
s.step("Two answers each, single or multiple, give four classes.", [s.take("Flynn: count instruction streams × data streams")])
s.step("Here are the seven stages.", [s.untake(), {"action": "show", "target": "stages"}])
s.step("The idea, then each of the four classes, with how multiple-instruction machines are actually programmed.", [{"action": "highlight", "target": "stages[0..=4]"}])
s.step("Then the exam trap about superscalar processors, and a set of real machines to classify.", [{"action": "highlight", "target": "stages[5..=6]"}])

# ---------------------------------------------------------------- idea
s.scene("idea")
s.step("Stage 1: what is a stream?", [s.head("Stage 1 of 7: streams"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "defs"}])
s.step("An instruction stream is the sequence of instructions coming from one program counter.", [{"action": "highlight", "target": "defs[0]"}])
s.step("A data stream is the sequence of data those instructions operate on.", [{"action": "highlight", "target": "defs[1]"}])
s.step("Put single and multiple on each axis, and you get a two by two grid.", [{"action": "show", "target": "grid"}])
s.step("Single instruction, single data: SISD.", [{"action": "highlight", "target": "grid[0][1]"}])
s.step("Single instruction, multiple data: SIMD.", [{"action": "highlight", "target": "grid[0][2]"}])
s.step("Multiple instruction, single data: MISD.", [{"action": "highlight", "target": "grid[1][1]"}])
s.step("And multiple instruction, multiple data: MIMD.", [{"action": "highlight", "target": "grid[1][2]"}])
s.step("Keep the rule in mind: Flynn counts streams, not how fast or how many instructions finish per cycle.", [{"action": "hide", "target": "defs"}, s.take("Flynn counts streams — not speed, not issue width")])

# ---------------------------------------------------------------- SISD
s.scene("sisd")
s.step("Stage 2: SISD, single instruction stream, single data stream.", [s.head("Stage 2 of 7: SISD"), {"action": "hide", "target": "grid"}, s.untake(), {"action": "show", "target": "sisd"}])
s.step("One control unit fetches instructions from one program counter.", [{"action": "highlight", "target": "sisd.cu"}])
s.step("One processing unit carries them out on data from memory.", [{"action": "highlight", "target": "sisd.pe"}, {"action": "highlight", "target": "sisd.m", "delay": 0.4}])
s.step("This is the classic uniprocessor, the von Neumann machine.", [{"action": "show", "target": "sisdx"}, {"action": "highlight", "target": "sisdx[0..=1]"}])
s.step("Adding 10 to eight numbers takes eight separate add instructions, one data item each.", [{"action": "highlight", "target": "sisdx[2]"}])

# ---------------------------------------------------------------- SIMD
s.scene("simd")
s.step("Stage 3: SIMD, single instruction stream, multiple data streams.", [s.head("Stage 3 of 7: SIMD"), {"action": "hide", "target": "sisd"}, {"action": "hide", "target": "sisdx"}, {"action": "show", "target": "simd"}])
s.step("One control unit fetches and decodes each instruction once.", [{"action": "highlight", "target": "simd.cu"}])
s.step("It broadcasts that instruction to many processing elements, called PEs.", [{"action": "highlight", "target": "simd.p0"}, {"action": "highlight", "target": "simd.p3", "delay": 0.4}])
s.step("Each PE applies it to its own piece of data, all in the same cycle, in lockstep.", [{"action": "mark", "target": "simd.d0"}, {"action": "mark", "target": "simd.d1", "delay": 0.2}, {"action": "mark", "target": "simd.d2", "delay": 0.4}, {"action": "mark", "target": "simd.d3", "delay": 0.6}])
s.step("Example: brighten eight pixels by adding 10 to each, with one instruction.", [{"action": "show", "target": "pix"}, {"action": "highlight", "target": "pix[0..=7]"}])
s.step("40 becomes 50, 52 becomes 62, and so on: eight results from one instruction.", [{"action": "set", "target": "pix[0]", "value": 50}, {"action": "set", "target": "pix[1]", "value": 62}, {"action": "set", "target": "pix[2]", "value": 43},
    {"action": "set", "target": "pix[3]", "value": 71}, {"action": "set", "target": "pix[4]", "value": 57}, {"action": "set", "target": "pix[5]", "value": 68},
    {"action": "set", "target": "pix[6]", "value": 49}, {"action": "set", "target": "pix[7]", "value": 54}])
s.step("Vector processors, GPUs and instruction sets like SSE and AVX are all SIMD.", [{"action": "hide", "target": "pix"}, {"action": "show", "target": "simdx"}, {"action": "highlight", "target": "simdx[3]"}])
s.step("If the code branches, some elements must sit idle while others run, because every PE follows the one instruction stream.", [{"action": "highlight", "target": "simdx[2]"}])
s.step("So SIMD is fastest when every element does exactly the same work.", [])
s.step("SIMD fits data-level parallelism: the same operation on many items.", [s.take("SIMD exploits data-level parallelism")])

# ---------------------------------------------------------------- MISD
s.scene("misd")
s.step("Stage 4: MISD, multiple instruction streams, single data stream.", [s.head("Stage 4 of 7: MISD"), {"action": "hide", "target": "simd"}, {"action": "hide", "target": "simdx"}, s.untake(), {"action": "show", "target": "misd"}])
s.step("Several units each run their own instructions, all on the same stream of data.", [{"action": "highlight", "target": "misd.d"}, {"action": "mark", "target": "misd.f1", "delay": 0.3}, {"action": "mark", "target": "misd.f2", "delay": 0.5}, {"action": "mark", "target": "misd.f3", "delay": 0.7}])
s.step("It is the rare class: no mainstream general-purpose computer is built this way.", [{"action": "show", "target": "misdx"}, {"action": "highlight", "target": "misdx[3]"}])
s.step("The usual example is fault tolerance: redundant flight computers process the same sensor data and vote on the answer.", [{"action": "highlight", "target": "misdx[1]"}])
s.step("Systolic arrays are also cited: data pulses through a chain of units, each doing a different step to it.", [{"action": "highlight", "target": "misdx[2]"}])
s.step("Textbooks disagree on whether these are truly MISD, so in an exam, give the example and say that MISD is rare.", [s.take("MISD: rare · examples: redundant voting computers, systolic arrays")])

# ---------------------------------------------------------------- MIMD + SPMD
s.scene("mimd")
s.step("Stage 5: MIMD, multiple instruction streams, multiple data streams.", [s.head("Stage 5 of 7: MIMD and SPMD"), {"action": "hide", "target": "misd"}, {"action": "hide", "target": "misdx"}, s.untake(), {"action": "show", "target": "mimd"}])
s.step("Every processor has its own program counter, fetches its own instructions, and works on its own data.", [{"action": "mark", "target": "mimd.c0"}, {"action": "mark", "target": "mimd.c1", "delay": 0.2}, {"action": "mark", "target": "mimd.c2", "delay": 0.4}, {"action": "mark", "target": "mimd.c3", "delay": 0.6}])
s.step("Multicore chips are MIMD with shared memory: all cores read and write one memory.", [{"action": "show", "target": "mimdx"}, {"action": "highlight", "target": "mimdx[1]"}])
s.step("Clusters are MIMD with distributed memory: each node has its own memory, and nodes exchange messages over a network.", [{"action": "highlight", "target": "mimdx[2]"}])
s.step("MIMD is the most flexible class, and it exploits thread-level and request-level parallelism.", [s.take("MIMD exploits thread-level and request-level parallelism")])
s.step("But how do you program a thousand processors? Usually with one program: SPMD, single program, multiple data.", [{"action": "hide", "target": "mimd"}, {"action": "hide", "target": "mimdx"}, s.untake(), {"action": "show", "target": "spmd"}])
s.step("Every core runs this same code, but first asks which core it is.", [{"action": "goto_line", "target": "spmd", "line": 1}])
s.step("Core 2, for example, gets lo equal to 4000 and hi equal to 6000, and sums only that part.", [{"action": "mark_lines", "target": "spmd", "from": 2, "to": 5}])
s.step("And only core 0 takes this branch to combine the results.", [{"action": "goto_line", "target": "spmd", "line": 6}])
s.step("So how is SPMD different from SIMD? Compare them.", [{"action": "show", "target": "spmdx"}])
s.step("SIMD has one shared program counter; in SPMD, each processor has its own.", [{"action": "highlight", "target": "spmdx[0]"}])
s.step("SIMD elements run the same instruction in lockstep; SPMD processors run the same program, each at its own pace.", [{"action": "highlight", "target": "spmdx[1]"}])
s.step("And SPMD processors can take different branches, like core 0 here. That is why SPMD runs on MIMD hardware.", [{"action": "highlight", "target": "spmdx[2]"}, s.take("SPMD = one program on MIMD hardware, each processor on its own data")])

# ---------------------------------------------------------------- trap
s.scene("trap")
s.step("Stage 6, the trap: a superscalar core issues four instructions per cycle. Is it MIMD?", [s.head("Stage 6 of 7: the trap"), {"action": "hide", "target": "spmd"}, {"action": "hide", "target": "spmdx"}, s.untake(), {"action": "show", "target": "trap"}])
s.step("A simple single core runs one instruction at a time: one instruction stream, one data stream, SISD.", [{"action": "highlight", "target": "trap[0]"}])
s.step("Pipelining overlaps several instructions, but they still come from one program counter: still SISD.", [{"action": "highlight", "target": "trap[1]"}])
s.step("A 4-wide superscalar core issues up to four instructions per cycle.", [{"action": "highlight", "target": "trap[2][1]"}])
s.step("But all four come from the same program, one instruction stream, working on one data stream. So it is still SISD.", [{"action": "highlight", "target": "trap[2]"}, {"action": "mark", "target": "trap[2][4]", "delay": 0.5}])
s.step("Only when there are several independent instruction streams, like four cores running four threads, does it become MIMD.", [{"action": "highlight", "target": "trap[3]"}])
s.step("Flynn counts streams, not issue width. Pipelining and superscalar are instruction-level parallelism inside SISD.", [s.take("superscalar and pipelined cores are still SISD: one instruction stream")])

# ---------------------------------------------------------------- exam
s.scene("exam")
answers = ["SISD", "MIMD", "SIMD", "SIMD", "MISD", "MIMD (SPMD)"]
says = [
    "a: one program, one instruction stream, however wide the core: SISD.",
    "b: eight threads with eight program counters, each on its own data: MIMD.",
    "c: one instruction, sixteen pairs of data: SIMD.",
    "d: one kernel applied to many pixels: SIMD. GPUs are SIMD machines, built from many threads.",
    "e: different computers, the same data, voting: the usual MISD example.",
    "f: one program on many nodes, each with its own data and program counter: MIMD, programmed as SPMD.",
]
s.step("Now an exam question: classify each machine.", [s.head("Exam question"), {"action": "hide", "target": "trap"}, s.untake(), {"action": "show", "target": "qx"}])
s.step("Pause and classify all six, then check with me.", [{"action": "highlight", "target": "qx.machine"}])
for i, (a, t) in enumerate(zip(answers, says)):
    s.step(t, [{"action": "highlight", "target": f"qx[{i}]"}, {"action": "set", "target": f"qx[{i}][2]", "value": a, "delay": 0.4}])
s.step("Count the marks you lose most often: a, where width tempts you to say MIMD, and f, where one program tempts you to say SIMD.", [{"action": "highlight", "target": "qx[0]"}, {"action": "highlight", "target": "qx[5]", "delay": 0.4}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qx"}, {"action": "show", "target": "stages"}])
s.step("Flynn's grid counts instruction streams and data streams.", [{"action": "highlight", "target": "stages[0]"}])
s.step("SISD is the uniprocessor; SIMD broadcasts one instruction to many data.", [{"action": "highlight", "target": "stages[1..=2]"}])
s.step("MISD is rare; MIMD gives each processor its own instructions and data, and is usually programmed as SPMD.", [{"action": "highlight", "target": "stages[3..=4]"}])
s.step("Superscalar is still SISD. Next video: the instruction pipeline, stage by stage.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Next: the instruction pipeline — IF, ID, EX, MEM, WB")])

s.save(sys.argv[1])

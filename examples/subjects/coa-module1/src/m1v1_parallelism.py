"""Module 1, video 1: data-level and task-level parallelism, and the four ways hardware exploits them."""
import sys
sys.path.insert(0, ".")
from common import Script

N = 64
scalar_per_elem = 6          # load, add, store, increment index, compare, branch
scalar_total = N * scalar_per_elem
vector_total = 3             # vector load, vector add (scalar 10 to every element), vector store
assert scalar_total == 384
cores, total = 4, 8000
assert total // cores == 2000

s = Script("Parallelism: data-level, task-level, and how hardware exploits them")

s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Two kinds of parallelism in programs: data-level and task-level"],
    [2, "Instruction-level parallelism: overlap independent instructions"],
    [3, "Vector architectures and GPUs: one instruction, many data"],
    [4, "Thread-level parallelism: tightly coupled threads"],
    [5, "Request-level parallelism: many independent requests"],
    [6, "One table: what each exploits, and who finds the parallelism"]]})
s.obj({"id": "kinds", "type": "table", "region": "center", "columns": ["kind", "what is parallel", "example"], "rows": [
    ["data-level (DLP)", "the same operation on many data items at once", "add 10 to every element of an array"],
    ["task-level (TLP)", "different tasks that can run independently", "a browser downloads, decodes video and draws the page"]]})
s.obj({"id": "arr", "type": "array", "region": "center", "values": [3, 8, 1, 6, 4, 9, 2, 7]})
s.obj({"id": "arr2", "type": "array", "region": "center", "values": [13, 18, 11, 16, 14, 19, 12, 17]})

# ILP
s.obj({"id": "ilpcode", "type": "code", "region": "left", "language": "c", "lines": [
    "a = b + c;", "d = e + f;", "g = a + d;"]})
s.obj({"id": "ilptime", "type": "timeline", "region": "right", "lanes": ["unit 1", "unit 2"], "end": 4, "unit": "clock cycle", "now": 0,
       "blocks": []})

# vector
s.obj({"id": "vcode", "type": "code", "region": "left", "language": "asm", "lines": [
    "loop: LD   R1, 0(R2)", "      ADDI R1, R1, 10", "      SD   R1, 0(R2)", "      ADDI R2, R2, 8", "      SUBI R3, R3, 1", "      BNEZ R3, loop"]})
s.obj({"id": "vcode2", "type": "code", "region": "right", "language": "asm", "lines": [
    "LV    V1, 0(R2)", "ADDVS V1, V1, 10", "SV    V1, 0(R2)"]})
s.obj({"id": "vmath", "type": "math", "region": "bottom", "lines": [
    "\"scalar\": 64 times 6 = 384 \"instructions\" quad \"vector\": 3 \"instructions\""]})

# TLP
s.obj({"id": "tlp", "type": "diagram", "region": "center", "layout": "layers", "direction": "down", "nodes": [
    {"id": "data", "label": "8000 numbers, shared"},
    {"id": "c0", "label": "T0: 0–1999"}, {"id": "c1", "label": "T1: 2000–3999"},
    {"id": "c2", "label": "T2: 4000–5999"}, {"id": "c3", "label": "T3: 6000–7999"},
    {"id": "sum", "label": "add 4 sums", "shape": "pill"}],
    "edges": [{"from": "data", "to": "c0"}, {"from": "data", "to": "c1"}, {"from": "data", "to": "c2"}, {"from": "data", "to": "c3"},
              {"from": "c0", "to": "sum"}, {"from": "c1", "to": "sum"}, {"from": "c2", "to": "sum"}, {"from": "c3", "to": "sum"}]})

# RLP
s.obj({"id": "rlp", "type": "diagram", "region": "center", "layout": "layers", "direction": "right", "nodes": [
    {"id": "u1", "label": "student 1: result?", "shape": "pill"}, {"id": "u2", "label": "student 2: result?", "shape": "pill"},
    {"id": "u3", "label": "student 3: result?", "shape": "pill"},
    {"id": "lb", "label": "load balancer"},
    {"id": "s1", "label": "server 1"}, {"id": "s2", "label": "server 2"}, {"id": "s3", "label": "server 3"}],
    "edges": [{"from": "u1", "to": "lb"}, {"from": "u2", "to": "lb"}, {"from": "u3", "to": "lb"},
              {"from": "lb", "to": "s1"}, {"from": "lb", "to": "s2"}, {"from": "lb", "to": "s3"}]})

s.obj({"id": "summary", "type": "table", "region": "center", "columns": ["hardware approach", "exploits", "who finds the parallelism", "example"], "rows": [
    ["instruction-level (ILP)", "data-level, modestly", "hardware and compiler: implicit", "pipelining, superscalar"],
    ["vector, GPU, SIMD instructions", "data-level", "programmer or compiler: explicit", "add 10 to 64 numbers at once"],
    ["thread-level", "data-level or task-level", "programmer: explicit threads", "4 cores share one array"],
    ["request-level", "largely independent tasks", "programmer or OS", "a web server's many users"]]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["#", "situation", "parallelism exploited"], "rows": [
    ["a", "a GPU blurs every pixel of a photo with the same filter", ""],
    ["b", "a CPU starts the next independent add before the last one finishes", ""],
    ["c", "8 threads share memory and each sorts part of one array, then merge", ""],
    ["d", "a search engine answers millions of separate queries", ""],
    ["e", "one vector instruction multiplies 128 pairs of numbers", ""]]})

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("A computer gets faster in two ways: a faster clock, or doing more than one thing at a time.", [s.head("Parallelism: what programs offer, and how hardware uses it")])
s.step("Doing more at once is parallelism, and it comes in a few clear kinds.", [s.take("parallelism = doing more than one thing at the same time")])
s.step("Here is the plan, in six stages.", [s.untake(), {"action": "show", "target": "stages"}])
s.step("First, the two kinds of parallelism a program can contain: data-level and task-level.", [{"action": "highlight", "target": "stages[0]"}])
s.step("Then the four ways hardware exploits them: instruction-level, vector and GPU, thread-level, and request-level.", [{"action": "highlight", "target": "stages[1..=4]"}])
s.step("And one table at the end that puts all four side by side.", [{"action": "highlight", "target": "stages[5]"}])

# ---------------------------------------------------------------- two kinds
s.scene("kinds")
s.step("Stage 1: what kind of parallelism is in the program itself?", [s.head("Stage 1 of 6: data-level and task-level"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "kinds"}])
s.step("Data-level parallelism means the same operation is applied to many data items, and they can all be done at once.", [{"action": "highlight", "target": "kinds[0]"}])
s.step("Adding 10 to every element of an array is the classic example.", [{"action": "highlight", "target": "kinds[0][2]"}])
s.step("Task-level parallelism means different tasks that do not depend on each other, so they can run at the same time.", [{"action": "highlight", "target": "kinds[1]"}])
s.step("A browser downloading a file, playing a video and drawing a page is task-level parallelism.", [{"action": "highlight", "target": "kinds[1][2]"}])
s.step("Here is our data-level example: eight numbers, and we want to add 10 to each one.", [{"action": "hide", "target": "kinds"}, {"action": "show", "target": "arr"}])
s.step("Done one at a time, that is eight separate adds, one after another.", [{"action": "highlight", "target": "arr[0]"}])
s.step("But no element depends on any other, so all eight adds could happen together.", [{"action": "highlight", "target": "arr[0..=7]"}])
s.step("3 becomes 13, 8 becomes 18, and so on, all in one go.", [{"action": "hide", "target": "arr"}, {"action": "show", "target": "arr2"}, {"action": "mark", "target": "arr2[0..=7]", "delay": 0.4}])
s.step("A program offers the parallelism; the hardware decides how much of it to use. There are four ways.", [s.take("programs offer DLP and TLP · hardware exploits them in 4 ways")])

# ---------------------------------------------------------------- ILP
s.scene("ilp")
s.step("Stage 2: instruction-level parallelism, or ILP.", [s.head("Stage 2 of 6: instruction-level parallelism"), {"action": "hide", "target": "arr2"}, s.untake(), {"action": "show", "target": "ilpcode"}])
s.step("Look at these three lines. The first adds b and c; the second adds e and f.", [{"action": "goto_line", "target": "ilpcode", "line": 1}])
s.step("Neither uses the other's result, so the hardware can work on both at the same time.", [{"action": "mark_lines", "target": "ilpcode", "from": 1, "to": 2}])
s.step("The third line needs a and d, so it must wait for both.", [{"action": "goto_line", "target": "ilpcode", "line": 3}])
s.step("With two adders, lines one and two run together in cycle one.", [{"action": "show", "target": "ilptime"},
    {"action": "add_block", "target": "ilptime", "id": "i1", "lane": "unit 1", "start": 0, "end": 1, "label": "a = b + c"},
    {"action": "add_block", "target": "ilptime", "id": "i2", "lane": "unit 2", "start": 0, "end": 1, "label": "d = e + f", "delay": 0.3}])
s.step("Line three runs in cycle two: two cycles instead of three.", [{"action": "add_block", "target": "ilptime", "id": "i3", "lane": "unit 1", "start": 1, "end": 2, "label": "g = a + d"}, {"action": "advance", "target": "ilptime", "to": 2}])
s.step("The programmer wrote ordinary sequential code; the hardware and compiler found the overlap themselves.", [s.take("ILP is implicit: hardware and compiler find it, the program looks sequential")])
s.step("Pipelining overlaps the stages of instructions; superscalar issues several per cycle; speculation guesses past branches. All are ILP.", [])
s.step("ILP exploits data-level parallelism, but only modestly: programs rarely have more than a few independent instructions close together.", [s.take("ILP exploits DLP at modest levels: a few instructions at a time")])

# ---------------------------------------------------------------- vector
s.scene("vector")
s.step("Stage 3: vector architectures and GPUs, which go after data-level parallelism directly.", [s.head("Stage 3 of 6: vector architectures and GPUs"), {"action": "hide", "target": "ilpcode"}, {"action": "hide", "target": "ilptime"}, s.untake(), {"action": "show", "target": "vcode"}])
s.step("Take 64 numbers. A scalar processor runs this loop once per element.", [{"action": "mark_lines", "target": "vcode", "from": 1, "to": 6}])
s.step("Load one number, add 10, store it back, move the pointer, count down, and branch: 6 instructions each time.", [{"action": "goto_line", "target": "vcode", "line": 2}])
s.step("A vector processor uses one instruction for all 64: load a whole vector, add 10 to every element, store the vector.", [{"action": "show", "target": "vcode2"}, {"action": "mark_lines", "target": "vcode2", "from": 1, "to": 3, "delay": 0.4}])
s.step("Count them: 64 times 6 is 384 instructions for the loop, against just 3 vector instructions.", [{"action": "show", "target": "vmath"}, {"action": "highlight", "target": "vmath[0]"}])
s.step("Fewer instructions also means less fetching and decoding, which saves time and energy.", [])
s.step("This is single instruction, multiple data, or SIMD: one instruction, applied to a whole collection of data.", [])
s.step("GPUs do the same with thousands of small threads, and multimedia instructions like Intel's AVX do it on short vectors inside a normal CPU.", [])
s.step("Unlike ILP, this is explicit: the programmer or the compiler must write the vector operation.", [{"action": "hide", "target": "vmath"}, s.take("vector, GPU, SIMD: exploit DLP explicitly, one instruction for many data")])

# ---------------------------------------------------------------- TLP
s.scene("tlp")
s.step("Stage 4: thread-level parallelism.", [s.head("Stage 4 of 6: thread-level parallelism"), {"action": "hide", "target": "vcode"}, {"action": "hide", "target": "vcode2"}, s.untake(), {"action": "show", "target": "tlp"}])
s.step("Say we want the sum of 8000 numbers on a processor with 4 cores.", [{"action": "highlight", "target": "tlp.data"}])
s.step("Split the work: 8000 divided by 4 is 2000 numbers per thread.", [{"action": "highlight", "target": "tlp.c0"}, {"action": "highlight", "target": "tlp.c3", "delay": 0.4}])
s.step("Thread 0 sums elements 0 to 1999, thread 1 sums 2000 to 3999, and so on, all at once.", [{"action": "mark", "target": "tlp.c0"}, {"action": "mark", "target": "tlp.c1", "delay": 0.2}, {"action": "mark", "target": "tlp.c2", "delay": 0.4}, {"action": "mark", "target": "tlp.c3", "delay": 0.6}])
s.step("Then the four partial sums are combined into one answer.", [{"action": "highlight", "target": "tlp.sum"}])
s.step("The threads share memory and must coordinate at the end, so we call them tightly coupled.", [s.take("TLP: many threads, shared memory, they interact")])
s.step("Thread-level parallelism can exploit data-level parallelism, as here, or task-level, by giving each thread a different job.", [])
s.step("It is explicit too: the programmer creates the threads and decides how to split the work.", [])

# ---------------------------------------------------------------- RLP
s.scene("rlp")
s.step("Stage 5: request-level parallelism.", [s.head("Stage 5 of 6: request-level parallelism"), {"action": "hide", "target": "tlp"}, s.untake(), {"action": "show", "target": "rlp"}])
s.step("On results day, thousands of students ask the university website for their marks at the same moment.", [{"action": "highlight", "target": "rlp.u1"}, {"action": "highlight", "target": "rlp.u3", "delay": 0.4}])
s.step("Each request is independent: one student's result has nothing to do with another's.", [])
s.step("A load balancer simply hands requests to many servers, and each one answers on its own.", [{"action": "highlight", "target": "rlp.lb"}, {"action": "mark", "target": "rlp.s1", "delay": 0.3}, {"action": "mark", "target": "rlp.s2", "delay": 0.5}, {"action": "mark", "target": "rlp.s3", "delay": 0.7}])
s.step("This is request-level parallelism: largely decoupled tasks, set up by the programmer or the operating system.", [s.take("RLP: largely independent requests, hardly any interaction")])
s.step("The difference from thread-level is coupling: these tasks barely talk to each other, so they scale across whole warehouses of servers.", [])

# ---------------------------------------------------------------- summary
s.scene("summary")
s.step("Stage 6: all four, side by side.", [s.head("Stage 6 of 6: what each exploits"), {"action": "hide", "target": "rlp"}, s.untake(), {"action": "show", "target": "summary"}])
s.step("Instruction-level: exploits data-level parallelism modestly, found implicitly by hardware and compiler.", [{"action": "highlight", "target": "summary[0]"}])
s.step("Vector, GPU and SIMD instructions: exploit data-level parallelism directly, written explicitly.", [{"action": "highlight", "target": "summary[1]"}])
s.step("Thread-level: exploits data-level or task-level parallelism, with threads that share memory and interact.", [{"action": "highlight", "target": "summary[2]"}])
s.step("Request-level: exploits largely independent tasks, like the requests to a web server.", [{"action": "highlight", "target": "summary[3]"}])
s.step("Read the third column for the exam: only instruction-level parallelism is implicit; the other three are explicit.", [{"action": "highlight", "target": "summary.c2"}])
s.step("Moving down the table, the units grow from instructions, to data items, to threads, to whole requests.", [{"action": "mark", "target": "summary.c0"}])

# ---------------------------------------------------------------- exam
s.scene("exam")
answers = ["data-level, by a GPU (SIMD)", "instruction-level (implicit)", "thread-level, tightly coupled", "request-level", "data-level, by a vector unit"]
says = [
    "a: the same filter on every pixel is data-level parallelism, exploited by the GPU.",
    "b: overlapping independent instructions on its own is instruction-level parallelism, found implicitly.",
    "c: threads that share memory and merge their results are thread-level parallelism, tightly coupled.",
    "d: millions of separate queries are request-level parallelism.",
    "e: one instruction on 128 pairs is data-level parallelism on a vector unit.",
]
s.step("Now an exam question: name the parallelism each situation exploits.", [s.head("Exam question"), {"action": "hide", "target": "summary"}, {"action": "show", "target": "qx"}])
s.step("Pause and try all five, then check with me.", [{"action": "highlight", "target": "qx.situation"}])
for i, (a, t) in enumerate(zip(answers, says)):
    s.step(t, [{"action": "highlight", "target": f"qx[{i}]"}, {"action": "set", "target": f"qx[{i}][2]", "value": a, "delay": 0.4}])
s.step("The usual mistake is between c and d: if the tasks share data and interact, it is thread-level; if they are independent requests, it is request-level.", [{"action": "highlight", "target": "qx[2]"}, {"action": "highlight", "target": "qx[3]", "delay": 0.4}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages once more.", [s.head("Recap"), {"action": "hide", "target": "qx"}, {"action": "show", "target": "stages"}])
s.step("Programs offer two kinds: data-level, the same work on many items, and task-level, independent jobs.", [{"action": "highlight", "target": "stages[0]"}])
s.step("ILP overlaps independent instructions, implicitly. Vector machines and GPUs apply one instruction to many data.", [{"action": "highlight", "target": "stages[1..=2]"}])
s.step("Thread-level uses tightly coupled threads; request-level uses independent requests.", [{"action": "highlight", "target": "stages[3..=4]"}])
s.step("Next video: Flynn's taxonomy, which sorts machines by how many instruction and data streams they have.", [{"action": "mark", "target": "stages[0..=5]"}, s.take("Next: Flynn's taxonomy — SISD, SIMD, MISD, MIMD")])

s.save(sys.argv[1])

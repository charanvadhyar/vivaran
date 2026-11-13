"""DSA Module 1, video 8: queues: linear, circular, deque, priority queue, print queue."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

class CQ:
    def __init__(s, n): s.n, s.q, s.h, s.t = n, [""] * n, 0, 0
    def full(s): return s.h == (s.t + 1) % s.n
    def empty(s): return s.h == s.t
    def enq(s, x):
        if s.full(): return "overflow"
        s.q[s.t] = x; s.t = (s.t + 1) % s.n
    def deq(s):
        x = s.q[s.h]; s.h = (s.h + 1) % s.n; return x
    def count(s): return (s.t - s.h) % s.n
q = CQ(5)
for x in (10, 20, 30, 40): q.enq(x)
assert q.full() and q.t == 4 and q.count() == 4
assert q.deq() == 10 and q.deq() == 20 and q.h == 2
q.enq(50); assert q.t == 0; q.enq(60); assert q.t == 1 and q.full() and q.q == [60, 20, 30, 40, 50] and q.count() == 4
e = CQ(6)
for x in "ABCD": e.enq(x)
e.deq(); e.deq()
for x in "EFG": assert e.enq(x) is None
assert e.h == 2 and e.t == 1 and e.full() and e.count() == 5 and e.enq("H") == "overflow"
assert [e.q[(e.h + k) % 6] for k in range(5)] == list("CDEFG")
jobs = [("J1", 0, 3), ("J2", 1, 2), ("J3", 2, 4), ("J4", 6, 1)]
t = 0; res = []
for j, a, d in jobs:
    start = max(t, a); t = start + d; res.append((j, start, t, start - a))
assert res == [("J1", 0, 3, 0), ("J2", 3, 5, 2), ("J3", 5, 9, 3), ("J4", 9, 10, 3)] and sum(r[3] for r in res) / 4 == 2

s = Script("Queues")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "First in, first out"],
    [2, "A queue in an array, and its flaw"],
    [3, "The circular queue"],
    [4, "Full or empty?"],
    [5, "A linked queue and a deque"],
    [6, "Priority queues"],
    [7, "The printer queue"],
    [8, "Exam question"]]})
s.obj({"id": "ops", "type": "table", "region": "center", "columns": ["operation", "does", "cost"], "rows": [
    ["enqueue(x)", "add x at the rear", "Θ(1)"],
    ["dequeue()", "remove and return the front", "Θ(1)"],
    ["front()", "look at the front", "Θ(1)"],
    ["isEmpty(), isFull()", "", "Θ(1)"],
    ["in at the rear, out at the front", "first in, first out: FIFO", ""]]})
s.obj({"id": "qa1", "type": "array", "region": "center", "values": ["", "", "", "", ""]})
s.obj({"id": "fp", "type": "pointer", "label": "front", "target": "qa1[0]"})
s.obj({"id": "rp", "type": "pointer", "label": "rear", "target": "qa1[0]"})
s.obj({"id": "cq", "type": "array", "region": "center", "values": ["", "", "", "", ""]})
s.obj({"id": "hp", "type": "pointer", "label": "head", "target": "cq[0]"})
s.obj({"id": "tp", "type": "pointer", "label": "tail", "target": "cq[0]"})
s.obj({"id": "fe", "type": "table", "region": "center", "columns": ["circular queue of n cells", "test"], "rows": [
    ["next index", "(i + 1) mod n"],
    ["empty", "head == tail"],
    ["full", "head == (tail + 1) mod n: one cell is always left unused"],
    ["number of elements", "(tail − head + n) mod n"],
    ["why waste a cell?", "otherwise head == tail would mean both full and empty"]]})
s.obj({"id": "ld", "type": "table", "region": "center", "columns": ["structure", "operations", "notes"], "rows": [
    ["linked queue", "enqueue at rear, dequeue at front", "two pointers, no fixed size, Θ(1)"],
    ["deque", "insert and delete at both ends", "double-ended queue"],
    ["input-restricted deque", "insert at one end only", "delete at both"],
    ["output-restricted deque", "delete at one end only", "insert at both"]]})
s.obj({"id": "pq", "type": "table", "region": "center", "columns": ["priority queue built on", "insert", "remove the highest priority"], "rows": [
    ["unsorted array", "Θ(1): append", "Θ(n): search for it"],
    ["sorted array", "Θ(n): shift to make room", "Θ(1): it is at the end"],
    ["binary heap (Module 2)", "Θ(log n)", "Θ(log n)"]]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["job", "arrives", "minutes", "starts", "finishes", "waits"], "rows": [
    ["J1", "0", "3", "", "", ""], ["J2", "1", "2", "", "", ""], ["J3", "2", "4", "", "", ""], ["J4", "6", "1", "", "", ""]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: a circular queue with n = 6 cells, head = tail = 0"], "rows": [
    ["enqueue A, B, C, D;  dequeue twice;  enqueue E, F, G;  then enqueue H"],
    ["a) head and tail after each group      b) is the queue full before H?"],
    ["c) how many elements, and in what order from the front?      d) what happens to H?"]]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["after", "head", "tail", "elements"], "rows": [
    ["enqueue A, B, C, D", "0", "4", "A B C D"],
    ["dequeue twice", "2", "4", "C D"],
    ["enqueue E, F, G", "2", "(4 + 3) mod 6 = 1", "C D E F G"],
    ["full?", "head == (1 + 1) mod 6 = 2: yes", "", "(1 − 2 + 6) mod 6 = 5"],
    ["enqueue H", "", "", "overflow: H is refused"]]})

s.scene("intro")
s.step("A queue is the fair structure: whoever arrives first is served first. Printers, processors, network routers and call centres all run on queues. This video builds one, finds its flaw, and fixes it.", [s.head("Queues")])
s.step("Here are the eight stages.", show("stages"))
s.step("What a queue is, a queue in an array and its flaw, the circular queue, and how to tell full from empty.", [hl("stages[0..=3]")])
s.step("Then linked queues and deques, priority queues, the printer queue from the lab, and an exam question.", [hl("stages[4..=7]")])

s.scene("fifo")
s.step("Stage 1: enqueue adds an item at the rear of the queue.", [s.head("Stage 1 of 8: first in, first out")] + hide("stages") + show("ops") + [hl("ops[0]")])
s.step("Dequeue removes the item at the front. Front just looks at it.", [hl("ops[1..=2]")])
s.step("All of them cost Theta of 1.", [hl("ops[3]")])
s.step("Items leave in the order they arrived: first in, first out, FIFO. The opposite of a stack.", [hl("ops[4]"), s.take("FIFO: in at the rear, out at the front")])

s.scene("lin")
s.step("Stage 2: a queue in an array of 5 cells, with indices front and rear. Enqueue 10, 20, 30, 40 and 50: rear moves right each time.", [s.head("Stage 2 of 8: a queue in an array"), s.untake()] + hide("ops") + show("qa1", "fp", "rp") + [x for i, v in enumerate([10, 20, 30, 40, 50]) for x in (st(f"qa1[{i}]", v, round(0.15 * i, 2)), pt("rp", f"qa1[{i}]", round(0.15 * i + 0.05, 2)))])
s.step("Dequeue twice: 10 and 20 leave, and front moves right to index 2.", [dim("qa1[0]"), pt("fp", "qa1[1]", 0.2), dim("qa1[1]", 0.4), pt("fp", "qa1[2]", 0.6)])
s.step("Now enqueue 60. rear is already at the last cell, so the queue reports overflow, even though two cells at the front are empty.", [hl("qa1[4]"), hl("qa1[0..=1]", 0.5)])
s.step("Shifting everything left on each dequeue would fix it, but that costs Theta of n. There is a better way.", [s.take("linear array queue: wasted space at the front")])

s.scene("circ")
s.step("Stage 3: the circular queue. Treat the array as a ring: after the last cell comes cell 0. Here, as in Cormen, head is the front, and tail is the next free cell.", [s.head("Stage 3 of 8: the circular queue"), s.untake()] + hide("qa1", "fp", "rp") + show("cq", "hp", "tp"))
s.step("Enqueue 10, 20, 30 and 40. tail moves to 4.", [x for i, v in enumerate([10, 20, 30, 40]) for x in (st(f"cq[{i}]", v, round(0.2 * i, 2)), pt("tp", f"cq[{i + 1}]", round(0.2 * i + 0.1, 2)))])
s.step("Dequeue twice: 10 and 20 leave, and head moves to 2.", [dim("cq[0]"), pt("hp", "cq[1]", 0.2), dim("cq[1]", 0.4), pt("hp", "cq[2]", 0.6)])
s.step("Enqueue 50 into cell 4. tail plus 1 is 5, and 5 mod 5 is 0: tail wraps around to the start.", [st("cq[4]", 50), pt("tp", "cq[0]", 0.5)])
s.step("Enqueue 60 into cell 0, reusing the space. tail is now 1. The queue holds 30, 40, 50, 60, in that order, around the ring.", [st("cq[0]", 60), rs("cq[0]", 0.1), pt("tp", "cq[1]", 0.5), hl("cq[2..=4]", 0.6)])
s.step("Every index moves by i plus 1 mod n, so every operation is still Theta of 1, and no cell is wasted for good.", [s.take("advance with (i + 1) mod n")])

s.scene("fe")
s.step("Stage 4: when is a circular queue full, and when empty? Indices move by plus 1 mod n.", [s.head("Stage 4 of 8: full or empty?"), s.untake()] + hide("cq", "hp", "tp") + show("fe") + [hl("fe[0]")])
s.step("Empty: head equals tail. Nothing lies between them.", [hl("fe[1]")])
s.step("Full: one more enqueue would make tail equal head. So full means head equals tail plus 1, mod n. One cell always stays unused: our 5-cell queue holds at most 4.", [hl("fe[2]")])
s.step("The number of elements is tail minus head, plus n, mod n. Adding n keeps the result positive after a wrap.", [hl("fe[3]")])
s.step("Why waste a cell? If the queue could fill every cell, then head equal to tail would mean both full and empty. The alternative is to keep a separate count.", [hl("fe[4]"), s.take("empty: head = tail · full: head = tail + 1 (mod n)")])

s.scene("ld")
s.step("Stage 5: a queue can also be a linked list with two pointers: dequeue at the front node, enqueue after the rear node. No size limit, still Theta of 1.", [s.head("Stage 5 of 8: linked queues and deques"), s.untake()] + hide("fe") + show("ld") + [hl("ld[0]")])
s.step("A deque, a double-ended queue, allows inserting and deleting at both ends. It can act as a stack or as a queue.", [hl("ld[1]")])
s.step("Two restricted forms: an input-restricted deque inserts at one end only but deletes at both; an output-restricted deque deletes at one end only but inserts at both.", [hl("ld[2..=3]"), s.take("deque: both ends open")])

s.scene("pq")
s.step("Stage 6: a priority queue serves the most important item first, not the earliest. An emergency room, or an operating system choosing the next process.", [s.head("Stage 6 of 8: priority queues"), s.untake()] + hide("ld") + show("pq"))
s.step("On an unsorted array, insert just appends: Theta of 1. But removing the highest priority means searching: Theta of n.", [hl("pq[0]")])
s.step("On a sorted array, it is the other way round: insert shifts, Theta of n; removal takes the end, Theta of 1.", [hl("pq[1]")])
s.step("A binary heap does both in Theta of log n. That is the right structure, and Module 2 builds it.", [hl("pq[2]"), s.take("priority queue: heap gives log n both ways")])

s.scene("print")
s.step("Stage 7: the lab's printer queue. Four jobs arrive at a shared printer. Each is enqueued when it arrives, and the printer always takes the front job.", [s.head("Stage 7 of 8: the printer queue"), s.untake()] + hide("pq") + show("pr"))
s.step("J1 arrives at minute 0 to an idle printer: it starts at once and finishes at 3. It waits 0.", [st("pr[0][3]", "0"), st("pr[0][4]", "3", 0.2), st("pr[0][5]", "0", 0.4), hl("pr[0]")])
s.step("J2 arrived at 1, but waits in the queue until J1 finishes. It starts at 3, finishes at 5: waited 2.", [st("pr[1][3]", "3"), st("pr[1][4]", "5", 0.2), st("pr[1][5]", "2", 0.4), hl("pr[1]")])
s.step("J3 arrived at 2, starts at 5, finishes at 9: waited 3.", [st("pr[2][3]", "5"), st("pr[2][4]", "9", 0.2), st("pr[2][5]", "3", 0.4), hl("pr[2]")])
s.step("J4 arrives at 6 while J3 prints. It starts at 9 and finishes at 10: waited 3. Average wait: 8 over 4, 2 minutes.", [st("pr[3][3]", "9"), st("pr[3][4]", "10", 0.2), st("pr[3][5]", "3", 0.4), hl("pr[3]"), s.take("start = max(arrival, previous finish)")])

s.scene("exam")
s.step("Now an exam question: a circular queue of 6 cells.", [s.head("Exam question"), s.untake()] + hide("pr") + show("q") + [hl("q[0]")])
s.step("Track head and tail through these operations, decide whether it is full, count and list the elements, and say what happens to H. Pause and work it out.", [hl("q[1..=2]")])
s.step("Four enqueues: tail goes from 0 to 4. Two dequeues remove A and B: head goes to 2.", hide("q") + show("qx") + [hl("qx[0..=1]")])
s.step("E goes into cell 4, F into cell 5, and G into cell 0. tail is 4 plus 3, mod 6: 1.", [hl("qx[2]")])
s.step("Is it full? tail plus 1 is 2, which equals head: yes. The count: 1 minus 2 plus 6, mod 6: 5 elements, C, D, E, F, G from the front.", [hl("qx[3]")])
s.step("So enqueue H is refused: overflow, with one cell, cell 1, deliberately left empty.", [hl("qx[4]"), mk("qx[4][3]", 0.4)])
s.step("The usual slip: writing tail minus head for the count, which gives minus 1 here. Always add n before the mod.", [s.take("count = (tail − head + n) mod n")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qx") + show("stages"))
s.step("A queue is first in, first out. A plain array queue wastes the cells it has dequeued; a circular queue wraps indices with mod n, and leaves one cell empty to tell full from empty.", [hl("stages[0..=3]")])
s.step("Linked queues have no size limit, deques open both ends, priority queues serve by importance, and the printer queue serves jobs in arrival order.", [hl("stages[4..=6]")])
s.step("Next video: the structure that frees us from contiguous memory. Linked lists.", [mk("stages[0..=7]"), s.take("Next: linked lists")])

s.save("/home/claude/playlist/dsa1/d1v8.json")

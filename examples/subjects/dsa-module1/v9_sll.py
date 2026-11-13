"""DSA Module 1, video 9: singly linked lists."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

class Node:
    def __init__(s, v, n=None): s.v, s.n = v, n
def build(vals):
    h = None
    for v in reversed(vals): h = Node(v, h)
    return h
def tolist(h):
    out = []
    while h: out.append(h.v); h = h.n
    return out
def reverse(h):
    prev, cur, steps = None, h, []
    while cur:
        nxt = cur.n; cur.n = prev; prev = cur; cur = nxt
        steps.append((prev.v, cur.v if cur else None))
    return prev, steps
h, stp = reverse(build([1, 2, 3, 4])); assert tolist(h) == [4, 3, 2, 1] and stp == [(1, 2), (2, 3), (3, 4), (4, None)]
L = build([10, 20, 30, 40]); L = Node(5, L)                     # insert at head
p = L
while p.v != 20: p = p.n
p.n = Node(25, p.n)                                             # insert after 20
p = L
while p.n.v != 30: p = p.n
p.n = p.n.n                                                     # delete 30
assert tolist(L) == [5, 10, 20, 25, 40]
L, _ = reverse(L); assert tolist(L) == [40, 25, 20, 10, 5]
def middle(h):
    slow = fast = h
    while fast and fast.n: slow, fast = slow.n, fast.n.n
    return slow.v
assert middle(build(list(range(1, 8)))) == 4 and middle(build([1, 2, 3, 4])) == 3

s = Script("Singly linked lists")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Nodes and pointers"],
    [2, "Walking the list"],
    [3, "Inserting"],
    [4, "Deleting"],
    [5, "Reversing in place"],
    [6, "Arrays or linked lists?"],
    [7, "Two-pointer tricks"],
    [8, "Exam question"]]})
G = lambda i, l, c, r=1, sh=None: {"id": i, "label": l, "at": [c, r], **({"shape": sh} if sh else {})}
s.obj({"id": "ll", "type": "diagram", "region": "center", "layout": "grid", "nodes": [
    G("hd", "head", 0, 1, "pill"), G("a", "10", 2), G("b", "20", 4), G("c", "30", 6), G("d", "40", 8), G("nul", "null", 10, 1, "pill")],
    "edges": [{"from": "hd", "to": "a"}, {"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}, {"from": "d", "to": "nul"}]})
s.obj({"id": "nd", "type": "table", "region": "center", "columns": ["a node", ""], "rows": [
    ["data", "the value stored"],
    ["next", "the address of the next node, or null at the end"],
    ["head", "a pointer to the first node: the only entry point"],
    ["nodes live anywhere in memory", "no shifting, no fixed size, but no A[i]"]]})
s.obj({"id": "tc", "type": "code", "region": "center", "language": "text", "lines": [
    "SEARCH(head, x)",
    "    p = head",
    "    while p != null and p.data != x",
    "        p = p.next",
    "    return p              // null if x is absent",
    "",
    "// every operation that needs position k walks k nodes: Θ(n) worst"]})
s.obj({"id": "rv", "type": "diagram", "region": "center", "layout": "grid", "nodes": [
    G("z", "null", 0, 1, "pill"), G("n1", "1", 2), G("n2", "2", 4), G("n3", "3", 6), G("n4", "4", 8), G("zz", "null", 10, 1, "pill")],
    "edges": [{"from": "n1", "to": "n2"}, {"from": "n2", "to": "n3"}, {"from": "n3", "to": "n4"}, {"from": "n4", "to": "zz"}]})
s.obj({"id": "pv", "type": "pointer", "label": "prev", "target": "rv.z"})
s.obj({"id": "cu", "type": "pointer", "label": "curr", "target": "rv.n1"})
s.obj({"id": "rc", "type": "code", "region": "center", "language": "text", "lines": [
    "REVERSE(head)",
    "    prev = null;  curr = head",
    "    while curr != null",
    "        next = curr.next      // remember the rest",
    "        curr.next = prev      // turn the arrow round",
    "        prev = curr;  curr = next",
    "    return prev               // the new head"]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["operation", "array", "singly linked list"], "rows": [
    ["access element k", "Θ(1)", "Θ(k)"],
    ["insert or delete at the front", "Θ(n): shift", "Θ(1)"],
    ["insert after a known node", "Θ(n): shift", "Θ(1)"],
    ["insert at the end", "Θ(1) if there is room", "Θ(1) with a tail pointer"],
    ["extra memory", "none (unused capacity)", "one pointer per node"],
    ["cache behaviour", "contiguous: fast", "scattered: slower"]]})
s.obj({"id": "tp", "type": "table", "region": "center", "columns": ["slow and fast pointers", ""], "rows": [
    ["slow moves 1, fast moves 2", "when fast reaches the end, slow is at the middle"],
    ["1 → 2 → 3 → 4 → 5 → 6 → 7", "middle: 4, after 3 moves"],
    ["cycle check (Floyd)", "if fast ever meets slow, the list has a cycle"],
    ["k-th from the end", "start one pointer k nodes ahead, move both"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: start with 10 → 20 → 30 → 40"], "rows": [
    ["a) insert 5 at the head; insert 25 after 20; delete 30. Draw the list."],
    ["b) reverse it: the final list, and how many next pointers change?"],
    ["c) where does the slow pointer stop on 1 → 2 → 3 → 4?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "new.next = head; head = new", "5 → 10 → 20 → 30 → 40"],
    ["a", "new.next = p.next; p.next = new  (p at 20)", "5 → 10 → 20 → 25 → 30 → 40"],
    ["a", "q at 25: q.next = q.next.next", "5 → 10 → 20 → 25 → 40"],
    ["b", "every node's next is turned round: 5 changes", "40 → 25 → 20 → 10 → 5"],
    ["c", "fast: 1 → 3 → null after 4; slow: 1 → 2 → 3", "3 (the second of the two middles)"]]})

s.scene("intro")
s.step("Arrays are fast to read but slow to change, because their elements sit side by side. A linked list breaks that rule: each element can live anywhere, and points to the next. This video builds one, inserts, deletes and reverses it.", [s.head("Singly linked lists")])
s.step("Here are the eight stages.", show("stages"))
s.step("Nodes and pointers, walking the list, inserting, and deleting.", [hl("stages[0..=3]")])
s.step("Then reversing a list in place, arrays against linked lists, two-pointer tricks, and an exam question.", [hl("stages[4..=7]")])

s.scene("node")
s.step("Stage 1: a linked list is a chain of nodes. Each node holds data, and next, the address of the following node.", [s.head("Stage 1 of 8: nodes and pointers")] + hide("stages") + show("nd") + [hl("nd[0..=1]")])
s.step("head points to the first node: it is the only way in. The last node's next is null.", [hl("nd[2]")])
s.step("Here is the list 10, 20, 30, 40.", hide("nd") + show("ll") + [hl("ll.hd"), hl("ll.a", 0.3)])
s.step("The nodes can be anywhere in memory, so nothing ever shifts and there is no fixed size. The price: there is no A of i. To reach the fourth node, you must follow three arrows.", [hl("ll.d"), s.take("node = data + next · head = the way in")])

s.scene("walk")
s.step("Stage 2: walking the list. Start a pointer p at head.", [s.head("Stage 2 of 8: walking the list"), s.untake()] + hide("ll") + show("tc") + [ml("tc", 1, 2)])
s.step("While p is not null and its data is not x, move p to p dot next.", [ml("tc", 3, 4)])
s.step("Return p: the node holding x, or null if the walk fell off the end.", [ml("tc", 5, 5)])
s.step("Searching, counting, printing, and reaching position k all walk the list: Theta of n in the worst case. Even sorted, a linked list cannot use binary search, because it cannot jump to the middle.", [ml("tc", 7, 7), s.take("no random access: walking is Θ(n)")])

s.scene("ins")
s.step("Stage 3: insert 5 at the front. Make a node, point its next at the current first node, 10.", [s.head("Stage 3 of 8: inserting"), s.untake()] + hide("tc") + show("ll") + [{"action": "add_node", "target": "ll", "id": "e", "label": "5", "at": [1, 0]}, {"action": "add_edge", "target": "ll", "from": "e", "to": "a", "delay": 0.5}])
s.step("Then move head to the new node. Two pointer changes: Theta of 1, however long the list.", [rm("ll.hd->a"), adde("ll", "hd", "e", None, 0.3), hl("ll.e", 0.6)])
s.step("The order matters. Move head first, and the rest of the list is lost: nothing points to 10 any more.", [hl("ll.a")])
s.step("Insert 25 after 20. Point the new node at 20's successor, 30, then point 20 at the new node.", [{"action": "add_node", "target": "ll", "id": "f", "label": "25", "at": [5, 0]}, {"action": "add_edge", "target": "ll", "from": "f", "to": "c", "delay": 0.3}, rm("ll.b->c", 0.5), adde("ll", "b", "f", None, 0.6)])
s.step("Again Theta of 1, once you hold a pointer to 20. Finding 20 is the walk that costs Theta of n.", [hl("ll.f"), s.take("new.next = p.next, then p.next = new")])

s.scene("del")
s.step("Stage 4: delete 30. We need the node before it, here 25, because that is the pointer that must change.", [s.head("Stage 4 of 8: deleting"), s.untake(), hl("ll.f")])
s.step("Set 25's next to 30's next, which is 40. Nothing points to 30 any more: it is unlinked, and its memory can be freed.", [rm("ll.f->c"), adde("ll", "f", "d", None, 0.3), dim("ll.c", 0.5)])
s.step("Remove it.", [rm("ll.c")])
s.step("Deleting the first node is the special case: there is no node before it, so head itself moves to head dot next. Forgetting this case is the classic bug.", [hl("ll.hd"), s.take("delete: prev.next = prev.next.next")])

s.scene("rev")
s.step("Stage 5: reverse a list in place, using three pointers: prev, curr and next.", [s.head("Stage 5 of 8: reversing in place"), s.untake()] + hide("ll") + show("rc") + [ml("rc", 1, 7)])
s.step("prev starts at null, curr at the head. Each pass saves curr's next, turns curr's arrow round to point at prev, then moves both pointers one step.", [ml("rc", 3, 6)])
s.step("The list 1, 2, 3, 4. prev is null, curr is 1.", hide("rc") + show("rv", "pv", "cu"))
s.step("Pass 1: save next, 2. Point 1 back at null. prev moves to 1, curr to 2.", [rm("rv.n1->n2"), adde("rv", "n1", "z", None, 0.3), pt("pv", "rv.n1", 0.6), pt("cu", "rv.n2", 0.7)])
s.step("Pass 2: point 2 back at 1. prev moves to 2, curr to 3.", [rm("rv.n2->n3"), adde("rv", "n2", "n1", None, 0.3), pt("pv", "rv.n2", 0.6), pt("cu", "rv.n3", 0.7)])
s.step("Pass 3: point 3 back at 2. Pass 4: point 4 back at 3.", [rm("rv.n3->n4"), adde("rv", "n3", "n2", None, 0.2), rm("rv.n4->zz", 0.4), adde("rv", "n4", "n3", None, 0.5), pt("pv", "rv.n4", 0.7), pt("cu", "rv.zz", 0.8)])
s.step("curr is null, so the loop stops. prev, at 4, is the new head: 4, 3, 2, 1. One pass, Theta of n time, and Theta of 1 extra space.", [mk("rv.n4"), s.take("save next · turn the arrow · advance")])

s.scene("cmp")
s.step("Stage 6: arrays or linked lists? Access by position: the array wins, Theta of 1 against Theta of k.", [s.head("Stage 6 of 8: arrays or linked lists?"), s.untake()] + hide("rv", "pv", "cu") + show("cmp") + [hl("cmp[0]")])
s.step("Insert or delete at the front, or after a node you already hold: the list wins, Theta of 1 against shifting.", [hl("cmp[1..=2]")])
s.step("At the end, both are Theta of 1, if the list keeps a tail pointer.", [hl("cmp[3]")])
s.step("And memory: a list pays one pointer per node, and its scattered nodes are slower for the cache. Arrays win when you mostly read; lists when you often insert and delete.", [hl("cmp[4..=5]"), s.take("read a lot: array · change a lot: list")])

s.scene("two")
s.step("Stage 7: two pointers moving at different speeds solve several classic problems. Move slow one node and fast two nodes at a time.", [s.head("Stage 7 of 8: two-pointer tricks"), s.untake()] + hide("cmp") + show("tp") + [hl("tp[0]")])
s.step("When fast reaches the end, slow is at the middle. On 1 to 7: fast visits 1, 3, 5, 7; slow visits 1, 2, 3, 4. Middle: 4.", [hl("tp[1]")])
s.step("If the list has a cycle, fast never reaches null; instead it laps slow and they meet. That is Floyd's cycle check.", [hl("tp[2]")])
s.step("And to find the k-th node from the end in one pass, start one pointer k nodes ahead and move both until the leader falls off.", [hl("tp[3]"), s.take("fast and slow: middle, cycle, k-th from end")])

s.scene("exam")
s.step("Now an exam question on 10, 20, 30, 40.", [s.head("Exam question"), s.untake()] + hide("tp") + show("q") + [hl("q[0]")])
s.step("Insert, insert, delete, then reverse and count the pointer changes, and find where the slow pointer stops on a list of 4. Pause and work it out.", [hl("q[1..=2]")])
s.step("Insert 5 at the head: point it at 10, then move head. 5, 10, 20, 30, 40.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Insert 25 after 20: new dot next is 30, then 20 dot next is the new node.", [hl("qa[1]")])
s.step("Delete 30: stand at 25, and set its next to 40. 5, 10, 20, 25, 40.", [hl("qa[2]")])
s.step("b: reversing turns every node's next round: 5 pointer changes, plus head. 40, 25, 20, 10, 5.", [hl("qa[3]"), mk("qa[3][2]", 0.4)])
s.step("c: on 1, 2, 3, 4, fast goes 1, then 3, then off the end; slow goes 1, 2, 3. It stops at 3, the second of the two middle nodes.", [hl("qa[4]")])
s.step("The usual slip: in insertion, changing p dot next before saving where it pointed. Link the new node first.", [s.take("link the new node before breaking the old link")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A node holds data and a next pointer, and head is the way in. Walking is Theta of n, but inserting and deleting next to a known node is Theta of 1.", [hl("stages[0..=3]")])
s.step("Three pointers reverse a list in one pass. Arrays win at reading, lists at changing, and fast and slow pointers find middles and cycles.", [hl("stages[4..=6]")])
s.step("Next video: lists with two pointers per node, lists that loop back, and two applications: polynomials and a music playlist.", [mk("stages[0..=7]"), s.take("Next: doubly and circular lists")])

s.save("/home/claude/playlist/dsa1/d1v9.json")

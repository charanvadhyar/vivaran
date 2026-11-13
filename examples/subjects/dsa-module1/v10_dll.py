"""DSA Module 1, video 10: doubly and circular lists, polynomials, the playlist lab."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *

def padd(p, q):
    i = j = 0; out = []; steps = []
    while i < len(p) and j < len(q):
        (a, ea), (b, eb) = p[i], q[j]
        if ea == eb:
            if a + b: out.append((a + b, ea))
            steps.append(("=", ea)); i += 1; j += 1
        elif ea > eb: out.append(p[i]); steps.append(("p", ea)); i += 1
        else: out.append(q[j]); steps.append(("q", eb)); j += 1
    out += p[i:] + q[j:]
    return out, steps
R, S = padd([(3, 14), (2, 8), (1, 0)], [(8, 14), (-3, 10), (10, 6)])
assert R == [(11, 14), (-3, 10), (2, 8), (10, 6), (1, 0)] and S == [("=", 14), ("q", 10), ("p", 8), ("q", 6)]
R2, _ = padd([(5, 4), (3, 2), (-7, 0)], [(2, 5), (-3, 2), (4, 1), (7, 0)])
assert R2 == [(2, 5), (5, 4), (4, 1)]
pl = []
for x in ("S1", "S2", "S3"): pl.insert(0, x)
pl.remove("S2"); assert pl == ["S3", "S1"]

s = Script("Doubly and circular lists")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Doubly linked lists"],
    [2, "Inserting and deleting both ways"],
    [3, "Circular lists"],
    [4, "Header nodes and sentinels"],
    [5, "Polynomials as lists"],
    [6, "Adding two polynomials"],
    [7, "The playlist lab"],
    [8, "Exam question"]]})
G = lambda i, l, c, r=1, sh=None: {"id": i, "label": l, "at": [c, r], **({"shape": sh} if sh else {})}
E = lambda a, b: {"from": a, "to": b}
s.obj({"id": "dl", "type": "diagram", "region": "center", "layout": "grid", "nodes": [
    G("hd", "head", 0, 1, "pill"), G("a", "A", 2), G("b", "B", 4), G("c", "C", 6), G("d", "D", 8)],
    "edges": [E("hd", "a"), E("a", "b"), E("b", "a"), E("b", "c"), E("c", "b"), E("c", "d"), E("d", "c")]})
s.obj({"id": "dt", "type": "table", "region": "center", "columns": ["a doubly linked node", ""], "rows": [
    ["prev · data · next", "a pointer each way"],
    ["walk backwards", "as easily as forwards"],
    ["delete a node you hold", "Θ(1): no need to find its predecessor"],
    ["the price", "two pointers per node, four to update on insert"]]})
s.obj({"id": "dc", "type": "code", "region": "center", "language": "text", "lines": [
    "INSERT-AFTER(b, x)            // put x between b and c = b.next",
    "    x.prev = b;   x.next = b.next",
    "    b.next.prev = x",
    "    b.next = x",
    "",
    "DELETE(x)",
    "    x.prev.next = x.next",
    "    x.next.prev = x.prev"]})
s.obj({"id": "cl", "type": "diagram", "region": "center", "layout": "ring", "nodes": [
    {"id": "p1", "label": "P1"}, {"id": "p2", "label": "P2"}, {"id": "p3", "label": "P3"}, {"id": "p4", "label": "P4"}, {"id": "last", "label": "last", "shape": "pill"}],
    "edges": [E("p1", "p2"), E("p2", "p3"), E("p3", "p4"), E("p4", "p1"), E("last", "p4")]})
s.obj({"id": "ct", "type": "table", "region": "center", "columns": ["circular singly linked list", ""], "rows": [
    ["the last node points back to the first", "no null anywhere"],
    ["keep a pointer to the last node", "then last.next is the first"],
    ["insert at the front or the end", "Θ(1) both"],
    ["used for", "round-robin scheduling, repeating playlists, turn-taking"]]})
s.obj({"id": "sn", "type": "table", "region": "center", "columns": ["header node (sentinel)", ""], "rows": [
    ["a dummy node that is always there", "holds no data"],
    ["circular doubly linked with a sentinel", "Cormen's L.nil: nil.next is the first, nil.prev the last"],
    ["an empty list", "nil.next = nil.prev = nil"],
    ["why", "inserting or deleting at either end is no longer a special case"]]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["a polynomial as a list", ""], "rows": [
    ["one node per non-zero term", "coefficient · exponent · next"],
    ["kept in decreasing exponent order", "3x¹⁴ + 2x⁸ + 1 → (3,14) → (2,8) → (1,0)"],
    ["why not an array of coefficients?", "x¹⁰⁰⁰ + 1 would need 1001 cells for 2 terms"]]})
s.obj({"id": "pa", "type": "array", "region": "center", "values": ["3x¹⁴", "2x⁸", "1"]})
s.obj({"id": "qa2", "type": "array", "region": "center", "values": ["8x¹⁴", "−3x¹⁰", "10x⁶"]})
s.obj({"id": "ra", "type": "array", "region": "center", "values": []})
s.obj({"id": "lab", "type": "table", "region": "center", "columns": ["playlist requirement", "list operation"], "rows": [
    ["the newest song plays first", "insert at the head: Θ(1)"],
    ["delete a song", "find it, then unlink it"],
    ["next and previous buttons", "doubly linked: follow next or prev"],
    ["repeat all", "circular: the last song links back to the first"],
    ["add S1, S2, S3, then delete S2", "S3 → S1"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) in the doubly linked list A ⇄ B ⇄ C ⇄ D, which pointers change to delete C?"],
    ["b) add 5x⁴ + 3x² − 7 and 2x⁵ − 3x² + 4x + 7 using lists"],
    ["c) a circular list keeps only a pointer to its last node: how do you insert at the front?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "C.prev.next = C.next;  C.next.prev = C.prev", "B.next = D, D.prev = B"],
    ["b", "x⁵: only in Q · x⁴: only in P · x²: 3 − 3 = 0, dropped", ""],
    ["b", "x: only in Q · constant: −7 + 7 = 0, dropped", "2x⁵ + 5x⁴ + 4x"],
    ["c", "x.next = last.next;  last.next = x", "last stays put; x is the new first"]]})

s.scene("intro")
s.step("A singly linked list only goes forward, and deleting a node needs the one before it. Adding a second pointer, or joining the ends into a ring, fixes that. This video covers those variants, and two applications: polynomials and a music playlist.", [s.head("Doubly and circular lists")])
s.step("Here are the eight stages.", show("stages"))
s.step("Doubly linked lists, inserting and deleting in them, circular lists, and sentinel nodes.", [hl("stages[0..=3]")])
s.step("Then polynomials as lists, adding two of them, the playlist lab, and an exam question.", [hl("stages[4..=7]")])

s.scene("dll")
s.step("Stage 1: each node of a doubly linked list has two pointers: prev to the node before, next to the node after.", [s.head("Stage 1 of 8: doubly linked lists")] + hide("stages") + show("dl") + [hl("dl.b")])
s.step("So the list can be walked backwards as easily as forwards.", hide("dl") + show("dt") + [hl("dt[0..=1]")])
s.step("And a node you already hold can be deleted in Theta of 1, because it knows its own predecessor.", [hl("dt[2]")])
s.step("The price: two pointers per node, and four pointer updates on every insert.", [hl("dt[3]"), s.take("prev + next: both directions, Θ(1) delete")])

s.scene("ops")
s.step("Stage 2: insert x after B, between B and C. First set x's own pointers: prev to B, next to C.", [s.head("Stage 2 of 8: inserting and deleting"), s.untake()] + hide("dt") + show("dc") + [ml("dc", 1, 2)])
s.step("Then make C point back to x, and B point forward to x. Four assignments, in an order that never loses C.", [ml("dc", 3, 4)])
s.step("Deleting x needs just two: x's predecessor skips forward over it, and x's successor skips back over it.", [ml("dc", 6, 8)])
s.step("To insert before a node instead, use its prev as b. No walk is needed in either direction.", [ml("dc", 1, 4)])
s.step("In a singly linked list, deleting needs a walk to find the predecessor. Here it comes for free.", [s.take("insert: 4 pointer changes · delete: 2")])

s.scene("circ")
s.step("Stage 3: in a circular list, the last node points back to the first. There is no null.", [s.head("Stage 3 of 8: circular lists"), s.untake()] + hide("dc") + show("cl") + [hl("cl.p4->p1")])
s.step("Keep one pointer, to the last node. Then the first node is just last dot next.", [hl("cl.last")])
s.step("So inserting at either end is Theta of 1: link the new node after last, and to insert at the end, also move last to it.", hide("cl") + show("ct") + [hl("ct[1..=2]")])
s.step("One trap: walking a circular list never meets null. Start at the first node and stop when you come back to it, which is why the loop is usually written as do, then while.", [hl("ct[0]")])
s.step("Circular lists suit anything that takes turns: round-robin CPU scheduling, players in a game, or a playlist on repeat.", [hl("ct[3]"), s.take("circular: last.next = first")])

s.scene("sent")
s.step("Stage 4: a header node, or sentinel, is a dummy node that is always present and holds no data.", [s.head("Stage 4 of 8: sentinels"), s.untake()] + hide("ct") + show("sn") + [hl("sn[0]")])
s.step("Cormen's lists are circular, doubly linked, with a sentinel called nil. nil dot next is the first node, nil dot prev the last.", [hl("sn[1]")])
s.step("An empty list is just the sentinel pointing to itself.", [hl("sn[2]")])
s.step("The pay-off: every real node always has a node on both sides, so inserting or deleting at either end is no longer a special case. The code has no if statements for empty lists or heads.", [hl("sn[3]"), s.take("sentinel: no special cases")])

s.scene("poly")
s.step("Stage 5: a polynomial as a linked list. One node per non-zero term, holding the coefficient and the exponent.", [s.head("Stage 5 of 8: polynomials as lists"), s.untake()] + hide("sn") + show("pr") + [hl("pr[0]")])
s.step("Terms are kept in decreasing order of exponent. 3x to the 14, plus 2x to the 8, plus 1, is three nodes.", [hl("pr[1]")])
s.step("An array indexed by exponent would need 1001 cells for x to the 1000 plus 1. The list needs 2 nodes.", [hl("pr[2]"), s.take("store only non-zero terms, highest exponent first")])

s.scene("add")
s.step("Stage 6: add P, 3x to the 14 plus 2x to the 8 plus 1, and Q, 8x to the 14 minus 3x to the 10 plus 10x to the 6. Walk both lists together, like merging.", [s.head("Stage 6 of 8: adding polynomials"), s.untake()] + hide("pr") + show("pa", "qa2", "ra"))
s.step("Top row: P. Middle row: Q. Bottom row: the sum, built from the front. At each step compare the exponents at the front of what is left.", [hl("pa[0]"), hl("qa2[0]", 0.2)])
s.step("Both fronts have exponent 14: add the coefficients, 3 plus 8 is 11. Output 11x to the 14, and advance both.", [cmp("pa[0]", "qa2[0]"), ins("ra", 0, "11x¹⁴", 0.4)])
s.step("8 against 10: Q's exponent is larger, so copy minus 3x to the 10 and advance q.", [cmp("pa[1]", "qa2[1]"), ins("ra", 1, "−3x¹⁰", 0.4)])
s.step("8 against 6: copy 2x to the 8 from P and advance p.", [cmp("pa[1]", "qa2[2]"), ins("ra", 2, "2x⁸", 0.4)])
s.step("0 against 6: copy 10x to the 6. Q is used up, so copy the rest of P: plus 1.", [cmp("pa[2]", "qa2[2]"), ins("ra", 3, "10x⁶", 0.3), ins("ra", 4, "1", 0.6)])
s.step("11x to the 14, minus 3x to the 10, plus 2x to the 8, plus 10x to the 6, plus 1. Each term is looked at once: Theta of m plus n. If coefficients cancel to 0, that term is simply not output.", [mk("ra[0..=4]"), s.take("merge by exponent: Θ(m + n)")])

s.scene("lab")
s.step("Stage 7: the lab's playlist, where the most recently added song must always come first. That is insertion at the head: Theta of 1, like a stack.", [s.head("Stage 7 of 8: the playlist lab"), s.untake()] + hide("pa", "qa2", "ra") + show("lab") + [hl("lab[0]")])
s.step("Deleting a song: find it by walking, then unlink it.", [hl("lab[1]")])
s.step("Next and previous buttons want both directions: a doubly linked list.", [hl("lab[2]")])
s.step("Repeat-all wants the last song to lead back to the first: make it circular.", [hl("lab[3]")])
s.step("Add S1, S2 and S3: each goes to the front, so the list is S3, S2, S1. Delete S2: S3, then S1.", [hl("lab[4]"), s.take("newest first = insert at head")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("lab") + show("q") + [hl("q[0]")])
s.step("Delete a node from a doubly linked list, add two polynomials as lists, and insert at the front of a circular list. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: C's predecessor B must skip to D, and D must point back to B. B dot next becomes D, D dot prev becomes B.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: x to the 5 is only in the second: copy 2x to the 5. x to the 4 is only in the first: 5x to the 4.", [hl("qa[1]")])
s.step("x squared: 3 minus 3 is 0, so no node. x: 4x. Constants: minus 7 plus 7, 0 again. The sum: 2x to the 5, plus 5x to the 4, plus 4x.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("c: point the new node at last dot next, the current first node, then set last dot next to the new node. last itself does not move.", [hl("qa[3]")])
s.step("The usual slip in polynomial addition: keeping a term whose coefficients cancel to zero.", [s.take("drop zero-coefficient terms")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Doubly linked lists go both ways and delete a held node in Theta of 1. Circular lists loop back, so a pointer to the last node reaches both ends. Sentinels remove special cases.", [hl("stages[0..=3]")])
s.step("Polynomials are lists of non-zero terms, added by merging in Theta of m plus n, and the playlist inserts at the head.", [hl("stages[4..=6]")])
s.step("That completes Module 1. Module 2 leaves straight lines behind: trees, heaps and graphs.", [mk("stages[0..=7]"), s.take("End of Module 1")])

s.save("/home/claude/playlist/dsa1/d1v10.json")

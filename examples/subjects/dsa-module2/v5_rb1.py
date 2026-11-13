"""DSA Module 2, video 5: red-black trees, properties and insertion."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from rb import RB

def depths(sn):
    root, L, R = sn[0], sn[1], sn[2]; d = {}
    def go(x, k):
        if x is None: return
        d[x] = k; go(L.get(x), k + 1); go(R.get(x), k + 1)
    go(root, 0); return d
def rb_obj(i, sn, region="center"):
    root, L, R, col = sn; d = depths(sn); keys = sorted(d); c = {k: j for j, k in enumerate(keys)}
    return {"id": i, "type": "diagram", "region": region, "layout": "grid",
            "nodes": [{"id": f"n{k}", "label": f"{k} {col[k]}", "at": [c[k], d[k]], "shape": "circle" if col[k] == "B" else "pill"} for k in keys],
            "edges": [{"from": f"n{p}", "to": f"n{q}"} for side in (L, R) for p, q in side.items()]}

t = RB(); snaps = []; cases = []
for k in [41, 38, 31, 12, 19, 8]:
    n = len(t.log); t.insert(k); t.check(); snaps.append(t.snap()); cases.append([c[1].split(":")[0] for c in t.log[n:]])
assert cases == [[], [], ["case 3"], ["case 1"], ["case 2", "case 3"], ["case 1"]]
assert snaps[-1][0] == 38 and t.check() - 1 == 2
# pre-fix pictures: plain insert as red
def plain(sn, k):
    root, L, R, col = sn[0], dict(sn[1]), dict(sn[2]), dict(sn[3]); x = root
    while True:
        side = L if k < x else R
        if x in side: x = side[x]
        else: side[x] = k; col[k] = "R"; return (root, L, R, col)
pre31, pre12, pre19, pre8 = plain(snaps[1], 31), plain(snaps[2], 12), plain(snaps[3], 19), plain(snaps[4], 8)
e = RB(); ecases = []
for k in [5, 10, 15, 20, 25, 30]:
    n = len(e.log); e.insert(k); ecases.append([c[1].split(":")[0] for c in e.log[n:]])
assert ecases == [[], [], ["case 3"], ["case 1"], ["case 3"], ["case 1"]] and e.snap()[0] == 10 and e.check() - 1 == 2
ES = e.snap()
assert ES[3] == {5: "B", 10: "B", 15: "B", 20: "R", 25: "B", 30: "R"}
assert round(2 * math.log2(10**6 + 1)) == 40

s = Script("Red-black trees 1")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Five rules"],
    [2, "Black-height, and why the tree stays short"],
    [3, "Inserting: the new node is red"],
    [4, "The three fix-up cases"],
    [5, "Inserting 41, 38, 31"],
    [6, "Inserting 12, 19, 8"],
    [7, "Red-black against AVL"],
    [8, "Exam question"]]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["red-black properties (Cormen)", ""], "rows": [
    ["1", "every node is red or black"],
    ["2", "the root is black"],
    ["3", "every leaf (nil) is black"],
    ["4", "a red node's children are both black: no two reds in a row"],
    ["5", "every path from a node down to a nil has the same number of black nodes"],
    ["in the pictures", "a node is labelled R or B"]]})
s.obj({"id": "bh", "type": "math", "region": "center", "lines": [
    "\"bh\"(x) = \"black nodes on any path from\" x \"down to a nil, not counting\" x",
    "\"a subtree rooted at\" x \"holds at least\" 2^(\"bh\"(x)) - 1 \"keys\"",
    "\"no two reds in a row:\" quad \"bh\"(\"root\") >= h / 2",
    "n >= 2^(h/2) - 1 quad => quad h <= 2 log_2(n + 1)",
    "n = 10^6: quad h <= 40"]})
s.obj({"id": "ins", "type": "table", "region": "center", "columns": ["inserting key z", ""], "rows": [
    ["insert z as in a BST", "it becomes a leaf"],
    ["colour it red", "black-heights stay equal: rule 5 is safe"],
    ["only rules 2 or 4 can break", "z is the root, or z's parent is red"],
    ["while z's parent is red", "apply one of three cases, looking at z's uncle"],
    ["finally", "colour the root black"]]})
s.obj({"id": "cs", "type": "table", "region": "center", "columns": ["case", "uncle", "fix"], "rows": [
    ["1", "red", "parent, uncle → black; grandparent → red; z = grandparent"],
    ["2", "black, z makes a bend", "rotate at the parent → case 3"],
    ["3", "black, z makes a line", "rotate at the grandparent; swap their colours"],
    ["cost", "", "case 1 may repeat; at most 2 rotations"]]})
s.obj(rb_obj("s1", snaps[1])); s.obj(rb_obj("p31", pre31)); s.obj(rb_obj("s2", snaps[2]))
s.obj(rb_obj("p12", pre12)); s.obj(rb_obj("s3", snaps[3])); s.obj(rb_obj("p19", pre19)); s.obj(rb_obj("s4", snaps[4]))
s.obj(rb_obj("p8", pre8)); s.obj(rb_obj("s5", snaps[5]))
s.obj({"id": "vs", "type": "table", "region": "center", "columns": ["", "AVL", "red-black"], "rows": [
    ["height bound", "1.44 log₂ n", "2 log₂ n"],
    ["searches", "slightly faster", "slightly slower"],
    ["rotations per insert", "at most 2", "at most 2"],
    ["rotations per delete", "up to O(log n)", "at most 3"],
    ["extra data per node", "height or balance factor", "one colour bit"],
    ["used in", "lookup-heavy tables", "C++ map, Java TreeMap, Linux scheduler"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["insert 5, 10, 15, 20, 25, 30 into an empty red-black tree"],
    ["a) which fix-up case does each insertion need?"],
    ["b) the final tree with colours, and the root's black-height"],
    ["c) how tall would a plain BST be with the same insertions?"]]})
s.obj(rb_obj("qt", ES, "left"))
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["insert", "case"], "rows": [
    ["5, 10", "none: root black, 10 red"],
    ["15", "3: left-rotate 5, recolour"],
    ["20", "1: recolour; root back to black"],
    ["25", "3: left-rotate 15, recolour"],
    ["30", "1: recolour"],
    ["bh(root)", "2 · plain BST height 5"]]})

s.scene("intro")
s.step("AVL trees balance by heights. Red-black trees balance more loosely, by colouring every node red or black and keeping a few rules about the colours. They rotate less, and they sit inside the C plus plus map, Java's TreeMap and the Linux scheduler. This video covers their rules and insertion.", [s.head("Red-black trees, part 1")])
s.step("Here are the eight stages.", show("stages"))
s.step("The five rules, black-height and the height bound, inserting a red node, and the three fix-up cases.", [hl("stages[0..=3]")])
s.step("Then a full worked insertion sequence, a comparison with AVL trees, and an exam question.", [hl("stages[4..=7]")])

s.scene("rules")
s.step("Stage 1: Cormen's five properties. Every node is red or black.", [s.head("Stage 1 of 8: five rules")] + hide("stages") + show("pr") + [hl("pr[0]")])
s.step("The root is black. Every leaf is black, where the leaves are the nil pointers below the real nodes.", [hl("pr[1..=2]")])
s.step("A red node has two black children: there are never two reds in a row on a path.", [hl("pr[3]")])
s.step("And every path from a node down to a nil passes the same number of black nodes.", [hl("pr[4]")])
s.step("These pictures have no colour, so each node is labelled R or B, and red nodes are drawn as rounded boxes.", [hl("pr[5]"), s.take("root black · no red-red · equal black counts")])

s.scene("bh")
s.step("Stage 2: the black-height of a node is the number of black nodes on any path from it down to a nil, not counting itself. Rule 5 makes this well defined.", [s.head("Stage 2 of 8: black-height"), s.untake()] + hide("pr") + show("bh") + [hl("bh[0]")])
s.step("By induction, a subtree whose root has black-height b holds at least 2 to the b, minus 1, keys.", [rv("bh[1]"), hl("bh[1]")])
s.step("Reds never come two in a row, so at least half the nodes on any root-to-leaf path are black: the root's black-height is at least h over 2.", [rv("bh[2]"), hl("bh[2]")])
s.step("Put them together: n is at least 2 to the h over 2, minus 1, so h is at most 2 log 2 of n plus 1.", [rv("bh[3]"), hl("bh[3]")])
s.step("A million keys: height at most 40. Looser than AVL's 29, but still logarithmic.", [rv("bh[4]"), hl("bh[4]"), s.take("h ≤ 2 log₂(n + 1)")])

s.scene("ins")
s.step("Stage 3: to insert, first insert as in an ordinary BST: the new key becomes a leaf.", [s.head("Stage 3 of 8: the new node is red"), s.untake()] + hide("bh") + show("ins") + [hl("ins[0]")])
s.step("Colour it red. A red node adds no black to any path, so rule 5 cannot break.", [hl("ins[1]")])
s.step("Only two things can go wrong: the new node is the root, which must be black, or its parent is also red.", [hl("ins[2]")])
s.step("While the parent is red, apply one of three cases. The deciding node is the uncle: the parent's sibling. At the end, colour the root black.", [hl("ins[3..=4]"), s.take("insert red · fix red-red using the uncle")])

s.scene("cases")
s.step("Stage 4: case 1, the uncle is red. Recolour: parent and uncle become black, the grandparent becomes red. No rotation. But the grandparent may now have a red parent, so move up and check again.", [s.head("Stage 4 of 8: the three cases"), s.untake()] + hide("ins") + show("cs") + [hl("cs[0]")])
s.step("Case 2, the uncle is black and the new node is an inner child: a bend, like left then right. Rotate at the parent to straighten it, which turns it into case 3.", [hl("cs[1]")])
s.step("Case 3, the uncle is black and the new node is an outer child: a line. Rotate at the grandparent, and swap the colours of the parent and the grandparent. Done.", [hl("cs[2]")])
s.step("Case 1 may climb the tree, but costs only recolouring. Cases 2 and 3 finish the job, so an insertion needs at most two rotations.", [hl("cs[3]"), s.take("uncle red: recolour · uncle black: rotate")])

s.scene("ex1")
s.step("Stage 5: Cormen's exercise: insert 41, 38, 31, 12, 19, 8. 41 is the root: black. 38 goes left of it, red. No rule is broken.", [s.head("Stage 5 of 8: inserting 41, 38, 31"), s.untake()] + hide("cs") + show("s1"))
s.step("31 goes left of 38: red under red. The uncle, 41's right child, is nil, which counts as black. 31, 38, 41 form a line: case 3.", hide("s1") + show("p31") + [hl("p31.n31"), hl("p31.n38", 0.3)])
s.step("Right-rotate at 41, and swap colours: 38 becomes the black root, with red 31 and red 41 below it.", hide("p31") + show("s2") + [mk("s2.n38")])
s.step("Insert 12, left of 31: red under red again. This time the uncle, 41, is red: case 1.", hide("s2") + show("p12") + [hl("p12.n12"), hl("p12.n41", 0.4)])
s.step("Recolour: 31 and 41 become black, 38 becomes red. 38 is the root, so it is coloured black again. Every path now has the same black count.", hide("p12") + show("s3") + [mk("s3.n31"), mk("s3.n41", 0.2)])

s.scene("ex2")
s.step("Stage 6: insert 19: left of 38, left of 31, right of 12. Red under red, and the uncle, 31's right child, is nil: black.", [s.head("Stage 6 of 8: inserting 12, 19, 8"), s.untake()] + hide("s3") + show("p19") + [hl("p19.n19"), hl("p19.n12", 0.3)])
s.step("19 is a right child of a left child: a bend, case 2. Left-rotate at 12, so 12 hangs below 19 in a straight line. Now case 3 applies with 12 as the new node.", [hl("p19.n31")])
s.step("Right-rotate at 31 and swap colours: 19 becomes black, with red 12 and red 31 as children.", hide("p19") + show("s4") + [mk("s4.n19")])
s.step("Insert 8, left of 12: red under red, and the uncle 31 is red: case 1. 12 and 31 turn black, 19 turns red. Its parent 38 is black, so we stop.", hide("s4") + show("p8") + [hl("p8.n8"), hl("p8.n31", 0.4)])
s.step("The final tree: 38 black at the root; 19 red with black children 12 and 31; 8 red under 12; 41 black. Every root-to-nil path passes 2 black nodes below the root.", hide("p8") + show("s5") + [mk("s5.n38"), s.take("case 2 straightens, case 3 rotates, case 1 recolours")])

s.scene("vs")
s.step("Stage 7: red-black against AVL. AVL trees are more tightly balanced, 1.44 log n against 2 log n, so their searches are a little faster.", [s.head("Stage 7 of 8: red-black against AVL"), s.untake()] + hide("s5") + show("vs") + [hl("vs[0..=1]")])
s.step("Both need at most two rotations per insertion. But deletion can rotate at every level of an AVL tree, while a red-black tree needs at most three.", [hl("vs[2..=3]")])
s.step("A red-black node stores a single colour bit instead of a height.", [hl("vs[4]")])
s.step("So libraries that insert and delete often choose red-black trees: the C plus plus map, Java's TreeMap, and the Linux process scheduler.", [hl("vs[5]"), s.take("RB: looser balance, cheaper updates")])

s.scene("exam")
s.step("Now an exam question: insert the sorted keys 5 to 30, in steps of 5.", [s.head("Exam question"), s.untake()] + hide("vs") + show("q") + [hl("q[0]")])
s.step("Name the case each insertion needs, draw the final coloured tree with its black-height, and compare with a plain BST. Pause and work it out.", [hl("q[1..=3]")])
s.step("5 is the black root, and 10 hangs red on its right. 15 makes a red-red line with a nil uncle: case 3. Left-rotate 5; 10 becomes the black root with red children 5 and 15.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("20: right of 15, red under red, uncle 5 is red: case 1. 5 and 15 turn black, 10 turns red, then the root goes back to black.", [hl("qa[2]")])
s.step("25: a line 15, 20, 25 with a nil uncle: case 3. Left-rotate 15; 20 becomes black with red 15 and 25. 30: under 25, uncle 15 is red: case 1. 15 and 25 turn black, 20 turns red.", [hl("qa[3..=4]")])
s.step("The final tree: 10 black at the root; 5 black on its left; 20 red on its right, with black children 15 and 25; and 30 red under 25. Black-height of the root: 2. A plain BST would be a chain of height 5.", hide("qa") + show("qt", "qa") + [hl("qa[5]"), mk("qt.n10", 0.3)])
s.step("The usual slip: treating a missing uncle as red. A nil uncle is black, so it means a rotation, not a recolouring.", [s.take("nil counts as black")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt", "qa") + show("stages"))
s.step("Five colour rules give equal black-heights and no red-red pairs, which keep the height under 2 log of n plus 1. New nodes are red, so only a red-red pair can appear.", [hl("stages[0..=3]")])
s.step("A red uncle means recolour and move up; a black uncle means one or two rotations and stop. Red-black trees rotate less than AVL trees, especially on deletion.", [hl("stages[4..=6]")])
s.step("Next video: deleting from a red-black tree, and the double-black node.", [mk("stages[0..=7]"), s.take("Next: red-black trees, part 2")])

s.save("/home/claude/playlist/dsa2/d2v5.json")

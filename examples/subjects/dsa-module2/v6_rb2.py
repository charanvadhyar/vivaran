"""DSA Module 2, video 6: red-black trees, deletion."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from rbd import RBT

def depths(sn):
    root, L, R = sn[0], sn[1], sn[2]; d = {}
    def go(x, k):
        if x is None: return
        d[x] = k; go(L.get(x), k + 1); go(R.get(x), k + 1)
    go(root, 0); return d
def rb_obj(i, sn, region="center", extra=None):
    root, L, R, col = sn; d = depths(sn); keys = sorted(d); c = {k: j for j, k in enumerate(keys)}
    nodes = [{"id": f"n{k}", "label": f"{k} {col[k]}", "at": [c[k], d[k]], "shape": "circle" if col[k] == "B" else "pill"} for k in keys]
    edges = [{"from": f"n{p}", "to": f"n{q}"} for side in (L, R) for p, q in side.items()]
    if extra:  # (parent key, label) of a double-black nil to draw
        pk, lab = extra; nodes.append({"id": "dbl", "label": lab, "at": [c[pk] - 1 if c[pk] > 0 else 0, d[pk] + 1], "shape": "pill"})
        edges.append({"from": f"n{pk}", "to": "dbl"})
    return {"id": i, "type": "diagram", "region": region, "layout": "grid", "nodes": nodes, "edges": edges}

A = RBT()
for k in [20, 15, 95, 85, 80, 75]: A.insert(k)
A0 = A.snap(); A.frames = []
assert A.delete(15) == ["case 1", "case 3", "case 4"] and A.check() == 3
F = {name: sn for name, sn in A.frames}
assert A0 == (20, {20: 15, 85: 80, 80: 75}, {20: 85, 85: 95}, {20: "B", 15: "B", 85: "R", 80: "B", 75: "R", 95: "B"})
assert A.snap() == (85, {85: 75, 75: 20}, {75: 80, 85: 95}, {85: "B", 75: "R", 20: "B", 80: "B", 95: "B"})
A1 = (20, {85: 80, 80: 75}, {20: 85, 85: 95}, {20: "B", 85: "R", 80: "B", 75: "R", 95: "B"})
E = RBT()
for k in [41, 38, 31, 12, 19, 8]: E.insert(k)
E0 = E.snap(); evs = [E.delete(k) for k in (8, 12, 19)]
assert evs == [["removed a red node: nothing to fix"], ["case 2", "x is red: colour it black"], ["x is red: colour it black"]]
assert E.snap() == (38, {38: 31}, {38: 41}, {38: "B", 31: "B", 41: "B"})

s = Script("Red-black trees 2")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Delete as in a BST"],
    [2, "When nothing needs fixing"],
    [3, "The double-black node"],
    [4, "Four cases, by the sibling"],
    [5, "A deletion that needs cases 1, 3 and 4"],
    [6, "Costs and summary"],
    [7, "Exam question"]]})
s.obj({"id": "st", "type": "table", "region": "center", "columns": ["deleting key z", ""], "rows": [
    ["0 or 1 child", "z itself is removed; its child (or nil) x takes its place"],
    ["2 children", "z's successor y takes z's place and z's colour; y is what leaves its old spot"],
    ["the node that really left", "decides everything: call its colour the removed colour"],
    ["removed colour red", "no black count changed, no red-red created: done"],
    ["removed colour black", "every path through x lost one black: fix it"]]})
s.obj({"id": "db", "type": "table", "region": "center", "columns": ["the node x that took its place", ""], "rows": [
    ["x is red", "colour it black: the lost black is restored, done"],
    ["x is the root", "the whole tree lost one black evenly: done"],
    ["otherwise", "x is 'double black': it must count as two blacks"],
    ["the fix", "push the extra black up, or rotate it away, using x's sibling w"]]})
s.obj({"id": "cs", "type": "table", "region": "center", "columns": ["case", "sibling w", "fix"], "rows": [
    ["1", "red", "rotate at the parent, swap colours: w becomes black → case 2, 3 or 4"],
    ["2", "black, both children black", "colour w red; the extra black moves up to the parent"],
    ["3", "black, near child red, far child black", "rotate at w, swap colours → case 4"],
    ["4", "black, far child red", "rotate at the parent, recolour: the extra black disappears. Done"]]})
s.obj(rb_obj("a0", A0)); s.obj(rb_obj("a1", A1, extra=(20, "x: double black")))
s.obj(rb_obj("f1", F["case 1"], extra=(20, "x"))); s.obj(rb_obj("f3", F["case 3"], extra=(20, "x"))); s.obj(rb_obj("f4", F["case 4"]))
s.obj({"id": "co", "type": "table", "region": "center", "columns": ["red-black operation", "cost"], "rows": [
    ["search", "O(log n), height ≤ 2 log₂(n + 1)"],
    ["insert", "O(log n): recolourings climb, at most 2 rotations"],
    ["delete", "O(log n): case 2 climbs, at most 3 rotations"],
    ["case 1 → case 2 ends", "the parent was red, so the climb stops at once"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: the tree from part 1 (insert 41, 38, 31, 12, 19, 8)"], "rows": [
    ["delete 8, then 12, then 19"],
    ["a) which case or rule handles each deletion?"],
    ["b) draw the final tree with colours"]]})
s.obj(rb_obj("e0", E0, "left"))
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["delete", "what happens"], "rows": [
    ["8", "red leaf: remove"],
    ["12", "case 2: 31 → R, x = 19"],
    ["", "19 is red → B"],
    ["19", "red child 31 moves up → B"],
    ["final", "38 B · 31 B · 41 B"]]})

s.scene("intro")
s.step("Inserting into a red-black tree can only create two reds in a row. Deleting is harder: removing a black node shortens some paths, breaking the equal-black rule. This video shows the idea of a double-black node, and the four cases that remove it.", [s.head("Red-black trees, part 2")])
s.step("Here are the seven stages.", show("stages"))
s.step("Deleting as in a BST, the easy outcomes, the double-black node, and four cases decided by the sibling.", [hl("stages[0..=3]")])
s.step("Then one deletion that needs three of the cases in turn, the costs, and an exam question.", [hl("stages[4..=6]")])

s.scene("bst")
s.step("Stage 1: start as in an ordinary BST. If z has at most one child, z itself is removed, and its child, or nil, takes its place. Call that node x.", [s.head("Stage 1 of 7: delete as in a BST")] + hide("stages") + show("st") + [hl("st[0]")])
s.step("If z has two children, its successor y moves into z's position and takes z's colour. Then it is y that has really left its old spot, and y's child becomes x.", [hl("st[1]")])
s.step("So what matters is the colour of the node that really disappeared from its position.", [hl("st[2]"), s.take("track the colour that left, and the node x that replaced it")])

s.scene("easy")
s.step("Stage 2: if that colour was red, nothing breaks. Black counts are unchanged, and a red node removed cannot create two reds in a row. Done.", [s.head("Stage 2 of 7: when nothing needs fixing"), s.untake(), hl("st[3]")])
s.step("If it was black, every path through x lost one black node. That breaks rule 5, and needs fixing.", [hl("st[4]")])
s.step("Two quick cases: if x is red, colour it black. The missing black is back.", hide("st") + show("db") + [hl("db[0]")])
s.step("If x is the root, every path lost one black equally, so the rule still holds. Done.", [hl("db[1]"), s.take("removed red: done · x red: paint it black")])

s.scene("dbl")
s.step("Stage 3: otherwise x is black and not the root. Cormen pretends x carries an extra black: it is double black, counting as two. That restores the counts, but breaks the rule that a node is red or black.", [s.head("Stage 3 of 7: the double-black node"), s.untake(), hl("db[2]")])
s.step("The fix moves that extra black up the tree, or rotates it away, by looking at x's sibling, w, and w's children.", [hl("db[3]"), s.take("double black: an extra black to get rid of")])

s.scene("cases")
s.step("Stage 4: case 1, the sibling w is red. Rotate at the parent and swap the colours of w and the parent. Now x has a black sibling, so one of the other cases applies.", [s.head("Stage 4 of 7: four cases"), s.untake()] + hide("db") + show("cs") + [hl("cs[0]")])
s.step("Case 2, w is black and both its children are black. Take one black off both x and w: w turns red, and the extra black moves up to the parent, which becomes the new x.", [hl("cs[1]")])
s.step("Case 3, w is black, its near child is red and its far child black. Rotate at w and swap colours, so the red child becomes the far one: that is case 4.", [hl("cs[2]")])
s.step("Case 4, w is black and its far child is red. Rotate at the parent, give w the parent's colour, and colour the parent and the far child black. The extra black is absorbed, and the fix ends.", [hl("cs[3]")])
s.step("Case 2 may climb towards the root. The others end within three rotations at most.", [s.take("sibling red: 1 · black, black kids: 2 · near red: 3 · far red: 4")])

s.scene("ex")
s.step("Stage 5: this tree: 20 black at the root; 15 black on the left; 85 red on the right, with black children 80 and 95; and 75 red under 80. Delete 15.", [s.head("Stage 5 of 7: cases 1, 3 and 4"), s.untake()] + hide("cs") + show("a0") + [hl("a0.n15")])
s.step("15 is a black leaf. Its place is taken by nil, which is now double black. Its sibling, 85, is red: case 1.", hide("a0") + show("a1") + [hl("a1.dbl"), hl("a1.n85", 0.4)])
s.step("Left-rotate at 20 and swap the colours of 20 and 85. 85 is now the black root, 20 is red, and x's new sibling is 80, black.", hide("a1") + show("f1") + [hl("f1.n80")])
s.step("80's near child, 75, is red, and its far child is nil, black: case 3. Right-rotate at 80, and swap colours: 75 turns black, 80 red.", hide("f1") + show("f3") + [hl("f3.n75")])
s.step("Now x's sibling 75 is black with a red far child, 80: case 4. Left-rotate at 20. 75 takes the parent's colour, red; 20 and 80 turn black.", hide("f3") + show("f4") + [hl("f4.n75")])
s.step("Done. 85 black at the root; 75 red with black children 20 and 80; 95 black. Every path from the root to a nil passes 3 black nodes, counting the nil.", [mk("f4.n85"), s.take("1 → 3 → 4: three rotations, then stop")])

s.scene("cost")
s.step("Stage 6: costs. Search, insert and delete are all O of log n, because the height is at most 2 log of n plus 1.", [s.head("Stage 6 of 7: costs"), s.untake()] + hide("f4") + show("co") + [hl("co[0]")])
s.step("Insertion recolours up the tree, with at most 2 rotations. Deletion's case 2 climbs, with at most 3 rotations in all.", [hl("co[1..=2]")])
s.step("And when case 1 leads to case 2, the parent is red, so the climb ends at once. That bounded number of rotations is why libraries prefer red-black trees for data that changes often.", [hl("co[3]"), s.take("delete: O(log n), at most 3 rotations")])

s.scene("exam")
s.step("Now an exam question, on the tree built in part 1.", [s.head("Exam question"), s.untake()] + hide("co") + show("q") + [hl("q[0]")])
s.step("Delete 8, then 12, then 19, naming the case each time, and draw the final tree. Pause and work it out.", [hl("q[1..=2]")])
s.step("The tree: 38 black; 19 red with black children 12 and 31; 8 red under 12; 41 black.", hide("q") + show("e0", "qa"))
s.step("Delete 8: a red leaf. Removing red breaks nothing.", [hl("e0.n8"), hl("qa[0]", 0.3)])
s.step("Delete 12: a black leaf, so x is a double-black nil. Its sibling 31 is black with no red children: case 2. 31 turns red, and the extra black moves up to 19.", [hl("e0.n12"), hl("qa[1]", 0.3)])
s.step("19 is red, so colour it black, and the fix ends.", [hl("qa[2]")])
s.step("Delete 19: it is black, with one child, 31, which is red. 31 takes its place and is coloured black. The final tree is 38, with black children 31 and 41.", [hl("qa[3..=4]"), mk("qa[4][1]", 0.5)])
s.step("The usual slip: running the four cases when the node removed was red. Check the removed colour first.", [s.take("removed red → nothing to do")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("e0", "qa") + show("stages"))
s.step("Delete as in a BST, and track the colour that left. Red: done. Black: x is painted black if red, or carries an extra black.", [hl("stages[0..=2]")])
s.step("The sibling decides: red, rotate; black with black children, push the black up; near child red, rotate at the sibling; far child red, rotate and finish. All O of log n.", [hl("stages[3..=5]")])
s.step("Next video: a tree with many keys per node, built for disks. The B-tree.", [mk("stages[0..=6]"), s.take("Next: B-trees")])

s.save("/home/claude/playlist/dsa2/d2v6.json")

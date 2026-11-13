"""DSA Module 2, video 4: AVL trees."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from avl import AVL, snap, depths

def bst_add(sn, k):
    root, L, R = sn[0], dict(sn[1]), dict(sn[2])
    if root is None: return (k, L, R)
    x = root
    while True:
        side = L if k < x else R
        if x in side: x = side[x]
        else: side[x] = k; return (root, L, R)
def hgt(sn):
    d = depths(sn); return max(d.values())
def bfs(sn):
    root, L, R = sn
    def h(x): return -1 if x is None else 1 + max(h(L.get(x)), h(R.get(x)))
    return {x: h(L.get(x)) - h(R.get(x)) for x in depths(sn)}

t = AVL(); states = []
for k in [10, 20, 30, 40, 50, 25]:
    before = snap(t.root); pre = bst_add(before, k); r = t.insert(k); states.append((k, pre, r, snap(t.root)))
assert [s[2] for s in states] == [None, None, ("RR", 10), None, ("RR", 30), ("RL", 20)]
assert states[-1][3] == (30, {30: 20, 20: 10}, {20: 25, 30: 40, 40: 50})
assert bfs(states[2][1])[10] == -2 and bfs(states[4][1])[30] == -2 and bfs(states[5][1])[20] == -2 and bfs(states[5][1])[40] == 1
e = AVL(); log = []
for k in [50, 20, 60, 10, 8, 15, 32, 46, 11, 48]:
    r = e.insert(k)
    if r: log.append((k,) + r)
assert log == [(8, "LL", 20), (15, "LR", 50), (48, "RR", 32)] and snap(e.root)[0] == 20 and e.root.h == 3
EF = snap(e.root)
Nm = [1, 2]
for _ in range(4): Nm.append(Nm[-1] + Nm[-2] + 1)
assert Nm == [1, 2, 4, 7, 12, 20] and round(1.44 * math.log2(1_000_000)) == 29

def tree_obj(i, sn, region="center", hi=None):
    root, L, R = sn; d = depths(sn); keys = sorted(d); col = {k: j for j, k in enumerate(keys)}
    return {"id": i, "type": "diagram", "region": region, "layout": "grid",
            "nodes": [{"id": f"n{k}", "label": str(k), "at": [col[k], d[k]], "shape": "circle"} for k in keys],
            "edges": [{"from": f"n{p}", "to": f"n{c}"} for side in (L, R) for p, c in side.items()]}

s = Script("AVL trees")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The balance factor"],
    [2, "Why AVL trees stay short"],
    [3, "Single rotations"],
    [4, "Double rotations"],
    [5, "Inserting 10, 20, 30"],
    [6, "Inserting 40, 50, 25"],
    [7, "Deleting, and the costs"],
    [8, "Exam question"]]})
s.obj({"id": "bf", "type": "table", "region": "center", "columns": ["AVL tree (Adelson-Velsky and Landis, 1962)", ""], "rows": [
    ["balance factor of a node", "height(left subtree) − height(right subtree)"],
    ["height of an empty subtree", "−1, so a leaf has height 0"],
    ["the AVL rule", "every node's balance factor is −1, 0 or +1"],
    ["after an insert or delete", "if some node reaches ±2, rotate to repair it"]]})
s.obj({"id": "hb", "type": "math", "region": "center", "lines": [
    "N(h) = \"fewest nodes in an AVL tree of height\" h",
    "N(h) = N(h - 1) + N(h - 2) + 1, quad N(0) = 1, N(1) = 2",
    "N: quad 1, 2, 4, 7, 12, 20, dots quad \"(Fibonacci-like: grows like\" 1.618^h \")\"",
    "\"so\" h < 1.44 log_2(n + 2) quad n = 10^6: quad h <= 29 \"instead of up to\" 999999"]})
s.obj({"id": "rt", "type": "table", "region": "center", "columns": ["case", "new key went into", "fix"], "rows": [
    ["LL", "the left subtree of the left child", "one right rotation at the unbalanced node"],
    ["RR", "the right subtree of the right child", "one left rotation"],
    ["LR", "the right subtree of the left child", "left-rotate the child, then right-rotate the node"],
    ["RL", "the left subtree of the right child", "right-rotate the child, then left-rotate the node"],
    ["after the fix", "the subtree has its old height again", "nothing above it changes: at most 2 rotations per insert"]]})
s.obj({"id": "rr", "type": "code", "region": "center", "language": "text", "lines": [
    "LEFT-ROTATE(x)                 // x is too heavy on the right",
    "    y = x.right",
    "    x.right = y.left           // y's left subtree moves across to x",
    "    y.left = x                 // x becomes y's left child",
    "    update heights of x, then y; y takes x's place",
    "",
    "keys in order before and after:  x < y.left < y  — unchanged"]})
for i, (k, pre, r, post) in enumerate(states):
    if i >= 1: s.obj(tree_obj(f"pre{i}", pre))
    if r: s.obj(tree_obj(f"post{i}", post))
s.obj({"id": "co", "type": "table", "region": "center", "columns": ["operation on an AVL tree of n keys", "cost"], "rows": [
    ["search", "O(log n): the height is at most 1.44 log₂ n"],
    ["insert", "O(log n) walk + at most one single or double rotation"],
    ["delete", "O(log n) walk + up to O(log n) rotations, one per level"],
    ["the price", "a height (or balance factor) stored in every node"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["insert 50, 20, 60, 10, 8, 15, 32, 46, 11, 48 into an empty AVL tree"],
    ["a) after which insertions is a rotation needed, of which kind, at which node?"],
    ["b) draw the final tree and give its height"]]})
s.obj(tree_obj("qt", EF, "left"))
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["insert", "unbalanced at", "case"], "rows": [
    ["8", "20 (bf +2)", "LL: right-rotate 20"],
    ["15", "50 (bf +2)", "LR: left-rotate 10, right-rotate 50"],
    ["48", "32 (bf −2)", "RR: left-rotate 32"],
    ["final", "root 20", "height 3"]]})

s.scene("intro")
s.step("A binary search tree is fast only while it stays short, and sorted input makes it a chain. The AVL tree, the first self-balancing tree, checks its balance after every change and repairs it with rotations. This video shows how.", [s.head("AVL trees")])
s.step("Here are the eight stages.", show("stages"))
s.step("The balance factor, why AVL trees stay short, and single and double rotations.", [hl("stages[0..=3]")])
s.step("Then two worked insertion sequences, deletion and costs, and an exam question.", [hl("stages[4..=7]")])

s.scene("bf")
s.step("Stage 1: the balance factor of a node is the height of its left subtree minus the height of its right subtree.", [s.head("Stage 1 of 8: the balance factor")] + hide("stages") + show("bf") + [hl("bf[0]")])
s.step("An empty subtree has height minus 1, so a leaf has height 0 and balance factor 0.", [hl("bf[1]")])
s.step("An AVL tree keeps every node's balance factor at minus 1, 0 or plus 1: the two subtrees of any node differ in height by at most one.", [hl("bf[2]")])
s.step("An insertion or deletion can push some node to plus or minus 2. Then a rotation restores the rule.", [hl("bf[3]"), s.take("balance factor ∈ {−1, 0, +1} at every node")])

s.scene("height")
s.step("Stage 2: why does this keep the tree short? Ask the opposite: what is the fewest nodes an AVL tree of height h can have?", [s.head("Stage 2 of 8: why AVL trees stay short"), s.untake()] + hide("bf") + show("hb") + [hl("hb[0]")])
s.step("The sparsest tree of height h has a root, one subtree of height h minus 1, and one of height h minus 2, both as sparse as possible.", [rv("hb[1]"), hl("hb[1]")])
s.step("That gives 1, 2, 4, 7, 12, 20: a Fibonacci-like sequence, growing exponentially in h.", [rv("hb[2]"), hl("hb[2]")])
s.step("Turn it round: the height is less than 1.44 log 2 of n plus 2. A million keys give a height of at most 29, where a plain BST could reach 999,999.", [rv("hb[3]"), hl("hb[3]"), s.take("AVL height < 1.44 log₂ n")])

s.scene("single")
s.step("Stage 3: rotations. Find the lowest node that became unbalanced, and look at where the new key went. Four cases.", [s.head("Stage 3 of 8: single rotations"), s.untake()] + hide("hb") + show("rt") + [hl("rt[0..=1]")])
s.step("LL: the key went into the left subtree of the left child. One right rotation fixes it. RR is the mirror image: one left rotation.", [hl("rt[0..=1]")])
s.step("A left rotation at x: y, x's right child, moves up. y's left subtree moves across to become x's right subtree. x becomes y's left child.", hide("rt") + show("rr") + [ml("rr", 1, 5)])
s.step("Only three pointers change, and the inorder order of the keys is untouched: it is still a search tree.", [ml("rr", 7, 7), s.take("rotation: 3 pointers, order kept")])

s.scene("double")
s.step("Stage 4: LR: the key went into the right subtree of the left child. One rotation is not enough; it just moves the bend to the other side.", [s.head("Stage 4 of 8: double rotations"), s.untake()] + hide("rr") + show("rt") + [hl("rt[2]")])
s.step("So first left-rotate the child, turning it into an LL case, then right-rotate the node. RL is the mirror: right-rotate the child, then left-rotate the node.", [hl("rt[2..=3]")])
s.step("After either fix, the repaired subtree has the same height it had before the insertion. So nothing above it can be unbalanced any more: an insertion needs at most one single or one double rotation.", [hl("rt[4]"), s.take("LL, RR: single · LR, RL: double")])

s.scene("ex1")
s.step("Stage 5: insert 10, 20, 30 into an empty AVL tree. 10, then 20 to its right: balance factor of 10 is minus 1, still fine.", [s.head("Stage 5 of 8: inserting 10, 20, 30"), s.untake()] + hide("rt") + show("pre1"))
s.step("Insert 30. Now 10 has an empty left subtree, height minus 1, and a right subtree of height 1: balance factor minus 2.", hide("pre1") + show("pre2") + [hl("pre2.n10")])
s.step("The key went right, then right: the RR case. Left-rotate at 10: 20 comes up as the root, with 10 and 30 as its children. Perfectly balanced.", hide("pre2") + show("post2") + [mk("post2.n20")])
s.step("Without rotations these three keys would have made a chain. Insert 40: it goes right of 30, and every balance factor is still within 1.", hide("post2") + show("pre3") + [hl("pre3.n40")])

s.scene("ex2")
s.step("Stage 6: insert 50. It goes right of 40, and now 30 has balance factor minus 2. The lowest unbalanced node is 30, not the root.", [s.head("Stage 6 of 8: inserting 40, 50, 25"), s.untake()] + hide("pre3") + show("pre4") + [hl("pre4.n30")])
s.step("RR again: left-rotate at 30. 40 takes its place, with 30 and 50 as children. The root's balance is fine again.", hide("pre4") + show("post4") + [mk("post4.n40")])
s.step("Insert 25: right of 20, left of 40, left of 30. Now the root 20 has a left subtree of height 0 and a right subtree of height 2: balance factor minus 2.", hide("post4") + show("pre5") + [hl("pre5.n20"), hl("pre5.n25", 0.4)])
s.step("The key went right of 20, then left of 40: the RL case. Right-rotate 40, bringing 30 up; then left-rotate 20. 30 becomes the root, with 20 and 40 below it.", hide("pre5") + show("post5") + [mk("post5.n30")])
s.step("Six keys inserted in a nearly sorted order, and the tree has height 2. Inorder still gives 10, 20, 25, 30, 40, 50.", [s.take("rotate at the lowest node with balance ±2")])

s.scene("cost")
s.step("Stage 7: costs. Search is O of log n, because the height is at most 1.44 log 2 n.", [s.head("Stage 7 of 8: deleting and the costs"), s.untake()] + hide("post5") + show("co") + [hl("co[0]")])
s.step("Insert walks down, then back up updating heights, and does at most one single or double rotation.", [hl("co[1]")])
s.step("Delete works like BST deletion, then walks back up; a rotation can shorten a subtree and unbalance its parent, so up to one rotation per level, O of log n.", [hl("co[2]")])
s.step("The price is a height or balance factor stored in every node, and the code to keep it up to date. Red-black trees, next, relax the rule to rotate less often.", [hl("co[3]"), s.take("every operation O(log n), guaranteed")])

s.scene("exam")
s.step("Now an exam question: ten insertions into an AVL tree.", [s.head("Exam question"), s.untake()] + hide("co") + show("q") + [hl("q[0]")])
s.step("Find each rotation, its kind and where it happens, and draw the final tree. Pause and work it out.", [hl("q[1..=2]")])
s.step("50, 20, 60 and 10 need nothing. Then 8 goes left of 10, and 20 has balance factor plus 2. Left, then left: LL. Right-rotate 20; 10 comes up, with 8 and 20.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("15: left of 50, right of 10, left of 20. Now 50 has a left subtree of height 2 and a right subtree of height 0: balance factor plus 2. Left, then right: LR. Left-rotate 10, then right-rotate 50. 20 becomes the root.", [hl("qa[1]")])
s.step("32, 46 and 11 fit without trouble. Then 48 goes right of 46, which hangs right of 32: 32 has balance factor minus 2. RR: left-rotate 32, and 46 takes its place.", [hl("qa[2]")])
s.step("The final tree: 20 at the root; 10 on its left with 8 and 15, and 11 under 15; 50 on its right, with 46, holding 32 and 48, and 60. Height 3.", hide("qa") + show("qt", "qa") + [hl("qa[3]"), mk("qt.n20", 0.3)])
s.step("The usual slip: rotating at the root instead of at the lowest unbalanced node. Always walk up from the new leaf and stop at the first node with balance plus or minus 2.", [s.take("rotate at the lowest unbalanced node")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt", "qa") + show("stages"))
s.step("Every AVL node has balance factor minus 1, 0 or 1, which keeps the height below 1.44 log n. LL and RR need one rotation; LR and RL need two.", [hl("stages[0..=3]")])
s.step("Insertions rotate at the lowest unbalanced node, at most once. Deletions may rotate on every level. Every operation is O of log n.", [hl("stages[4..=6]")])
s.step("Next video: a looser balance rule with colours instead of heights. Red-black trees.", [mk("stages[0..=7]"), s.take("Next: red-black trees")])

s.save("/home/claude/playlist/dsa2/d2v4.json")

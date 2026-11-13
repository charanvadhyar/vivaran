"""DSA Module 2, video 3: binary search trees."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from bst import build

KEYS = [50, 30, 70, 20, 40, 60, 80, 35]
t = build(KEYS); D = t.depth(); COL = {k: i for i, k in enumerate(sorted(KEYS))}
assert t.inorder() == sorted(KEYS) and t.search(35) == [50, 30, 40, 35] and t.search(65) == [50, 70, 60]
paths = {}
tt = build([])
for k in KEYS: paths[k] = tt.insert(k)
assert paths[35] == [50, 30, 40] and t.height() == 3
t2 = build(KEYS); t2.delete(20); t2.delete(40); y = t2.delete(50)
assert y == 60 and t2.root == 60 and t2.inorder() == [30, 35, 60, 70, 80]
E = build([45, 15, 79, 90, 10, 55, 12, 20, 50])
assert E.height() == 3 and E.search(12) == [45, 15, 10, 12] and E.delete(45) == 50 and E.root == 50 and E.inorder() == [10, 12, 15, 20, 50, 55, 79, 90]
S = build([10, 20, 30, 40, 50]); assert S.height() == 4

def node(k): return {"id": f"k{k}", "label": str(k), "at": [COL[k], D[k]], "shape": "circle"}
s = Script("Binary search trees")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The search-tree property"],
    [2, "Searching"],
    [3, "Inserting"],
    [4, "Minimum, maximum, successor"],
    [5, "Deleting: leaf and one child"],
    [6, "Deleting: two children"],
    [7, "Why the shape matters"],
    [8, "Exam question"]]})
s.obj({"id": "bp", "type": "table", "region": "center", "columns": ["binary search tree property", ""], "rows": [
    ["every key in x's left subtree", "< x.key"],
    ["every key in x's right subtree", "> x.key"],
    ["so an inorder traversal", "lists the keys in sorted order"],
    ["search, insert, delete, min, max, successor", "all O(h), h = the height"]]})
s.obj({"id": "bt", "type": "diagram", "region": "center", "layout": "grid", "nodes": [node(50)], "edges": []})
s.obj({"id": "sc", "type": "code", "region": "right", "language": "text", "lines": [
    "SEARCH(x, k)",
    "  while x != nil and k != x.key",
    "    if k < x.key",
    "      x = x.left",
    "    else x = x.right",
    "  return x"]})
s.obj({"id": "su", "type": "table", "region": "center", "columns": ["query", "how", "in our tree"], "rows": [
    ["minimum", "follow left pointers to the end", "20"],
    ["maximum", "follow right pointers to the end", "80"],
    ["successor of x, x has a right subtree", "the minimum of that right subtree", "succ(30) = 35"],
    ["successor of x, no right subtree", "go up until you arrive from a left child", "succ(40) = 50"]]})
s.obj({"id": "sk", "type": "table", "region": "center", "columns": ["insert in this order", "shape", "height"], "rows": [
    ["50 30 70 20 40 60 80 35", "bushy", "3"],
    ["10 20 30 40 50", "a right-leaning chain", "4 = n − 1"],
    ["random order, n keys", "expected height", "O(log n)"],
    ["sorted order, n keys", "a linked list", "n − 1: every operation Θ(n)"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) insert 45, 15, 79, 90, 10, 55, 12, 20, 50 into an empty BST: draw it and give its height"],
    ["b) the comparisons made when searching for 12"],
    ["c) delete 45: what replaces it?  d) the inorder traversal afterwards"]]})
EK = [45, 15, 79, 90, 10, 55, 12, 20, 50]; ED = build(EK).depth(); EC = {k: i for i, k in enumerate(sorted(EK))}
s.obj({"id": "et", "type": "diagram", "region": "center", "layout": "grid",
       "nodes": [{"id": f"e{k}", "label": str(k), "at": [EC[k], ED[k]], "shape": "circle"} for k in EK],
       "edges": [{"from": f"e{p}", "to": f"e{c}"} for side in (build(EK).l, build(EK).r) for p, c in side.items()]})
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["part", "answer"], "rows": [
    ["a) height", "3"],
    ["b) search 12", "45 → 15 → 10 → 12: 4"],
    ["c) delete 45", "successor 50 moves up"],
    ["d) inorder", "10 12 15 20 50 55 79 90"]]})

def ins_steps(k, d0=0.0):
    out = [{"action": "add_node", "target": "bt", "id": f"k{k}", "label": str(k), "at": [COL[k], D[k]], "shape": "circle", "delay": d0}]
    p = paths[k][-1]
    out.append({"action": "add_edge", "target": "bt", "from": f"k{p}", "to": f"k{k}", "delay": round(d0 + 0.05, 2)})
    return out

s.scene("intro")
s.step("A sorted array finds a key in log n steps, but inserting costs n. A linked list inserts cheaply but searches in n. The binary search tree aims to do both in time proportional to its height. This video builds one.", [s.head("Binary search trees")])
s.step("Here are the eight stages.", show("stages"))
s.step("The search-tree property, searching, inserting, and finding the minimum, maximum and successor.", [hl("stages[0..=3]")])
s.step("Then deleting, in three cases, why the shape of the tree decides everything, and an exam question.", [hl("stages[4..=7]")])

s.scene("prop")
s.step("Stage 1: in a binary search tree, every key in a node's left subtree is smaller than the node's key.", [s.head("Stage 1 of 8: the property")] + hide("stages") + show("bp") + [hl("bp[0]")])
s.step("And every key in its right subtree is larger. This holds at every node, not just between parent and child.", [hl("bp[1]")])
s.step("So an inorder traversal, left, node, right, lists the keys in sorted order.", [hl("bp[2]")])
s.step("Every operation follows one path from the root, so each costs O of h, the height of the tree.", [hl("bp[3]"), s.take("left < node < right, everywhere")])

s.scene("insert")
s.step("Stage 2, done first because we need a tree: insert 50, 30, 70, 20, 40, 60, 80 and 35, in that order. 50 becomes the root.", [s.head("Stage 2 of 8: inserting"), s.untake()] + hide("bp") + show("bt") + [hl("bt.k50")])
s.step("30 is smaller than 50: go left, the spot is empty, put it there. 70 is larger: go right.", ins_steps(30) + ins_steps(70, 0.4))
s.step("20: left of 50, left of 30. 40: left of 50, then right of 30.", ins_steps(20) + ins_steps(40, 0.4))
s.step("60 and 80 settle under 70, on its left and right.", ins_steps(60) + ins_steps(80, 0.4))
s.step("35: smaller than 50, larger than 30, smaller than 40. It becomes 40's left child. A new key always becomes a leaf, at the end of the search path for it.", [hl("bt.k50"), hl("bt.k30", 0.15), hl("bt.k40", 0.3)] + ins_steps(35, 0.5) + [s.take("insert = search, then hang a new leaf")])

s.scene("search")
s.step("Stage 3: searching. Compare the key with the current node: smaller, go left; larger, go right; equal, found.", [s.head("Stage 3 of 8: searching"), s.untake(), {"action": "move", "target": "bt", "region": "left"}] + show("sc") + [ml("sc", 1, 6)])
s.step("Search for 35: 35 is less than 50, go left. More than 30, go right. Less than 40, go left. Found, after 4 comparisons.", [hl("bt.k50"), hl("bt.k30", 0.25), hl("bt.k40", 0.5), mk("bt.k35", 0.75)])
s.step("Search for 65: right of 50, left of 70, right of 60: that pointer is nil. Not found, after 3 comparisons. Each step discards a whole subtree.", [rs("bt.k35"), hl("bt.k50"), hl("bt.k70", 0.3), hl("bt.k60", 0.6)])
s.step("The cost is at most the height plus 1 comparisons. Here the height is 3.", [s.take("each comparison discards a subtree")])

s.scene("succ")
s.step("Stage 4: the minimum is found by going left until you cannot: 20. The maximum, by going right: 80.", [s.head("Stage 4 of 8: min, max, successor"), s.untake()] + hide("sc") + [{"action": "move", "target": "bt", "region": "center"}, mk("bt.k20"), mk("bt.k80", 0.4)])
s.step("The successor of x is the next key in sorted order. If x has a right subtree, it is that subtree's minimum: the successor of 30 is the leftmost node under 40, which is 35.", hide("bt") + show("su") + [hl("su[0..=1]"), hl("su[2]", 0.4)])
s.step("If x has no right subtree, go up until you arrive at a node from its left child. 40 has none: up to 30, arriving from the right; up to 50, arriving from the left. So the successor of 40 is 50.", [hl("su[3]"), s.take("successor: min of right subtree, or the first left-turn ancestor")])

s.scene("del1")
s.step("Stage 5: deleting has three cases. A leaf just disappears: delete 20.", [s.head("Stage 5 of 8: deleting, easy cases"), s.untake()] + hide("su") + show("bt") + [hl("bt.k20"), rm("bt.k20", 0.5)])
s.step("A node with one child is replaced by that child. Delete 40: its only child, 35, moves up and becomes 30's right child.", [hl("bt.k40"), {"action": "add_edge", "target": "bt", "from": "k30", "to": "k35", "delay": 0.4}, rm("bt.k40", 0.6)])
s.step("The ordering survives: 35 was in 30's right subtree before, and still is.", [hl("bt.k35"), s.take("leaf: remove · one child: splice it up")])

s.scene("del2")
s.step("Stage 6: a node with two children cannot simply vanish. Delete 50, the root.", [s.head("Stage 6 of 8: deleting, two children"), s.untake(), hl("bt.k50")])
s.step("Replace its key with its successor, the smallest key in its right subtree: 60. That keeps everything on the left smaller and everything on the right larger.", [hl("bt.k60"), st("bt.k50", "60", 0.5)])
s.step("The successor has no left child, by definition, so removing it from its old place is one of the easy cases. Here 60 was a leaf.", [rm("bt.k60")])
s.step("The tree is now 60 at the root, with 30 and 35 on the left, 70 and 80 on the right. Inorder: 30, 35, 60, 70, 80, still sorted. The predecessor, the largest key on the left, works equally well.", [hl("bt.k50"), s.take("two children: copy in the successor, delete it below")])

s.scene("shape")
s.step("Stage 7: everything costs O of h. Our 8 keys gave a bushy tree of height 3.", [s.head("Stage 7 of 8: why the shape matters"), s.untake()] + hide("bt") + show("sk") + [hl("sk[0]")])
s.step("Insert 10, 20, 30, 40, 50 in sorted order, and every key goes right: a chain of height 4, which is n minus 1.", [hl("sk[1]")])
s.step("In random order, the expected height is O of log n.", [hl("sk[2]")])
s.step("But sorted input, which is common in practice, turns the tree into a linked list, and every operation into Theta of n. AVL and red-black trees, next, rebalance as they go to guarantee O of log n.", [hl("sk[3]"), s.take("unbalanced: up to n − 1 high")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("sk") + show("q") + [hl("q[0]")])
s.step("Build the tree, count the comparisons to find 12, delete the root and list the keys in order. Pause and work it out.", [hl("q[1..=2]")])
s.step("45 is the root. 15 goes left, 79 right. 90 right of 79. 10 left of 15. 55 left of 79. 12: left of 45, left of 15, right of 10. 20 right of 15. 50: right of 45, left of 79, left of 55.", hide("q") + show("et"))
s.step("The deepest nodes, 12 and 50, are 3 edges down: height 3.", [{"action": "move", "target": "et", "region": "left"}, hl("et.e12"), hl("et.e50", 0.3)] + show("qa") + [hl("qa[0]", 0.5)])
s.step("b: searching for 12 compares with 45, 15, 10 and 12: 4 comparisons.", [hl("qa[1]")])
s.step("c: 45 has two children. Its successor is the leftmost key in its right subtree: 79, then 55, then 50. 50 is copied into the root and removed from below, where it was a leaf.", [hl("et.e50"), hl("qa[2]", 0.4)])
s.step("d: inorder gives 10, 12, 15, 20, 50, 55, 79, 90: sorted, as it must be.", [hl("qa[3]"), mk("qa[3][1]", 0.4)])
s.step("The usual slip: using the parent's key instead of the successor when deleting a node with two children.", [s.take("two children: successor (or predecessor), never the parent")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("et", "qa") + show("stages"))
s.step("In a BST, left is smaller and right is larger at every node, so inorder is sorted. Search and insert follow one path; a new key becomes a leaf. Minimum, maximum and successor follow pointers.", [hl("stages[0..=3]")])
s.step("Deleting removes a leaf, splices out a one-child node, or copies in the successor. Every operation is O of height, and height can reach n minus 1.", [hl("stages[4..=6]")])
s.step("Next video: a tree that rebalances itself after every insertion. The AVL tree.", [mk("stages[0..=7]"), s.take("Next: AVL trees")])

s.save("/home/claude/playlist/dsa2/d2v3.json")

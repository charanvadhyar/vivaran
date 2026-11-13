"""DSA Module 2, video 2: tree traversals."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from tree import pre, ino, post, level, rebuild

T = {"A": ("B", "C"), "B": ("D", "E"), "C": ("F", "G"), "E": ("H", "I")}
PRE, IN, POST, LV = pre(T, "A"), ino(T, "A"), post(T, "A"), level(T, "A")
assert "".join(PRE) == "ABDEHICFG" and "".join(IN) == "DBHEIAFCG" and "".join(POST) == "DHIEBFGCA" and "".join(LV) == "ABCDEFGHI"
X = {"*": ("+", "-"), "+": ("a", "b"), "-": ("c", "d")}
assert pre(X, "*") == list("*+ab-cd") and post(X, "*") == list("ab+cd-*") and ino(X, "*") == list("a+b*c-d")
R, r = rebuild(list("ABDECF"), list("DBEAFC")); assert R == {"B": ("D", "E"), "C": ("F", None), "A": ("B", "C")} and post(R, r) == list("DEBFCA")
W, w = rebuild(list("FBADCEGIH"), list("ABCDEFGHI"))
assert w == "F" and W == {"D": ("C", "E"), "B": ("A", "D"), "I": ("H", None), "G": (None, "I"), "F": ("B", "G")}
assert "".join(post(W, w)) == "ACEDBHIGF" and "".join(level(W, w)) == "FBGADICEH"

def tree_obj(i, t, root, region="left"):
    ns = sorted(set([root] + [c for v in t.values() for c in v if c]))
    return {"id": i, "type": "diagram", "region": region, "layout": "tree", "shape": "circle", "directed": False,
            "nodes": [{"id": n} for n in ns], "edges": [{"from": p, "to": c} for p in t for c in t[p] if c]}
def visit(seq, arr, d0=0.0, step=0.1):
    out = []
    for k, x in enumerate(seq):
        dd = round(min(0.95, d0 + k * step), 2)
        out += [mk(f"tr.{x}", dd), ins(arr, k, x, dd)]
    return out

s = Script("Tree traversals")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Three recursive orders"],
    [2, "Preorder"],
    [3, "Inorder"],
    [4, "Postorder"],
    [5, "Level order, with a queue"],
    [6, "Expression trees"],
    [7, "Rebuilding a tree from two orders"],
    [8, "Exam question"]]})
s.obj({"id": "rec", "type": "code", "region": "center", "language": "text", "lines": [
    "PREORDER(x)                 INORDER(x)                  POSTORDER(x)",
    "  if x != null                if x != null                if x != null",
    "    visit(x)                    INORDER(x.left)             POSTORDER(x.left)",
    "    PREORDER(x.left)            visit(x)                    POSTORDER(x.right)",
    "    PREORDER(x.right)           INORDER(x.right)            visit(x)",
    "",
    "node-left-right             left-node-right             left-right-node",
    "every node visited once: Θ(n) time; the recursion stack is Θ(height)"]})
s.obj(tree_obj("tr", T, "A", "left"))
for k in range(1, 5): s.obj({"id": f"out{k}", "type": "array", "region": "right", "values": []})
s.obj({"id": "qq", "type": "array", "region": "right", "values": []})
s.obj({"id": "ex", "type": "diagram", "region": "center", "layout": "tree", "shape": "circle", "directed": False,
       "nodes": [{"id": "mul", "label": "*"}, {"id": "add", "label": "+"}, {"id": "sub", "label": "−"}] + [{"id": v} for v in "abcd"],
       "edges": [{"from": "mul", "to": "add"}, {"from": "mul", "to": "sub"}, {"from": "add", "to": "a"}, {"from": "add", "to": "b"}, {"from": "sub", "to": "c"}, {"from": "sub", "to": "d"}]})
s.obj({"id": "ext", "type": "table", "region": "center", "columns": ["traversal of the expression tree", "gives"], "rows": [
    ["preorder", "* + a b − c d: prefix (Polish) notation"],
    ["inorder", "a + b * c − d: infix, but the brackets are lost"],
    ["inorder with brackets", "((a + b) * (c − d))"],
    ["postorder", "a b + c d − *: postfix, ready for a stack"]]})
s.obj({"id": "rb", "type": "table", "region": "center", "columns": ["preorder A B D E C F · inorder D B E A F C", ""], "rows": [
    ["preorder's first is the root", "A"],
    ["split the inorder at A", "left: D B E · right: F C"],
    ["left subtree: preorder B D E, inorder D B E", "root B, children D and E"],
    ["right subtree: preorder C F, inorder F C", "root C, F on its left"],
    ["the tree's postorder", "D E B F C A"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["preorder:  F B A D C E G I H"],
    ["inorder:   A B C D E F G H I"],
    ["a) rebuild the tree   b) its postorder   c) its level order   d) why do preorder and postorder alone not fix a tree?"]]})
s.obj(tree_obj("qt", W, "F", "left"))
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["part", "answer"], "rows": [
    ["root", "F; left A B C D E, right G H I"],
    ["b) post", "A C E D B H I G F"],
    ["c) level", "F B G A D I C E H"],
    ["d)", "a single child: left or right?"]]})

s.scene("intro")
s.step("A list has one obvious order: front to back. A tree has several, and each one answers a different question. This video walks the same tree four ways, and then runs the process backwards: rebuilding a tree from its traversals.", [s.head("Tree traversals")])
s.step("Here are the eight stages.", show("stages"))
s.step("The three recursive orders, then preorder, inorder and postorder traced on one tree.", [hl("stages[0..=3]")])
s.step("Then level order with a queue, expression trees, rebuilding a tree, and an exam question.", [hl("stages[4..=7]")])

s.scene("rec")
s.step("Stage 1: the three classic traversals are the same recursion with the visit in a different place. Preorder visits the node before its subtrees.", [s.head("Stage 1 of 8: three recursive orders")] + hide("stages") + show("rec") + [ml("rec", 1, 5)])
s.step("Inorder visits it between the left and the right subtree. Postorder, after both.", [ml("rec", 7, 7)])
s.step("Recursion is not required. An iterative inorder keeps its own stack: push nodes while going left, pop one, visit it, then go right. The stack holds the path back up, exactly what the recursion stored for us.", [ml("rec", 2, 5)])
s.step("Each node is visited exactly once: Theta of n time. The recursion stack holds one frame per level: Theta of the height.", [ml("rec", 8, 8), s.take("pre: N L R · in: L N R · post: L R N")])

s.scene("pre")
s.step("Stage 2: preorder on this tree. Visit A, then all of A's left subtree, then all of its right subtree.", [s.head("Stage 2 of 8: preorder"), s.untake()] + hide("rec") + show("tr", "out1") + [hl("tr.A")])
s.step("A, then B, then B's left, D. B's right is E: visit E, then H and I. Then the right side: C, F, G.", visit(PRE, "out1", 0.05, 0.1))
s.step("Notice the rhythm: a node is visited the first time the walk reaches it, on the way down.", [hl("tr.E")])
s.step("A, B, D, E, H, I, C, F, G. Every node comes before its descendants, so preorder is the order to copy a tree, or print it as an indented outline.", [hl("out1"), s.take("preorder: A B D E H I C F G")])

s.scene("in")
s.step("Stage 3: inorder. Go as far left as possible before visiting anything: D first, then its parent B.", [s.head("Stage 3 of 8: inorder"), s.untake(), rs("tr")] + hide("out1") + show("out2"))
s.step("Then B's right subtree, in inorder: H, E, I. Then A. Then A's right subtree: F, C, G.", visit(IN, "out2", 0.05, 0.1))
s.step("D, B, H, E, I, A, F, C, G: every node sits between its left and right subtrees. In a binary search tree, next video, inorder gives the keys in sorted order.", [hl("out2"), s.take("inorder: D B H E I A F C G")])

s.scene("post")
s.step("Stage 4: postorder. A node is visited only after both its subtrees are finished.", [s.head("Stage 4 of 8: postorder"), s.untake(), rs("tr")] + hide("out2") + show("out3"))
s.step("D; then H, I and their parent E; then B. Then F, G and C. A comes last.", visit(POST, "out3", 0.05, 0.1))
s.step("D, H, I, E, B, F, G, C, A. Children always come before parents, so postorder is the order to delete a tree, or to compute sizes and heights from the bottom up.", [hl("out3"), s.take("postorder: D H I E B F G C A")])

s.scene("lvl")
s.step("Stage 5: level order visits level 0, then level 1, then level 2, left to right. Recursion cannot do this; a queue can. Start with the root in the queue.", [s.head("Stage 5 of 8: level order"), s.untake(), rs("tr")] + hide("out3") + show("out4", "qq") + [ins("qq", 0, "A", 0.5)])
s.step("Dequeue A, visit it, and enqueue its children B and C.", [rm("qq[0]"), mk("tr.A", 0.2), ins("out4", 0, "A", 0.2), ins("qq", 0, "B", 0.5), ins("qq", 1, "C", 0.6)])
s.step("Dequeue B, visit it, enqueue D and E. Dequeue C, visit it, enqueue F and G.", [rm("qq[0]"), mk("tr.B", 0.1), ins("out4", 1, "B", 0.1), ins("qq", 1, "D", 0.2), ins("qq", 2, "E", 0.3), rm("qq[0]", 0.5), mk("tr.C", 0.55), ins("out4", 2, "C", 0.55), ins("qq", 2, "F", 0.65), ins("qq", 3, "G", 0.75)])
s.step("D, E, F, G come out in turn; E adds H and I behind them, and they come out last. A, B, C, D, E, F, G, H, I.", [x for k, n in enumerate("DEFGHI") for x in (mk(f"tr.{n}", round(0.1 * k, 2)), ins("out4", 3 + k, n, round(0.1 * k, 2)))] + hide("qq"))
s.step("The queue makes nodes leave in the order their levels were reached. This is breadth-first search, which we will run on graphs later in this module.", [hl("out4"), s.take("level order = a queue, not recursion")])

s.scene("expr")
s.step("Stage 6: an expression tree puts operators at internal nodes and operands at leaves. This one is a plus b, times, c minus d.", [s.head("Stage 6 of 8: expression trees"), s.untake()] + hide("tr", "out4") + show("ex"))
s.step("Preorder gives prefix, or Polish, notation: times, plus a b, minus c d.", hide("ex") + show("ext") + [hl("ext[0]")])
s.step("Inorder gives infix, but loses the brackets: a plus b times c minus d means something else. Printing a bracket around every subtree restores it.", [hl("ext[1..=2]")])
s.step("Postorder gives postfix: a b plus c d minus times. Exactly what the stack evaluator of Module 1 needs.", [hl("ext[3]"), s.take("pre → prefix · in → infix · post → postfix")])

s.scene("rebuild")
s.step("Stage 7: going backwards. Given preorder A B D E C F and inorder D B E A F C, rebuild the tree. Preorder's first element is the root: A.", [s.head("Stage 7 of 8: rebuilding a tree"), s.untake()] + hide("ext") + show("rb") + [hl("rb[0]")])
s.step("Find A in the inorder. Everything before it, D B E, is the left subtree; everything after, F C, is the right.", [hl("rb[1]")])
s.step("Repeat on the left: its preorder is B D E, so B is its root, and the inorder D B E puts D on its left and E on its right.", [hl("rb[2]")])
s.step("On the right: preorder C F makes C the root, and inorder F C puts F on its left.", [hl("rb[3]")])
s.step("The tree is A with children B and C; B has D and E; C has F on the left. Its postorder is D E B F C A.", [hl("rb[4]"), s.take("preorder picks the root, inorder splits the rest")])

s.scene("exam")
s.step("Now an exam question: the classic preorder and inorder pair.", [s.head("Exam question"), s.untake()] + hide("rb") + show("q") + [hl("q[0..=1]")])
s.step("Rebuild the tree, give its postorder and level order, and explain why preorder and postorder alone are not enough. Pause and work it out.", [hl("q[2]")])
s.step("F is the root. In the inorder, A B C D E lie on its left, and G H I on its right.", hide("q") + show("qt", "qa") + [hl("qt.F"), hl("qa[0]", 0.3)])
s.step("Left: preorder B A D C E makes B the root, with A on its left and D, C, E on its right; D's children are C and E. Right: preorder G I H makes G the root with right child I, and I has left child H.", [hl("qt.B"), hl("qt.D", 0.3), hl("qt.G", 0.6), hl("qt.I", 0.8)])
s.step("b: postorder A, C, E, D, B, H, I, G, F. c: level order F, B, G, A, D, I, C, E, H.", [hl("qa[1..=2]")])
s.step("d: with preorder and postorder, a node with a single child cannot be placed: left and right give the same two lists. Inorder is what separates left from right.", [hl("qa[3]")])
s.step("The usual slip: taking the root from the end of the preorder. The root is the first in preorder and the last in postorder.", [s.take("root: first in pre, last in post")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt", "qa") + show("stages"))
s.step("Preorder visits node, left, right; inorder left, node, right; postorder left, right, node. Each takes Theta of n time and Theta of height stack.", [hl("stages[0..=3]")])
s.step("Level order uses a queue. On expression trees the three orders give prefix, infix and postfix. Preorder or postorder, together with inorder, fix a tree uniquely.", [hl("stages[4..=6]")])
s.step("Next video: a binary tree that keeps its keys in order, so that searching follows a single path. The binary search tree.", [mk("stages[0..=7]"), s.take("Next: binary search trees")])

s.save("/home/claude/playlist/dsa2/d2v2.json")

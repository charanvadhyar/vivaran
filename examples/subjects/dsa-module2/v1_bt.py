"""DSA Module 2, video 1: binary trees and their properties."""
import sys, math
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *

T = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "E": ["G", "H"], "F": ["I"]}
nodes = "ABCDEFGHI"
deg = {x: len(T.get(x, [])) for x in nodes}
n0, n1, n2 = (sum(1 for x in nodes if deg[x] == k) for k in (0, 1, 2))
assert (n0, n1, n2) == (4, 2, 3) and n0 == n2 + 1 and len(nodes) - 1 == n1 + 2 * n2
def height(x): return 0 if x not in T else 1 + max(height(c) for c in T[x])
assert height("A") == 3
assert [2**i for i in range(4)] == [1, 2, 4, 8] and 2**4 - 1 == 15
minh = lambda n: math.ceil(math.log2(n + 1)) - 1
assert minh(9) == 3 and minh(100) == 6 and minh(7) == 2 and minh(8) == 3
assert math.comb(6, 3) // 4 == 5
# exam
assert 20 - 1 == 19 and 20 + 10 + 19 == 49 and 49 + 1 == 50
assert 37 // 2 == 18 and (74, 75) == (2 * 37, 2 * 37 + 1) and 100 // 2 == 50 and 51 > 50 and 2 * 51 > 100
assert 2**(3 + 1) - 1 == 15

s = Script("Binary trees")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The words for trees"],
    [2, "Binary trees and their kinds"],
    [3, "How many nodes per level"],
    [4, "Leaves and two-child nodes"],
    [5, "Height and number of nodes"],
    [6, "Storing a tree in an array"],
    [7, "Storing a tree with pointers"],
    [8, "Exam question"]]})
s.obj({"id": "tr", "type": "diagram", "region": "left", "layout": "tree", "shape": "circle", "directed": False,
       "nodes": [{"id": x} for x in nodes], "edges": [{"from": p, "to": c} for p in T for c in T[p]]})
s.obj({"id": "wd", "type": "table", "region": "right", "columns": ["word", "in this tree"], "rows": [
    ["root", "A"],
    ["B's children", "D, E: siblings"],
    ["leaves", "D, G, H, I"],
    ["degree", "A 2 · C 1 · D 0"],
    ["depth", "A 0 · E 2 · G 3"],
    ["height", "3"]]})
s.obj({"id": "ty", "type": "table", "region": "center", "columns": ["kind", "rule", "example"], "rows": [
    ["binary tree", "each node has at most 2 children: a left and a right", "left ≠ right"],
    ["full (strict)", "every node has 0 or 2 children", "no single children"],
    ["perfect", "every level completely filled", "height h: 2ʰ⁺¹ − 1 nodes"],
    ["complete", "all levels full except the last, filled from the left", "heaps (video 9)"],
    ["skewed", "every node has only one child", "a linked list in disguise"]]})
s.obj({"id": "lv", "type": "math", "region": "center", "lines": [
    "\"level\" 0: 1 quad \"level\" 1: 2 quad \"level\" 2: 4 quad \"level\" 3: 8",
    "\"at most\" 2^i \"nodes on level\" i quad \"(each node has at most 2 children)\"",
    "\"height\" h: quad \"at most\" 1 + 2 + 4 + dots.c + 2^h = 2^(h+1) - 1 \"nodes\"",
    "h = 3: quad 15 \"nodes at most\""]})
s.obj({"id": "lf", "type": "math", "region": "center", "lines": [
    "n_0 = \"leaves\", quad n_1 = \"one child\", quad n_2 = \"two children\"",
    "\"nodes:\" quad n = n_0 + n_1 + n_2",
    "\"edges: every node but the root has one edge up:\" quad n - 1 = n_1 + 2 n_2",
    "\"subtract:\" quad n_0 = n_2 + 1",
    "\"our tree:\" quad n_0 = 4, quad n_2 = 3 quad checkmark"]})
s.obj({"id": "hn", "type": "math", "region": "center", "lines": [
    "n <= 2^(h+1) - 1 quad => quad h >= log_2(n + 1) - 1",
    "\"minimum height:\" quad h_min = ceil(log_2(n + 1)) - 1 quad \"(a complete tree)\"",
    "\"maximum height:\" quad h_max = n - 1 quad \"(a skewed tree)\"",
    "n = 9: quad h_min = ceil(log_2 10) - 1 = 3 quad h_max = 8",
    "\"search cost follows height: keeping trees short is the goal of AVL and red-black trees\""]})
s.obj({"id": "ar", "type": "table", "region": "center", "columns": ["index", "1", "2", "3", "4", "5", "6"], "rows": [
    ["node", "A", "B", "C", "D", "E", "F"]]})
s.obj({"id": "arf", "type": "table", "region": "center", "columns": ["node at index i (from 1)", "where"], "rows": [
    ["left child", "2i"], ["right child", "2i + 1"], ["parent", "⌊i / 2⌋"],
    ["a node is a leaf when", "2i > n"],
    ["fits", "complete trees; skewed trees waste cells"]]})
s.obj({"id": "lk", "type": "table", "region": "center", "columns": ["linked representation", ""], "rows": [
    ["each node", "left · data · right"],
    ["n nodes", "2n pointer fields"],
    ["used pointers", "n − 1: one per edge"],
    ["null pointers", "2n − (n − 1) = n + 1"],
    ["fits", "any shape; no wasted cells, but 2 pointers per node"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) a binary tree has 20 leaves and 10 nodes with one child: how many nodes in all?"],
    ["b) a complete binary tree of 100 nodes in an array from index 1: parent and children of 37; is 51 a leaf?"],
    ["c) the minimum height of a binary tree with 100 nodes"],
    ["d) null pointers in the linked form of the tree in (a)"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "n₂ = n₀ − 1 = 19;  n = 20 + 10 + 19", "49"],
    ["b", "parent ⌊37/2⌋ = 18;  children 74 and 75", "18; 74, 75"],
    ["b", "2 × 51 = 102 > 100: no child exists", "yes, a leaf"],
    ["c", "⌈log₂ 101⌉ − 1 = 7 − 1", "6"],
    ["d", "n + 1", "50"]]})

s.scene("intro")
s.step("Lists are straight lines. Trees branch, and that one change lets us search, sort and organise data in logarithmic time. This first video of Module 2 sets up the words, the counting rules, and two ways to store a binary tree.", [s.head("Binary trees")])
s.step("Here are the eight stages.", show("stages"))
s.step("The vocabulary, binary trees and their kinds, nodes per level, and the rule linking leaves to two-child nodes.", [hl("stages[0..=3]")])
s.step("Then height against number of nodes, storing a tree in an array, storing it with pointers, and an exam question.", [hl("stages[4..=7]")])

s.scene("words")
s.step("Stage 1: here is a tree of 9 nodes. A is the root, the only node with no parent.", [s.head("Stage 1 of 8: the words")] + hide("stages") + show("tr", "wd") + [hl("tr.A"), hl("wd[0]", 0.3)])
s.step("B is A's child and A is B's parent. D and E, children of the same parent, are siblings.", [hl("tr.E"), hl("wd[1]", 0.3)])
s.step("A node with no children is a leaf: D, G, H and I.", [mk("tr.D"), mk("tr.G", 0.1), mk("tr.H", 0.2), mk("tr.I", 0.3), hl("wd[2]", 0.4)])
s.step("The degree of a node is its number of children. A has 2, C has 1, a leaf has 0.", [hl("tr.C"), hl("wd[3]", 0.3)])
s.step("The depth, or level, of a node counts edges from the root: A is at 0, E at 2, G at 3. The height of the tree is the largest depth: 3.", [hl("tr.G"), hl("wd[4..=5]", 0.3), s.take("root · leaf · degree · depth · height")])

s.scene("kinds")
s.step("Stage 2: in a binary tree, every node has at most two children, and they are told apart: left and right. A single left child is a different tree from a single right child.", [s.head("Stage 2 of 8: kinds of binary tree"), s.untake()] + hide("tr", "wd") + show("ty") + [hl("ty[0]")])
s.step("A full, or strict, binary tree has no single children: every node has 0 or 2.", [hl("ty[1]")])
s.step("A perfect tree fills every level completely.", [hl("ty[2]")])
s.step("A complete tree fills every level except perhaps the last, and the last is filled from the left. Heaps are complete trees.", [hl("ty[3]")])
s.step("A skewed tree gives every node one child: it is really a linked list, and loses all the advantages of branching.", [hl("ty[4]"), s.take("full · perfect · complete · skewed")])

s.scene("level")
s.step("Stage 3: how many nodes can each level hold? Level 0 has the root: 1. Each node has at most 2 children, so level 1 has at most 2, level 2 at most 4, level 3 at most 8.", [s.head("Stage 3 of 8: nodes per level"), s.untake()] + hide("ty") + show("lv") + [hl("lv[0]")])
s.step("In general, at most 2 to the i nodes on level i.", [rv("lv[1]"), hl("lv[1]")])
s.step("Add the levels from 0 to h: 1 plus 2 plus up to 2 to the h, which is 2 to the h plus 1, minus 1.", [rv("lv[2]"), hl("lv[2]")])
s.step("A tree of height 3 holds at most 15 nodes; our tree has 9.", [rv("lv[3]"), hl("lv[3]"), s.take("level i ≤ 2ⁱ · height h ≤ 2ʰ⁺¹ − 1 nodes")])

s.scene("leaf")
s.step("Stage 4: a rule that appears in almost every exam. Let n 0, n 1 and n 2 count the nodes with 0, 1 and 2 children.", [s.head("Stage 4 of 8: leaves and two-child nodes"), s.untake()] + hide("lv") + show("lf") + [hl("lf[0]")])
s.step("Every node is one of the three: n is n 0 plus n 1 plus n 2.", [rv("lf[1]"), hl("lf[1]")])
s.step("Count edges two ways. Every node except the root has exactly one edge up to its parent: n minus 1 edges. And every node has as many edges down as children: n 1 plus 2 n 2.", [rv("lf[2]"), hl("lf[2]")])
s.step("Subtract the two equations: n 0 equals n 2 plus 1. Leaves always outnumber two-child nodes by exactly one.", [rv("lf[3]"), mk("lf[3]")])
s.step("Check our tree: 4 leaves, D, G, H and I; 3 two-child nodes, A, B and E. 4 is 3 plus 1.", [rv("lf[4]"), hl("lf[4]"), s.take("n₀ = n₂ + 1, whatever the shape")])

s.scene("height")
s.step("Stage 5: turn the node count round. Since n is at most 2 to the h plus 1, minus 1, the height is at least log 2 of n plus 1, minus 1.", [s.head("Stage 5 of 8: height and node count"), s.untake()] + hide("lf") + show("hn") + [hl("hn[0]")])
s.step("So the minimum height is the ceiling of log 2 of n plus 1, minus 1, reached by a complete tree.", [rv("hn[1]"), hl("hn[1]")])
s.step("The maximum is n minus 1, reached by a skewed tree.", [rv("hn[2]"), hl("hn[2]")])
s.step("For 9 nodes: between 3 and 8.", [rv("hn[3]"), hl("hn[3]")])
s.step("Searching a tree costs about its height. So the same 9, or the same million, nodes can cost log n or n, depending on shape. Balanced trees, later in this module, exist to keep the height logarithmic.", [rv("hn[4]"), hl("hn[4]"), s.take("height between log₂ n and n − 1")])

s.scene("array")
s.step("Stage 6: a complete tree fits neatly in an array. Number the nodes level by level, left to right, from 1: A, B, C, D, E, F.", [s.head("Stage 6 of 8: in an array"), s.untake()] + hide("hn") + show("ar"))
s.step("Then the node at index i has its left child at 2i and its right child at 2i plus 1. B, at 2, has children at 4 and 5: D and E.", show("arf") + [hl("arf[0..=1]"), hl("ar[0][2]", 0.3)])
s.step("Its parent is at i over 2, rounded down. F, at 6, has its parent at 3: C.", [hl("arf[2]"), hl("ar[0][6]", 0.3)])
s.step("A node is a leaf when 2i is beyond n: here, nodes 4, 5 and 6.", [hl("arf[3]")])
s.step("No pointers are stored at all. But other shapes waste space: a skewed tree of height h needs 2 to the h plus 1 cells for only h plus 1 nodes.", [hl("arf[4]"), s.take("children 2i, 2i + 1 · parent ⌊i/2⌋")])

s.scene("link")
s.step("Stage 7: for general trees, each node holds a left pointer, the data, and a right pointer.", [s.head("Stage 7 of 8: with pointers"), s.untake()] + hide("ar", "arf") + show("lk") + [hl("lk[0]")])
s.step("n nodes have 2n pointer fields.", [hl("lk[1]")])
s.step("Only n minus 1 of them are used: one per edge.", [hl("lk[2]")])
s.step("So n plus 1 are null. Threaded binary trees reuse those empty fields to point to the next node in order.", [hl("lk[3]")])
s.step("Any shape fits, with no wasted cells, at the cost of two pointers per node.", [hl("lk[4]"), s.take("n nodes: n + 1 null pointers")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("lk") + show("q") + [hl("q[0..=1]")])
s.step("Count the nodes, use the array formulas, find the minimum height, and count null pointers. Pause and work it out.", [hl("q[2..=3]")])
s.step("a: n 2 is n 0 minus 1, 19. Total: 20 plus 10 plus 19, 49 nodes.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: the parent of 37 is 37 over 2 rounded down, 18. Its children are 74 and 75.", [hl("qa[1]")])
s.step("Node 51: 2 times 51 is 102, beyond 100, so it has no children. A leaf. In fact every node from 51 to 100 is a leaf.", [hl("qa[2]")])
s.step("c: log 2 of 101 is about 6.66; the ceiling is 7; minus 1 is 6.", [hl("qa[3]")])
s.step("d: 49 nodes have 49 plus 1, 50 null pointers.", [hl("qa[4]"), mk("qa[4][2]", 0.4)])
s.step("The usual slip: using 0-based formulas with 1-based numbering. From index 0, the children are 2i plus 1 and 2i plus 2.", [s.take("check whether the array starts at 0 or 1")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Trees have roots, leaves, depths and a height. Binary trees can be full, perfect, complete or skewed. Level i holds at most 2 to the i nodes, and leaves are always two-child nodes plus one.", [hl("stages[0..=3]")])
s.step("Height lies between log n and n minus 1. Complete trees fit an array with children at 2i and 2i plus 1; pointers fit any shape and leave n plus 1 nulls.", [hl("stages[4..=6]")])
s.step("Next video: visiting every node of a tree. Preorder, inorder, postorder and level order.", [mk("stages[0..=7]"), s.take("Next: tree traversals")])

s.save("/home/claude/playlist/dsa2/d2v1.json")

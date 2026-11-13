"""DSA Module 2, video 7: B-trees."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *
from btree import BTree

def run(t, keys):
    b = BTree(t); states = []
    for k in keys:
        n = len(b.splits); b.insert(k); states.append((k, b.splits[n:], b.snap(), b.levels()))
    return b, states
B, ST = run(2, [10, 20, 30, 40, 50, 60, 70, 80, 90])
assert [s[1] for s in ST] == [[], [], [], [20], [], [40], [], [60], [40]]
assert ST[-1][3] == [[[40]], [[20], [60]], [[10], [30], [50], [70, 80, 90]]] and B.search(70) == 3
E, ES = run(2, [8, 3, 12, 5, 1, 9, 15, 2, 7])
assert [s[1] for s in ES] == [[], [], [], [8], [], [], [], [3], []]
assert ES[-1][3] == [[[3, 8]], [[1, 2], [5, 7], [9, 12, 15]]] and E.search(7) == 2 and E.search(6) == -2
assert 1000 + 1001 * 1000 + 1001**2 * 1000 == 1_003_003_000

def bt_obj(i, snap, region="center"):
    ids = {n[0]: n for n in snap}; kids = {}
    for nid, keys, d, p in snap:
        if p is not None: kids.setdefault(p, []).append(nid)
    col = {}; nxt = [0]
    def place(nid):
        if nid not in kids: col[nid] = nxt[0]; nxt[0] += 2; return
        for c in kids[nid]: place(c)
        col[nid] = (col[kids[nid][0]] + col[kids[nid][-1]]) // 2
    place(snap[0][0])
    return {"id": i, "type": "diagram", "region": region, "layout": "tree",
            "nodes": [{"id": f"b{nid}", "label": " | ".join(map(str, keys)), "shape": "box"} for nid, keys, d, p in snap],
            "edges": [{"from": f"b{p}", "to": f"b{nid}"} for nid, keys, d, p in snap if p is not None]}

s = Script("B-trees")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why disks need wide trees"],
    [2, "The rules, with minimum degree t"],
    [3, "How short a B-tree is"],
    [4, "Searching"],
    [5, "Splitting a full node"],
    [6, "Inserting 10 to 90"],
    [7, "Deleting, briefly"],
    [8, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["", "main memory", "disk (SSD or hard disk)"], "rows": [
    ["one access", "about 100 nanoseconds", "about 0.1 to 10 milliseconds"],
    ["unit of transfer", "a word or a cache line", "a whole block or page: 4 to 16 KB"],
    ["so the goal", "", "few block reads: fill each block with many keys"],
    ["a binary tree of a billion keys", "", "about 30 levels: 30 disk reads"],
    ["a B-tree with 1000 keys per node", "", "3 levels: 3 disk reads"]]})
s.obj({"id": "ru", "type": "table", "region": "center", "columns": ["B-tree of minimum degree t ≥ 2 (Cormen)", ""], "rows": [
    ["every node except the root", "has between t − 1 and 2t − 1 keys"],
    ["the root", "has at least 1 key (unless the tree is empty)"],
    ["a node with k keys", "has k + 1 children; its keys separate theirs"],
    ["all leaves", "are at the same depth"],
    ["t = 2", "1 to 3 keys per node: the 2-3-4 tree"],
    ["other books say order m", "at most m children: m = 2t"]]})
s.obj({"id": "hb", "type": "math", "region": "center", "lines": [
    "\"fewest keys at height\" h: quad \"root 1 key; then 2, 2t, 2t^2, dots \" \"nodes with\" t - 1 \"keys\"",
    "n >= 1 + (t - 1) sum_(i=1)^h 2 t^(i-1) = 2 t^h - 1",
    "h <= log_t ((n + 1) / 2)",
    "\"1001 children per node, height 2:\" quad 1000 + 1001 dot 1000 + 1001^2 dot 1000 approx 10^9 \"keys\"",
    "\"a billion keys, the root kept in memory: 2 disk reads per search\""]})
s.obj({"id": "sc", "type": "table", "region": "center", "columns": ["B-TREE-SEARCH(x, k)", ""], "rows": [
    ["scan x's keys", "find the first key ≥ k"],
    ["if it equals k", "found"],
    ["else, if x is a leaf", "not there"],
    ["else", "read the child between the two keys from disk, and repeat"],
    ["cost", "O(h) disk reads, O(t h) comparisons"]]})
s.obj({"id": "sp", "type": "table", "region": "center", "columns": ["splitting a full node (2t − 1 keys)", "t = 2: 10 | 20 | 30"], "rows": [
    ["the median key", "moves up into the parent: 20"],
    ["the keys left of it", "stay in one node: 10"],
    ["the keys right of it", "go into a new node: 30"],
    ["Cormen splits on the way down", "any full node met is split before entering it"],
    ["so the parent always has room", "and one pass down the tree is enough"],
    ["the tree grows taller", "only when the root splits: it grows at the top"]]})
for i in (2, 3, 5, 7, 8): s.obj(bt_obj(f"s{i}", ST[i][2]))
s.obj({"id": "dl", "type": "table", "region": "center", "columns": ["deleting key k (Cormen)", ""], "rows": [
    ["from a leaf with more than t − 1 keys", "just remove it"],
    ["from an internal node", "replace with predecessor or successor from a child with ≥ t keys, or merge"],
    ["before descending into a child with only t − 1 keys", "borrow a key through the parent from a sibling, or merge with a sibling"],
    ["the tree shrinks", "only when the root loses its last key"],
    ["cost", "one pass down: O(h) disk reads"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: a B-tree with t = 2"], "rows": [
    ["insert 8, 3, 12, 5, 1, 9, 15, 2, 7 into an empty tree, splitting full nodes on the way down"],
    ["a) after which insertions does a split happen, and which key moves up?"],
    ["b) the final tree   c) disk reads to search for 7, and for 6"]]})
s.obj(bt_obj("qt", ES[-1][2], "left"))
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["part", "answer"], "rows": [
    ["insert 5", "root 3 | 8 | 12 full: split, 8 up"],
    ["insert 2", "1 | 3 | 5 full: split, 3 up"],
    ["final", "3 | 8 over 1 | 2, 5 | 7, 9 | 12 | 15"],
    ["search 7", "2 reads: found"],
    ["search 6", "2 reads: not found"]]})

s.scene("intro")
s.step("AVL and red-black trees are built for main memory. Databases and file systems keep their data on disk, where each access costs a million times more and moves a whole block. The B-tree is designed for that: wide and very short. This video builds one.", [s.head("B-trees")])
s.step("Here are the eight stages.", show("stages"))
s.step("Why disks need wide trees, the rules, how short a B-tree is, and searching.", [hl("stages[0..=3]")])
s.step("Then splitting full nodes, a sequence of insertions, deletion in outline, and an exam question.", [hl("stages[4..=7]")])

s.scene("why")
s.step("Stage 1: main memory answers in about 100 nanoseconds. A disk takes from a tenth of a millisecond to ten milliseconds.", [s.head("Stage 1 of 8: why wide trees")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("And a disk always transfers a whole block, typically 4 to 16 kilobytes, even if you want one key.", [hl("why[1]")])
s.step("So what matters is the number of blocks read, and each block should be packed with useful keys.", [hl("why[2]")])
s.step("A balanced binary tree of a billion keys is about 30 levels deep: 30 disk reads per search. A B-tree with a thousand keys per node needs 3.", [hl("why[3..=4]"), s.take("count disk reads, not comparisons")])

s.scene("rules")
s.step("Stage 2: Cormen describes a B-tree by its minimum degree t, at least 2. Every node except the root holds between t minus 1 and 2t minus 1 keys.", [s.head("Stage 2 of 8: the rules"), s.untake()] + hide("why") + show("ru") + [hl("ru[0]")])
s.step("The root may hold as few as 1.", [hl("ru[1]")])
s.step("A node with k keys has k plus 1 children, and its keys, in sorted order, separate the key ranges of those children.", [hl("ru[2]")])
s.step("All leaves are at the same depth: the tree is perfectly balanced in height.", [hl("ru[3]")])
s.step("With t equal to 2, nodes hold 1 to 3 keys: this is the 2-3-4 tree. Some books instead give the order m, the most children a node may have; then m is 2t.", [hl("ru[4..=5]"), s.take("t − 1 to 2t − 1 keys per node · leaves level")])

s.scene("height")
s.step("Stage 3: how tall can it be? The sparsest tree of height h has 1 key in the root, then 2 nodes, then 2t, then 2t squared, each with only t minus 1 keys.", [s.head("Stage 3 of 8: how short a B-tree is"), s.untake()] + hide("ru") + show("hb") + [hl("hb[0]")])
s.step("Adding them up, n is at least 2 t to the h, minus 1.", [rv("hb[1]"), hl("hb[1]")])
s.step("So the height is at most log base t of n plus 1 over 2. The base is t, not 2: a much smaller number.", [rv("hb[2]"), hl("hb[2]")])
s.step("With 1001 children per node, a tree of height 2 holds about a billion keys.", [rv("hb[3]"), hl("hb[3]")])
s.step("Keep the root in memory, and any of a billion keys is found with 2 disk reads.", [rv("hb[4]"), hl("hb[4]"), s.take("h ≤ log_t((n + 1)/2)")])

s.scene("search")
s.step("Stage 4: searching generalises the BST. In a node, scan its keys for the first one at least k.", [s.head("Stage 4 of 8: searching"), s.untake()] + hide("hb") + show("sc") + [hl("sc[0]")])
s.step("If it equals k, done. If the node is a leaf, k is not in the tree.", [hl("sc[1..=2]")])
s.step("Otherwise read the child that lies between the two neighbouring keys, and repeat there.", [hl("sc[3]")])
s.step("One disk read per level: O of h reads, and O of t h comparisons in memory, which are almost free in comparison.", [hl("sc[4]"), s.take("one block per level")])

s.scene("split")
s.step("Stage 5: a node is full when it holds 2t minus 1 keys: with t equal to 2, three keys, like 10, 20, 30.", [s.head("Stage 5 of 8: splitting a full node"), s.untake()] + hide("sc") + show("sp"))
s.step("Splitting it moves the median key, 20, up into the parent; 10 stays in one node, and 30 goes into a new node beside it.", [hl("sp[0..=2]")])
s.step("Cormen splits proactively: on the way down, any full node is split before we enter it. So whenever a key moves up, the parent is guaranteed to have room, and one pass down is enough.", [hl("sp[3..=4]")])
s.step("A B-tree grows taller only when the root splits. It grows at the top, not at the leaves, which is why all leaves stay at one depth.", [hl("sp[5]"), s.take("full node: median up, halves apart")])

s.scene("ins")
s.step("Stage 6: insert 10 to 90 in steps of 10, with t equal to 2. 10, 20 and 30 fill the root.", [s.head("Stage 6 of 8: inserting 10 to 90"), s.untake()] + hide("sp") + show("s2"))
s.step("Insert 40. The root is full, so it is split first: 20 becomes a new root, with 10 and 30 below it. Then 40 joins 30.", hide("s2") + show("s3") + [hl("s3.b0")])
s.step("50 joins 30 and 40, filling that leaf. Insert 60: on the way down, the full leaf 30, 40, 50 is split. 40 moves up beside 20, and 60 joins 50.", hide("s3") + show("s5") + [hl("s5.b0")])
s.step("70 fills the leaf 50, 60, 70. Insert 80: that leaf splits, 60 moves up, and the root is now full: 20, 40, 60.", hide("s5") + show("s7") + [hl("s7.b0")])
s.step("Insert 90. The root is full, so it splits before anything else: 40 becomes the new root, with 20 and 60 as children. The tree grew one level, at the top. Then 90 joins 70 and 80.", hide("s7") + show("s8") + [mk("s8.b0")])
s.step("Sorted input, yet every leaf is at depth 2. A search for 70 reads the root, then 60, then the leaf: 3 blocks.", [s.take("grows at the root, always balanced")])

s.scene("del")
s.step("Stage 7: deletion, in outline. Removing a key from a leaf that has more than t minus 1 keys is simple.", [s.head("Stage 7 of 8: deleting"), s.untake()] + hide("s8") + show("dl") + [hl("dl[0]")])
s.step("From an internal node, the key is replaced by its predecessor or successor from a child, or two children are merged.", [hl("dl[1]")])
s.step("Like insertion, Cormen's deletion works in one pass down: before entering a child that has only t minus 1 keys, it borrows a key from a sibling through the parent, or merges with a sibling.", [hl("dl[2]")])
s.step("The tree loses a level only when the root's last key is merged away. O of h disk reads.", [hl("dl[3..=4]"), s.take("delete: borrow or merge on the way down")])

s.scene("exam")
s.step("Now an exam question on a B-tree with t equal to 2.", [s.head("Exam question"), s.untake()] + hide("dl") + show("q") + [hl("q[0]")])
s.step("Insert nine keys, name every split, draw the final tree, and count disk reads for two searches. Pause and work it out.", [hl("q[1..=2]")])
s.step("8, 3 and 12 fill the root: 3, 8, 12. Inserting 5 finds it full, so it splits: 8 moves up as the new root, with 3 and 12 below. 5 joins 3.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("1 joins 3 and 5, filling that leaf. 9 and 15 join 12. Inserting 2 meets the full leaf 1, 3, 5 on the way down: it splits, 3 moves up beside 8, and 2 joins 1.", [hl("qa[1]")])
s.step("7 joins 5. The final tree: root 3, 8; leaves 1, 2; then 5, 7; then 9, 12, 15.", show("qt") + [hl("qa[2]")])
s.step("c: 7 lies between 3 and 8, so the root, then the middle leaf: 2 reads, found. 6 follows the same path and is not in the leaf: 2 reads, not found.", [hl("qa[3..=4]"), mk("qa[3][1]", 0.5)])
s.step("The usual slip: inserting first and splitting afterwards from the bottom. With proactive splitting, you split every full node you pass on the way down, even if it would not overflow.", [s.take("split full nodes on the way down")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt", "qa") + show("stages"))
s.step("Disks reward few, large reads, so B-tree nodes hold t minus 1 to 2t minus 1 keys, all leaves share one depth, and the height is at most log base t of n plus 1 over 2.", [hl("stages[0..=3]")])
s.step("Search reads one block per level. Insertion splits full nodes on the way down, sending the median up, and the tree grows at the root. Deletion borrows or merges on the way down.", [hl("stages[4..=6]")])
s.step("Next video: a tree built over an array to answer range questions fast. The segment tree.", [mk("stages[0..=7]"), s.take("Next: segment trees")])

s.save("/home/claude/playlist/dsa2/d2v7.json")

"""DSA Module 3, video 9: Huffman coding."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *
from greedy import huffman

F = [("a", 45), ("b", 13), ("c", 12), ("d", 16), ("e", 9), ("f", 5)]
C, L, COST, K, R = huffman(F)
assert C == {"a": "0", "b": "101", "c": "100", "d": "111", "e": "1101", "f": "1100"} and COST == 224 and 3 * 100 == 300
assert [x[4] for x in L] == [14, 25, 30, 55, 100]
EF = [("A", 10), ("E", 15), ("I", 12), ("S", 3), ("T", 4), ("P", 13), ("N", 1)]
EC, EL, ECOST, _, _ = huffman(EF)
assert ECOST == 146 and [x[4] for x in EL] == [4, 8, 18, 25, 33, 58] and 3 * 58 == 174
assert {s: len(c) for s, c in EC.items()} == {"I": 2, "P": 2, "E": 2, "A": 3, "T": 4, "N": 5, "S": 5}
assert "".join(C[x] for x in "face") == "1100" + "0" + "100" + "1101"
assert 45 * 1 + 13 * 3 + 12 * 3 + 16 * 3 + 9 * 4 + 5 * 4 == 224

# tree: ids from frequencies
lab = {}; ids = {}
def nid(n):
    if n not in ids: ids[n] = f"n{len(ids)}"
    return ids[n]
fd = dict(F); sums = {}
def walk(n):
    if n in K: f = walk(K[n][0]) + walk(K[n][1])
    else: f = fd[n]
    sums[n] = f; return f
walk(R)
nodes = []; edges = []
def build(n):
    nodes.append({"id": nid(n), "label": f"{n}:{sums[n]}" if n not in K else str(sums[n])})
    if n in K:
        l, r = K[n]; build(l); build(r)
        edges.append({"from": nid(n), "to": nid(l), "label": "0"}); edges.append({"from": nid(n), "to": nid(r), "label": "1"})
build(R)

s = Script("Huffman coding")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Fixed-length and variable-length codes"],
    [2, "Prefix codes and code trees"],
    [3, "Huffman's greedy rule"],
    [4, "Cormen's example, merge by merge"],
    [5, "Reading off the codes; encoding and decoding"],
    [6, "The algorithm, its cost, and why it is optimal"],
    [7, "Exam question"]]})
s.obj({"id": "fx", "type": "table", "region": "center", "columns": ["character", "a", "b", "c", "d", "e", "f"], "rows": [
    ["frequency (thousands)", "45", "13", "12", "16", "9", "5"],
    ["fixed-length code", "000", "001", "010", "011", "100", "101"],
    ["variable-length code", "0", "101", "100", "111", "1101", "1100"]]})
s.obj({"id": "cost", "type": "math", "region": "center", "lines": [
    "\"fixed: \" 3 times 100000 = 300000 \" bits\"",
    "\"variable: \" (45 dot 1 + 13 dot 3 + 12 dot 3 + 16 dot 3 + 9 dot 4 + 5 dot 4) times 1000 = 224000 \" bits\"",
    "\"saving: about 25 percent\""]})
s.obj({"id": "pf", "type": "table", "region": "center", "columns": ["prefix codes", ""], "rows": [
    ["prefix code", "no codeword is a prefix of another"],
    ["why", "decoding is unambiguous: read bits until a codeword matches"],
    ["bad example", "a = 0, b = 01: does 01 start a or b?"],
    ["code tree", "a binary tree: 0 = go left, 1 = go right; characters at the leaves"],
    ["cost of a tree", "B(T) = Σ freq(c) × depth(c)"]]})
s.obj({"id": "gr", "type": "table", "region": "center", "columns": ["Huffman's greedy rule", ""], "rows": [
    ["start", "every character is a one-node tree, weighted by its frequency"],
    ["repeat n − 1 times", "take the two trees of least weight; join them under a new root"],
    ["new root's weight", "the sum of the two"],
    ["intuition", "the rarest characters end up deepest, with the longest codes"]]})
s.obj({"id": "mg", "type": "table", "region": "center", "columns": ["queue (by weight)", "merge the two smallest", "new tree"], "rows": [
    ["f 5, e 9, c 12, b 13, d 16, a 45", "", ""], ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]]})
s.obj({"id": "tr", "type": "diagram", "region": "left", "layout": "tree", "nodes": nodes, "edges": edges})
s.obj({"id": "ct", "type": "table", "region": "right", "columns": ["char", "freq", "code", "bits"],
       "rows": [[c, str(f), "", ""] for c, f in F]})
s.obj({"id": "hc", "type": "code", "region": "center", "language": "text", "lines": [
    "HUFFMAN(C)",
    "    n = |C|;   Q = C                       // a min-priority queue on frequency",
    "    for i = 1 to n − 1",
    "        allocate a new node z",
    "        z.left = x = EXTRACT-MIN(Q)",
    "        z.right = y = EXTRACT-MIN(Q)",
    "        z.freq = x.freq + y.freq",
    "        INSERT(Q, z)",
    "    return EXTRACT-MIN(Q)                 // the root",
    "",
    "binary heap: n − 1 rounds × O(log n) = O(n log n)"]})
s.obj({"id": "op", "type": "table", "region": "center", "columns": ["why Huffman is optimal", ""], "rows": [
    ["greedy choice", "some optimal tree has the two rarest characters as sibling leaves at the greatest depth"],
    ["reason", "swapping a rarer character deeper never increases Σ freq × depth"],
    ["optimal substructure", "merge them into one character z of their summed frequency: the rest is the same problem, smaller"],
    ["so", "every merge keeps an optimal tree within reach: the final tree is optimal among prefix codes"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["frequencies: A 10, E 15, I 12, S 3, T 4, P 13, N 1"],
    ["a) the merges, in order"],
    ["b) the length of each character's code"],
    ["c) total bits, against a fixed-length code"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "result"], "rows": [
    ["a)", "N 1 + S 3 = 4;  T 4 + (4) = 8;  (8) + A 10 = 18", ""],
    ["a)", "I 12 + P 13 = 25;  E 15 + (18) = 33;  (25) + (33) = 58", "root 58"],
    ["b)", "depths in the tree", "I, P, E: 2 · A: 3 · T: 4 · N, S: 5"],
    ["c)", "10·3 + 15·2 + 12·2 + 3·5 + 4·4 + 13·2 + 1·5", "146 bits"],
    ["c)", "7 characters need 3 bits each: 3 × 58", "174 bits"]]})

s.scene("intro")
s.step("Every zip file, every JPEG and MP3 uses a trick from 1952: give frequent symbols short codes and rare ones long codes. David Huffman, then a student, found the greedy algorithm that makes the best such code. This video builds it.", [s.head("Huffman coding")])
s.step("Here are the seven stages.", show("stages"))
s.step("Fixed and variable-length codes, prefix codes and code trees, Huffman's rule, and Cormen's example.", [hl("stages[0..=3]")])
s.step("Then reading off the codes, the algorithm and why it is optimal, and an exam question.", [hl("stages[4..=6]")])

s.scene("fx")
s.step("Stage 1: Cormen's example. A file of 100 thousand characters uses only six: a to f, with these frequencies, in thousands.", [s.head("Stage 1 of 7: fixed or variable length")] + hide("stages") + show("fx") + [hl("fx[0]")])
s.step("A fixed-length code needs 3 bits per character, since 2 bits give only four codewords.", [hl("fx[1]")])
s.step("A variable-length code gives a, the most common, a single bit, and f, the rarest, four bits.", [hl("fx[2]")])
s.step("The fixed code needs 300 thousand bits.", hide("fx") + show("cost") + [hl("cost[0]")])
s.step("The variable code: 45 times 1, plus 13 times 3, and so on: 224 thousand bits.", [rv("cost[1]"), hl("cost[1]")])
s.step("A saving of about a quarter, and Huffman's algorithm proves no prefix code can do better.", [rv("cost[2]"), hl("cost[2]"), s.take("frequent: short code · rare: long code")])

s.scene("pf")
s.step("Stage 2: a variable-length code must be decodable. In a prefix code, no codeword is the start of another.", [s.head("Stage 2 of 7: prefix codes"), s.untake()] + hide("cost") + show("pf") + [hl("pf[0]")])
s.step("Then decoding is easy: read bits until they spell a codeword, output that character, and start again.", [hl("pf[1]")])
s.step("If a were 0 and b were 0 1, then a 0 could be the whole of a, or the start of b. We could not tell.", [hl("pf[2]")])
s.step("A prefix code is a binary tree: 0 means go left, 1 means go right, and each character sits at a leaf. Leaves can never be on the path to other leaves, which is exactly the prefix property.", [hl("pf[3]")])
s.step("The cost of a tree is the sum, over characters, of frequency times depth: the depth is the code length.", [hl("pf[4]"), s.take("code = path from the root to a leaf")])

s.scene("gr")
s.step("Stage 3: Huffman builds the tree bottom up. Start with each character as a tree of one node, weighted by its frequency.", [s.head("Stage 3 of 7: the greedy rule"), s.untake()] + hide("pf") + show("gr") + [hl("gr[0]")])
s.step("Then repeatedly take the two trees of smallest weight and join them under a new root.", [hl("gr[1]")])
s.step("The new root's weight is the sum of the two.", [hl("gr[2]")])
s.step("Rare characters are merged first, so they end up deepest in the tree, with the longest codes.", [hl("gr[3]"), s.take("merge the two lightest, repeat")])

s.scene("mg")
s.step("Stage 4: the queue starts with all six, by frequency: f 5, e 9, c 12, b 13, d 16, a 45.", [s.head("Stage 4 of 7: merge by merge"), s.untake()] + hide("gr") + show("mg") + [hl("mg[0]")])
rows = [("f 5 + e 9", "14", "c 12, b 13, (14), d 16, a 45"),
        ("c 12 + b 13", "25", "(14), d 16, (25), a 45"),
        ("(14) + d 16", "30", "(25), (30), a 45"),
        ("(25) + (30)", "55", "a 45, (55)"),
        ("a 45 + (55)", "100", "")]
say = ["The two smallest are f, 5, and e, 9. Merge them into a tree of weight 14.",
       "Now the smallest are c, 12, and b, 13: merge into 25.",
       "Next, the 14 tree and d, 16: merge into 30.",
       "Then 25 and 30: merge into 55. Only a, 45, and the 55 tree remain.",
       "Finally a and 55 make the root, 100: the whole file. Five merges for six characters."]
for k, (m, w, rest) in enumerate(rows):
    acts = [st(f"mg[{k}][1]", m), st(f"mg[{k}][2]", w, 0.3), hl(f"mg[{k}]")]
    if rest: acts.append(st(f"mg[{k + 1}][0]", rest, 0.6))
    if k == 4: acts += [mk("mg[4][2]", 0.7), s.take("n − 1 merges build the tree")]
    s.step(say[k], acts)

s.scene("codes")
s.step("Stage 5: here is the finished tree. Left edges are 0, right edges are 1. a hangs right below the root, on the left.", [s.head("Stage 5 of 7: reading the codes"), s.untake()] + hide("mg") + show("tr", "ct") + [hl(f"tr.{nid('a')}")])
s.step("So a's code is just 0. On the right, 55 splits into 25 and 30; 25 holds c and b: c is 1, 0, 0, and b is 1, 0, 1.", [st("ct[0][2]", "0"), st("ct[0][3]", "1", 0.1), st("ct[2][2]", "100", 0.4), st("ct[2][3]", "3", 0.45), st("ct[1][2]", "101", 0.6), st("ct[1][3]", "3", 0.65), hl(f"tr.{nid('c')}", 0.4), hl(f"tr.{nid('b')}", 0.6)])
s.step("Under 30, d is on the right: 1, 1, 1. And the 14 tree holds f and e: 1, 1, 0, 0 and 1, 1, 0, 1.", [st("ct[3][2]", "111"), st("ct[3][3]", "3", 0.1), st("ct[5][2]", "1100", 0.4), st("ct[5][3]", "4", 0.45), st("ct[4][2]", "1101", 0.6), st("ct[4][3]", "4", 0.65), hl(f"tr.{nid('d')}"), hl(f"tr.{nid('f')}", 0.4), hl(f"tr.{nid('e')}", 0.6)])
s.step("To encode the word face: f, 1 1 0 0; a, 0; c, 1 0 0; e, 1 1 0 1. Twelve bits, the same as a fixed code would need, because this word uses two rare letters. On typical text, full of a's, the saving appears.", [hl("ct[5]"), hl("ct[0]", 0.3), hl("ct[2]", 0.5), hl("ct[4]", 0.7)])
s.step("To decode, start at the root and follow the bits: 1, 1, 0, 0 reaches the leaf f. Output f, return to the root, and continue. No separators are needed.", [hl(f"tr.{nid('f')}"), s.take("decode: walk from the root, restart at each leaf")])
s.step("Try one: decode 0 1 0 1 1 1 0 0. The first 0 reaches a at once. Then 1, 0, 1 reaches b. Then 1, 1, 0, 0 reaches f. The message is a, b, f.", [hl(f"tr.{nid('a')}"), hl(f"tr.{nid('b')}", 0.4), hl(f"tr.{nid('f')}", 0.75)])
s.step("Real compressors store the tree, or the code lengths, at the start of the file, so the decoder can rebuild it.", [hl("ct")])

s.scene("algo")
s.step("Stage 6: Cormen's HUFFMAN keeps the trees in a min-priority queue, keyed on frequency.", [s.head("Stage 6 of 7: algorithm and proof"), s.untake()] + hide("tr", "ct") + show("hc") + [ml("hc", 1, 2)])
s.step("n minus 1 times: extract the two smallest, x and y, make them the children of a new node z, whose frequency is their sum, and insert z.", [ml("hc", 3, 8)])
s.step("The last tree left is the root. With a binary heap, each round costs log n: O of n log n in all.", [ml("hc", 9, 11)])
s.step("Why optimal? First, the greedy choice: some optimal tree has the two rarest characters as siblings at the deepest level. Swapping a rarer character deeper never increases the cost.", hide("hc") + show("op") + [hl("op[0..=1]")])
s.step("Second, optimal substructure: treat the merged pair as one character with their total frequency, and what remains is the same problem with one fewer character.", [hl("op[2]")])
s.step("So every merge stays on the path to an optimal tree, and Huffman's code is the best possible prefix code.", [hl("op[3]"), s.take("O(n log n); optimal among prefix codes")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("op") + show("q") + [hl("q[0]")])
s.step("List the merges, give each code length, and compare the total with a fixed-length code. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: N 1 and S 3 make 4. Then T 4 and that 4 make 8. Then 8 and A 10 make 18.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Then I 12 and P 13 make 25. E 15 and 18 make 33. Finally 25 and 33 make the root, 58.", [hl("qa[1]")])
s.step("b: reading depths off the tree: I, P and E have 2-bit codes, A 3, T 4, and N and S 5.", [hl("qa[2]")])
s.step("c: 10 times 3, plus 15 times 2, and so on: 146 bits. A fixed code needs 3 bits for 7 characters: 3 times 58, 174. Huffman saves 28 bits.", [hl("qa[3..=4]"), mk("qa[3][2]", 0.5)])
s.step("The usual slip: with ties, different trees are possible, and so are different codes. But the total, 146 bits, is always the same. Check your total, not just your codes.", [s.take("ties change codes, never the total")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Variable-length prefix codes give frequent characters short codewords; a prefix code is a binary tree with characters at the leaves.", [hl("stages[0..=2]")])
s.step("Huffman repeatedly merges the two lightest trees, in O of n log n, and the result is an optimal prefix code.", [hl("stages[3..=5]")])
s.step("That completes Module 3. Next, Module 4: dynamic programming, starting with matrix chain multiplication.", [mk("stages[0..=6]"), s.take("Next: Module 4, dynamic programming")])

s.save("/home/claude/playlist/dsa3/d3v9.json")

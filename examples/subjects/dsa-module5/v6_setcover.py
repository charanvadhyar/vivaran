"""DSA Module 5, video 6: greedy set cover."""
import sys, itertools
from fractions import Fraction
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa5")
from common import Script
from h import *

def greedy(S):
    U = set().union(*S.values()); C = []
    while U:
        b = max(S, key=lambda k: (len(S[k] & U), -list(S).index(k))); C.append((b, sorted(S[b] & U))); U -= S[b]
    return C
def opt(S):
    X = set().union(*S.values())
    for k in range(1, len(S) + 1):
        f = [c for c in itertools.combinations(S, k) if set().union(*[S[x] for x in c]) == X]
        if f: return f
S = {"S1": {1, 2, 3, 4, 5, 6}, "S2": {5, 6, 8, 9}, "S3": {1, 4, 7, 10}, "S4": {2, 5, 7, 8, 11}, "S5": {3, 6, 9, 12}, "S6": {10, 11}}
G = greedy(S); assert G == [("S1", [1, 2, 3, 4, 5, 6]), ("S4", [7, 8, 11]), ("S5", [9, 12]), ("S3", [10])] and opt(S) == [("S3", "S4", "S5")]
H = lambda n: sum(Fraction(1, i) for i in range(1, n + 1))
assert round(float(H(6)), 2) == 2.45 and round(float(H(4)), 2) == 2.08
SE = {"A": {1, 2, 3, 4}, "B": {1, 2, 5}, "C": {3, 4, 6}}
assert greedy(SE) == [("A", [1, 2, 3, 4]), ("B", [5]), ("C", [6])] and opt(SE) == [("B", "C")]

s = Script("Approximation: set cover")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The set-cover problem"],
    [2, "The greedy rule"],
    [3, "Twelve elements, six sets, traced"],
    [4, "The algorithm and its cost"],
    [5, "How far from optimal: the harmonic bound"],
    [6, "Vertex cover is a special case"],
    [7, "Exam question"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["set cover", ""], "rows": [
    ["given", "a universe X of elements, and a family of subsets of X"],
    ["find", "the fewest subsets whose union is all of X"],
    ["examples", "hire the fewest people covering every needed skill · place the fewest towers covering every village"],
    ["complexity", "NP-hard: its decision version is NP-complete"],
    ["vertex cover", "the special case where each element (edge) lies in exactly two sets (its ends)"]]})
s.obj({"id": "gr", "type": "table", "region": "center", "columns": ["greedy rule", ""], "rows": [
    ["repeat", "take the subset covering the most elements not yet covered"],
    ["until", "everything is covered"],
    ["intuition", "the biggest bite each time"],
    ["guarantee?", "not optimal, but provably close: within a factor H(max |S|)"]]})
s.obj({"id": "st", "type": "table", "region": "left", "columns": ["set", "elements"], "rows": [[k, " ".join(map(str, sorted(v)))] for k, v in S.items()]})
s.obj({"id": "tt", "type": "table", "region": "right", "columns": ["round", "picked", "newly covered", "still uncovered"], "rows": [["", "", "", ""] for _ in G]})
s.obj({"id": "gc", "type": "code", "region": "center", "language": "text", "lines": [
    "GREEDY-SET-COVER(X, F)",
    "    U = X;   C = ∅",
    "    while U is not empty",
    "        pick S in F maximising |S ∩ U|",
    "        U = U − S",
    "        C = C ∪ {S}",
    "    return C",
    "",
    "simple version: O(|X| · |F| · min(|X|, |F|));  with care, linear in Σ |S|"]})
s.obj({"id": "hb", "type": "math", "region": "center", "lines": [
    "H(d) = 1 + 1/2 + 1/3 + dots + 1/d approx ln d",
    "\"greedy uses at most \" H(max |S|) \" times the optimal number of sets\"",
    "\"our example: \" max |S| = 6, quad H(6) approx 2.45: quad 4 <= 2.45 times 3",
    "\"overall: \" rho <= ln |X| + 1",
    "\"no polynomial algorithm does much better, unless P = NP\""]})
s.obj({"id": "vc", "type": "table", "region": "center", "columns": ["vertex cover as set cover", ""], "rows": [
    ["universe", "the edges"],
    ["one set per vertex", "the edges touching it"],
    ["a set cover", "a set of vertices touching every edge: a vertex cover"],
    ["greedy set cover", "= take the vertex covering the most uncovered edges: the max-degree heuristic"],
    ["compare", "vertex cover's own algorithm guarantees 2; general set cover only ln n"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["X = {1, 2, 3, 4, 5, 6};  A = {1, 2, 3, 4},  B = {1, 2, 5},  C = {3, 4, 6}"],
    ["a) run GREEDY-SET-COVER"],
    ["b) an optimal cover"],
    ["c) is the result within the H(max |S|) bound?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "A covers 4 new · then B covers 5, C covers 6 (1 each)", "A, B, C: 3 sets"],
    ["b)", "B ∪ C = {1, 2, 3, 4, 5, 6}", "B, C: 2 sets"],
    ["c)", "max |S| = 4: H(4) = 1 + 1/2 + 1/3 + 1/4 ≈ 2.08;  3 ≤ 2.08 × 2", "yes: ratio 1.5"]]})

s.scene("intro")
s.step("A company needs a team that covers a list of skills, and each candidate has some of them. What is the smallest team? That is set cover, one of the most widely applied NP-hard problems. A simple greedy rule gets provably close.", [s.head("Approximation: set cover")])
s.step("Here are the seven stages.", show("stages"))
s.step("The problem, the greedy rule, a full trace, and the algorithm.", [hl("stages[0..=3]")])
s.step("Then how close greedy gets, the link to vertex cover, and an exam question.", [hl("stages[4..=6]")])

s.scene("pb")
s.step("Stage 1: we have a universe of elements, and a family of subsets.", [s.head("Stage 1 of 7: the problem")] + hide("stages") + show("pb") + [hl("pb[0]")])
s.step("We want the fewest subsets whose union is the whole universe.", [hl("pb[1]")])
s.step("Skills and candidates, villages and towers, test cases and requirements: the same structure everywhere.", [hl("pb[2]")])
s.step("It is NP-hard. And vertex cover is a special case: each edge is an element, covered by the sets of its two ends.", [hl("pb[3..=4]"), s.take("fewest sets covering everything")])
s.step("Brute force tries every collection of subsets: with 6 subsets, 64 collections; with 50, over a thousand million million.", [hl("pb[1]")])

s.scene("gr")
s.step("Stage 2: the greedy rule. Take the subset that covers the most elements not yet covered.", [s.head("Stage 2 of 7: the greedy rule"), s.untake()] + hide("pb") + show("gr") + [hl("gr[0]")])
s.step("Repeat until everything is covered.", [hl("gr[1]")])
s.step("The biggest bite each time. It is not always optimal, but it comes with a guarantee we will prove.", [hl("gr[2..=3]"), s.take("most new elements first")])

s.scene("trace")
s.step("Stage 3: twelve elements, 1 to 12, and six subsets.", [s.head("Stage 3 of 7: a trace"), s.untake()] + hide("gr") + show("st", "tt"))
say = ["Round 1: S1 covers 6 elements, more than any other. Take it: 1 to 6 are covered.",
       "Round 2: count only new elements. S4 now covers 7, 8 and 11: three. S2, S3 and S5 cover two each. Take S4.",
       "Round 3: S5 adds 9 and 12. The others add at most one. Take S5.",
       "Round 4: only 10 remains. S3 and S6 both contain it; take S3. Everything is covered with 4 sets."]
U = set(range(1, 13))
for k, (nm, new) in enumerate(G):
    U -= set(new); i = list(S).index(nm)
    acts = [hl(f"st[{i}]"), mk(f"st[{i}]", 0.5), st(f"tt[{k}][0]", str(k + 1)), st(f"tt[{k}][1]", nm, 0.2), st(f"tt[{k}][2]", " ".join(map(str, new)), 0.4), st(f"tt[{k}][3]", " ".join(map(str, sorted(U))) or "none", 0.6), hl(f"tt[{k}]")]
    if k == len(G) - 1: acts.append(s.take("greedy: 4 sets"))
    s.step(say[k], acts)
s.step("At the last round, S3 and S6 tied; choosing S6 would also give 4 sets. Ties never change the guarantee.", [hl("st[5]")])
s.step("But S3, S4 and S5 alone cover everything: 3 sets. Greedy's first, biggest choice, S1, turned out not to be needed.", [hl("st[2]"), hl("st[3]", 0.3), hl("st[4]", 0.6), s.take("greedy 4 · optimal 3")])

s.scene("algo")
s.step("Stage 4: GREEDY-SET-COVER keeps U, the uncovered elements.", [s.head("Stage 4 of 7: the algorithm"), s.untake()] + hide("st", "tt") + show("gc") + [ml("gc", 1, 2)])
s.step("While U is not empty, pick the subset with the largest intersection with U.", [ml("gc", 3, 4)])
s.step("Remove its elements from U and add it to the cover.", [ml("gc", 5, 7)])
s.step("Done simply, each round scans all subsets: polynomial. With bucket queues it can be made linear in the total size of the subsets.", [ml("gc", 9, 9), s.take("polynomial time")])
s.step("The trick for speed: keep, for every subset, a count of its uncovered elements. When an element becomes covered, decrease the count of each subset containing it. Then the best subset is just the one with the largest count.", [ml("gc", 4, 4)])

s.scene("hb")
s.step("Stage 5: how far from optimal? Define H of d, the harmonic number: 1 plus a half plus a third, up to 1 over d. It grows like the natural log of d.", [s.head("Stage 5 of 7: the bound"), s.untake()] + hide("gc") + show("hb") + [hl("hb[0]")])
s.step("Cormen proves greedy uses at most H of the largest subset size, times the optimal number. The idea: charge each chosen set's cost to the elements it newly covers; an optimal set's elements together are charged at most H of its size.", [rv("hb[1]"), hl("hb[1]")])
s.step("In our example, the largest set has 6 elements, H of 6 is about 2.45, and indeed 4 is at most 2.45 times 3.", [rv("hb[2]"), hl("hb[2]")])
s.step("In our trace, S1 cost 1 set for 6 new elements: each element was charged a sixth. S4 charged a third to each of 7, 8 and 11; S5 a half each to 9 and 12; S3 a whole 1 to element 10. The charges add up to the 4 sets used.", [hl("hb[1]")])
s.step("In general the ratio is at most log of the universe size, plus 1: a ratio that grows, but slowly.", [rv("hb[3]"), hl("hb[3]")])
s.step("Remarkably, that is essentially the best possible: no polynomial algorithm can guarantee much better unless P equals NP.", [rv("hb[4]"), hl("hb[4]"), s.take("ρ ≤ H(max |S|) ≤ ln |X| + 1")])

s.scene("vc")
s.step("Stage 6: vertex cover as set cover. The universe is the edges, and each vertex gives the set of edges touching it.", [s.head("Stage 6 of 7: vertex cover again"), s.untake()] + hide("hb") + show("vc") + [hl("vc[0..=1]")])
s.step("A set cover is then exactly a vertex cover.", [hl("vc[2]")])
s.step("And greedy set cover becomes: take the vertex touching the most uncovered edges. That is the max-degree rule from the last video.", [hl("vc[3]")])
s.step("So the max-degree heuristic inherits set cover's log n guarantee, which is why it can be log n times worse on bad graphs.", [hl("vc[3]")])
s.step("General set cover can only promise log n; but vertex cover, with its special structure, gets a factor of 2 from the take-both-ends algorithm.", [hl("vc[4]"), s.take("structure buys a better ratio")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("vc") + show("q") + [hl("q[0]")])
s.step("Run greedy, find an optimal cover, and check the bound. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: A covers 4 elements, the most. Then B and C each add just one new element: B adds 5, C adds 6. Greedy uses 3 sets.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: B and C together cover 1 to 6: 2 sets suffice.", [hl("qa[1]")])
s.step("c: the largest set has 4 elements. H of 4 is about 2.08, and 3 is at most 2.08 times 2. Within the bound: the actual ratio is 1.5.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("The usual slip: counting all of a set's elements in later rounds. Greedy compares only the elements still uncovered.", [s.take("count only new elements")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Set cover picks the fewest subsets covering a universe. Greedy repeatedly takes the subset with the most uncovered elements.", [hl("stages[0..=3]")])
s.step("It is within H of the largest set size, about log n, of optimal, and vertex cover is the special case where structure gives a factor of 2.", [hl("stages[4..=5]")])
s.step("Next video: the travelling salesman. A tour at most twice the optimum, built from a minimum spanning tree.", [mk("stages[0..=6]"), s.take("Next: approximating TSP")])

s.save("/home/claude/playlist/dsa5/d5v6.json")

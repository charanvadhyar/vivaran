"""DSA Module 5, video 3: Circuit satisfiability and 3-CNF satisfiability."""
import sys, itertools
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa5")
from common import Script
from h import *

def circ(x1, x2, x3):
    w1 = x1 and x2; w2 = not x3; w3 = x2 or x3; return int(bool(w1 and w2 and w3))
assert [a for a in itertools.product([0, 1], repeat=3) if circ(*a)] == [(1, 1, 0)]
C = [(1, -2, 3), (-1, 2, 3), (-1, -2, -3), (1, 2, -3)]
sat = lambda F, a: all(any((a[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in F)
assert sat(C, (1, 1, 0)) and not sat(C, (1, 1, 1)) and sum(sat(C, a) for a in itertools.product([0, 1], repeat=3)) == 4
EF = [(1, 2, -3), (-1, -2, 3), (-1, 2, -3), (1, -2, 3)]
assert sat(EF, (1, 0, 0))
# Tseitin AND gate clauses equivalent to y = x1 & x2
for y, a, b in itertools.product([0, 1], repeat=3):
    cl = [(not y) or a, (not y) or b, y or (not a) or (not b)]
    assert all(cl) == (y == (a and b))
assert 2 ** 50 > 10 ** 15

s = Script("Circuit-SAT and 3-CNF-SAT")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Boolean circuits"],
    [2, "CIRCUIT-SAT is in NP, and NP-hard"],
    [3, "From circuits to formulas: SAT"],
    [4, "Conjunctive normal form and 3-CNF"],
    [5, "Checking a 3-CNF certificate"],
    [6, "Two literals are easy, three are hard"],
    [7, "Exam question"]]})
s.obj({"id": "cg", "type": "diagram", "region": "left", "layout": "layers", "directed": True,
       "nodes": [{"id": "x1", "label": "x1"}, {"id": "x2", "label": "x2"}, {"id": "x3", "label": "x3"},
                 {"id": "g1", "label": "AND"}, {"id": "g2", "label": "NOT"}, {"id": "g3", "label": "OR"}, {"id": "out", "label": "AND"}],
       "edges": [{"from": "x1", "to": "g1"}, {"from": "x2", "to": "g1"}, {"from": "x3", "to": "g2"}, {"from": "x2", "to": "g3"}, {"from": "x3", "to": "g3"},
                 {"from": "g1", "to": "out"}, {"from": "g2", "to": "out"}, {"from": "g3", "to": "out"}]})
s.obj({"id": "ct", "type": "table", "region": "right", "columns": ["boolean circuit", ""], "rows": [
    ["gates", "AND, OR, NOT, wired without loops"],
    ["inputs", "x1, x2, x3: each 0 or 1"],
    ["here", "out = (x1 ∧ x2) ∧ ¬x3 ∧ (x2 ∨ x3)"],
    ["satisfiable?", "is there an input making the output 1?"],
    ["answer", "x1 = 1, x2 = 1, x3 = 0: the only one of 8"]]})
s.obj({"id": "np", "type": "table", "region": "center", "columns": ["CIRCUIT-SAT", ""], "rows": [
    ["in NP", "certificate: the input values; evaluate the gates in order: O(size of circuit)"],
    ["NP-hard (Cook–Levin, 1971)", "any NP verifier, run for polynomial time, can be wired as a polynomial-size circuit"],
    ["so", "\"does some certificate make the verifier say yes?\" becomes \"is this circuit satisfiable?\""],
    ["CIRCUIT-SAT", "the first NP-complete problem: the root of the tree"]]})
s.obj({"id": "ts", "type": "table", "region": "center", "columns": ["CIRCUIT-SAT ≤p SAT: one variable per wire", "clauses saying the gate works"], "rows": [
    ["y = x1 ∧ x2", "(¬y ∨ x1) ∧ (¬y ∨ x2) ∧ (y ∨ ¬x1 ∨ ¬x2)"],
    ["y = x1 ∨ x2", "(y ∨ ¬x1) ∧ (y ∨ ¬x2) ∧ (¬y ∨ x1 ∨ x2)"],
    ["y = ¬x", "(y ∨ x) ∧ (¬y ∨ ¬x)"],
    ["the formula", "all gate clauses, AND the output wire"],
    ["size", "a few clauses per gate: polynomial (substituting formulas instead could blow up exponentially)"]]})
s.obj({"id": "cnf", "type": "table", "region": "center", "columns": ["normal forms", ""], "rows": [
    ["literal", "a variable or its negation: x, ¬x"],
    ["clause", "an OR of literals"],
    ["CNF", "an AND of clauses"],
    ["3-CNF", "every clause has exactly 3 distinct literals"],
    ["SAT ≤p 3-CNF-SAT", "rewrite into CNF, split long clauses with new variables, pad short ones"],
    ["3-CNF-SAT", "NP-complete: the usual starting point for reductions"]]})
s.obj({"id": "ck", "type": "table", "region": "center", "columns": ["clause", "x = (1, 1, 0)", "x = (1, 1, 1)"], "rows": [
    ["x1 ∨ ¬x2 ∨ x3", "", ""], ["¬x1 ∨ x2 ∨ x3", "", ""], ["¬x1 ∨ ¬x2 ∨ ¬x3", "", ""], ["x1 ∨ x2 ∨ ¬x3", "", ""]]})
s.obj({"id": "tw", "type": "table", "region": "center", "columns": ["", "2-CNF-SAT", "3-CNF-SAT"], "rows": [
    ["clause size", "2 literals", "3 literals"],
    ["key idea", "(a ∨ b) means ¬a → b and ¬b → a: an implication graph", "no such structure is known"],
    ["algorithm", "strongly connected components: O(n + m)", "best known: exponential"],
    ["class", "P", "NP-complete"],
    ["in practice", "—", "SAT solvers handle millions of clauses on real instances"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) write clauses that force y = x1 ∧ x2, and check them on x1 = 1, x2 = 0"],
    ["b) does x = (1, 0, 0) satisfy (x1 ∨ x2 ∨ ¬x3)(¬x1 ∨ ¬x2 ∨ x3)(¬x1 ∨ x2 ∨ ¬x3)(x1 ∨ ¬x2 ∨ x3)?"],
    ["c) how many assignments must brute force try for 50 variables?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "(¬y ∨ x1)(¬y ∨ x2)(y ∨ ¬x1 ∨ ¬x2)", ""],
    ["a)", "x2 = 0: clause 2 forces ¬y, so y = 0; clauses 1 and 3 then hold", "y = 0 = 1 ∧ 0 ✓"],
    ["b)", "clause 1: x1 ✓ · clause 2: ¬x2 ✓ · clause 3: ¬x3 ✓ · clause 4: x1 ✓", "yes: satisfied"],
    ["c)", "2⁵⁰", "over 10¹⁵ assignments"]]})

s.scene("intro")
s.step("Every NP-completeness proof in the course traces back to one problem: can the inputs of a logic circuit be set so that its output is 1? This video meets that root problem, circuit satisfiability, and its most useful descendant, 3-CNF satisfiability.", [s.head("Circuit-SAT and 3-CNF-SAT")])
s.step("Here are the seven stages.", show("stages"))
s.step("Boolean circuits, why circuit satisfiability is NP-complete, the step to formulas, and conjunctive normal form.", [hl("stages[0..=3]")])
s.step("Then checking a certificate, the gap between two and three literals, and an exam question.", [hl("stages[4..=6]")])

s.scene("circ")
s.step("Stage 1: a boolean circuit is made of AND, OR and NOT gates, wired together without loops.", [s.head("Stage 1 of 7: boolean circuits")] + hide("stages") + show("cg", "ct") + [hl("ct[0]")])
s.step("Its inputs, x1, x2 and x3, are each 0 or 1.", [hl("ct[1]"), hl("cg.x1"), hl("cg.x2", 0.2), hl("cg.x3", 0.4)])
s.step("This one computes x1 and x2, and not x3, and x2 or x3, all joined by a final AND.", [hl("ct[2]"), hl("cg.out")])
s.step("It is satisfiable if some setting of the inputs makes the output 1.", [hl("ct[3]")])
s.step("Try x1 equal 1, x2 equal 1, x3 equal 0: the AND gives 1, the NOT gives 1, the OR gives 1, and the output is 1. Of the 8 possible inputs, this is the only one that works.", [hl("ct[4]"), mk("cg.out", 0.6), s.take("satisfiable: some input gives output 1")])

s.scene("np")
s.step("Stage 2: circuit satisfiability is in NP. The certificate is the input values: evaluate the gates in order and look at the output, in time proportional to the circuit's size.", [s.head("Stage 2 of 7: the first NP-complete problem"), s.untake()] + hide("cg", "ct") + show("np") + [hl("np[0]")])
s.step("And it is NP-hard. Cook and Levin's insight: any NP problem has a polynomial-time verifier, and a computer running that verifier for polynomially many steps can be written out as a polynomial-size circuit.", [hl("np[1]")])
s.step("Then the question, does some certificate make the verifier say yes, becomes exactly: is this circuit satisfiable?", [hl("np[2]")])
s.step("So circuit satisfiability is NP-complete: the root of the family tree.", [hl("np[3]"), s.take("CIRCUIT-SAT: the first NP-complete problem")])
s.step("A year after Cook's paper, Richard Karp used reductions to show 21 famous problems NP-complete, including clique, vertex cover, Hamiltonian cycle and graph colouring. The flood has not stopped since.", [hl("np[3]")])

s.scene("ts")
s.step("Stage 3: now reduce circuits to formulas. Give every wire its own variable, and write clauses that say each gate computes correctly. For an AND gate, y equals x1 and x2:", [s.head("Stage 3 of 7: circuits to formulas"), s.untake()] + hide("np") + show("ts") + [hl("ts[0]")])
s.step("Not y or x1, and not y or x2: if y is 1, both inputs must be 1. And y or not x1 or not x2: if both inputs are 1, y must be 1.", [hl("ts[0]")])
s.step("An OR gate and a NOT gate have similar small sets of clauses.", [hl("ts[1..=2]")])
s.step("The formula is the AND of all these clauses, together with the output variable itself. It is satisfiable exactly when the circuit is.", [hl("ts[3]")])
s.step("A few clauses per gate keeps the formula polynomial in size. Simply substituting each gate's formula into the next could double the size at every level.", [hl("ts[4]"), s.take("one variable per wire, a few clauses per gate")])

s.scene("cnf")
s.step("Stage 4: some vocabulary. A literal is a variable or its negation. A clause is an OR of literals.", [s.head("Stage 4 of 7: CNF and 3-CNF"), s.untake()] + hide("ts") + show("cnf") + [hl("cnf[0..=1]")])
s.step("A formula in conjunctive normal form is an AND of clauses. Our gate clauses are already in this form.", [hl("cnf[2]")])
s.step("In 3-CNF, every clause has exactly three distinct literals.", [hl("cnf[3]")])
s.step("Any formula can be rewritten in 3-CNF with polynomial growth: long clauses are split with new variables, and short ones padded. So SAT reduces to 3-CNF-SAT.", [hl("cnf[4]")])
s.step("3-CNF-SAT is NP-complete, and its rigid, simple shape makes it the favourite starting point for further reductions.", [hl("cnf[5]"), s.take("3-CNF: AND of 3-literal ORs")])

s.scene("ck")
s.step("Stage 5: checking a certificate. Here are four clauses on x1, x2 and x3. Is x equal to 1, 1, 0 a satisfying assignment?", [s.head("Stage 5 of 7: checking a certificate"), s.untake()] + hide("cnf") + show("ck"))
s.step("Clause 1: x1 is 1. True. Clause 2: x2 is 1. True.", [st("ck[0][1]", "x1 ✓"), st("ck[1][1]", "x2 ✓", 0.4), hl("ck[0..=1]")])
s.step("Clause 3: not x3 is 1. True. Clause 4: x1 again. True. Every clause holds: satisfied.", [st("ck[2][1]", "¬x3 ✓"), st("ck[3][1]", "x1 ✓", 0.4), hl("ck[2..=3]")])
s.step("Now try 1, 1, 1. Clauses 1, 2 and 4 hold, but clause 3, not x1 or not x2 or not x3, has all three literals false. One false clause sinks the whole formula.", [st("ck[0][2]", "✓"), st("ck[1][2]", "✓", 0.1), st("ck[2][2]", "all false ✗", 0.3), st("ck[3][2]", "✓", 0.5), hl("ck[2]", 0.3)])
s.step("Checking takes one pass over the clauses: linear time. Finding a satisfying assignment, as far as anyone knows, needs exponential time in the worst case. This formula has 4 satisfying assignments out of 8.", [s.take("check: one pass · find: exponential")])

s.scene("tw")
s.step("Stage 6: with two literals per clause, satisfiability is easy. A clause a or b says: if not a, then b; and if not b, then a.", [s.head("Stage 6 of 7: two against three"), s.untake()] + hide("ck") + show("tw") + [hl("tw[0..=1]")])
s.step("Those implications form a graph, and the formula is unsatisfiable exactly when some variable and its negation imply each other. Strongly connected components find that in linear time.", [hl("tw[2]")])
s.step("With three literals, no such structure is known, and the problem is NP-complete.", [hl("tw[3]")])
s.step("Yet practical SAT solvers routinely solve industrial formulas with millions of clauses. NP-complete describes the worst case, not every case.", [hl("tw[4]"), s.take("2-CNF ∈ P · 3-CNF NP-complete")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("tw") + show("q") + [hl("q[0]")])
s.step("Write and test the clauses for an AND gate, check a certificate, and count brute-force assignments. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: not y or x1; not y or x2; y or not x1 or not x2.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("With x1 equal 1 and x2 equal 0: clause 2, not y or x2, can only hold if y is 0. Then clause 1 holds, and clause 3 holds through not x2. So y is 0, which is 1 and 0. Correct.", [hl("qa[1]")])
s.step("b: clause 1 holds through x1; clause 2 through not x2; clause 3 through not x3; clause 4 through x1. Satisfied.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("c: 2 to the 50, over a thousand million million assignments.", [hl("qa[3]")])
s.step("The usual slip: thinking one true clause is enough. In CNF every clause must be true; in each clause, one true literal is enough.", [s.take("every clause, at least one literal")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Circuit satisfiability is in NP, and Cook and Levin showed every NP problem reduces to it: the first NP-complete problem.", [hl("stages[0..=2]")])
s.step("One variable per wire turns circuits into formulas, and formulas into 3-CNF. Checking a 3-CNF certificate is linear; with two literals per clause the whole problem is easy.", [hl("stages[3..=5]")])
s.step("Next video: from formulas to graphs. Cliques and independent sets.", [mk("stages[0..=6]"), s.take("Next: independent set and clique")])

s.save("/home/claude/playlist/dsa5/d5v3.json")

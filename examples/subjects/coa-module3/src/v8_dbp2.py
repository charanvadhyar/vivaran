"""Module 3, video 8: dynamic branch prediction, part 2: correlating (m,n) predictors and tournament predictors."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from bp import corr11, onebit_per

SEQ = [('b1', 'T'), ('b2', 'T'), ('b1', 'N'), ('b2', 'N')] * 2
C, _ = corr11(SEQ); O = onebit_per(SEQ)
assert [p for _, p, _ in C] == list('NNNNTTNN') and sum(not c for *_, c in C) == 2
assert [h for h, _, _ in C] == list('NTTNNTTN')
assert sum(not c for _, c in O) == 8
EX = [('b1', 'T'), ('b2', 'T'), ('b1', 'N'), ('b2', 'N'), ('b1', 'N'), ('b2', 'N'), ('b1', 'T'), ('b2', 'T')]
CE, _ = corr11(EX); OE = onebit_per(EX)
assert sum(not c for *_, c in CE) == 4 and sum(not c for _, c in OE) == 6
assert [p for p, _ in OE] == list('NNTTNNNN') and [i + 1 for i, (_, c) in enumerate(OE) if not c] == [1, 2, 3, 4, 7, 8]
assert [i + 1 for i, (*_, c) in enumerate(CE) if not c] == [1, 2, 5, 7]
assert True and [p for _, p, _ in CE] == list('NNNNTNNT')
assert 2 ** 0 * 2 * 4096 == 8192 == 2 ** 2 * 2 * 1024
assert 4096 * 2 + 4096 * 2 + 1024 * 10 + 1024 * 3 == 29 * 1024
assert 2 ** 2 * 2 * 1024 == 8192 and 2 ** 3 * 2 * 512 == 8192 and 8192 // (2 ** 2 * 2) == 1024

s = Script("Dynamic branch prediction, part 2")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Branches that depend on other branches"],
    [2, "The correlating (m, n) predictor"],
    [3, "Tracing a (1, 1) predictor"],
    [4, "Counting bits"],
    [5, "Tournament predictors"],
    [6, "A real one: the Alpha 21264"],
    [7, "Exam question"]]})
s.obj({"id": "cc", "type": "code", "region": "center", "language": "c", "lines": [
    "if (aa == 2)  aa = 0;   // b1",
    "if (bb == 2)  bb = 0;   // b2",
    "if (aa != bb) { ... }   // b3"]})
s.obj({"id": "ccx", "type": "table", "region": "center", "columns": ["if", "then"], "rows": [
    ["b1 and b2 both set their variable to 0", "aa = bb = 0, so b3's test is false: certain"],
    ["a predictor that sees only b3's own past", "can never learn this"]]})
s.obj({"id": "mn", "type": "table", "region": "center", "columns": ["(m, n) predictor", "meaning"], "rows": [
    ["global history", "an m-bit shift register: the outcomes of the last m branches, any branch"],
    ["per entry", "2^m separate n-bit counters"],
    ["prediction", "the branch address picks the entry; the history picks the counter inside it"],
    ["(0, 2)", "no history: the plain 2-bit table from part 1"]]})
s.obj({"id": "dc", "type": "code", "region": "center", "language": "c", "lines": [
    "if (d == 0) d = 1;   // b1: taken when d != 0",
    "if (d == 1) ...      // b2: taken when d != 1"]})
s.obj({"id": "dx", "type": "table", "region": "center", "columns": ["d", "b1", "d after b1", "b2"], "rows": [
    ["2", "T", "2", "T"], ["0", "N", "1", "N"]]})
s.obj({"id": "tr", "type": "table", "region": "center", "columns": ["execution", "1", "2", "3", "4", "5", "6", "7", "8"], "rows": [
    ["branch", *[b for b, _ in SEQ]],
    ["outcome", *[o for _, o in SEQ]],
    ["1-bit predicts", "", "", "", "", "", "", "", ""],
    ["last outcome (history)", "", "", "", "", "", "", "", ""],
    ["(1,1) predicts", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "bits", "type": "math", "region": "center", "lines": [
    "\"bits\" = 2^m times n times \"entries\"",
    "(0, 2) \"with 4K entries:\" quad 2^0 times 2 times 4096 = 8 \"K bits\"",
    "(2, 2) \"with the same 8K bits:\" quad 8192 / (2^2 times 2) = 1024 \"entries\"",
    "\"gshare: index with branch address XOR global history, to spread entries\""]})
s.obj({"id": "tn", "type": "table", "region": "center", "columns": ["part", "role"], "rows": [
    ["local predictor", "each branch's own recent history: good for loops"],
    ["global predictor", "the last few branches' outcomes: good for correlated branches"],
    ["selector", "a 2-bit counter per entry: which of the two to believe"],
    ["selector update", "one right and one wrong: move toward the right one · both equal: no change"]]})
s.obj({"id": "alpha", "type": "table", "region": "center", "columns": ["Alpha 21264 part", "size", "bits"], "rows": [
    ["selector", "4K × 2-bit counters, indexed by 12 bits of global history", "8K"],
    ["global predictor", "4K × 2-bit counters, same index", "8K"],
    ["local histories", "1K × 10-bit, indexed by branch address", "10K"],
    ["local predictor", "1K × 3-bit counters, indexed by the local history", "3K"],
    ["total", "", "29K bits"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["a (2, 2) predictor with 1K entries", "a) its size in bits"],
    ["the same bit budget, m = 3, n = 2", "b) how many entries"],
    ["b1, b2: T T · N N · N N · T T (history starts N, all counters N)", "c) mispredictions: 1-bit, and (1, 1)"]]})
s.obj({"id": "qt", "type": "table", "region": "center", "columns": ["execution", "1", "2", "3", "4", "5", "6", "7", "8"], "rows": [
    ["branch", *[b for b, _ in EX]],
    ["outcome", *[o for _, o in EX]],
    ["1-bit predicts", *[p for p, _ in OE]],
    ["history", *[h for h, _, _ in CE]],
    ["(1,1) predicts", *[p for _, p, _ in CE]]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 2^2 times 2 times 1024 = 8192 \"bits\" = 8 \"K bits\"",
    "\"b)\" quad 8192 / (2^3 times 2) = 512 \"entries\"",
    "\"c)\" quad \"1-bit: 6 wrong of 8\" quad \"(1, 1): 4 wrong of 8\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]
go = lambda t, n: {"action": "goto_line", "target": t, "line": n}

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("A 2-bit counter only looks at one branch's own past. But branches talk to each other: what one branch did often decides what the next will do. This video teaches the predictor to listen.", [s.head("Dynamic branch prediction, part 2")])
s.step("Here are the seven stages.", show("stages"))
s.step("Correlated branches, the (m, n) predictor, a trace, and counting its bits.", [hl("stages[0..=3]")])
s.step("Then tournament predictors, a real one from the Alpha 21264, and an exam question.", [hl("stages[4..=6]")])

# ---------------------------------------------------------------- correlation
s.scene("corr")
s.step("Stage 1: a fragment of real code, from the textbook. Three branches.", [s.head("Stage 1 of 7: correlated branches")] + hide("stages") + show("cc") + [go("cc", 1)])
s.step("If the first two both set their variable to 0, then aa equals bb, and the third test must be false. Its outcome is certain, given the first two.", [go("cc", 3)])
s.step("Put as a rule, in a table.", hide("cc") + show("ccx") + [hl("ccx[0]")])
s.step("A predictor that looks only at the third branch's own history can never learn that. It has to see the other branches.", [hl("ccx[1]"), s.take("a branch's outcome can depend on earlier branches")])

# ---------------------------------------------------------------- (m,n)
s.scene("mn")
s.step("Stage 2: the correlating, or two-level, predictor. It keeps a global history: the outcomes of the last m branches, whichever branches they were, in a shift register.", [s.head("Stage 2 of 7: the (m, n) predictor"), s.untake()] + hide("ccx") + show("mn") + [hl("mn[0]")])
s.step("Each table entry holds not one counter, but 2 to the m counters, each n bits wide.", [hl("mn[1]")])
s.step("To predict, the branch address picks the entry, and the global history picks the counter inside it. So the same branch gets a different prediction depending on what just happened.", [hl("mn[2]")])
s.step("In this notation the plain 2-bit table from part 1 is a (0, 2) predictor: no history at all.", [hl("mn[3]"), s.take("address picks the entry · history picks the counter")])

# ---------------------------------------------------------------- trace
s.scene("trace")
s.step("Stage 3: a trace. Two branches. b1 is taken when d is not 0, and b2 is taken when d is not 1.", [s.head("Stage 3 of 7: tracing a (1, 1) predictor"), s.untake()] + hide("mn") + show("dc"))
s.step("If d is 2: b1 is taken, d stays 2, and b2 is taken too. If d is 0: b1 falls through and sets d to 1, so b2 falls through as well. Let d alternate 2, 0, 2, 0.", hide("dc") + show("dx") + [hl("dx[0]"), hl("dx[1]", 0.5)])
s.step("So the outcomes go: b1 taken, b2 taken, b1 not, b2 not, and so on. Every branch flips each time it runs.", hide("dx") + show("tr") + [hl("tr[0..=1]")])
s.step("A 1-bit predictor per branch, starting at not taken, predicts the last outcome of that same branch, and is wrong every single time. 8 out of 8.", [st(f"tr[2][{k + 1}]", p, round(0.1 * k, 2)) for k, (p, _) in enumerate(O)] + [hl("tr[2]", 0.9)])
s.step("Now a (1, 1) predictor. One bit of global history: the outcome of the last branch, any branch. Each branch has two 1-bit predictors, one for when that history was not taken, one for when it was taken.", [st(f"tr[3][{k + 1}]", h, round(0.1 * k, 2)) for k, (h, _, _) in enumerate(C)])
s.step("The first two executions are wrong, while the predictors warm up. b1 learns: after a not taken, I am taken. b2 learns: after a taken, I am taken.", [st("tr[4][1]", C[0][1]), st("tr[4][2]", C[1][1], 0.3), hl("tr[4][1]", 0.5), hl("tr[4][2]", 0.6)])
s.step("From then on, every prediction is right. b2 simply copies what b1 just did, and the history bit tells it.", [st(f"tr[4][{k + 1}]", C[k][1], round(0.1 * (k - 2), 2)) for k in range(2, 8)] + [mk("tr[4][3]", 0.7), mk("tr[4][8]", 0.8)])
s.step("2 wrong out of 8, against 8 out of 8. And in the long run, none.", [s.take("one bit of global history turned 100% wrong into 0%")])

# ---------------------------------------------------------------- bits
s.scene("bits")
s.step("Stage 4: what does it cost? Each entry has 2 to the m counters of n bits.", [s.head("Stage 4 of 7: counting bits"), s.untake()] + hide("tr") + show("bits") + [hl("bits[0]")])
s.step("The plain 2-bit table with 4K entries: 1, times 2, times 4096. 8K bits.", rv("bits", 1))
s.step("A (2, 2) predictor with the same 8K bits: each entry needs 4 times 2 bits, so only 1024 entries. The textbook's studies found it still beats the bigger plain table.", rv("bits", 2))
s.step("A popular variation, gshare, combines the branch address and the global history with an XOR to form one index, which spreads the entries more evenly.", rv("bits", 3) + [s.take("bits = 2^m × n × entries")])

# ---------------------------------------------------------------- tournament
s.scene("tour")
s.step("Stage 5: some branches are best predicted from their own past, like loops. Others from the global past, like correlated ifs. Why not use both?", [s.head("Stage 5 of 7: tournament predictors"), s.untake()] + hide("bits") + show("tn"))
s.step("A tournament predictor runs a local predictor, built on each branch's own history.", [hl("tn[0]")])
s.step("And a global predictor, built on the recent outcomes of all branches.", [hl("tn[1]")])
s.step("A selector, one more 2-bit counter per entry, decides which of the two to believe for this branch.", [hl("tn[2]")])
s.step("After the outcome is known: if one predictor was right and the other wrong, the selector moves one step toward the right one. If both were right or both wrong, it stays. So each branch drifts to the predictor that suits it.", [hl("tn[3]")])
s.step("An example. A selector at 10 leans toward the global predictor. On a branch where global is wrong and local is right, it drops to 01, now leaning local. If both are right next time, it stays at 01.", [mk("tn[2]")])
s.step("A second local win takes it to 00, strongly local. It would take two global wins in a row to swing it back. The same saturating trick as the 2-bit counter, applied to the choice.", [mk("tn[3]"), s.take("tournament: local + global + a selector")])

# ---------------------------------------------------------------- alpha
s.scene("alpha")
s.step("Stage 6: a real one, from the Alpha 21264 of 1998.", [s.head("Stage 6 of 7: the Alpha 21264"), s.untake()] + hide("tn") + show("alpha"))
s.step("The selector: 4K 2-bit counters, indexed by the last 12 branch outcomes. 8K bits.", [hl("alpha[0]")])
s.step("The global predictor: another 4K 2-bit counters, with the same index. 8K bits.", [hl("alpha[1]")])
s.step("The local side has two levels. 1K entries of 10-bit history, one per branch address. Each history then indexes 1K 3-bit counters.", [hl("alpha[2]"), hl("alpha[3]", 0.5)])
s.step("29K bits in all, and much more accurate than any single predictor of the same size. Modern processors go further, with tagged predictors that use several history lengths at once, but the idea is the same.", [hl("alpha[4]"), s.take("8K + 8K + 10K + 3K = 29K bits")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("alpha") + show("q"))
s.step("The size of a (2, 2) predictor with 1K entries. How many entries a (3, 2) predictor gets in the same budget. And mispredictions for a 1-bit and a (1, 1) predictor on this sequence. Pause and work it out.", [hl("q[0]"), hl("q[1]", 0.3), hl("q[2]", 0.6)])
s.step("a: 4 counters of 2 bits per entry, times 1024: 8K bits. b: 8 counters of 2 bits is 16 bits per entry, and 8192 over 16 is 512 entries.", hide("q") + show("qa") + [hl("qa[0]")] + rv("qa", 1))
s.step("c: the 1-bit predictors, starting at not taken, follow each branch's own last outcome.", hide("qa") + show("qt") + [hl("qt[2]")])
s.step("They are wrong at executions 1 to 4, right at 5 and 6, and wrong again at 7 and 8. 6 of 8.", [hl("qt[2][1]"), hl("qt[2][2]", 0.1), hl("qt[2][3]", 0.2), hl("qt[2][4]", 0.3), hl("qt[2][7]", 0.6), hl("qt[2][8]", 0.7)])
s.step("The (1, 1) predictor is wrong at 1 and 2 while it warms up, then right at 3 and 4. At 5, b1 after a not taken uses the entry trained to taken: wrong. b2 at 6 gets it right. At 7, b1 after not taken again: the entry now says not taken, wrong. b2 at 8, right. 4 of 8.", [hl("qt[4][1]"), hl("qt[4][2]", 0.1), hl("qt[4][5]", 0.4), hl("qt[4][7]", 0.7), mk("qt[4][6]", 0.5), mk("qt[4][8]", 0.8)])
s.step("Notice that b2 is always right once warmed up: it just copies b1. b1 has no pattern to learn. The usual slip: using the branch's own last outcome as the history, instead of the last outcome of any branch.", [s.take("global history = the last branches, whichever they were")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qt") + show("stages"))
s.step("Branches correlate. An (m, n) predictor lets the last m outcomes pick among 2 to the m counters per entry, at 2 to the m, times n, times entries bits.", [hl("stages[0..=3]")])
s.step("Tournament predictors run a local and a global predictor, and a selector learns which to trust for each branch.", [hl("stages[4..=5]")])
s.step("Next video: hardware speculation and the reorder buffer, which lets the machine act on these predictions before it knows they are right.", [mk("stages[0..=6]"), s.take("Next: speculation and the reorder buffer")])

s.save("/home/claude/playlist/m3/m3v8.json")

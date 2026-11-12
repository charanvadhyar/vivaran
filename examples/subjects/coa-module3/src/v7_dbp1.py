"""Module 3, video 7: dynamic branch prediction, part 1: BHT, 1-bit and 2-bit predictors, the BTB."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from bp import one_bit, two_bit

loop = ('T' * 9 + 'N') * 2
assert sum(not c for _, c in one_bit(loop, 'T')) == 3 and sum(not c for *_, c in two_bit(loop, 3)[0]) == 2
tr = 'TTTN' * 2
R1 = one_bit(tr, 'T'); R2, _ = two_bit(tr, 3)
assert [p for p, _ in R1] == list('TTTTNTTT') and sum(not c for _, c in R1) == 3
assert [s for s, _, _ in R2] == [3, 3, 3, 3, 2, 3, 3, 3] and sum(not c for *_, c in R2) == 2
ex = 'TTN' * 3
E1 = one_bit(ex, 'N'); E2, fin = two_bit(ex, 1)
assert [p for p, _ in E1] == list('NTTNTTNTT') and sum(not c for _, c in E1) == 6
assert [s for s, _, _ in E2] == [1, 2, 3, 2, 3, 3, 2, 3, 3] and sum(not c for *_, c in E2) == 4 and fin == 2
assert round(0.9 * 0.1 * 2 + 0.1 * 0.6 * 2, 2) == 0.30
assert round(0.95 * 0.1 * 2 + 0.05 * 0.7 * 2, 2) == 0.26 and 1024 * 2 // 8 == 256 and 4096 * 2 // 8 == 1024

ST = {3: "11", 2: "10", 1: "01", 0: "00"}
s = Script("Dynamic branch prediction, part 1")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why predict while running"],
    [2, "The branch history table"],
    [3, "The 1-bit predictor and its weakness"],
    [4, "The 2-bit saturating counter"],
    [5, "Tracing both on a loop"],
    [6, "The branch target buffer"],
    [7, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["problem", "why it matters"], "rows": [
    ["a branch's behaviour changes with the data", "a fixed guess cannot follow it"],
    ["deep pipelines and multiple issue", "a wrong guess throws away many instructions"],
    ["Tomasulo needs a steady stream of instructions", "stopping at every branch wastes its window"]]})
s.obj({"id": "bht", "type": "table", "region": "left", "columns": ["index", "prediction"], "rows": [
    ["000…000", "T"], ["000…001", "N"], ["…", "…"], ["111…111", "T"]]})
s.obj({"id": "bhm", "type": "math", "region": "right", "lines": [
    "\"index\" = \"low bits of the branch address\"",
    "4096 \"entries\" = 2^12 : quad \"PC bits\" 13 \"to\" 2",
    "\"no tag: two branches may share an entry\"",
    "\"size\" = 4096 times 2 \"bits\" = 1 \"KB\""]})
s.obj({"id": "ob", "type": "table", "region": "center", "columns": ["1-bit, loop of 10", "what happens"], "rows": [
    ["rule", "predict whatever the branch did last time"],
    ["last iteration", "predicted T, actually N: wrong"],
    ["first iteration of the next run", "predicted N, actually T: wrong again"],
    ["result", "2 wrong per 10: only 80% right"]]})
s.obj({"id": "fsm", "type": "diagram", "region": "center", "layout": "layers", "direction": "right",
       "nodes": [{"id": "s3", "label": "11: strong T"}, {"id": "s2", "label": "10: weak T"},
                 {"id": "s1", "label": "01: weak N"}, {"id": "s0", "label": "00: strong N"}],
       "edges": [{"from": "s3", "to": "s2", "label": "N"}, {"from": "s2", "to": "s1", "label": "N"}, {"from": "s1", "to": "s0", "label": "N"}]})
s.obj({"id": "fsx", "type": "table", "region": "center", "columns": ["2-bit counter rule", "effect"], "rows": [
    ["taken: count up (stop at 11)", "not taken: count down (stop at 00)"],
    ["predict taken in 11 and 10", "predict not taken in 01 and 00"],
    ["one odd outcome", "moves only to the weak state: the prediction stays"],
    ["on the loop of 10", "wrong only at the exit: 90% right"]]})
s.obj({"id": "tr", "type": "table", "region": "center", "columns": ["branch execution", "1", "2", "3", "4", "5", "6", "7", "8"], "rows": [
    ["outcome", *list(tr)],
    ["1-bit predicts", "", "", "", "", "", "", "", ""],
    ["2-bit state", "", "", "", "", "", "", "", ""],
    ["2-bit predicts", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "btb", "type": "table", "region": "center", "columns": ["BTB entry", "holds"], "rows": [
    ["tag", "the full address of a branch (it is a cache: no aliasing)"],
    ["predicted target", "where to fetch next if taken"],
    ["looked up", "in the fetch stage, with the address of the instruction being fetched"],
    ["hit, predicted taken", "fetch from the target in the very next cycle: no penalty"]]})
s.obj({"id": "btp", "type": "table", "region": "center", "columns": ["in BTB?", "prediction", "actual", "penalty"], "rows": [
    ["yes", "taken", "taken", "0"],
    ["yes", "taken", "not taken", "2"],
    ["no", "–", "taken", "2"],
    ["no", "–", "not taken", "0"]]})
s.obj({"id": "btm", "type": "math", "region": "center", "lines": [
    "\"BTB hit rate 90% · its predictions 90% right · 60% of the others taken\"",
    "\"penalty\" = 0.9 times 0.1 times 2 + 0.1 times 0.6 times 2 = 0.18 + 0.12 = 0.30 \"cycles per branch\""]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["one branch's outcomes: T T N T T N T T N", "a) mispredictions, 1-bit starting at N"],
    ["", "b) mispredictions, 2-bit starting at 01"],
    ["a BHT of 1024 entries, 4-byte instructions", "c) index bits, and the table size"],
    ["BTB hit rate 95%, accuracy 90%, 70% of misses taken, penalty 2", "d) penalty per branch"]]})
s.obj({"id": "qt", "type": "table", "region": "center", "columns": ["execution", "1", "2", "3", "4", "5", "6", "7", "8", "9"], "rows": [
    ["outcome", *list(ex)],
    ["1-bit predicts", *[p for p, _ in E1]],
    ["2-bit state", *[ST[x] for x, _, _ in E2]],
    ["2-bit predicts", *[p for _, p, _ in E2]]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 6 \"of\" 9 \"wrong\" quad \"b)\" quad 4 \"of\" 9 \"wrong, ending in state 10\"",
    "\"c)\" quad 1024 = 2^10 : quad \"PC bits\" 11 \"to\" 2 quad 1024 times 2 \"bits\" = 256 \"bytes\"",
    "\"d)\" quad 0.95 times 0.1 times 2 + 0.05 times 0.7 times 2 = 0.19 + 0.07 = 0.26 \"cycles\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Tomasulo's machine can look far ahead, but only if it knows where the program is going. Every branch is a fork. Dynamic predictors learn each branch's habits while the program runs.", [s.head("Dynamic branch prediction, part 1")])
s.step("Here are the seven stages.", show("stages"))
s.step("Why predict at run time, the branch history table, and the 1-bit and 2-bit predictors.", [hl("stages[0..=3]")])
s.step("Then a trace of both on a loop, the branch target buffer, and an exam question.", [hl("stages[4..=6]")])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: three reasons static prediction is not enough.", [s.head("Stage 1 of 7: why predict while running")] + hide("stages") + show("why"))
s.step("A branch's behaviour depends on the data. A fixed guess cannot follow a branch that changes its mind.", [hl("why[0]")])
s.step("Deep pipelines that issue several instructions per cycle throw away a lot of work on every wrong guess.", [hl("why[1]")])
s.step("And dynamic scheduling only helps if instructions keep flowing past branches.", [hl("why[2]"), s.take("the deeper and wider the machine, the more prediction matters")])

# ---------------------------------------------------------------- BHT
s.scene("bht")
s.step("Stage 2: the simplest dynamic predictor is a branch history table, or branch prediction buffer. A small memory, indexed by the low bits of the branch's address.", [s.head("Stage 2 of 7: the branch history table"), s.untake()] + hide("why") + show("bht", "bhm") + [hl("bhm[0]")])
s.step("Each entry holds a prediction. In the fetch stage the hardware reads the entry for this branch, and guesses.", [hl("bht[0..=3]")])
s.step("With 4096 entries, the index needs 12 bits. Instructions are 4 bytes, so the lowest 2 address bits are always zero: the index is PC bits 13 down to 2.", rv("bhm", 1))
s.step("There is no tag. Two branches whose addresses share those bits share an entry, and may spoil each other's prediction. That is called aliasing; with a few thousand entries it is rare.", rv("bhm", 2))
s.step("With 2 bits per entry, 4096 entries cost just 1 kilobyte.", rv("bhm", 3) + [s.take("BHT: indexed by low PC bits · no tag · tiny")])

# ---------------------------------------------------------------- 1-bit
s.scene("onebit")
s.step("Stage 3: the 1-bit predictor. Each entry remembers what the branch did last time, and predicts the same again.", [s.head("Stage 3 of 7: the 1-bit predictor"), s.untake()] + hide("bht", "bhm") + show("ob") + [hl("ob[0]")])
s.step("Take a loop of 10 iterations, run many times. Its branch is taken 9 times, then not taken once to exit.", [hl("ob[0]")])
s.step("On the last iteration the entry says taken, but the loop exits. Wrong. And now the entry flips to not taken.", [hl("ob[1]")])
s.step("Next time the loop runs, its first branch is predicted not taken. Wrong again.", [hl("ob[2]")])
s.step("Two mistakes per 10 executions: 80 percent right, for a branch that is taken 90 percent of the time. One odd outcome costs two mispredictions.", [hl("ob[3]"), s.take("1-bit: one exit costs two mistakes")])

# ---------------------------------------------------------------- 2-bit
s.scene("twobit")
s.step("Stage 4: the fix is a 2-bit saturating counter. Four states, from strongly taken down to strongly not taken.", [s.head("Stage 4 of 7: the 2-bit counter"), s.untake()] + hide("ob") + show("fsm"))
s.step("A taken branch counts up, stopping at 11. A not-taken branch counts down, stopping at 00.", [hl("fsm.s3"), hl("fsm.s0", 0.4)])
s.step("The top two states predict taken; the bottom two, not taken.", [hl("fsm.s3"), hl("fsm.s2", 0.2), hl("fsm.s1", 0.5), hl("fsm.s0", 0.7)])
s.step("The key: from strongly taken, one not-taken outcome only drops it to weakly taken. The prediction is still taken. It takes two wrong outcomes in a row to change its mind.", [hl("fsm.s3->s2"), hl("fsm.s2", 0.4)])
s.step("The rules in one table.", hide("fsm") + show("fsx") + [hl("fsx[0..=1]")])
s.step("So on the loop of 10, the exit is mispredicted, but the counter only drops to weakly taken, and the next run's first branch is predicted right. 90 percent right.", [hl("fsx[2..=3]"), s.take("2-bit: change the prediction only after two misses")])

# ---------------------------------------------------------------- trace
s.scene("trace")
s.step("Stage 5: trace both on an inner loop of 4 iterations, run twice: taken, taken, taken, not taken, and again. Both predictors start warmed up, predicting taken.", [s.head("Stage 5 of 7: tracing both"), s.untake()] + hide("fsx") + show("tr") + [hl("tr[0]")])
s.step("The 1-bit predictor: taken, taken, taken, taken. The fourth is wrong. It flips to not taken, so execution 5 is wrong too. Then taken again, and execution 8 is wrong.", [st(f"tr[1][{k + 1}]", p, round(0.1 * k, 2)) for k, (p, _) in enumerate(R1)] + [hl("tr[1][4]", 0.85), hl("tr[1][5]", 0.9)])
s.step("3 mistakes in 8.", [hl("tr[1][8]")])
s.step("The 2-bit counter starts at 11. The exit drops it only to 10, and the next taken brings it back to 11.", [st(f"tr[2][{k + 1}]", ST[x], round(0.1 * k, 2)) for k, (x, _, _) in enumerate(R2)])
s.step("So it predicts taken all eight times, and is wrong only at the two exits. 2 mistakes in 8.", [st(f"tr[3][{k + 1}]", p, round(0.1 * k, 2)) for k, (_, p, _) in enumerate(R2)] + [hl("tr[3][4]", 0.85), hl("tr[3][8]", 0.9)])
s.step("In the long run, per run of the loop: 2 mistakes for 1-bit, 1 for 2-bit. Studies found that more than 2 bits per entry hardly helps.", [s.take("per loop exit: 1-bit misses twice, 2-bit once")])

# ---------------------------------------------------------------- BTB
s.scene("btb")
s.step("Stage 6: a prediction is only half the answer. To fetch from the target, we must also know the target address, and early: in the fetch stage, before the instruction is even decoded.", [s.head("Stage 6 of 7: the branch target buffer"), s.untake()] + hide("tr") + show("btb"))
s.step("A branch target buffer is a small cache. Each entry has a tag, the full address of a branch, so there is no aliasing.", [hl("btb[0]")])
s.step("And it holds the predicted target address.", [hl("btb[1]")])
s.step("Every fetch looks up its own address in the BTB. A hit means: this is a branch, predicted taken, and here is where to go. The next fetch comes from the target, with no penalty.", [hl("btb[2]"), hl("btb[3]", 0.5)])
s.step("The penalties. In the buffer, predicted taken, and taken: 0. In the buffer but not taken: 2 cycles to recover. Not in the buffer but taken: 2. Not in the buffer, not taken: 0.", hide("btb") + show("btp") + [hl("btp[0]"), hl("btp[1]", 0.3), hl("btp[2]", 0.6), hl("btp[3]", 0.8)])
s.step("The textbook's example. 90 percent of branches hit in the BTB, 90 percent of those predictions are right, and 60 percent of the branches that miss are taken.", hide("btp") + show("btm") + [hl("btm[0]")])
s.step("Penalty: 0.9 times 0.1 times 2, plus 0.1 times 0.6 times 2. 0.18 plus 0.12: 0.3 cycles per branch.", [{"action": "reveal", "target": "btm[1]"}, hl("btm[1]")])
s.step("Some BTBs store the target instruction itself, not just its address. Then an unconditional jump can vanish completely: branch folding.", [s.take("BTB: a tagged cache of branch → target, read during fetch")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("btm") + show("q"))
s.step("One branch goes taken, taken, not taken, three times over. Count the mispredictions for a 1-bit predictor starting at not taken, and a 2-bit counter starting at 01. Then the index bits and size of a 1024-entry table, and the BTB penalty. Pause and work it out.", [hl("q[0..=1]"), hl("q[2]", 0.4), hl("q[3]", 0.7)])
s.step("a: the 1-bit predictor always guesses the last outcome. It is wrong on the first taken, on every not taken, and on every taken right after one. 6 of 9.", hide("q") + show("qt") + [hl("qt[0]"), hl("qt[1]", 0.4)])
s.step("b: the 2-bit counter starts at 01 and predicts not taken: wrong. Then 10, 11, and it predicts taken from then on. Each not taken only drops it to 10. Wrong at execution 1 and at the three not-takens: 4 of 9.", [hl("qt[2]"), hl("qt[3]", 0.4)])
s.step("c: 1024 is 2 to the 10: index bits 11 down to 2. 1024 entries of 2 bits: 256 bytes. d: 0.95 times 0.1 times 2, plus 0.05 times 0.7 times 2: 0.26 cycles per branch.", hide("qt") + show("qa") + [hl("qa[0]")] + rv("qa", 1) + rv("qa", 2))
s.step("The usual slips: forgetting that the counter saturates at 11, and multiplying the miss-in-BTB term by the hit rate instead of by 1 minus it.", [s.take("saturate at 00 and 11 · misses in the BTB use 1 − hit rate")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A branch history table is indexed by low address bits. A 1-bit entry misses twice per loop exit; a 2-bit counter only once.", [hl("stages[0..=4]")])
s.step("A branch target buffer supplies the target in the fetch stage, so a correctly predicted taken branch costs nothing.", [hl("stages[5]")])
s.step("Next video: part 2. Correlating predictors, which look at other branches, and tournament predictors, which pick the best of two.", [mk("stages[0..=6]"), s.take("Next: correlating and tournament predictors")])

s.save("/home/claude/playlist/m3/m3v7.json")

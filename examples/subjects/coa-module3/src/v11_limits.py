"""Module 3, video 11: limits of ILP."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

r = lambda x, n=2: round(x, n)
assert r(0.95 ** 20, 3) == 0.358 and r(0.99 ** 20, 3) == 0.818 and r(0.9 ** 20, 3) == 0.122
assert 4 * 10 == 40 and 32 / 4 == 8
assert r(0.97 ** 20, 2) == 0.54 and 3 * 12 == 36 and 80 - 32 == 48 and 120 // 6 == 20
assert r(1 / 0.54, 2) == 1.85
assert round(5 / 0.05) == 100 and 64 / 10 == 6.4 and 15 / 100 == 0.15 and r(0.25 + 0.15) == 0.4 and r(1 / 0.4, 1) == 2.5
assert r(0.4 + 200 / 1000) == 0.6 and r(1 / 0.6, 2) == 1.67

s = Script("The limits of ILP")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "An ideal machine"],
    [2, "How much ILP the ideal machine finds"],
    [3, "Limit 1: the window, and Little's law"],
    [4, "Limit 2: branch prediction over a window"],
    [5, "Limit 3: renaming registers and memory aliases"],
    [6, "Putting the limits together"],
    [7, "The practical ceiling, and what came next"],
    [8, "Exam question"]]})
s.obj({"id": "ideal", "type": "table", "region": "center", "columns": ["the ideal machine has", "so"], "rows": [
    ["infinite renaming registers", "no WAR or WAW hazard ever stalls"],
    ["perfect branch and jump prediction", "the window is never on a wrong path"],
    ["perfect memory address analysis", "a load waits only for a store to the same address"],
    ["perfect caches, 1-cycle latency", "only true data dependences remain"],
    ["an unlimited window and issue width", "it can look at the whole program at once"]]})
s.obj({"id": "res", "type": "table", "region": "center", "columns": ["program (SPEC92)", "kind", "IPC on the ideal machine"], "rows": [
    ["li (Lisp interpreter)", "integer", "18"],
    ["gcc (compiler)", "integer", "55"],
    ["espresso (logic)", "integer", "63"],
    ["fpppp", "floating point", "75"],
    ["doduc", "floating point", "119"],
    ["tomcatv", "floating point", "150"]]})
s.obj({"id": "ll", "type": "math", "region": "center", "lines": [
    "\"Little's law:\" quad \"IPC\" = \"instructions in flight\" / \"average latency (cycles)\"",
    "\"IPC 4, average latency 10:\" quad \"window\" = 4 times 10 = 40 \"instructions\"",
    "\"window 32, latency 4:\" quad \"IPC\" <= 32 / 4 = 8 quad \"capped by the issue width\"",
    "\"a 200-cycle cache miss at the head:\" quad \"the window fills, then everything waits\""]})
s.obj({"id": "bp", "type": "table", "region": "center", "columns": ["accuracy", "20 branches in the window", "whole window useful"], "rows": [
    ["90%", "0.9^20", "12%"],
    ["95%", "0.95^20", "36%"],
    ["99%", "0.99^20", "82%"]]})
s.obj({"id": "rn", "type": "table", "region": "center", "columns": ["limit", "why it caps ILP"], "rows": [
    ["renaming registers", "every instruction in flight with a result needs its own physical register"],
    ["the rule", "in-flight results ≤ physical registers − architectural registers"],
    ["memory aliases", "without knowing addresses, a load must wait for every earlier store"],
    ["what helps", "address prediction and speculative loads, checked at commit"]]})
s.obj({"id": "tog", "type": "math", "region": "center", "lines": [
    "\"issue width 4:\" quad \"CPI\" >= 1 / 4 = 0.25",
    "\"window 64, average latency 10:\" quad 64 / 10 = 6.4 > 4 quad \"not the limit\"",
    "\"a branch every 5, 95% right:\" quad \"a misprediction every\" 5 / 0.05 = 100 \"instructions\"",
    "\"15 cycles each:\" quad 15 / 100 = 0.15 \"CPI\"",
    "\"CPI\" = 0.25 + 0.15 = 0.40 quad \"IPC\" = 2.5",
    "\"plus one 200-cycle memory miss per 1000:\" quad 0.40 + 0.20 = 0.60 quad \"IPC\" approx 1.67"]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["the practical ceiling", "meaning"], "rows": [
    ["real cores issue 4 to 8 per cycle", "but sustain far less on integer code: often 1 to 2"],
    ["each step wider costs more", "comparators grow as w(w − 1); windows and ports grow too"],
    ["power", "the extra logic burns energy even when it finds nothing"],
    ["the turn, around 2005", "stop chasing ILP; put several cores on a chip: thread-level parallelism"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["target IPC 3, average latency 12 cycles", "a) the window needed"],
    ["97% accuracy, a branch every 6 instructions, window 120", "b) chance the whole window is on the right path"],
    ["80 physical registers, 32 architectural", "c) the most results in flight"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad \"window\" = 3 times 12 = 36 \"instructions\"",
    "\"b)\" quad 120 / 6 = 20 \"branches\" quad 0.97^20 approx 0.54",
    "\"c)\" quad 80 - 32 = 48 \"results in flight\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Renaming, prediction, speculation, wide issue: how far can this go? This video asks how much parallelism is really in programs, and what stops a real machine from finding it.", [s.head("The limits of ILP")])
s.step("Here are the eight stages.", show("stages"))
s.step("An ideal machine, and how much ILP it finds.", [hl("stages[0..=1]")])
s.step("Then three real limits, all of them together on one machine, the practical ceiling, and an exam question.", [hl("stages[2..=7]")])

# ---------------------------------------------------------------- ideal
s.scene("ideal")
s.step("Stage 1: imagine a perfect machine. Infinite renaming registers, so name dependences never matter.", [s.head("Stage 1 of 8: an ideal machine")] + hide("stages") + show("ideal") + [hl("ideal[0]")])
s.step("Perfect prediction of every branch and jump.", [hl("ideal[1]")])
s.step("Perfect knowledge of every memory address, so a load waits only for a store to the very same address.", [hl("ideal[2]")])
s.step("Perfect caches, with every operation taking one cycle.", [hl("ideal[3]")])
s.step("And an unlimited window: it can look at the entire program, and issue any number of instructions per cycle. Only true data dependences are left to limit it.", [hl("ideal[4]"), s.take("ideal: only true dependences remain")])

# ---------------------------------------------------------------- results
s.scene("res")
s.step("Stage 2: the textbook ran SPEC92 programs on such a machine, by analysing their traces. Here is the IPC it achieved.", [s.head("Stage 2 of 8: what the ideal machine finds"), s.untake()] + hide("ideal") + show("res"))
s.step("Integer programs: from 18 for the Lisp interpreter, to 55 for gcc and 63 for espresso.", [hl("res[0..=2]")])
s.step("Floating-point programs, with their big regular loops: 75, 119, up to 150 instructions per cycle.", [hl("res[3..=5]")])
s.step("So the parallelism is there. Programs are not sequential at heart. The question is how much of it a buildable machine can reach.", [s.take("the ideal IPC: 18 to 150")])

# ---------------------------------------------------------------- window
s.scene("window")
s.step("Stage 3: the first limit is the window, the number of instructions the machine can hold and examine at once: its ROB and stations.", [s.head("Stage 3 of 8: the window"), s.untake()] + hide("res") + show("ll") + [hl("ll[0]")])
s.step("Little's law ties it together: IPC equals the instructions in flight, divided by how long each one stays. To sustain 4 per cycle when instructions take 10 cycles on average, 40 must be in flight.", rv("ll", 1))
s.step("Turn it around: a 32-entry window with 4-cycle latency allows at most 8 per cycle. And the issue width caps it again.", rv("ll", 2))
s.step("Now let a load at the head miss the cache for 200 cycles. It cannot commit; the window fills behind it in a few dozen cycles, and then the whole machine waits. That is why windows have grown to hundreds of entries, and why memory latency is the hardest limit of all.", rv("ll", 3) + [s.take("Little's law: window = IPC × latency")])

# ---------------------------------------------------------------- branch
s.scene("branch")
s.step("Stage 4: the second limit is branch prediction, compounded over a big window.", [s.head("Stage 4 of 8: prediction over a window"), s.untake()] + hide("ll") + show("bp"))
s.step("Say a branch comes every 5 instructions. A window of 100 then holds 20 branches, and all 20 must be guessed right for the whole window to be useful.", [hl("bp")])
s.step("At 90 percent accuracy per branch: 0.9 to the 20th is only 12 percent.", [hl("bp[0]")])
s.step("At 95 percent: 36 percent. At 99 percent: 82 percent.", [hl("bp[1]"), hl("bp[2]", 0.4)])
s.step("Another way to see it: with accuracy p, a misprediction comes on average every 1 over 1 minus p branches. At 95 percent, every 20 branches: every 100 instructions. A window much bigger than that is mostly filled with work that will be thrown away.", [hl("bp[1]")])
s.step("So a bigger window demands much better prediction. Each extra percent of accuracy is worth far more than it looks.", [s.take("chance the window is useful = accuracy ^ branches in it")])

# ---------------------------------------------------------------- rename
s.scene("rename")
s.step("Stage 5: the third limit is names.", [s.head("Stage 5 of 8: registers and aliases"), s.untake()] + hide("bp") + show("rn"))
s.step("Every instruction in flight that produces a result needs its own physical register until it commits.", [hl("rn[0]")])
s.step("The architectural registers hold the committed state, so the results in flight can be at most the physical registers minus the architectural ones.", [hl("rn[1]")])
s.step("And memory: if the machine cannot tell whether a load and an earlier store touch the same address, the load must wait for the store, even when they never overlap.", [hl("rn[2]")])
s.step("Modern cores predict that they do not alias, let the load go early, and check at commit, replaying it if the guess was wrong. Speculation once again.", [hl("rn[3]"), s.take("in flight ≤ physical − architectural registers")])

# ---------------------------------------------------------------- together
s.scene("together")
s.step("Stage 6: put the limits together for one machine. It issues 4 per cycle, so its CPI can never drop below 0.25.", [s.head("Stage 6 of 8: putting it together"), s.untake()] + hide("rn") + show("tog") + [hl("tog[0]")])
s.step("Its window holds 64 instructions, and they take 10 cycles on average. By Little's law that allows 6.4 per cycle, more than the issue width, so the window is not the limit here.", rv("tog", 1))
s.step("Branches come every 5 instructions and are predicted 95 percent right: a misprediction every 100 instructions. Each costs 15 cycles to refill, adding 0.15 to the CPI.", rv("tog", 2) + rv("tog", 3))
s.step("So the CPI is 0.4, an IPC of 2.5, on a 4-wide machine.", rv("tog", 4))
s.step("Now add one memory miss of 200 cycles per 1000 instructions, which the window cannot hide. Another 0.2: CPI 0.6, IPC about 1.67. That is how a 4-wide core ends up sustaining 1 to 2.", rv("tog", 5) + [s.take("add up every source of lost cycles")])

# ---------------------------------------------------------------- ceiling
s.scene("ceiling")
s.step("Stage 7: the practical ceiling.", [s.head("Stage 7 of 8: the practical ceiling"), s.untake()] + hide("tog") + show("pr"))
s.step("Real cores can issue 4 to 8 instructions per cycle, but on integer code they often sustain only 1 to 2.", [hl("pr[0]")])
s.step("Every step wider costs more than the last: comparators grow as w times w minus 1, and so do windows, ports and buses.", [hl("pr[1]")])
s.step("And that logic burns power, even in cycles where it finds nothing to do.", [hl("pr[2]")])
s.step("Around 2005, the industry turned. Rather than one ever-wider core, put several cores on a chip, and run separate threads on them. That is thread-level parallelism, the rest of this module.", [hl("pr[3]"), s.take("ILP hit diminishing returns → multithreading and multicore")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("pr") + show("q"))
s.step("How big a window sustains IPC 3 when instructions take 12 cycles on average?", [hl("q[0]")])
s.step("The chance a 120-instruction window is all on the right path, with a branch every 6 instructions and 97 percent accuracy. And the most results in flight with 80 physical and 32 architectural registers. Pause and work it out.", [hl("q[1]"), hl("q[2]", 0.5)])
s.step("a: Little's law: 3 times 12, a window of 36.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 120 over 6 is 20 branches. 0.97 to the 20th is about 0.54: barely half the time.", rv("qa", 1))
s.step("c: 80 minus 32: at most 48 results in flight.", rv("qa", 2))
s.step("The usual slip: multiplying accuracies is easy to forget. Ninety-seven percent per branch sounds high, but over 20 branches it is a coin toss.", [s.take("small per-branch errors compound across a window")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("An ideal machine finds 18 to 150 instructions per cycle: the parallelism exists.", [hl("stages[0..=1]")])
s.step("Real machines are limited by the window, by prediction compounded across it, by registers and memory aliases, and in the end by cost and power.", [hl("stages[2..=6]")])
s.step("Next video: multithreading. If one thread cannot fill the machine, let several share it.", [mk("stages[0..=7]"), s.take("Next: multithreading")])

s.save("/home/claude/playlist/m3/m3v11.json")

"""Video 3: write policies (write-through / write-back, write-allocate / no-write-allocate) and the three C's."""
import sys
sys.path.insert(0, ".")
from common import Script

SEQ = [0, 4, 0, 4, 1, 1, 2, 3, 5, 0]


def classify(seq, lines=4):
    dm, fa, seen, out = [None] * lines, [], set(), []
    for b in seq:
        i = b % lines
        dmhit, fahit = dm[i] == b, b in fa
        if fahit:
            fa.remove(b)
        elif len(fa) == lines:
            fa.pop(0)
        fa.append(b)
        c = "hit" if dmhit else "compulsory" if b not in seen else "capacity" if not fahit else "conflict"
        out.append(dict(b=b, line=i, dmhit=dmhit, seen=b in seen, fahit=fahit, c=c, was=dm[i]))
        seen.add(b); dm[i] = b
    return out


C = classify(SEQ)
counts = {k: sum(o["c"] == k for o in C) for k in ("compulsory", "capacity", "conflict", "hit")}
assert counts == {"compulsory": 6, "capacity": 1, "conflict": 2, "hit": 1}

s = Script("The three C's of cache misses")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Compulsory, capacity, conflict: what each means"],
    [2, "A two-question test to classify any miss"],
    [3, "Classify every miss of a reference string"],
    [4, "What changes each kind of miss"],
    [5, "Exam question"]]})
s.obj({"id": "threec", "type": "table", "region": "center", "columns": ["miss", "cause", "it would miss even in"], "rows": [
    ["compulsory", "the first reference to a block", "an infinite cache"],
    ["capacity", "the cache cannot hold every block the program is using", "a fully associative cache of the same size"],
    ["conflict", "too many blocks map to one set", "nothing: a fully associative cache would have hit"]]})
s.obj({"id": "test", "type": "diagram", "region": "right", "layout": "layers", "direction": "down", "nodes": [
    {"id": "m", "label": "a miss"},
    {"id": "q1", "label": "first use?"},
    {"id": "comp", "label": "compulsory", "shape": "pill"},
    {"id": "q2", "label": "FA LRU hit?"},
    {"id": "conf", "label": "conflict", "shape": "pill"},
    {"id": "cap", "label": "capacity", "shape": "pill"}],
    "edges": [{"from": "m", "to": "q1"}, {"from": "q1", "to": "comp", "label": "yes"}, {"from": "q1", "to": "q2", "label": "no"},
              {"from": "q2", "to": "conf", "label": "yes"}, {"from": "q2", "to": "cap", "label": "no"}]})
s.obj({"id": "cls", "type": "table", "region": "center", "columns": ["#", "block", "line", "direct-mapped", "seen?", "FA hits?", "class"],
       "rows": [[i + 1, o["b"], "", "", "", "", ""] for i, o in enumerate(C)]})
s.obj({"id": "fix", "type": "table", "region": "center", "columns": ["miss", "reduced by", "but it costs"], "rows": [
    ["compulsory", "larger blocks, prefetching", "a longer miss penalty; more conflict misses if blocks get too big"],
    ["capacity", "a larger cache", "a longer hit time, more power and area"],
    ["conflict", "higher associativity", "a longer hit time"]]})

s.obj({"id": "eff", "type": "table", "region": "center", "columns": ["change", "compulsory", "capacity", "conflict"], "rows": [
    ["bigger cache, same blocks", "same", "fewer", "fewer"],
    ["higher associativity", "same", "same", "fewer"],
    ["bigger blocks, same cache", "fewer", "can rise", "can rise"],
    ["fully associative", "same", "same", "none at all"]]})
# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Every miss has a cause. Knowing the cause tells you which fix will help, and which will not.", [s.head("The three C's of cache misses")])
s.step("Here are the five stages.", [{"action": "show", "target": "stages"}])
s.step("The three kinds of miss, and a test that sorts any miss into one of them.", [{"action": "highlight", "target": "stages[0..=1]"}])
s.step("Then a full reference string classified by hand, what changes each kind, and an exam question.", [{"action": "highlight", "target": "stages[2..=4]"}])

# ---------------------------------------------------------------- 3 Cs
s.scene("three-cs")
s.step("Stage 1: every miss has a cause, and there are three kinds, the three C's.", [s.head("Stage 1 of 5: the three C's"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "threec"}])
s.step("Compulsory misses happen on the very first reference to a block; it has never been in the cache.", [{"action": "highlight", "target": "threec[0]"}])
s.step("Even an infinite cache would take these misses.", [{"action": "highlight", "target": "threec[0][2]"}])
s.step("Capacity misses happen when the program uses more blocks than the cache can hold.", [{"action": "highlight", "target": "threec[1]"}])
s.step("The test: even a fully associative cache of the same size would miss.", [{"action": "highlight", "target": "threec[1][2]"}])
s.step("Conflict misses happen when too many blocks map to one set, although other lines are free.", [{"action": "highlight", "target": "threec[2]"}])
s.step("A fully associative cache of the same size would have hit, so the mapping is to blame.", [{"action": "highlight", "target": "threec[2][2]"}])

# ---------------------------------------------------------------- classify
s.scene("classify")
s.step("Stages 2 and 3: classify every miss of a real trace. The procedure has two questions.", [s.head("Stage 2 and 3 of 5: classifying misses"), {"action": "hide", "target": "threec"}, {"action": "show", "target": "test"}])
s.step("First: is this the first time the block is used? If yes, it is compulsory.", [{"action": "highlight", "target": "test.q1"}, {"action": "highlight", "target": "test.comp", "delay": 0.5}])
s.step("If not: would a fully associative LRU cache of the same size have hit?", [{"action": "highlight", "target": "test.q2"}])
s.step("If it would, the miss is conflict; if it would not, the miss is capacity.", [{"action": "highlight", "target": "test.conf"}, {"action": "highlight", "target": "test.cap", "delay": 0.5}])
s.step("Our cache: direct-mapped, 4 lines, so block b goes to line b mod 4.", [{"action": "hide", "target": "test"}, {"action": "show", "target": "cls"}, s.take("direct-mapped, 4 lines · line = block mod 4 · shadow: FA LRU, 4 lines")])
s.step("Beside it we keep a shadow: a fully associative LRU cache, also 4 lines.", [{"action": "highlight", "target": "cls.c5"}])
s.step("The blocks referenced are 0, 4, 0, 4, 1, 1, 2, 3, 5, 0.", [{"action": "highlight", "target": "cls.block"}])

say = {
    0: "Block 0 goes to line 0; never seen before, so a compulsory miss.",
    1: "Block 4: 4 mod 4 is 0, line 0 again, and it is new: compulsory, and block 0 is thrown out.",
    2: "Block 0 again: line 0 holds 4, a miss. But we have seen 0, and the shadow still holds 0 and 4, so it would hit: conflict.",
    3: "Block 4: line 0 now holds 0, a miss; the shadow would hit again, so conflict.",
    4: "Block 1 goes to line 1, first use: compulsory.",
    5: "Block 1 again: line 1 holds 1, a hit.",
    6: "Block 2 goes to line 2, first use: compulsory.",
    7: "Block 3 goes to line 3, first use: compulsory. The shadow is now full: 4, 1, 2, 3.",
    8: "Block 5: 5 mod 4 is 1, so line 1, first use: compulsory, and block 1 is thrown out.",
    9: "Block 0: line 0 holds 4, a miss. We have seen 0, but the shadow evicted it to make room, so capacity.",
}
for i, o in enumerate(C):
    s.step(say[i], [{"action": "highlight", "target": f"cls[{i}]"},
                    {"action": "set", "target": f"cls[{i}][2]", "value": str(o["line"])},
                    {"action": "set", "target": f"cls[{i}][3]", "value": "hit" if o["dmhit"] else "miss", "delay": 0.2},
                    {"action": "set", "target": f"cls[{i}][4]", "value": "yes" if o["seen"] else "no", "delay": 0.4},
                    {"action": "set", "target": f"cls[{i}][5]", "value": ("yes" if o["fahit"] else "no") if o["seen"] and not o["dmhit"] else "–", "delay": 0.5},
                    {"action": "set", "target": f"cls[{i}][6]", "value": o["c"], "delay": 0.7}])
s.step("Count: 6 compulsory, 2 conflict, 1 capacity, and 1 hit.", [{"action": "mark", "target": "cls.class"}, s.take("6 compulsory · 2 conflict · 1 capacity · 1 hit")])
s.step("Check: 6 plus 2 plus 1 misses, plus 1 hit, gives all 10 references.", [])
s.step("Each kind of miss has its own cure, and its own cost.", [{"action": "hide", "target": "cls"}, s.untake(), {"action": "show", "target": "fix"}])
s.step("Larger blocks and prefetching cut compulsory misses, but each miss takes longer.", [{"action": "highlight", "target": "fix[0]"}])
s.step("A larger cache cuts capacity misses, but slows the hit and costs power.", [{"action": "highlight", "target": "fix[1]"}])
s.step("Higher associativity cuts conflict misses, but also slows the hit.", [{"action": "highlight", "target": "fix[2]"}])
s.step("These three ideas start the list of basic cache optimizations.", [{"action": "mark", "target": "fix"}])
s.scene("effect")
s.step("Stage 4: what does each change do to each kind of miss? GATE asks this as a true or false.", [s.head("Stage 4 of 5: what changes each kind"), {"action": "hide", "target": "fix"}, {"action": "show", "target": "eff"}])
s.step("A bigger cache cuts capacity misses, and usually conflict misses too. Compulsory misses do not change: first uses are first uses.", [{"action": "highlight", "target": "eff[0]"}])
s.step("Higher associativity cuts only conflict misses. Same size, so the same capacity.", [{"action": "highlight", "target": "eff[1]"}])
s.step("Bigger blocks bring in more neighbours on each miss, so fewer compulsory misses. But with the same cache size there are fewer lines, so capacity and conflict misses can rise.", [{"action": "highlight", "target": "eff[2]"}])
s.step("A fully associative cache has no conflict misses at all, by definition.", [{"action": "highlight", "target": "eff[3]"}])
s.step("And in multiprocessors there is a fourth C, coherence: a line thrown out because another core wrote to it. We meet it later.", [s.take("cache ↑ → capacity ↓ · ways ↑ → conflict ↓ · block ↑ → compulsory ↓")])

# ---------------------------------------------------------------- exam question
QSEQ = [0, 2, 0, 1, 3, 1, 2]
QC = classify(QSEQ, lines=2)
assert [o["c"] for o in QC] == ["compulsory", "compulsory", "conflict", "compulsory", "compulsory", "conflict", "capacity"]
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["#", "block", "line", "seen?", "FA hits?", "class"],
       "rows": [[i + 1, o["b"], "", "", "", ""] for i, o in enumerate(QC)]})
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), {"action": "hide", "target": "eff"}, s.untake(), {"action": "show", "target": "qx"}])
s.step("A direct-mapped cache has 2 lines. Classify each miss for the blocks 0, 2, 0, 1, 3, 1, 2.", [{"action": "highlight", "target": "qx.block"}])
s.step("Pause and try it. Remember the shadow: a fully associative LRU cache with 2 lines.", [s.take("line = block mod 2 · shadow: fully associative LRU, 2 lines")])
qsay = [
    "Block 0 goes to line 0, first use: compulsory.",
    "Block 2: 2 mod 2 is 0, line 0, first use: compulsory, and 0 is thrown out.",
    "Block 0: line 0 holds 2, a miss. The shadow still holds 0 and 2, so it would hit: conflict.",
    "Block 1 goes to line 1, first use: compulsory. The shadow drops 2 and keeps 0 and 1.",
    "Block 3: line 1, first use: compulsory. The shadow drops 0 and keeps 1 and 3.",
    "Block 1: line 1 holds 3, a miss; the shadow holds 1, so it would hit: conflict.",
    "Block 2: line 0 holds 0, a miss; the shadow holds 3 and 1, not 2, so capacity.",
]
for i, o in enumerate(QC):
    s.step(qsay[i], [{"action": "highlight", "target": f"qx[{i}]"},
                     {"action": "set", "target": f"qx[{i}][2]", "value": str(o["line"])},
                     {"action": "set", "target": f"qx[{i}][3]", "value": "yes" if o["seen"] else "no", "delay": 0.3},
                     {"action": "set", "target": f"qx[{i}][4]", "value": ("yes" if o["fahit"] else "no") if o["seen"] else "–", "delay": 0.4},
                     {"action": "set", "target": f"qx[{i}][5]", "value": o["c"], "delay": 0.6}])
s.step("Answer: 4 compulsory, 2 conflict and 1 capacity, so all 7 references miss.", [{"action": "mark", "target": "qx.class"}, s.take("4 compulsory · 2 conflict · 1 capacity")])
s.step("The usual slip is calling the last miss conflict: always check the shadow, not just the line.", [{"action": "highlight", "target": "qx[6]"}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qx"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("Compulsory: the first use. Capacity: even a fully associative cache of the same size would miss. Conflict: it would have hit.", [{"action": "highlight", "target": "stages[0..=1]"}])
s.step("Classify with a shadow fully associative LRU cache, and match each fix to the kind of miss it removes.", [{"action": "highlight", "target": "stages[2..=4]"}])
s.step("Next video: putting numbers on misses, with average memory access time.", [{"action": "mark", "target": "stages[0..=4]"}, s.take("Next: AMAT")])

s.save("./m2v4.json")
